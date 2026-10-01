"""Обработка CSV Google Trends, снятых 30.09.2026 (кнопка скачивания «Динамика популярности»):
Россия и Казахстан (UML, BPMN), Беларусь (пересъём UML, BPMN), весь мир (mermaid diagram, mermaid js, plantuml).

Методика та же, что в 04_gt_indicators.py и 02_trend_seasonality.py (таблицы 12, 13, 33, 34):
 - 12-месячное окно: 52 полные недели (последняя неделя 27.09-03.10.2026 неполная и исключена);
 - 5-летнее окно: помесячное среднее недель (месяц по дате начала недели), 59 полных месяцев 2021-10..2026-08;
 - уровень интереса: GT-РБ табл. 14 (60/30/10) и АРГ табл. 10 (70/40/20);
 - относительное изменение: среднее последних 12 мес. к первым 12 мес. (Excel, порог ±15 %) и к предыдущим 12 мес. (Word);
 - наклон SLOPE по порядковому номеру месяца; стд. отклонение генеральное, CV = СКО / среднее.
12-месячное окно для РФ и КЗ вычислено из 5-летнего ряда (отдельная 12-месячная выгрузка не делалась).
"""
import csv, json
from pathlib import Path
from statistics import mean, pstdev

BASE = Path(__file__).resolve().parent.parent
M = BASE / "Материалы_собранные"
F = {
    "RU": M / "GT_Россия_Казахстан" / "GT_2026-09-30_RU_5y_UML_BPMN_multiTimeline.csv",
    "KZ": M / "GT_Россия_Казахстан" / "GT_2026-09-30_KZ_5y_UML_BPMN_multiTimeline.csv",
    "BY": M / "GT_Беларусь" / "GT_2026-09-30_BY_5y_UML_BPMN_multiTimeline.csv",
    "WORLD": M / "GT_Весь_мир" / "GT_2026-09-30_world_5y_mermaid_diagram_mermaid_js_plantuml_multiTimeline.csv",
}


def read(path):
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    i = next(k for k, r in enumerate(rows) if r and r[0] == "Week")
    names = [c.split(":")[0].strip() for c in rows[i][1:]]
    data = [(r[0], [float(x) if x else 0.0 for x in r[1:]]) for r in rows[i + 1:] if r and r[0]]
    return names, data


def lv_rb(v):
    return "высокий" if v >= 60 else "средний" if v >= 30 else "низкий" if v >= 10 else "недостаточный"


def lv_arg(v):
    return ("70-100 высокая" if v >= 70 else "40-69 средний" if v >= 40 else "20-39 нишевый" if v >= 20
            else "0-19 низкий/недостаточный")


def slope(ys):
    xs = list(range(1, len(ys) + 1)); mx, my = mean(xs), mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def monthly(data, col):
    d = {}
    for w, v in data:
        d.setdefault(w[:7], []).append(v[col])
    return {k: (mean(x), len(x)) for k, x in sorted(d.items())}


def cls(ch):
    return "растущий" if ch > 0.15 else "снижающийся" if ch < -0.15 else "стабильный"


