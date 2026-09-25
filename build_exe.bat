@echo off
setlocal enabledelayedexpansion

echo =======================================================
echo   Razer Macro Unlocker - Standalone Executable Build
echo =======================================================
echo.

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM Do not terminate or overwrite a running service during a build.
powershell -NoProfile -Command "if (Get-Process -Name 'RazerMacroUnlocker' -ErrorAction SilentlyContinue) { exit 1 }"
if %ERRORLEVEL% neq 0 (
    echo [ERROR] RazerMacroUnlocker.exe is running. Close it before rebuilding.
    exit /b 1
)

set "BUILD_EXIT_CODE=0"
set "BUILD_PYTHON=.venv\Scripts\python.exe"

REM Reuse the project's virtual environment when it exists.
if exist "%BUILD_PYTHON%" (
    "%BUILD_PYTHON%" -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))" >nul 2>&1
    if !ERRORLEVEL! equ 0 goto python_build
    echo [ERROR] Existing .venv does not use Python 3.14.
    exit /b 1
)

REM Check for uv first
where uv >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo [INFO] Found uv package manager. Building with uv and PyInstaller...
    uv run --Python 3.14 --with pyinstaller==6.22.3 python -m PyInstaller --onefile --noconsole --clean --name RazerMacroUnlocker --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib razer_unlocker.pyw
    set "BUILD_EXIT_CODE=!ERRORLEVEL!"
    goto check_result
)

REM Check for python and create an isolated build environment.
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Neither 'uv' nor 'python' was found in PATH!
    echo Please install Python or uv to build the executable locally.
    pause
    exit /b 1
)

python -c "import sys; sys.exit(sys.version_info[:2] != (3, 14))" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python 3.14 is required to build the executable.
    exit /b 1
)

echo [INFO] Creating local Python 3.14 environment...
python -m venv .venv
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to create .venv.
    pause
    exit /b 1
)

:python_build
echo [INFO] Checking PyInstaller in Python environment...
"%BUILD_PYTHON%" -c "import PyInstaller, sys; sys.exit(PyInstaller.__version__ != '6.22.3')" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] PyInstaller not found. Installing via pip...
    "%BUILD_PYTHON%" -m pip install pyinstaller==6.22.3
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install PyInstaller via pip.
        pause
        exit /b 1
    )
)

echo [INFO] Building standalone executable...
"%BUILD_PYTHON%" -m PyInstaller --onefile --noconsole --clean --name RazerMacroUnlocker --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib razer_unlocker.pyw
set "BUILD_EXIT_CODE=!ERRORLEVEL!"

:check_result
if !BUILD_EXIT_CODE! equ 0 if not exist "dist\RazerMacroUnlocker.exe" set "BUILD_EXIT_CODE=1"
if !BUILD_EXIT_CODE! equ 0 (
    echo.
    echo =======================================================
    echo   [OK] Build successful!
    echo   Executable located at:
    echo   %SCRIPT_DIR%dist\RazerMacroUnlocker.exe
    echo =======================================================
) else (
    echo.
    echo =======================================================
    echo   [ERROR] Build failed with exit code !BUILD_EXIT_CODE!!
    echo   Check the output above for details.
    echo =======================================================
)

echo.
pause
exit /b !BUILD_EXIT_CODE!

