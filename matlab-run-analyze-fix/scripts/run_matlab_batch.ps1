param(
    [Parameter(Mandatory = $true)]
    [string]$WorkDir,

    [Parameter(Mandatory = $true)]
    [string]$Command,

    [string]$OutputDir,

    [switch]$SaveFigures
)

function Initialize-OutputDir {
    param(
        [string]$WorkDir,
        [string]$RequestedOutputDir
    )

    $rootDir = Join-Path $WorkDir 'output\matlab-runs'
    $latestDir = Join-Path $rootDir 'latest'
    $resultsDir = Join-Path $rootDir 'results'

    if ([string]::IsNullOrWhiteSpace($RequestedOutputDir)) {
        $RequestedOutputDir = $latestDir
    }

    $resolved = [System.IO.Path]::GetFullPath($RequestedOutputDir)
    $resolvedLatest = [System.IO.Path]::GetFullPath($latestDir)

    New-Item -ItemType Directory -Force -Path $rootDir | Out-Null
    New-Item -ItemType Directory -Force -Path $resultsDir | Out-Null

    if ($resolved -eq $resolvedLatest) {
        $hasExisting = (Test-Path $resolvedLatest) -and ((Get-ChildItem -Path $resolvedLatest -Force -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0)
        if ($hasExisting) {
            $dateFolder = Get-Date -Format 'MMdd'
            $timeFolder = Get-Date -Format 'HHmmss'
            $archiveDir = Join-Path (Join-Path $resultsDir $dateFolder) $timeFolder
            New-Item -ItemType Directory -Force -Path $archiveDir | Out-Null

            Get-ChildItem -Path $resolvedLatest -Force | ForEach-Object {
                Move-Item -Path $_.FullName -Destination (Join-Path $archiveDir $_.Name) -Force
            }
        }

        New-Item -ItemType Directory -Force -Path $resolvedLatest | Out-Null
        return $resolvedLatest
    }

    New-Item -ItemType Directory -Force -Path $resolved | Out-Null
    return $resolved
}

$matlabCmd = Get-Command matlab -ErrorAction SilentlyContinue
if (-not $matlabCmd) {
    throw 'MATLAB executable not found in PATH.'
}

if (-not (Test-Path $WorkDir)) {
    throw "WorkDir does not exist: $WorkDir"
}

$OutputDir = Initialize-OutputDir -WorkDir $WorkDir -RequestedOutputDir $OutputDir

$prefDir = Join-Path $WorkDir '.matlab_prefs'
New-Item -ItemType Directory -Force -Path $prefDir | Out-Null
$env:MATLAB_PREFDIR = $prefDir

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$scriptDirMatlab = ($scriptDir -replace '\\','/')
$workDirMatlab = ($WorkDir -replace '\\','/')
$outputDirMatlab = ($OutputDir -replace '\\','/')
$logPath = Join-Path $OutputDir 'matlab_output.log'

if ($SaveFigures) {
    $batch = "cd('$workDirMatlab'); addpath('$scriptDirMatlab'); try; ${Command}; save_open_figures('$outputDirMatlab'); catch ME; disp(getReport(ME,'extended')); exit(1); end; exit(0);"
} else {
    $batch = "cd('$workDirMatlab'); try; ${Command}; catch ME; disp(getReport(ME,'extended')); exit(1); end; exit(0);"
}

& $matlabCmd.Source -batch $batch 2>&1 | Tee-Object -FilePath $logPath
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    exit $exitCode
}

Write-Output "OutputDir=$OutputDir"
Write-Output "LogPath=$logPath"

