-- =========================================================
-- 10. TRIGGERS (INSERT / UPDATE / DELETE) in MySQL
-- Main table + a log (audit) table that the triggers write into
-- =========================================================
DROP DATABASE IF EXISTS trig;
CREATE DATABASE trig;
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
);

-- ---------- AFTER INSERT trigger ----------
DELIMITER //
CREATE TRIGGER trg_after_insert
AFTER INSERT ON Account
FOR EACH ROW
BEGIN
    INSERT INTO Account_Log (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (NEW.AccountNo, 'INSERT', NULL, NEW.Balance, NOW());
END //
DELIMITER ;

-- ---------- AFTER UPDATE trigger ----------
DELIMITER //
CREATE TRIGGER trg_after_update
AFTER UPDATE ON Account
FOR EACH ROW
BEGIN
    INSERT INTO Account_Log (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (NEW.AccountNo, 'UPDATE', OLD.Balance, NEW.Balance, NOW());
END //
DELIMITER ;

-- ---------- AFTER DELETE trigger ----------
DELIMITER //
CREATE TRIGGER trg_after_delete
AFTER DELETE ON Account
FOR EACH ROW
BEGIN
    INSERT INTO Account_Log (AccountNo, Action, OldBalance, NewBalance, ActionTime)
    VALUES (OLD.AccountNo, 'DELETE', OLD.Balance, NULL, NOW());
END //
DELIMITER ;

-- Test them (this is the "implement" part)
INSERT INTO Account VALUES (1001, 'Arun', 5000);
INSERT INTO Account VALUES (1002, 'Priya', 8000);
UPDATE Account SET Balance = 6000 WHERE AccountNo = 1001;
DELETE FROM Account WHERE AccountNo = 1002;
SELECT * FROM Account_Log;

-- ---------- BEFORE INSERT trigger (validation example) ----------
DELIMITER //
CREATE TRIGGER trg_before_insert
BEFORE INSERT ON Account
FOR EACH ROW
BEGIN
    IF NEW.Balance < 0 THEN
        SET NEW.Balance = 0;
    END IF;
END //
DELIMITER ;
INSERT INTO Account VALUES (1003, 'Kumar', -500);
SELECT * FROM Account;

SHOW TRIGGERS;
-- DROP TRIGGER IF EXISTS trg_after_insert;
