Attribute VB_Name = "VBA_Common"
'==============================================================================
' Attribute VB_Name = "VBA_Common"  (общий модуль VBA, книга-хозяин сводки)
' ПереносИтоговВСводку: открывает 7 книг методов (только чтение), читает итоговые
' ячейки и собирает таблицу на листе «Сводка_методов» книги-хозяина.
' Книги закрываются без сохранения. Формат: VBA 7, Option Explicit.
' Каталог книг задаётся константой КАТАЛОГ_EXCEL (относительно ThisWorkbook.Path).
'==============================================================================
Option Explicit

' Относительный путь к каталогу с книгами методов (от папки книги-хозяина)
Private Const КАТАЛОГ_EXCEL As String = "\..\Excel\"
Private Const ЛИСТ_СВОДКИ As String = "Сводка_методов"

Public Sub ПереносИтоговВСводку()
    Dim fso As Object
    Dim каталог As String
    Dim wsOut As Worksheet
    Dim wb As Workbook
    Dim открытаЗдесь As Boolean
    Dim r As Long
    Dim алертыИсх As Boolean
    Dim обновлениеИсх As Boolean

    On Error GoTo ОбработкаОшибки
    If Len(ThisWorkbook.Path) = 0 Then
        MsgBox "Сначала сохраните книгу-хозяин: путь к каталогу Excel вычисляется от ThisWorkbook.Path.", vbExclamation
        Exit Sub
    End If
    алертыИсх = Application.DisplayAlerts
    обновлениеИсх = Application.ScreenUpdating
    Application.DisplayAlerts = False
    Application.ScreenUpdating = False

    Set fso = CreateObject("Scripting.FileSystemObject")
    каталог = fso.GetAbsolutePathName(ThisWorkbook.Path & КАТАЛОГ_EXCEL)
    If Right$(каталог, 1) <> "\" Then каталог = каталог & "\"

    Set wsOut = ПолучитьЛистСводки(ЛИСТ_СВОДКИ)
    wsOut.Cells.Clear
    wsOut.Range("A1").Value = "Сводка методов оценки объёма рынка"
    wsOut.Range("A1").Font.Bold = True
    wsOut.Range("A2").Value = "Каталог: " & каталог & "; дата: " & Format(Now, "dd.mm.yyyy hh:nn")
    wsOut.Range("A4:E4").Value = Array("Метод", "Осторожный", "Базовый", "Оптимистичный", "Уровень (рынок/SOM)")
    wsOut.Range("A4:E4").Font.Bold = True
    r = 5

    Set wb = ОткрытьКнигу(каталог & "ПС_поисковый_спрос_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "ПС: поисковый спрос", "06_Воронка", "B14", "C14", "D14", "рынок (выручка/год, BYN)"
    ЗакрытьКнигу wb, открытаЗдесь

    Set wb = ОткрытьКнигу(каталог & "ЦВ_цифровая_воронка_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "ЦВ: цифровая воронка", "05_Сценарии", "C9", "C10", "C11", "рынок (выручка/год, BYN)"
    ЗакрытьКнигу wb, открытаЗдесь

    Set wb = ОткрытьКнигу(каталог & "ПЛ_платежеспособность_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "ПЛ: платежеспособность", "08_Итоговая_панель", "B9", "B10", "B11", "SOM (достижимая выручка)"
    ЗакрытьКнигу wb, открытаЗдесь

    Set wb = ОткрытьКнигу(каталог & "ПК_потенциальные_клиенты_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "ПК: потенциальные клиенты", "06_Дашборд", "B14", "B15", "B16", "TAM"
    ДобавитьСтроку wb, wsOut, r, "ПК: потенциальные клиенты", "06_Дашборд", "C14", "C15", "C16", "SAM"
    ДобавитьСтроку wb, wsOut, r, "ПК: потенциальные клиенты", "06_Дашборд", "D14", "D15", "D16", "SOM"
    ЗакрытьКнигу wb, открытаЗдесь

    Set wb = ОткрытьКнигу(каталог & "СЦ_сценарная_оценка_Similarweb_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "СЦ: сценарная оценка SW", "04_Воронка", "H5", "H6", "H7", "рынок (выручка/год, BYN)"
    ДобавитьСтроку wb, wsOut, r, "СЦ: сценарная оценка SW", "04_Воронка", "J5", "J6", "J7", "SOM (достижимая выручка/год)"
    ЗакрытьКнигу wb, открытаЗдесь

    Set wb = ОткрытьКнигу(каталог & "СВ_сверху_вниз_снизу_вверх_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "СВ: сверху вниз", "06_Сверка", "B5", "C5", "D5", "рынок"
    ДобавитьСтроку wb, wsOut, r, "СВ: снизу вверх", "06_Сверка", "B6", "C6", "D6", "рынок"
    ДобавитьСтроку wb, wsOut, r, "СВ: Similarweb + воронка", "06_Сверка", "B7", "C7", "D7", "рынок"
    ЗакрытьКнигу wb, открытаЗдесь

    Set wb = ОткрытьКнигу(каталог & "SW_объем_рынка_Similarweb_NotaCode.xlsx", открытаЗдесь)
    ДобавитьСтроку wb, wsOut, r, "SW: объем рынка Similarweb", "06_Воронка_сценарии", "J5", "J6", "J7", "рынок (выручка/год, BYN)"
    ДобавитьСтроку wb, wsOut, r, "SW: объем рынка Similarweb", "06_Воронка_сценарии", "D12", "D13", "D14", "SOM (выручка нового бизнеса/год)"
    ЗакрытьКнигу wb, открытаЗдесь

    wsOut.Columns("A:E").AutoFit
    wsOut.Range("B5:D" & (r - 1)).NumberFormat = "#,##0.00"

Выход:
    On Error Resume Next
    If Not wb Is Nothing Then ЗакрытьКнигу wb, открытаЗдесь
    Application.DisplayAlerts = алертыИсх
    Application.ScreenUpdating = True
    Exit Sub
ОбработкаОшибки:
    MsgBox "Ошибка в ПереносИтоговВСводку: " & Err.Number & " - " & Err.Description, vbExclamation
    Resume Выход
End Sub

'==============================================================================
' Вспомогательные процедуры (Private)
'==============================================================================
Private Function ПолучитьЛистСводки(ByVal имяЛиста As String) As Worksheet
    Dim ws As Worksheet
    On Error Resume Next
    Set ws = ThisWorkbook.Worksheets(имяЛиста)
    On Error GoTo 0
    If ws Is Nothing Then
        Set ws = ThisWorkbook.Worksheets.Add(After:=ThisWorkbook.Worksheets(ThisWorkbook.Worksheets.Count))
        ws.Name = имяЛиста
    End If
    Set ПолучитьЛистСводки = ws
End Function

' Открывает книгу только для чтения; если уже открыта - использует её (не закрывается)
Private Function ОткрытьКнигу(ByVal путь As String, ByRef открытаЗдесь As Boolean) As Workbook
    Dim wb As Workbook
    Dim имяФайла As String
    имяФайла = Mid$(путь, InStrRev(путь, "\") + 1)
    открытаЗдесь = False
    On Error Resume Next
    Set wb = Workbooks(имяФайла)
    On Error GoTo 0
    If wb Is Nothing Then
        On Error Resume Next
        Set wb = Workbooks.Open(Filename:=путь, ReadOnly:=True, UpdateLinks:=0)
        On Error GoTo 0
        If Not wb Is Nothing Then открытаЗдесь = True
    End If
    Set ОткрытьКнигу = wb
End Function

Private Sub ЗакрытьКнигу(ByRef wb As Workbook, ByVal открытаЗдесь As Boolean)
    If wb Is Nothing Then Exit Sub
    If открытаЗдесь Then wb.Close SaveChanges:=False
    Set wb = Nothing
End Sub

Private Sub ДобавитьСтроку(ByVal wb As Workbook, ByVal wsOut As Worksheet, ByRef r As Long, _
                           ByVal метод As String, ByVal имяЛиста As String, _
                           ByVal адрес1 As String, ByVal адрес2 As String, ByVal адрес3 As String, _
                           ByVal уровень As String)
    Dim ws As Worksheet
    wsOut.Cells(r, 1).Value = метод
    wsOut.Cells(r, 5).Value = уровень
    If wb Is Nothing Then
        wsOut.Cells(r, 2).Value = "книга не открыта"
        r = r + 1
        Exit Sub
    End If
    On Error Resume Next
    Set ws = wb.Worksheets(имяЛиста)
    On Error GoTo 0
    If ws Is Nothing Then
        wsOut.Cells(r, 2).Value = "лист не найден: " & имяЛиста
        r = r + 1
        Exit Sub
    End If
    ПеренестиЯчейку wsOut.Cells(r, 2), ws.Range(адрес1)
    ПеренестиЯчейку wsOut.Cells(r, 3), ws.Range(адрес2)
    ПеренестиЯчейку wsOut.Cells(r, 4), ws.Range(адрес3)
    r = r + 1
End Sub

Private Sub ПеренестиЯчейку(ByVal dst As Range, ByVal src As Range)
    Dim v As Variant
    v = src.Value
    If IsError(v) Then
        dst.NumberFormat = "@"
        dst.Value = "ошибка в ячейке источника"
    ElseIf VarType(v) = vbString Then
        dst.NumberFormat = "@"
        dst.Value = v
    Else
        dst.Value = src.Value2
    End If
End Sub
