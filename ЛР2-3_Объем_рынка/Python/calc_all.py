# -*- coding: utf-8 -*-
"""Независимый пересчёт всех методик на Python: проверка значений Excel-копий, варианты по Word, чувствительность, сводка.
Результат: results.json (читается скриптами рисунков и сборки отчёта)."""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inputs as I
from assumptions import A

HERE = os.path.dirname(os.path.abspath(__file__))
ld = lambda n: json.load(open(os.path.join(HERE, n), encoding="utf-8"))
X = {k: ld(f"out_{k}_excel.json") for k in ("ps", "cv", "pl", "pk", "sv", "sc", "sw")}
R = {}
chk = []


def close(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def check(name, py, xl):
    ok = close(py, xl, 1e-4)
    chk.append((name, py, xl, ok))
    return ok


FX, PM = I.FX, I.PRICE_BYN_MONTH
PY = round(I.PRICE_BYN_YEAR_BASE, 2)        # как в Excel-копиях
GEO = round(I.GEO_BY, 6)
CHEQ = [I.PRICE_BYN_YEAR_DISC, I.PRICE_BYN_YEAR_BASE, sorted(I.ENTRY_PRICES.values())[len(I.ENTRY_PRICES) // 2] * 12 * FX]
CHEQ = [round(x, 2) for x in CHEQ]
R["cheques"] = CHEQ
R["median_entry_usd"] = sorted(I.ENTRY_PRICES.values())[len(I.ENTRY_PRICES) // 2]

# ============================================================ ПС
groups = list(I.GROUP_SERIES)
w = I.INTENT_WEIGHT
F = [sum(I.GROUP_SERIES[g][i] for g in groups) for i in range(12)]
G = [(sum(I.GROUP_SERIES[g][i] * w[g] for g in groups) / F[i]) if F[i] else 0 for i in range(12)]
H = [F[i] * G[i] for i in range(12)]
Hm = sum(H) / 12
import assumptions as AS
CTR, CR1, CR2, REP = AS.PS_CTR, AS.PS_CR1, I.CR_PRO, AS.REPEAT
ps = {"F": F, "G": G, "H": H, "H_mean": Hm}
ps["visits"] = [Hm * c for c in CTR]
ps["leads"] = [ps["visits"][j] * CR1[j] for j in range(3)]
ps["sales"] = [ps["leads"][j] * CR2[j] for j in range(3)]
ps["rev_month"] = [ps["sales"][j] * CHEQ[j] * REP[j] for j in range(3)]
ps["rev_year"] = [x * 12 for x in ps["rev_month"]]
check("ПС: среднее взвешенной частотности", Hm, X["ps"]["F_mean_weighted"])
for j in range(3):
    check(f"ПС: выручка/год сц.{j}", ps["rev_year"][j], X["ps"]["rev_year"][j])
# сводный индекс (Р-3)
gt_avg = [sum(v) / 4 for v in I.GT_MONTHLY]
mx_gt, mx_ws = max(gt_avg), max(H)
idx = [0.4 * (gt_avg[i] / mx_gt * 100 if mx_gt else 0) + 0.6 * (H[i] / mx_ws * 100) for i in range(12)]
ps["index"] = idx; ps["index_mean"] = sum(idx) / 12
ps["gt_avg"] = gt_avg
ps["gt_norm_mean"] = sum(g / mx_gt * 100 for g in gt_avg) / 12 if mx_gt else 0
ps["ws_norm_mean"] = sum(h / mx_ws * 100 for h in H) / 12
check("ПС: сводный индекс (среднее)", ps["index_mean"], X["ps"]["index_mean"])
# Word-вариант
reg_k = AS.REGION_K
sumJ = sum(r[4] * r[6] * r[7] for r in I.SEMANTICS)
ps["sumJ_excel"] = sumJ
ps["sumJ_word"] = sumJ * reg_k
check("ПС: сумма J", sumJ, X["ps"]["sumJ"])
ctr_w, cr1_w = AS.PS_CTR_W, AS.PS_CR1_W
cr2_w_scale = AS.PS_CR2_SCALE
word_no_rep = [sum(H) * ctr_w[j] * cr1_w[j] * CR2[j] * CHEQ[j] for j in range(3)]              # сумма 12 месяцев, без повторов (Р-4, Р-5)
ps["word_year_sum_months"] = word_no_rep
ps["word_year_excel_params_no_rep"] = [sum(H) * CTR[j] * CR1[j] * CR2[j] * CHEQ[j] for j in range(3)]
ps["word_base_sumJ"] = [sumJ * CTR[j] * CR1[j] * CR2[j] * CHEQ[j] * 12 for j in range(3)]      # база воронки = сумма по ядру (Р-2)
ps["cr2_scale_year"] = [Hm * CTR[j] * CR1[j] * cr2_w_scale[j] * CHEQ[j] * REP[j] * 12 for j in range(3)]  # чувствительность: CR2 по шкале ПС
R["ps"] = ps

# ============================================================ ЦВ
cv = {}
reach_share = AS.CV_SHARE; cv_cr1 = AS.CV_CR1
vis_rel = Hm * AS.PS_CTR[1] * 1.0
cv["relevant_visits"] = vis_rel
cv["reach"] = [vis_rel * s for s in reach_share]
cv["sales"] = [cv["reach"][j] * cv_cr1[j] * CR2[j] for j in range(3)]
cv["rev_year"] = [cv["sales"][j] * CHEQ[j] * 12 for j in range(3)]
cv["rev_year_repeat"] = [cv["rev_year"][j] * REP[j] for j in range(3)]
for j in range(3):
    check(f"ЦВ: выручка/год сц.{j}", cv["rev_year"][j], X["cv"]["rev_year"][j])
    check(f"ЦВ: с повторами сц.{j}", cv["rev_year_repeat"][j], X["cv"]["rev_year_repeat"][j])
cv["word_no_share"] = [vis_rel * cv_cr1[j] * CR2[j] * CHEQ[j] * 12 for j in range(3)]   # Р-10: доли = 1
# подписочная модель ЦВ табл. 8: платящие × ежемесячный платёж × срок удержания (мес.)
cv["subscription"] = [cv["sales"][j] * 12 * PM * (12 * REP[j]) for j in range(3)]
cv["sw_fixed"] = X["cv"]["sw_rev_year_fixed"]; cv["sw_old"] = X["cv"]["sw_before"]["C14_old"]
R["cv"] = cv

# ============================================================ ПК
pk = {}
segs = I.SEGMENTS
def sam_seg(s, m=(1, 1, 1, 1)):
    return s["pop"] * s["k1"] * s["k2"] * s["k3"] * s["k4"] * PY
pk["sam_seg"] = [sam_seg(s) for s in segs]; pk["sam"] = sum(pk["sam_seg"])
pk["som_seg"] = [pk["sam_seg"][i] * segs[i]["k5"] for i in range(3)]; pk["som_seg_total"] = sum(pk["som_seg"])
pk["som_single"] = pk["sam"] * 0.02
pk["payers"] = sum(s["pop"] * s["k1"] * s["k2"] * s["k3"] * s["k4"] for s in segs)
pk["tam"] = sum(s["pop"] for s in segs) * PY
check("ПК: SAM", pk["sam"], X["pk"]["sam"]); check("ПК: SOM по сегментам", pk["som_seg_total"], X["pk"]["som"])
check("ПК: платящие", pk["payers"], X["pk"]["addressable"]); check("ПК: SOM 2 %", pk["som_single"], X["pk"]["scen"]["base"][2])
mult = AS.PK_MULT
pk["scen"] = {}
for k, (mn, mo, mp, mc, mf, sh) in mult.items():
    tam = sum(s["pop"] for s in segs) * PY * mc * mf
    sam = pk["payers"] * PY * mn * mo * mp * mc * mf
    pk["scen"][k] = [tam, sam, sam * sh]
    check(f"ПК: SAM {k}", sam, X["pk"]["scen"][k][1])
# Word: диапазоны К1–К5 (ПК табл. 7), середины диапазонов
wr = {k: tuple(AS.K_RANGE[f"K{i}"][j] for i in range(1, 6)) for j, k in enumerate(("cautious", "base", "optimistic"))}
pop = sum(s["pop"] for s in segs)
pk["word_ranges"] = {}
for k, (k1, k2, k3, k4, k5) in wr.items():
    sam = pop * k1 * k2 * k3 * k4 * PY
    pk["word_ranges"][k] = [sam, sam * k5, pop * k2 * k3 * k4 * PY]   # SAM, SOM, формула без К1 (Р-20)
# попадание значений Excel-сценариев в диапазоны Word
rng = {"К1": ((0.10, 0.20), (0.20, 0.40), (0.40, 0.60)), "К2": ((0.05, 0.15), (0.15, 0.30), (0.30, 0.50)),
       "К3": ((0.20, 0.40), (0.40, 0.70), (0.70, 0.90)), "К4": ((0.05, 0.10), (0.10, 0.25), (0.25, 0.40)),
       "К5": ((0.005, 0.01), (0.01, 0.03), (0.03, 0.07))}
hit = []
for si, (k, m) in enumerate(mult.items()):
    idx_ = {"cautious": 0, "base": 1, "optimistic": 2}[k]
    # значения по взвешенному среднему сегментов (К1) и базовым долям
    k1 = sum(s["pop"] * s["k1"] for s in segs) / pop
    k2 = segs[0]["k2"] * m[0]; k3 = segs[0]["k3"] * m[1]
    k4 = (pk["payers"] / sum(s["pop"] * s["k1"] * s["k2"] * s["k3"] for s in segs)) * m[2]
    k5 = m[5]
    for nm, val in (("К1", k1), ("К2", k2), ("К3", k3), ("К4", k4), ("К5", k5)):
        lo, hi = rng[nm][idx_]
        hit.append((k, nm, val, lo, hi, lo - 1e-9 <= val <= hi + 1e-9))
pk["hit"] = hit
R["pk"] = pk

# ============================================================ ПЛ
pl = {}
pl["payers"] = pk["payers"]; pl["market"] = pk["sam"]
check("ПЛ: платёжеспособные", pl["payers"], X["pl"]["payers_total"]); check("ПЛ: рынок", pl["market"], X["pl"]["market_total"])
HOURS = AS.HOURS / AS.WORK_H
pl["seg"] = []
cor_avg_med = X["pl"]["corridor_avg"][1]       # BYN/мес., среднее медианных цен
for s in segs:
    eff = 0.0 if s["code"] == "S-01" else s["income"] * HOURS
    budget = round(s["income"] * AS.BUDGET_SHARE, 2)
    just = eff
    allowed = min(cor_avg_med, budget, just)
    pl["seg"].append(dict(code=s["code"], income=s["income"], effect=eff, budget=budget, price=PM, index=budget / round(PM, 3),
                          justif=(eff / PM), roi=(eff - PM) / PM, share_income=PM / s["income"], allowed=allowed, just_price=just))
for i, sg in enumerate(pl["seg"]):
    check(f"ПЛ: индекс платёжеспособности {sg['code']}", sg["index"], X["pl"]["budget_index"][i][0])
# чувствительность к Д-08 (доля бюджета)
pl["sens_budget"] = {str(sh): [round(s["income"] * sh / PM, 2) for s in segs] for sh in (0.03, 0.05, 0.10)}
R["pl"] = pl

# ============================================================ СВ
sv = {}
K1, K2, K3, K4 = (AS.K_RANGE[k] for k in ('K1', 'K2', 'K3', 'K4'))
sv["topdown"] = [pop * K1[j] * 1.0 * K3[j] * (K2[j] * K4[j]) * PY for j in range(3)]
sv["bottomup"] = sum(round(s["pop"] * s["k1"]) * (s["k2"] * s["k4"]) * s["k3"] * 1 * round(PY, 2) for s in segs)
for j in range(3):
    check(f"СВ: сверху вниз сц.{j}", sv["topdown"][j], X["sv"]["topdown"][j])
check("СВ: снизу вверх", sv["bottomup"], X["sv"]["bottomup"])
sv["bu_scen"] = [sv["bottomup"] * m for m in (0.6, 1.0, 1.4)]
obs = sum(d[3] * GEO * d[5] * 0.35 * 1.0 for d in I.SW_DOMAINS) * 12
sv["sw_year_visits"] = obs
check("СВ: визиты SW/год", obs, X["sv"]["sw_year_visits"] if False else X["sv"]["sw_year_visits"])
cr1s = tuple(AS.SV_CR1 * m for m in AS.SV_FUN['cr1']); cr2s = tuple(CR2[1] * m for m in AS.SV_FUN['cr2'])
chs = tuple(PY * m for m in AS.SV_FUN['cheq']); reps = tuple(AS.SV_REP * m for m in AS.SV_FUN['rep']); scm = AS.SV_SCEN
sv["sw_funnel"] = [obs * scm[j] * AS.SV_ADJ * cr1s[j] * cr2s[j] * chs[j] * reps[j] for j in range(3)]
for j in range(3):
    check(f"СВ: SW-воронка сц.{j}", sv["sw_funnel"][j], X["sv"]["sw_funnel"][j])
# Word: «сверху вниз» от трафика (ф. 1–4) с покрытием 0,5 / 0,7 / 0,9
cover_w = AS.SV_COVER_W
vis_total = sum(d[3] for d in I.SW_DOMAINS)
vis_geo = vis_total * GEO                                   # ф. 2 (доля РБ по допущению Д-01)
est = [vis_geo / c for c in cover_w]                            # ф. 3
conv = 0.025 * CR2[1]
sv["word_topdown_traffic"] = est
sv["word_topdown"] = [est[j] * conv * PY * 12 for j in range(3)]    # ф. 4 (12 периодов в году; чек — годовой за оплату)
# Word: «снизу вверх» по каналам (ф. 5): посещения × доля коммерческого трафика × CR1 × CR2 × чек; каналы — только Organic
org = 0.4847
comm = AS.SV_COMM
sv["word_bottomup_channels"] = [vis_geo * org * comm[j] * 0.025 * CR2[1] * PY * 12 for j in range(3)]
# подписной сервис (табл. 17): посещения × регистрация × оплата × средний период удержания (мес.)
sv["word_subscription"] = [vis_geo * comm[j] * 0.025 * CR2[j] * (12 * REP[j]) * PM * 12 for j in range(3)]
# итог Word: [минимум из осторожных; максимум из проверенных базовых/оптимистичных]
methods = {"top": sv["topdown"], "bottom": sv["bu_scen"], "sw": sv["sw_funnel"]}
sv["word_range"] = [min(v[0] for v in methods.values()), max(max(v[1], v[2]) for v in methods.values())]
sv["excel_range"] = [min(v[0] for v in methods.values()), sum(v[1] for v in methods.values()) / 3, max(v[2] for v in methods.values())]
R["sv"] = sv

# ============================================================ СЦ
sc = {}
vis_rel_m = sum(d[3] * GEO * d[5] * d[6] for d in I.SW_DOMAINS)
cover, rel, unav = AS.SC_COVER, AS.SC_RELIAB, AS.SC_UNAV
sc_cr1, sc_cheq, share = AS.SC_CR1, AS.SC_CHEQ, AS.SC_SHARE
sc["traffic_year"] = [vis_rel_m * cover[j] * rel[j] * unav[j] * 12 for j in range(3)]
sc["market_rev"] = [sc["traffic_year"][j] * sc_cr1[j] * CR2[j] * PY * sc_cheq[j] * 1 for j in range(3)]
sc["som"] = [sc["market_rev"][j] * share[j] for j in range(3)]
for j in range(3):
    check(f"СЦ: трафик/год {j}", sc["traffic_year"][j], X["sc"]["traffic_year"][j]); check(f"СЦ: рынок {j}", sc["market_rev"][j], X["sc"]["market_rev"][j])
cover_w2 = AS.SC_COVER_W                                  # Word СЦ табл. 10: 40–50 / 55–70 / 75–90 % (середины)
rel_w = AS.SC_REL_W                                      # 20–30 / 35–55 / 60–75 % (середины)
cr1_w2 = AS.SC_CR1_W
sc["word_traffic_full"] = [sum(d[3] * GEO * rel_w[j] for d in I.SW_DOMAINS) / cover_w2[j] * 12 for j in range(3)]
sc["word_market"] = [sc["word_traffic_full"][j] * cr1_w2[j] * CR2[j] * PY * 1 for j in range(3)]
sc["word_som"] = [sc["word_market"][j] * share[j] for j in range(3)]
R["sc"] = sc

# ============================================================ SW
sw = {}
obs_m = sum(d[3] * GEO for d in I.SW_DOMAINS)
sw["observed_month"] = obs_m
cov_x, cr1_x, sh_x = AS.SW_COVER, AS.SW_CR1, AS.SW_SHARE
sw["market_year"] = [obs_m / cov_x[j] * cr1_x[j] * CR2[j] * CHEQ[j] * 12 * 1 for j in range(3)]
sw["som"] = [sw["market_year"][j] * sh_x[j] for j in range(3)]
for j in range(3):
    check(f"SW: рынок/год {j}", sw["market_year"][j], X["sw"]["market_year"][j])
cov_m2, comm_m2, cr1_m2 = AS.SW_COVER_M2, AS.SW_COMM_M2, AS.SW_CR1_M2
sw["m2_year"] = [obs_m / cov_m2[j] * comm_m2[j] * cr1_m2[j] * CR2[j] * CHEQ[j] * 12 for j in range(3)]
check("SW: М2 базовый", sw["m2_year"][1], X["sw"]["m2_year"][1])
sw["m2_som"] = [sw["m2_year"][j] * sh_x[j] for j in range(3)]
# CR3/CR5/HHI
vis = [d[3] for d in I.SW_DOMAINS]; shs = [v / sum(vis) for v in vis]
srt = sorted(shs, reverse=True)
sw["shares"] = dict(zip([d[0] for d in I.SW_DOMAINS], shs))
sw["cr3"] = sum(srt[:3]) * 100; sw["cr5"] = sum(srt[:5]) * 100; sw["hhi"] = sum((s * 100) ** 2 for s in shs)
check("SW: HHI", sw["hhi"], X["sw"]["hhi_raw"]); check("SW: CR3", sw["cr3"], X["sw"]["cr3_raw"])
sw["hhi_min_check"] = sw["cr3"] ** 2 / 3
# проверка шкал конверсий (Р-39): значения SW-X против диапазонов М1 и М2
sw["scale_check"] = {
    "CR1 SW-X": cr1_x, "CR1 M1 (0.3–1/1–3/3–7 %)": ((0.003, 0.01), (0.01, 0.03), (0.03, 0.07)),
    "CR1 M2 (0.2–0.5/0.5–1.5/1.5–3 %)": ((0.002, 0.005), (0.005, 0.015), (0.015, 0.03)),
}
def inr(v, r): return r[0] - 1e-12 <= v <= r[1] + 1e-12
sw["cr1_in_m1"] = [inr(cr1_x[j], sw["scale_check"]["CR1 M1 (0.3–1/1–3/3–7 %)"][j]) for j in range(3)]
sw["cr1_in_m2"] = [inr(cr1_x[j], sw["scale_check"]["CR1 M2 (0.2–0.5/0.5–1.5/1.5–3 %)"][j]) for j in range(3)]
sw["cr2_in_m1"] = [inr(CR2[j], ((0.05, 0.15), (0.15, 0.30), (0.30, 0.50))[j]) for j in range(3)]
sw["cr2_in_m2"] = [inr(CR2[j], ((0.05, 0.10), (0.10, 0.25), (0.25, 0.40))[j]) for j in range(3)]
# чувствительность к составу выборки: только домены, значения которых подтверждены первой работой (plantuml.com, app.diagrams.net)
d2 = I.SW_DOMAINS[:2]
obs2 = sum(d[3] for d in d2) * GEO
sh2 = [d[3] / sum(x[3] for x in d2) for d in d2]
sw["two"] = dict(obs=obs2, market=[obs2 / cov_x[j] * cr1_x[j] * CR2[j] * CHEQ[j] * 12 for j in range(3)],
                 hhi=sum((s * 100) ** 2 for s in sh2), cr3=100.0, tam=sum(d[3] for d in d2))
R["sw"] = sw

# ============================================================ МП (маркетплейсы)
mp = {"rows": []}
rows = I.load_marketplaces()[1:]
def num(s):
    import re
    m = re.match(r"\s*([\d\s]+)", s.replace(" ", " "))
    return int(m.group(1).replace(" ", "")) if m and m.group(1).strip() else None
vs = []
for r in rows:
    plat, prod, url, inst, revs = r[0], r[1], r[2], r[3], r[4]
    n_inst, n_rev = num(inst), num(revs) if revs and revs[0].isdigit() else None
    mp["rows"].append([plat, prod, n_inst, n_rev, r[5], r[6][:80]])
    if plat.startswith("VS Marketplace") and n_inst and n_rev:
        vs.append((prod, n_inst, n_rev))
mp["vs_ratio"] = [(p, i, r, r / i) for p, i, r in vs]
mp["vs_ratio_median"] = statistics.median([x[3] for x in mp["vs_ratio"]]) if vs else None
mp["vs_installs_total"] = sum(i for _, i, _ in vs)
R["mp"] = mp

# ============================================================ сводка по уровням
R["summary"] = {
    "SOM": {
        "ПС-X (поиск)": ps["rev_year"], "ЦВ-X (воронка)": cv["rev_year"], "СЦ-X (Similarweb)": sc["som"],
        "ПК-X (SOM, сценарии)": [pk["scen"][k][2] for k in ("cautious", "base", "optimistic")],
        "ПЛ-X (достижимая выручка)": X["pl"]["scen_revenue"], "SW-X (SOM)": sw["som"], "SW-X вариант М2 (SOM)": sw["m2_som"],
    },
    "MARKET": {
        "ПК-X (SAM)": [pk["scen"][k][1] for k in ("cautious", "base", "optimistic")],
        "ПЛ-X (рынок)": X["pl"]["scen_market"], "СВ-X сверху вниз": sv["topdown"], "СВ-X снизу вверх": sv["bu_scen"],
        "СВ-X Similarweb + воронка": sv["sw_funnel"], "СЦ-X (рынок)": sc["market_rev"], "SW-X (рынок)": sw["market_year"],
        "SW-X вариант М2 (рынок)": sw["m2_year"],
    },
}
for lvl, d in list(R["summary"].items()):
    vals = list(d.values())
    R["summary"][lvl + "_stats"] = [min(v[0] for v in vals), statistics.mean(v[1] for v in vals), max(v[2] for v in vals)]

R["checks"] = chk
json.dump(R, open(os.path.join(HERE, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
bad = [c for c in chk if not c[3]]
print("Проверок сверки Python ↔ Excel:", len(chk), " расхождений:", len(bad))
for c in bad:
    print("  РАСХОЖДЕНИЕ", c)
for lvl in ("SOM", "MARKET"):
    print(lvl)
    for k, v in R["summary"][lvl].items():
        print("  %-32s" % k, " / ".join("%12.1f" % x for x in v))
    print("  stats min/avg/max:", [round(x, 1) for x in R["summary"][lvl + "_stats"]])
