# Bank Database Admin

A Flask application for administering a sample banking database. Browse and manage customers, accounts, loans, transactions, and transaction cards from a responsive dashboard.

## Features

- Dashboard with database record counts, recent transaction activity, and a table overview.
- Browse, add, edit, and delete customer, account, and loan records.
- Browse, add, and delete transactions and transaction-card records.
- Search customer records by name or email.
- MySQL schema and sample data scripts for local development.

## Requirements

- Python 3.10 or later.
- MySQL Server and the MySQL command-line client.

## Setup

1. Create the database schema from the project root:

   ```bash
   mysql -u root -p < BankTables.sql
   ```

   This script creates the `Bank` database, its tables, foreign keys, and transaction trigger.

2. Create the app's local database configuration:

   ```bash
   cd DB-app
   cp db.yaml.example db.yaml
   ```

   Edit `db.yaml` and set `mysql_password` to your local MySQL root password. The application currently connects to MySQL on `localhost` as `root` and uses the `Bank` database. `db.yaml` is ignored by Git and must not be committed.

3. Create and activate a Python virtual environment, then install dependencies:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

4. Start the application from inside `DB-app`:

   ```bash
   python run.py
   ```

   Open [http://127.0.0.1:5000](http://127.0.0.1:5000). Stop the development server with **Ctrl+C**.

On first startup, the app loads synthetic demo rows from `../sample_data.sql` if the `Customers` table is empty. You can also load that SQL file manually from the project root:

```bash
mysql -u root -p Bank < sample_data.sql
```

## Project layout

```text
.
├── BankTables.sql       # MySQL database schema and trigger
├── sample_data.sql      # Synthetic sample rows for local development
└── DB-app/
    ├── app/             # Flask app, routes, templates, and static assets
    ├── db.yaml.example  # Local MySQL password configuration template
    ├── requirements.txt
    └── run.py
```

## Development notes

- The original local SQL exports are excluded from Git because they contain customer information. `sample_data.sql` contains synthetic demo records instead.
- `DB-app/clear_db.py` and `DB-app/reset_db.py` delete database records. Review their contents and confirm the target database before running either script.
- Do not commit `DB-app/db.yaml`, credentials, or real customer data.
