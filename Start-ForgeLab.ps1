param(
    [int]$ApiPort = 8765,
    [int]$DashboardPort = 5173
)

$ErrorActionPreference = "Stop"

$ProjectRoot  = $PSScriptRoot
$DashboardRoot = Join-Path $ProjectRoot "dashboard"
$RunsRoot       = Join-Path $ProjectRoot ".forgelab\runs"
$RuntimeRoot    = Join-Path $ProjectRoot ".forgelab\runtime"

$ApiBase         = "http://127.0.0.1:$ApiPort"
$DashboardOrigin = "http://127.0.0.1:$DashboardPort"

New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
New-Item -ItemType Directory -Path $RunsRoot -Force | Out-Null


function Get-ListenerProcess {
    param([int]$Port)

    $listener = Get-NetTCPConnection `
        -State Listen `
        -LocalPort $Port `
        -ErrorAction SilentlyContinue |
        Select-Object -First 1

    if (-not $listener) {
        return $null
    }

    return Get-CimInstance Win32_Process `
        -Filter "ProcessId=$($listener.OwningProcess)" `
        -ErrorAction SilentlyContinue
}


function Stop-ForgeLabDashboardPort {
    param([int]$Port)

    $proc = Get-ListenerProcess -Port $Port

    if (-not $proc) {
        return
    }

    $dashboardNodeModules = (Join-Path $DashboardRoot "node_modules") + [IO.Path]::DirectorySeparatorChar

    # Cloudflare workerd spawned by this ForgeLab dashboard
    if (
        $proc.Name -ieq "workerd.exe" -and
        $proc.ExecutablePath -and
        $proc.ExecutablePath.StartsWith(
            $dashboardNodeModules,
            [System.StringComparison]::OrdinalIgnoreCase
        )
    ) {
        $parent = Get-CimInstance Win32_Process `
            -Filter "ProcessId=$($proc.ParentProcessId)" `
            -ErrorAction SilentlyContinue

        if (
            $parent -and
            $parent.CommandLine -match "wrangler" -and
            $parent.CommandLine -match "dist[/\\]server[/\\]wrangler\.json"
        ) {
            $owner = Get-RecordedForgeLabProcess -Role "dashboard_launcher"
            if ($owner) { Stop-ForgeLabProcessTree -ProcessId $owner.ProcessId }
            else { Stop-ForgeLabProcessTree -ProcessId $parent.ProcessId }
        }
        else {
            Stop-ForgeLabProcessTree -ProcessId $proc.ProcessId
        }

        Start-Sleep -Seconds 1
        return
    }

    # Previous vinext/vite ForgeLab development runtime
    if (
        $proc.Name -match "^node(\.exe)?$" -and
        (Get-RecordedForgeLabProcess -Role "dashboard_launcher" -ExpectedId $proc.ProcessId)
    ) {
        Stop-ForgeLabProcessTree -ProcessId $proc.ProcessId
        Start-Sleep -Seconds 1
        return
    }

    throw "Porta $Port occupata da processo non identificato come ForgeLab: PID $($proc.ProcessId), $($proc.Name)"
}


function Stop-ForgeLabApi {
    param([int]$Port)

    $proc = Get-ListenerProcess -Port $Port

    if (-not $proc) {
        return
    }

    if (-not (Get-RecordedForgeLabProcess -Role "api" -ExpectedId $proc.ProcessId)) {
        throw "Porta API $Port occupata da processo non verificato come ForgeLab."
    }

    try {
        $health = Invoke-RestMethod `
            -Uri "http://127.0.0.1:$Port/health" `
            -TimeoutSec 2

        if (
            $health.status -eq "ok" -and
            $health.version -eq "0.9.1"
        ) {
            Stop-ForgeLabProcessTree -ProcessId $proc.ProcessId
            Start-Sleep -Seconds 1
            return
        }
    }
    catch {}

    throw "Porta API $Port occupata da processo non verificato come ForgeLab."
}


function Get-RecordedForgeLabProcess {
    param([string]$Role, [int]$ExpectedId = 0)

    # PID alone is insufficient: Windows can reuse it after the old runtime exits.
    try {
        $record = Get-Content (Join-Path $RuntimeRoot "runtime.json") -Raw | ConvertFrom-Json
        $recordedId = $record."${Role}_pid"
        $recordedStart = $record."${Role}_start_time"
        if (-not $recordedId -or -not $recordedStart) { return $null }
        if ($ExpectedId -and $recordedId -ne $ExpectedId) { return $null }
        $process = Get-CimInstance Win32_Process -Filter "ProcessId=$recordedId" -ErrorAction Stop
        if ($process -and $process.CreationDate.ToUniversalTime() -eq ([datetime]$recordedStart).ToUniversalTime()) {
            return $process
        }
    } catch {}
    return $null
}


function Stop-ForgeLabProcessTree {
    param([int]$ProcessId)
    & taskkill.exe /PID $ProcessId /T /F | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "Impossibile arrestare il process tree ForgeLab PID $ProcessId." }
}


Write-Host ""
Write-Host "Verifica ambiente..."

# ---------------------------------------------------------
# PYTHON
# ---------------------------------------------------------

$PythonExe = (& py -3.11 -c "import sys; print(sys.executable)").Trim()

if (-not $PythonExe -or -not (Test-Path $PythonExe)) {
    throw "Python 3.11 non disponibile."
}

$env:PYTHONPATH = Join-Path $ProjectRoot "src"

$RuntimeSha = (& git -C $ProjectRoot rev-parse HEAD).Trim()

if (-not $RuntimeSha) {
    throw "Impossibile determinare il Git SHA runtime ForgeLab."
}

$env:FORGELAB_RUNTIME_SHA = $RuntimeSha


# ---------------------------------------------------------
# NODE / COREPACK
# ---------------------------------------------------------

$NodeExe = (Get-Command node.exe -ErrorAction Stop).Source
$CorepackExe = (Get-Command corepack.cmd -ErrorAction Stop).Source

$NodeVersionText = (& $NodeExe -p "process.versions.node").Trim()
$NodeVersion = [version]$NodeVersionText

if (
    $NodeVersion.Major -lt 22 -or
    (
        $NodeVersion.Major -eq 22 -and
        $NodeVersion.Minor -lt 13
    )
) {
    throw "Node >= 22.13 richiesto. Versione: $NodeVersionText"
}

Write-Host "Python   : $PythonExe"
Write-Host "Node     : $NodeVersionText"
Write-Host "Corepack : $CorepackExe"
Write-Host "Runtime  : $RuntimeSha"


# ---------------------------------------------------------
# REUSE-FIRST LOCAL EDITOR TOOLCHAIN
# ---------------------------------------------------------

$AiderVersion = "0.86.2"
$ToolsRoot = Join-Path $ProjectRoot ".forgelab\tools"
$AiderRoot = Join-Path $ToolsRoot "aider-$AiderVersion"
$AiderPython = Join-Path $AiderRoot "Scripts\python.exe"
$AiderExe = Join-Path $AiderRoot "Scripts\aider.exe"

New-Item -ItemType Directory -Path $ToolsRoot -Force | Out-Null

if (-not (Test-Path $AiderExe)) {
    Write-Host ""
    Write-Host "REUSE-FIRST: preparo Aider $AiderVersion in ambiente locale isolato..."

    & $PythonExe -m venv $AiderRoot

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $AiderPython)) {
        throw "Creazione ambiente Aider fallita."
    }

    & $AiderPython -m pip install --disable-pip-version-check --no-input "aider-chat==$AiderVersion"

    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $AiderExe)) {
        throw "Installazione Aider $AiderVersion fallita."
    }
}

$AiderVersionText = (& $AiderExe --version 2>&1 | Out-String).Trim()

if ($LASTEXITCODE -ne 0 -or $AiderVersionText -notmatch "0\.86\.2") {
    throw "Aider locale non valido. Atteso $AiderVersion, ottenuto: $AiderVersionText"
}

Write-Host ""
Write-Host "Verifica contratto Aider..."

$AiderHelp = (& $AiderExe --help 2>&1 | Out-String)

if ($LASTEXITCODE -ne 0) {
    throw "Aider --help fallito durante il preflight."
}

$RequiredAiderFlags = @(
    "--model-metadata-file",
    "--timeout",
    "--map-tokens",
    "--no-git",
    "--no-gitignore",
    "--no-add-gitignore-files",
    "--no-auto-commits",
    "--no-dirty-commits",
    "--no-auto-lint",
    "--no-auto-test",
    "--no-watch-files",
    "--no-cache-prompts",
    "--no-restore-chat-history",
    "--no-suggest-shell-commands",
    "--no-notifications",
    "--no-detect-urls",
    "--no-pretty",
    "--no-stream",
    "--no-show-model-warnings",
    "--no-check-model-accepts-settings",
    "--analytics-disable",
    "--no-check-update",
    "--no-show-release-notes",
    "--chat-history-file",
    "--input-history-file"
)

foreach ($flag in $RequiredAiderFlags) {
    if ($AiderHelp -notmatch [regex]::Escape($flag)) {
        throw "Aider $AiderVersion non espone il flag richiesto: $flag"
    }
}

& $AiderPython -m pip check | Out-Host

if ($LASTEXITCODE -ne 0) {
    throw "Dipendenze Aider incoerenti: pip check fallito."
}

$AiderFreeze = Join-Path $RuntimeRoot "aider-freeze.txt"
$AiderFreezeText = (& $AiderPython -m pip freeze 2>&1 | Out-String)

if ($LASTEXITCODE -ne 0) {
    throw "Impossibile acquisire il fingerprint dipendenze Aider."
}

$AiderFreezeText | Set-Content $AiderFreeze -Encoding UTF8

$AiderFreezeSha256 = (
    Get-FileHash -Algorithm SHA256 -Path $AiderFreeze
).Hash.ToLowerInvariant()

$AiderGatePatterns = @(
    "test_editor_adapter.py",
    "test_orchestrator.py",
    "test_api.py",
    "test_dashboard_run_form_feedback.py"
)

foreach ($pattern in $AiderGatePatterns) {
    Write-Host "Aider gate: $pattern"

    & $PythonExe -m unittest discover -s (Join-Path $ProjectRoot "tests") -p $pattern -q

    if ($LASTEXITCODE -ne 0) {
        throw "Aider stabilization gate fallito: $pattern"
    }
}

Write-Host "[PASS] Aider stabilization gate"
& (Get-Process -Id $PID).Path -NoProfile -File (Join-Path $ProjectRoot "tests\test_launcher_lifecycle.ps1")
if ($LASTEXITCODE -ne 0) { throw "Launcher lifecycle gate fallito." }
$env:FORGELAB_AIDER_EXECUTABLE = $AiderExe
$env:FORGELAB_OLLAMA_URL = "http://127.0.0.1:11434"

Write-Host "Aider    : $AiderVersionText"
Write-Host "Editor   : REUSE-FIRST / Aider + Ollama locale"


# ---------------------------------------------------------
# CLEAN PREVIOUS FORGELAB RUNTIMES
# ---------------------------------------------------------

Write-Host ""
Write-Host "Pulizia runtime ForgeLab precedenti..."

Stop-ForgeLabDashboardPort -Port 8787
Stop-ForgeLabDashboardPort -Port $DashboardPort
Stop-ForgeLabApi -Port $ApiPort

if (
    Get-NetTCPConnection `
        -State Listen `
        -LocalPort 8787 `
        -ErrorAction SilentlyContinue
) {
    throw "Porta 8787 ancora occupata dopo cleanup."
}

