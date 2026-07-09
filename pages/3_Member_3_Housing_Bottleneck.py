"""
Member 3 - The Housing Premium Bottleneck
Name - Noorul Fahima

Hypothesis
----------
Singapore's high homeownership rate hides an aggressive, stress-inducing surge
in the cost of securing a home, which creates real financial stress for
first-time buyers.

Target audiences
----------------
- Housing & Development Board (HDB)
- Ministry of National Development (MND)
- First-time and young homebuyers

Structure of this page
----------------------
The sidebar lists my seven charts. Pick one and only that chart shows, with its
own analysis and recommendation. A year-range filter in the sidebar feeds into
whichever chart is open, so every chart is interactive. Chart 7 is the
choropleth map with its own year slider, and also gets its own flat type
filter since that one does not apply to the other six charts.
"""

import json
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

st.set_page_config(page_title="Member 3 - Housing", layout="wide")

# One shared palette so all seven charts feel like the same page. Blue is the
# neutral price line, red is the "expensive / unaffordable" warning colour, and
# green is the "still affordable" colour.
BLUE = "#2A6FBB"
RED = "#D1495B"
GREEN = "#5B8C5A"
GREY = "#8A8D91"

# The $400k line I use across the page. It is roughly the old price ceiling for
# a 3-room flat, which is the entry-level "affordable" tier for a first-timer,
# based on historical HDB data [1].
AFFORDABLE_LINE = 400_000

# Work out the project root from this file so the data paths keep working no
# matter which folder Streamlit is launched from.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw" / "member_3"


# ---------------------------------------------------------------------------
# Data loading
# @st.cache_data means each file is read once and reused. Without it, every
# click on the sidebar would re-read the big 23MB transactions file and the page
# would feel slow.
# ---------------------------------------------------------------------------
@st.cache_data
def load_transactions() -> pd.DataFrame:
    """Every HDB resale transaction from Jan 2017 onwards (town, flat type, price)."""
    df = pd.read_csv(PROC_DIR / "hdb_resale_monthly.csv")
    df["month"] = pd.to_datetime(df["month"])
    df["year"] = df["month"].dt.year
    df["resale_price"] = pd.to_numeric(df["resale_price"], errors="coerce")
    # Tidy the text columns so towns and flat types match up cleanly later.
    df["flat_type"] = df["flat_type"].str.strip().str.upper()
    df["town"] = df["town"].str.strip().str.title()
    df = df.dropna(subset=["year", "town", "resale_price"])
    df["year"] = df["year"].astype(int)
    return df


@st.cache_data
def load_price_index() -> pd.DataFrame:
    """Quarterly HDB resale price index going back to 1990 (1Q2009 = 100)."""
    df = pd.read_csv(PROC_DIR / "hdb_price_index_quarterly.csv")
    df["year"] = df["quarter"].str.slice(0, 4).astype(int)
    df["index"] = pd.to_numeric(df["index"], errors="coerce")
    return df


@st.cache_data
def load_master() -> pd.DataFrame:
    """The team's merged master file. I only need income and price to compare
    them side by side in Chart 6, so I pull just those two columns."""
    return pd.read_csv(PROC_DIR / "master_clean.csv")


@st.cache_data
def load_geojson():
    """Planning-area boundaries for the map. Returns None if the file is missing
    so the map chart can show a friendly warning instead of crashing."""
    name = "MasterPlan2025PlanningAreaBoundaryNoSea.geojson"
    for folder in (PROC_DIR, RAW_DIR):
        path = folder / name
        if path.exists():
            with open(path) as f:
                return json.load(f)
    return None


txn_all = load_transactions()
price_index = load_price_index()
master = load_master()
sg_geo = load_geojson()

# The flat types in a sensible small-to-big order, dropping any that are not in
# the data so the filter never shows an empty option.
FLAT_ORDER = ["1 ROOM", "2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM", "EXECUTIVE", "MULTI-GENERATION"]
FLAT_ORDER = [f for f in FLAT_ORDER if f in txn_all["flat_type"].unique()]


