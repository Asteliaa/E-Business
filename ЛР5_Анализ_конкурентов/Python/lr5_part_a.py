# -*- coding: utf-8 -*-
"""Часть A ЛР5: реестр компаний, оценка критериев C1-C10, расчёт по формулам шаблона, доказательства."""
import lr5_common as C

DATE = C.DATE

WEIGHTS = [20, 15, 18, 10, 8, 8, 7, 7, 4, 3]
CRIT_NAMES = ["Потребительская задача", "Целевая аудитория", "Функциональная заменяемость", "Сценарий использования",
              "Ценовой уровень и форма оплаты", "Каналы продаж и привлечения", "География, язык, регулирование",
              "Модель монетизации", "Зрелость и доверие", "Вероятность переключения"]
LEVELS = ["Прямой конкурент", "Близкий альтернативный конкурент", "Косвенный конкурент / заменитель",
          "Смежная или потенциальная конкуренция", "Не конкурент / объект наблюдения", "Недостаточно данных"]

# --- Реестр: id, название, ключ данных (домен), рынок, тип, товар, сегмент, гипотеза, приоритет, источник обнаружения, C1..C4
# Баллы C1-C4 назначены аналитиком по правилам таблицы «Правила выставления баллов» отчёта; C5-C10 считаются по собранным данным.
COMPANIES = [
    dict(id="K001", name="PlantUML", dom="plantuml.com", market="Весь мир (английский язык)", ctype="Текстовый DSL, открытый код",
         product="Построение UML-диаграмм из текстового описания, экспорт PNG, LaTeX, EPS, SVG", seg="Разработчики, студенты, архитекторы ПО",
         hyp=0, prio="Высокий", disc="ЛР4 табл. 3 (кандидат 1); ЛР1 табл. 44 (прямой конкурент); Вордстат «plantuml»", c=(5, 4, 4, 5), bc=True,
         home_note="Главное обещание совпадает с задачей NotaCode: диаграммы UML из текста"),
    dict(id="K002", name="Mermaid (библиотека)", dom="mermaid.js.org", market="Весь мир (английский язык)", ctype="Текстовый DSL, открытый код",
         product="Диаграммы и визуализации из текста и кода (JavaScript-библиотека)", seg="Разработчики, авторы технической документации",
         hyp=0, prio="Высокий", disc="ЛР4 табл. 3 (кандидат 2); ЛР1 табл. 44 (прямой конкурент)", c=(5, 4, 4, 5), bc=True,
         home_note="Задача та же (диаграммы из текста и кода), нотаций UML/BPMN/IDEF как набора с проверкой правил в описании нет"),
    dict(id="K003", name="Mermaid Chart", dom="mermaidchart.com", market="Весь мир (США, Великобритания, Япония в топ-странах)", ctype="Облачный сервис на основе Mermaid",
         product="Облачный редактор диаграмм Mermaid с тарифами Free, Plus, Premium", seg="Команды разработки и документации",
         hyp=0, prio="Высокий", disc="ЛР4 табл. 3 (кандидат 3); ЛР1 табл. 42 (тарифы)", c=(5, 3, 4, 4), bc=True,
         home_note="Платная надстройка над Mermaid; домен, вероятно, перенесён на mermaid.ai (трафик mermaidchart.com -82,22 %)"),
    dict(id="K004", name="D2 (Terrastruct)", dom="d2lang.com", market="Весь мир", ctype="Текстовый DSL, открытый код",
         product="Язык описания диаграмм D2 и документация", seg="Разработчики, архитекторы ПО",
         hyp=0, prio="Средний", disc="ЛР4 табл. 3 (кандидат 4)", c=(4, 3, 3, 4), bc=False,
         home_note="Описание на главной отсутствует (meta description пуста); отнесение по ЛР4 (язык диаграмм D2)"),
    dict(id="K005", name="Kroki", dom="kroki.io", market="Весь мир", ctype="API отрисовки текстовых диаграмм",
         product="Единый API для отрисовки диаграмм из текста (PlantUML, Mermaid, D2 и др.)", seg="Разработчики, интеграторы",
         hyp=0, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 5); ЛР2-3 (движки рендеринга)", c=(3, 3, 2, 2), bc=False,
         home_note="Отрисовка через API без самостоятельного редактора; NotaCode планирует Kroki как альтернативный движок (документация проекта)"),
    dict(id="K006", name="PlantText", dom="planttext.com", market="Весь мир (Индонезия, Боливия, Вьетнам в топ-странах)", ctype="Онлайн-редактор PlantUML",
         product="Онлайн-редактор PlantUML: классовые, последовательностные, деятельностные диаграммы", seg="Студенты, разработчики",
         hyp=0, prio="Средний", disc="ЛР4 табл. 3 (кандидат 6)", c=(5, 4, 4, 5), bc=False,
         home_note="В заголовке заявлены бесплатность и онлайн-доступ; редактор поверх PlantUML"),
    dict(id="K007", name="StarUML", dom="staruml.io", market="Весь мир", ctype="Программа для моделирования UML",
         product="Программа визуального моделирования UML", seg="Разработчики, архитекторы ПО",
         hyp=0, prio="Средний", disc="ЛР4 табл. 3 (кандидат 7); Вордстат «staruml» (16)", c=(4, 4, 3, 3), bc=False,
         home_note="Графический моделер UML; страница тарифов в HTML упомянута 2 раза, цены не получены"),
    dict(id="K008", name="Visual Paradigm", dom="visual-paradigm.com", market="Весь мир (Индия, Индонезия, Россия в топ-странах)", ctype="Платформа UML, BPMN, архитектуры",
         product="Универсальная платформа моделирования UML, BPMN, Enterprise Architecture с генеративным ИИ", seg="Аналитики, архитекторы ПО, студенты",
         hyp=0, prio="Высокий", disc="ЛР4 табл. 3 (кандидат 8); ЛР1 табл. 42, 44", c=(4, 4, 4, 3), bc=False,
         home_note="Широкий набор нотаций и ИИ; графический ввод, ценовой уровень выше NotaCode"),
    dict(id="K009", name="Sparx Systems (Enterprise Architect)", dom="sparxsystems.com", market="Весь мир", ctype="Корпоративная платформа моделирования",
         product="Enterprise Architect (UML, BPMN)", seg="Корпоративные архитекторы",
         hyp=0, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 9); ЛР1 табл. 44", c=(4, None, 3, None), bc=False,
         home_note="Главная страница вернула HTTP 403 автоматическому запросу; отнесение по ЛР1 (табл. 44)"),
    dict(id="K010", name="bpmn.io", dom="bpmn.io", market="Весь мир", ctype="Редактор BPMN, открытый код",
         product="Веб-инструменты для BPMN, DMN, CMMN и форм (встраиваемые)", seg="Разработчики, аналитики процессов",
         hyp=2, prio="Средний", disc="ЛР4 табл. 3 (кандидат 10); ЛР1 табл. 44 (частичный заменитель)", c=(3, 3, 2, 3), bc=False,
         home_note="Только BPMN-семейство; в NotaCode BPMN относится ко второй волне нотаций"),
    dict(id="K011", name="Camunda (Modeler)", dom="camunda.com", market="Весь мир", ctype="Платформа оркестрации процессов",
         product="Платформа агентной оркестрации; Camunda Modeler - отдельный редактор BPMN", seg="Корпоративные команды автоматизации",
         hyp=3, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 11, не прошёл как домен); ЛР1 табл. 44; Вордстат «camunda modeler» (17)", c=(2, 2, 2, 2), bc=False,
         home_note="Классифицируется Modeler, а не вся компания; главная страница описывает платформу оркестрации"),
    dict(id="K012", name="Storm (StormBPMN)", dom="stormbpmn.com", market="Россия и СНГ (Россия 62,99 %, Беларусь 2,49 %)", ctype="Платформа процессного управления",
         product="Платформа из семи модулей: редактор, реестр, архитектура, оргструктура, опросы, ИИ, симуляция", seg="Процессные аналитики, русскоязычный рынок",
         hyp=0, prio="Средний", disc="ЛР4 табл. 3 (кандидат 12); Similarweb Pro (Беларусь в топ-5 стран)", c=(3, 3, 2, 3), bc=True,
         home_note="Русскоязычная платформа; BPMN-редактор входит в состав платформы процессного управления"),
    dict(id="K013", name="draw.io (diagrams.net)", dom="app.diagrams.net", market="Весь мир (США, Индонезия, Индия, Китай, Россия)", ctype="Универсальный редактор диаграмм, открытый код",
         product="Бесплатный онлайн-редактор блок-схем, UML, ER и других диаграмм", seg="Студенты, разработчики, команды",
         hyp=2, prio="Высокий", disc="ЛР4 табл. 3 (кандидат 13); ЛР1 табл. 42 (главный по спросу заменитель); Вордстат «draw io» (1072)", c=(3, 4, 3, 3), bc=True,
         home_note="Универсальный графический редактор; бесплатный, открытый код, заявлено более 100 млн пользователей"),
    dict(id="K014", name="Lucidchart", dom="lucidchart.com", market="Весь мир (США, Мексика, Бразилия в топ-странах)", ctype="Универсальный редактор диаграмм (подписка)",
         product="Облачный редактор диаграмм с тарифами Free, Individual, Team, Enterprise", seg="Команды, бизнес-пользователи",
         hyp=2, prio="Средний", disc="ЛР4 табл. 3 (кандидат 14); ЛР1 табл. 42", c=(3, 3, 3, 3), bc=True,
         home_note="Автоматический запрос вернул HTTP 403; страницы lucid.co/lucidchart и тарифы просмотрены 01.10.2026 во встроенном браузере: диаграммы с ИИ, шаблоны (UML, BPMN, ERD), Free, Individual 9 USD, Team 10 USD, Enterprise"),
    dict(id="K015", name="Creately", dom="creately.com", market="Весь мир (США, Индия, Филиппины в топ-странах)", ctype="Универсальный редактор диаграмм",
         product="ИИ-платформа визуальной коммуникации: блок-схемы, оргструктуры, ментальные карты", seg="Команды, бизнес-пользователи",
         hyp=2, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 15); Capterra (ЛР2-3)", c=(3, 3, 3, 3), bc=False,
         home_note="Универсальный редактор; отзывы на Trustpilot низкие (1,9 из 5 при 58 отзывах)"),
    dict(id="K016", name="Miro", dom="miro.com", market="Весь мир (США, Россия, Германия в топ-странах)", ctype="Универсальная онлайн-доска",
         product="Платформа визуальной совместной работы (доски)", seg="Команды продуктов и дизайна",
         hyp=2, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 16); ЛР1 табл. 43 (вне границ рынка); Вордстат «miro» (1660)", c=(2, 2, 2, 2), bc=False,
         home_note="Доска для совместной работы; в продуктовые границы ЛР1 как самостоятельный рынок не входит"),
    dict(id="K017", name="Excalidraw", dom="excalidraw.com", market="Весь мир (Индия, США, Китай в топ-странах)", ctype="Доска со схемами, открытый код",
         product="Виртуальная доска для набросков диаграмм в рукописном стиле", seg="Разработчики, авторы схем",
         hyp=2, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 17)", c=(2, 3, 2, 2), bc=False,
         home_note="Наброски вместо нотационных диаграмм; репозиторий с 133 301 звездой"),
    dict(id="K018", name="dbdiagram.io", dom="dbdiagram.io", market="Весь мир (Индия, США, Индонезия в топ-странах)", ctype="Текстовый конструктор ERD",
         product="Схемы баз данных (ERD) из текстового описания на языке DBML", seg="Разработчики баз данных",
         hyp=0, prio="Средний", disc="ЛР4 табл. 3 (кандидат 18)", c=(3, 3, 2, 4), bc=False,
         home_note="Одна нотация (ERD) с вводом текстом; ERD входит в первую волну нотаций NotaCode"),
    dict(id="K019", name="DrawSQL", dom="drawsql.app", market="Весь мир (география в Similarweb недоступна)", ctype="Конструктор ERD",
         product="Интерактивная схема базы данных из SQL", seg="Разработчики баз данных, команды",
         hyp=0, prio="Низкий", disc="ЛР4 табл. 3 (кандидат 19)", c=(3, 3, 2, 3), bc=False,
         home_note="Одна нотация (ERD); данные по каналам и географии в Similarweb недоступны"),
    dict(id="K020", name="Eraser", dom="eraser.io", market="Весь мир", ctype="ИИ-генерация технических диаграмм",
         product="Создание технических диаграмм с помощью ИИ", seg="Инженерные команды, разработчики",
         hyp=1, prio="Высокий", disc="ЛР4 табл. 3 (кандидат 20); ЛР2-3 (тарифы, Product Hunt); Вордстат «eraser io» (2)", c=(4, 3, 3, 4), bc=True,
         home_note="ИИ-режим сопоставим с режимами ИИ-ассистента NotaCode; раздел обзора Similarweb данных не показал"),
    dict(id="K021", name="Whimsical", dom="whimsical.com", market="Весь мир", ctype="Универсальный редактор диаграмм и досок",
         product="Редактор диаграмм, схем интерфейсов и документов; тарифы Free, Pro, Business (страница тарифов, 01.10.2026)", seg="Команды продуктов",
         hyp=2, prio="Низкий", disc="ЛР2-3 (заменители; тарифы; Capterra)", c=(3, 3, 2, 3), bc=True,
         home_note="Главная страница и тарифы просмотрены 01.10.2026: диаграммы и схемы интерфейсов для команд продуктов, формальных нотаций UML и BPMN как набора нет; Similarweb не собирался; запрос «whimsical» в Вордстате - омоним"),
    dict(id="K022", name="Microsoft Visio", dom="microsoft.com/visio", market="Весь мир", ctype="Универсальный редактор (подписка)",
         product="Редактор диаграмм Microsoft Visio (Plan 1, Plan 2)", seg="Корпоративные аналитики",
         hyp=2, prio="Средний", disc="ЛР4 табл. 3 (кандидат 21); ЛР1 табл. 42, 44; Вордстат «visio» (1501)", c=(3, 3, 2, 2), bc=False,
         home_note="Домен-раздел без отдельного трафика (ЛР4); использованы тарифы ЛР1 и частота запроса «visio» (1501)"),
]

