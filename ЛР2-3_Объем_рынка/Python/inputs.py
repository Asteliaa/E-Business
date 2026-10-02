# -*- coding: utf-8 -*-
"""Исходные данные ЛР2-3: собранные значения (с источниками) и допущения проекта.

Все числа разделены на три класса:
  ФАКТ        - значение взято из открытого источника (дата, ссылка в журнале источников);
  ПРОЕКТ      - данные проекта NotaCode (концепция: цена Pro, конверсия Free -> Pro);
  ДОПУЩЕНИЕ   - значение задано автором в диапазоне шкалы методики, где фактических данных нет
                (каждое допущение имеет код Д-NN и запись в журнале допущений).
"""
import csv
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "Материалы_собранные")

DATE = "30.09.2026"

# ---------------------------------------------------------------- курс, цена
FX = 3.0285                     # НБРБ, USD/BYN на 30.09.2026 (ФАКТ, решение В-12)
PRICE_USD_MONTH = 4.0           # ПРОЕКТ: помесячный тариф Pro, концепция NotaCode, раздел 6 (гипотеза A-06)
PRICE_USD_YEAR_BASE = 40.0      # ПРОЕКТ: основной годовой чек Pro (решение В-5)
PRICE_USD_YEAR_ALT = PRICE_USD_MONTH * 12    # 48 USD: альтернативный вариант (4 USD x 12), показывается рядом
PRICE_USD_YEAR_DISCOUNT = PRICE_USD_YEAR_BASE   # имя сохранено для совместимости сценариев
PRICE_BYN_MONTH = PRICE_USD_YEAR_BASE * FX / 12     # 10,10 BYN: месячный эквивалент годового тарифа 40 USD
PRICE_BYN_MONTH_ALT = PRICE_USD_YEAR_ALT * FX / 12  # 12,11 BYN: эквивалент 48 USD/год (= 4 USD x курс)
PRICE_BYN_YEAR_BASE = PRICE_USD_YEAR_BASE * FX
PRICE_BYN_YEAR_ALT = PRICE_USD_YEAR_ALT * FX
PRICE_BYN_YEAR_DISC = PRICE_BYN_YEAR_BASE

# Конверсия Free -> Pro: ПРОЕКТ (концепция раздел 6): 3-5 %
from assumptions import CR_PRO, INTENT_WEIGHT as _IW, SEG_K, BUDGET_SHARE, REL_SHARE, QUALITY

# Тарифы платных планов (USD/мес., оплата за год; страницы тарифов, 30.09.2026)
# ФАКТ; порядок: (продукт, тариф, цена USD/мес, примечание)
PRICES = [
    ("Lucidchart", "Individual", 9.0, "оплата за год, без НДС"),
    ("Lucidchart", "Team (за пользователя)", 10.0, "оплата за год, без НДС"),
    ("Miro", "Starter (за участника)", 8.0, "оплата за год"),
    ("Miro", "Business (за участника)", 20.0, "оплата за год"),
    ("Mermaid Chart", "Plus (за пользователя)", 10.0, "оплата за год"),
    ("Mermaid Chart", "Premium (за пользователя)", 20.0, "оплата за год"),
    ("Visual Paradigm Online", "Starter", 4.0, "оплата за год"),
    ("Visual Paradigm Online", "Advance", 9.0, "оплата за год"),
    ("Visual Paradigm Online", "Combo", 15.0, "оплата за год; включает VPasCode (PlantUML/Mermaid)"),
    ("Visual Paradigm Online", "Deluxe", 30.0, "оплата за год"),
    ("Creately", "Starter", 5.0, "оплата за год (8 USD помесячно)"),
    ("Creately", "Team", 5.0, "по данным страницы тарифов (plans)"),
    ("Creately", "Business", 89.0, "по данным страницы тарифов (plans)"),
    ("Eraser", "Starter", 15.0, "оплата за год (20 USD помесячно)"),
    ("Eraser", "Business", 45.0, "оплата за год (60 USD помесячно)"),
    ("Whimsical", "Pro", 10.0, "оплата за год"),
    ("Whimsical", "Business", 20.0, "оплата за год"),
    ("dbdiagram.io", "Personal Pro", 8.0, "цена при помесячной оплате"),
    ("Microsoft Visio", "Plan 1", 5.0, "оплата за год, за пользователя"),
    ("Microsoft Visio", "Plan 2", 15.0, "оплата за год, за пользователя"),
]
# Входные (минимальные платные) тарифы по продуктам - для "чека по ценам конкурентов"
ENTRY_PRICES = {
    "Lucidchart": 9.0, "Miro": 8.0, "Mermaid Chart": 10.0, "Visual Paradigm Online": 4.0,
    "Creately": 5.0, "Eraser": 15.0, "Whimsical": 10.0, "dbdiagram.io": 8.0, "Microsoft Visio": 5.0,
}

