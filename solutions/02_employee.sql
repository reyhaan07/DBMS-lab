-- =========================================================
-- 2. EMPLOYEE MANAGEMENT
-- Employee(EmpID, EmpName, DeptID, Salary, HireDate)
-- Department(DeptID, DeptName, ManagerID)
-- =========================================================
DROP DATABASE IF EXISTS company;
CREATE DATABASE company;
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
INSERT INTO Department VALUES (1, 'HR', 201), (2, 'IT', 202);

INSERT INTO Employee VALUES (201, 'Ravi',  1, 45000, '2020-06-15');
INSERT INTO Employee VALUES (202, 'Meena', 2, 60000, '2019-03-10');
INSERT INTO Employee VALUES (203, 'Suresh',2, 52000, '2021-01-05');

-- Update Meena's salary to 75000
UPDATE Employee SET Salary = 75000 WHERE EmpName = 'Meena';

-- Add a foreign key from Employee.DeptID to Department.DeptID
ALTER TABLE Employee
ADD CONSTRAINT fk_dept FOREIGN KEY (DeptID) REFERENCES Department(DeptID);

-- Try inserting an employee with DeptID 99  -> FAILS
-- INSERT INTO Employee VALUES (205, 'Vijay', 99, 30000, '2022-02-02');
-- ERROR 1452: Cannot add or update a child row: a foreign key constraint fails.
-- Reason: DeptID 99 does not exist in the parent table Department
-- (referential integrity).

-- Employees with salary > average salary
SELECT EmpID, EmpName, Salary FROM Employee
WHERE Salary > (SELECT AVG(Salary) FROM Employee);

-- Departments having more than one employee (GROUP BY + HAVING)
SELECT DeptID, COUNT(*) AS EmpCount
FROM Employee
GROUP BY DeptID
HAVING COUNT(*) > 1;

-- Highest salary in each department
SELECT DeptID, MAX(Salary) AS HighestSalary
FROM Employee
GROUP BY DeptID;

-- Pairs of employees in the same department (SELF JOIN)
SELECT e1.EmpName AS Employee1, e2.EmpName AS Employee2, e1.DeptID
FROM Employee e1
JOIN Employee e2 ON e1.DeptID = e2.DeptID AND e1.EmpID < e2.EmpID;

-- Increase salary of all employees in a department, COMMIT
SET autocommit = 0;
START TRANSACTION;
UPDATE Employee SET Salary = Salary + 5000 WHERE DeptID = 2;
COMMIT;

-- Update salary, savepoint, update department, rollback to savepoint
START TRANSACTION;
UPDATE Employee SET Salary = 50000 WHERE EmpID = 201;
SAVEPOINT sp1;
UPDATE Employee SET DeptID = 2 WHERE EmpID = 201;
ROLLBACK TO sp1;
COMMIT;

-- Delete an employee and ROLLBACK
START TRANSACTION;
DELETE FROM Employee WHERE EmpID = 203;
ROLLBACK;

-- Insert new department and employee, COMMIT both
START TRANSACTION;
INSERT INTO Department VALUES (3, 'Sales', 204);
INSERT INTO Employee VALUES (204, 'Anil', 3, 35000, '2023-07-01');
COMMIT;

-- Increase by 10%, savepoint, another 5%, rollback to first savepoint
START TRANSACTION;
UPDATE Employee SET Salary = Salary * 1.10;
SAVEPOINT after_10;
UPDATE Employee SET Salary = Salary * 1.05;
ROLLBACK TO after_10;
COMMIT;
SET autocommit = 1;
SELECT * FROM Employee;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'hr_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'manager_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'employee_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON company.Employee TO 'hr_user'@'localhost';
GRANT SELECT, UPDATE ON company.Employee TO 'manager_user'@'localhost';
GRANT INSERT ON company.Employee TO 'hr_user'@'localhost';
REVOKE UPDATE ON company.Employee FROM 'manager_user'@'localhost';
GRANT SELECT ON company.Department TO 'employee_user'@'localhost';

-- VIEW + INDEX
CREATE VIEW Employee_Department_View AS
SELECT e.EmpID, e.EmpName, e.Salary, d.DeptName
FROM Employee e
JOIN Department d ON e.DeptID = d.DeptID;
SELECT * FROM Employee_Department_View;

CREATE INDEX idx_employee_salary ON Employee(Salary);
