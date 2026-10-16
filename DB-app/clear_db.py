import pymysql
import yaml

db_config = yaml.safe_load(open('db.yaml'))
connection = pymysql.connect(host='localhost', user='root', password=db_config['mysql_password'], database='Bank')
cursor = connection.cursor()

cursor.execute("DELETE FROM TransactionCard")
cursor.execute("DELETE FROM Transactions")
cursor.execute("DELETE FROM Loan")
cursor.execute("DELETE FROM Accounts")
cursor.execute("DELETE FROM Customers")

connection.commit()
cursor.close()
connection.close()
print("Database cleared")
