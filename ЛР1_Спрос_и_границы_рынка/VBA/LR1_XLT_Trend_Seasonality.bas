Attribute VB_Name = "LR1_XLT_Trend_Seasonality"
' ЛР1. Макросы для рабочих копий Excel-шаблона оценки тренда, сезонности и деловых циклов
' (shablon_excel_ocenka_trenda_sezonnosti_delovyh_ciklov_google_trends_wordstat.xlsx).
' Формулы шаблона макросы не меняют: они только заполняют лист «Ввод_данных»,
' пересчитывают книгу и выводят итоговые показатели листов «Панель» и «Деловые_циклы».
'
' Порядок работы:
'   1) открыть рабочую копию шаблона (например, XLT_ОСНОВНОЙ_UML_BY.xlsx);
'   2) Alt+F11 -> File -> Import File... -> выбрать этот .bas;
'   3) Alt+F8 -> ImportInputCsv (выбрать CSV из Материалы_собранные\GT_Беларусь\XLT_ввод_данных_*.csv);
'   4) Alt+F8 -> ShowSummary — сводка Панели и Деловых_циклов в окне сообщения
'      и на листе «Сводка_макроса»;
'   5) при необходимости Alt+F8 -> KeepOnlySource — вариант «только GT» или «только Вордстат»
'      (правило Word «не складывать источники механически»); делать на копии книги.
'   6) Alt+F8 -> CheckErrors — поиск ячеек с ошибками «#…» на всех листах.
' Книгу с макросами сохранять как .xlsm (или удалить модуль перед сохранением в .xlsx).

Option Explicit

Private Const FIRST_ROW As Long = 5
Private Const LAST_ROW As Long = 64

' Чтение текстового файла в кодировке UTF-8 (CSV скриптов Python сохранены в UTF-8).
Private Function ReadUtf8(ByVal path As String) As String
    Dim st As Object
    Set st = CreateObject("ADODB.Stream")
    st.Type = 2
    st.Charset = "utf-8"
    st.Open
    st.LoadFromFile path
    ReadUtf8 = st.ReadText
    st.Close
End Function

' Заполняет «Ввод_данных»!A5:F64 из CSV с разделителем «;»:
' Период; Кластер запросов; Google Trends, 0-100; Яндекс Вордстат, запросов; Регион/рынок; Комментарий.
Public Sub ImportInputCsv()
    Dim f As Variant, txt As String, lines() As String, parts() As String
    Dim ws As Worksheet, i As Long, r As Long, c As Long
    f = Application.GetOpenFilename("CSV (*.csv),*.csv", , "CSV ввода данных для шаблона")
    If VarType(f) = vbBoolean Then Exit Sub
    Set ws = ThisWorkbook.Worksheets("Ввод_данных")
    ws.Range(ws.Cells(FIRST_ROW, 1), ws.Cells(LAST_ROW, 6)).ClearContents
    txt = Replace(ReadUtf8(CStr(f)), vbCr, "")
    lines = Split(txt, vbLf)
    r = FIRST_ROW
    For i = 1 To UBound(lines)                      ' строка 0 — заголовок
        If Len(Trim$(lines(i))) > 0 Then
            If r > LAST_ROW Then
                MsgBox "В шаблоне 60 строк ввода; лишние строки CSV не загружены.", vbExclamation
                Exit For
            End If
            parts = Split(lines(i), ";")
            ws.Cells(r, 1).Value = DateSerial(CInt(Left$(parts(0), 4)), CInt(Mid$(parts(0), 6, 2)), 1)
            ws.Cells(r, 2).Value = parts(1)
            For c = 2 To 3                           ' GT и Вордстат — числа; пусто остаётся пустым
                If UBound(parts) >= c Then
                    If Len(Trim$(parts(c))) > 0 Then ws.Cells(r, c + 1).Value = CDbl(Replace(parts(c), ".", Application.DecimalSeparator))
                End If
            Next c
            If UBound(parts) >= 4 Then ws.Cells(r, 5).Value = parts(4)
            If UBound(parts) >= 5 Then ws.Cells(r, 6).Value = parts(5)
            r = r + 1
        End If
    Next i
    Application.CalculateFull
    MsgBox "Загружено строк: " & (r - FIRST_ROW) & ". Книга пересчитана.", vbInformation
