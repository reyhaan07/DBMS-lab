"""Build phone-friendly PDFs: cheat sheet, study notes (from the videos), full solutions."""
import glob, html, os, re, subprocess, sys, json
from content import PARTS
from render_slides import highlight, inline

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "pdf")
TMP = sys.argv[1]
os.makedirs(OUT, exist_ok=True); os.makedirs(TMP, exist_ok=True)

CSS = """
@page{size:105mm 190mm;margin:7mm 6mm 9mm 6mm}
*{box-sizing:border-box}
body{font-family:'Inter',sans-serif;font-size:10.5pt;line-height:1.45;color:#1a2233;margin:0}
h1{font-size:19pt;line-height:1.15;margin:0 0 4mm;color:#0f172a}
h2{font-size:13.5pt;margin:6mm 0 2.5mm;padding:2mm 3mm;background:#1e3a8a;color:#fff;border-radius:2mm;break-after:avoid}
h3{font-size:11pt;margin:4.5mm 0 1.5mm;color:#1e3a8a;break-after:avoid}
p{margin:1.5mm 0}
.cover{height:170mm;display:flex;flex-direction:column;justify-content:center;break-after:page}
.cover .k{color:#0891b2;font-weight:800;letter-spacing:1px;font-size:9pt;text-transform:uppercase}
.cover h1{font-size:26pt}
.cover .s{color:#475569;font-size:11pt}
.toc{font-size:10pt}.toc div{padding:1.2mm 0;border-bottom:1px solid #e2e8f0}
pre{font-family:'DejaVu Sans Mono',monospace;font-size:7.6pt;line-height:1.38;background:#f1f5fb;border:1px solid #d6dfee;
 border-radius:2mm;padding:2.5mm 3mm;margin:2mm 0;white-space:pre-wrap;word-break:break-word;color:#1a2233}
pre.big{font-size:8.4pt}
.kw{color:#1d4ed8;font-weight:700}.str{color:#15803d}.com{color:#6b7280;font-style:italic}.num{color:#b45309}
.tag{color:#be185d}.ph{color:#c2410c;font-style:italic;border-bottom:1px dashed #c2410c}
.arrow{color:#0891b2;font-weight:800}
pre .com.q{color:#7c2d12;font-style:normal;font-weight:700;background:#fff3e0;display:inline-block;margin-top:1.5mm}
ol.steps,ul.pts{margin:1.5mm 0;padding-left:5mm}ol.steps li,ul.pts li{margin:0.8mm 0}
ol.steps li::marker{color:#7c3aed;font-weight:800}
.say{font-size:9.6pt;color:#334155;background:#fafafa;border-left:2.5px solid #22d3ee;padding:1.5mm 2.5mm;margin:2mm 0}
table{border-collapse:collapse;width:100%;font-size:8.8pt;margin:2mm 0}
td{border:1px solid #d6dfee;padding:1.4mm 1.8mm;vertical-align:top}
td:first-child{width:42%;background:#f8fafc;font-weight:600}
td code,li code,p code{font-family:'DejaVu Sans Mono',monospace;font-size:8pt;color:#1d4ed8}
.card{break-inside:auto;margin-bottom:3mm}
.tip{background:#ecfeff;border:1px solid #a5f3fc;border-radius:2mm;padding:2mm 3mm;font-size:9.6pt;margin:2mm 0}
"""

def doc(title, body):
    return f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'

def cover(kicker, title, sub, toc=None):
    t = ""
    if toc:
        t = '<div class="toc" style="margin-top:8mm">' + "".join(f"<div>{html.escape(x)}</div>" for x in toc) + "</div>"
    return f'<div class="cover"><div class="k">{kicker}</div><h1>{html.escape(title)}</h1><div class="s">{html.escape(sub)}</div>{t}</div>'

def code(c, big=False):
    h = highlight(c)
    # make question comments ("-- Q:", "-- Insert ...") stand out
    return f'<pre class="{"big" if big else ""}">{h}</pre>'

def md_inline(t):
    t = html.escape(t)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", t)

