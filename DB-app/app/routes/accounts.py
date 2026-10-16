from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import db
from ..models import Account, AccountOwner, Branch, Customer

an = Blueprint('account', __name__)


def _account_form_context(account=None):
    return {
        'account': account,
        'customers': Customer.query.order_by(Customer.last_name, Customer.first_name).all(),
        'branches': Branch.query.order_by(Branch.branch_name).all(),
        'selected_customer_ids': (
            {owner.customer_id for owner in account.ownerships} if account else set()
        ),
    }


def _apply_account_form(account, set_opening_balance=False):
    customer_ids = request.form.getlist('customer_ids')
    if not customer_ids:
        flash('Choose at least one account owner.', 'error')
        return False

    try:
        parsed_customer_ids = list(dict.fromkeys(int(value) for value in customer_ids))
        branch_id = int(request.form['branch_id'])
        balance = (
            Decimal(request.form['balance'])
            if set_opening_balance else account.balance
        )
    except (KeyError, ValueError, InvalidOperation):
        flash('Enter valid account details, including a branch and opening balance.', 'error')
        return False

    if balance < 0 or not balance.is_finite():
        flash('The opening balance must be a non-negative amount.', 'error')
        return False

    customers = Customer.query.filter(Customer.customer_id.in_(parsed_customer_ids)).all()
    branch = db.session.get(Branch, branch_id)
    if len(customers) != len(parsed_customer_ids) or branch is None:
        flash('Choose existing customers and a valid branch.', 'error')
        return False
    customer_by_id = {customer.customer_id: customer for customer in customers}

    account.branch_id = branch.branch_id
    account.balance = balance
    account.account_status = request.form.get('account_status')
    account.account_type = request.form.get('account_type')
    if account.account_status not in ('Active', 'Inactive'):
        flash('Choose a valid account status.', 'error')
        return False
    if account.account_type not in ('Checking', 'Savings', 'Credit Card'):
        flash('Choose a valid account type.', 'error')
        return False
    account.ownerships[:] = [
        AccountOwner(
            customer=customer_by_id[customer_id],
            owner_role='Primary' if index == 0 else 'Joint'
        )
        for index, customer_id in enumerate(parsed_customer_ids)
    ]
    return True


@an.route('/', methods=['GET'])
def Accounts():
    accounts = Account.query.order_by(Account.account_id.desc()).all()
    return render_template('accounts.html', accounts=accounts)


@an.route('/add', methods=['GET', 'POST'])
def add_account():
    if request.method == 'POST':
        account = Account(
            branch_id=0,
            balance=0,
            account_status='Active',
            account_type='Checking'
        )
        if not _apply_account_form(account, set_opening_balance=True):
            return render_template('add_account.html', **_account_form_context())
        db.session.add(account)
        db.session.commit()
        return redirect(url_for('account.Accounts'))

    return render_template('add_account.html', **_account_form_context())


@an.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    account = Account.query.get_or_404(request.args.get('account_id'))
    if account.transactions:
        flash('Accounts with transaction history cannot be deleted.', 'error')
        return redirect(url_for('account.Accounts'))

    if request.method == 'POST':
        db.session.delete(account)
        db.session.commit()
        return redirect(url_for('account.Accounts'))

    return render_template('delete_account.html', account=account)


@an.route('/update/<int:account_id>', methods=['GET', 'POST'])
def update_account(account_id):
    account = Account.query.get_or_404(account_id)

    if request.method == 'POST':
        if not _apply_account_form(account):
            return render_template(
                'update_account.html',
                **_account_form_context(account)
            )
        db.session.commit()
        return redirect(url_for('account.Accounts'))

    return render_template('update_account.html', **_account_form_context(account))
