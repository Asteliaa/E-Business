# -*- coding: utf-8 -*-
"""Построение рисунков отчёта ЛР2-3 (PNG, 200 dpi) по собранным данным и results.json."""
import json
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(HERE), "Рисунки")
os.makedirs(OUT, exist_ok=True)
R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": 0.3})
C = ["#1f4e79", "#c0504d", "#4f8f3a", "#e0a400", "#6a5acd", "#7f7f7f"]
MLAB = [f"{y % 100:02d}-{m:02d}" for y, m in I.MONTHS_24]
MLAB12 = MLAB[12:]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=200)
    plt.close(fig)
    print("saved", name)


# 1. Динамика Вордстата: ядро, 24 месяца
fig, ax = plt.subplots(figsize=(9, 4.2))
for q, c in zip(["uml", "bpmn", "plantuml", "idef0"], C):
    ax.plot(MLAB, I.WS_ALL[q]["m"], marker="o", ms=3, label=q, color=c)
ax.set_xticks(range(0, 24, 2)); ax.set_xticklabels(MLAB[::2], rotation=45)
ax.set_ylabel("запросов в месяц"); ax.legend(ncol=4, frameon=False)
save(fig, "01_wordstat_dinamika_yadro_RB.png")

# 2. Частотность (Топы, 30 дней): ядро и заменители
names = ["miro", "visio", "draw io", "uml", "bpmn", "plantuml", "idef0", "нейросеть схема", "excalidraw", "diagrams.net", "visual paradigm", "нейросеть диаграмма", "dfd диаграмма", "erd диаграмма", "lucidchart", "mermaid diagram"]
vals = [I.WS_ALL[n]["top"] for n in names]
fig, ax = plt.subplots(figsize=(9, 5))
cols = [C[1] if n in ("miro", "visio", "draw io", "excalidraw", "diagrams.net", "visual paradigm", "lucidchart") else C[0] for n in names]
ax.barh(names[::-1], vals[::-1], color=cols[::-1])
for i, v in enumerate(vals[::-1]):
    ax.text(v + 15, i, str(v), va="center", fontsize=8)
ax.set_xlabel("запросов за 30 дней (25.08–23.09.2026), Беларусь")
save(fig, "02_wordstat_topy_yadro_i_zameniteli_RB.png")

# 3. Группы запросов и взвешенный спрос (12 мес.)
ps = R["ps"]
fig, ax = plt.subplots(figsize=(9, 4.2))
bottom = np.zeros(12)
for g, c in zip(["Коммерческие запросы", "Проблемные запросы", "Инструментальные запросы"], C):
    v = np.array(I.GROUP_SERIES[g]); ax.bar(MLAB12, v, bottom=bottom, label=g, color=c); bottom += v
ax.plot(MLAB12, ps["H"], color="black", marker="o", ms=3, label="взвешенная частотность")
ax.set_ylabel("запросов в месяц"); ax.legend(frameon=False, fontsize=8); plt.setp(ax.get_xticklabels(), rotation=45)
save(fig, "03_gruppy_zaprosov_i_vzveshennyy_spros.png")

# 4. Google Trends: недельные значения (Беларусь, 12 месяцев)
rows = I.load_gt_weekly()
fig, ax = plt.subplots(figsize=(9, 3.8))
x = np.arange(len(rows))
for k, c in zip(["UML", "BPMN", "PlantUML", "IDEF0"], C):
    ax.plot(x, [float(r[k]) for r in rows], marker="o", ms=3, lw=1, label=k, color=c)
ax.set_xticks(x[::6]); ax.set_xticklabels([r["week_start"][2:] for r in rows][::6], rotation=45)
ax.set_ylabel("индекс GT (0–100)"); ax.legend(ncol=4, frameon=False)
save(fig, "04_google_trends_nedeli_RB.png")

