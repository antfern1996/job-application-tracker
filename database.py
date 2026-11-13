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