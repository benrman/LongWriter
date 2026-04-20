Param(
    [string]$VenvPath = ".venv-graphic-novel-ai"
)

$ErrorActionPreference = "Stop"
$RootDir = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RootDir

Write-Host "==> Checking Python version (>=3.10)"
$VersionCheck = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
$Parts = $VersionCheck.Split(".")
if ([int]$Parts[0] -lt 3 -or ([int]$Parts[0] -eq 3 -and [int]$Parts[1] -lt 10)) {
    throw "Python 3.10 or newer is required."
}

if (-not (Test-Path $VenvPath)) {
    Write-Host "==> Creating virtual environment at $VenvPath"
    python -m venv $VenvPath
} else {
    Write-Host "==> Virtual environment already exists at $VenvPath"
}

$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (-not (Test-Path $ActivateScript)) {
    throw "Cannot find activation script at $ActivateScript"
}

Write-Host "==> Activating virtual environment"
. $ActivateScript

Write-Host "==> Upgrading pip"
python -m pip install --upgrade pip

Write-Host "==> Installing Python dependencies"
pip install -r requirements.txt

Write-Host "==> Checking Ollama availability"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Warning "Ollama is not installed. Install from https://ollama.com/download"
    Write-Host "Then run: ollama serve"
    Write-Host "And pull models:"
    Write-Host "  ollama pull llama3.1:8b-instruct-q4_K_M"
    Write-Host "  ollama pull qwen2.5:7b-instruct-q4_K_M"
} else {
    Write-Host "==> Pulling recommended local models for RTX 3070 profile"
    ollama pull llama3.1:8b-instruct-q4_K_M
    ollama pull qwen2.5:7b-instruct-q4_K_M
}

Write-Host ""
Write-Host "Installation complete."
Write-Host "CLI wizard: python -m graphic_novel_ai --interactive --profile rtx3070"
Write-Host "GUI:        python -m graphic_novel_ai.gui"
