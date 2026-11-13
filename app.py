import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cop4751-job-tracker-secret-key')


@app.route('/')
def dashboard():
    data = db.get_dashboard_data()
    return render_template(
        'dashboard.html',
        stats=data['stats'],
        status_counts=data['status_counts'],
        recent_applications=data['recent_applications']
    )


@app.route('/companies', methods=['GET', 'POST'])
def companies():
    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        if not company_name:
            flash('Company name is required.', 'error')
            return redirect(url_for('companies'))

        db.add_company(
            company_name=company_name,
            industry=request.form.get('industry', '').strip() or None,
            website=request.form.get('website', '').strip() or None,
            city=request.form.get('city', '').strip() or None,
            state=request.form.get('state', '').strip() or None,
            notes=request.form.get('notes', '').strip() or None
        )
        flash('Company added.', 'success')
        return redirect(url_for('companies'))

    all_companies = db.get_all_companies()
    return render_template('companies.html', companies=all_companies)


@app.route('/companies/update/<int:company_id>', methods=['POST'])
def update_company(company_id):
    company_name = request.form.get('company_name', '').strip()
    if not company_name:
        flash('Company name is required.', 'error')
        return redirect(url_for('companies'))

    db.update_company(
        company_id=company_id,
        company_name=company_name,
        industry=request.form.get('industry', '').strip() or None,
        website=request.form.get('website', '').strip() or None,
        city=request.form.get('city', '').strip() or None,
        state=request.form.get('state', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None
    )
    flash('Company updated.', 'success')
    return redirect(url_for('companies'))


@app.route('/companies/delete/<int:company_id>', methods=['POST'])
def delete_company(company_id):
    try:
        db.delete_company(company_id)
        flash('Company deleted.', 'success')
    except mysql.connector.Error:
        flash('Cannot delete company while jobs or contacts are linked to it.', 'error')
    return redirect(url_for('companies'))


if __name__ == '__main__':
    app.run(debug=True)