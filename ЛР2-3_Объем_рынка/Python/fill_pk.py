# -*- coding: utf-8 -*-
"""Заполнение рабочей копии ПК-X (оценка через количество потенциальных клиентов)."""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from xl_com import Book

NAME = "ПК_потенциальные_клиенты_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)
import assumptions as AS
CR1, CR2 = AS.SV_CR1, I.CR_PRO[1]
COMM = AS.COMM_SW


def main():
    b = Book(NAME)
    try:
        s1 = "01_Параметры"
        b.set(s1, "B4", "NotaCode — веб-IDE для построения и проверки диаграмм формальных нотаций как текста (подписка Free / Pro)")
        b.set(s1, "B5", "Аналитика и проектирование ПО (UML, BPMN, ERD, IDEF, DFD)")
        b.set(s1, "B6", "Онлайн-редакторы и генераторы диаграмм формальных нотаций по текстовому описанию; UML/BPMN-редакторы; универсальные редакторы в части нотационных диаграмм. Исключены: универсальные доски, корпоративные CASE-платформы, курсы программирования")
        b.set(s1, "B7", "Республика Беларусь (РФ/СНГ — гипотеза вне расчёта, решение В-6)")
        b.set(s1, "B8", "B2C-подписка (freemium Free / Pro); единица клиента — пользователь (физическое лицо)")
        b.set(s1, "B11", D)
        b.set(s1, "B12", "К. А. Хаджинова")

        s2 = "02_Сегменты"
        for i, sg in enumerate(I.SEGMENTS):
            r = 4 + i
            b.set(s2, f"A{r}", f"{sg['code']} {sg['name']}")
            b.set(s2, f"B{r}", "B2C")
            b.set(s2, f"C{r}", sg["src"])
            b.set(s2, f"D{r}", sg["pop"]); b.set(s2, f"E{r}", sg["k1"]); b.set(s2, f"G{r}", sg["k2"])
            b.set(s2, f"H{r}", sg["k3"]); b.set(s2, f"I{r}", sg["k4"])
            b.set(s2, f"K{r}", round(I.PRICE_BYN_YEAR_BASE, 2)); b.set(s2, f"L{r}", 1)
            b.set(s2, f"N{r}", sg["k5"]); b.set(s2, f"P{r}", sg["reliab"])
            b.set(s2, f"Q{r}", f"Тариф {sg['tariff']}. К1–К4 — допущения в диапазонах ПК табл. 7 (базовые значения), К5 — достижимая доля. Годовой чек 40 USD × 3,0285.")
        for r in range(7, 11):
            for col in "ABCDEGHIKLNPQ":
                b.ws(s2).Range(f"{col}{r}").ClearContents()
        b.set(s2, "A14", "Строка-гипотеза вне расчёта (решение В-6)")
        b.set(s2, "C14", "Расширение РФ/СНГ: Росстат и национальные статистики — 🔲 ДОСНЯТЬ; в итоговый диапазон не включается")

        s5 = "05_Similarweb"
        for i, (dom, name, typ, visits, status, rel, q) in enumerate(I.SW_DOMAINS):
            r = 4 + i
            b.set(s5, f"A{r}", name); b.set(s5, f"B{r}", "https://www.similarweb.com/website/" + dom + "/")
            b.set(s5, f"C{r}", typ); b.set(s5, f"D{r}", visits); b.set(s5, f"E{r}", round(I.GEO_BY, 6))
            b.set(s5, f"G{r}", rel); b.set(s5, f"H{r}", COMM)
            b.set(s5, f"J{r}", CR1); b.set(s5, f"K{r}", CR2); b.set(s5, f"L{r}", round(I.PRICE_BYN_YEAR_BASE, 2))
        for col in "ABCDEGHJKL":
            b.ws(s5).Range(f"{col}8").ClearContents()
        b.set(s5, "A14", "Визиты: plantuml.com — Similarweb, авг. 2026 (скриншот); остальные — отчёт ЛР1 и предварительный замер 17–23.09.2026 без скриншота (mermaidchart.com — верхняя граница «менее 20 тыс.»). Доля РБ — допущение Д-01. "
                         "Конверсии и чек — параметры NotaCode (CR1 — шаблон, CR2 = 4 % — проект, чек = цена Pro), поэтому результат — «выручка при параметрах NotaCode», а не фактическая выручка конкурентов. Выборка 4 домена < 5 — 🔲 ДОСНЯТЬ.")

        s7 = "07_Источники"
        rows = [
            ("Количество клиентов", "Студенты УВО РБ: 229,0 тыс.", "Белстат, «Образование в Республике Беларусь, 2026», табл. 7.1", "belstat.gov.by/upload/iblock/6af/m93v33ohm51kl00b333cmrhjbhj42ouo.pdf", "факт", "Высокая"),
            ("Количество клиентов", "Работники организаций цифровой экономики: 130 549 (2024)", "Белстат, digital_economy-2024.xls", "belstat.gov.by/upload-belstat/upload-belstat-excel/Oficial_statistika/2024/digital_economy-2024.xls", "факт", "Средняя"),
            ("Количество клиентов", "ППС вузов: 17,1 тыс.", "Белстат, «Образование в Республике Беларусь, 2026»", "там же", "факт", "Средняя"),
            ("К1 релевантность сегмента", "30 % / 30 % / 20 %", "Допущение в диапазоне ПК табл. 7 (20–40 %)", "🔲 разбивка студентов по профилям (Белстат / Минобразования)", "экспертное допущение", "Низкая"),
            ("К2 потребность", "22,5 %", "Допущение, середина диапазона ПК табл. 7 (15–30 %)", "🔲 опрос ≥20–30 респондентов; Вордстат", "экспертное допущение", "Низкая"),
            ("К3 цифровая доступность", "55 %", "Допущение, середина диапазона ПК табл. 7 (40–70 %); потолок — 94,3 % населения в интернете (Белстат 2024)", "belstat.gov.by", "экспертное допущение", "Низкая"),
            ("К4 готовность платить", "8,75 % / 17,5 % / 10 %", "Допущение в диапазонах ПК табл. 7 (5–10 % и 10–25 %); проектное Free → Pro 3–5 %", "🔲 опрос", "экспертное допущение", "Низкая"),
            ("Средний чек", "121,14 BYN/год", "Концепция NotaCode (годовой тариф 40 USD) × курс НБРБ 3,0285 (30.09.2026); альтернатива 48 USD (4 USD × 12) = 145,37 BYN", "api.nbrb.by/exrates/rates/431", "проектное допущение", "Средняя"),
            ("Similarweb", "Трафик домена-образца", "Similarweb, бесплатная карточка, август 2026 (plantuml.com)", "similarweb.com/website/plantuml.com/", "факт / оценка", "Средняя"),
            ("Доля географии", "0,1958 %", "Расчёт: 9,07 % (Россия, Similarweb) × 170/7874 (РБ/РФ, Вордстат, окно 29.08–27.09.2026)", "wordstat.yandex.ru; similarweb.com", "экспертное допущение", "Низкая"),
        ]
        for i, (a, bb, c, d, f, g) in enumerate(rows):
            r = 4 + i
            b.set(s7, f"A{r}", a); b.set(s7, f"B{r}", bb); b.set(s7, f"C{r}", c); b.set(s7, f"D{r}", d)
            b.set(s7, f"E{r}", D); b.set(s7, f"F{r}", f); b.set(s7, f"G{r}", g)
        b.recalc()
        sam_v, som_v = b.get("04_Расчет", "C7"), b.get("04_Расчет", "C8")
        fmt = lambda x: f"{x:,.0f}".replace(",", " ")
        b.set("06_Дашборд", "A20", f"По результатам оценки через количество потенциальных клиентов базовый доступный объем рынка составляет ориентировочно {fmt(sam_v)} BYN в год, а реалистично достижимый объем для нового бизнеса составляет {fmt(som_v)} BYN в год (по долям сегментов; по единой доле 2 % — {fmt(b.get('03_Сценарии', 'J5'))} BYN). Оценка является сценарной и требует проверки через фактические данные о клиентах, конкурентах, рекламных каналах, Similarweb, поисковом спросе и платежеспособности целевых сегментов.")
        res = {
            "tam_base": b.get("04_Расчет", "C4"), "in_bounds": b.get("04_Расчет", "C5"), "addressable": b.get("04_Расчет", "C6"),
            "sam": b.get("04_Расчет", "C7"), "som": b.get("04_Расчет", "C8"), "som_sam": b.get("04_Расчет", "C9"),
            "addr_share": b.get("04_Расчет", "C14"), "sam_per_client": b.get("04_Расчет", "C15"), "som_vs_sw": b.get("04_Расчет", "C16"),
            "scen": {n: [b.get("03_Сценарии", f"{c}{r}") for c in "HIJ"] for n, r in (("cautious", 4), ("base", 5), ("optimistic", 6))},
            "by_seg": [(b.get(s2, f"M{r}"), b.get(s2, f"O{r}"), b.get(s2, f"J{r}")) for r in (4, 5, 6)],
            "sw_year": b.get(s5, "N12"),
            "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_pk_excel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()


if __name__ == "__main__":
    main()
