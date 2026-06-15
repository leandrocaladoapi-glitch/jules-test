# Global Data Jobs Scraper

An autonomous, containerized web scraping system built in Python to track, filter, and consolidate exclusive international remote jobs in the Data field (Data Engineering, Data Analysis, and Data Science).

## Mission & Architecture

This system autonomously curates top-tier data opportunities globally. It eliminates the noise of local residency requirements by processing job descriptions against strict geographic eligibility rules.

### Features
1. **Global Collection Engine**: Fetches data opportunities from the Remotive API.
2. **'Open Borders' Filter**: Employs rigorous regex patterns to guarantee the job accepts candidates globally, explicitly looking for terms like `Remote Worldwide`, `LatAm`, `Visa Sponsorship`, etc.
3. **Silent Exclusion (Red Flags)**: Instantly discards jobs hiding local residency requirements in the text (e.g., `US Only`, `Must reside in the UK`, `No Sponsorship`).
4. **Tech Stack QA**: Extracts and highlights the modern data ecosystem demanded by the job (Cloud: AWS/GCP/Azure, Big Data: Spark/Databricks, Core: Python/SQL).
5. **Zero-Touch Operation**: Runs asynchronously every 6 hours via a Python scheduler.
6. **Clean Output**: Stores approved opportunities into a persistent SQLite database containing: Company Name, Job Title, Direct Link, Main Tech Stack, and the exact eligibility proof phrase.

## Tech Stack
* Python 3.11
* `requests` & `beautifulsoup4` (Scraping / HTML parsing)
* `schedule` (Orchestration)
* SQLite (Storage)
* Docker & Docker Compose (Containerization)

## Directory Structure

```
├── data/                  # Contains the persistent SQLite database (jobs.db)
├── src/
│   ├── database.py        # SQLite initialization and insertion logic
│   ├── filters.py         # Regex logic for inclusion, exclusion, and tech stack
│   ├── main.py            # Scheduler orchestrator
│   ├── requirements.txt   # Python dependencies
│   └── scraper.py         # Crawler implementation fetching APIs
├── Dockerfile             # Container definition
├── docker-compose.yml     # Container deployment orchestration
└── README.md
```

## Quick Start (Docker)

1. **Build and Run the System**
   Simply run the orchestrator in the background:
   ```bash
   docker compose up -d --build
   ```
   The scraper will execute immediately and then schedule itself to run every 6 hours. The output will be persisted in `./data/jobs.db`.

2. **Check Logs**
   ```bash
   docker compose logs -f scraper
   ```

## Local Development & Testing

If you want to run the code locally without Docker:

1. **Install Dependencies**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

2. **Run a Single Test Cycle**
   ```bash
   python main.py --test
   ```

3. **Query the Database**
   ```bash
   sqlite3 ../data/jobs.db "SELECT * FROM jobs;"
   ```
