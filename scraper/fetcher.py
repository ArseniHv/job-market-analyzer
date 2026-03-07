import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")

BASE_URL = "https://api.adzuna.com/v1/api/jobs"

SEARCH_TERMS = [
    "python developer",
    "java developer",
    "software engineer",
    "data engineer",
    "backend developer",
    "frontend developer",
    "devops engineer",
    "machine learning engineer",
]

COUNTRIES = ["gb", "us"]  


def fetch_jobs(country: str, search_term: str, pages: int = 3) -> list[dict]:
    """Fetch job listings from Adzuna API."""
    all_jobs = []

    for page in range(1, pages + 1):
        url = f"{BASE_URL}/{country}/search/{page}"
        params = {
            "app_id": APP_ID,
            "app_key": APP_KEY,
            "what": search_term,
            "results_per_page": 50,
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            jobs = data.get("results", [])
            all_jobs.extend(jobs)
            print(f"  [{country.upper()}] '{search_term}' page {page}: {len(jobs)} jobs fetched")
            time.sleep(0.5) 

        except requests.RequestException as e:
            print(f"  Error fetching page {page}: {e}")
            break

    return all_jobs


def fetch_all_and_save():
    """Fetch all jobs and save raw data to /data folder."""
    all_jobs = []

    for country in COUNTRIES:
        for term in SEARCH_TERMS:
            print(f"Fetching: {term} in {country.upper()}")
            jobs = fetch_jobs(country, term, pages=3)
            for job in jobs:
                job["_search_term"] = term
                job["_country"] = country
            all_jobs.extend(jobs)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"data/raw_jobs_{timestamp}.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=2, default=str)

    print(f"\nDone. {len(all_jobs)} total jobs saved to {output_path}")
    return all_jobs


if __name__ == "__main__":
    fetch_all_and_save()