def insight_block(analysis_md: str, explanation_md: str, audience: str, recommendation: str) -> None:
    """The same footer under every chart - analysis, explanation, who it is for,
    and what to do about it. Writing it once here keeps all seven sections
    consistent."""
    st.markdown("#### Analysis")
    st.markdown(analysis_md)
    st.markdown("#### Explanation")
    st.markdown(explanation_md)
    st.markdown(f"**Target audience:** {audience}")
    st.markdown(f"**Recommendation:** {recommendation}")


def get_filtered_txn():
    """Read the year filter from the sidebar and return that slice of the
    transactions. Every transaction-based chart calls this, so all of them react
    to the same year range."""
    yr = st.session_state.get("year_range", (txn_all["year"].min(), txn_all["year"].max()))
    return txn_all[(txn_all["year"] >= yr[0]) & (txn_all["year"] <= yr[1])].copy()


# ===========================================================================
# CHART 1 - Yearly median resale price
# ===========================================================================
def chart_yearly_median():
    st.subheader("Prices Have Been Climbing for Years")
    fdf = get_filtered_txn()
    if fdf.empty:
        st.warning("No data for the selected filters. Widen the year range or add a flat type.")
        return

    g1 = fdf.groupby("year")["resale_price"].median().reset_index()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=g1["year"], y=g1["resale_price"], mode="lines+markers",
        line=dict(color=BLUE, width=3), marker=dict(size=8),
        hovertemplate="Year %{x}<br>Median: S$%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=AFFORDABLE_LINE, line_dash="dash", line_color=RED,
                  annotation_text="Affordability line (S$400k)", annotation_position="bottom right")
    fig.update_layout(
        title="Median HDB Resale Price by Year",
        xaxis_title="Year", yaxis_title="Median resale price (S$)",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "Median HDB resale prices rose from S\\$410,000 in 2017 to S\\$628,000 by "
        "2025, a jump of over 50% in eight years. Prices stayed flat during "
        "2019, then climbed every year after with no year showing a drop.",
        "2019 is when COVID-19 started. Build-To-Order (BTO) construction was "
        "slowed and the supply of public housing was reduced [2][3]. The pandemic also "
        "drove demand for larger living space. With new-flat supply constrained "
        "at the moment demand rose, buyers were pushed towards the resale "
        "market, driving the yearly climb shown here.",
        "HDB and MND supply planners, first-time buyers.",
        "Maintain or increase BTO supply in mature estates to take the pressure "
        "off the resale market.",
    )


# ===========================================================================
# CHART 2 - Quarterly price index
# ===========================================================================
def chart_price_index():
    st.subheader("It Accelerated Sharply After 2020")
    yr = st.session_state.get("year_range", (txn_all["year"].min(), txn_all["year"].max()))
    pidx = price_index[(price_index["year"] >= yr[0]) & (price_index["year"] <= yr[1])]
    if pidx.empty:
        st.warning("No index data in the selected year range.")
        return

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pidx["quarter"], y=pidx["index"], mode="lines",
        line=dict(color=BLUE, width=2),
        hovertemplate="%{x}<br>Index: %{y:.1f}<extra></extra>",
    ))
    # Shade the post-2020 sprint only if it falls inside the chosen years.
    if yr[1] >= 2021:
        fig.add_vrect(x0="2021-Q1", x1=pidx["quarter"].iloc[-1],
                      fillcolor=RED, opacity=0.10, line_width=0,
                      annotation_text="Post-2020 acceleration", annotation_position="top left")
    fig.update_layout(
        title="HDB Resale Price Index (1Q2009 = 100)",
        xaxis_title="Quarter", yaxis_title="Price index",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
    )
    fig.update_xaxes(nticks=15)
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "The index climbs from around 25 in 1990 to a first peak near 100 by "
        "1997, drops sharply, then spends two decades in the 70-150 range. The "
        "real story is the shaded zone from 2021: the index climbs almost in a "
        "straight line to above 200 by 2026. Prices have effectively doubled "
        "since the 2009 base, with nearly all of that in the last five years.",
        "Same driver as Chart 1. COVID-era BTO undersupply pushed buyers who "
        "could not wait 3 to 5 years for a BTO into the resale market instead "
        "[3]. This chart proves the rise was not a slow drift the whole time, it is a "
        "distinct acceleration that starts exactly where Chart 1's flat line ends.",
        "HDB and MND policy makers.",
        "Consider phased, targeted cooling measures timed with construction-delay "
        "cycles.",
    )


