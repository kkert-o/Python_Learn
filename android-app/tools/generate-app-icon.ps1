param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath
)

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Drawing

$sourceFullPath = [System.IO.Path]::GetFullPath($SourcePath)
if (-not (Test-Path -LiteralPath $sourceFullPath)) {
    throw "Icon source does not exist: $sourceFullPath"
}

$projectRoot = Split-Path -Parent $PSScriptRoot
$resourceRoot = Join-Path $projectRoot "app\src\main\res"
$designRoot = Join-Path $projectRoot "docs\design"
New-Item -ItemType Directory -Force -Path $designRoot | Out-Null

$code = @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;

public static class IconBackgroundRemover
{
    public static Bitmap RemoveConnectedWhite(string path, int threshold, out Rectangle bounds)
    {
        using (var source = new Bitmap(path))
        {
            int width = source.Width;
            int height = source.Height;
            var output = new Bitmap(width, height, PixelFormat.Format32bppArgb);
            using (var graphics = Graphics.FromImage(output))
            {
                graphics.DrawImage(source, new Rectangle(0, 0, width, height));
            }

            var rect = new Rectangle(0, 0, width, height);
            var data = output.LockBits(rect, ImageLockMode.ReadWrite, PixelFormat.Format32bppArgb);
            int stride = data.Stride;
            int byteCount = stride * height;
            byte[] pixels = new byte[byteCount];
            Marshal.Copy(data.Scan0, pixels, 0, byteCount);
            bool[] visited = new bool[width * height];
            int[] queue = new int[width * height];
            int queueHead = 0;
            int queueTail = 0;

            Action<int, int> enqueue = (x, y) =>
            {
                int index = y * width + x;
                if (visited[index]) return;
                int offset = y * stride + x * 4;
                byte b = pixels[offset];
                byte g = pixels[offset + 1];
                byte r = pixels[offset + 2];
                if (r < threshold || g < threshold || b < threshold) return;
                visited[index] = true;
                queue[queueTail++] = index;
            };

            for (int x = 0; x < width; x++)
            {
                enqueue(x, 0);
                enqueue(x, height - 1);
            }
            for (int y = 0; y < height; y++)
            {
                enqueue(0, y);
                enqueue(width - 1, y);
            }

            while (queueHead < queueTail)
            {
                int index = queue[queueHead++];
                int x = index % width;
                int y = index / width;
                int offset = y * stride + x * 4;
                pixels[offset] = 0;
                pixels[offset + 1] = 0;
                pixels[offset + 2] = 0;
                pixels[offset + 3] = 0;
                if (x > 0) enqueue(x - 1, y);
                if (x + 1 < width) enqueue(x + 1, y);
                if (y > 0) enqueue(x, y - 1);
                if (y + 1 < height) enqueue(x, y + 1);
            }

            Marshal.Copy(pixels, 0, data.Scan0, byteCount);
            output.UnlockBits(data);

            int minX = width;
            int minY = height;
            int maxX = -1;
            int maxY = -1;
            for (int y = 0; y < height; y++)
            {
                for (int x = 0; x < width; x++)
                {
                    int offset = y * stride + x * 4;
                    if (pixels[offset + 3] <= 8) continue;
                    if (x < minX) minX = x;
                    if (x > maxX) maxX = x;
                    if (y < minY) minY = y;
                    if (y > maxY) maxY = y;
                }
            }

            if (maxX < minX || maxY < minY)
            {
                bounds = new Rectangle(0, 0, width, height);
            }
            else
            {
                var detected = Rectangle.FromLTRB(minX, minY, maxX + 1, maxY + 1);
                int marginX = Math.Max(8, detected.Width / 50);
                int marginY = Math.Max(8, detected.Height / 50);
                detected.Inflate(marginX, marginY);
                detected.Intersect(rect);
                bounds = detected;
            }

            return output;
        }
    }
}
'@

$references = @(
    (Join-Path $PSHOME "System.Drawing.Common.dll"),
    (Join-Path $PSHOME "System.Drawing.Primitives.dll"),
    (Join-Path $PSHOME "System.Private.Windows.Core.dll"),
    (Join-Path $PSHOME "System.Private.Windows.GdiPlus.dll"),
    (Join-Path $PSHOME "System.Private.CoreLib.dll")
) | Select-Object -Unique
Add-Type -TypeDefinition $code -ReferencedAssemblies $references

