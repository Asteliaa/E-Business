# -*- coding: utf-8 -*-
"""Сбор текстовых признаков со страниц конкурентов (запрос curl-типа, 30.09-01.10.2026). Сырые извлечения - в Материалы_собранные."""
import json, os, re, ssl, sys, urllib.request, datetime
import lr5_common as C
OUT = os.path.join(C.LAB5, "Материалы_собранные")
PAGES = {
 "plantuml.com": ["https://plantuml.com/", "https://plantuml.com/guide", "https://plantuml.com/faq", "https://plantuml.com/running", "https://plantuml.com/download", "https://plantuml.com/class-diagram", "https://plantuml.com/ie-diagram", "https://plantuml.com/activity-diagram-beta"],
 "mermaid.js.org": ["https://mermaid.js.org/", "https://mermaid.js.org/intro/", "https://mermaid.js.org/intro/getting-started.html", "https://mermaid.js.org/ecosystem/integrations-community.html", "https://mermaid.js.org/syntax/classDiagram.html", "https://mermaid.js.org/syntax/entityRelationshipDiagram.html", "https://mermaid.js.org/syntax/flowchart.html"],
 "mermaidchart.com": ["https://www.mermaidchart.com/", "https://www.mermaidchart.com/plans", "https://mermaid.ai/pricing", "https://docs.mermaidchart.com/"],
 "stormbpmn.com": ["https://stormbpmn.com/", "https://stormbpmn.com/pricing", "https://stormbpmn.com/tariffs", "https://stormbpmn.com/about", "https://stormbpmn.com/docs", "https://stormbpmn.com/blog"],
 "app.diagrams.net": ["https://www.drawio.com/", "https://www.drawio.com/features", "https://www.drawio.com/doc/", "https://www.drawio.com/integrations", "https://www.drawio.com/blog", "https://www.drawio.com/trust/security"],
 "lucidchart.com": ["https://www.lucidchart.com/", "https://lucid.app/pricing/lucidchart", "https://www.lucidchart.com/pages/templates", "https://www.lucidchart.com/pages/security"],
 "eraser.io": ["https://www.eraser.io/", "https://www.eraser.io/pricing", "https://docs.eraser.io/docs", "https://www.eraser.io/ai", "https://www.eraser.io/changelog", "https://www.eraser.io/diagramgpt", "https://docs.eraser.io/"],
 "whimsical.com": ["https://whimsical.com/", "https://whimsical.com/pricing", "https://whimsical.com/features/flowcharts", "https://whimsical.com/security", "https://whimsical.com/templates", "https://whimsical.com/ai", "https://whimsical.com/diagrams"],
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
ctx = ssl.create_default_context()
KW = {"free": r"\bfree\b", "trial": r"free trial|try for free|14-day|30-day|trial", "enterprise": r"enterprise", "api": r"\bAPI\b", "export": r"export", "import": r"import",
      "collab": r"collaborat|real-time|realtime", "templates": r"template", "versions": r"version history|revision|history", "security": r"security|SOC ?2|GDPR|ISO 27001|SSO|SAML",
      "ai": r"\bAI\b|artificial intelligence|generative", "integr": r"integrat|plugin|extension", "docs": r"documentation|docs\b|guide|tutorial", "support": r"support|help center|contact",
      "privacy": r"privacy|terms|cookie", "customers": r"customers|trusted by|case stud|testimonial|reviews|users", "pricing": r"pricing|price|per month|/mo|per user|USD|\$ ?\d", "roadmap": r"roadmap|changelog|release notes|what's new",
      "idef": r"IDEF", "dfd": r"bDFDb|data flow", "petri": r"Petri|Петри", "validate": r"validat|lint|syntax check|error check",
      "uml": r"\bUML\b", "bpmn": r"\bBPMN\b", "erd": r"\bER\b|entity.relationship|ERD", "code": r"diagram.as.code|text|markdown|DSL|syntax", "opensource": r"open.source|github"}
def fetch(u):
    try:
        req = urllib.request.Request(u, headers={"User-Agent": UA, "Accept-Language": "en,ru;q=0.8"})
        with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
            raw = r.read(1500000)
            cs = r.headers.get_content_charset() or "utf-8"
            return r.status, r.geturl(), raw.decode(cs, "ignore")
    except urllib.error.HTTPError as e:
        return e.code, u, ""
    except Exception as e:
        return 0, u, "ERR " + str(e)[:80]
def text_of(h):
    h = re.sub(r"(?is)<(script|style|noscript|svg).*?</\1>", " ", h)
    t = re.sub(r"(?s)<[^>]+>", " ", h)
    t = re.sub(r"&nbsp;|&#160;", " ", t); t = re.sub(r"&amp;", "&", t)
    return re.sub(r"\s+", " ", t).strip()
res = {}
for dom, urls in PAGES.items():
    res[dom] = []
    for u in urls:
        st, fin, h = fetch(u)
        rec = {"url": u, "final": fin, "status": st, "len": len(h)}
        if st == 200 and h and not h.startswith("ERR"):
            t = text_of(h)
            m = re.search(r"(?is)<title[^>]*>(.*?)</title>", h); rec["title"] = re.sub(r"\s+", " ", m.group(1)).strip() if m else None
            m = re.search(r'(?is)<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']', h) or re.search(r'(?is)<meta[^>]+content=["\'](.*?)["\'][^>]+name=["\']description["\']', h)
            rec["description"] = m.group(1).strip() if m else None
            rec["h"] = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x)).strip() for x in re.findall(r"(?is)<h[1-3][^>]*>(.*?)</h[1-3]>", h)][:25]
            rec["kw"] = {k: len(re.findall(p, t, re.I)) for k, p in KW.items()}
            rec["prices"] = sorted(set(re.findall(r"\$\s?\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?\s?(?:USD|EUR|€|\$)", t)))[:15]
            rec["text_len"] = len(t)
        res[dom].append(rec)
        print(dom, st, len(h), u, flush=True)
json.dump({"fetched": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "method": "HTTP GET (urllib), извлечение заголовков, метаданных и счётчиков ключевых слов", "data": res},
          open(os.path.join(OUT, "sajty_konkurentov_stranicy_2026-10-01.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