# Правила расчёта C5-C10 по собранным данным
MARKET = {"plantuml.com", "mermaid.js.org", "mermaidchart.com", "app.diagrams.net", "eraser.io", "excalidraw.com"}
IMPORT_PLAN = {"plantuml.com", "mermaid.js.org", "mermaidchart.com", "d2lang.com", "planttext.com", "app.diagrams.net", "bpmn.io", "camunda.com"}
AMBIG = {"kroki.io"}
PRICING_EXTRA = {"planttext.com": dict(free=True, entry=None, note="заголовок страницы: Free & Fast", src="https://www.planttext.com/"),
                 "dbdiagram.io": dict(free=True, entry=8, note="описание: free tool; платный тариф около 8 USD (ЛР2-3)", src="https://dbdiagram.io/pricing")}
C8_NONE = {"drawsql.app"}


def pricing(dom):
    p = dict(C.PRICING)
    p.update(PRICING_EXTRA)
    return p.get(dom)


def c5(dom):
    p = pricing(dom)
    if not p:
        return None
    if p["entry"] is None:
        return 4 if p.get("free") else None
    e = p["entry"]
    return 4 if e <= 6 else 3 if e <= 12 else 2 if e <= 30 else 1


def c6(dom):
    s = C.sw(dom)
    ws = C.ws_brand(dom)
    if dom in ("eraser.io", "drawsql.app", "whimsical.com"):
        return None
    pts = 1
    if s and s.get("organic_pct") is not None and s["organic_pct"] >= 40:
        pts += 1
    stars = sum(x[1] for x in C.gh_total_stars(dom))
    if stars >= 1000 or dom in MARKET:
        pts += 1
    if ws is not None and ws >= 10 and dom not in AMBIG:
        pts += 1
    if s and ((s.get("referral_pct") or 0) >= 10 or ((s.get("social_org_pct") or 0) + (s.get("social_paid_pct") or 0)) >= 5):
        pts += 1
    return min(5, pts)


