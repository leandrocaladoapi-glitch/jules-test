import requests
import re
import logging
from bs4 import BeautifulSoup
from filters import is_eligible, extract_tech_stack
from database import insert_job

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Target roles to filter from feeds
TARGET_ROLES = [r'data engineer', r'data analyst', r'data scientist', r'machine learning', r'analytics engineer']
TARGET_ROLES_REGEX = re.compile(r'|'.join(TARGET_ROLES), re.IGNORECASE)

class RemotiveScraper:
    def __init__(self):
        # Remotive API for Data jobs
        self.api_url = 'https://remotive.com/api/remote-jobs?category=data'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

    def fetch_jobs(self):
        try:
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('jobs', [])
        except requests.RequestException as e:
            logging.error(f"Error fetching Remotive API: {e}")
            return []

    def run(self):
        logging.info("Starting Remotive API scrape...")
        jobs = self.fetch_jobs()
        if not jobs:
            return

        jobs_processed = 0
        jobs_saved = 0

        for job in jobs:
            job_title = job.get('title', '')
            company_name = job.get('company_name', 'Unknown')
            link = job.get('url', '')
            description_text = job.get('description', '')

            # Check if it's a target role
            if not TARGET_ROLES_REGEX.search(job_title):
                continue

            jobs_processed += 1

            # The API returns HTML in description, clean it up roughly
            description_text = BeautifulSoup(description_text, 'html.parser').get_text(separator=' ', strip=True)

            if not description_text:
                continue

            # Apply filters
            eligible, proof = is_eligible(description_text)

            if eligible:
                tech_stack = extract_tech_stack(description_text)

                job_data = {
                    'company_name': company_name,
                    'job_title': job_title,
                    'direct_link': link,
                    'tech_stack': tech_stack,
                    'eligibility_proof': proof
                }

                # Attempt to save to DB
                if insert_job(job_data):
                    logging.info(f"Saved new job: {job_title} at {company_name}")
                    jobs_saved += 1
                else:
                    # Duplicate
                    pass

        logging.info(f"Scrape completed. Processed {jobs_processed} relevant jobs, saved {jobs_saved} new global opportunities.")

def run_all_scrapers():
    """Runs all registered scrapers."""
    # Initialize DB in case it hasn't been created yet
    from database import init_db
    init_db()

    scrapers = [RemotiveScraper()]
    for scraper in scrapers:
        scraper.run()

if __name__ == '__main__':
    run_all_scrapers()
