@echo off
setlocal
echo =======================================================
echo   Razer BlackWidow Chroma V2 - Autostart Installation
echo =======================================================

set "SCRIPT_DIR=%~dp0"
set "VBS_PATH=%SCRIPT_DIR%razer_unlocker_launcher.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\RazerUnlocker.lnk"

echo Creating autostart shortcut in:
echo %SHORTCUT_PATH%
echo.

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_PATH%\"'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"

if exist "%SHORTCUT_PATH%" (
    echo [OK] Autostart successfully configured!
    echo.
    echo Starting background service silently...
    start "" wscript.exe "%VBS_PATH%"
    echo [OK] Service is now running silently in the background.
) else (
    echo [ERROR] Failed to create autostart shortcut.
)

echo.
pause
