"""
Member 1 - Work-Life Balance & Overwork
Name - Joseph Abey
Student ID - 35720739
=======================================

Hypothesis
----------
Singapore's economic success masks a chronic culture of long working hours
that directly eats into happiness and leisure.

Target audiences
----------------
- Ministry of Manpower (MOM)
- Workplace Wellness Advocates
- Human Resource (HR) Policy Makers

Structure of this page
----------------------
The sidebar lists my eight charts. Pick one and only that chart is shown, with
its own data-analysis insights and a recommendation. Interactivity:
- A global year-range filter in the sidebar feeds the five time-series charts
  (1-5), so every one of them is interactive.
- Chart 3 has an age-band multiselect.
- Chart 7 (world map) has a colour-metric radio and a projection selector.
- Chart 8 (cross-country scatter) has trend-line and country-label toggles.
A References section with clickable sources sits at the bottom of the page.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Member 1 - Work-Life Balance", layout="wide")

# One shared palette so every chart on the page looks like it belongs together.
BLUE = "#2A6FBB"
RED = "#D1495B"
GREEN = "#3C896D"
GREY = "#8A8D91"

# Work out the project root from this file's location, so the data paths keep
# working no matter which folder Streamlit is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "member_1"
PROC_DIR = PROJECT_ROOT / "data" / "processed"

# The five time-series charts share one global year filter. The two global
# (cross-country) charts and the single-year bar chart ignore it.
YEAR_MIN, YEAR_MAX = 2010, 2025
YR = (YEAR_MIN, YEAR_MAX)   # overwritten from the sidebar before a chart is drawn


# ---------------------------------------------------------------------------
# Data loading
# @st.cache_data means each CSV is read once and reused. Without it, every
# click on the sidebar would re-read the files from disk and feel sluggish.
# ---------------------------------------------------------------------------
@st.cache_data
def load_hours() -> pd.DataFrame:
    """Mean usual weekly hours and % of workers doing 40+ hours (2010-2025)."""
    raw = pd.read_csv(RAW_DIR / "MOM_Usual_Hours_Worked_Annual.csv")
    # MOM ships this table sideways: one row per metric, years across the top.
    # Set the metric names as the index and transpose (.T) so we end up with the
    # normal shape - one row per year, one column per metric.
    tidy = raw.set_index("DataSeries").T.reset_index()
    tidy.columns = ["year", "mean_hours", "pct_40plus"]
    tidy["year"] = pd.to_numeric(tidy["year"], errors="coerce")
    for col in ["mean_hours", "pct_40plus"]:
        # 2025's "40+ hours" cell is the text "na", so coerce turns it into NaN
        # instead of crashing. Plotly just leaves a gap for it later.
        tidy[col] = pd.to_numeric(tidy[col], errors="coerce")
    return tidy.dropna(subset=["year"]).sort_values("year").reset_index(drop=True)


@st.cache_data
def load_happiness() -> pd.DataFrame:
    """National happiness (Life Ladder) from the shared master dataset."""
    # Happiness isn't my dataset - I borrow the one column I need from the team's
    # merged master file so Chart 2 can line it up against working hours.
    master = pd.read_csv(PROC_DIR / "master_yearly.csv")
    return master[["year", "m4_life_ladder"]].copy()


@st.cache_data
def load_participation() -> pd.DataFrame:
    """Resident labour force participation rate, long format."""
    df = pd.read_csv(RAW_DIR / "SingStat_Labour_Force_Participation_Rate.csv")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    return df.dropna(subset=["period", "value"])


@st.cache_data
def load_injury() -> pd.DataFrame:
    """Workplace fatal and non-fatal injury rates per 100,000 workers."""
    df = pd.read_csv(RAW_DIR / "SingStat_Workplace_Injury_Rate_Annual.csv")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    return df.dropna(subset=["period", "value"])


@st.cache_data
def load_unemployment() -> pd.DataFrame:
    """Resident unemployment rate, long format (Total, sex, age, qualification)."""
    # This one file holds every breakdown stacked in a "series" column, so both
    # Chart 5 (Total) and Chart 6 (by qualification) filter out of it.
    df = pd.read_csv(RAW_DIR / "SingStat_Resident_Unemployment_Rate_Annual.csv")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    return df.dropna(subset=["period", "value"])


@st.cache_data
def load_longterm_unemployment() -> pd.DataFrame:
    """Long-term unemployment rate, long format."""
    df = pd.read_csv(RAW_DIR / "SingStat_LongTerm_Unemployment_Rate_Annual.csv")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["period"] = pd.to_numeric(df["period"], errors="coerce")
    return df.dropna(subset=["period", "value"])


@st.cache_data
def load_country_context() -> pd.DataFrame:
    """International context: average annual working hours (OWID/OECD/ILO 2023)
    merged with national happiness and GDP (World Happiness Report 2024), for the
    52-economy comparison used by the map (Chart 7) and scatter (Chart 8)."""
    h = pd.read_csv(PROC_DIR / "working_hours_by_country.csv")
    whr = pd.read_csv(PROC_DIR / "whr_2024_ranking.csv")[
        ["Country name", "Ladder score", "Log GDP per capita"]]
    c = h.merge(whr, left_on="whr_name", right_on="Country name", how="left")
    c["weekly_hours"] = (c["annual_hours_2023"] / 52).round(1)
    return c


def clamp(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Keep only the rows whose year column falls inside the global filter YR."""
    return df[(df[col] >= YR[0]) & (df[col] <= YR[1])]


