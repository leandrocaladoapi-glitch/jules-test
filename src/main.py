import asyncio
import logging
import argparse
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from scraper import run_all_scrapers
from database import init_db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def job():
    logging.info("Starting scheduled job scraping cycle...")
    await run_all_scrapers()
    logging.info("Scheduled cycle completed. Waiting for next run...")

async def main():
    parser = argparse.ArgumentParser(description="Run the Global Data Job Scraper")
    parser.add_argument('--test', action='store_true', help='Run the scraper once immediately for testing')
    args = parser.parse_args()

    # Ensure DB is initialized
    init_db()

    if args.test:
        logging.info("Running in test mode: executing one scrape cycle immediately.")
        await job()
        return

    scheduler = AsyncIOScheduler()

    # Schedule the job every 6 hours
    scheduler.add_job(job, trigger=IntervalTrigger(hours=6))

    logging.info("Job Scraper Orchestrator started. Running every 6 hours.")

    scheduler.start()

    # Run once at startup
    await job()

    # Keep the event loop running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    # Prevent RuntimeError: Event loop is closed on Windows
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())