# ===========================================================================
# CHART 3 - Median price by flat type
# ===========================================================================
def chart_by_flat_type():
    st.subheader("Every Flat Type Is Affected, Not Just Big Ones")
    fdf = get_filtered_txn()
    if fdf.empty:
        st.warning("No data for the selected filters.")
        return

    order = [f for f in FLAT_ORDER if f in fdf["flat_type"].unique()]
    g3 = fdf.groupby("flat_type")["resale_price"].median().reindex(order).dropna().reset_index()
    # Green if the median is still under the affordability line, red if not.
    colors = [GREEN if v < AFFORDABLE_LINE else RED for v in g3["resale_price"]]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=g3["flat_type"], y=g3["resale_price"], marker_color=colors,
        text=[f"S${v:,.0f}" for v in g3["resale_price"]], textposition="outside",
        hovertemplate="%{x}<br>Median: S$%{y:,.0f}<extra></extra>",
    ))
    fig.add_hline(y=AFFORDABLE_LINE, line_dash="dash", line_color="#333",
                  annotation_text="Affordability line (S$400k)", annotation_position="top left")
    fig.update_layout(
        title="Median Resale Price by Flat Type",
        xaxis_title="Flat type", yaxis_title="Median resale price (S$)",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40), showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "A clean staircase across flat types, but the affordability line falls "
        "right under the 3-room type. Every other type sits above it. 3-room and "
        "4-room flats are also the two highest-volume types transacted every "
        "year, so the affordability threshold cuts through the two flat types "
        "that see the most activity, not the edges of the market.",
        "The price surge from Charts 1 and 2 was not isolated to one flat type, "
        "it lifted the whole market. Even 3-room and 4-room flats, built across "
        "every town and sized for a typical household, now sit at or above the "
        "S\\$400k line [4]. This is not about people wanting bigger homes, the flats "
        "people were already buying the most became unaffordable at roughly the "
        "same pace as everything else.",
        "First-time buyers deciding which flat type fits their budget.",
        "Give different housing grant amounts based on flat size instead of a "
        "flat rate for everyone.",
    )


# ===========================================================================
# CHART 4 - Share of transactions below $400k
# ===========================================================================
def chart_affordable_share():
    st.subheader("Affordable Flats Have Basically Disappeared")
    fdf = get_filtered_txn()
    if fdf.empty:
        st.warning("No data for the selected filters.")
        return

    g4 = (fdf.assign(is_affordable=fdf["resale_price"] < AFFORDABLE_LINE)
          .groupby("year")["is_affordable"].mean().mul(100).reset_index(name="affordable_pct"))
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=g4["year"], y=g4["affordable_pct"], mode="lines+markers",
        line=dict(color=RED, width=3), marker=dict(size=8),
        fill="tozeroy", fillcolor="rgba(209,73,91,0.12)",
        hovertemplate="Year %{x}<br>%{y:.0f}% affordable<extra></extra>",
    ))
    fig.update_layout(
        title="Share of Resale Transactions Below S$400,000",
        xaxis_title="Year", yaxis_title="Share below S$400k (%)",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "The sharpest trend of the whole set. Affordable share held between "
        "45% and 49% from 2017 to 2019, close to half the market. From 2020 it "
        "falls every single year: 41%, then 25%, 19%, 16%, 12%, then 8% by "
        "2025. The affordable half of the market has shrunk to roughly a tenth "
        "of transactions in six years. This is the clearest evidence in the "
        "whole dashboard that first-time buyers are under real financial stress, "
        "not just paying a bit more.",
        "As overall prices rise, cheap resale flats are disappearing. Private "
        "downgraders selling private property to buy HDB drove prices up. Even "
        "the government's 15-month wait-out rule, which slowed price growth, did "
        "not reverse the affordability collapse [5]. The problem is not just "
        "downgraders, there is a deeper shortage of available flats.",
        "HDB grant policy team, Ministry of National Development.",
        "Adjust housing grants based on how rare cheap flats are becoming, "
        "rather than a fixed amount.",
    )