def insight_block(insights_md: str, recommendation: str, audiences: str) -> None:
    """The same insight / recommendation / audience footer under every chart,
    so the eight sections stay consistent and I only write the layout once."""
    st.markdown("#### Data analysis insights")
    st.markdown(insights_md)
    st.markdown("#### Recommendation")
    st.success(recommendation)
    st.caption(f"**Links to target audience:** {audiences}")


# ---------------------------------------------------------------------------
# CHART 1 - The Overwork Paradox (dual-axis line)
# ---------------------------------------------------------------------------
def chart_overwork_paradox() -> None:
    st.header("Chart 1 - The Overwork Paradox")
    st.markdown(
        "A dual-axis line chart tracking **mean usual weekly hours** (left) against "
        "the **share of workers doing 40+ hours** (right). Use the **year-range "
        "filter in the sidebar** to zoom the timeline."
    )

    hours = clamp(load_hours(), "year")
    if hours.empty:
        st.warning("No data in the selected year range. Widen the filter.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=hours["year"], y=hours["mean_hours"],
            name="Mean weekly hours", mode="lines+markers",
            line=dict(color=BLUE, width=3), marker=dict(size=7), yaxis="y",
        )
    )
    # Hours (~42) and the 40+ share (~83%) sit on completely different scales.
    # Putting the second line on its own right-hand axis (yaxis="y2") stops one
    # line from looking like a flat floor next to the other.
    fig.add_trace(
        go.Scatter(
            x=hours["year"], y=hours["pct_40plus"],
            name="% working 40+ hours", mode="lines+markers",
            line=dict(color=RED, width=3, dash="dot"), marker=dict(size=7), yaxis="y2",
        )
    )
    # A reference line at 38h (a typical full-time week overseas) gives the reader
    # something to judge "high" against instead of guessing.
    fig.add_hline(
        y=38, line=dict(color=GREY, width=1, dash="dash"),
        annotation_text="~38h international full-time norm", annotation_position="bottom right",
    )
    fig.update_layout(
        title="Working hours have eased slightly but stay high",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Mean weekly hours", showgrid=True, gridcolor="#E8E8E8",
                   range=[35, 48]),
        yaxis2=dict(title="% working 40+ hours", overlaying="y", side="right",
                    showgrid=False, range=[70, 92]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- Mean weekly hours fell from **46.6h (2010) to 41.6h (2024)** - real "
            "progress, but still **above the ~38h international full-time norm**.\n"
            "- The more telling line is the dotted one: even in 2024, **82.6% of "
            "workers still put in 40+ hours a week**, barely down from 88.3% in 2010.\n"
            "- So the headline improvement is thin. The *typical* Singapore worker "
            "still works a long full week - the overwork culture eased, it did not end."
        ),
        recommendation=(
            "Shift the policy target from average hours to the 40+ hour share. A "
            "concrete goal (e.g. cut the 40+ share below 75% by 2030) would attack "
            "the part of the distribution that actually drives burnout."
        ),
        audiences="Ministry of Manpower (MOM), Workplace Wellness Advocates",
    )


