# Render the deliberately small SVG vocabulary without a graphics dependency.
# RazerMacroUnlocker.svg is the source of truth; keep its shapes to filled rounded rects.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$assets = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../src/RazerMacroUnlocker/Assets'))
[xml]$source = Get-Content -LiteralPath (Join-Path $assets 'RazerMacroUnlocker.svg') -Raw
$rectangles = $source.SelectNodes("//*[local-name()='rect']")
$sizes = @(16, 20, 24, 32, 40, 48, 64, 128, 256)
$pngs = [Collections.Generic.List[byte[]]]::new()

foreach ($size in $sizes) {
    $bitmap = [Drawing.Bitmap]::new($size, $size, [Drawing.Imaging.PixelFormat]::Format32bppArgb)
    $graphics = [Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.PixelOffsetMode = [Drawing.Drawing2D.PixelOffsetMode]::HighQuality
    $graphics.Clear([Drawing.Color]::Transparent)
    $graphics.ScaleTransform($size / 256.0, $size / 256.0)
    foreach ($rectangle in $rectangles) {
        $x = [single]$rectangle.x
        $y = [single]$rectangle.y
        $width = [single]$rectangle.width
        $height = [single]$rectangle.height
        $diameter = [single]$rectangle.rx * 2
        $path = [Drawing.Drawing2D.GraphicsPath]::new()
        $path.AddArc($x, $y, $diameter, $diameter, 180, 90)
        $path.AddArc($x + $width - $diameter, $y, $diameter, $diameter, 270, 90)
        $path.AddArc($x + $width - $diameter, $y + $height - $diameter, $diameter, $diameter, 0, 90)
        $path.AddArc($x, $y + $height - $diameter, $diameter, $diameter, 90, 90)
        $path.CloseFigure()
        $brush = [Drawing.SolidBrush]::new([Drawing.ColorTranslator]::FromHtml($rectangle.fill))
        $graphics.FillPath($brush, $path)
        $brush.Dispose()
        $path.Dispose()
    }
    $stream = [IO.MemoryStream]::new()
    $bitmap.Save($stream, [Drawing.Imaging.ImageFormat]::Png)
    $pngs.Add($stream.ToArray())
    if ($size -eq 256) {
        $bitmap.Save((Join-Path $assets 'RazerMacroUnlocker.png'), [Drawing.Imaging.ImageFormat]::Png)
    }
    $stream.Dispose()
    $graphics.Dispose()
    $bitmap.Dispose()
}

$output = [IO.File]::Create((Join-Path $assets 'RazerMacroUnlocker.ico'))
$writer = [IO.BinaryWriter]::new($output)
try {
    $writer.Write([uint16]0)
    $writer.Write([uint16]1)
    $writer.Write([uint16]$sizes.Count)
    $offset = 6 + 16 * $sizes.Count
    for ($i = 0; $i -lt $sizes.Count; $i++) {
        $dimension = if ($sizes[$i] -eq 256) { 0 } else { $sizes[$i] }
        $writer.Write([byte]$dimension)
        $writer.Write([byte]$dimension)
        $writer.Write([byte]0)
        $writer.Write([byte]0)
        $writer.Write([uint16]1)
        $writer.Write([uint16]32)
        $writer.Write([uint32]$pngs[$i].Length)
        $writer.Write([uint32]$offset)
        $offset += $pngs[$i].Length
    }
    foreach ($png in $pngs) { $writer.Write($png) }
}
finally { $writer.Dispose() }
Write-Host "Generated RazerMacroUnlocker.ico ($($sizes -join ', ') px) and RazerMacroUnlocker.png from SVG."
