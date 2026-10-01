Attribute VB_Name = "VBA_SW"
'==============================================================================
' Attribute VB_Name = "VBA_SW"  (модуль VBA для книги: SW_объем_рынка_Similarweb_NotaCode.xlsx)
' Метод SW (объем рынка по Similarweb): проверка, сводка, чувствительность к покрытию, исправления П-1/П-18.
' Процедуры: ПроверкаРасчёта, СводкаРезультатов, СценарииЧувствительность,
'            ПримененитьИсправленияШаблона.
' Макросы не сохраняют книгу. Формат: VBA 7, Option Explicit.
'==============================================================================
Option Explicit

Private Const ЛИСТ_ПРОВЕРКИ As String = "Проверка_макрос"
Private Const ЛИСТ_ЧУВСТВ As String = "Чувствительность_макрос"

'------------------------------------------------------------------------------
' 1. Полный пересчёт и поиск ячеек-формул с ошибками + число диаграмм
'------------------------------------------------------------------------------
Public Sub ПроверкаРасчёта()
    Dim ws As Worksheet
    Dim wsOut As Worksheet
    Dim rngErr As Range
    Dim c As Range
    Dim r As Long
    Dim nErr As Long
    Dim nGraf As Long
    Dim nГрафЛистов As Long

    On Error GoTo ОбработкаОшибки
    Application.ScreenUpdating = False
    Application.CalculateFull

    Set wsOut = ПолучитьЛистВывода(ЛИСТ_ПРОВЕРКИ)
    wsOut.Range("A:E").Clear
    wsOut.Range("A1").Value = "Проверка расчёта книги: " & ThisWorkbook.Name
    wsOut.Range("A2").Value = "Дата и время: " & Format(Now, "dd.mm.yyyy hh:nn:ss")
    wsOut.Range("A4:D4").Value = Array("Лист", "Ячейка", "Формула", "Ошибка")
    wsOut.Range("A4:D4").Font.Bold = True
    r = 5

    Debug.Print "=== Проверка расчёта: " & ThisWorkbook.Name & " ==="
    For Each ws In ThisWorkbook.Worksheets
        If ws.Name <> wsOut.Name Then
            Set rngErr = Nothing
            On Error Resume Next
            Set rngErr = ws.UsedRange.SpecialCells(xlCellTypeFormulas, xlErrors)
            On Error GoTo ОбработкаОшибки
            If Not rngErr Is Nothing Then
                For Each c In rngErr.Cells
                    nErr = nErr + 1
                    wsOut.Cells(r, 1).Value = ws.Name
                    wsOut.Cells(r, 2).Value = c.Address(False, False)
                    wsOut.Cells(r, 3).NumberFormat = "@"
                    wsOut.Cells(r, 3).Value = c.Formula
                    wsOut.Cells(r, 4).Value = ТекстОшибки(c.Value)
                    Debug.Print ws.Name & "!" & c.Address(False, False) & " | " & c.Formula & " | " & ТекстОшибки(c.Value)
                    r = r + 1
                Next c
            End If
            nGraf = nGraf + ws.ChartObjects.Count
        End If
    Next ws
    nГрафЛистов = ThisWorkbook.Charts.Count

    r = r + 1
    If nErr = 0 Then
        wsOut.Cells(r, 1).Value = "Ячеек-формул с ошибками не найдено."
    Else
        wsOut.Cells(r, 1).Value = "Найдено ячеек-формул с ошибками: " & nErr
    End If
    wsOut.Cells(r + 1, 1).Value = "Диаграмм на листах (ChartObjects): " & nGraf
    wsOut.Cells(r + 2, 1).Value = "Отдельных листов-диаграмм: " & nГрафЛистов
    wsOut.Cells(r + 3, 1).Value = "Всего диаграмм в книге: " & (nGraf + nГрафЛистов)
    Debug.Print "Ошибок: " & nErr & "; диаграмм в книге: " & (nGraf + nГрафЛистов)
    wsOut.Columns("A:D").AutoFit

