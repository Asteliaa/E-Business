"""Динамика Яндекс Вордстат (Беларусь) по остальным запросам ядра, устройствам и расширенному периоду.

Расчёты повторяют правила скрипта 02 (Excel-логика XL-Т и Word-логика ЦИКЛЫ), применённые к ряду Вордстата
(нормирован к 0-100 по максимуму ряда, как в варианте «только YW»). Источник данных -- JSON из
Материалы_собранные/Wordstat_Беларусь.
"""
import importlib.util
import json
import math
from pathlib import Path
from statistics import mean

BASE = Path(__file__).resolve().parent.parent
D = BASE / "Материалы_собранные" / "Wordstat_Беларусь"
spec = importlib.util.spec_from_file_location("ts02", Path(__file__).with_name("02_trend_seasonality.py"))
ts = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ts)
MN = ts.MONTH_NAMES

QUERIES = [("uml", "uml"), ("bpmn", "bpmn"), ("plantuml", "plantuml"), ("idef0", "idef0"),
           ("dfd диаграмма", "dfd-diagramma"), ("erd диаграмма", "erd-diagramma"),
           ("erd (омоним, без уточнения)", "erd-bez-utochneniya"), ("сеть петри", "set-petri"),
           ("нейросеть схема", "neyroset-shema"), ("нейросеть диаграмма", "neyroset-diagramma")]
S24 = "2024-09_2026-08"
S104 = "2018-01_2026-08"


def load(slug, suffix):
    j = json.load(open(D / f"wordstat_{slug}_dinamika_RB_{suffix}.json", encoding="utf-8"))
    return [r["month"] for r in j["data"]], [float(r["value"]) for r in j["data"]]


def corr(a, b):
    ma, mb = mean(a), mean(b)
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / math.sqrt(
        sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))


print("=== 05_wordstat_dinamika_ostalnye.py ===")
print("\n[1] Динамика Вордстата, Беларусь, 24 мес. (09.2024-08.2026): суммы по годам и показатели")
for name, slug in QUERIES:
    per, v = load(slug, S24)
    y1, y2 = sum(v[:12]), sum(v[12:])
    ch = (y2 / y1 - 1) * 100 if y1 else float("nan")
    p1 = per[v.index(max(v[:12]))]
    p2 = per[12 + v[12:].index(max(v[12:]))]
    mn = per[v.index(min(v))]
    mx = max(v)
    norm = [x / mx * 100 for x in v]
    mnums = [int(p[5:7]) for p in per]
    ex = ts.excel_style(norm, mnums)
    wd = ts.word_style(norm, mnums)
    print(f"{name}: Σ 1-й год {y1:.0f}; Σ 2-й год {y2:.0f}; Δ {ch:.1f} %; пик 1-го года {p1} ({max(v[:12]):.0f}); "
          f"пик 2-го года {p2} ({max(v[12:]):.0f}); минимум {mn} ({min(v):.0f})")
    print(f"    Excel: изменение {ts.fmt(ex['rel_change'] * 100)} % ({ex['trend_class']}); {ex['season_strength']}, "
          f"амплитуда {ts.fmt(ex['amplitude'])}, пик {MN[ex['max_month'] - 1]}, минимум {MN[ex['min_month'] - 1]}; "
          f"K последнего месяца {ts.fmt(ex['last_cycle_coef'], 2)} ({ex['phase']})")
    print(f"    Word: последний год к предыдущему {ts.fmt(wd['change_pct_yoy'])} %; {wd['dyn_type']}; "
          f"доля месяцев роста {ts.fmt(wd['share_growth_months_pct'], 1)} %")
    si = wd["season_index"]
    top = sorted(si, key=lambda m: -si[m])[:2]
    low = sorted(si, key=lambda m: si[m])[:2]
    print("    Word, сезонный индекс: выше всего " + ", ".join(f"{MN[m - 1]} {si[m]:.0f}" for m in top)
          + "; ниже всего " + ", ".join(f"{MN[m - 1]} {si[m]:.0f}" for m in low))

print("\n[2] Проверка омонимии «erd»")
_, e_all = load("erd-bez-utochneniya", S24)
_, e_d = load("erd-diagramma", S24)
_, u = load("uml", S24)
print(f"Σ erd = {sum(e_all):.0f}; Σ erd диаграмма = {sum(e_d):.0f}; доля = {sum(e_d) / sum(e_all) * 100:.1f} %")
print(f"Корреляция помесячных рядов: erd и erd диаграмма = {corr(e_all, e_d):.2f}; erd и uml = {corr(e_all, u):.2f}; "
      f"erd диаграмма и uml = {corr(e_d, u):.2f}")


def summer_ratio(x):
    summer = x[10:12] + x[22:24]
    rest = x[:10] + x[12:22]
    return mean(summer) / mean(rest)


print(f"Отношение среднего июля-августа к среднему остальных месяцев: erd = {summer_ratio(e_all):.2f}; "
      f"erd диаграмма = {summer_ratio(e_d):.2f}; uml = {summer_ratio(u):.2f}")

print("\n[3] Расширенный период 2018-01 - 2026-08 (Вордстат, Беларусь): суммы по календарным годам (2026 -- 8 месяцев)")
print("годы: " + " ".join(str(y) for y in range(2018, 2027)))
for name, slug in QUERIES:
    per, v = load(slug, S104)
    row = [sum(x for p, x in zip(per, v) if p.startswith(str(y))) for y in range(2018, 2027)]
    print(f"{name}: " + " ".join(f"{x:.0f}" for x in row))
print("Сравнимые окна январь-август каждого года:")
for name, slug in QUERIES:
    per, v = load(slug, S104)
    row = [sum(x for p, x in zip(per, v) if p.startswith(str(y)) and int(p[5:7]) <= 8) for y in range(2018, 2027)]
    print(f"{name}: " + " ".join(f"{x:.0f}" for x in row))

