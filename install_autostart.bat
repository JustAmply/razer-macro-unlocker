@echo off
setlocal
echo =======================================================
echo   Universal Razer Macro Key Unlocker - Autostart Setup
echo =======================================================

set "SCRIPT_DIR=%~dp0"
set "EXE_PATH=%SCRIPT_DIR%RazerMacroUnlocker.exe"
set "DIST_EXE_PATH=%SCRIPT_DIR%dist\RazerMacroUnlocker.exe"
set "VBS_PATH=%SCRIPT_DIR%razer_unlocker_launcher.vbs"
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SHORTCUT_PATH=%STARTUP_FOLDER%\RazerUnlocker.lnk"

echo Creating autostart shortcut in:
echo %SHORTCUT_PATH%
echo.

if exist "%EXE_PATH%" (
    echo [INFO] Detected standalone executable: RazerMacroUnlocker.exe
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"
    set "RUN_TARGET=%EXE_PATH%"
    set "RUN_TYPE=EXE"
) else if exist "%DIST_EXE_PATH%" (
    echo [INFO] Detected built executable: dist\RazerMacroUnlocker.exe
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = '%DIST_EXE_PATH%'; $s.WorkingDirectory = '%SCRIPT_DIR%dist'; $s.Save()"
    set "RUN_TARGET=%DIST_EXE_PATH%"
    set "RUN_TYPE=EXE"
) else if exist "%VBS_PATH%" (
    echo [INFO] Detected Python script launcher: razer_unlocker_launcher.vbs
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT_PATH%'); $s.TargetPath = 'wscript.exe'; $s.Arguments = '\"%VBS_PATH%\"'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Save()"
    set "RUN_TARGET=%VBS_PATH%"
    set "RUN_TYPE=VBS"
) else (
    echo [ERROR] Neither RazerMacroUnlocker.exe nor razer_unlocker_launcher.vbs found!
    pause
    exit /b 1
)

if exist "%SHORTCUT_PATH%" (
    echo [OK] Autostart successfully configured!
    echo.
    echo Starting background service silently...
    if "%RUN_TYPE%"=="VBS" (
        start "" wscript.exe "%RUN_TARGET%"
    ) else (
        start "" "%RUN_TARGET%"
    )
    echo [OK] Service is now running silently in the background.
) else (
    echo [ERROR] Failed to create autostart shortcut.
)

echo.
pause
