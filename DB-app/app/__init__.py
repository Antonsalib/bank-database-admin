from flask import Flask, render_template
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import urllib.parse
import yaml
import os

# Initialize SQLAlchemy and Marshmallow
db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)

    # Secret key for flash message
    app.secret_key = os.urandom(26)

    # Load database configuration from YAML
    db_config = yaml.safe_load(open('db.yaml'))
    raw_password = db_config['mysql_password']

    # URL encode the password to handle special characters like '@'
    encoded_password = urllib.parse.quote_plus(raw_password)

    # Construct the SQLAlchemy URI using the encoded password
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://root:{encoded_password}@localhost/Bank"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy and Marshmallow with the app
    db.init_app(app)
    ma.init_app(app)

    # Register blueprints for Transaction
    from .routes.transactions import tp 
    app.register_blueprint(tp, url_prefix='/transactions')

    # Register blueprints for Customer
    from .routes.customers import bp 
    app.register_blueprint(bp, url_prefix='/customers')

    # Register blueprints for Loan
    from .routes.loans import ln 
    app.register_blueprint(ln, url_prefix='/loans')

    # Register blueprints for Account
    from .routes.accounts import an 
    app.register_blueprint(an, url_prefix='/accounts')

    # Register blueprints for Transaction Card
    from .routes.transactionCards import tc 
    app.register_blueprint(tc, url_prefix='/transactionCards')

    @app.route('/')
    def index():
        from .models import Account, Customer, Loan, Transaction, TransactionCard

        stats = {
            'customers': Customer.query.count(),
            'accounts': Account.query.count(),
            'loans': Loan.query.count(),
            'transactions': Transaction.query.count(),
            'transaction_cards': TransactionCard.query.count(),
        }
        recent_transactions = (
            Transaction.query
            .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
            .limit(5)
            .all()
        )
        return render_template('index.html', stats=stats, recent_transactions=recent_transactions)

    # Add global context processor for customers
    @app.context_processor
    def inject_customers():
        from .models import Customer  # Ensure Customer model is imported here
        try:
            customers = Customer.query.all()
        except Exception as e:
            customers = []  # Handle database connection errors gracefully
        return dict(customers=customers)

    return app
