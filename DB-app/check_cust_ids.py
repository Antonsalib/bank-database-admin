import pymysql
import yaml

db_config = yaml.safe_load(open('db.yaml'))
connection = pymysql.connect(host='localhost', user='root', password=db_config['mysql_password'], database='Bank')
cursor = connection.cursor()

cursor.execute("SELECT customer_id FROM Customers LIMIT 10")
results = cursor.fetchall()
print("First 10 customer IDs in database:")
for row in results:
    print(row[0])

cursor.execute("SELECT MIN(customer_id), MAX(customer_id), COUNT(*) FROM Customers")
result = cursor.fetchone()
print(f"\nCustomer ID range: {result[0]} to {result[1]}, Count: {result[2]}")

cursor.close()
connection.close()