Выход:
    Application.ScreenUpdating = True
    Exit Sub
ОбработкаОшибки:
    MsgBox "Ошибка в ПроверкаРасчёта: " & Err.Number & " - " & Err.Description, vbExclamation
    Resume Выход
End Sub

'------------------------------------------------------------------------------
' 2. Сводка ключевых итогов книги на листе «Проверка_макрос» (столбцы G:Q)
'------------------------------------------------------------------------------
Public Sub СводкаРезультатов()
    Dim wsOut As Worksheet
    Dim r As Long

    On Error GoTo ОбработкаОшибки
    Application.ScreenUpdating = False
    Application.Calculate

    Set wsOut = ПолучитьЛистВывода(ЛИСТ_ПРОВЕРКИ)
    wsOut.Range("G:Q").Clear
    wsOut.Range("G1").Value = "Сводка ключевых итогов: " & ThisWorkbook.Name
    wsOut.Range("G2").Value = "Дата и время: " & Format(Now, "dd.mm.yyyy hh:nn:ss")
    wsOut.Range("G3:M3").Value = Array("Лист", "Диапазон", "Показатель", "Значение 1", "Значение 2", "Значение 3", "Значение 4")
    wsOut.Range("G3:Q3").Font.Bold = True
    r = 4

    ВывестиДиапазон ThisWorkbook, wsOut, r, "06_Воронка_сценарии", "J5:J7"
    ВывестиДиапазон ThisWorkbook, wsOut, r, "06_Воронка_сценарии", "D12:D14"
    ВывестиДиапазон ThisWorkbook, wsOut, r, "01_Параметры", "B8:B13"
    ВывестиДиапазон ThisWorkbook, wsOut, r, "09_Концентрация", "A11:C16"
    ВывестиДиапазон ThisWorkbook, wsOut, r, "10_TAM_SAM_SOM_М1", "A3:B17"
    ВывестиДиапазон ThisWorkbook, wsOut, r, "11_Вариант_М2", "A4:D17"
    wsOut.Columns("G:Q").AutoFit
    Debug.Print "Сводка результатов записана на лист " & ЛИСТ_ПРОВЕРКИ

Выход:
    Application.ScreenUpdating = True
    Exit Sub
ОбработкаОшибки:
    MsgBox "Ошибка в СводкаРезультатов: " & Err.Number & " - " & Err.Description, vbExclamation
    Resume Выход
End Sub

'------------------------------------------------------------------------------
' 3. Чувствительность: пошаговое изменение входа(ов) с обязательным возвратом
'------------------------------------------------------------------------------
Public Sub СценарииЧувствительность()
    Dim rs(1 To 3) As Range
    Dim сохр(1 To 3) As Variant
    Dim естьФорм(1 To 3) As Boolean
    Dim wsOut As Worksheet
    Dim режим As XlCalculation
    Dim режимСохранён As Boolean
    Dim сохранено As Boolean
    Dim k As Long
    Dim r As Long
    Dim i As Long
    Dim v As Double

    On Error GoTo ОбработкаОшибки
    Set rs(1) = ThisWorkbook.Worksheets("01_Параметры").Range("B11")
    Set rs(2) = ThisWorkbook.Worksheets("06_Воронка_сценарии").Range("B6")
    Set rs(3) = ThisWorkbook.Worksheets("11_Вариант_М2").Range("C7")
    Set wsOut = ПолучитьЛистВывода(ЛИСТ_ЧУВСТВ)
    wsOut.Cells.Clear
    wsOut.Range("A1").Value = "Чувствительность: коэффициент покрытия конкурентов от 0,4 до 0,9"
    wsOut.Range("A2").Value = "Одно значение подставляется в 01_Параметры!B11, 06_Воронка_сценарии!B6 (базовый) и 11_Вариант_М2!C7."
    wsOut.Range("A4:H4").Value = Array("Коэффициент покрытия", "Трафик рынка/мес. (01!B12)", "Трафик рынка/год (01!B13)", "Посещения/мес., базовый (06!C6)", "Выручка/год, базовый (06!J6)", "SOM/год, базовый (06!D13)", "V_total, М2 базовый (11!C8)", "SOM М2 базовый (11!C17)")
    wsOut.Range("A4:H4").Font.Bold = True
    r = 5

    Application.ScreenUpdating = False
    режим = Application.Calculation
    режимСохранён = True
    Application.Calculation = xlCalculationAutomatic

    ' Сохраняем исходные значения входов ДО цикла
    For k = 1 To 3
        естьФорм(k) = ЕстьФормулы(rs(k))
        If естьФорм(k) Then
            сохр(k) = rs(k).Formula
        Else
            сохр(k) = rs(k).Value2
        End If
    Next k
    сохранено = True

    For i = 4 To 9
        v = i / 10
        rs(1).Value2 = v
        rs(2).Value2 = v
        rs(3).Value2 = v
        Application.Calculate
        ЗаписатьСтроку wsOut, r, v, Знач("01_Параметры", "B12"), Знач("01_Параметры", "B13"), _
            Знач("06_Воронка_сценарии", "C6"), Знач("06_Воронка_сценарии", "J6"), _
            Знач("06_Воронка_сценарии", "D13"), Знач("11_Вариант_М2", "C8"), Знач("11_Вариант_М2", "C17")
        r = r + 1
    Next i

