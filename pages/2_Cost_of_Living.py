from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Cost of Living", layout="wide")

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
    st.subheader("Food CPI vs Overall CPI")
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
        title="Food prices rose faster than overall prices",
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
            f"- All Items CPI rose by **{all_change:.1f} index points** in the "
            "same years, so food is not just a random category I picked.\n"
            "- I focused on Food CPI because grocery spending is something families "
            "cannot really skip."
        ),
        explanation=(
            "This chart is my starting point. Food is a basic cost, so when this "
            "line rises faster than overall CPI, it helps explain why people can "
            "feel squeezed even if the economy looks okay."
        ),
        audience="MTI, NTUC, social service policy analysts.",
        recommendation=(
            "Track Food CPI separately when planning cost-of-living help. If food "
            "is the part rising fastest, support should focus more on essentials."
        ),
    )


def chart_income_vs_real_change() -> None:
    st.subheader("Income Rose, But Real Income Was Uneven")
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
        title="Income rose, but real income did not rise smoothly",
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
            "- Median household income goes up in dollars, so at first glance it "
            "looks like households are doing fine.\n"
            f"- The weakest year in the selected window is **{int(worst['year'])}**, "
            f"where real income change was **{worst['m2_real_income_change_pct']:.1f}%**.\n"
            "- This is why I do not want to look at income alone. Real income gives "
            "a better idea of whether people actually feel better off."
        ),
        explanation=(
            "Real income adjusts for inflation. If this line is weak, then a higher "
            "salary may not mean much because prices have also gone up."
        ),
        audience="NTUC, MTI.",
        recommendation=(
            "Use real-income change when discussing wages, not just the raw income "
            "number. It is closer to what workers actually feel."
        ),
    )


def chart_2022_squeeze() -> None:
    st.subheader("The 2022 Squeeze")
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
        title="Food inflation growth vs median income growth",
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
            "so households did not get much breathing room.\n"
            "- This is the clearest year for my argument because prices were moving "
            "fast while real income barely improved."
        ),
        explanation=(
            "This chart is basically my main evidence. It shows why just saying "
            "\"income went up\" is not enough. The timing of inflation matters too."
        ),
        audience="MTI, NTUC, social service policy analysts.",
        recommendation=(
            "In years like 2022, MTI and NTUC could react faster with temporary food "
            "support or stronger wage guidance for lower-paid workers."
        ),
    )


def chart_gdp_vs_income() -> None:
    st.subheader("GDP Looks Better Than Household Income")
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
        title="GDP per capita is far above estimated household income per person",
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
            "- This supports my EDA point: Singapore can look very rich from GDP, "
            "but that does not mean the median household feels rich.\n"
            "- I am not claiming this proves elite earners caused the whole gap. "
            "For that, I would need income data by income group."
        ),
        explanation=(
            "GDP per capita is an average national number. It is useful, but it is "
            "not the same as what a normal household can spend each month."
        ),
        audience="MTI, social service policy analysts.",
        recommendation=(
            "When reporting economic progress, show GDP together with household "
            "income and real income. Otherwise the cost pressure can be hidden."
        ),
    )


def chart_gap_and_gini() -> None:
    st.subheader("GDP-Income Gap and Gini")
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
        title="GDP-income gap peaked around 2022",
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
            "- Gini trends downward overall in this dataset, so I should not say "
            "inequality got worse every year.\n"
            "- The safer point is that GDP can make things look better than they "
            "feel for households, especially around 2022."
        ),
        explanation=(
            "This chart is here so I do not overclaim. It supports a GDP-versus-"
            "household-income gap, but it does not prove exactly who gained the most."
        ),
        audience="MTI, social service policy analysts, NTUC.",
        recommendation=(
            "For a better version of this analysis, add income data by income group. "
            "That would show whether lower-income households are falling behind."
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


st.title("Cost of Living & Inflationary Pressures")
st.markdown("**Author:** Chew David Zhi Heng")
st.markdown(
    """
My section checks whether household income has really kept up with inflation.
My EDA pointed me to a simple story: food prices went up, real income growth
was not steady, and GDP per capita can make Singapore look richer than what a
normal household may actually feel.

**Hypothesis:** while median household income has risen, essential inflation and
the GDP-income gap can still create financial pressure.

**My five charts** follow that story from food prices, to real income, to the
2022 squeeze, and then to the GDP-income gap. Pick one chart from the sidebar.
"""
)

CHARTS = {
    "1. Food CPI vs All Items CPI": chart_cpi_food_vs_all,
    "2. Income vs Real Income Change": chart_income_vs_real_change,
    "3. The 2022 Squeeze": chart_2022_squeeze,
    "4. GDP vs Household Income": chart_gdp_vs_income,
    "5. GDP-Income Gap + Gini": chart_gap_and_gini,
}

st.sidebar.header("Cost of Living")
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
