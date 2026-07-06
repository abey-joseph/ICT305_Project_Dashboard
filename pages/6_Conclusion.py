"""
Conclusion - combined insights across all five member sections.

This page ties the M1 to M5 chain together. It reuses the data each member
already presented and adds two synthesis charts, the indexed timeline and the
causal-chain diagram, plus the written Big Idea and recommendations.
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Conclusion", layout="wide")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROC = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_master():
    df = pd.read_csv(PROC / "master_clean.csv")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    return df


master = load_master()

st.title("Conclusion: The Whole Story, M1 to M5")

st.markdown(
    """
Each member looked at one slice of Singapore life. On their own, each slice is a
fair point. Put together, they form a single chain that explains why a country
ranked among the happiest in the world has a youth mental-health crisis hidden
inside it.
"""
)

st.subheader("The Storyboard, Member by Member")
st.markdown(
    """
| Stage | Member | What they showed |
|---|---|---|
| The setup | M1 Work-Life | Singaporeans work long hours, over 41 a week on average, most doing 40 or more |
| The catch | M2 Cost of Living | Headline GDP per capita is high, but the median person only sees a fraction of it |
| The squeeze | M3 Housing | Even that low real pay cannot keep up with housing. Resale prices rose about 50% in eight years and affordable flats nearly vanished |
| The strain | M4 Sleep and Happiness | Under that pressure, national happiness stopped rising after 2014 and Singapore sits below peer "happy" countries |
| The endpoint | M5 Youth | The accumulated pressure lands hardest on the young. In 2024, one in four deaths among 10 to 19 year-olds was suicide |

The two charts below bring these five threads into one view. We keep this to
synthesis, reusing the data each member already presented rather than running
new analysis.
"""
)


# ---------------------------------------------------------------------------
# Synthesis 1 - indexed timeline
# ---------------------------------------------------------------------------
st.subheader("Synthesis 1: More Expensive, Not Happier")

metrics = {
    "Working hours (M1)":    ("m1_mean_weekly_hours", "#8A8D91"),
    "GDP-income gap (M2)":   ("m2_gdp_vs_income_gap_x", "#E8A33D"),
    "HDB resale price (M3)": ("m3_hdb_resale_price_index", "#D1495B"),
    "Happiness (M4)":        ("m4_life_ladder", "#5B8C5A"),
}
cols = [c for c, _ in metrics.values()]
common = master[["year"] + cols].dropna().sort_values("year")
base = common.iloc[0]

fig1 = go.Figure()
for label, (col, colour) in metrics.items():
    fig1.add_trace(go.Scatter(
        x=common["year"], y=common[col] / base[col] * 100,
        name=label, mode="lines+markers", line=dict(color=colour, width=3),
        hovertemplate=label + "<br>%{x}: %{y:.0f}<extra></extra>",
    ))
fig1.add_hline(y=100, line_dash="dot", line_color="#999",
               annotation_text=f"Baseline ({int(base['year'])} = 100)",
               annotation_position="bottom right")
fig1.update_layout(
    title=f"Indexed to {int(base['year'])} = 100: Housing Ran Away While Happiness Stayed Flat",
    xaxis_title="Year", yaxis_title="Index (base year = 100)",
    template="plotly_white", margin=dict(l=40, r=40, t=70, b=40),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
)
st.plotly_chart(fig1, use_container_width=True)

hdb_end = (common["m3_hdb_resale_price_index"].iloc[-1] / base["m3_hdb_resale_price_index"] - 1) * 100
happ_end = (common["m4_life_ladder"].iloc[-1] / base["m4_life_ladder"] - 1) * 100

st.markdown(
    f"""
**Reading the chart:** By the end of the window, the HDB resale price index is
about {hdb_end:.0f}% above its starting level, the steepest line by far. Working
hours drifted down slightly. Happiness barely moved, ending only about
{happ_end:.0f}% above where it started. The honest headline is not that
happiness collapsed, it is that life became far more expensive without becoming
any happier.

