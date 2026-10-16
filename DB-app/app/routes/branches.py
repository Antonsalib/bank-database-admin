from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .. import db
from ..models import Branch

bp = Blueprint('branch', __name__)


@bp.route('/')
def branches():
    rows = Branch.query.order_by(Branch.branch_name).all()
    return render_template('branches.html', branches=rows)


@bp.route('/add', methods=['GET', 'POST'])
@bp.route('/<int:branch_id>/edit', methods=['GET', 'POST'])
def edit_branch(branch_id=None):
    branch = db.session.get(Branch, branch_id) if branch_id else Branch()
    if branch_id and branch is None:
        abort(404)

    if request.method == 'POST':
        name = request.form.get('branch_name', '').strip()
        address = request.form.get('address', '').strip()
        phone = request.form.get('phone_number', '').strip() or None
        duplicate_name = Branch.query.filter(
            Branch.branch_name == name,
            Branch.branch_id != branch.branch_id
        ).first() if branch_id else Branch.query.filter_by(branch_name=name).first()
        if not name or not address:
            flash('Branch name and address are required.', 'error')
        elif duplicate_name:
            flash('A branch with this name already exists.', 'error')
        else:
            branch.branch_name = name
            branch.address = address
            branch.phone_number = phone
            db.session.add(branch)
            db.session.commit()
            return redirect(url_for('branch.branches'))

    return render_template('branch_form.html', branch=branch, is_edit=branch_id is not None)


@bp.route('/<int:branch_id>/delete', methods=['POST'])
def delete_branch(branch_id):
    branch = Branch.query.get_or_404(branch_id)
    if branch.accounts:
        flash('Move the branch accounts before deleting this branch.', 'error')
    else:
        db.session.delete(branch)
        db.session.commit()
        flash('Branch deleted.', 'success')
    return redirect(url_for('branch.branches'))
