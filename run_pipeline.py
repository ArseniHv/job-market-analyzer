"""
Main pipeline runner.
Run this to: fetch → clean → store jobs in PostgreSQL.
"""
import json
import glob
from scraper.fetcher import fetch_all_and_save
from scraper.cleaner import clean_jobs, save_jobs_to_db
from database.db import get_engine


def run():
    print("=" * 50)
    print("JOB MARKET ANALYZER — Data Pipeline")
    print("=" * 50)

    # Step 1: Fetch from API
    print("\n[1/3] Fetching jobs from Adzuna API...")
    raw_jobs = fetch_all_and_save()

    # Step 2: Clean data
    print("\n[2/3] Cleaning and extracting technologies...")
    df = clean_jobs(raw_jobs)

    # Step 3: Store in DB
    print("\n[3/3] Storing in PostgreSQL...")
    engine = get_engine()
    save_jobs_to_db(df, engine)

    print("\n✅ Pipeline complete!")


if __name__ == "__main__":
    run()