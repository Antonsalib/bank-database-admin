from . import db
from flask_marshmallow import Marshmallow

# Initialize Marshmallow
ma = Marshmallow()

# Define the Customer model
class Customer(db.Model):
    __tablename__ = 'Customers' 
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60), nullable=False, unique=True)
    phone_number = db.Column(db.String(13), nullable=False)
    address = db.Column(db.String(50), nullable=False)

    def __init__(self, first_name, last_name, email, phone_number, address):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone_number = phone_number
        self.address = address

# Define the Marshmallow schema for Customer
class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


# Define the Customer model
class Loan(db.Model):
    __tablename__ = 'Loan'
    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False)
    loan_amount = db.Column(db.Integer, nullable=False)
    interest_rate = db.Column(db.Integer, nullable=False)
    loan_status = db.Column(db.Enum('Approved', 'Pending', 'Closed'), nullable=False)

    # Relationship with Customer
    customer = db.relationship('Customer', backref='loans')
    
    def __init__(self, customer_id, loan_amount, interest_rate, loan_status):
        self.customer_id = customer_id
        self.loan_amount = loan_amount
        self.interest_rate = interest_rate
        self.loan_status = loan_status

# Define the Marshmallow schema for Loan
class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loan


# Define the Account model
class Account(db.Model):
    __tablename__ = 'Accounts'
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    account_status = db.Column(db.Enum('Active', 'Inactive',), nullable=False)
    account_type = db.Column(db.Enum('Checking', 'Savings', 'Credit Card'), nullable=False)

    # Relationship with Customer
    customer = db.relationship('Customer', backref='accounts')
    
    def __init__(self, customer_id, balance, account_status, account_type):
        self.customer_id = customer_id
        self.balance = balance
        self.account_status = account_status
        self.account_type = account_type

# Define the Marshmallow schema for Loan
class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account

# Define the Transaction model
class Transaction(db.Model):
    __tablename__ = 'Transactions'
    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey('Accounts.account_id'), nullable=False)
    related_account_id = db.Column(db.Integer, db.ForeignKey('Accounts.account_id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.Enum('Withdrawal', 'Deposit', 'Payment', 'Transfer', 'Purchase'), nullable=False)

    # Relationship with Account
    #account = db.relationship('Account', backref='transactions')

    def __init__(self, account_id, amount, transaction_date, transaction_type, related_account_id=None):
        self.account_id = account_id
        self.amount = amount
        self.transaction_date = transaction_date
        self.transaction_type = transaction_type
        self.related_account_id = related_account_id

    
# Define the Marshmallow schema for Transaction
class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction

# Define the Transaction Card model
class TransactionCard(db.Model):
    __tablename__ = 'TransactionCard'
    transaction_card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('Transactions.transaction_id'), nullable=False)
    card_type = db.Column(db.Enum('Debit Card', 'Check', 'Credit Card'), nullable=False)
    
    def __init__(self, transaction_id, card_type):
        self.card_type = card_type
        self.transaction_id = transaction_id

# Define the Marshmallow schema for Loan
class TransactionCardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TransactionCard

# Initialize the schema
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
transaction_schema =  TransactionSchema()
transactions_schema = TransactionSchema(many=True)
loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)
transaction_card_schema = TransactionCardSchema()
transaction_cards_schema = TransactionCardSchema(many=True)