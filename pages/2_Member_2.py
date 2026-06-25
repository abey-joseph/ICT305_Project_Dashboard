from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Member 2 - Cost of Living", layout="wide")

st.title("Member 2 - Cost of Living & Inflationary Pressures")

st.header("Overview / Executive Summary")
st.markdown(
    """
My section checks whether household income has really kept up with inflation.
I focus on the CPI columns, median household income, and real income change
because these are the variables most directly connected to everyday cost
pressure.

**Hypothesis:** while median household income has risen, CPI pressure may
outpace real-wage growth and create financial anxiety.
"""
)


# ---------------------------------------------------------------------------
# 1. Load the master dataset
#    The first two paths follow the project requirement. The extra processed
#    paths help the page still run from this repository's current structure.
# ---------------------------------------------------------------------------
try:
    df = pd.read_csv("data/master_cleaned.csv")
except FileNotFoundError:
    try:
        df = pd.read_csv("../data/master_yearly.csv")
    except FileNotFoundError:
        project_root = Path(__file__).resolve().parent.parent
        try:
            df = pd.read_csv(project_root / "data" / "processed" / "master_clean.csv")
        except FileNotFoundError:
            df = pd.read_csv(project_root / "data" / "processed" / "master_yearly.csv")


required_columns = [
    "year",
    "m2_cpi_all_items",
    "m2_cpi_food",
    "m2_median_household_income_sgd",
    "m2_real_income_change_pct",
]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()


# Keep only Member 2 columns and remove rows that cannot be plotted.
df_m2 = df[required_columns].copy()
df_m2["year"] = pd.to_numeric(df_m2["year"], errors="coerce")
df_m2 = df_m2.dropna(subset=["year"]).sort_values("year")
df_m2["year"] = df_m2["year"].astype(int)

for col in required_columns[1:]:
    df_m2[col] = pd.to_numeric(df_m2[col], errors="coerce")


# ---------------------------------------------------------------------------
# 2. Create the three required filters for this page.
#    These choices control the dataframe used in the chart below.
# ---------------------------------------------------------------------------
st.sidebar.header("Member 2 - Filters")

cpi_options = {
    "All Items CPI": "m2_cpi_all_items",
    "Food CPI": "m2_cpi_food",
}
selected_cpi_label = st.sidebar.selectbox("CPI metric", list(cpi_options.keys()))

income_options = {
    "Median Household Income": "m2_median_household_income_sgd",
    "Real Income Change %": "m2_real_income_change_pct",
}
selected_income_label = st.sidebar.radio("Income metric", list(income_options.keys()))

min_year = int(df_m2["year"].min())
max_year = int(df_m2["year"].max())
selected_years = st.sidebar.slider(
    "Year range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1,
)


# Filter the dataset based on the chosen year range.
cpi_col = cpi_options[selected_cpi_label]
income_col = income_options[selected_income_label]
filtered_df = df_m2[
    (df_m2["year"] >= selected_years[0]) & (df_m2["year"] <= selected_years[1])
].dropna(subset=[cpi_col, income_col])

if filtered_df.empty:
    st.warning("No data is available for the selected filters.")
    st.stop()


# ---------------------------------------------------------------------------
# 3. Dual-axis chart
#    Left axis shows CPI, while right axis overlays the selected income metric.
# ---------------------------------------------------------------------------
income_axis_title = (
    "Median household income (SGD)"
    if income_col == "m2_median_household_income_sgd"
    else "Real income change (%)"
)

start_row = filtered_df.iloc[0]
end_row = filtered_df.iloc[-1]
start_year = int(start_row["year"])
end_year = int(end_row["year"])
start_cpi = start_row[cpi_col]
end_cpi = end_row[cpi_col]
start_income = start_row[income_col]
end_income = end_row[income_col]
cpi_change = end_cpi - start_cpi
income_change = end_income - start_income

if income_col == "m2_median_household_income_sgd":
    income_start_text = f"SGD {start_income:,.0f}"
    income_end_text = f"SGD {end_income:,.0f}"
    income_change_text = f"SGD {income_change:,.0f}"
else:
    income_start_text = f"{start_income:.1f}%"
    income_end_text = f"{end_income:.1f}%"
    income_change_text = f"{income_change:.1f} percentage points"

year_2022 = df_m2[df_m2["year"] == 2022]
if not year_2022.empty:
    food_2022 = year_2022["m2_cpi_food"].iloc[0]
    real_income_2022 = year_2022["m2_real_income_change_pct"].iloc[0]
    context_2022 = (
        f"In 2022, Food CPI was {food_2022:.1f}, but real income change was "
        f"only {real_income_2022:.1f}%. That is the year where the cost "
        "pressure looks most obvious to me."
    )
else:
    context_2022 = (
        "The dataset does not include 2022, so I focused on the selected "
        "year range instead."
    )

st.header("Exploratory Analysis")
st.markdown(
    f"""
I plotted **{selected_cpi_label}** against **{selected_income_label}** from
**{start_year} to {end_year}**. In this selected period, the CPI value moved
from **{start_cpi:.1f} to {end_cpi:.1f}**, a change of **{cpi_change:.1f}**
index points. The income measure moved from **{income_start_text} to
{income_end_text}**, a change of **{income_change_text}**.
"""
)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=filtered_df["year"],
        y=filtered_df[cpi_col],
        name=selected_cpi_label,
        mode="lines+markers",
        line=dict(color="#2A6FBB", width=3),
        marker=dict(size=7),
        yaxis="y",
    )
)

fig.add_trace(
    go.Scatter(
        x=filtered_df["year"],
        y=filtered_df[income_col],
        name=selected_income_label,
        mode="lines+markers",
        line=dict(color="#D1495B", width=3),
        marker=dict(size=7),
        yaxis="y2",
    )
)

fig.update_layout(
    title=f"{selected_cpi_label} vs {selected_income_label}",
    xaxis=dict(title="Year", showgrid=False),
    yaxis=dict(title=f"{selected_cpi_label} index", showgrid=True, gridcolor="#E8E8E8"),
    yaxis2=dict(
        title=income_axis_title,
        overlaying="y",
        side="right",
        showgrid=False,
    ),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=40, r=40, t=80, b=40),
    template="plotly_white",
    hovermode="x unified",
)

st.plotly_chart(fig, use_container_width=True)


# ---------------------------------------------------------------------------
# 4. Dashboard narrative for interpretation and decision support
# ---------------------------------------------------------------------------
st.header("Insight Highlights")
st.markdown(
    f"""
- I plotted **{selected_cpi_label}** against **{selected_income_label}** to
  check whether income kept up with prices. From {start_year} to {end_year},
  the CPI line changed by **{cpi_change:.1f} index points**, so the price
  pressure is not just a small movement.
- {context_2022}
- The part that matters for households is the mismatch: income may go up in
  dollar terms, but **m2_real_income_change_pct** shows that purchasing power
  can still be weak when CPI rises faster.
"""
)

st.header("Decision Support")
st.markdown(
    f"""
For **MTI**, this page can help flag years where inflation is likely to hurt
household purchasing power, especially if **m2_cpi_food** rises while
**m2_real_income_change_pct** stays low. For **NTUC**, the same evidence can
support wage talks by pointing to specific years, such as 2022, where food
prices rose but real income barely moved. My practical takeaway is simple:
when essential CPI keeps rising, wage adjustments and food-related subsidies
should be more targeted instead of being treated as a general cost-of-living
issue.
"""
)
