CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(255) UNIQUE,
    title VARCHAR(500),
    company VARCHAR(255),
    location VARCHAR(255),
    country VARCHAR(10),
    salary_min NUMERIC(12, 2),
    salary_max NUMERIC(12, 2),
    salary_currency VARCHAR(10),
    description TEXT,
    category VARCHAR(255),
    contract_type VARCHAR(100),
    created_at TIMESTAMP,
    fetched_at TIMESTAMP DEFAULT NOW(),
    url TEXT
);

CREATE TABLE IF NOT EXISTS job_technologies (
    id SERIAL PRIMARY KEY,
    job_id INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    technology VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_jobs_country ON jobs(country);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_tech_name ON job_technologies(technology);