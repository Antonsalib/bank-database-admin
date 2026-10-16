"""Load the synthetic development dataset into the local Bank database."""

import os

import pymysql
import yaml


def _database_password():
    with open('db.yaml', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    password = config.get('mysql_password') if isinstance(config, dict) else None
    if not password:
        raise ValueError("Set 'mysql_password' in DB-app/db.yaml before connecting.")
    return password


def load_sample_data():
    """Load all synthetic sample statements atomically."""
    sample_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data.sql')
    with open(sample_path, encoding='utf-8') as sample_file:
        statements = [
            statement.strip()
            for statement in sample_file.read().split(';')
            if statement.strip()
        ]

    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=_database_password(),
        database='Bank',
        autocommit=False
    )
    try:
        with connection.cursor() as cursor:
            for statement in statements:
                cursor.execute(statement)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print(f'Successfully loaded sample data! ({len(statements)} SQL statements executed)')
    return True


def check_data_exists():
    """Return whether the Bank database already has customer records."""
    connection = pymysql.connect(
        host='localhost',
        user='root',
        password=_database_password(),
        database='Bank'
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT COUNT(*) FROM Customers')
            return cursor.fetchone()[0] > 0
    finally:
        connection.close()


if __name__ == '__main__':
    if not check_data_exists():
        load_sample_data()
    else:
        print('Database already contains customer records; skipping sample load.')
