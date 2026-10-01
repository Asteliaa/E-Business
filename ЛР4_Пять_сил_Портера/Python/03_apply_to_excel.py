# -*- coding: utf-8 -*-
"""Перенос входных CSV в рабочую копию Excel через COM, протяжка формул 04-06 на заполненные строки (Д5), пересчёт.
Запуск: python 03_apply_to_excel.py [--data папка] [--xlsx файл]"""
import os
import sys
import argparse

sys.path.insert(0, os.path.dirname(__file__))
import lr4_io as io
from xl_com import Book, XLS

FORM = {  # лист: {столбец: формула с {r}} (копии формул шаблона)
    "04_Поиск_реклама": {
        "K": "=MIN(1,AVERAGE(MIN(E{r}/2,1),F{r},G{r}/100,MIN(H{r}/10,1),MIN(J{r}/50,1)))",
        "L": "=IF(K{r}>=0.7,5,IF(K{r}>=0.4,3,1))"},
    "05_Отзывы_рейтинги": {
        "L": "=MIN(1,AVERAGE(IFERROR(AVERAGE(B{r},D{r},F{r},H{r})/5,0),MIN((C{r}+E{r}+G{r}+I{r})/300,1),MIN(J{r}/30,1),MIN(K{r}/10,1)))",
        "M": "=IF(L{r}>=0.7,5,IF(L{r}>=0.4,3,1))"},
    "06_Технологии_финансы": {
        "K": '=MIN(1,AVERAGE(MIN(B{r}/500000,1),MIN(C{r}/60,1),D{r}/5,E{r}/5,IF(F{r}="да",1,0),IF(G{r}="да",1,0),MIN(H{r}/50,1),MIN(I{r}/6,1),IF(J{r}>0,1,0)))',
        "L": "=IF(K{r}>=0.7,5,IF(K{r}>=0.4,3,1))"},
}


def main(data_dir, xlsx):
    b = Book(xlsx)
    log = []
    try:
        sw = [r for r in io.read("sw02", data_dir) if r.get("include") != 0]
        sites = [r["site"] for r in sw]
        import csv as _csv
        with open(os.path.join(data_dir, "sw02.csv"), encoding="utf-8-sig", newline="") as _f:
            raw_sw = [r for r in _csv.DictReader(_f, delimiter=";") if r.get("include") != "0"]
        sheets = {"sw02": sw,
                  "q04": io.read("q04", data_dir),
                  "rev05": [r for r in io.read("rev05", data_dir) if r["site"] in sites],
                  "tech06": [r for r in io.read("tech06", data_dir) if r["site"] in sites]}
        for name, rows in sheets.items():
            sheet, cols = io.SPEC[name]
            ws = b.ws(sheet)
            for col in cols.values():
                ws.Range(f"{col}4:{col}33").ClearContents()
            if sheet in FORM:
                for col in FORM[sheet]:
                    ws.Range(f"{col}4:{col}33").ClearContents()
            raw = raw_sw if name == "sw02" else None
            for i, row in enumerate(rows[:30]):
                r = 4 + i
                for k, col in cols.items():
                    if row.get(k) is not None:
                        ws.Range(f"{col}{r}").Value = row[k]
                    elif raw is not None and k in ("visits", "geo") and raw[i].get(k, "").startswith("🔲"):
                        ws.Range(f"{col}{r}").Value = raw[i][k]     # отметка об отсутствии данных; в формулах даёт 0
                if sheet in FORM:
                    if io.complete(name, row):
                        for col, f in FORM[sheet].items():
                            ws.Range(f"{col}{r}").Formula = f.format(r=r)
                    else:
                        log.append(f"{sheet} строка {r} ({row.get('site') or row.get('query')}): неполные данные, формулы не протянуты")
        man = {r["field"]: r["value"] for r in io.read("manual07", data_dir)}
        w7 = b.ws("07_Барьеры_входа")
        for field, cell in (("platform_dependency", "C11"), ("substitute_threat", "C12")):
            w7.Range(cell).ClearContents()
            if man.get(field) is not None:
                w7.Range(cell).Value = man[field]
        w7.Range("E13").Formula = "=SUM(E4:E12)"
        b.xl.CalculateFull()
        errs = []
        for ws in b.wb.Worksheets:
            try:
                errs += [(ws.Name, c.Address, c.Text) for c in ws.UsedRange.SpecialCells(-4123, 16).Cells]
            except Exception:
                pass
        log.append(f"ошибок формул: {len(errs)}")
    finally:
        b.close(True)
    print("\n".join(log))


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--data", default=io.DATA)
    a.add_argument("--xlsx", default=XLS)
    x = a.parse_args()
    main(x.data, x.xlsx)
