"""Sample data + every query taught in Videos 2-9, run to capture real output."""

SEED = r"""
DROP DATABASE IF EXISTS college; CREATE DATABASE college; USE college;
CREATE TABLE Student (StudentID INT PRIMARY KEY, Name VARCHAR(50) NOT NULL UNIQUE, Dept VARCHAR(20) NOT NULL,
  City VARCHAR(30), CGPA DECIMAL(4,2) CHECK (CGPA BETWEEN 0 AND 10));
CREATE TABLE Course (CourseID VARCHAR(10) PRIMARY KEY, CourseName VARCHAR(50) NOT NULL, Credits INT);
CREATE TABLE Enrollment (EnrollID INT PRIMARY KEY, StudentID INT, CourseID VARCHAR(10), Marks INT,
  FOREIGN KEY (StudentID) REFERENCES Student(StudentID), FOREIGN KEY (CourseID) REFERENCES Course(CourseID));
INSERT INTO Student VALUES (101,'Arun','CSE','Chennai',8.50),(102,'Priya','ECE','Madurai',9.10),(103,'Karthik','CSE','Chennai',7.20);
INSERT INTO Course VALUES ('C1','DBMS',4),('C2','Networks',3);
INSERT INTO Enrollment VALUES (1,101,'C1',85),(2,102,'C2',78);

DROP DATABASE IF EXISTS company; CREATE DATABASE company; USE company;
CREATE TABLE Department (DeptID INT PRIMARY KEY, DeptName VARCHAR(30) NOT NULL, ManagerID INT);
CREATE TABLE Employee (EmpID INT PRIMARY KEY, EmpName VARCHAR(50) NOT NULL, DeptID INT,
  Salary DECIMAL(10,2) CHECK (Salary > 20000), HireDate DATE, FOREIGN KEY (DeptID) REFERENCES Department(DeptID));
INSERT INTO Department VALUES (1,'HR',201),(2,'IT',202),(3,'Sales',204);
INSERT INTO Employee VALUES (201,'Ravi',1,45000,'2020-06-15'),(202,'Meena',2,75000,'2019-03-10'),
  (203,'Suresh',2,52000,'2021-01-05'),(204,'Anil',3,35000,'2023-07-01'),(205,'Kavya',2,61000,'2022-04-12');

DROP DATABASE IF EXISTS railway; CREATE DATABASE railway; USE railway;
CREATE TABLE Passenger (PassengerID INT PRIMARY KEY, Name VARCHAR(50) NOT NULL, Age INT);
CREATE TABLE Train (TrainID INT PRIMARY KEY, TrainName VARCHAR(50) UNIQUE, Source VARCHAR(30), Destination VARCHAR(30));
CREATE TABLE Booking (BookingID INT PRIMARY KEY, PassengerID INT, TrainID INT, SeatsBooked INT, Fare DECIMAL(8,2),
  FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID),
  FOREIGN KEY (TrainID) REFERENCES Train(TrainID) ON DELETE CASCADE);
INSERT INTO Passenger VALUES (1,'Arun',25),(2,'Priya',30),(3,'Kumar',40),(4,'Divya',22);
INSERT INTO Train VALUES (1,'Vaigai Express','Chennai','Madurai'),(2,'Kovai Express','Chennai','Coimbatore');
INSERT INTO Booking VALUES (1,1,1,2,500),(2,2,1,1,300),(3,1,2,3,900),(4,4,2,1,450);

DROP DATABASE IF EXISTS hospital; CREATE DATABASE hospital; USE hospital;
CREATE TABLE Patient (PatientID INT PRIMARY KEY, PatientName VARCHAR(50) NOT NULL, City VARCHAR(30));
CREATE TABLE Doctor (DoctorID INT PRIMARY KEY, DoctorName VARCHAR(50) NOT NULL, Specialization VARCHAR(40) NOT NULL);
CREATE TABLE Appointment (AppID INT PRIMARY KEY, PatientID INT, DoctorID INT, VisitDate DATE, Fee DECIMAL(8,2),
  FOREIGN KEY (PatientID) REFERENCES Patient(PatientID), FOREIGN KEY (DoctorID) REFERENCES Doctor(DoctorID));
INSERT INTO Patient VALUES (1,'Arun','Chennai'),(2,'Priya','Madurai'),(3,'Kavya','Salem');
INSERT INTO Doctor VALUES (1,'Dr. Ravi','Cardiology'),(2,'Dr. Meena','Neurology'),(3,'Dr. Kumar','Ortho');
INSERT INTO Appointment VALUES (1,1,1,'2025-01-10',500),(2,2,1,'2025-01-11',500),(3,1,2,'2025-01-12',800),(4,3,1,'2025-01-15',600);

DROP DATABASE IF EXISTS bank; CREATE DATABASE bank; USE bank;
CREATE TABLE Customer (CustomerID INT PRIMARY KEY, CustomerName VARCHAR(50) NOT NULL, City VARCHAR(30));
CREATE TABLE Account (AccountNo INT PRIMARY KEY, CustomerID INT, AccountType VARCHAR(20),
  Balance DECIMAL(12,2) CHECK (Balance >= 1000), FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID));
CREATE TABLE `Transaction` (TxnID INT PRIMARY KEY, AccountNo INT, Amount DECIMAL(12,2), TxnType VARCHAR(10),
  FOREIGN KEY (AccountNo) REFERENCES Account(AccountNo));
INSERT INTO Customer VALUES (1,'Arun','Chennai'),(2,'Priya','Madurai'),(3,'Kumar','Salem'),(4,'Divya','Trichy');
INSERT INTO Account VALUES (1001,1,'Savings',50000),(1002,2,'Current',80000),(1003,3,'Savings',20000),(1004,4,'Savings',15000);
INSERT INTO `Transaction` VALUES (1,1001,5000,'Credit');

DROP DATABASE IF EXISTS airline; CREATE DATABASE airline; USE airline;
CREATE TABLE Passenger (PassengerID INT PRIMARY KEY, Name VARCHAR(50) NOT NULL);
CREATE TABLE Flight (FlightID VARCHAR(10) PRIMARY KEY, FlightName VARCHAR(50), Source VARCHAR(30), Destination VARCHAR(30), TicketPrice DECIMAL(8,2));
CREATE TABLE Ticket (TicketID INT PRIMARY KEY, PassengerID INT, FlightID VARCHAR(10), SeatNo VARCHAR(5),
  FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID), FOREIGN KEY (FlightID) REFERENCES Flight(FlightID));
INSERT INTO Passenger VALUES (1,'Arun'),(2,'Priya'),(3,'Kumar');
INSERT INTO Flight VALUES ('F1','IndiGo 6E201','Chennai','Delhi',6000),('F2','Air India 440','Chennai','Mumbai',4200),
  ('F3','SpiceJet 112','Chennai','Bengaluru',3500);
INSERT INTO Ticket VALUES (1,3,'F1','12A'),(2,1,'F2','5B');

DROP DATABASE IF EXISTS cinema; CREATE DATABASE cinema; USE cinema;
CREATE TABLE Movie (MovieID INT PRIMARY KEY, MovieName VARCHAR(50) NOT NULL, Genre VARCHAR(20), TicketPrice DECIMAL(6,2) DEFAULT 150);
CREATE TABLE Customer (CustomerID INT PRIMARY KEY, CustomerName VARCHAR(50) NOT NULL);
CREATE TABLE Booking (BookingID INT PRIMARY KEY, CustomerID INT, MovieID INT, SeatsBooked INT,
  FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID), FOREIGN KEY (MovieID) REFERENCES Movie(MovieID));
INSERT INTO Movie VALUES (1,'Leo','Action',200),(2,'Jailer','Action',150),(3,'Vikram','Thriller',150),(4,'Amaran','Drama',180);
INSERT INTO Customer VALUES (1,'Arun'),(2,'Priya'),(3,'Kumar');
INSERT INTO Booking VALUES (1,1,1,4),(2,2,1,5),(3,1,2,2),(4,3,3,3);

DROP DATABASE IF EXISTS food; CREATE DATABASE food; USE food;
CREATE TABLE Restaurant (RestaurantID INT PRIMARY KEY, RestaurantName VARCHAR(50) NOT NULL, City VARCHAR(30));
CREATE TABLE Customer (CustomerID INT PRIMARY KEY, CustomerName VARCHAR(50) NOT NULL, City VARCHAR(30));
CREATE TABLE FoodOrder (OrderID INT PRIMARY KEY, CustomerID INT, RestaurantID INT, Quantity INT, Price DECIMAL(8,2), Rating DECIMAL(2,1),
  FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID) ON UPDATE CASCADE,
  FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON UPDATE CASCADE);
INSERT INTO Restaurant VALUES (1,'A2B','Chennai'),(2,'Murugan Idli','Madurai'),(3,'Dindigul Biryani','Chennai'),(4,'Adyar Bakery','Chennai');
INSERT INTO Customer VALUES (1,'Arun','Chennai'),(2,'Priya','Madurai');
INSERT INTO FoodOrder VALUES (1,1,1,2,300,4.5),(2,2,2,3,150,5.0),(3,1,1,1,200,3.9),(4,2,3,2,400,4.8);

DROP USER IF EXISTS 'student_user'@'localhost', 'faculty_user'@'localhost', 'course_admin'@'localhost';
"""