# 5. Выборка Similarweb
fig, ax = plt.subplots(figsize=(8, 3.8))
d = I.SW_DOMAINS
b = ax.bar([x[0] for x in d], [x[3] for x in d], color=[C[0] if "ФАКТ" in x[4] else C[5] for x in d])
ax.set_yscale("log"); ax.set_ylabel("визитов в месяц (лог. шкала)")
for r, x_ in zip(b, d):
    ax.text(r.get_x() + r.get_width() / 2, x_[3] * 1.15, f"{x_[3]:,}".replace(",", " "), ha="center", fontsize=8)
ax.set_ylim(1e4, 3e7)
save(fig, "05_similarweb_vyborka_vizity.png")

# 6. Доли трафика и HHI
sw = R["sw"]
fig, ax = plt.subplots(figsize=(6.5, 4))
sh = sw["shares"]
ax.bar(sh.keys(), [v * 100 for v in sh.values()], color=C[0])
for i, v in enumerate(sh.values()):
    ax.text(i, v * 100 + 1, f"{v * 100:.1f} %", ha="center", fontsize=8)
ax.set_ylabel("доля в суммарных визитах выборки, %")
ax.set_title(f"CR3 = {sw['cr3']:.1f} %, HHI = {sw['hhi']:.0f} (высокая)", fontsize=10)
plt.setp(ax.get_xticklabels(), rotation=15)
save(fig, "06_doli_trafika_CR3_HHI.png")


def ranges_plot(data, title_x, name, figsize=(9, 4.6)):
    fig, ax = plt.subplots(figsize=figsize)
    keys = list(data.keys())[::-1]
    for i, k in enumerate(keys):
        lo, ba, hi = data[k]
        ax.plot([max(lo, 0.5), hi], [i, i], color=C[0], lw=6, alpha=0.35, solid_capstyle="round")
        ax.plot([ba], [i], "D", color=C[1], ms=7)
        ax.plot([max(lo, 0.5)], [i], "|", color=C[0], ms=12); ax.plot([hi], [i], "|", color=C[0], ms=12)
    ax.set_yticks(range(len(keys))); ax.set_yticklabels(keys, fontsize=8)
    ax.set_xscale("log"); ax.set_xlabel(title_x)
    save(fig, name)


ranges_plot(R["summary"]["SOM"], "достижимая выручка (SOM), BYN/год; ромб — базовый сценарий (лог. шкала)", "07_diapazony_SOM_po_metodam.png")
ranges_plot(R["summary"]["MARKET"], "объём рынка (SAM), BYN/год; ромб — базовый сценарий (лог. шкала)", "08_diapazony_rynka_po_metodam.png")

# 9. ПК: SAM и SOM по сегментам
pk = R["pk"]
fig, ax = plt.subplots(figsize=(8, 4))
lab = [s["code"] for s in I.SEGMENTS]
xx = np.arange(3)
ax.bar(xx - 0.2, pk["sam_seg"], 0.4, label="SAM", color=C[0]); ax.bar(xx + 0.2, pk["som_seg"], 0.4, label="SOM", color=C[1])
for i in range(3):
    ax.text(i - 0.2, pk["sam_seg"][i], f"{pk['sam_seg'][i]:,.0f}".replace(",", " "), ha="center", va="bottom", fontsize=8)
    ax.text(i + 0.2, pk["som_seg"][i], f"{pk['som_seg'][i]:,.0f}".replace(",", " "), ha="center", va="bottom", fontsize=8)
ax.set_xticks(xx); ax.set_xticklabels(lab); ax.set_ylabel("BYN в год"); ax.legend(frameon=False)
save(fig, "09_PK_SAM_SOM_po_segmentam.png")

# 10. Ценовой коридор
import statistics
prods = ["Miro", "Lucidchart", "Mermaid Chart", "Visual Paradigm Online", "Creately", "Eraser", "Whimsical", "dbdiagram.io"]
mn, md, mx = [], [], []
for p in prods:
    ps_ = [x[2] * I.FX for x in I.PRICES if x[0] == p]
    mn.append(min(ps_)); md.append(statistics.median(ps_)); mx.append(max(ps_))
