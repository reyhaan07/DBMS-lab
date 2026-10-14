-- =========================================================
-- 8. FOOD DELIVERY
-- Restaurant(RestaurantID, RestaurantName, City)
-- Customer(CustomerID, CustomerName, City)
-- FoodOrder(OrderID, CustomerID, RestaurantID, Quantity, Price, Rating)
-- =========================================================
DROP DATABASE IF EXISTS food;
CREATE DATABASE food;
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
-- FoodOrder with FKs and ON UPDATE CASCADE
CREATE TABLE FoodOrder (
    OrderID      INT PRIMARY KEY,
    CustomerID   INT,
    RestaurantID INT,
    Quantity     INT,
    Price        DECIMAL(8,2),
    Rating       DECIMAL(2,1),
    FOREIGN KEY (CustomerID)   REFERENCES Customer(CustomerID)     ON UPDATE CASCADE,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON UPDATE CASCADE
);
-- ON UPDATE CASCADE: if RestaurantID changes in Restaurant, it changes
-- automatically in FoodOrder too.

INSERT INTO Restaurant VALUES (1, 'A2B', 'Chennai'), (2, 'Murugan Idli', 'Madurai'),
                              (3, 'Dindigul Biryani', 'Chennai');
INSERT INTO Customer VALUES (1, 'Arun', 'Chennai'), (2, 'Priya', 'Madurai');
INSERT INTO FoodOrder VALUES (1, 1, 1, 2, 300, 4.5), (2, 2, 2, 3, 150, 5.0),
                             (3, 1, 1, 1, 200, 3.9);

-- Show cascade
UPDATE Restaurant SET RestaurantID = 10 WHERE RestaurantID = 1;
SELECT * FROM FoodOrder;     -- orders 1 and 3 now show RestaurantID 10

-- For each city: total orders, avg price, total quantity where rating >= 4.2
SELECT r.City, COUNT(f.OrderID) AS TotalOrders,
       AVG(f.Price) AS AvgPrice, SUM(f.Quantity) AS TotalQty
FROM FoodOrder f
JOIN Restaurant r ON f.RestaurantID = r.RestaurantID
WHERE f.Rating >= 4.2
GROUP BY r.City;

-- Restaurants with at least one order rated 5
SELECT * FROM Restaurant
WHERE RestaurantID IN (SELECT RestaurantID FROM FoodOrder WHERE Rating = 5);

-- Restaurants that never received any order
SELECT * FROM Restaurant
WHERE RestaurantID NOT IN (SELECT RestaurantID FROM FoodOrder);

-- New customer + order, COMMIT; update qty & price, ROLLBACK
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Customer VALUES (3, 'Kumar', 'Salem');
INSERT INTO FoodOrder VALUES (4, 3, 2, 2, 180, 4.0);
COMMIT;
START TRANSACTION;
UPDATE FoodOrder SET Quantity = 5, Price = 450 WHERE OrderID = 4;
ROLLBACK;

-- Place order, savepoint, update rating, rollback to savepoint
START TRANSACTION;
INSERT INTO FoodOrder VALUES (5, 2, 3, 1, 250, 4.0);
SAVEPOINT sp1;
UPDATE FoodOrder SET Rating = 2.0 WHERE OrderID = 5;
ROLLBACK TO sp1;
COMMIT;

-- Delete an order and ROLLBACK
START TRANSACTION;
DELETE FROM FoodOrder WHERE OrderID = 5;
ROLLBACK;

-- New customer, order, savepoint, another order, roll back the second
START TRANSACTION;
INSERT INTO Customer VALUES (4, 'Divya', 'Trichy');
INSERT INTO FoodOrder VALUES (6, 4, 2, 2, 160, 4.8);
SAVEPOINT sp2;
INSERT INTO FoodOrder VALUES (7, 4, 3, 1, 220, 4.1);
ROLLBACK TO sp2;
COMMIT;
SET autocommit = 1;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'delivery_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'order_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'customer_user'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'restaurant_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON food.Restaurant TO 'delivery_user'@'localhost';
GRANT SELECT, INSERT ON food.FoodOrder TO 'order_user'@'localhost';
GRANT SELECT, INSERT, UPDATE ON food.Customer TO 'customer_user'@'localhost';
REVOKE INSERT ON food.FoodOrder FROM 'order_user'@'localhost';
GRANT ALL PRIVILEGES ON food.FoodOrder TO 'restaurant_admin'@'localhost';

-- VIEW
CREATE VIEW Food_Order_View AS
SELECT f.OrderID, c.CustomerName, r.RestaurantName, f.Quantity, f.Price, f.Rating
FROM FoodOrder f
JOIN Customer c   ON f.CustomerID   = c.CustomerID
JOIN Restaurant r ON f.RestaurantID = r.RestaurantID;
SELECT * FROM Food_Order_View;
