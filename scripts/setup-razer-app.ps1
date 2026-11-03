$ErrorActionPreference = 'Stop'
$destination = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../vendor/VirtualDesktopAccessor'))
New-Item -ItemType Directory -Force $destination | Out-Null
$dll = Join-Path $destination 'VirtualDesktopAccessor.dll'
$expectedHash = '8740C572A1C000E3B87FFEB1E4C397EAE9AF3BD4A2ABDC3BCFFACAB4493F8FF5'
if ((Test-Path -LiteralPath $dll) -and (Get-FileHash -LiteralPath $dll -Algorithm SHA256).Hash -eq $expectedHash) {
    Write-Host 'VirtualDesktopAccessor already verified.'
    return
}
$temporary = "$dll.download"
try {
    Invoke-WebRequest 'https://github.com/Ciantic/VirtualDesktopAccessor/releases/download/2024-12-16-windows11/VirtualDesktopAccessor.dll' -OutFile $temporary
    if ((Get-FileHash -LiteralPath $temporary -Algorithm SHA256).Hash -ne $expectedHash) {
        throw 'VirtualDesktopAccessor checksum mismatch; existing DLL was not replaced.'
    }
    Move-Item -LiteralPath $temporary -Destination $dll -Force
}
finally {
    if (Test-Path -LiteralPath $temporary) { Remove-Item -LiteralPath $temporary }
}
Write-Host 'VirtualDesktopAccessor downloaded and verified.'
