#!/bin/bash
# Полный пересчёт: заполнение Excel-копий, сверка, рисунки, отчёт
cd "$(dirname "$0")"
PY="E:/VisualDSL_Tools/Python311/python.exe"
for f in fill_ps fill_cv fill_pl fill_pk fill_sv fill_sc fill_sw; do
  "$PY" $f.py > /tmp/$f.log 2>&1; echo "$f: код $? ; ошибок вычисления: $(grep -c '"errors": \[\]' /tmp/$f.log) (1 = нет ошибок)"
done
"$PY" calc_all.py | head -2
"$PY" make_figures.py > /dev/null && echo "рисунки готовы"
"$PY" build_report.py
echo ПОЛНЫЙ_ПЕРЕСЧЁТ_ЗАВЕРШЁН
