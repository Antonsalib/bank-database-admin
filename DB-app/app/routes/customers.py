from flask import Blueprint, render_template, request, redirect, url_for, flash
from .. import db
from ..models import Customer, Loan, Account

# Blueprint for customer route
bp = Blueprint('customer', __name__)

@bp.route('/', methods=['GET', 'POST'])
def Customers():
    # Get the search query from the form or query parameters
    search_query = request.args.get('search', '').strip()

    if search_query:
        # Filter customers by the search query (e.g., first name, last name, or email)
        customers = Customer.query.filter(
            (Customer.first_name.ilike(f'%{search_query}%')) |
            (Customer.last_name.ilike(f'%{search_query}%')) |
            (Customer.email.ilike(f'%{search_query}%'))
        ).all()
    else:
        # Fetch all customers if no search query is provided
        customers = Customer.query.all()

    return render_template('customers.html', customers=customers, search_query=search_query)


@bp.route('/add', methods=['GET', 'POST'])
def add_customer():
    if request.method == 'POST':
        userDetails = request.form
        first_name = userDetails['first_name']
        last_name = userDetails['last_name']
        email = userDetails['email']
        phone_number = userDetails['phone_number']
        address = userDetails['address']
        
        # Creating new user object using SQLAlchemy
        new_customer = Customer(
            first_name=first_name, 
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            address=address)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('customer.Customers'))
    return render_template('add_customer.html')

@bp.route('/delete/confirm', methods=['GET', 'POST'])
def delete_confirmation():
    # Get customer ID from the query parameters
    customer_id = request.args.get('customer_id')
    customer = Customer.query.get_or_404(customer_id)

    # Check for associated loans
    associated_loans = Loan.query.filter_by(customer_id=customer_id).all()
    if associated_loans:
        # Separate closed loans
        closed_loans = [loan for loan in associated_loans if loan.loan_status == 'Closed']
        open_loans = [loan for loan in associated_loans if loan.loan_status != 'Closed']

        # Delete closed loans 
        for loan in closed_loans:
            db.session.delete(loan)
        
        # If there are open loans, prevent customer deletion
        if open_loans:
            flash(
                f"Cannot delete customer ID {customer_id} because they have open loan(s).",
                "error"
            )
            return redirect(url_for('customer.Customers'))
        
    associated_accounts = Account.query.filter_by(customer_id=customer_id).all()
    if associated_accounts:
        flash(
                f"Cannot delete customer ID {customer_id} because they have open account(s).",
                "error"
            )
        return redirect(url_for('customer.Customers'))

    if request.method == 'POST':
        # On confirmation, delete the customer
        db.session.delete(customer)
        db.session.commit()
        return redirect(url_for('customer.Customers'))
        
    # Render confirmation page
    return render_template('delete_customer.html', customer=customer)

@bp.route('/update/<int:customer_id>', methods=['GET', 'POST'])
def update_customer(customer_id):
    # Fetch the customer from the database
    customer = Customer.query.get_or_404(customer_id)

    if request.method == 'POST':
        # Get updated details from the form
        userDetails = request.form
        customer.first_name = userDetails['first_name']
        customer.last_name = userDetails['last_name']
        customer.email = userDetails['email']
        customer.phone_number = userDetails['phone_number']
        customer.address = userDetails['address']
        
        # Commit the changes to the database
        db.session.commit()
        return redirect(url_for('customer.Customers'))

    # Render a template to show the form with current customer details
    return render_template('update_customer.html', customer=customer)

