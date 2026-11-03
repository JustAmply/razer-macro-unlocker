param([switch]$SelfContained)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
& (Join-Path $PSScriptRoot 'setup-razer-app.ps1')
$selfContainedValue = $SelfContained.IsPresent.ToString().ToLowerInvariant()
dotnet publish (Join-Path $repo 'src/RazerMacroUnlocker.WinUI/RazerMacroUnlocker.WinUI.csproj') -c Release -r win-x64 --self-contained $selfContainedValue -o (Join-Path $repo 'dist/RazerMacroUnlocker')
if ($LASTEXITCODE -ne 0) { throw "RazerMacroUnlocker editor build failed ($LASTEXITCODE)." }
if (-not (Test-Path (Join-Path $repo 'dist/RazerMacroUnlocker/resources.pri'))) {
    throw 'The application XAML resource index is missing from the publish output.'
}
dotnet publish (Join-Path $repo 'src/RazerMacroUnlocker/RazerMacroUnlocker.csproj') -c Release -r win-x64 --self-contained $selfContainedValue -o (Join-Path $repo 'dist/RazerMacroUnlocker/runtime')
if ($LASTEXITCODE -ne 0) { throw "RazerMacroUnlocker host build failed ($LASTEXITCODE)." }
Write-Host "Ready: $repo\dist\RazerMacroUnlocker\RazerMacroUnlocker.exe"
