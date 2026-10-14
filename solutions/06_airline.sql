-- =========================================================
-- 6. AIRLINE RESERVATION
-- Passenger(PassengerID, Name)
-- Flight(FlightID, FlightName, Source, Destination, TicketPrice)
-- Ticket(TicketID, PassengerID, FlightID, SeatNo)
-- =========================================================
DROP DATABASE IF EXISTS airline;
CREATE DATABASE airline;
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
-- Insert two flights, add 500 to F1's price
INSERT INTO Flight VALUES ('F1', 'IndiGo 6E201', 'Chennai', 'Delhi',  5500);
INSERT INTO Flight VALUES ('F2', 'Air India 440', 'Chennai', 'Mumbai', 4200);
UPDATE Flight SET TicketPrice = TicketPrice + 500 WHERE FlightID = 'F1';

-- Ticket with FKs to Passenger and Flight
CREATE TABLE Ticket (
    TicketID    INT PRIMARY KEY,
    PassengerID INT,
    FlightID    VARCHAR(10),
    SeatNo      VARCHAR(5),
    FOREIGN KEY (PassengerID) REFERENCES Passenger(PassengerID),
    FOREIGN KEY (FlightID)    REFERENCES Flight(FlightID)
);
INSERT INTO Passenger VALUES (1, 'Arun'), (2, 'Priya');

-- Flights by ticket price, descending
SELECT * FROM Flight ORDER BY TicketPrice DESC;

-- All possible passenger-flight combinations (CROSS JOIN)
SELECT p.Name, f.FlightName
FROM Passenger p CROSS JOIN Flight f;

-- Insert passenger + ticket, COMMIT; update seat, ROLLBACK
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Passenger VALUES (3, 'Kumar');
INSERT INTO Ticket VALUES (1, 3, 'F1', '12A');
COMMIT;
START TRANSACTION;
UPDATE Ticket SET SeatNo = '20C' WHERE TicketID = 1;
ROLLBACK;

-- Insert passenger, savepoint, book ticket, rollback to savepoint
START TRANSACTION;
INSERT INTO Passenger VALUES (4, 'Divya');
SAVEPOINT sp1;
INSERT INTO Ticket VALUES (2, 4, 'F2', '5B');
ROLLBACK TO sp1;
COMMIT;

-- Delete ticket and ROLLBACK
START TRANSACTION;
DELETE FROM Ticket WHERE TicketID = 1;
ROLLBACK;

-- Book two tickets, savepoint after first, rollback the second
START TRANSACTION;
INSERT INTO Ticket VALUES (3, 1, 'F1', '1A');
SAVEPOINT after_first;
INSERT INTO Ticket VALUES (4, 2, 'F2', '2B');
ROLLBACK TO after_first;
COMMIT;
SET autocommit = 1;
SELECT * FROM Ticket;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'flight_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'reservation_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'airline_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON airline.Flight TO 'flight_user'@'localhost';
GRANT SELECT, INSERT ON airline.Ticket TO 'booking_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON airline.Passenger TO 'reservation_user'@'localhost';
REVOKE INSERT ON airline.Ticket FROM 'booking_user'@'localhost';
GRANT ALL PRIVILEGES ON airline.Ticket TO 'airline_admin'@'localhost';

-- VIEW + INDEX
CREATE VIEW Ticket_Details_View AS
SELECT t.TicketID, p.Name, f.FlightName, f.Source, f.Destination, t.SeatNo
FROM Ticket t
JOIN Passenger p ON t.PassengerID = p.PassengerID
JOIN Flight f    ON t.FlightID    = f.FlightID;
SELECT * FROM Ticket_Details_View;

CREATE INDEX idx_flight_source ON Flight(Source);
