import sys, subprocess, os, lr6_common as C
book = sys.argv[1]
if not os.path.isabs(book): book = os.path.join(C.LAB6, "Материалы", book)
ps = """$xl=New-Object -ComObject Excel.Application;$xl.Visible=$false;$xl.DisplayAlerts=$false;$sb=New-Object System.Text.StringBuilder
try{$wb=$xl.Workbooks.Open('%s',0,$true)
foreach($a in '%s'.Split('|')){$p=$a.Split('!');$ws=$wb.Worksheets.Item($p[0]);foreach($c in $ws.Range($p[1]).Cells){$f=[string]$c.Formula;$k=$(if($f.StartsWith('=')){'F'}else{'V'});[void]$sb.AppendLine($p[0]+'!'+$c.Address($false,$false)+' '+$k+' '+$f.Substring(0,[Math]::Min(70,$f.Length)))}}
[IO.File]::WriteAllText('fchk.out',$sb.ToString(),(New-Object System.Text.UTF8Encoding($false)));$wb.Close($false)}finally{$xl.Quit()}""" % (book, sys.argv[2])
open("fchk.ps1", "w", encoding="utf-8-sig").write(ps)
subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "fchk.ps1"], capture_output=True)
print(open("fchk.out", encoding="utf-8").read())
