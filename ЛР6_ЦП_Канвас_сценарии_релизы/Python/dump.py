import sys, os, lr6_xl as X, lr6_common as C
# usage: dump.py книга.xlsx лист диапазон...
book = sys.argv[1]
if not os.path.isabs(book): book = os.path.join(C.LAB6, "Материалы", book)
d = X.read(book, sys.argv[2:])
for k in sorted(d): print("%s r%d c%d: %s" % (k[0], k[1], k[2], d[k][:130].replace("\n", " ")))
