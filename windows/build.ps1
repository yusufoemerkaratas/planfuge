param(
    [string]$Version = "0.0.0-dev",
    [string]$TesseractDir = "C:\Program Files\Tesseract-OCR"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

if (-not (Test-Path "$TesseractDir\tesseract.exe")) {
    throw "Tesseract was not found at $TesseractDir"
}
foreach ($Language in @("eng", "deu")) {
    if (-not (Test-Path "$TesseractDir\tessdata\$Language.traineddata")) {
        throw "Tesseract language data is missing: $Language.traineddata"
    }
}

Write-Host "Building React frontend..."
Push-Location client
npm ci
npm run build
Pop-Location

Write-Host "Building self-contained PlanFuge application..."
$env:PLANFUGE_TESSERACT_DIR = $TesseractDir
python -m pip install --requirement requirements-windows.txt
python -m PyInstaller --noconfirm --clean windows/PlanFuge.spec

$IsccCandidates = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)
$Iscc = $IsccCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $Iscc) {
    throw "Inno Setup 6 was not found. Install it or run this build in GitHub Actions."
}

Write-Host "Building Windows installer..."
& $Iscc "/DMyAppVersion=$Version" "windows\installer.iss"

Write-Host "Installer created in dist\installer"
