# Starts the E1 scheduler and its watchdog as detached background processes (they outlive the session that starts them).
# usage:  powershell -NoProfile -ExecutionPolicy Bypass -File launch_e1.ps1 [-Root <e1 folder>] [-NP 6] [-CapHours 8] [-Wmi]
#   -Wmi : create the two processes through WMI (Win32_Process.Create) instead of Start-Process. They then do not
#          belong to any job object of the calling session. Used automatically when the calling session sits in a job
#          object that ends its processes when it closes and does not allow them to leave it.
# A second start while a scheduler is alive is refused. A start after a stop RESUMES: the cap counts from out\T0.txt.
param([string]$Root = "", [int]$NP = 6, [double]$CapHours = 8, [switch]$Wmi)
$ErrorActionPreference = "Stop"
if ($Root -eq "") { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path }
$Root = (Resolve-Path $Root).Path
$py = "C:\Python311\python.exe"
$code = Join-Path $Root "code"
$out = Join-Path $Root "out"
$logs = Join-Path $out "logs"
New-Item -ItemType Directory -Force $logs | Out-Null
$cap = $CapHours.ToString([cultureinfo]::InvariantCulture)
$stamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
$mark = (Join-Path (Join-Path (Split-Path -Leaf (Split-Path -Parent $Root)) (Split-Path -Leaf $Root)) "code").ToLower()

$alive = Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object { $_.CommandLine -and $_.CommandLine.Replace("/", "\").ToLower().Contains($mark) -and $_.CommandLine -match "run_e1\.py" }
if ($alive) { Write-Output "REFUSED: a scheduler is alive (pid $($alive.ProcessId -join ', ')). Nothing started."; exit 2 }
foreach ($f in @("STOP", "KILL", "RUN_EXIT", "WATCHDOG_FIRED")) { $p = Join-Path $out $f; if (Test-Path $p) { Move-Item -Force $p (Join-Path $logs "$f.$stamp.txt") } }

# is this session inside a job object that would end the processes it starts?
$job = "unknown"
try {
  Add-Type -Namespace E1 -Name Job -MemberDefinition @"
[DllImport("kernel32.dll")] public static extern IntPtr GetCurrentProcess();
[DllImport("kernel32.dll", SetLastError=true)] public static extern bool IsProcessInJob(IntPtr p, IntPtr j, out bool r);
[DllImport("kernel32.dll", SetLastError=true)] public static extern bool QueryInformationJobObject(IntPtr j, int c, byte[] b, int n, IntPtr r);
"@
  $inJob = $false
  [void][E1.Job]::IsProcessInJob([E1.Job]::GetCurrentProcess(), [IntPtr]::Zero, [ref]$inJob)
  if (-not $inJob) { $job = "no job object" }
  else {
    $buf = New-Object byte[] 144
    if ([E1.Job]::QueryInformationJobObject([IntPtr]::Zero, 9, $buf, 144, [IntPtr]::Zero)) {
      $flags = [BitConverter]::ToUInt32($buf, 16)
      $kill = ($flags -band 0x2000) -ne 0; $brk = ($flags -band 0x1800) -ne 0
      $job = "in a job object; limit flags 0x{0:X}; ends its processes on close: {1}; processes may leave it: {2}" -f $flags, $kill, $brk
      if ($kill -and -not $brk) { $Wmi = $true }
    } else { $job = "in a job object; flags not readable" }
  }
} catch { $job = "check failed: $($_.Exception.Message)" }

$env:OMP_NUM_THREADS = "2"; $env:MKL_NUM_THREADS = "2"; $env:OPENBLAS_NUM_THREADS = "2"
if ($Wmi) {
  $c1 = "cmd.exe /c `"`"$py`" -B `"$code\run_e1.py`" $NP $cap > `"$logs\scheduler_$stamp.out.txt`" 2> `"$logs\scheduler_$stamp.err.txt`"`""
  $c2 = "cmd.exe /c `"`"$py`" -B `"$code\watchdog_e1.py`" $cap > `"$logs\watchdog_$stamp.out.txt`" 2> `"$logs\watchdog_$stamp.err.txt`"`""
  $r1 = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $c1; CurrentDirectory = $code }
  $r2 = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = $c2; CurrentDirectory = $code }
  $line = "$stamp started through WMI: scheduler shell pid $($r1.ProcessId) (rc $($r1.ReturnValue)), watchdog shell pid $($r2.ProcessId) (rc $($r2.ReturnValue)); NP $NP; cap $cap h; session: $job"
} else {
  $s = Start-Process -FilePath $py -ArgumentList @("-B", "`"$code\run_e1.py`"", "$NP", $cap) -WorkingDirectory $code -WindowStyle Hidden -RedirectStandardOutput "$logs\scheduler_$stamp.out.txt" -RedirectStandardError "$logs\scheduler_$stamp.err.txt" -PassThru
  $w = Start-Process -FilePath $py -ArgumentList @("-B", "`"$code\watchdog_e1.py`"", $cap) -WorkingDirectory $code -WindowStyle Hidden -RedirectStandardOutput "$logs\watchdog_$stamp.out.txt" -RedirectStandardError "$logs\watchdog_$stamp.err.txt" -PassThru
  $line = "$stamp started with Start-Process: scheduler pid $($s.Id), watchdog pid $($w.Id); NP $NP; cap $cap h; session: $job"
}
Add-Content -Path (Join-Path $out "launch_log.txt") -Value $line
Write-Output $line
