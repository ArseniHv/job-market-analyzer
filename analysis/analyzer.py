import pandas as pd
from sqlalchemy import text
from database.db import get_engine


def get_top_technologies(limit=20) -> pd.DataFrame:
    sql = text(f"""
        SELECT technology, COUNT(*) as job_count
        FROM job_technologies
        GROUP BY technology
        ORDER BY job_count DESC
        LIMIT {limit}
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)


def get_salary_by_technology(min_jobs=10) -> pd.DataFrame:
    sql = text(f"""
        SELECT
            jt.technology,
            COUNT(DISTINCT j.id) as job_count,
            ROUND(AVG(j.salary_min)::numeric, 0) as avg_salary_min,
            ROUND(AVG(j.salary_max)::numeric, 0) as avg_salary_max,
            ROUND(((AVG(j.salary_min) + AVG(j.salary_max)) / 2)::numeric, 0) as avg_salary_mid
        FROM job_technologies jt
        JOIN jobs j ON jt.job_id = j.id
        WHERE j.salary_min IS NOT NULL AND j.salary_max IS NOT NULL
        GROUP BY jt.technology
        HAVING COUNT(DISTINCT j.id) >= {min_jobs}
        ORDER BY avg_salary_mid DESC
        LIMIT 20
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)


def get_top_companies(limit=15) -> pd.DataFrame:
    sql = text(f"""
        SELECT company, COUNT(*) as job_count
        FROM jobs
        WHERE company != 'Unknown'
        GROUP BY company
        ORDER BY job_count DESC
        LIMIT {limit}
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)


def get_jobs_over_time() -> pd.DataFrame:
    sql = text("""
        SELECT
            DATE_TRUNC('day', created_at) as date,
            COUNT(*) as job_count
        FROM jobs
        WHERE created_at IS NOT NULL
        GROUP BY DATE_TRUNC('day', created_at)
        ORDER BY date
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)


def get_remote_vs_onsite() -> pd.DataFrame:
    sql = text("""
        SELECT
            CASE
                WHEN LOWER(title) LIKE '%remote%'
                  OR LOWER(description) LIKE '%remote%' THEN 'Remote'
                ELSE 'On-site / Hybrid'
            END as work_type,
            COUNT(*) as job_count
        FROM jobs
        GROUP BY work_type
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)


def get_country_breakdown() -> pd.DataFrame:
    sql = text("""
        SELECT country, COUNT(*) as job_count
        FROM jobs
        GROUP BY country
        ORDER BY job_count DESC
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(sql, conn)


def get_summary_stats() -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        total = pd.read_sql(text("SELECT COUNT(*) as n FROM jobs"), conn).iloc[0]["n"]
        with_salary = pd.read_sql(
            text("SELECT COUNT(*) as n FROM jobs WHERE salary_min IS NOT NULL"), conn
        ).iloc[0]["n"]
        companies = pd.read_sql(
            text("SELECT COUNT(DISTINCT company) as n FROM jobs WHERE company != 'Unknown'"), conn
        ).iloc[0]["n"]
        techs = pd.read_sql(
            text("SELECT COUNT(DISTINCT technology) as n FROM job_technologies"), conn
        ).iloc[0]["n"]

    return {
        "total_jobs": int(total),
        "jobs_with_salary": int(with_salary),
        "unique_companies": int(companies),
        "unique_technologies": int(techs),
    }