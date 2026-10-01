# -*- coding: utf-8 -*-
"""Заполнение рабочей копии SW-X (объём рынка по Similarweb): исправление П-1, добавление листов
09_Концентрация (CR3/CR5/HHI, Р-42), 10_TAM_SAM_SOM_М1 (М1 табл. 22) и 11_Вариант_М2 (М2 табл. 9, 21)."""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
import fill_ps as P
from xl_com import Book

NAME = "SW_объем_рынка_Similarweb_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)
HERE = os.path.dirname(os.path.abspath(__file__))
import assumptions as AS
COVER_X = AS.SW_COVER
CR1_X = AS.SW_CR1
CR2 = I.CR_PRO
CHEQ = P.CHEQUE
BUY = AS.SW_BUY
SHARE = AS.SW_SHARE
COVER_M2 = AS.SW_COVER_M2
COMM_M2 = AS.SW_COMM_M2
CR1_M2 = AS.SW_CR1_M2
QUERIES = [  # запрос, тип намерения, вес (SW-X 05!F), сегмент, решение
    ("uml купить", "коммерческий", 1.0, "S-02/S-03", "включить"),
    ("visio купить", "коммерческий", 1.0, "S-02/S-03", "включить (конкурент)"),
    ("нейросеть схема", "инструментальный", 0.7, "все", "включить"),
    ("uml онлайн", "инструментальный", 0.7, "S-01/S-03", "включить"),
    ("plantuml online", "инструментальный", 0.7, "S-03", "включить"),
    ("idef0 как", "проблемный", 0.6, "S-01", "включить"),
    ("uml", "информационный", 0.1, "S-01", "исключить (не подтверждает платёжеспособный спрос)"),
]


