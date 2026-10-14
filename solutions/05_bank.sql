-- =========================================================
-- 5. BANK MANAGEMENT
-- Customer(CustomerID, CustomerName, City)
-- Account(AccountNo, CustomerID, AccountType, Balance)
-- Transaction(TxnID, AccountNo, Amount, TxnType)
-- =========================================================
DROP DATABASE IF EXISTS bank;
CREATE DATABASE bank;
USE bank;

CREATE TABLE Customer (
    CustomerID   INT PRIMARY KEY,
    CustomerName VARCHAR(50) NOT NULL,
    City         VARCHAR(30)
);
-- Account with CHECK (Balance >= 1000)
CREATE TABLE Account (
    AccountNo   INT PRIMARY KEY,
    CustomerID  INT,
    AccountType VARCHAR(20),
    Balance     DECIMAL(12,2) CHECK (Balance >= 1000)
);
-- Add FK from Account.CustomerID to Customer.CustomerID
ALTER TABLE Account
ADD CONSTRAINT fk_cust FOREIGN KEY (CustomerID) REFERENCES Customer(CustomerID);

-- "Transaction" is a keyword, so wrap it in backticks to be safe
CREATE TABLE `Transaction` (
    TxnID     INT PRIMARY KEY,
    AccountNo INT,
    Amount    DECIMAL(12,2),
    TxnType   VARCHAR(10),
    FOREIGN KEY (AccountNo) REFERENCES Account(AccountNo)
);

INSERT INTO Customer VALUES (1, 'Arun', 'Chennai'), (2, 'Priya', 'Madurai'), (3, 'Kumar', 'Salem');
INSERT INTO Account VALUES (1001, 1, 'Savings', 50000), (1002, 2, 'Current', 80000),
                           (1003, 3, 'Savings', 20000);
INSERT INTO `Transaction` VALUES (1, 1001, 5000, 'Credit');

-- Accounts with balance > average balance
SELECT AccountNo, CustomerID, Balance FROM Account
WHERE Balance > (SELECT AVG(Balance) FROM Account);

-- Customers whose balance > average balance
SELECT c.CustomerName, a.Balance
FROM Customer c
JOIN Account a ON c.CustomerID = a.CustomerID
WHERE a.Balance > (SELECT AVG(Balance) FROM Account);

-- Accounts with balance = maximum balance
SELECT * FROM Account
WHERE Balance = (SELECT MAX(Balance) FROM Account);

-- New customer + account, COMMIT
SET autocommit = 0;
START TRANSACTION;
INSERT INTO Customer VALUES (4, 'Divya', 'Trichy');
INSERT INTO Account VALUES (1004, 4, 'Savings', 15000);
COMMIT;

-- Deduct 5000 and record the transaction, COMMIT
START TRANSACTION;
UPDATE Account SET Balance = Balance - 5000 WHERE AccountNo = 1001;
INSERT INTO `Transaction` VALUES (2, 1001, 5000, 'Debit');
COMMIT;

-- Transfer 10000 from 1002 to 1003, record both; ROLLBACK if anything fails
START TRANSACTION;
UPDATE Account SET Balance = Balance - 10000 WHERE AccountNo = 1002;
UPDATE Account SET Balance = Balance + 10000 WHERE AccountNo = 1003;
INSERT INTO `Transaction` VALUES (3, 1002, 10000, 'Debit');
INSERT INTO `Transaction` VALUES (4, 1003, 10000, 'Credit');
COMMIT;      -- if any statement gave an error, run ROLLBACK; instead

-- Deduct, savepoint, insert transaction, rollback to savepoint
START TRANSACTION;
UPDATE Account SET Balance = Balance - 2000 WHERE AccountNo = 1003;
SAVEPOINT sp1;
INSERT INTO `Transaction` VALUES (5, 1003, 2000, 'Debit');
ROLLBACK TO sp1;
COMMIT;

-- Delete a transaction and ROLLBACK
START TRANSACTION;
DELETE FROM `Transaction` WHERE TxnID = 1;
ROLLBACK;
SET autocommit = 1;

-- GRANT / REVOKE
CREATE USER IF NOT EXISTS 'bank_clerk'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'bank_manager'@'localhost' IDENTIFIED BY 'pass123';
CREATE USER IF NOT EXISTS 'bank_admin'@'localhost' IDENTIFIED BY 'pass123';
GRANT SELECT ON bank.Account TO 'bank_clerk'@'localhost';
GRANT SELECT, INSERT ON bank.`Transaction` TO 'bank_clerk'@'localhost';
GRANT SELECT, UPDATE ON bank.Account TO 'bank_manager'@'localhost';
GRANT UPDATE ON bank.Account TO 'bank_clerk'@'localhost';
REVOKE UPDATE ON bank.Account FROM 'bank_clerk'@'localhost';
GRANT ALL PRIVILEGES ON bank.Account TO 'bank_admin'@'localhost';

-- VIEW + INDEX
CREATE VIEW Customer_Account_View AS
SELECT c.CustomerID, c.CustomerName, a.AccountNo, a.AccountType, a.Balance
FROM Customer c
JOIN Account a ON c.CustomerID = a.CustomerID;
SELECT * FROM Customer_Account_View;

CREATE INDEX idx_account_balance ON Account(Balance);
