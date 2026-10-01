# -*- coding: utf-8 -*-
"""Рисунки ЛР4, не требующие внешних данных: схема модели, связи листов шаблона, веса факторов 07."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, os.path.dirname(__file__))
import lr4_calc as C

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Рисунки")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.family": "Times New Roman", "font.size": 11})
INK, FILL, ACC = "#222222", "#F2F2F2", "#8A8A8A"


def box(ax, x, y, w, h, text, fc=FILL, fs=10, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=INK, lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK,
            fontweight="bold" if bold else "normal", wrap=True)


def arrow(ax, p, q):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="-|>", mutation_scale=12, color=INK, lw=1))


def fig_model():
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis("off")
    box(ax, 3.6, 2.6, 2.8, 1.6, "Конкуренция между\nсуществующими игроками\n(трафик, видимость, рейтинги,\nудержание)", bold=True)
    box(ax, 3.6, 5.3, 2.8, 1.3, "Угроза новых участников\n(реклама, доверие, данные,\nплатформенные правила)")
    box(ax, 3.6, 0.2, 2.8, 1.3, "Угроза заменителей\n(самостоятельное решение,\nавтоматизация, AI-сервисы, обучение)")
    box(ax, 0.1, 2.75, 2.8, 1.3, "Сила поставщиков\n(поисковики, реклама, облака,\nплатежи, данные)")
    box(ax, 7.1, 2.75, 2.8, 1.3, "Сила покупателей\n(сравнение цен и отзывов,\nиздержки переключения)")
    for p, q in (((5, 5.3), (5, 4.2)), ((5, 1.5), (5, 2.6)), ((2.9, 3.4), (3.6, 3.4)), ((7.1, 3.4), (6.4, 3.4))):
        arrow(ax, p, q)
    ax.text(5, 6.85, "Цифровые факторы: сетевые эффекты, данные, алгоритмическая видимость,\nиздержки переключения, экосистемная зависимость",
            ha="center", va="center", fontsize=9.5, color=INK)
    fig.savefig(os.path.join(OUT, "рис1_модель_пяти_сил.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_flow():
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.3, 6)
    ax.axis("off")
    box(ax, 0.1, 4.2, 2.3, 1.2, "01_Параметры\nпороги, границы рынка")
    box(ax, 0.1, 2.3, 2.3, 1.2, "02_Конкуренты_SW\nвизиты, доли, каналы\nCR3, CR5, HHI")
    box(ax, 3.3, 3.3, 2.3, 1.2, "03_Каналы_трафика\nвзвешенные доли каналов")
    box(ax, 3.3, 1.5, 2.3, 1.2, "04_Поиск_реклама\nиндекс давления запросов")
    box(ax, 3.3, 0.0, 2.3, 1.2, "05, 06: отзывы,\nтехнологии и финансы")
    box(ax, 6.3, 2.1, 1.7, 1.6, "07_Барьеры_входа\n9 факторов,\nвеса, индекс", bold=True)
    box(ax, 8.4, 2.1, 1.5, 1.6, "08_Дашборд\nпоказатели,\nдиаграмма")
    box(ax, 6.3, 4.3, 3.6, 1.1, "09_Источники:\nжурнал доказательной базы")
    for p, q in (((2.4, 4.8), (3.3, 4.2)), ((2.4, 2.9), (3.3, 3.8)), ((5.6, 3.9), (6.3, 3.2)), ((5.6, 2.1), (6.3, 2.6)),
                 ((5.6, 0.6), (6.3, 2.2)), ((8.0, 2.9), (8.4, 2.9)), ((2.4, 2.6), (6.3, 3.0))):
        arrow(ax, p, q)
    fig.savefig(os.path.join(OUT, "рис2_связи_листов_шаблона.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_weights():
    fig, ax = plt.subplots(figsize=(8, 4.6))
    names = [f"{i + 4}. {n}" for i, n in enumerate(C.FACTORS)]
    bars = ax.barh(range(len(names))[::-1], C.WEIGHTS, color=ACC, edgecolor=INK)
    ax.set_yticks(range(len(names))[::-1])
    ax.set_yticklabels(names, fontsize=9)
    for b, w in zip(bars, C.WEIGHTS):
        ax.text(w + 0.003, b.get_y() + b.get_height() / 2, f"{w:.2f}".replace(".", ","), va="center", fontsize=9)
    ax.set_xlim(0, 0.2)
    ax.set_xlabel("Вес фактора в листе 07 (строки 4-12)")
    s = sum(C.WEIGHTS)
    ax.set_title(f"Сумма весов по шаблону: {s:.2f}".replace(".", ",") + " (константа в E13 шаблона: 1)", fontsize=10)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(os.path.join(OUT, "рис3_веса_факторов_07.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def fig_visits():
    """Визиты доменов с данными Semrush (август 2026) и матрицы А/Б: читает results_lr4.json (скрипт 08_word_variant.py)."""
    import json
    res = json.load(open(os.path.join(os.path.dirname(__file__), "results_lr4.json"), encoding="utf-8"))
    top = res["semrush"]["top"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    names = [t[0] for t in top][::-1]
    vals = [t[1] / 1e6 for t in top][::-1]
    bars = ax.barh(names, vals, color=ACC, edgecolor=INK)
    ax.set_xscale("log")
    for b, v, t in zip(bars, vals, [t[2] for t in top][::-1]):
        ax.text(v * 1.08, b.get_y() + b.get_height() / 2, f"{v:.2f}".replace(".", ",") + " млн (" + f"{t * 100:.1f}".replace(".", ",") + " %)", va="center", fontsize=8)
    ax.set_xlim(0.05, 300)
    ax.set_xlabel("Визиты в месяц, млн (логарифмическая шкала); Semrush, август 2026")
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(os.path.join(OUT, "рис4_визиты_semrush_2026-08.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    names5 = ["Конкуренция игроков", "Новые участники", "Покупатели", "Поставщики", "Заменители", "Цифровые усилители"]
    a = res["matrix_a"]["scores"]
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.bar(range(6), a, color=ACC, edgecolor=INK)
    ax.set_xticks(range(6))
    ax.set_xticklabels([n.replace(' ', chr(10)) for n in names5], fontsize=9)
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Оценка 1-5 (матрица А)")
    for i, v in enumerate(a):
        ax.text(i, v + 0.08, f"{v:.0f}", ha="center", fontsize=9)
    m6 = res["matrix_a"]["m6"]
    ax.axhline(m6, color=INK, lw=1, ls="--")
    ax.text(5.45, m6 + 0.08, "среднее " + f"{m6:.1f}".replace(".", ","), ha="right", fontsize=9)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    fig.savefig(os.path.join(OUT, "рис5_матрица_А.png"), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    fig_model()
    fig_flow()
    fig_weights()
    fig_visits()
    print("ok", OUT)
