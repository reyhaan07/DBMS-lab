"""Rebuild the course with OUTPUT slides (real query results) added to each part."""
import json, re, sys
from content import PARTS
import render_slides

R = json.load(open(sys.argv[2]))
res = {num: items for num, items in R["videos"]}
PART_OF = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 9: 9}

def speak(t):
    for a, b in [("CGPA", "C G P A"), ("→", " to "), ("×", " times "), ("≥", " at least "), ("Dr.", "Doctor"),
                 ("(IT)", "(I T)"), ("NULLs", "nulls"), ("NULL", "null"), ("XML", "X M L"), ("XSD", "X S D"),
                 ("SELECT", "select"), ("ID ", "I D "), ("−", " minus "), ("–", " to "), ("'A%'", "A percent"),
                 ("%", " percent"), ("USAGE", "usage")]:
        t = t.replace(a, b)
    return t

def chunks(steps, max_lines=38):
    """Split long transcripts so each slide stays readable."""
    out, cur, n = [], [], 0
    for st in steps:
        k = st[0].count("\n") + 1 + ((st[1].count("\n") + 1) if st[1] is not None else 0)
        if cur and n + k > max_lines:
            out.append(cur); cur, n = [], 0
        cur.append(st); n += k
    if cur: out.append(cur)
    return out

def output_slides(items):
    slides = []
    for title, note, db, steps in items:
        steps = [tuple(s) for s in steps]
        if db:
            steps = [(f"USE {db};", "Database changed")] + steps
        parts = chunks(steps)
        last_tbl = next((o for _, o in reversed(steps) if o and "in set" in o), None)
        for i, ch in enumerate(parts):
            t = title + (f" ({i+1}/{len(parts)})" if len(parts) > 1 else "")
            if i == 0:
                say = f"Output: {title}. "
                if len(parts) > 1:
                    say += "Read each command and the line printed under it. "
            else:
                say = "Continuing. "
            if i == len(parts) - 1:
                if note:
                    say += note
                elif last_tbl == "Empty set" or (last_tbl is None and any(o == "Empty set" for _, o in steps)):
                    say += "The result is an empty set."
                elif last_tbl:
                    m = re.search(r"(\d+) rows? in set", last_tbl)
                    if m: say += f"The query returns {m.group(1)} row{'s' if m.group(1) != '1' else ''}."
            slides.append(dict(kind="output", title=t, steps=ch, note=note if i == len(parts) - 1 else None, say=speak(say)))
    return slides

INTRO = lambda n: dict(kind="points", title="Now let's RUN them", bullets=[
    "Every query from this part, run on real sample data",
    "Purple  mysql>  line = what you type",
    "White table = what the screen prints",
    "Blue box = why you get that answer",
    "Pause on any slide to study the output"],
    say="Now let's run every query from this part on real sample data, and look at the actual output. The purple line is what you type at the my sequel prompt, and the table under it is exactly what the screen prints. Pause on any slide if you want to study the table.")

for p in PARTS:
    n = p["num"]; sl = p["slides"]
    extra = []
    vnum = {v: k for k, v in PART_OF.items()}.get(n)
    if vnum in res:
        extra = [INTRO(n)] + output_slides(res[vnum])
    if n == 8:
        extra = [INTRO(n),
                 dict(kind="output", title="Valid XML", steps=[("$ javac Validate.java", None), ("$ java Validate", R["java_ok"])],
                      note="No error, so the XML follows every rule in the XSD.",
                      say="Output for the valid X M L file. The program prints: X M L is valid according to the X S D."),
                 dict(kind="output", title="Broken XML (Priya's <name> deleted)", steps=[("$ java Validate", R["java_bad"])],
                      note="The validator says exactly what is wrong: it expected <name> but found <dept>.",
                      say="Now I deleted Priya's name tag and ran it again. It prints invalid, and says it expected name but found dept. Always show both runs in the exam.")]
    if not extra:
        continue
    if n == 9:
        pos = next(i for i, s in enumerate(sl) if s["title"].startswith("That unseen question")) + 1
    elif sl[-1]["kind"] == "points" and ("Recap" in sl[-1]["title"] or "Which JOIN" in sl[-1]["title"] or "dictionary" in sl[-1]["title"]):
        pos = len(sl) - 1
    else:
        pos = len(sl)
    sl[pos:pos] = extra

# terminal prompt for shell lines should be $, not mysql>
orig = render_slides.term_html
def term_html(steps):
    body, n, m = orig(steps)
    body = body.replace('<span class="prompt">mysql&gt; </span>$ ', '<span class="prompt">$ </span>')
    return body, n, m
render_slides.term_html = term_html
sys.argv = [sys.argv[0], sys.argv[1]]
render_slides.main()
print("parts:", [(p["num"], len(p["slides"])) for p in PARTS])
