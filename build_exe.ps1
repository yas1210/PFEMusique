$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $scriptRoot 'venv\Scripts\python.exe'
if (-not (Test-Path $python)) {
    throw "Python executable not found at $python. Run this script from the project root or activate the venv."
}

Write-Host "Installing PyInstaller if needed..."
& $python -m pip install --upgrade pyinstaller

Write-Host "Building MPipophone executable..."
& $python -m PyInstaller --clean --noconfirm MPipophone.spec

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed with exit code $LASTEXITCODE"
}

Write-Host "Build complete. Executable produced at dist\MPipophone.exe"
