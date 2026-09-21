@echo off
setlocal
echo =======================================================
echo   Razer BlackWidow Chroma V2 - Autostart Installation
echo =======================================================

set "SCRIPT_DIR=%~dp0"
set "VBS_PATH=%SCRIPT_DIR%razer_unlocker_launcher.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\RazerUnlocker.lnk"

echo Erstelle Autostart-Verknuepfung in:
echo %SHORTCUT_PATH%
echo.

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_PATH%\"'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo [OK] Autostart erfolgreich eingerichtet!
    echo.
    echo Starte den Hintergrunddienst jetzt geraeuschlos...
    start "" wscript.exe "%VBS_PATH%"
    echo [OK] Dienst laeuft ab sofort unsichtbar im Hintergrund.
) else (
    echo [FEHLER] Verknuepfung konnte nicht erstellt werden.
)

echo.
pause
