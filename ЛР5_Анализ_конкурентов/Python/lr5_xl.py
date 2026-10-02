# -*- coding: utf-8 -*-
"""Чтение значений из рабочих книг через PowerShell (COM). Python не открывает xlsx сам."""
import os
import subprocess
import tempfile

import lr5_common as C

PS = os.path.join(C.LAB5, "Excel_COM", "read_values.ps1")


def read(book, ranges):
    """ranges: список 'лист!A1:B2'. Возвращает dict {(лист, строка, столбец): строка}."""
    out = os.path.join(tempfile.gettempdir(), "lr5_read_%d.tsv" % os.getpid())
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS, "-Book", book,
           "-Ranges", "|".join(ranges), "-Out", out]
    r = subprocess.run(cmd, capture_output=True)
    if not os.path.exists(out):
        raise RuntimeError("Не удалось прочитать книгу: " + r.stdout.decode("cp866", "ignore") + r.stderr.decode("cp866", "ignore"))
    res = {}
    with open(out, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            sh, r_, c_, v = line.split("\t", 3)
            res[(sh, int(r_), int(c_))] = v.replace("\\n", "\n").replace("\\t", "\t")
    os.remove(out)
    return res


def fnum(x):
    try:
        return float(str(x).replace(",", "."))
    except (TypeError, ValueError):
        return None
