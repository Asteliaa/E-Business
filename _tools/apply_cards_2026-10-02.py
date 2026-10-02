# Заполняет карточки конкурентов ЛР4 данными от 02.10.2026 (реклама Google Ads Transparency, Similarweb Worldwide, Capterra).
# Повторный запуск безопасен.
import re

P = 'ЛР4_Пять_сил_Портера/ОТЧЕТ.md'
t = open(P, encoding='utf-8').read()

ADS = {  # объявлений в Беларуси, Google Ads Transparency Center, 02.10.2026
    'plantuml.com': 0, 'mermaidchart.com': 0, 'd2lang.com': 0, 'kroki.io': 0, 'planttext.com': 0, 'staruml.io': 0,
    'visual-paradigm.com': 0, 'sparxsystems.com': 0, 'bpmn.io': 0, 'stormbpmn.com': 0, 'app.diagrams.net': 0,
    'lucidchart.com': 6, 'creately.com': 0, 'miro.com': 23, 'excalidraw.com': 0, 'dbdiagram.io': 0, 'drawsql.app': 0,
    'eraser.io': 0,
}
SW = {  # Similarweb Worldwide, июнь - август 2026
    'eraser.io': ("2,18 млн визитов за 3 месяца, −5,16 % к прошлому месяцу (Similarweb Worldwide, 02.10.2026; доля Беларуси недоступна)",
                  "Direct 47,60 %, Organic Search 38,48 %, Referrals 3,33 %, Paid Search 0,01 % (Similarweb Worldwide, 02.10.2026)"),
    'lucidchart.com': ("lucid.app: 13,38 млн визитов за 3 месяца, −6,27 % к прошлому месяцу (Similarweb Worldwide, 02.10.2026; доля Беларуси недоступна)",
                       "Direct 62,57 %, Referrals 19,84 %, Organic Search 5,00 %, Paid Search 0,18 % (lucid.app, Similarweb Worldwide, 02.10.2026)"),
    'miro.com': ("визиты не снимались; каналы – Similarweb Worldwide, 02.10.2026",
                 "Direct 65,72 %, Organic Search 12,20 %, Referrals 7,84 %, Paid Search 0,65 % (Similarweb Worldwide, 02.10.2026)"),
    'app.diagrams.net': ("drawio.com: 7,19 млн визитов за 3 месяца, −9,21 % к прошлому месяцу (Similarweb Worldwide, 02.10.2026; доля Беларуси недоступна)",
                         "Organic Search 58,23 %, Direct 33,54 %, Referrals 5,45 %, платный поиск нет данных (drawio.com, Similarweb Worldwide, 02.10.2026)"),
    'mermaidchart.com': ("mermaid.ai: 6,27 млн визитов за 3 месяца, −15,42 % к прошлому месяцу (Similarweb Worldwide, 02.10.2026; доля Беларуси недоступна)",
                         "Direct 40,85 %, Referrals 31,38 %, Organic Search 14,40 %, Paid Search 3,98 % (mermaid.ai, Similarweb Worldwide, 02.10.2026)"),
}
BLOCK_RE = re.compile(r'(?m)^Таблица \d+ – Карточка конкурента: (\S+)\n\n(?:\|.*\n)+')

SW_OLD = "🔲 ДОСНЯТЬ: Similarweb (доступ закрыт, HTTP 403 30.09.2026)"
ADS_OLD = "🔲 ДОСНЯТЬ: Google Ads Transparency Center, LinkedIn Ad Library (не проверялись)"


def ads_text(dom):
    if dom in ADS:
        n = ADS[dom]
        s = f"Google Ads Transparency Center, Беларусь, 02.10.2026: {n} объявлений"
        if n == 0:
            s += " (платная реклама по домену не найдена)"
        return s + "; LinkedIn Ad Library недоступна без фильтра по компании"
    return "Google Ads Transparency Center по домену не снимался; LinkedIn Ad Library недоступна"


def fix(m):
    dom = m.group(1)
    b = m.group(0)
    lines = b.split('\n')
    out = []
    for ln in lines:
        if ln.startswith('| Трафик и динамика |') and dom in SW and SW_OLD in ln:
            ln = ln.replace(SW_OLD, SW[dom][0])
        if ln.startswith('| Каналы привлечения |') and dom in SW and SW_OLD in ln:
            ln = ln.replace(SW_OLD, SW[dom][1])
        if ln.startswith('| Рекламная активность |'):
            ln = ln.replace(ADS_OLD, ads_text(dom)).replace("рекламные библиотеки 🔲 ДОСНЯТЬ", ads_text(dom))
        if 'Capterra: 🔲 ДОСНЯТЬ' in ln:
            ln = ln.replace('Capterra: 🔲 ДОСНЯТЬ', 'Capterra: сайт закрыт проверкой безопасности (02.10.2026)')
        out.append(ln)
    return '\n'.join(out)


new = BLOCK_RE.sub(fix, t)
open(P, 'w', encoding='utf-8').write(new)
print('карточек обработано:', len(BLOCK_RE.findall(t)), 'изменено символов:', len(new) - len(t))
print('осталось 🔲 в ЛР4:', new.count('🔲'))
