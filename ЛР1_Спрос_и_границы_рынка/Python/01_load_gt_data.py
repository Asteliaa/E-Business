import json
import csv
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
RAW_DIR = BASE / "Материалы_собранные" / "GT_Беларусь"
YW_DIR = BASE / "Материалы_собранные" / "Wordstat_Беларусь"
OUT_DIR = RAW_DIR

GT_PACKET6 = RAW_DIR / "GT_2026-09-29_BY_5y_packet6_UML_BPMN_monthly.json"  # keywords: UML(0), BPMN(1)
YW_UML = YW_DIR / "wordstat_uml_dinamika_RB_2024-09_2026-08.json"
YW_BPMN = YW_DIR / "wordstat_bpmn_dinamika_RB_2024-09_2026-08.json"

# Третий (доп.) вариант -- мировой прокси категории "diagram as code" (GT-only)
SECOND_FILE = RAW_DIR / "GT_2026-09-29_world_5y_packet1_monthly.json"
SECOND_KEYWORD = "Mermaid"
SECOND_KEYWORD_INDEX = 1


def load_gt_monthly(path, idx):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {m["month"]: m["avg"][idx] for m in data["monthly"]}


def load_yw_monthly(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {d["month"]: d["value"] for d in data["data"]}, data["query"]


def build_combined(gt_map, yw_map, keyword, region_label):
    """Строит помесячный ряд GT (0-100) + YW (абс. число запросов) за период,
    покрытый ОБОИМИ источниками (2024-09..2026-08, реальные данные Вордстата)."""
    months = sorted(set(gt_map.keys()) & set(yw_map.keys()))
    rows = []
    for m in months:
        rows.append({
            "period": m + "-01",
            "cluster": keyword,
            "gt": gt_map[m],
            "yw": yw_map[m],
            "region": region_label,
        })
    return rows


def write_combined_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Период", "Кластер запросов", "Google Trends, 0-100", "Яндекс Вордстат, запросов", "Регион/рынок", "Комментарий"])
        for r in rows:
            comment = "GT: недостаточно данных для этой недели/месяца" if r["gt"] == 0 else ""
            w.writerow([r["period"], r["cluster"], r["gt"], r["yw"], r["region"], comment])
    print(f"Записано: {path} ({len(rows)} строк, GT+YW объединены)")


def load_gt_only_monthly(path, idx):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    rows = [{"month": m["month"], "weeks": m["weeks"], "value": m["avg"][idx]} for m in data["monthly"]]
    return rows


def clean_edges(rows, label):
    if len(rows) < 3:
        return rows
    first, last = rows[0], rows[-1]
    print(f"[{label}] удалены неполные периоды по краям окна: {first['month']} ({first['weeks']} нед.), {last['month']} ({last['weeks']} нед.)")
    return rows[1:-1]


def write_gt_only_csv(rows, path, keyword, region_label):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["Период", "Кластер запросов", "Google Trends, 0-100", "Яндекс Вордстат, запросов", "Регион/рынок", "Комментарий"])
        for r in rows:
            comment = "" if r["value"] > 0 else "GT: недостаточно данных (hasData=false) для этой недели/месяца"
            w.writerow([r["month"] + "-01", keyword, r["value"], "", region_label, comment + "; Яндекс Вордстат не собран для этого запроса/территории"])
    print(f"Записано: {path} ({len(rows)} строк)")


def main():
    print("=== 01_load_gt_data.py ===")
    print(f"Источник GT: {RAW_DIR}")
    print(f"Источник YW (данные сняты 29.09.2026 через личный аккаунт Яндекс ID): {YW_DIR}\n")

    gt_uml = load_gt_monthly(GT_PACKET6, 0)
    gt_bpmn = load_gt_monthly(GT_PACKET6, 1)
    yw_uml, q1 = load_yw_monthly(YW_UML)
    yw_bpmn, q2 = load_yw_monthly(YW_BPMN)

    # ОСНОВНОЙ сценарий: UML, Беларусь, GT + YW объединены (24 месяца реального перекрытия)
    rows_uml = build_combined(gt_uml, yw_uml, "uml", "Беларусь")
    print(f"[ОСНОВНОЙ] UML, Беларусь: {len(rows_uml)} месяцев (GT+YW), период "
          f"{rows_uml[0]['period']}..{rows_uml[-1]['period']}")
    nonzero_gt = sum(1 for r in rows_uml if r["gt"] > 0)
    print(f"  GT с данными (>0): {nonzero_gt}/{len(rows_uml)} ({nonzero_gt/len(rows_uml)*100:.0f}%); "
          f"YW мин/макс: {min(r['yw'] for r in rows_uml)}/{max(r['yw'] for r in rows_uml)}")
    write_combined_csv(rows_uml, OUT_DIR / "XLT_ввод_данных_ОСНОВНОЙ_UML_BY.csv")

    # ВТОРОЙ ВАРИАНТ: BPMN, Беларусь, GT + YW объединены
    rows_bpmn = build_combined(gt_bpmn, yw_bpmn, "bpmn", "Беларусь")
    print(f"\n[ВТОРОЙ ВАРИАНТ] BPMN, Беларусь: {len(rows_bpmn)} месяцев (GT+YW), период "
          f"{rows_bpmn[0]['period']}..{rows_bpmn[-1]['period']}")
    nonzero_gt2 = sum(1 for r in rows_bpmn if r["gt"] > 0)
    print(f"  GT с данными (>0): {nonzero_gt2}/{len(rows_bpmn)} ({nonzero_gt2/len(rows_bpmn)*100:.0f}%); "
          f"YW мин/макс: {min(r['yw'] for r in rows_bpmn)}/{max(r['yw'] for r in rows_bpmn)}")
    write_combined_csv(rows_bpmn, OUT_DIR / "XLT_ввод_данных_ВТОРОЙ_BPMN_BY.csv")

    # ТРЕТИЙ ВАРИАНТ (доп., GT-only, мир): Mermaid, прокси категории "diagram as code"
    second_rows = load_gt_only_monthly(SECOND_FILE, SECOND_KEYWORD_INDEX)
    second_clean = clean_edges(second_rows, f"ТРЕТИЙ ВАРИАНТ (доп.): {SECOND_KEYWORD} (мир)")
    print(f"\n[ТРЕТИЙ ВАРИАНТ, доп.] {SECOND_KEYWORD}, мир: {len(second_clean)} месяцев после очистки (только GT; по Вордстату этот ряд не собирался)")
    write_gt_only_csv(second_clean, OUT_DIR / "XLT_ввод_данных_ТРЕТИЙ_Mermaid_world.csv", SECOND_KEYWORD, "мир (весь мир, без ограничения geo)")

    print("\nИтог: для UML и BPMN по Беларуси объединены оба источника (Google Trends и Яндекс Вордстат, 24 месяца).")
    print("Mermaid (весь мир) -- только GT, справочный ряд: пик мая-июня 2023 г. совпадает с премьерой фильма")
    print("'Русалочка' (омонимия), поэтому вывод о росте категории 'diagram as code' по нему ненадёжен.")


if __name__ == "__main__":
    main()