Восстановить:
    ' Аналог блока Finally: возврат исходных значений входов
    On Error Resume Next
    If сохранено Then
        For k = 1 To 3
            If естьФорм(k) Then
                rs(k).Formula = сохр(k)
            Else
                rs(k).Value2 = сохр(k)
            End If
        Next k
    End If
    Application.Calculate
    If режимСохранён Then Application.Calculation = режим
    If Not wsOut Is Nothing Then
        wsOut.Cells(r + 1, 1).Value = "Исходные значения входных ячеек восстановлены."
        wsOut.Columns("A:H").AutoFit
    End If
    Application.ScreenUpdating = True
    Exit Sub
ОбработкаОшибки:
    MsgBox "Ошибка в СценарииЧувствительность: " & Err.Number & " - " & Err.Description, vbExclamation
    Resume Восстановить
End Sub

'------------------------------------------------------------------------------
' 5. Исправления шаблона
'------------------------------------------------------------------------------
Public Sub ПримененитьИсправленияШаблона()
    ' П-1: суммы наблюдаемого трафика (01_Параметры!B9, B10).
    ' П-18: взвешенные доли каналов (02_Конкуренты_SW!M25:R25) по столбцам.
    Dim wsP As Worksheet
    Dim wsK As Worksheet
    Dim c As Long
    Dim лет As String
    On Error GoTo ОбработкаОшибки
    Set wsP = ThisWorkbook.Worksheets("01_Параметры")
    Set wsK = ThisWorkbook.Worksheets("02_Конкуренты_SW")
    wsP.Range("B9").Formula = "=SUM('02_Конкуренты_SW'!G4:G23)"
    wsP.Range("B10").Formula = "=SUM('02_Конкуренты_SW'!H4:H23)"
    For c = 13 To 18
        лет = wsK.Cells(1, c).Address(False, False)
        лет = Left$(лет, Len(лет) - 1)
        wsK.Cells(25, c).Formula = "=IFERROR(SUMPRODUCT($G$4:$G$23," & лет & "4:" & лет & "23)/SUMIF(" & _
            лет & "4:" & лет & "23,"">0"",$G$4:$G$23),0)"
    Next c
    Application.Calculate
    Debug.Print "П-1/П-18 применены: 01_Параметры!B9:B10, 02_Конкуренты_SW!M25:R25"
    Exit Sub
ОбработкаОшибки:
    MsgBox "Ошибка в ПримененитьИсправленияШаблона: " & Err.Number & " - " & Err.Description, vbExclamation
