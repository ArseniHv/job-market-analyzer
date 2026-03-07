import re
import pandas as pd
from datetime import datetime

# Master list of technologies to detect in job descriptions
TECH_KEYWORDS = [
    # Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "golang",
    "rust", "kotlin", "swift", "php", "ruby", "scala", "r",
    # Frameworks & Libraries
    "react", "angular", "vue", "django", "flask", "fastapi", "spring", "node.js",
    "express", ".net", "rails", "laravel", "tensorflow", "pytorch", "pandas",
    "numpy", "scikit-learn", "keras",
    # Databases
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch", "cassandra",
    "sqlite", "oracle", "mssql", "dynamodb",
    # Cloud & DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "github actions", "gitlab", "ansible", "linux",
    # Data & ML
    "spark", "kafka", "airflow", "dbt", "snowflake", "databricks", "hadoop",
    "tableau", "power bi", "looker",
    # Other tools
    "git", "rest api", "graphql", "microservices", "agile", "scrum",
]


def extract_technologies(text: str) -> list[str]:
    """Extract technology keywords from a job description."""
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for tech in TECH_KEYWORDS:
        pattern = r'\b' + re.escape(tech) + r'\b'
        if re.search(pattern, text_lower):
            found.append(tech)
    return found


def clean_salary(salary_min, salary_max, currency="GBP"):
    """Normalize salary values."""
    try:
        s_min = float(salary_min) if salary_min else None
        s_max = float(salary_max) if salary_max else None

        if s_min and s_min < 1000:
            s_min = None
        if s_max and s_max < 1000:
            s_max = None
        if s_min and s_min > 500000:
            s_min = None
        if s_max and s_max > 500000:
            s_max = None

        return s_min, s_max
    except (ValueError, TypeError):
        return None, None


def clean_jobs(raw_jobs: list[dict]) -> pd.DataFrame:
    """Transform raw Adzuna API results into a clean DataFrame."""
    records = []

    for job in raw_jobs:
        salary_min, salary_max = clean_salary(
            job.get("salary_min"),
            job.get("salary_max"),
        )

        description = job.get("description", "") or ""
        title = job.get("title", "") or ""
        full_text = title + " " + description

        technologies = extract_technologies(full_text)

        created_raw = job.get("created")
        try:
            created_at = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        except Exception:
            created_at = None

        records.append({
            "external_id": job.get("id"),
            "title": title.strip()[:500],
            "company": (job.get("company", {}) or {}).get("display_name", "Unknown"),
            "location": (job.get("location", {}) or {}).get("display_name", "Unknown"),
            "country": job.get("_country", "").upper(),
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": "USD" if job.get("_country") == "us" else "GBP",
            "description": description[:5000],
            "category": (job.get("category", {}) or {}).get("label", "Unknown"),
            "contract_type": job.get("contract_type", "Unknown"),
            "created_at": created_at,
            "url": job.get("redirect_url", ""),
            "technologies": technologies,
        })

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["external_id"])
    print(f"Cleaned {len(df)} unique job records.")
    return df


def save_jobs_to_db(df: pd.DataFrame, engine):
    """Insert cleaned jobs and their technologies into PostgreSQL."""
    from sqlalchemy import text

    inserted = 0
    skipped = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            result = conn.execute(text("""
                INSERT INTO jobs (
                    external_id, title, company, location, country,
                    salary_min, salary_max, salary_currency,
                    description, category, contract_type, created_at, url
                ) VALUES (
                    :external_id, :title, :company, :location, :country,
                    :salary_min, :salary_max, :salary_currency,
                    :description, :category, :contract_type, :created_at, :url
                )
                ON CONFLICT (external_id) DO NOTHING
                RETURNING id
            """), {
                "external_id": row["external_id"],
                "title": row["title"],
                "company": row["company"],
                "location": row["location"],
                "country": row["country"],
                "salary_min": row["salary_min"],
                "salary_max": row["salary_max"],
                "salary_currency": row["salary_currency"],
                "description": row["description"],
                "category": row["category"],
                "contract_type": row["contract_type"],
                "created_at": row["created_at"],
                "url": row["url"],
            })

            row_id = result.fetchone()
            if row_id is None:
                skipped += 1
                continue

            job_db_id = row_id[0]
            inserted += 1

            for tech in row["technologies"]:
                conn.execute(text("""
                    INSERT INTO job_technologies (job_id, technology)
                    VALUES (:job_id, :technology)
                """), {"job_id": job_db_id, "technology": tech})

    print(f"Inserted: {inserted} jobs | Skipped (duplicates): {skipped}")