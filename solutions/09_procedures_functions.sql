-- =========================================================
-- 9. STORED PROCEDURES and FUNCTIONS (MySQL)
-- Simple table used by the "student" procedures/functions
-- =========================================================
DROP DATABASE IF EXISTS plsql;
CREATE DATABASE plsql;
USE plsql;

CREATE TABLE Student (
    StudentID INT PRIMARY KEY,
    Name      VARCHAR(50),
    Dept      VARCHAR(20),
    Marks     INT
);
INSERT INTO Student VALUES (1, 'Arun', 'CSE', 72), (2, 'Priya', 'IT', 35), (3, 'Kumar', 'ECE', 58);

-- ---------- PROCEDURE: welcome message ----------
DELIMITER //
CREATE PROCEDURE Welcome()
BEGIN
    SELECT 'Welcome to the DBMS Lab!' AS Message;
END //
DELIMITER ;
CALL Welcome();

-- ---------- PROCEDURE: increase marks of a specified student ----------
DELIMITER //
CREATE PROCEDURE IncreaseMarks(IN p_id INT, IN p_inc INT)
BEGIN
    UPDATE Student SET Marks = Marks + p_inc WHERE StudentID = p_id;
    SELECT * FROM Student WHERE StudentID = p_id;
END //
DELIMITER ;
CALL IncreaseMarks(1, 5);

-- ---------- PROCEDURE: display details of a student by ID ----------
DELIMITER //
CREATE PROCEDURE GetStudent(IN p_id INT)
BEGIN
    SELECT * FROM Student WHERE StudentID = p_id;
END //
DELIMITER ;
CALL GetStudent(2);

-- ---------- PROCEDURE: delete a student record ----------
DELIMITER //
CREATE PROCEDURE DeleteStudent(IN p_id INT)
BEGIN
    DELETE FROM Student WHERE StudentID = p_id;
    SELECT 'Student deleted' AS Message;
END //
DELIMITER ;
CALL DeleteStudent(3);
SELECT * FROM Student;

-- ---------- FUNCTION: square of a number ----------
DELIMITER //
CREATE FUNCTION Square(n INT)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN n * n;
END //
DELIMITER ;
SELECT Square(7) AS Result;

-- ---------- FUNCTION: add two numbers ----------
DELIMITER //
CREATE FUNCTION AddNumbers(a INT, b INT)
RETURNS INT
DETERMINISTIC
BEGIN
    RETURN a + b;
END //
DELIMITER ;
SELECT AddNumbers(10, 20) AS Sum;

-- ---------- FUNCTION: pass or fail ----------
DELIMITER //
CREATE FUNCTION PassOrFail(m INT)
RETURNS VARCHAR(10)
DETERMINISTIC
BEGIN
    IF m >= 40 THEN
        RETURN 'PASS';
    ELSE
        RETURN 'FAIL';
    END IF;
END //
DELIMITER ;
SELECT Name, Marks, PassOrFail(Marks) AS Result FROM Student;

-- Useful extras
SHOW PROCEDURE STATUS WHERE Db = 'plsql';
SHOW FUNCTION STATUS WHERE Db = 'plsql';
-- DROP PROCEDURE IF EXISTS Welcome;
-- DROP FUNCTION IF EXISTS Square;
