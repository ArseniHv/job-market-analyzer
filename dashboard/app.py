import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analysis.analyzer import (
    get_top_technologies,
    get_salary_by_technology,
    get_top_companies,
    get_jobs_over_time,
    get_remote_vs_onsite,
    get_country_breakdown,
    get_summary_stats,
)

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Market Analyzer",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Job Market Analyzer")
st.caption("Real-time insights from software engineering job listings — powered by Adzuna API")

# ── Summary metrics ───────────────────────────────────────────────────────────
with st.spinner("Loading data..."):
    stats = get_summary_stats()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", f"{stats['total_jobs']:,}")
col2.metric("Jobs with Salary", f"{stats['jobs_with_salary']:,}")
col3.metric("Unique Companies", f"{stats['unique_companies']:,}")
col4.metric("Technologies Tracked", f"{stats['unique_technologies']:,}")

st.divider()

# ── Top Technologies ──────────────────────────────────────────────────────────
st.subheader("🔥 Most In-Demand Technologies")
tech_df = get_top_technologies(20)

if not tech_df.empty:
    fig = px.bar(
        tech_df,
        x="job_count",
        y="technology",
        orientation="h",
        color="job_count",
        color_continuous_scale="Blues",
        labels={"job_count": "Number of Jobs", "technology": "Technology"},
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=550)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No technology data available yet. Run the pipeline first.")

st.divider()

# ── Salary by Technology ──────────────────────────────────────────────────────
st.subheader("💰 Average Salary by Technology")
salary_df = get_salary_by_technology()

if not salary_df.empty:
    fig2 = px.bar(
        salary_df,
        x="avg_salary_mid",
        y="technology",
        orientation="h",
        color="avg_salary_mid",
        color_continuous_scale="Greens",
        hover_data=["job_count", "avg_salary_min", "avg_salary_max"],
        labels={
            "avg_salary_mid": "Avg Mid Salary",
            "technology": "Technology",
            "job_count": "Jobs Analyzed",
        },
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"}, height=500)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("Only technologies with 10+ salary data points are shown.")
else:
    st.info("Not enough salary data yet.")

st.divider()

# ── Two columns: Companies & Remote ──────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏢 Top Hiring Companies")
    company_df = get_top_companies(15)
    if not company_df.empty:
        fig3 = px.bar(
            company_df,
            x="job_count",
            y="company",
            orientation="h",
            color="job_count",
            color_continuous_scale="Oranges",
        )
        fig3.update_layout(yaxis={"categoryorder": "total ascending"}, height=450)
        st.plotly_chart(fig3, use_container_width=True)

with col_right:
    st.subheader("🌍 Remote vs On-site")
    remote_df = get_remote_vs_onsite()
    if not remote_df.empty:
        fig4 = px.pie(
            remote_df,
            names="work_type",
            values="job_count",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hole=0.4,
        )
        fig4.update_layout(height=450)
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── Jobs Over Time ────────────────────────────────────────────────────────────
st.subheader("📈 Job Postings Over Time")
time_df = get_jobs_over_time()

if not time_df.empty:
    fig5 = px.line(
        time_df,
        x="date",
        y="job_count",
        markers=True,
        labels={"date": "Date", "job_count": "Jobs Posted"},
    )
    fig5.update_traces(line_color="#636EFA")
    st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── Country Breakdown ─────────────────────────────────────────────────────────
st.subheader("🗺️ Jobs by Country")
country_df = get_country_breakdown()

if not country_df.empty:
    fig6 = px.bar(
        country_df,
        x="country",
        y="job_count",
        color="job_count",
        color_continuous_scale="Purples",
    )
    st.plotly_chart(fig6, use_container_width=True)

st.divider()
st.caption("Data source: Adzuna Public API | Built with Python, PostgreSQL, Streamlit & Plotly")