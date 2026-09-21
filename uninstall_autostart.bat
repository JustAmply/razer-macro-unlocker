@echo off
setlocal
echo =======================================================
echo   Razer BlackWidow Chroma V2 - Autostart Deinstallation
echo =======================================================

set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\RazerUnlocker.lnk"

if exist "%SHORTCUT_PATH%" (
    del "%SHORTCUT_PATH%"
    echo [OK] Autostart-Verknuepfung entfernt.
) else (
    echo [INFO] Keine Verknuepfung im Autostart gefunden.
)

echo Beende laufende Hintergrunddienste...
powershell -Command "Get-CimInstance Win32_Process | Where-Object CommandLine -like '*razer_unlocker.pyw*' | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }" 2>nul

echo.
echo Deinstallation abgeschlossen.
pause
