# Job Market Analyzer

A data pipeline and interactive dashboard that collects, stores, and analyzes
real software engineering job listings to reveal trends in the tech job market.

## What it does

- Fetches live job listings from the **Adzuna public API** (US & UK markets)
- Extracts 60+ technology keywords from job descriptions using regex
- Stores structured data in **PostgreSQL**
- Generates insights: most demanded technologies, salary ranges, top companies
- Renders everything in an **interactive Streamlit dashboard**

## Tech Stack

| Layer | Technology |
|---|---|
| Data collection | Python, Requests, Adzuna API |
| Storage | PostgreSQL, SQLAlchemy |
| Processing | Pandas |
| Visualization | Streamlit, Plotly |
| Version control | Git, GitHub |

## Project Structure
```
job-market-analyzer/
├── scraper/          # API fetcher and data cleaner
├── database/         # Schema and DB connection
├── analysis/         # SQL + Pandas analysis queries
├── dashboard/        # Streamlit app
├── data/             # Raw JSON dumps (gitignored)
├── run_pipeline.py   # One-command pipeline runner
└── requirements.txt
```

## Setup
```bash
git clone https://github.com/YOUR_USERNAME/job-market-analyzer.git
cd job-market-analyzer
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=jobmarket
DB_USER=postgres
DB_PASSWORD=yourpassword
ADZUNA_APP_ID=your_id
ADZUNA_APP_KEY=your_key
```

Run:
```bash
python run_pipeline.py
streamlit run dashboard/app.py
```

## Example Insights

- Python, SQL and JavaScript are the most demanded technologies
- AWS, Docker and React appear together in 40%+ of senior job listings
- Rust and Go roles offer the highest average salaries

## Future Improvements

- ML salary prediction model
- Weekly trend email report
- Tech stack co-occurrence clustering
- LinkedIn or Indeed integration