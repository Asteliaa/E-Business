# -*- coding: utf-8 -*-
"""Рисунки ЛР5: карта конкурентной близости (лист 07_Карта), итоговые баллы сравнения (06_Сравнение), доли признаков (07_Стандарт_рынка)."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import lr5_common as C
import lr5_xl as X
import spec_bc as B

OUT = os.path.join(C.LAB5, "Рисунки")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})
INK = "#222222"
LEV = {"Прямой конкурент": ("#222222", "o"), "Близкий альтернативный конкурент": ("#555555", "s"), "Косвенный конкурент / заменитель": ("#888888", "^"),
       "Смежная или потенциальная конкуренция": ("#BBBBBB", "D"), "Недостаточно данных": ("#222222", "x")}


def fig_map():
    book = os.path.join(C.LAB5, "Excel", "klassifikaciya_urovni_konkurencii_NotaCode.xlsx")
    d = X.read(book, ["07_Карта!A4:G25", "04_Оценка!A4:S25"])
    pts = []
    for r in range(4, 26):
        name = d.get(("07_Карта", r, 2), "")
        x, y = C.num(d.get(("07_Карта", r, 3))), C.num(d.get(("07_Карта", r, 4)))
        lvl = d.get(("07_Карта", r, 6), "")
        if name and x is not None and y is not None:
            pts.append((name, x, y, lvl))
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.add_patch(plt.Rectangle((4, 4), 1.1, 1.1, color="#E6E6E6", zorder=0))
    ax.text(4.95, 4.95, "ядро прямой конкуренции", ha="right", va="top", fontsize=9, style="italic")
    ax.axvline(3, color="#999999", lw=0.8, ls="--")
    ax.axhline(3, color="#999999", lw=0.8, ls="--")
    ax.axvline(4, color="#999999", lw=0.8, ls=":")
    ax.axhline(4, color="#999999", lw=0.8, ls=":")
    seen = set()
    offs = {}
    for name, x, y, lvl in pts:
        col, mk = LEV.get(lvl, ("#222222", "x"))
        k = (round(x, 2), round(y, 2))
        n = offs.get(k, 0)
        offs[k] = n + 1
        x, y = x + 0.07 * n, y - 0.07 * n
        ax.scatter(x, y, s=70, c=col, marker=mk, edgecolors=INK, linewidths=0.9, zorder=3, label=None if lvl in seen else lvl)
        seen.add(lvl)
        ax.annotate(name.split(" (")[0], (x, y), xytext=(5, 4 + 9 * n), textcoords="offset points", fontsize=8.5, color=INK)
    ax.set_xlim(1.8, 5.1)
    ax.set_ylim(1.8, 5.1)
    ax.set_xlabel("X: среднее (задача C1, заменяемость C3)")
    ax.set_ylabel("Y: среднее (аудитория C2, география C7)")
    ax.legend(loc="lower right", fontsize=8.5, frameon=True)
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис1_карта_близости.png"), dpi=200)
    plt.close(fig)
    return len(pts)


def fig_scores():
    B.build_b()
    names = [B.CO[d]["name"].split(" (")[0] for d in B.DOMS]
    vals = [B.total(d) for d in B.DOMS]
    order = sorted(range(8), key=lambda i: vals[i])
    fig, ax = plt.subplots(figsize=(8, 4.6))
    ax.barh([names[i] for i in order], [vals[i] for i in order], color="#8A8A8A", edgecolor=INK)
    for k, i in enumerate(order):
        ax.text(vals[i] + 0.03, k, str(vals[i]).replace(".", ","), va="center", fontsize=10)
    ax.axvline(3.5, color=INK, lw=0.8, ls="--")
    ax.axvline(4.2, color=INK, lw=0.8, ls=":")
    ax.set_xlim(0, 5.2)
    ax.set_xlabel("Итоговый взвешенный балл (0–5); пунктир – 3,5 и 4,2")
    ax.grid(axis="x", alpha=0.2)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис2_итоговые_баллы.png"), dpi=200)
    plt.close(fig)


def fig_shares():
    items = sorted(B.KEYS, key=lambda k: B.n(k))
    fig, ax = plt.subplots(figsize=(8.5, 7.5))
    shade = {"Обязательное": "#444444", "Линейное": "#8A8A8A", "Привлекательное": "#C8C8C8", "Безразличное": "#EEEEEE"}
    ax.barh([B.FEATS[k][1][:48] for k in items], [B.n(k) / 8 for k in items], color=[shade[B.FEATS[k][4]] for k in items], edgecolor=INK)
    ax.axvline(0.7, color=INK, lw=0.9, ls="--")
    ax.axvline(0.4, color=INK, lw=0.9, ls=":")
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("Доля конкурентов с признаком (из 8); пунктир – 0,4 и 0,7")
    ax.tick_params(axis="y", labelsize=8)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=c, ec=INK, label=k) for k, c in shade.items()], loc="lower right", fontsize=8.5, title="Категория Кано (экспертно)")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис3_доли_признаков.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    print(fig_map())
    fig_scores()
    fig_shares()
    print(os.listdir(OUT))
