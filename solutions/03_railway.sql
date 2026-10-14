-- =========================================================
-- 3. RAILWAY RESERVATION
-- Passenger(PassengerID, Name, Age)
-- Train(TrainID, TrainName, Source, Destination)
-- Booking(BookingID, PassengerID, TrainID, SeatsBooked, Fare)
-- =========================================================
DROP DATABASE IF EXISTS railway;
CREATE DATABASE railway;
USE railway;

CREATE TABLE Passenger (
    PassengerID INT PRIMARY KEY,
    Name        VARCHAR(50) NOT NULL,
    Age         INT
);

-- Train with TrainName UNIQUE
CREATE TABLE Train (
    TrainID     INT PRIMARY KEY,
    TrainName   VARCHAR(50) UNIQUE,
    Source      VARCHAR(30),
    Destination VARCHAR(30)
);
INSERT INTO Train VALUES (1, 'Vaigai Express', 'Chennai', 'Madurai');
INSERT INTO Train VALUES (2, 'Kovai Express',  'Chennai', 'Coimbatore');
-- Delete the train whose destination is Coimbatore
DELETE FROM Train WHERE Destination = 'Coimbatore';
INSERT INTO Train VALUES (2, 'Kovai Express',  'Chennai', 'Coimbatore');

-- Booking with FKs; ON DELETE CASCADE on TrainID
CREATE TABLE Booking (
    BookingID   INT PRIMARY KEY,
    PassengerID INT,
    TrainID     INT,
    SeatsBooked INT,
    Fare        DECIMAL(8,2),
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID),
    FOREIGN KEY (TrainID) REFERENCES Train(TrainID) ON DELETE CASCADE
);
-- ON DELETE CASCADE: when a train is deleted from Train, all bookings
-- in Booking with that TrainID are deleted automatically.

INSERT INTO Passenger VALUES (1, 'Arun', 25), (2, 'Priya', 30), (3, 'Kumar', 40);
INSERT INTO Booking VALUES (1, 1, 1, 2, 500), (2, 2, 1, 1, 300), (3, 1, 2, 3, 900);

-- Show cascade
DELETE FROM Train WHERE TrainID = 2;
SELECT * FROM Booking;           -- booking 3 disappeared automatically
INSERT INTO Train VALUES (2, 'Kovai Express', 'Chennai', 'Coimbatore');
INSERT INTO Booking VALUES (3, 1, 2, 3, 900);

-- Passengers who made at least one booking
SELECT Name FROM Passenger
WHERE PassengerID IN (SELECT PassengerID FROM Booking);

-- All passengers and their bookings incl. those with no booking (LEFT JOIN)
SELECT p.PassengerID, p.Name, b.BookingID, b.TrainID, b.Fare
FROM Passenger p
LEFT JOIN Booking b ON p.PassengerID = b.PassengerID;

-- Bookings whose fare > average fare of the SAME train (CORRELATED subquery)
SELECT * FROM Booking b1
WHERE Fare > (SELECT AVG(Fare) FROM Booking b2 WHERE b2.TrainID = b1.TrainID);

-- Insert passenger + booking, COMMIT
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Passenger VALUES (4, 'Divya', 22);
INSERT INTO Booking VALUES (4, 4, 1, 2, 600);
COMMIT;

-- Total fare collected for each train
SELECT TrainID, SUM(Fare) AS TotalFare FROM Booking GROUP BY TrainID;

-- Update seats & fare, ROLLBACK
START TRANSACTION;
UPDATE Booking SET SeatsBooked = 5, Fare = 1500 WHERE BookingID = 1;
ROLLBACK;

-- Insert passenger, SAVEPOINT, booking, rollback to savepoint
START TRANSACTION;
INSERT INTO Passenger VALUES (5, 'Rahul', 28);
SAVEPOINT sp1;
INSERT INTO Booking VALUES (5, 5, 2, 1, 450);
ROLLBACK TO sp1;
COMMIT;

-- Delete a booking and ROLLBACK
START TRANSACTION;
DELETE FROM Booking WHERE BookingID = 2;
ROLLBACK;

-- Modify fare, savepoint, modify seats, rollback to savepoint
START TRANSACTION;
UPDATE Booking SET Fare = 550 WHERE BookingID = 1;
SAVEPOINT sp2;
UPDATE Booking SET SeatsBooked = 4 WHERE BookingID = 1;
ROLLBACK TO sp2;
COMMIT;
SET autocommit = 1;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'reservation_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'railway_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON railway.Train TO 'reservation_user'@'localhost';
GRANT SELECT, INSERT ON railway.Booking TO 'booking_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON railway.Passenger TO 'reservation_user'@'localhost';
REVOKE INSERT ON railway.Booking FROM 'booking_user'@'localhost';
GRANT ALL PRIVILEGES ON railway.Booking TO 'railway_admin'@'localhost';

-- VIEW + INDEX
CREATE VIEW Booking_Details_View AS
SELECT b.BookingID, p.Name, t.TrainName, b.SeatsBooked, b.Fare
FROM Booking b
JOIN Passenger p ON b.PassengerID = p.PassengerID
JOIN Train t     ON b.TrainID     = t.TrainID;
SELECT * FROM Booking_Details_View;

CREATE INDEX idx_train_destination ON Train(Destination);
