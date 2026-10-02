# -*- coding: utf-8 -*-
"""Общие входные данные ЛР5: загрузка собранных материалов ЛР1-ЛР4 и справочные константы.

Все числа читаются из файлов папок ЛР4/Материалы_собранные и ЛР2-3/Материалы_собранные;
вручную здесь заданы только значения, взятые из отчётов ЛР1 (табл. 42, 44) и ЛР2-3 (табл. 61, 70)."""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
LAB5 = os.path.dirname(HERE)
ROOT = os.path.dirname(LAB5)
COLL4 = os.path.join(ROOT, "ЛР4_Пять_сил_Портера", "Материалы_собранные")
COLL23 = os.path.join(ROOT, "ЛР2-3_Объем_рынка", "Материалы_собранные")
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

DATE = "30.09.2026"
RATE = 3.0285  # BYN за USD, НБРБ на 30.09.2026 (ЛР2-3)

F_TITLE = "sajty_konkurentov_title_description_2026-09-30.json"
F_FLAGS = "sajty_konkurentov_priznaki_2026-09-30.json"
F_SW = "similarweb_pro_obzor_2026-09-30.csv"
F_SWNOTE = "similarweb_pro_ogovorki_2026-09-30.md"
F_GH = "github_repos_2026-09-30.json"
F_TP = "trustpilot_reviews_2026-09-30.json"
F_RDAP = "rdap_domeny_2026-09-30.json"
F_AGE = "vozrast_domenov_raschet_2026-09-30.json"
F_WS = "wordstat_zaprosy_RB_2026-09-30.csv"
F_SEM = "semrush_website_overview_visits_2026-08_snyato_2026-09-30.csv"
F_MKT = "marketplaces.csv"
F_REV = "rev05.csv"


def _json(path):
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def _csv(path, delim=";"):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f, delimiter=delim))


