# -*- coding: utf-8 -*-
"""Самопроверка конвейера на синтетических данных во временной папке (в отчёт не входит).
Проверяет перенос CSV в Excel, протяжку формул и сверку Python и Excel на полном наборе строк."""
import os
import sys
import csv
import random
import shutil
import tempfile
import importlib

sys.path.insert(0, os.path.dirname(__file__))
import lr4_io as io
from xl_com import XLS

apply_ = importlib.import_module("03_apply_to_excel")
ver = importlib.import_module("04_verify")
random.seed(7)
td = tempfile.mkdtemp()
shutil.copytree(io.DATA, td, dirs_exist_ok=True)


def rw(name, fn):
    p = os.path.join(td, name + ".csv")
    with open(p, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    for r in rows:
        fn(r)
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter=";")
        w.writeheader()
        w.writerows(rows)


def sw(r):
    ch = [random.random() for _ in range(6)]
    s = sum(ch)
    ch = [c / s for c in ch]
    r.update(visits=random.randint(2000, 500000), geo=round(random.uniform(0.02, 0.3), 2), dur=random.randint(60, 400),
             direct=round(ch[0], 3), organic=round(ch[1], 3), paid=round(ch[2], 3), social=round(ch[3], 3),
             referral=round(ch[4], 3), display=round(ch[5], 3), brand_search=round(random.uniform(0, .2), 3))


rw("sw02", sw)
rw("q04", lambda r: r.update(cpc=round(random.uniform(.1, 3), 2), ppc=round(random.random(), 2),
                             seo=random.randint(5, 90), top=random.randint(1, 10), ads=random.randint(0, 60)))
rw("rev05", lambda r: r.update(g2=round(random.uniform(3.5, 5), 1), g2_n=random.randint(0, 900),
                               trustpilot=round(random.uniform(3, 5), 1), trustpilot_n=random.randint(0, 50),
                               cases=random.randint(0, 30), age=random.randint(1, 20)))
rw("tech06", lambda r: r.update(fund=random.choice([0, 100000, 900000]), staff=random.randint(2, 200),
                                stack=random.randint(1, 5), crm=random.randint(1, 5),
                                app=random.choice(["да", "нет"]), cabinet=random.choice(["да", "нет"]),
                                ads=random.randint(0, 80), jobs=random.randint(0, 9), assets=random.randint(0, 2)))
rw("manual07", lambda r: r.update(value="0.5"))
tx = os.path.join(td, "t.xlsx")
shutil.copy(XLS, tx)
apply_.main(td, tx)
ver.main(td, tx)
shutil.rmtree(td, ignore_errors=True)