# ---------------------------------------------------------------------------
# CHART 2 - Long Hours vs National Happiness
# ---------------------------------------------------------------------------
def chart_hours_vs_happiness() -> None:
    st.header("Chart 2 - Long Hours vs National Happiness")
    st.markdown(
        "Working hours lined up against Singapore's national happiness score "
        "(World Happiness *Life Ladder*). Use the **year-range filter in the "
        "sidebar** - drag it to 2014-2023 to isolate the decline the hypothesis is "
        "built on."
    )

    hours = load_hours()
    happiness = load_happiness()
    # Left join keeps every year of hours; happiness only covers some years, so
    # dropna removes the years where we have no happiness score to compare.
    merged = hours.merge(happiness, on="year", how="left").dropna(subset=["m4_life_ladder"])
    view = clamp(merged, "year")
    if view.empty:
        st.warning("No data in the selected year range. Widen the filter.")
        return

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=view["year"], y=view["mean_hours"],
            name="Mean weekly hours", mode="lines+markers",
            line=dict(color=BLUE, width=3), marker=dict(size=7), yaxis="y",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=view["year"], y=view["m4_life_ladder"],
            name="Happiness (Life Ladder)", mode="lines+markers",
            line=dict(color=GREEN, width=3), marker=dict(size=8), yaxis="y2",
        )
    )
    # Label the happiest year currently in view. idxmax finds that row; if the
    # user slides past 2014 the label just hops to the next-highest peak.
    if view["m4_life_ladder"].notna().any():
        peak_row = view.loc[view["m4_life_ladder"].idxmax()]
        fig.add_annotation(
            x=peak_row["year"], y=peak_row["m4_life_ladder"], yref="y2",
            text=f"Peak {peak_row['m4_life_ladder']:.2f} ({int(peak_row['year'])})",
            showarrow=True, arrowhead=2, ax=0, ay=-30, font=dict(color=GREEN),
        )
    fig.update_layout(
        title=f"Working hours vs happiness, {int(view['year'].min())}-{int(view['year'].max())}",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Mean weekly hours", showgrid=True, gridcolor="#E8E8E8"),
        yaxis2=dict(title="Happiness (Life Ladder, 0-10)", overlaying="y",
                    side="right", showgrid=False),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    # Plain-English readout of the exact window the user picked (first vs last
    # year), so the takeaway updates live with the filter.
    first, last = view.iloc[0], view.iloc[-1]
    hrs_delta = last["mean_hours"] - first["mean_hours"]
    hap_delta = last["m4_life_ladder"] - first["m4_life_ladder"]
    st.info(
        f"In {int(first['year'])}-{int(last['year'])}, mean weekly hours changed by "
        f"**{hrs_delta:+.1f}h** while happiness changed by **{hap_delta:+.2f}** points."
    )

    insight_block(
        insights_md=(
            "- Across the full window, happiness **peaked at 7.06 in 2014 and never "
            "recovered**, settling around 6.3-6.7 in recent years.\n"
            "- Hours drifted down over the same period, yet happiness did **not** rise "
            "with it - so shorter average hours alone did not buy back wellbeing.\n"
            "- The stubborn 40+ hour share (Chart 1) is the more likely culprit: the "
            "workload intensity that squeezes leisure has not really changed."
        ),
        recommendation=(
            "Treat working-time reform as a wellbeing lever, not just a productivity "
            "one. Pilot right-to-disconnect and four-day-week trials, then track "
            "whether the happiness line responds - this chart is the monitoring tool."
        ),
        audiences="HR Policy Makers, Workplace Wellness Advocates",
    )


# ---------------------------------------------------------------------------
# CHART 3 - Working Later in Life (multi-line participation by age)
# ---------------------------------------------------------------------------
def chart_working_later() -> None:
    st.header("Chart 3 - Working Later in Life")
    st.markdown(
        "Resident labour force participation by age band. If overwork is structural, "
        "we expect older Singaporeans to keep working rather than retire. Pick which "
        "age bands to show in the sidebar."
    )

    part = load_participation()
    # Fixed colours so the legend stays stable whichever bands are picked.
    palette = {
        "Total Resident Participation Rate": GREY,
        "55 - 59 Years": BLUE,
        "60 - 64 Years": GREEN,
        "65 - 69 Years": RED,
    }

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 3 control")
    chosen = st.sidebar.multiselect(
        "Age bands to show", list(palette.keys()), default=list(palette.keys()),
    )
    if not chosen:
        st.warning("Pick at least one age band in the sidebar.")
        return

    view = clamp(part[part["series"].isin(chosen)], "period")
    fig = px.line(
        view, x="period", y="value", color="series",
        color_discrete_map=palette, markers=True,
        labels={"period": "Year", "value": "Participation rate (%)", "series": "Age band"},
        title="Older cohorts are staying in the workforce",
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        template="plotly_white", hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- Participation among **60-64 year-olds and 65-69 year-olds has risen "
            "sharply** over the decade, far faster than the overall rate.\n"
            "- The national total sits near ~68%, held up partly by these older bands "
            "rejoining or never leaving work.\n"
            "- This is consistent with an economy where working longer - across a "
            "career *and* across a week - is the norm rather than the exception."
        ),
        recommendation=(
            "Pair the push for longer working lives with age-friendly job redesign and "
            "phased-retirement options, so rising senior participation reflects choice "
            "and capacity rather than financial necessity."
        ),
        audiences="Ministry of Manpower (MOM), HR Policy Makers",
    )


