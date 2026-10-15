"""Run every taught query and build a phone PDF showing each query with its real output."""
import textwrap, datetime, decimal, html, json, os, re, subprocess, sys
import pymysql
from outputs_content import SEED, SAMPLE, VIDEOS, PRE_DROP
from render_slides import highlight

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TMP = sys.argv[1]; os.makedirs(TMP, exist_ok=True)

def connect(db=None):
    return pymysql.connect(unix_socket="/run/mysqld/mysqld.sock", user="root", database=db, autocommit=True)

def run_script_raw(sql):
    subprocess.run(["mariadb"], input=sql.encode(), check=True)

def split(script):
    """Split like the mysql client: honours DELIMITER. Returns [(display, exec_or_None)]."""
    out, delim, buf = [], ";", []
    for line in script.split("\n"):
        m = re.match(r"\s*DELIMITER\s+(\S+)\s*$", line, re.I)
        if m and not buf:
            out.append((line.strip(), None)); delim = m.group(1); continue
        buf.append(line)
        if line.rstrip().endswith(delim):
            disp = "\n".join(buf).strip()
            ex = disp[: -len(delim)].strip()
            out.append((disp, ex)); buf = []
    if "".join(buf).strip():
        raise ValueError("unterminated statement: " + "\n".join(buf))
    return out

def fmt_val(v):
    if v is None: return "NULL"
    if isinstance(v, bytes): return v.decode()
    return str(v)

def is_num(v):
    return isinstance(v, (int, float, decimal.Decimal)) and not isinstance(v, bool)

KEEP = {"SHOW INDEX": ["Table", "Non_unique", "Key_name", "Seq_in_index", "Column_name"],
        "SHOW TRIGGERS": ["Trigger", "Event", "Table", "Timing"]}

def table(cols, rows, stmt):
    up = stmt.upper()
    for k, keep in KEEP.items():
        if up.startswith(k):
            idx = [cols.index(c) for c in keep]; cols = keep; rows = [[r[i] for i in idx] for r in rows]
    if up.startswith("SHOW GRANTS"):
        rows = [[re.sub(r" IDENTIFIED BY PASSWORD '[^']*'", "", fmt_val(r[0]))] for r in rows]
    srows = [[fmt_val(v) for v in r] for r in rows]
    w = [max([len(c)] + [len(r[i]) for r in srows]) for i, c in enumerate(cols)]
    sep = "+" + "+".join("-" * (x + 2) for x in w) + "+"
    lines = [sep, "| " + " | ".join(c.ljust(w[i]) for i, c in enumerate(cols)) + " |", sep]
    for r, raw in zip(srows, rows):
        lines.append("| " + " | ".join((v.rjust(w[i]) if is_num(raw[i]) else v.ljust(w[i])) for i, v in enumerate(r)) + " |")
    lines.append(sep)
    n = len(rows)
    lines.append(f"{n} row in set" if n == 1 else f"{n} rows in set")
    return "\n".join(lines)

def execute(cur, stmt):
    up = stmt.lstrip().upper()
    try:
        cur.execute(stmt)
    except pymysql.MySQLError as e:
        code, msg = e.args[0], e.args[1]
        return f"ERROR {code}: {msg}", True
    if up.startswith("USE "):
        return "Database changed", False
    if cur.description:
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        while cur.nextset():
            pass
        if not rows:
            return "Empty set", False
        return table(cols, [list(r) for r in rows], stmt), False
    n = max(cur.rowcount, 0)
    if up.startswith(("CREATE", "DROP", "ALTER", "SET", "START", "COMMIT", "ROLLBACK", "SAVEPOINT", "GRANT", "REVOKE")):
        n = 0
    return f"Query OK, {n} row{'' if n == 1 else 's'} affected", False

def run_item(db, script):
    conn = connect(db); cur = conn.cursor(); steps = []
    for disp, ex in split(script):
        if ex is None:
            steps.append((disp, None)); continue
        out, err = execute(cur, ex)
        if err:
            raise RuntimeError(f"Unexpected error in:\n{ex}\n{out}")
        steps.append((disp, out))
    conn.close()
    return steps

