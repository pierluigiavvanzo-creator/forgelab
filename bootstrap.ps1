[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

function Invoke-ForgePython {
    param([string[]]$Arguments)
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3.11 @Arguments
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python @Arguments
    }
    else {
        throw "Python 3.11 o superiore non trovato. Installalo e rilancia bootstrap.ps1."
    }
    if ($LASTEXITCODE -ne 0) { throw "Comando Python non riuscito." }
}

Push-Location $ProjectRoot
try {
    $env:PYTHONPATH = Join-Path $ProjectRoot "src"
    Invoke-ForgePython -Arguments @("-c", "import sys; assert sys.version_info >= (3, 11), sys.version")
    Invoke-ForgePython -Arguments @("-m", "unittest", "discover", "-s", "tests", "-v")
    Invoke-ForgePython -Arguments @("-m", "forgelab", "smoke", "--output", ".forgelab/runs")
    Invoke-ForgePython -Arguments @("-m", "forgelab", "metrics", "--runs", ".forgelab/runs")
    Write-Host "ForgeLab M8.1 verificato correttamente." -ForegroundColor Green
    Write-Host "Per avviare runner e dashboard: .\Start-ForgeLab.ps1"
}
finally {
    Pop-Location
}