# Sample data shown at the start (db, tables)
SAMPLE = [("college", ["Student", "Course", "Enrollment"]), ("company", ["Department", "Employee"]),
          ("railway", ["Passenger", "Train", "Booking"]), ("hospital", ["Patient", "Doctor", "Appointment"]),
          ("bank", ["Customer", "Account", "`Transaction`"]), ("airline", ["Passenger", "Flight", "Ticket"]),
          ("cinema", ["Movie", "Customer", "Booking"]), ("food", ["Restaurant", "Customer", "FoodOrder"])]

# (video number, video title, reseed_before, [ (item title, db, script, note) ])
VIDEOS = []
def video(n, title, items, reseed=True):
    VIDEOS.append({"num": n, "title": title, "items": items, "reseed": reseed})

video(2, "SELECT, GROUP BY, HAVING & Subqueries", [
 ("WHERE: exact match", "college", "SELECT * FROM Student WHERE City = 'Chennai';", None),
 ("WHERE with AND", "college", "SELECT * FROM Student WHERE Dept = 'CSE' AND CGPA > 8;", None),
 ("WHERE with BETWEEN", "company", "SELECT * FROM Employee WHERE Salary BETWEEN 30000 AND 60000;", "BETWEEN includes both ends."),
 ("WHERE with IN (list)", "college", "SELECT * FROM Student WHERE City IN ('Chennai', 'Madurai');", None),
 ("WHERE with LIKE", "college", "SELECT * FROM Student WHERE Name LIKE 'A%';", "'A%' = starts with A."),
 ("WHERE with IS NULL", "hospital", "SELECT * FROM Doctor WHERE Specialization IS NULL;", "No doctor has a NULL specialization (it is NOT NULL), so the answer is an empty set."),
 ("ORDER BY ... DESC", "airline", "SELECT * FROM Flight ORDER BY TicketPrice DESC;", "Highest price first."),
 ("ORDER BY (ASC is default)", "college", "SELECT * FROM Student ORDER BY Name;", None),
 ("COUNT", "company", "SELECT COUNT(*) FROM Employee;", None),
 ("SUM", "railway", "SELECT SUM(Fare) FROM Booking;", None),
 ("AVG with WHERE", "college", "SELECT AVG(CGPA) FROM Student WHERE Dept = 'CSE';", "(8.50 + 7.20) / 2 = 7.85"),
 ("MAX and MIN", "company", "SELECT MAX(Salary), MIN(Salary) FROM Employee;", None),
 ("Alias with AS", "college", "SELECT AVG(CGPA) AS Avg_CSE_CGPA FROM Student WHERE Dept = 'CSE';", "Same answer, nicer column name."),
 ("GROUP BY: highest salary in each department", "company", "SELECT DeptID, MAX(Salary) AS HighestSalary\nFROM Employee\nGROUP BY DeptID;", None),
 ("GROUP BY: total fare collected for each train", "railway", "SELECT TrainID, SUM(Fare) AS TotalFare\nFROM Booking\nGROUP BY TrainID;", None),
 ("HAVING: departments with more than one employee", "company", "SELECT DeptID, COUNT(*) AS EmpCount\nFROM Employee\nGROUP BY DeptID\nHAVING COUNT(*) > 1;", "Only Dept 2 (IT) has more than one employee (Meena, Suresh, Kavya)."),
 ("HAVING: movies with average seats > 3", "cinema", "SELECT MovieID, AVG(SeatsBooked) AS AvgSeats\nFROM Booking\nGROUP BY MovieID\nHAVING AVG(SeatsBooked) > 3;", "Movie 1: (4 + 5) / 2 = 4.5. Movies 2 and 3 have averages 2 and 3, so they are filtered out."),
 ("WHERE + GROUP BY: per city, rating ≥ 4.2", "food", "SELECT r.City,\n       COUNT(f.OrderID) AS TotalOrders,\n       AVG(f.Price)     AS AvgPrice,\n       SUM(f.Quantity)  AS TotalQty\nFROM FoodOrder f\nJOIN Restaurant r ON f.RestaurantID = r.RestaurantID\nWHERE f.Rating >= 4.2\nGROUP BY r.City;", "Order 3 (rating 3.9) is removed by WHERE before grouping."),
 ("Count appointments handled by each doctor", "hospital", "SELECT DoctorID, COUNT(*) AS TotalAppointments\nFROM Appointment\nGROUP BY DoctorID;", None),
 ("Subquery: students with CGPA > average", "college", "SELECT Name FROM Student\nWHERE CGPA > (SELECT AVG(CGPA) FROM Student);", "Average = (8.50 + 9.10 + 7.20) / 3 = 8.27."),
 ("Subquery: employees earning more than average", "company", "SELECT EmpID, EmpName, Salary FROM Employee\nWHERE Salary > (SELECT AVG(Salary) FROM Employee);", "Average salary = 53600."),
 ("Subquery: accounts with balance > average", "bank", "SELECT AccountNo, CustomerID, Balance FROM Account\nWHERE Balance > (SELECT AVG(Balance) FROM Account);", "Average balance = 41250."),
 ("Subquery: account with the maximum balance", "bank", "SELECT * FROM Account\nWHERE Balance = (SELECT MAX(Balance) FROM Account);", None),
 ("IN: passengers who made at least one booking", "railway", "SELECT Name FROM Passenger\nWHERE PassengerID IN (SELECT PassengerID FROM Booking);", "Kumar has no booking, so he is not listed."),
 ("IN: doctors who have at least one appointment", "hospital", "SELECT * FROM Doctor\nWHERE DoctorID IN (SELECT DoctorID FROM Appointment);", "Dr. Kumar has no appointment."),
 ("IN with WHERE inside: restaurants with an order rated 5", "food", "SELECT * FROM Restaurant\nWHERE RestaurantID IN (SELECT RestaurantID FROM FoodOrder WHERE Rating = 5);", None),
 ("NOT IN: restaurants that never received an order", "food", "SELECT * FROM Restaurant\nWHERE RestaurantID NOT IN (SELECT RestaurantID FROM FoodOrder);", None),
 ("Correlated: fare > average fare of that same train", "railway", "SELECT * FROM Booking b1\nWHERE Fare > (SELECT AVG(Fare)\n              FROM Booking b2\n              WHERE b2.TrainID = b1.TrainID);", "Train 1 average = 400 → booking 1 (500). Train 2 average = 675 → booking 3 (900)."),
])