def c7(dom):
    if dom == "stormbpmn.com":
        return 5
    ws = C.ws_brand(dom)
    s = C.sw(dom)
    top = (s or {}).get("top_countries_share") or ""
    if dom == "whimsical.com":
        return None
    if "RU " in top or "BY " in top:
        return 4
    if ws is not None and ws >= 100:
        return 4
    if ws is not None and ws >= 10 and dom not in AMBIG:
        return 3
    if ws is not None:
        return 2
    return None


def c8(dom):
    p = pricing(dom)
    if not p or dom in C8_NONE:
        return None
    if p.get("free") is True and p["entry"] is not None:
        return 5
    if p.get("free") is True:
        return 1
    if p.get("free") is False:
        return 3 if dom == "visual-paradigm.com" else 4
    return 4


def reviews_n(dom):
    r = C.REVIEWS.get(dom)
    return r["n"] if r else None


def c9(dom):
    a = C.age(dom)
    s = C.sw(dom)
    rv = reviews_n(dom)
    if a is None and rv is None and s is None:
        return None
    if dom == "microsoft.com/visio":
        return None
    pts = 1
    if a is not None:
        pts += (a >= 5) + (a >= 12)
    if rv is not None and rv >= 30:
        pts += 1
    stars = sum(x[1] for x in C.gh_total_stars(dom))
    visits = (s or {}).get("monthly_visits") or 0
    if visits >= 500000 or stars >= 10000:
        pts += 1
    if dom == "whimsical.com":
        return 2 if (rv or 0) >= 30 else None
    return min(5, pts)