**Why this matters:** A country that is genuinely getting better off would
expect happiness to rise as the economy grows. Instead the economic pressure
lines climb while the happiness line sits flat. That gap, expensive but not
happier, is the space where the youth crisis in Member 5 grows.
"""
)


# ---------------------------------------------------------------------------
# Synthesis 2 - causal chain diagram
# ---------------------------------------------------------------------------
st.subheader("Synthesis 2: The Causal Chain in One Diagram")

steps = [
    ("M1  Long working hours", "Over 41 hours a week, most work 40+", "#2A6FBB"),
    ("M2  But low real pay", "GDP looks high, the median sees a fraction", "#E8A33D"),
    ("M3  Housing out of reach", "Resale prices up ~50%, affordable flats vanish", "#D1495B"),
    ("M4  Happiness stalls", "No rise since 2014, below peer countries", "#5B8C5A"),
    ("M5  Youth pay the cost", "1 in 4 deaths of 10-19 year-olds is suicide", "#6B2737"),
]

fig2 = go.Figure()
n = len(steps)
for i, (title, sub, colour) in enumerate(steps):
    y = n - i
    fig2.add_shape(type="rect", x0=0.1, x1=0.9, y0=y - 0.4, y1=y + 0.4,
                   line=dict(color=colour, width=2), fillcolor=colour, opacity=0.15)
    fig2.add_annotation(x=0.5, y=y + 0.12, text=f"<b>{title}</b>", showarrow=False,
                        font=dict(size=14, color=colour))
    fig2.add_annotation(x=0.5, y=y - 0.18, text=sub, showarrow=False,
                        font=dict(size=11, color="#333"))
    if i < n - 1:
        fig2.add_annotation(x=0.5, y=y - 0.5, ax=0.5, ay=y - 0.42,
                            xref="x", yref="y", axref="x", ayref="y",
                            showarrow=True, arrowhead=2, arrowsize=1.5,
                            arrowwidth=2, arrowcolor="#666")
fig2.update_layout(
    title="The Chain: From the Daily Grind to the Human Cost",
    xaxis=dict(visible=False, range=[0, 1]),
    yaxis=dict(visible=False, range=[0.3, n + 0.7]),
    template="plotly_white", height=560, margin=dict(l=20, r=20, t=60, b=20),
    showlegend=False,
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    """
**Reading the diagram:** Read top to bottom. Long hours feed into low real pay,
which cannot keep up with housing, which adds to the pressure that keeps
happiness flat, which lands hardest on the young. Each box is one member's
finding. The arrows are the argument that ties them together. No single ministry
owns the whole chain, which is exactly why it stays unsolved.
"""
)


# ---------------------------------------------------------------------------
# Big Idea and Recommendations
# ---------------------------------------------------------------------------
st.subheader("Big Idea and Recommendations")

st.markdown(
    """
**Big Idea:** Singapore is ranked one of the happiest cities in the world, but
that ranking is a national average that hides a connected chain of pressures.
Long working hours and low real pay meet housing that keeps climbing, wellbeing
stops improving, and the accumulated strain surfaces as a youth mental-health
crisis, where one in four deaths of 10 to 19 year-olds is a suicide. The
happy-city headline is true on average and misleading in detail.

**Recommendations, by stakeholder:**

- **Ministry of Manpower:** treat working hours as a wellbeing indicator, not
  only a productivity one. The long-hours culture is the first link in the chain.
- **Ministry of Trade and Industry and MAS:** report a median-income measure
  alongside GDP per capita. The headline number overstates what most residents
  actually have.
- **HDB and Ministry of National Development:** affordability is not
  self-correcting. Pair housing-grant policy with income measures rather than
  treating it as a housing-only problem.
- **MOH, IMH, MOE and HPB:** make youth mental health a primary, measured
  priority. Add a mental-health measure to routine primary-care reporting so the
  burden is visible before it reaches the mortality data.
- **Whole-of-government:** treat these indicators as one linked dashboard.
  Because the pressures are correlated, moving one lever should be expected to
  move the others.

**What we are not claiming:** the data shows association, not proof of cause.
Happiness did not collapse, it stalled, and the youth suicide projection is
illustrative because only one detailed year of age-by-cause data is available.
The strength of the argument is not any single number, it is that every member's
slice points the same way and the metrics move together.
"""
)
