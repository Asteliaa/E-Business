import csv
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "Материалы_собранные" / "GT_Беларусь"
FIG_DIR = BASE / "Рисунки"
FIG_DIR.mkdir(exist_ok=True)

MONTH_NAMES = ["янв", "фев", "мар", "апр", "май", "июн",
               "июл", "авг", "сен", "окт", "ноя", "дек"]

plt.rcParams["figure.figsize"] = (10, 5)
plt.rcParams["axes.grid"] = True
plt.rcParams["grid.alpha"] = 0.3


def read_combined(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            period = row["Период"]
            gt = float(row["Google Trends, 0-100"])
            yw = row["Яндекс Вордстат, запросов"]
            yw = float(yw) if yw not in (None, "") else None
            rows.append({"period": period, "gt": gt, "yw": yw, "month_num": int(period[5:7])})
    return rows


def read_gt_only(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            period = row["Период"]
            value = float(row["Google Trends, 0-100"])
            rows.append({"period": period, "value": value, "month_num": int(period[5:7])})
    return rows


# Пять градаций сезонного индекса по ЦИКЛЫ табл. 9 (до 80 / 80–95 / 95–105 / 105–120 / выше 120)
GRADES = ["до 80 — низкий сезон", "80–95 — период умеренного спроса", "95–105 — средний уровень",
          "105–120 — повышенный интерес", "выше 120 — пик сезона"]
GRADE_COLORS = dict(zip(GRADES, ["#9ecae1", "#6baed6", "#bdbdbd", "#fdae6b", "#e6550d"]))


def grade(v):
    if v < 80:
        return GRADES[0]
    if v < 95:
        return GRADES[1]
    if v <= 105:
        return GRADES[2]
    if v <= 120:
        return GRADES[3]
    return GRADES[4]


def moving_avg(values, window):
    ma = [None] * len(values)
    for i in range(window - 1, len(values)):
        ma[i] = mean(values[i - window + 1:i + 1])
    return ma


def chart_gt_vs_yw(rows, title, fname, num):
    labels = [r["period"][:7] for r in rows]
    # GT = 0 в месяцах «недостаточно данных» (GT табл. 5) — это пропуск, а не нулевой спрос:
    # такие месяцы не рисуются (разрыв линии), чтобы не изображать их как ноль.
    gt = [r["gt"] if r["gt"] > 0 else float("nan") for r in rows]
    yw = [r["yw"] for r in rows]
    fig, ax1 = plt.subplots()
    l1, = ax1.plot(range(len(gt)), gt, color="#4C72B0", marker="o", markersize=4, linewidth=1.6,
                   label="Google Trends, индекс 0-100 (разрыв — нет данных)")
    ax1.set_ylabel("Google Trends, индекс 0-100", color="#4C72B0")
    ax1.set_ylim(bottom=0)
    ax2 = ax1.twinx()
    l2, = ax2.plot(range(len(yw)), yw, color="#C44E52", linewidth=1.6, label="Яндекс Вордстат, запросов/мес.")
    ax2.set_ylabel("Яндекс Вордстат, запросов/мес.", color="#C44E52")
    ax2.set_ylim(bottom=0)
    step = max(1, len(labels) // 12)
    ax1.set_xticks(range(0, len(labels), step))
    ax1.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=45, ha="right")
    ax1.set_title(title)
    ax1.legend(handles=[l1, l2], loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=9)
    fig.tight_layout()
    out = FIG_DIR / fname
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Рисунок {num} сохранён: {out.name}")


def chart_seasonal_bars_combined(rows, title, fname, num, use="yw"):
    month_vals = {m: [] for m in range(1, 13)}
    for r in rows:
        v = r["yw"] if use == "yw" else r["gt"]
        month_vals[r["month_num"]].append(v)
    month_avg = {m: (mean(v) if v else 0) for m, v in month_vals.items()}
    overall = mean([v for v in month_avg.values() if v > 0]) if any(month_avg.values()) else 1
    idx = [(month_avg[m] / overall * 100) if overall else 0 for m in range(1, 13)]
    fig, ax = plt.subplots()
    colors = [GRADE_COLORS[grade(v)] for v in idx]
    ax.bar(MONTH_NAMES, idx, color=colors)
    ax.axhline(100, color="gray", linewidth=1, linestyle="--")
    for v_line in (80, 95, 105, 120):
        ax.axhline(v_line, color="lightgray", linewidth=0.8, linestyle=":")
    ax.set_ylabel("Сезонный индекс, %  (100 = среднегодовой уровень)")
    ax.set_title(title)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=GRADE_COLORS[g], label=g) for g in GRADES],
              title="Оценка месяца (ЦИКЛЫ, табл. 9)", fontsize=8, title_fontsize=8,
              loc="upper center", bbox_to_anchor=(0.5, -0.08), ncol=3)
    fig.tight_layout()
    out = FIG_DIR / fname
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Рисунок {num} сохранён: {out.name}")


