from datetime import date

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .. import db
from ..models import Account, PaymentCard

bp = Blueprint('paymentCard', __name__)


@bp.route('/')
def payment_cards():
    cards = PaymentCard.query.order_by(PaymentCard.payment_card_id.desc()).all()
    return render_template('payment_cards.html', payment_cards=cards)


@bp.route('/add', methods=['GET', 'POST'])
def add_payment_card():
    accounts = Account.query.order_by(Account.account_id).all()
    if request.method == 'POST':
        account = Account.query.get_or_404(request.form.get('account_id'))
        card_type = request.form.get('card_type')
        last_four = request.form.get('last_four', '').strip() or None
        expiry_text = request.form.get('expiry_date', '').strip()
        try:
            expiry_date = date.fromisoformat(expiry_text) if expiry_text else None
        except ValueError:
            flash('Enter a valid card expiration date.', 'error')
            return render_template('payment_card_form.html', accounts=accounts)

        if card_type not in ('Debit Card', 'Credit Card'):
            flash('Choose a valid payment card type.', 'error')
        elif last_four and (len(last_four) != 4 or not last_four.isdigit()):
            flash('Enter only the last four digits of the card, or leave them blank.', 'error')
        elif card_type == 'Credit Card' and account.account_type != 'Credit Card':
            flash('Credit cards must be linked to a credit-card account.', 'error')
        elif card_type == 'Debit Card' and account.account_type == 'Credit Card':
            flash('Debit cards cannot be linked to a credit-card account.', 'error')
        else:
            card = PaymentCard(
                account=account,
                card_type=card_type,
                last_four=last_four,
                expiry_date=expiry_date,
                card_status=request.form.get('card_status', 'Active')
            )
            db.session.add(card)
            db.session.commit()
            return redirect(url_for('paymentCard.payment_cards'))

    return render_template('payment_card_form.html', accounts=accounts)


@bp.route('/<int:payment_card_id>/status', methods=['POST'])
def update_status(payment_card_id):
    card = PaymentCard.query.get_or_404(payment_card_id)
    status = request.form.get('card_status')
    if status not in ('Active', 'Blocked', 'Expired'):
        flash('Choose a valid card status.', 'error')
    else:
        card.card_status = status
        db.session.commit()
    return redirect(url_for('paymentCard.payment_cards'))


@bp.route('/<int:payment_card_id>/delete', methods=['POST'])
def delete_payment_card(payment_card_id):
    card = PaymentCard.query.get_or_404(payment_card_id)
    db.session.delete(card)
    db.session.commit()
    flash('Card removed. Transaction history is retained without card details.', 'success')
    return redirect(url_for('paymentCard.payment_cards'))