# ------------------------------------------------------------------ 1. CHEAT SHEET
def cheatsheet():
    b = cover("SQL Lab Exam", "One-Page Cheat Sheet", "Read this the morning of the exam. Templates + word-to-SQL dictionary + error fixes.")
    b += "<h2>The 5-step method (any table)</h2><ol class='steps'>" + "".join(f"<li>{md_inline(x)}</li>" for x in [
        "Read the schema. Mark PKs and FKs. The table with 2 FKs is the middle / child table.",
        "Split the question at every full stop. Each sentence = one SQL statement.",
        "Spot the keyword and pick the recipe below.",
        "Fill the template with the new table / column names.",
        "Insert 2–3 sample rows yourself, run it, and show `SELECT * FROM ...;`"]) + "</ol>"
    b += "<h2>Golden rules</h2><ul class='pts'>" + "".join(f"<li>{md_inline(x)}</li>" for x in [
        "Every statement ends with `;`", "Text and dates in single quotes: `'Chennai'`  `'2024-05-10'`",
        "Numbers without quotes: `8.5`  `75000`", "Create parent tables first, child (FK) tables after",
        "Insert parent rows before child rows", "ID like C1 / F1 → `VARCHAR(10)`, not INT",
        "Money → `DECIMAL(10,2)`, CGPA → `DECIMAL(4,2)`, rating → `DECIMAL(2,1)`"]) + "</ul>"
    rows = [("for each / per", "GROUP BY col"), ("having more than N", "HAVING COUNT(*) > N"),
            ("greater than average", "WHERE c > (SELECT AVG(c) FROM t)"), ("equal to maximum", "WHERE c = (SELECT MAX(c) FROM t)"),
            ("at least one", "WHERE id IN (SELECT id FROM other)"), ("never / have not", "WHERE id NOT IN (SELECT id FROM other)"),
            ("of that same X", "correlated: ... WHERE b2.X = b1.X"), ("include those who have not", "LEFT JOIN (keep-all table first)"),
            ("every A and every B, blanks", "LEFT JOIN ... UNION ... RIGHT JOIN"), ("all possible combinations", "CROSS JOIN"),
            ("pairs in the same ...", "SELF JOIN with e1.id < e2.id"), ("descending / highest first", "ORDER BY c DESC"),
            ("count / total / average", "COUNT(*) / SUM(c) / AVG(c)"), ("highest / lowest", "MAX(c) / MIN(c)"),
            ("increase by 10%", "SET c = c * 1.10"), ("add ₹500", "SET c = c + 500")]
    b += "<h2>Question words → SQL</h2><table>" + "".join(
        f"<tr><td>\"{html.escape(a)}\"</td><td><code>{html.escape(c)}</code></td></tr>" for a, c in rows) + "</table>"
    sections = [
        ("Create table + constraints", """CREATE DATABASE db;
USE db;

CREATE TABLE T (
  id    INT PRIMARY KEY,
  name  VARCHAR(50) NOT NULL UNIQUE,
  sal   DECIMAL(10,2) CHECK (sal > 20000),
  cgpa  DECIMAL(4,2) CHECK (cgpa BETWEEN 0 AND 10),
  price DECIMAL(6,2) DEFAULT 150,
  pid   INT,
  FOREIGN KEY (pid) REFERENCES P(pid)
      ON DELETE CASCADE        -- or ON UPDATE CASCADE
);
ALTER TABLE T ADD CONSTRAINT fk1
  FOREIGN KEY (pid) REFERENCES P(pid);
DESC T;"""),
        ("Insert / update / delete", """INSERT INTO T VALUES (1, 'A', 30000, 8.5, 200, 5);
INSERT INTO T (id, name, sal, pid)
  VALUES (2, 'B', 40000, 5);        -- DEFAULT used
UPDATE T SET sal = 75000 WHERE name = 'Meena';
UPDATE T SET sal = sal * 1.10;      -- +10%
DELETE FROM T WHERE id = 2;
-- FK insert fails (ERROR 1452): parent value
-- does not exist = referential integrity"""),
        ("Select order", """SELECT   cols
FROM     t
WHERE    row condition
GROUP BY col
HAVING   COUNT(*) > 1      -- condition with COUNT/SUM/AVG
ORDER BY col DESC;"""),
        ("Joins", """-- 2 tables
SELECT e.EmpName, d.DeptName
FROM Employee e JOIN Department d ON e.DeptID = d.DeptID;
-- 3 tables: start from the middle table
SELECT p.PatientName, d.DoctorName
FROM Appointment a
JOIN Patient p ON a.PatientID = p.PatientID
JOIN Doctor  d ON a.DoctorID  = d.DoctorID;
-- LEFT / FULL OUTER / CROSS / SELF
... FROM A a LEFT JOIN B b ON a.id = b.id;
SELECT .. LEFT JOIN .. UNION SELECT .. RIGHT JOIN ..;
SELECT * FROM A CROSS JOIN B;
SELECT e1.n, e2.n FROM E e1 JOIN E e2
  ON e1.d = e2.d AND e1.id < e2.id;"""),
        ("Transactions", """SET autocommit = 0;
START TRANSACTION; ...changes...; COMMIT;

START TRANSACTION; ...change...;
SELECT * FROM t; ROLLBACK; SELECT * FROM t;

START TRANSACTION;
A;  SAVEPOINT sp1;  B;
ROLLBACK TO sp1;    -- B undone, A kept
COMMIT;"""),
        ("Grant / revoke", """CREATE USER 'u'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT, INSERT ON db.T TO 'u'@'localhost';
REVOKE INSERT ON db.T FROM 'u'@'localhost';
GRANT ALL PRIVILEGES ON db.T TO 'u'@'localhost';
SHOW GRANTS FOR 'u'@'localhost';"""),
        ("View + index", """CREATE VIEW V AS
SELECT ... FROM ... JOIN ... ON ...;
SELECT * FROM V;
CREATE INDEX idx_t_col ON T(col);
SHOW INDEX FROM T;"""),
        ("Procedure / function", """DELIMITER //
CREATE PROCEDURE p(IN x INT)
BEGIN
  SELECT * FROM T WHERE id = x;
END //
CREATE FUNCTION f(a INT, b INT)
RETURNS INT DETERMINISTIC
BEGIN
  RETURN a + b;
END //
DELIMITER ;
CALL p(1);   SELECT f(2, 3);
-- IF m >= 40 THEN RETURN 'PASS'; ELSE RETURN 'FAIL'; END IF;"""),
        ("Trigger", """DELIMITER //
CREATE TRIGGER trg AFTER INSERT ON T FOR EACH ROW
BEGIN
  INSERT INTO T_Log(id, action, at)
  VALUES (NEW.id, 'INSERT', NOW());
END //
DELIMITER ;
-- INSERT: NEW only · UPDATE: OLD + NEW · DELETE: OLD only
-- Test: do an INSERT, then SELECT * FROM T_Log;"""),
    ]
    for t, c in sections:
        b += f"<h2>{html.escape(t)}</h2>" + code(c, big=True)
    b += "<h2>Error → fix</h2><table>" + "".join(f"<tr><td>{html.escape(a)}</td><td>{md_inline(c)}</td></tr>" for a, c in [
        ("1452 FK fails", "Insert the parent row first"), ("1062 Duplicate entry", "PK / UNIQUE value already used"),
        ("3819 / 4025 CHECK", "Value breaks the CHECK rule"), ("1064 Syntax", "Missing comma, quote, bracket or `;`"),
        ("1050 Table exists", "`DROP TABLE IF EXISTS t;` (child before parent)"),
        ("ROLLBACK did nothing", "Forgot `SET autocommit = 0;` / `START TRANSACTION;`")]) + "</table>"
    return doc("SQL Exam Cheat Sheet", b)