def chart_line_with_trend(rows, title, fname, num):
    labels = [r["period"][:7] for r in rows]
    values = [r["value"] for r in rows]
    ma12 = moving_avg(values, 12)
    fig, ax = plt.subplots()
    ax.plot(range(len(values)), values, label="Индекс Google Trends", color="#4C72B0", linewidth=1.3)
    ax.plot(range(len(values)), ma12, label="Скользящее среднее, 12 мес.", color="#C44E52", linewidth=2)
    step = max(1, len(labels) // 12)
    ax.set_xticks(range(0, len(labels), step))
    ax.set_xticklabels([labels[i] for i in range(0, len(labels), step)], rotation=45, ha="right")
    ax.set_ylabel("Индекс, 0-100")
    ax.set_title(title)
    if "2023-05" in labels:
        i = labels.index("2023-05")
        ax.annotate("май–июнь 2023: премьера фильма\n«Русалочка» (The Little Mermaid) —\nомонимия, не спрос на инструмент",
                    xy=(i, values[i]), xytext=(i + 6, values[i] - 5), fontsize=9,
                    arrowprops=dict(arrowstyle="->", color="gray"))
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / fname
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Рисунок {num} сохранён: {out.name}")


def chart_compare_uml_bpmn(rows_a, rows_b, label_a, label_b, title, fname, num):
    n = min(len(rows_a), len(rows_b))
    labels = [rows_a[i]["period"][:7] for i in range(n)]
    va = [rows_a[i]["yw"] for i in range(n)]
    vb = [rows_b[i]["yw"] for i in range(n)]
    fig, ax = plt.subplots()
    ax.plot(range(n), va, label=label_a, color="#4C72B0")
    ax.plot(range(n), vb, label=label_b, color="#DD8452")
    ax.set_xticks(range(0, n, 2))
    ax.set_xticklabels([labels[i] for i in range(0, n, 2)], rotation=45, ha="right")
    ax.set_ylabel("Яндекс Вордстат, запросов/мес.")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    out = FIG_DIR / fname
    fig.savefig(out, dpi=150)
    plt.close(fig)
    print(f"Рисунок {num} сохранён: {out.name}")


def main():
    print("=== 03_charts.py ===\n")
    uml = read_combined(DATA_DIR / "XLT_ввод_данных_ОСНОВНОЙ_UML_BY.csv")
    bpmn = read_combined(DATA_DIR / "XLT_ввод_данных_ВТОРОЙ_BPMN_BY.csv")
    mermaid = read_gt_only(DATA_DIR / "XLT_ввод_данных_ТРЕТИЙ_Mermaid_world.csv")

    chart_gt_vs_yw(uml, "UML, Беларусь: Google Trends и Яндекс Вордстат, 24 месяца",
                   "01_uml_by_gt_vs_yw.png", 1)
    chart_seasonal_bars_combined(uml, "Сезонный индекс запроса UML по месяцам, Беларусь (Яндекс Вордстат)",
                                  "02_uml_by_seasonal_yw.png", 2, use="yw")
    chart_gt_vs_yw(bpmn, "BPMN, Беларусь: Google Trends и Яндекс Вордстат, 24 месяца",
                   "03_bpmn_by_gt_vs_yw.png", 3)
    chart_seasonal_bars_combined(bpmn, "Сезонный индекс запроса BPMN по месяцам, Беларусь (Яндекс Вордстат)",
                                  "04_bpmn_by_seasonal_yw.png", 4, use="yw")
    chart_compare_uml_bpmn(uml, bpmn, "UML (Беларусь)", "BPMN (Беларусь)",
                            "Частотность Яндекс Вордстат по месяцам: UML и BPMN, Беларусь",
                            "05_comparison_uml_vs_bpmn_yw.png", 5)
    chart_line_with_trend(mermaid, "Google Trends: Mermaid, весь мир, 5 лет (справочно, помесячно)",
                           "06_gt_mermaid_world_trend.png", 6)

    list_path = FIG_DIR / "СПИСОК_РИСУНКОВ.md"
    with open(list_path, "w", encoding="utf-8") as f:
        f.write("Рисунок 1 – Google Trends и Яндекс Вордстат по запросу UML, Беларусь, 24 месяца (сентябрь 2024 – август 2026)\n\n")
        f.write("Рисунок 2 – Сезонный индекс запроса UML по месяцам, Беларусь, по данным Яндекс Вордстат\n\n")
        f.write("Рисунок 3 – Google Trends и Яндекс Вордстат по запросу BPMN, Беларусь, 24 месяца\n\n")
        f.write("Рисунок 4 – Сезонный индекс запроса BPMN по месяцам, Беларусь, по данным Яндекс Вордстат\n\n")
        f.write("Рисунок 5 – Сравнение месячной частотности Яндекс Вордстат: UML и BPMN, Беларусь\n\n")
        f.write("Рисунок 6 – Динамика индекса Google Trends по запросу Mermaid, весь мир, 5 лет (справочный ряд; пик мая–июня 2023 г. связан с омонимией)\n")
    print(f"\nСписок рисунков сохранён: {list_path}")


if __name__ == "__main__":
    main()