# ---------------------------------------------------------------------------
# CHART 4 - The Human Cost (workplace injury rate, bar + line)
# ---------------------------------------------------------------------------
def chart_human_cost() -> None:
    st.header("Chart 4 - The Human Cost of a Hard-Working Economy")
    st.markdown(
        "Workplace injury rates per 100,000 workers: non-fatal injuries (bars, right "
        "axis) and fatal injuries (line, left axis). Filter the years in the sidebar."
    )

    inj = load_injury()
    fatal = clamp(inj[inj["series"] == "Workplace Fatal Injuries"], "period").sort_values("period")
    nonfatal = clamp(inj[inj["series"] == "Workplace Non-Fatal Injuries"], "period").sort_values("period")
    if fatal.empty and nonfatal.empty:
        st.warning("No injury data in the selected year range. Widen the filter.")
        return

    # Non-fatal injuries run in the hundreds while fatal ones are around 1 per
    # 100k. Bars for the big number, a line for the small one, each on its own
    # axis - otherwise the fatal line would be invisible flat against zero.
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=nonfatal["period"], y=nonfatal["value"],
            name="Non-fatal injuries", marker_color=BLUE, opacity=0.75, yaxis="y2",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=fatal["period"], y=fatal["value"],
            name="Fatal injuries", mode="lines+markers",
            line=dict(color=RED, width=3), marker=dict(size=8), yaxis="y",
        )
    )
    fig.update_layout(
        title="Injury rates per 100,000 workers",
        xaxis=dict(title="Year", showgrid=False, dtick=1),
        yaxis=dict(title="Fatal injuries (per 100k)", showgrid=False,
                   range=[0, 3], color=RED),
        yaxis2=dict(title="Non-fatal injuries (per 100k)", overlaying="y",
                    side="right", showgrid=True, gridcolor="#E8E8E8", color=BLUE),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- **Fatal injuries have trended down** from ~1.8 to ~1.2 per 100k - a "
            "genuine safety win worth acknowledging.\n"
            "- But **non-fatal injuries remain high (~320-360 per 100k)**, meaning "
            "physical strain on the workforce is still substantial.\n"
            "- Read alongside the long-hours picture, the risk is fatigue-related: "
            "tired workers are more injury-prone, so working time and safety are linked."
        ),
        recommendation=(
            "Target the non-fatal injury rate explicitly in workplace-safety KPIs, and "
            "test whether fatigue-management rules (rest breaks, overtime caps) in "
            "high-injury sectors move the bars down."
        ),
        audiences="Ministry of Manpower (MOM), Workplace Wellness Advocates",
    )


