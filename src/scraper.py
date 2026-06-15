import asyncio
import re
import logging
from playwright.async_api import async_playwright, Page, Browser
from filters import is_eligible, extract_tech_stack
from database import insert_job

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Target roles to filter from feeds
TARGET_ROLES = [r'data engineer', r'data analyst', r'data scientist', r'machine learning', r'analytics engineer']
TARGET_ROLES_REGEX = re.compile(r'|'.join(TARGET_ROLES), re.IGNORECASE)

class WeWorkRemotelyScraper:
    def __init__(self):
        self.base_url = 'https://weworkremotely.com'
        self.category_url = 'https://weworkremotely.com/categories/remote-data-jobs'

    async def fetch_job_details(self, page: Page, job_url: str):
        try:
            await page.goto(job_url, timeout=30000, wait_until='domcontentloaded')
            # Extract description
            # WWR job descriptions are inside div class "listing-container"
            container = await page.query_selector('.listing-container')
            if container:
                return await container.inner_text()
            return ""
        except Exception as e:
            logging.error(f"Error fetching job details for {job_url}: {e}")
            return ""

    async def run(self, browser: Browser):
        logging.info("Starting WeWorkRemotely Playwright scrape...")

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        jobs_processed = 0
        jobs_saved = 0

        try:
            await page.goto(self.category_url, timeout=30000, wait_until='domcontentloaded')

            # WWR lists jobs in sections with class 'jobs' and li elements inside
            job_elements = await page.query_selector_all('li.feature')

            # Extract links and titles first so we don't hold the DOM while navigating
            job_links = []
            for element in job_elements:
                # Find the main job link within the li
                a_tags = await element.query_selector_all('a')
                href = None
                for a in a_tags:
                    link = await a.get_attribute('href')
                    if link and '/remote-jobs/' in link:
                        href = link
                        break

                if href:
                    title_elem = await element.query_selector('.new-listing__header__title__text')
                    company_elem = await element.query_selector('.new-listing__company-name')

                    # WWR has different DOM structures sometimes, fallback to standard .title / .company
                    if not title_elem:
                         title_elem = await element.query_selector('.title')
                    if not company_elem:
                         company_elem = await element.query_selector('.company')

                    title = await title_elem.inner_text() if title_elem else ""
                    company = await company_elem.inner_text() if company_elem else "Unknown"

                    if title and href:
                        job_links.append({
                            'title': title.strip(),
                            'company': company.strip(),
                            'link': self.base_url + href
                        })

            logging.info(f"Found {len(job_links)} data jobs on WWR.")

            # Now visit each job and parse
            for job in job_links:
                if not TARGET_ROLES_REGEX.search(job['title']):
                    continue

                jobs_processed += 1

                # Fetch full description
                description = await self.fetch_job_details(page, job['link'])
                if not description:
                    continue

                eligible, proof = is_eligible(description)
                if eligible:
                    tech_stack = extract_tech_stack(description)
                    job_data = {
                        'company_name': job['company'],
                        'job_title': job['title'],
                        'direct_link': job['link'],
                        'tech_stack': tech_stack,
                        'eligibility_proof': proof
                    }
                    if insert_job(job_data):
                         logging.info(f"Saved new job: {job['title']} at {job['company']}")
                         jobs_saved += 1

                # Small sleep to be polite to the server
                await asyncio.sleep(1)

        except Exception as e:
            logging.error(f"Error during WWR scrape: {e}")
        finally:
            await context.close()

        logging.info(f"WWR Scrape completed. Processed {jobs_processed} relevant jobs, saved {jobs_saved} new global opportunities.")


async def run_all_scrapers():
    """Runs all registered scrapers."""
    # Initialize DB in case it hasn't been created yet
    from database import init_db
    init_db()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        scrapers = [WeWorkRemotelyScraper()]
        for scraper in scrapers:
            await scraper.run(browser)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run_all_scrapers())