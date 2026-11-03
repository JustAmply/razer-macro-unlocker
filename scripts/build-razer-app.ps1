param([switch]$SelfContained, [string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
& (Join-Path $PSScriptRoot 'setup-razer-app.ps1')
$selfContainedValue = $SelfContained.IsPresent.ToString().ToLowerInvariant()
$keyboardOutput = Join-Path $repo 'build/keyboard'
& $Python -m PyInstaller --clean --noconfirm --onefile --noconsole --name RazerMacroUnlocker.Keyboard --distpath $keyboardOutput --workpath (Join-Path $repo 'build/keyboard-work') --specpath (Join-Path $repo 'build') --exclude-module ssl --exclude-module _ssl --exclude-module hashlib --exclude-module _hashlib (Join-Path $repo 'razer_unlocker.pyw')
if ($LASTEXITCODE -ne 0) { throw 'Keyboard helper build failed. Install PyInstaller 6.22.3 for the selected Python interpreter.' }
& $Python (Join-Path $repo 'scripts/smoke_exe.py') (Join-Path $keyboardOutput 'RazerMacroUnlocker.Keyboard.exe')
if ($LASTEXITCODE -ne 0) { throw 'Keyboard helper smoke test failed.' }
dotnet publish (Join-Path $repo 'src/RazerMacroUnlocker.WinUI/RazerMacroUnlocker.WinUI.csproj') -c Release -r win-x64 --self-contained $selfContainedValue -o (Join-Path $repo 'dist/RazerMacroUnlocker')
if ($LASTEXITCODE -ne 0) { throw "RazerMacroUnlocker editor build failed ($LASTEXITCODE)." }
if (-not (Test-Path (Join-Path $repo 'dist/RazerMacroUnlocker/resources.pri'))) {
    throw 'The application XAML resource index is missing from the publish output.'
}
dotnet publish (Join-Path $repo 'src/RazerMacroUnlocker/RazerMacroUnlocker.csproj') -c Release -r win-x64 --self-contained $selfContainedValue -o (Join-Path $repo 'dist/RazerMacroUnlocker/runtime')
if ($LASTEXITCODE -ne 0) { throw "RazerMacroUnlocker host build failed ($LASTEXITCODE)." }
Copy-Item (Join-Path $keyboardOutput 'RazerMacroUnlocker.Keyboard.exe') (Join-Path $repo 'dist/RazerMacroUnlocker/runtime/RazerMacroUnlocker.Keyboard.exe') -Force
Write-Host "Ready: $repo\dist\RazerMacroUnlocker\RazerMacroUnlocker.exe"
