# Vivado 시뮬레이터(xsim -gui)로 WDB를 열고 화면을 캡처한 뒤 창을 닫는다.
# 사용: powershell -File capture_xsim.ps1 -WorkDir <xsim 실행 폴더> -Wcfg tb.wcfg -Out shot.png
param(
    [Parameter(Mandatory)] [string]$WorkDir,
    [Parameter(Mandatory)] [string]$Wcfg,
    [Parameter(Mandatory)] [string]$Out,
    [string]$Xsim = 'C:\AMDDesignTools\2025.2\Vivado\bin\xsim.bat',
    [int]$SettleSeconds = 12,
    [int]$Width = 0,      # 0이면 최대화, 아니면 이 크기의 창으로 캡처(글자가 상대적으로 커진다)
    [int]$Height = 0
)
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class Win {
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int ht, bool repaint);
}
'@
[Win]::SetProcessDPIAware() | Out-Null

$before = @(Get-Process | Where-Object { $_.MainWindowHandle -ne 0 } | ForEach-Object { $_.Id })
$launcher = Start-Process -FilePath $Xsim -ArgumentList "tb_sim.wdb -gui -view $Wcfg -nolog" `
    -WorkingDirectory $WorkDir -WindowStyle Hidden -PassThru

$window = $null
for ($i = 0; $i -lt 180 -and -not $window; $i++) {
    Start-Sleep -Seconds 1
    $window = Get-Process | Where-Object {
        $_.MainWindowHandle -ne 0 -and $before -notcontains $_.Id -and $_.MainWindowTitle -match 'tb_sim|Vivado'
    } | Select-Object -First 1
}
if (-not $window) { throw 'Vivado simulator window did not appear' }

if ($Width -gt 0) {
    [Win]::ShowWindow($window.MainWindowHandle, 1) | Out-Null   # 1 = normal
    [Win]::MoveWindow($window.MainWindowHandle, 0, 0, $Width, $Height, $true) | Out-Null
} else {
    [Win]::ShowWindow($window.MainWindowHandle, 3) | Out-Null   # 3 = maximize
}
[Win]::SetForegroundWindow($window.MainWindowHandle) | Out-Null
Start-Sleep -Seconds $SettleSeconds
[Win]::SetForegroundWindow($window.MainWindowHandle) | Out-Null
Start-Sleep -Seconds 2

$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
if ($Width -gt 0) { $bounds = New-Object System.Drawing.Rectangle 0, 0, $Width, $Height }
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size)
$bitmap.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
"captured $Out ($($bounds.Width)x$($bounds.Height)) from '$($window.MainWindowTitle)'"

& taskkill /PID $window.Id /T /F | Out-Null
if (-not $launcher.HasExited) { & taskkill /PID $launcher.Id /T /F 2>$null | Out-Null }