def main():
    b = Book(NAME)
    try:
        s1, s2 = "01_Параметры", "02_Конкуренты_SW"
        b.set(s1, "B4", "Веб-инструменты построения и проверки диаграмм формальных нотаций (UML, BPMN, ERD, IDEF, DFD) для студентов и специалистов по ПО")
        b.set(s1, "B5", "Республика Беларусь")
        b.set(s1, "B6", "последние 3 месяца (июнь–август 2026); требование М1 «не менее 12 мес.» при бесплатном доступе невыполнимо")
        b.set(s1, "B7", D); b.set(s1, "B11", 0.7)
        b.set(s1, "D11", "Значение шаблона (базовый сценарий листа 06 — 0,7); шкала М2 табл. 9 для типовой ситуации 0,60–0,75")

        for r in range(4, 24):                      # удалить демонстрационные значения шаблона
            for col in "ABCDEFJKLMNOPQRS":
                b.ws(s2).Range(f"{col}{r}").ClearContents()
        for i, (dom, name, typ, visits, status, rel, q) in enumerate(I.SW_DOMAINS):
            r = 4 + i
            b.set(s2, f"A{r}", dom); b.set(s2, f"B{r}", name)
            b.set(s2, f"C{r}", "диаграммы по тексту" if "DSL" in typ or "AI" in typ else "визуальные редакторы")
            b.set(s2, f"D{r}", typ.split(" (")[0])
            b.set(s2, f"E{r}", visits); b.set(s2, f"F{r}", round(I.GEO_BY, 6))
            if dom == "plantuml.com":
                b.set(s2, f"J{r}", 0.4552); b.set(s2, f"K{r}", 3.18); b.set(s2, f"L{r}", "00:03:16"); b.set(s2, f"N{r}", 0.4847)
            b.set(s2, f"S{r}", f"{status}. Доля РБ — допущение Д-01 (Similarweb не показывает). Каналы: бесплатная карточка показывает только Organic (plantuml.com); остальные — «нет данных в бесплатном доступе».")
        b.set(s2, "A27", "Каналы: у plantuml.com показана только доля Organic Search 48,47 %; Direct и Referrals названы 2-м и 3-м без долей, Social, Paid, Mail, Display бесплатная карточка не показывает. "
                         "Средневзвешенные доли каналов (строка 25) в копии считаются только по строкам, где доля показана (П-18).")
        # П-18: средневзвешенные доли каналов делятся на сумму G по строкам с данными
        for col in "MNOPQR":
            b.formula(s2, f"{col}25", f'=IFERROR(SUMPRODUCT($G$4:$G$23,{col}4:{col}23)/SUMIF({col}4:{col}23,">0",$G$4:$G$23),0)')

        # П-1: значение до и после исправления
        b.recalc()
        before = sum(b.get(s2, f"G{r}") for r in range(5, 25)) if False else sum(b.get(s2, f"G{r}") for r in range(5, 8))
        b.formula(s1, "B9", "=SUM('02_Конкуренты_SW'!G4:G23)")
        b.formula(s1, "B10", "=SUM('02_Конкуренты_SW'!H4:H23)")
        b.set(s1, "D9", "Исправлено в рабочей копии (П-1): суммирование с 4-й строки; в шаблоне диапазон G5:G24 терял первого конкурента.")
        b.set(s1, "D10", "Исправлено (П-1): H4:H23.")
        b.recalc()
        after = b.get(s1, "B9")

        # 03_Каналы, 04_География, 05_Запросы
        s3, s4, s5 = "03_Каналы", "04_География", "05_Запросы"
        for r in range(4, 10):
            b.set(s3, f"E{r}", b.get(s3, f"E{r}"))
        for r in (4, 6, 7, 8, 9):
            b.set(s3, f"H{r}", "нет данных")
        b.set(s3, "A11", "Показан только Organic (plantuml.com); остальные доли — «нет данных в бесплатном доступе»; приоритет по каналам, кроме Organic, не определяется.")
        geo = [("Республика Беларусь", I.GEO_BY, "средняя", "средняя", "Основная география (В-6). Доля — допущение Д-01"),
               ("Минск (город)", I.GEO_MINSK, "выше средней", "высокая", "Вордстат, plantuml: Минск 124 из 170 запросов РБ (73 %), окно 29.08–27.09.2026"),
               ("Остальная Беларусь (включая областные центры)", I.GEO_BY - I.GEO_MINSK, "средняя", "средняя", "Разница; данных по областным центрам нет"),
               ("Россия (другие русскоязычные рынки)", I.SW_RUSSIA_SHARE_PLANTUML, "разная", "высокая", "Similarweb, plantuml.com, август 2026: 9,07 % (факт); гипотеза расширения, вне итогового диапазона (В-6)")]
        for i, (a, v, e, f, h) in enumerate(geo):
            r = 4 + i
            b.set(s4, f"A{r}", a); b.set(s4, f"B{r}", round(v, 6)); b.set(s4, f"E{r}", e); b.set(s4, f"F{r}", f); b.set(s4, f"H{r}", h)
            # корректный вариант (П-10): доля × трафик до географического сужения
            b.formula(s4, f"I{r}", f"=B{r}*SUM('02_Конкуренты_SW'!$E$4:$E$23)/'01_Параметры'!$B$11")
            b.formula(s4, f"J{r}", f"=I{r}*12")
        b.set(s4, "I3", "Корректно (П-10): трафик до географического сужения × доля, мес."); b.set(s4, "J3", "Корректно, год")
        b.set(s4, "A9", "В шаблоне (столбцы C, D) доля умножается на B12 — трафик, уже суженный до Беларуси (П-10); корректный вариант — столбцы I, J.")

        tot = sum(q[1] for q in [(x, I.WS_ALL[x[0]]["top"]) for x in QUERIES])
        for i, (q, typ, w, seg, dec) in enumerate(QUERIES):
            r = 4 + i
            b.set(s5, f"A{r}", q); b.set(s5, f"B{r}", "Яндекс Вордстат (РБ, Топы, 30 дней)")
            b.set(s5, f"C{r}", round(I.WS_ALL[q]["top"] / tot, 4)); b.set(s5, f"E{r}", typ); b.set(s5, f"F{r}", w)
            b.set(s5, f"H{r}", seg); b.set(s5, f"I{r}", dec)
            b.set(s5, f"J{r}", f"Частотность {I.WS_ALL[q]['top']} запр./мес.; доля — среди перечисленных запросов (Similarweb долей запросов в бесплатном доступе не показывает)")
            b.formula(s5, f"K{r}", f"=D{r}*'03_Каналы'!$B$5")
        b.set(s5, "K3", "Корректно (П-11): D × доля Organic")
        b.set(s5, "A12", "Столбец D в шаблоне = доля × трафик всего рынка (П-11), что вероятно завышает поисковую часть; в столбце K — умножение на долю Organic (48,47 %, plantuml.com). Веса намерений SW-X (проблемный 0,6–0,8, информационный 0,1) отличаются от ПС табл. 9 (проблемный 0,30–0,60) — Р-44.")

        # 06_Воронка_сценарии
        s6 = "06_Воронка_сценарии"
        for j, r in enumerate((5, 6, 7)):
            b.set(s6, f"B{r}", COVER_X[j]); b.set(s6, f"D{r}", CR1_X[j]); b.set(s6, f"E{r}", CR2[j])
            b.set(s6, f"F{r}", CHEQ[j]); b.set(s6, f"G{r}", BUY[j]); b.set(s6, f"C{12 + j}", SHARE[j])

        # 08_Источники: журнал ручного сбора
        s8 = "08_Источники"
        for r in range(4, 10):
            b.set(s8, f"E{r}", D)
        jr = [
            (D, "plantuml.com", "Overview", "Total visits (август 2026)", 507000, "скриншот similarweb_traffic_plantuml.com_global_last3months_2026-09-30.png"),
            (D, "plantuml.com", "Overview", "Global Rank", 93517, "ранг; Country Rank #24 334 (Россия); Category Rank #692"),
            (D, "plantuml.com", "Geography", "Доля России в трафике", 0.0907, "Беларусь в топ-5 стран не показана: нет данных в бесплатном доступе"),
            (D, "plantuml.com", "Marketing Channels", "Organic Search", 0.4847, "Direct и Referrals — 2-е и 3-е места без долей"),
            (D, "plantuml.com", "Engagement", "Bounce rate", 0.4552, "Pages/visit 3,18; Avg duration 00:03:16"),
            (D, "app.diagrams.net", "Overview", "Total visits", "доступ закрыт", "лимит бесплатных просмотров (скриншот ...global_limit_2026-09-30.png); значение 7,8 млн — из выгрузки ЛР1"),
            (D, "mermaid.live", "Overview", "Total visits", "доступ закрыт", "лимит бесплатных просмотров"),
            (D, "lucidchart.com", "Overview", "Total visits", "доступ закрыт", "лимит бесплатных просмотров; 🔲 ДОСНЯТЬ: Similarweb, страница lucidchart.com, снимок экрана (вручную, по странице источника; табл. 91, п. 1)"),
        ]
        for i, row in enumerate(jr):
            for col, v in zip("ABCDEF", row):
                b.set(s8, f"{col}{14 + i}", v)
        b.set(s8, "A24", "Значения eraser.io (678,5 тыс.), app.diagrams.net (7,8 млн), mermaidchart.com (< 20 тыс.) указаны без скриншота (app.diagrams.net — по отчёту ЛР1, остальные — предварительный замер 17–23.09.2026); повторный замер 30.09.2026 невозможен (лимит). 🔲 ДОСНЯТЬ минимум ещё 6 доменов.")

        # --- новые листы ---
        wb = b.wb
        for nm in [w.Name for w in wb.Worksheets]:
            if nm[:2] in ("09", "10", "11") and nm not in ("09_Источники",) or nm.startswith("Лист"):
                wb.Worksheets(nm).Delete()
        last = wb.Worksheets(wb.Worksheets.Count)
        ws9 = wb.Worksheets.Add(After=last); ws9.Name = "09_Концентрация"
        ws10 = wb.Worksheets.Add(After=ws9); ws10.Name = "10_TAM_SAM_SOM_М1"
        ws11 = wb.Worksheets.Add(After=ws10); ws11.Name = "11_Вариант_М2"

        def put(ws, addr, v):
            ws.Range(addr).Value = v

        def fml(ws, addr, f):
            ws.Range(addr).Formula = f

        # 09_Концентрация
        put(ws9, "A1", "Концентрация цифрового трафика: CR3, CR5, HHI (дополнение к шаблону, Р-42; М1 §7.2, М2 §12)")
        heads = ["Домен", "Визиты/мес. (сырые)", "Доля по сырым визитам (М1 ф. 2, SWБ §7)", "Доля² × 10 000 (сырые)",
                 "Релевантные визиты (РБ)", "Доля по релевантным визитам (М2 §7)", "Доля² × 10 000 (релевантные)"]
        for j, h in enumerate(heads):
            put(ws9, f"{chr(65 + j)}3", h)
        n = len(I.SW_DOMAINS)
        for i in range(n):
            r = 4 + i
            fml(ws9, f"A{r}", f"='02_Конкуренты_SW'!A{4 + i}")
            fml(ws9, f"B{r}", f"='02_Конкуренты_SW'!E{4 + i}")
            fml(ws9, f"C{r}", f"=B{r}/SUM($B$4:$B${3 + n})")
            fml(ws9, f"D{r}", f"=C{r}^2*10000")
            fml(ws9, f"E{r}", f"='02_Конкуренты_SW'!G{4 + i}")
            fml(ws9, f"F{r}", f"=E{r}/SUM($E$4:$E${3 + n})")
            fml(ws9, f"G{r}", f"=F{r}^2*10000")
        for j, h in enumerate(["Доля релевантного трафика (Д-02)", "Релевантные визиты с учётом Д-02", "Доля по визитам с учётом Д-02", "Доля² × 10 000 (с учётом Д-02)"]):
            put(ws9, f"{chr(72 + j)}3", h)
        for i in range(n):
            r = 4 + i
            put(ws9, f"H{r}", I.SW_DOMAINS[i][5])
            fml(ws9, f"I{r}", f"=E{r}*H{r}")
            fml(ws9, f"J{r}", f"=I{r}/SUM($I$4:$I${3 + n})")
            fml(ws9, f"K{r}", f"=J{r}^2*10000")
        r0 = 4 + n + 1
        fml(ws9, f"I{r0}", f"=SUM(I4:I{3 + n})"); fml(ws9, f"K{r0}", f"=SUM(K4:K{3 + n})")
        rows = [("Сумма", f"=SUM(B4:B{3 + n})", None, f"=SUM(D4:D{3 + n})", f"=SUM(E4:E{3 + n})", None, f"=SUM(G4:G{3 + n})")]
        for j, v in enumerate(rows[0]):
            if v:
                fml(ws9, f"{chr(65 + j)}{r0}", v) if str(v).startswith("=") else put(ws9, f"{chr(65 + j)}{r0}", v)
        q = r0 + 2
        put(ws9, f"A{q}", "Показатель"); put(ws9, f"B{q}", "По сырым визитам"); put(ws9, f"C{q}", "По релевантным визитам"); put(ws9, f"D{q}", "С учётом доли релевантного (Д-02)")
        fml(ws9, f"D{q + 1}", f"=(LARGE(J4:J{3 + n},1)+LARGE(J4:J{3 + n},2)+LARGE(J4:J{3 + n},3))*100")
        fml(ws9, f"D{q + 2}", f"=SUM(J4:J{3 + n})*100"); fml(ws9, f"D{q + 3}", f"=K{r0}")
        fml(ws9, f"D{q + 4}", f'=IF(D{q + 3}<1500,"низкая концентрация",IF(D{q + 3}<=2500,"умеренная","высокая"))')
        fml(ws9, f"D{q + 5}", f'=IF(D{q + 3}>=D{q + 1}^2/3,"выполняется","НЕ выполняется")')
        put(ws9, f"A{q + 1}", "CR3, %")
        fml(ws9, f"B{q + 1}", f"=(LARGE(C4:C{3 + n},1)+LARGE(C4:C{3 + n},2)+LARGE(C4:C{3 + n},3))*100")
        fml(ws9, f"C{q + 1}", f"=(LARGE(F4:F{3 + n},1)+LARGE(F4:F{3 + n},2)+LARGE(F4:F{3 + n},3))*100")
        put(ws9, f"A{q + 2}", "CR5, %")
        fml(ws9, f"B{q + 2}", f"=SUM(C4:C{3 + n})*100"); fml(ws9, f"C{q + 2}", f"=SUM(F4:F{3 + n})*100")
        put(ws9, f"A{q + 3}", "HHI = Σ (доля в %)²")
        fml(ws9, f"B{q + 3}", f"=D{r0}"); fml(ws9, f"C{q + 3}", f"=G{r0}")
        put(ws9, f"A{q + 4}", "Уровень по шкале М2 табл. 16")
        for col in "BC":
            fml(ws9, f"{col}{q + 4}", f'=IF({col}{q + 3}<1500,"низкая концентрация",IF({col}{q + 3}<=2500,"умеренная","высокая"))')
        put(ws9, f"A{q + 5}", "Проверка: HHI ≥ CR3² / 3")
        for col in "BC":
            fml(ws9, f"{col}{q + 5}", f'=IF({col}{q + 3}>={col}{q + 1}^2/3,"выполняется","НЕ выполняется")')
        put(ws9, f"A{q + 7}", "Пояснения: шкала М2 табл. 16 — до 1 500 низкая, 1 500–2 500 умеренная, выше 2 500 высокая; М1 табл. 10 задаёт три качественных уровня без чисел. "
                               "Значения — оценка концентрации ЦИФРОВОГО ТРАФИКА выборки из 4 доменов (не выручки и не рыночной власти); CR5 при 4 доменах равен 100 %. "
                               "Выборка меньше минимума М2 (5 доменов) и состоит из доменов разных типов; доминирует универсальный редактор draw.io.")

        # 10_TAM_SAM_SOM_М1
        put(ws10, "A1", "TAM / SAM / SOM цифрового внимания по М1 табл. 22 (базовый сценарий листа 06)")
        lines = [
            ("TAM цифрового внимания: суммарный трафик релевантных сайтов категории, визиты/мес.", "=SUM('02_Конкуренты_SW'!E4:E23)"),
            ("Доля страны (Беларусь), допущение Д-01", "='02_Конкуренты_SW'!F4"),
            ("SAM по географии, визиты/мес. = TAM × доля страны", "=B3*B4"),
            ("Доля релевантных каналов (Organic Search, plantuml.com)", "='03_Каналы'!B5"),
            ("SAM по каналу, визиты/мес.", "=B5*B6"),
            ("Достижимая доля (базовая, лист 06)", "='06_Воронка_сценарии'!C13"),
            ("SOM по трафику, визиты/мес. = SAM × достижимая доля", "=B7*B8"),
            ("CR1 (лист 06, базовый)", "='06_Воронка_сценарии'!D6"),
            ("CR2 (лист 06, базовый)", "='06_Воронка_сценарии'!E6"),
            ("Средний чек, BYN (лист 06)", "='06_Воронка_сценарии'!F6"),
            ("Число покупок в год", "='06_Воронка_сценарии'!G6"),
            ("SOM по выручке, BYN/год = SOM по трафику × 12 × CR1 × CR2 × чек × число покупок", "=B9*12*B10*B11*B12*B13"),
            ("Проверка конкурентами: средняя выручка конкурента (при параметрах NotaCode), BYN/год", "=AVERAGE('02_Конкуренты_SW'!G4:G7)*12*B10*B11*B12*B13"),
            ("Число активных конкурентов в выборке", "='01_Параметры'!B8"),
            ("Проверка конкурентами: сумма, BYN/год", "=B15*B16"),
        ]
        for i, (t, f) in enumerate(lines):
            put(ws10, f"A{3 + i - 1}", t) if False else None
        for i, (t, f) in enumerate(lines):
            r = 3 + i
            put(ws10, f"A{r}", t); fml(ws10, f"B{r}", f)
        put(ws10, "A20", "Канальный SAM рассчитан по доле Organic одного домена (plantuml.com) — остальные доли в бесплатном доступе не показаны. Проверка поиском — лист 05_Запросы.")

        # 11_Вариант_М2
        put(ws11, "A1", "Вариант по М2 (табл. 9, 11, 21): охват 0,45 / 0,65 / 0,85; коммерчески релевантная доля 20 / 35 / 50 %; годовой объём = месячный × 12")
        for j, h in enumerate(["Показатель", "Осторожный", "Базовый", "Оптимистичный", "Комментарий"]):
            put(ws11, f"{chr(65 + j)}3", h)
        rows = [
            ("V_sample: визиты выборки, мес. (Σ)", ["=SUM('02_Конкуренты_SW'!E4:E23)"] * 3, "М2 табл. 8"),
            ("Доля географии (РБ), Д-01", ["='02_Конкуренты_SW'!F4"] * 3, ""),
            ("V_geo = V_sample × доля географии", ["=B4*B5", "=C4*C5", "=D4*D5"], ""),
            ("Коэффициент охвата выборки", list(COVER_M2), "М2 табл. 21 (шкала табл. 9: 0,40–0,55 / 0,60–0,75 / 0,80–0,90)"),
            ("V_total = V_geo / охват", ["=B6/B7", "=C6/C7", "=D6/D7"], "Осторожный сценарий даёт БОЛЬШЕ трафика (W-15)"),
            ("Коммерчески релевантная доля", list(COMM_M2), "М2 табл. 21"),
            ("Коммерчески релевантные визиты, мес.", ["=B8*B9", "=C8*C9", "=D8*D9"], ""),
            ("CR1 (визит → заявка)", list(CR1_M2), "середины диапазонов М2 табл. 11"),
            ("CR2 (заявка → оплата Pro)", list(CR2), "допущение проекта Free → Pro 3–5 % (шкала М2 5–40 % для freemium неприменима)"),
            ("Средний чек, BYN/год", list(CHEQ), "40 USD/год (осторожный, базовый); медиана входных тарифов конкурентов"),
            ("Месячный объём, BYN", ["=B10*B11*B12*B13", "=C10*C11*C12*C13", "=D10*D11*D12*D13"], ""),
            ("Годовой объём, BYN (× 12, М2)", ["=B14*12", "=C14*12", "=D14*12"], "М2: × 12 (в SW-X: × 12 × покупок)"),
            ("Достижимая доля (SOM)", list(SHARE), "как в листе 06"),
            ("SOM, BYN/год", ["=B15*B16", "=C15*C16", "=D15*D16"], ""),
        ]
        for i, (t, vals, cm) in enumerate(rows):
            r = 4 + i
            put(ws11, f"A{r}", t)
            for col, v in zip("BCD", vals):
                if isinstance(v, str):
                    fml(ws11, f"{col}{r}", v)
                else:
                    put(ws11, f"{col}{r}", v)
            put(ws11, f"E{r}", cm)
        for ws in (ws9, ws10, ws11):
            ws.Columns("A").ColumnWidth = 60
            ws.Columns("B:G").ColumnWidth = 22

        b.recalc()
        res = {
            "p1_before": before, "p1_after": after,
            "observed_month": b.get(s1, "B9"), "market_traffic_month": b.get(s1, "B12"),
            "market_year": [b.get(s6, f"J{r}") for r in (5, 6, 7)], "som": [b.get(s6, f"D{r}") for r in (12, 13, 14)],
            "orders": [b.get(s6, f"H{r}") for r in (5, 6, 7)],
            "hhi_raw": b.get("09_Концентрация", f"B{q + 3}"), "hhi_rel": b.get("09_Концентрация", f"C{q + 3}"),
            "cr3_raw": b.get("09_Концентрация", f"B{q + 1}"), "cr3_rel": b.get("09_Концентрация", f"C{q + 1}"),
            "hhi_level": [b.get("09_Концентрация", f"{c}{q + 4}") for c in "BCD"], "hhi_check": [b.get("09_Концентрация", f"{c}{q + 5}") for c in "BCD"], "hhi_rel2": b.get("09_Концентрация", f"D{q + 3}"), "cr3_rel2": b.get("09_Концентрация", f"D{q + 1}"), "q_row": q,
            "m1_som_rev": b.get("10_TAM_SAM_SOM_М1", "B14"), "m1_som_traffic": b.get("10_TAM_SAM_SOM_М1", "B9"),
            "m1_tam": b.get("10_TAM_SAM_SOM_М1", "B3"), "m1_sam_geo": b.get("10_TAM_SAM_SOM_М1", "B5"),
            "m2_year": [b.get("11_Вариант_М2", f"{c}15") for c in "BCD"], "m2_som": [b.get("11_Вариант_М2", f"{c}17") for c in "BCD"],
            "m2_vtotal": [b.get("11_Вариант_М2", f"{c}8") for c in "BCD"],
            "channels": [(b.get(s3, f"A{r}"), b.get(s3, f"B{r}"), b.get(s3, f"H{r}")) for r in range(4, 10)],
            "geo_fix": [(b.get(s4, f"C{r}"), b.get(s4, f"I{r}")) for r in range(4, 8)],
            "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(HERE, "out_sw_excel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()


if __name__ == "__main__":
    main()
