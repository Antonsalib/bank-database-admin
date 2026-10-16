from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Transaction, Account
from decimal import Decimal

# Blueprint for transaction route
tp = Blueprint('transaction', __name__)

@tp.route('/', methods=['GET'])
def transactions():
    # Fetch transactions with account and customer details
    transactions = db.session.query(
        Transaction.transaction_id.label('transaction_id'),
        Transaction.related_account_id.label('related_account_id'),
        Transaction.amount.label('amount'),
        Transaction.transaction_date.label('transaction_date'),
        Transaction.transaction_type.label('transaction_type'),
        Account.account_type.label('account_type'),
        Account.account_id.label('account_id')
    
    ).join(Account, Transaction.account_id == Account.account_id).all()
   
    return render_template('transactions.html', transactions=transactions)

@tp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        userDetails = request.form
        account_id = userDetails['account_id']
        related_account_id = userDetails.get('related_account_id')  # May be null
        amount = userDetails['amount']
        transaction_date = userDetails['transaction_date']
        transaction_type = userDetails['transaction_type']

        # Check if account_id exists in the Account table
        account = Account.query.get(account_id)
        if not account:
            # Flash an error message if the customer_id doesn't exist
            flash(f"Account with ID {account_id} does not exist. Please check and try again.", "error")
            return redirect(url_for('transaction.add_transaction'))
        
        # Validate `related_account_id` only if provided
        if related_account_id:
            related_account = Account.query.get(related_account_id)
            if not related_account:
                flash(f"Related account with ID {related_account_id} does not exist. Please check and try again.", "error")
                return redirect(url_for('transaction.add_transaction'))

        # Convert empty string to None
        if not related_account_id:
            related_account_id = None

        # Ensure `amount` is converted to Decimal
        try:
            amount = Decimal(amount)  # Converts string input to Decimal
        except (ValueError, TypeError):
            flash('Invalid amount. Please enter a valid number.')
            return redirect(url_for('transaction.add_transaction'))

        # Check account status
        if account.account_status == 'Inactive':
            flash('Transaction not allowed on an inactive account.')
            return redirect(url_for('transaction.add_transaction'))

        # Ensure sufficient funds for specific transactions
        if transaction_type in ('Withdrawal', 'Payment', 'Transfer', 'Purchase'):
            # Check if the transaction exceeds the credit card limit
            if account.account_type == 'Credit Card':
                if account.balance + amount > 10000:    # Credit card balance cannot exceed $10,000
                    flash('Transaction denied. Credit card balance cannot exceed $10,000.')
                    return redirect(url_for('transaction.add_transaction'))
                
            else:
                # Check if there are sufficient funds in non-credit accounts
                if account.balance < amount:
                    flash('Insufficient funds for transaction.')
                    return redirect(url_for('transaction.add_transaction'))

        # Add transaction
        new_transaction = Transaction(
            account_id=account_id,
            related_account_id=related_account_id,
            amount=amount,
            transaction_date=transaction_date,
            transaction_type=transaction_type
        )
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('transaction.transactions'))

    return render_template('add_transaction.html')

@tp.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    # Get account ID from the query parameters
    transaction_id = request.args.get('transaction_id')
    transaction = Transaction.query.get_or_404(transaction_id)

    if request.method == 'POST':
        # On confirmation, delete the account
        db.session.delete(transaction)
        db.session.commit()
        return redirect(url_for('transaction.transactions'))
        
    # Render confirmation page
    return render_template('delete_transaction.html', transaction=transaction)