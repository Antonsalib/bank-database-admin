from . import db
from flask_marshmallow import Marshmallow

ma = Marshmallow()


class Branch(db.Model):
    __tablename__ = 'Branches'

    branch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_name = db.Column(db.String(80), nullable=False, unique=True)
    address = db.Column(db.String(160), nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)

    accounts = db.relationship('Account', back_populates='branch')


class Customer(db.Model):
    __tablename__ = 'Customers'

    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    phone_number = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(160), nullable=False)

    account_ownerships = db.relationship(
        'AccountOwner', back_populates='customer', cascade='all, delete-orphan'
    )
    loans = db.relationship('Loan', back_populates='customer')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'


class AccountOwner(db.Model):
    __tablename__ = 'AccountOwners'

    account_id = db.Column(
        db.Integer, db.ForeignKey('Accounts.account_id', ondelete='CASCADE'),
        primary_key=True
    )
    customer_id = db.Column(
        db.Integer, db.ForeignKey('Customers.customer_id', ondelete='RESTRICT'),
        primary_key=True
    )
    owner_role = db.Column(db.Enum('Primary', 'Joint'), nullable=False)

    account = db.relationship('Account', back_populates='ownerships')
    customer = db.relationship('Customer', back_populates='account_ownerships')


class Account(db.Model):
    __tablename__ = 'Accounts'

    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    branch_id = db.Column(
        db.Integer, db.ForeignKey('Branches.branch_id', ondelete='RESTRICT'),
        nullable=False
    )
    balance = db.Column(db.Numeric(15, 2), nullable=False)
    account_status = db.Column(db.Enum('Active', 'Inactive'), nullable=False)
    account_type = db.Column(
        db.Enum('Checking', 'Savings', 'Credit Card'), nullable=False
    )

    branch = db.relationship('Branch', back_populates='accounts')
    ownerships = db.relationship(
        'AccountOwner', back_populates='account', cascade='all, delete-orphan'
    )
    payment_cards = db.relationship(
        'PaymentCard', back_populates='account', cascade='all, delete-orphan'
    )
    transactions = db.relationship(
        'Transaction', foreign_keys='Transaction.account_id', back_populates='account'
    )
    transfers_sent = db.relationship(
        'Transfer', foreign_keys='Transfer.from_account_id', back_populates='from_account'
    )
    transfers_received = db.relationship(
        'Transfer', foreign_keys='Transfer.to_account_id', back_populates='to_account'
    )

    @property
    def owners(self):
        return [ownership.customer for ownership in self.ownerships]


class Loan(db.Model):
    __tablename__ = 'Loan'

    loan_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey('Customers.customer_id', ondelete='RESTRICT'),
        nullable=False
    )
    loan_amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 2), nullable=False)
    loan_status = db.Column(
        db.Enum('Approved', 'Pending', 'Closed'), nullable=False
    )

    customer = db.relationship('Customer', back_populates='loans')
    payments = db.relationship('LoanPayment', back_populates='loan')

    @property
    def principal_paid(self):
        return sum((payment.principal_amount for payment in self.payments), start=0)

    @property
    def principal_remaining(self):
        return max(self.loan_amount - self.principal_paid, 0)


class Transfer(db.Model):
    __tablename__ = 'Transfers'

    transfer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    from_account_id = db.Column(
        db.Integer, db.ForeignKey('Accounts.account_id', ondelete='RESTRICT'),
        nullable=False
    )
    to_account_id = db.Column(
        db.Integer, db.ForeignKey('Accounts.account_id', ondelete='RESTRICT'),
        nullable=False
    )
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    initiated_date = db.Column(db.Date, nullable=False)

    from_account = db.relationship(
        'Account', foreign_keys=[from_account_id], back_populates='transfers_sent'
    )
    to_account = db.relationship(
        'Account', foreign_keys=[to_account_id], back_populates='transfers_received'
    )
    entries = db.relationship(
        'Transaction', back_populates='transfer', cascade='all, delete-orphan'
    )


class PaymentCard(db.Model):
    __tablename__ = 'PaymentCards'

    payment_card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(
        db.Integer, db.ForeignKey('Accounts.account_id', ondelete='CASCADE'),
        nullable=False
    )
    card_type = db.Column(db.Enum('Debit Card', 'Credit Card'), nullable=False)
    last_four = db.Column(db.String(4), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    card_status = db.Column(
        db.Enum('Active', 'Blocked', 'Expired'), nullable=False, default='Active'
    )

    account = db.relationship('Account', back_populates='payment_cards')
    transactions = db.relationship('Transaction', back_populates='payment_card')


class Transaction(db.Model):
    __tablename__ = 'Transactions'

    transaction_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(
        db.Integer, db.ForeignKey('Accounts.account_id', ondelete='RESTRICT'),
        nullable=False
    )
    related_account_id = db.Column(
        db.Integer, db.ForeignKey('Accounts.account_id', ondelete='SET NULL'),
        nullable=True
    )
    transfer_id = db.Column(
        db.Integer, db.ForeignKey('Transfers.transfer_id', ondelete='CASCADE'),
        nullable=True
    )
    payment_card_id = db.Column(
        db.Integer, db.ForeignKey('PaymentCards.payment_card_id', ondelete='SET NULL'),
        nullable=True
    )
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(
        db.Enum(
            'Withdrawal', 'Deposit', 'Payment', 'Purchase',
            'Transfer Out', 'Transfer In'
        ),
        nullable=False
    )
    payment_method = db.Column(
        db.Enum('Debit Card', 'Credit Card', 'Check', 'Cash', 'Bank Transfer'),
        nullable=True
    )

    account = db.relationship(
        'Account', foreign_keys=[account_id], back_populates='transactions'
    )
    transfer = db.relationship('Transfer', back_populates='entries')
    payment_card = db.relationship('PaymentCard', back_populates='transactions')
    loan_payment = db.relationship('LoanPayment', back_populates='transaction', uselist=False)


class LoanPayment(db.Model):
    __tablename__ = 'LoanPayments'

    loan_payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    loan_id = db.Column(
        db.Integer, db.ForeignKey('Loan.loan_id', ondelete='RESTRICT'),
        nullable=False
    )
    transaction_id = db.Column(
        db.Integer,
        db.ForeignKey('Transactions.transaction_id', ondelete='RESTRICT'),
        nullable=False,
        unique=True
    )
    payment_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    principal_amount = db.Column(db.Numeric(15, 2), nullable=False)
    interest_amount = db.Column(db.Numeric(15, 2), nullable=False)

    loan = db.relationship('Loan', back_populates='payments')
    transaction = db.relationship('Transaction', back_populates='loan_payment')


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer


class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loan


class AccountSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Account


class TransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction


class PaymentCardSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = PaymentCard


class BranchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Branch


class LoanPaymentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LoanPayment


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
transaction_schema = TransactionSchema()
transactions_schema = TransactionSchema(many=True)
loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)
account_schema = AccountSchema()
accounts_schema = AccountSchema(many=True)
payment_card_schema = PaymentCardSchema()
payment_cards_schema = PaymentCardSchema(many=True)
