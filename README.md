# Bank Database Admin

An educational Flask/MySQL project for exploring relational database design through a small banking administration app. It demonstrates normalized ownership relationships, branches, card and loan-payment lifecycles, auditable transactions, and balanced account transfers. It is a local learning/demo application, **not a production banking system**.

## What the project models

- **Customers** can own one or more accounts; accounts can have primary and joint owners.
- **Branches** group accounts by their servicing location.
- **Transactions** are a ledger. Transfers create paired debit/credit entries in one database transaction.
- **PaymentCards** belong to accounts. The app stores only optional last-four digits—never full card numbers or CVVs.
- **LoanPayments** link a repayment to both its loan and the account transaction that debited the repayment.

The core schema has nine tables: `Customers`, `Accounts`, `AccountOwners`, `Branches`, `Loan`, `LoanPayments`, `Transactions`, `PaymentCards`, and `Transfers`.

## Requirements

- Python 3.10 or later.
- MySQL 8.0 or later.

## Fresh database setup

From this project root, create the schema:

```bash
mysql -u root -p < BankTables.sql
```

Create a local password configuration:

```bash
cd DB-app
cp db.yaml.example db.yaml
```

Edit `DB-app/db.yaml` and set `mysql_password` to your local MySQL root password. The app expects MySQL on `localhost`, the `root` user, and a database named `Bank`. The credentials file is ignored by Git; never commit it.

Create a Python environment, install dependencies, and run the app:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Stop the development server with **Ctrl+C**.

When the database has no customers, the app loads synthetic records from `../sample_data.sql`. To load them manually, run this from the project root after creating the schema:

```bash
mysql -u root -p Bank < sample_data.sql
```

## Upgrade an existing database

The normalized schema changes the account/customer relationship, replaces transaction-attached cards with account cards, and converts each old transfer into two ledger entries. The migration preserves customer, account, loan, and transaction records and assigns existing accounts to a new `Main Branch`. Legacy card rows become masked card records where applicable; check-payment labels remain on their transactions.

**Back up your database first** and save the backup outside this repository. MySQL schema changes auto-commit, so the migration cannot be rolled back as one transaction.

```bash
mysqldump -u root -p Bank > "$HOME/Bank-before-001.sql"
mysql -u root -p < migrations/001_realistic_banking_schema.sql
```

Run the migration exactly once against the existing `Bank` database. It stops before changing the schema if it finds a legacy transfer without a related account. Do not run `BankTables.sql` over an existing database; that file is for a fresh setup.

## Project layout

```text
.
├── BankTables.sql
├── migrations/
│   └── 001_realistic_banking_schema.sql
├── sample_data.sql
└── DB-app/
    ├── app/                 # Models, routes, templates, and static assets
    ├── db.yaml.example
    ├── requirements.txt
    └── run.py
```

## Safety notes

- `sample_data.sql` contains synthetic demo records. Original local SQL exports with personal data are intentionally excluded.
- The app is for learning and local demonstrations. Do not use real banking/customer data or real payment-card details.
- `DB-app/clear_db.py` and `DB-app/reset_db.py` delete database data. Review the target database and back it up before running destructive scripts.
