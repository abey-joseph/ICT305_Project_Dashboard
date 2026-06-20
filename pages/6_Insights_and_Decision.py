"""
Insight Highlights + Decision Support  (required sections 3 & 4, team-level).
============================================================================

This page pulls the headline finding from every member's section into one
place, then frames the team's overall decision-support story.

Member ownership:
  - Each member writes their one-line headline insight in the INSIGHTS dict.
  - The Stakeholder Analyst / team leads fill in the decision-support narrative.
"""
from __future__ import annotations

import streamlit as st

from src import config
from src.data_loader import load_member_data

st.set_page_config(page_title="Insights & Decision Support", page_icon="💡", layout="wide")

st.title("💡 Insight Highlights & Decision Support")
st.caption(
    "The 'so what' of the dashboard — key findings per theme and the decisions "
    "they enable for stakeholders."
)
st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Insight highlights (one per member)
# ---------------------------------------------------------------------------
# TODO each member: replace your placeholder with your real headline insight.
INSIGHTS = {
    1: "TODO — Member 1's headline insight.",
    2: "TODO — Member 2's headline insight.",
    3: "TODO — Member 3's headline insight.",
    4: "TODO — Member 4's headline insight.",
    5: "TODO — Member 5's headline insight.",
}

st.subheader("Key findings across themes")
for m in config.MEMBERS:
    df, is_real = load_member_data(m["id"])
    metric = next((x for x in m["metrics"] if x in df.columns), None)
    auto = ""
    if metric and m["category_col"] in df.columns:
        top = df.groupby(m["category_col"])[metric].mean().idxmax()
        auto = f"  \n*(auto): highest average {metric} → **{top}**.*"
    with st.container(border=True):
        st.markdown(f"#### {m['emoji']} {m['theme_title']} — {m['name']}")
        st.markdown(INSIGHTS.get(m["id"], "") + auto)

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Decision support narrative
# ---------------------------------------------------------------------------
st.subheader("Decision support")
st.markdown(
    f"""
**Who this is for:** {config.PROJECT_STAKEHOLDER}

**Decision context:** {config.DECISION_CONTEXT}

**Decisions this dashboard enables**
1. *TODO — primary decision the combined analysis supports.*
2. *TODO — secondary decision.*
3. *TODO — operational/tactical follow-up.*

**How stakeholders should use it**
- Start on the **Overview** for the situational snapshot.
- Open the relevant member section, apply the filters to the period/segment in question.
- Read the trend, comparison and distribution together before acting.

**Recommended actions**
- *TODO — concrete action the evidence points to.*
"""
)

with st.expander("Limitations & data integrity notes"):
    st.markdown(
        "- *TODO — note any data gaps, interpolation, sample-size caveats, or "
        "assumptions so readers know how much confidence to place in each finding.*"
    )
