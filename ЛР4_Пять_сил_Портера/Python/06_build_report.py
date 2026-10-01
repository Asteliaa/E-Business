# -*- coding: utf-8 -*-
"""Собирает ОТЧЕТ.md из шаблона текста: сквозная нумерация таблиц и рисунков, таблицы кандидатов, реестров, карточек,
числа из results_lr4.json (скрипт 08_word_variant.py) и CSV Материалы_собранные."""
import csv
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from candidates import CANDIDATES
import from_prev_labs as fp
import cards_data as cd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(__file__)
text = open(os.path.join(HERE, "report_body.tmpl"), encoding="utf-8").read()
R = json.load(open(os.path.join(HERE, "results_lr4.json"), encoding="utf-8"))


def f1(x, n=1):
    return f"{x:.{n}f}".replace(".", ",")


def sp(x):
    return f"{x:,.0f}".replace(",", " ")


S, WI, MA = R["semrush"], R["word_index"], R["matrix_a"]
V = {
    "SEM_N": str(S["n"]), "SEM_TOTAL": sp(S["total"]), "SEM_CR3": f1(S["cr3"] * 100) + " %", "SEM_CR5": f1(S["cr5"] * 100) + " %",
    "SEM_HHI": sp(S["hhi"]), "SEM_SCORE": str(S["score_band"]),
    "NM_TOTAL": sp(S["total_no_miro"]), "NM_CR3": f1(S["cr3_no_miro"] * 100) + " %", "NM_CR5": f1(S["cr5_no_miro"] * 100) + " %",
    "NM_HHI": sp(S["hhi_no_miro"]),
    "WI_LO": f1(WI["lo"], 2), "WI_HI": f1(WI["hi"], 2), "WI_LVL_LO": WI["level_lo"].lower(), "WI_LVL_HI": WI["level_hi"].lower(),
    "MA6": f1(MA["m6"]), "MA5": f1(MA["m5"]), "MA6L": MA["l6"].lower(), "MA5L": MA["l5"].lower(),
    "MB": " / ".join(f"{int(x)}" for x in R["matrix_b"]),
}

# --- кандидаты и результат проверки релевантности (вместо проверки по Similarweb) ---
PASS = {
    "plantuml.com": "прошёл: основная задача - диаграммы UML из текста",
    "mermaid.js.org": "прошёл: диаграммы из текста и кода",
    "mermaidchart.com": "прошёл: сервис диаграмм на основе Mermaid",
    "d2lang.com": "прошёл: язык диаграмм D2",
    "kroki.io": "прошёл: отрисовка диаграмм из текста через API",
    "planttext.com": "прошёл: онлайн-редактор PlantUML",
    "staruml.io": "прошёл: программа для моделирования UML",
    "visual-paradigm.com": "прошёл: платформа UML, BPMN, архитектуры",
    "sparxsystems.com": "прошёл: Enterprise Architect (UML, BPMN); главная страница недоступна автоматическим запросам, отнесение по границам ЛР1, табл. 44",
    "bpmn.io": "прошёл: редактор и библиотека BPMN",
    "camunda.com": "не прошёл: главная страница - платформа оркестрации процессов; трафик домена не отражает редактор Modeler, который учтён как частичный заменитель (ЛР1, табл. 44)",
    "stormbpmn.com": "прошёл: редактор BPMN в составе платформы процессного управления",
    "app.diagrams.net": "прошёл: универсальный редактор диаграмм (косвенный)",
    "lucidchart.com": "прошёл: универсальный редактор диаграмм (косвенный); главная страница недоступна автоматическим запросам",
    "creately.com": "прошёл: универсальный редактор диаграмм (косвенный)",
    "miro.com": "прошёл как косвенный заменитель: универсальная доска (вне продуктовых границ как самостоятельный рынок, ЛР1)",
    "excalidraw.com": "прошёл как косвенный заменитель: доска со схемами",
    "dbdiagram.io": "прошёл: схемы баз данных (ERD)",
    "drawsql.app": "прошёл: схемы баз данных (ERD)",
    "eraser.io": "прошёл: генерация технических диаграмм (AI)",
}
cand = ["| № | Домен | Группа и роль | Проверка релевантности (главная страница, границы ЛР1), 30.09.2026 |", "|---|---|---|---|"]
for i, (d, n) in enumerate(CANDIDATES, 1):
    cand.append(f"| {i} | {d} | {n} | {PASS[d]} |")
cand.append(f"| {len(CANDIDATES) + 1} | microsoft.com/visio | Универсальный редактор, косвенный | не включён в расчёт: домен-раздел, трафик отдельно не виден; 🔲 ДОСНЯТЬ: трафик Visio (платный Similarweb или Semrush, домен microsoft.com) |")
text = text.replace("{{CAND_TABLE}}", "\n".join(cand))

# --- реестры ---
reg = [f"| {c} | {w} | {s} | {d} | {v} | {st} |" for c, w, s, d, v, st in fp.FROM_LR1 + fp.FROM_LR23]
text = text.replace("{{REGISTRY}}", "\n".join(reg))
col = [f"| {c} | {w} | {r} | {st} |" for c, w, r, st in fp.COLLECT]
text = text.replace("{{COLLECT}}", "\n".join(col))

