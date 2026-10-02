# -*- coding: utf-8 -*-
import os
HERE = os.path.dirname(os.path.abspath(__file__))
LAB6 = os.path.dirname(HERE)
ROOT = os.path.dirname(LAB6)
LAB5 = os.path.join(ROOT, "ЛР5_Анализ_конкурентов")
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)
DATE = "01.10.2026"