print("\n[3a] Месяц максимума по годам (расширенный ряд)")
for name, slug in QUERIES[:2]:
    per, v = load(slug, S104)
    out = []
    for y in range(2018, 2027):
        pv = [(x, p) for p, x in zip(per, v) if p.startswith(str(y))]
        out.append(f"{y}: {max(pv)[1][5:]} ({max(pv)[0]:.0f})")
    print(name + ": " + "; ".join(out))
for name, slug in QUERIES[:2]:
    per, v = load(slug, S104)
    mnums = [int(p[5:7]) for p in per]
    ex = ts.excel_style(v, mnums)
    wd = ts.word_style(v, mnums)
    print(f"{name}, 104 мес.: сезонность (Excel) {ex['season_strength']}, амплитуда {ts.fmt(ex['amplitude'])}, "
          f"пик {MN[ex['max_month'] - 1]}, минимум {MN[ex['min_month'] - 1]}; Word, сезонный индекс: "
          + ", ".join(f"{MN[m - 1]} {wd['season_index'][m]:.0f}" for m in range(1, 13)))

print("\n[4] Разбивка по устройствам (uml, bpmn), сентябрь 2024 - август 2026")
dv = json.load(open(D / "wordstat_uml_bpmn_dinamika_po_ustroystvam_RB_2024-09_2026-08.json", encoding="utf-8"))["series"]
for q in ("uml", "bpmn"):
    tot = {d: sum(r["value"] for r in dv[f"{q}|{d}"]) for d in ("desktop", "phone", "tablet")}
    s = sum(tot.values())
    print(f"{q}: всего {s}; десктопы {tot['desktop']} ({tot['desktop'] / s * 100:.1f} %), "
          f"смартфоны {tot['phone']} ({tot['phone'] / s * 100:.1f} %), планшеты {tot['tablet']} ({tot['tablet'] / s * 100:.1f} %)")
    for d in tot:
        a = sum(r["value"] for r in dv[f"{q}|{d}"][:12])
        b = sum(r["value"] for r in dv[f"{q}|{d}"][12:])
        print(f"   {d}: 1-й год {a}, 2-й год {b}, изменение {(b / a - 1) * 100:.1f} %")
    ph = [r["value"] for r in dv[f"{q}|phone"]]
    dsk = [r["value"] for r in dv[f"{q}|desktop"]]
    tb = [r["value"] for r in dv[f"{q}|tablet"]]
    print(f"   смартфоны: июнь 2026 {ph[-3]}, июль 2026 {ph[-2]}, август 2026 {ph[-1]}; медиана за 23 предыдущих месяца {sorted(ph[:-1])[11]}")
    print(f"   десктопы: август 2026 {dsk[-1]}")
    print("   доля смартфонов по месяцам, %: " + " ".join(f"{p / (p + d + t) * 100:.0f}" for p, d, t in zip(ph, dsk, tb)))

print("\n[5] Дрейф скользящего окна «Топы запросов»: те же запросы в окнах 25.08-23.09 и 29.08-29.09.2026")
old = {"uml": 591, "bpmn": 476, "plantuml": 198, "idef0": 105, "dfd диаграмма": 28, "erd диаграмма": 24,
       "сеть петри": 8, "нейросеть схема": 76, "нейросеть диаграмма": 31, "miro": 1660, "visio": 1501,
       "draw io": 1072, "creately": 4}
new = {"uml": 652, "bpmn": 473, "plantuml": 200, "idef0": 101, "dfd диаграмма": 28, "erd диаграмма": 25,
       "сеть петри": 16, "нейросеть схема": 81, "нейросеть диаграмма": 28, "miro": 1713, "visio": 1507,
       "draw io": 1142, "creately": 3}
for k in old:
    print(f"{k}: {old[k]} -> {new[k]} ({(new[k] / old[k] - 1) * 100:+.1f} %)")

print("\n[6] Регионы Вордстата по bpmn и uml, окно 29.08-29.09.2026 (запросы; индекс интереса, %)")
rg = json.load(open(D / "wordstat_regiony_bpmn_uml_RB_okno_2026-08-29_09-29.json", encoding="utf-8"))
for q in ("bpmn", "uml"):
    by = [r for r in rg[q] if r[0] == "Беларусь"][0][1]
    mo = [r for r in rg[q] if r[0] == "Минск и область"][0][1]
    mk = [r for r in rg[q] if r[0] == "Минск"][0][1]
    print(f"{q}: Беларусь {by}; Минск и область {mo} ({mo / by * 100:.1f} % от Беларуси); Минск {mk} ({mk / by * 100:.1f} %)")
    obl = ["Брест и область", "Витебск и область", "Гомель и область", "Гродно и область", "Могилёв и область", "Минск и область"]
    print(f"   сумма шести областей (с Минском и Минской областью) = {sum(r[1] for r in rg[q] if r[0] in obl)}")
print("Предыдущее окно 25.08-23.09.2026: bpmn Беларусь 428 (73,98), Минск и область 330 (124,33), Минск 258 (139,15); "
      "uml Беларусь 513 (127,61), Минск и область 372 (194,99)")

print("\n[7] Коммерческие, проблемные, сегментные, географические и обучающие формулировки (Топы, окно 29.08-29.09.2026)")
tp = json.load(open(D / "wordstat_topy_kommercheskie_problemnye_segmentnye_geo_RB_okno_2026-08-29_09-29.json",
                    encoding="utf-8"))["queries"]
for r in tp[:23]:
    print(f"{r['query']}: {r['total']}" + (f" [{r['rows']}]" if r["rows"] else ""))
