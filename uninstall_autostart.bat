@echo off
setlocal
echo =======================================================
echo   Universal Razer Macro Key Unlocker - Autostart Removal
echo =======================================================

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\RazerUnlocker.lnk"

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo [OK] Autostart shortcut removed.
) else (
    echo [INFO] No autostart shortcut found.
)

echo Terminating running background services...
taskkill /F /IM RazerMacroUnlocker.exe >nul 2>&1
powershell -Command "Get-CimInstance Win32_Process | Where-Object CommandLine -like '*razer_unlocker.pyw*' | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" 2>nul

echo.
echo Uninstallation completed.
pause