video(3, "JOINs", [
 ("INNER JOIN (2 tables)", "company", "SELECT e.EmpName, e.Salary, d.DeptName\nFROM Employee e\nJOIN Department d ON e.DeptID = d.DeptID;", None),
 ("3-table JOIN: patient and doctor names", "hospital", "SELECT p.PatientName, d.DoctorName\nFROM Appointment a\nJOIN Patient p ON a.PatientID = p.PatientID\nJOIN Doctor  d ON a.DoctorID  = d.DoctorID;", None),
 ("3-table JOIN: student and course names", "college", "SELECT s.Name, c.CourseName\nFROM Student s\nJOIN Enrollment e ON s.StudentID = e.StudentID\nJOIN Course     c ON e.CourseID  = c.CourseID;", "Karthik is not enrolled, so a normal JOIN leaves him out."),
 ("LEFT JOIN: include passengers with no booking", "railway", "SELECT p.PassengerID, p.Name, b.BookingID, b.TrainID, b.Fare\nFROM Passenger p\nLEFT JOIN Booking b ON p.PassengerID = b.PassengerID;", "Kumar appears with NULLs because he has no booking."),
 ("FULL OUTER JOIN (LEFT UNION RIGHT)", "cinema", "SELECT b.BookingID, b.SeatsBooked, m.MovieID, m.MovieName\nFROM Booking b LEFT JOIN Movie m ON b.MovieID = m.MovieID\nUNION\nSELECT b.BookingID, b.SeatsBooked, m.MovieID, m.MovieName\nFROM Booking b RIGHT JOIN Movie m ON b.MovieID = m.MovieID;", "Amaran has no booking, so its booking columns are NULL (the 'blanks')."),
 ("CROSS JOIN: all passenger–flight combinations", "airline", "SELECT p.Name, f.FlightName\nFROM Passenger p\nCROSS JOIN Flight f;", "3 passengers × 3 flights = 9 rows."),
 ("SELF JOIN: pairs of employees in the same department", "company", "SELECT e1.EmpName AS Employee1, e2.EmpName AS Employee2, e1.DeptID\nFROM Employee e1\nJOIN Employee e2\n  ON e1.DeptID = e2.DeptID\n AND e1.EmpID < e2.EmpID;", "Only Dept 2 has more than one person, so all pairs come from it."),
])