# ===========================================================================
# CHART 5 - Top 10 vs bottom 10 towns
# ===========================================================================
def chart_town_comparison():
    st.subheader("Some Towns Are Far Worse Than Others")
    fdf = get_filtered_txn()
    if fdf.empty:
        st.warning("No data for the selected filters.")
        return

    town_med = fdf.groupby("town")["resale_price"].median().sort_values(ascending=False)
    top10 = town_med.head(10).sort_values()
    bottom10 = town_med.tail(10).sort_values()

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Top 10 most expensive", "Bottom 10 most affordable"),
                        horizontal_spacing=0.15)
    fig.add_trace(go.Bar(y=top10.index, x=top10.values, orientation="h",
                         marker_color=RED,
                         hovertemplate="%{y}<br>S$%{x:,.0f}<extra></extra>"), row=1, col=1)
    fig.add_trace(go.Bar(y=bottom10.index, x=bottom10.values, orientation="h",
                         marker_color=GREEN,
                         hovertemplate="%{y}<br>S$%{x:,.0f}<extra></extra>"), row=1, col=2)
    fig.update_layout(title="Town Comparison: Median Resale Price",
                      template="plotly_white", margin=dict(l=40, r=40, t=90, b=40),
                      showlegend=False)
    fig.update_xaxes(title_text="Median price (S$)", row=1, col=1)
    fig.update_xaxes(title_text="Median price (S$)", row=1, col=2)
    st.plotly_chart(fig, use_container_width=True)

    top_price = top10.iloc[-1]
    top_name = top10.index[-1]
    bottom_price = bottom10.iloc[0]
    bottom_name = bottom10.index[0]
    gap = top_price - bottom_price

    insight_block(
        f"Two panels on different x-axis scales, and that gap is the point. "
        f"{top_name} leads at S\\${top_price:,.0f}, against {bottom_name}'s "
        f"S\\${bottom_price:,.0f}, a gap of around S\\${gap:,.0f} for the median "
        f"flat. Even the most affordable town sits close to or above the "
        f"S\\$400,000 cut-off, so there is barely any town left where the median "
        f"resale flat sits comfortably under the affordability line.",
        "The most expensive towns are not random, they have the best locations "
        "and the newest resale flats, close to MRT stations, good schools, and "
        "established amenities, which makes them highly sought-after.",
        "HDB urban planners, Ministry of National Development.",
        "Build new MRT stations and amenities in non-mature estates to spread "
        "housing demand more evenly.",
    )


