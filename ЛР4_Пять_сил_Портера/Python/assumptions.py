# -*- coding: utf-8 -*-
"""ЕДИНЫЙ ЖУРНАЛ ДОПУЩЕНИЙ ЛР4. Значения, общие с ЛР2-3, сверяются с ЛР2-3\Python\assumptions.py (функция check_with_lr23).
Кортежи - (осторожный, базовый, оптимистичный), где применимо."""
import importlib.util
import os

# ---- общие с ЛР2-3 (сверяются) ----
FX_USD_BYN = 3.0285                     # курс НБРБ на 30.09.2026 (ЛР2-3, В-12); Р-4: USD и курс на дату ЛР2-3
FX_DATE = "30.09.2026"
CR_PRO = (0.03, 0.04, 0.05)             # конверсия регистрация -> оплата Pro, 3-5 % (ЛР2-3, Д-09; концепция NotaCode)
PRICE_PRO_USD_YEAR = 40.0               # годовой чек Pro, USD (ЛР2-3, В-5); месячная оплата 4 USD

# ---- решения ЛР4 (ЗАДАНИЕ, раздел 16) ----
WEIGHTS_SUM_NOT_NORMALIZED = True       # Р-1: веса листа 07 не меняются и не нормируются (сумма 1,04, максимум 5,2)
GEO_SHARE_POLICY = "доля Беларуси из Similarweb; если не показана - отметка 'недоступно в бесплатном доступе', трафик в Excel = 0"   # Р-5
LEADERS_TOP_K = (3, 5)                  # Р-9: лидеры для вариантов Word - топ-3, рядом топ-5
MATRIX_A_SCALE = {"low": 2.0, "mid": 3.5}   # Р-7: пороги 5С (1,0-2,0 / 2,1-3,5 / 3,6-5,0)

# ---- Р-2: ручные значения 07 C11 и C12 (0-1). Оценка типа: 0 - угрозы нет, 0,5 - частичная, 1 - выраженная ----
PLATFORM_TYPES = {"трафик (поисковые системы)": 0.5, "платформы продаж": 0.0, "платёжная инфраструктура": 0.5}
SUBSTITUTE_TYPES = {"прямой (открытый код, бесплатно)": 1.0, "частичный (bpmn.io, Camunda Modeler)": 0.5,
                    "цифровой сервис (draw.io, Miro, Visio)": 1.0, "генерация нейросетью": 0.5, "обучающее решение": 0.0}
PLATFORM_DEPENDENCY = round(sum(PLATFORM_TYPES.values()) / len(PLATFORM_TYPES), 2)   # 0,33
SUBSTITUTE_THREAT = round(sum(SUBSTITUTE_TYPES.values()) / len(SUBSTITUTE_TYPES), 2)  # 0,6

# ---- проверка релевантности кандидатов (вместо проверки по Similarweb, шаг 2 SW §3) ----
RELEVANCE_RULE = ("Кандидат проходит, если на 30.09.2026 сайт доступен и его основная задача - построение диаграмм "
                  "(нотационных или универсальных как косвенный заменитель) в продуктовых границах ЛР1; "
                  "домен платформы, где редактор - лишь часть продукта, не проходит (camunda.com).")

# ---- источники снимка ----
SNAPSHOT_DATE = "30.09.2026"
SEMRUSH_PERIOD = "август 2026 (страницы обновлены 17.09.2026), все устройства, весь мир"
WORDSTAT_WINDOW = "29.08.2026-27.09.2026, Беларусь, все устройства"


def check_with_lr23():
    """Сверка общих значений с ЛР2-3 (только чтение). Возвращает список расхождений."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "ЛР2-3_Объем_рынка", "Python", "assumptions.py")
    spec = importlib.util.spec_from_file_location("lr23_assumptions", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    bad = []
    if tuple(m.CR_PRO) != CR_PRO:
        bad.append(("CR_PRO", m.CR_PRO, CR_PRO))
    if "3,0285" not in str(m.A["В-12"]["what"]):
        bad.append(("FX", m.A["В-12"]["what"], FX_USD_BYN))
    if float(m.A["В-5"]["v"]) != PRICE_PRO_USD_YEAR:
        bad.append(("PRICE", m.A["В-5"]["v"], PRICE_PRO_USD_YEAR))
    return bad


if __name__ == "__main__":
    print("Расхождения с ЛР2-3:", check_with_lr23() or "нет")
    print("C11 =", PLATFORM_DEPENDENCY, "| C12 =", SUBSTITUTE_THREAT)
