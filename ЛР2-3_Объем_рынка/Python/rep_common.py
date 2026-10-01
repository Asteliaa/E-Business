# -*- coding: utf-8 -*-
"""Общие функции сборки ОТЧЕТ.md: форматирование чисел, таблицы с подписями, рисунки, чтение значений Excel-копий."""
import json
import os
import re
import warnings

import openpyxl

warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
XL = os.path.join(ROOT, "Excel")
R = json.load(open(os.path.join(HERE, "results.json"), encoding="utf-8"))
ALT = json.load(open(os.path.join(HERE, "results_alt48.json"), encoding="utf-8"))   # расчёт при чеке 48 USD в год (4 USD x 12)
OUT = {k: json.load(open(os.path.join(HERE, f"out_{k}_excel.json"), encoding="utf-8")) for k in ("ps", "cv", "pl", "pk", "sv", "sc", "sw")}

NBSP = " "


def n(x, d=0, sign=False):
    """Число в русском формате: разряды пробелом, десятичная запятая."""
    if x is None or x == "":
        return "—"
    if isinstance(x, str):
        return x
    s = f"{abs(x):,.{d}f}".replace(",", NBSP).replace(".", ",")
    neg = x < 0 and float(s.replace(NBSP, "").replace(",", ".")) != 0
    return ("−" if neg else ("+" if sign else "")) + s


def pct(x, d=1):
    return n(x * 100, d) + " %" if isinstance(x, (int, float)) else str(x)


def rng3(v, d=0):
    return " / ".join(n(x, d) for x in v)


_books = {}


def wb(name):
    if name not in _books:
        _books[name] = openpyxl.load_workbook(os.path.join(XL, name), data_only=True)
    return _books[name]


def cell(book, sheet, addr):
    return wb(book)[sheet][addr].value


def cells(book, sheet, rng):
    ws = wb(book)[sheet]
    return [[c.value for c in row] for row in ws[rng]]


def fv(v, d=2):
    """Значение ячейки Excel для таблицы."""
    if v is None or v == "":
        return "—"
    if isinstance(v, (int, float)):
        if isinstance(v, float) and abs(v) < 1 and v != 0:
            return n(v, 4 if abs(v) < 0.01 else 3)
        return n(v, d if isinstance(v, float) and v != int(v) else 0)
    if hasattr(v, "strftime"):
        return v.strftime("%d.%m.%Y")
    return str(v).replace("|", "/").replace("\n", " ")


class Doc:
    """Накопитель текста с сквозной нумерацией таблиц и рисунков."""

    def __init__(self):
        self.parts = []
        self.tab = {}
        self.fig = {}
        self.figinfo = {}

    def add(self, text=""):
        self.parts.append(text.rstrip("\n") + "\n")

    def h(self, level, title):
        self.parts.append("#" * level + " " + title + "\n")

    def table(self, key, title, header, rows, note=None):
        assert key not in self.tab, key
        self.tab[key] = len(self.tab) + 1
        lines = [f"Таблица {{T:{key}}} – {title}", "", "| " + " | ".join(header) + " |", "|" + "|".join("---" for _ in header) + "|"]
        for r in rows:
            cells_ = [str(c).replace("|", "/").replace("\n", " ") if c is not None and c != "" else "—" for c in r]
            assert len(cells_) == len(header), (key, len(cells_), len(header), cells_)
            lines.append("| " + " | ".join(cells_) + " |")
        self.parts.append("\n".join(lines) + "\n")
        if note:
            self.parts.append(note.rstrip() + "\n")

    def figure(self, key, file, title):
        assert key not in self.fig, key
        self.fig[key] = len(self.fig) + 1
        self.figinfo[key] = (file, title)
        self.parts.append(f"![](Рисунки/{file})\n\nРисунок {{F:{key}}} – {title}\n")

    def text(self):
        t = "\n".join(self.parts)
        t = re.sub(r"\{T:(\w+)\}", lambda m: str(self.tab[m.group(1)]), t)
        t = re.sub(r"\{F:(\w+)\}", lambda m: str(self.fig[m.group(1)]), t)
        return t