def c10(dom):
    return 3 if dom in IMPORT_PLAN else None


def scores(co):
    dom = co["dom"]
    c1, c2, c3, c4 = co["c"]
    return [c1, c2, c3, c4, c5(dom), c6(dom), c7(dom), c8(dom), c9(dom), c10(dom)]


# --- Формулы шаблона листа 04
def weighted(sc):
    filled = [x for x in sc if x is not None]
    if not filled:
        return None
    return sum((x or 0) * w for x, w in zip(sc, WEIGHTS)) / sum(WEIGHTS)


def limiter(sc):
    n = sum(1 for x in sc if x is not None)
    if n < 6:
        return "Недостаточно данных"
    if (sc[0] or 0) < 3:
        return "Низкое совпадение задачи"
    if (sc[2] or 0) < 3:
        return "Низкая товарная заменяемость"
    return "Нет"


def calc_level(sc):
    n = weighted(sc)
    lim = limiter(sc)
    if n is None:
        return None
    if lim == "Недостаточно данных":
        return LEVELS[5]
    if (sc[0] or 0) < 3 or (sc[2] or 0) < 3:
        return LEVELS[2] if n >= 2.5 else LEVELS[3] if n >= 1.6 else LEVELS[4]
    return LEVELS[0] if n >= 4.2 else LEVELS[1] if n >= 3.4 else LEVELS[2] if n >= 2.5 else LEVELS[3] if n >= 1.6 else LEVELS[4]


