INSERT INTO Branches (branch_id, branch_name, address, phone_number)
VALUES (1, 'Central Branch', '100 Example Avenue, Sample City', '5550100001'),
       (2, 'West Branch', '200 Example Avenue, Sample City', '5550100002');

INSERT INTO Customers (first_name, last_name, email, phone_number, address)
VALUES ('Alex', 'Morgan', 'alex.morgan@example.test', '5550101001', '100 Example Avenue, Sample City'),
       ('Jordan', 'Lee', 'jordan.lee@example.test', '5550101002', '200 Example Avenue, Sample City'),
       ('Sam', 'Rivera', 'sam.rivera@example.test', '5550101003', '300 Example Avenue, Sample City');

INSERT INTO Accounts (account_id, branch_id, balance, account_status, account_type)
VALUES (1, 1, 2500.00, 'Active', 'Checking'),
       (2, 2, 7200.00, 'Active', 'Savings'),
       (3, 1, 950.00, 'Active', 'Checking');

INSERT INTO AccountOwners (account_id, customer_id, owner_role)
VALUES (1, 1, 'Primary'),
       (2, 2, 'Primary'),
       (3, 3, 'Primary'),
       (1, 2, 'Joint');

INSERT INTO PaymentCards (payment_card_id, account_id, card_type, last_four, expiry_date, card_status)
VALUES (1, 1, 'Debit Card', '1001', '2028-12-31', 'Active'),
       (2, 2, 'Debit Card', '1002', '2028-12-31', 'Active');

INSERT INTO Transfers (transfer_id, from_account_id, to_account_id, amount, initiated_date)
VALUES (1, 1, 2, 50.00, '2025-01-18');

INSERT INTO Transactions (
    transaction_id, account_id, related_account_id, transfer_id, amount, transaction_date,
    transaction_type, payment_card_id, payment_method
)
VALUES (1, 1, NULL, NULL, 125.50, '2025-01-15', 'Deposit', NULL, NULL),
       (2, 2, NULL, NULL, 40.00, '2025-01-16', 'Withdrawal', 2, 'Debit Card'),
       (3, 1, NULL, NULL, 25.00, '2025-01-17', 'Purchase', 1, 'Debit Card'),
       (4, 1, 2, 1, 50.00, '2025-01-18', 'Transfer Out', NULL, 'Bank Transfer'),
       (5, 2, 1, 1, 50.00, '2025-01-18', 'Transfer In', NULL, 'Bank Transfer'),
       (6, 1, NULL, NULL, 300.00, '2025-01-20', 'Payment', NULL, 'Bank Transfer');

INSERT INTO Loan (customer_id, loan_amount, interest_rate, loan_status)
VALUES (1, 12000.00, 4.25, 'Approved'),
       (2, 6500.00, 5.10, 'Pending'),
       (3, 3000.00, 3.75, 'Closed');

INSERT INTO LoanPayments (
    loan_id, transaction_id, payment_date, amount, principal_amount, interest_amount
)
VALUES (1, 6, '2025-01-20', 300.00, 250.00, 50.00);
