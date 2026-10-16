import pymysql
import yaml

db_config = yaml.safe_load(open('db.yaml'))
connection = pymysql.connect(host='localhost', user='root', password=db_config['mysql_password'], database='Bank')
cursor = connection.cursor()

# Clear all data
cursor.execute("DELETE FROM TransactionCard")
cursor.execute("DELETE FROM Transactions")
cursor.execute("DELETE FROM Loan")
cursor.execute("DELETE FROM Accounts")
cursor.execute("DELETE FROM Customers")

# Reset auto-increment for all tables
cursor.execute("ALTER TABLE Customers AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE Accounts AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE Transactions AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE Loan AUTO_INCREMENT = 1")
cursor.execute("ALTER TABLE TransactionCard AUTO_INCREMENT = 1")

connection.commit()
print("Database cleared and auto-increment reset to 1")

cursor.close()
connection.close()
