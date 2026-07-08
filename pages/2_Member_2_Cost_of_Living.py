from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Member 2 - Cost of Living", layout="wide")

BLUE = "#2A6FBB"
RED = "#D1495B"
GREEN = "#3C896D"
ORANGE = "#E8A33D"
GREY = "#8A8D91"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_m2() -> pd.DataFrame:
    df = pd.read_csv(PROC_DIR / "master_clean.csv")
    cols = [
        "year",
        "m2_cpi_all_items",
        "m2_cpi_food",
        "m2_median_household_income_sgd",
        "m2_real_income_change_pct",
        "m2_gini_coefficient",
        "m2_gdp_per_capita_sgd",
        "m2_income_per_person_sgd",
        "m2_gdp_vs_income_gap_x",
        "m2_income_growth_pct",
        "m2_cpi_growth_pct",
    ]
    missing = [col for col in cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing Member 2 columns: {', '.join(missing)}")

    m2 = df[cols].copy()
    for col in cols:
        m2[col] = pd.to_numeric(m2[col], errors="coerce")
    m2 = m2.dropna(subset=["year"]).sort_values("year")
    m2["year"] = m2["year"].astype(int)
    m2 = m2[(m2["year"] >= 2010) & (m2["year"] <= 2025)].copy()
    m2["m2_food_cpi_growth_pct"] = m2["m2_cpi_food"].pct_change() * 100
    m2["m2_food_vs_income_growth_gap"] = (
        m2["m2_food_cpi_growth_pct"] - m2["m2_income_growth_pct"]
    )
    m2["m2_income_per_person_annual_sgd"] = m2["m2_income_per_person_sgd"] * 12
    return m2


def insight_block(analysis: str, explanation: str, audience: str, recommendation: str) -> None:
    st.markdown("#### Analysis")
    st.markdown(analysis)
    st.markdown("#### Explanation")
    st.markdown(explanation)
    st.markdown(f"**Target audience:** {audience}")
    st.markdown(f"**Recommendation:** {recommendation}")


def filter_years(df: pd.DataFrame) -> pd.DataFrame:
    yr = st.session_state.get("m2_year_range", (2010, 2025))
    return df[(df["year"] >= yr[0]) & (df["year"] <= yr[1])].copy()


try:
    m2_all = load_m2()
except Exception as exc:
    st.error(str(exc))
    st.stop()


def chart_cpi_food_vs_all() -> None:
    st.subheader("Food CPI Rose Faster Than Overall CPI")
    view = filter_years(m2_all)
    if view.empty:
        st.warning("No data in the selected year range.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_cpi_all_items"], name="All Items CPI",
        mode="lines+markers", line=dict(color=BLUE, width=3), marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_cpi_food"], name="Food CPI",
        mode="lines+markers", line=dict(color=RED, width=3), marker=dict(size=7),
    ))
    fig.update_layout(
        title="Food prices climbed faster than the general CPI basket",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="CPI index", showgrid=True, gridcolor="#E8E8E8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_white", hovermode="x unified",
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    first, last = view.iloc[0], view.iloc[-1]
    food_change = last["m2_cpi_food"] - first["m2_cpi_food"]
    all_change = last["m2_cpi_all_items"] - first["m2_cpi_all_items"]
    insight_block(
        analysis=(
            f"- Food CPI moved from **{first['m2_cpi_food']:.1f} to "
            f"{last['m2_cpi_food']:.1f}**, a rise of **{food_change:.1f} index "
            f"points** in the selected window.\n"
            f"- All Items CPI rose by **{all_change:.1f} index points** over the "
            "same window, so the essential food basket is not a small side issue.\n"
            "- This is why I focus on Food CPI in the EDA: groceries are a daily "
            "cost households cannot easily postpone."
        ),
        explanation=(
            "A household can delay some purchases, but it cannot opt out of food. "
            "When Food CPI rises faster than the general basket, lower- and middle-"
            "income households feel the pressure quickly even if headline income rises."
        ),
        audience="MTI, NTUC, social service policy analysts.",
        recommendation=(
            "Use Food CPI as a separate stress indicator when deciding whether cost-"
            "of-living support should target essentials rather than broad rebates."
        ),
    )


def chart_income_vs_real_change() -> None:
    st.subheader("Income Went Up, But Real Income Growth Was Uneven")
    view = filter_years(m2_all)
    if view.empty:
        st.warning("No data in the selected year range.")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_median_household_income_sgd"],
        name="Median household income", mode="lines+markers",
        line=dict(color=GREEN, width=3), marker=dict(size=7),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_real_income_change_pct"],
        name="Real income change", mode="lines+markers",
        line=dict(color=RED, width=3, dash="dot"), marker=dict(size=7),
    ), secondary_y=True)
    fig.add_hline(y=0, line_dash="dash", line_color=GREY, secondary_y=True)
    fig.update_layout(
        title="Nominal income rose, but purchasing-power gains were uneven",
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Median household income (SGD/month)", secondary_y=False)
    fig.update_yaxes(title_text="Real income change (%)", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    worst = view.loc[view["m2_real_income_change_pct"].idxmin()]
    insight_block(
        analysis=(
            "- Median household income rises in dollar terms, which can make the "
            "situation look healthier than it feels.\n"
            f"- The weakest year in the selected window is **{int(worst['year'])}**, "
            f"where real income change was **{worst['m2_real_income_change_pct']:.1f}%**.\n"
            "- This supports my notebook finding: nominal income is not enough; "
            "real income is the better pressure signal."
        ),
        explanation=(
            "Real income adjusts for inflation. When that line is low or negative, "
            "households can feel squeezed even though their monthly income number "
            "has technically increased."
        ),
        audience="NTUC, MTI.",
        recommendation=(
            "Use real-income change, not just median income, when negotiating wage "
            "guidelines or assessing whether workers are keeping up with prices."
        ),
    )


def chart_2022_squeeze() -> None:
    st.subheader("The 2022 Squeeze: Inflation Growth vs Income Growth")
    view = filter_years(m2_all).dropna(
        subset=["m2_food_cpi_growth_pct", "m2_income_growth_pct"]
    )
    if view.empty:
        st.warning("No growth-rate data in the selected year range.")
        return

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=view["year"], y=view["m2_food_cpi_growth_pct"],
        name="Food CPI growth (%)", marker_color=RED,
    ))
    fig.add_trace(go.Bar(
        x=view["year"], y=view["m2_income_growth_pct"],
        name="Median income growth (%)", marker_color=GREEN,
    ))
    if 2022 >= view["year"].min() and 2022 <= view["year"].max():
        fig.add_vline(
            x=2022, line_dash="dash", line_color=ORANGE,
            annotation_text="2022 squeeze", annotation_position="top",
        )
    fig.update_layout(
        title="Food inflation growth versus median household income growth",
        xaxis_title="Year", yaxis_title="Year-on-year change (%)",
        barmode="group", template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    y2022 = m2_all[m2_all["year"] == 2022].iloc[0]
    insight_block(
        analysis=(
            f"- In **2022**, All Items CPI growth was "
            f"**{y2022['m2_cpi_growth_pct']:.1f}%** and median income growth was "
            f"**{y2022['m2_income_growth_pct']:.1f}%**.\n"
            f"- But real income change was only **{y2022['m2_real_income_change_pct']:.1f}%**, "
            "which is why this year looks like the clearest squeeze year.\n"
            "- The chart shows the stress better than a simple income line because it "
            "compares the speed of price growth against the speed of income growth."
        ),
        explanation=(
            "When prices and income rise at nearly the same pace, households do not "
            "gain much breathing room. The 2022 line is the bridge between my EDA and "
            "the final Streamlit message."
        ),
        audience="MTI, NTUC, social service policy analysts.",
        recommendation=(
            "Treat high-inflation years as trigger points for targeted temporary "
            "support, especially food vouchers or wage guidance for lower-paid workers."
        ),
    )


def chart_gdp_vs_income() -> None:
    st.subheader("GDP Per Capita Looks Better Than Household Income Per Person")
    view = filter_years(m2_all)
    if view.empty:
        st.warning("No data in the selected year range.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_gdp_per_capita_sgd"],
        name="GDP per capita", mode="lines+markers",
        line=dict(color=ORANGE, width=3), marker=dict(size=7),
    ))
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_income_per_person_annual_sgd"],
        name="Estimated income per person", mode="lines+markers",
        line=dict(color=BLUE, width=3), marker=dict(size=7),
    ))
    fig.update_layout(
        title="Headline GDP per capita sits far above estimated household income per person",
        xaxis_title="Year", yaxis_title="SGD per year",
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    last = view.iloc[-1]
    insight_block(
        analysis=(
            f"- In **{int(last['year'])}**, GDP per capita was about "
            f"**SGD {last['m2_gdp_per_capita_sgd']:,.0f}**, while estimated annual "
            f"income per person from median household income was about "
            f"**SGD {last['m2_income_per_person_annual_sgd']:,.0f}**.\n"
            "- This supports the EDA's headline prosperity gap: Singapore can look "
            "rich in GDP terms while households feel less comfortable.\n"
            "- Important caveat: this does not prove elite earners alone caused the "
            "gap. That would need income decile or quintile data."
        ),
        explanation=(
            "GDP per capita is an average of national output, not the same thing as "
            "what a median household can spend. Comparing both prevents the dashboard "
            "from over-reading headline prosperity."
        ),
        audience="MTI, social service policy analysts.",
        recommendation=(
            "Pair GDP reporting with household-income and real-income indicators so "
            "policy discussions do not treat national growth as household comfort."
        ),
    )


def chart_gap_and_gini() -> None:
    st.subheader("GDP-Income Gap With Inequality Context")
    view = filter_years(m2_all)
    if view.empty:
        st.warning("No data in the selected year range.")
        return

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_gdp_vs_income_gap_x"],
        name="GDP vs income gap", mode="lines+markers",
        line=dict(color=ORANGE, width=3), marker=dict(size=7),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=view["year"], y=view["m2_gini_coefficient"],
        name="Gini coefficient", mode="lines+markers",
        line=dict(color=GREY, width=3, dash="dot"), marker=dict(size=7),
    ), secondary_y=True)
    if 2022 >= view["year"].min() and 2022 <= view["year"].max():
        fig.add_vline(x=2022, line_dash="dash", line_color=RED,
                      annotation_text="gap peak", annotation_position="top")
    fig.update_layout(
        title="GDP-income gap peaked around the inflation pressure period",
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="GDP per capita / income per person gap (x)", secondary_y=False)
    fig.update_yaxes(title_text="Gini coefficient", secondary_y=True)
    st.plotly_chart(fig, use_container_width=True)

    peak = m2_all.loc[m2_all["m2_gdp_vs_income_gap_x"].idxmax()]
    insight_block(
        analysis=(
            f"- The GDP-income gap peaks in **{int(peak['year'])}** at about "
            f"**{peak['m2_gdp_vs_income_gap_x']:.2f}x**.\n"
            "- Gini trends downward overall in this dataset, so I should not claim "
            "that inequality simply got worse every year.\n"
            "- The safer finding is that GDP can overstate household comfort, and "
            "the 2022 pressure year deserves attention."
        ),
        explanation=(
            "This chart keeps the GDP discussion honest. It supports a prosperity-gap "
            "argument, but it avoids overclaiming that elite earners alone explain the "
            "whole pattern."
        ),
        audience="MTI, social service policy analysts, NTUC.",
        recommendation=(
            "Add lower-income decile or quintile income data in future work. That would "
            "let policymakers test whether support should be aimed specifically at the "
            "bottom-income households rather than the broad median."
        ),
    )


