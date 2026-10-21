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
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
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

# 화면을 복사하지 않고 PrintWindow로 창 내용만 받아 온다. 다른 창이 앞을 가려도 Vivado 창이 찍힌다.
# (lab6에서 추가: 화면 복사 방식은 캡처 도중 다른 창으로 포커스가 옮겨지면 그 창이 찍혔다.)
$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
if ($Width -gt 0) { $bounds = New-Object System.Drawing.Rectangle 0, 0, $Width, $Height }
$bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
# 최대화한 창은 테두리만큼 화면 밖(음수 좌표)에서 시작하므로, 창 그림을 창 위치에 놓아 화면 좌표와 맞춘다.
$rect = New-Object Win+RECT
[Win]::GetWindowRect($window.MainWindowHandle, [ref]$rect) | Out-Null
$winBmp = New-Object System.Drawing.Bitmap ($rect.Right - $rect.Left), ($rect.Bottom - $rect.Top)
$wg = [System.Drawing.Graphics]::FromImage($winBmp)
$hdc = $wg.GetHdc()
[Win]::PrintWindow($window.MainWindowHandle, $hdc, 2) | Out-Null   # 2 = PW_RENDERFULLCONTENT
$wg.ReleaseHdc($hdc); $wg.Dispose()
$graphics.Clear([System.Drawing.Color]::White)
$graphics.DrawImageUnscaled($winBmp, $rect.Left - $bounds.X, $rect.Top - $bounds.Y)
$winBmp.Dispose()
$bitmap.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose(); $bitmap.Dispose()
"captured $Out ($($bounds.Width)x$($bounds.Height)) from '$($window.MainWindowTitle)'"

& taskkill /PID $window.Id /T /F | Out-Null
if (-not $launcher.HasExited) { & taskkill /PID $launcher.Id /T /F 2>$null | Out-Null }
