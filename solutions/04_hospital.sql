-- =========================================================
-- 4. HOSPITAL MANAGEMENT
-- Patient(PatientID, PatientName, City)
-- Doctor(DoctorID, DoctorName, Specialization)
-- Appointment(AppID, PatientID, DoctorID, VisitDate, Fee)
-- =========================================================
DROP DATABASE IF EXISTS hospital;
CREATE DATABASE hospital;
USE hospital;

CREATE TABLE Patient (
    PatientID   INT PRIMARY KEY,
    PatientName VARCHAR(50) NOT NULL,
    City        VARCHAR(30)
);
-- Doctor with Specialization NOT NULL
CREATE TABLE Doctor (
    DoctorID       INT PRIMARY KEY,
    DoctorName     VARCHAR(50) NOT NULL,
    Specialization VARCHAR(40) NOT NULL
);
-- Appointment with FKs to Patient and Doctor
CREATE TABLE Appointment (
    AppID     INT PRIMARY KEY,
    PatientID INT,
    DoctorID  INT,
    VisitDate DATE,
    Fee       DECIMAL(8,2),
    FOREIGN KEY (PatientID) REFERENCES Patient(PatientID),
    FOREIGN KEY (DoctorID)  REFERENCES Doctor(DoctorID)
);
INSERT INTO Patient VALUES (1, 'Arun', 'Chennai'), (2, 'Priya', 'Madurai');
INSERT INTO Doctor VALUES (1, 'Dr. Ravi', 'Cardiology'), (2, 'Dr. Meena', 'Neurology'),
                          (3, 'Dr. Kumar', 'Ortho');
INSERT INTO Appointment VALUES (1, 1, 1, '2025-01-10', 500),
                               (2, 2, 1, '2025-01-11', 500),
                               (3, 1, 2, '2025-01-12', 800);

-- Doctors who have at least one appointment
SELECT * FROM Doctor
WHERE DoctorID IN (SELECT DoctorID FROM Appointment);

-- Count appointments handled by each doctor
SELECT d.DoctorName, COUNT(a.AppID) AS TotalAppointments
FROM Doctor d
LEFT JOIN Appointment a ON d.DoctorID = a.DoctorID
GROUP BY d.DoctorID, d.DoctorName;

-- Patient names and doctor names for all appointments
SELECT p.PatientName, d.DoctorName
FROM Appointment a
JOIN Patient p ON a.PatientID = p.PatientID
JOIN Doctor d  ON a.DoctorID  = d.DoctorID;

-- Insert patient + appointment, COMMIT; update fee, ROLLBACK
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Patient VALUES (3, 'Kavya', 'Salem');
INSERT INTO Appointment VALUES (4, 3, 3, '2025-02-01', 600);
COMMIT;
START TRANSACTION;
UPDATE Appointment SET Fee = 1000 WHERE AppID = 4;
ROLLBACK;

-- Insert patient, savepoint, insert appointment, rollback to savepoint
START TRANSACTION;
INSERT INTO Patient VALUES (4, 'Rahul', 'Trichy');
SAVEPOINT sp1;
INSERT INTO Appointment VALUES (5, 4, 2, '2025-02-05', 800);
ROLLBACK TO sp1;
COMMIT;

-- Delete appointment and ROLLBACK
START TRANSACTION;
DELETE FROM Appointment WHERE AppID = 3;
ROLLBACK;

-- Update specialization, savepoint, update fee, rollback to savepoint
START TRANSACTION;
UPDATE Doctor SET Specialization = 'Cardiac Surgery' WHERE DoctorID = 1;
SAVEPOINT sp2;
UPDATE Appointment SET Fee = 900 WHERE AppID = 1;
ROLLBACK TO sp2;
COMMIT;
SET autocommit = 1;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'receptionist'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'hospital_staff'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'doctor_user'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON hospital.Doctor TO 'receptionist'@'localhost';
GRANT SELECT, INSERT ON hospital.Appointment TO 'receptionist'@'localhost';
GRANT SELECT, INSERT, UPDATE ON hospital.Patient TO 'hospital_staff'@'localhost';
REVOKE INSERT ON hospital.Appointment FROM 'receptionist'@'localhost';
GRANT SELECT ON hospital.Doctor TO 'doctor_user'@'localhost';

-- VIEW + INDEX
CREATE VIEW Appointment_Details_View AS
SELECT a.AppID, p.PatientName, d.DoctorName, d.Specialization, a.VisitDate, a.Fee
FROM Appointment a
JOIN Patient p ON a.PatientID = p.PatientID
JOIN Doctor d  ON a.DoctorID  = d.DoctorID;
SELECT * FROM Appointment_Details_View;

CREATE INDEX idx_doctor_specialization ON Doctor(Specialization);
