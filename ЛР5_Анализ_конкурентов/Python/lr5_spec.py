# -*- coding: utf-8 -*-
"""Описание изменений книги Excel в виде JSON-спецификации для PowerShell (COM)."""
import json
import os
import re

import lr5_common as C

EXCEL_DIR = os.path.join(C.LAB5, "Excel")
TPL_DIR = os.path.join(C.LAB5, "Материалы")


def col_index(letters):
    n = 0
    for ch in letters:
        n = n * 26 + (ord(ch) - 64)
    return n


def split_addr(addr):
    m = re.match(r"^([A-Z]+)(\d+)$", addr)
    return col_index(m.group(1)), int(m.group(2))


class Spec:
    def __init__(self, tpl_name, out_name):
        self.tpl = os.path.join(TPL_DIR, tpl_name)
        self.out = os.path.join(EXCEL_DIR, out_name)
        self.writes = []
        self.dv = []
        self.formulas = []
        self.autofit = []
        self.widths = []
        self.new_sheets = []
        self.clear = []
        self.extra = {}

    def w(self, sheet, addr, value):
        c, r = split_addr(addr)
        self._check(value)
        self.writes.append([sheet, r, c, value])

    def wrc(self, sheet, row, col, value):
        self._check(value)
        self.writes.append([sheet, row, col, value])

    def _check(self, v):
        if isinstance(v, str) and v and v[0] in "=+-@":
            raise ValueError("Строка начинается со служебного символа: " + v[:40])

    def row(self, sheet, row, start_col_letter, values):
        c0 = col_index(start_col_letter)
        for i, v in enumerate(values):
            if v is not None:
                self.wrc(sheet, row, c0 + i, v)

    def date(self, sheet, addr, iso="2026-09-30"):
        self.w(sheet, addr, {"d": iso})

    def fx(self, sheet, addr, formula):
        c, r = split_addr(addr)
        self.formulas.append([sheet, r, c, formula])

    def dv_list(self, sheet, rng, formula_or_list):
        self.dv.append(dict(sheet=sheet, range=rng, type="list", f1=formula_or_list))

    def dv_whole(self, sheet, rng, lo, hi):
        self.dv.append(dict(sheet=sheet, range=rng, type="whole", lo=lo, hi=hi))

    def fit(self, sheet, rng):
        self.autofit.append(dict(sheet=sheet, range=rng))

    def to_json(self, path):
        data = dict(template=self.tpl, out=self.out, writes=self.writes, dv=self.dv, formulas=self.formulas,
                    autofit=self.autofit, widths=self.widths, new_sheets=self.new_sheets, clear=self.clear, extra=self.extra)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        return path
