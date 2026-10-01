# -*- coding: utf-8 -*-
"""Заполнение рабочей копии ПС-X (оценка рынка через поисковый спрос) через Excel COM и проверка пересчёта."""
import datetime
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from xl_com import Book

NAME = "ПС_поисковый_спрос_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)

# сценарные параметры воронки (осторожный, базовый, оптимистичный)
import assumptions as AS
CTR = AS.PS_CTR
CR1 = AS.PS_CR1
CR2 = I.CR_PRO                  # проект: Free -> Pro 3-5 % (вне шкалы ПС 10-50 %, см. журнал допущений)
CHEQUE = (round(I.PRICE_BYN_YEAR_DISC, 2), round(I.PRICE_BYN_YEAR_BASE, 2),
          round(sorted(I.ENTRY_PRICES.values())[len(I.ENTRY_PRICES) // 2] * 12 * I.FX, 2))
REPEAT = AS.REPEAT
CTR_W = AS.PS_CTR_W
CR1_W = AS.PS_CR1_W
CR2_W = CR2                     # для freemium шкала ПС 10-50 % неприменима; в чувствительности - отдельно
REGION_K = AS.REGION_K


def main():
    b = Book(NAME)
    try:
        s1 = "01_Параметры"
        b.set(s1, "B4", "Республика Беларусь")
        b.set(s1, "B5", "сентябрь 2025 – август 2026 (12 мес.)")
        b.set(s1, "B6", round(I.PRICE_BYN_YEAR_BASE, 2))
        b.set(s1, "C6", "BYN/год")
        b.set(s1, "D6", "Годовой чек Pro: 40 USD × курс НБРБ 3,0285 (30.09.2026). Альтернатива 4 USD × 12 = 48 USD/год — 145,37 BYN.")
        b.set(s1, "B7", CTR[1]); b.set(s1, "D7", "Базовое значение шкалы ПС табл. 17 (5–8 %).")
        b.set(s1, "B8", CR1[1]); b.set(s1, "D8", "Посетитель → регистрация (заявка). ПС табл. 17: 3–5 %.")
        b.set(s1, "B9", CR2[1]); b.set(s1, "D9", "Регистрация → оплата Pro. Допущение проекта (концепция NotaCode: Free → Pro 3–5 %); шкала ПС 25–35 % для freemium неприменима.")
        b.set(s1, "B10", REPEAT[1]); b.set(s1, "D10", "Среднее число годовых оплат на платящего пользователя; шкала шаблона, срок удержания — допущение проекта (🔲 данных нет).")
        b.set(s1, "D11", "В расчёте 05_Нормализация; механическое сложение GT и Вордстат запрещено ПС §3 — показан для сравнения (см. отчёт).")
        b.set(s1, "D13", "Не используется формулами (особенность шаблона П-13).")

        # 02_Семантика
        s2 = "02_Семантика"
        for i, (q, grp, intent, reg, freq, gt, rel, comm) in enumerate(I.SEMANTICS):
            r = 4 + i
            b.set(s2, f"A{r}", i + 1)
            b.set(s2, f"B{r}", q)
            b.set(s2, f"C{r}", grp)
            b.set(s2, f"D{r}", intent)
            b.set(s2, f"E{r}", reg)
            b.set(s2, f"F{r}", freq)
            if gt is None:
                b.set(s2, f"G{r}", 14.52)      # GT UML, 12 мес. (ЛР1, недельный ряд, среднее)
            else:
                b.set(s2, f"G{r}", gt)
            b.set(s2, f"H{r}", rel)
            b.set(s2, f"I{r}", comm)
        b.set(s2, "A15", "Примечание")
        b.set(s2, "B15", "Частотность — Яндекс Вордстат, Беларусь, «Топы запросов», 25.08–23.09.2026, все устройства. "
                         "GT-индекс: н/д = недостаточно данных по Беларуси; у «uml» — среднее недельного ряда за 12 мес. по данным ЛР1. "
                         "«mermaid» без уточнения — омоним (фильм «Русалочка»), вес 0,00 по ПС табл. 9 (особенность шаблона П-14).")

        # 03_Google_Trends
        s3 = "03_Google_Trends"
        for j, name in enumerate(["UML", "BPMN", "PlantUML", "IDEF0"]):
            b.set(s3, f"{'BCDE'[j]}3", name)
        for i, ((y, m), vals) in enumerate(zip(I.MONTHS_12, I.GT_MONTHLY)):
            r = 4 + i
            b.set(s3, f"A{r}", datetime.datetime(y, m, 1))
            for j, v in enumerate(vals):
                b.set(s3, f"{'BCDE'[j]}{r}", v)
            b.set(s3, f"G{r}", "все значения 0: недостаточно данных Google Trends по Беларуси" if sum(vals) == 0 else "")
        b.set(s3, "A17", "Источник: Google Trends, Беларусь, today 12-m, категория «все», веб-поиск, один запрос из 4 терминов (единая шкала); "
                         "недельные значения усреднены по месяцам (по дате начала недели). Выгрузка 30.09.2026.")

        # 04_Wordstat
        s4 = "04_Wordstat"
        groups = list(I.GROUP_SERIES)
        for i, (y, m) in enumerate(I.MONTHS_12):
            r = 4 + i
            b.set(s4, f"A{r}", datetime.datetime(y, m, 1))
            for j, g in enumerate(groups):
                b.set(s4, f"{'BCDE'[j]}{r}", I.GROUP_SERIES[g][i])
            b.formula(s4, f"G{r}", f"=IF(F{r}=0,0,(B{r}*$L$4+C{r}*$L$5+D{r}*$L$6+E{r}*$L$7)/F{r})")
        b.set(s4, "K3", "Вес намерения"); b.set(s4, "L3", "ПС табл. 9")
        for j, g in enumerate(groups):
            b.set(s4, f"K{4 + j}", g)
            b.set(s4, f"L{4 + j}", I.INTENT_WEIGHT[g])
        b.set(s4, "K8", "Коммерческий коэффициент (столбец G) — средневзвешенный вес намерения по составу месяца.")
        b.set(s4, "A17", "Источник: Яндекс Вордстат, Беларусь (id=149), все устройства, вкладка «Динамика», месячные значения; "
                         "групповой ряд — сумма рядов отдельных формулировок (операторы группировки в «Динамике» не поддерживаются). "
                         "Состав групп и учёт пересечений — в отчёте. Локальные запросы: ряд ниже порога отображения (Топы: uml минск 3, bpmn минск 4 за 30 дней).")

        # 06_Воронка
        s6 = "06_Воронка"
        for j, col in enumerate("BCD"):
            b.set(s6, f"{col}5", CTR[j]); b.set(s6, f"{col}7", CR1[j]); b.set(s6, f"{col}9", CR2[j])
            b.set(s6, f"{col}11", CHEQUE[j]); b.set(s6, f"{col}12", REPEAT[j])
        b.set(s6, "E9", "Регистрация → оплата Pro: допущение проекта 3–5 % (вне шкалы ПС 10–50 %).")
        b.set(s6, "E11", "Годовой чек Pro, BYN: 40 USD/год (осторожный и базовый); медиана входных платных тарифов конкурентов (8 USD/мес. × 12).")
        b.set(s6, "E12", "Число годовых оплат на платящего; шкала шаблона (1 / 1,2 / 1,5), срок удержания — допущение.")

        # 09_Источники
        s9 = "09_Источники"
        b.set(s9, "C4", "Беларусь; 12 мес. (сент. 2025 – авг. 2026)"); b.set(s9, "C6", "Беларусь (id=149); 24 мес. и 30 дней")
        for r in (4, 5, 6, 7):
            b.set(s9, f"D{r}", D)
        b.set(s9, "E8", "🔲 ДОСНЯТЬ: Google Ads Keyword Planner / Яндекс Директ (прогноз показов и CPC) — нужны рекламные кабинеты (нужен доступ)")
        b.set(s9, "E9", "Собственной аналитики нет (MVP не запущен): конверсии — допущение проекта (концепция NotaCode: Free → Pro 3–5 %)")
        extra = [
            ("Курс НБРБ USD/BYN", "3,0285 BYN за 1 USD", "30.09.2026", "https://api.nbrb.by/exrates/rates/431"),
            ("Концепция NotaCode", "Цена Pro 40 USD/год (помесячно 4 USD); конверсия Free → Pro 3–5 % (гипотеза A-06)", "30.09.2026", "документ проекта (концепция, раздел 6)"),
            ("Тарифы конкурентов", "Входные платные тарифы, медиана 8 USD/мес. при оплате за год", "30.09.2026", "страницы тарифов Miro, Lucidchart, Mermaid Chart и др."),
        ]
        for i, (a, bb, c, d) in enumerate(extra):
            r = 10 + i
            b.set(s9, f"A{r}", a); b.set(s9, f"B{r}", bb); b.set(s9, f"C{r}", "—"); b.set(s9, f"D{r}", D); b.set(s9, f"E{r}", d)

        b.recalc()
        res = {
            "F_mean_weighted": b.get("06_Воронка", "C4"),
            "visits": [b.get(s6, f"{c}6") for c in "BCD"],
            "leads": [b.get(s6, f"{c}8") for c in "BCD"],
            "sales": [b.get(s6, f"{c}10") for c in "BCD"],
            "rev_month": [b.get(s6, f"{c}13") for c in "BCD"],
            "rev_year": [b.get(s6, f"{c}14") for c in "BCD"],
            "index_mean": b.get("08_Дашборд", "B4"), "index_max": b.get("08_Дашборд", "B5"),
            "weighted_mean": b.get("08_Дашборд", "B6"),
            "range_text": b.text("08_Дашборд", "B9"), "level": b.get("08_Дашборд", "B10"),
            "sumJ": sum(b.get(s2, f"J{r}") for r in range(4, 14)),
            "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_ps_excel.json"), "w", encoding="utf-8"),
                  ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()


if __name__ == "__main__":
    main()