# ------------------------------------------------------------------ run everything
results = []   # (video, [(title, note, steps)])
run_script_raw(PRE_DROP + SEED)
sample = []
for db, tabs in SAMPLE:
    sample.append((db, run_item(db, "\n".join(f"SELECT * FROM {t};" for t in tabs))))
for v in VIDEOS:
    if v["reseed"]:
        run_script_raw(SEED)
    items = []
    for title, db, script, note in v["items"]:
        items.append((title, note, db, run_item(db, script)))
    results.append((v, items))

# XML validation outputs (video 8)
xml_dir = os.path.join(ROOT, "solutions", "xml")
xml_tmp = os.path.join(TMP, "xml"); os.makedirs(xml_tmp, exist_ok=True)
for f in ["students.xsd", "students.xml", "Validate.java"]:
    open(os.path.join(xml_tmp, f), "w").write(open(os.path.join(xml_dir, f)).read())
env = dict(os.environ); env.pop("JAVA_TOOL_OPTIONS", None)
subprocess.run(["javac", "Validate.java"], cwd=xml_tmp, check=True, env=env)
java_ok = subprocess.run(["java", "Validate"], cwd=xml_tmp, capture_output=True, text=True, env=env).stdout.strip()
good = open(os.path.join(xml_tmp, "students.xml")).read()
open(os.path.join(xml_tmp, "students.xml"), "w").write(good.replace("<name>Priya</name>\n", ""))
java_bad = subprocess.run(["java", "Validate"], cwd=xml_tmp, capture_output=True, text=True, env=env).stdout.strip()
py = os.path.join(xml_dir, "validate.py")

# ------------------------------------------------------------------ render
CSS = """
@page{size:115mm 200mm;margin:7mm 5mm 9mm 5mm}
*{box-sizing:border-box}
body{font-family:'Inter',sans-serif;font-size:10.2pt;line-height:1.42;color:#1a2233;margin:0}
h1{font-size:24pt;line-height:1.1;margin:0 0 4mm;color:#0f172a}
h2{font-size:13pt;margin:0 0 3mm;padding:2mm 3mm;background:#1e3a8a;color:#fff;border-radius:2mm;break-before:page;break-after:avoid}
h3{font-size:10.8pt;margin:5mm 0 1.5mm;color:#1e3a8a;break-after:avoid}
.cover{height:178mm;display:flex;flex-direction:column;justify-content:center;break-after:page}
.k{color:#0891b2;font-weight:800;letter-spacing:1px;font-size:9pt;text-transform:uppercase}
.s{color:#475569;font-size:10.5pt}
.toc{margin-top:7mm;font-size:9.6pt}.toc div{padding:1.1mm 0;border-bottom:1px solid #e2e8f0}
.cmd{font-family:'DejaVu Sans Mono',monospace;white-space:pre-wrap;word-break:break-word;background:#f1f5fb;border:1px solid #d6dfee;
 border-radius:1.6mm 1.6mm 0 0;padding:1.6mm 2.4mm;margin:1.6mm 0 0;font-size:7.6pt;line-height:1.38;break-after:avoid}
.cmd.solo{border-radius:1.6mm}
.prompt{color:#7c3aed;font-weight:700}.cont{color:#94a3b8}
.out{font-family:'DejaVu Sans Mono',monospace;white-space:pre;background:#0f172a;color:#e2e8f0;border-radius:0 0 1.6mm 1.6mm;
 padding:1.6mm 2.4mm;margin:0 0 1.6mm;line-height:1.3;overflow:hidden;break-inside:avoid}
.out.err{color:#fca5a5}
.kw{color:#1d4ed8;font-weight:700}.str{color:#15803d}.com{color:#6b7280;font-style:italic}.num{color:#b45309}.tag{color:#be185d}
.note{font-size:9.2pt;color:#0f3d4a;background:#ecfeff;border-left:2.5px solid #06b6d4;padding:1.3mm 2.3mm;margin:1mm 0 2mm;break-before:avoid}
.intro{font-size:9.6pt;background:#fff7ed;border:1px solid #fed7aa;border-radius:2mm;padding:2.2mm 3mm;margin:2mm 0}
.db{font-size:8.8pt;color:#64748b;margin:0.5mm 0}
"""
WIDTH_PT = (115 - 10) / 25.4 * 72 - 14   # usable width in pt minus padding

