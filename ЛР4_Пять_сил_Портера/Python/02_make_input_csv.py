# -*- coding: utf-8 -*-
"""Создаёт пустые входные CSV (заголовки + перечень кандидатов). Числа вносятся по мере получения (реестр from_prev_labs.py)."""
import os, csv, sys
sys.path.insert(0, os.path.dirname(__file__))
from lr4_io import SPEC, DATA
from candidates import CANDIDATES, QUERIES
os.makedirs(DATA, exist_ok=True)
def write(name, rows, cols):
    with open(os.path.join(DATA, name + ".csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";"); w.writerow(cols); w.writerows(rows)
cols = ["include"] + list(SPEC["sw02"][1].keys())
write("sw02", [[1, s, "цифровой сервис"] + [""] * (len(cols) - 4) + ["кандидат: " + n] for s, n in CANDIDATES], cols)
write("q04", [[q] + [""] * (len(SPEC["q04"][1]) - 1) for q in QUERIES], list(SPEC["q04"][1].keys()))
write("rev05", [[s] + [""] * (len(SPEC["rev05"][1]) - 1) for s, _ in CANDIDATES], list(SPEC["rev05"][1].keys()))
write("tech06", [[s] + [""] * (len(SPEC["tech06"][1]) - 1) for s, _ in CANDIDATES], list(SPEC["tech06"][1].keys()))
write("manual07", [["platform_dependency", "", "🔲 Р-2: из матрицы заменителей ЛР1 и фактов сбора"],
                   ["substitute_threat", "", "🔲 Р-2: из матрицы заменителей ЛР1 и фактов сбора"]], ["field", "value", "comment"])
write("word_criteria", [[i, n, "", ""] for i, n in enumerate(["Количество релевантных конкурентов", "Концентрация трафика",
      "Стоимость входа в каналы", "Поисковая конкуренция", "Рекламная конкуренция", "Репутационный барьер",
      "Технологический барьер", "Издержки переключения клиента"], 1)], ["n", "criterion", "score_min", "score_max"])
write("matrix_a", [[n, "", ""] for n in ["Конкуренция игроков", "Угроза новых участников", "Сила покупателей",
      "Сила поставщиков", "Угроза заменителей", "Цифровые усилители"]], ["force", "score", "comment"])
write("matrix_b", [[n, ""] for n in ["Конкуренция игроков", "Угроза новых участников", "Сила покупателей",
      "Сила поставщиков", "Угроза заменителей"]], ["force", "score_0_3"])
print("ok", DATA)
