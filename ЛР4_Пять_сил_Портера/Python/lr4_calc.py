# -*- coding: utf-8 -*-
"""Расчёты ЛР4 строго по формулам Excel-шаблона (основной вариант) и по тексту методик (вариант Word).
Собственных формул и нормировок в основном расчёте нет; справочная нормировка весов вынесена отдельно."""
from __future__ import annotations

PARAMS = dict(cr3=0.6, cr5=0.75, hhi=2500.0, paid=0.2, organic=0.45, brand=0.5, reviews=100, ads=30)
CHANNEL_THRESH = dict(direct=0.30, social=0.20, referral=0.15, display=0.10)
WEIGHTS = [0.16, 0.12, 0.12, 0.12, 0.12, 0.12, 0.12, 0.08, 0.08]   # 07 E4:E12 по шаблону
FACTORS = ["Концентрация трафика", "Органическое SEO-давление", "Платное рекламное давление",
           "Брендовая сила конкурентов", "Поисково-рекламная конкуренция", "Репутационный барьер",
           "Технологический и ресурсный барьер", "Платформенная зависимость", "Угроза заменителей"]


def num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def score3(v, hi, mid):          # 5 / 3 / 1 по порогам
    return 5 if v >= hi else (3 if v >= mid else 1)


def avg(xs):
    xs = [x for x in xs if num(x)]
    return sum(xs) / len(xs) if xs else None


# ---------- лист 02 ----------
def sheet02(rows, p=PARAMS):
    """rows: dict(site, visits, geo, dur, direct, organic, paid, social, referral, display, brand).
    Возвращает основной (Excel: релевантный трафик E = визиты * доля географии) и сравнительный (Word: сырые визиты)."""
    E = [(r["visits"] or 0) * (r["geo"] or 0) for r in rows]
    sE = sum(E)
    F = [e / sE if sE else 0 for e in E]
    def conc(shares):
        s = sorted(shares, reverse=True)
        return dict(cr3=sum(s[:3]), cr5=sum(s[:5]), hhi=sum(x * x for x in shares) * 10000)
    V = [r["visits"] or 0 for r in rows]
    sV = sum(V)
    G = [v / sV if sV else 0 for v in V]
    out = dict(E=E, F=F, total=sE, excel=conc(F), word=conc(G), word_shares=G)
    out["dur"] = (sum(e * (r["dur"] or 0) for e, r in zip(E, rows)) / sE) if sE else 0
    def band(c):
        hi = c["cr3"] >= p["cr3"] or c["hhi"] >= p["hhi"]
        mid = c["cr3"] >= 0.65 * p["cr3"] or c["hhi"] >= 0.65 * p["hhi"]
        return 5 if hi else (3 if mid else 1)
    out["score_excel"] = band(out["excel"])
    out["score_word_raw"] = band(out["word"])
    return out


# ---------- лист 03 ----------
def sheet03(rows, E, p=PARAMS):
    sE = sum(E)
    def w(key, extra=None):
        if not sE: return 0.0
        return sum(e * ((r[key] or 0) + ((r[extra] or 0) if extra else 0)) for e, r in zip(E, rows)) / sE
    C = dict(direct=w("direct"), organic=w("organic"), paid=w("paid"), social=w("social"),
             referral=w("referral"), display=w("display"), brand=w("direct", "brand_search"))
    D = dict(direct=CHANNEL_THRESH["direct"], organic=p["organic"], paid=p["paid"], social=CHANNEL_THRESH["social"],
             referral=CHANNEL_THRESH["referral"], display=CHANNEL_THRESH["display"], brand=p["brand"])
    S = {k: (5 if C[k] >= D[k] else (3 if C[k] >= 0.65 * D[k] else 1)) for k in C}
    return dict(C=C, D=D, S=S)


# ---------- листы 04-06 ----------
def k04(r):
    return min(1, avg([min(r["cpc"] / 2, 1), r["ppc"], r["seo"] / 100, min(r["top"] / 10, 1), min(r["ads"] / 50, 1)]))


def sheet04(rows):
    K = [k04(r) for r in rows]
    L = [score3(k, 0.7, 0.4) for k in K]
    b37 = avg(K)
    b38 = L.count(5) / len(L) if L else None
    return dict(K=K, L=L, b37=b37, b38=b38,
                c37=None if b37 is None else ("высокое" if b37 >= 0.7 else "среднее" if b37 >= 0.4 else "низкое"))


def l05(r):
    rat = [r.get(k) for k in ("g2", "capterra", "trustpilot", "google_rating") if num(r.get(k))]
    a = (sum(rat) / len(rat) / 5) if rat else 0          # IFERROR(...,0)
    n = sum((r.get(k) or 0) for k in ("g2_n", "capterra_n", "trustpilot_n", "google_n"))
    return min(1, avg([a, min(n / 300, 1), min((r.get("cases") or 0) / 30, 1), min((r.get("age") or 0) / 10, 1)]))


