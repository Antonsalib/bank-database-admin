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

def create_app(config=None):
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
    if config:
        app.config.update(config)

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

    from .routes.branches import bp as branches_bp
    app.register_blueprint(branches_bp, url_prefix='/branches')

    from .routes.paymentCards import bp as payment_cards_bp
    app.register_blueprint(payment_cards_bp, url_prefix='/payment-cards')

    from .routes.loanPayments import bp as loan_payments_bp
    app.register_blueprint(loan_payments_bp, url_prefix='/loan-payments')

    @app.route('/')
    def index():
        from .models import (
            Account, Branch, Customer, Loan, LoanPayment, PaymentCard,
            AccountOwner, Transaction, Transfer,
        )

        stats = {
            'customers': Customer.query.count(),
            'accounts': Account.query.count(),
            'loans': Loan.query.count(),
            'transactions': Transaction.query.count(),
            'branches': Branch.query.count(),
            'payment_cards': PaymentCard.query.count(),
            'loan_payments': LoanPayment.query.count(),
            'transfers': Transfer.query.count(),
            'account_owners': AccountOwner.query.count(),
        }
        recent_transactions = (
            Transaction.query
            .order_by(Transaction.transaction_date.desc(), Transaction.transaction_id.desc())
            .limit(5)
            .all()
        )
        return render_template(
            'index.html',
            stats=stats,
            recent_transactions=recent_transactions
        )

    # Add global context processor for customers
    @app.context_processor
    def inject_customers():
        from .models import Customer
        return dict(customers=Customer.query.all())

    return app
