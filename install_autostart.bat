@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
set "EXE_PATH=%SCRIPT_DIR%RazerMacroUnlocker.exe"
set "DIST_EXE_PATH=%SCRIPT_DIR%dist\RazerMacroUnlocker.exe"
set "PY_SCRIPT=%SCRIPT_DIR%razer_unlocker.pyw"

if exist "%EXE_PATH%" (
    "%EXE_PATH%" --install
) else if exist "%DIST_EXE_PATH%" (
    "%DIST_EXE_PATH%" --install
) else if exist "%PY_SCRIPT%" (
    python "%PY_SCRIPT%" --install
) else (
    echo [ERROR] Neither RazerMacroUnlocker.exe nor razer_unlocker.pyw found!
)

echo.
pause