def zone(sc):
    x = avg([sc[0], sc[2]])
    y = avg([sc[1], sc[6]])
    if x is None or y is None:
        return None, None, "" if False else None
    z = "Ядро прямой конкуренции" if x >= 4 and y >= 4 else "Близкая альтернатива" if x >= 3 and y >= 3 else \
        "Функциональный заменитель" if x >= 3 else "Аудиторное пересечение" if y >= 3 else "Периферия"
    return x, y, z


def avg(v):
    """AVERAGE Excel: пустые ячейки игнорируются; если нет чисел - ошибка (в листе IFERROR даёт пусто)."""
    w = [x for x in v if x is not None]
    return sum(w) / len(w) if w else None


# Экспертные корректировки: id -> (уровень, обоснование)
CORRECTIONS = {
    "K001": (LEVELS[0],
             "Расчётный балл 4,10 лишь на 0,10 ниже порога 4,20; по правилу методики (индекс 65-79 и постоянное присутствие в тех же запросах) допускается повышение до прямого. "
             "Подтверждения: (1) запрос «plantuml» - 200 запросов в месяц в Беларуси (Вордстат, 29.08-27.09.2026), максимум среди брендов текстовых DSL; (2) страница товара и описание совпадают с задачей NotaCode (title/description 30.09.2026); "
             "(3) ЛР1 табл. 44 относит PlantUML к прямым конкурентам; (4) плагины IDE: 3 712 111 установок VS Marketplace и 5 014 362 загрузки JetBrains (ЛР2-3)."),
}