video(4, "Transactions + GRANT / REVOKE", [
 ("COMMIT: insert student + enrollment", "college", """SET autocommit = 0;
START TRANSACTION;
INSERT INTO Student VALUES (104, 'Divya', 'IT', 'Coimbatore', 8.80);
INSERT INTO Enrollment VALUES (3, 104, 'C1', 90);
COMMIT;
SELECT * FROM Enrollment;""", "After COMMIT the new rows are permanent."),
 ("ROLLBACK: delete then restore", "college", """START TRANSACTION;
DELETE FROM Enrollment WHERE EnrollID = 2;
SELECT * FROM Enrollment;
ROLLBACK;
SELECT * FROM Enrollment;""", "Row 2 disappears, then comes back after ROLLBACK."),
 ("ROLLBACK undoes BOTH changes", "college", """START TRANSACTION;
UPDATE Student SET CGPA = 9.50 WHERE StudentID = 103;
INSERT INTO Enrollment VALUES (4, 103, 'C2', 70);
ROLLBACK;
SELECT * FROM Student WHERE StudentID = 103;
SELECT * FROM Enrollment WHERE EnrollID = 4;""", "CGPA is still 7.20 and enrollment 4 does not exist."),
 ("SAVEPOINT + ROLLBACK TO", "college", """START TRANSACTION;
INSERT INTO Student VALUES (105, 'Rahul', 'MECH', 'Salem', 7.90);
SAVEPOINT sp1;
INSERT INTO Enrollment VALUES (5, 105, 'C1', 65);
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Student    WHERE StudentID = 105;
SELECT * FROM Enrollment WHERE StudentID = 105;""", "The student (before the savepoint) stays; the enrollment (after it) is undone."),
 ("+10%, savepoint, +5%, roll back to the savepoint", "company", """SET autocommit = 0;
SELECT EmpID, EmpName, Salary FROM Employee;
START TRANSACTION;
UPDATE Employee SET Salary = Salary * 1.10;
SAVEPOINT after_10;
UPDATE Employee SET Salary = Salary * 1.05;
SELECT EmpID, EmpName, Salary FROM Employee;
ROLLBACK TO after_10;
COMMIT;
SELECT EmpID, EmpName, Salary FROM Employee;""", "Final salaries = original × 1.10 (the extra 5% was rolled back)."),
 ("Book two tickets, roll back only the second", "airline", """SET autocommit = 0;
START TRANSACTION;
INSERT INTO Ticket VALUES (3, 1, 'F1', '1A');
SAVEPOINT after_first;
INSERT INTO Ticket VALUES (4, 2, 'F2', '2B');
ROLLBACK TO after_first;
COMMIT;
SELECT * FROM Ticket;""", "Ticket 3 is saved, ticket 4 is gone."),
 ("Bank transfer (all-or-nothing)", "bank", """SET autocommit = 0;
START TRANSACTION;
UPDATE Account SET Balance = Balance - 10000 WHERE AccountNo = 1002;
UPDATE Account SET Balance = Balance + 10000 WHERE AccountNo = 1003;
INSERT INTO `Transaction` VALUES (3, 1002, 10000, 'Debit');
INSERT INTO `Transaction` VALUES (4, 1003, 10000, 'Credit');
COMMIT;
SELECT * FROM Account WHERE AccountNo IN (1002, 1003);
SELECT * FROM `Transaction`;""", "1002: 80000 → 70000, 1003: 20000 → 30000, both transactions recorded."),
 ("What a FAILED transfer looks like → ROLLBACK", "bank", """SET autocommit = 0;
START TRANSACTION;
UPDATE Account SET Balance = Balance - 10000 WHERE AccountNo = 1004;
ROLLBACK;
SELECT * FROM Account WHERE AccountNo = 1004;""", "Suppose a later step of the transfer failed after this UPDATE. Typing ROLLBACK undoes the deduction, so the balance is back to 15000. Nothing is half-done."),
 ("GRANT, REVOKE and SHOW GRANTS", "college", """CREATE USER 'student_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER 'faculty_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER 'course_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON college.Student TO 'student_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON college.Student TO 'faculty_user'@'localhost';
GRANT SELECT, INSERT ON college.Enrollment TO 'faculty_user'@'localhost';
REVOKE INSERT ON college.Enrollment FROM 'faculty_user'@'localhost';
GRANT ALL PRIVILEGES ON college.Course TO 'course_admin'@'localhost';
SHOW GRANTS FOR 'faculty_user'@'localhost';
SHOW GRANTS FOR 'course_admin'@'localhost';""", "After the REVOKE, faculty_user keeps only SELECT on Enrollment. 'USAGE' just means the user can log in."),
])