# ---------------------------------------------------------------- статистика (ФАКТ)
STUD_TOTAL = 229_000            # студенты УВО РБ, начало 2025/26 (Белстат, сб. «Образование в РБ, 2026», табл. 7.1)
STUD_PREV = 224_200             # 2024/25
PPS = 17_100                    # ППС вузов (там же)
DIGITAL_ORGS = 8_533            # организации цифровой экономики, 2024 (Белстат)
ICT_ORGS = 5_462
DIGITAL_WORKERS = 130_549       # работники организаций цифровой экономики, 2024 (Белстат, digital_economy-2024.xls)
ICT_WORKERS = 104_381
PVT_WORKERS = 60_000            # порядка, park.by (страница без даты; данные за 2025)
ICT_SALARY_2024 = 5_661.8       # BYN, средняя з/п сектора ИКТ, 2024
SALARY_ALL_JUL2026 = 3_172.0    # BYN, средняя начисленная з/п по РБ, июль 2026
SALARY_INFO_JUL2026 = 6_413.0   # BYN, «информация и связь», июль 2026 (Белстат, nach_sr_zarplata-2607.xlsx)
STIPEND_MIN, STIPEND_MAX = 229.75, 367.60   # БГУИР ИКТ-специальности с 01.08.2026 (таблица bsuir.by), BYN/мес.
STIPEND_SOCIAL = 128.38
BASE_UNIT = 45.0                # базовая величина, BYN (с 01.01.2026)
MSP_ORGS, MSP_IE = 135_000, 204_400   # МСП на 01.01.2026 (в расчётах не используются: B2B-сегмента нет)
INTERNET_SHARE = 0.943          # Белстат 2024, 6-72 года

# ---------------------------------------------------------------- Вордстат
def _load(name):
    with open(os.path.join(RAW, "Wordstat_Беларусь", name), encoding="utf-8") as f:
        return json.load(f)

WS_CORE = _load("wordstat_core_RB_2026-09-30.json")["data"]
WS_GRP = _load("wordstat_groups_RB_2026-09-30.json")["data"]
WS_ALL = {**WS_CORE, **WS_GRP}