Write-Host "[PASS] Runtime cleanup"


# ---------------------------------------------------------
# DASHBOARD DEPENDENCIES
# ---------------------------------------------------------

Write-Host ""
Write-Host "Verifica dipendenze dashboard..."

Push-Location $DashboardRoot

try {
    & $CorepackExe pnpm install --frozen-lockfile

    if ($LASTEXITCODE -ne 0) {
        throw "pnpm install fallito."
    }

    Write-Host ""
    Write-Host "Verifica lifecycle dashboard..."
    & $NodeExe scripts/test-run-lifecycle.mjs
    if ($LASTEXITCODE -ne 0) {
        throw "Dashboard lifecycle gate fallito."
    }

    Write-Host ""
    Write-Host "Build dashboard production..."

    & $CorepackExe pnpm run build

    if ($LASTEXITCODE -ne 0) {
        throw "Dashboard production build fallito."
    }
}
finally {
    Pop-Location
}

$WranglerConfig = Join-Path $DashboardRoot "dist\server\wrangler.json"

if (-not (Test-Path $WranglerConfig)) {
    throw "dist\server\wrangler.json non trovato."
}


# ---------------------------------------------------------
# ENSURE INITIAL RUN EXISTS
# ---------------------------------------------------------

$AnyRun = Get-ChildItem `
    $RunsRoot `
    -Filter "RunSummary.json" `
    -Recurse `
    -ErrorAction SilentlyContinue |
    Select-Object -First 1