video(5, "Views & Indexes", [
 ("View: Ticket_Details_View (3 tables)", "airline", """CREATE VIEW Ticket_Details_View AS
SELECT t.TicketID, p.Name, f.FlightName, f.Source, f.Destination, t.SeatNo
FROM Ticket t
JOIN Passenger p ON t.PassengerID = p.PassengerID
JOIN Flight    f ON t.FlightID    = f.FlightID;
SELECT * FROM Ticket_Details_View;""", None),
 ("Index on Flight(Source)", "airline", """CREATE INDEX idx_flight_source ON Flight(Source);
SHOW INDEX FROM Flight;""", "SHOW INDEX prints many columns; only the important ones are shown here. PRIMARY is created automatically for the primary key."),
 ("View: Employee_Department_View", "company", """CREATE VIEW Employee_Department_View AS
SELECT e.EmpID, e.EmpName, e.Salary, d.DeptName
FROM Employee e JOIN Department d ON e.DeptID = d.DeptID;
SELECT * FROM Employee_Department_View;""", None),
 ("View: Customer_Account_View", "bank", """CREATE VIEW Customer_Account_View AS
SELECT c.CustomerID, c.CustomerName, a.AccountNo, a.AccountType, a.Balance
FROM Customer c JOIN Account a ON c.CustomerID = a.CustomerID;
SELECT * FROM Customer_Account_View;""", None),
 ("View: Student_Course_View", "college", """CREATE VIEW Student_Course_View AS
SELECT s.StudentID, s.Name, c.CourseName, e.Marks
FROM Student s
JOIN Enrollment e ON s.StudentID = e.StudentID
JOIN Course     c ON e.CourseID  = c.CourseID;
SELECT * FROM Student_Course_View;""", None),
 ("Index on Student(Dept)", "college", """CREATE INDEX idx_student_dept ON Student(Dept);
SHOW INDEX FROM Student;""", "Name also has an index automatically, because it is UNIQUE."),
])

