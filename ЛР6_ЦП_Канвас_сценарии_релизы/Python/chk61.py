import lr6_xl as X, lr6_common as C, os
d=X.read(os.path.join(C.LAB6,"Excel","6_1_cennostnoe_predlozhenie_NotaCode.xlsx"),["Проблемы клиентов!K5:L10","Конкурентные решения!J5:K16","Ценностные предложения!K5:L5","Цифровой товар!K5:L5","Единица монетизации!H5:N6","Бизнес-модель!L5:L5","Проверка связности!G5:H6","Дашборд!A5:C10","Дашборд!E5:G14"])
for k in sorted(d): print(k[0][:12],k[1],k[2],d[k][:50])
