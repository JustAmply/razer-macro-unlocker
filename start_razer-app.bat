@echo off
cd /d "%~dp0"
if not exist "dist\RazerMacroUnlocker\RazerMacroUnlocker.exe" (
    echo Build RazerMacroUnlocker first: powershell -File scripts\build-razer-app.ps1
    pause
    exit /b 1
)
start "" "dist\RazerMacroUnlocker\RazerMacroUnlocker.exe"
