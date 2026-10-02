import os, subprocess, lr6_common as C
for f in sorted(os.listdir(os.path.join(C.LAB6, "Материалы"))):
    if f.endswith(".xlsx"):
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "sheets.ps1", "-Book", os.path.join(C.LAB6, "Материалы", f)], capture_output=True)
        print("==", f); print(open("sheets.out", encoding="utf-8").read())
