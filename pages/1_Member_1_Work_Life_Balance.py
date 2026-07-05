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
The sidebar lists my six charts. Pick one and only that chart is shown, with
its own data-analysis insights and a recommendation. Chart 2 is the interactive
one: a year-range slider appears in the sidebar only while that chart is open.
"""

from pathlib import Path

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


def insight_block(insights_md: str, recommendation: str, audiences: str) -> None:
    """The same insight / recommendation / audience footer under every chart,
    so the six sections stay consistent and I only write the layout once."""
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
        "the **share of workers doing 40+ hours** (right), from 2010 to 2025."
    )

    hours = load_hours()

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
        title="Working hours have eased slightly but stay high (2010-2025)",
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
# CHART 2 - Long Hours vs National Happiness  (INTERACTIVE: year-range slider)
# ---------------------------------------------------------------------------
def chart_hours_vs_happiness() -> None:
    st.header("Chart 2 - Long Hours vs National Happiness Interactive")
    st.markdown(
        "This is my interactive chart. Use the **year-range slider in the sidebar** "
        "to focus any window between 2010 and 2023 and watch how working hours line "
        "up against Singapore's national happiness score (World Happiness *Life "
        "Ladder*)."
    )

    hours = load_hours()
    happiness = load_happiness()
    # Left join keeps every year of hours; happiness only covers some years, so
    # dropna removes the years where we have no happiness score to compare.
    merged = hours.merge(happiness, on="year", how="left").dropna(subset=["m4_life_ladder"])

    # Building the slider *inside* this function is deliberate - it means the
    # control only appears while Chart 2 is the one on screen, and disappears
    # again when the user switches to another chart.
    st.sidebar.markdown("---")
    st.sidebar.subheader("Chart 2 control")
    yr_min, yr_max = int(merged["year"].min()), int(merged["year"].max())
    start_year, end_year = st.sidebar.slider(
        "Year range", min_value=yr_min, max_value=yr_max,
        value=(yr_min, yr_max), step=1,
    )

    # Everything below reads from `view`, so the whole chart redraws to match
    # whatever the slider is set to.
    view = merged[(merged["year"] >= start_year) & (merged["year"] <= end_year)]
    if view.empty:
        st.warning("No data in the selected year range. Widen the slider.")
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
        title=f"Working hours vs happiness, {start_year}-{end_year}",
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
    # year), so the takeaway updates live with the slider.
    first, last = view.iloc[0], view.iloc[-1]
    hrs_delta = last["mean_hours"] - first["mean_hours"]
    hap_delta = last["m4_life_ladder"] - first["m4_life_ladder"]
    st.info(
        f"In {start_year}-{end_year}, mean weekly hours changed by "
        f"**{hrs_delta:+.1f}h** while happiness changed by **{hap_delta:+.2f}** points."
    )

    insight_block(
        insights_md=(
            "- Across the full window, happiness **peaked at 7.06 in 2014 and never "
            "recovered**, settling around 6.3-6.7 in recent years.\n"
            "- Hours drifted down over the same period, yet happiness did **not** rise "
            "with it - so shorter average hours alone did not buy back wellbeing.\n"
            "- The stubborn 40+ hour share (Chart 1) is the more likely culprit: the "
            "workload intensity that squeezes leisure has not really changed.\n"
            "- Drag the slider to 2014-2023 to isolate the decline the hypothesis is "
            "built on."
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
        "Resident labour force participation by age band since 2010. If overwork is "
        "structural, we expect older Singaporeans to keep working rather than retire."
    )

    part = load_participation()
    # Only these four bands are plotted - the full file has ~19 series and drawing
    # them all would be an unreadable spaghetti chart. The dict also pins a fixed
    # colour to each band so the legend stays stable.
    bands = {
        "Total Resident Participation Rate": GREY,
        "55 - 59 Years": BLUE,
        "60 - 64 Years": GREEN,
        "65 - 69 Years": RED,
    }
    view = part[(part["series"].isin(bands)) & (part["period"] >= 2010)]

    fig = px.line(
        view, x="period", y="value", color="series",
        color_discrete_map=bands, markers=True,
        labels={"period": "Year", "value": "Participation rate (%)", "series": "Age band"},
        title="Older cohorts are staying in the workforce (2010-2025)",
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
        "Workplace injury rates per 100,000 workers, 2014-2024: non-fatal injuries "
        "(bars, right axis) and fatal injuries (line, left axis)."
    )

    inj = load_injury()
    fatal = inj[inj["series"] == "Workplace Fatal Injuries"].sort_values("period")
    nonfatal = inj[inj["series"] == "Workplace Non-Fatal Injuries"].sort_values("period")

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
        title="Injury rates per 100,000 workers (2014-2024)",
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
        "Resident unemployment vs long-term unemployment since 2010. A persistently "
        "tight market is part of *why* hours stay long - there is little slack."
    )

    unemp = load_unemployment()
    longterm = load_longterm_unemployment()
    # Pull just the "Total" line from each of the two files and rename its value
    # column so they don't collide when merged.
    ut = (unemp[(unemp["series"] == "Total") & (unemp["period"] >= 2010)]
          [["period", "value"]].rename(columns={"value": "unemp"}))
    lt = (longterm[(longterm["series"] == "Total") & (longterm["period"] >= 2010)]
          [["period", "value"]].rename(columns={"value": "longterm"}))
    # Outer join on year: the long-term file ends a year earlier, and an outer
    # join keeps that extra overall-unemployment year rather than dropping it.
    view = ut.merge(lt, on="period", how="outer").sort_values("period")

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
        title="Unemployment stays low - a consistently tight market (2010-2025)",
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
        "the assumption that more education means more job security."
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
# Page header, hypothesis, and the sidebar chart selector
# ---------------------------------------------------------------------------
st.title("Member 1 - Work-Life Balance & Overwork")
st.markdown(
    """
**Hypothesis:** Singapore's economic success masks a chronic culture of long
working hours that directly eats into happiness and leisure.

**My six charts** each expose one layer of that story - working time, its link
to happiness, who keeps working, the physical cost, the tight market behind it,
and who feels the insecurity. Pick a chart from the sidebar to explore it.
"""
)

# Each sidebar label maps to the function that draws it. The radio returns one
# label, and we call only that function - which is how the page shows a single
# chart at a time (and, for Chart 2, only then builds its slider).
CHARTS = {
    "1. The Overwork Paradox": chart_overwork_paradox,
    "2. Long Hours vs Happiness (interactive)": chart_hours_vs_happiness,
    "3. Working Later in Life": chart_working_later,
    "4. The Human Cost (injuries)": chart_human_cost,
    "5. The Tight Labour Market": chart_tight_market,
    "6. Who Bears the Burden": chart_who_bears_burden,
}

st.sidebar.header("Member 1 - Work-Life Balance")
st.sidebar.caption("Choose one of my six charts:")
selection = st.sidebar.radio("My charts", list(CHARTS.keys()), label_visibility="collapsed")

st.divider()
CHARTS[selection]()   # draw the chart the user picked