STATUS_OK = "В работе"
STATUS_LOW = "Требует уточнения"


def confidence(co, sc):
    n = sum(1 for x in sc if x is not None)
    has_title = co["dom"] in C.TITLES and (C.TITLES[co["dom"]].get("title") or C.TITLES[co["dom"]].get("description"))
    if n >= 8 and has_title and C.sw(co["dom"]):
        return "средняя"
    if n >= 6 and (has_title or C.sw(co["dom"])):
        return "средняя" if has_title else "низкая"
    return "низкая"


def rationale(co, sc, calc, final):
    p = pricing(co["dom"])
    parts = [f"Уверенность: {confidence(co, sc)}."]
    s = C.sw(co["dom"])
    if s and s.get("monthly_visits"):
        parts.append(f"Similarweb Pro: {C.fmt_int(s['monthly_visits'])} визитов в месяц (июнь-август 2026).")
    ws = C.ws_brand(co["dom"])
    if ws is not None:
        parts.append(f"Вордстат, Беларусь: {ws} запр. в месяц.")
    if p and p.get("tiers"):
        parts.append("Тарифы: " + p["tiers"].split(";")[0] + ".")
    elif p and p.get("note"):
        parts.append("Цена: " + p["note"] + ".")
    parts.append(co["home_note"] + ".")
    return " ".join(parts)


def build():
    rows = []
    for co in COMPANIES:
        sc = scores(co)
        n = weighted(sc)
        lim = limiter(sc)
        lev = calc_level(sc)
        corr = CORRECTIONS.get(co["id"])
        final = corr[0] if corr else lev
        x, y, z = zone(sc)
        rows.append(dict(co=co, sc=sc, n=n, lim=lim, calc=lev, corr=corr, final=final, x=x, y=y, zone=z,
                         conf=confidence(co, sc), nfilled=sum(1 for v in sc if v is not None)))
    return rows