if (-not $AnyRun) {
    & $PythonExe -m forgelab smoke --output $RunsRoot

    if ($LASTEXITCODE -ne 0) {
        throw "Creazione run iniziale fallita."
    }
}


# ---------------------------------------------------------
# TOKEN
# ---------------------------------------------------------

$bytes = New-Object byte[] 32
$rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()

try {
    $rng.GetBytes($bytes)
}
finally {
    $rng.Dispose()
}

$Token = (
    [System.BitConverter]::ToString($bytes)
).Replace("-", "").ToLowerInvariant()

$env:FORGELAB_API_TOKEN = $Token


# ---------------------------------------------------------
# LOG FILES
# ---------------------------------------------------------

$ApiStdOut = Join-Path $RuntimeRoot "api.stdout.log"
$ApiStdErr = Join-Path $RuntimeRoot "api.stderr.log"

$DashboardStdOut = Join-Path $RuntimeRoot "dashboard.stdout.log"
$DashboardStdErr = Join-Path $RuntimeRoot "dashboard.stderr.log"

Remove-Item `
    $ApiStdOut,
    $ApiStdErr,
    $DashboardStdOut,
    $DashboardStdErr `
    -Force `
    -ErrorAction SilentlyContinue


# ---------------------------------------------------------
# START API
# ---------------------------------------------------------

# BEGIN OWNED RUNTIME
$ApiProcess = $null
$DashboardProcess = $null
try {
$ApiArgs = @(
    "-m",
    "forgelab",
    "api",
    "--runs",
    ".forgelab/runs",
    "--port",
    "$ApiPort",
    "--allowed-origin",
    $DashboardOrigin
)

$ApiProcess = Start-Process `
    -WindowStyle Hidden `
    -FilePath $PythonExe `
    -ArgumentList $ApiArgs `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $ApiStdOut `
    -RedirectStandardError $ApiStdErr `
    -PassThru


# ---------------------------------------------------------
# START PRODUCTION DASHBOARD DIRECTLY
#
# IMPORTANT:
# NO pnpm argument separator.
# --port reaches Wrangler directly.
# ---------------------------------------------------------

$DashboardArgs = @(
    "--import",
    "./scripts/sites-env.mjs",
    "./node_modules/wrangler/bin/wrangler.js",
    "dev",
    "--config",
    "dist/server/wrangler.json",
    "--local",
    "--persist-to",
    ".wrangler/state",
    "--ip",
    "127.0.0.1",
    "--inspector-port",
    "0",
    "--port",
    "$DashboardPort"
)

$DashboardProcess = Start-Process `
    -WindowStyle Hidden `
    -FilePath $NodeExe `
    -ArgumentList $DashboardArgs `
    -WorkingDirectory $DashboardRoot `
    -RedirectStandardOutput $DashboardStdOut `
    -RedirectStandardError $DashboardStdErr `
    -PassThru


