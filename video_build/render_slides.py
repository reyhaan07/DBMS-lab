"""Turn content.py into one HTML file per slide (1920x1080)."""
import html, json, os, re, sys
from content import PARTS

OUT = sys.argv[1] if len(sys.argv) > 1 else "out"

KEYWORDS = r"""SELECT FROM WHERE GROUP BY HAVING ORDER ASC DESC AND OR NOT IN IS NULL LIKE BETWEEN AS ON
JOIN LEFT RIGHT INNER CROSS UNION CREATE TABLE DATABASE USE SHOW TABLES DESC INSERT INTO VALUES UPDATE SET
DELETE ALTER ADD CONSTRAINT PRIMARY KEY FOREIGN REFERENCES UNIQUE CHECK DEFAULT CASCADE DROP IF EXISTS
VIEW INDEX START TRANSACTION COMMIT ROLLBACK SAVEPOINT TO GRANT REVOKE ALL PRIVILEGES USER IDENTIFIED FOR
GRANTS DELIMITER PROCEDURE FUNCTION BEGIN END CALL RETURNS RETURN DETERMINISTIC THEN ELSE TRIGGER AFTER
BEFORE EACH ROW NEW OLD INT VARCHAR DECIMAL DATE DATETIME AUTO_INCREMENT COUNT SUM AVG MAX MIN NOW
autocommit import public class static void try catch new if else for print""".split()
KW = "|".join(sorted(set(KEYWORDS), key=len, reverse=True))

TOKEN = re.compile(
    r"(?P<ph>\{\{.*?\}\})"
    r"|(?P<com>--[^\n]*|#[^\n]*|//[ \t]+[A-Za-z][^\n]*|<!--.*?-->)"
    r"|(?P<str>'[^'\n]*'|\"[^\"\n]*\"|`[^`\n]*`)"
    r"|(?P<tag></?[\w:]+|/?>)"
    r"|(?P<kw>\b(?:" + KW + r")\b)"
    r"|(?P<num>\b\d+(?:\.\d+)?\b)"
)

def ph(text):
    return f'<span class="ph">{html.escape(text[2:-2])}</span>'

def esc_with_ph(text):
    out, pos = [], 0
    for m in re.finditer(r"\{\{.*?\}\}", text):
        out.append(html.escape(text[pos:m.start()])); out.append(ph(m.group())); pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)

def highlight(code):
    out, pos = [], 0
    for m in TOKEN.finditer(code):
        out.append(html.escape(code[pos:m.start()]))
        kind, val = m.lastgroup, m.group()
        if kind == "ph":
            out.append(ph(val))
        elif kind == "str":
            out.append(f'<span class="str">{esc_with_ph(val)}</span>')
        else:
            out.append(f'<span class="{kind}">{html.escape(val)}</span>')
        pos = m.end()
    out.append(html.escape(code[pos:]))
    return "".join(out)

