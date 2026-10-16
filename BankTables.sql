CREATE DATABASE Bank;
USE Bank;

CREATE TABLE Customers(
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(60) NOT NULL,
    last_name VARCHAR(60) NOT NULL,
    email VARCHAR(60) NOT NULL UNIQUE,
    phone_number VARCHAR(13) NOT NULL,
    address VARCHAR(50) NOT NULL
);

CREATE TABLE Accounts(
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    balance DECIMAL(15, 2) NOT NULL,
    account_status ENUM('Active', 'Inactive') NOT NULL,
    account_type ENUM('Checking', 'Savings', 'Credit Card') NOT NULL,
    CONSTRAINT fk_customer_id FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
                            ON DELETE RESTRICT
);

CREATE TABLE Transactions(
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    amount FLOAT NOT NULL,
    transaction_date DATE NOT NULL,
    transaction_type ENUM('Withdrawal', 'Deposit', 'Payment', 'Transfer', 'Purchase') NOT NULL,
    related_account_id INT NULL,
    CONSTRAINT fk_account_id FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
                            ON DELETE CASCADE,
    CONSTRAINT fk_related_account FOREIGN KEY (related_account_id) REFERENCES Accounts(account_id)
                                ON DELETE SET NULL
);

CREATE TABLE Loan(
    loan_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_id INT NOT NULL,
    loan_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    loan_status ENUM('Approved', 'Pending', 'Closed') NOT NULL,
    CONSTRAINT fk_customer1_id FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
                        ON DELETE CASCADE
);

CREATE TABLE TransactionCard(
    transaction_card_id INT PRIMARY KEY AUTO_INCREMENT,
    transaction_id INT NOT NULL,
    card_type ENUM('Credit Card', 'Debit Card', 'Check') NOT NULL,
    CONSTRAINT fk_transaction_id FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
                        ON DELETE CASCADE
);


DELIMITER $$

CREATE TRIGGER validate_and_update_balance
AFTER INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE current_balance DECIMAL(15, 2);
    DECLARE related_balance DECIMAL(15, 2);
    DECLARE current_account_type ENUM('Checking', 'Savings', 'Credit Card');

    -- Fetch the balance and account type of the account
    SELECT balance, account_type INTO current_balance, current_account_type
    FROM Accounts
    WHERE account_id = NEW.account_id;

    -- Handle different transaction types
    IF NEW.transaction_type = 'Deposit' THEN
        -- Add amount to the account
        UPDATE Accounts
        SET balance = current_balance + NEW.amount
        WHERE account_id = NEW.account_id;

    ELSEIF NEW.transaction_type IN ('Withdrawal', 'Purchase') THEN
        IF current_account_type = 'Credit Card' THEN
            -- Increase credit card balance (debt increases)
            UPDATE Accounts
            SET balance = current_balance + NEW.amount
            WHERE account_id = NEW.account_id;


        ELSE
            -- Deduct amount from non-credit accounts (Checking/Savings)
            UPDATE Accounts
            SET balance = current_balance - NEW.amount
            WHERE account_id = NEW.account_id;
        END IF;

    ELSEIF NEW.transaction_type = 'Payment' THEN
        IF current_account_type = 'Credit Card' THEN
            -- Increase credit card balance (debt increases)
            UPDATE Accounts
            SET balance = current_balance + NEW.amount
            WHERE account_id = NEW.account_id;
        ELSE
            -- Deduct from the account making the payment
            UPDATE Accounts
            SET balance = current_balance - NEW.amount
            WHERE account_id = NEW.account_id;
        END IF;

        -- Deduct from the related account (e.g., Credit Card) if specified
        IF NEW.related_account_id IS NOT NULL THEN
            SELECT balance INTO related_balance
            FROM Accounts
            WHERE account_id = NEW.related_account_id;

            UPDATE Accounts
            SET balance = related_balance - NEW.amount
            WHERE account_id = NEW.related_account_id;
        END IF;

    ELSEIF NEW.transaction_type = 'Transfer' THEN
        -- Deduct amount from sender account
        UPDATE Accounts
        SET balance = current_balance - NEW.amount
        WHERE account_id = NEW.account_id;

        -- Add amount to receiver account if specified
        IF NEW.related_account_id IS NOT NULL THEN
            SELECT balance INTO related_balance
            FROM Accounts
            WHERE account_id = NEW.related_account_id;

            UPDATE Accounts
            SET balance = related_balance + NEW.amount
            WHERE account_id = NEW.related_account_id;
        END IF;

    END IF;
END$$

DELIMITER ;