# ---------------------------------------------------------------------------
# CHART 5 - The Tight Labour Market (unemployment vs long-term unemployment)
# ---------------------------------------------------------------------------
def chart_tight_market() -> None:
    st.header("Chart 5 - The Tight Labour Market")
    st.markdown(
        "Resident unemployment vs long-term unemployment. A persistently tight market "
        "is part of *why* hours stay long - there is little slack. Filter the years "
        "in the sidebar."
    )

    unemp = load_unemployment()
    longterm = load_longterm_unemployment()
    # Pull just the "Total" line from each of the two files and rename its value
    # column so they don't collide when merged.
    ut = (unemp[unemp["series"] == "Total"][["period", "value"]]
          .rename(columns={"value": "unemp"}))
    lt = (longterm[longterm["series"] == "Total"][["period", "value"]]
          .rename(columns={"value": "longterm"}))
    # Outer join on year: the long-term file ends a year earlier, and an outer
    # join keeps that extra overall-unemployment year rather than dropping it.
    view = ut.merge(lt, on="period", how="outer").sort_values("period")
    view = clamp(view, "period")
    if view.empty:
        st.warning("No data in the selected year range. Widen the filter.")
        return

    fig = go.Figure()
    # Fill under the overall line so it reads as the "baseline" level, with the
    # long-term line sitting on top as the smaller, more worrying slice.
    fig.add_trace(
        go.Scatter(
            x=view["period"], y=view["unemp"], name="Overall unemployment",
            mode="lines+markers", line=dict(color=BLUE, width=3),
            fill="tozeroy", fillcolor="rgba(42,111,187,0.12)", marker=dict(size=7),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=view["period"], y=view["longterm"], name="Long-term unemployment",
            mode="lines+markers", line=dict(color=RED, width=3, dash="dot"),
            marker=dict(size=7),
        )
    )
    fig.update_layout(
        title="Unemployment stays low - a consistently tight market",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Rate (% of residents)", showgrid=True,
                   gridcolor="#E8E8E8", rangemode="tozero"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40), template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- Overall resident unemployment stayed in a **narrow ~2.7-4.1% band**, "
            "with only a brief COVID bump in 2020 - a structurally tight market.\n"
            "- **Long-term unemployment is very low (well under 1%)**: people who lose "
            "jobs generally find new ones quickly.\n"
            "- The flip side of near-full employment is thin labour slack, which keeps "
            "pressure on existing staff to absorb workload - feeding the long-hours "
            "culture the hypothesis describes."
        ),
        recommendation=(
            "Use tight-market periods to justify headcount and workload planning: when "
            "unemployment is this low, employers should expect to invest in retention "
            "and automation rather than lean harder on current employees' hours."
        ),
        audiences="Ministry of Manpower (MOM), HR Policy Makers",
    )


# ---------------------------------------------------------------------------
# CHART 6 - Who Bears the Burden (unemployment by qualification, latest year)
# ---------------------------------------------------------------------------
def chart_who_bears_burden() -> None:
    st.header("Chart 6 - Who Bears the Unemployment Burden")

    unemp = load_unemployment()
    # Keep only the "by qualification" rows out of the stacked series column.
    qual = unemp[unemp["series"].str.contains("Qualification", na=False)].copy()
    # Grab the newest year automatically instead of hard-coding it, so the chart
    # keeps working when next year's data is added.
    latest = int(qual["period"].max())
    view = qual[qual["period"] == latest].copy()
    view["label"] = view["series"].str.replace(
        "Highest Qualification Attained: ", "", regex=False
    )
    # Force the bars into education order (least -> most qualified). As a plain
    # Categorical with an explicit order, sort_values follows that order instead
    # of sorting the labels alphabetically.
    order = ["Below Secondary", "Secondary", "Post-Secondary (Non-Tertiary)",
             "Diploma & Professional Qualification", "Degree"]
    view["label"] = pd.Categorical(view["label"], categories=order, ordered=True)
    view = view.sort_values("label")

    st.markdown(
        f"Resident unemployment rate by highest qualification, **{latest}** - testing "
        "the assumption that more education means more job security. *(This chart is a "
        "single-year snapshot, so it is not affected by the year filter.)*"
    )

    # Colour only the worst-off group red and leave the rest blue, so the eye
    # lands straight on the group carrying the highest unemployment.
    top = view["value"].max()
    colors = [RED if v == top else BLUE for v in view["value"]]
    fig = go.Figure(
        go.Bar(
            x=view["label"].astype(str), y=view["value"],
            marker_color=colors, text=view["value"].map(lambda v: f"{v:.1f}%"),
            textposition="outside",
        )
    )
    fig.update_layout(
        title=f"Unemployment rate by qualification level ({latest})",
        xaxis=dict(title="Highest qualification attained"),
        yaxis=dict(title="Unemployment rate (%)", rangemode="tozero", gridcolor="#E8E8E8"),
        template="plotly_white", margin=dict(l=40, r=40, t=80, b=80),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            f"- In {latest}, **higher qualifications did not guarantee lower "
            "unemployment**: Diploma/Professional and Post-Secondary holders sit at "
            "the top of the range, and Degree holders are no lower than Secondary.\n"
            "- **Below-Secondary shows the lowest rate**, likely because those workers "
            "concentrate in hard-to-automate manual and service roles.\n"
            "- The takeaway: credential inflation means even well-qualified "
            "Singaporeans feel job insecurity - another pressure to over-work and "
            "prove value."
        ),
        recommendation=(
            "Direct reskilling and job-matching support at mid-tier qualification "
            "holders (Diploma / Post-Secondary), not only the low-skilled - they carry "
            "surprisingly high unemployment and are easy to overlook."
        ),
        audiences="HR Policy Makers, Workplace Wellness Advocates",
    )