def inline(text):
    """Bullets: make `SQL-looking` bits mono via simple heuristic on '→'."""
    t = esc_with_ph(text)
    return t.replace("→", '<span class="arrow">→</span>')

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1920px;height:1080px;background:#0f1420;color:#e8ecf4;font-family:'Inter',sans-serif;overflow:hidden;position:relative}
.top{position:absolute;left:0;right:0;top:0;height:8px;background:linear-gradient(90deg,#3b82f6,#22d3ee,#a78bfa)}
.hdr{position:absolute;left:70px;right:70px;top:46px;display:flex;align-items:baseline;gap:28px}
.tag{font-size:24px;font-weight:700;color:#0f1420;background:#22d3ee;padding:6px 16px;border-radius:8px;white-space:nowrap}
h1{font-size:54px;font-weight:800;letter-spacing:-0.5px;line-height:1.15}
.body{position:absolute;left:70px;right:70px;top:150px;bottom:80px;display:flex;gap:40px}
.code{flex:1;background:#161d2e;border:1px solid #26314a;border-radius:18px;padding:28px 34px;font-family:'DejaVu Sans Mono',monospace;white-space:pre;overflow:hidden;color:#dbe3f0}
.steps{width:440px;flex:none;display:flex;flex-direction:column;gap:18px}
.step{background:#1b2338;border-left:6px solid #a78bfa;border-radius:12px;padding:18px 22px;font-size:27px;line-height:1.35;color:#e8ecf4}
.step b{color:#a78bfa;font-weight:800;margin-right:8px}
ul{list-style:none;display:flex;flex-direction:column;gap:22px;width:100%;justify-content:center}
li{font-size:38px;line-height:1.35;background:#161d2e;border:1px solid #26314a;border-radius:14px;padding:20px 30px}
li.compact{font-size:33px;padding:16px 28px}
.kw{color:#60a5fa;font-weight:700}.str{color:#86efac}.com{color:#7c8aa5;font-style:italic}
.num{color:#fbbf24}.tag{}.code .tag{color:#f472b6;background:none;padding:0;font-size:inherit;font-weight:400}
.ph{color:#fb923c;font-style:italic;border-bottom:2px dashed #fb923c}
.arrow{color:#22d3ee;font-weight:800}
.foot{position:absolute;left:70px;right:70px;bottom:28px;display:flex;justify-content:space-between;font-size:22px;color:#7c8aa5}
.bar{position:absolute;left:0;bottom:0;height:8px;background:#22d3ee}
.title-wrap{position:absolute;inset:0;display:flex;flex-direction:column;justify-content:center;padding:0 140px;
 background:radial-gradient(circle at 80% 20%,#1e3a8a55,transparent 50%),radial-gradient(circle at 10% 90%,#6d28d955,transparent 45%)}
.title-wrap .kicker{font-size:34px;color:#22d3ee;font-weight:700;letter-spacing:2px;text-transform:uppercase;margin-bottom:26px}
.title-wrap h1{font-size:110px;line-height:1.05;margin-bottom:36px}
.title-wrap .sub{font-size:42px;color:#b6c2d9;line-height:1.35;max-width:1500px}
"""

def code_font(code, has_steps):
    lines = code.split("\n")
    width = (1780 - (480 if has_steps else 0)) - 70
    maxlen = max(len(l) for l in lines)
    height = 850 - 60
    fs = min(40, width / (0.602 * maxlen), height / (1.42 * len(lines)))
    return round(fs, 1)

def page(part, idx, total, s):
    foot = (f'<div class="foot"><span>SQL Lab Exam Crash Course · Part {part["num"]}: {html.escape(part["name"])}</span>'
            f'<span>{idx+1} / {total}</span></div><div class="bar" style="width:{(idx+1)/total*100:.2f}%"></div>')
    if s["kind"] == "title":
        inner = (f'<div class="title-wrap"><div class="kicker">Part {part["num"]} of {len(PARTS)}</div>'
                 f'<h1>{html.escape(s["title"])}</h1><div class="sub">{html.escape(s["sub"])}</div></div>')
    else:
        code = s.get("code")
        steps = s.get("steps") or (s.get("bullets") if code else None)
        right = ""
        if steps:
            right = '<div class="steps">' + "".join(
                f'<div class="step"><b>{i+1}</b>{inline(t)}</div>' for i, t in enumerate(steps)) + "</div>"
        if code:
            fs = code_font(code, bool(steps))
            left = f'<div class="code" style="font-size:{fs}px;line-height:1.42">{highlight(code)}</div>'
        else:
            bl = s["bullets"]
            cls = ' class="compact"' if len(bl) > 6 or max(len(b) for b in bl) > 70 else ""
            left = "<ul>" + "".join(f"<li{cls}>{inline(b)}</li>" for b in bl) + "</ul>"
        label = "RECIPE" if s["title"].startswith("RECIPE") else ("EXAMPLE" if s["title"].startswith("EXAMPLE") else f"PART {part['num']}")
        title = re.sub(r"^(RECIPE|EXAMPLE) · ", "", s["title"])
        inner = (f'<div class="hdr"><span class="tag">{label}</span><h1>{html.escape(title)}</h1></div>'
                 f'<div class="body">{left}{right}</div>')
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body><div class="top"></div>{inner}{foot}</body></html>'

manifest = []
for p in PARTS:
    d = os.path.join(OUT, f"part{p['num']}")
    os.makedirs(d, exist_ok=True)
    for i, s in enumerate(p["slides"]):
        fn = os.path.join(d, f"s{i:02d}.html")
        open(fn, "w").write(page(p, i, len(p["slides"]), s))
        manifest.append({"part": p["num"], "i": i, "html": os.path.abspath(fn), "say": s["say"]})
json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), indent=1)
print(len(manifest), "slides")