# --- Доказательства
def evidence(rows):
    ev = []
    for r in rows:
        co = r["co"]
        dom = co["dom"]
        cid = co["id"]
        t = C.TITLES.get(dom) or C.TITLES.get("www.drawio.com" if dom == "app.diagrams.net" else dom)
        url = C.URL_HOME.get(dom, "https://" + dom)
        if t and (t.get("title") or t.get("description")):
            fact = f"title: «{t.get('title')}»" + (f"; description: «{t.get('description')}»" if t.get("description") else "; description отсутствует")
            ev.append([cid, "Главная страница (title, description)", url, fact, "Цифровой товар", 4, DATE, co["home_note"], 4, C.F_TITLE, "метаданные главной страницы, curl 30.09.2026"])
        if dom == "app.diagrams.net":
            t2 = C.TITLES["www.drawio.com"]
            ev.append([cid, "Главная страница drawio.com (title, description)", "https://www.drawio.com/",
                       f"title: «{t2['title']}»; description: «{t2['description']}»", "Потребительская задача", 4, DATE,
                       "Заявлены бесплатность, открытый код, более 100 млн пользователей и хранение данных у пользователя", 4, C.F_TITLE, "метаданные главной страницы, curl 30.09.2026"])
        s = C.sw(dom)
        if s and s.get("monthly_visits"):
            ev.append([cid, "Similarweb Pro, Website performance", "https://pro.similarweb.com/",
                       f"{C.fmt_int(s['monthly_visits'])} визитов в месяц; уникальных {C.fmt_int(s['unique_monthly'])}; длительность {s['duration']}; {C.fmt_num(s['pages_visit'])} стр. за визит; отказы {C.fmt_num(s['bounce_pct'])} %; окно июнь-август 2026, весь мир",
                       "Доверие и зрелость", 3, DATE, "Масштаб видимости (оценочная модель, не измерение)", 3, C.F_SW, "пробный доступ Similarweb Pro, снимок 30.09.2026"])
            if s.get("direct_pct") is not None:
                ps = s.get("paid_search_pct")
                ev.append([cid, "Similarweb Pro, Marketing channels", "https://pro.similarweb.com/",
                           f"Прямой {C.fmt_num(s['direct_pct'])} %; органический поиск {C.fmt_num(s['organic_pct'])} %; платный поиск {('нет данных' if ps is None else C.fmt_num(ps) + ' %')}; реферальный {C.fmt_num(s['referral_pct'])} %; соцсети (орг.) {C.fmt_num(s['social_org_pct'] or 0)} %",
                           "Каналы продаж", 3, DATE, "Структура привлечения; сравнивается с каналами NotaCode (поиск, сообщества, каталоги расширений)", 3, C.F_SW, "Similarweb Pro, 30.09.2026"])
            if s.get("top_countries_share") and s["top_countries_share"] not in ("нет данных (мало)",):
                ev.append([cid, "Similarweb Pro, Geography", "https://pro.similarweb.com/",
                           f"Топ-5 стран: {s['top_countries_share']}", "География и язык", 3, DATE,
                           "Пересечение с рынком РБ и РФ/СНГ оценивается по наличию RU и BY среди стран", 3, C.F_SW, "Similarweb Pro, 30.09.2026; доля Беларуси недоступна (пробный доступ)"])
        ws = C.ws_brand(dom)
        if ws is not None:
            k = C.WS_KEY[dom]
            src = C.F_WS if k[1] == "wordstat" else "ЛР1 (Вордстат, 30 дней на 29.09.2026)"
            note = "омоним, спрос на сервис не выделяется" if dom == "whimsical.com" else "возможна омонимия" if dom in C.AMBIG_WS else ""
            ev.append([cid, "Яндекс Вордстат, Беларусь", "https://wordstat.yandex.ru/", f"Запрос «{k[0]}»: {ws} запросов в месяц (регион Беларусь, все устройства)" + (f"; {note}" if note else ""),
                       "География и язык", 3, DATE, "Спрос в РБ по бренду как признак пересечения по каналу выбора", 4, src, "Вордстат, 30.09.2026"])
        p = pricing(dom)
        if p:
            txt = p.get("tiers") or p.get("note")
            ev.append([cid, "Тарифы и цена", p["src"] if str(p["src"]).startswith("http") else C.URL_HOME.get(dom, p["src"]), txt,
                       "Цена и тарифы", 5, DATE, "Ценовая логика сопоставляется с Free и Pro 40 USD в год (4 USD в месяц) у NotaCode", 4,
                       "ЛР1 табл. 42; ЛР2-3 табл. 70", "значения считаны с официальных страниц 30.09.2026 (ЛР1, ЛР2-3)"])
        rv = C.REVIEWS.get(dom)
        if rv:
            ev.append([cid, "Отзывы и рейтинги (каталоги)", "https://www.g2.com/ ; https://www.capterra.com/ ; https://www.trustpilot.com/review/" + dom.split("/")[0],
                       rv["txt"], "Доверие и зрелость", 3, DATE, "Независимые отзывы; тональность может быть смещена", 3, "rev05.csv; trustpilot_reviews_2026-09-30.json; marketplaces.csv", "значения считаны 30.09.2026"])
        gh = C.gh_total_stars(dom)
        if gh:
            txt = "; ".join(f"{g[0]}: {C.fmt_int(g[1])} звёзд, {C.fmt_int(g[2])} форков, лицензия {g[3]}, последнее обновление {g[4][:10]}" for g in gh)
            ev.append([cid, "GitHub (репозиторий)", "https://github.com/" + gh[0][0], txt, "Доверие и зрелость", 3, DATE,
                       "Активность сообщества и открытость кода", 5, C.F_GH, "GitHub REST API, 30.09.2026"])
        a = C.age(dom)
        if a is not None and dom != "whimsical.com":
            ev.append([cid, "Регистрационные данные домена (RDAP)", "https://rdap.org/domain/" + dom, f"Возраст домена или репозитория около {C.fmt_num(a, 1)} лет (верхняя оценка возраста бренда)",
                       "Доверие и зрелость", 2, DATE, "Историю продукта подтверждает косвенно", 4, C.F_AGE, "RDAP, 30.09.2026"])
        fl = C.FLAGS.get(dom) or (C.FLAGS.get("www.drawio.com") if dom == "app.diagrams.net" else None)
        if fl and fl.get("http") == "200" and "pricing" in fl:
            ev.append([cid, "Признаки на главной странице (HTML)", url,
                       f"Совпадения шаблонов в HTML: вход - {fl['login']}, тарифы - {fl['pricing']}, интеграции - {fl['integrations']}, вакансии - {fl['careers']}, магазин приложений - {fl['appstore']}, GitHub - {fl['github']}",
                       "Функциональность", 2, DATE, "Косвенный признак (автоматический подсчёт, не просмотр страницы человеком)", 3, C.F_FLAGS, "curl главной страницы, 30.09.2026"])
        elif fl and fl.get("http") != "200":
            ev.append([cid, "Доступность главной страницы", url, f"Автоматический запрос вернул HTTP {fl['http']}; содержимое не получено", "Доверие и зрелость", 1, DATE,
                       "Описание продукта с сайта не использовано; нужен ручной просмотр", 2, C.F_FLAGS, "🔲 ДОСНЯТЬ: ручной просмотр страницы и скриншот"])
        if dom in IMPORT_PLAN:
            ev.append([cid, "Совместимость форматов NotaCode", "docs/business/01-project-concept.md, разделы 2 и 5",
                       "В документации проекта предусмотрены экспорт и импорт форматов PlantUML, Mermaid, D2, BPMN XML, draw.io", "Замена и переключение", 2, DATE,
                       "Переключение с формата этого инструмента на NotaCode возможно при реализации импорта (план)", 3, "NotaCode/docs/business/01-project-concept.md", "импорт - не в MVP"])
    return ev


C.AMBIG_WS = {"kroki.io", "whimsical.com", "mermaid.js.org"}

if __name__ == "__main__":
    rows = build()
    for r in rows:
        co = r["co"]
        sc = ["-" if v is None else v for v in r["sc"]]
        print(f"{co['id']} {co['name'][:22]:22} {sc} N={r['n']:.2f} lim={r['lim'][:12]:12} calc={r['calc'][:20]:20} fin={r['final'][:20]:20} zone={r['zone']} conf={r['conf']} nf={r['nfilled']}")
    ev = evidence(rows)
    print(len(ev))