video(6, "Stored Procedures & Functions", [
 ("Table used by the student procedures", None, """CREATE DATABASE plsql;
USE plsql;
CREATE TABLE Student (StudentID INT PRIMARY KEY, Name VARCHAR(50),
                      Dept VARCHAR(20), Marks INT);
INSERT INTO Student VALUES (1,'Arun','CSE',72), (2,'Priya','IT',35), (3,'Kumar','ECE',58);
SELECT * FROM Student;""", None),
 ("Procedure: welcome message", "plsql", """DELIMITER //
CREATE PROCEDURE Welcome()
BEGIN
    SELECT 'Welcome to the DBMS Lab!' AS Message;
END //
DELIMITER ;
CALL Welcome();""", None),
 ("Procedure: display a student by ID", "plsql", """DELIMITER //
CREATE PROCEDURE GetStudent(IN p_id INT)
BEGIN
    SELECT * FROM Student WHERE StudentID = p_id;
END //
DELIMITER ;
CALL GetStudent(2);""", None),
 ("Procedure: increase marks of a specified student", "plsql", """DELIMITER //
CREATE PROCEDURE IncreaseMarks(IN p_id INT, IN p_inc INT)
BEGIN
    UPDATE Student SET Marks = Marks + p_inc WHERE StudentID = p_id;
END //
DELIMITER ;
CALL IncreaseMarks(1, 5);
SELECT * FROM Student;""", "Arun: 72 → 77."),
 ("Procedure: delete a student record", "plsql", """DELIMITER //
CREATE PROCEDURE DeleteStudent(IN p_id INT)
BEGIN
    DELETE FROM Student WHERE StudentID = p_id;
END //
DELIMITER ;
CALL DeleteStudent(3);
SELECT * FROM Student;""", "Kumar (ID 3) is gone."),
 ("Function: square of a number", "plsql", """DELIMITER //
CREATE FUNCTION Square(n INT) RETURNS INT DETERMINISTIC
BEGIN
    RETURN n * n;
END //
DELIMITER ;
SELECT Square(7);""", None),
 ("Function: add two numbers", "plsql", """DELIMITER //
CREATE FUNCTION AddNumbers(a INT, b INT) RETURNS INT DETERMINISTIC
BEGIN
    RETURN a + b;
END //
DELIMITER ;
SELECT AddNumbers(10, 20);""", None),
 ("Function: pass or fail", "plsql", """DELIMITER //
CREATE FUNCTION PassOrFail(m INT) RETURNS VARCHAR(10) DETERMINISTIC
BEGIN
    IF m >= 40 THEN
        RETURN 'PASS';
    ELSE
        RETURN 'FAIL';
    END IF;
END //
DELIMITER ;
SELECT PassOrFail(65);
SELECT Name, Marks, PassOrFail(Marks) AS Result FROM Student;""", None),
], reseed=False)