def num(x):
    if x is None:
        return None
    s = str(x).strip().replace(",", ".")
    if s == "" or s.lower() in ("n/a", "нет данных"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


TITLES = _json(os.path.join(COLL4, F_TITLE))["data"]
TITLES["whimsical.com"] = {"title": "Whimsical - The whiteboard for product builders", "description": "Диаграммы, схемы интерфейсов, документы (страница whimsical.com, 01.10.2026)"}
TITLES["lucidchart.com"] = {"title": "Lucidchart | Diagramming Powered By Intelligence", "description": "Diagramming powered by intelligence (страница lucid.co/lucidchart, 01.10.2026, встроенный браузер)"}
FLAGS = _json(os.path.join(COLL4, F_FLAGS))["data"]
GH = {r["repo"]: r for r in _json(os.path.join(COLL4, F_GH))["data"]}
TP = _json(os.path.join(COLL4, F_TP))["data"]
AGE = _json(os.path.join(COLL4, F_AGE))
SW = {r["domain"]: r for r in _csv(os.path.join(COLL4, F_SW))}
WS = {r["query"]: int(r["count_per_window"]) for r in _csv(os.path.join(COLL4, F_WS))}
REV = {r["site"]: r for r in _csv(os.path.join(ROOT, "ЛР4_Пять_сил_Портера", "Python", "data", F_REV))}

# Значения из отчёта ЛР1 (Вордстат, Беларусь, 30 дней на 29.09.2026) для брендов, которых нет в файле ЛР4
WS_LR1 = {"miro": 1660, "visio": 1501, "draw io": 1072, "excalidraw": 70, "diagrams.net": 61,
          "visual paradigm": 46, "lucidchart": 24, "staruml": 16, "creately": 4,
          "sparx enterprise architect": 9, "mermaid diagram": 19, "whimsical": 59}

# Тарифы: ЛР1 табл. 42 (USD в месяц при оплате за год) и ЛР2-3 табл. 70 (BYN в месяц)
PRICING = {
    "plantuml.com": dict(free=True, entry=None, note="открытый код, бесплатно (ЛР1, табл. 42)", src="plantuml.com"),
    "mermaid.js.org": dict(free=True, entry=None, note="открытый код (MIT); платные планы у Mermaid Chart", src="mermaid.js.org"),
    "mermaidchart.com": dict(free=True, entry=10, tiers="Free (до 6 диаграмм, 15 AI-кредитов); Plus 10 USD; Premium 20 USD за пользователя в месяц при оплате за год; Enterprise по запросу",
                             byn=(30.29, 45.43, 60.57), src="https://mermaid.ai/pricing"),
    "lucidchart.com": dict(free=True, entry=9, tiers="Free (3 редактируемых документа, 75 фигур на документ); Individual 9 USD; Team 10 USD за пользователя в месяц при оплате за год; Enterprise по запросу",
                           byn=(27.26, 28.77, 30.29), src="https://lucid.app/pricing/lucidchart"),
    "miro.com": dict(free=True, entry=8, tiers="Free (3 редактируемые доски); Starter 8 USD; Business 20 USD за участника в месяц при оплате за год; Enterprise по запросу",
                     byn=(24.23, 42.40, 60.57), src="https://miro.com/pricing/"),
    "microsoft.com/visio": dict(free=False, entry=5, tiers="Plan 1 - 5 USD, Plan 2 - 15 USD за пользователя в месяц при оплате за год; бесплатного тарифа нет (пробный месяц)",
                                byn=None, src="https://www.microsoft.com/ru-ru/microsoft-365/visio/flowchart-software"),
    "app.diagrams.net": dict(free=True, entry=None, note="полностью бесплатный, открытый код (Apache 2.0) (ЛР1, табл. 42)", src="https://www.drawio.com/"),
    "visual-paradigm.com": dict(free=False, entry=6, tiers="Подписка: Modeler 6, Standard 19, Professional 35, Enterprise 89 USD в месяц; бессрочные лицензии: 99, 349, 799, 1999 USD; бесплатного тарифа на странице магазина нет",
                                byn=None, src="https://www.visual-paradigm.com/shop/"),
    "creately.com": dict(free=None, entry=5, tiers="Платные тарифы от 5 до 89 USD в месяц (ЛР2-3, табл. 70: 15,14 - 269,54 BYN)",
                         byn=(15.14, 15.14, 269.54), src="https://creately.com/plans/"),
    "eraser.io": dict(free=True, entry=15, tiers="Free (0 USD; 3 файла, 3 ИИ-диаграммы); Starter 15 USD (20 USD при помесячной оплате); Business 45 USD (60 USD); Enterprise по запросу; цены за участника в месяц (страница тарифов, 01.10.2026)",
                      byn=(45.43, 90.86, 136.28), src="https://www.eraser.io/pricing"),
    "whimsical.com": dict(free=True, entry=10, tiers="Free (0 USD; 50 объектов доски и 50 блоков документа в месяц, водяной знак при экспорте); Pro 10 USD, Business 20 USD за редактора в месяц (страница тарифов, 01.10.2026)",
                          byn=(30.29, 45.43, 60.57), src="https://whimsical.com/pricing"),
    "dbdiagram.io": dict(free=None, entry=8, tiers="Платный тариф около 8 USD в месяц (ЛР2-3, табл. 70: 24,23 BYN)",
                         byn=(24.23, 24.23, 24.23), src="https://dbdiagram.io/pricing"),
}

# Независимые отзывы (G2, Capterra, Trustpilot, Product Hunt, каталоги расширений): значения считаны 30.09.2026 из файлов ЛР2-3 и ЛР4
REVIEWS = {
    "plantuml.com": dict(n=207, txt="оценки расширений: VS Marketplace jebbs.plantuml 4,72 (105), JetBrains plantuml4idea 4,63 (102); G2 и Trustpilot: карточка не найдена"),
    "mermaid.js.org": dict(n=169, txt="оценки расширений: VS Marketplace (bierner.markdown-mermaid 60, vstirbu 27, tomoyukim 17) и JetBrains Mermaid 2,96 (65)"),
    "mermaidchart.com": dict(n=45, txt="G2 (карточка Mermaid) 4,8 (16); Trustpilot 3,5 (3); Product Hunt 4,8 (26)"),
    "app.diagrams.net": dict(n=1991, txt="Capterra 4,6 (773); Trustpilot draw.io 3,4 (11) и diagrams.net 3,8 (2); Atlassian Marketplace draw.io Diagrams 4,8 (1 205)"),
    "lucidchart.com": dict(n=11368, txt="G2 4,5 (8 988); Capterra/GetApp/Software Advice 4,5 (2 264); Trustpilot lucidchart.com 1,5 (116)"),
    "creately.com": dict(n=274, txt="Capterra 4,4 (216); Trustpilot 1,9 (58)"),
    "miro.com": dict(n=15443, txt="G2 4,6 (13 583); Capterra 4,7 (1 705); Trustpilot 2,1 (155)"),
    "visual-paradigm.com": dict(n=21, txt="Capterra 4,3 (19); Trustpilot 3,5 (2)"),
    "sparxsystems.com": dict(n=0, txt="Trustpilot: профиль без отзывов"),
    "camunda.com": dict(n=1, txt="Trustpilot 3,2 (1)"),
    "eraser.io": dict(n=15, txt="Product Hunt 4,9 (10); расширение VS Code 4,8 (5)"),
    "whimsical.com": dict(n=59, txt="Capterra 4,7 (59)"),
}

# Страницы-источники (URL) для доказательств
URL_HOME = {
    "plantuml.com": "https://plantuml.com/", "mermaid.js.org": "https://mermaid.js.org/", "mermaidchart.com": "https://www.mermaidchart.com/",
    "d2lang.com": "https://d2lang.com/", "kroki.io": "https://kroki.io/", "planttext.com": "https://www.planttext.com/",
    "staruml.io": "https://staruml.io/", "visual-paradigm.com": "https://www.visual-paradigm.com/", "sparxsystems.com": "https://sparxsystems.com/",
    "bpmn.io": "https://bpmn.io/", "camunda.com": "https://camunda.com/", "stormbpmn.com": "https://stormbpmn.com/",
    "app.diagrams.net": "https://app.diagrams.net/", "lucidchart.com": "https://www.lucidchart.com/", "creately.com": "https://creately.com/",
    "miro.com": "https://miro.com/", "excalidraw.com": "https://excalidraw.com/", "dbdiagram.io": "https://dbdiagram.io/",
    "drawsql.app": "https://drawsql.app/", "eraser.io": "https://www.eraser.io/", "whimsical.com": "https://whimsical.com/",
}

# Репозитории GitHub по доменам
GH_REPO = {
    "plantuml.com": ["plantuml/plantuml"], "mermaid.js.org": ["mermaid-js/mermaid", "mermaid-js/mermaid-live-editor"],
    "d2lang.com": ["terrastruct/d2"], "kroki.io": ["yuzutech/kroki"], "bpmn.io": ["bpmn-io/bpmn-js"],
    "camunda.com": ["camunda/camunda-modeler"], "app.diagrams.net": ["jgraph/drawio", "jgraph/drawio-desktop"],
    "excalidraw.com": ["excalidraw/excalidraw"], "dbdiagram.io": ["holistics/dbml"],
}

# Ключи Wordstat (Беларусь, запросов за окно 29.08-27.09.2026 и значения ЛР1) для брендов
WS_KEY = {
    "plantuml.com": ("plantuml", "wordstat"), "mermaid.js.org": ("mermaid diagram", "lr1"), "mermaidchart.com": ("mermaidchart", "wordstat"),
    "d2lang.com": ("d2lang", "wordstat"), "kroki.io": ("kroki", "wordstat"), "planttext.com": ("planttext", "wordstat"),
    "staruml.io": ("staruml", "lr1"), "visual-paradigm.com": ("visual paradigm", "lr1"), "sparxsystems.com": ("sparx enterprise architect", "lr1"),
    "bpmn.io": ("bpmn io", "wordstat"), "camunda.com": ("camunda modeler", "wordstat"), "stormbpmn.com": ("stormbpmn", "wordstat"),
    "app.diagrams.net": ("draw io", "lr1"), "lucidchart.com": ("lucidchart", "lr1"), "creately.com": ("creately", "lr1"),
    "miro.com": ("miro", "lr1"), "excalidraw.com": ("excalidraw", "lr1"), "dbdiagram.io": ("dbdiagram", "wordstat"),
    "drawsql.app": ("drawsql", "wordstat"), "eraser.io": ("eraser io", "wordstat"), "whimsical.com": ("whimsical", "lr1"),
    "microsoft.com/visio": ("visio", "lr1"),
}


def ws_brand(domain):
    k = WS_KEY.get(domain)
    if not k:
        return None
    return WS.get(k[0]) if k[1] == "wordstat" else WS_LR1.get(k[0])


def sw(domain):
    r = SW.get(domain)
    if not r:
        return None
    return {k: (num(v) if k not in ("domain", "snapshot", "period", "scope", "duration", "top_countries_share", "comment") else v) for k, v in r.items()}


def age(domain):
    return AGE.get(domain)


def gh_total_stars(domain):
    repos = GH_REPO.get(domain, [])
    out = []
    for r in repos:
        g = GH.get(r)
        if g and g.get("stars") is not None:
            out.append((r, g["stars"], g["forks"], g["license"], g["pushed_at"]))
    return out


def fmt_int(n):
    return f"{int(round(n)):,}".replace(",", " ")


def fmt_num(x, d=2):
    return f"{x:.{d}f}".replace(".", ",")


if __name__ == "__main__":
    print(len(TITLES), len(FLAGS), len(SW), len(WS), len(REV))
    print(sw("plantuml.com"))
    print(ws_brand("plantuml.com"), ws_brand("miro.com"), gh_total_stars("plantuml.com"))
