from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Loan, Customer

# Blueprint for loan routes
ln = Blueprint('loan', __name__)

@ln.route('/', methods=['GET'])
def Loans():
    # Fetch loans with customer details using a join
    loans = db.session.query(
        Loan.loan_id.label('loan_id'),
        Loan.loan_amount.label('loan_amount'),
        Loan.interest_rate.label('interest_rate'),
        Loan.loan_status.label('loan_status'),
        Customer.first_name.label('first_name'),
        Customer.last_name.label('last_name'),
        Customer.customer_id.label('customer_id')
    ).join(Customer, Loan.customer_id == Customer.customer_id).all()

    return render_template('loans.html', loans=loans)
    

@ln.route('/add', methods=['GET', 'POST'])
def add_loan():
    if request.method == 'POST':
        userDetails = request.form
        customer_id = userDetails['customer_id']
        loan_amount = userDetails['loan_amount']
        interest_rate = userDetails['interest_rate']
        loan_status = userDetails['loan_status']

        # Check if customer_id exists in the Customer table
        customer = Customer.query.get(customer_id)
        if not customer:
            # Flash an error message if the customer_id doesn't exist
            flash(f"Customer with ID {customer_id} does not exist. Please check and try again.", "error")
            return redirect(url_for('loan.add_loan'))
        
        # Creating new loan object using SQLAlchemy
        new_loan = Loan( 
            customer_id=customer_id,
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            loan_status=loan_status)
        db.session.add(new_loan)
        db.session.commit()

        return redirect(url_for('loan.Loans'))
    return render_template('add_loan.html')

@ln.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    # Get account ID from the query parameters
    loan_id = request.args.get('loan_id')
    loan = Loan.query.get_or_404(loan_id)

    if request.method == 'POST':
        # On confirmation, delete the account
        db.session.delete(loan)
        db.session.commit()
        return redirect(url_for('loan.Loans'))
        
    # Render confirmation page
    return render_template('delete_loan.html', loan=loan)

@ln.route('/update/<int:loan_id>', methods=['GET', 'POST'])
def update_loan(loan_id):
    # Fetch the loan from the database
    loan = Loan.query.get_or_404(loan_id)

    if request.method == 'POST':
        # Get updated details from the form
        userDetails = request.form
        loan.customer_id = userDetails['customer_id']
        loan.loan_amount= userDetails['loan_amount']
        loan.interest_rate = userDetails['interest_rate']
        loan.loan_status = userDetails['loan_status']
        
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('loan.Loans'))

    # Render a template to show the form with current loan details
    return render_template('update_loan.html', loan=loan)