End Sub

' Оставляет один источник: очищает колонку Вордстата (только GT) или Google Trends (только Вордстат).
Public Sub KeepOnlySource()
    Dim ans As VbMsgBoxResult, ws As Worksheet, col As String
    ans = MsgBox("Да — оставить только Google Trends (очистить Вордстат)." & vbLf & _
                 "Нет — оставить только Вордстат (очистить Google Trends).", vbYesNoCancel + vbQuestion, _
                 "Вариант расчёта (делать на копии книги)")
    If ans = vbCancel Then Exit Sub
    col = IIf(ans = vbYes, "D", "C")
    Set ws = ThisWorkbook.Worksheets("Ввод_данных")
    ws.Range(col & FIRST_ROW & ":" & col & LAST_ROW).ClearContents
    Application.CalculateFull
    ShowSummary
End Sub

' Сводка итоговых показателей шаблона.
Public Sub ShowSummary()
    Dim p As Worksheet, d As Worksheet, s As Worksheet, out As Worksheet
    Dim items As Variant, i As Long, msg As String
    Application.CalculateFull
    Set p = ThisWorkbook.Worksheets("Панель")
    Set d = ThisWorkbook.Worksheets("Деловые_циклы")
    Set s = ThisWorkbook.Worksheets("Сезонность")
    On Error Resume Next
    Set out = ThisWorkbook.Worksheets("Сводка_макроса")
    On Error GoTo 0
    If out Is Nothing Then
        Set out = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        out.Name = "Сводка_макроса"
    End If
    out.Cells.Clear
    items = Array( _
        Array("Количество месяцев", p.Range("C6")), _
        Array("Классификация тренда", p.Range("C7")), _
        Array("Изменение последних 12 мес. к первым 12 мес.", p.Range("C8")), _
        Array("Сила сезонности", p.Range("C9")), _
        Array("Амплитуда сезонности", s.Range("B21")), _
        Array("Месяц максимума", p.Range("C10")), _
        Array("Месяц минимума", p.Range("C11")), _
        Array("Последний период", d.Range("B5")), _
        Array("Текущий циклический коэффициент (Деловые_циклы!B6)", d.Range("B6")), _
        Array("Текущая фаза (Деловые_циклы!B7)", d.Range("B7")), _
        Array("Минимальный коэффициент", d.Range("B8")), _
        Array("Максимальный коэффициент", d.Range("B9")), _
        Array("Итоговая формулировка (Панель!A17)", p.Range("A17")))
    out.Range("A1:B1").Value = Array("Показатель", "Значение (как в шаблоне)")
    For i = LBound(items) To UBound(items)
        out.Cells(i + 2, 1).Value = items(i)(0)
        out.Cells(i + 2, 2).Value = "'" & items(i)(1).Text
        If items(i)(1).Text = "" Then out.Cells(i + 2, 2).Value = "нет значения"
        msg = msg & items(i)(0) & ": " & out.Cells(i + 2, 2).Value & vbLf
    Next i
    out.Columns("A:B").AutoFit
    MsgBox msg, vbInformation, ThisWorkbook.Name
End Sub

' Перечень ячеек с ошибками «#…» на всех листах книги.
Public Sub CheckErrors()
    Dim ws As Worksheet, rng As Range, cell As Range, msg As String, n As Long
    For Each ws In ThisWorkbook.Worksheets
        Set rng = Nothing
        On Error Resume Next
        Set rng = ws.UsedRange.SpecialCells(xlCellTypeFormulas, xlErrors)
        On Error GoTo 0
        If Not rng Is Nothing Then
            For Each cell In rng.Cells
                n = n + 1
                If n <= 40 Then msg = msg & ws.Name & "!" & cell.Address(False, False) & " = " & cell.Text & vbLf
            Next cell
        End If
    Next ws
    If n = 0 Then
        MsgBox "Ячеек с ошибками нет.", vbInformation
    Else
        MsgBox "Ячеек с ошибками: " & n & vbLf & msg, vbExclamation
    End If
End Sub
