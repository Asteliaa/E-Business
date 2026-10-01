# -*- coding: utf-8 -*-
"""Заполнение рабочей копии СВ-X («сверху вниз» и «снизу вверх» с Similarweb)."""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from xl_com import Book

NAME = "СВ_сверху_вниз_снизу_вверх_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)
import assumptions as AS
CR1, CR2, REP, ADJ = AS.SV_CR1, I.CR_PRO[1], AS.SV_REP, AS.SV_ADJ
# сценарные доли «сверху вниз» - середины диапазонов ПК табл. 7 (осторожный / базовый / оптимистичный)
K1, K2, K3, K4 = (AS.K_RANGE[k] for k in ('K1', 'K2', 'K3', 'K4'))


def main():
    b = Book(NAME)
    try:
        s1 = "01_Параметры"
        b.set(s1, "B5", "Веб-инструменты построения и проверки диаграмм формальных нотаций (UML, BPMN, ERD, IDEF, DFD) для студентов и специалистов по ПО в Республике Беларусь")
        b.set(s1, "B6", "Республика Беларусь"); b.set(s1, "B7", "BYN")
        b.set(s1, "B8", round(I.PRICE_BYN_YEAR_BASE, 2)); b.set(s1, "E8", "Pro: 40 USD × 3,0285 (НБРБ, 30.09.2026); альтернатива 48 USD/год = 145,37 BYN")
        b.set(s1, "B9", 1); b.set(s1, "E9", "Годовой тариф — одна оплата в год (в формулах не используется)")
        b.set(s1, "B10", CR1); b.set(s1, "E10", "Посетитель → регистрация; значение шаблона (Word СВ табл. 22 — 2–6 %)")
        b.set(s1, "B11", CR2); b.set(s1, "E11", "Регистрация → оплата Pro: допущение проекта (Free → Pro 3–5 %); шкалы методик для услуг неприменимы")
        b.set(s1, "B12", REP); b.set(s1, "E12", "Шкала шаблона; срок удержания — допущение")
        b.set(s1, "B13", ADJ); b.set(s1, "E13", "Значение шаблона; в варианте Word — явное покрытие 0,5 / 0,7 / 0,9")
        for c, v in zip("B", (0.6,)):
            pass
        b.set(s1, "B14", AS.SV_SCEN[0]); b.set(s1, "B15", AS.SV_SCEN[1]); b.set(s1, "B16", AS.SV_SCEN[2])

        s2 = "02_Сверху_вниз"
        total = sum(sg["pop"] for sg in I.SEGMENTS)
        for j, col in enumerate("BCD"):
            b.set(s2, f"{col}5", total)
            b.set(s2, f"{col}6", K1[j]); b.set(s2, f"{col}7", 1.0); b.set(s2, f"{col}8", K3[j])
            b.set(s2, f"{col}9", round(K2[j] * K4[j], 6))
        b.set(s2, "F5", "Численность целевых групп по статистике РБ: студенты 229,0 тыс. + работники цифровой экономики 130,5 тыс. + ППС 17,1 тыс. (ИНСТР §7.1: число пользователей)")
        b.set(s2, "F6", "К1 по ПК табл. 7: 15 / 30 / 50 % (середины диапазонов сценариев)")
        b.set(s2, "F7", "Исходные данные уже по Республике Беларусь — 1,0")
        b.set(s2, "F8", "К3 по ПК табл. 7: 30 / 55 / 80 %")
        b.set(s2, "F9", "К2 × К4 (потребность × готовность платить) по ПК табл. 7: 10×7,5 % / 22,5×17,5 % / 40×32,5 %")

        s3 = "03_Снизу_вверх"
        for i, sg in enumerate(I.SEGMENTS):
            r = 5 + i
            b.set(s3, f"A{r}", f"{sg['code']} {sg['name']}")
            b.set(s3, f"B{r}", round(sg["pop"] * sg["k1"])); b.set(s3, f"C{r}", round(sg["k2"] * sg["k4"], 6))
            b.set(s3, f"D{r}", sg["k3"]); b.set(s3, f"E{r}", 1); b.set(s3, f"F{r}", round(I.PRICE_BYN_YEAR_BASE, 2))
            b.set(s3, f"I{r}", sg["src"] + "; C = К2 × К4 (потребность и готовность платить)")
            b.set(s3, f"J{r}", "Допущение")
        for r in range(8, 11):
            for col in "ABCDEFIJ":
                b.ws(s3).Range(f"{col}{r}").ClearContents()

        s4 = "04_Similarweb"
        for i, (dom, name, typ, visits, status, rel, q) in enumerate(I.SW_DOMAINS):
            r = 5 + i
            b.set(s4, f"A{r}", dom); b.set(s4, f"B{r}", typ.split(" (")[0].capitalize())
            b.set(s4, f"C{r}", visits); b.set(s4, f"D{r}", round(I.GEO_BY, 6)); b.set(s4, f"E{r}", rel)
            b.set(s4, f"F{r}", AS.COMM_SW); b.set(s4, f"G{r}", 1.0)
            b.set(s4, f"K{r}", "https://www.similarweb.com/website/" + dom + "/"); b.set(s4, f"L{r}", D)
            b.set(s4, f"M{r}", status + "; доля РБ — допущение Д-01; коммерческая релевантность 35 % (М2 табл. 21, базовый); вовлечённость 1,0")
        for r in range(9, 15):
            for col in "ABCDEFGKLM":
                b.ws(s4).Range(f"{col}{r}").ClearContents()

        s8 = "08_Источники"
        b.set(s8, "B5", "Similarweb (plantuml.com, авг. 2026; остальные домены — отчёт ЛР1 и предварительный замер 17–23.09.2026)")
        b.recalc()
        res = {
            "topdown": [b.get(s2, f"{c}12") for c in "BCD"], "topdown_clients": [b.get(s2, f"{c}11") for c in "BCD"],
            "bottomup": b.get(s3, "G11"), "bottomup_seg": [b.get(s3, f"G{r}") for r in (5, 6, 7)],
            "sw_year_visits": b.get(s4, "I15"),
            "sw_funnel": [b.get("05_Воронка_SW", f"{c}14") for c in "BCD"],
            "reconcile": {n: [b.get("06_Сверка", f"{c}{r}") for c in "BCD"] for n, r in (("top", 5), ("bottom", 6), ("sw", 7), ("min", 8), ("avg", 9), ("max", 10))},
            "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_sv_excel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()

if __name__ == "__main__":
    main()
