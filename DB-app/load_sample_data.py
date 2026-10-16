"""
Script to load sample data into the database
"""
import pymysql
import yaml
import os

def load_sample_data():
    """Load the synthetic sample data from sample_data.sql into the database."""
    try:
        # Load database configuration
        db_config = yaml.safe_load(open('db.yaml'))
        
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=db_config['mysql_password'],
            database='Bank',
            autocommit=False
        )
        
        # Read the SQL file
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'sample_data.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"Sample data file not found at {sql_file_path}")
            connection.close()
            return False
        
        cursor = connection.cursor()
        loaded_count = 0
        
        with open(sql_file_path, 'r') as f:
            sql_content = f.read()
        
        # Parse SQL file more carefully
        # Split by lines and rebuild complete statements
        lines = sql_content.split('\n')
        current_statement = ""
        
        for line in lines:
            line = line.rstrip()
            
            # Skip empty lines and comments
            if not line or line.startswith('--'):
                continue
            
            current_statement += ' ' + line
            
            # Check if statement is complete (ends with semicolon)
            if line.endswith(';'):
                statement = current_statement.strip()
                if statement:
                    try:
                        cursor.execute(statement)
                        connection.commit()  # Commit after each statement
                        loaded_count += 1
                    except pymysql.Error as e:
                        error_str = str(e)
                        if 'Duplicate entry' in error_str:
                            print(f"Data already exists in database. Rolling back.")
                            connection.rollback()
                            cursor.close()
                            connection.close()
                            return False
                        else:
                            print(f"Error executing statement: {error_str}")
                            print(f"Statement was: {statement[:100]}...")
                            # Continue to next statement instead of aborting
                            connection.rollback()
                
                current_statement = ""
        print(f"Successfully loaded sample data! ({loaded_count} SQL statements executed)")
        cursor.close()
        connection.close()
        return True
        
    except Exception as e:
        print(f"Error loading sample data: {e}")
        return False

def check_data_exists():
    """Check if sample data already exists in the database"""
    try:
        db_config = yaml.safe_load(open('db.yaml'))
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password=db_config['mysql_password'],
            database='Bank'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM Customers")
        count = cursor.fetchone()[0]
        cursor.close()
        connection.close()
        return count > 0
    except:
        return False

if __name__ == '__main__':
    if not check_data_exists():
        print("Loading sample data...")
        load_sample_data()
    else:
        print("Database already contains data. Skipping load.")
