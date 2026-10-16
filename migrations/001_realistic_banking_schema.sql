USE Bank;

DELIMITER $$
CREATE PROCEDURE verify_legacy_transfers()
BEGIN
    DECLARE invalid_transfers INT DEFAULT 0;
    SELECT COUNT(*) INTO invalid_transfers
    FROM Transactions
    WHERE transaction_type = 'Transfer' AND related_account_id IS NULL;

    IF invalid_transfers > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Migration stopped: every legacy transfer must have a related account';
    END IF;
END$$
DELIMITER ;

CALL verify_legacy_transfers();
DROP PROCEDURE verify_legacy_transfers;

DROP TRIGGER IF EXISTS validate_and_update_balance;

ALTER TABLE Customers
    MODIFY email VARCHAR(120) NOT NULL,
    MODIFY phone_number VARCHAR(20) NOT NULL,
    MODIFY address VARCHAR(160) NOT NULL;

CREATE TABLE Branches (
    branch_id INT PRIMARY KEY AUTO_INCREMENT,
    branch_name VARCHAR(80) NOT NULL UNIQUE,
    address VARCHAR(160) NOT NULL,
    phone_number VARCHAR(20) NULL
);

INSERT INTO Branches (branch_name, address, phone_number)
VALUES ('Main Branch', 'Address not recorded', NULL);
SET @default_branch_id = LAST_INSERT_ID();

CREATE TABLE AccountOwners (
    account_id INT NOT NULL,
    customer_id INT NOT NULL,
    owner_role ENUM('Primary', 'Joint') NOT NULL DEFAULT 'Joint',
    PRIMARY KEY (account_id, customer_id),
    CONSTRAINT fk_account_owners_account
        FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_account_owners_customer
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON DELETE RESTRICT
);

INSERT INTO AccountOwners (account_id, customer_id, owner_role)
SELECT account_id, customer_id, 'Primary'
FROM Accounts;

CREATE TABLE PaymentCards (
    payment_card_id INT PRIMARY KEY AUTO_INCREMENT,
    account_id INT NOT NULL,
    card_type ENUM('Debit Card', 'Credit Card') NOT NULL,
    last_four CHAR(4) NULL,
    expiry_date DATE NULL,
    card_status ENUM('Active', 'Blocked', 'Expired') NOT NULL DEFAULT 'Active',
    CONSTRAINT fk_payment_cards_account
        FOREIGN KEY (account_id) REFERENCES Accounts(account_id)
        ON DELETE CASCADE
);