# ---------------------------------------------------------------------------
# CHART 7 - Singapore in Global Context (world choropleth map)
# ---------------------------------------------------------------------------
def chart_global_map() -> None:
    st.header("Chart 7 - Singapore in Global Context")
    st.markdown(
        "A world map of **average annual working hours (2023)** across 52 economies. "
        "Switch the **colour metric** and **map projection** in the sidebar, and hover "
        "any country for its hours and happiness side by side."
    )

    ctry = load_country_context()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 7 controls")
    metric = st.sidebar.radio("Colour countries by", ["Working hours", "Happiness"])
    projection = st.sidebar.selectbox(
        "Map projection",
        ["natural earth", "equirectangular", "orthographic", "robinson"],
    )

    cmap = ctry.dropna(subset=["annual_hours_2023"]).copy()
    if metric == "Working hours":
        z, scale, cbar = cmap["annual_hours_2023"], "OrRd", "Annual<br>hours"
    else:
        cmap = cmap.dropna(subset=["Ladder score"])
        z, scale, cbar = cmap["Ladder score"], "YlGnBu", "Happiness"

    cd = cmap[["country", "annual_hours_2023", "weekly_hours", "Ladder score"]].values
    hover = ("<b>%{customdata[0]}</b><br>Annual hours: %{customdata[1]:,}"
             "<br>Weekly hours: %{customdata[2]}<br>Happiness: %{customdata[3]:.2f}"
             "<extra></extra>")

    fig = go.Figure(
        go.Choropleth(
            locations=cmap["iso3"], z=z, colorscale=scale, colorbar_title=cbar,
            customdata=cd, hovertemplate=hover,
            marker_line_color="white", marker_line_width=0.4,
        )
    )
    # Singapore is physically tiny, so a plain marker is easy to lose among the
    # large landmasses. Instead of a star we drop a red dot on its exact location
    # and attach a text callout carrying its real values, so it always stands out
    # and is labelled directly - the geo-map equivalent of the annotation used on
    # Chart 8. (A true add_annotation arrow can't be used here: annotations are not
    # anchored to lat/lon, so they would drift when the map projection is changed.)
    sg = cmap[cmap["country"] == "Singapore"]
    if not sg.empty:
        sg = sg.iloc[0]
        sg_label = (
            f"  Singapore - {int(sg['annual_hours_2023']):,} h/yr"
            f" | Happiness {sg['Ladder score']:.2f}"
        )
        fig.add_trace(
            go.Scattergeo(
                lon=[103.82], lat=[1.35], text=[sg_label], mode="markers+text",
                marker=dict(size=8, color=RED, line=dict(color="white", width=1)),
                textposition="middle right",
                textfont=dict(size=12, color=RED, family="Arial Black"),
                showlegend=False, hoverinfo="skip",
            )
        )
    fig.update_layout(
        title=f"{metric} by country (2023)",
        template="plotly_white", margin=dict(l=10, r=10, t=70, b=10),
        geo=dict(showframe=False, showcoastlines=False, projection_type=projection),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- This is the chart that tests the hypothesis head-on. Across 52 "
            "economies, **Singapore is the 3rd-richest** (by GDP per capita) yet works "
            "the **10th-longest hours - 2,283 a year, about 43.9 a week**.\n"
            "- The ten richest economies average just **1,706 hours a year**; Singapore "
            "works roughly **577 more hours - about 11 extra hours every week** - than "
            "its wealth peers.\n"
            "- Switch the colour to *Happiness* and Singapore is only **mid-pack (23rd "
            "of 52)**. Wealth bought the hours, not the wellbeing."
        ),
        recommendation=(
            "Benchmark Singapore's working time against high-income peers, not the "
            "regional average. The gap to comparably rich economies (Netherlands, "
            "Norway, Denmark all near ~1,400h) is the realistic target space for reform."
        ),
        audiences="Ministry of Manpower (MOM), HR Policy Makers",
    )