# Child processes already inherited the runtime settings.
$env:FORGELAB_API_TOKEN = $null
$env:FORGELAB_AIDER_EXECUTABLE = $null
$env:FORGELAB_RUNTIME_SHA = $null


# ---------------------------------------------------------
# API READINESS
# ---------------------------------------------------------

$ApiReady = $false

for ($i = 1; $i -le 60; $i++) {
    try {
        $health = Invoke-RestMethod `
            -Uri "$ApiBase/health" `
            -TimeoutSec 2

        if (
            $health.status -eq "ok" -and
            $health.version -eq "0.9.1"
        ) {
            $ApiReady = $true
            break
        }
    }
    catch {}

    Start-Sleep -Seconds 1
}

if (-not $ApiReady) {
    if (Test-Path $ApiStdErr) {
        Get-Content $ApiStdErr -Tail 100
    }

    throw "ForgeLab API non ha superato readiness."
}


# ---------------------------------------------------------
# DASHBOARD READINESS
# ---------------------------------------------------------

$DashboardReady = $false

for ($i = 1; $i -le 90; $i++) {

    try {
        $response = Invoke-WebRequest `
            -Uri $DashboardOrigin `
            -UseBasicParsing `
            -TimeoutSec 2

        if ($response.StatusCode -eq 200) {
            $DashboardReady = $true
            break
        }
    }
    catch {}

    Start-Sleep -Seconds 1
}

if (-not $DashboardReady) {

    Write-Host ""
    Write-Host "=== DASHBOARD STDOUT ==="

    if (Test-Path $DashboardStdOut) {
        Get-Content $DashboardStdOut -Tail 100
    }

    Write-Host ""
    Write-Host "=== DASHBOARD STDERR ==="

    if (Test-Path $DashboardStdErr) {
        Get-Content $DashboardStdErr -Tail 100
    }

    throw "ForgeLab production dashboard non ha superato readiness."
}


# ---------------------------------------------------------
# STABILITY WINDOW
# ---------------------------------------------------------

Write-Host ""
Write-Host "[PASS] Initial readiness."
Write-Host "Stability window: 30 secondi..."

for ($i = 1; $i -le 6; $i++) {

    Start-Sleep -Seconds 5

    try {
        $response = Invoke-WebRequest `
            -Uri $DashboardOrigin `
            -UseBasicParsing `
            -TimeoutSec 3

        if ($response.StatusCode -ne 200) {
            throw "HTTP non 200."
        }

        $health = Invoke-RestMethod `
            -Uri "$ApiBase/health" `
            -TimeoutSec 3

        if ($health.status -ne "ok") {
            throw "API non healthy."
        }
    }
    catch {
        throw "ForgeLab instabile durante stability window: $($_.Exception.Message)"
    }

    Write-Host "[PASS] Stability $i/6"
}