CREATE TABLE Transfers (
    transfer_id INT PRIMARY KEY AUTO_INCREMENT,
    from_account_id INT NOT NULL,
    to_account_id INT NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    initiated_date DATE NOT NULL,
    CONSTRAINT fk_transfers_from_account
        FOREIGN KEY (from_account_id) REFERENCES Accounts(account_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_transfers_to_account
        FOREIGN KEY (to_account_id) REFERENCES Accounts(account_id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_transfer_distinct_accounts CHECK (from_account_id <> to_account_id),
    CONSTRAINT chk_transfer_amount CHECK (amount > 0)
);

ALTER TABLE Accounts
    ADD COLUMN branch_id INT NULL AFTER account_id;
UPDATE Accounts SET branch_id = @default_branch_id;

ALTER TABLE Transactions
    ADD COLUMN transfer_id INT NULL,
    ADD COLUMN payment_card_id INT NULL,
    ADD COLUMN payment_method ENUM(
        'Debit Card', 'Credit Card', 'Check', 'Cash', 'Bank Transfer'
    ) NULL,
    MODIFY amount DECIMAL(15, 2) NOT NULL,
    MODIFY transaction_type ENUM(
        'Withdrawal', 'Deposit', 'Payment', 'Transfer', 'Purchase',
        'Transfer Out', 'Transfer In'
    ) NOT NULL;

CREATE TEMPORARY TABLE LegacyTransactionMethods AS
SELECT
    transaction_id,
    SUBSTRING_INDEX(GROUP_CONCAT(card_type ORDER BY transaction_card_id), ',', 1) AS payment_method,
    MIN(CASE
        WHEN card_type IN ('Debit Card', 'Credit Card') THEN transaction_card_id
        ELSE NULL
    END) AS payment_card_id
FROM TransactionCard
GROUP BY transaction_id;

INSERT INTO PaymentCards (
    payment_card_id, account_id, card_type, last_four, expiry_date, card_status
)
SELECT
    old_card.transaction_card_id,
    old_transaction.account_id,
    old_card.card_type,
    NULL,
    NULL,
    'Active'
FROM TransactionCard AS old_card
JOIN Transactions AS old_transaction
    ON old_transaction.transaction_id = old_card.transaction_id
WHERE old_card.card_type IN ('Debit Card', 'Credit Card');

UPDATE Transactions AS transaction_record
JOIN LegacyTransactionMethods AS legacy_method
    ON legacy_method.transaction_id = transaction_record.transaction_id
SET
    transaction_record.payment_method = legacy_method.payment_method,
    transaction_record.payment_card_id = legacy_method.payment_card_id;

DROP TEMPORARY TABLE LegacyTransactionMethods;

INSERT INTO Transfers (
    transfer_id, from_account_id, to_account_id, amount, initiated_date
)
SELECT
    transaction_id, account_id, related_account_id, amount, transaction_date
FROM Transactions
WHERE transaction_type = 'Transfer';

UPDATE Transactions
SET transfer_id = transaction_id, transaction_type = 'Transfer Out'
WHERE transaction_type = 'Transfer';

INSERT INTO Transactions (
    account_id, related_account_id, transfer_id, amount, transaction_date, transaction_type
)
SELECT
    to_account_id, from_account_id, transfer_id, amount, initiated_date, 'Transfer In'
FROM Transfers;

ALTER TABLE Transactions
    MODIFY transaction_type ENUM(
        'Withdrawal', 'Deposit', 'Payment', 'Purchase', 'Transfer Out', 'Transfer In'
    ) NOT NULL,
    ADD CONSTRAINT fk_transactions_transfer
        FOREIGN KEY (transfer_id) REFERENCES Transfers(transfer_id)
        ON DELETE CASCADE,
    ADD CONSTRAINT fk_transactions_payment_card
        FOREIGN KEY (payment_card_id) REFERENCES PaymentCards(payment_card_id)
        ON DELETE SET NULL,
    ADD CONSTRAINT chk_transfer_entry_link CHECK (
        (transaction_type IN ('Transfer Out', 'Transfer In') AND transfer_id IS NOT NULL)
        OR (transaction_type NOT IN ('Transfer Out', 'Transfer In') AND transfer_id IS NULL)
    ),
    ADD CONSTRAINT chk_transaction_amount CHECK (amount > 0);

DROP TABLE TransactionCard;

ALTER TABLE Accounts
    MODIFY branch_id INT NOT NULL,
    DROP FOREIGN KEY fk_customer_id,
    DROP COLUMN customer_id,
    ADD CONSTRAINT fk_accounts_branch
        FOREIGN KEY (branch_id) REFERENCES Branches(branch_id)
        ON DELETE RESTRICT;

ALTER TABLE Loan
    DROP FOREIGN KEY fk_customer1_id,
    ADD CONSTRAINT fk_loan_customer
        FOREIGN KEY (customer_id) REFERENCES Customers(customer_id)
        ON DELETE RESTRICT;

CREATE TABLE LoanPayments (
    loan_payment_id INT PRIMARY KEY AUTO_INCREMENT,
    loan_id INT NOT NULL,
    transaction_id INT NOT NULL UNIQUE,
    payment_date DATE NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    principal_amount DECIMAL(15, 2) NOT NULL,
    interest_amount DECIMAL(15, 2) NOT NULL,
    CONSTRAINT fk_loan_payments_loan
        FOREIGN KEY (loan_id) REFERENCES Loan(loan_id)
        ON DELETE RESTRICT,
    CONSTRAINT fk_loan_payments_transaction
        FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id)
        ON DELETE RESTRICT,
    CONSTRAINT chk_loan_payment_amount CHECK (amount > 0),
    CONSTRAINT chk_loan_payment_principal CHECK (principal_amount > 0),
    CONSTRAINT chk_loan_payment_interest CHECK (interest_amount >= 0),
    CONSTRAINT chk_loan_payment_split CHECK (
        amount = principal_amount + interest_amount
    )
);

DELIMITER $$

CREATE TRIGGER validate_transaction_before_insert
BEFORE INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE current_balance DECIMAL(15, 2);
    DECLARE current_account_type VARCHAR(20);
    DECLARE card_account_id INT;
    DECLARE current_card_status VARCHAR(20);
    DECLARE transfer_from_account_id INT;
    DECLARE transfer_to_account_id INT;
    DECLARE transfer_amount DECIMAL(15, 2);

    IF NEW.amount <= 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transaction amount must be positive';
    END IF;

    SELECT balance, account_type
    INTO current_balance, current_account_type
    FROM Accounts
    WHERE account_id = NEW.account_id;

    IF NEW.transaction_type IN ('Withdrawal', 'Payment', 'Purchase', 'Transfer Out')
       AND current_account_type <> 'Credit Card'
       AND current_balance < NEW.amount THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Insufficient account balance';
    END IF;

    IF NEW.payment_card_id IS NOT NULL THEN
        SELECT account_id, card_status
        INTO card_account_id, current_card_status
        FROM PaymentCards
        WHERE payment_card_id = NEW.payment_card_id;

        IF card_account_id <> NEW.account_id OR current_card_status <> 'Active' THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Payment card is not active for this account';
        END IF;
    END IF;

    IF NEW.transaction_type IN ('Transfer Out', 'Transfer In') THEN
        SELECT from_account_id, to_account_id, amount
        INTO transfer_from_account_id, transfer_to_account_id, transfer_amount
        FROM Transfers
        WHERE transfer_id = NEW.transfer_id;

        IF transfer_amount <> NEW.amount
           OR (NEW.transaction_type = 'Transfer Out'
               AND (NEW.account_id <> transfer_from_account_id
                    OR NEW.related_account_id <> transfer_to_account_id))
           OR (NEW.transaction_type = 'Transfer In'
               AND (NEW.account_id <> transfer_to_account_id
                    OR NEW.related_account_id <> transfer_from_account_id)) THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Transfer entry does not match its transfer';
        END IF;
    END IF;
END$$

CREATE TRIGGER apply_transaction_balance_after_insert
AFTER INSERT ON Transactions
FOR EACH ROW
BEGIN
    DECLARE current_account_type VARCHAR(20);

    SELECT account_type INTO current_account_type
    FROM Accounts
    WHERE account_id = NEW.account_id;

    IF NEW.transaction_type IN ('Deposit', 'Transfer In') THEN
        UPDATE Accounts
        SET balance = balance + NEW.amount
        WHERE account_id = NEW.account_id;
    ELSEIF current_account_type = 'Credit Card' THEN
        IF NEW.transaction_type = 'Payment' THEN
            UPDATE Accounts
            SET balance = GREATEST(balance - NEW.amount, 0)
            WHERE account_id = NEW.account_id;
        ELSE
            UPDATE Accounts
            SET balance = balance + NEW.amount
            WHERE account_id = NEW.account_id;
        END IF;
    ELSE
        UPDATE Accounts
        SET balance = balance - NEW.amount
        WHERE account_id = NEW.account_id;
    END IF;
END$$

CREATE TRIGGER protect_transaction_ledger_before_delete
BEFORE DELETE ON Transactions
FOR EACH ROW
BEGIN
    SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Posted ledger entries are immutable';
END$$

DELIMITER ;

SELECT 'Migration 001 completed. Existing accounts were assigned to Main Branch.' AS migration_status;