# ===========================================================================
# CHART 6 - Income growth vs price growth (links Member 2)
# ===========================================================================
def chart_income_vs_price():
    st.subheader("Income Has Not Kept Up With Prices")
    yr = st.session_state.get("year_range", (txn_all["year"].min(), txn_all["year"].max()))
    g6 = master[["year", "m2_median_household_income_sgd", "m3_hdb_resale_price_index"]].dropna().copy()
    g6 = g6[(g6["year"] >= yr[0]) & (g6["year"] <= yr[1])].sort_values("year")

    if len(g6) < 2:
        st.info("Not enough years in the selected range to index income against price. Widen the year range.")
        return

    # Index both series to 100 at the first year in view so we compare growth,
    # not raw levels (income is in dollars, the price index is unitless).
    base_income = g6["m2_median_household_income_sgd"].iloc[0]
    base_price = g6["m3_hdb_resale_price_index"].iloc[0]
    g6["income_idx"] = g6["m2_median_household_income_sgd"] / base_income * 100
    g6["price_idx"] = g6["m3_hdb_resale_price_index"] / base_price * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=g6["year"], y=g6["price_idx"], mode="lines+markers",
                             name="HDB resale price (indexed)", line=dict(color=RED, width=3)))
    fig.add_trace(go.Scatter(x=g6["year"], y=g6["income_idx"], mode="lines+markers",
                             name="Median household income (indexed)", line=dict(color=BLUE, width=3)))
    fig.update_layout(
        title=f"Income vs HDB Price, indexed to {int(g6['year'].iloc[0])} = 100",
        xaxis_title="Year", yaxis_title="Index (base year = 100)",
        template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    insight_block(
        "Both median household income and HDB median resale price start at 100 "
        "and stay close until 2019, income even edges slightly ahead in "
        "2018-2019. After 2020, prices shoot past income and never slow down. "
        "By 2025 the price index hits 150+ while income only reaches 130+, a gap "
        "of over 20 points that opened up entirely after 2020, the same window "
        "when prices surged and flats became much less affordable.",
        "Headline GDP figures include corporate profits and investment returns "
        "that do not flow into household paychecks, so aggregate prosperity "
        "overstates what a typical resident can spend. Singapore's wage share of "
        "GDP has also lagged behind comparable economies for years [9]. This is the "
        "closing argument of the section: it is not just that flats got more "
        "expensive, it is that income never had a chance to keep up.",
        "MTI, MAS, and MND jointly - this is the cross-domain chart that needs "
        "both teams' attention.",
        "Pair housing grant policy with income growth measures rather than "
        "treating affordability as a housing-only problem.",
    )


# ===========================================================================
# CHART 7 - Interactive choropleth map
# ===========================================================================
def chart_map():
    st.subheader("Explore the Town-Level Price Gap Year by Year (interactive)")
    st.markdown(
        "This map is the interactive extension of Chart 5. Use the year slider "
        "under the map to watch how the price gap between towns opened up over "
        "time. Use the flat type filter in the sidebar to narrow the map down "
        "to specific flat types only."
    )
    fdf = get_filtered_txn()

    # apply the flat type filter, only relevant on this chart
    selected_flat_types = st.session_state.get("map_flat_types", FLAT_ORDER)
    fdf = fdf[fdf["flat_type"].isin(selected_flat_types)]

    if sg_geo is None or fdf.empty:
        st.warning("No data for the selected filters, or the GeoJSON file could not be found.")
        return

    # A couple of HDB town names do not match the map's area names exactly, so
    # map them across before drawing.
    name_map = {"KALLANG/WHAMPOA": "KALLANG", "CENTRAL AREA": "DOWNTOWN CORE"}
    choro = fdf.groupby(["year", "town"])["resale_price"].median().reset_index()
    choro["town_geo"] = choro["town"].str.upper().replace(name_map)

    years = sorted(choro["year"].unique())
    price_min = choro["resale_price"].min()
    price_max = choro["resale_price"].max()

    # One frame per year so the slider can jump between them. Keeping zmin/zmax
    # fixed across frames means the colours mean the same thing every year.
    frames = []
    for y in years:
        d = choro[choro["year"] == y]
        frames.append(go.Frame(name=str(y), data=[go.Choroplethmapbox(
            geojson=sg_geo, locations=d["town_geo"], featureidkey="properties.PLN_AREA_N",
            z=d["resale_price"], zmin=price_min, zmax=price_max, colorscale="RdYlGn_r",
            hovertemplate="<b>%{location}</b><br>Median Price: S$%{z:,.0f}<extra></extra>",
            colorbar=dict(title="Median Price (S$)"),
        )]))

    first = choro[choro["year"] == years[0]]
    fig = go.Figure(data=[go.Choroplethmapbox(
        geojson=sg_geo, locations=first["town_geo"], featureidkey="properties.PLN_AREA_N",
        z=first["resale_price"], zmin=price_min, zmax=price_max, colorscale="RdYlGn_r",
        hovertemplate="<b>%{location}</b><br>Median Price: S$%{z:,.0f}<extra></extra>",
        colorbar=dict(title="Median Price (S$)"),
    )], frames=frames)
    fig.update_layout(
        title=f"HDB Resale Median Price by Town ({years[0]}-{years[-1]})",
        mapbox=dict(style="carto-positron", center=dict(lat=1.3521, lon=103.8198), zoom=10),
        height=620, margin=dict(l=0, r=0, t=50, b=0),
        sliders=[dict(steps=[dict(method="animate",
            args=[[str(y)], dict(mode="immediate", frame=dict(duration=0), transition=dict(duration=0))],
            label=str(y)) for y in years],
            currentvalue=dict(prefix="Year: ", visible=True, xanchor="center"),
            x=0.1, y=0, len=0.8)],
    )
    st.plotly_chart(fig, use_container_width=True)

    latest = choro[choro["year"] == years[-1]].sort_values("resale_price", ascending=False)
    top_town, bottom_town = latest.iloc[0], latest.iloc[-1]
    gap = top_town["resale_price"] - bottom_town["resale_price"]
    insight_block(
        f"The map colours each town by its median resale price for the selected "
        f"year, red for the most expensive and green for the most affordable. "
        f"Moving the slider shows red areas spreading and deepening over time, "
        f"concentrated in the central and southern parts of the island. In "
        f"{years[-1]}, {top_town['town']} is the most expensive town at "
        f"S\\${top_town['resale_price']:,.0f}, while {bottom_town['town']} is the "
        f"most affordable at S\\${bottom_town['resale_price']:,.0f}, a gap of "
        f"S\\${gap:,.0f}.",
        "The towns that turn red earliest are the same mature estates from Chart "
        "5, with strong MRT links, established amenities, and a steady pipeline "
        "of newly MOP-eligible flats. Watching it year by year makes clear the "
        "gap widened gradually rather than appearing all at once.",
        "HDB urban planners, URA, MND, and prospective buyers researching towns.",
        "Use this map as an early-warning tool, flagging towns crossing a set "
        "price growth rate for infrastructure or supply help before they follow "
        "the same path as Queenstown or Toa Payoh.",
    )


# ===========================================================================
# Page layout - intro, sidebar filters, and the chart selector
# ===========================================================================
st.title("The Housing Premium Bottleneck")
st.markdown(
    """
**Noorul Fahima**


My section checks whether Singapore's high homeownership rate is hiding a real
affordability problem underneath it. I look at resale price, flat type, town,
and how income has kept pace, because these are the variables that show whether
"high homeownership" actually means housing is affordable.

**Hypothesis:** the traditional metric of high homeownership hides an
aggressive, stress-inducing surge in the cost of securing a home, which creates
financial stress for first-time buyers.

**Affordability cut-off:** the S\\$400,000 line used across these charts is
based on historical HDB data showing this was roughly the price ceiling for
3-room flats, the entry-level "affordable" tier for first-time buyers [1].

**My seven charts** each expose one layer of that story. Pick a chart from the
sidebar to explore it. The year-range filter in the sidebar feeds into
whichever chart is open.
"""
)

# Each sidebar label maps to the function that draws it. The radio returns one
# label and we call only that function, which is how the page shows a single
# chart at a time.
CHARTS = {
    "1. Prices Climbing for Years": chart_yearly_median,
    "2. The Post-2020 Acceleration": chart_price_index,
    "3. Every Flat Type Affected": chart_by_flat_type,
    "4. Affordable Flats Vanishing": chart_affordable_share,
    "5. Town-by-Town Divide": chart_town_comparison,
    "6. Income vs Price Gap": chart_income_vs_price,
    "7. Price Map (interactive)": chart_map,
}

st.sidebar.header("Housing")
st.sidebar.caption("Choose one of my seven charts:")
selection = st.sidebar.radio("My charts", list(CHARTS.keys()), label_visibility="collapsed")

st.sidebar.divider()
st.sidebar.caption("Year filter (applies to the chart on screen):")

# Store the year range in session_state so the chart functions can read it
# without me passing arguments around everywhere.
min_year = int(txn_all["year"].min())
max_year = int(txn_all["year"].max())
st.session_state["year_range"] = st.sidebar.slider(
    "Year range", min_value=min_year, max_value=max_year,
    value=(min_year, max_year), step=1,
)

# Flat type filter only matters for the map, so only show it when that chart is picked.
if selection == "7. Price Map (interactive)":
    st.sidebar.divider()
    st.sidebar.caption("Flat type filter (map only):")
    st.session_state["map_flat_types"] = st.sidebar.multiselect(
        "Flat types shown on the map", FLAT_ORDER, default=FLAT_ORDER,
    )

st.divider()
CHARTS[selection]()   # draw the chart the user picked


# ---------------------------------------------------------------------------
# Conclusion
# ---------------------------------------------------------------------------
with st.expander("Conclusion", expanded=False):
    st.markdown(
        """
This section set out to test the hypothesis that Singapore's high
homeownership rate hides a real affordability problem underneath it. Going
through the story arc, here is how each chart answers that.

**Chart 1: Prices have been climbing for years.** Median resale prices
went from S\\$410,000 in 2017 to S\\$628,000 by 2025, over 50% higher in eight
years. Prices only stayed flat in 2019, every year after that it kept
going up. This tells us the hypothesis has a clear starting point, the
"asset cost" of a flat really has been getting bigger every year.

**Chart 2: It accelerated sharply after 2020.** The price index shows this
was not just a slow steady climb the whole way, it sped up hard right
after 2020, going from around 130 to over 200 in just five years. So the
hypothesis is not just that prices went up, it is that they went up fast
and recently, which matches when people started actually feeling the
squeeze.

**Chart 3: Every flat type is affected, not just big ones.** Even 3-room
and 4-room flats, the ones most people are actually buying, now sit at or
above the S\\$400,000 line used as the affordability cut-off. This matters
because it shows the hypothesis is not only about fancy big flats getting
pricier, it is the normal, entry-level flats too.

**Chart 4: Affordable flats have basically disappeared.** Back in
2017-2019 almost half the market was still under S\\$400,000. By 2025 that
is down to about 1 in 10 transactions. This is the strongest proof of the
hypothesis, it is not just that flats cost more, it is that the actual
option to buy something affordable has mostly vanished.

**Chart 5: Some towns are far worse than others.** The most expensive
towns are way more expensive than the most affordable ones, but even the
cheapest town in the data is still above the S\\$400,000 line. So the
hypothesis holds everywhere, just to different degrees, there is genuinely
no town left where a flat is cheap anymore.

**Chart 6: Income has not kept up with prices.** This is where we link
back to Member 2's data. Prices grew to an index of over 150 by 2025, but
household income only grew to about 130 in the same time. This is really
the core of the hypothesis, homeownership numbers can look fine on paper,
but if income is not growing as fast as the price of the thing you need to
buy, that is exactly where the financial stress comes from.

**Chart 7 (the interactive map), built from Chart 5.** This map takes the
same idea from Chart 5, that some towns are worse than others, and lets
you actually watch it happen year by year instead of only seeing one
snapshot. You can see the price gap between towns start small in 2017 and
widen every year after 2020, right when Charts 2 and 4 show prices
speeding up and affordable flats disappearing.

**Putting it all together:** going chart by chart against the hypothesis,
Chart 1 agrees, prices really have been climbing for years. Chart 2 agrees
and sharpens it, showing the climb turned into a sprint after 2020. Chart 3
also agrees, and rules out the idea that this is only a big flat problem,
since even the small, entry-level flats got pulled up too. Chart 4 agrees
the strongest out of all of them, since it shows the affordable tier of
the market did not just shrink, it nearly disappeared. Chart 5 agrees but
adds a twist, it is not one uniform squeeze, some towns are hit far worse
than others, though none of them are actually affordable anymore either
way. Chart 6 is really where the hypothesis gets proven, since it is not
just prices going up, it is income failing to keep pace with them, which
is the actual mechanism that turns rising prices into financial stress.
Every chart in this section supports the hypothesis, none of them show
evidence against it. The interactive map (Chart 7) does not add new
evidence on its own, it just lets you explore Chart 5's finding yourself,
year by year, instead of taking our word for it.
"""
    )


# ---------------------------------------------------------------------------
# References
# ---------------------------------------------------------------------------
with st.expander("References"):
    st.markdown(
        """
[1] Singapore House, "Resale prices of HDB flats in Singapore are rising steadily"
https://singapore.house.world/zh/local-info/detail-743.html

[2] HDB, "Further Support for First-Time Homebuyers"
https://www.hdb.gov.sg/hdb-pulse/news/2023/further-support-for-first-time-homebuyers

[3] Straits Times, "HDB resale price growth moderates in Q2, more flats sold"
https://www.straitstimes.com/singapore/housing/hdb-resale-price-growth-moderates-in-q2-more-flats-sold

[4] DollarBack Mortgage, "Is A Smaller Resale HDB Flat In Singapore The Best Start In 2025?"
https://dollarbackmortgage.com/blog/smaller-resale-hdb-flat-best-2025/

[5] PropNex, "Sell Private, Buy Resale HDB: No More 15-Month Wait?"
https://www.propnex.com/picks-details/1075/sell-private-buy-resale-hdb-no-more-15-month-wait

[9] MOM/CPF Occasional Paper, "Adequacy of Singapore's Central Provident Fund Payouts"
mom.gov.sg
"""
    )
