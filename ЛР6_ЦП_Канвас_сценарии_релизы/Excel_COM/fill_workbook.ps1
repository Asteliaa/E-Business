# Заполнение рабочей копии Excel-шаблона по JSON-спецификации (Excel только через COM)
# Запуск: powershell -NoProfile -ExecutionPolicy Bypass -File fill_workbook.ps1 -SpecPath <spec.json>
param([Parameter(Mandatory = $true)][string]$SpecPath)
$ErrorActionPreference = 'Stop'

# 1. Завершить зависшие процессы Excel (процессы excel-mcp-server не затрагиваются)
Get-Process -Name EXCEL -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Milliseconds 500

$json = [System.IO.File]::ReadAllText($SpecPath, [System.Text.Encoding]::UTF8)
$spec = $json | ConvertFrom-Json
Copy-Item -LiteralPath $spec.template -Destination $spec.out -Force

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false
$xl.DisplayAlerts = $false
$oldAuto = $xl.AutoCorrect.AutoFillFormulasInLists
$oldUser = $xl.UserName
$xl.AutoCorrect.AutoFillFormulasInLists = $false
$xl.ScreenUpdating = $false
$xl.EnableEvents = $false
$bind = [System.Reflection.BindingFlags]

function Set-DocProp($props, $name, $value) {
    $p = [System.__ComObject].InvokeMember('Item', $bind::GetProperty, $null, $props, @($name))
    [System.__ComObject].InvokeMember('Value', $bind::SetProperty, $null, $p, @($value)) | Out-Null
}