fig, ax = plt.subplots(figsize=(9, 4.2))
y = np.arange(len(prods))
ax.hlines(y, mn, mx, color=C[0], lw=5, alpha=0.4); ax.plot(md, y, "o", color=C[1], label="медиана тарифов")
ax.plot(mn, y, "|", color=C[0], ms=10); ax.plot(mx, y, "|", color=C[0], ms=10)
ax.axvline(I.PRICE_BYN_MONTH, color=C[2], ls="--", label=f"NotaCode Pro, {I.PRICE_BYN_MONTH:.2f} BYN")
ax.set_yticks(y); ax.set_yticklabels(prods); ax.set_xscale("log"); ax.set_xlabel("цена платных тарифов, BYN в месяц (оплата за год; лог. шкала)")
ax.legend(frameon=False, loc="lower right")
save(fig, "10_cenovoy_koridor_konkurentov.png")

# 11. Маркетплейсы расширений
mp = R["mp"]["rows"]
items = [(r[1].split(" (")[0][:30] + " [VS Code]", r[2]) for r in mp if r[0].startswith("VS Marketplace") and r[2]][:8]
items += [(r[1].split(" (")[0][:30] + " [JetBrains]", r[2]) for r in mp if r[0].startswith("JetBrains") and r[2]][:5]
items.sort(key=lambda t: t[1])
fig, ax = plt.subplots(figsize=(9, 5))
ax.barh([i[0] for i in items], [i[1] / 1e6 for i in items], color=C[0])
ax.set_xlabel("установки / загрузки, млн (VS Marketplace и JetBrains Marketplace, 30.09.2026)")
plt.setp(ax.get_yticklabels(), fontsize=7)
save(fig, "11_marketplejsy_rasshireniy_ustanovki.png")

# 12. Торнадо чувствительности SAM ПК по коэффициентам К1–К5 (диапазоны ПК табл. 7)
base = {"К1": 0.30, "К2": 0.225, "К3": 0.55, "К4": 0.175}
lo_hi = {"К1": (0.15, 0.50), "К2": (0.10, 0.40), "К3": (0.30, 0.80), "К4": (0.075, 0.325)}
pop = sum(s["pop"] for s in I.SEGMENTS)
def sam(k): return pop * k["К1"] * k["К2"] * k["К3"] * k["К4"] * round(I.PRICE_BYN_YEAR_BASE, 2)
b0 = sam(base)
fig, ax = plt.subplots(figsize=(8, 3.8))
for i, k in enumerate(base):
    lo = dict(base); lo[k] = lo_hi[k][0]; hi = dict(base); hi[k] = lo_hi[k][1]
    ax.barh(i, sam(hi) - b0, left=b0, color=C[2]); ax.barh(i, sam(lo) - b0, left=b0, color=C[1])
ax.axvline(b0, color="black"); ax.set_yticks(range(4)); ax.set_yticklabels(list(base)); ax.invert_yaxis()
ax.set_xlabel(f"SAM, BYN/год (базовый {b0:,.0f} при одинаковых К для всех сегментов)".replace(",", " "))
save(fig, "12_chuvstvitelnost_SAM_K1_K4.png")

# 13. Воронка: поиск (ПС-X) и подписка
fig, ax = plt.subplots(figsize=(8, 3.8))
lab = ["Осторожный", "Базовый", "Оптимистичный"]
ax.bar(np.arange(3) - 0.2, ps["rev_year"], 0.4, label="ПС-X: поисковый канал", color=C[0])
ax.bar(np.arange(3) + 0.2, R["cv"]["rev_year"], 0.4, label="ЦВ-X: воронка", color=C[1])
ax.set_xticks(range(3)); ax.set_xticklabels(lab); ax.set_ylabel("BYN в год"); ax.set_yscale("log"); ax.legend(frameon=False)
save(fig, "13_voronka_poisk_i_CV.png")