End Sub

'==============================================================================
' Вспомогательные процедуры (Private)
'==============================================================================
Private Function ПолучитьЛистВывода(ByVal имяЛиста As String) As Worksheet
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(имяЛиста)
    On Error GoTo 0
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        ws.Name = имяЛиста
    End If
    Set ПолучитьЛистВывода = ws
End Function

Private Function ТекстОшибки(ByVal v As Variant) As String
    If Not IsError(v) Then
        ТекстОшибки = ""
        Exit Function
    End If
    Select Case CLng(Val(Mid$(CStr(v), 7)))
        Case 2007: ТекстОшибки = "#ДЕЛ/0!"
        Case 2015: ТекстОшибки = "#ЗНАЧ!"
        Case 2029: ТекстОшибки = "#ИМЯ?"
        Case 2023: ТекстОшибки = "#ССЫЛ!"
        Case 2042: ТекстОшибки = "#Н/Д"
        Case 2036: ТекстОшибки = "#ЧИСЛО!"
        Case 2000: ТекстОшибки = "#ПУСТО!"
        Case Else: ТекстОшибки = CStr(v)
    End Select
End Function

Private Sub ЗаписатьЗначение(ByVal dst As Range, ByVal src As Range)
    Dim v As Variant
    v = src.Value
    If IsError(v) Then
        dst.NumberFormat = "@"
        dst.Value = ТекстОшибки(v)
    ElseIf IsEmpty(v) Then
        dst.ClearContents
    ElseIf VarType(v) = vbString Then
        dst.NumberFormat = "@"
        dst.Value = v
    Else
        dst.Value = src.Value2
    End If
End Sub

Private Sub ВывестиДиапазон(ByVal wb As Workbook, ByVal wsOut As Worksheet, ByRef r As Long, _
                            ByVal имяЛиста As String, ByVal адрес As String)
    Dim ws As Worksheet
    Dim rng As Range
    Dim i As Long
    Dim j As Long
    Dim j0 As Long
    Dim colOut As Long

    On Error Resume Next
    Set ws = wb.Worksheets(имяЛиста)
    Set rng = ws.Range(адрес)
    On Error GoTo 0
    If rng Is Nothing Then
        wsOut.Cells(r, 7).Value = имяЛиста
        wsOut.Cells(r, 8).Value = адрес
        wsOut.Cells(r, 9).Value = "лист или диапазон не найден"
        r = r + 1
        Exit Sub
    End If

    For i = 1 To rng.Rows.Count
        wsOut.Cells(r, 7).Value = имяЛиста
        wsOut.Cells(r, 8).Value = rng.Rows(i).Address(False, False)
        If rng.Column = 1 Then
            ЗаписатьЗначение wsOut.Cells(r, 9), rng.Cells(i, 1)
            j0 = 2
        Else
            ЗаписатьЗначение wsOut.Cells(r, 9), ws.Cells(rng.Row + i - 1, 1)
            j0 = 1
        End If
        colOut = 10
        For j = j0 To rng.Columns.Count
            If colOut <= 17 Then
                ЗаписатьЗначение wsOut.Cells(r, colOut), rng.Cells(i, j)
                colOut = colOut + 1
            End If
        Next j
        r = r + 1
    Next i
End Sub

Private Function Знач(ByVal имяЛиста As String, ByVal адрес As String) As Variant
    Знач = ThisWorkbook.Worksheets(имяЛиста).Range(адрес).Value
End Function

Private Sub ЗаписатьСтроку(ByVal ws As Worksheet, ByVal r As Long, ParamArray значения() As Variant)
    Dim i As Long
    For i = LBound(значения) To UBound(значения)
        ws.Cells(r, i + 1).Value = значения(i)
    Next i
End Sub

Private Function ЕстьФормулы(ByVal rng As Range) As Boolean
    Dim h As Variant
    h = rng.HasFormula
    ЕстьФормулы = IsNull(h) Or (h = True)
End Function