SOURCES = {
    "bel_edu": "Образование в Республике Беларусь, 2026: статистический сборник. — Минск: Национальный статистический комитет Республики Беларусь, 2026. — Табл. 7.1. — Режим доступа: https://www.belstat.gov.by/upload/iblock/6af/m93v33ohm51kl00b333cmrhjbhj42ouo.pdf. — Дата доступа: 30.09.2026.",
    "bel_dig": "Национальные статистические показатели развития цифровой экономики, 2024 [Электронный ресурс]. — Национальный статистический комитет Республики Беларусь. — Режим доступа: https://www.belstat.gov.by/upload-belstat/upload-belstat-excel/Oficial_statistika/2024/digital_economy-2024.xls. — Дата доступа: 30.09.2026.",
    "bel_exp": "Основные социально-экономические показатели Республики Беларусь, январь–август 2026 г.: экспресс-информация [Электронный ресурс]. — Национальный статистический комитет Республики Беларусь. — Режим доступа: https://www.belstat.gov.by/upload-belstat/upload-belstat-excel/Oficial_statistika/2026/express_info-2608.xlsx. — Дата доступа: 30.09.2026.",
    "bel_zp": "Номинальная начисленная средняя заработная плата работников Республики Беларусь по видам экономической деятельности, июль 2026 г. [Электронный ресурс]. — Национальный статистический комитет Республики Беларусь. — Режим доступа: https://www.belstat.gov.by/upload-belstat/upload-belstat-excel/Oficial_statistika/2026/nach_sr_zarplata-2607.xlsx. — Дата доступа: 30.09.2026.",
    "teenage": "Сравниваем стипендии в белорусских вузах [Электронный ресурс]. — Teenage.by, 2026. — Режим доступа: https://teenage.by/article/sravnivaem-stipendiju-v-belorusskih-vuzah. — Дата доступа: 30.09.2026.",
    "bsuir": "Стипендии БГУИР [Электронный ресурс]. — Белорусский государственный университет информатики и радиоэлектроники. — Режим доступа: https://www.bsuir.by/ru/stipendii-bguir. — Дата доступа: 30.09.2026.",
    "pvt": "Парк высоких технологий: факты [Электронный ресурс]. — Режим доступа: https://www.park.by/htp/facts/. — Дата доступа: 30.09.2026.",
    "datarep": "Digital 2026: Belarus [Электронный ресурс]. — DataReportal. — Режим доступа: https://datareportal.com/reports/digital-2026-belarus. — Дата доступа: 30.09.2026.",
    "nbrb": "Официальные курсы валют, USD [Электронный ресурс]. — Национальный банк Республики Беларусь. — Режим доступа: https://api.nbrb.by/exrates/rates/431. — Дата доступа: 30.09.2026.",
    "wordstat": "Яндекс Вордстат [Электронный ресурс]. — Яндекс. — Режим доступа: https://wordstat.yandex.ru/. — Дата доступа: 30.09.2026. Регион «Беларусь».",
    "gt": "Google Trends [Электронный ресурс]. — Google. — Режим доступа: https://trends.google.com/. — Дата доступа: 30.09.2026. Территория «Беларусь».",
    "gt_help": "Google Trends Help. FAQ about Google Trends data [Электронный ресурс]. — Режим доступа: https://support.google.com/trends/answer/4365533. — Дата доступа: 30.09.2026.",
    "sw_plantuml": "plantuml.com Traffic Analytics, Ranking & Audience [Электронный ресурс]. — Similarweb. — Режим доступа: https://www.similarweb.com/website/plantuml.com/. — Дата доступа: 30.09.2026.",
    "sw_method": "Similarweb Data Methodology [Электронный ресурс]. — Режим доступа: https://support.similarweb.com/hc/en-us/articles/360001631538-Similarweb-Data-Methodology. — Дата доступа: 30.09.2026.",
    "vsm": "Visual Studio Marketplace: Extensions [Электронный ресурс]. — Microsoft. — Режим доступа: https://marketplace.visualstudio.com/. — Дата доступа: 30.09.2026. Публичный интерфейс extensionquery.",
    "jbm": "JetBrains Marketplace [Электронный ресурс]. — JetBrains. — Режим доступа: https://plugins.jetbrains.com/. — Дата доступа: 30.09.2026. Публичный интерфейс.",
    "capterra": "Capterra: Lucidchart, Miro, draw.io, Creately, Whimsical, Visual Paradigm — отзывы [Электронный ресурс]. — Режим доступа: https://www.capterra.com/. — Дата доступа: 30.09.2026.",
    "github": "GitHub REST API: repositories [Электронный ресурс]. — Режим доступа: https://api.github.com/. — Дата доступа: 30.09.2026.",
    "npm": "npm downloads API [Электронный ресурс]. — Режим доступа: https://api.npmjs.org/downloads/. — Дата доступа: 30.09.2026.",
    "miro": "Miro Pricing [Электронный ресурс]. — Режим доступа: https://miro.com/pricing/. — Дата доступа: 30.09.2026.",
    "lucid": "Lucidchart Pricing [Электронный ресурс]. — Режим доступа: https://lucid.app/pricing/lucidchart. — Дата доступа: 30.09.2026.",
    "mermaid": "Mermaid Chart Pricing [Электронный ресурс]. — Режим доступа: https://mermaid.ai/pricing. — Дата доступа: 30.09.2026.",
    "vp": "Visual Paradigm Online: Pricing [Электронный ресурс]. — Режим доступа: https://online.visual-paradigm.com/. — Дата доступа: 30.09.2026.",
    "creately": "Creately Plans [Электронный ресурс]. — Режим доступа: https://creately.com/plans/. — Дата доступа: 30.09.2026.",
    "eraser": "Eraser Pricing [Электронный ресурс]. — Режим доступа: https://www.eraser.io/pricing. — Дата доступа: 30.09.2026.",
    "whimsical": "Whimsical Pricing [Электронный ресурс]. — Режим доступа: https://whimsical.com/pricing. — Дата доступа: 30.09.2026.",
    "dbd": "dbdiagram.io Pricing [Электронный ресурс]. — Режим доступа: https://dbdiagram.io/pricing. — Дата доступа: 30.09.2026.",
    "visio": "Microsoft Visio: планы и цены [Электронный ресурс]. — Microsoft. — Режим доступа: https://www.microsoft.com/ru-ru/microsoft-365/visio/flowchart-software. — Дата доступа: 30.09.2026.",
    "concept": "Концепция проекта NotaCode: раздел 6 «Модель монетизации», раздел 8 «Допущения» [Электронный ресурс]. — Документация проекта, 2026.",
    "pravo_bv": "Базовая величина с 1 января 2026 г. [Электронный ресурс]. — Pravo.by, 2025. — Режим доступа: https://pravo.by/novosti/novosti-pravo-by/2025/november/91047/. — Дата доступа: 30.09.2026.",
    "m_instr": "Инструкция по применению методик оценки рынка электронного бизнеса [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_ps": "Методика оценки рынка через поисковый спрос и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_cv": "Методика оценки рынка через цифровую воронку и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_mp": "Методика оценки рынка через маркетплейсы и платформы [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_pl": "Методика проверки рынка через платёжеспособность и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_pk": "Методика оценки объёма рынка через количество потенциальных клиентов и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_sc": "Методика сценарной оценки рынка с данными Similarweb и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_sv": "Методика «сверху вниз» и «снизу вверх» с данными Similarweb и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_swb": "Методика оценки рынка: Similarweb при бесплатном доступе [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_m1": "Методика оценки объёма рынка по данным Similarweb и шаблон Excel [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "m_m2": "Методика оценки рынка на основе данных Similarweb [Электронный ресурс]. — Методические материалы дисциплины «Электронный бизнес», 2026.",
    "ec": "European Commission. Revised Market Definition Notice [Электронный ресурс]. — Режим доступа: https://ec.europa.eu/commission/presscorner/detail/en/ip_23_6001. — Дата доступа: 30.09.2026.",
}
_cited = {}


def cite(*keys):
    """Возвращает [n] или [n, m] в порядке первого упоминания."""
    nums = []
    for k in keys:
        assert k in SOURCES, k
        if k not in _cited:
            _cited[k] = len(_cited) + 1
        nums.append(_cited[k])
    return "[" + ", ".join(str(x) for x in nums) + "]"


def source_list():
    return "\n".join(f"{i}. {SOURCES[k]}" for k, i in sorted(_cited.items(), key=lambda t: t[1]))

T = "{T:todo}"
