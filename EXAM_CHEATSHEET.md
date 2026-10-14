# SQL Lab Exam: One-Page Cheat Sheet

## The 5-step method (works for ANY table)
1. Read the schema: mark the PKs and FKs. The table with 2 FKs is the **middle/child** table.
2. Split the question at every full stop. Each sentence = one SQL statement.
3. Spot the keyword and pick the recipe below.
4. Fill the template with the new table/column names.
5. Insert 2–3 sample rows yourself, run, and show `SELECT * FROM ...;`

## Word → SQL dictionary
| Question says | Write |
|---|---|
| "for each / per" | `GROUP BY col` |
| "having more than N" | `HAVING COUNT(*) > N` |
| "greater than average" | `WHERE c > (SELECT AVG(c) FROM t)` |
| "equal to maximum" | `WHERE c = (SELECT MAX(c) FROM t)` |
| "at least one" | `WHERE id IN (SELECT id FROM other)` |
| "never / not" | `WHERE id NOT IN (SELECT id FROM other)` |
| "of that same X" | correlated subquery `... WHERE b2.X = b1.X` |
| "include those who have not" | `LEFT JOIN` |
| "every A and every B, blanks" | `LEFT JOIN ... UNION ... RIGHT JOIN` |
| "all possible combinations" | `CROSS JOIN` |
| "pairs in the same ..." | self join, `e1.id < e2.id` |
| "descending / highest first" | `ORDER BY c DESC` |
| "+10%" | `SET c = c * 1.10` |

## Templates
```sql
CREATE DATABASE db;  USE db;

CREATE TABLE T (
  id    INT PRIMARY KEY,
  name  VARCHAR(50) NOT NULL UNIQUE,
  sal   DECIMAL(10,2) CHECK (sal > 20000),
  price DECIMAL(6,2) DEFAULT 150,
  pid   INT,
  FOREIGN KEY (pid) REFERENCES P(pid) ON DELETE CASCADE   -- or ON UPDATE CASCADE
);
ALTER TABLE T ADD CONSTRAINT fk1 FOREIGN KEY (pid) REFERENCES P(pid);

INSERT INTO T VALUES (1, 'A', 30000, 200, 5);
INSERT INTO T (id, name, sal, pid) VALUES (2, 'B', 40000, 5);  -- DEFAULT used
UPDATE T SET sal = 75000 WHERE name = 'Meena';
DELETE FROM T WHERE id = 2;

SELECT cols FROM t WHERE ... GROUP BY ... HAVING ... ORDER BY ... DESC;
SELECT a.x, b.y FROM A a JOIN B b ON a.id = b.id;            -- 3 tables: start from middle
-- FK fails (ERROR 1452) because the parent value does not exist = referential integrity

SET autocommit = 0;
START TRANSACTION; ...; COMMIT;
START TRANSACTION; ...; ROLLBACK;
START TRANSACTION; A; SAVEPOINT sp1; B; ROLLBACK TO sp1; COMMIT;   -- A kept, B undone

CREATE USER 'u'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT, INSERT ON db.T TO 'u'@'localhost';
REVOKE INSERT ON db.T FROM 'u'@'localhost';
GRANT ALL PRIVILEGES ON db.T TO 'u'@'localhost';

CREATE VIEW V AS SELECT ... FROM ... JOIN ... ON ...;
CREATE INDEX idx_t_col ON T(col);

DELIMITER //
CREATE PROCEDURE p(IN x INT)
BEGIN  SELECT * FROM T WHERE id = x;  END //
CREATE FUNCTION f(a INT, b INT) RETURNS INT DETERMINISTIC
BEGIN  RETURN a + b;  END //
CREATE TRIGGER trg AFTER INSERT ON T FOR EACH ROW
BEGIN  INSERT INTO T_Log(id, action, at) VALUES (NEW.id, 'INSERT', NOW());  END //
DELIMITER ;
CALL p(1);  SELECT f(2, 3);
-- INSERT trigger: NEW only · UPDATE: OLD + NEW · DELETE: OLD only
```

## Error → fix
- **1452**: FK fails. Insert the parent row first.
- **1062**: duplicate PK/UNIQUE value.
- **3819 / 4025**: CHECK constraint violated.
- **1064**: syntax. Look for a missing comma, quote, bracket or `;`.
- **1050**: table exists. `DROP TABLE IF EXISTS t;` (drop the child before the parent).
- **ROLLBACK did nothing**: you forgot `SET autocommit = 0;` / `START TRANSACTION;`.
