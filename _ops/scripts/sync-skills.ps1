# sync-skills.ps1 - Skills upstream sync script
# Uses git ls-remote to check remote changes, only pulls when needed
# Clone cache lives at _ops/.sync-cache/<name> (inside project, sandbox-safe)

$ErrorActionPreference = "Continue"

$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$OpsDir       = Split-Path -Parent $ScriptDir
$ProjectRoot  = Split-Path -Parent $OpsDir
$ConfigFile   = Join-Path $OpsDir "sync-config.json"
$StateFile    = Join-Path $OpsDir "sync-state.json"
$LogFile      = Join-Path $OpsDir "sync-logs\$(Get-Date -Format 'yyyy-MM-dd').log"
$CacheDir     = Join-Path $OpsDir ".sync-cache"
$ExcludeFlags = @("/XD", ".git", "node_modules", "/XF", ".env")

$logBuffer = [System.Collections.ArrayList]::new()
$anySkillSynced = $false

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    $script:logBuffer.Add($line) | Out-Null
}

function FlushLog {
    $logDir = Split-Path $LogFile -Parent
    if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
    $script:logBuffer | Add-Content -Path $LogFile
}

function LoadState {
    if (Test-Path $StateFile) {
        return Get-Content $StateFile -Raw | ConvertFrom-Json
    }
    return [PSCustomObject]@{}
}

function SaveState($state) {
    $json = $state | ConvertTo-Json -Depth 5
    [System.IO.File]::WriteAllText($StateFile, $json, (New-Object System.Text.UTF8Encoding($false)))
}

function RoboSync($src, $dst) {
    if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }
    $args = @($src, $dst, "/MIR", "/NFL", "/NDL", "/NJH", "/NJS", "/NP") + $ExcludeFlags
    & robocopy @args | Out-Null
}

# --- main ---
Log "=== Skills sync started ==="
Log "ProjectRoot: $ProjectRoot"
Log "ConfigFile: $ConfigFile"

$config = Get-Content $ConfigFile -Raw | ConvertFrom-Json
$state = LoadState
$changed = $false

foreach ($repo in $config.repos) {
    $name = $repo.name
    $remoteUrl = $repo.remoteUrl
    $repoPath = Join-Path $CacheDir $name

    # Step 1: check remote HEAD via ls-remote
    $remoteHead = git ls-remote $remoteUrl HEAD 2>$null
    if ($LASTEXITCODE -ne 0 -or -not $remoteHead) {
        Log "SKIP $name : ls-remote failed"
        continue
    }
    $remoteHash = ($remoteHead -split "`t")[0]

    # Compare with last known hash
    $lastHash = ""
    if ($state.PSObject.Properties[$name]) { $lastHash = $state.$name }

    if ($remoteHash -eq $lastHash -and $lastHash -ne "") {
        Log "OK   $name : no remote changes ($($remoteHash.Substring(0,7)))"
        continue
    }

    if ($lastHash -eq "") {
        Log "SYNC $name : first run ($($remoteHash.Substring(0,7)))"
    } else {
        Log "SYNC $name : $($lastHash.Substring(0,7)) -> $($remoteHash.Substring(0,7))"
    }

    # Step 2: ensure local clone exists and pull
    if (-not (Test-Path $repoPath)) {
        Log "  cloning $name into cache..."
        if (-not (Test-Path $CacheDir)) { New-Item -ItemType Directory -Path $CacheDir -Force | Out-Null }
        git clone --depth 1 $remoteUrl $repoPath 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Log "SKIP $name : clone failed"
            continue
        }
        Log "  cloned $name (shallow)"
    } else {
        git -C $repoPath pull --rebase 2>&1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Log "WARN $name : pull failed, attempting rebase --abort"
            git -C $repoPath rebase --abort 2>$null
            # Nuke and re-clone on persistent failure
            Log "  re-cloning $name..."
            Remove-Item -Recurse -Force $repoPath 2>$null
            git clone --depth 1 $remoteUrl $repoPath 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Log "SKIP $name : re-clone failed"
                continue
            }
            Log "  re-cloned $name (shallow)"
        }
    }

    # Step 3: sync files based on strategy
    $syncedThisRepo = $false
    switch ($repo.strategy) {
        "whole" {
            $src = if ($repo.source -eq ".") { $repoPath } else { Join-Path $repoPath $repo.source }
            $dst = Join-Path $ProjectRoot $repo.target
            RoboSync $src $dst
            $syncedThisRepo = $true
            Log "  whole -> $($repo.target)"
        }
        "filtered" {
            foreach ($inc in $repo.include) {
                $src = Join-Path $repoPath $inc
                $dst = Join-Path $ProjectRoot "$($repo.target)\$inc"
                if (Test-Path $src) {
                    RoboSync $src $dst
                    $syncedThisRepo = $true
                    Log "  filtered $inc -> $($repo.target)\$inc"
                }
            }
        }
        "mapped" {
            foreach ($m in $repo.mappings) {
                $src = Join-Path $repoPath $m.source
                $dst = Join-Path $ProjectRoot $m.target
                if (Test-Path $src) {
                    RoboSync $src $dst
                    $syncedThisRepo = $true
                    Log "  mapped $($m.source) -> $($m.target)"
                } else {
                    Log "  SKIP $($m.source): not found"
                }
            }
        }
    }

    # Update state
    $state | Add-Member -NotePropertyName $name -NotePropertyValue $remoteHash -Force
    $changed = $true

    if ($syncedThisRepo) {
        $script:anySkillSynced = $true
        Log "  files synced for $name"
    } else {
        Log "  no files synced for $name (strategy matched no paths)"
    }
}

# Save state
if ($changed) { SaveState $state }

# Commit only when skill files were actually synced
Push-Location $ProjectRoot

if (-not $anySkillSynced) {
    Log "No skill updates this run. Skipping commit."
} else {
    # Check for actual changes excluding _ops (log/state files)
    $skillChanges = git status --porcelain 2>$null | Where-Object {
        $_ -notmatch '^[_ACDMR]+\s+_ops/'
    }
    if ($skillChanges) {
        $addResult = git add -A 2>&1
        if ($LASTEXITCODE -ne 0) {
            Log "BLOCKED: git add failed (sandbox .git DENY ACE)."
            Log "ACTION: Run these commands outside sandbox:"
            Log "  cd $ProjectRoot"
            Log "  git add -A"
            $dateStr = Get-Date -Format "yyyy-MM-dd"
            Log "  git commit -m `"sync: update skills from upstream $dateStr`""
            Log "  git push"
        } else {
            $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm"
            git commit --no-verify -m "sync: update skills from upstream $dateStr" 2>&1 | Out-Null
            if ($LASTEXITCODE -ne 0) {
                Log "BLOCKED: git commit failed (sandbox .git DENY ACE)."
                Log "ACTION: Run these commands outside sandbox:"
                Log "  cd $ProjectRoot"
                Log "  git commit -m `"sync: update skills from upstream $dateStr`""
                Log "  git push"
            } else {
                Log "Committed skill changes. Do NOT push."
            }
        }
    } else {
        Log "Skill sync ran but produced no file changes. Skipping commit."
    }
}
Pop-Location

Log "=== Skills sync finished ==="
FlushLog