# ---------------------------------------------------------
# VERIFY PORT OWNERSHIP
# ---------------------------------------------------------

$Listener5173 = Get-NetTCPConnection `
    -State Listen `
    -LocalPort $DashboardPort `
    -ErrorAction Stop |
    Select-Object -First 1

$Listener8765 = Get-NetTCPConnection `
    -State Listen `
    -LocalPort $ApiPort `
    -ErrorAction Stop |
    Select-Object -First 1

$Unexpected8787 = Get-NetTCPConnection `
    -State Listen `
    -LocalPort 8787 `
    -ErrorAction SilentlyContinue

if ($Unexpected8787) {
    throw "Runtime errato: esiste ancora listener su 8787."
}


# ---------------------------------------------------------
# RUNTIME METADATA
# ---------------------------------------------------------

$Metadata = [ordered]@{
    version = "0.9.1"
    started_at = (Get-Date).ToString("o")
    api = $ApiBase
    dashboard = $DashboardOrigin
    api_pid = $Listener8765.OwningProcess
    api_start_time = (Get-CimInstance Win32_Process -Filter "ProcessId=$($ApiProcess.Id)").CreationDate.ToUniversalTime().ToString("o")
    dashboard_listener_pid = $Listener5173.OwningProcess
    dashboard_launcher_pid = $DashboardProcess.Id
    dashboard_launcher_start_time = (Get-CimInstance Win32_Process -Filter "ProcessId=$($DashboardProcess.Id)").CreationDate.ToUniversalTime().ToString("o")
    runtime_sha = $RuntimeSha
    mode = "production-local"
    aider_version = $AiderVersion
    aider_dependency_fingerprint = $AiderFreezeSha256
    aider_dependency_snapshot = $AiderFreeze
}

$Metadata |
    ConvertTo-Json |
    Set-Content `
        (Join-Path $RuntimeRoot "runtime.json") `
        -Encoding UTF8

} catch {
    # All startup failures, including stability/metadata failures, own the same cleanup.
    $startupFailure = $_
    foreach ($ownedProcess in @($DashboardProcess, $ApiProcess)) {
        if ($ownedProcess) {
            try { Stop-ForgeLabProcessTree -ProcessId $ownedProcess.Id }
            catch { Write-Warning $_.Exception.Message }
        }
    }
    throw $startupFailure
} finally {
    $env:FORGELAB_API_TOKEN = $null
    $env:FORGELAB_AIDER_EXECUTABLE = $null
    $env:FORGELAB_RUNTIME_SHA = $null
}


# ---------------------------------------------------------
# OPEN AUTHENTICATED DASHBOARD
# ---------------------------------------------------------

$Fragment =
    "api_base=$([Uri]::EscapeDataString($ApiBase))" +
    "&api_token=$([Uri]::EscapeDataString($Token))"

$DashboardUrl = "$DashboardOrigin/#$Fragment"

Start-Process $DashboardUrl


# ---------------------------------------------------------
# FINAL REPORT
# ---------------------------------------------------------

Write-Host ""
Write-Host "================================================"
Write-Host " FORGELAB v0.9.1 PRODUCTION LOCAL READY"
Write-Host "================================================"
Write-Host ""
Write-Host "API HEALTH       : PASS"
Write-Host "DASHBOARD HTTP   : 200"
Write-Host "API              : $ApiBase"
Write-Host "Dashboard        : $DashboardOrigin"
Write-Host "API PID          : $($Listener8765.OwningProcess)"
Write-Host "Dashboard PID    : $($Listener5173.OwningProcess)"
Write-Host "Port 8787        : FREE"
Write-Host ""
Write-Host "Dashboard stdout : $DashboardStdOut"
Write-Host "Dashboard stderr : $DashboardStdErr"
Write-Host ""
Write-Host "================================================"
