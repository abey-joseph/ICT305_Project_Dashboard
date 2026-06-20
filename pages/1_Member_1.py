"""
Member 1 — section.   (WORKED EXAMPLE — reference for the whole team)

This page shows the standard pattern: add filters in the sidebar, use their
return values to filter your data, then draw charts from the filtered data.
Copy this approach into your own page and adapt it to your dataset.

The other member pages are left empty on purpose — this one is the reference.
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Member 1", layout="wide")
st.title("Member 1 — [your theme]")

# ---------------------------------------------------------------------------
# 1. Load your data
#    Put your CSV in data/member1/ . This grabs the first .csv it finds.
# ---------------------------------------------------------------------------
data_dir = Path(__file__).resolve().parent.parent / "data" / "member1"
csv_files = sorted(data_dir.glob("*.csv"))

if not csv_files:
    st.info("Add a .csv file to data/member1/ to see this section in action.")
    st.stop()   # nothing more to draw until data exists

# Adjust parse_dates to your actual date column name (or remove if you have none)
df = pd.read_csv(csv_files[0], parse_dates=["date"])

# ---------------------------------------------------------------------------
# 2. Filters / controls — live in the sidebar.
#    Each widget RETURNS the user's choice, and only shows on THIS page.
#    (Change the column names below to match your dataset.)
# ---------------------------------------------------------------------------
st.sidebar.header("Member 1 — Filters")

# Dropdown for a categorical column
category = st.sidebar.selectbox("Category", sorted(df["category"].unique()))

# Slider for a date range
min_date = df["date"].min().to_pydatetime()
max_date = df["date"].max().to_pydatetime()
date_range = st.sidebar.slider(
    "Date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
)

# ---------------------------------------------------------------------------
# 3. Apply the filters to the data.
#    Reuse `filtered` for every chart so they all update together.
# ---------------------------------------------------------------------------
filtered = df[
    (df["category"] == category)
    & (df["date"].between(date_range[0], date_range[1]))
]

if filtered.empty:
    st.warning("No rows match the current filters. Widen your selection.")
    st.stop()

# ---------------------------------------------------------------------------
# 4. Charts — built from `filtered`, so they react to the filters automatically.
#    Pick whatever chart types suit your analysis.
# ---------------------------------------------------------------------------
st.subheader(f"Trend — {category}")
st.plotly_chart(
    px.line(filtered, x="date", y="value"),   # change "value" to your metric column
    use_container_width=True,
)
