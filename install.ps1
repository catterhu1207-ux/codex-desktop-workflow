[CmdletBinding()]
param(
    [string]$Source,
    [string]$Target,
    [string]$InstallRoot = (Join-Path $env:LOCALAPPDATA "CodexDesktopWorkflow"),
    [string]$BundlePath,
    [string]$Version,
    [switch]$NoVerify,
    [switch]$Launch,
    [switch]$MigrateData,
    [switch]$NoShortcut,
    [switch]$InstallPython,
    [switch]$DryRun,
    [int]$ObserveSeconds = 60,
    [int]$Launches = 2
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$Repository = "catterhu1207-ux/codex-desktop-workflow"
$BundleAsset = "codex-desktop-workflow-bundle.zip"
$SumsAsset = "SHA256SUMS.txt"
$ExitPrerequisite = 2
$ExitBuild = 3
$ExitMigration = 4
$ExitDownload = 5

function Write-Step([string]$Message) {
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok([string]$Message) {
    Write-Host "OK  $Message" -ForegroundColor Green
}

function Write-Warn([string]$Message) {
    Write-Host "!!  $Message" -ForegroundColor Yellow
}

function Stop-WithCode([string]$Message, [int]$Code) {
    Write-Host "ERROR $Message" -ForegroundColor Red
    exit $Code
}

function Get-Sha256([string]$Path) {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()
}

function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE`: $Executable $($Arguments -join ' ')"
    }
}

function Resolve-Python {
    $candidates = @(
        @("py", "-3"),
        @("python"),
        @("python3"),
        @((Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe")),
        @((Join-Path $env:LOCALAPPDATA "Programs\Python\Python311\python.exe"))
    )
    foreach ($candidate in $candidates) {
        try {
            $command = $candidate[0]
            [string[]]$arguments = @()
            if ($candidate.Count -gt 1) {
                $arguments += $candidate[1..($candidate.Count - 1)]
            }
            [string[]]$probe = $arguments
            $probe += @("-c", "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)")
            & $command @probe *> $null
            if ($LASTEXITCODE -eq 0) {
                return $candidate
            }
        }
        catch {
            continue
        }
    }
    return $null
}

function Get-ReleaseRoot([string]$ResolvedVersion) {
    if ($ResolvedVersion -eq "latest") {
        return "https://github.com/$Repository/releases/latest/download"
    }
    return "https://github.com/$Repository/releases/download/$ResolvedVersion"
}

function Get-Bundle([string]$ResolvedVersion) {
    if ($BundlePath) {
        $resolved = (Resolve-Path -LiteralPath $BundlePath).Path
        if ((Get-Item -LiteralPath $resolved).PSIsContainer) {
            return $resolved
        }
        $extractRoot = Join-Path $InstallRoot "downloads\local"
        if (Test-Path -LiteralPath $extractRoot) {
            Remove-Item -LiteralPath $extractRoot -Recurse -Force
        }
        New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null
        Expand-Archive -LiteralPath $resolved -DestinationPath $extractRoot -Force
        return $extractRoot
    }

    $releaseRoot = Get-ReleaseRoot $ResolvedVersion
    $downloadRoot = Join-Path $InstallRoot ("downloads\" + $ResolvedVersion.Replace("/", "_"))
    if (Test-Path -LiteralPath $downloadRoot) {
        Remove-Item -LiteralPath $downloadRoot -Recurse -Force
    }
    New-Item -ItemType Directory -Path $downloadRoot -Force | Out-Null
    $bundleZip = Join-Path $downloadRoot $BundleAsset
    $sumsFile = Join-Path $downloadRoot $SumsAsset
    Write-Step "Downloading $BundleAsset"
    Invoke-WebRequest -Uri "$releaseRoot/$BundleAsset" -OutFile $bundleZip -UseBasicParsing
    Invoke-WebRequest -Uri "$releaseRoot/$SumsAsset" -OutFile $sumsFile -UseBasicParsing

    $expected = $null
    foreach ($line in Get-Content -LiteralPath $sumsFile) {
        if ($line -match "^\s*([0-9a-fA-F]{64})\s+[ *]?$([regex]::Escape($BundleAsset))\s*$") {
            $expected = $Matches[1].ToLowerInvariant()
            break
        }
    }
    if (-not $expected) {
        throw "$SumsAsset does not contain $BundleAsset"
    }
    $actual = Get-Sha256 $bundleZip
    if ($actual -ne $expected) {
        throw "Bundle SHA-256 mismatch: expected $expected, actual $actual"
    }
    Write-Ok "Bundle checksum verified"

    $extractRoot = Join-Path $downloadRoot "bundle"
    New-Item -ItemType Directory -Path $extractRoot -Force | Out-Null
    Expand-Archive -LiteralPath $bundleZip -DestinationPath $extractRoot -Force
    return $extractRoot
}

function Test-BundleContents([string]$BundleRoot) {
    $allowed = @(".whl", ".json", ".ps1", ".txt", ".md", "")
    $unexpected = @()
    foreach ($file in Get-ChildItem -LiteralPath $BundleRoot -Recurse -File) {
        $extension = $file.Extension.ToLowerInvariant()
        if ($allowed -notcontains $extension) {
            $unexpected += $file.FullName
        }
    }
    if ($unexpected.Count -gt 0) {
        throw "Bundle contains unexpected file types: $($unexpected -join ', ')"
    }
}

function Get-OfficialSource([string]$RequestedSource) {
    if ($RequestedSource) {
        $source = (Resolve-Path -LiteralPath $RequestedSource).Path
    }
    else {
        $package = Get-AppxPackage -Name "OpenAI.Codex" |
            Sort-Object Version -Descending |
            Select-Object -First 1
        if (-not $package) {
            throw "OpenAI.Codex is not installed for this Windows user"
        }
        $source = $package.InstallLocation
    }
    $app = if (Test-Path -LiteralPath (Join-Path $source "app\resources\app.asar")) {
        Join-Path $source "app"
    }
    else {
        $source
    }
    if (-not (Test-Path -LiteralPath (Join-Path $app "resources\app.asar"))) {
        throw "Official Codex app directory was not found below $source"
    }
    return (Resolve-Path -LiteralPath $app).Path
}

function Test-CodexProcesses {
    $names = @("ChatGPT", "codex")
    return @(Get-Process -Name $names -ErrorAction SilentlyContinue)
}

Write-Host "codex-desktop-workflow installer" -ForegroundColor White
Write-Host "This tool creates an independent workflow copy. It never modifies the official app."

if ($env:OS -ne "Windows_NT") {
    Stop-WithCode "Windows is required." $ExitPrerequisite
}

try {
    $python = Resolve-Python
    if (-not $python) {
        if ($InstallPython) {
            if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
                Stop-WithCode "Python 3.10+ is missing and winget is unavailable." $ExitPrerequisite
            }
            Write-Step "Installing Python 3.12 with winget"
            Invoke-Checked "winget" @(
                "install", "--id", "Python.Python.3.12", "-e",
                "--scope", "user",
                "--accept-package-agreements",
                "--accept-source-agreements"
            )
            $python = Resolve-Python
        }
        if (-not $python) {
            Stop-WithCode "Python 3.10+ is required. Re-run with -InstallPython or install it from python.org." $ExitPrerequisite
        }
    }

    $resolvedVersion = if ($Version) {
        $Version
    }
    elseif ($BundlePath) {
        "local"
    }
    else {
        "latest"
    }
    Write-Step "Resolving release $resolvedVersion"
    $bundleRoot = Get-Bundle $resolvedVersion
    Test-BundleContents $bundleRoot
    $versionFile = Join-Path $bundleRoot "version.json"
    if (-not (Test-Path -LiteralPath $versionFile)) {
        throw "Bundle is missing version.json"
    }
    $versionInfo = Get-Content -LiteralPath $versionFile -Raw | ConvertFrom-Json
    $packageName = if ($versionInfo.package) { [string]$versionInfo.package } else { "codex-desktop-workflow" }
    $packageVersion = if ($versionInfo.version) { [string]$versionInfo.version } else { "0.2.1" }
    Write-Ok "Bundle prepared for $packageName $packageVersion"

    $officialSource = Get-OfficialSource $Source
    $sourceAsar = Join-Path $officialSource "resources\app.asar"
    $sourceHashBefore = Get-Sha256 $sourceAsar
    Write-Ok "Official source detected: $officialSource"

    if ($DryRun) {
        Write-Ok "Dry run complete. No files were built or installed."
        exit 0
    }

    $venvRoot = Join-Path $InstallRoot "venv"
    $venvPython = Join-Path $venvRoot "Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $venvPython)) {
        Write-Step "Creating isolated Python environment"
        New-Item -ItemType Directory -Path $InstallRoot -Force | Out-Null
        $command = $python[0]
        [string[]]$arguments = @()
        if ($python.Count -gt 1) {
            $arguments += $python[1..($python.Count - 1)]
        }
        $arguments += @("-m", "venv", $venvRoot)
        Invoke-Checked $command $arguments
    }

    Write-Step "Installing dependencies from the verified bundle"
    Invoke-Checked $venvPython @(
        "-m", "pip", "install",
        "--no-index",
        "--find-links", $bundleRoot,
        "electron-update-safety",
        "desktop-adaptation-lab"
    )
    Write-Step "Installing package from the verified bundle"
    Invoke-Checked $venvPython @(
        "-m", "pip", "install",
        "--no-index",
        "--find-links", $bundleRoot,
        "--no-deps",
        "$packageName==$packageVersion"
    )

    $artifactRoot = Join-Path $InstallRoot "artifacts\$packageVersion"
    $resolvedTarget = if ($Target) { $Target } else { Join-Path $artifactRoot "app" }
    if (Test-Path -LiteralPath $resolvedTarget) {
        Stop-WithCode "Target already exists: $resolvedTarget. Choose a new -Target or remove it explicitly." $ExitBuild
    }

    Write-Step "Inspecting the official package"
    Invoke-Checked $venvPython @(
        "-m", "codex_desktop_workflow.cli", "inspect",
        "--source", $officialSource
    )
    Write-Step "Building an independent copy"
    Invoke-Checked $venvPython @(
        "-m", "codex_desktop_workflow.cli", "build",
        "--source", $officialSource,
        "--target", $resolvedTarget
    )

    if (-not $NoVerify) {
        Write-Step "Verifying two isolated launches (about two minutes)"
        Invoke-Checked $venvPython @(
            "-m", "codex_desktop_workflow.cli", "verify",
            "--source", $officialSource,
            "--portable", $resolvedTarget,
            "--runs-root", (Join-Path $InstallRoot "verification"),
            "--observe-seconds", [string]$ObserveSeconds,
            "--launches", [string]$Launches
        )
    }

    $sourceHashAfter = Get-Sha256 $sourceAsar
    if ($sourceHashBefore -ne $sourceHashAfter) {
        Stop-WithCode "The official app.asar changed during installation. Stop and inspect the machine." $ExitBuild
    }
    Write-Ok "Official app.asar remained unchanged"

    $dataRoot = Join-Path $InstallRoot "data"
    if ($MigrateData) {
        if (Test-CodexProcesses) {
            Stop-WithCode "Close every ChatGPT/codex process before data migration." $ExitMigration
        }
        if (Test-Path -LiteralPath $dataRoot) {
            Stop-WithCode "Data target already exists: $dataRoot" $ExitMigration
        }
        $userCodex = Join-Path $env:USERPROFILE ".codex"
        if (-not (Test-Path -LiteralPath $userCodex)) {
            Stop-WithCode "No existing Codex data directory was found at $userCodex" $ExitMigration
        }
        Write-Step "Migrating a separate task-data copy"
        Invoke-Checked $venvPython @(
            "-m", "codex_desktop_workflow.cli", "import-data",
            "--source", $userCodex,
            "--target", $dataRoot
        )
    }
    if (-not (Test-Path -LiteralPath $dataRoot)) {
        New-Item -ItemType Directory -Path $dataRoot -Force | Out-Null
    }

    $launcher = Join-Path $InstallRoot "launch.cmd"
    $launcherContent = @"
@echo off
set "CODEX_DESKTOP_WORKFLOW_HOME=%~dp0"
"%~dp0venv\Scripts\python.exe" -m codex_desktop_workflow.cli launch --portable "$resolvedTarget" --data "$dataRoot" --runs-root "%~dp0runs" %*
"@
    [IO.File]::WriteAllText($launcher, $launcherContent, (New-Object Text.UTF8Encoding($false)))

    if (-not $NoShortcut) {
        $programs = [Environment]::GetFolderPath("Programs")
        $shortcutPath = Join-Path $programs "Codex Desktop Workflow.lnk"
        $shell = New-Object -ComObject WScript.Shell
        $shortcut = $shell.CreateShortcut($shortcutPath)
        $shortcut.TargetPath = $launcher
        $shortcut.WorkingDirectory = $InstallRoot
        $shortcut.Description = "Launch the independent Codex Desktop workflow copy"
        $shortcut.Save()
        Write-Ok "Start Menu shortcut created"
    }

    Write-Ok "Installation complete"
    Write-Host "Artifact: $resolvedTarget"
    Write-Host "Data:     $dataRoot"
    Write-Host "Launcher: $launcher"
    if (-not $MigrateData) {
        Write-Host "Next: close Codex, then run this installer again with -MigrateData to copy your existing task history."
    }
    if ($Launch) {
        Start-Process -FilePath $launcher
    }
    exit 0
}
catch {
    Stop-WithCode $_.Exception.Message $ExitBuild
}
