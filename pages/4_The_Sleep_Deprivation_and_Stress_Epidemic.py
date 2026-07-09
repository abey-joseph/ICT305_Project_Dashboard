"""
Member 4 - The Sleep Deprivation & Stress Epidemic
Name - Lai Soo Seng
Student ID - 35535456
==================================================

Hypothesis
----------
Singapore's world-class wealth and high "happy city" ranking mask a wellbeing
problem visible in the World Happiness Report data: national happiness peaked
in 2014 and never recovered, sits below every genuine peer "happy city", and
is held back by the social side of wellbeing rather than by money or health.

Target audiences
----------------
- Ministry of Health (MOH) and Health Promotion Board (HPB)
- Ministry of Social and Family Development (MSF)
- Employers and corporate wellbeing teams

Structure of this page
----------------------
The sidebar lists my seven charts. Pick one and only that chart is shown, with
its own data-analysis insights and a recommendation. Interactivity:
- A global year-range filter in the sidebar feeds the time-series charts.
- Chart 1 has a wellbeing-dimension multiselect.
- Chart 3 lets you pick a peer country to benchmark against.
A References section with clickable sources sits at the bottom of the page.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Sleep & Happiness", layout="wide")

# Shared palette so every chart looks like it belongs with the rest of the team.
BLUE = "#2A6FBB"
RED = "#D1495B"
GREEN = "#3C896D"
GREY = "#8A8D91"
PURPLE = "#B07AA1"

# Work out the project root from this file's location, so data paths keep
# working no matter which folder Streamlit is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = PROJECT_ROOT / "data" / "processed"

# The time-series charts share one global year filter.
YEAR_MIN, YEAR_MAX = 2010, 2025
YR = (YEAR_MIN, YEAR_MAX)   # overwritten from the sidebar before a chart is drawn

# WHR ranking column names (confirmed from the 2024 snapshot)
RANK_COUNTRY = "Country name"
RANK_LADDER = "Ladder score"
SUB_SCORES = [
    "Log GDP per capita", "Healthy life expectancy",
    "Social support", "Freedom to make life choices", "Generosity",
]
PEER_COUNTRIES = ["Finland", "Denmark", "Switzerland", "Sweden",
                  "Norway", "South Korea", "Singapore"]


# ---------------------------------------------------------------------------
# Data loading (cached so each CSV is read once and reused)
# ---------------------------------------------------------------------------
@st.cache_data
def load_master() -> pd.DataFrame:
    """Yearly Singapore master table (we use the m4_ and a few cross-member columns)."""
    return pd.read_csv(PROC_DIR / "master_clean.csv")


@st.cache_data
def load_rank() -> pd.DataFrame:
    """WHR 2024 snapshot ranking (143 countries, with sub-scores)."""
    return pd.read_csv(PROC_DIR / "whr_2024_ranking.csv")


@st.cache_data
def load_panel() -> pd.DataFrame:
    """WHR full multi-country yearly panel."""
    return pd.read_csv(PROC_DIR / "whr_panel_full.csv")


@st.cache_data
def load_sleep() -> pd.DataFrame:
    """Global sleep-health dataset (no Singapore rows)."""
    return pd.read_csv(PROC_DIR / "sleep_health_global.csv")


# Friendly labels for the M4 wellbeing dimensions
DIMENSIONS = {
    "m4_life_ladder":     "Life Ladder (overall happiness)",
    "m4_social_support":  "Social support",
    "m4_freedom_score":   "Freedom to make life choices",
    "m4_positive_affect": "Positive affect",
    "m4_negative_affect": "Negative affect",
}

# Friendly labels for the cross-member correlation chart
CHAIN_COLS = {
    "m1_mean_weekly_hours":           "Working hours (M1)",
    "m2_median_household_income_sgd": "Household income (M2)",
    "m2_cpi_all_items":               "Cost of living / CPI (M2)",
    "m3_hdb_resale_price_index":      "Housing price index (M3)",
    "m4_life_ladder":                 "Happiness (M4)",
}


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def clamp(df: pd.DataFrame, col: str = "year") -> pd.DataFrame:
    """Keep only rows whose year falls inside the global filter YR."""
    return df[(df[col] >= YR[0]) & (df[col] <= YR[1])]


def insight_block(insights_md: str, recommendation: str, audiences: str) -> None:
    """Same insight / recommendation / audience footer under every chart."""
    st.markdown("#### Data analysis insights")
    st.markdown(insights_md)
    st.markdown("#### Recommendation")
    st.success(recommendation)
    st.caption(f"**Links to target audience:** {audiences}")


# ---------------------------------------------------------------------------
# CHART 1 - The Peak We Never Returned To (Life Ladder time series)
# ---------------------------------------------------------------------------
def chart_hook() -> None:
    st.header("Chart 1 - The Peak We Never Returned To")
    st.markdown(
        "Singapore's national happiness (World Happiness *Life Ladder*) over time. "
        "Use the **year-range filter in the sidebar**, and the **dimension picker "
        "below** to add sub-scores like social support or freedom."
    )

    master = clamp(load_master())
    if master.empty:
        st.warning("No data in the selected year range. Widen the filter.")
        return

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 1 control")
    chosen = st.sidebar.multiselect(
        "Wellbeing dimensions",
        options=list(DIMENSIONS.keys()),
        default=["m4_life_ladder"],
        format_func=lambda k: DIMENSIONS[k],
    )
    if not chosen:
        st.info("Select at least one dimension in the sidebar to draw the chart.")
        return

    fig = go.Figure()
    palette = [RED, BLUE, GREEN, GREY, PURPLE]
    for i, col in enumerate(chosen):
        d = master[["year", col]].dropna()
        fig.add_trace(
            go.Scatter(
                x=d["year"], y=d[col], name=DIMENSIONS[col],
                mode="lines+markers",
                line=dict(color=palette[i % len(palette)], width=3),
                marker=dict(size=7),
            )
        )

    if "m4_life_ladder" in chosen:
        ll = master[["year", "m4_life_ladder"]].dropna()
        if not ll.empty:
            peak_val = ll["m4_life_ladder"].max()
            peak_year = int(ll.loc[ll["m4_life_ladder"].idxmax(), "year"])
            fig.add_hline(
                y=peak_val, line=dict(color=GREY, width=1, dash="dash"),
                annotation_text=f"{peak_year} peak = {peak_val:.2f}",
                annotation_position="top left",
            )

    fig.update_layout(
        title="Singapore's happiness peaked in 2014 and has not recovered since",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Score", showgrid=True, gridcolor="#E8E8E8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- Singapore's Life Ladder **peaked at 7.06 in 2014** and has not "
            "returned to that level since, falling to **6.03 in 2016** and sitting "
            "at **6.65 in 2023**.\n"
            "- The dashed line marks the 2014 peak: no later year climbs back to it.\n"
            "- This happened while the economy kept growing, so rising national "
            "wealth did not translate into rising happiness. Survey gaps in 2012 "
            "and 2020 appear as breaks in the line."
        ),
        recommendation=(
            "Track a national wellbeing indicator alongside GDP and income, so a "
            "stalled happiness trend is monitored in its own right rather than "
            "averaged away inside a 'happy city' ranking."
        ),
        audiences="Ministry of Health (MOH), Health Promotion Board (HPB), corporate wellbeing teams",
    )


# ---------------------------------------------------------------------------
# CHART 2 - Incomes Keep Rising, Happiness Does Not Follow (dual-axis)
# ---------------------------------------------------------------------------
def chart_bridge() -> None:
    st.header("Chart 2 - Incomes Keep Rising, Happiness Does Not Follow")
    st.markdown(
        "Median household income (Member 2) against Singapore's happiness score. "
        "Use the **year-range filter in the sidebar**. The two lines share a "
        "timeline but sit on different axes, so watch the shapes, not the heights."
    )

    master = clamp(load_master())
    d = master[["year", "m2_median_household_income_sgd", "m4_life_ladder"]].dropna()
    if d.empty:
        st.warning("No data in the selected year range. Widen the filter.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=d["year"], y=d["m2_median_household_income_sgd"],
            name="Median household income (SGD)", mode="lines+markers",
            line=dict(color=GREEN, width=3), marker=dict(size=7), yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=d["year"], y=d["m4_life_ladder"],
            name="Life Ladder score", mode="lines+markers",
            line=dict(color=RED, width=3), marker=dict(size=7), yaxis="y2",
        )
    )

    ll = d[["year", "m4_life_ladder"]].dropna()
    peak_year = int(ll.loc[ll["m4_life_ladder"].idxmax(), "year"])
    fig.add_vline(
        x=peak_year, line=dict(color=GREY, width=1, dash="dash"),
        annotation_text=f"Happiness peaks ({peak_year})", annotation_position="top",
    )

    fig.update_layout(
        title="Incomes keep rising, happiness does not follow",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Median household income (SGD)", showgrid=True,
                   gridcolor="#E8E8E8"),
        yaxis2=dict(title="Life Ladder score (0-10)", overlaying="y", side="right",
                    showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- Median household income rose from around **SGD 6,300 (2010) to nearly "
            "SGD 11,000 (2023)**, while happiness peaked in 2014 and diverged "
            "downward after it.\n"
            "- The two series track loosely until 2014, then clearly split apart.\n"
            "- This is a **divergence, not proof of cause**: the chart shows income "
            "and happiness moving in opposite directions, not that income lowered "
            "happiness."
        ),
        recommendation=(
            "Do not read rising income or GDP as a proxy for a happier population. "
            "Pair economic dashboards with a tracked wellbeing measure so the gap is "
            "flagged early. For employers, recognise that pay rises alone do not lift "
            "engagement; invest in workload and autonomy too."
        ),
        audiences="Ministry of Health (MOH), Ministry of Trade and Industry (MTI), employers and HR leaders",
    )


# ---------------------------------------------------------------------------
# CHART 3 - Singapore vs Peer "Happy Cities" (interactive peer picker)
# ---------------------------------------------------------------------------
def chart_peer() -> None:
    st.header("Chart 3 - Ranked \"Happy\", Yet Near the Bottom")
    st.markdown(
        "Singapore benchmarked against the countries that stand in for the world's "
        "\"happiest cities\" (WHR 2024, three-year average). Use the **peer picker "
        "below** to highlight one country against Singapore."
    )

    rank = load_rank()
    peers = rank[rank[RANK_COUNTRY].isin(PEER_COUNTRIES)].copy()
    peers = peers.sort_values(RANK_LADDER, ascending=True)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 3 control")
    others = [c for c in peers[RANK_COUNTRY] if c != "Singapore"]
    highlight = st.sidebar.selectbox("Highlight one peer vs Singapore",
                                     ["(show all)"] + others)

    # Colour: Singapore red, highlighted peer blue, rest grey
    colors = []
    for c in peers[RANK_COUNTRY]:
        if c == "Singapore":
            colors.append(RED)
        elif highlight != "(show all)" and c == highlight:
            colors.append(BLUE)
        else:
            colors.append("#C9D6E3" if highlight != "(show all)" else "#9bb8d3")

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=peers[RANK_LADDER], y=peers[RANK_COUNTRY], orientation="h",
            marker_color=colors,
            text=[f"{v:.2f}" for v in peers[RANK_LADDER]],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Singapore sits near the bottom of its peer \"happy cities\"",
        xaxis=dict(title="Ladder score (0-10, WHR 2024, 3-year average)",
                   range=[0, 8.5], showgrid=True, gridcolor="#E8E8E8"),
        yaxis=dict(title=""),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    sg_score = peers.loc[peers[RANK_COUNTRY] == "Singapore", RANK_LADDER].values[0]
    top_score = peers[RANK_LADDER].max()
    insight_block(
        insights_md=(
            f"- Singapore sits near the bottom of the group at **{sg_score:.2f}**, "
            f"ahead of only South Korea, while **Finland leads at {top_score:.2f}**.\n"
            f"- The gap to the top of the group is about **{top_score - sg_score:.2f} "
            "points**.\n"
            "- Placed next to the specific cities the \"happy city\" narrative "
            "celebrates, Singapore is clearly behind them rather than among them. "
            "This score is a three-year average, so it will not exactly match the "
            "single-year value in Chart 1."
        ),
        recommendation=(
            "Be cautious about leaning on aggregate \"happy city\" rankings, since a "
            "flattering headline can hide that Singapore sits below true peer "
            "leaders. Benchmark on wellbeing, not only economic competitiveness."
        ),
        audiences="Ministry of Health (MOH), national policy planners, multinational employers",
    )


# ---------------------------------------------------------------------------
# CHART 4 - Winning on Money, Losing on Connection (sub-score breakdown)
# ---------------------------------------------------------------------------
def chart_subscore() -> None:
    st.header("Chart 4 - Winning on Money, Losing on Connection")
    st.markdown(
        "The happiness score broken into its components: Singapore versus the "
        "average of the peer \"happy cities\". Singapore leads on the material "
        "factors but not on the social ones."
    )

    rank = load_rank()
    peers = rank[rank[RANK_COUNTRY].isin(PEER_COUNTRIES)].copy()
    sg_row = peers[peers[RANK_COUNTRY] == "Singapore"][SUB_SCORES].iloc[0]
    peer_avg = peers[peers[RANK_COUNTRY] != "Singapore"][SUB_SCORES].mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=SUB_SCORES, y=peer_avg.values, name='Peer "happy cities" average',
        marker_color="#9bb8d3",
        text=[f"{v:.2f}" for v in peer_avg.values], textposition="outside",
    ))
    fig.add_trace(go.Bar(
        x=SUB_SCORES, y=sg_row.values, name="Singapore",
        marker_color=RED,
        text=[f"{v:.2f}" for v in sg_row.values], textposition="outside",
    ))
    fig.update_layout(
        title="Singapore leads on money and health, but not on the social factors",
        barmode="group",
        xaxis=dict(title=""),
        yaxis=dict(title="Contribution to Ladder score", showgrid=True,
                   gridcolor="#E8E8E8"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=80), template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- Singapore's advantage is material: its **Log GDP per capita (2.12) is "
            "the highest in the group**, and Healthy life expectancy (0.77) is also "
            "above the peer average.\n"
            "- But it does not lead on the social factors. On **Social support "
            "(1.36 vs 1.45), Freedom (0.74 vs 0.78), and Generosity (0.17 vs 0.18)**, "
            "Singapore sits marginally below the peer average.\n"
            "- The gaps are small but consistent: Singapore builds a large lead on "
            "money, gives it up on the social dimensions, and ends up lower overall. "
            "The material advantage is not being converted into wellbeing."
        ),
        recommendation=(
            "Direct wellbeing effort at the social dimensions where Singapore only "
            "matches or slightly trails its peers, not the material ones where it "
            "already leads. For employers, strong pay has diminishing returns if team "
            "support and autonomy do not match it; invest in belonging and genuine "
            "choice."
        ),
        audiences="Ministry of Health (MOH), Ministry of Social and Family Development (MSF), corporate wellbeing teams",
    )


# ---------------------------------------------------------------------------
# CHART 5 - Pressure Without a Same-Year Echo (scatter, null result)
# ---------------------------------------------------------------------------
def chart_stress() -> None:
    st.header("Chart 5 - Pressure Without a Same-Year Echo")
    st.markdown(
        "Do the pressures from Member 1 (working hours) and Member 3 (housing) line "
        "up with happiness in the same year? Use the **selector below** to switch "
        "between the two."
    )

    master = load_master()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 5 control")
    which = st.sidebar.radio(
        "Pressure to plot",
        ["Working hours (M1)", "Housing price index (M3)"],
    )
    col = "m1_mean_weekly_hours" if which.startswith("Working") else "m3_hdb_resale_price_index"

    d = master[["year", col, "m4_life_ladder"]].dropna()
    r = np.corrcoef(d[col], d["m4_life_ladder"])[0, 1]

    fig = px.scatter(
        d, x=col, y="m4_life_ladder", color="year",
        color_continuous_scale="Viridis",
        labels={col: which, "m4_life_ladder": "Life Ladder score (0-10)",
                "year": "Year"},
    )
    fig.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
    fig.update_layout(
        title=f"{which} vs happiness — Pearson r = {r:.2f} (n = {len(d)} years)",
        template="plotly_white",
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- The correlations are **weak and positive (r = 0.23 for hours, r = 0.14 "
            "for housing)** across 12 years, which means there is **no clear "
            "year-to-year link** between these pressures and happiness.\n"
            "- The points are scattered with no obvious trend.\n"
            "- This is a useful **null result**: the pressures from Members 1 and 3 "
            "do not map onto happiness in a simple same-year way. If anything, it "
            "supports the idea that they act slowly and cumulatively rather than "
            "within the same year."
        ),
        recommendation=(
            "Do not read any single year's numbers as proof that pressure is or is "
            "not affecting wellbeing. Because the link is weak and likely lagged, "
            "wellbeing should be tracked over multiple years so slow-building effects "
            "are not dismissed."
        ),
        audiences="Ministry of Manpower (MOM), Ministry of Health (MOH), employers",
    )


# ---------------------------------------------------------------------------
# CHART 6 - The Global Sleep-Stress Pattern (context, no Singapore data)
# ---------------------------------------------------------------------------
def chart_sleep() -> None:
    st.header("Chart 6 - The Global Sleep-Stress Pattern")
    st.markdown(
        "A global sleep dataset with **no Singapore rows**, included as context for "
        "the \"stress\" theme. It shows how sleep varies by occupation worldwide, "
        "coloured by average stress. It is not a claim about Singapore."
    )

    sleep = load_sleep()
    occ = (sleep.groupby("Occupation")
           .agg(sleep=("Sleep Duration", "mean"),
                stress=("Stress Level", "mean"),
                n=("Person ID", "count"))
           .reset_index())
    occ = occ[occ["n"] >= 5].sort_values("sleep")

    fig = px.bar(
        occ, x="sleep", y="Occupation", orientation="h",
        color="stress", color_continuous_scale="Reds",
        labels={"sleep": "Average sleep duration (hours)",
                "stress": "Avg stress level", "Occupation": ""},
        text=occ["sleep"].map(lambda v: f"{v:.1f}h"),
    )
    fig.add_vline(x=7, line=dict(color=GREY, width=1, dash="dash"),
                  annotation_text="7 hrs", annotation_position="top")
    fig.update_traces(textposition="outside")
    fig.update_layout(
        title="Global pattern: several high-stress occupations sleep under 7 hours",
        template="plotly_white",
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Global sample (n=374), no Singapore data. Context only, not a Singapore claim.")

    insight_block(
        insights_md=(
            "- Across occupations worldwide, several higher-stress roles report "
            "shorter average sleep, with the most demanding jobs sitting **below the "
            "7-hour mark**.\n"
            "- This dataset has **no Singapore data**, so it cannot say anything about "
            "Singapore specifically.\n"
            "- It illustrates the general pattern behind the \"sleep and stress\" "
            "theme: demanding, high-pressure work tends to come with less rest."
        ),
        recommendation=(
            "As global context, this should not drive local policy on its own. It "
            "supports a general point: the stress behind the happiness gap has a "
            "physical dimension, and reducing workload pressure is one lever that "
            "plausibly touches both rest and wellbeing."
        ),
        audiences="Health Promotion Board (HPB), employers and corporate wellbeing teams",
    )


# ---------------------------------------------------------------------------
# CHART 7 - The Pressure Chain in One View (cross-member correlation heatmap)
# ---------------------------------------------------------------------------
def chart_chain() -> None:
    st.header("Chart 7 - The Pressure Chain in One View")
    st.markdown(
        "A correlation matrix tying together working hours (M1), cost of living and "
        "income (M2), housing (M3), and happiness (M4). It summarises the whole "
        "section and shows how the pressures relate to one another and to happiness."
    )

    master = load_master()
    chain = master[["year"] + list(CHAIN_COLS.keys())].dropna()
    corr = chain[list(CHAIN_COLS.keys())].corr()
    labels = [CHAIN_COLS[c] for c in corr.columns]

    fig = px.imshow(
        corr.values, x=labels, y=labels,
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        text_auto=".2f", aspect="auto",
    )
    fig.update_layout(
        title="How the pressures and happiness move together",
        template="plotly_white",
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"Based on {len(chain)} shared years. Correlations are associations, not proof of cause.")

    insight_block(
        insights_md=(
            "- The strongest links are **among the economic variables themselves**: "
            "working hours, income, cost of living, and housing all move tightly "
            "with each other, which is the pressure chain Members 1 to 3 describe.\n"
            "- **Happiness sits apart**: its correlation with each individual "
            "pressure is weak, consistent with the null result in Chart 5.\n"
            "- The economic pressures are clearly connected to one another, but none "
            "maps onto happiness in a simple same-year way. That gap between a "
            "tightly-linked economy and a flat wellbeing signal is what the \"happy "
            "city\" ranking hides."
        ),
        recommendation=(
            "Because the pressures are interlinked but only weakly and indirectly "
            "tied to happiness, wellbeing policy should be coordinated across labour, "
            "cost of living, and housing rather than treated in isolation, and "
            "tracked over time rather than judged by same-year correlations. This is "
            "where Member 5 takes over: the young, who fall hardest."
        ),
        audiences="Whole-of-government (cross-domain view), corporate strategy and wellbeing teams",
    )


# ---------------------------------------------------------------------------
# References (clickable sources), shown under every chart
# ---------------------------------------------------------------------------
def references() -> None:
    st.markdown("---")
    with st.expander("References & data sources (Charts 1-7)"):
        st.markdown(
            "- World Happiness Report (2024). *World Happiness Report 2024.* "
            "Wellbeing Research Centre, University of Oxford. "
            "[worldhappiness.report](https://worldhappiness.report/)\n"
            "- World Happiness Report (2024). *Life Ladder panel and country "
            "rankings* [Data set]. "
            "[worldhappiness.report/data](https://worldhappiness.report/data/)\n"
            "- *Sleep Health and Lifestyle Dataset* [Data set]. Kaggle. "
            "[kaggle.com](https://www.kaggle.com/datasets/uom190346a/sleep-health-and-lifestyle-dataset)\n"
            "- Department of Statistics Singapore. *Median monthly household income "
            "from work* [Data set]. SingStat. "
            "[singstat.gov.sg](https://www.singstat.gov.sg/)"
        )


# ---------------------------------------------------------------------------
# Chart registry + sidebar navigation
# ---------------------------------------------------------------------------
CHARTS = {
    "Chart 1 - The Peak We Never Returned To": chart_hook,
    "Chart 2 - Incomes Keep Rising, Happiness Does Not Follow": chart_bridge,
    "Chart 3 - Ranked Happy, Yet Near the Bottom": chart_peer,
    "Chart 4 - Winning on Money, Losing on Connection": chart_subscore,
    "Chart 5 - Pressure Without a Same-Year Echo": chart_stress,
    "Chart 6 - The Global Sleep-Stress Pattern": chart_sleep,
    "Chart 7 - The Pressure Chain in One View": chart_chain,
}

st.sidebar.header("Sleep & Happiness")
st.sidebar.caption("Choose one of my charts:")
selection = st.sidebar.radio("My charts", list(CHARTS.keys()), label_visibility="collapsed")

# Global year filter
st.sidebar.markdown("---")
st.sidebar.subheader("Year range")
YR = st.sidebar.slider(
    "Filter the time-series charts",
    min_value=YEAR_MIN, max_value=YEAR_MAX,
    value=(YEAR_MIN, YEAR_MAX),
)

st.title("Sleep Deprivation & Stress Epidemic")
st.markdown("**Author:** Lai Soo Seng")

# Draw the selected chart, then the shared references
CHARTS[selection]()
references()
