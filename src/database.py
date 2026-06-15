import sqlite3
import os

DB_PATH = os.environ.get('DB_PATH', '../data/jobs.db')

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            direct_link TEXT UNIQUE NOT NULL,
            tech_stack TEXT,
            eligibility_proof TEXT,
            insertion_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def insert_job(job):
    """Insert a job into the database if it doesn't already exist.
    job is a dict containing: company_name, job_title, direct_link, tech_stack, eligibility_proof
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO jobs (company_name, job_title, direct_link, tech_stack, eligibility_proof)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            job['company_name'],
            job['job_title'],
            job['direct_link'],
            job['tech_stack'],
            job['eligibility_proof']
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Job already exists (unique direct_link)
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized.")