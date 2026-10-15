"""20-slide revision deck (16:9 PDF): 5 concept slides + 15 slides of solved exam questions."""
import html, os, re, sys, json
from render_slides import highlight

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SOL = os.path.join(ROOT, "solutions")
TMP = sys.argv[1]; os.makedirs(TMP, exist_ok=True)

def esc(t):
    t = html.escape(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", t)

def code(c):
    return f'<pre>{highlight(c.strip())}</pre>'

def panel(title, body, cls=""):
    return f'<div class="panel {cls}"><div class="ph">{esc(title)}</div>{body}</div>'

def bullets(items):
    return "<ul>" + "".join(f"<li>{esc(i)}</li>" for i in items) + "</ul>"

def table(rows, head=None):
    h = ""
    if head: h = "<tr>" + "".join(f"<th>{esc(x)}</th>" for x in head) + "</tr>"
    return "<table>" + h + "".join("<tr>" + "".join(f"<td>{esc(x)}</td>" for x in r) + "</tr>" for r in rows) + "</table>"

# ------------------------------------------------------------------ concept slides
C = []
C.append(("Concept 1 · Tables, data types, constraints, INSERT / UPDATE / DELETE", "".join([
 panel("Start every answer", code("""CREATE DATABASE college;
USE college;
SHOW TABLES;
DESC Student;        -- shows columns, types, keys""") + bullets([
   "Every statement ends with `;`. Text and dates go in single quotes (`'Chennai'`, `'2024-05-10'`); numbers have no quotes.",
   "Create **parent** tables first, then **child** tables (the ones with FOREIGN KEY). Insert parent rows before child rows.",
   "After every change run `SELECT * FROM table;` so the examiner sees the result."])),
 panel("Data types", table([
   ["INT", "IDs, counts, seats, quantity, credits, marks"],
   ["VARCHAR(50)", "names, city, dept, genre, any text"],
   ["DECIMAL(10,2)", "money: salary, fare, balance, price, fee"],
   ["DECIMAL(4,2) / (2,1)", "CGPA 8.75 / rating 4.5"],
   ["DATE", "'YYYY-MM-DD' e.g. HireDate, VisitDate"],
   ["VARCHAR(10)", "IDs with letters: 'C1', 'F1'"]], ["Type", "Use for"])),
 panel("Constraints (one-line meanings for the viva)", table([
   ["PRIMARY KEY", "unique + not null; identifies each row"],
   ["NOT NULL", "value is compulsory"],
   ["UNIQUE", "no duplicate values (NULL allowed)"],
   ["CHECK (cond)", "every value must satisfy the rule"],
   ["DEFAULT v", "used when no value is given"],
   ["FOREIGN KEY … REFERENCES", "value must exist in the parent table (referential integrity)"],
   ["ON DELETE CASCADE", "delete parent row → child rows deleted automatically"],
   ["ON UPDATE CASCADE", "parent key changes → child rows updated automatically"]])),
 panel("CREATE TABLE template", code("""CREATE TABLE Employee (
    EmpID    INT PRIMARY KEY,
    EmpName  VARCHAR(50) NOT NULL,
    Email    VARCHAR(50) UNIQUE,
    Salary   DECIMAL(10,2) CHECK (Salary > 20000),
    Bonus    DECIMAL(8,2) DEFAULT 1000,
    DeptID   INT,
    FOREIGN KEY (DeptID) REFERENCES Department(DeptID)
        ON DELETE CASCADE          -- only if asked
);
-- FK added later:
ALTER TABLE Employee ADD CONSTRAINT fk_dept
FOREIGN KEY (DeptID) REFERENCES Department(DeptID);""")),
 panel("Change data", code("""INSERT INTO Student VALUES (101, 'Arun', 'CSE', 'Chennai', 8.50);
INSERT INTO Movie (MovieID, MovieName, Genre)      -- column list:
VALUES (2, 'Jailer', 'Action');                    -- DEFAULT is used
INSERT INTO Train VALUES (1,'Vaigai','Chennai','Madurai'),
                         (2,'Kovai','Chennai','Coimbatore');
UPDATE Employee SET Salary = 75000 WHERE EmpName = 'Meena';
UPDATE Flight SET TicketPrice = TicketPrice + 500 WHERE FlightID = 'F1';
UPDATE Employee SET Salary = Salary * 1.10;        -- +10% (1.05 = +5%)
DELETE FROM Train WHERE Destination = 'Coimbatore';""") + bullets([
   "Never forget WHERE on UPDATE / DELETE, or every row changes.",
   "FK insert with a missing parent value (DeptID 99) → **ERROR 1452**: the parent row does not exist, so referential integrity is violated."])),
]), "grid3"))

C.append(("Concept 2 · SELECT, aggregates, GROUP BY, HAVING, subqueries", "".join([
 panel("Fixed order (Some Funny Wizards Get Hungry Often)", code("""SELECT    columns / aggregates
FROM      table
WHERE     row condition          -- filters ROWS
GROUP BY  column                 -- makes piles
HAVING    COUNT(*) > 1           -- filters PILES
ORDER BY  column DESC;           -- ASC is default""") + bullets([
   "MySQL runs it as: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY.",
   "WHERE cannot use COUNT/SUM/AVG (piles don't exist yet), so those conditions go in HAVING."])),
 panel("WHERE operators", code("""WHERE City = 'Chennai'
WHERE Dept = 'CSE' AND CGPA > 8
WHERE Salary BETWEEN 30000 AND 60000   -- both ends included
WHERE City IN ('Chennai', 'Madurai')
WHERE Name LIKE 'A%'                   -- starts with A
WHERE Name LIKE '%n'                   -- ends with n
WHERE Specialization IS NULL           -- never  = NULL""")),
 panel("GROUP BY = make piles, one output row per pile", code("""-- Ravi D1 45000 | Meena D2 75000 | Suresh D2 52000
-- Kavya D2 61000 | Anil D3 35000
SELECT DeptID, COUNT(*), MAX(Salary), SUM(Salary)
FROM Employee GROUP BY DeptID;
--  1 | 1 | 45000 |  45000
--  2 | 3 | 75000 | 188000
--  3 | 1 | 35000 |  35000""") + bullets([
   "Rule: SELECT may only contain the GROUP BY column(s) + aggregates. `SELECT DeptID, EmpName … GROUP BY DeptID` → ERROR 1055.",
   "COUNT = how many, SUM = total, AVG = average, MAX = highest, MIN = lowest. Use AS for a column name."])),
 panel("Subqueries", code("""-- greater than average
SELECT Name FROM Student
WHERE CGPA > (SELECT AVG(CGPA) FROM Student);
-- equal to maximum
SELECT * FROM Account
WHERE Balance = (SELECT MAX(Balance) FROM Account);
-- at least one / never
SELECT Name FROM Passenger
WHERE PassengerID IN (SELECT PassengerID FROM Booking);
SELECT * FROM Restaurant
WHERE RestaurantID NOT IN (SELECT RestaurantID FROM FoodOrder);
-- of that SAME train (correlated)
SELECT * FROM Booking b1
WHERE Fare > (SELECT AVG(Fare) FROM Booking b2
              WHERE b2.TrainID = b1.TrainID);""")),
 panel("Question words → SQL", table([
   ["for each / per / in every", "GROUP BY that column"], ["having more than N", "HAVING COUNT(*) > N"],
   ["greater than average", "> (SELECT AVG(c) FROM t)"], ["equal to maximum", "= (SELECT MAX(c) FROM t)"],
   ["at least one", "IN (SELECT id FROM other)"], ["never / not / no", "NOT IN (SELECT id FROM other)"],
   ["of that same X", "correlated subquery"], ["descending / highest first", "ORDER BY c DESC"],
   ["count / total / average", "COUNT(*) / SUM / AVG"], ["where rating ≥ 4.2 (row rule)", "WHERE, before GROUP BY"]])),
]), "grid3"))

C.append(("Concept 3 · JOINs, VIEWs, INDEXes", "".join([
 panel("JOIN recipe", bullets([
   "1. Find which tables hold the columns you need.", "2. Give each table a short alias (e, d, p…).",
   "3. JOIN … ON the common ID column (same name in both tables).",
   "3 tables → start from the **middle** table (the one with 2 FKs: Booking, Ticket, Appointment, Enrollment, FoodOrder) and add one JOIN per FK."]) +
   code("""SELECT e.EmpName, d.DeptName
FROM Employee e
JOIN Department d ON e.DeptID = d.DeptID;

SELECT p.PatientName, d.DoctorName
FROM Appointment a
JOIN Patient p ON a.PatientID = p.PatientID
JOIN Doctor  d ON a.DoctorID  = d.DoctorID;""")),
 panel("Other joins", code("""-- include rows with no match (keep-all table FIRST)
SELECT p.Name, b.BookingID
FROM Passenger p LEFT JOIN Booking b ON p.PassengerID = b.PassengerID;

-- FULL OUTER: MySQL has no keyword → LEFT UNION RIGHT
SELECT b.BookingID, m.MovieName
FROM Booking b LEFT JOIN Movie m ON b.MovieID = m.MovieID
UNION
SELECT b.BookingID, m.MovieName
FROM Booking b RIGHT JOIN Movie m ON b.MovieID = m.MovieID;

-- all possible combinations (rows = A × B)
SELECT p.Name, f.FlightName FROM Passenger p CROSS JOIN Flight f;

-- pairs in the same department (SELF join)
SELECT e1.EmpName, e2.EmpName, e1.DeptID
FROM Employee e1 JOIN Employee e2
  ON e1.DeptID = e2.DeptID AND e1.EmpID < e2.EmpID;""")),
 panel("Which join?", table([
   ["matching rows from 2–3 tables", "(INNER) JOIN … ON"], ["include those who have not …", "LEFT JOIN"],
   ["every A and every B, blanks for unmatched", "LEFT JOIN UNION RIGHT JOIN"],
   ["all possible combinations", "CROSS JOIN"], ["pairs … in the same …", "SELF JOIN, e1.id < e2.id"]]) +
   bullets(["Unmatched columns show **NULL** in LEFT / FULL joins."])),
 panel("VIEW = saved SELECT (virtual table)", code("""CREATE VIEW Ticket_Details_View AS
SELECT t.TicketID, p.Name, f.FlightName,
       f.Source, f.Destination, t.SeatNo
FROM Ticket t
JOIN Passenger p ON t.PassengerID = p.PassengerID
JOIN Flight    f ON t.FlightID    = f.FlightID;
SELECT * FROM Ticket_Details_View;
DROP VIEW Ticket_Details_View;      -- if you must redo it""") + bullets([
   "Write the JOIN first, then put `CREATE VIEW name AS` on top.",
   "A view stores no data; it runs its query each time it is used."])),
 panel("INDEX = faster searching on a column", code("""CREATE INDEX idx_flight_source ON Flight(Source);
SHOW INDEX FROM Flight;
DROP INDEX idx_flight_source ON Flight;""") + bullets([
   "The name tells you table + column: idx_movie_genre → Movie(Genre).",
   "PRIMARY KEY and UNIQUE columns get an index automatically."])),
]), "grid3"))

C.append(("Concept 4 · Transactions (COMMIT / ROLLBACK / SAVEPOINT) + GRANT / REVOKE", "".join([
 panel("The words", table([
   ["SET autocommit = 0;", "MySQL saves every statement by default; turn that off first"],
   ["START TRANSACTION;", "begin a group of changes"], ["COMMIT;", "save permanently (cannot be undone)"],
   ["ROLLBACK;", "undo everything since START TRANSACTION"], ["SAVEPOINT sp1;", "checkpoint in the middle"],
   ["ROLLBACK TO sp1;", "undo only what came after sp1"]]) +
   bullets(["Atomicity = all or nothing (bank transfer).", "Always SELECT before and after to prove what happened."])),
 panel("Recipe 1 · … use COMMIT", code("""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Student VALUES (104,'Divya','IT','Coimbatore',8.80);
INSERT INTO Enrollment VALUES (3, 104, 'C1', 90);
COMMIT;
SELECT * FROM Enrollment;""")),
 panel("Recipe 2 · … use ROLLBACK to undo / restore", code("""START TRANSACTION;
DELETE FROM Enrollment WHERE EnrollID = 2;
SELECT * FROM Enrollment;     -- row 2 missing
ROLLBACK;
SELECT * FROM Enrollment;     -- row 2 back""")),
 panel("Recipe 3 · A, SAVEPOINT, B, ROLLBACK TO", code("""START TRANSACTION;
UPDATE Employee SET Salary = Salary * 1.10;   -- A
SAVEPOINT after_10;
UPDATE Employee SET Salary = Salary * 1.05;   -- B
ROLLBACK TO after_10;                          -- B undone
COMMIT;                                        -- A kept""") + bullets([
   "Same shape for: insert passenger → savepoint → booking; book ticket 1 → savepoint → ticket 2; place order → savepoint → update rating."])),
 panel("Bank transfer", code("""START TRANSACTION;
UPDATE Account SET Balance = Balance - 10000 WHERE AccountNo = 1002;
UPDATE Account SET Balance = Balance + 10000 WHERE AccountNo = 1003;
INSERT INTO `Transaction` VALUES (3, 1002, 10000, 'Debit');
INSERT INTO `Transaction` VALUES (4, 1003, 10000, 'Credit');
COMMIT;        -- any error → ROLLBACK; instead""") + bullets(["`Transaction` is a keyword → wrap it in backticks."])),
 panel("GRANT / REVOKE (DCL)", code("""CREATE USER 'faculty_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON college.Student TO 'student_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON college.Student TO 'faculty_user'@'localhost';
REVOKE INSERT ON college.Enrollment FROM 'faculty_user'@'localhost';
GRANT ALL PRIVILEGES ON college.Course TO 'course_admin'@'localhost';
SHOW GRANTS FOR 'faculty_user'@'localhost';""") + bullets([
   "GRANT … **TO**, REVOKE … **FROM**. Format: ON database.table.",
   "MySQL 8 needs CREATE USER before GRANT."])),
]), "grid3"))

C.append(("Concept 5 · Procedures, functions, triggers, XML + XSD", "".join([
 panel("Procedure (run with CALL)", code("""DELIMITER //
CREATE PROCEDURE IncreaseMarks(IN p_id INT, IN p_inc INT)
BEGIN
    UPDATE Student SET Marks = Marks + p_inc
    WHERE StudentID = p_id;
END //
DELIMITER ;
CALL IncreaseMarks(1, 5);""") + bullets([
   "DELIMITER // lets the body contain `;`. Switch back with DELIMITER ;",
   "No inputs → `CREATE PROCEDURE Welcome()`. Body = normal SQL using the parameter."])),
 panel("Function (use inside SELECT)", code("""DELIMITER //
CREATE FUNCTION PassOrFail(m INT)
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
    IF m >= 40 THEN RETURN 'PASS';
    ELSE RETURN 'FAIL';
    END IF;
END //
DELIMITER ;
SELECT Name, PassOrFail(Marks) FROM Student;""") + bullets([
   "RETURNS (with S) = type, RETURN (no S) = value, DETERMINISTIC = same input → same output.",
   "No IN keyword on function parameters."])),
 panel("Trigger (runs automatically)", code("""DELIMITER //
CREATE TRIGGER trg_after_update
AFTER UPDATE ON Account
FOR EACH ROW
BEGIN
    INSERT INTO Account_Log
      (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (NEW.AccountNo, 'UPDATE', OLD.Balance, NEW.Balance, NOW());
END //
DELIMITER ;
UPDATE Account SET Balance = 6000 WHERE AccountNo = 1001;
SELECT * FROM Account_Log;     -- proves it fired""") + bullets([
   "INSERT trigger → NEW only; UPDATE → OLD and NEW; DELETE → OLD only.",
   "Plan: main table + log table (LogID INT AUTO_INCREMENT PRIMARY KEY …) + trigger + test.", "SHOW TRIGGERS; DROP TRIGGER name;"])),
 panel("XML + XSD", code("""<!-- students.xsd -->
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
 <xs:element name="students"><xs:complexType><xs:sequence>
  <xs:element name="student" maxOccurs="unbounded">
   <xs:complexType><xs:sequence>
     <xs:element name="name" type="xs:string"/>
     <xs:element name="cgpa" type="xs:decimal"/>
   </xs:sequence>
   <xs:attribute name="id" type="xs:integer" use="required"/>
 </xs:complexType></xs:element>
 </xs:sequence></xs:complexType></xs:element>
</xs:schema>
<!-- students.xml -->
<students xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:noNamespaceSchemaLocation="students.xsd">
  <student id="101"><name>Arun</name><cgpa>8.5</cgpa></student>
</students>""") + bullets([
   "Validate in Java: SchemaFactory → newSchema(xsd) → newValidator() → validate(xml). Valid → print VALID; exception → INVALID + message.",
   "Show a valid run AND a broken run (e.g. delete a tag)."])),
]), "grid4"))

# ------------------------------------------------------------------ question slides from solutions
def blocks(path):
    txt = open(path).read()
    out = []
    for b in re.split(r"\n\s*\n", txt.strip()):
        lines = b.strip().split("\n")
        if lines[0].startswith("-- ====") or lines[0].startswith("DROP DATABASE"):
            continue
        if not lines[0].startswith("--"):
            if out: out[-1][1].append(b.strip()); continue
            out.append(["Setup", [b.strip()]]); continue
        head = []
        while lines and lines[0].startswith("--"):
            head.append(lines.pop(0)[2:].strip().removeprefix("Q:").strip())
        out.append([" · ".join(head), ["\n".join(lines)]])
    return [(h, "\n\n".join(x for x in c if x)) for h, c in out]

def split2(bl):
    sizes = [len(c.split("\n")) + 2 for _, c in bl]
    total, acc = sum(sizes), 0
    for i, s in enumerate(sizes):
        acc += s
        if acc >= total / 2:
            return bl[:i + 1], bl[i + 1:]
    return bl, []

SCHEMAS = [
 ("01_student.sql", "Student Management", "Student(StudentID PK, Name, Dept, City, CGPA) · Course(CourseID PK, CourseName, Credits) · Enrollment(EnrollID PK, StudentID FK, CourseID FK, Marks)", 2),
 ("02_employee.sql", "Employee Management", "Employee(EmpID, EmpName, DeptID, Salary, HireDate) · Department(DeptID, DeptName, ManagerID)", 2),
 ("03_railway.sql", "Railway Reservation", "Passenger(PassengerID, Name, Age) · Train(TrainID, TrainName, Source, Destination) · Booking(BookingID, PassengerID, TrainID, SeatsBooked, Fare)", 2),
 ("04_hospital.sql", "Hospital Management", "Patient(PatientID, PatientName, City) · Doctor(DoctorID, DoctorName, Specialization) · Appointment(AppID, PatientID, DoctorID, VisitDate, Fee)", 2),
 ("05_bank.sql", "Bank Management", "Customer(CustomerID, CustomerName, City) · Account(AccountNo, CustomerID, AccountType, Balance) · Transaction(TxnID, AccountNo, Amount, TxnType)", 2),
 ("06_airline.sql", "Airline Reservation", "Passenger(PassengerID, Name) · Flight(FlightID, FlightName, Source, Destination, TicketPrice) · Ticket(TicketID, PassengerID, FlightID, SeatNo)", 2),
 ("07_movie.sql", "Movie Booking", "Movie(MovieID, MovieName, Genre, TicketPrice) · Customer(CustomerID, CustomerName) · Booking(BookingID, CustomerID, MovieID, SeatsBooked)", 1),
 ("08_food.sql", "Food Delivery", "Restaurant(RestaurantID, RestaurantName, City) · Customer(CustomerID, CustomerName, City) · FoodOrder(OrderID, CustomerID, RestaurantID, Quantity, Price, Rating)", 1),
]

def qcards(bl):
    return "".join(f'<div class="card"><div class="qh">{esc(h)}</div>{code(c)}</div>' for h, c in bl)

Q = []
for fn, name, schema, n in SCHEMAS:
    bl = blocks(os.path.join(SOL, fn))
    halves = split2(bl) if n == 2 else (bl,)
    for k, part in enumerate(halves):
        t = f"Questions · {name}" + (f" ({k+1}/2)" if n == 2 else "")
        Q.append((t, f'<div class="schema">{esc(schema)}</div><div class="cols">{qcards(part)}</div>'))

# programs slide: procedures/functions + triggers (compact)
pf = [b for b in blocks(os.path.join(SOL, "09_procedures_functions.sql")) if not b[0].startswith("Useful")]
tg = [b for b in blocks(os.path.join(SOL, "10_triggers.sql")) if "BEFORE" not in b[0]]
Q.append(("Questions · Procedures, functions & triggers (Q2 of every set)",
          '<div class="schema">Any table works. These use Student(StudentID, Name, Dept, Marks) and Account(AccountNo, Name, Balance) + Account_Log.</div>'
          f'<div class="cols">{qcards(pf + tg)}</div>'))

slides = [(t, h) for t, h, *_ in C] + Q
assert len(slides) == 20, len(slides)

CSS = """
@page{size:1600px 900px;margin:0}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Inter',sans-serif;color:#0f172a;background:#fff}
.slide{width:1600px;height:900px;position:relative;overflow:hidden;break-after:page;background:#fff}
.top{height:64px;background:linear-gradient(90deg,#1e3a8a,#0e7490);color:#fff;display:flex;align-items:center;padding:0 28px;gap:18px}
.top .n{background:#fff;color:#1e3a8a;font-weight:800;border-radius:8px;padding:3px 12px;font-size:20px}
.top h1{font-size:27px;font-weight:800;letter-spacing:-0.3px}
.top .r{margin-left:auto;font-size:15px;opacity:.85}
.fit{position:absolute;left:18px;right:18px;top:76px;bottom:16px;overflow:hidden;font-size:15px}
.grid3{display:grid;grid-template-columns:repeat(3,1fr);grid-auto-flow:dense;gap:10px;align-content:start}
.grid4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;align-content:start}
.panel{border:1px solid #cbd5e1;border-radius:10px;padding:8px 10px;background:#f8fafc;break-inside:avoid}
.ph{font-weight:800;color:#1e3a8a;margin-bottom:5px;font-size:1.05em}
pre{font-family:'DejaVu Sans Mono',monospace;font-size:.86em;line-height:1.32;white-space:pre-wrap;word-break:break-word;background:#eef3fb;
 border:1px solid #d6dfee;border-radius:6px;padding:5px 7px;margin:3px 0}
ul{padding-left:1.1em;margin:3px 0}li{margin:2px 0;line-height:1.3}
table{border-collapse:collapse;width:100%;font-size:.92em;margin:2px 0}
td,th{border:1px solid #d6dfee;padding:3px 6px;text-align:left;vertical-align:top;line-height:1.25}
th{background:#1e3a8a;color:#fff}td:first-child{font-weight:600;background:#fff}
code{font-family:'DejaVu Sans Mono',monospace;font-size:.9em;color:#1d4ed8}
.kw{color:#1d4ed8;font-weight:700}.str{color:#15803d}.com{color:#6b7280;font-style:italic}.num{color:#b45309}.tag{color:#be185d}
.schema{font-size:.95em;background:#fff7ed;border:1px solid #fed7aa;border-radius:8px;padding:5px 10px;margin-bottom:8px;font-weight:600;color:#7c2d12}
.cols{column-count:3;column-gap:12px;column-fill:balance}
.card{break-inside:avoid;margin-bottom:8px;border-left:4px solid #0e7490;padding-left:7px}
.qh{font-weight:800;color:#0e7490;font-size:.98em;line-height:1.25;margin-bottom:2px}
"""
FIT = """
<script>
document.querySelectorAll('.fit').forEach(f=>{
  let s=26; f.style.fontSize=s+'px';
  const over=()=>f.scrollHeight>f.clientHeight+1||f.scrollWidth>f.clientWidth+1;
  while(over() && s>7){ s-=0.25; f.style.fontSize=s+'px'; }
  f.dataset.size=s;
});
</script>"""
body = ""
for i, (t, inner) in enumerate(slides):
    kind = "Concept revision" if i < 5 else "Solved exam questions"
    if inner.startswith('<div class="panel'):
        grid = "grid4" if "Concept 5" in t else "grid3"
        inner = f'<div class="{grid}">{inner}</div>'
    body += (f'<div class="slide"><div class="top"><span class="n">{i+1}/20</span><h1>{esc(t)}</h1>'
             f'<span class="r">SQL Lab Exam · {kind}</span></div><div class="fit">{inner}</div></div>')
src = os.path.join(TMP, "5_SQL_Revision_Deck.html")
open(src, "w").write(f'<!doctype html><html><head><meta charset="utf-8"><title>SQL Revision Deck</title><style>{CSS}</style></head><body>{body}{FIT}</body></html>')
json.dump([[src, os.path.join(ROOT, "pdf", "5_SQL_Revision_Deck_20_Slides.pdf")]], open(os.path.join(TMP, "pptjobs.json"), "w"))
print("slides", len(slides))
