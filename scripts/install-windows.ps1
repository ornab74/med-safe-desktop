Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$AppDir = if ($env:APP_DIR) { $env:APP_DIR } else { Join-Path $HOME "med-safe-desktop" }
$VenvDir = Join-Path $AppDir "venv"
$RepoUrl = if ($env:REPO_URL) { $env:REPO_URL } else { "https://github.com/ornab74/humoid-gui-gemma-4.git" }

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "Git is required. Install Git for Windows first."
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python Launcher is required. Install Python 3.11+ first."
}

Write-Host "Cloning or updating repository..."
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null

if (Test-Path (Join-Path $AppDir ".git")) {
    git -C $AppDir pull --ff-only
} else {
    git clone $RepoUrl $AppDir
}

Write-Host "Creating Python virtual environment..."
py -3 -m venv $VenvDir

$PythonExe = Join-Path $VenvDir "Scripts\python.exe"

Write-Host "Installing Python dependencies..."
& $PythonExe -m pip install --upgrade pip

$RequirementsTxt = Join-Path $AppDir "requirements.txt"
$RequirementsIn = Join-Path $AppDir "requirements.in"

if (Test-Path $RequirementsTxt) {
    & $PythonExe -m pip install -r $RequirementsTxt
} elseif (Test-Path $RequirementsIn) {
    & $PythonExe -m pip install -r $RequirementsIn
} else {
    Write-Host "No requirements file found in $AppDir"
}

Write-Host ""
Write-Host "Windows setup complete."
Write-Host ""
Write-Host "To run it manually:"
Write-Host "cd `"$AppDir`""
Write-Host ".\venv\Scripts\Activate.ps1"
Write-Host "python -u main.py"
