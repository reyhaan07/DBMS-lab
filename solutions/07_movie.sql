-- =========================================================
-- 7. MOVIE BOOKING
-- Movie(MovieID, MovieName, Genre, TicketPrice)
-- Customer(CustomerID, CustomerName)
-- Booking(BookingID, CustomerID, MovieID, SeatsBooked)
-- =========================================================
DROP DATABASE IF EXISTS cinema;
CREATE DATABASE cinema;
USE cinema;

-- Movie with TicketPrice DEFAULT 150
CREATE TABLE Movie (
    MovieID     INT PRIMARY KEY,
    MovieName   VARCHAR(50) NOT NULL,
    Genre       VARCHAR(20),
    TicketPrice DECIMAL(6,2) DEFAULT 150
);
INSERT INTO Movie VALUES (1, 'Leo', 'Action', 200);
-- No ticket price given -> DEFAULT 150 is used
INSERT INTO Movie (MovieID, MovieName, Genre) VALUES (2, 'Jailer', 'Action');
INSERT INTO Movie (MovieID, MovieName, Genre) VALUES (3, 'Vikram', 'Thriller');
SELECT * FROM Movie;

CREATE TABLE Customer (
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
INSERT INTO Booking VALUES (1, 1, 1, 4), (2, 2, 1, 5), (3, 1, 2, 2);

-- Average seats per movie, only where avg > 3
SELECT MovieID, AVG(SeatsBooked) AS AvgSeats
FROM Booking
GROUP BY MovieID
HAVING AVG(SeatsBooked) > 3;

-- Every booking and every movie (FULL OUTER JOIN = LEFT JOIN UNION RIGHT JOIN in MySQL)
SELECT b.BookingID, b.SeatsBooked, m.MovieID, m.MovieName
FROM Booking b LEFT JOIN Movie m ON b.MovieID = m.MovieID
UNION
SELECT b.BookingID, b.SeatsBooked, m.MovieID, m.MovieName
FROM Booking b RIGHT JOIN Movie m ON b.MovieID = m.MovieID;

-- New customer + booking, COMMIT; update seats, ROLLBACK
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Customer VALUES (3, 'Kumar');
INSERT INTO Booking VALUES (4, 3, 3, 3);
COMMIT;
START TRANSACTION;
UPDATE Booking SET SeatsBooked = 10 WHERE BookingID = 4;
ROLLBACK;

-- Booking, savepoint, modify seats, rollback to savepoint
START TRANSACTION;
INSERT INTO Booking VALUES (5, 2, 3, 2);
SAVEPOINT sp1;
UPDATE Booking SET SeatsBooked = 6 WHERE BookingID = 5;
ROLLBACK TO sp1;
COMMIT;

-- Delete booking and ROLLBACK
START TRANSACTION;
DELETE FROM Booking WHERE BookingID = 5;
ROLLBACK;

-- Two bookings, savepoint between, roll back only the second
START TRANSACTION;
INSERT INTO Booking VALUES (6, 1, 3, 1);
SAVEPOINT between_bookings;
INSERT INTO Booking VALUES (7, 2, 2, 2);
ROLLBACK TO between_bookings;
COMMIT;
SET autocommit = 1;
SELECT * FROM Booking;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'movie_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'booking_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'customer_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'movie_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON cinema.Movie TO 'movie_user'@'localhost';
GRANT SELECT, INSERT ON cinema.Booking TO 'booking_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON cinema.Customer TO 'customer_user'@'localhost';
REVOKE INSERT ON cinema.Booking FROM 'booking_user'@'localhost';
GRANT ALL PRIVILEGES ON cinema.Booking TO 'movie_admin'@'localhost';

-- VIEW + INDEX
CREATE VIEW Movie_Booking_View AS
SELECT b.BookingID, c.CustomerName, m.MovieName, m.Genre, b.SeatsBooked
FROM Booking b
JOIN Customer c ON b.CustomerID = c.CustomerID
JOIN Movie m    ON b.MovieID    = m.MovieID;
SELECT * FROM Movie_Booking_View;

CREATE INDEX idx_movie_genre ON Movie(Genre);
