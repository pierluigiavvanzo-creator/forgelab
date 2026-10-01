param(
    [string]$ExpectedHead = ""
)

$ErrorActionPreference = "Stop"

$RepoRoot = (Get-Location).Path
$Log = Join-Path $env:USERPROFILE "Desktop\FORGELAB_VALIDATION.txt"

function Write-LogLine {
    param([string]$Text)
    $Text | Tee-Object -FilePath $Log -Append
}

function Invoke-PythonStep {
    param(
        [string]$Name,
        [string[]]$Arguments
    )

    Write-LogLine ""
    Write-LogLine "=== $Name ==="

    $stdoutFile = [System.IO.Path]::GetTempFileName()
    $stderrFile = [System.IO.Path]::GetTempFileName()

    try {
        $allArgs = @("-3.11") + $Arguments
        $process = Start-Process `
            -FilePath "py" `
            -ArgumentList $allArgs `
            -NoNewWindow `
            -Wait `
            -PassThru `
            -RedirectStandardOutput $stdoutFile `
            -RedirectStandardError $stderrFile

        $stdout = Get-Content $stdoutFile -Raw -ErrorAction SilentlyContinue
        $stderr = Get-Content $stderrFile -Raw -ErrorAction SilentlyContinue
        $exitCode = $process.ExitCode
    }
    finally {
        Remove-Item $stdoutFile, $stderrFile -Force -ErrorAction SilentlyContinue
    }

    if ($stdout) {
        $stdout.TrimEnd() | Tee-Object -FilePath $Log -Append
    }
    if ($stderr) {
        $stderr.TrimEnd() | Tee-Object -FilePath $Log -Append
    }

    Write-LogLine "EXIT_CODE: $exitCode"

    $combinedOutput = $stdout + [Environment]::NewLine + $stderr
    if (
        $Name -eq "FULL PYTHON REGRESSION" -and
        $combinedOutput -match "Ran\s+0\s+tests"
    ) {
        throw "FULL_PYTHON_REGRESSION_DISCOVERED_ZERO_TESTS"
    }

    if ($exitCode -ne 0) {
        throw "$Name FAILED"
    }
}

$Head = (git rev-parse HEAD).Trim()

"=== FORGELAB VALIDATION ===" | Set-Content $Log -Encoding utf8
Write-LogLine "REPO: $RepoRoot"
Write-LogLine "HEAD: $Head"

if ($ExpectedHead -and $Head -ne $ExpectedHead) {
    throw "UNEXPECTED_HEAD: $Head"
}

Get-ChildItem -Path $RepoRoot -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force

Write-LogLine ""
Write-LogLine "=== GIT STATUS BEFORE TESTS ==="
$beforeStatus = git status --porcelain
if ($beforeStatus) {
    $beforeStatus | Tee-Object -FilePath $Log -Append
    throw "VALIDATION_WORKTREE_NOT_CLEAN"
}
Write-LogLine "CLEAN"

$env:PYTHONPATH = Join-Path $RepoRoot "src"
$env:PYTHONDONTWRITEBYTECODE = "1"

Invoke-PythonStep -Name "PLAN -> DEVELOPER -> SEMANTIC REPAIR CONTRACT" -Arguments @("-m", "unittest", "tests.test_orchestrator.MultiAgentTests.test_semantic_review_failure_uses_bounded_repair_and_rereview", "-v")

Invoke-PythonStep -Name "API AI-GENERATE REGRESSION" -Arguments @("-m", "unittest", "tests.test_api.ApiTests.test_create_run_accepts_ai_generate_without_old_new", "tests.test_api.ApiTests.test_create_run_accepts_ai_generate_with_two_authorized_paths", "-v")

Invoke-PythonStep -Name "FULL PYTHON REGRESSION" -Arguments @("-m", "unittest", "discover", "-s", "tests", "-p", "test*.py", "-v")

Write-LogLine ""
Write-LogLine "=== GIT STATUS AFTER TESTS ==="
$status = git status --porcelain
if ($status) {
    $status | Tee-Object -FilePath $Log -Append
    throw "VALIDATION_DIRTY_WORKTREE"
}

Write-LogLine "CLEAN"
Write-LogLine ""
Write-LogLine "=== FORGELAB VALIDATION PASS ==="

Write-Host ""
Write-Host "=========================================="
Write-Host " FORGELAB VALIDATION PASS"
Write-Host " HEAD: $Head"
Write-Host " LOG : $Log"
Write-Host "=========================================="
