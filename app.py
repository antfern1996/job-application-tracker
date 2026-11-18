import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import database as db

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cop4751-job-tracker-secret-key')


def _parse_float(raw_value):
    val = raw_value.strip()
    if not val:
        return None
    try:
        return float(val)
    except ValueError:
        return None


def _parse_job_form(form):
    required_skills = [s.strip() for s in form.get('required_skills', '').split(',') if s.strip()]
    preferred_skills = [s.strip() for s in form.get('preferred_skills', '').split(',') if s.strip()]
    education = form.get('education', '').strip()
    exp_raw = form.get('experience_years', '').strip()
    remote_option = form.get('remote_option') == 'on'

    requirements = {}
    if required_skills:
        requirements['required_skills'] = required_skills
    if preferred_skills:
        requirements['preferred_skills'] = preferred_skills
    if education:
        requirements['education'] = education
    if exp_raw.isdigit():
        requirements['experience_years'] = int(exp_raw)
    if remote_option or requirements:
        requirements['remote_option'] = remote_option

    return {
        'company_id': form.get('company_id', type=int),
        'job_title': form.get('job_title', '').strip(),
        'job_type': form.get('job_type', '').strip() or None,
        'salary_min': _parse_float(form.get('salary_min', '')),
        'salary_max': _parse_float(form.get('salary_max', '')),
        'posting_url': form.get('posting_url', '').strip() or None,
        'date_posted': form.get('date_posted', '').strip() or None,
        'is_active': 1 if form.get('is_active') == 'on' else 0,
        'job_description': form.get('job_description', '').strip() or None,
        'requirements': requirements or None
    }


def _parse_application_form(form):
    rounds_raw = form.get('interview_rounds', '').strip()
    interviewers = [s.strip() for s in form.get('interviewers', '').split(',') if s.strip()]
    questions = [s.strip() for s in form.get('technical_questions', '').split(',') if s.strip()]
    feedback = form.get('feedback', '').strip()
    next_steps = form.get('next_steps', '').strip()
    offer_amount = _parse_float(form.get('offer_amount', ''))

    interview_data = {}
    if rounds_raw.isdigit():
        interview_data['interview_rounds'] = int(rounds_raw)
    if interviewers:
        interview_data['interviewers'] = interviewers
    if questions:
        interview_data['technical_questions'] = questions
    if feedback:
        interview_data['feedback'] = feedback
    if next_steps:
        interview_data['next_steps'] = next_steps
    if offer_amount is not None:
        interview_data['offer_amount'] = offer_amount

    return {
        'job_id': form.get('job_id', type=int),
        'application_date': form.get('application_date', '').strip(),
        'status': form.get('status', 'Applied').strip() or 'Applied',
        'resume_version': form.get('resume_version', '').strip() or None,
        'cover_letter_sent': 1 if form.get('cover_letter_sent') == 'on' else 0,
        'response_date': form.get('response_date', '').strip() or None,
        'notes': form.get('notes', '').strip() or None,
        'interview_data': interview_data or None
    }


def _rank_jobs_by_skills(user_skills_raw):
    user_skills_map = {s.strip().lower(): s.strip() for s in user_skills_raw.split(',') if s.strip()}
    if not user_skills_map:
        return [], 0

    all_jobs = db.get_all_jobs()
    ranked = []
    unlisted_count = 0

    for job in all_jobs:
        req = job.get('requirements') or {}
        req_skills = req.get('required_skills', [])
        pref_skills = req.get('preferred_skills', [])

        if not req_skills:
            unlisted_count += 1
            continue

        matched_req = [s for s in req_skills if s.lower() in user_skills_map]
        missing_req = [s for s in req_skills if s.lower() not in user_skills_map]
        matched_pref = [s for s in pref_skills if s.lower() in user_skills_map]

        match_pct = round((len(matched_req) / len(req_skills)) * 100)
        ranked.append({
            'job': job,
            'match_pct': match_pct,
            'matched_count': len(matched_req),
            'total_required': len(req_skills),
            'matched_req': matched_req,
            'missing_req': missing_req,
            'matched_pref': matched_pref
        })

    ranked.sort(key=lambda item: (item['match_pct'], len(item['matched_pref'])), reverse=True)
    return ranked, unlisted_count


@app.route('/')
def dashboard():
    data = db.get_dashboard_data()
    return render_template(
        'dashboard.html',
        stats=data['stats'],
        status_counts=data['status_counts'],
        recent_applications=data['recent_applications']
    )


# --- COMPANIES ---
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


