# -*- coding: utf-8 -*-
"""Заполнение рабочей копии СЦ-X (сценарная оценка рынка с данными Similarweb); исправление П-8, П-9."""
import datetime, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from xl_com import Book

NAME = "СЦ_сценарная_оценка_Similarweb_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)
HERE = os.path.dirname(os.path.abspath(__file__))
ld = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))
import assumptions as AS
COVER, RELIAB, UNAV = AS.SC_COVER, AS.SC_RELIAB, AS.SC_UNAV
CR1 = AS.SC_CR1
CR2 = I.CR_PRO                  # проект
CHEQ, BUY, SHARE = AS.SC_CHEQ, AS.SC_BUY, AS.SC_SHARE


def main():
    b = Book(NAME)
    try:
        s1 = "01_Параметры"
        tot = sum(d[3] for d in I.SW_DOMAINS)
        rel_w = sum(d[3] * d[5] for d in I.SW_DOMAINS) / tot
        q_w = sum(d[3] * d[6] for d in I.SW_DOMAINS) / tot
        b.set(s1, "B4", "NotaCode — веб-IDE для построения и проверки диаграмм формальных нотаций как текста (подписка Free / Pro)")
        b.set(s1, "B5", "Республика Беларусь"); b.set(s1, "B7", 12)
        b.set(s1, "B8", round(I.PRICE_BYN_YEAR_BASE, 2)); b.set(s1, "F8", "Pro: 40 USD × 3,0285 (НБРБ 30.09.2026)")
        b.set(s1, "B9", 1); b.set(s1, "F9", "Годовой тариф — одна оплата в год; для помесячного Pro — 12 оплат по 10,10 BYN (эквивалент годового тарифа; тот же результат)")
        b.set(s1, "B10", round(I.GEO_BY, 6)); b.set(s1, "F10", "Допущение Д-01 (доля РФ по Similarweb × отношение запросов РБ/РФ в Вордстате); не используется формулами (П-13), доля вводится по доменам на листе 02")
        b.set(s1, "B11", round(rel_w, 4)); b.set(s1, "F11", "Средневзвешенная по визитам; не используется формулами (П-13)")
        b.set(s1, "B12", round(q_w, 4)); b.set(s1, "F12", "Средневзвешенная; не используется формулами (П-13)")
        b.set(s1, "B13", D)
        for j, col in enumerate("BCD"):
            for r, v in zip((16, 17, 18, 19, 20, 21, 22, 23), (COVER[j], RELIAB[j], UNAV[j], CR1[j], CR2[j], CHEQ[j], BUY[j], SHARE[j])):
                b.set(s1, f"{col}{r}", v)
        b.set(s1, "F20", "Регистрация → оплата Pro: допущение проекта 3–5 % (вне шкалы Word СЦ 10–60 % и шкалы шаблона)")

        s2 = "02_Similarweb"
        for i, (dom, name, typ, visits, status, rel, q) in enumerate(I.SW_DOMAINS):
            r = 5 + i
            b.set(s2, f"A{r}", i + 1); b.set(s2, f"B{r}", name); b.set(s2, f"C{r}", dom); b.set(s2, f"D{r}", typ)
            b.set(s2, f"E{r}", visits); b.set(s2, f"F{r}", round(I.GEO_BY, 6)); b.set(s2, f"G{r}", rel); b.set(s2, f"H{r}", q)
            b.set(s2, f"L{r}", "https://www.similarweb.com/website/" + dom + "/")
            b.set(s2, f"M{r}", f"{status}; период «последние 3 месяца» (августовское значение). Доля РБ — допущение Д-01, доля релевантного — Д-02")
        for r in range(9, 20):
            for col in "ABCDEFGHLM":
                b.ws(s2).Range(f"{col}{r}").ClearContents()
        b.set(s2, "B22", "Выборка — 4 домена (< 5, Word СЦ: 5–15); 🔲 ДОСНЯТЬ: Similarweb, минимум ещё 6 доменов (plantuml.com подтверждён скриншотом, остальные — выгрузка ЛР1).")

        # 06_Сверка: П-9 — только результаты того же уровня (достижимая выручка, SOM); платформенная строка исключена
        ps, pk = ld("out_ps_excel.json"), ld("out_pk_excel.json")
        s6 = "06_Сверка"
        b.set(s6, "E6", "Не применяется: NotaCode не является платформой (решение В-3); строка в MIN / AVERAGE / MAX не включается (П-9)")
        for col in "BCD":
            b.ws(s6).Range(f"{col}6").ClearContents()
        for j, col in enumerate("BCD"):
            b.set(s6, f"{col}7", ps["rev_year"][j])
            b.set(s6, f"{col}8", pk["scen"][("cautious", "base", "optimistic")[j]][2])
            b.ws(s6).Range(f"{col}9").ClearContents()
        b.set(s6, "E7", "Результат ПС-X (достижимая выручка через поисковый канал, BYN/год) — уровень SOM")
        b.set(s6, "E8", "Результат ПК-X (SOM по сценариям, BYN/год)")
        b.set(s6, "E9", "Уровень «рынок» (СВ-X, ПК-X SAM) сопоставляется отдельно; здесь только SOM (П-9)")
        for col in "BCD":
            b.formula(s6, f"{col}15", f'=TEXT({col}12,"# ##0")&" – "&TEXT({col}14,"# ##0")')      # П-8
        b.recalc()
        res = {
            "traffic_year": [b.get("03_Сценарии", f"G{r}") for r in (5, 6, 7)],
            "market_rev": [b.get("04_Воронка", f"H{r}") for r in (5, 6, 7)],
            "som": [b.get("04_Воронка", f"J{r}") for r in (5, 6, 7)],
            "sales": [b.get("04_Воронка", f"E{r}") for r in (5, 6, 7)],
            "range_text": [b.text(s6, f"{c}15") for c in "BCD"],
            "reconcile": {n: [b.get(s6, f"{c}{r}") for c in "BCD"] for n, r in (("min", 12), ("avg", 13), ("max", 14))},
            "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(HERE, "out_sc_excel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()

if __name__ == "__main__":
    main()