def out_block(text, err=False):
    longest = max(len(l) for l in text.split("\n"))
    fs = min(7.6, WIDTH_PT / (0.602 * max(longest, 1)))
    return f'<div class="out{" err" if err else ""}" style="font-size:{fs:.2f}pt">{html.escape(text)}</div>'

def cmd_block(disp, solo):
    lines = highlight(disp).split("\n")
    body = '<span class="prompt">mysql&gt; </span>' + lines[0] + "".join("\n" + '<span class="cont">    -&gt; </span>' + l for l in lines[1:])
    return f'<div class="cmd{" solo" if solo else ""}">{body}</div>'

def steps_html(steps):
    h = ""
    for disp, out in steps:
        h += cmd_block(disp, out is None)
        if out is not None:
            h += out_block(out, out.startswith("ERROR"))
    return h

toc = ["0 · Sample data used for every output"] + [f"Video {v['num']} · {v['title']}" for v, _ in results]
toc.insert(len(toc) - 1, "Video 8 · XML + XSD validation")
b = f"""<div class="cover"><div class="k">SQL Lab Exam · Outputs</div><h1>Every Query with Its Output</h1>
<div class="s">All the queries taught in Videos 2–9, run on real sample data. Each query is shown the way you type it at the
<b>mysql&gt;</b> prompt, followed by exactly what the screen prints.</div>
<div class="toc">{''.join(f'<div>{html.escape(t)}</div>' for t in toc)}</div></div>"""

b += '<h2>0 · Sample data used for every output</h2>'
b += ('<div class="intro">These are the rows inside each table before the queries run. Look back here to see <b>why</b> a query '
      'gives its answer. Your exam data will be different, so the numbers will differ, but the <b>shape</b> of the output is the same. '
      'Outputs were produced on MariaDB, which behaves like MySQL; the only difference you might see is an error number '
      '(a CHECK failure is 3819 in MySQL 8 and 4025 in MariaDB).</div>')
for db, steps in sample:
    b += f"<h3>Database: {db}</h3>" + steps_html([(f"USE {db};", "Database changed")] + steps)

for v, items in results:
    if v["num"] == 9:
        b += '<h2>Video 8 · XML + XSD validation</h2>'
        b += ('<div class="intro">XML is checked with a program, not at the mysql&gt; prompt. These are the real outputs of '
              '<b>Validate.java</b> (see the Full Solutions PDF for the three files).</div>')
        b += "<h3>Valid XML</h3>" + '<div class="cmd">$ javac Validate.java\n$ java Validate</div>' + out_block(java_ok)
        b += ("<h3>Broken XML (deleted Priya's &lt;name&gt; tag)</h3>" + '<div class="cmd">$ java Validate</div>' + out_block(textwrap.fill(java_bad, 62), True)
              + '<div class="note">The validator says exactly what is wrong: it expected &lt;name&gt; but found &lt;dept&gt;. '
                'Showing both the valid and the invalid run proves the XSD really checks the XML.</div>')
    b += f'<h2>Video {v["num"]} · {html.escape(v["title"])}</h2>'
    if v["num"] == 4:
        b += ('<div class="intro">Each block starts from the original sample data. Watch the SELECT outputs: they prove what '
              'COMMIT keeps and what ROLLBACK undoes.</div>')
    for title, note, db, steps in items:
        b += f"<h3>{html.escape(title)}</h3>"
        if db:
            b += f'<div class="db">database: {db}</div>'
        b += steps_html(steps)
        if note:
            b += f'<div class="note">{html.escape(note)}</div>'

doc = f'<!doctype html><html><head><meta charset="utf-8"><title>SQL Queries with Outputs</title><style>{CSS}</style></head><body>{b}</body></html>'
src = os.path.join(TMP, "4_SQL_Queries_With_Outputs.html"); open(src, "w").write(doc)
json.dump([[src, os.path.join(ROOT, "pdf", "4_SQL_Queries_With_Outputs.pdf")]], open(os.path.join(TMP, "outjobs.json"), "w"))
print("items:", sum(len(i) for _, i in results))
