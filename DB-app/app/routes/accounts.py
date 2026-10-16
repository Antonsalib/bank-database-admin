from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Account, Customer

# Blueprint for accounts routes
an = Blueprint('account', __name__)

@an.route('/', methods=['GET'])
def Accounts():
    # Fetch accounts with customer details using a join
    accounts = db.session.query(
        Account.account_id.label('account_id'),
        Account.balance.label('balance'),
        Account.account_status.label('account_status'),
        Account.account_type.label('account_type'),
        Customer.first_name.label('first_name'),
        Customer.last_name.label('last_name'),
        Customer.customer_id.label('customer_id')
    ).join(Customer, Account.customer_id == Customer.customer_id).all()


    return render_template('accounts.html', accounts=accounts)


@an.route('/add', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        userDetails = request.form
        customer_id = userDetails['customer_id']
        balance = userDetails['balance']
        account_status = userDetails['account_status']
        account_type = userDetails['account_type']

         # Check if customer_id exists in the Customer table
        customer = Customer.query.get(customer_id)
        if not customer:
            # Flash an error message if the customer_id doesn't exist
            flash(f"Customer with ID {customer_id} does not exist. Please check and try again.", "error")
            return redirect(url_for('account.add_account'))
        
        # Creating new account object using SQLAlchemy
        new_account = Account( 
            customer_id=customer_id,
            balance=balance,
            account_status=account_status,
            account_type=account_type)
        db.session.add(new_account)
        db.session.commit()

        return redirect(url_for('account.Accounts'))
    return render_template('add_account.html')


@an.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    # Get account ID from the query parameters
    account_id = request.args.get('account_id')
    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':
        # On confirmation, delete the account
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('account.Accounts'))
        
    # Render confirmation page
    return render_template('delete_account.html', account=account)

@an.route('/update/<int:account_id>', methods=['GET', 'POST'])
def update_account(account_id):
    # Fetch the account from the database
    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':
        # Get updated details from the form
        userDetails = request.form
        account.customer_id = userDetails['customer_id']
        account.balance = userDetails['balance']
        account.account_status = userDetails['account_status']
        account.account_type = userDetails['account_type']
        
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('account.Accounts'))

    # Render a template to show the form with current loan details
    return render_template('update_account.html', account=account)