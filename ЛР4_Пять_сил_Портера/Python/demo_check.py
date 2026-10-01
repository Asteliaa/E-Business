# -*- coding: utf-8 -*-
"""Проверка конвейера на демоданных самого шаблона (временная копия вне проекта):
значения «до/после» исправлений Д2-Д6 и сверка Python с Excel."""
import os, shutil, sys, json, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import lr4_calc as C
from xl_com import Book, XLS

tmp = os.path.join(tempfile.gettempdir(), "lr4_demo.xlsx")
shutil.copy(XLS, tmp)
b = Book(tmp)
res = {}
try:
    g = lambda s, a: b.ws(s).Range(a).Value
    t = lambda s, a: b.ws(s).Range(a).Text
    res["before"] = {"01!B8": t("01_Параметры", "B8"), "01!B9": t("01_Параметры", "B9"), "01!B10": t("01_Параметры", "B10"),
                     "05!B38": t("05_Отзывы_рейтинги", "B38"), "06!B38": t("06_Технологии_финансы", "B38"),
                     "07!E13": t("07_Барьеры_входа", "E13"), "07!F13": t("07_Барьеры_входа", "F13"),
                     "07!sumE": b.xl.WorksheetFunction.Sum(b.ws("07_Барьеры_входа").Range("E4:E12"))}
    # исправления Д2-Д6
    p = b.ws("01_Параметры")
    p.Range("B10").Formula = "=SUM('02_Конкуренты_SW'!E4:E33)"
    p.Range("B9").Formula = "=COUNTA('02_Конкуренты_SW'!A4:A33)"
    b.ws("05_Отзывы_рейтинги").Range("B38").Formula = "=SUMPRODUCT(C4:C33+E4:E33+G4:G33+I4:I33)/COUNTA(A4:A33)"
    b.ws("06_Технологии_финансы").Range("B38").Formula = '=SUMPRODUCT(--(((F4:F33="да")+(G4:G33="да"))>0))/COUNTA(A4:A33)'
    b.ws("07_Барьеры_входа").Range("E13").Formula = "=SUM(E4:E12)"
    b.xl.CalculateFull()
    res["after"] = {"01!B9": t("01_Параметры", "B9"), "01!B10": t("01_Параметры", "B10"),
                    "05!B38": t("05_Отзывы_рейтинги", "B38"), "06!B38": t("06_Технологии_финансы", "B38"),
                    "07!E13": t("07_Барьеры_входа", "E13"), "07!F13": t("07_Барьеры_входа", "F13")}
    # данные демо
    w2 = b.ws("02_Конкуренты_SW"); rows2 = []
    for r in range(4, 34):
        if w2.Cells(r, 1).Value:
            v = [w2.Cells(r, c).Value for c in range(1, 17)]
            rows2.append(dict(site=v[0], visits=v[2], geo=v[3], dur=v[6], direct=v[9], organic=v[10], paid=v[11],
                              social=v[12], referral=v[13], display=v[14], brand_search=v[15]))
    s02 = C.sheet02(rows2); s03 = C.sheet03(rows2, s02["E"])
    w4 = b.ws("04_Поиск_реклама"); r4 = []
    for r in range(4, 34):
        if w4.Cells(r, 1).Value:
            v = [w4.Cells(r, c).Value for c in range(1, 11)]
            r4.append(dict(cpc=v[4], ppc=v[5], seo=v[6], top=v[7], ads=v[9]))
    s04 = C.sheet04(r4)
    w5 = b.ws("05_Отзывы_рейтинги"); r5 = []
    for r in range(4, 34):
        if w5.Cells(r, 1).Value:
            v = [w5.Cells(r, c).Value for c in range(1, 12)]
            r5.append(dict(g2=v[1], g2_n=v[2], capterra=v[3], capterra_n=v[4], trustpilot=v[5], trustpilot_n=v[6],
                           google_rating=v[7], google_n=v[8], cases=v[9], age=v[10]))
    s05 = C.sheet05(r5)
    w6 = b.ws("06_Технологии_финансы"); r6 = []
    for r in range(4, 34):
        if w6.Cells(r, 1).Value:
            v = [w6.Cells(r, c).Value for c in range(1, 11)]
            r6.append(dict(fund=v[1], staff=v[2], stack=v[3], crm=v[4], app=v[5], cabinet=v[6], ads=v[7], jobs=v[8], assets=v[9]))
    s06 = C.sheet06(r6)
    w7 = b.ws("07_Барьеры_входа")
    s07 = C.sheet07(s02, s03, s04["b37"], s05["b37"], s06["b37"], w7.Range("C11").Value, w7.Range("C12").Value)
    cmp = [("02!B38 CR3", g("02_Конкуренты_SW", "B38"), s02["excel"]["cr3"]),
           ("02!B39 CR5", g("02_Конкуренты_SW", "B39"), s02["excel"]["cr5"]),
           ("02!B40 HHI", g("02_Конкуренты_SW", "B40"), s02["excel"]["hhi"]),
           ("02!B41 длит.", g("02_Конкуренты_SW", "B41"), s02["dur"]),
           ("03!C5 органика", g("03_Каналы_трафика", "C5"), s03["C"]["organic"]),
           ("03!C6 платный", g("03_Каналы_трафика", "C6"), s03["C"]["paid"]),
           ("03!C10 бренд", g("03_Каналы_трафика", "C10"), s03["C"]["brand"]),
           ("04!B37", g("04_Поиск_реклама", "B37"), s04["b37"]),
           ("04!B38", g("04_Поиск_реклама", "B38"), s04["b38"]),
           ("05!B37", g("05_Отзывы_рейтинги", "B37"), s05["b37"]),
           ("05!B38 (после)", g("05_Отзывы_рейтинги", "B38"), s05["b38"]),
           ("06!B37", g("06_Технологии_финансы", "B37"), s06["b37"]),
           ("06!B38 (после)", g("06_Технологии_финансы", "B38"), s06["b38"]),
           ("07!F13 индекс", g("07_Барьеры_входа", "F13"), s07["index"])]
    res["cmp"] = [(n, x, y, abs(x - y) < 1e-9) for n, x, y in cmp]
    res["ref_index"] = s07["ref_index"]; res["max"] = s07["max_index"]
    res["n"] = len(rows2)
finally:
    b.close(False)
for k, v in res.items():
    print(k, json.dumps(v, ensure_ascii=False, default=str))