# --- Semrush ---
rows = list(csv.DictReader(open(os.path.join(ROOT, "Материалы_собранные", "semrush_website_overview_visits_2026-08_snyato_2026-09-30.csv"), encoding="utf-8-sig"), delimiter=";"))
have = [r for r in rows if r["visits_aug_2026"]]
tot = sum(float(r["visits_aug_2026"]) for r in have if r["domain"] != "draw.io")
sem = ["| Домен | Визиты в месяц, август 2026 | Доля в сумме восьми доменов | Authority Score |", "|---|---|---|---|"]
for r in sorted(have, key=lambda r: -float(r["visits_aug_2026"])):
    v = float(r["visits_aug_2026"])
    share = "не включён (отдельный домен продукта diagrams.net)" if r["domain"] == "draw.io" else f1(v / tot * 100) + " %"
    sem.append(f"| {r['domain']} | {sp(v)} | {share} | {r['authority_score']} |")
sem.append(f"| Домены без страницы в публичном индексе | {len(rows) - len(have)} из {len(rows)} проверенных адресов | - | - |")
text = text.replace("{{SEMRUSH_TABLE}}", "\n".join(sem))

# --- Вордстат ---
ws = list(csv.DictReader(open(os.path.join(ROOT, "Материалы_собранные", "wordstat_zaprosy_RB_2026-09-30.csv"), encoding="utf-8-sig"), delimiter=";"))
wt = ["| Запрос | Запросов за окно 29.08-27.09.2026 | Запросов по ЛР1 (последние 30 дней на 29.09.2026) | Комментарий |", "|---|---|---|---|"]
LR1 = {"uml": "591", "bpmn": "476", "plantuml": "198", "idef0": "105", "dfd диаграмма": "28", "erd диаграмма": "24", "сеть петри": "8",
       "конструктор диаграмм онлайн": "6", "нейросеть схема": "76", "нейросеть диаграмма": "31"}
for r in ws:
    kind = "ядро" if "ядро" in r["comment"] else "бренд"
    extra = {"kroki": "возможная омонимия", "d2lang": "нет подходящих запросов (окно до 29.09.2026)", "mermaidchart": "нет подходящих запросов (окно до 29.09.2026)"}.get(r["query"], "")
    wt.append(f"| {r['query']} | {r['count_per_window']} | {LR1.get(r['query'], '-')} | {kind}{'; ' + extra if extra else ''} |")
text = text.replace("{{WORDSTAT_TABLE}}", "\n".join(wt))

# --- карточки ---
fields = [("Название и домен", None), ("Роль в рынке", None), ("Трафик и динамика", "traffic"), ("Каналы привлечения", "channels"),
          ("География", "geo"), ("Репутация", "rep"), ("Цены", "price"), ("Технологии", "tech"),
          ("Рекламная активность", "ads"), ("Вывод по барьеру", "concl")]
cards = []
k = 0
for d, n in CANDIDATES:
    if d not in cd.C:
        continue
    c = cd.C[d]
    cards.append(f"Таблица {{T:card{k}}} – Карточка конкурента: {d}\n")
    cards.append("| Поле | Значение |\n|---|---|")
    for f, key in fields:
        if f == "Название и домен":
            v = f"{d}; тип: {n}"
        elif f == "Роль в рынке":
            v = n
        elif key == "rep":
            v = cd.rep(d)
        elif key == "ads":
            v = "plantuml.com: доля платного трафика 0 % (Similarweb, ЛР2-3); рекламные библиотеки 🔲 ДОСНЯТЬ" if d == "plantuml.com" else cd.NOADS
        else:
            v = c[key]
        cards.append(f"| {f} | {v} |")
    cards.append("")
    k += 1
text = text.replace("{{CARDS}}", "\n".join(cards))

for key, val in V.items():
    text = text.replace("{{V:" + key + "}}", val)

# нумерация
tn, fn = {}, {}


def numT(m):
    tn[m.group(1)] = len(tn) + 1
    return f"Таблица {tn[m.group(1)]} –"


def numF(m):
    fn[m.group(1)] = len(fn) + 1
    return f"Рисунок {fn[m.group(1)]} –"


text = re.sub(r"Таблица \{T:(\w+)\} –", numT, text)
text = re.sub(r"Рисунок \{F:(\w+)\} –", numF, text)


def ref(m):
    kk = m.group(1)
    return str(tn[kk] if kk in tn else fn[kk])


text = re.sub(r"\{R:(\w+)\}", ref, text)
left = re.findall(r"\{[TFR]:\w+\}|\{\{[\w:]+\}\}", text)
assert not left, left
out = os.path.join(ROOT, "ОТЧЕТ.md")
open(out, "w", encoding="utf-8", newline="\n").write(text)
print("таблиц:", len(tn), "рисунков:", len(fn), "карточек:", k)
