"""Teach every Model-paper question: question, how to think, answer + real output. Phone PDF."""
import decimal, html, json, os, re, subprocess, sys
import pymysql
from model_content import S, DROP_USERS
from render_slides import highlight

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TMP = sys.argv[1]; os.makedirs(TMP, exist_ok=True)

# reuse the console runner/formatter from build_outputs_pdf.py without running that script
src = open(os.path.join(os.path.dirname(__file__), "build_outputs_pdf.py")).read()
exec(src[src.index("def connect"):src.index("# ------------------------------------------------------------------ run everything")])
CSS0 = src[src.index('CSS = """') + 9: src.index('"""', src.index('CSS = """') + 9)]
exec(src[src.index("WIDTH_PT"):src.index("toc = [")])

errors = []
def run_seq(db_holder, script):
    conn = connect(db_holder[0]); cur = conn.cursor(); steps = []
    for disp, ex in split(script):
        if ex is None: steps.append((disp, None)); continue
        out, err = execute(cur, ex)
        if err: errors.append(out)
        m = re.match(r"\s*USE\s+(\w+)", ex, re.I)
        if m: db_holder[0] = m.group(1)
        steps.append((disp, out))
    conn.close()
    return steps

subprocess.run(["mariadb"], input=(DROP_USERS + "".join(f"DROP DATABASE IF EXISTS {s['db']};" for s in S)).encode(), check=True)
for s in S:
    holder = [None]
    for it in s["items"]:
        it["steps"] = run_seq(holder, it["sql"])
    for i, (q, think, sql) in enumerate(s["also"]):
        s["also"][i] = (q, think, run_seq([s["db"]], sql))

CSS = CSS0 + """
.qbox{background:#1e3a8a;color:#fff;border-radius:2mm;padding:2.2mm 3mm;margin:6mm 0 2mm;font-weight:600;font-size:10pt;line-height:1.38;break-after:avoid}
.qbox .qn{display:inline-block;background:#fbbf24;color:#1e293b;border-radius:1mm;padding:0 1.5mm;margin-right:1.5mm;font-weight:800}
.think{background:#f5f3ff;border-left:2.5px solid #7c3aed;padding:1.5mm 2.5mm;margin:1mm 0 2mm;font-size:9.3pt;break-inside:avoid}
.think b{color:#6d28d9}.think ul{margin:0.5mm 0 0;padding-left:4mm}.think li{margin:0.5mm 0}
.setup{background:#f1f5f9;border:1px dashed #94a3b8;border-radius:2mm;padding:1.5mm 2.5mm;margin:5mm 0 1.5mm;font-size:9pt;color:#475569;break-after:avoid}
.tables{font-size:9.2pt;background:#fff7ed;border:1px solid #fed7aa;border-radius:2mm;padding:2mm 3mm;margin:0 0 2mm}
.tables div{font-family:'DejaVu Sans Mono',monospace;font-size:8.2pt;color:#7c2d12;margin:0.6mm 0}
.also{border-top:2px dashed #f59e0b;margin-top:6mm;padding-top:1mm}
.howto{font-size:9.6pt;background:#ecfeff;border:1px solid #a5f3fc;border-radius:2mm;padding:2.2mm 3mm;margin:2mm 0}
"""
def think_html(items, title="How to think"):
    return f'<div class="think"><b>{title}</b><ul>' + "".join(f"<li>{html.escape(t)}</li>" for t in items) + "</ul></div>"

b = f"""<div class="cover"><div class="k">SQL Lab Exam · Model Questions</div><h1>Every Model Question, Taught</h1>
<div class="s">All questions from <b>Model-questions – final.pdf</b>, in order. For each one: the exact question,
<b>how to think</b> (which recipe and why), the answer you type, and the <b>real output</b> it prints. Each schema runs from an empty database, top to bottom, exactly as you would in the lab.</div>
<div class="toc">{''.join(f"<div>{s['num']} · {html.escape(s['name'])}</div>" for s in S)}</div></div>
<h2>How to use this</h2>
<div class="howto"><b>1.</b> Read the purple question.<br><b>2.</b> Cover the answer and say which recipe you'd use.<br>
<b>3.</b> Check the <b>How to think</b> box, then the answer.<br><b>4.</b> Look at the output: that's what proves it worked.<br><br>
Grey <b>Setup</b> boxes are not asked in the question, but you need them so the next question has tables/data. In the exam, do the same: create parent tables and insert 2–3 rows yourself.<br><br>
At the end of each schema, an orange <b>Also asked in Sets 1–3</b> part covers the repeated questions that are not in the Model paper.</div>"""
qn = 0
for s in S:
    b += f'<h2>{s["num"]} · {html.escape(s["name"])}</h2><div class="tables"><b>Schema</b>' + "".join(f"<div>{html.escape(t)}</div>" for t in s["tables"]) + "</div>"
    local = 0
    for it in s["items"]:
        if it["setup"]:
            b += f'<div class="setup"><b>Setup (not asked):</b> {html.escape(it["think"][0])}</div>' + steps_html(it["steps"])
            continue
        qn += 1; local += 1
        b += f'<div class="qbox"><span class="qn">Q{local}</span>{html.escape(it["q"])}</div>' + think_html(it["think"]) + steps_html(it["steps"])
    if s["also"]:
        b += '<div class="also"></div>'
        for q, think, steps in s["also"]:
            b += f'<div class="qbox" style="background:#b45309"><span class="qn">ALSO</span>{html.escape(q)}</div>' + think_html(think) + steps_html(steps)

doc = f'<!doctype html><html><head><meta charset="utf-8"><title>Model Questions Taught</title><style>{CSS}</style></head><body>{b}</body></html>'
out = os.path.join(TMP, "6_Model_Questions_Taught.html"); open(out, "w").write(doc)
json.dump([[out, os.path.join(ROOT, "pdf", "6_Model_Questions_Taught_With_Outputs.pdf")]], open(os.path.join(TMP, "modeljobs.json"), "w"))
print("questions:", qn); print("errors shown:"); [print(" ", e[:110]) for e in errors]
