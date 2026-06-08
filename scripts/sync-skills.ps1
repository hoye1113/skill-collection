# sync-skills.ps1 - Skills upstream sync script
# Reads sync-config.json, pulls each repo, syncs changed files to skill-collection

$ErrorActionPreference = "Continue"

$ProjectRoot  = "D:\workSpace\hoye-skills-main\skill-collection"
$ConfigFile   = Join-Path $ProjectRoot "sync-config.json"
$LogFile      = Join-Path $ProjectRoot "sync-logs\$(Get-Date -Format 'yyyy-MM-dd').log"
$ExcludeFlags = @("/XD", ".git", "node_modules", "/XF", ".env")

function Log($msg) {
    $ts = Get-Date -Format "HH:mm:ss"
    $line = "[$ts] $msg"
    Write-Host $line
    Add-Content -Path $LogFile -Value $line
}

function RoboSync($src, $dst) {
    if (-not (Test-Path $dst)) { New-Item -ItemType Directory -Path $dst -Force | Out-Null }
    $args = @($src, $dst, "/MIR", "/NFL", "/NDL", "/NJH", "/NJS", "/NP") + $ExcludeFlags
    & robocopy @args | Out-Null
}

Log "=== Skills sync started ==="

$config = Get-Content $ConfigFile -Raw | ConvertFrom-Json
$syncedAny = $false

foreach ($repo in $config.repos) {
    $repoPath = $repo.path
    if (-not (Test-Path $repoPath)) {
        Log "SKIP $($repo.name): path not found ($repoPath)"
        continue
    }

    $oldHead = git -C $repoPath rev-parse HEAD 2>$null
    if ($LASTEXITCODE -ne 0) {
        Log "SKIP $($repo.name): not a git repo"
        continue
    }

    git -C $repoPath pull --rebase 2>&1 | ForEach-Object { Log "  git: $_" }
    if ($LASTEXITCODE -ne 0) {
        Log "WARN $($repo.name): pull failed, attempting rebase --abort"
        git -C $repoPath rebase --abort 2>$null
        continue
    }

    $newHead = git -C $repoPath rev-parse HEAD 2>$null
    if ($oldHead -eq $newHead) {
        Log "OK   $($repo.name): no changes"
        continue
    }

    Log "SYNC $($repo.name): $($oldHead.Substring(0,7)) -> $($newHead.Substring(0,7))"
    $syncedAny = $true

    switch ($repo.strategy) {
        "whole" {
            $src = if ($repo.source -eq ".") { $repoPath } else { Join-Path $repoPath $repo.source }
            $dst = Join-Path $ProjectRoot $repo.target
            RoboSync $src $dst
            Log "  whole: $src -> $dst"
        }
        "filtered" {
            foreach ($inc in $repo.include) {
                $src = Join-Path $repoPath $inc
                $dst = Join-Path $ProjectRoot "$($repo.target)\$inc"
                if (Test-Path $src) {
                    RoboSync $src $dst
                    Log "  filtered: $src -> $dst"
                }
            }
        }
        "mapped" {
            foreach ($m in $repo.mappings) {
                $src = Join-Path $repoPath $m.source
                $dst = Join-Path $ProjectRoot $m.target
                if (Test-Path $src) {
                    RoboSync $src $dst
                    Log "  mapped: $src -> $dst"
                } else {
                    Log "  SKIP mapping $($m.source): source not found"
                }
            }
        }
    }
}

Push-Location $ProjectRoot
$status = git status --porcelain 2>$null
if ($status) {
    git add -A 2>&1 | ForEach-Object { Log "  git add: $_" }
    $dateStr = Get-Date -Format "yyyy-MM-dd HH:mm"
    git commit -m "sync: update skills from upstream $dateStr" 2>&1 | ForEach-Object { Log "  git commit: $_" }
    Log "Committed changes. Do NOT push."
} else {
    Log "No file changes in skill-collection after sync."
}
Pop-Location

Log "=== Skills sync finished ==="
