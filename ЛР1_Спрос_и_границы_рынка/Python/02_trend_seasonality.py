import csv
from pathlib import Path
from statistics import mean

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "Материалы_собранные" / "GT_Беларусь"

COMBINED_FILES = [
    ("ОСНОВНОЙ: UML, Беларусь (GT + Яндекс Вордстат)", DATA_DIR / "XLT_ввод_данных_ОСНОВНОЙ_UML_BY.csv"),
    ("ВТОРОЙ ВАРИАНТ: BPMN, Беларусь (GT + Яндекс Вордстат)", DATA_DIR / "XLT_ввод_данных_ВТОРОЙ_BPMN_BY.csv"),
]
GT_ONLY_FILES = [
    ("ТРЕТИЙ ВАРИАНТ (справочно): Mermaid, мир (только GT; ряд содержит омонимию -- фильм 'Русалочка', пик 2023-05/06)",DATA_DIR / "XLT_ввод_данных_ТРЕТИЙ_Mermaid_world.csv"),
]

MONTH_NAMES = ["январь", "февраль", "март", "апрель", "май", "июнь",
               "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь"]

W_GT = 0.5
W_YW = 0.5


def read_combined(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            period = row["Период"]
            gt = float(row["Google Trends, 0-100"])
            yw = row["Яндекс Вордстат, запросов"]
            yw = float(yw) if yw not in (None, "") else None
            rows.append({"period": period, "gt": gt, "yw": yw, "month_num": int(period[5:7])})
    return rows


def read_gt_only(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        r = csv.DictReader(f, delimiter=";")
        for row in r:
            period = row["Период"]
            value = float(row["Google Trends, 0-100"])
            rows.append({"period": period, "value": value, "month_num": int(period[5:7])})
    return rows


def slope(xs, ys):
    n = len(xs)
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den else 0.0


def fmt(v, nd=2):
    if v is None:
        return "н/д"
    if isinstance(v, str):
        return v
    return f"{v:.{nd}f}"


# ---------- EXCEL-логика (XL-Т), применяется к любому числовому ряду G ----------

def excel_style(g_series, month_nums):
    n = len(g_series)
    h = [None] * n
    for i in range(11, n):
        h[i] = mean(g_series[i - 11:i + 1])
    yt = [None] * n
    for i in range(n):
        if h[i] not in (None, 0):
            yt[i] = g_series[i] / h[i]
    month_yt = {m: [] for m in range(1, 13)}
    for i in range(n):
        if yt[i] is not None and yt[i] > 0:
            month_yt[month_nums[i]].append(yt[i])
    month_avg_yt = {m: (mean(v) if v else None) for m, v in month_yt.items()}
    valid_avgs = [v for v in month_avg_yt.values() if v is not None]
    overall_avg = mean(valid_avgs) if valid_avgs else None
    seasonal_index = {}
    if overall_avg:
        for m in range(1, 13):
            seasonal_index[m] = (month_avg_yt[m] / overall_avg) if month_avg_yt[m] is not None else None

    b4 = n
    b5 = mean(g_series[:12]) if b4 >= 12 else None
    b6 = mean(g_series[-12:]) if b4 >= 12 else None
    b7 = (b6 - b5) if (b5 is not None and b6 is not None) else None
    b8 = (b7 / b5) if (b7 is not None and b5) else None
    b9 = slope(list(range(1, n + 1)), g_series)
    if b8 is None:
        b10 = "недостаточно данных"
    elif b8 >= 0.15:
        b10 = "растущий тренд"
    elif b8 <= -0.15:
        b10 = "снижающийся тренд"
    else:
        b10 = "стабильный тренд"

    amp = max_m = min_m = None
    if valid_avgs:
        max_v = max(v for v in seasonal_index.values() if v is not None)
        min_v = min(v for v in seasonal_index.values() if v is not None)
        amp = max_v - min_v
        max_m = max((m for m in seasonal_index if seasonal_index[m] is not None), key=lambda m: seasonal_index[m])
        min_m = min((m for m in seasonal_index if seasonal_index[m] is not None), key=lambda m: seasonal_index[m])
    if amp is None:
        season_strength = "недостаточно данных"
    elif amp >= 0.30:
        season_strength = "выраженная сезонность"
    elif amp >= 0.15:
        season_strength = "умеренная сезонность"
    else:
        season_strength = "слабая сезонность"

    # Расчет!K = G / (H × D). Для месяцев, у которых сезонный индекс в шаблоне пуст
    # (COUNTIFS(Y/T > 0) = 0 — например, GT = 0 в оба года), Excel возвращает #ЗНАЧ!
    # (условие шаблона IFERROR(VLOOKUP(...),0)=0 не срабатывает на пустой строке);
    # здесь такие месяцы помечаются None.
    k = [None] * n
    for i in range(n):
        si = seasonal_index.get(month_nums[i])
        if h[i] not in (None, 0) and si not in (None, 0):
            k[i] = g_series[i] / (h[i] * si)
    # Деловые_циклы!B6 = INDEX(Расчет!K, Оценка_тренда!B4): коэффициент ПОСЛЕДНЕГО месяца ряда,
    # а не последний непустой. Если у последнего месяца K не определён, значение шаблона пустое.
    last_k = k[-1]
    if last_k is None:
        phase = "нет значения (у последнего месяца K не определён)"
    elif last_k < 0.90:
        phase = "ниже тренда"
    elif last_k > 1.10:
        phase = "выше тренда"
    else:
        phase = "норма"

    k_defined = [v for v in k if v is not None]
    return {
        "n": b4, "avg_first12": b5, "avg_last12": b6, "abs_change": b7,
        "rel_change": b8, "slope": b9, "trend_class": b10,
        "amplitude": amp, "season_strength": season_strength,
        "max_month": max_m, "min_month": min_m,
        "last_cycle_coef": last_k, "phase": phase,
        "k": k, "k_min": min(k_defined) if k_defined else None,
        "k_max": max(k_defined) if k_defined else None,
        "k_undefined_with_ma": sum(1 for i in range(n) if h[i] not in (None, 0) and k[i] is None),
        "avg_month_yt": overall_avg,
        "yt_count_by_month": {m: len(v) for m, v in month_yt.items()},
    }


# ---------- WORD-логика (ЦИКЛЫ) ----------

def word_style(g_series, month_nums):
    n = len(g_series)
    abs_change = g_series[-1] - g_series[0]
    rate_change = ((g_series[-1] / g_series[0]) - 1) * 100 if g_series[0] else None

    def moving_avg(window):
        ma = [None] * n
        for i in range(window - 1, n):
            ma[i] = mean(g_series[i - window + 1:i + 1])
        return ma

    ma3 = moving_avg(3)
    ma12 = moving_avg(12) if n >= 12 else [None] * n

    avg_last_year = mean(g_series[-12:]) if n >= 12 else None
    avg_prev_year = mean(g_series[-24:-12]) if n >= 24 else None
    change_pct = None
    if avg_last_year is not None and avg_prev_year:
        change_pct = (avg_last_year - avg_prev_year) / avg_prev_year * 100
    # ЦИКЛЫ табл. 7 не задаёт числовых порогов: тип динамики определяется по признакам
    # «скользящее среднее падает/растёт» и «пики становятся ниже/выше».
    ma12_valid = [v for v in ma12 if v is not None]
    ma12_falls = (ma12_valid[-1] < ma12_valid[0]) if len(ma12_valid) >= 2 else None
    peak_last = max(g_series[-12:]) if n >= 24 else None
    peak_prev = max(g_series[-24:-12]) if n >= 24 else None
    peaks_lower = (peak_last < peak_prev) if n >= 24 else None
    if change_pct is None:
        dyn_type = "недостаточно данных (< 24 месяцев)"
    elif ma12_falls and peaks_lower:
        dyn_type = "снижение интереса (MA12 падает, пики ниже)"
    elif ma12_falls is False and peaks_lower is False and change_pct > 0:
        dyn_type = "признаки роста (MA12 растёт, пики выше)"
    else:
        dyn_type = "признаки смешанные (см. MA12 и пики)"

    months_up = sum(1 for i in range(1, n) if g_series[i] > g_series[i - 1])
    share_growth_months = months_up / (n - 1) * 100 if n > 1 else None

    month_vals = {m: [] for m in range(1, 13)}
    for i in range(n):
        month_vals[month_nums[i]].append(g_series[i])
    month_avg = {m: (mean(v) if v else None) for m, v in month_vals.items()}
    valid = [v for v in month_avg.values() if v is not None]
    overall = mean(valid) if valid else None
    season_idx_word = {}
    if overall:
        for m in range(1, 13):
            season_idx_word[m] = (month_avg[m] / overall * 100) if month_avg[m] is not None else None

    def grade(v):
        if v is None:
            return "нет данных"
        if v < 80:
            return "низкий сезон"
        if v < 95:
            return "период умеренного спроса"
        if v <= 105:
            return "средний уровень"
        if v <= 120:
            return "повышенный интерес"
        return "пик сезона"

    season_grades = {m: grade(season_idx_word.get(m)) for m in range(1, 13)}

    # ЦИКЛЫ §6.2, шаги 3-4: ряд, скорректированный на сезонность (значение / (индекс/100)),
    # и 12-месячное скользящее среднее по очищенному ряду.
    adjusted = []
    for i in range(n):
        si = season_idx_word.get(month_nums[i])
        adjusted.append(g_series[i] / (si / 100) if si else None)
    ma12_adj = [None] * n
    for i in range(11, n):
        win = adjusted[i - 11:i + 1]
        if all(v is not None for v in win):
            ma12_adj[i] = mean(win)

    return {
        "ma3": ma3, "ma12": ma12, "adjusted": adjusted, "ma12_adj": ma12_adj,
        "ma12_falls": ma12_falls, "peak_last": peak_last, "peak_prev": peak_prev,
        "series": list(g_series),
        "abs_change": abs_change, "rate_change_pct": rate_change,
        "ma3_last": ma3[-1], "ma12_last": ma12[-1] if n >= 12 else None,
        "avg_last_year": avg_last_year, "avg_prev_year": avg_prev_year,
        "change_pct_yoy": change_pct, "dyn_type": dyn_type,
        "share_growth_months_pct": share_growth_months,
        "season_index": season_idx_word, "season_grades": season_grades,
        "month_avg": month_avg,
    }


def print_series(name, periods, wd):
    print(f"\n--- {name}: ряды ЦИКЛЫ §4.3 и §6.2 (MA3, MA12, очищенный от сезонности ряд, MA12 очищенного) ---")
    print(f"{'Месяц':>8} {'Значение':>9} {'MA3':>7} {'MA12':>7} {'Очищ.':>7} {'MA12 очищ.':>10}")
    for i, p in enumerate(periods):
        print(f"{p[:7]:>8} {fmt(wd['series'][i],1):>9} {fmt(wd['ma3'][i],1):>7} {fmt(wd['ma12'][i],1):>7} "
              f"{fmt(wd['adjusted'][i],1):>7} {fmt(wd['ma12_adj'][i],1):>10}")
    valid = [(periods[i][:7], v) for i, v in enumerate(wd['ma12_adj']) if v is not None]
    if len(valid) >= 2:
        print(f"MA12 очищенного ряда: {valid[0][0]} = {fmt(valid[0][1])} -> {valid[-1][0]} = {fmt(valid[-1][1])} "
              f"({fmt((valid[-1][1] / valid[0][1] - 1) * 100 if valid[0][1] else None)}%)")
    else:
        print("MA12 очищенного ряда не рассчитывается: в окне есть месяцы с нулевым сезонным индексом (нет данных GT).")


def print_block(name, ex, wd):
    print(f"\n--- {name}: EXCEL-логика (XL-Т) ---")
    print(f"Количество наблюдений: {ex['n']}")
    print(f"Средний первые/последние 12 мес.: {fmt(ex['avg_first12'])} / {fmt(ex['avg_last12'])}")
    rel = ex['rel_change']
    print(f"Относительное изменение: {fmt(rel*100 if rel is not None else None)}%  -> {ex['trend_class']}")
    print(f"Наклон (SLOPE): {fmt(ex['slope'], 4)}")
    print(f"Сезонность: амплитуда={fmt(ex['amplitude'])}, {ex['season_strength']}")
    if ex['max_month']:
        print(f"Месяц максимума: {MONTH_NAMES[ex['max_month']-1]}; минимума: {MONTH_NAMES[ex['min_month']-1]}")
    print(f"Текущий цикл. коэффициент (Деловые_циклы!B6, последний месяц ряда): {fmt(ex['last_cycle_coef'], 3)}; "
          f"фаза: {ex['phase']}")
    periods = ex.get("periods")
    k_line = "; ".join(f"{periods[i][:7]}={fmt(v, 3)}" for i, v in enumerate(ex["k"]) if i >= 11) if periods else ""
    print(f"K по месяцам с MA12: {k_line}")
    print(f"Мин./макс. K (Деловые_циклы!B8/B9): {fmt(ex['k_min'], 3)} / {fmt(ex['k_max'], 3)}; "
          f"месяцев с MA12, но без K (в Excel — #ЗНАЧ!): {ex['k_undefined_with_ma']}")
    single = sum(1 for m, c in ex["yt_count_by_month"].items() if c == 1)
    print(f"Среднее сезонных Y/T (AVERAGE(Сезонность!C4:C15)): {fmt(ex['avg_month_yt'], 3)}; "
          f"месяцев календаря, где сезонный индекс построен по одному Y/T: {single} "
          f"(для них K = G/(H·(Y/T)/ср.) = ср. Y/T — коэффициент вырожден)")

    print(f"\n--- {name}: WORD-логика (ЦИКЛЫ) ---")
    print(f"Абс. изменение (последнее-первое): {fmt(wd['abs_change'])}; темп: {fmt(wd['rate_change_pct'])}%")
    print(f"MA3 последнее: {fmt(wd['ma3_last'])}; MA12 последнее: {fmt(wd['ma12_last'])}")
    print(f"Среднее последнего/предыдущего года: {fmt(wd['avg_last_year'])} / {fmt(wd['avg_prev_year'])} "
          f"-> {fmt(wd['change_pct_yoy'])}%")
    print(f"Пик предыдущего/последнего года: {fmt(wd['peak_prev'])} / {fmt(wd['peak_last'])}; "
          f"MA12 падает: {wd['ma12_falls']} -> тип по ЦИКЛЫ табл. 7: {wd['dyn_type']}")
    print(f"Доля месяцев роста: {fmt(wd['share_growth_months_pct'])}%")
    print("Среднее значение месяца S_m и сезонный индекс по месяцам (x100), ЦИКЛЫ табл. 19:")
    for m in range(1, 13):
        si = wd['season_index'].get(m)
        print(f"  {MONTH_NAMES[m-1]:>10}: S_m={fmt(wd['month_avg'].get(m), 2)}; индекс {fmt(si, 1)}  "
              f"[{wd['season_grades'][m]}]")


def process_combined(label, path):
    print("=" * 72)
    print(label)
    print("=" * 72)
    rows = read_combined(path)
    month_nums = [r["month_num"] for r in rows]
    gt_series = [r["gt"] for r in rows]

    yw_vals = [r["yw"] for r in rows]
    yw_max = max(yw_vals)
    yw_norm = [(v / yw_max * 100) if yw_max else 0 for v in yw_vals]

    # Excel: сводный индекс G = GT*0.5 + YW_норм*0.5 (правило шаблона XL-Т)
    combined = [gt_series[i] * W_GT + yw_norm[i] * W_YW for i in range(len(rows))]

    periods = [r["period"] for r in rows]
    print(f"\n[Excel] Сводный индекс (G = GT*{W_GT} + YW_норм*{W_YW}):")
    ex_c = excel_style(combined, month_nums)
    ex_c["periods"] = periods
    print_block("Сводный индекс (Excel-правило)", ex_c, word_style(combined, month_nums))

    print(f"\n[ЦИКЛЫ §7 / ВЫГР: 'нельзя механически складывать'] -- отдельно GT и отдельно YW (норм.):")
    ex_gt = excel_style(gt_series, month_nums)
    ex_gt["periods"] = periods
    wd_gt = word_style(gt_series, month_nums)
    print_block("Только GT", ex_gt, wd_gt)
    print_series("Только GT", periods, wd_gt)

    ex_yw = excel_style(yw_norm, month_nums)
    ex_yw["periods"] = periods
    wd_yw = word_style(yw_norm, month_nums)
    print_block("Только YW (норм. к 0-100)", ex_yw, wd_yw)
    print_series("Только YW (норм. к 0-100)", periods, wd_yw)
    yw_raw = [v for v in yw_vals]
    print(f"\nYW в абсолютных числах: сумма первого года {sum(yw_raw[:12]):.0f}, последнего года {sum(yw_raw[-12:]):.0f} "
          f"({(sum(yw_raw[-12:]) / sum(yw_raw[:12]) - 1) * 100:.2f}%); первое/последнее значение {yw_raw[0]:.0f}/{yw_raw[-1]:.0f} "
          f"(абс. {yw_raw[-1] - yw_raw[0]:.0f}; темп {(yw_raw[-1] / yw_raw[0] - 1) * 100:.2f}%)")

    # Интегральная оценка по ЦИКЛЫ табл.14 (по динамике)
    gt_dyn = "рост" if ex_gt["rel_change"] and ex_gt["rel_change"] > 0 else "спад/стабильность"
    yw_dyn = "рост" if ex_yw["rel_change"] and ex_yw["rel_change"] > 0 else "спад/стабильность"
    print(f"\n[ЦИКЛЫ табл.14] GT: {gt_dyn}; YW: {yw_dyn} -> ", end="")
    if gt_dyn == "рост" and yw_dyn == "рост":
        print("оба источника растут -- высокая уверенность в росте интереса")
    elif gt_dyn != yw_dyn:
        print("источники расходятся -- проверить формулировки, период, регион")
    else:
        print("оба источника снижаются/стабильны -- переоценка идеи или сужение сегмента")


def process_gt_only(label, path):
    print("=" * 72)
    print(label)
    print("=" * 72)
    rows = read_gt_only(path)
    month_nums = [r["month_num"] for r in rows]
    g = [r["value"] for r in rows]
    ex = excel_style(g, month_nums)
    ex["periods"] = [r["period"] for r in rows]
    wd = word_style(g, month_nums)
    print_block(label, ex, wd)
    print_series(label, [r["period"] for r in rows], wd)


def main():
    print("=== 02_trend_seasonality.py ===")
    for label, path in COMBINED_FILES:
        process_combined(label, path)
        print()
    for label, path in GT_ONLY_FILES:
        process_gt_only(label, path)
        print()
    print("Замечание: доля месяцев с GT=0 велика (недели/месяцы 'недостаточно данных', а не 'нулевой спрос',")
    print("GT табл.5). Реальные данные Яндекс Вордстат (24 мес.) не содержат пропусков.")


if __name__ == "__main__":
    main()
