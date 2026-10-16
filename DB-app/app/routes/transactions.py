from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import db
from ..models import Account, LoanPayment, PaymentCard, Transaction, Transfer

tp = Blueprint('transaction', __name__)
POSTED_TRANSACTION_TYPES = ('Withdrawal', 'Deposit', 'Payment', 'Purchase')


def _amount_from_form():
    try:
        amount = Decimal(request.form.get('amount', ''))
        transaction_date = date.fromisoformat(request.form.get('transaction_date', ''))
    except (InvalidOperation, ValueError, TypeError):
        return None, None
    if not amount.is_finite() or amount <= 0:
        return None, None
    return amount, transaction_date


@tp.route('/', methods=['GET'])
def transactions():
    rows = Transaction.query.order_by(
        Transaction.transaction_date.desc(), Transaction.transaction_id.desc()
    ).all()
    return render_template('transactions.html', transactions=rows)


@tp.route('/transfers')
def transfers():
    rows = Transfer.query.order_by(
        Transfer.initiated_date.desc(), Transfer.transfer_id.desc()
    ).all()
    return render_template('transfers.html', transfers=rows)


@tp.route('/add', methods=['GET', 'POST'])
def add_transaction():
    accounts = Account.query.order_by(Account.account_id).all()
    cards = PaymentCard.query.filter_by(card_status='Active').order_by(
        PaymentCard.payment_card_id
    ).all()

    if request.method == 'POST':
        account = Account.query.get_or_404(request.form.get('account_id'))
        transaction_type = request.form.get('transaction_type')
        amount, transaction_date = _amount_from_form()
        card_id = request.form.get('payment_card_id', '').strip()
        card = PaymentCard.query.get(card_id) if card_id else None
        payment_method = request.form.get('payment_method') or None

        if transaction_type not in POSTED_TRANSACTION_TYPES:
            flash('Choose a valid transaction type. Transfers use the transfer form.', 'error')
        elif amount is None:
            flash('Enter a valid positive amount and transaction date.', 'error')
        elif account.account_status != 'Active':
            flash('Transactions cannot be posted to an inactive account.', 'error')
        elif card_id and (card is None or card.account_id != account.account_id or card.card_status != 'Active'):
            flash('Choose an active payment card linked to the selected account.', 'error')
        elif card and account.account_type == 'Credit Card' and card.card_type != 'Credit Card':
            flash('The payment card type does not match the account.', 'error')
        elif card and account.account_type != 'Credit Card' and card.card_type != 'Debit Card':
            flash('The payment card type does not match the account.', 'error')
        elif payment_method not in (None, 'Check', 'Cash', 'Bank Transfer') and card is None:
            flash('Select an account card or choose another payment method.', 'error')
        elif (
            account.account_type != 'Credit Card'
            and transaction_type in ('Withdrawal', 'Payment', 'Purchase')
            and account.balance < amount
        ):
            flash('Insufficient funds for this transaction.', 'error')
        else:
            transaction = Transaction(
                account=account,
                payment_card=card,
                amount=amount,
                transaction_date=transaction_date,
                transaction_type=transaction_type,
                payment_method=card.card_type if card else payment_method
            )
            db.session.add(transaction)
            db.session.commit()
            return redirect(url_for('transaction.transactions'))

    return render_template('add_transaction.html', accounts=accounts, cards=cards)


@tp.route('/transfer', methods=['GET', 'POST'])
def add_transfer():
    accounts = Account.query.filter(
        Account.account_status == 'Active',
        Account.account_type.in_(('Checking', 'Savings'))
    ).order_by(Account.account_id).all()

    if request.method == 'POST':
        from_account = Account.query.get_or_404(request.form.get('from_account_id'))
        to_account = Account.query.get_or_404(request.form.get('to_account_id'))
        amount, transfer_date = _amount_from_form()

        if from_account.account_id == to_account.account_id:
            flash('Choose two different accounts for a transfer.', 'error')
        elif amount is None:
            flash('Enter a valid positive amount and transfer date.', 'error')
        elif any(
            account.account_status != 'Active'
            or account.account_type == 'Credit Card'
            for account in (from_account, to_account)
        ):
            flash('Transfers require active checking or savings accounts.', 'error')
        elif from_account.balance < amount:
            flash('The sending account has insufficient funds.', 'error')
        else:
            transfer = Transfer(
                from_account_id=from_account.account_id,
                to_account_id=to_account.account_id,
                amount=amount,
                initiated_date=transfer_date
            )
            db.session.add(transfer)
            db.session.flush()
            db.session.add_all([
                Transaction(
                    account_id=from_account.account_id,
                    related_account_id=to_account.account_id,
                    transfer_id=transfer.transfer_id,
                    amount=amount,
                    transaction_date=transfer_date,
                    transaction_type='Transfer Out',
                    payment_method='Bank Transfer'
                ),
                Transaction(
                    account_id=to_account.account_id,
                    related_account_id=from_account.account_id,
                    transfer_id=transfer.transfer_id,
                    amount=amount,
                    transaction_date=transfer_date,
                    transaction_type='Transfer In',
                    payment_method='Bank Transfer'
                )
            ])
            db.session.commit()
            return redirect(url_for('transaction.transactions'))

    return render_template('add_transfer.html', accounts=accounts)


@tp.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    transaction = Transaction.query.get_or_404(request.args.get('transaction_id'))
    if transaction.transfer_id or LoanPayment.query.filter_by(
        transaction_id=transaction.transaction_id
    ).first():
        flash('Transfer and loan-payment ledger entries cannot be deleted directly.', 'error')
        return redirect(url_for('transaction.transactions'))
    flash('Posted transactions are immutable ledger entries and cannot be deleted.', 'error')
    return redirect(url_for('transaction.transactions'))
