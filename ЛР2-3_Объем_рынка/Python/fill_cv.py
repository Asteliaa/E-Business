# -*- coding: utf-8 -*-
"""Заполнение рабочей копии ЦВ-X (цифровая воронка) через Excel COM; исправление П-2; проверка пересчёта."""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from xl_com import Book
import fill_ps as P

NAME = "ЦВ_цифровая_воронка_NotaCode.xlsx"
D = datetime.datetime(2026, 9, 30)
import assumptions as AS
SHARE_REACH = AS.CV_SHARE
CR1 = AS.CV_CR1
CR2 = I.CR_PRO
REPEAT = AS.REPEAT
COVER = AS.COVER_CV
ws_mean = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_ps_excel.json"), encoding="utf-8"))["weighted_mean"]


def relevant_share_weighted():
    tot = sum(d[3] for d in I.SW_DOMAINS)
    return sum(d[3] * d[5] for d in I.SW_DOMAINS) / tot


def main():
    b = Book(NAME)
    try:
        s1 = "01_Параметры"
        b.set(s1, "B4", "NotaCode — веб-IDE для построения и проверки диаграмм формальных нотаций (UML, BPMN, ERD, IDEF, DFD) как текста")
        b.set(s1, "B5", "Республика Беларусь")
        b.set(s1, "B6", "месяц / год")
        b.set(s1, "B7", "BYN")
        b.set(s1, "B8", "пользователи-физические лица: студенты (S-01), аналитики (S-02), архитекторы и разработчики (S-03), преподаватели (S-04)")
        b.set(s1, "B9", round(I.PRICE_BYN_YEAR_BASE, 2)); b.set(s1, "C9", "BYN/оплата (год)")
        b.set(s1, "D9", "Pro: годовой тариф 40 USD × 3,0285 (курс НБРБ 30.09.2026)")
        b.set(s1, "B10", round(I.PRICE_BYN_YEAR_DISC, 2)); b.set(s1, "C10", "BYN/оплата (год)")
        b.set(s1, "D10", "Альтернативный вариант: 4 USD × 12 = 48 USD × 3,0285 = 145,37 BYN")
        b.set(s1, "B11", P.CHEQUE[2]); b.set(s1, "C11", "BYN/оплата (год)")
        b.set(s1, "D11", "Медиана входных платных тарифов конкурентов (8 USD/мес.) × 12 × 3,0285")
        rs = relevant_share_weighted()
        b.set(s1, "B12", round(rs, 4)); b.set(s1, "D12", "Допущение Д-02: средневзвешенная по визитам доля релевантного трафика четырёх доменов выборки (расчёт в 03_Конкуренты_SW); в формулах шаблона не должна использоваться как покрытие (П-2)")
        b.set(s1, "B13", COVER); b.set(s1, "D13", "Допущение Д-05: коэффициент покрытия выборки; значение базового сценария М2 табл. 21 (0,65); шкала М2 табл. 9 для типовой ситуации 0,60–0,75")
        b.set(s1, "B14", D)
        for j, r in enumerate((17, 18, 19)):
            b.set(s1, f"B{r}", SHARE_REACH[j]); b.set(s1, f"C{r}", CR1[j]); b.set(s1, f"D{r}", CR2[j]); b.set(s1, f"F{r}", REPEAT[j])

        s2 = "02_Трафик_охват"
        b.set(s2, "B4", "Яндекс Вордстат (Беларусь), взвешенная частотность ядра, среднее за 12 мес. (см. расчёт ПС)")
        b.set(s2, "C4", round(ws_mean, 2)); b.set(s2, "D4", P.CTR[1]); b.set(s2, "F4", 1.0); b.set(s2, "H4", "среднее")
        b.set(s2, "I4", "Релевантность учтена весами ядра (ПС), поэтому доля релевантной аудитории = 1; CTR — базовое значение ПС табл. 17.")
        for r, note in ((5, "🔲 ДОСНЯТЬ: прогноз показов/кликов Яндекс Директ или Google Ads Keyword Planner по ядру запросов (нужен рекламный кабинет)"),
                        (6, "🔲 ДОСНЯТЬ: оценка охвата аудитории в рекламных кабинетах VK / Meta (нужен рекламный кабинет)"),
                        (7, "Нет данных: продукт не размещён в каталогах и у партнёров (MVP не запущен)"),
                        (8, "Нет данных: бренд NotaCode не запущен, прямых заходов нет"),
                        (9, "Не применяется: NotaCode не размещается на маркетплейсах услуг"),
                        (10, "Нет данных")):
            b.set(s2, f"C{r}", 0); b.set(s2, f"D{r}", 0 if r != 8 else 1); b.set(s2, f"F{r}", 0); b.set(s2, f"H{r}", "нет данных")
            b.set(s2, f"I{r}", note)

        s3 = "03_Конкуренты_SW"
        for i, (dom, name, typ, visits, status, rel, q) in enumerate(I.SW_DOMAINS):
            r = 4 + i
            b.set(s3, f"A{r}", dom); b.set(s3, f"B{r}", typ); b.set(s3, f"C{r}", visits)
            b.set(s3, f"D{r}", round(I.GEO_BY, 6)); b.set(s3, f"E{r}", rel)
            b.set(s3, f"G{r}", CR1[1] * CR2[1]); b.set(s3, f"H{r}", round(I.PRICE_BYN_YEAR_BASE, 2))
            b.set(s3, f"J{r}", f"Визиты: {status}. Доля Беларуси — допущение Д-01 (Similarweb не показывает). Конверсия = CR1 × CR2 базового сценария; чек = цена Pro.")
        for col in "ABCDEGHJ":
            b.ws(s3).Range(f"{col}8").ClearContents()
        b.set(s3, "J8", "Строка не заполнена: выборка — 4 домена; 🔲 ДОСНЯТЬ минимум ещё 6–16 доменов (Similarweb, вручную)")
        # П-2: ссылка на B13 вместо B12
        before_c12 = b.get(s3, "C11") / b.get(s1, "B12") if b.get(s1, "B12") else 0
        b.recalc()
        c11 = b.get(s3, "C11"); c13 = b.get(s3, "C13")
        before = {"C12_old": c11 / rs, "C14_old": c13 / rs * 12}
        b.formula(s3, "C12", "=C11/'01_Параметры'!B13")
        b.formula(s3, "C14", "=C13/'01_Параметры'!B13*12")
        b.set(s3, "D12", "Исправлено в рабочей копии (П-2): деление на коэффициент покрытия B13, в шаблоне — на долю релевантного трафика B12.")
        b.set(s3, "D14", "Исправлено (П-2): C13 / B13 × 12.")

        s7 = "07_Платформа_GMV"
        for col in "BCD":
            for r in (4, 5, 7):
                b.set(s7, f"{col}{r}", 0)
        b.set(s7, "G4", "Не применяется: NotaCode — не многосторонняя платформа (подписка одного вида клиента); решение В-3.")
        b.set(s7, "G5", "Не применяется."); b.set(s7, "G7", "Не применяется.")

        s9 = "09_Источники"
        for r in range(4, 9):
            b.set(s9, f"D{r}", D)
        b.set(s9, "C4", "🔲 собственного сайта нет (MVP не запущен)")
        b.set(s9, "C5", "🔲 ДОСНЯТЬ: рекламный кабинет (нужен доступ)")
        b.set(s9, "C8", "https://www.similarweb.com/website/plantuml.com/ (замер 30.09.2026); остальные домены — отчёт ЛР1 и предварительный замер 17–23.09.2026")
        b.set(s9, "C9", "🔲 ДОСНЯТЬ: рекламные кабинеты VK / Meta")
        b.set(s9, "C10", "Страницы тарифов конкурентов (30.09.2026); курс НБРБ https://api.nbrb.by/exrates/rates/431")
        b.set(s9, "D9", D); b.set(s9, "D10", D)

        b.recalc()
        res = {
            "visits_relevant_month": b.get(s2, "C14"),
            "sw_visible": b.get(s3, "C11"), "sw_total_fixed": b.get(s3, "C12"), "sw_rev_month": b.get(s3, "C13"), "sw_rev_year_fixed": b.get(s3, "C14"),
            "sw_before": before,
            "reach": [b.get("04_Воронка", f"{c}6") for c in "BCD"],
            "leads": [b.get("04_Воронка", f"{c}8") for c in "BCD"],
            "sales": [b.get("04_Воронка", f"{c}10") for c in "BCD"],
            "rev_year": [b.get("04_Воронка", f"{c}13") for c in "BCD"],
            "rev_year_repeat": [b.get("06_Повторы_LTV", f"{c}10") for c in "BCD"],
            "min": b.get("05_Сценарии", "C9"), "base": b.get("05_Сценарии", "C10"), "max": b.get("05_Сценарии", "C11"),
            "rel_share": rs, "errors": b.errors(), "charts": b.charts(),
        }
        json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "out_cv_excel.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(json.dumps(res, ensure_ascii=False, indent=1))
    finally:
        b.close()


if __name__ == "__main__":
    main()