MONTHS_24 = [(2024 + (8 + i) // 12, (8 + i) % 12 + 1) for i in range(24)]   # 2024-09 .. 2026-08
MONTHS_12 = MONTHS_24[12:]                                                  # 2025-09 .. 2026-08
PREV_12 = MONTHS_24[:12]

def ws12(q):
    return WS_ALL[q]["m"][12:]

def ws_prev12(q):
    return WS_ALL[q]["m"][:12]

def _sum_series(queries, which=12):
    n = 24
    tot = [0] * n
    for q in queries:
        for i, v in enumerate(WS_ALL[q]["m"]):
            tot[i] += v
    return tot[12:] if which == 12 else tot[:12]

# Группы запросов ядра для ПС-X/04_Wordstat (суммы рядов отдельных формулировок; операторы в «Динамике» не работают)
GROUP_QUERIES = {
    "Коммерческие запросы": ["visio купить", "uml купить", "miro подписка", "visio лицензия", "miro стоимость"],
    "Проблемные запросы": ["idef0 как", "bpmn пример", "uml пример", "idef0 пример", "dfd пример"],
    "Инструментальные запросы": ["uml онлайн", "bpmn онлайн", "idef0 онлайн", "bpmn скачать", "uml скачать",
                                 "plantuml editor", "uml editor", "plantuml online", "bpmn редактор",
                                 "uml редактор", "idef0 программа",
                                 "нейросеть схема", "нейросеть диаграмма",
                                 "конструктор диаграмм онлайн", "конструктор схем онлайн"],
    "Локальные запросы": [],   # динамика недоступна: формулировки с «минск» дают ряд ниже порога отображения
}
GROUP_SERIES = {g: (_sum_series(qs) if qs else [0] * 12) for g, qs in GROUP_QUERIES.items()}
GROUP_SERIES_PREV = {g: (_sum_series(qs, 0) if qs else [0] * 12) for g, qs in GROUP_QUERIES.items()}

# Веса намерений (ПС табл. 9) - значения внутри диапазонов методики (Д-03)
INTENT_WEIGHT = _IW

# Строки 02_Семантика (ПС-X): запрос, группа, намерение, регион, частотность (Топы, 30 дней), GT-индекс, релевантность, близость
SEMANTICS = [
    ("uml купить", "Коммерческий спрос", "коммерческое", "РБ", WS_ALL["uml купить"]["top"], "н/д", 1.00, 0.90),
    ("visio купить", "Коммерческий спрос", "коммерческое", "РБ", WS_ALL["visio купить"]["top"], "н/д", 0.70, 0.85),
    ("uml онлайн", "Инструментальный спрос", "инструментальное", "РБ", WS_ALL["uml онлайн"]["top"], "н/д", 1.00, 0.65),
    ("bpmn онлайн", "Инструментальный спрос", "инструментальное", "РБ", WS_ALL["bpmn онлайн"]["top"], "н/д", 0.90, 0.65),
    ("plantuml online", "Инструментальный спрос", "инструментальное", "РБ", WS_ALL["plantuml online"]["top"], "н/д", 0.90, 0.70),
    ("нейросеть схема", "Инструментальный спрос", "инструментальное (AI)", "РБ", WS_ALL["нейросеть схема"]["top"], "н/д", 0.70, 0.55),
    ("idef0 как", "Проблемный спрос", "проблемное", "РБ", WS_ALL["idef0 как"]["top"], "н/д", 1.00, 0.45),
    ("bpmn пример", "Проблемный спрос", "проблемное", "РБ", WS_ALL["bpmn пример"]["top"], "н/д", 0.90, 0.40),
    ("uml", "Общий тематический спрос", "информационное", "РБ", WS_ALL["uml"]["top"], None, 1.00, 0.20),
    ("mermaid", "Исключаемый (омоним)", "омоним: фильм", "РБ", 1163, "н/д", 0.00, 0.00),
]

# GT (Беларусь, 12 мес.; единая шкала четырёх запросов)
def load_gt_weekly():
    rows = []
    p = os.path.join(RAW, "GT_Беларусь_ЛР2-3", "GT_2026-09-30_BY_12m_UML_BPMN_PlantUML_IDEF0_weekly.csv")
    with open(p, encoding="utf-8") as f:
        for r in csv.DictReader(f, delimiter=";"):
            rows.append(r)
    return rows

def gt_monthly():
    """Месячные индексы: простое среднее недель месяца (по дате начала недели), сентябрь 2025 - август 2026."""
    rows = load_gt_weekly()
    acc = {}
    for r in rows:
        y, m = int(r["week_start"][:4]), int(r["week_start"][5:7])
        acc.setdefault((y, m), []).append([float(r[k]) for k in ("UML", "BPMN", "PlantUML", "IDEF0")])
    out = []
    for ym in MONTHS_12:
        ws = acc.get(ym, [])
        out.append([round(sum(w[i] for w in ws) / len(ws), 2) if ws else 0 for i in range(4)])
    return out

GT_MONTHLY = gt_monthly()

# ---------------------------------------------------------------- Similarweb (бесплатная карточка, последние 3 месяца)
# ФАКТ только по plantuml.com (замер 30.09.2026, август 2026). Остальные визиты - из отчёта ЛР1 и предварительного замера 17-23.09.2026 (не подтверждены
# скриншотом; повторный замер невозможен: лимит бесплатных просмотров). Mermaid Chart - верхняя граница («менее 20 тыс.»).
SW_RUSSIA_SHARE_PLANTUML = 0.0907
# вкладка «Регионы» Вордстата, запрос plantuml, окно 29.08.2026-27.09.2026, снято 30.09.2026 (файл Wordstat_Регионы_из_ЛР1)
WS_PLANTUML_BY, WS_PLANTUML_RU, WS_PLANTUML_KZ = 170, 7874, 154
WS_PLANTUML_MINSK, WS_PLANTUML_MINSK_OBL = 124, 142
# Допущение Д-01: доля Беларуси в визитах = доля России по Similarweb x отношение числа запросов Беларусь/Россия в Вордстате
GEO_BY = SW_RUSSIA_SHARE_PLANTUML * WS_PLANTUML_BY / WS_PLANTUML_RU           # ~0,1958 %
GEO_MINSK = GEO_BY * WS_PLANTUML_MINSK / WS_PLANTUML_BY                        # Минск (город)
SW_DOMAINS = [
    # домен, название, тип, визиты/мес., статус данных, доля релевантного трафика (Д-02), коэф. качества, комментарий
    ("plantuml.com", "PlantUML", "прямой (текстовый DSL)", 507_000, "ФАКТ (Similarweb, авг. 2026, скриншот)", REL_SHARE["plantuml.com"], QUALITY["plantuml.com"]),
    ("app.diagrams.net", "draw.io (diagrams.net)", "заменитель (визуальный редактор)", 7_800_000, "отчёт ЛР1, без скриншота", REL_SHARE["app.diagrams.net"], QUALITY["app.diagrams.net"]),
    ("eraser.io", "Eraser", "прямой (AI + diagram as code)", 678_500, "предварительный замер 17–23.09.2026, не подтверждён", REL_SHARE["eraser.io"], QUALITY["eraser.io"]),
    ("mermaidchart.com", "Mermaid Chart", "прямой (текстовый DSL)", 20_000, "предварительный замер: «менее 20 тыс.» (верхняя граница), не подтверждён", REL_SHARE["mermaidchart.com"], QUALITY["mermaidchart.com"]),
]

# ---------------------------------------------------------------- Маркетплейсы
def load_marketplaces():
    p = os.path.join(RAW, "Маркетплейсы", "marketplaces.csv")
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.reader(f, delimiter=";"))

if __name__ == "__main__":
    print("FX", FX, "цена/год BYN", round(PRICE_BYN_YEAR_BASE, 2), "мес.", round(PRICE_BYN_MONTH, 3))
    print("GEO_BY %.4f%%  Минск %.4f%%" % (GEO_BY * 100, GEO_MINSK * 100))
    for g, s in GROUP_SERIES.items():
        print(g, sum(s), s)
    print("GT", GT_MONTHLY)


# ---------------------------------------------------------------- сегменты клиентов (ПК-X, ПЛ-X, СВ-X)
# К1-К5 - коэффициенты сужения по ПК табл. 7; значения задаются внутри диапазонов методики (допущения Д-06..Д-10)
# К1 релевантность сегмента: 10-20 / 20-40 / 40-60 %;   К2 наличие потребности: 5-15 / 15-30 / 30-50 %
# К3 цифровая доступность: 20-40 / 40-70 / 70-90 %;     К4 готовность платить: 5-10 / 10-25 / 25-40 %
# К5 достижимая доля: 0,5-1 / 1-3 / 3-7 %
SEGMENTS = [
    # код, название, численность, источник численности, К1, К2, К3, К4, К5, доход/мес. (BYN), тариф
    dict(code="S-01", name="Студенты технических и экономических специальностей", pop=STUD_TOTAL,
         src="Белстат, «Образование в Республике Беларусь, 2026», табл. 7.1 (229,0 тыс., 2025/26)",
         **SEG_K["S-01"], income=round((STIPEND_MIN + STIPEND_MAX) / 2, 2),
         income_src="стипендия БГУИР (ИКТ), середина диапазона 229,75–367,60 BYN (таблица БГУИР с 01.08.2026)", tariff="Free (первичный)", reliab="Средняя"),
    dict(code="S-02/S-03", name="Аналитики, архитекторы ПО и разработчики", pop=DIGITAL_WORKERS,
         src="Белстат, работники организаций цифровой экономики, 2024 (130 549)",
         **SEG_K["S-02/S-03"], income=SALARY_INFO_JUL2026,
         income_src="средняя з/п «информация и связь», июль 2026 (6 413 BYN, Белстат)", tariff="Pro", reliab="Низкая"),
    dict(code="S-04", name="Преподаватели технических дисциплин", pop=PPS,
         src="Белстат, ППС вузов (17,1 тыс., 2025/26); доля технических дисциплин неизвестна",
         **SEG_K["S-04"], income=SALARY_ALL_JUL2026,
         income_src="средняя з/п по РБ, июль 2026 (3 172,0 BYN; данных по преподавателям нет)", tariff="Free / Pro", reliab="Низкая"),
]
