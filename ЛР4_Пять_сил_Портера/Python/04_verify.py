# -*- coding: utf-8 -*-
"""Расчёт на Python по тем же CSV и сверка с ячейками Excel (основной расчёт), плюс вариант Word и справочная нормировка.
Запуск: python 04_verify.py [--data папка] [--xlsx файл] [--json файл]"""
import os
import sys
import json
import argparse

sys.path.insert(0, os.path.dirname(__file__))
import lr4_io as io
import lr4_calc as C
from xl_com import Book, XLS


def compute(data_dir):
    sw = [r for r in io.read("sw02", data_dir) if r.get("include") != 0 and r.get("visits") is not None and r.get("geo") is not None]   # пустые каналы = 0, как в формулах Excel
    if not sw:
        return None
    s02 = C.sheet02(sw)
    s03 = C.sheet03(sw, s02["E"])
    q = [r for r in io.read("q04", data_dir) if io.complete("q04", r)]
    sites = [r["site"] for r in sw]
    rv = [r for r in io.read("rev05", data_dir) if r["site"] in sites and io.complete("rev05", r)]
    tc = [r for r in io.read("tech06", data_dir) if r["site"] in sites and io.complete("tech06", r)]
    s04, s05, s06 = C.sheet04(q), C.sheet05(rv), C.sheet06(tc)
    # B38 листов 05 и 06 считаются по всем строкам списка (COUNTA по столбцу A), в том числе с неполными данными
    rv_all = [r for r in io.read("rev05", data_dir) if r["site"] in sites]
    tc_all = [r for r in io.read("tech06", data_dir) if r["site"] in sites]
    s05["b38"] = sum(sum((r.get(k) or 0) for k in ("g2_n", "capterra_n", "trustpilot_n", "google_n")) for r in rv_all) / len(rv_all) if rv_all else None
    s06["b38"] = sum(1 for r in tc_all if r.get("app") == "да" or r.get("cabinet") == "да") / len(tc_all) if tc_all else None
    man = {r["field"]: r["value"] for r in io.read("manual07", data_dir)}
    s07 = None
    if None not in (s04["b37"], s05["b37"], s06["b37"]):
        s07 = C.sheet07(s02, s03, s04["b37"], s05["b37"], s06["b37"],
                        man.get("platform_dependency") or 0, man.get("substitute_threat") or 0)
    return dict(s02=s02, s03=s03, s04=s04, s05=s05, s06=s06, s07=s07, sw=sw,
                word=C.word_channels(sw, s02["E"], 3), word5=C.word_channels(sw, s02["E"], 5))


def main(data_dir, xlsx, out_json=None):
    res = compute(data_dir)
    if res is None:
        print("нет строк с полными данными: сверка значений листов 04-07 не выполнялась (реестр данных - from_prev_labs.py)")
        return
    b = Book(xlsx)
    try:
        g = lambda s, a: b.ws(s).Range(a).Value
        pairs = [("02!B38 CR3", g("02_Конкуренты_SW", "B38"), res["s02"]["excel"]["cr3"]),
                 ("02!B39 CR5", g("02_Конкуренты_SW", "B39"), res["s02"]["excel"]["cr5"]),
                 ("02!B40 HHI", g("02_Конкуренты_SW", "B40"), res["s02"]["excel"]["hhi"]),
                 ("02!B41 длительность", g("02_Конкуренты_SW", "B41"), res["s02"]["dur"]),
                 ("03!C5", g("03_Каналы_трафика", "C5"), res["s03"]["C"]["organic"]),
                 ("03!C6", g("03_Каналы_трафика", "C6"), res["s03"]["C"]["paid"]),
                 ("03!C10", g("03_Каналы_трафика", "C10"), res["s03"]["C"]["brand"]),
                 ("04!B37", g("04_Поиск_реклама", "B37"), res["s04"]["b37"]),
                 ("05!B37", g("05_Отзывы_рейтинги", "B37"), res["s05"]["b37"]),
                 ("05!B38", g("05_Отзывы_рейтинги", "B38"), res["s05"]["b38"]),
                 ("06!B37", g("06_Технологии_финансы", "B37"), res["s06"]["b37"]),
                 ("06!B38", g("06_Технологии_финансы", "B38"), res["s06"]["b38"]),
                 ("07!F13 индекс", g("07_Барьеры_входа", "F13"), res["s07"]["index"] if res["s07"] else None)]
        ok = True
        for n, x, y in pairs:
            err = isinstance(x, int) and x < -2146820000          # код ошибки Excel (#ДЕЛ/0! и т. п.)
            same = (y is None and err) or (x is not None and y is not None and not err and abs(x - y) < 1e-9)
            ok &= same
            print(f"{n:22} Excel={x!s:>22} Python={y!s:>22} {'OK' if same else 'РАСХОЖДЕНИЕ'}")
        print("Сверка:", "все значения совпадают" if ok else "ЕСТЬ РАСХОЖДЕНИЯ")
        if res["s07"]:
            print("Справочно (не основной): индекс с нормировкой на сумму весов =", round(res["s07"]["ref_index"], 4),
                  "| сумма весов =", round(res["s07"]["weights_sum"], 2), "| максимум по шаблону =", round(res["s07"]["max_index"], 2))
        else:
            print("Индекс барьеров не определён: нет данных листов 04-06 (в Excel #ДЕЛ/0!, в Python None) - согласовано")
        if out_json:
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump({k: v for k, v in res.items() if k != "sw"}, f, ensure_ascii=False, indent=1, default=str)
    finally:
        b.close(False)


if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("--data", default=io.DATA)
    a.add_argument("--xlsx", default=XLS)
    a.add_argument("--json")
    x = a.parse_args()
    main(x.data, x.xlsx, x.json)
