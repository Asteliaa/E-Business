# -*- coding: utf-8 -*-
import os, win32com.client
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XLS = os.path.join(ROOT, "Excel", "ocenka_konkurencii_NotaCode.xlsx")

class Book:
    def __init__(self, path=XLS):
        self.xl = win32com.client.DispatchEx("Excel.Application")
        self.xl.Visible = False; self.xl.DisplayAlerts = False
        self._af = self.xl.AutoCorrect.AutoFillFormulasInLists
        self.xl.AutoCorrect.AutoFillFormulasInLists = False   # без автопротяжки формул в списках
        self.wb = self.xl.Workbooks.Open(path)
    def ws(self, n): return self.wb.Worksheets(n)
    def close(self, save=True):
        try:
            if save: self.wb.Save()
            self.wb.Close(False)
        finally:
            self.xl.AutoCorrect.AutoFillFormulasInLists = self._af
            self.xl.Quit()
