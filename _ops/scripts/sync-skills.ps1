# sync-skills.ps1 - Skills upstream sync script
# Uses git ls-remote to check remote changes, only pulls when needed

$ErrorActionPreference = "Continue"

$ScriptDir    = Split-Path -Parent $MyInvocation.MyCommand.Path
$OpsDir       = Split-Path -Parent $ScriptDir
$ProjectRoot  = Split-Path -Parent $OpsDir
$ConfigFile   = Join-Path $OpsDir "sync-config.json"
$StateFile    = Join-Path $OpsDir "sync-state.json"
$LogFile      = Join-Path $OpsDir "sync-logs\$(Get-Date -Format 'yyyy-MM-dd').log"
$ExcludeFlags = @("/XD", ".git", "node_modules", "/XF", ".env")

$logBuffer = [System.Collections.ArrayList]::new()

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
    $repoPath = $repo.path

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
        Log "SKIP $name : local path not found"
        continue
    }

    git -C $repoPath pull --rebase 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Log "WARN $name : pull failed, attempting rebase --abort"
        git -C $repoPath rebase --abort 2>$null
        continue
    }

    # Step 3: sync files based on strategy
    switch ($repo.strategy) {
        "whole" {
            $src = if ($repo.source -eq ".") { $repoPath } else { Join-Path $repoPath $repo.source }
            $dst = Join-Path $ProjectRoot $repo.target
            RoboSync $src $dst
            Log "  whole -> $($repo.target)"
        }
        "filtered" {
            foreach ($inc in $repo.include) {
                $src = Join-Path $repoPath $inc
                $dst = Join-Path $ProjectRoot "$($repo.target)\$inc"
                if (Test-Path $src) {
                    RoboSync $src $dst
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
}

# Save state
if ($changed) { SaveState $state }

# Commit if file changes
Push-Location $ProjectRoot
$status = git status --porcelain 2>$null
if ($status) {
    git add -A 2>&1 | Out-Null
    $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "sync: update skills from upstream $dateStr" 2>&1 | Out-Null
    Log "Committed changes. Do NOT push."
} else {
    Log "No file changes after sync."
}
Pop-Location

Log "=== Skills sync finished ==="
FlushLog