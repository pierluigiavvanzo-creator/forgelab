$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path $PSScriptRoot -Parent
$DashboardRoot = Join-Path $ProjectRoot 'dashboard'
$source = Get-Content (Join-Path $ProjectRoot 'Start-ForgeLab.ps1') -Raw
$tokens = $null
$parseErrors = $null
$ast = [System.Management.Automation.Language.Parser]::ParseInput($source, [ref]$tokens, [ref]$parseErrors)
if ($parseErrors.Count) { throw 'Launcher syntax invalid' }
foreach ($definition in $ast.FindAll({ param($node) $node -is [System.Management.Automation.Language.FunctionDefinitionAst] }, $false)) {
    . ([scriptblock]::Create($definition.Extent.Text))
}

# Exercise the real functions with process operations replaced, never kill real processes.
function Get-ListenerProcess { param($Port) return $script:listener }
function Get-CimInstance { param($ClassName, $Filter, $ErrorAction) return $null }
function Start-Sleep { param($Seconds) }
function Stop-Process { param($Id, [switch]$Force, $ErrorAction) $script:stopped += $Id }
function taskkill.exe { $script:killed += ($args -join ' '); $global:LASTEXITCODE = 0 }
function Invoke-RestMethod { param($Uri, $TimeoutSec) return @{status='ok'; version='0.9.1'; runtime_sha='candidate'} }
$RuntimeRoot = $ProjectRoot
$script:record = '{}'
function Get-Content { param($Path, [switch]$Raw) return $script:record }

$failures = @()
foreach ($case in @(
    @{name='foreign Vite'; process=@{ProcessId=41001; Name='node.exe'; CommandLine='node C:\other\vite\bin\vite.js'; ExecutablePath='C:\node.exe'}},
    @{name='sibling-prefix workerd'; process=@{ProcessId=41002; ParentProcessId=41003; Name='workerd.exe'; CommandLine='workerd serve'; ExecutablePath=(Join-Path $DashboardRoot 'node_modules-other\workerd.exe')}},
    @{name='foreign API with matching health'; api=$true; process=@{ProcessId=41004; Name='python.exe'; CommandLine='python -m unrelated_api'; ExecutablePath='C:\python.exe'}}
)) {
    $script:listener = [pscustomobject]$case.process
    $script:stopped = @()
    $script:killed = @()
    $refused = $false
    try {
        if ($case.api) { Stop-ForgeLabApi -Port 8765 }
        else { Stop-ForgeLabDashboardPort -Port 5173 }
    } catch { $refused = $true }
    if (-not $refused -or $script:stopped.Count -or $script:killed.Count) {
        $failures += "$($case.name): unverified process was not preserved"
    } else { Write-Output "PASS: $($case.name) preserved" }
}

# Verify persisted ownership permits restart, but a reused PID does not.
$script:creationDate = [datetime]'2026-10-08T10:00:00Z'
$script:record = @{api_pid=41005; api_start_time=$script:creationDate.ToUniversalTime().ToString('o')} | ConvertTo-Json
function Get-CimInstance {
    param($ClassName, $Filter, $ErrorAction)
    return [pscustomobject]@{ProcessId=41005; CreationDate=$script:creationDate}
}
$script:listener = [pscustomobject]@{ProcessId=41005; Name='python.exe'}
$script:killed = @()
Stop-ForgeLabApi -Port 8765
if (-not ($script:killed -match '/PID 41005 /T /F')) { $failures += 'registered API tree was not stopped' }
else { Write-Output 'PASS: registered API tree stopped' }
$script:creationDate = $script:creationDate.AddSeconds(1)
$script:killed = @()
$refused = $false
try { Stop-ForgeLabApi -Port 8765 } catch { $refused = $true }
if (-not $refused -or $script:killed.Count) { $failures += 'reused API PID was not preserved' }
else { Write-Output 'PASS: reused API PID preserved' }

# Run the actual startup/readiness/stability statements with a deterministic outage.
$runtimeStart = $source.IndexOf('# BEGIN OWNED RUNTIME')
$runtimeEnd = $source.IndexOf('# OPEN AUTHENTICATED DASHBOARD')
$runtimeScript = [scriptblock]::Create($source.Substring($runtimeStart, $runtimeEnd - $runtimeStart))
$ApiPort = 8765
$DashboardPort = 5173
$ApiBase = 'http://127.0.0.1:8765'
$DashboardOrigin = 'http://127.0.0.1:5173'
$RuntimeSha = 'candidate'
$PythonExe = 'python.exe'
$NodeExe = 'node.exe'
$ApiStdOut = $ApiStdErr = $DashboardStdOut = $DashboardStdErr = 'unused-test-log'
$script:started = 0
$script:requests = 0
$script:stopped = @()
$script:killed = @()
function Start-Process {
    param($WindowStyle, $FilePath, $ArgumentList, $WorkingDirectory, $RedirectStandardOutput, $RedirectStandardError, [switch]$PassThru)
    $script:started++
    return [pscustomobject]@{Id=(42000 + $script:started)}
}
function Invoke-WebRequest {
    param($Uri, [switch]$UseBasicParsing, $TimeoutSec)
    $script:requests++
    if ($script:requests -gt 1) { throw 'simulated stability failure' }
    return @{StatusCode=200}
}
$failed = $false
try { & $runtimeScript } catch { $failed = $_.Exception.Message -match 'instabile' }
if (-not $failed -or -not ($script:killed -match '/PID 42001 /T /F') -or -not ($script:killed -match '/PID 42002 /T /F')) {
    $failures += 'stability failure: both owned process trees must be cleaned'
} else { Write-Output 'PASS: failed startup cleans both process trees' }
$script:started = 0
$script:killed = @()
function Start-Process {
    param($WindowStyle, $FilePath, $ArgumentList, $WorkingDirectory, $RedirectStandardOutput, $RedirectStandardError, [switch]$PassThru)
    $script:started++
    if ($script:started -eq 2) { throw 'simulated dashboard launch failure' }
    return [pscustomobject]@{Id=42001}
}
$failed = $false
try { & $runtimeScript } catch { $failed = $_.Exception.Message -match 'simulated dashboard launch failure' }
if (-not $failed -or $script:killed.Count -ne 1 -or -not ($script:killed -match '/PID 42001 /T /F')) {
    $failures += 'partial startup: the API tree must be cleaned'
} else { Write-Output 'PASS: partial startup cleans the API tree' }
if ($failures.Count) { throw ($failures -join "`n") }
Write-Output 'PASS: launcher lifecycle regressions'
