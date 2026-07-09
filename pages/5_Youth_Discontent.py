"""
Youth Discontent & Future Anxiety
Name - Parthiban

Sub-heuristic
-------------
The Happy City Index and the World Happiness Report both report a single number
for the whole country. That national average hides one group for whom Singapore
is not a happy place, its youth. Split the data by age and a very different
picture appears.

Target audiences
----------------
- Institute of Mental Health (IMH)
- Ministry of Education (MOE)
- Health Promotion Board (HPB)

Structure of this page
----------------------
The sidebar lists my eight charts. Pick one and only that chart shows, with its
own analysis and recommendation. Three of the charts have their own built-in
controls (a metric dropdown, an age toggle, and a year slider), so they stay
interactive inside the page.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Youth Discontent", layout="wide")

# Shared palette. Red is the youth / danger colour, grey is the older baseline.
M5_RED = "#D1495B"
M5_GREY = "#B8B8B8"
M5_BLUE = "#2A6FBB"
M5_GREEN = "#5B8C5A"

# Work out the project root from this file so data paths keep working no matter
# which folder Streamlit is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "processed"

VALID_AGE_BANDS = [
    "10-19", "20 - 29", "30 - 39", "40 - 49", "50 - 59",
    "60 - 64", "65 - 69", "70 - 74", "75 - 79", "80 - 84",
    "85 - 89", "90 and Over",
]
AGE_RANK = {b: i for i, b in enumerate(VALID_AGE_BANDS)}


# ---------------------------------------------------------------------------
# Data loading
# @st.cache_data means each file is read once and reused. Without it, clicking
# between charts in the sidebar would re-read the CSVs every time and feel slow.
# ---------------------------------------------------------------------------
@st.cache_data
def load_master():
    df = pd.read_csv(PROC / "master_clean.csv")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


@st.cache_data
def load_suicide_age():
    df = pd.read_csv(PROC / "suicide_share_by_age_2024.csv")
    df = df[df["DEATH_AGE"].isin(VALID_AGE_BANDS)].copy()
    df["rank"] = df["DEATH_AGE"].map(AGE_RANK)
    return df.sort_values("rank")


@st.cache_data
def load_cod():
    df = pd.read_csv(PROC / "cause_of_death_2024_long.csv")
    df["DEATH_COUNT"] = pd.to_numeric(df["DEATH_COUNT"], errors="coerce")
    return df


@st.cache_data
def load_polyclinic():
    return pd.read_csv(PROC / "top4_polyclinic_attendances.csv")


master = load_master()
suicide_age = load_suicide_age()
cod = load_cod()
poly = load_polyclinic()

# The suicide rows from the detailed death file, reused by several charts.
suicide = cod[cod["ICD_DETAILED_CATEGORY"].str.contains("Intentional self-harm", case=False, na=False)]


def insight_block(analysis, explanation, audience, recommendation):
    """The same footer under every chart, so the eight sections stay consistent
    and I only write the layout once."""
    st.markdown("#### Analysis")
    st.markdown(analysis)
    st.markdown("#### Explanation")
    st.markdown(explanation)
    st.markdown(f"**Target audience:** {audience}")
    st.markdown(f"**Recommendation:** {recommendation}")


# ===========================================================================
# CHART 1 - Suicide share by age (with metric dropdown)
# ===========================================================================
def chart_suicide_share():
    st.subheader("Suicide Share of Deaths by Age (2024)")
    x = suicide_age["DEATH_AGE"]
    share = suicide_age["suicide_share_pct"]
    count = suicide_age["suicide_deaths"]
    total = suicide_age["total_deaths"]
    colors = [M5_RED if AGE_RANK[a] <= AGE_RANK["30 - 39"] else M5_GREY for a in x]

    fig = go.Figure(go.Bar(
        x=x, y=share, marker_color=colors,
        text=[f"{v:.1f}%" for v in share], textposition="outside",
        hovertemplate="Age %{x}<br>%{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="Suicide as a Share of All Deaths, by Age Band (Singapore 2024)",
        xaxis_title="Age band", yaxis_title="Suicide share of deaths (%)",
        template="plotly_white", margin=dict(l=40, r=40, t=95, b=40), showlegend=False,
        updatemenus=[dict(type="dropdown", x=1.0, y=1.20, xanchor="right", buttons=[
            dict(label="Suicide share (%)", method="update",
                 args=[{"y": [share], "text": [[f"{v:.1f}%" for v in share]]},
                       {"yaxis": {"title": "Suicide share of deaths (%)"}}]),
            dict(label="Suicide deaths (count)", method="update",
                 args=[{"y": [count], "text": [[f"{int(v)}" for v in count]]},
                       {"yaxis": {"title": "Number of suicide deaths"}}]),
            dict(label="Total deaths (all causes)", method="update",
                 args=[{"y": [total], "text": [[f"{int(v)}" for v in total]]},
                       {"yaxis": {"title": "Total deaths"}}]),
        ])],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Use the dropdown on the chart to switch between share, count, and total deaths.")

    insight_block(
        "In 2024 suicide accounted for about 25% of all deaths among 10 to 19 "
        "year-olds and about 21% among 20 to 29 year-olds. For residents in "
        "their 70s and 80s the share is under 1%. Use the dropdown to see the "
        "raw counts, the youth percentages are extreme even though the absolute "
        "numbers are smaller than for the old.",
        "Most deaths in any country happen among the elderly from natural "
        "causes, so the national mortality picture is dominated by them. When "
        "suicide is one in four youth deaths but under one in a hundred elderly "
        "deaths, averaging the whole population together erases the youth "
        "signal. This is the core of why the Happy City ranking misses the crisis.",
        "IMH, MOE, HPB.",
        "Age-disaggregate the national wellbeing indicators. A single ranking "
        "should never be used on its own for youth policy.",
    )


# ===========================================================================
# CHART 2 - Population pyramid of suicide deaths
# ===========================================================================
def chart_pyramid():
    st.subheader("Suicide Deaths by Age and Gender (2024)")
    pyr = (suicide[suicide["DEATH_AGE"].isin(VALID_AGE_BANDS)]
           .groupby(["DEATH_AGE", "GENDER"])["DEATH_COUNT"].sum()
           .unstack("GENDER").reindex(VALID_AGE_BANDS).fillna(0))

    fig = go.Figure()
    fig.add_trace(go.Bar(y=pyr.index, x=-pyr["M"], name="Male", orientation="h",
                         marker_color=M5_BLUE, customdata=pyr["M"],
                         hovertemplate="%{y}<br>Male: %{customdata}<extra></extra>"))
    fig.add_trace(go.Bar(y=pyr.index, x=pyr["F"], name="Female", orientation="h",
                         marker_color=M5_RED,
                         hovertemplate="%{y}<br>Female: %{x}<extra></extra>"))
    maxv = max(pyr["M"].max(), pyr["F"].max())
    ticks = list(range(-int(maxv // 10 * 10 + 10), int(maxv // 10 * 10 + 11), 10))
    fig.update_layout(
        title="Suicide Deaths by Age and Gender (Singapore 2024)",
        xaxis=dict(title="Male   |   Female  (number of suicide deaths)",
                   tickvals=ticks, ticktext=[str(abs(t)) for t in ticks]),
        yaxis_title="Age band", barmode="overlay",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "In the 10 to 19 band more girls than boys died by suicide (14 versus "
        "8). That flips in the 20 to 29 band, where young men overtake young "
        "women (28 versus 19), and the male count keeps rising into the 30s. "
        "The teenage-girl figure stands out because it runs against the common "
        "assumption that suicide is mostly a male problem.",
        "The reversal points to two different pressures at two life stages. "
        "Teenage distress shows up earlier and more sharply for girls, while "
        "young-adult pressure around work, money, and housing lands hardest on "
        "men in their 20s and 30s. That second pressure is exactly the chain the "
        "rest of the team documents.",
        "IMH, MOE school counselling services, family-support agencies.",
        "Split youth mental-health outreach by both age and gender rather than "
        "treating youth as one block.",
    )


# ===========================================================================
# CHART 3 - Leading causes of death 10-29
# ===========================================================================
def chart_causes():
    st.subheader("Leading Causes of Death for Ages 10 to 29 (2024)")
    y1029 = cod[cod["DEATH_AGE"].isin(["10-19", "20 - 29"])]
    top = (y1029.groupby("ICD_DETAILED_CATEGORY")["DEATH_COUNT"].sum()
           .sort_values(ascending=False).head(6))

    def short(label):
        label = label.split("(")[0]
        for c_ in ["1-094-", "1-101-", "1-096-", "1-074-", "1-061-", "1-046-"]:
            label = label.replace(c_, "")
        return label.strip()[:42]

    labels = [short(x) for x in top.index]
    colors = [M5_RED if "self-harm" in x.lower() else M5_GREY for x in top.index]
    fig = go.Figure(go.Bar(
        y=labels[::-1], x=top.values[::-1], orientation="h", marker_color=colors[::-1],
        text=[f"{int(v)}" for v in top.values[::-1]], textposition="outside",
        hovertemplate="%{y}<br>%{x} deaths<extra></extra>",
    ))
    fig.update_layout(title="Leading Causes of Death, Ages 10 to 29 (Singapore 2024)",
                      xaxis_title="Number of deaths", template="plotly_white",
                      margin=dict(l=40, r=40, t=70, b=40), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "Setting aside the undefined symptoms-and-abnormal-findings catch-all, "
        "intentional self-harm is the single largest identifiable cause of death "
        "for 10 to 29 year-olds, ahead of transport accidents, pneumonia, and "
        "cancers. The most common clear reason a young Singaporean dies is that "
        "they took their own life.",
        "For older groups the leading causes are cancer and heart disease, the "
        "diseases of ageing. For the young, who are otherwise physically "
        "healthy, the leading cause is a mental-health outcome. That is the "
        "strongest single sign that the youth problem is about wellbeing, not "
        "physical health, and it is exactly what the national ranking cannot show.",
        "MOH, IMH, MOE.",
        "Treat youth mental health as a primary public-health priority, on the "
        "same footing as the physical diseases that dominate older-age mortality.",
    )


# ===========================================================================
# CHART 4 - One in four donut (with age toggle)
# ===========================================================================
def chart_donut():
    st.subheader("One in Four: Suicide vs All Other Causes (2024)")

    def split(age):
        tot = cod[cod["DEATH_AGE"] == age]["DEATH_COUNT"].sum()
        suic = suicide[suicide["DEATH_AGE"] == age]["DEATH_COUNT"].sum()
        return [suic, tot - suic]

    d1019, d2029 = split("10-19"), split("20 - 29")
    fig = go.Figure(go.Pie(
        labels=["Suicide", "All other causes"], values=d1019, hole=0.55,
        marker=dict(colors=[M5_RED, M5_GREY]), textinfo="label+percent", sort=False,
    ))
    fig.update_layout(
        title="Share of Deaths from Suicide, Ages 10 to 19 (Singapore 2024)",
        template="plotly_white", margin=dict(l=40, r=40, t=95, b=40),
        updatemenus=[dict(type="buttons", direction="right", x=0.5, y=1.18,
                          xanchor="center", buttons=[
            dict(label="Ages 10-19", method="update",
                 args=[{"values": [d1019]}, {"title": "Share of Deaths from Suicide, Ages 10 to 19 (2024)"}]),
            dict(label="Ages 20-29", method="update",
                 args=[{"values": [d2029]}, {"title": "Share of Deaths from Suicide, Ages 20 to 29 (2024)"}]),
        ])],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Use the buttons on the chart to toggle between the 10 to 19 and 20 to 29 age groups.")

    insight_block(
        "For 10 to 19 year-olds, 22 of the 87 deaths in 2024 were suicides, "
        "roughly one in four. For 20 to 29 year-olds it is 47 of 223, about one "
        "in five. The donut reduces the whole argument to a single, "
        "hard-to-argue-with picture.",
        "Percentages in a table are easy to skim past. Seeing a full quarter of "
        "the ring filled red makes the scale immediate. This is the chart to "
        "lead with in a presentation, because it needs no explanation to land.",
        "General public, policymakers, media.",
        "Use this framing in public communication. One in four youth deaths is "
        "suicide is a clearer call to action than any national ranking.",
    )


# ===========================================================================
# CHART 5 - Mental health invisible in polyclinic top 4 (year slider)
# ===========================================================================
def chart_invisible():
    st.subheader("The Invisible Burden: Mental Health Is Not in the Top Conditions")
    years = sorted(poly["year"].unique())
    frames = []
    for yr in years:
        d = poly[poly["year"] == yr].sort_values("percentage_diagnoses", ascending=True)
        frames.append(go.Frame(name=str(int(yr)), data=[go.Bar(
            x=d["percentage_diagnoses"], y=d["condition"], orientation="h",
            marker_color=M5_BLUE,
            text=[f"{v:.1f}%" for v in d["percentage_diagnoses"]], textposition="outside")]))

    d0 = poly[poly["year"] == years[-1]].sort_values("percentage_diagnoses", ascending=True)
    fig = go.Figure(
        data=[go.Bar(x=d0["percentage_diagnoses"], y=d0["condition"], orientation="h",
                     marker_color=M5_BLUE,
                     text=[f"{v:.1f}%" for v in d0["percentage_diagnoses"]], textposition="outside")],
        frames=frames,
    )
    fig.update_layout(
        title=f"Top 4 Polyclinic Conditions ({years[-1]}) - Notice What Is Missing",
        xaxis_title="Share of diagnoses (%)", template="plotly_white",
        margin=dict(l=40, r=40, t=70, b=40),
        sliders=[dict(steps=[dict(method="animate",
            args=[[str(int(yr))], dict(mode="immediate", frame=dict(duration=0))],
            label=str(int(yr))) for yr in years],
            currentvalue=dict(prefix="Year: "), x=0.1, len=0.8)],
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Use the year slider under the chart to confirm mental health is absent in every year.")

    insight_block(
        "Across every year from 2006 to 2024, the four most common polyclinic "
        "conditions are the same physical ones, high cholesterol, high blood "
        "pressure, diabetes, and upper respiratory infections. Mental health "
        "never appears, in any year. Slide through the years and the pattern "
        "never breaks.",
        "Suicide is the leading identifiable cause of youth death, yet the "
        "day-to-day health system tracks and reports on physical conditions "
        "almost exclusively. The problem is real in the mortality data but "
        "absent from what the primary-care system routinely measures. What you "
        "do not measure, you cannot manage.",
        "MOH primary-care planning, HPB, polyclinic operators.",
        "Add a mental-health screening and reporting measure to routine "
        "primary-care statistics so the burden becomes visible before it reaches "
        "the mortality data.",
    )


# ===========================================================================
# CHART 6 - Cross-member line (happiness vs housing)
# ===========================================================================
def chart_squeeze():
    st.subheader("The Squeeze: Happiness Falling While Housing Rises")
    link = master[["year", "m4_life_ladder", "m3_hdb_resale_price_index"]].copy()
    happ = link.dropna(subset=["m4_life_ladder"])
    price = link.dropna(subset=["m3_hdb_resale_price_index"])

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=happ["year"], y=happ["m4_life_ladder"],
                             name="Happiness (Life Ladder, M4)", mode="lines+markers",
                             line=dict(color=M5_GREEN, width=3)), secondary_y=False)
    fig.add_trace(go.Scatter(x=price["year"], y=price["m3_hdb_resale_price_index"],
                             name="HDB resale price index (M3)", mode="lines+markers",
                             line=dict(color=M5_RED, width=3)), secondary_y=True)
    fig.update_layout(
        title="Happiness Flat-to-Falling While Housing Costs Climb (Singapore)",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="Year")
    fig.update_yaxes(title_text="Happiness (0-10)", secondary_y=False, color=M5_GREEN)
    fig.update_yaxes(title_text="HDB resale price index", secondary_y=True, color=M5_RED)
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "The green happiness line peaks in 2014 and drifts sideways-to-down "
        "after that, while the red housing-price line climbs steadily and then "
        "sharply after 2020. Rising housing costs are not being matched by "
        "rising happiness. My youth suicide finding is the human cost that sits "
        "underneath this squeeze.",
        "This is the light version of the story the conclusion tells in full. "
        "Member 1 shows the long hours, Member 2 shows the pay that does not "
        "match headline GDP, Member 3 shows housing moving out of reach, and "
        "Member 4 shows the flat-to-falling happiness. My section is where that "
        "pressure finally surfaces as a mortality statistic among the young.",
        "Whole-of-government, this is the cross-domain chart that shows why no "
        "single ministry owns the problem.",
        "Coordinate youth-wellbeing policy across housing, labour, and health "
        "rather than treating each in isolation.",
    )


# ===========================================================================
# CHART 7 - Correlation heatmap
# ===========================================================================
def chart_heatmap():
    st.subheader("The Chain in Numbers: Correlation Heatmap")
    chain = {
        "Weekly hours (M1)": "m1_mean_weekly_hours",
        "GDP-income gap (M2)": "m2_gdp_vs_income_gap_x",
        "Inequality Gini (M2)": "m2_gini_coefficient",
        "HDB price (M3)": "m3_hdb_resale_price_index",
        "Happiness (M4)": "m4_life_ladder",
    }
    sub = master[list(chain.values())].dropna()
    corr = sub.corr()
    corr.index = list(chain.keys())
    corr.columns = list(chain.keys())

    fig = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index, colorscale="RdBu",
        zmid=0, zmin=-1, zmax=1, text=corr.round(2).values, texttemplate="%{text}",
        hovertemplate="%{y} vs %{x}<br>r = %{z:.2f}<extra></extra>",
        colorbar=dict(title="Correlation"),
    ))
    fig.update_layout(title="How the Team's Metrics Move Together (2010-2025)",
                      template="plotly_white", margin=dict(l=40, r=40, t=70, b=40), height=520)
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "The strongest cells are the ones that prove the chain. Weekly hours and "
        "inequality move together very strongly (about +0.9). Housing price and "
        "inequality move in opposite numeric directions (about -0.8), which is "
        "the GDP illusion in one number. These are not separate coincidences, "
        "they form one connected system.",
        "A single strong pair could be luck. A whole matrix where labour, "
        "income, housing, and happiness metrics all correlate in the directions "
        "the story predicts is much harder to dismiss. This is the statistical "
        "backbone under the visual storyboard.",
        "Whole-of-government analysts, policy researchers.",
        "Treat these indicators as one linked dashboard. Moving one lever, such "
        "as housing, should be expected to move the others.",
    )


# ===========================================================================
# CHART 8 - Forecast
# ===========================================================================
def chart_forecast():
    st.subheader("Where the Trend Points: Youth Suicide Share to 2030")
    youth_bands = ["10-19", "20 - 29", "30 - 39"]
    youth_share = suicide_age[suicide_age["DEATH_AGE"].isin(youth_bands)]["suicide_share_pct"].mean()
    older_share = suicide_age[~suicide_age["DEATH_AGE"].isin(youth_bands)]["suicide_share_pct"].mean()
    future = list(range(2024, 2031))
    youth_line = [youth_share * (1 + 0.02 * (y - 2024)) for y in future]
    older_line = [older_share for _ in future]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=future, y=youth_line, mode="lines+markers",
                             name="Youth (10-39) suicide share", line=dict(color=M5_RED, width=3)))
    fig.add_trace(go.Scatter(x=future, y=older_line, mode="lines+markers",
                             name="Older population baseline",
                             line=dict(color=M5_GREY, width=3, dash="dash")))
    fig.update_layout(title="Illustrative Projection: Youth vs Older Suicide Share, 2024 to 2030",
                      xaxis_title="Year", yaxis_title="Suicide share of deaths (%)",
                      template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "Holding the current gap and applying a small upward drift, the youth "
        "suicide share stays far above the older-population baseline through "
        "2030. Even under a conservative assumption, nothing in the data "
        "suggests the gap closes on its own.",
        "The projection is illustrative because we only have one detailed year "
        "of the age-by-cause data. The point is not the exact number, it is that "
        "the signal is visible and directional now. If the data already shows "
        "where this is heading and no system is watching it, that gap is itself "
        "the problem worth fixing.",
        "MOH planning, IMH, MOE.",
        "Stand up an age-disaggregated youth mental-health surveillance metric so "
        "this stops being something we only notice after the fact.",
    )


# ===========================================================================
# Page layout - intro and the chart selector
# ===========================================================================
st.title("Youth Discontent & Future Anxiety")
st.markdown("**Author:** Poysollameyyar Parthiban")
st.markdown(
    """
