# -*- coding: utf-8 -*-
"""Сохраняет снимок листа 08_Дашборд (через Excel COM) в Скриншоты/дашборд_барьеров_входа.png."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from xl_com import Book, ROOT
out = os.path.join(ROOT, "Скриншоты", "дашборд_барьеров_входа.png")
import tempfile
b = Book()
try:
    ws = b.ws("08_Дашборд")
    ws.PageSetup.Orientation = 2
    ws.PageSetup.Zoom = False
    ws.PageSetup.FitToPagesWide = 1
    ws.PageSetup.FitToPagesTall = 1
    pdf = os.path.join(tempfile.gettempdir(), "dash08.pdf")
    ws.ExportAsFixedFormat(0, pdf)
finally:
    b.close(False)       # книга не сохраняется: параметры страницы не попадают в файл
import fitz
doc = fitz.open(pdf)
doc[0].get_pixmap(dpi=170).save(out)
print("ok", out)