# ------------------------------------------------------------------ 2. STUDY NOTES
def notes():
    b = cover("SQL Lab Exam · Study Notes", "The Video Course in Text",
              "Every slide from the 9 videos with its recipe, template and explanation. Orange text = blanks you fill in.",
              [f"Part {p['num']} · {p['name']}" for p in PARTS])
    for p in PARTS:
        b += f'<h2 style="break-before:page">Part {p["num"]} · {html.escape(p["name"])}</h2>'
        for s in p["slides"]:
            if s["kind"] == "title":
                b += f'<div class="say">{html.escape(s["say"])}</div>'; continue
            b += f'<div class="card"><h3>{html.escape(s["title"])}</h3>'
            c = s.get("code"); steps = s.get("steps") or (s.get("bullets") if c else None)
            if steps:
                b += "<ol class='steps'>" + "".join(f"<li>{inline(x)}</li>" for x in steps) + "</ol>"
            if c:
                b += code(c)
            elif s.get("bullets"):
                b += "<ul class='pts'>" + "".join(f"<li>{inline(x)}</li>" for x in s["bullets"]) + "</ul>"
            b += f'<div class="say">{html.escape(s["say"])}</div></div>'
    return doc("SQL Study Notes", b)

# ------------------------------------------------------------------ 3. SOLUTIONS
def solutions():
    sol = os.path.join(ROOT, "solutions")
    files = sorted(glob.glob(os.path.join(sol, "*.sql")))
    names = []
    for f in files:
        first = [l for l in open(f).read().splitlines() if re.match(r"-- \d+\. ", l)]
        names.append(first[0][3:].title() if first else os.path.basename(f))
    names.append("11. Xml + Xsd Validation")
    b = cover("SQL Lab Exam · Answers", "Full Tested Solutions",
              "Answers to every question in the 8 schemas from Question Sets 1–3 and the Model Questions, plus procedures, functions, triggers and XML. All tested on MySQL-compatible MariaDB.",
              names)
    for f, n in zip(files, names):
        b += f'<h2 style="break-before:page">{html.escape(n)}</h2>' + code(open(f).read())
    b += f'<h2 style="break-before:page">{html.escape(names[-1])}</h2>'
    for fn, label in [("students.xsd", "File 1 · students.xsd (the rules)"), ("students.xml", "File 2 · students.xml (the data)"),
                      ("Validate.java", "File 3 · Validate.java"), ("validate.py", "Or · validate.py (Python + lxml)")]:
        b += f"<h3>{label}</h3>" + code(open(os.path.join(sol, "xml", fn)).read())
    b += '<div class="tip">Run Java: <code>javac Validate.java</code> then <code>java Validate</code>. Break the XML on purpose (e.g. CGPA 12 or delete &lt;name&gt;) and run again to show "INVALID".</div>'
    return doc("SQL Full Solutions", b)

jobs = {"1_SQL_Exam_CheatSheet": cheatsheet(), "2_SQL_Study_Notes_All_Videos": notes(), "3_SQL_Full_Solutions": solutions()}
for name, h in jobs.items():
    open(os.path.join(TMP, name + ".html"), "w").write(h)
json.dump([[os.path.join(TMP, n + ".html"), os.path.join(OUT, n + ".pdf")] for n in jobs], open(os.path.join(TMP, "pdfjobs.json"), "w"))
