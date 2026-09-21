@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   Razer Macro Unlocker - Standalone Executable Build
echo =======================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Check for uv first
where uv >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Found uv package manager. Building with uv and PyInstaller...
    uv run --with pyinstaller pyinstaller --onefile --noconsole --clean --name RazerMacroUnlocker razer_unlocker.pyw
    goto check_result
)

REM Check for python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Neither 'uv' nor 'python' was found in PATH!
    echo Please install Python or uv to build the executable locally.
    pause
    exit /b 1
)

echo [INFO] Checking PyInstaller in Python environment...
python -m PyInstaller --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] PyInstaller not found. Installing via pip...
    python -m pip install --upgrade pyinstaller
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install PyInstaller via pip.
        pause
        exit /b 1
    )
)

echo [INFO] Building standalone executable...
python -m PyInstaller --onefile --noconsole --clean --name RazerMacroUnlocker razer_unlocker.pyw

:check_result
if exist "dist\RazerMacroUnlocker.exe" (
    echo.
    echo =======================================================
    echo   [OK] Build successful!
    echo   Executable located at:
    echo   %SCRIPT_DIR%dist\RazerMacroUnlocker.exe
    echo =======================================================
) else (
    echo.
    echo [ERROR] Build failed! Check the output above for details.
)

echo.
pause
