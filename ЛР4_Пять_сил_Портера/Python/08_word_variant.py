# -*- coding: utf-8 -*-
"""Вариант Word и итоговые оценки. Основа - снимок Similarweb PRO 30.09.2026 (data/sw02.csv, мировые визиты, доля географии 100 %);
для сравнения - Semrush (август 2026) и ЛР2-3. Индекс барьеров Excel при неполных листах 04-06: границы по шаблонным весам.
Результат - results_lr4.json. Запуск: python 08_word_variant.py"""
import os, sys, csv, json, statistics
sys.path.insert(0, os.path.dirname(__file__))
import lr4_io as io
import lr4_calc as C

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEM = os.path.join(ROOT, "Материалы_собранные", "semrush_website_overview_visits_2026-08_snyato_2026-09-30.csv")


def fmt(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


sw = [r for r in io.read("sw02") if r.get("include") != 0 and r.get("visits") is not None]
s02 = C.sheet02(sw)
s03 = C.sheet03(sw, s02["E"])
order = sorted(range(len(sw)), key=lambda i: -s02["F"][i])
top = [(sw[i]["site"], sw[i]["visits"], s02["F"][i]) for i in order]
nm = C.sheet02([r for r in sw if r["site"] != "miro.com"])
w3, w5 = C.word_channels(sw, s02["E"], 3), C.word_channels(sw, s02["E"], 5)
dur = [r["dur"] for r in sw if r["dur"]]
pg = [r["pages"] for r in sw if r["pages"]]
md, mp = statistics.mean(dur), statistics.mean(pg)
above = [r["site"] for r in sw if r["dur"] and r["pages"] and r["dur"] > md and r["pages"] > mp]

# Semrush (справочно): 8 доменов; тот же набор по Similarweb
with open(SEM, encoding="utf-8-sig", newline="") as f:
    sem = [r for r in csv.DictReader(f, delimiter=";") if r["visits_aug_2026"] and r["domain"] != "draw.io"]
srows = [dict(site=r["domain"], visits=float(r["visits_aug_2026"]), geo=None, dur=None) for r in sem]
ss = C.sheet02(srows)["word"]
names = {"diagrams.net": "app.diagrams.net"}
sub = [r for r in sw if r["site"] in {names.get(r["domain"], r["domain"]) for r in sem}]
ssw = C.sheet02(sub)["excel"]

# индекс барьеров Excel при неполных 04-06
man = {r["field"]: r["value"] for r in io.read("manual07")}
c11, c12 = man["platform_dependency"], man["substitute_threat"]
D = dict(d4=s02["score_excel"], d5=s03["S"]["organic"], d7=s03["S"]["brand"], d11=C.score3(c11, 0.7, 0.4), d12=C.score3(c12, 0.7, 0.4))
W = C.WEIGHTS
known = D["d4"] * W[0] + D["d5"] * W[1] + D["d7"] * W[3] + D["d11"] * W[7] + D["d12"] * W[8]
# D6 = среднее(03!C6; 04!B37): при 03!C6 < 0,01 и 04!B37 <= 1 значение не выше 0,51 -> балл 1 или 3; D8, D9, D10 - 1..5
lo = known + W[2] * 1 + (W[4] + W[5] + W[6]) * 1
hi = known + W[2] * 3 + (W[4] + W[5] + W[6]) * 5
lvl = lambda x: "высокие барьеры" if x >= 4 else "средние барьеры" if x >= 2.5 else "низкие барьеры"
sw_sum = sum(W)

crit = io.read("word_criteria")
wlo, whi, llo, lhi = C.word_index([(r["score_min"], r["score_max"]) for r in crit])
ma = [r["score"] for r in io.read("matrix_a")]
m6, l6, m5, l5 = C.matrix_a(ma)
mb = [r["score_0_3"] for r in io.read("matrix_b")]

res = dict(
    sw=dict(n=len(sw), total=s02["total"], top=top, cr3=s02["excel"]["cr3"], cr5=s02["excel"]["cr5"], hhi=s02["excel"]["hhi"], score=s02["score_excel"],
            cr3_nm=nm["excel"]["cr3"], cr5_nm=nm["excel"]["cr5"], hhi_nm=nm["excel"]["hhi"], total_nm=nm["total"], dur=s02["dur"],
            C=s03["C"], D=s03["D"], S=s03["S"], w3=w3, w5=w5, mean_dur=md, mean_pages=mp, above=above),
    semrush=dict(n=len(srows), total=sum(r["visits"] for r in srows), cr3=ss["cr3"], cr5=ss["cr5"], hhi=ss["hhi"], sw_same_cr3=ssw["cr3"], sw_same_cr5=ssw["cr5"], sw_same_hhi=ssw["hhi"]),
    excel_index=dict(known=known, lo=lo, hi=hi, lvl_lo=lvl(lo), lvl_hi=lvl(hi), ref_lo=lo / sw_sum, ref_hi=hi / sw_sum, D=D, c11=c11, c12=c12),
    word_index=dict(lo=wlo, hi=whi, level_lo=llo, level_hi=lhi),
    matrix_a=dict(scores=ma, m6=m6, l6=l6, m5=m5, l5=l5), matrix_b=mb, weights_sum=sw_sum, max_index=5 * sw_sum)
json.dump(res, open(os.path.join(os.path.dirname(__file__), "results_lr4.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("SW: n", len(sw), "CR3", fmt(s02["excel"]["cr3"] * 100), "CR5", fmt(s02["excel"]["cr5"] * 100), "HHI", fmt(s02["excel"]["hhi"], 0), "балл", s02["score_excel"])
print("без miro CR3", fmt(nm["excel"]["cr3"] * 100), "HHI", fmt(nm["excel"]["hhi"], 0))
print("Semrush 8: CR3", fmt(ss["cr3"] * 100), "HHI", fmt(ss["hhi"], 0), "| SW тот же набор:", fmt(ssw["cr3"] * 100), fmt(ssw["hhi"], 0))
print("Excel-индекс границы:", fmt(lo, 2), fmt(hi, 2), lvl(lo), lvl(hi), "известные", fmt(known, 2), D)
print("Word:", fmt(wlo, 2), fmt(whi, 3), llo, lhi, "| A", m6, l6, m5, "| B", mb)
