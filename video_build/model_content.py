"""Every question of Model-questions_-_final.pdf: exact text, how to think, answer script (run for real)."""
USERS = ["student_user","faculty_user","course_admin","hr_user","manager_user","employee_user","reservation_user",
         "booking_user","railway_admin","receptionist","hospital_staff","doctor_user","bank_clerk","bank_manager",
         "bank_admin","flight_user","airline_admin","movie_user","customer_user","movie_admin","delivery_user",
         "order_user","restaurant_admin"]
DROP_USERS = "DROP USER IF EXISTS " + ", ".join(f"'{u}'@'localhost'" for u in USERS) + ";"

S = []   # schemas
def schema(num, name, tables, db, items, also=None):
    S.append(dict(num=num, name=name, tables=tables, db=db, items=items, also=also or []))

# item: dict(q=question text or None for setup, think=[...], sql=script, setup=bool)
def Q(q, think, sql): return dict(q=q, think=think, sql=sql, setup=False)
def SETUP(why, sql): return dict(q=None, think=[why], sql=sql, setup=True)

# ------------------------------------------------------------ 1 STUDENT
schema(1, "Student Management", ["Student(StudentID PK, Name, Dept, City, CGPA)",
  "Course(CourseID PK, CourseName, Credits)", "Enrollment(EnrollID PK, StudentID FK, CourseID FK, Marks)"], "college", [
Q("Create the Student table with PRIMARY KEY, NOT NULL, UNIQUE, and CHECK (CGPA BETWEEN 0 AND 10) constraints. Insert the three sample student records.",
 ["CREATE TABLE recipe: name, type, constraint on every column.", "Put each constraint the question names on a sensible column: PK on StudentID, NOT NULL on Name/Dept, UNIQUE on Name, CHECK on CGPA.",
  "Then 3 INSERTs (text in quotes, numbers without) and SELECT * to show them."],
"""CREATE DATABASE college;
USE college;
CREATE TABLE Student (
    StudentID INT PRIMARY KEY,
    Name      VARCHAR(50) NOT NULL UNIQUE,
    Dept      VARCHAR(20) NOT NULL,
    City      VARCHAR(30),
    CGPA      DECIMAL(4,2) CHECK (CGPA BETWEEN 0 AND 10)
);
INSERT INTO Student VALUES (101, 'Arun', 'CSE', 'Chennai', 8.50);
INSERT INTO Student VALUES (102, 'Priya', 'ECE', 'Madurai', 9.10);
INSERT INTO Student VALUES (103, 'Karthik', 'CSE', 'Chennai', 7.20);
SELECT * FROM Student;
DESC Student;"""),
SETUP("Enrollment needs a Course table to point to, so create it first (parent before child).",
"""CREATE TABLE Course (
    CourseID   VARCHAR(10) PRIMARY KEY,
    CourseName VARCHAR(50) NOT NULL,
    Credits    INT
);
INSERT INTO Course VALUES ('C1', 'DBMS', 4), ('C2', 'Networks', 3);"""),
Q("Create Enrollment with foreign keys referencing Student and Course. Insert an enrollment record for StudentID 101 and CourseID C1. Display all students from Chennai and Find the average CGPA of CSE students.",
 ["4 sentences → 4 statements.", "Child table: FK column types must match the parents (CourseID is VARCHAR). Two FOREIGN KEY lines at the end.",
  "\"Display … from Chennai\" → WHERE City = 'Chennai'.", "\"average CGPA of CSE\" → AVG(CGPA) with WHERE Dept = 'CSE'."],
"""CREATE TABLE Enrollment (
    EnrollID  INT PRIMARY KEY,
    StudentID INT,
    CourseID  VARCHAR(10),
    Marks     INT,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (CourseID)  REFERENCES Course(CourseID)
);
INSERT INTO Enrollment VALUES (1, 101, 'C1', 85);
INSERT INTO Enrollment VALUES (2, 102, 'C2', 78);
SELECT * FROM Student WHERE City = 'Chennai';
SELECT AVG(CGPA) AS Avg_CSE_CGPA FROM Student WHERE Dept = 'CSE';"""),
Q("Insert a new student and enroll the student in a course. Use COMMIT to permanently save the transaction. Display student names and course names for all enrolled students.",
 ["COMMIT recipe: SET autocommit = 0 → START TRANSACTION → the two INSERTs → COMMIT.", "Student first, then Enrollment (parent before child).",
  "\"student names and course names\" are in two tables linked through Enrollment → 3-table JOIN starting from the middle table."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Student VALUES (104, 'Divya', 'IT', 'Coimbatore', 8.80);
INSERT INTO Enrollment VALUES (3, 104, 'C1', 90);
COMMIT;
SELECT s.Name, c.CourseName
FROM Student s
JOIN Enrollment e ON s.StudentID = e.StudentID
JOIN Course c     ON e.CourseID  = c.CourseID;"""),
Q("Update the CGPA of a student and insert a new enrollment record. Use ROLLBACK to undo both changes. Insert a new student, create a SAVEPOINT, then insert an enrollment record. Roll back to the savepoint and verify which changes remain.",
 ["Part 1 = ROLLBACK recipe: START TRANSACTION → UPDATE → INSERT → ROLLBACK → SELECT to prove nothing changed.",
  "Part 2 = SAVEPOINT recipe: A (insert student) → SAVEPOINT → B (insert enrollment) → ROLLBACK TO → COMMIT.",
  "\"verify which changes remain\" → SELECT both tables: the student stays, the enrollment is gone."],
"""START TRANSACTION;
UPDATE Student SET CGPA = 9.50 WHERE StudentID = 103;
INSERT INTO Enrollment VALUES (4, 103, 'C2', 70);
ROLLBACK;
SELECT * FROM Student WHERE StudentID = 103;
SELECT * FROM Enrollment WHERE EnrollID = 4;
START TRANSACTION;
INSERT INTO Student VALUES (105, 'Rahul', 'MECH', 'Salem', 7.90);
SAVEPOINT sp1;
INSERT INTO Enrollment VALUES (5, 105, 'C1', 65);
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Student WHERE StudentID = 105;
SELECT * FROM Enrollment WHERE StudentID = 105;"""),
Q("Update the marks of a student in Enrollment, create a savepoint, update the student's CGPA, and roll back to the savepoint. Delete an enrollment record and use ROLLBACK to restore it.",
 ["SAVEPOINT recipe again: A = update marks, B = update CGPA. After ROLLBACK TO, the marks change stays and the CGPA change is undone.",
  "Then the restore recipe: DELETE → SELECT (gone) → ROLLBACK → SELECT (back)."],
"""START TRANSACTION;
UPDATE Enrollment SET Marks = 95 WHERE EnrollID = 1;
SAVEPOINT before_cgpa;
UPDATE Student SET CGPA = 9.90 WHERE StudentID = 101;
ROLLBACK TO before_cgpa;
COMMIT;
SELECT EnrollID, Marks FROM Enrollment WHERE EnrollID = 1;
SELECT StudentID, CGPA FROM Student WHERE StudentID = 101;
START TRANSACTION;
DELETE FROM Enrollment WHERE EnrollID = 2;
SELECT * FROM Enrollment;
ROLLBACK;
SELECT * FROM Enrollment;"""),
Q("Grant SELECT permission on Student to user student_user. Grant SELECT and INSERT permissions on Enrollment to faculty_user. Grant SELECT, INSERT, and UPDATE permissions on Student to faculty_user.",
 ["Create each user first (MySQL 8 needs it).", "GRANT perms ON database.table TO 'user'@'localhost'; one line per sentence.", "SHOW GRANTS proves it."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'student_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'faculty_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON college.Student TO 'student_user'@'localhost';
GRANT SELECT, INSERT ON college.Enrollment TO 'faculty_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON college.Student TO 'faculty_user'@'localhost';
SHOW GRANTS FOR 'faculty_user'@'localhost';"""),
Q("Revoke INSERT permission on Enrollment from faculty_user. Grant all privileges on Course to course_admin.",
 ["REVOKE uses FROM (GRANT uses TO).", "\"all privileges\" → GRANT ALL PRIVILEGES."],
"""REVOKE INSERT ON college.Enrollment FROM 'faculty_user'@'localhost';
CREATE USER IF NOT EXISTS 'course_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT ALL PRIVILEGES ON college.Course TO 'course_admin'@'localhost';
SHOW GRANTS FOR 'faculty_user'@'localhost';"""),
Q("Create a view named Student_Course_View to display StudentID, Name, CourseName, and Marks by joining Student, Course, and Enrollment and Create an index named idx_student_dept on the Dept column of the Student table.",
 ["Write the 3-table JOIN with exactly the columns asked, then put CREATE VIEW … AS on top.", "Index: CREATE INDEX name ON Table(Column). The name tells you: Student, Dept."],
"""CREATE VIEW Student_Course_View AS
SELECT s.StudentID, s.Name, c.CourseName, e.Marks
FROM Student s
JOIN Enrollment e ON s.StudentID = e.StudentID
JOIN Course c     ON e.CourseID  = c.CourseID;
SELECT * FROM Student_Course_View;
CREATE INDEX idx_student_dept ON Student(Dept);
SHOW INDEX FROM Student;"""),
], also=[("Find the names of students whose CGPA is greater than the average CGPA of all students. (Sets 1, 2, 3)",
 ["\"greater than average\" → compare with (SELECT AVG(…)) in brackets."],
 "SELECT Name FROM Student\nWHERE CGPA > (SELECT AVG(CGPA) FROM Student);")])

# ------------------------------------------------------------ 2 EMPLOYEE
schema(2, "Employee Management", ["Employee(EmpID, EmpName, DeptID, Salary, HireDate)", "Department(DeptID, DeptName, ManagerID)"], "company", [
Q("Create Department and Employee tables with salary CHECK (Salary > 20000) and Insert three employees and update Meena's salary to 75000. Add a foreign key from Employee.DeptID to Department.DeptID. Try inserting an employee with DeptID 99 and explain why it fails.",
 ["Department first (parent). Employee gets CHECK (Salary > 20000). Leave the FK out of CREATE because the question says ADD it later → ALTER TABLE.",
  "\"update Meena's salary\" → UPDATE … SET … WHERE EmpName = 'Meena'.",
  "DeptID 99 is not in Department → ERROR 1452. Explain: referential integrity, the parent row must exist."],
"""CREATE DATABASE company;
USE company;
CREATE TABLE Department (
    DeptID    INT PRIMARY KEY,
    DeptName  VARCHAR(30) NOT NULL,
    ManagerID INT
);
CREATE TABLE Employee (
    EmpID    INT PRIMARY KEY,
    EmpName  VARCHAR(50) NOT NULL,
    DeptID   INT,
    Salary   DECIMAL(10,2) CHECK (Salary > 20000),
    HireDate DATE
);
INSERT INTO Department VALUES (1, 'HR', 201), (2, 'IT', 202), (3, 'Sales', 204);
INSERT INTO Employee VALUES (201, 'Ravi',   1, 45000, '2020-06-15');
INSERT INTO Employee VALUES (202, 'Meena',  2, 60000, '2019-03-10');
INSERT INTO Employee VALUES (203, 'Suresh', 2, 52000, '2021-01-05');
UPDATE Employee SET Salary = 75000 WHERE EmpName = 'Meena';
SELECT * FROM Employee;
ALTER TABLE Employee
ADD CONSTRAINT fk_dept FOREIGN KEY (DeptID) REFERENCES Department(DeptID);
INSERT INTO Employee VALUES (205, 'Vijay', 99, 30000, '2022-02-02');"""),
SETUP("Add two more employees so the GROUP BY questions have interesting groups.",
"INSERT INTO Employee VALUES (204, 'Anil', 3, 35000, '2023-07-01'), (206, 'Kavya', 2, 61000, '2022-04-12');"),
Q("Show departments having more than one employee using GROUP BY and HAVING. Find the highest salary in each department. Find pairs of employees who work in the same department.",
 ["\"having more than one\" → GROUP BY DeptID + HAVING COUNT(*) > 1.", "\"highest … in each\" → MAX(Salary) with GROUP BY DeptID.",
  "\"pairs … same department\" → SELF JOIN: Employee e1 JOIN Employee e2 ON same DeptID AND e1.EmpID < e2.EmpID."],
"""SELECT DeptID, COUNT(*) AS EmpCount
FROM Employee
GROUP BY DeptID
HAVING COUNT(*) > 1;
SELECT DeptID, MAX(Salary) AS HighestSalary
FROM Employee
GROUP BY DeptID;
SELECT e1.EmpName AS Employee1, e2.EmpName AS Employee2, e1.DeptID
FROM Employee e1
JOIN Employee e2 ON e1.DeptID = e2.DeptID AND e1.EmpID < e2.EmpID;"""),
Q("Increase the salary of all employees in a particular department and permanently save the changes using COMMIT. Update the salary of an employee, create a savepoint, update the employee's department, and roll back to the savepoint.",
 ["\"permanently save\" = COMMIT recipe with one UPDATE … WHERE DeptID = 2.", "Then SAVEPOINT recipe: A = salary update (kept), B = department update (undone)."],
"""SET autocommit = 0;
START TRANSACTION;
UPDATE Employee SET Salary = Salary + 5000 WHERE DeptID = 2;
COMMIT;
START TRANSACTION;
UPDATE Employee SET Salary = 50000 WHERE EmpID = 201;
SAVEPOINT sp1;
UPDATE Employee SET DeptID = 2 WHERE EmpID = 201;
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Employee;"""),
Q("Delete an employee record and use ROLLBACK to undo the deletion. Insert a new department and employee. Use COMMIT to save both operations.",
 ["Restore recipe: DELETE → SELECT → ROLLBACK → SELECT.", "COMMIT recipe: department first (parent), then the employee in it."],
"""START TRANSACTION;
DELETE FROM Employee WHERE EmpID = 203;
SELECT COUNT(*) FROM Employee;
ROLLBACK;
SELECT COUNT(*) FROM Employee;
START TRANSACTION;
INSERT INTO Department VALUES (4, 'Finance', 207);
INSERT INTO Employee VALUES (207, 'Nisha', 4, 40000, '2024-01-10');
COMMIT;
SELECT * FROM Employee WHERE DeptID = 4;"""),
Q("Increase the salary of employees by 10%, create a savepoint, increase it by another 5%, and roll back to the first savepoint.",
 ["+10% → Salary * 1.10, +5% → Salary * 1.05.", "After ROLLBACK TO, only the 10% stays."],
"""SELECT EmpID, Salary FROM Employee;
START TRANSACTION;
UPDATE Employee SET Salary = Salary * 1.10;
SAVEPOINT after_10;
UPDATE Employee SET Salary = Salary * 1.05;
ROLLBACK TO after_10;
COMMIT;
SELECT EmpID, Salary FROM Employee;"""),
Q("Grant SELECT permission on Employee to hr_user. Grant SELECT and UPDATE permissions on Employee to manager_user. Grant INSERT permission on Employee to hr_user.",
 ["One GRANT per sentence; create the users first."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'hr_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'manager_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON company.Employee TO 'hr_user'@'localhost';
GRANT SELECT, UPDATE ON company.Employee TO 'manager_user'@'localhost';
GRANT INSERT ON company.Employee TO 'hr_user'@'localhost';
SHOW GRANTS FOR 'hr_user'@'localhost';"""),
Q("Revoke UPDATE permission on Employee from manager_user. Grant SELECT permission on Department to employee_user.",
 ["REVOKE … FROM; new user employee_user needs CREATE USER first."],
"""REVOKE UPDATE ON company.Employee FROM 'manager_user'@'localhost';
CREATE USER IF NOT EXISTS 'employee_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON company.Department TO 'employee_user'@'localhost';
SHOW GRANTS FOR 'manager_user'@'localhost';"""),
Q("Create a view named Employee_Department_View to display EmpID, EmpName, Salary, and DeptName by joining Employee and Department and Create an index named idx_employee_salary on the Salary column of the Employee table.",
 ["2-table JOIN on DeptID with the four columns asked, CREATE VIEW on top.", "Index on Employee(Salary)."],
"""CREATE VIEW Employee_Department_View AS
SELECT e.EmpID, e.EmpName, e.Salary, d.DeptName
FROM Employee e
JOIN Department d ON e.DeptID = d.DeptID;
SELECT * FROM Employee_Department_View;
CREATE INDEX idx_employee_salary ON Employee(Salary);"""),
], also=[("Display the EmpID, EmpName, and Salary of employees whose salary is greater than the average salary of all employees. (ALL 4 papers)",
 ["Average subquery."], "SELECT EmpID, EmpName, Salary FROM Employee\nWHERE Salary > (SELECT AVG(Salary) FROM Employee);")])

# ------------------------------------------------------------ 3 RAILWAY
schema(3, "Railway Reservation", ["Passenger(PassengerID, Name, Age)", "Train(TrainID, TrainName, Source, Destination)",
  "Booking(BookingID, PassengerID, TrainID, SeatsBooked, Fare)"], "railway", [
Q("Create the Train table with TrainName UNIQUE. Insert two trains and delete the train whose destination is Coimbatore.",
 ["UNIQUE on TrainName. Two INSERTs. DELETE … WHERE Destination = 'Coimbatore'.", "SELECT before and after to show it."],
"""CREATE DATABASE railway;
USE railway;
CREATE TABLE Train (
    TrainID     INT PRIMARY KEY,
    TrainName   VARCHAR(50) UNIQUE,
    Source      VARCHAR(30),
    Destination VARCHAR(30)
);
INSERT INTO Train VALUES (1, 'Vaigai Express', 'Chennai', 'Madurai');
INSERT INTO Train VALUES (2, 'Kovai Express', 'Chennai', 'Coimbatore');
SELECT * FROM Train;
DELETE FROM Train WHERE Destination = 'Coimbatore';
SELECT * FROM Train;"""),
SETUP("Booking needs Passenger rows and two trains, so add them back.",
"""CREATE TABLE Passenger (
    PassengerID INT PRIMARY KEY,
    Name        VARCHAR(50) NOT NULL,
    Age         INT
);
INSERT INTO Passenger VALUES (1, 'Arun', 25), (2, 'Priya', 30), (3, 'Kumar', 40);
INSERT INTO Train VALUES (2, 'Kovai Express', 'Chennai', 'Coimbatore');"""),
Q("Create Booking with foreign keys to Passenger and Train. Add ON DELETE CASCADE on Booking.TrainID and explain what happens when a train is deleted.",
 ["Two FOREIGN KEY lines; put ON DELETE CASCADE on the TrainID one.",
  "Explain: deleting a train automatically deletes all its bookings. Prove it: delete train 2, then SELECT * FROM Booking."],
"""CREATE TABLE Booking (
    BookingID   INT PRIMARY KEY,
    PassengerID INT,
    TrainID     INT,
    SeatsBooked INT,
    Fare        DECIMAL(8,2),
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID),
    FOREIGN KEY (TrainID) REFERENCES Train(TrainID) ON DELETE CASCADE
);
INSERT INTO Booking VALUES (1, 1, 1, 2, 500), (2, 2, 1, 1, 300), (3, 1, 2, 3, 900);
DELETE FROM Train WHERE TrainID = 2;
SELECT * FROM Booking;"""),
SETUP("Put train 2 and its booking back, and add one more booking.",
"""INSERT INTO Train VALUES (2, 'Kovai Express', 'Chennai', 'Coimbatore');
INSERT INTO Booking VALUES (3, 1, 2, 3, 900), (4, 2, 2, 1, 450);"""),
Q("Show all passengers and their bookings; include passengers who have not booked any train.",
 ["\"include … who have not\" → LEFT JOIN with Passenger first. Kumar shows NULLs."],
"""SELECT p.PassengerID, p.Name, b.BookingID, b.TrainID, b.Fare
FROM Passenger p
LEFT JOIN Booking b ON p.PassengerID = b.PassengerID;"""),
Q("Find bookings whose fare is greater than the average fare of that same train.",
 ["\"of that same train\" → correlated subquery: inner WHERE b2.TrainID = b1.TrainID."],
"""SELECT * FROM Booking b1
WHERE Fare > (SELECT AVG(Fare) FROM Booking b2 WHERE b2.TrainID = b1.TrainID);"""),
Q("Insert a new passenger and create a booking for the passenger. Use COMMIT. Calculate the total fare collected for each train. Update the number of seats booked and fare for a booking. Use ROLLBACK to cancel the changes.",
 ["COMMIT recipe (passenger then booking).", "\"total … for each train\" → SUM(Fare) GROUP BY TrainID.", "ROLLBACK recipe on one UPDATE that changes 2 columns (SET a = …, b = …)."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Passenger VALUES (4, 'Divya', 22);
INSERT INTO Booking VALUES (5, 4, 1, 2, 600);
COMMIT;
SELECT TrainID, SUM(Fare) AS TotalFare FROM Booking GROUP BY TrainID;
START TRANSACTION;
UPDATE Booking SET SeatsBooked = 5, Fare = 1500 WHERE BookingID = 1;
ROLLBACK;
SELECT * FROM Booking WHERE BookingID = 1;"""),
Q("Insert a passenger, create a SAVEPOINT, make a booking, and roll back to the savepoint. Delete a booking and use ROLLBACK to restore it. Modify the fare of a booking, create a savepoint, modify the seats booked, and roll back to the savepoint.",
 ["Three small recipes in a row: SAVEPOINT, restore, SAVEPOINT."],
"""START TRANSACTION;
INSERT INTO Passenger VALUES (5, 'Rahul', 28);
SAVEPOINT sp1;
INSERT INTO Booking VALUES (6, 5, 2, 1, 450);
ROLLBACK TO sp1;
COMMIT;
START TRANSACTION;
DELETE FROM Booking WHERE BookingID = 2;
ROLLBACK;
START TRANSACTION;
UPDATE Booking SET Fare = 550 WHERE BookingID = 1;
SAVEPOINT sp2;
UPDATE Booking SET SeatsBooked = 4 WHERE BookingID = 1;
ROLLBACK TO sp2;
COMMIT;
SELECT * FROM Booking;"""),
Q("Grant SELECT permission on Train to reservation_user. Grant SELECT and INSERT permissions on Booking to booking_user. Grant SELECT, INSERT, and UPDATE permissions on Passenger to reservation_user.",
 ["Create the two users, then one GRANT per sentence."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'reservation_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON railway.Train TO 'reservation_user'@'localhost';
GRANT SELECT, INSERT ON railway.Booking TO 'booking_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON railway.Passenger TO 'reservation_user'@'localhost';
SHOW GRANTS FOR 'reservation_user'@'localhost';"""),
Q("Revoke INSERT permission on Booking from booking_user. Grant all privileges on Booking to railway_admin.",
 ["REVOKE … FROM, GRANT ALL PRIVILEGES … TO."],
"""REVOKE INSERT ON railway.Booking FROM 'booking_user'@'localhost';
CREATE USER IF NOT EXISTS 'railway_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT ALL PRIVILEGES ON railway.Booking TO 'railway_admin'@'localhost';
SHOW GRANTS FOR 'booking_user'@'localhost';"""),
Q("Create a view named Booking_Details_View to display BookingID, passenger Name, TrainName, SeatsBooked, and Fare by joining Passenger, Train, and Booking. Create an index named idx_train_destination on the Destination column of the Train table.",
 ["Middle table Booking, JOIN Passenger and Train.", "Index on Train(Destination)."],
"""CREATE VIEW Booking_Details_View AS
SELECT b.BookingID, p.Name, t.TrainName, b.SeatsBooked, b.Fare
FROM Booking b
JOIN Passenger p ON b.PassengerID = p.PassengerID
JOIN Train t     ON b.TrainID     = t.TrainID;
SELECT * FROM Booking_Details_View;
CREATE INDEX idx_train_destination ON Train(Destination);"""),
], also=[("Display the names of passengers who have made at least one booking. (ALL 4 papers)",
 ["\"at least one\" → IN (SELECT PassengerID FROM Booking)."], "SELECT Name FROM Passenger\nWHERE PassengerID IN (SELECT PassengerID FROM Booking);")])

# ------------------------------------------------------------ 4 HOSPITAL
schema(4, "Hospital Management", ["Patient(PatientID, PatientName, City)", "Doctor(DoctorID, DoctorName, Specialization)",
  "Appointment(AppID, PatientID, DoctorID, VisitDate, Fee)"], "hospital", [
SETUP("Appointment needs a Patient table too.",
"""CREATE DATABASE hospital;
USE hospital;
CREATE TABLE Patient (
    PatientID   INT PRIMARY KEY,
    PatientName VARCHAR(50) NOT NULL,
    City        VARCHAR(30)
);
INSERT INTO Patient VALUES (1, 'Arun', 'Chennai'), (2, 'Priya', 'Madurai');"""),
Q("Create the Doctor table with Specialization NOT NULL. Create Appointment with foreign keys to Patient and Doctor.",
 ["NOT NULL on Specialization. Appointment = middle table with two FOREIGN KEY lines.", "Bonus proof: inserting a doctor without specialization fails."],
"""CREATE TABLE Doctor (
    DoctorID       INT PRIMARY KEY,
    DoctorName     VARCHAR(50) NOT NULL,
    Specialization VARCHAR(40) NOT NULL
);
CREATE TABLE Appointment (
    AppID     INT PRIMARY KEY,
    PatientID INT,
    DoctorID  INT,
    VisitDate DATE,
    Fee       DECIMAL(8,2),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID)  REFERENCES Doctor(DoctorID)
);
INSERT INTO Doctor VALUES (1, 'Dr. Ravi', 'Cardiology'), (2, 'Dr. Meena', 'Neurology'), (3, 'Dr. Kumar', 'Ortho');
INSERT INTO Doctor (DoctorID, DoctorName) VALUES (4, 'Dr. X');
INSERT INTO Appointment VALUES (1, 1, 1, '2025-01-10', 500), (2, 2, 1, '2025-01-11', 500), (3, 1, 2, '2025-01-12', 800);"""),
Q("Count the number of appointments handled by each doctor.",
 ["\"number of … each doctor\" → COUNT with GROUP BY. JOIN Doctor to show names (LEFT JOIN also shows doctors with 0)."],
"""SELECT d.DoctorName, COUNT(a.AppID) AS TotalAppointments
FROM Doctor d
LEFT JOIN Appointment a ON d.DoctorID = a.DoctorID
GROUP BY d.DoctorID, d.DoctorName;"""),
Q("Display patient names and doctor names for all appointments.",
 ["3-table JOIN from the middle table Appointment."],
"""SELECT p.PatientName, d.DoctorName
FROM Appointment a
JOIN Patient p ON a.PatientID = p.PatientID
JOIN Doctor d  ON a.DoctorID  = d.DoctorID;"""),
Q("Insert a new patient and create an appointment for the patient. Use COMMIT. Update the appointment fee and use ROLLBACK to undo the change.",
 ["COMMIT recipe, then ROLLBACK recipe with a SELECT to prove the fee is unchanged."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Patient VALUES (3, 'Kavya', 'Salem');
INSERT INTO Appointment VALUES (4, 3, 3, '2025-02-01', 600);
COMMIT;
START TRANSACTION;
UPDATE Appointment SET Fee = 1000 WHERE AppID = 4;
ROLLBACK;
SELECT * FROM Appointment WHERE AppID = 4;"""),
Q("Insert a new patient, create a savepoint, insert an appointment, and roll back to the savepoint. Delete an appointment and use ROLLBACK to restore it.",
 ["SAVEPOINT recipe (patient kept, appointment undone), then restore recipe."],
"""START TRANSACTION;
INSERT INTO Patient VALUES (4, 'Rahul', 'Trichy');
SAVEPOINT sp1;
INSERT INTO Appointment VALUES (5, 4, 2, '2025-02-05', 800);
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Appointment WHERE PatientID = 4;
START TRANSACTION;
DELETE FROM Appointment WHERE AppID = 3;
ROLLBACK;
SELECT COUNT(*) FROM Appointment;"""),
Q("Update a doctor's specialization, create a savepoint, update an appointment fee, and roll back to the savepoint.",
 ["A = specialization (kept), B = fee (undone)."],
"""START TRANSACTION;
UPDATE Doctor SET Specialization = 'Cardiac Surgery' WHERE DoctorID = 1;
SAVEPOINT sp2;
UPDATE Appointment SET Fee = 900 WHERE AppID = 1;
ROLLBACK TO sp2;
COMMIT;
SELECT * FROM Doctor WHERE DoctorID = 1;
SELECT AppID, Fee FROM Appointment WHERE AppID = 1;"""),
Q("Grant SELECT permission on Doctor to receptionist. Grant SELECT and INSERT permissions on Appointment to receptionist. Grant SELECT, INSERT, and UPDATE permissions on Patient to hospital_staff.",
 ["Create users, one GRANT per sentence."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'receptionist'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'hospital_staff'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON hospital.Doctor TO 'receptionist'@'localhost';
GRANT SELECT, INSERT ON hospital.Appointment TO 'receptionist'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospital.Patient TO 'hospital_staff'@'localhost';
SHOW GRANTS FOR 'receptionist'@'localhost';"""),
Q("Revoke INSERT permission on Appointment from receptionist. Grant SELECT permission on Doctor to doctor_user.",
 ["REVOKE … FROM; create doctor_user first."],
"""REVOKE INSERT ON hospital.Appointment FROM 'receptionist'@'localhost';
CREATE USER IF NOT EXISTS 'doctor_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON hospital.Doctor TO 'doctor_user'@'localhost';
SHOW GRANTS FOR 'receptionist'@'localhost';"""),
Q("Create a view named Appointment_Details_View to display AppID, patient PatientName, doctor DoctorName, Specialization, VisitDate, and Fee by joining Patient, Doctor, and Appointment. Create an index named idx_doctor_specialization on the Specialization column of the Doctor table.",
 ["Middle table Appointment + two JOINs. Index on Doctor(Specialization)."],
"""CREATE VIEW Appointment_Details_View AS
SELECT a.AppID, p.PatientName, d.DoctorName, d.Specialization, a.VisitDate, a.Fee
FROM Appointment a
JOIN Patient p ON a.PatientID = p.PatientID
JOIN Doctor d  ON a.DoctorID  = d.DoctorID;
SELECT * FROM Appointment_Details_View;
CREATE INDEX idx_doctor_specialization ON Doctor(Specialization);"""),
], also=[("Display the details of doctors who have at least one appointment. (ALL 4 papers)",
 ["\"at least one\" → IN."], "SELECT * FROM Doctor\nWHERE DoctorID IN (SELECT DoctorID FROM Appointment);")])

# ------------------------------------------------------------ 5 BANK
schema(5, "Bank Management", ["Customer(CustomerID, CustomerName, City)", "Account(AccountNo, CustomerID, AccountType, Balance)",
  "Transaction(TxnID, AccountNo, Amount, TxnType)"], "bank", [
SETUP("Account's FK needs the Customer table.",
"""CREATE DATABASE bank;
USE bank;
CREATE TABLE Customer (
    CustomerID   INT PRIMARY KEY,
    CustomerName VARCHAR(50) NOT NULL,
    City         VARCHAR(30)
);
INSERT INTO Customer VALUES (1, 'Arun', 'Chennai'), (2, 'Priya', 'Madurai'), (3, 'Kumar', 'Salem');"""),
Q("Create the Account table with CHECK (Balance >= 1000). Add a foreign key from Account.CustomerID to Customer.CustomerID.",
 ["CHECK on Balance in CREATE. \"Add a foreign key\" → ALTER TABLE … ADD CONSTRAINT.", "Proof: a balance of 500 is rejected by the CHECK."],
"""CREATE TABLE Account (
    AccountNo   INT PRIMARY KEY,
    CustomerID  INT,
    AccountType VARCHAR(20),
    Balance     DECIMAL(12,2) CHECK (Balance >= 1000)
);
ALTER TABLE Account
ADD CONSTRAINT fk_cust FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID);
INSERT INTO Account VALUES (1001, 1, 'Savings', 50000), (1002, 2, 'Current', 80000), (1003, 3, 'Savings', 20000);
INSERT INTO Account VALUES (1009, 1, 'Savings', 500);"""),
SETUP("The Transaction table (keyword → backticks).",
"""CREATE TABLE `Transaction` (
    TxnID     INT PRIMARY KEY,
    AccountNo INT,
    Amount    DECIMAL(12,2),
    TxnType   VARCHAR(10),
    FOREIGN KEY (AccountNo) REFERENCES Account(AccountNo)
);
INSERT INTO `Transaction` VALUES (1, 1001, 5000, 'Credit');"""),
Q("Find customers whose account balance is greater than the average balance.",
 ["Customer names live in Customer, balance in Account → JOIN, plus the average subquery."],
"""SELECT c.CustomerName, a.Balance
FROM Customer c
JOIN Account a ON c.CustomerID = a.CustomerID
WHERE a.Balance > (SELECT AVG(Balance) FROM Account);"""),
Q("Find accounts whose balance is equal to the maximum balance in the bank.",
 ["\"equal to maximum\" → = (SELECT MAX(Balance) …)."],
"""SELECT * FROM Account
WHERE Balance = (SELECT MAX(Balance) FROM Account);"""),
Q("Insert a new customer and create an account for the customer. Use COMMIT. Deduct ₹5,000 from an account balance and record the transaction. Use COMMIT.",
 ["Two COMMIT recipes.", "Deduct → SET Balance = Balance - 5000, and record → INSERT a 'Debit' row."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Customer VALUES (4, 'Divya', 'Trichy');
INSERT INTO Account VALUES (1004, 4, 'Savings', 15000);
COMMIT;
START TRANSACTION;
UPDATE Account SET Balance = Balance - 5000 WHERE AccountNo = 1001;
INSERT INTO `Transaction` VALUES (2, 1001, 5000, 'Debit');
COMMIT;
SELECT * FROM Account;"""),
Q("Transfer ₹10,000 from one account to another account and record both transactions. Use ROLLBACK if any operation fails. Deduct an amount from an account, create a savepoint, insert the transaction record, and roll back to the savepoint.",
 ["Transfer = − on one account, + on the other, 2 transaction rows, COMMIT (say: if any step errors, type ROLLBACK instead, all or nothing).",
  "Then SAVEPOINT recipe: A = deduct (kept), B = transaction row (undone)."],
"""START TRANSACTION;
UPDATE Account SET Balance = Balance - 10000 WHERE AccountNo = 1002;
UPDATE Account SET Balance = Balance + 10000 WHERE AccountNo = 1003;
INSERT INTO `Transaction` VALUES (3, 1002, 10000, 'Debit');
INSERT INTO `Transaction` VALUES (4, 1003, 10000, 'Credit');
COMMIT;
START TRANSACTION;
UPDATE Account SET Balance = Balance - 2000 WHERE AccountNo = 1003;
SAVEPOINT sp1;
INSERT INTO `Transaction` VALUES (5, 1003, 2000, 'Debit');
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Account;
SELECT * FROM `Transaction`;"""),
Q("Delete a transaction record and use ROLLBACK to undo the deletion. Grant SELECT permission on Account to bank_clerk. Grant SELECT and INSERT permissions on Transaction to bank_clerk.",
 ["Restore recipe, then two GRANTs (backticks around Transaction)."],
"""START TRANSACTION;
DELETE FROM `Transaction` WHERE TxnID = 1;
ROLLBACK;
SELECT COUNT(*) FROM `Transaction`;
SET autocommit = 1;
CREATE USER IF NOT EXISTS 'bank_clerk'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON bank.Account TO 'bank_clerk'@'localhost';
GRANT SELECT, INSERT ON bank.`Transaction` TO 'bank_clerk'@'localhost';
SHOW GRANTS FOR 'bank_clerk'@'localhost';"""),
Q("Grant SELECT and UPDATE permissions on Account to bank_manager. Revoke UPDATE permission on Account from bank_clerk. Grant all privileges on Account to bank_admin.",
 ["bank_clerk never got UPDATE above, so give it first, then revoke (otherwise MySQL says there is no such grant)."],
"""CREATE USER IF NOT EXISTS 'bank_manager'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'bank_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT, UPDATE ON bank.Account TO 'bank_manager'@'localhost';
GRANT UPDATE ON bank.Account TO 'bank_clerk'@'localhost';
REVOKE UPDATE ON bank.Account FROM 'bank_clerk'@'localhost';
GRANT ALL PRIVILEGES ON bank.Account TO 'bank_admin'@'localhost';
SHOW GRANTS FOR 'bank_clerk'@'localhost';"""),
Q("Create a view named Customer_Account_View to display CustomerID, CustomerName, AccountNo, AccountType, and Balance by joining Customer and Account. Create an index named idx_account_balance on the Balance column of the Account table.",
 ["2-table JOIN on CustomerID + CREATE VIEW. Index on Account(Balance)."],
"""CREATE VIEW Customer_Account_View AS
SELECT c.CustomerID, c.CustomerName, a.AccountNo, a.AccountType, a.Balance
FROM Customer c
JOIN Account a ON c.CustomerID = a.CustomerID;
SELECT * FROM Customer_Account_View;
CREATE INDEX idx_account_balance ON Account(Balance);"""),
], also=[("Display the AccountNo, CustomerID, and Balance of accounts whose balance is greater than the average account balance. (ALL 4 papers)",
 ["Average subquery."], "SELECT AccountNo, CustomerID, Balance FROM Account\nWHERE Balance > (SELECT AVG(Balance) FROM Account);")])

# ------------------------------------------------------------ 6 AIRLINE
schema(6, "Airline Reservation", ["Passenger(PassengerID, Name)", "Flight(FlightID, FlightName, Source, Destination, TicketPrice)",
  "Ticket(TicketID, PassengerID, FlightID, SeatNo)"], "airline", [
SETUP("Create Passenger and Flight first.",
"""CREATE DATABASE airline;
USE airline;
CREATE TABLE Passenger (
    PassengerID INT PRIMARY KEY,
    Name        VARCHAR(50) NOT NULL
);
CREATE TABLE Flight (
    FlightID    VARCHAR(10) PRIMARY KEY,
    FlightName  VARCHAR(50),
    Source      VARCHAR(30),
    Destination VARCHAR(30),
    TicketPrice DECIMAL(8,2)
);
INSERT INTO Passenger VALUES (1, 'Arun'), (2, 'Priya');"""),
Q("Insert two flights and modify the ticket price of Flight F1 by adding ₹500. Create Ticket with foreign keys to Passenger and Flight.",
 ["FlightID 'F1' has letters → VARCHAR. \"adding ₹500\" → SET TicketPrice = TicketPrice + 500.", "Ticket = middle table with two FKs (FlightID VARCHAR to match)."],
"""INSERT INTO Flight VALUES ('F1', 'IndiGo 6E201', 'Chennai', 'Delhi', 5500);
INSERT INTO Flight VALUES ('F2', 'Air India 440', 'Chennai', 'Mumbai', 4200);
UPDATE Flight SET TicketPrice = TicketPrice + 500 WHERE FlightID = 'F1';
SELECT * FROM Flight;
CREATE TABLE Ticket (
    TicketID    INT PRIMARY KEY,
    PassengerID INT,
    FlightID    VARCHAR(10),
    SeatNo      VARCHAR(5),
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID),
    FOREIGN KEY (FlightID)    REFERENCES Flight(FlightID)
);"""),
Q("Display flights ordered by ticket price in descending order. Display all possible passenger–flight combinations.",
 ["ORDER BY TicketPrice DESC.", "\"all possible combinations\" → CROSS JOIN (rows = passengers × flights)."],
"""SELECT * FROM Flight ORDER BY TicketPrice DESC;
SELECT p.Name, f.FlightName
FROM Passenger p CROSS JOIN Flight f;"""),
Q("Insert a new passenger and book a ticket. Use COMMIT.",
 ["COMMIT recipe: passenger then ticket."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Passenger VALUES (3, 'Kumar');
INSERT INTO Ticket VALUES (1, 3, 'F1', '12A');
COMMIT;
SELECT * FROM Ticket;"""),
Q("Update the ticket's seat number and use ROLLBACK to cancel the change.",
 ["ROLLBACK recipe; SELECT shows the seat is still 12A."],
"""START TRANSACTION;
UPDATE Ticket SET SeatNo = '20C' WHERE TicketID = 1;
SELECT * FROM Ticket;
ROLLBACK;
SELECT * FROM Ticket;"""),
Q("Insert a passenger, create a savepoint, book a ticket, and roll back to the savepoint.",
 ["A = passenger (kept), B = ticket (undone)."],
"""START TRANSACTION;
INSERT INTO Passenger VALUES (4, 'Divya');
SAVEPOINT sp1;
INSERT INTO Ticket VALUES (2, 4, 'F2', '5B');
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Passenger WHERE PassengerID = 4;
SELECT * FROM Ticket WHERE PassengerID = 4;"""),
Q("Delete a ticket record and use ROLLBACK to restore it.",
 ["Restore recipe."],
"""START TRANSACTION;
DELETE FROM Ticket WHERE TicketID = 1;
SELECT * FROM Ticket;
ROLLBACK;
SELECT * FROM Ticket;"""),
Q("Book two tickets, create a savepoint after the first booking, and roll back the second booking using the savepoint.",
 ["Ticket 1 → SAVEPOINT → ticket 2 → ROLLBACK TO → COMMIT. Only the first stays."],
"""START TRANSACTION;
INSERT INTO Ticket VALUES (3, 1, 'F1', '1A');
SAVEPOINT after_first;
INSERT INTO Ticket VALUES (4, 2, 'F2', '2B');
ROLLBACK TO after_first;
COMMIT;
SELECT * FROM Ticket;"""),
Q("Grant SELECT permission on Flight to flight_user. Grant SELECT and INSERT permissions on Ticket to booking_user. Grant SELECT, INSERT, and UPDATE permissions on Passenger to reservation_user. Revoke INSERT permission on Ticket from booking_user. Grant all privileges on Ticket to airline_admin.",
 ["5 sentences → create 4 users, then 5 lines (one is REVOKE … FROM)."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'flight_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'reservation_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'airline_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON airline.Flight TO 'flight_user'@'localhost';
GRANT SELECT, INSERT ON airline.Ticket TO 'booking_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON airline.Passenger TO 'reservation_user'@'localhost';
REVOKE INSERT ON airline.Ticket FROM 'booking_user'@'localhost';
GRANT ALL PRIVILEGES ON airline.Ticket TO 'airline_admin'@'localhost';
SHOW GRANTS FOR 'booking_user'@'localhost';"""),
Q("Create a view named Ticket_Details_View to display TicketID, passenger Name, FlightName, Source, Destination, and SeatNo by joining Passenger, Flight, and Ticket. Create an index named idx_flight_source on the Source column of the Flight table.",
 ["Middle table Ticket + two JOINs. Index on Flight(Source)."],
"""CREATE VIEW Ticket_Details_View AS
SELECT t.TicketID, p.Name, f.FlightName, f.Source, f.Destination, t.SeatNo
FROM Ticket t
JOIN Passenger p ON t.PassengerID = p.PassengerID
JOIN Flight f    ON t.FlightID    = f.FlightID;
SELECT * FROM Ticket_Details_View;
CREATE INDEX idx_flight_source ON Flight(Source);"""),
])

# ------------------------------------------------------------ 7 MOVIE
schema(7, "Movie Booking", ["Movie(MovieID, MovieName, Genre, TicketPrice)", "Customer(CustomerID, CustomerName)",
  "Booking(BookingID, CustomerID, MovieID, SeatsBooked)"], "cinema", [
Q("Create the Movie table with TicketPrice DEFAULT 150 and insert movies without specifying the ticket price for one row.",
 ["DEFAULT 150 on TicketPrice.", "To skip the price, INSERT with a column list that leaves TicketPrice out → it becomes 150."],
"""CREATE DATABASE cinema;
USE cinema;
CREATE TABLE Movie (
    MovieID     INT PRIMARY KEY,
    MovieName   VARCHAR(50) NOT NULL,
    Genre       VARCHAR(20),
    TicketPrice DECIMAL(6,2) DEFAULT 150
);
INSERT INTO Movie VALUES (1, 'Leo', 'Action', 200);
INSERT INTO Movie (MovieID, MovieName, Genre) VALUES (2, 'Jailer', 'Action');
INSERT INTO Movie VALUES (3, 'Vikram', 'Thriller', 180), (4, 'Amaran', 'Drama', 170);
SELECT * FROM Movie;"""),
SETUP("Customer and Booking tables with some bookings.",
"""CREATE TABLE Customer (
    CustomerID   INT PRIMARY KEY,
    CustomerName VARCHAR(50) NOT NULL
);
CREATE TABLE Booking (
    BookingID   INT PRIMARY KEY,
    CustomerID  INT,
    MovieID     INT,
    SeatsBooked INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID),
    FOREIGN KEY (MovieID)    REFERENCES Movie(MovieID)
);
INSERT INTO Customer VALUES (1, 'Arun'), (2, 'Priya');
INSERT INTO Booking VALUES (1, 1, 1, 4), (2, 2, 1, 5), (3, 1, 2, 2), (4, 2, 3, 3);"""),
Q("Find the average seats booked for each movie and show only movies with average seats greater than 3.",
 ["\"for each movie\" → GROUP BY MovieID. Condition on AVG → HAVING."],
"""SELECT MovieID, AVG(SeatsBooked) AS AvgSeats
FROM Booking
GROUP BY MovieID
HAVING AVG(SeatsBooked) > 3;"""),
Q("Show every booking and every movie, matched where possible, with blanks for unmatched rows.",
 ["That wording = FULL OUTER JOIN. MySQL has no keyword → LEFT JOIN UNION RIGHT JOIN. Amaran (no booking) shows NULLs."],
"""SELECT b.BookingID, b.SeatsBooked, m.MovieID, m.MovieName
FROM Booking b LEFT JOIN Movie m ON b.MovieID = m.MovieID
UNION
SELECT b.BookingID, b.SeatsBooked, m.MovieID, m.MovieName
FROM Booking b RIGHT JOIN Movie m ON b.MovieID = m.MovieID;"""),
Q("Insert a new customer and book tickets for a movie. Use COMMIT.",
 ["COMMIT recipe: customer then booking."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Customer VALUES (3, 'Kumar');
INSERT INTO Booking VALUES (5, 3, 3, 3);
COMMIT;
SELECT * FROM Booking WHERE CustomerID = 3;"""),
Q("Update the number of seats booked and use ROLLBACK.",
 ["ROLLBACK recipe."],
"""START TRANSACTION;
UPDATE Booking SET SeatsBooked = 10 WHERE BookingID = 5;
ROLLBACK;
SELECT * FROM Booking WHERE BookingID = 5;"""),
Q("Create a booking, create a savepoint, modify the number of seats, and roll back to the savepoint.",
 ["A = new booking (kept), B = seat change (undone)."],
"""START TRANSACTION;
INSERT INTO Booking VALUES (6, 2, 3, 2);
SAVEPOINT sp1;
UPDATE Booking SET SeatsBooked = 6 WHERE BookingID = 6;
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM Booking WHERE BookingID = 6;"""),
Q("Delete a booking and use ROLLBACK to restore it.",
 ["Restore recipe."],
"""START TRANSACTION;
DELETE FROM Booking WHERE BookingID = 6;
ROLLBACK;
SELECT * FROM Booking WHERE BookingID = 6;"""),
Q("Insert two bookings, create a savepoint between them, and roll back only the second booking.",
 ["Booking 1 → SAVEPOINT → booking 2 → ROLLBACK TO → COMMIT."],
"""START TRANSACTION;
INSERT INTO Booking VALUES (7, 1, 3, 1);
SAVEPOINT between_bookings;
INSERT INTO Booking VALUES (8, 2, 2, 2);
ROLLBACK TO between_bookings;
COMMIT;
SELECT * FROM Booking WHERE BookingID IN (7, 8);"""),
Q("Grant SELECT permission on Movie to movie_user. Grant SELECT and INSERT permissions on Booking to booking_user. Grant SELECT, INSERT, and UPDATE permissions on Customer to customer_user. Revoke INSERT permission on Booking from booking_user. Grant all privileges on Booking to movie_admin.",
 ["Create 4 users, then 5 lines."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'movie_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'customer_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'movie_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON cinema.Movie TO 'movie_user'@'localhost';
GRANT SELECT, INSERT ON cinema.Booking TO 'booking_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON cinema.Customer TO 'customer_user'@'localhost';
REVOKE INSERT ON cinema.Booking FROM 'booking_user'@'localhost';
GRANT ALL PRIVILEGES ON cinema.Booking TO 'movie_admin'@'localhost';
SHOW GRANTS FOR 'booking_user'@'localhost';"""),
Q("Create a view named Movie_Booking_View to display BookingID, CustomerName, MovieName, Genre, and SeatsBooked by joining Customer, Movie, and Booking. Create an index named idx_movie_genre on the Genre column of the Movie table.",
 ["Middle table Booking + two JOINs. Index on Movie(Genre)."],
"""CREATE VIEW Movie_Booking_View AS
SELECT b.BookingID, c.CustomerName, m.MovieName, m.Genre, b.SeatsBooked
FROM Booking b
JOIN Customer c ON b.CustomerID = c.CustomerID
JOIN Movie m    ON b.MovieID    = m.MovieID;
SELECT * FROM Movie_Booking_View;
CREATE INDEX idx_movie_genre ON Movie(Genre);"""),
])

# ------------------------------------------------------------ 8 FOOD
schema(8, "Food Delivery", ["Restaurant(RestaurantID, RestaurantName, City)", "Customer(CustomerID, CustomerName, City)",
  "FoodOrder(OrderID, CustomerID, RestaurantID, Quantity, Price, Rating)"], "food", [
SETUP("Parent tables first.",
"""CREATE DATABASE food;
USE food;
CREATE TABLE Restaurant (
    RestaurantID   INT PRIMARY KEY,
    RestaurantName VARCHAR(50) NOT NULL,
    City           VARCHAR(30)
);
CREATE TABLE Customer (
    CustomerID   INT PRIMARY KEY,
    CustomerName VARCHAR(50) NOT NULL,
    City         VARCHAR(30)
);
INSERT INTO Restaurant VALUES (1, 'A2B', 'Chennai'), (2, 'Murugan Idli', 'Madurai'),
                              (3, 'Dindigul Biryani', 'Chennai'), (4, 'Adyar Bakery', 'Chennai');
INSERT INTO Customer VALUES (1, 'Arun', 'Chennai'), (2, 'Priya', 'Madurai');"""),
Q("Create FoodOrder with foreign keys to Customer and Restaurant and use ON UPDATE CASCADE.",
 ["Two FOREIGN KEY lines, each ending ON UPDATE CASCADE.",
  "Explain: if a RestaurantID changes in Restaurant, it changes automatically in FoodOrder. Prove it with an UPDATE."],
"""CREATE TABLE FoodOrder (
    OrderID      INT PRIMARY KEY,
    CustomerID   INT,
    RestaurantID INT,
    Quantity     INT,
    Price        DECIMAL(8,2),
    Rating       DECIMAL(2,1),
    FOREIGN KEY (CustomerID)   REFERENCES Customer(CustomerID)     ON UPDATE CASCADE,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON UPDATE CASCADE
);
INSERT INTO FoodOrder VALUES (1, 1, 1, 2, 300, 4.5), (2, 2, 2, 3, 150, 5.0),
                             (3, 1, 1, 1, 200, 3.9), (4, 2, 3, 2, 400, 4.8);
UPDATE Restaurant SET RestaurantID = 10 WHERE RestaurantID = 1;
SELECT * FROM FoodOrder;"""),
Q("For each city, display total orders, average price, and total quantity where rating is at least 4.2.",
 ["\"for each city\" → GROUP BY City (City is in Restaurant → JOIN).", "\"rating at least 4.2\" is a row rule → WHERE Rating >= 4.2 (before grouping).",
  "total orders = COUNT, average price = AVG, total quantity = SUM."],
"""SELECT r.City, COUNT(f.OrderID) AS TotalOrders,
       AVG(f.Price) AS AvgPrice, SUM(f.Quantity) AS TotalQty
FROM FoodOrder f
JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
WHERE f.Rating >= 4.2
GROUP BY r.City;"""),
Q("Find restaurants that have received at least one order with rating 5, and also write a query to find restaurants that have never received any order.",
 ["\"at least one … rating 5\" → IN (SELECT … WHERE Rating = 5).", "\"never\" → NOT IN."],
"""SELECT * FROM Restaurant
WHERE RestaurantID IN (SELECT RestaurantID FROM FoodOrder WHERE Rating = 5);
SELECT * FROM Restaurant
WHERE RestaurantID NOT IN (SELECT RestaurantID FROM FoodOrder);"""),
Q("Insert a new customer and place a food order. Use COMMIT.",
 ["COMMIT recipe."],
"""SET autocommit = 0;
START TRANSACTION;
INSERT INTO Customer VALUES (3, 'Kumar', 'Salem');
INSERT INTO FoodOrder VALUES (5, 3, 2, 2, 180, 4.0);
COMMIT;
SELECT * FROM FoodOrder WHERE OrderID = 5;"""),
Q("Update the quantity and price of an order and use ROLLBACK.",
 ["ROLLBACK recipe on SET Quantity = …, Price = …."],
"""START TRANSACTION;
UPDATE FoodOrder SET Quantity = 5, Price = 450 WHERE OrderID = 5;
ROLLBACK;
SELECT * FROM FoodOrder WHERE OrderID = 5;"""),
Q("Place an order, create a savepoint, update its rating, and roll back to the savepoint.",
 ["A = new order (kept), B = rating change (undone)."],
"""START TRANSACTION;
INSERT INTO FoodOrder VALUES (6, 2, 3, 1, 250, 4.0);
SAVEPOINT sp1;
UPDATE FoodOrder SET Rating = 2.0 WHERE OrderID = 6;
ROLLBACK TO sp1;
COMMIT;
SELECT * FROM FoodOrder WHERE OrderID = 6;"""),
Q("Delete a food order and use ROLLBACK to restore it.",
 ["Restore recipe."],
"""START TRANSACTION;
DELETE FROM FoodOrder WHERE OrderID = 6;
ROLLBACK;
SELECT * FROM FoodOrder WHERE OrderID = 6;"""),
Q("Insert a new customer, place an order, create a savepoint, place another order, and roll back the second order.",
 ["Customer + order 1 (kept) → SAVEPOINT → order 2 → ROLLBACK TO."],
"""START TRANSACTION;
INSERT INTO Customer VALUES (4, 'Divya', 'Trichy');
INSERT INTO FoodOrder VALUES (7, 4, 2, 2, 160, 4.8);
SAVEPOINT sp2;
INSERT INTO FoodOrder VALUES (8, 4, 3, 1, 220, 4.1);
ROLLBACK TO sp2;
COMMIT;
SELECT * FROM FoodOrder WHERE CustomerID = 4;"""),
Q("Grant SELECT permission on Restaurant to delivery_user. Grant SELECT and INSERT permissions on FoodOrder to order_user. Grant SELECT, INSERT, and UPDATE permissions on Customer to customer_user. Revoke INSERT permission on FoodOrder from order_user. Grant all privileges on FoodOrder to restaurant_admin.",
 ["Create 4 users, then 5 lines."],
"""SET autocommit = 1;
CREATE USER IF NOT EXISTS 'delivery_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'order_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'customer_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'restaurant_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON food.Restaurant TO 'delivery_user'@'localhost';
GRANT SELECT, INSERT ON food.FoodOrder TO 'order_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON food.Customer TO 'customer_user'@'localhost';
REVOKE INSERT ON food.FoodOrder FROM 'order_user'@'localhost';
GRANT ALL PRIVILEGES ON food.FoodOrder TO 'restaurant_admin'@'localhost';
SHOW GRANTS FOR 'order_user'@'localhost';"""),
], also=[("Create a view named Food_Order_View to display OrderID, CustomerName, RestaurantName, Quantity, Price, and Rating by joining Customer, Restaurant, and FoodOrder. (Set 1)",
 ["Middle table FoodOrder + two JOINs."],
 "CREATE VIEW Food_Order_View AS\nSELECT f.OrderID, c.CustomerName, r.RestaurantName, f.Quantity, f.Price, f.Rating\nFROM FoodOrder f\nJOIN Customer c   ON f.CustomerID   = c.CustomerID\nJOIN Restaurant r ON f.RestaurantID = r.RestaurantID;\nSELECT * FROM Food_Order_View;")])
