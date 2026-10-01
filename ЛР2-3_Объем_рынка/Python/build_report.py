# -*- coding: utf-8 -*-
"""Сборка ОТЧЕТ.md из частей rep_part*.py (числа берутся из results.json и Excel-копий)."""
import importlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rep_common import Doc, source_list, ROOT

PARTS = [p for p in sys.argv[1:] if not p.startswith("-")] or ["rep_part1", "rep_part2", "rep_part3", "rep_part4", "rep_part5"]


def main():
    d = Doc()
    for p in PARTS:
        try:
            mod = importlib.import_module(p)
        except ModuleNotFoundError as e:
            if e.name == p:
                print("пропущена часть", p)
                continue
            raise
        mod.build(d)
        if p == "rep_part4":
            d.h(2, "Список использованных источников")
            d.add("{{SOURCES}}")
    txt = d.text().replace("{{SOURCES}}", source_list())
    if len(PARTS) >= 5:
        with open(os.path.join(ROOT, "ОТЧЕТ.md"), "w", encoding="utf-8") as f:
            f.write(txt)
        lst = ["# Список рисунков ЛР2-3", "", "Рисунки построены скриптом Python/make_figures.py по данным Материалы_собранные и results.json; подписи — как в отчёте.", "", "| № | Файл | Подпись в отчёте | Скрипт |", "|---|---|---|---|"]
        for k, num in sorted(d.fig.items(), key=lambda t: t[1]):
            f, t = d.figinfo[k]
            lst.append(f"| {num} | Рисунки/{f} | {t} | Python/make_figures.py |")
        open(os.path.join(ROOT, "Рисунки", "СПИСОК_РИСУНКОВ.md"), "w", encoding="utf-8").write(chr(10).join(lst) + chr(10))
        print("ОТЧЕТ.md записан:", len(txt), "символов; таблиц", len(d.tab), "рисунков", len(d.fig))
    else:
        out = os.path.join(ROOT, "Python", "_preview.md")
        open(out, "w", encoding="utf-8").write(txt)
        print("предпросмотр:", out, len(txt), "символов; таблиц", len(d.tab), "рисунков", len(d.fig))


if __name__ == "__main__":
    main()
