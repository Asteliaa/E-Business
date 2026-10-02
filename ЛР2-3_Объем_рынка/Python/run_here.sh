#!/bin/bash
cd "$(dirname "$0")"
PYTHONIOENCODING=utf-8 python calc_all.py > ./calc0.log 2>&1; echo "calc0: $?"
for f in fill_ps fill_cv fill_pl fill_pk fill_sv fill_sc fill_sw; do
  PYTHONIOENCODING=utf-8 python $f.py > ./$f.log 2>&1; echo "$f: код $? ; без ошибок вычисления: $(grep -c '"errors": \[\]' ./$f.log)"
done
PYTHONIOENCODING=utf-8 python calc_all.py | head -2
PYTHONIOENCODING=utf-8 python make_figures.py > /dev/null && echo "рисунки готовы"
PYTHONIOENCODING=utf-8 python build_report.py | tail -3
echo ПЕРЕСЧЁТ_ЗАВЕРШЁН
