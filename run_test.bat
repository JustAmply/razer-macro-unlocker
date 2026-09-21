@echo off
setlocal
title Universal Razer Macro Key Unlocker - Live Test
set "SCRIPT_DIR=%~dp0"
set "EXE_PATH=%SCRIPT_DIR%RazerMacroUnlocker.exe"
set "DIST_EXE_PATH=%SCRIPT_DIR%dist\RazerMacroUnlocker.exe"

if exist "%EXE_PATH%" (
    "%EXE_PATH%" --test
) else if exist "%DIST_EXE_PATH%" (
    "%DIST_EXE_PATH%" --test
) else (
    echo [ERROR] RazerMacroUnlocker.exe not found!
    echo Please ensure RazerMacroUnlocker.exe is in this folder or in 'dist'.
)

echo.
pause
