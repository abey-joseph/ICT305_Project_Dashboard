"""
ICT305 — Interactive Data Dashboard  |  ENTRY POINT
====================================================

Run from the project root:

    streamlit run app.py

This file is the HOME / Overview-Executive-Summary page (required section 1).
Other sections live in pages/ and appear in the left sidebar automatically:

    pages/1_Member_1.py ... 5_Member_5.py   -> each member's themed section
    pages/6_Insights_and_Decision.py        -> Insight Highlights + Decision Support

Role: Dashboard Developer scaffolds & maintains this shared framework.
Each member owns their own page file + data/memberN/ folder.
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src import components as ui
from src import config
from src.data_loader import load_member_data

st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title(f"{config.APP_ICON} {config.APP_TITLE}")
st.markdown(
    f"**Topic:** {config.PROJECT_TOPIC} &nbsp;|&nbsp; "
    f"**Stakeholders:** {config.PROJECT_STAKEHOLDER} &nbsp;|&nbsp; "
    f"**Decision context:** {config.DECISION_CONTEXT}"
)
st.caption(
    "Executive Summary — a high-level snapshot across all five themes. "
    "Use the sidebar to drill into each member's section."
)
st.divider()

# ---------------------------------------------------------------------------
# Cross-team KPI strip
# ---------------------------------------------------------------------------
st.subheader("Team snapshot")

any_real = False
summary_rows = []
for m in config.MEMBERS:
    df, is_real = load_member_data(m["id"])
    any_real = any_real or is_real
    primary_metric = next((x for x in m["metrics"] if x in df.columns), None)
    if primary_metric is None:
        continue
    summary_rows.append(
        {
            "Member": m["name"],
            "Theme": m["theme_title"],
            "Metric": primary_metric,
            "Total": df[primary_metric].sum(),
            "Average": df[primary_metric].mean(),
            "Data": "Real" if is_real else "Sample",
        }
    )

summary = pd.DataFrame(summary_rows)

kpi_cols = st.columns(len(config.MEMBERS))
for col, (_, row) in zip(kpi_cols, summary.iterrows()):
    col.metric(
        label=f"{row['Theme']}",
        value=f"{row['Total']:,.0f}",
        help=f"{row['Member']} · total {row['Metric']} ({row['Data']} data)",
    )

if not any_real:
    st.info(
        "All sections are currently running on **sample data** so the dashboard "
        "works end-to-end. Each member swaps in their real CSV when ready.",
        icon="📦",
    )

st.divider()

# ---------------------------------------------------------------------------
# High-level comparison across themes
# ---------------------------------------------------------------------------
left, right = st.columns([3, 2])

with left:
    st.markdown("##### Average level by theme")
    if not summary.empty:
        fig = px.bar(
            summary,
            x="Theme",
            y="Average",
            color="Theme",
            color_discrete_sequence=config.PALETTE,
            text="Member",
        )
        fig.update_layout(showlegend=False, height=380, margin=dict(l=10, r=10, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("##### Sections")
    for m in config.MEMBERS:
        st.markdown(f"- {m['emoji']} **{m['theme_title']}** — {m['name']}")
    st.caption("Open any section from the sidebar →")

st.divider()
st.markdown(
    "###### How to read this dashboard\n"
    "Start here for the big picture, then open a member's section for the "
    "**Exploratory analysis**, **Insight highlights**, and **Decision support** "
    "specific to that theme. Every chart inside a section responds to that "
    "section's sidebar filters."
)
