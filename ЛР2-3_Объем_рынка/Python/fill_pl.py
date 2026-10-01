# -*- coding: utf-8 -*-
"""Заполнение рабочей копии ПЛ-X (проверка рынка через платёжеспособность)."""
import datetime
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from assumptions import A
from xl_com import Book

NAME = "ПЛ_платежеспособность_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)
import assumptions as AS
HOURS, WORK_H = AS.HOURS, AS.WORK_H
CR1 = AS.SV_CR1
CR2 = I.CR_PRO[1]


def corridor():
    rows = []
    for prod in ["Miro", "Lucidchart", "Mermaid Chart", "Visual Paradigm Online", "Creately", "Eraser", "Whimsical", "dbdiagram.io"]:
        ps = [p[2] for p in I.PRICES if p[0] == prod]
        rows.append((prod, min(ps) * I.FX, statistics.median(ps) * I.FX, max(ps) * I.FX, [p[1] for p in I.PRICES if p[0] == prod]))
    return rows


def main():
    b = Book(NAME)
    try:
        s1 = "01_Параметры"
        b.set(s1, "B5", "NotaCode — веб-IDE для построения и проверки диаграмм формальных нотаций как текста (подписка Free / Pro)")
        b.set(s1, "B6", "Республика Беларусь")
        b.set(s1, "B9", CR2); b.set(s1, "C9", "Доля регистраций, оплативших Pro: допущение проекта Free → Pro 3–5 % (базовое 4 %); формулами не используется (П-13)")
        b.set(s1, "B10", 1.0); b.set(s1, "C10", "Бюджет / цена ≥ 1 — покупка возможна; ниже 1 — затруднена (формулами не используется)")
        b.set(s1, "B11", "🔲"); b.set(s1, "C11", "Себестоимость обслуживания пользователя в концепции не определена — 🔲 (формулами не используется)")
        b.set(s1, "B12", D)

        # 02_Сегменты: B = клиентов в границах рынка (К1), C = К2, D = К3, E = К4; F = 1 оплата в год; G = годовой чек
        s2 = "02_Сегменты"
        for i, sg in enumerate(I.SEGMENTS):
            r = 5 + i
            b.set(s2, f"A{r}", f"{sg['code']} {sg['name']}")
            b.set(s2, f"B{r}", round(sg["pop"] * sg["k1"]))
            b.set(s2, f"C{r}", sg["k2"]); b.set(s2, f"D{r}", sg["k3"]); b.set(s2, f"E{r}", sg["k4"])
            b.set(s2, f"F{r}", 1); b.set(s2, f"G{r}", round(I.PRICE_BYN_YEAR_BASE, 2))
            b.set(s2, f"K{r}", f"Тариф: {sg['tariff']}. Клиенты в границах = численность {sg['pop']:,} × К1 {sg['k1']}".replace(",", " "))
            b.set(s2, f"L{r}", sg["src"])
        for r in range(8, 15):
            for col in "ABCDEFGKL":
                b.ws(s2).Range(f"{col}{r}").ClearContents()
        b.set(s2, "A18", "Примечание")
        b.set(s2, "B18", "Годовой чек 40 USD (решение В-5; альтернатива 48 USD = 4 USD × 12), в BYN по курсу НБРБ 3,0285 (30.09.2026); число оплат в год = 1 (годовой тариф). "
                         "Доля платёжеспособных (E) совмещает финансовую возможность и готовность платить (К4 по ПК табл. 7). Строки ниже S-04 не используются (П-5).")

        # 03_Ценовой_коридор
        s3 = "03_Ценовой_коридор"
        cor = corridor()
        for i, (prod, mn, md, mx, tiers) in enumerate(cor):
            r = 5 + i
            b.set(s3, f"A{r}", prod + " (платные тарифы, BYN/мес.)")
            b.set(s3, f"B{r}", round(mn, 2)); b.set(s3, f"C{r}", round(md, 2)); b.set(s3, f"D{r}", round(mx, 2))
            b.ws(s3).Range(f"E{r}").ClearContents()
            b.formula(s3, f"F{r}", f'=IF(OR(A{r}="",E{r}=""),"нет данных",(G{r}-E{r})/G{r})')
            b.set(s3, f"I{r}", "Тарифы: " + ", ".join(tiers) + "; оплата за год, USD × 3,0285")
            b.set(s3, f"J{r}", "Страница тарифов продукта, 30.09.2026")
        for r in range(13, 13):
            pass
        b.set(s3, "A16", "Справочно (в среднее не входят)")
        ref = [("NotaCode Pro", round(I.PRICE_BYN_MONTH, 2), "годовой тариф 40 USD = 10,10 BYN/мес.; помесячно 4 USD = 12,11 BYN"),
               ("Microsoft Visio Plan 1 / Plan 2", f"{5 * I.FX:.2f} / {15 * I.FX:.2f}", "5 и 15 USD/мес. за пользователя"),
               ("draw.io, PlantUML", 0, "бесплатные заменители (цена заменителя = 0)")]
        for i, (a, v, n) in enumerate(ref):
            b.set(s3, f"A{17 + i}", a); b.set(s3, f"C{17 + i}", v); b.set(s3, f"I{17 + i}", n)
        b.set(s3, "A21", "Себестоимость (столбец E) у конкурентов не публикуется — нет данных; формула валовой маржи в копии возвращает «нет данных» (в шаблоне при пустой ячейке давала 100 %). "
                         "Индекс доступности цены H всегда равен 1 (особенность шаблона П-3) и в выводах не используется.")

        # 04_Экономика_покупки
        s4 = "04_Экономика_покупки"
        for i, sg in enumerate(I.SEGMENTS):
            r = 5 + i
            share = 0.0 if sg["code"] == "S-01" else HOURS / WORK_H
            b.set(s4, f"A{r}", f"{sg['code']} {sg['name']}")
            b.set(s4, f"B{r}", sg["income"]); b.set(s4, f"C{r}", 1.0); b.set(s4, f"D{r}", round(share, 6))
            b.set(s4, f"F{r}", round(I.PRICE_BYN_MONTH, 3))
            if sg["code"] == "S-01":
                b.set(s4, f"J{r}", "Денежного эффекта у студента нет (продукт Free); показано для случая покупки Pro")
            else:
                b.set(s4, f"J{r}", f"Эффект = доход × доля сэкономленного времени ({HOURS:g} ч из {WORK_H:g} ч в месяц; допущение Д-07, 🔲 опрос)")
            b.set(s4, f"K{r}", sg["income_src"])
        for r in range(8, 13):
            for col in "ABCDFJK":
                b.ws(s4).Range(f"{col}{r}").ClearContents()
        b.set(s4, "A16", "Доход клиента — средняя месячная зарплата/стипендия; маржинальность принята 1,0 (трудовой доход, не выручка компании).")

        # 05_Платежеспособность
        s5 = "05_Платежеспособность"
        for i, sg in enumerate(I.SEGMENTS):
            r = 5 + i
            b.set(s5, f"A{r}", f"{sg['code']} {sg['name']}")
            b.set(s5, f"B{r}", round(sg["income"] * AS.BUDGET_SHARE, 2)); b.set(s5, f"C{r}", round(I.PRICE_BYN_MONTH, 3))
            b.set(s5, f"F{r}", sg["k4"]); b.set(s5, f"H{r}", round(I.PRICE_BYN_YEAR_BASE, 2))
            b.set(s5, f"J{r}", f"Бюджет = доход × {A['Д-08']['v']:.0%} (Д-08); доля F = доле платёжеспособных листа 02 (решение В-11)")
        for r in range(8, 13):
            for col in "ABCFHJ":
                b.ws(s5).Range(f"{col}{r}").ClearContents()

        # 06_Сценарии: множители шаблона сохраняются; строки 13-15 ссылаются на 02
        # 07_Similarweb
        s7 = "07_Similarweb"
        for i, (dom, name, typ, visits, status, rel, q) in enumerate(I.SW_DOMAINS):
            r = 5 + i
            b.set(s7, f"A{r}", dom); b.set(s7, f"B{r}", visits); b.set(s7, f"C{r}", round(I.GEO_BY, 6))
            if dom == "plantuml.com":
                b.set(s7, f"E{r}", 0.4847)
            b.set(s7, f"H{r}", CR1 * CR2); b.set(s7, f"J{r}", round(I.PRICE_BYN_YEAR_BASE, 2))
            b.set(s7, f"L{r}", f"{status}; 30.09.2026. Доля РБ — допущение Д-01. H = CR1 × CR2 (в шаблоне отдельной конверсии в оплату нет)")
        for r in range(9, 13):
            for col in "ABCEFGHJL":
                b.ws(s7).Range(f"{col}{r}").ClearContents()
        b.set(s7, "A16", "Доля поискового трафика (E) показана бесплатной карточкой только у plantuml.com (Organic 48,47 %); прямой трафик и соцсети не показаны («нет данных в бесплатном доступе»).")

        s9 = "09_Источники"
        for r in (5, 6, 7, 8):
            b.set(s9, f"E{r}", D)
        b.set(s9, "E9", D); b.set(s9, "D9", "Страницы тарифов Miro, Lucidchart, Mermaid Chart, Visual Paradigm, Creately, Eraser, Whimsical, dbdiagram.io (30.09.2026)")
        b.set(s9, "D10", "🔲 ДОСНЯТЬ: опрос ≥20–30 респондентов (готовность платить, допустимая цена) — провести опрос")
        for i, (a, bb, c, d, e) in enumerate([
            ("Белстат, стипендия и зарплата", "Доход сегментов", "Доля цены в доходе, бюджет", "стипендия БГУИР (вторичный источник teenage.by); з/п: Белстат, экспресс-информация янв.–авг. 2026; «информация и связь» — Белстат, таблица по видам деятельности, июль 2026 (nach_sr_zarplata-2607.xlsx)", "30.09.2026"),
            ("НБРБ", "Курс USD/BYN 3,0285", "Перевод цен", "https://api.nbrb.by/exrates/rates/431", "30.09.2026")]):
            r = 12 + i
            b.set(s9, f"A{r}", a); b.set(s9, f"B{r}", bb); b.set(s9, f"C{r}", c); b.set(s9, f"D{r}", d); b.set(s9, f"E{r}", D)

        # П-20: пустые сегменты на листе 06 превращались в 0 и давали #ЗНАЧ! — условие пустоты исправлено в рабочей копии
        s6 = "06_Сценарии"
        for k, r in enumerate(range(13, 21)):
            b.formula(s6, f"A{r}", f"=IF('02_Сегменты'!A{5 + k}=\"\",\"\",'02_Сегменты'!A{5 + k})")
        # П-21: средняя себестоимость без данных
        b.formula(s3, "E14", '=IFERROR(AVERAGE(E5:E12),"нет данных")')
        b.formula(s3, "F14", '=IFERROR(AVERAGE(F5:F12),"нет данных")')

        b.recalc()
        res = {
            "payers_total": b.get(s2, "H16"), "market_total": b.get(s2, "J16"),
            "payers_by_seg": [b.get(s2, f"H{r}") for r in (5, 6, 7)], "market_by_seg": [b.get(s2, f"J{r}") for r in (5, 6, 7)],
            "corridor_avg": [b.get(s3, f"{c}14") for c in "BCD"],
            "econ": [(b.get(s4, f"E{r}"), b.get(s4, f"G{r}"), b.get(s4, f"H{r}"), b.get(s4, f"I{r}")) for r in (5, 6, 7)],
            "budget_index": [(b.get(s5, f"D{r}"), b.get(s5, f"E{r}")) for r in (5, 6, 7)],
            "p4_G": [b.get(s5, f"G{r}") for r in (5, 6, 7)], "p4_I": b.get(s5, "I14"),
            "scen_market": [b.get("06_Сценарии", f"{c}22") for c in "CDE"],
            "scen_revenue": [b.get("06_Сценарии", f"{c}22") for c in "FGH"],
            "sw_rev_month": b.get(s7, "K14"), "sw_relevant": b.get(s7, "D14"),
            "avg_index": b.get("08_Итоговая_панель", "B7"), "avg_roi": b.get("08_Итоговая_панель", "B8"),
            "conclusion": b.get("08_Итоговая_панель", "A16"),
            "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_pl_excel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()


if __name__ == "__main__":
    main()
