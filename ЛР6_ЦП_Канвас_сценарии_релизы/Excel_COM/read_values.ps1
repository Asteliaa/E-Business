# Чтение значений диапазонов рабочей книги Excel через COM (только чтение)
# Запуск: powershell -NoProfile -ExecutionPolicy Bypass -File read_values.ps1 -Book <xlsx> -Ranges "лист!A1:B5|лист2!C3:D9" -Out <tsv>
param([Parameter(Mandatory = $true)][string]$Book, [Parameter(Mandatory = $true)][string]$Ranges, [Parameter(Mandatory = $true)][string]$Out)
$ErrorActionPreference = 'Stop'
Get-Process -Name EXCEL -ErrorAction SilentlyContinue | Stop-Process -Force
$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$sb = New-Object System.Text.StringBuilder
try {
    $wb = $xl.Workbooks.Open($Book, 0, $true)
    foreach ($spec in $Ranges.Split('|')) {
        $parts = $spec.Split('!')
        $ws = $wb.Worksheets.Item($parts[0])
        $rng = $ws.Range($parts[1])
        $r0 = $rng.Row; $c0 = $rng.Column
        foreach ($cell in $rng.Cells) {
            $v = $cell.Value2
            if ($null -eq $v) { continue }
            $t = [string]$v
            if ($cell.Text -like '#*' -and $cell.Text.Length -le 8 -and $v -is [int]) { $t = $cell.Text }
            $t = $t.Replace("`r", '').Replace("`n", '\n').Replace("`t", '\t')
            [void]$sb.AppendLine($parts[0] + "`t" + $cell.Row + "`t" + $cell.Column + "`t" + $t)
        }
    }
    [System.IO.File]::WriteAllText($Out, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))
    $wb.Close($false)
    Write-Output ("OK " + $Out)
}
finally {
    $xl.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    Get-Process -Name EXCEL -ErrorAction SilentlyContinue | Stop-Process -Force
}
