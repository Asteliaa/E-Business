# -*- coding: utf-8 -*-
"""Формирует data/sw02.csv из снимка Similarweb PRO (Материалы_собранные/similarweb_pro_obzor_2026-09-30.csv).
Правила: visits = monthly_visits (лист 02 принимает месячные визиты; eraser.io - 3-месячное значение / 3);
geo = 1 (мировые визиты, решение пользовательницы: релевантность географии не учтена);
direct, organic, paid, referral, display - доли из снимка; social = social_org + social_paid;
brand_search = branded_pct_aug x (organic + paid search) - допущение Р-15 (Similarweb даёт долю брендовых запросов в поиске, не в общем трафике);
N/A и 'нет данных' - пусто (в формулах 0). email и genai в шаблоне нет - в комментарий."""
import csv, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "Материалы_собранные", "similarweb_pro_obzor_2026-09-30.csv")
OLD = os.path.join(os.path.dirname(__file__), "data", "sw02.csv")
types = {}
for r in csv.DictReader(open(OLD, encoding="utf-8-sig"), delimiter=";"):
    types[r["site"]] = (r["type"], r["comment"].split(";")[0])
def num(s):
    s = (s or "").strip().replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None
def sec(t):
    try:
        h, m, s = t.split(":"); return int(h) * 3600 + int(m) * 60 + int(s)
    except Exception:
        return None
def fmt(x, n=6):
    return "" if x is None else repr(round(x, n))
cols = ["include", "site", "type", "visits", "geo", "dur", "pages", "bounce", "direct", "organic", "paid", "social", "referral", "display", "brand_search", "comment"]
rows = []
for r in csv.DictReader(open(SRC, encoding="utf-8-sig"), delimiter=";"):
    d = r["domain"]
    if d == "app.diagrams.net": pass
    tot = num(r["total_visits_3m"]); mv = num(r["monthly_visits"])
    visits = mv if mv is not None else (tot / 3 if tot else None)
    p = lambda k: (num(r[k]) / 100 if num(r[k]) is not None else None)
    org, paid, dr = p("organic_pct"), p("paid_search_pct"), p("direct_pct")
    so, sp = p("social_org_pct"), p("social_paid_pct")
    social = None if (so is None and sp is None) else (so or 0) + (sp or 0)
    br = num(r["branded_pct_aug"])
    brand = None
    if br is not None and org is not None:
        brand = br / 100 * (org + (paid or 0))
    note = []
    if r["email_pct"]: note.append("email " + r["email_pct"] + " %")
    if r["genai_pct"]: note.append("genai " + r["genai_pct"] + " %")
    note.append("Similarweb PRO 30.09.2026, Jun-Aug 2026, весь мир; доля Беларуси недоступна, основной расчёт по мировым визитам (geo = 100 %)")
    if d == "stormbpmn.com": note.append("справочно: Беларусь 2,49 % трафика (пятая страна)")
    if d == "eraser.io": note.append("визиты = 3-месячное значение / 3 (сравнение на странице plantuml.com); каналы и вовлечённость не показаны")
    if d == "drawsql.app": note.append("каналы и география: недостаточно данных")
    if d in ("mermaidchart.com", "lucidchart.com"): note.append("резкое падение трафика к прошлому месяцу, возможна смена домена")
    if br is None: note.append("брендовый поиск: нет данных")
    if r["comment"] and "affiliates" not in r["comment"][:0]: pass
    typ = types.get(d, ("цифровой сервис", ""))[0]
    rows.append([1, d, typ, fmt(visits, 1), 1, sec(r["duration"]) if sec(r["duration"]) is not None else "", r["pages_visit"],
                 fmt(num(r["bounce_pct"]) / 100 if num(r["bounce_pct"]) is not None else None), fmt(dr), fmt(org), fmt(paid), fmt(social), fmt(p("referral_pct")), fmt(p("display_pct")), fmt(brand), "; ".join(note)])
rows.append([0, "camunda.com", "другое", "", "", "", "", "", "", "", "", "", "", "", "", "не прошёл проверку релевантности: главная страница - платформа оркестрации процессов, трафик домена не отражает редактор Modeler"])
with open(OLD, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f, delimiter=";"); w.writerow(cols); w.writerows(rows)
print(len(rows))
