# -*- coding: utf-8 -*-
"""Россия и Казахстан: Google Trends (UML, BPMN) и Вордстат «Регионы» (bpmn, uml).

Данные перенесены из первой работы (ЛР1): CSV «Динамика популярности» Google Trends от 30.09.2026 и выгрузка вкладки «Регионы»
Вордстата (окно 29.08.2026-29.09.2026). Новые выгрузки не выполнялись. Расчёт показателей повторяет скрипт первой работы
06_gt_ru_kz_mermaid.py: 12-месячное окно - 52 полные недели (последняя неделя 27.09-03.10.2026 неполная и исключена),
5-летнее окно - помесячное среднее недель (месяц по дате начала недели), 59 полных месяцев октябрь 2021 - август 2026.
"""
import csv
import json
import os
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "Материалы_собранные")
GT_FILES = {
    "Россия": os.path.join(RAW, "GT_Россия_Казахстан_из_ЛР1", "GT_2026-09-30_RU_5y_UML_BPMN_multiTimeline.csv"),
    "Казахстан": os.path.join(RAW, "GT_Россия_Казахстан_из_ЛР1", "GT_2026-09-30_KZ_5y_UML_BPMN_multiTimeline.csv"),
}
WS_REG_FILE = os.path.join(RAW, "Wordstat_Регионы_из_ЛР1", "wordstat_regiony_bpmn_uml_RB_okno_2026-08-29_09-29.json")


def _read(path):
    rows = list(csv.reader(open(path, encoding="utf-8-sig")))
    i = next(k for k, r in enumerate(rows) if r and r[0] == "Week")
    return [(r[0], [float(x) if x else 0.0 for x in r[1:]]) for r in rows[i + 1:] if r and r[0]]


def _monthly(data, col):
    d = {}
    for w, v in data:
        d.setdefault(w[:7], []).append(v[col])
    return {k: mean(x) for k, x in sorted(d.items())}


def gt_stats():
    """{страна: {запрос: показатели}}; запросы: UML (столбец 0), BPMN (столбец 1)."""
    out = {}
    for country, path in GT_FILES.items():
        data = _read(path)
        full = data[:-1]
        out[country] = {}
        for c, q in enumerate(("UML", "BPMN")):
            w52 = [v[c] for _, v in full[-52:]]
            mo = _monthly(data, c)
            keys = list(mo)[1:-1]          # без неполных крайних месяцев 2021-09 и 2026-09
            vals = [mo[k] for k in keys]
            l12, p12 = mean(vals[-12:]), mean(vals[-24:-12])
            out[country][q] = dict(
                weeks=sum(x > 0 for x in w52), mean12=mean(w52), maxw=max(w52),
                months=sum(v > 0 for v in vals), mean5=mean(vals),
                last12=l12, prev12=p12, chg=(l12 / p12 - 1) if p12 else None,
                first=keys[0], last=keys[-1], week_from=full[-52][0], week_to=full[-1][0], n_weeks=len(full))
    return out


def ws_regions():
    """Вкладка «Регионы», окно 29.08-29.09.2026: {запрос: {регион: (запросов, индекс)}}."""
    d = json.load(open(WS_REG_FILE, encoding="utf-8"))
    return {q: {r[0]: (r[1], r[2]) for r in d[q]} for q in ("bpmn", "uml")}


if __name__ == "__main__":
    for c, qs in gt_stats().items():
        for q, s in qs.items():
            print(c, q, {k: (round(v, 2) if isinstance(v, float) else v) for k, v in s.items()})
    print(ws_regions()["uml"]["Россия"])
