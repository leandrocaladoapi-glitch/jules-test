import schedule
import time
import logging
import argparse
from scraper import run_all_scrapers
from database import init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    logging.info("Starting scheduled job scraping cycle...")
    run_all_scrapers()
    logging.info("Scheduled cycle completed. Waiting for next run...")

def main():
    parser = argparse.ArgumentParser(description="Run the Global Data Job Scraper")
    parser.add_argument('--test', action='store_true', help='Run the scraper once immediately for testing')
    args = parser.parse_args()

    # Ensure DB is initialized
    init_db()

    if args.test:
        logging.info("Running in test mode: executing one scrape cycle immediately.")
        job()
        return

    # Schedule the job every 6 hours
    schedule.every(6).hours.do(job)

    logging.info("Job Scraper Orchestrator started. Running every 6 hours.")

    # Run once at startup
    job()

    # Loop forever
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()