def references_section() -> None:
    with st.expander("References & data sources"):
        st.markdown(
            """
**Data files used**

1. `data/processed/master_clean.csv` - merged yearly dataset from the group notebook.
2. `data/processed/cpi_monthly.csv` - CPI side-table prepared for Member 2's inflation analysis.

**Original source families**

3. Department of Statistics Singapore (SingStat), Consumer Price Index series.
4. Department of Statistics Singapore (SingStat), household employment income indicators.
5. Department of Statistics Singapore (SingStat), GDP per capita and Gini coefficient indicators.
"""
        )


st.title("Member 2 - Cost of Living & Inflationary Pressures")
st.markdown(
    """
My section checks whether household income has really kept up with inflation.
The EDA showed a sharper story than just "prices went up": food prices rose,
real income growth was uneven, and GDP per capita can make Singapore look more
comfortable than a median household actually feels.

**Hypothesis:** while median household income has risen, essential inflation and
the headline GDP-income gap create financial pressure that prosperity numbers
can hide.

**My five charts** follow that story from food prices, to real income, to the
2022 squeeze, and finally to the GDP-income gap. Pick one chart from the
sidebar to explore it.
"""
)

CHARTS = {
    "1. Food CPI vs All Items CPI": chart_cpi_food_vs_all,
    "2. Income vs Real Income Change": chart_income_vs_real_change,
    "3. The 2022 Squeeze": chart_2022_squeeze,
    "4. GDP vs Household Income": chart_gdp_vs_income,
    "5. GDP-Income Gap + Gini": chart_gap_and_gini,
}

st.sidebar.header("Member 2 - Cost of Living")
st.sidebar.caption("Choose one of my five charts:")
selection = st.sidebar.radio("My charts", list(CHARTS.keys()), label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.caption("Year filter (applies to the chart on screen):")
st.session_state["m2_year_range"] = st.sidebar.slider(
    "Year range",
    min_value=int(m2_all["year"].min()),
    max_value=int(m2_all["year"].max()),
    value=(int(m2_all["year"].min()), int(m2_all["year"].max())),
    step=1,
)

st.divider()
CHARTS[selection]()
st.divider()
references_section()
