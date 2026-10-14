-- =========================================================
-- 1. STUDENT MANAGEMENT
-- Student(StudentID PK, Name, Dept, City, CGPA)
-- Course(CourseID PK, CourseName, Credits)
-- Enrollment(EnrollID PK, StudentID FK, CourseID FK, Marks)
-- =========================================================
DROP DATABASE IF EXISTS college;
CREATE DATABASE college;
USE college;

-- Q: Create Student with PRIMARY KEY, NOT NULL, UNIQUE, CHECK (CGPA BETWEEN 0 AND 10)
CREATE TABLE Student (
    StudentID INT PRIMARY KEY,
    Name      VARCHAR(50) NOT NULL UNIQUE,
    Dept      VARCHAR(20) NOT NULL,
    City      VARCHAR(30),
    CGPA      DECIMAL(4,2) CHECK (CGPA BETWEEN 0 AND 10)
);

-- Insert the three sample student records
INSERT INTO Student VALUES (101, 'Arun',  'CSE', 'Chennai',    8.50);
INSERT INTO Student VALUES (102, 'Priya', 'ECE', 'Madurai',    9.10);
INSERT INTO Student VALUES (103, 'Karthik','CSE', 'Chennai',   7.20);
SELECT * FROM Student;

CREATE TABLE Course (
    CourseID   VARCHAR(10) PRIMARY KEY,
    CourseName VARCHAR(50) NOT NULL,
    Credits    INT
);
INSERT INTO Course VALUES ('C1', 'DBMS', 4), ('C2', 'Networks', 3);

-- Q: Create Enrollment with foreign keys referencing Student and Course
CREATE TABLE Enrollment (
    EnrollID  INT PRIMARY KEY,
    StudentID INT,
    CourseID  VARCHAR(10),
    Marks     INT,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (CourseID)  REFERENCES Course(CourseID)
);
-- Insert an enrollment record for StudentID 101 and CourseID C1
INSERT INTO Enrollment VALUES (1, 101, 'C1', 85);
INSERT INTO Enrollment VALUES (2, 102, 'C2', 78);

-- Display all students from Chennai
SELECT * FROM Student WHERE City = 'Chennai';
-- Average CGPA of CSE students
SELECT AVG(CGPA) AS Avg_CSE_CGPA FROM Student WHERE Dept = 'CSE';

-- Q: Students whose CGPA > average CGPA of all students (SUBQUERY)
SELECT Name FROM Student
WHERE CGPA > (SELECT AVG(CGPA) FROM Student);

-- Q: Insert new student, enroll in a course, COMMIT
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Student VALUES (104, 'Divya', 'IT', 'Coimbatore', 8.80);
INSERT INTO Enrollment VALUES (3, 104, 'C1', 90);
COMMIT;

-- Display student names and course names for all enrolled students (JOIN)
SELECT s.Name, c.CourseName
FROM Student s
JOIN Enrollment e ON s.StudentID = e.StudentID
JOIN Course c     ON e.CourseID  = c.CourseID;

-- Q: Update CGPA and insert enrollment, ROLLBACK both
START TRANSACTION;
UPDATE Student SET CGPA = 9.50 WHERE StudentID = 103;
INSERT INTO Enrollment VALUES (4, 103, 'C2', 70);
ROLLBACK;
SELECT * FROM Student WHERE StudentID = 103;   -- CGPA still 7.20

-- Q: Insert student, SAVEPOINT, insert enrollment, roll back to savepoint
START TRANSACTION;
INSERT INTO Student VALUES (105, 'Rahul', 'MECH', 'Salem', 7.90);
SAVEPOINT sp1;
INSERT INTO Enrollment VALUES (5, 105, 'C1', 65);
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Student WHERE StudentID = 105;    -- student remains
SELECT * FROM Enrollment WHERE StudentID = 105; -- enrollment gone

-- Q: Update marks, savepoint, update CGPA, rollback to savepoint
START TRANSACTION;
UPDATE Enrollment SET Marks = 95 WHERE EnrollID = 1;
SAVEPOINT before_cgpa;
UPDATE Student SET CGPA = 9.90 WHERE StudentID = 101;
ROLLBACK TO before_cgpa;
COMMIT;                                  -- marks change kept, CGPA change undone

-- Delete an enrollment record and ROLLBACK to restore it
START TRANSACTION;
DELETE FROM Enrollment WHERE EnrollID = 2;
ROLLBACK;
SELECT * FROM Enrollment;
SET autocommit = 1;

-- Q: GRANT / REVOKE
CREATE USER IF NOT EXISTS 'student_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'faculty_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'course_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON college.Student TO 'student_user'@'localhost';
GRANT SELECT, INSERT ON college.Enrollment TO 'faculty_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON college.Student TO 'faculty_user'@'localhost';
REVOKE INSERT ON college.Enrollment FROM 'faculty_user'@'localhost';
GRANT ALL PRIVILEGES ON college.Course TO 'course_admin'@'localhost';
SHOW GRANTS FOR 'faculty_user'@'localhost';

-- Q: VIEW + INDEX
CREATE VIEW Student_Course_View AS
SELECT s.StudentID, s.Name, c.CourseName, e.Marks
FROM Student s
JOIN Enrollment e ON s.StudentID = e.StudentID
JOIN Course c     ON e.CourseID  = c.CourseID;
SELECT * FROM Student_Course_View;

CREATE INDEX idx_student_dept ON Student(Dept);
SHOW INDEX FROM Student;
