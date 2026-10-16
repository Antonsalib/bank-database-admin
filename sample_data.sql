INSERT INTO Customers (first_name, last_name, email, phone_number, address)
VALUES ('Alex', 'Morgan', 'alex.morgan@example.test', '5550101001', '100 Example Avenue, Sample City'),
       ('Jordan', 'Lee', 'jordan.lee@example.test', '5550101002', '200 Example Avenue, Sample City'),
       ('Sam', 'Rivera', 'sam.rivera@example.test', '5550101003', '300 Example Avenue, Sample City');

INSERT INTO Accounts (customer_id, balance, account_status, account_type)
VALUES (1, 2500.00, 'Active', 'Checking'),
       (2, 7200.00, 'Active', 'Savings'),
       (3, 950.00, 'Active', 'Checking');

INSERT INTO Transactions (account_id, amount, transaction_date, transaction_type, related_account_id)
VALUES (1, 125.50, '2025-01-15', 'Deposit', NULL),
       (2, 40.00, '2025-01-16', 'Withdrawal', NULL),
       (1, 25.00, '2025-01-17', 'Purchase', NULL);

INSERT INTO Loan (customer_id, loan_amount, interest_rate, loan_status)
VALUES (1, 12000.00, 4.25, 'Approved'),
       (2, 6500.00, 5.10, 'Pending'),
       (3, 3000.00, 3.75, 'Closed');

INSERT INTO TransactionCard (transaction_id, card_type)
VALUES (1, 'Debit Card'),
       (2, 'Check'),
       (3, 'Credit Card');