# --- JOBS ---
@app.route('/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'POST':
        data = _parse_job_form(request.form)
        if not data['job_title'] or not data['company_id']:
            flash('Company and Job Title are required.', 'error')
            return redirect(url_for('jobs'))

        db.add_job(**data)
        flash('Job added.', 'success')
        return redirect(url_for('jobs'))

    all_jobs = db.get_all_jobs()
    all_companies = db.get_all_companies()
    return render_template('jobs.html', jobs=all_jobs, companies=all_companies)


@app.route('/jobs/update/<int:job_id>', methods=['POST'])
def update_job(job_id):
    data = _parse_job_form(request.form)
    if not data['job_title'] or not data['company_id']:
        flash('Company and Job Title are required.', 'error')
        return redirect(url_for('jobs'))

    db.update_job(job_id=job_id, **data)
    flash('Job updated.', 'success')
    return redirect(url_for('jobs'))


@app.route('/jobs/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    try:
        db.delete_job(job_id)
        flash('Job deleted.', 'success')
    except mysql.connector.Error:
        flash('Cannot delete job while applications are linked to it.', 'error')
    return redirect(url_for('jobs'))


# --- APPLICATIONS ---
@app.route('/applications', methods=['GET', 'POST'])
def applications():
    if request.method == 'POST':
        data = _parse_application_form(request.form)
        if not data['job_id'] or not data['application_date']:
            flash('Job and Application Date are required.', 'error')
            return redirect(url_for('applications'))

        db.add_application(**data)
        flash('Application added.', 'success')
        return redirect(url_for('applications'))

    all_applications = db.get_all_applications()
    all_jobs = db.get_all_jobs()
    return render_template('applications.html', applications=all_applications, jobs=all_jobs)


@app.route('/applications/update/<int:application_id>', methods=['POST'])
def update_application(application_id):
    data = _parse_application_form(request.form)
    if not data['job_id'] or not data['application_date']:
        flash('Job and Application Date are required.', 'error')
        return redirect(url_for('applications'))

    db.update_application(application_id=application_id, **data)
    flash('Application updated.', 'success')
    return redirect(url_for('applications'))


@app.route('/applications/delete/<int:application_id>', methods=['POST'])
def delete_application(application_id):
    db.delete_application(application_id)
    flash('Application deleted.', 'success')
    return redirect(url_for('applications'))


# --- CONTACTS ---
@app.route('/contacts', methods=['GET', 'POST'])
def contacts():
    if request.method == 'POST':
        company_id = request.form.get('company_id', type=int)
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        if not company_id or not first_name or not last_name:
            flash('Company, First Name, and Last Name are required.', 'error')
            return redirect(url_for('contacts'))

        db.add_contact(
            company_id=company_id,
            first_name=first_name,
            last_name=last_name,
            job_title=request.form.get('job_title', '').strip() or None,
            email=request.form.get('email', '').strip() or None,
            phone=request.form.get('phone', '').strip() or None,
            linkedin_url=request.form.get('linkedin_url', '').strip() or None,
            notes=request.form.get('notes', '').strip() or None
        )
        flash('Contact added.', 'success')
        return redirect(url_for('contacts'))

    all_contacts = db.get_all_contacts()
    all_companies = db.get_all_companies()
    return render_template('contacts.html', contacts=all_contacts, companies=all_companies)


@app.route('/contacts/update/<int:contact_id>', methods=['POST'])
def update_contact(contact_id):
    company_id = request.form.get('company_id', type=int)
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    if not company_id or not first_name or not last_name:
        flash('Company, First Name, and Last Name are required.', 'error')
        return redirect(url_for('contacts'))

    db.update_contact(
        contact_id=contact_id,
        company_id=company_id,
        first_name=first_name,
        last_name=last_name,
        job_title=request.form.get('job_title', '').strip() or None,
        email=request.form.get('email', '').strip() or None,
        phone=request.form.get('phone', '').strip() or None,
        linkedin_url=request.form.get('linkedin_url', '').strip() or None,
        notes=request.form.get('notes', '').strip() or None
    )
    flash('Contact updated.', 'success')
    return redirect(url_for('contacts'))


@app.route('/contacts/delete/<int:contact_id>', methods=['POST'])
def delete_contact(contact_id):
    db.delete_contact(contact_id)
    flash('Contact deleted.', 'success')
    return redirect(url_for('contacts'))


# --- JOB MATCH ---
@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    skills_input = ''
    matches = []
    unlisted_count = 0
    searched = False

    if request.method == 'POST':
        skills_input = request.form.get('skills', '').strip()
        if not skills_input:
            flash('Enter at least one skill to match jobs.', 'error')
            return redirect(url_for('job_match'))

        searched = True
        matches, unlisted_count = _rank_jobs_by_skills(skills_input)

    return render_template(
        'job_match.html',
        skills_input=skills_input,
        matches=matches,
        unlisted_count=unlisted_count,
        searched=searched
    )


if __name__ == '__main__':
    app.run()