My section challenges the happy-city ranking by looking at the one group the
national average hides, young people. Both the Happy City Index and the World
Happiness Report report a single number for the whole country. When I break the
data down by age, a very different picture appears.

**Hypothesis:** the ranking averages happiness nationally and hides a growing
fracture in life satisfaction among younger generations, who face the highest
share of self-harm mortality and report weaker confidence in the future.

**My eight charts** each expose one layer of that story. Pick a chart from the
sidebar. Three of them (the age bar, the donut, and the polyclinic chart) have
their own built-in controls.
"""
)

CHARTS = {
    "1. Suicide Share by Age": chart_suicide_share,
    "2. Deaths by Age and Gender": chart_pyramid,
    "3. Leading Causes, 10 to 29": chart_causes,
    "4. One in Four (donut)": chart_donut,
    "5. The Invisible Burden": chart_invisible,
    "6. The Squeeze (cross-member)": chart_squeeze,
    "7. The Chain in Numbers": chart_heatmap,
    "8. Forecast to 2030": chart_forecast,
}

st.sidebar.header("Youth Discontent")
st.sidebar.caption("Choose one of my eight charts:")
selection = st.sidebar.radio("My charts", list(CHARTS.keys()), label_visibility="collapsed")

st.divider()
CHARTS[selection]()


# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------
with st.expander("References"):
    st.markdown(
        """
[1] Immigration & Checkpoints Authority (ICA), "Cause of Death by Age Group, 2024", data.gov.sg (d_716c31ea00d7c05d43d4109d8b0db3bb)

[2] Ministry of Culture, Community and Youth (MCCY), "Social Values Survey 2018-2019", data.gov.sg

[3] Ministry of Health (MOH), "Top 4 Conditions of Polyclinic Attendances, 2006-2024", data.gov.sg

[4] Ministry of Health (MOH), "Principal Causes of Death, 2006-2022", data.gov.sg

[5] Helliwell, J. et al., "World Happiness Report 2024", https://worldhappiness.report

[6] Samaritans of Singapore (SOS), youth suicide statistics, https://www.sos.org.sg

[7] Institute of Mental Health (IMH), "Singapore Mental Health Study", https://www.imh.com.sg
"""
    )
