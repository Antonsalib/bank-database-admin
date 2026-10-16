from app import create_app
from load_sample_data import load_sample_data, check_data_exists

app = create_app()

# Load sample data on startup if database is empty
if not check_data_exists():
    print("Database is empty. Loading sample data...")
    load_sample_data()
else:
    print("Database already contains data.")

if __name__ == '__main__':
    app.run(debug=True)