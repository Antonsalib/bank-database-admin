from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import db
from ..models import Account, Loan, LoanPayment, Transaction

bp = Blueprint('loanPayment', __name__)


@bp.route('/')
def loan_payments():
    payments = (
        LoanPayment.query
        .join(Loan)
        .join(Transaction)
        .order_by(LoanPayment.payment_date.desc(), LoanPayment.loan_payment_id.desc())
        .all()
    )
    return render_template('loan_payments.html', loan_payments=payments)


@bp.route('/add', methods=['GET', 'POST'])
def add_loan_payment():
    loans = Loan.query.filter_by(loan_status='Approved').order_by(Loan.loan_id).all()
    accounts = Account.query.filter(
        Account.account_status == 'Active',
        Account.account_type.in_(('Checking', 'Savings'))
    ).order_by(Account.account_id).all()

    if request.method == 'POST':
        loan = Loan.query.get_or_404(request.form.get('loan_id'))
        account = Account.query.get_or_404(request.form.get('account_id'))
        try:
            amount = Decimal(request.form.get('amount', ''))
            principal = Decimal(request.form.get('principal_amount', ''))
            interest = Decimal(request.form.get('interest_amount', ''))
            payment_date = date.fromisoformat(request.form.get('payment_date', ''))
        except (InvalidOperation, ValueError, TypeError):
            flash('Enter valid payment amounts and a payment date.', 'error')
            return render_template(
                'loan_payment_form.html', loans=loans, accounts=accounts
            )

        paid_principal = sum(
            (payment.principal_amount for payment in loan.payments), start=Decimal('0')
        )
        if loan.loan_status != 'Approved':
            flash('Payments can only be posted to approved loans.', 'error')
        elif account.account_status != 'Active' or account.account_type not in ('Checking', 'Savings'):
            flash('Choose an active checking or savings account for repayment.', 'error')
        elif not all(value.is_finite() for value in (amount, principal, interest)):
            flash('Payment amounts must be finite numbers.', 'error')
        elif amount <= 0 or principal <= 0 or interest < 0 or amount != principal + interest:
            flash('Payment amount must equal principal plus non-negative interest.', 'error')
        elif principal > loan.loan_amount - paid_principal:
            flash('Principal payment exceeds the loan principal still outstanding.', 'error')
        elif account.balance < amount:
            flash('The repayment account does not have sufficient funds.', 'error')
        else:
            transaction = Transaction(
                account=account,
                amount=amount,
                transaction_date=payment_date,
                transaction_type='Payment',
                payment_method='Bank Transfer'
            )
            db.session.add(transaction)
            db.session.flush()
            payment = LoanPayment(
                loan=loan,
                transaction=transaction,
                payment_date=payment_date,
                amount=amount,
                principal_amount=principal,
                interest_amount=interest
            )
            db.session.add(payment)
            if principal == loan.loan_amount - paid_principal:
                loan.loan_status = 'Closed'
            db.session.commit()
            return redirect(url_for('loanPayment.loan_payments'))

    return render_template('loan_payment_form.html', loans=loans, accounts=accounts)
