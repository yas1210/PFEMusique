@echo off
setlocal

set "PYTHON=%~dp0venv\Scripts\python.exe"
if not exist "%PYTHON%" (
  echo ERROR: Virtual environment Python not found at %PYTHON%
  echo Run this script from the project root, or activate your venv first.
  exit /b 1
)

echo Installing PyInstaller if needed...
"%PYTHON%" -m pip install --upgrade pyinstaller

echo Building MPipophone executable...
"%PYTHON%" -m PyInstaller --clean --noconfirm MPipophone.spec

if %ERRORLEVEL% neq 0 (
  echo ERROR: PyInstaller build failed.
  exit /b %ERRORLEVEL%
)

echo.
echo Build complete.
echo Executable produced at dist\MPipophone.exe
pause