def sheet05(rows, p=PARAMS):
    L = [l05(r) for r in rows]
    M = [score3(x, 0.7, 0.4) for x in L]
    b37 = avg(L)
    tot = sum(sum((r.get(k) or 0) for k in ("g2_n", "capterra_n", "trustpilot_n", "google_n")) for r in rows)
    b38 = tot / len(rows) if rows else None               # исправленная формула (Д3)
    lvl = None if b38 is None else ("высокий барьер" if b38 >= p["reviews"] else "средний барьер" if b38 >= p["reviews"] * 0.5 else "низкий барьер")
    return dict(L=L, M=M, b37=b37, b38=b38, c38=lvl)


def k06(r):
    yes = lambda v: 1 if v == "да" else 0
    return min(1, avg([min(r["fund"] / 500000, 1), min(r["staff"] / 60, 1), r["stack"] / 5, r["crm"] / 5,
                       yes(r["app"]), yes(r["cabinet"]), min(r["ads"] / 50, 1), min(r["jobs"] / 6, 1),
                       1 if r["assets"] > 0 else 0]))


def sheet06(rows):
    K = [k06(r) for r in rows]
    L = [score3(x, 0.7, 0.4) for x in K]
    b38 = sum(1 for r in rows if r["app"] == "да" or r["cabinet"] == "да") / len(rows) if rows else None   # исправленная формула (Д4)
    return dict(K=K, L=L, b37=avg(K), b38=b38)


# ---------- лист 07 ----------
def sheet07(s02, s03, b37_04, b37_05, b37_06, c11, c12, weights=WEIGHTS):
    C = [s02["excel"]["cr3"], s03["C"]["organic"], (s03["C"]["paid"] + b37_04) / 2, s03["C"]["brand"], b37_04,
         b37_05, b37_06, c11, c12]
    D = [s02["score_excel"], s03["S"]["organic"], score3(C[2], 0.6, 0.35), s03["S"]["brand"],
         score3(C[4], 0.7, 0.4), score3(C[5], 0.7, 0.4), score3(C[6], 0.7, 0.4),
         score3(C[7], 0.7, 0.4), score3(C[8], 0.7, 0.4)]
    Fw = [d * w for d, w in zip(D, weights)]
    idx = sum(Fw)
    lvl = "высокие барьеры" if idx >= 4 else "средние барьеры" if idx >= 2.5 else "низкие барьеры"
    sw = sum(weights)
    ref = idx / sw                                        # справочно, не основной результат
    return dict(C=C, D=D, F=Fw, index=idx, level=lvl, weights_sum=sw, max_index=5 * sw,
                ref_index=ref, ref_level="высокие барьеры" if ref >= 4 else "средние барьеры" if ref >= 2.5 else "низкие барьеры")


# ---------- вариант Word ----------
def word_index(criteria):
    """criteria: список 8 значений; число либо (мин, макс) при неполных данных. Простое среднее (SW табл. 7-8)."""
    lo = [c[0] if isinstance(c, tuple) else c for c in criteria]
    hi = [c[1] if isinstance(c, tuple) else c for c in criteria]
    a, b = sum(lo) / len(lo), sum(hi) / len(hi)
    return a, b, word_level(a), word_level(b)


def word_level(x):
    x = round(x, 1)
    return "Низкий" if x <= 2.0 else "Умеренный" if x <= 3.0 else "Высокий" if x <= 4.0 else "Очень высокий"


def matrix_a(scores6):
    """5С табл. 25-28: 6 строк; основная средняя по 6, рядом по 5 силам без цифровых усилителей (Р-7)."""
    m6 = round(sum(scores6) / 6, 1)
    m5 = round(sum(scores6[:5]) / 5, 1)
    lv = lambda m: "Низкое" if m <= 2.0 else "Умеренное" if m <= 3.5 else "Высокое"
    return m6, lv(m6), m5, lv(m5)


def word_channels(rows, E, k=3):
    """Вариант Word (SW табл. 6): индексы по сырым долям; лидеры = топ-k по доле релевантного трафика (Р-9)."""
    order = sorted(range(len(rows)), key=lambda i: -E[i])[:k]
    lead = [rows[i] for i in order]
    mean = lambda xs: sum(xs) / len(xs) if xs else None
    return dict(
        paid=mean([mean([r["paid"] or 0, r["display"] or 0]) for r in rows]),
        organic_leaders=mean([r["organic"] or 0 for r in lead]),
        brand_leaders=mean([(r["direct"] or 0) for r in lead]),
    )