# ---------------------------------------------------------------------------
# CHART 8 - Long Hours, Not Proportionally Happier (cross-country scatter)
# ---------------------------------------------------------------------------
def chart_global_scatter() -> None:
    st.header("Chart 8 - Long Hours, Not Proportionally Happier")
    st.markdown(
        "Each dot is a country: **annual working hours** (x) vs **happiness** (y), "
        "sized by GDP per capita. Singapore is highlighted. Toggle the trend line and "
        "country labels in the sidebar."
    )

    ctry = load_country_context()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 8 controls")
    show_trend = st.sidebar.checkbox("Show trend line", value=True)
    label_all = st.sidebar.checkbox("Label every country", value=False)

    sc = ctry.dropna(subset=["annual_hours_2023", "Ladder score"]).copy()
    sc["group"] = np.where(sc["country"] == "Singapore", "Singapore", "Other economies")

    fig = px.scatter(
        sc, x="annual_hours_2023", y="Ladder score", color="group",
        color_discrete_map={"Singapore": RED, "Other economies": BLUE},
        size="Log GDP per capita", size_max=24, hover_name="country",
        text="country" if label_all else None,
        labels={"annual_hours_2023": "Average annual working hours (2023)",
                "Ladder score": "Happiness (Life Ladder, 0-10)", "group": ""},
        title="More hours do not buy more happiness (r = -0.67 across 52 economies)",
    )
    if label_all:
        fig.update_traces(textposition="top center", textfont_size=9)

    if show_trend:
        z = np.polyfit(sc["annual_hours_2023"], sc["Ladder score"], 1)
        xs = np.array([sc["annual_hours_2023"].min(), sc["annual_hours_2023"].max()])
        fig.add_trace(
            go.Scatter(x=xs, y=z[0] * xs + z[1], mode="lines",
                       line=dict(color=GREY, dash="dash"), name="Trend", hoverinfo="skip")
        )

    sg = sc[sc["country"] == "Singapore"].iloc[0]
    fig.add_annotation(
        x=sg["annual_hours_2023"], y=sg["Ladder score"],
        text="Singapore: long hours, mid-pack happiness", showarrow=True, arrowhead=2,
        ax=30, ay=-45, font=dict(color=RED),
    )
    fig.update_layout(
        template="plotly_white", margin=dict(l=40, r=40, t=80, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        insights_md=(
            "- The relationship is **negative: r = -0.67**. Economies that work longer "
            "are, on average, *less* happy - the dashed trend line slopes down.\n"
            "- Singapore sits well to the right (long hours) but only middling on the "
            "vertical axis: a large GDP bubble stranded below the happier, shorter-hours "
            "cluster of Northern Europe.\n"
            "- This is the hypothesis in a single frame: **economic success is real, but "
            "the long hours it runs on are not translating into wellbeing.**"
        ),
        recommendation=(
            "Frame overwork reform as closing the 'hours-to-happiness gap' with peer "
            "economies. The countries top-left of this chart - high happiness on far "
            "fewer hours - are proof that Singapore's trade-off is a choice, not a "
            "necessity."
        ),
        audiences="Ministry of Manpower (MOM), HR Policy Makers, Workplace Wellness Advocates",
    )


# ---------------------------------------------------------------------------
# References (clickable sources), shown under every chart
# ---------------------------------------------------------------------------
def references_section() -> None:
    with st.expander("References & data sources (Charts 1-8)"):
        st.markdown(
            "**Data sources used across Charts 1-8:**\n\n"
            "1. Ministry of Manpower (MOM), *Usual Hours Worked Per Week and % of "
            "Workers Working 40+ Hours, Annual* - "
            "[stats.mom.gov.sg](https://stats.mom.gov.sg/Pages/hours-worked.aspx)\n"
            "2. Department of Statistics Singapore (SingStat), *Resident Labour Force "
            "Participation Rate, Annual* - "
            "[tablebuilder.singstat.gov.sg](https://tablebuilder.singstat.gov.sg)\n"
            "3. Ministry of Manpower (MOM), *Workplace Fatal and Non-Fatal Injury "
            "Rates* - "
            "[mom.gov.sg/workplace-safety-and-health](https://www.mom.gov.sg/workplace-safety-and-health)\n"
            "4. Department of Statistics Singapore (SingStat), *Resident Unemployment "
            "and Long-Term Unemployment Rate, Annual* - "
            "[tablebuilder.singstat.gov.sg](https://tablebuilder.singstat.gov.sg)\n"
            "5. Helliwell, J. et al., *World Happiness Report 2024* - "
            "[worldhappiness.report](https://worldhappiness.report)\n"
            "6. Our World in Data, *Working Hours* (average annual hours worked per "
            "worker, 2023; OECD/ILO/PWT) - "
            "[ourworldindata.org/working-hours](https://ourworldindata.org/working-hours)\n\n"
            "**Supporting context:**\n\n"
            "7. OECD, *Hours worked* indicator - "
            "[oecd.org](https://www.oecd.org/en/data/indicators/hours-worked.html)\n"
            "8. ILOSTAT, *Mean weekly hours actually worked per employed person* - "
            "[ilostat.ilo.org](https://ilostat.ilo.org)\n"
            "9. Wikipedia, *List of countries by average annual labor hours* - "
            "[en.wikipedia.org](https://en.wikipedia.org/wiki/List_of_countries_by_average_annual_labor_hours)"
        )


# ---------------------------------------------------------------------------
# Page header, hypothesis, and the sidebar chart selector
# ---------------------------------------------------------------------------
st.title("Member 1 - Work-Life Balance & Overwork")
st.markdown(
    """
**Hypothesis:** Singapore's economic success masks a chronic culture of long
working hours that directly eats into happiness and leisure.

**My eight charts** each expose one layer of that story - working time, its link
to happiness, who keeps working, the physical cost, the tight market behind it,
who feels the insecurity, and finally where Singapore sits among 52 economies on
a world map and a cross-country scatter. Pick a chart from the sidebar to explore
it, then use the interactive controls that appear.
"""
)

# Each sidebar label maps to the function that draws it. The radio returns one
# label, and we call only that function - which is how the page shows a single
# chart at a time.
CHARTS = {
    "1. The Overwork Paradox": chart_overwork_paradox,
    "2. Long Hours vs Happiness": chart_hours_vs_happiness,
    "3. Working Later in Life": chart_working_later,
    "4. The Human Cost (injuries)": chart_human_cost,
    "5. The Tight Labour Market": chart_tight_market,
    "6. Who Bears the Burden": chart_who_bears_burden,
    "7. Singapore in Global Context (map)": chart_global_map,
    "8. Long Hours vs Happiness (countries)": chart_global_scatter,
}
# The five time-series charts respond to the global year filter. Charts 6, 7, 8
# are single-year / cross-country, so they ignore it.
TIME_CHARTS = {
    "1. The Overwork Paradox", "2. Long Hours vs Happiness",
    "3. Working Later in Life", "4. The Human Cost (injuries)",
    "5. The Tight Labour Market",
}

st.sidebar.header("Member 1 - Work-Life Balance")
st.sidebar.caption("Choose one of my eight charts:")
selection = st.sidebar.radio("My charts", list(CHARTS.keys()), label_visibility="collapsed")

# Global year filter - only shown while a time-series chart is open, and it feeds
# straight into whichever of those charts is being drawn.
if selection in TIME_CHARTS:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Year range")
    YR = st.sidebar.slider(
        "Filter years (time-series charts)",
        min_value=YEAR_MIN, max_value=YEAR_MAX, value=(YEAR_MIN, YEAR_MAX), step=1,
    )

st.divider()
CHARTS[selection]()   # draw the chart the user picked
st.divider()
references_section()
