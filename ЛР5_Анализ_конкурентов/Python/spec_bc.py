# -*- coding: utf-8 -*-
"""Спецификации заполнения книг части B (цифровой товар: Левитт, Кано) и части C (бизнес-модель).

Источники: главные страницы, тарифы, документация и разделы 8 конкурентов (просмотр 01.10.2026: автоматическое извлечение текста и
чтение во встроенном браузере), ЛР1-ЛР4 (Similarweb Pro, GitHub, отзывы). Оценки по шкалам - экспертные, правила в журналах книг."""
import json
import os

import lr5_common as C
import lr5_part_a as A
from lr5_spec import Spec

WHO = "К. А. Хаджинова"
VIEW = "2026-10-01"
DOMS = ["plantuml.com", "mermaid.js.org", "mermaidchart.com", "stormbpmn.com", "app.diagrams.net", "lucidchart.com", "eraser.io", "whimsical.com"]
CO = {c["dom"]: c for c in A.COMPANIES}
FINAL = {r["co"]["dom"]: r["final"] for r in A.build()}
IDS = {d: "C%02d" % (i + 1) for i, d in enumerate(DOMS)}
BY = {v: k for k, v in IDS.items()}
HOME = C.URL_HOME
SAAS = {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io", "whimsical.com"}
L1, L2, L3, L4, L5 = ("1. Базовая выгода", "2. Родовой товар", "3. Ожидаемый товар", "4. Расширенный товар", "5. Потенциальный товар")

PG = json.load(open(os.path.join(C.LAB5, "Материалы_собранные", "sajty_konkurentov_stranicy_2026-10-01.json"), encoding="utf-8"))["data"]
BROWSER = {  # страницы, прочитанные во встроенном браузере (автоматический запрос: 403 или пустой ответ)
    "lucidchart.com": [("https://lucid.co/lucidchart", "Главная: «Diagramming powered by intelligence»; ИИ, шаблоны, интеграции", "Главная", 5),
                       ("https://lucid.app/pricing/lucidchart", "Тарифы: Free 0 USD, Individual 9 USD, Team 10 USD, Enterprise по запросу", "Тарифы", 5)],
    "mermaidchart.com": [("https://mermaid.ai/pricing/", "Тарифы: Basic Free, Plus 10 USD, Premium 20 USD, Enterprise по запросу", "Тарифы", 5)],
}
TXT = {
    "plantuml.com": "«Open-source tool that uses simple textual descriptions to draw beautiful UML diagrams»",
    "mermaid.js.org": "«Create diagrams and visualizations using text and code»",
    "mermaidchart.com": "«Create diagrams, flowcharts, and documentation with Mermaid»; «You already think in systems»",
    "stormbpmn.com": "«Соберите все процессы компании»; «Одна платформа - девять модулей процессного управления»",
    "app.diagrams.net": "«Security-first diagramming for teams»; «Free, open source diagramming application with 100M+ users»",
    "lucidchart.com": "«Diagramming powered by intelligence»: диаграммы с ИИ, данными и автоматизацией",
    "eraser.io": "«AI for diagrams that matter»; «Create technical diagrams using AI»",
    "whimsical.com": "«The whiteboard for product builders»: диаграммы, схемы интерфейсов, документы",
}


def ptype(url):
    u = url.lower()
    if "pricing" in u or "plans" in u:
        return "Тарифы"
    if "security" in u:
        return "Безопасность"
    if "template" in u:
        return "Шаблоны"
    if "blog" in u or "changelog" in u:
        return "Блог и обновления"
    if "integr" in u or "ecosystem" in u:
        return "Интеграции"
    if "/ai" in u or "diagramgpt" in u:
        return "ИИ-функции"
    if any(x in u for x in ("syntax", "diagram", "guide", "faq", "running", "download", "intro", "getting-started", "docs")):
        return "Документация"
    return "Главная"


def pages_of(dom):
    """[(url, тип, краткий вывод, достоверность)]"""
    out = []
    for r in PG.get(dom, []):
        if r["status"] == 200 and r.get("text_len", 0) > 800:
            t = (r.get("title") or "").replace("&amp;", "&").strip()
            kw = [k for k in ("free", "pricing", "ai", "collab", "integr", "api", "export", "templates", "security", "uml", "bpmn", "erd") if r["kw"].get(k)]
            sm = ("Заголовок: " + t[:70] if t else "Заголовок отсутствует") + ". Признаки в тексте: " + (", ".join(kw[:6]) or "не найдены")
            out.append((r["final"], ptype(r["final"]), sm, 4))
    for u, sm, t, q in BROWSER.get(dom, []):
        out.append((u, t, sm, q))
    return out


def conf(url, q):
    return 5 if (q == 5 or "pricing" in url) else q


# --------------------------------------------------------------------------- признаки (29)
# ключ, название, задача, уровень Левитта, категория Кано, влияние 1-5, элемент бизнес-модели, домены, доказательство
F = [
    ("text_dsl", "Описание диаграммы текстом (DSL)", "Быстро создавать и версионировать диаграммы как код", L2, "Обязательное", 5, "цифровой товар",
     {"plantuml.com", "mermaid.js.org", "mermaidchart.com", "eraser.io", "lucidchart.com"}, "Главные страницы PlantUML, Mermaid, Mermaid Chart; «Diagram-as-code» в тарифе Free Eraser; «Diagram as code» на lucid.co/lucidchart"),
    ("free", "Бесплатный доступ или Free-тариф", "Начать работу без оплаты", L3, "Обязательное", 5, "потоки доходов",
     set(DOMS), "Открытый код или тариф Free на страницах 8 из 8 конкурентов"),
    ("paid", "Платная подписка по тарифным уровням", "Получить расширенные возможности за оплату", L3, "Линейное", 4, "потоки доходов",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io", "whimsical.com"}, "Страницы тарифов Mermaid Chart, Storm, Lucidchart, Eraser, Whimsical"),
    ("pricing_page", "Открытая страница тарифов", "Понять цену и состав тарифа до регистрации", L3, "Обязательное", 5, "потоки доходов",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io", "whimsical.com"}, "Страницы тарифов (01.10.2026)"),
    ("enterprise", "Корпоративный тариф (Enterprise или on-prem)", "Подключить организацию целиком", L4, "Безразличное", 2, "потоки доходов",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io"}, "Enterprise по запросу на страницах тарифов; Storm: on-prem от 990 тыс. руб. в год"),
    ("annual", "Скидка или цена при годовой оплате", "Снизить стоимость при долгом использовании", L3, "Линейное", 3, "потоки доходов",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io"}, "Цены «billed annually» (Mermaid Chart, Lucidchart, Eraser), скидка 20 % (Storm)"),
    ("trial", "Пробный период платного тарифа", "Проверить платные функции до оплаты", L3, "Безразличное", 2, "потоки доходов",
     {"lucidchart.com"}, "FAQ Lucidchart: пробный период 7 дней"),
    ("guests", "Бесплатные гости или зрители", "Показать диаграмму без оплаты за каждого читателя", L4, "Привлекательное", 3, "отношения с клиентами",
     {"mermaidchart.com", "stormbpmn.com", "eraser.io", "whimsical.com"}, "Unlimited viewer seats (Mermaid Chart Premium); 100 гостей на участника (Storm); unlimited guests (Eraser, Whimsical)"),
    ("ai", "ИИ-генерация или ИИ-помощник", "Ускорить создание диаграммы по описанию", L4, "Привлекательное", 4, "цифровой товар",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io", "whimsical.com"}, "ИИ-кредиты (Mermaid Chart); ИИ-ассистент (Storm); Lucid AI; Eraser AI; ИИ в Whimsical"),
    ("integr", "Интеграции с другими сервисами", "Встроить инструмент в рабочие процессы", L3, "Линейное", 4, "ключевые партнеры",
     set(DOMS), "Разделы и упоминания интеграций на страницах 8 из 8 конкурентов"),
    ("api", "API или платформа разработчика", "Автоматизировать генерацию диаграмм", L4, "Привлекательное", 3, "цифровой товар",
     {"mermaid.js.org", "mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io"}, "API Mermaid; пункт API в меню Mermaid Chart; API в Enterprise Storm; Developer platform Lucidchart; API calls Eraser"),
    ("open", "Открытый код и сообщество", "Доверять инструменту и расширять его", L4, "Привлекательное", 4, "ключевые ресурсы",
     {"plantuml.com", "mermaid.js.org", "app.diagrams.net"}, "GitHub API, 30.09.2026; лицензия Apache 2.0 у draw.io"),
    ("reviews", "Независимые отзывы и оценки", "Оценить качество до выбора", L4, "Линейное", 3, "отношения с клиентами",
     {"plantuml.com", "mermaid.js.org", "mermaidchart.com", "app.diagrams.net", "lucidchart.com", "eraser.io", "whimsical.com"}, "G2, Capterra, Trustpilot, каталоги расширений (ЛР2-3, ЛР4)"),
    ("customer_stats", "Данные о числе пользователей или клиентов на сайте", "Оценить масштаб и надёжность продукта", L4, "Линейное", 3, "отношения с клиентами",
     {"mermaidchart.com", "stormbpmn.com", "app.diagrams.net", "lucidchart.com"}, "5M человек и 200k компаний (Mermaid Chart); более 1 000 клиентов (Storm); 100M+ пользователей (draw.io); 99 % Fortune 500 (Lucidchart)"),
    ("security_page", "Раздел или упоминание о безопасности и приватности", "Понять, где хранятся данные", L4, "Линейное", 3, "ценностное предложение",
     {"mermaidchart.com", "stormbpmn.com", "app.diagrams.net", "lucidchart.com", "eraser.io", "whimsical.com"}, "Страница Security (Whimsical); раздел безопасности (Lucidchart, Eraser); privacy-first (draw.io)"),
    ("sso", "Единый вход SSO или SAML", "Подключить корпоративную учётную запись", L4, "Безразличное", 2, "потоки доходов",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io", "whimsical.com"}, "SSO или SAML в старших тарифах"),
    ("login", "Вход и личный кабинет", "Сохранять диаграммы и настройки", L3, "Обязательное", 3, "каналы",
     {"mermaidchart.com", "stormbpmn.com", "app.diagrams.net", "eraser.io", "lucidchart.com"}, "Ссылки на вход на главных страницах"),
    ("templates", "Шаблоны диаграмм", "Начать работу с готового образца", L3, "Линейное", 4, "цифровой товар",
     {"lucidchart.com", "eraser.io", "whimsical.com"}, "100 шаблонов в Free и более 1 000 в платных тарифах (Lucidchart); раздел шаблонов Eraser и Whimsical"),
    ("collab", "Совместная работа в реальном времени", "Редактировать диаграмму командой", L3, "Линейное", 4, "цифровой товар",
     {"mermaidchart.com", "stormbpmn.com", "app.diagrams.net", "lucidchart.com", "eraser.io", "whimsical.com"}, "Real-time collaboration (draw.io, Lucidchart, Whimsical); совместное редактирование в браузере (Storm); Co-editing (Mermaid Chart)"),
    ("export", "Экспорт диаграмм (PNG, SVG, PDF и др.)", "Вставить диаграмму в документ или презентацию", L3, "Обязательное", 5, "цифровой товар",
     set(DOMS), "Экспорт упомянут на страницах 8 из 8 конкурентов (PNG, SVG, PDF, DOCX у Storm, Visio у Lucidchart)"),
    ("version_history", "История версий", "Вернуться к предыдущей версии", L4, "Линейное", 3, "цифровой товар",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io", "whimsical.com"}, "7 и 90 дней (Eraser, Whimsical); Revision history (Lucidchart Team); версионирование (меню Storm)"),
    ("docs", "Документация и руководства", "Научиться пользоваться без обращения в поддержку", L3, "Обязательное", 4, "отношения с клиентами",
     {"plantuml.com", "mermaid.js.org", "mermaidchart.com", "app.diagrams.net", "eraser.io", "lucidchart.com"}, "PlantUML Language Reference Guide; Mermaid User Guide; docs.mermaidchart.com; docs.eraser.io; Learning center Lucidchart"),
    ("uml", "Диаграммы UML", "Строить диаграммы классов, последовательностей и др.", L3, "Обязательное", 5, "цифровой товар",
     {"plantuml.com", "mermaid.js.org", "app.diagrams.net", "lucidchart.com"}, "Страницы class-diagram (PlantUML, Mermaid); UML в описании draw.io; UML-шаблоны Lucidchart"),
    ("bpmn", "Диаграммы BPMN", "Моделировать бизнес-процессы", L4, "Линейное", 4, "цифровой товар",
     {"stormbpmn.com", "lucidchart.com", "eraser.io"}, "Редактор BPMN 2.0 (Storm); BPMN-шаблон (Lucidchart); упоминание BPMN на сайте Eraser"),
    ("erd", "Диаграммы ERD", "Описывать структуру базы данных", L4, "Линейное", 4, "цифровой товар",
     {"plantuml.com", "mermaid.js.org", "mermaidchart.com", "app.diagrams.net", "lucidchart.com", "eraser.io"}, "Страницы entityRelationshipDiagram (Mermaid), ie-diagram (PlantUML); ER в описании draw.io; ERD markup (Lucidchart)"),
    ("onprem", "Развёртывание на своём сервере", "Хранить данные внутри организации", L4, "Привлекательное", 3, "структура затрат",
     {"plantuml.com", "mermaid.js.org", "stormbpmn.com", "eraser.io"}, "Страницы running и download (PlantUML); библиотека Mermaid; on-prem (Storm); Flexible deployments (Eraser Enterprise)"),
    ("desktop", "Настольное приложение", "Работать без браузера", L4, "Безразличное", 2, "цифровой товар",
     {"plantuml.com", "app.diagrams.net", "whimsical.com"}, "Загрузка PlantUML; drawio-desktop (GitHub); Desktop app в таблице тарифов Whimsical"),
    ("ru_lang", "Русскоязычный интерфейс и тарифы в рублях", "Работать на русском языке и платить в рублях", L4, "Привлекательное", 4, "целевые сегменты",
     {"stormbpmn.com"}, "Сайт и тарифы Storm на русском языке, цены в рублях"),
    ("progress", "Признаки развития (ИИ-помощник, MCP, новые функции)", "Видеть, что продукт развивается", L5, "Привлекательное", 3, "масштабирование",
     {"mermaidchart.com", "stormbpmn.com", "lucidchart.com", "eraser.io"}, "MCP-интеграция (Storm); метки NEW: Lucid AI, Developer platform (Lucidchart); ИИ-кредиты (Mermaid Chart); AI-first (Eraser)"),
]
FEATS = {f[0]: f for f in F}
KEYS = [f[0] for f in F]
PRICE_KEYS = {"free", "paid", "pricing_page", "enterprise", "annual", "trial", "guests", "sso"}
STRONG = {"free", "paid", "pricing_page", "enterprise", "annual", "trial", "guests", "ai", "sso", "collab", "export", "version_history", "templates", "api",
          "uml", "bpmn", "erd", "text_dsl", "docs"}

DET = {
    ("free", "stormbpmn.com"): "Тариф «Персональный» бесплатно: до 50 моделей, ИИ-помощник безлимитно, делиться процессами 5 раз",
    ("free", "eraser.io"): "Free 0 USD за участника: 3 файла, 3 ИИ-диаграммы, 7 дней истории, diagram-as-code",
    ("free", "whimsical.com"): "Free 0 USD: 50 объектов доски и 50 блоков документа в месяц, водяной знак при экспорте",
    ("free", "lucidchart.com"): "Free 0 USD: 3 редактируемых документа, 75 фигур на документ, 100 шаблонов",
    ("free", "mermaidchart.com"): "Basic Free: до 6 диаграмм, 15 ИИ-кредитов",
    ("free", "app.diagrams.net"): "Бесплатное приложение с открытым кодом (Apache 2.0): «No enterprise tier for SSO»",
    ("free", "plantuml.com"): "Открытый код; раздел лицензирования на странице загрузки",
    ("free", "mermaid.js.org"): "Открытый код (MIT); платные планы вынесены в Mermaid Chart",
    ("paid", "mermaidchart.com"): "Plus 10 USD, Premium 20 USD за пользователя в месяц при оплате за год",
    ("paid", "stormbpmn.com"): "Команда 1 200 руб. (1 500 руб. помесячно), Бизнес 4 720 руб. (5 900 руб.) за пользователя в месяц",
    ("paid", "lucidchart.com"): "Individual 9 USD, Team 10 USD за пользователя в месяц при оплате за год",
    ("paid", "eraser.io"): "Starter 15 USD (20 USD помесячно), Business 45 USD (60 USD) за участника в месяц",
    ("paid", "whimsical.com"): "Pro 10 USD, Business 20 USD за редактора в месяц",
    ("enterprise", "stormbpmn.com"): "Enterprise на сервере заказчика от 990 тыс. руб. в год: on-prem, SSO, API, аудит",
    ("annual", "stormbpmn.com"): "Скидка 20 % при годовой оплате; для юридических лиц 1 800 руб. и 5 900 руб.",
    ("annual", "eraser.io"): "Starter 15 USD при годовой оплате против 20 USD помесячно",
    ("trial", "lucidchart.com"): "Пробный период 7 дней со всеми платными функциями, карта нужна при регистрации",
    ("ai", "mermaidchart.com"): "ИИ-кредиты: 15 (Basic), 300 (Plus), 2 000 в год (Premium)",
    ("ai", "stormbpmn.com"): "ИИ-ассистент во всех облачных тарифах, включая бесплатный",
    ("ai", "eraser.io"): "ИИ-диаграммы: 3 (Free), 40 (Starter), 250 (Business), без лимита (Enterprise)",
    ("version_history", "eraser.io"): "7 дней (Free), 90 дней (Starter), без ограничений (Business)",
    ("version_history", "whimsical.com"): "7 дней (Free), 90 дней (Pro), без ограничений (Business)",
    ("sso", "whimsical.com"): "SAML SSO и SCIM в тарифе Business",
    ("sso", "eraser.io"): "SAML SSO в тарифе Business",
    ("sso", "lucidchart.com"): "SAML authentication в тарифе Enterprise",
    ("sso", "mermaidchart.com"): "Строка SSO в таблице сравнения (Enterprise)",
    ("templates", "lucidchart.com"): "100 шаблонов в Free; более 1 000 премиум-шаблонов в платных тарифах",
    ("guests", "eraser.io"): "Unlimited guests на всех тарифах",
    ("guests", "whimsical.com"): "Viewers и Guests: Unlimited на всех тарифах",
    ("guests", "mermaidchart.com"): "Unlimited free viewer seats в Premium",
    ("guests", "stormbpmn.com"): "100 бесплатных гостей на участника в тарифе «Команда»",
    ("customer_stats", "mermaidchart.com"): "«trusted by over 5M people and over 200k companies»",
    ("customer_stats", "stormbpmn.com"): "«Нам доверяют больше 1 000 клиентов»",
    ("customer_stats", "app.diagrams.net"): "«100M+ users»",
    ("customer_stats", "lucidchart.com"): "«trusted partner of 99% of the Fortune 500»",
    ("ru_lang", "stormbpmn.com"): "Тарифы в рублях; Россия 62,99 % трафика (Similarweb Pro)",
}


def n(key):
    return len(FEATS[key][7])


def det(key, dom):
    return DET.get((key, dom)) or ("Признак найден на просмотренных страницах: " + FEATS[key][1].lower())


def feat_url(key, dom):
    if key in PRICE_KEYS or (key in ("version_history", "ai") and dom in ("eraser.io", "whimsical.com")):
        for u, t, sm, q in pages_of(dom):
            if t == "Тарифы":
                return u
    return HOME[dom]


def money(dom):
    p = C.PRICING.get(dom) or {}
    return p.get("tiers") or p.get("note")


TIERS = {d: money(d) for d in DOMS}
TIERS["stormbpmn.com"] = ("Персональный 0 руб. (до 50 моделей); Команда 1 200 руб. (1 500 руб. помесячно) за пользователя в месяц; Бизнес 4 720 руб. (5 900 руб.); "
                          "Enterprise на сервере заказчика от 990 тыс. руб. в год (страница тарифов, 01.10.2026)")
TIERS["mermaidchart.com"] = "Basic Free (до 6 диаграмм, 15 ИИ-кредитов); Plus 10 USD (300 кредитов); Premium 20 USD (2 000 кредитов, зрители без оплаты) за пользователя в месяц при оплате за год; Enterprise по запросу"
TIERS["lucidchart.com"] = "Free (3 документа, 75 фигур, 100 шаблонов); Individual 9 USD; Team 10 USD за пользователя в месяц при оплате за год; Enterprise по запросу; пробный период 7 дней"


def sw_channels(dom):
    s = C.sw(dom)
    if not s or s.get("direct_pct") is None:
        return None
    parts = [("прямые заходы", s.get("direct_pct")), ("органический поиск", s.get("organic_pct")), ("рефералы", s.get("referral_pct")),
             ("соцсети органика", s.get("social_org_pct")), ("ИИ-ассистенты", s.get("genai_pct")), ("e-mail", s.get("email_pct")),
             ("платный поиск", s.get("paid_search_pct"))]
    t = "; ".join("%s %s %%" % (nm, C.fmt_num(v, 2)) for nm, v in parts if v is not None)
    return t + " (Similarweb Pro, " + str(s.get("period")) + ", весь мир, снимок 30.09.2026)"


def levitt_rows():
    rows = []
    for d in DOMS:
        co, cid, url = CO[d], IDS[d], HOME[d]
        nm = co["name"]
        rows.append((cid, nm, url, L1, "Основное обещание главной страницы", TXT[d], "Главная страница, просмотр 01.10.2026", "L1"))
        rows.append((cid, nm, url, L2, "Форма поставки товара", co["ctype"] + ": " + co["product"], "Страницы сайта, ЛР1 табл. 42, ЛР4", "L2"))
        for k in KEYS:
            f = FEATS[k]
            if d in f[7]:
                rows.append((cid, nm, feat_url(k, d), f[3], f[1], det(k, d), "Страницы сайта, просмотр 01.10.2026", k))
    return rows


def lscore(key, dom):
    if key == "L1":
        return 3, 3, 5
    if key == "L2":
        return 3, 3, 4
    f = FEATS[key]
    return (3 if key in STRONG else 2), (3 if dom in SAAS else 2), f[5]


SC = {  # оценки 0-5 по критериям P01-P25; None - не подтверждено просмотренными страницами
    "plantuml.com": [5, 4, 4, 4, 4, 5, 2, 3, 2, 1, 2, 2, 4, 3, 3, 4, 2, 2, 5, 4, 3, 3, 2, 4, 4],
    "mermaid.js.org": [5, 4, 4, 4, 4, 5, 2, 3, 1, 2, 2, 3, 5, 3, 4, 3, 1, 2, 5, 5, 3, 3, 2, 4, 4],
    "mermaidchart.com": [5, 5, 4, 5, 4, 5, 4, 4, 5, 4, 4, 3, 5, 5, 4, 5, 4, 4, 5, 5, 4, 4, 4, 5, 5],
    "stormbpmn.com": [5, 4, 4, 5, None, 5, 3, 4, 5, 4, 4, None, 5, 5, 4, 5, 4, 3, None, 5, 3, 4, 4, 4, 4],
    "app.diagrams.net": [5, 4, 4, 4, 4, 5, 3, 4, 2, 3, 5, 3, 5, 4, 4, 4, 2, 3, 4, 5, None, 4, 4, 5, 5],
    "lucidchart.com": [5, 4, 4, 5, 5, 5, 4, 5, 5, 5, 5, None, 5, 5, 4, 5, 5, 4, 4, 5, 4, 4, 4, 5, 5],
    "eraser.io": [5, 5, 4, 5, 4, 5, 4, 5, 5, 4, 4, None, 5, 5, 4, 5, 4, 3, 4, 5, 4, 5, 4, 4, 4],
    "whimsical.com": [5, 4, 3, 4, 4, 5, 3, 4, 5, 4, 5, None, 5, 4, 4, 5, 4, 4, None, 4, 3, 3, 4, 3, 4],
}
WEIGHTS = [5, 5, 4, 5, 4, 4, 5, 5, 4, 4, 4, 3, 5, 4, 4, 5, 4, 3, 3, 4, 3, 5, 5, 5, 5]


def total(dom):
    sc = SC[dom]
    num = sum(w * v for w, v in zip(WEIGHTS, sc) if v is not None)
    den = sum(w for w, v in zip(WEIGHTS, sc) if v is not None)
    return round(num / den, 2)


# --------------------------------------------------------------------------- ЧАСТЬ B
def build_b():
    s = Spec("Шаблон_анализа_конкурентов_Левитт_Кано.xlsx", "analiz_konkurentov_Levitt_Kano_NotaCode.xlsx")
    s.extra["author"] = WHO
    s.extra["reparse_xlookup"] = True
    s.extra["title"] = "Анализ цифрового товара конкурентов (Левитт, Кано): NotaCode"
    S1, S2, S3, S4, S5, S6, S7, S8, S9 = ("01_Конкуренты", "02_Карта_сайтов", "03_Левитт", "04_Кано", "05_Матрица_товара", "06_Сравнение",
                                          "07_Стандарт_рынка", "08_Преимущества", "09_Дашборд")
    monet = {
        "plantuml.com": "Бесплатно, открытый код", "mermaid.js.org": "Бесплатно, открытый код (MIT); платные планы у Mermaid Chart",
        "mermaidchart.com": "Условно-бесплатная: Free, Plus 10 USD, Premium 20 USD, Enterprise", "stormbpmn.com": "Условно-бесплатная: Персональный бесплатно, Команда, Бизнес, Enterprise on-prem (руб.)",
        "app.diagrams.net": "Бесплатно, открытый код (Apache 2.0)", "lucidchart.com": "Условно-бесплатная: Free, Individual 9 USD, Team 10 USD, Enterprise",
        "eraser.io": "Условно-бесплатная: Free, Starter 15 USD, Business 45 USD, Enterprise", "whimsical.com": "Условно-бесплатная: Free, Pro 10 USD, Business 20 USD",
    }
    for i, d in enumerate(DOMS):
        co, rw = CO[d], 7 + i
        s.row(S1, rw, "B", [co["name"], d, co["market"], FINAL[d], co["seg"], monet[d], co["product"] + ". Главная страница: " + TXT[d], co["prio"], "Завершён"])
        s.w(S1, f"K{rw}", "Выборка из части A (поле «Переходит в части B и C»); страницы просмотрены 01.10.2026")
    s.fit(S1, "A7:K14")
    rw = 7
    pages = 0
    goals = {"Главная": "Определить обещание и состав товара", "Тарифы": "Состав тарифов и условия оплаты", "Документация": "Глубина документации, поддержка нотаций",
             "Интеграции": "Интеграции и экосистема", "ИИ-функции": "ИИ-функции товара", "Шаблоны": "Шаблоны и готовые образцы", "Безопасность": "Безопасность и приватность",
             "Блог и обновления": "Развитие продукта и контент"}
    for d in DOMS:
        cid = IDS[d]
        for u, t, summ, q in pages_of(d):
            s.row(S2, rw, "A", [cid, t, u, t, goals.get(t, "Состав товара"), "Заголовок, разделы, тарифы, ключевые признаки"])
            s.date(S2, f"G{rw}", VIEW)
            s.w(S2, f"H{rw}", "Просмотр во встроенном браузере" if u in [x[0] for x in BROWSER.get(d, [])] else "Текст страницы, запрос 01.10.2026")
            s.w(S2, f"I{rw}", conf(u, q))
            s.w(S2, f"J{rw}", summ[:240])
            rw += 1
            pages += 1
        for g in C.gh_total_stars(d):
            s.row(S2, rw, "A", [cid, "Репозиторий GitHub", "https://github.com/" + g[0], "Сообщество", "Открытый код, лицензия, активность", "Звёзды, форки, дата обновления"])
            s.date(S2, f"G{rw}", "2026-09-30")
            s.w(S2, f"H{rw}", "GitHub API, ЛР4")
            s.w(S2, f"I{rw}", 5)
            s.w(S2, f"J{rw}", "%s звёзд, лицензия %s, обновление %s" % (C.fmt_int(g[1]), g[3], g[4][:10]))
            rw += 1
            pages += 1
    s.fit(S2, f"A7:J{rw}")
    lv = levitt_rows()
    sums = {}
    for i, (cid, nm, url, lvl, feat, how, ev, key) in enumerate(lv):
        r = 7 + i
        sila, ponj, vl = lscore(key, BY[cid])
        s.row(S3, r, "A", [cid, nm, url, lvl, feat, how, ev, 1, sila, ponj, vl])
        if key in FEATS:
            sums.setdefault(key, []).append(sila)
    s.fit(S3, f"A7:M{6 + len(lv)}")
    r = 7
    for key in KEYS:
        f = FEATS[key]
        avg = round(sum(sums[key]) / len(sums[key]) / 3 * 5, 2)
        dec = {"Обязательное": "Включить в минимальный состав NotaCode", "Линейное": "Реализовать на уровне рынка", "Привлекательное": "Рассмотреть как дифференциатор Pro",
               "Безразличное": "Не приоритет для сегмента студентов и аналитиков"}[f[4]]
        s.row(S4, r, "B", [f[1], f[2], f[8] + ". Категория Кано - экспертная классификация по распространённости и роли признака (опрос не проводился)", f[4], f[5], n(key)])
        s.w(S4, f"I{r}", avg)
        s.w(S4, f"K{r}", dec)
        s.w(S4, f"L{r}", WHO)
        r += 1
    todo = [
        ("Несколько нотаций (UML, BPMN, ERD) в одном инструменте", "Работать с разными нотациями без смены инструмента", "Lucidchart: UML-, BPMN-шаблоны и ERD markup (lucid.co/lucidchart)", "Привлекательное", 5, 1, "Рассмотреть как дифференциатор: полный набор нотаций проекта"),
        ("Нотации IDEF0, DFD, сети Петри", "Строить диаграммы по учебным и отраслевым стандартам", "На просмотренных страницах 8 конкурентов не найдены (IDEF упомянут в блоге Storm)", "Привлекательное", 5, 0, "Дифференциатор NotaCode: у конкурентов не найден"),
        ("Проверка правил нотации при вводе", "Получать подсказки об ошибках в модели", "🔲 ДОСНЯТЬ: проверка работы продуктов (тест редакторов)", "Неясное", 4, None, "🔲 ДОСНЯТЬ: решение после проверки продуктов"),
        ("Импорт форматов PlantUML, Mermaid, D2, draw.io, BPMN XML", "Перенести существующие диаграммы", "🔲 ДОСНЯТЬ: проверка работы продуктов (Visio import найден у Lucidchart)", "Неясное", 4, None, "🔲 ДОСНЯТЬ: решение после проверки продуктов"),
    ]
    for feat, task, ev, cat, w, cnt, dec in todo:
        s.row(S4, r, "B", [feat, task, ev, cat, w])
        if cnt is not None:
            s.w(S4, f"G{r}", cnt)
        s.w(S4, f"K{r}", dec)
        s.w(S4, f"L{r}", WHO)
        r += 1
    kano_n = len(KEYS) + len(todo)
    s.fit(S4, f"A7:L{r}")
    mat = {
        7: ("Рынок обещает три вида задач: диаграммы из текста (PlantUML, Mermaid, Mermaid Chart, Eraser), рисование в редакторе (draw.io, Lucidchart, Whimsical), управление процессами (Storm); ИИ-генерация есть у 5 из 8.", "Главные страницы и страницы ИИ (01.10.2026)",
            "Принять", "Построение диаграммы по текстовому описанию", "ИИ-генерация диаграммы по описанию", "Низкий", "Обязательно", "Основа продукта"),
        8: ("Явные аудитории: разработчики и технические писатели (PlantUML, Mermaid), команды и бизнес-пользователи (Mermaid Chart, Lucidchart, Whimsical), процессные аналитики (Storm), инженерные команды (Eraser).", "Главные страницы, ЛР4 карточки",
            "Принять", "Студенты и аналитики ПО", "Преподаватели и команды", "Низкий", "Обязательно", "Сегмент NotaCode: студенты (Free), аналитики и разработчики (Pro)"),
        9: ("Родовой товар: онлайн-редактор с кодом диаграммы (PlantUML server, Mermaid Live), облачный SaaS (Mermaid Chart, Lucidchart, Eraser, Whimsical, Storm) или бесплатное приложение (draw.io).", "Страницы продуктов и тарифов",
            "Принять", "Веб-IDE «диаграммы как код» (PWA)", "Настольный режим и отдельный сервер", "Низкий", "Обязательно", "Форма поставки NotaCode - PWA"),
        10: ("Ожидаемый состав: UML (4 из 8), ERD (6 из 8), экспорт (8 из 8), документация (6 из 8), вход (5 из 8), шаблоны (3 из 8).", "Страницы документации и продуктов",
             "Принять", "UML, BPMN, ERD, экспорт PNG/SVG/PDF, документация", "Шаблоны, история версий", "Средний", "Включить", "IDEF0, DFD, сети Петри у конкурентов не найдены: отличие NotaCode"),
        11: ("Доступ: открытый код или Free-тариф у 8 из 8; вход и личный кабинет у 5 из 8; совместная работа у 6 из 8.", "Главные страницы и тарифы",
             "Принять", "Работа в браузере без установки, Free-доступ", "Совместное редактирование", "Низкий", "Включить", "Коллаборация - линейное требование"),
        12: ("Тарифы открыты у 5 из 8: Free плюс подписка 9-20 USD за пользователя в месяц (Mermaid Chart 10 и 20, Lucidchart 9 и 10, Eraser 15 и 45, Whimsical 10 и 20); цены при годовой оплате у 4 из 8.", "Страницы тарифов (01.10.2026)",
             "Принять", "Free и Pro 40 USD в год (48 USD при 4 x 12 рядом)", "Командный тариф за пользователя", "Средний", "Включить", "Цена Pro ниже минимальных тарифов конкурентов (от 9 USD в месяц)"),
        13: ("Поддержка: документация у 6 из 8, учебный центр у Lucidchart, раздел поддержки у Whimsical; чат поддержки не проверялся.", "Страницы документации и поддержки",
             "Принять", "Документация и примеры", "Обучающие материалы для студентов", "Средний", "Включить", "Документация - обязательное требование"),
        14: ("Расширение ценности: ИИ у 5 из 8, API у 5 из 8, интеграции у 8 из 8, история версий у 5 из 8.", "Страницы тарифов и продуктов",
             "Рассмотреть", "ИИ-помощник и экспорт", "API, интеграции, история версий", "Средний", "Рассмотреть", "ИИ - привлекательное требование"),
        15: ("Доверие: независимые отзывы у 7 из 8, данные о числе пользователей на сайте у 4 из 8, раздел о безопасности у 6 из 8, открытый код у 3 из 8.", "G2, Capterra, Trustpilot, страницы сайтов",
             "Принять", "Политика конфиденциальности, примеры", "Открытый репозиторий, отзывы", "Средний", "Включить", "Пока продукт до MVP: отзывов нет"),
        16: ("Потенциал: ИИ-помощник и MCP (Storm), Lucid AI и платформа разработчика (Lucidchart), ИИ-кредиты (Mermaid Chart).", "Страницы сайтов",
             "Рассмотреть", "Не требуется в минимальной версии", "ИИ-помощник, платформа разработчика", "Средний", "Рассмотреть", "Развитие после MVP"),
        17: ("Граница товара: у всех восьми товар - сервис или библиотека; консультации и обучение не входят в тарифы Free и Pro.", "Страницы тарифов",
             "Принять", "Сервис без консультаций", "Платное обучение", "Низкий", "Принять", "Консультации вне границы товара"),
    }
    for rw_, (c3, c4, st, mn, ex, rk, dc, cm) in mat.items():
        s.w(S5, f"C{rw_}", c3)
        s.w(S5, f"D{rw_}", c4)
        s.w(S5, f"G{rw_}", st)
        s.w(S5, f"H{rw_}", mn)
        s.w(S5, f"I{rw_}", ex)
        s.w(S5, f"J{rw_}", rk)
        s.w(S5, f"K{rw_}", dc)
        s.w(S5, f"L{rw_}", cm)
    s.w(S5, "C18", "Рынок: цифровой товар диаграмм - онлайн-редактор или библиотека с кодом диаграммы для разработчиков и аналитиков, бесплатный доступ и платная подписка, экспорт, документация.")
    s.w(S5, "D18", "Сводка по листам 03, 04, 07")
    s.w(S5, "H18", "Цифровой товар NotaCode - это веб-IDE «диаграммы как код» для студентов и аналитиков ПО, который решает задачу построения и проверки диаграмм UML, BPMN, ERD, IDEF0 и DFD по текстовому описанию за счёт онлайн-редактора с экспортом, бесплатного уровня Free и подписки Pro 40 USD в год.")
    s.w(S5, "K18", "Принять")
    s.fit(S5, "A7:L18")
    for j, d in enumerate(DOMS):
        for i, v in enumerate(SC[d]):
            if v is not None:
                s.wrc(S6, 7 + i, 5 + j, v)
    for col in "EFGHIJKL":
        s.fx(S6, f"{col}90", f'=IFERROR(ROUND(SUMPRODUCT($D$7:$D$86,{col}$7:{col}$86)/SUMIF({col}$7:{col}$86,">=0",$D$7:$D$86),2),"")')
        s.fx(S6, f"{col}91", f'=IF({col}90="","",IF({col}90>=4.2,"Лидерский уровень",IF({col}90>=3.5,"Сильный уровень",IF({col}90>=2.5,"Средний уровень","Слабый уровень"))))')
    for rw in range(7, 87):
        s.fx(S6, f"O{rw}", f'=IF(N{rw}="","",IFERROR(INDEX($E$6:$L$6,1,MATCH(N{rw},E{rw}:L{rw},0)),""))')
    s.fit(S6, "A7:M31")
    for i, key in enumerate(KEYS):
        f = FEATS[key]
        rw = 7 + i
        s.row(S7, rw, "B", [f[1], f[8], f[3], f[4]])
        s.w(S7, f"F{rw}", n(key))
        s.w(S7, f"H{rw}", round(sum(sums[key]) / len(sums[key]) / 3 * 5, 2))
        s.w(S7, f"J{rw}", "Признак есть у %d из 8 конкурентов; %s" % (n(key), {"Обязательное": "входит в минимальный состав товара", "Линейное": "реализовать на уровне рынка",
                                                                           "Привлекательное": "кандидат на дифференциацию", "Безразличное": "не приоритет"}[f[4]]))
    s.fit(S7, f"A7:J{6 + len(KEYS)}")
    adv = [
        ("C07", "ИИ-генерация и diagram-as-code в одном продукте", "«AI for diagrams that matter»; тариф Free включает diagram-as-code и 3 ИИ-диаграммы (eraser.io, 01.10.2026)", L4, "Привлекательное", "Функциональное", 4, 5, 4, 5),
        ("C04", "Девять модулей процессного управления и русскоязычный рынок с тарифами в рублях", "stormbpmn.com и /pricing, 01.10.2026; Россия 62,99 % трафика", L4, "Привлекательное", "Интеграционное", 5, 4, 4, 5),
        ("C06", "Глубина товара и масштаб: 100 шаблонов в Free, Visio import, SAML, Fortune 500", "lucid.app/pricing/lucidchart и lucid.co/lucidchart, 01.10.2026", L4, "Линейное", "Доверительное", 2, 5, 4, 5),
        ("C05", "Бесплатное приложение без enterprise-тарифа, privacy-first, 100M+ пользователей", "drawio.com, 01.10.2026; GitHub (ЛР4)", L3, "Привлекательное", "Экономическое", 3, 5, 5, 4),
        ("C02", "Открытая экосистема интеграций и крупнейшее сообщество (90 489 звёзд)", "mermaid.js.org/ecosystem; GitHub (ЛР4)", L4, "Привлекательное", "Сетевой эффект", 3, 5, 4, 5),
        ("C01", "Широкий набор UML-диаграмм и запуск на собственном сервере", "plantuml.com/running и /class-diagram, 01.10.2026", L2, "Обязательное", "Функциональное", 3, 4, 4, 4),
        ("C03", "Прозрачные тарифы и зрители без оплаты в Premium", "mermaid.ai/pricing, 01.10.2026", L3, "Привлекательное", "Экономическое", 3, 4, 4, 5),
        ("C08", "Неограниченные гости и зрители на всех тарифах", "whimsical.com/pricing, 01.10.2026", L4, "Привлекательное", "Экономическое", 3, 3, 3, 5),
    ]
    for i, (cid, feat, ev, lvl, kn, typ, rr, st, val, q) in enumerate(adv):
        s.row(S8, 7 + i, "B", [cid, feat, ev, lvl, kn, typ, rr, st, val, q])
    s.fit(S8, f"A7:M{6 + len(adv)}")
    top = sorted(DOMS, key=lambda d: -total(d))
    s.w(S9, "B21", "Минимальный состав: бесплатный доступ (8 из 8), экспорт (8 из 8), интеграции (8 из 8), UML (4 из 8), ERD (6 из 8), документация (6 из 8), открытая страница тарифов (5 из 8).")
    s.w(S9, "B22", "Нельзя игнорировать: Free-тариф, экспорт, понятные тарифы с ценой за пользователя в месяц, документация, ИИ-генерация (5 из 8) и интеграции.")
    s.w(S9, "B23", "Зоны дифференциации NotaCode: IDEF0, DFD и сети Петри на просмотренных сайтах не найдены; полный набор UML, BPMN, ERD найден только у Lucidchart; тарифы в рублях - только у Storm.")
    s.w(S9, "B24", "Лучшие практики: прозрачные тарифы с ИИ-лимитами (Eraser, Mermaid Chart), шаблоны в бесплатном тарифе (Lucidchart), зрители без оплаты (Whimsical, Mermaid Chart), открытая экосистема (Mermaid).")
    s.w(S9, "B25", "Риск: копировать тарифы за пользователя без проверки спроса студентов; цена Pro 40 USD в год ниже минимальных тарифов конкурентов (от 9 USD в месяц), её нужно подтвердить опросом.")
    nread = sum(len(pages_of(d)) for d in DOMS) + sum(len(C.gh_total_stars(d)) for d in DOMS)
    j = [["Исправление шаблона", "Д-1", "Лист 06_Сравнение, строки 90 и 91 (итоговый балл и интерпретация): формулы столбцов F-L ссылались на столбец E (баллы C01), поэтому итог был одинаковым (3,28) у всех конкурентов. Ссылки заменены на собственные столбцы (E-L); логика формулы сохранена."],
         ["Исправление шаблона", "Д-2", "Лист 06_Сравнение, столбец O (Лидер) в пустых строках P26-P80: MAX пустого диапазона даёт 0, MATCH не находит значение, результат #Н/Д. Формула обёрнута в IFERROR (при пустых баллах - пустая ячейка)."],
         ["Источники", "И-1", "Страницы 8 конкурентов (главные, тарифы, документация, интеграции, шаблоны, безопасность, блог): автоматическое извлечение текста 01.10.2026 (Материалы_собранные/sajty_konkurentov_stranicy_2026-10-01.json) и чтение во встроенном браузере (Lucidchart, тарифы Mermaid Chart); данные ЛР1-ЛР4 от 30.09.2026."],
         ["Выборка", "В-1", "8 компаний из 22 части A (поле «Переходит в части B и C»). Тип конкурента - итоговый уровень из части A."],
         ["Правило", "П-1", "Признак засчитывается, если он найден на просмотренных страницах; отсутствие на просмотренных страницах не доказывает отсутствия у продукта (значения занижают долю)."],
         ["Правило", "П-2", "Достоверность в 02_Карта_сайтов: 5 - страница прочитана целиком (тарифы, Lucidchart, Mermaid Chart) или данные GitHub API; 4 - автоматическое извлечение текста."],
         ["Правило", "П-3", "03_Левитт: сила реализации 3, если признак явно описан на странице (цена, тариф, функция), 2 - найден по ключевым словам; понятность 3 для SaaS-сайтов с отдельными разделами, 2 для остальных; влияние на ценность 1-5 - по типу признака."],
         ["Правило", "П-4", "Категории Кано присвоены экспертно (по распространённости и роли признака для студентов и аналитиков ПО); опрос по методу Кано не проводился. Требования без данных помечены «Неясное»."],
         ["Правило", "П-5", "06_Сравнение: баллы 0-5 по 25 критериям поставлены по просмотренным страницам; пусто - критерий не подтверждён страницами. Итог - взвешенный балл шаблона."],
         ["Правило", "П-6", "08_Преимущества: редкость, сила, ценность и качество доказательства - экспертные оценки 1-5 по просмотренным страницам и данным ЛР4."],
         ["Нормы дашборда", "К-1", "Страниц: %d (норма 30+); признаков по Левитту: %d (норма 40+); требований по Кано: %d (норма 25+)." % (nread, len(lv), kano_n)],
         ["Итог сравнения", "К-2", "Итоговые баллы: " + "; ".join("%s %s" % (CO[d]["name"], str(total(d)).replace(".", ",")) for d in top) + "."],
         ["Ограничения", "О-1", "Оценки экспертные; страницы просмотрены с одного устройства. 🔲 ДОСНЯТЬ: проверка работы продуктов (проверка правил нотации, импорт форматов), опрос для категорий Кано."]]
    s.new_sheets.append(dict(name="98_Журнал", title="Журнал рабочей копии: источники, правила, ограничения", header=["Раздел", "Код", "Содержание"], rows=j, widths=[22, 8, 150]))
    s.to_json(os.path.join(C.DATA, "spec_b.json"))
    return dict(pages=nread, levitt=len(lv), kano=kano_n, top=[(CO[d]["name"], total(d)) for d in top])


# --------------------------------------------------------------------------- ЧАСТЬ C
TYPE_C = {"plantuml.com": "прямой", "mermaid.js.org": "косвенный", "mermaidchart.com": "косвенный", "stormbpmn.com": "смежная модель",
          "app.diagrams.net": "косвенный", "lucidchart.com": "косвенный", "eraser.io": "косвенный", "whimsical.com": "заменитель"}
PRIO_C = {"Высокий": "высокий", "Средний": "средний", "Низкий": "низкий"}
MODEL_C = {"plantuml.com": "лицензия", "mermaid.js.org": "лицензия", "mermaidchart.com": "условно-бесплатная модель", "stormbpmn.com": "условно-бесплатная модель",
           "app.diagrams.net": "лицензия", "lucidchart.com": "условно-бесплатная модель", "eraser.io": "условно-бесплатная модель", "whimsical.com": "условно-бесплатная модель"}
BM = {  # деятельность, партнёры, затраты, данные и сеть, гипотеза
    "plantuml.com": ("Разработка языка и серверной части, выпуск релизов (страница загрузки), документация", "Интеграции в вики, редакторы, IDE и языки программирования (страница running)",
                     "Признаки: разработка сообщества и серверы; ИИ-расходов на сайте нет", "Сообщество на GitHub (13 346 звёзд), форумы", "ценность - диаграммы из текста; доход не из продажи самого инструмента"),
    "mermaid.js.org": ("Развитие библиотеки, экосистемы и документации", "Интеграции сообщества: редакторы, вики, платформы (страница integrations-community)",
                       "Признаки: разработка сообщества; платные планы вынесены в Mermaid Chart", "Сообщество: 90 489 звёзд GitHub, плагины", "ядро открытого стандарта, монетизация вынесена в Mermaid Chart"),
    "mermaidchart.com": ("Развитие облачного редактора, ИИ-функций, документации", "Плагины и интеграции (меню Product), экосистема Mermaid.js", "Признак: лимиты ИИ-кредитов указывают на стоимость ИИ-вызовов",
                         "Совместная работа и общий доступ; 5M пользователей и 200k компаний по заявлению сайта", "облачный сервис над открытым стандартом: доход от тарифов за пользователя"),
    "stormbpmn.com": ("Развитие девяти модулей платформы, ИИ-ассистента, MCP; продажи и внедрение on-prem", "MCP-интеграции, API в Enterprise", "Признаки: безлимитный ИИ в облачных тарифах, on-prem для крупных клиентов",
                      "Связи процессов, реестр, оргструктура и база знаний внутри платформы; более 1 000 клиентов", "платформа процессного управления для русскоязычного рынка: доход от тарифов в рублях и on-prem"),
    "app.diagrams.net": ("Развитие приложения, интеграций и встраивания; документация", "Google Drive, Microsoft SharePoint и OneDrive, Atlassian Confluence и Jira, GitHub, VS Code, Notion", "Признак: «Not VC-funded», нет enterprise-тарифа",
                         "Данные у пользователя («we cannot access it»); совместимость файлов с 2005 г.", "бесплатный массовый инструмент: привлекает аудиторию, монетизация на сайте не показана"),
    "lucidchart.com": ("Развитие продукта, ИИ, платформы разработчика, продажи Enterprise", "Microsoft 365, Confluence, Jira, LeanIX, Ardoq, Salesforce", "Признаки: ИИ, поддержка, учебный центр, Enterprise Shield",
                       "Совместная работа, шаблоны, связывание данных; Fortune 500 по заявлению сайта", "облачный сервис с лестницей тарифов Free, Individual, Team, Enterprise"),
    "eraser.io": ("Развитие ИИ-генерации диаграмм, интеграций, API", "GitHub, Notion, Confluence, VS Code", "Признак: лимиты ИИ-диаграмм по тарифам указывают на стоимость ИИ",
                  "Совместная работа, гости без оплаты; история версий по тарифам", "подписка вокруг ИИ-генерации и diagram-as-code для технических команд"),
    "whimsical.com": ("Развитие доски, диаграмм, документов и ИИ", "Интеграции указаны на сайте (число не проверялось)", "Признаки: хранилище и история версий по тарифам, ИИ",
                      "Совместная работа, гости и зрители без ограничений", "подписка для продуктовых команд: доход от платных мест редакторов"),
}
CHAN = {  # призыв, регистрация, пробный доступ, воронка, сложность 1-5, сила 1-5
    "plantuml.com": ("Онлайн-сервер без призыва к регистрации; ссылки на загрузку", "не требуется", "онлайн-сервер без регистрации", "контентная воронка", 1, 2),
    "mermaid.js.org": ("«Get started», документация, живой редактор", "не требуется для библиотеки", "Mermaid Live Editor", "контентная воронка", 2, 3),
    "mermaidchart.com": ("«Start free», «Contact sales»", "регистрация для Free", "Free (до 6 диаграмм)", "регистрация", 2, 4),
    "stormbpmn.com": ("«Начать бесплатно», «Рассчитать для команды», «Обсудить on-prem»", "регистрация для Персонального", "бесплатный тариф, «Попробовать всё» (Бизнес)", "корпоративные продажи", 2, 4),
    "app.diagrams.net": ("Открыть приложение; «Embed»; GitHub", "не требуется", "приложение без регистрации", "самостоятельная покупка", 1, 4),
    "lucidchart.com": ("«Sign up free», вход через Google и Microsoft", "регистрация", "Free; пробный период 7 дней платных тарифов", "пробный доступ", 2, 5),
    "eraser.io": ("«Try Eraser», «Get started for free»", "регистрация", "Free (3 файла)", "регистрация", 2, 4),
    "whimsical.com": ("«Get started», «Contact sales» (Business)", "регистрация", "Free (50 объектов)", "регистрация", 2, 4),
}
OPS = {  # ресурсы, процессы, технологии, данные, поддержка, масштаб, копирование, риск, вывод
    "plantuml.com": ("Сообщество разработчиков, домен с 2010 г.", "Выпуск релизов, поддержка форумов", "Серверный рендеринг на Java; языковой справочник", "Диаграммы обрабатываются на сервере проекта", "FAQ, форум", 3, 2, "Низкая монетизация", "Устойчив за счёт сообщества, не за счёт доходов"),
    "mermaid.js.org": ("Сообщество (90 489 звёзд), команда проекта", "Релизы библиотеки, развитие экосистемы", "JavaScript-библиотека", "Рендеринг в браузере", "Документация, сообщество", 4, 3, "Зависимость от Mermaid Chart в финансировании", "Устойчив за счёт экосистемы"),
    "mermaidchart.com": ("Команда Mermaid, облако, ИИ", "Развитие редактора и ИИ-функций", "Облачный редактор, ИИ, API", "Данные пользователей в облаке", "Документация, контакты продаж", 4, 3, "Расходы на ИИ", "Устойчив при росте платных мест"),
    "stormbpmn.com": ("Платформа из девяти модулей, база клиентов (более 1 000)", "Продажи, внедрение, развитие модулей", "BPMN-редактор, ИИ, симуляция DES, MCP", "Модели процессов, реестр, оргструктура, опросы", "База знаний; Enterprise: аудит и ИБ", 3, 4, "Зависимость от русскоязычного рынка", "Модель устойчива у корпоративных клиентов"),
    "app.diagrams.net": ("Репозитории (63 351 звезда desktop), независимая частная компания", "Развитие приложения и интеграций", "Приложение на JavaScript, desktop, плагины", "Данные хранятся у пользователя", "Документация, GitHub", 5, 3, "Неясная монетизация на сайте", "Очень устойчив за счёт аудитории и независимости"),
    "lucidchart.com": ("Команда и инфраструктура Lucid, платформа, бренд", "Продажи Enterprise, развитие ИИ и платформы", "Облако, ИИ, платформа разработчика, интеграции", "Связывание данных, импорт данных", "Учебный центр, поддержка, Enterprise Shield", 5, 5, "Высокая зависимость от платных мест", "Устойчив: широкий продукт и Enterprise"),
    "eraser.io": ("Команда продукта, ИИ-инфраструктура", "Развитие ИИ и интеграций", "ИИ-генерация, diagram-as-code, API", "Данные в облаке, лимиты ИИ", "Документация docs.eraser.io", 4, 3, "Расходы на ИИ при росте", "Умеренно устойчив; зависит от ИИ-расходов"),
    "whimsical.com": ("Команда продукта, бренд", "Развитие доски, диаграмм, документов", "Облако, desktop, ИИ", "Данные в облаке, история версий", "Раздел support, страница Security", 4, 2, "Сильная конкуренция универсальных досок", "Устойчив у продуктовых команд"),
}
BMS = {  # сегменты, ценность, товар, каналы, отношения, доходы, ресурсы, партнёры, данные/сеть, масштаб, защищённость
    "plantuml.com": [3, 4, 4, 3, 2, 2, 3, 4, 3, 3, 4], "mermaid.js.org": [3, 4, 4, 3, 3, 2, 4, 4, 4, 4, 4], "mermaidchart.com": [4, 4, 4, 4, 4, 4, 3, 4, 3, 4, 3],
    "stormbpmn.com": [4, 4, 5, 4, 4, 5, 3, 3, 3, 4, 3], "app.diagrams.net": [4, 5, 4, 3, 3, 2, 4, 5, 4, 5, 4], "lucidchart.com": [4, 4, 5, 5, 4, 5, 5, 5, 4, 5, 5],
    "eraser.io": [4, 4, 4, 4, 4, 5, 3, 4, 3, 3, 3], "whimsical.com": [3, 4, 4, 4, 4, 5, 3, 3, 3, 3, 3],
}
BMW = [.08, .13, .1, .09, .06, .12, .08, .06, .1, .09, .09]
FIN = {"plantuml.com": ("Бесплатно", "не применимо", "Нет единицы оплаты", 4, 2), "mermaid.js.org": ("Бесплатно", "не применимо", "Нет единицы оплаты", 5, 2),
       "mermaidchart.com": ("Basic Free, Plus 10 USD, Premium 20 USD, Enterprise", "за пользователя в месяц", "Basic: до 6 диаграмм, 15 ИИ-кредитов", 5, 4),
       "stormbpmn.com": ("Персональный 0, Команда 1 200 руб., Бизнес 4 720 руб., Enterprise от 990 тыс. руб. в год", "за пользователя в месяц", "Персональный: до 50 моделей, 5 раз делиться процессами", 5, 5),
       "app.diagrams.net": ("Бесплатно", "не применимо", "Нет единицы оплаты", 5, 2),
       "lucidchart.com": ("Free, Individual 9 USD, Team 10 USD, Enterprise", "за пользователя в месяц", "Free: 3 документа, 75 фигур на документ", 4, 4),
       "eraser.io": ("Free 0, Starter 15 USD, Business 45 USD, Enterprise", "за участника в месяц", "Free: 3 файла, 3 ИИ-диаграммы", 5, 4),
       "whimsical.com": ("Free 0, Pro 10 USD, Business 20 USD", "за редактора в месяц", "Free: 50 объектов доски и 50 блоков документа в месяц", 5, 4)}
PERIOD = {"plantuml.com": "нет платежей", "mermaid.js.org": "нет платежей", "mermaidchart.com": "при оплате за год", "stormbpmn.com": "месяц или год (скидка 20 %)",
          "app.diagrams.net": "нет платежей", "lucidchart.com": "при оплате за год", "eraser.io": "год (15 и 45 USD) или месяц (20 и 60 USD)", "whimsical.com": "месячная цена за редактора"}
TRIAL = {"lucidchart.com": "7 дней", "stormbpmn.com": "кнопка «Попробовать всё» в тарифе Бизнес"}
ENT = {"mermaidchart.com": "Enterprise: SSO, менеджер по успеху клиента, договор", "stormbpmn.com": "Enterprise on-prem: SSO, API, аудит, ИБ", "lucidchart.com": "Enterprise: SAML, Enterprise Shield, Salesforce",
       "eraser.io": "Enterprise: гибкое развёртывание, менеджер по успеху клиента", "whimsical.com": "Business с кнопкой «Contact sales», SAML SSO"}
MONCONCL = {"mermaidchart.com": "Подписка за пользователя; зрители без оплаты; ИИ-кредиты по тарифам", "stormbpmn.com": "Бесплатный старт и рост до on-prem: потоки от подписок и корпоративных договоров",
            "lucidchart.com": "Подписка за место с пробным периодом и Enterprise", "eraser.io": "Подписка за участника с лимитами ИИ", "whimsical.com": "Подписка за редактора, зрители бесплатно"}
ADV_C = [("C07", "Тарифы с лимитами ИИ-диаграмм и diagram-as-code в бесплатном тарифе", "товарное", "цифровой товар", "eraser.io/pricing", 4, 3, 4, 5),
         ("C04", "Бесплатный тариф с безлимитным ИИ и тарифы в рублях; on-prem", "ценовое", "потоки доходов", "stormbpmn.com/pricing", 4, 4, 4, 5),
         ("C06", "Лестница тарифов с пробным периодом и Enterprise Shield", "товарное", "потоки доходов", "lucid.app/pricing/lucidchart", 5, 5, 5, 5),
         ("C05", "Бесплатное приложение без enterprise-тарифа и данные у пользователя", "брендовое", "ценностное предложение", "drawio.com", 4, 4, 4, 4),
         ("C02", "Экосистема интеграций и сообщество 90 489 звёзд", "партнерское", "ключевые партнеры", "mermaid.js.org/ecosystem", 5, 4, 3, 5),
         ("C03", "Зрители без оплаты и четыре ясных тарифа", "ценовое", "потоки доходов", "mermaid.ai/pricing", 4, 3, 4, 5),
         ("C08", "Гости и зрители без ограничений на всех тарифах", "ценовое", "отношения с клиентами", "whimsical.com/pricing", 3, 3, 3, 5),
         ("C01", "Многолетний стандарт для UML из текста, запуск на своём сервере", "технологическое", "ключевые ресурсы", "plantuml.com/running", 4, 2, 4, 4)]


def evid(key, dom):
    return 5 if (key in PRICE_KEYS and dom in SAAS) else (4 if key in STRONG else 3)


def facts():
    out = []
    for d in DOMS:
        cid = IDS[d]
        out.append((cid, "Главная страница", HOME[d], "Заголовок и описание", "Обещание: " + TXT[d], "ценностное предложение", 4, "главная страница, 01.10.2026"))
        out.append((cid, "Главная страница", HOME[d], "Состав товара", CO[d]["product"], "цифровой товар", 4, "страницы сайта, ЛР4"))
        out.append((cid, "Тарифы", feat_url("pricing_page", d) if d in FEATS["pricing_page"][7] else HOME[d], "Тарифная таблица", TIERS[d] or "Условия использования", "потоки доходов", 5 if d in SAAS else 4, "страница тарифов или лицензия"))
        ch = sw_channels(d)
        if ch:
            out.append((cid, "Similarweb Pro", HOME[d], "Каналы", ch, "каналы", 3, "Similarweb Pro (ЛР4)"))
        gh = C.gh_total_stars(d)
        if gh:
            out.append((cid, "GitHub", "https://github.com/" + gh[0][0], "Репозиторий", "; ".join("%s: %s звёзд, лицензия %s" % (g[0], C.fmt_int(g[1]), g[3]) for g in gh), "ключевые ресурсы", 5, "GitHub API, 30.09.2026"))
        for k in KEYS:
            if k in ("free", "paid", "pricing_page", "reviews"):
                continue
            f = FEATS[k]
            if d in f[7]:
                out.append((cid, "Страницы сайта", feat_url(k, d), f[1], det(k, d), f[6], evid(k, d), f[8][:90]))
    return out


def build_c():
    s = Spec("Шаблон_анализа_бизнес_модели_конкурентов.xlsx", "analiz_biznes_modeli_konkurentov_NotaCode.xlsx")
    s.extra["author"] = WHO
    s.extra["reparse_xlookup"] = True
    s.extra["title"] = "Анализ бизнес-моделей конкурентов: NotaCode"
    S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12 = ("02_Конкуренты", "03_Факты_сайта", "04_Бизнес_модель", "05_Товар_ценность", "06_Монетизация", "07_Каналы", "08_Операц_модель",
                                                      "09_Матрица", "10_Стандарт", "11_Преимущества", "12_Сводка")
    for rw in range(4, 204):
        s.fx(S10, f"E{rw}", f"=IF($D{rw}=\"\",\"\",IFERROR($D{rw}/'12_Сводка'!$B$5,0))")
    for i, d in enumerate(DOMS):
        co, rw = CO[d], 4 + i
        s.w(S2, f"A{rw}", IDS[d])
        s.row(S2, rw, "B", [co["name"], d, co["seg"], TYPE_C[d], co["market"], PRIO_C[co["prio"]], "завершен"])
        s.date(S2, f"I{rw}", VIEW)
        s.w(S2, f"J{rw}", WHO)
        s.w(S2, f"K{rw}", "Профиль построен по просмотренным страницам; блоки деятельности, партнёров, затрат и сетевых эффектов - косвенные признаки и гипотезы")
    s.fit(S2, "A4:K11")
    fs = facts()
    for i, (cid, sect, url, blk, fact, el, ev, cit) in enumerate(fs):
        rw = 4 + i
        s.w(S3, f"A{rw}", "F%03d" % (i + 1))
        s.w(S3, f"B{rw}", cid)
        s.row(S3, rw, "D", [sect, url, blk, fact, el])
        s.w(S3, f"I{rw}", ev)
        s.date(S3, f"J{rw}", VIEW)
        s.w(S3, f"K{rw}", cit)
    s.fit(S3, f"A4:K{3 + len(fs)}")
    for i, d in enumerate(DOMS):
        co, rw = CO[d], 4 + i
        s.w(S4, f"A{rw}", IDS[d])
        act, par, cost, net, hyp = BM[d]
        fe = [FEATS[k][1].lower() for k in KEYS if d in FEATS[k][7]]
        rel = C.REVIEWS[d]["txt"] if d in FEATS["reviews"][7] else "Заявление сайта: " + DET[("customer_stats", d)]
        res = "; ".join("%s: %s звёзд" % (g[0], C.fmt_int(g[1])) for g in C.gh_total_stars(d)) or "Команда продукта и облачная инфраструктура (по описанию сайта)"
        s.row(S4, rw, "C", [co["seg"], TXT[d], co["product"] + "; " + ", ".join(fe[:8]), sw_channels(d) or "Вход и документация на сайте; данные Similarweb по домену не получены",
                            rel, TIERS[d] or MODEL_C[d], res, act, par, cost, net, "Гипотеза (для проверки): " + hyp])
    s.fit(S4, "A4:Q11")
    prod = {"plantuml.com": "Диаграммы UML из текста", "mermaid.js.org": "Диаграммы из текста и кода", "mermaidchart.com": "Облачный редактор Mermaid",
            "stormbpmn.com": "Моделирование и управление процессами", "app.diagrams.net": "Бесплатный редактор диаграмм", "lucidchart.com": "Облачный редактор диаграмм с ИИ",
            "eraser.io": "ИИ-генерация технических диаграмм", "whimsical.com": "Доска, диаграммы и документы"}
    for i, d in enumerate(DOMS):
        co, rw = CO[d], 4 + i
        s.w(S5, f"A{rw}", IDS[d])
        s.row(S5, rw, "C", [prod[d], co["product"], "Экспорт, документация, интеграции", "Шаблоны, совместная работа, ИИ, API по тарифам",
                            FEATS["progress"][8].split(";")[0] if d in FEATS["progress"][7] else "Признаки развития на просмотренных страницах не найдены"])
        s.w(S5, f"J{rw}", co["seg"])
        s.w(S5, f"K{rw}", BM[d][4])
        s.w(S5, f"L{rw}", HOME[d])
    s.fit(S5, "A4:M11")
    for i, d in enumerate(DOMS):
        rw = 4 + i
        tiers, unit, limits, tr, fl = FIN[d]
        s.w(S6, f"A{rw}", IDS[d])
        s.row(S6, rw, "C", [MODEL_C[d], feat_url("pricing_page", d) if d in FEATS["pricing_page"][7] else HOME[d], "да", TRIAL.get(d, "не найден на просмотренных страницах"), tiers, unit, limits,
                            PERIOD[d], ENT.get(d, "не найдены"), tr, fl, MONCONCL.get(d, "Нет прямых доходов на сайте: ценность создаёт аудиторию и сообщество")])
    s.fit(S6, "A4:N11")
    for i, d in enumerate(DOMS):
        rw = 4 + i
        s.w(S7, f"A{rw}", IDS[d])
        cta, reg, trial, funnel, cx, st = CHAN[d]
        sw = C.sw(d)
        org = ("Органический поиск " + C.fmt_num(sw["organic_pct"], 2) + " % трафика (Similarweb Pro)") if sw and sw.get("organic_pct") is not None else "Данные Similarweb по домену не получены"
        trust = C.REVIEWS[d]["txt"] if d in FEATS["reviews"][7] else DET[("customer_stats", d)]
        content = "Документация, примеры, блог на сайте" if d in ("plantuml.com", "mermaid.js.org", "mermaidchart.com", "app.diagrams.net", "eraser.io", "lucidchart.com", "stormbpmn.com") else "Страницы шаблонов и ИИ"
        s.row(S7, rw, "C", [sw_channels(d) or "Данные Similarweb Pro по домену не получены", content, org, cta, reg, funnel, reg, trial, trust, cx, st,
                            "Путь клиента: " + ("вход без регистрации" if cx == 1 else "регистрация или заявка") + "; тип воронки - " + funnel])
    s.fit(S7, "A4:N11")
    for i, d in enumerate(DOMS):
        rw = 4 + i
        res, proc, tech, data, sup, sc_, cp, risk, concl = OPS[d]
        s.w(S8, f"A{rw}", IDS[d])
        s.row(S8, rw, "C", [res, proc, tech, data, BM[d][1], BM[d][1], sup, BM[d][2], sc_, cp, risk, concl])
    s.fit(S8, "A4:N11")
    for i, d in enumerate(DOMS):
        rw = 4 + i
        s.w(S9, f"A{rw}", IDS[d])
        for j, v in enumerate(BMS[d]):
            s.wrc(S9, rw, 3 + j, v)
    s.fit(S9, "A4:Q11")
    std = [("free", "потоки доходов"), ("paid", "потоки доходов"), ("pricing_page", "потоки доходов"), ("enterprise", "потоки доходов"), ("annual", "потоки доходов"), ("trial", "потоки доходов"),
           ("guests", "отношения с клиентами"), ("integr", "ключевые партнеры"), ("api", "цифровой товар"), ("ai", "цифровой товар"), ("sso", "потоки доходов"), ("open", "ключевые ресурсы"),
           ("reviews", "отношения с клиентами"), ("customer_stats", "отношения с клиентами"), ("security_page", "ценностное предложение"), ("docs", "отношения с клиентами"),
           ("onprem", "структура затрат"), ("login", "каналы"), ("ru_lang", "целевые сегменты")]
    for i, (k, blk) in enumerate(std):
        rw = 4 + i
        f = FEATS[k]
        s.row(S10, rw, "A", [f[1], blk, f[2]])
        s.w(S10, f"D{rw}", n(k))
        s.w(S10, f"H{rw}", f[8])
    s.fit(S10, f"A4:H{3 + len(std)}")
    for i, (cid, feat, typ, blk, pg, sl, cp, com, dk) in enumerate(ADV_C):
        rw = 4 + i
        s.w(S11, f"A{rw}", cid)
        s.row(S11, rw, "C", [feat, typ, blk, pg, sl, cp, com, dk])
    s.fit(S11, "A4:L11")
    evavg = {d: sum(x[6] for x in fs if x[0] == IDS[d]) / sum(1 for x in fs if x[0] == IDS[d]) for d in DOMS}
    qual = {d: sum(w * v for w, v in zip(BMW, BMS[d])) / sum(BMW) * .6 + evavg[d] * .25 + 5 * .15 for d in DOMS}  # формула 09_Матрица, столбец Q
    top = sorted(DOMS, key=lambda d: -qual[d])
    s.w(S12, "B23", "Рыночный стандарт (порог шаблона 70 %): бесплатный доступ и интеграции (8 из 8), независимые отзывы (7 из 8), раздел о безопасности и документация (по 6 из 8).")
    s.w(S12, "B24", "Преобладает условно-бесплатная модель: Free плюс подписка за пользователя или редактора в месяц (Mermaid Chart, Storm, Lucidchart, Eraser, Whimsical - 5 из 8); три инструмента бесплатны с открытым кодом (PlantUML, Mermaid, draw.io).")
    s.w(S12, "B25", "Зона дифференциации по порогам шаблона: открытый код и сообщество (3 из 8). Формирующийся стандарт: подписка, открытая страница тарифов, ИИ, API, SSO, вход (по 5 из 8), корпоративный тариф, годовая оплата, гости, данные о числе клиентов (по 4 из 8). Слабые сигналы (по 1 из 8): пробный период (Lucidchart), тарифы в рублях (Storm); IDEF0, DFD и сети Петри на сайтах не найдены.")
    s.w(S12, "B26", "Сильнейшие по итогу матрицы с учётом надёжности: " + ", ".join("%s (%s)" % (CO[d]["name"], str(round(qual[d], 2)).replace(".", ",")) for d in top[:3]) + "; профили опираются на просмотренные страницы, доказательность 3,6-4,0.")
    s.w(S12, "B27", "Видимые элементы (тарифы, лимиты, отзывы) копировать можно; ресурсы (сообщество 90 489 звёзд Mermaid, 100M+ пользователей draw.io, Fortune 500 у Lucidchart) и партнёрства быстро не повторяются.")
    j = [["Исправление шаблона", "Д-1", "Лист 10_Стандарт, столбец E (Доля конкурентов): формула делила на ячейку 12_Сводка!B4 (заголовок «Значение»), поэтому доля везде была 0 и статус «слабый сигнал». Знаменатель заменён на 12_Сводка!B5 (число конкурентов в реестре); остальная логика сохранена."],
         ["Источники", "И-1", "Страницы тарифов, главные страницы, документация конкурентов: автоматическое извлечение текста 01.10.2026 и чтение во встроенном браузере (Lucidchart, тарифы Mermaid Chart); Similarweb Pro, GitHub, отзывы - ЛР1-ЛР4 (30.09.2026)."],
         ["Выборка", "В-1", "8 конкурентов части B. Типы по справочнику 13_Справочники: PlantUML - прямой; Storm - смежная модель; Whimsical - заменитель; остальные - косвенные."],
         ["Правило", "П-1", "Доказательность 1-5: 5 - данные GitHub API и страницы тарифов SaaS-конкурентов; 4 - явное описание на странице, главная страница; 3 - найдено по ключевым словам или данным Similarweb."],
         ["Правило", "П-2", "Баллы 09_Матрица (1-5) - экспертная оценка силы подтверждения блока и положения на рынке; веса в строке 2 заданы шаблоном. Оценки 1-5 листов 06, 07, 08, 11 - экспертные."],
         ["Правило", "П-3", "Статус «завершен»: все 12 блоков заполнены; блоки деятельности, партнёров, затрат и сетевых эффектов основаны на косвенных признаках и гипотезах и помечены в тексте."],
         ["Ограничения", "О-1", "Страницы просмотрены с одного устройства и из одной страны; рекламные библиотеки и выдача поиска не проверялись (доступ закрыт). 🔲 ДОСНЯТЬ: рекламные объявления, отзывы G2 и Capterra по Storm."]]
    s.new_sheets.append(dict(name="14_Журнал", title="Журнал рабочей копии: исправления, источники, правила, ограничения", header=["Раздел", "Код", "Содержание"], rows=j, widths=[22, 8, 150]))
    s.to_json(os.path.join(C.DATA, "spec_c.json"))
    return dict(facts=len(fs), top=[CO[d]["name"] for d in top])


if __name__ == "__main__":
    print("B", build_b())
    print("C", build_c())
    print({k: n(k) for k in KEYS})