video(7, "Triggers (INSERT / UPDATE / DELETE)", [
 ("Step 1: main table + log table", None, """CREATE DATABASE trig;
USE trig;
CREATE TABLE Account (
    AccountNo INT PRIMARY KEY,
    Name      VARCHAR(50),
    Balance   DECIMAL(10,2)
);
CREATE TABLE Account_Log (
    LogID      INT AUTO_INCREMENT PRIMARY KEY,
    AccountNo  INT,
    Action     VARCHAR(20),
    OldBalance DECIMAL(10,2),
    NewBalance DECIMAL(10,2),
    ActionTime DATETIME
);""", None),
 ("AFTER INSERT trigger + test", "trig", """DELIMITER //
CREATE TRIGGER trg_after_insert AFTER INSERT ON Account FOR EACH ROW
BEGIN
    INSERT INTO Account_Log (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (NEW.AccountNo, 'INSERT', NULL, NEW.Balance, NOW());
END //
DELIMITER ;
INSERT INTO Account VALUES (1001, 'Arun', 5000);
INSERT INTO Account VALUES (1002, 'Priya', 8000);
SELECT * FROM Account_Log;""", "We never inserted into Account_Log ourselves; the trigger did it."),
 ("AFTER UPDATE trigger + test", "trig", """DELIMITER //
CREATE TRIGGER trg_after_update AFTER UPDATE ON Account FOR EACH ROW
BEGIN
    INSERT INTO Account_Log (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (NEW.AccountNo, 'UPDATE', OLD.Balance, NEW.Balance, NOW());
END //
DELIMITER ;
UPDATE Account SET Balance = 6000 WHERE AccountNo = 1001;
SELECT * FROM Account_Log;""", "Row 3: OLD.Balance = 5000, NEW.Balance = 6000."),
 ("AFTER DELETE trigger + test", "trig", """DELIMITER //
CREATE TRIGGER trg_after_delete AFTER DELETE ON Account FOR EACH ROW
BEGIN
    INSERT INTO Account_Log (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (OLD.AccountNo, 'DELETE', OLD.Balance, NULL, NOW());
END //
DELIMITER ;
DELETE FROM Account WHERE AccountNo = 1002;
SELECT * FROM Account;
SELECT * FROM Account_Log;""", None),
 ("SHOW TRIGGERS", "trig", "SHOW TRIGGERS;", "Only the main columns are shown."),
], reseed=False)

