@echo off
setlocal
echo ==========================================
echo   pynotify-auto Installer
echo ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python before running this installer.
    pause
    exit /b 1
)

echo [1/2] Installing package via pip...
python -m pip install .

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed.
    pause
    exit /b 1
)

echo [2/2] Finalizing configuration...
:: Modern pip installs wheels which often miss the .pth file in the root of site-packages.
:: This helper ensures the hook is active by manually copying the .pth if needed.
for /f "tokens=*" %%i in ('python -c "import site; print(site.getusersitepackages())"') do set "SITE_PACKAGES=%%i"

if not exist "%SITE_PACKAGES%" mkdir "%SITE_PACKAGES%"
copy /y "pynotify-auto.pth" "%SITE_PACKAGES%\" >nul

echo.
echo ==========================================
echo   SUCCESS: pynotify-auto is installed!
echo ==========================================
echo Every Python script you run will now notify 
echo you if it runs for more than 5 seconds.
echo.
echo Configuration:
echo - Default: Popup (includes sound)
echo - Change Mode: set PYNOTIFY_MODE=sound
echo.
pause