try {
    $wb = $xl.Workbooks.Open($spec.out)
    $xl.Calculation = -4135   # ручной пересчёт на время записи
    $sheets = @{}
    foreach ($s in $wb.Worksheets) { $sheets[$s.Name] = $s }
    $sep = $xl.International(5)   # разделитель элементов списка

    # 2. Исправление проверки данных
    foreach ($d in $spec.dv) {
        $rng = $sheets[$d.sheet].Range($d.range)
        $rng.Validation.Delete()
        if ($d.type -eq 'list') {
            $f1 = $d.f1
            if ($f1 -notlike '=*') { $f1 = ($d.f1 -split ';') -join $sep }
            $rng.Validation.Add(3, 1, 1, $f1) | Out-Null
            $rng.Validation.InCellDropdown = $true
        }
        elseif ($d.type -eq 'whole') {
            $rng.Validation.Add(1, 1, 1, [string]$d.lo, [string]$d.hi) | Out-Null
        }
        $rng.Validation.IgnoreBlank = $true
    }

    # 3. Очистка диапазонов (при необходимости)
    foreach ($c in $spec.clear) { $sheets[$c.sheet].Range($c.range).ClearContents() | Out-Null }

    # 4. Запись значений
    $errs = New-Object System.Collections.ArrayList
    foreach ($w in $spec.writes) {
      try {
        $ws = $sheets[[string]$w[0]]
        $cell = $ws.Cells.Item([int]$w[1], [int]$w[2])
        $v = $w[3]
        if ($v -is [string]) { $cell.Value2 = $v }
        elseif ($v -is [int] -or $v -is [long] -or $v -is [double] -or $v -is [decimal]) { $cell.Value2 = [double]$v }
        elseif ($v -is [bool]) { $cell.Value2 = $v }
        elseif ($null -ne $v -and $v.PSObject.Properties['d']) {
            $dt = [datetime]::ParseExact($v.d, 'yyyy-MM-dd', [System.Globalization.CultureInfo]::InvariantCulture)
            $oa = [string][int]$dt.ToOADate(); $cell.Formula = $oa
        }
        elseif ($null -ne $v -and $v.PSObject.Properties['f']) {
            try { $cell.Formula2 = $v.f } catch { $cell.Formula = $v.f }
        }
      } catch { [void]$errs.Add(([string]$w[0] + '!R' + [string]$w[1] + 'C' + [string]$w[2] + ': ' + $_.Exception.GetType().FullName + " | " + $_.Exception.Message + " @" + $_.InvocationInfo.ScriptLineNumber + " | " + $_.InvocationInfo.PositionMessage)) }
    }
    if ($errs.Count -gt 0) { Write-Output ('WRITE ERRORS: ' + $errs.Count); $errs | Select-Object -First 15 | ForEach-Object { Write-Output $_ } }

    # 5. Формулы
    foreach ($f in $spec.formulas) {
        $cell = $sheets[[string]$f[0]].Cells.Item([int]$f[1], [int]$f[2])
        try { $cell.Formula2 = [string]$f[3] } catch { $cell.Formula = [string]$f[3] }
    }

    # 5а. Повторный ввод формул с XLOOKUP: в файле шаблона функция записана без префикса _xlfn и не вычисляется
    if ($spec.extra.reparse_xlookup) {
        foreach ($ws in $wb.Worksheets) {
            $fc = $null
            try { $fc = $ws.UsedRange.SpecialCells(-4123) } catch { }
            if ($null -ne $fc) {
                foreach ($cell in $fc.Cells) {
                    $ff = [string]$cell.Formula
                    if ($ff -like '*XLOOKUP*') { $cell.Formula2 = $ff }
                }
            }
        }
    }

    # 6. Новые листы (журнал)
    foreach ($ns in $spec.new_sheets) {
        $last = $wb.Worksheets.Item($wb.Worksheets.Count)
        $nws = $wb.Worksheets.Add([Type]::Missing, $last)
        $nws.Name = $ns.name

        $nws.Cells.Font.Size = 10
        $nws.Cells.Item(1, 1).Value2 = $ns.title
        $nws.Cells.Item(1, 1).Font.Bold = $true
        $nws.Cells.Item(1, 1).Font.Size = 12
        for ($c = 0; $c -lt $ns.header.Count; $c++) {
            $h = $nws.Cells.Item(3, $c + 1)
            $h.Value2 = $ns.header[$c]
            $h.Font.Bold = $true
            $h.Interior.Color = 15921906
            $h.Borders.LineStyle = 1
        }
        $r = 4
        foreach ($row in $ns.rows) {
            for ($c = 0; $c -lt $row.Count; $c++) {
                $x = $nws.Cells.Item($r, $c + 1)
                $x.Value2 = [string]$row[$c]
                $x.WrapText = $true
                $x.VerticalAlignment = -4160
                $x.Borders.LineStyle = 1
            }
            $r++
        }
        for ($c = 0; $c -lt $ns.widths.Count; $c++) { $nws.Columns.Item($c + 1).ColumnWidth = $ns.widths[$c] }
        $nws.Range($nws.Cells.Item(4, 1), $nws.Cells.Item($r, $ns.header.Count)).Rows.AutoFit() | Out-Null
        $sheets[$ns.name] = $nws
    }

    # 7. Ширина столбцов и высота строк
    foreach ($w in $spec.widths) { $sheets[$w.sheet].Columns.Item($w.col).ColumnWidth = [double]$w.width }
    foreach ($a in $spec.autofit) {
        $rng = $sheets[$a.sheet].Range($a.range)
        $rng.WrapText = $true
        $rng.VerticalAlignment = -4160
        $rng.Rows.AutoFit() | Out-Null
    }

    # 8. Пересчёт
    $xl.Calculation = -4105
    $xl.CalculateFull()

    # 9. Метаданные: автор
    $props = $wb.BuiltinDocumentProperties
    $author = $spec.extra.author
    $xl.UserName = $author
    Set-DocProp $props 'Author' $author
    Set-DocProp $props 'Last Author' $author
    Set-DocProp $props 'Company' ''
    Set-DocProp $props 'Comments' ''
    if ($spec.extra.title) { Set-DocProp $props 'Title' $spec.extra.title }

    $sheets[$wb.Worksheets.Item(1).Name].Activate()
    $wb.Save()
    $wb.Close($true)
    Write-Output ("OK: " + $spec.out)
}
catch {
    Write-Output ("ERROR at line " + $_.InvocationInfo.ScriptLineNumber + ": " + $_.Exception.Message + " | " + $_.InvocationInfo.Line.Trim())
    $global:failed = $true
}
finally {
    $xl.AutoCorrect.AutoFillFormulasInLists = $oldAuto
    try { $xl.UserName = $oldUser } catch {}
    $xl.ScreenUpdating = $true
    $xl.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
    Get-Process -Name EXCEL -ErrorAction SilentlyContinue | Stop-Process -Force
}
