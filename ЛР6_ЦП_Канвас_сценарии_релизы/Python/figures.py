# -*- coding: utf-8 -*-
"""Рисунки ЛР6: цепочка методик, Канвас, карта навигации, баллы единиц и релизы."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import lr6_common as C
import spec_62 as S62
import spec_64 as S64
import spec_65 as S65

OUT = os.path.join(C.LAB6, "Рисунки")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})
INK, FILL = "#222222", "#F2F2F2"


def box(ax, x, y, w, h, text, fc=FILL, fs=9.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=INK, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, fontweight="bold" if bold else "normal")


def arrow(ax, p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, color=INK, lw=1))


def fig_chain():
    steps = ["Проблема\nклиента", "Ценностное\nпредложение\n(6.1)", "Цифровой\nтовар и\nмонетизация\n(6.1)", "Канвас\n(6.2)", "Бизнес-логика\nи сценарии\n(6.3)", "Страницы\nи экраны\n(6.4)", "Релизы\n(6.5)"]
    fig, ax = plt.subplots(figsize=(11, 2.6))
    ax.set_xlim(0, 11.6)
    ax.set_ylim(0, 2.4)
    ax.axis("off")
    for i, t in enumerate(steps):
        x = 0.1 + i * 1.65
        box(ax, x, 0.5, 1.4, 1.5, t, fc="#E6E6E6" if i in (0, 6) else FILL)
        if i:
            arrow(ax, (x - 0.25, 1.25), (x, 1.25))
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис1_цепочка_методик.png"), dpi=200)
    plt.close(fig)


def fig_canvas():
    st = {3: "Готово", 4: "Проверить", 5: "Проверить", 6: "Проверить", 7: "Проверить", 8: "Требует доработки", 9: "Требует доработки", 10: "Требует доработки", 11: "Требует доработки"}
    names = {3: "Клиентские сегменты", 4: "Ценностное предложение", 5: "Каналы", 6: "Отношения с клиентами", 7: "Потоки доходов", 8: "Ключевые ресурсы", 9: "Ключевые виды деятельности", 10: "Ключевые партнёры", 11: "Структура затрат"}
    short = {3: "Студенты (Free),\nаналитики и\nразработчики ПО (Pro)", 4: "Диаграмма любой\nнотации из текста\nв одном инструменте", 5: "Поиск, сайт\nс ценой, вузы", 6: "Самообслуживание,\nдокументация", 7: "Pro 40 USD в год;\nFree без оплаты", 8: "Движок нотаций,\nИИ-ассистент, PWA", 9: "Разработка нотаций,\nдокументация,\nпродвижение", 10: "Вузы, платёжный и\nИИ-провайдеры,\nоблако", 11: "Разработка, облако, ИИ-вызовы, поддержка"}
    shade = {"Готово": "#C8C8C8", "Проверить": "#E6E6E6", "Требует доработки": "#FFFFFF"}
    # (x, y, w, h) в сетке 5 x 3
    lay = {10: (0, 1, 1, 2), 9: (1, 2, 1, 1), 8: (1, 1, 1, 1), 4: (2, 1, 1, 2), 6: (3, 2, 1, 1), 5: (3, 1, 1, 1), 3: (4, 1, 1, 2), 11: (0, 0, 2.5, 1), 7: (2.5, 0, 2.5, 1)}
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_xlim(-0.05, 5.05)
    ax.set_ylim(-0.1, 3.4)
    ax.axis("off")
    for k, (x, y, w, h) in lay.items():
        ax.add_patch(plt.Rectangle((x + 0.02, y + 0.02), w - 0.04, h - 0.04, fc=shade[st[k]], ec=INK, lw=1.2))
        ax.text(x + w / 2, y + h - 0.12, names[k], ha="center", va="top", fontsize=10, fontweight="bold")
        ax.text(x + w / 2, y + h / 2 - 0.05, short[k], ha="center", va="center", fontsize=9)
        ax.text(x + w / 2, y + 0.1, "[" + st[k] + "]", ha="center", va="bottom", fontsize=8.5, style="italic")
    ax.text(2.5, 3.28, "Канвас NotaCode (методика 6.2)", ha="center", fontsize=12.5, fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис2_канвас.png"), dpi=200)
    plt.close(fig)


def fig_nav():
    names = {"U-%03d" % (i + 1): u[1] for i, u in enumerate(S64.UNITS)}
    pos = {"U-001": (0, 3), "U-002": (2.2, 3), "U-003": (4.4, 3), "U-004": (6.6, 3), "U-005": (4.4, 1.8), "U-006": (6.6, 1.8), "U-007": (2.2, 0.6), "U-008": (4.4, 0.6),
           "U-009": (6.6, 0.6), "U-010": (2.2, -0.8), "U-011": (6.6, -0.8), "U-012": (8.8, 1.8), "U-013": (4.4, -0.8)}
    fig, ax = plt.subplots(figsize=(12, 6.4))
    ax.set_xlim(-1.2, 10.0)
    ax.set_ylim(-1.6, 4.0)
    ax.axis("off")
    for a_, b_, *_ in S64.NAV:
        dx, dy = abs(pos[b_][0] - pos[a_][0]), abs(pos[b_][1] - pos[a_][1])
        sh = 78 if dx > 1.5 * dy else 34
        an = ax.annotate("", xy=pos[b_], xytext=pos[a_], arrowprops=dict(arrowstyle="-|>", color=INK, lw=1, shrinkA=sh, shrinkB=sh, connectionstyle="arc3,rad=0.06"))
        an.set_zorder(6)
    for u, (x, y) in pos.items():
        site = S64.UNITS[int(u[2:]) - 1][0] == S64.SITE
        ax.add_patch(FancyBboxPatch((x - 0.95, y - 0.34), 1.9, 0.68, boxstyle="round,pad=0.02,rounding_size=0.08", fc="#E6E6E6" if site else "#FFFFFF", ec=INK, lw=1, zorder=3))
        ax.text(x, y, u + "\n" + names[u], ha="center", va="center", fontsize=8, zorder=4)
    ax.text(4.4, 3.8, "Серый – страницы сайта, белый – экраны приложения", ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис3_навигация.png"), dpi=200)
    plt.close(fig)


def fig_release():
    rows = sorted(S65.UNITS, key=lambda u: S65.s1(u))
    col = {"Первый": "#444444", "Следующий": "#999999", "Не включать": "#DDDDDD"}
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh([u[0] + " " + u[2][:34] for u in rows], [S65.s1(u) for u in rows], color=[col[S65.rec(u)] for u in rows], edgecolor=INK)
    ax.axvline(3.7, color=INK, lw=0.9, ls="--")
    ax.set_xlabel("Балл первого релиза (шкала 1–5); пунктир – порог 3,7")
    ax.tick_params(axis="y", labelsize=8)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(fc=c, ec=INK, label=k) for k, c in col.items()], loc="lower right", fontsize=9, title="Рекомендованный релиз")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "рис4_баллы_релизов.png"), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    fig_chain()
    fig_canvas()
    fig_nav()
    fig_release()
    print(os.listdir(OUT))
