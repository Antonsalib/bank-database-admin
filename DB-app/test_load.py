from load_sample_data import load_sample_data, check_data_exists
import pymysql
import yaml

print("Before load:")
db_config = yaml.safe_load(open('db.yaml'))
connection = pymysql.connect(host='localhost', user='root', password=db_config['mysql_password'], database='Bank')
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM Customers")
print(f"Customers: {cursor.fetchone()[0]}")
cursor.close()
connection.close()

print("\nLoading data...")
result = load_sample_data()
print(f"Load result: {result}")

print("\nAfter load:")
connection = pymysql.connect(host='localhost', user='root', password=db_config['mysql_password'], database='Bank')
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM Customers")
customers = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM Accounts")
accounts = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM Transactions")
transactions = cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM Loan")
loans = cursor.fetchone()[0]
cursor.close()
connection.close()

print(f"Customers: {customers}")
print(f"Accounts: {accounts}")
print(f"Transactions: {transactions}")
print(f"Loans: {loans}")
