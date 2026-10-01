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

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "py"
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $psi.ArgumentList.Add("-3.11")
    foreach ($arg in $Arguments) {
        $psi.ArgumentList.Add($arg)
    }

    $process = New-Object System.Diagnostics.Process
    $process.StartInfo = $psi
    [void]$process.Start()
    $stdout = $process.StandardOutput.ReadToEnd()
    $stderr = $process.StandardError.ReadToEnd()
    $process.WaitForExit()
    $exitCode = $process.ExitCode

    if ($stdout) {
        $stdout.TrimEnd() | Tee-Object -FilePath $Log -Append
    }
    if ($stderr) {
        $stderr.TrimEnd() | Tee-Object -FilePath $Log -Append
    }

    Write-LogLine "EXIT_CODE: $exitCode"

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
