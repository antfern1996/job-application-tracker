import json
import mysql.connector
from mysql.connector import Error


def get_db_connection():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='root123;',
            database='job_tracker'
        )
    except Error as e:
        print(f"Database connection error: {e}")
        return None


# --- DASHBOARD ---
def get_dashboard_data():
    conn = get_db_connection()
    data = {
        'stats': {'companies': 0, 'jobs': 0, 'applications': 0, 'contacts': 0},
        'status_counts': [],
        'recent_applications': []
    }
    if not conn:
        return data

    cursor = conn.cursor(dictionary=True)
    for table in data['stats']:
        cursor.execute(f"SELECT COUNT(*) AS count FROM {table}")
        data['stats'][table] = cursor.fetchone()['count']

    cursor.execute("""
        SELECT status, COUNT(*) AS count
        FROM applications
        GROUP BY status
        ORDER BY count DESC
    """)
    data['status_counts'] = cursor.fetchall()

    cursor.execute("""
        SELECT a.application_id, a.application_date, a.status, a.resume_version,
               j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC, a.application_id DESC
        LIMIT 5
    """)
    data['recent_applications'] = cursor.fetchall()

    cursor.close()
    conn.close()
    return data


# --- COMPANIES CRUD ---
def get_all_companies():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM companies ORDER BY company_name ASC")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def add_company(company_name, industry, website, city, state, notes):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO companies (company_name, industry, website, city, state, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (company_name, industry, website, city, state, notes))
    conn.commit()

    cursor.close()
    conn.close()


def update_company(company_id, company_name, industry, website, city, state, notes):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        UPDATE companies
        SET company_name = %s, industry = %s, website = %s, city = %s, state = %s, notes = %s
        WHERE company_id = %s
    """

    cursor.execute(query, (company_name, industry, website, city, state, notes, company_id))
    conn.commit()

    cursor.close()
    conn.close()


def delete_company(company_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    conn.commit()

    cursor.close()
    conn.close()


# --- JOBS CRUD ---
def get_all_jobs():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT j.*, c.company_name
        FROM jobs j
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY j.is_active DESC, j.date_posted DESC, j.job_id DESC
    """)
    rows = cursor.fetchall()

    for row in rows:
        raw_req = row.get('requirements')
        if isinstance(raw_req, str):
            row['requirements'] = json.loads(raw_req)
        elif raw_req is None:
            row['requirements'] = {}

    cursor.close()
    conn.close()
    return rows


def add_job(company_id, job_title, job_type, salary_min, salary_max, posting_url, date_posted, is_active, job_description, requirements):
    conn = get_db_connection()
    cursor = conn.cursor()

    req_json = json.dumps(requirements) if requirements else None
    query = """
        INSERT INTO jobs (
            company_id, job_title, job_type, salary_min, salary_max,
            posting_url, date_posted, is_active, job_description, requirements
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        company_id, job_title, job_type, salary_min, salary_max,
        posting_url, date_posted, is_active, job_description, req_json
    ))
    conn.commit()

    cursor.close()
    conn.close()


def update_job(job_id, company_id, job_title, job_type, salary_min, salary_max, posting_url, date_posted, is_active, job_description, requirements):
    conn = get_db_connection()
    cursor = conn.cursor()

    req_json = json.dumps(requirements) if requirements else None
    query = """
        UPDATE jobs
        SET company_id = %s, job_title = %s, job_type = %s,
            salary_min = %s, salary_max = %s, posting_url = %s,
            date_posted = %s, is_active = %s, job_description = %s,
            requirements = %s
        WHERE job_id = %s
    """

    cursor.execute(query, (
        company_id, job_title, job_type, salary_min, salary_max,
        posting_url, date_posted, is_active, job_description, req_json, job_id
    ))
    conn.commit()

    cursor.close()
    conn.close()


def delete_job(job_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM jobs WHERE job_id = %s", (job_id,))
    conn.commit()

    cursor.close()
    conn.close()


# --- APPLICATIONS CRUD ---
def get_all_applications():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT a.*, j.job_title, c.company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.job_id
        JOIN companies c ON j.company_id = c.company_id
        ORDER BY a.application_date DESC, a.application_id DESC
    """)
    rows = cursor.fetchall()

    for row in rows:
        raw_iv = row.get('interview_data')
        if isinstance(raw_iv, str):
            row['interview_data'] = json.loads(raw_iv)
        elif raw_iv is None:
            row['interview_data'] = {}

    cursor.close()
    conn.close()
    return rows


def add_application(job_id, application_date, status, resume_version, cover_letter_sent, response_date, notes, interview_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    iv_json = json.dumps(interview_data) if interview_data else None
    query = """
        INSERT INTO applications (
            job_id, application_date, status, resume_version,
            cover_letter_sent, response_date, notes, interview_data
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        job_id, application_date, status, resume_version,
        cover_letter_sent, response_date, notes, iv_json
    ))
    conn.commit()

    cursor.close()
    conn.close()


def update_application(application_id, job_id, application_date, status, resume_version, cover_letter_sent, response_date, notes, interview_data):
    conn = get_db_connection()
    cursor = conn.cursor()

    iv_json = json.dumps(interview_data) if interview_data else None
    query = """
        UPDATE applications
        SET job_id = %s, application_date = %s, status = %s,
            resume_version = %s, cover_letter_sent = %s,
            response_date = %s, notes = %s, interview_data = %s
        WHERE application_id = %s
    """

    cursor.execute(query, (
        job_id, application_date, status, resume_version,
        cover_letter_sent, response_date, notes, iv_json, application_id
    ))
    conn.commit()

    cursor.close()
    conn.close()


def delete_application(application_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM applications WHERE application_id = %s", (application_id,))
    conn.commit()

    cursor.close()
    conn.close()


# --- CONTACTS CRUD ---
def get_all_contacts():
    conn = get_db_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT ct.*, c.company_name
        FROM contacts ct
        JOIN companies c ON ct.company_id = c.company_id
        ORDER BY ct.last_name ASC, ct.first_name ASC
    """)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def add_contact(company_id, first_name, last_name, job_title, email, phone, linkedin_url, notes):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO contacts (
            company_id, first_name, last_name, job_title,
            email, phone, linkedin_url, notes
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(query, (
        company_id, first_name, last_name, job_title,
        email, phone, linkedin_url, notes
    ))
    conn.commit()

    cursor.close()
    conn.close()


def update_contact(contact_id, company_id, first_name, last_name, job_title, email, phone, linkedin_url, notes):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        UPDATE contacts
        SET company_id = %s, first_name = %s, last_name = %s,
            job_title = %s, email = %s, phone = %s,
            linkedin_url = %s, notes = %s
        WHERE contact_id = %s
    """

    cursor.execute(query, (
        company_id, first_name, last_name, job_title,
        email, phone, linkedin_url, notes, contact_id
    ))
    conn.commit()

    cursor.close()
    conn.close()


def delete_contact(contact_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM contacts WHERE contact_id = %s", (contact_id,))
    conn.commit()

    cursor.close()
    conn.close()