def report(title, names, data):
    print(f"\n===== {title}: {len(data)} недель {data[0][0]} .. {data[-1][0]} (последняя неделя неполная) =====")
    full = data[:-1]
    for c, n in enumerate(names):
        print(f"\n--- {n} ---")
        w52 = [v[c] for _, v in full[-52:]]
        lab = [w for w, _ in full[-52:]]
        prev52 = [v[c] for _, v in full[-104:-52]]
        sd = pstdev(w52); m = mean(w52)
        mx = max(w52)
        print(f"12 мес. (из 5-лет. ряда): недели {lab[0]}..{lab[-1]}, 52 полные; с данными {sum(x > 0 for x in w52)}; "
              f"среднее {m:.2f}; макс {mx:.0f} ({', '.join(l for l, x in zip(lab, w52) if x == mx)}); "
              f"СКО {sd:.2f}; CV {(sd / m if m else float('nan')):.2f}")
        print(f"   справочно с неполной неделей {data[-1][0]} = {data[-1][1][c]:.0f}")
        l13, p13 = mean(w52[-13:]), mean(w52[-26:-13])
        print(f"   последние 13 нед. {l13:.2f} против предыдущих 13 нед. {p13:.2f} "
              f"({((l13 / p13 - 1) * 100 if p13 else float('nan')):+.1f} %)")
        pm = mean(prev52)
        print(f"   предыдущие 52 недели (окно {full[-104][0]}..{full[-53][0]}): среднее {pm:.2f}, "
              f"изменение {((m / pm - 1) * 100 if pm else float('nan')):+.1f} %")
        print(f"   уровень 12 мес.: GT-РБ {lv_rb(m)}; АРГ {lv_arg(m)}")
        mo = monthly(data, c)
        keys = list(mo)[1:-1]  # без неполных 2021-09 и 2026-09
        vals = [mo[k][0] for k in keys]
        m5 = mean(vals)
        print(f"5 лет: {len(keys)} полных месяцев {keys[0]}..{keys[-1]}; с данными {sum(v > 0 for v in vals)}; "
              f"среднее {m5:.2f}; уровень GT-РБ {lv_rb(m5)}; АРГ {lv_arg(m5)}")
        mxv = max(vals)
        print(f"   макс. месяц {mxv:.2f} ({keys[vals.index(mxv)]}); недель с данными всего {sum(v[c] > 0 for _, v in data)} из {len(data)}")
        f12, l12, p12 = mean(vals[:12]), mean(vals[-12:]), mean(vals[-24:-12])
        print(f"   первые 12 мес. {f12:.2f}; предыдущие 12 мес. ({keys[-24]}..{keys[-13]}) {p12:.2f}; "
              f"последние 12 мес. ({keys[-12]}..{keys[-1]}) {l12:.2f}")
        if f12:
            ch = l12 / f12 - 1
            print(f"   Excel: последние к первым 12 мес. {ch * 100:+.1f} % ({cls(ch)}); SLOPE {slope(vals):.3f}")
        if p12:
            print(f"   Word: последние 12 к предыдущим 12 мес. {(l12 / p12 - 1) * 100:+.1f} %")
        i3 = mean(vals[-3:]); p3 = mean(vals[-6:-3])
        print(f"   последние 3 мес. ({', '.join(keys[-3:])}) {i3:.2f}; предыдущие 3 мес. {p3:.2f}")
        top = sorted(zip(vals, keys), reverse=True)[:3]
        print("   три максимальных месяца:", "; ".join(f"{k} {v:.2f}" for v, k in top))


def compare_by(names, data):
    print("\n===== Беларусь: сравнение пересъёма 30.09 с ранее использованным рядом (29.09) =====")
    old = json.load(open(M / "GT_Беларусь" / "GT_2026-09-29_BY_5y_packet6_UML_BPMN_monthly.json", encoding="utf-8"))
    print("недель в CSV:", len(data), "; недель в сводке 29.09 (сумма weeks):", sum(m["weeks"] for m in old["monthly"]))
    diffs = 0
    for c, n in enumerate(names):
        mo = monthly(data, c)
        for m in old["monthly"]:
            new, wk = mo[m["month"]]
            if abs(new - m["avg"][c]) > 0.01 or wk != m["weeks"]:
                diffs += 1
                print(f"  {n} {m['month']}: было {m['avg'][c]} ({m['weeks']} нед.), стало {new:.2f} ({wk} нед.)")
    print("различий в помесячных значениях:", diffs)
    p2 = json.load(open(M / "GT_Беларусь" / "GT_2026-09-29_BY_5y_packet2_time.json", encoding="utf-8"))
    import datetime as dt
    nz = {}
    for w in p2["nonzero"]:
        d = dt.datetime.fromtimestamp(int(w["t"]), tz=dt.timezone.utc).strftime("%Y-%m-%d")
        nz[d] = w["v"][3]  # BPMN в пакете 2 четвёртый
    nzv = {d: v for d, v in nz.items() if v}
    new = {w: v[1] for w, v in data if v[1]}
    print("BPMN недельный ряд: ненулевых недель в пакете 2 (29.09):", len(nzv), "; в CSV 30.09:", len(new))
    dd = [(d, nzv.get(d), new.get(d)) for d in sorted(set(nzv) | set(new)) if nzv.get(d) != new.get(d)]
    print("  расхождений по неделям:", len(dd), dd[:10])
    print("  UML в CSV: ненулевых недель", sum(v[0] > 0 for _, v in data), ", первая неделя", data[0])


if __name__ == "__main__":
    for key, title in (("RU", "Россия"), ("KZ", "Казахстан"), ("BY", "Беларусь (пересъём 30.09.2026)"),
                       ("WORLD", "Весь мир")):
        names, data = read(F[key])
        report(title, names, data)
        if key == "BY":
            compare_by(names, data)
