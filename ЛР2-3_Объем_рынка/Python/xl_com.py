# -*- coding: utf-8 -*-
"""Вспомогательные функции для работы с рабочими копиями Excel-шаблонов через COM.
Правка через Excel (а не openpyxl) сохраняет встроенные диаграммы шаблонов."""
import os
import datetime
import win32com.client

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XL_DIR = os.path.join(ROOT, "Excel")


class Book:
    def __init__(self, name, visible=False):
        self.path = os.path.join(XL_DIR, name)
        self.xl = win32com.client.DispatchEx("Excel.Application")
        self.xl.Visible = visible
        self.xl.DisplayAlerts = False
        self.wb = self.xl.Workbooks.Open(self.path)

    def ws(self, name):
        return self.wb.Worksheets(name)

    def set(self, sheet, addr, value):
        c = self.ws(sheet).Range(addr)
        if isinstance(value, (datetime.date, datetime.datetime)):
            c.Value = value
        else:
            c.Value = value
        return c

    def formula(self, sheet, addr, f):
        self.ws(sheet).Range(addr).Formula = f

    def get(self, sheet, addr):
        return self.ws(sheet).Range(addr).Value

    def text(self, sheet, addr):
        return self.ws(sheet).Range(addr).Text

    def fill_rows(self, sheet, top_left_row, col_letters, rows):
        """rows: список списков значений; None — пропуск ячейки."""
        for i, row in enumerate(rows):
            for col, v in zip(col_letters, row):
                if v is not None:
                    self.set(sheet, f"{col}{top_left_row + i}", v)

    def recalc(self):
        self.xl.CalculateFull()

    def errors(self):
        out = []
        for ws in self.wb.Worksheets:
            try:
                rng = ws.UsedRange.SpecialCells(-4123, 16)   # формулы с ошибками
            except Exception:
                continue
            for c in rng.Cells:
                t = str(c.Text)
                if "#####" not in t:
                    out.append((ws.Name, c.Address.replace("$", ""), c.Formula, t))
        return out

    def charts(self):
        n = 0
        for ws in self.wb.Worksheets:
            n += ws.ChartObjects().Count
        return n

    def save(self):
        self.wb.Save()

    def close(self, save=True):
        try:
            if save:
                self.wb.Save()
            self.wb.Close(False)
        finally:
            self.xl.Quit()
