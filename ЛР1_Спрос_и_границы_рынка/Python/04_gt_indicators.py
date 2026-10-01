"""Показатели Google Trends по GT-РБ §5.1 (табл. 13) и уровень интереса по двум шкалам:
GT-РБ §5.2 (табл. 14: 60/30/10) и АРГ лист 3 (табл. 10: 70/40/20).

Волатильность в GT-РБ описана только как «разброс значений по периоду» без формулы;
здесь в качестве показателя разброса взяты стандартное отклонение (генеральное) и
коэффициент вариации (стандартное отклонение / среднее) — это указано в отчёте.
Неполная последняя неделя 12-месячного окна (27.09–03.10.2026) исключена (ЦИКЛЫ табл. 5).
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, pstdev

BASE = Path(__file__).resolve().parent.parent
D = BASE / "Материалы_собранные" / "GT_Беларусь"


def level_gt_rb(v):
    if v >= 60:
        return "высокий"
    if v >= 30:
        return "средний"
    if v >= 10:
        return "низкий"
    return "недостаточный"


def level_arg(v):
    if v >= 70:
        return "высокая относительная выраженность (70–100)"
    if v >= 40:
        return "средний или устойчивый интерес (40–69)"
    if v >= 20:
        return "нишевый или слабовыраженный (20–39)"
    return "низкий интерес или недостаточный объём данных (0–19)"


def describe(name, vals, labels, unit):
    m = mean(vals)
    mx = max(vals)
    sd = pstdev(vals)
    cv = sd / m if m else None
    print(f"\n{name}: {len(vals)} {unit}, с данными {sum(v > 0 for v in vals)}")
    print(f"  средний индекс {m:.2f}; максимум {mx} ({', '.join(l for l, v in zip(labels, vals) if v == mx)})")
    print(f"  стандартное отклонение {sd:.2f}; коэффициент вариации {cv:.2f}")
    print(f"  уровень по GT-РБ табл. 14: {level_gt_rb(m)}; по АРГ табл. 10: {level_arg(m)}")
    return m


def weekly_12m(path, key_full=True):
    data = json.load(open(path, encoding="utf-8"))
    tl = data["timelineData"]
    full = tl[:-1]  # последняя неделя окна неполная на дату снятия
    return [w["v"] for w in full], [w["ft"] for w in full], tl[-1]


def main():
    print("=== 04_gt_indicators.py ===")
    for kw, fname in (("UML", "GT_2026-09-30_BY_12m_UML_time_regions_related.json"),
                      ("BPMN", "GT_2026-09-29_BY_12m_BPMN_time_regions_related.json")):
        vals, labels, last = weekly_12m(D / fname)
        describe(f"{kw}, Беларусь, 12 месяцев (полные недели)", vals, labels, "недель")
        print(f"  исключена неполная неделя: {last['ft']} = {last['v']}")
        l3, p3 = vals[-13:], vals[-26:-13]
        ch = (mean(l3) / mean(p3) - 1) * 100 if mean(p3) else None
        print(f"  последние 13 недель ({labels[-13]} … {labels[-1]}): {mean(l3):.2f}; "
              f"предыдущие 13 недель: {mean(p3):.2f}; изменение {ch:.1f}%" if ch is not None else "  н/д")

    p6 = json.load(open(D / "GT_2026-09-29_BY_5y_packet6_UML_BPMN_monthly.json", encoding="utf-8"))
    inner = p6["monthly"][1:-1]  # без неполных 2021-09 и 2026-09
    for i, kw in enumerate(p6["keywords"]):
        vals = [m["avg"][i] for m in inner]
        labels = [m["month"] for m in inner]
        describe(f"{kw}, Беларусь, 5 лет (месячный свод, {labels[0]}…{labels[-1]})", vals, labels, "месяцев")
        l3, p3 = vals[-3:], vals[-6:-3]
        print(f"  последние 3 мес. ({', '.join(labels[-3:])}): {mean(l3):.2f}; предыдущие 3 мес.: {mean(p3):.2f}")

    other_queries_5y()


def monthly_from_weeks(weeks):
    """Свод недель в месяцы: простое среднее недель, отнесённых к месяцу по дате начала недели."""
    by_month = {}
    for t, v in weeks:
        key = datetime.fromtimestamp(int(t), tz=timezone.utc).strftime("%Y-%m")
        by_month.setdefault(key, []).append(v)
    return {k: [mean(x[i] for x in vs) for i in range(len(vs[0]))] for k, vs in sorted(by_month.items())}


def other_queries_5y():
    """Помесячные средние (59 полных месяцев 10.2021–08.2026) для всех запросов пакетов 1–5 —
    та же база, что у UML/BPMN (пакет 6) и Figma/Miro (пакет 5) в таблице уровней интереса."""
    print("\nПакеты 1–5, Беларусь, 5 лет: помесячное среднее по 59 полным месяцам")
    res = []
    for fname in ("GT_2026-09-29_BY_5y_packet1_monthly.json", "GT_2026-09-29_BY_5y_packet2_monthly.json",
                  "GT_2026-09-29_BY_5y_packet5_time_monthly.json"):
        d = json.load(open(D / fname, encoding="utf-8"))
        inner = d["monthly"][1:-1]
        for i, kw in enumerate(d["keywords"]):
            res.append((kw, mean(m["avg"][i] for m in inner), fname))
    for fname in ("GT_2026-09-29_BY_5y_packet3_time.json", "GT_2026-09-29_BY_5y_packet4_time.json"):
        d = json.load(open(D / fname, encoding="utf-8"))
        t0 = 1632614400  # неделя 26.09–02.10.2021 (firstWeek), шаг 7 дней, всего totalWeeks недель
        nz = {w["t"]: w["v"] for w in d["nonzero"]}
        weeks = [(str(t0 + i * 604800), nz.get(str(t0 + i * 604800), [0] * len(d["keywords"])))
                 for i in range(d["totalWeeks"])]
        inner = list(monthly_from_weeks(weeks).items())[1:-1]
        for i, kw in enumerate(d["keywords"]):
            res.append((kw, mean(v[i] for _, v in inner), fname))
    for kw, m, fname in res:
        print(f"  {kw:<36} {m:6.2f}  ({fname})")
    rest = [(kw, m) for kw, m, _ in res if kw not in ("BPMN", "Miro", "Figma")]
    top = max(rest, key=lambda x: x[1])
    print(f"  Остальные запросы пакетов 1–5: от {min(m for _, m in rest):.2f} до {top[1]:.2f} (максимум — {top[0]})")


if __name__ == "__main__":
    main()