video(9, "The unseen Library question (from Part 9)", [
 ("Set up the new schema with sample data", None, """CREATE DATABASE lib;
USE lib;
CREATE TABLE Library (BookID INT PRIMARY KEY, Title VARCHAR(50), Author VARCHAR(50), Price DECIMAL(8,2));
CREATE TABLE Member (MemberID INT PRIMARY KEY, Name VARCHAR(50));
INSERT INTO Library VALUES (10,'Wings of Fire','Kalam',300), (11,'Ponniyin Selvan','Kalki',500),
                           (12,'Godan','Premchand',250);
INSERT INTO Member VALUES (1,'Arun'), (2,'Priya');""", None),
 ("Create Issue with foreign keys", "lib", """CREATE TABLE Issue (
    IssueID   INT PRIMARY KEY,
    MemberID  INT,
    BookID    INT,
    IssueDate DATE,
    FOREIGN KEY (MemberID) REFERENCES Member(MemberID),
    FOREIGN KEY (BookID)   REFERENCES Library(BookID)
);""", None),
 ("Books priced above average", "lib", "SELECT * FROM Library WHERE Price > (SELECT AVG(Price) FROM Library);", "Average = (300 + 500 + 250) / 3 = 350."),
 ("Issue, savepoint, issue, roll back the second", "lib", """SET autocommit = 0;
START TRANSACTION;
INSERT INTO Issue VALUES (1, 1, 10, '2025-03-01');
SAVEPOINT sp1;
INSERT INTO Issue VALUES (2, 1, 11, '2025-03-02');
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Issue;""", None),
 ("Count issues per member", "lib", """INSERT INTO Issue VALUES (3, 2, 12, '2025-03-03'), (4, 2, 11, '2025-03-04');
SELECT MemberID, COUNT(*) AS TotalIssues FROM Issue GROUP BY MemberID;""", None),
], reseed=False)

PRE_DROP = "DROP DATABASE IF EXISTS plsql; DROP DATABASE IF EXISTS trig; DROP DATABASE IF EXISTS lib;"
