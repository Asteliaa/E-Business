# -*- coding: utf-8 -*-
"""Чтение входных CSV (разделитель «;»). Пустая ячейка и значения, начинающиеся с 🔲, считаются «нет данных»."""
import csv, os

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

SPEC = {   # файл: (лист, первая строка, {поле: буква столбца Excel}, числовые поля)
    "sw02": ("02_Конкуренты_SW", {"site": "A", "type": "B", "visits": "C", "geo": "D", "dur": "G", "pages": "H", "bounce": "I",
             "direct": "J", "organic": "K", "paid": "L", "social": "M", "referral": "N", "display": "O", "brand_search": "P", "comment": "Q"}),
    "q04": ("04_Поиск_реклама", {"query": "A", "intent": "B", "source": "C", "freq": "D", "cpc": "E", "ppc": "F", "seo": "G",
            "top": "H", "advertisers": "I", "ads": "J", "comment": "M"}),
    "rev05": ("05_Отзывы_рейтинги", {"site": "A", "g2": "B", "g2_n": "C", "capterra": "D", "capterra_n": "E", "trustpilot": "F",
              "trustpilot_n": "G", "google_rating": "H", "google_n": "I", "cases": "J", "age": "K", "comment": "N"}),
    "tech06": ("06_Технологии_финансы", {"site": "A", "fund": "B", "staff": "C", "stack": "D", "crm": "E", "app": "F",
               "cabinet": "G", "ads": "H", "jobs": "I", "assets": "J", "comment": "M"}),
}
TEXT = {"field", "criterion", "force", "n", "site", "type", "comment", "query", "intent", "source", "app", "cabinet"}
REQUIRED = {"sw02": ["visits", "geo", "direct", "organic", "paid", "social", "referral", "display"],
            "q04": ["cpc", "ppc", "seo", "top", "ads"],
            "rev05": ["cases", "age"],
            "tech06": ["fund", "staff", "stack", "crm", "app", "cabinet", "ads", "jobs", "assets"]}


def _val(k, s):
    s = (s or "").strip()
    if not s or s.startswith("🔲"):
        return None
    if k in TEXT:
        return s
    return float(s.replace(",", "."))


def read(name, data_dir=DATA):
    path = os.path.join(data_dir, name + ".csv")
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = [{k: _val(k, v) for k, v in r.items()} for r in csv.DictReader(f, delimiter=";")]
    return rows


def complete(name, row):
    return all(row.get(k) is not None for k in REQUIRED[name])
