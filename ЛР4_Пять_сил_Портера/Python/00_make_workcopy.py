# -*- coding: utf-8 -*-
"""Рабочая копия Excel-шаблона: открыть с восстановлением (Д1) и сохранить средствами Excel."""
import os, shutil, tempfile, win32com.client
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "Материалы", "shablon_excel_ocenka_konkurencii_i_barerov_vhoda_similarweb.xlsx")
out = os.path.join(ROOT, "Excel", "ocenka_konkurencii_NotaCode.xlsx")
tmp = os.path.join(tempfile.gettempdir(), "lr4_tpl.xlsx")
shutil.copy(src, tmp)
xl = win32com.client.DispatchEx("Excel.Application")
xl.Visible = False; xl.DisplayAlerts = False
try:
    wb = xl.Workbooks.Open(tmp, 0, False, None, None, None, None, None, None, None, None, None, None, None, 1)
    wb.SaveAs(out, 51)
    for ws in wb.Worksheets:
        print(ws.Name, ws.UsedRange.Address, "charts:", ws.ChartObjects().Count)
    wb.Close(False)
finally:
    xl.Quit()
