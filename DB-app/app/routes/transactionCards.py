from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import TransactionCard, Transaction

# Blueprint for Transaction Card routes
tc = Blueprint('transactionCard', __name__)

@tc.route('/', methods=['GET'])
def TransactionCards():
    # Fetch transactions using a join
    transaction_cards = db.session.query(
        TransactionCard.transaction_card_id.label('transaction_card_id'),
        TransactionCard.card_type.label('card_type'),
        Transaction.transaction_id.label('transaction_id'),
        Transaction.amount.label('amount'),
        Transaction.transaction_type.label('transaction_type')
    ).join(Transaction, TransactionCard.transaction_id == Transaction.transaction_id).all()

    return render_template('transaction_cards.html', transaction_cards=transaction_cards)

@tc.route('/add', methods=['GET', 'POST'])
def add_transaction_card():
    if request.method == 'POST':
        userDetails = request.form
        transaction_id = userDetails['transaction_id']
        card_type = userDetails['card_type']
        
        # Check if transaction_id exists in the Transaction table
        transaction = Transaction.query.get(transaction_id)
        if not transaction:
            # Flash an error message if the customer_id doesn't exist
            flash(f"Transaction with ID {transaction_id} does not exist. Please check and try again.", "error")
            return redirect(url_for('transactionCard.add_transaction_card'))
        
        # Creating new Transaction card object using SQLAlchemy
        new_transaction_card = TransactionCard( 
            transaction_id=transaction_id,
            card_type=card_type)
        db.session.add(new_transaction_card)
        db.session.commit()

        return redirect(url_for('transactionCard.TransactionCards'))
    return render_template('add_transaction_card.html')

@tc.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    # Get transaction card ID from the query parameters
    transaction_card_id = request.args.get('transaction_card_id')
    transactionCard = TransactionCard.query.get_or_404(transaction_card_id)

    if request.method == 'POST':
        # On confirmation, delete the transaction card
        db.session.delete(transactionCard)
        db.session.commit()
        return redirect(url_for('transactionCard.TransactionCards'))

    # Render confirmation page
    return render_template('delete_transaction_card.html', transactionCard=transactionCard)