function Draw-ContainedImage {
    param(
        [System.Drawing.Graphics]$Graphics,
        [System.Drawing.Bitmap]$Image,
        [System.Drawing.Rectangle]$Bounds,
        [int]$CanvasSize,
        [single]$FillRatio,
        [int]$OffsetX = 0,
        [int]$OffsetY = 0
    )

    $inner = [single]($CanvasSize * $FillRatio)
    $scale = [Math]::Min($inner / $Bounds.Width, $inner / $Bounds.Height)
    $width = [int]($Bounds.Width * $scale)
    $height = [int]($Bounds.Height * $scale)
    $x = [int](($CanvasSize - $width) / 2) + $OffsetX
    $y = [int](($CanvasSize - $height) / 2) + $OffsetY
    $destination = [System.Drawing.Rectangle]::new($x, $y, $width, $height)
    $Graphics.DrawImage($Image, $destination, $Bounds, [System.Drawing.GraphicsUnit]::Pixel)
}

$bounds = [System.Drawing.Rectangle]::Empty
$snake = [IconBackgroundRemover]::RemoveConnectedWhite($sourceFullPath, 242, [ref]$bounds)

try {
    $launcherSizes = @{
        "mipmap-mdpi" = 48
        "mipmap-hdpi" = 72
        "mipmap-xhdpi" = 96
        "mipmap-xxhdpi" = 144
        "mipmap-xxxhdpi" = 192
    }
    $foregroundSizes = @{
        "drawable-mdpi" = 108
        "drawable-hdpi" = 162
        "drawable-xhdpi" = 216
        "drawable-xxhdpi" = 324
        "drawable-xxxhdpi" = 432
    }

    foreach ($entry in $launcherSizes.GetEnumerator()) {
        $directory = Join-Path $resourceRoot $entry.Key
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
        $size = [int]$entry.Value

        $square = [System.Drawing.Bitmap]::new(
            $size,
            $size,
            [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
        )
        $graphics = [System.Drawing.Graphics]::FromImage($square)
        try {
            $graphics.Clear([System.Drawing.Color]::White)
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
            Draw-ContainedImage -Graphics $graphics -Image $snake -Bounds $bounds -CanvasSize $size -FillRatio 0.82
        } finally {
            $graphics.Dispose()
        }
        $square.Save((Join-Path $directory "ic_launcher.png"), [System.Drawing.Imaging.ImageFormat]::Png)
        $square.Dispose()

        $round = [System.Drawing.Bitmap]::new(
            $size,
            $size,
            [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
        )
        $graphics = [System.Drawing.Graphics]::FromImage($round)
        $circle = [System.Drawing.Drawing2D.GraphicsPath]::new()
        try {
            $graphics.Clear([System.Drawing.Color]::Transparent)
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
            $circle.AddEllipse(0, 0, $size, $size)
            $graphics.FillPath([System.Drawing.Brushes]::White, $circle)
            $graphics.SetClip($circle)
            Draw-ContainedImage -Graphics $graphics -Image $snake -Bounds $bounds -CanvasSize $size -FillRatio 0.68
        } finally {
            $circle.Dispose()
            $graphics.Dispose()
        }
        $round.Save((Join-Path $directory "ic_launcher_round.png"), [System.Drawing.Imaging.ImageFormat]::Png)
        $round.Dispose()
    }

    foreach ($entry in $foregroundSizes.GetEnumerator()) {
        $directory = Join-Path $resourceRoot $entry.Key
        New-Item -ItemType Directory -Force -Path $directory | Out-Null
        $size = [int]$entry.Value
        $foreground = [System.Drawing.Bitmap]::new(
            $size,
            $size,
            [System.Drawing.Imaging.PixelFormat]::Format32bppArgb
        )
        $graphics = [System.Drawing.Graphics]::FromImage($foreground)
        try {
            $graphics.Clear([System.Drawing.Color]::Transparent)
            $graphics.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
            $graphics.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
            $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::HighQuality
            Draw-ContainedImage -Graphics $graphics -Image $snake -Bounds $bounds -CanvasSize $size -FillRatio 0.68
        } finally {
            $graphics.Dispose()
        }
        $foreground.Save((Join-Path $directory "ic_launcher_foreground.png"), [System.Drawing.Imaging.ImageFormat]::Png)
        $foreground.Dispose()
    }
} finally {
    $snake.Dispose()
}

Copy-Item -LiteralPath $sourceFullPath -Destination (Join-Path $designRoot "app-icon-source.png") -Force
Write-Output "Generated app icons from $sourceFullPath"
Write-Output "Detected content bounds: $($bounds.X),$($bounds.Y),$($bounds.Width),$($bounds.Height)"
