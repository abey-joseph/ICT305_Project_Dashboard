"""
ICT305 - Interactive Data Dashboard | Home

Run from this folder:
    streamlit run app.py

Other sections live in pages/ and appear in the left sidebar.
"""
import streamlit as st

st.set_page_config(page_title="ICT305 Dashboard", page_icon="📊", layout="wide")

# ---------------------------------------------------------------------------
# Team roster - 
# ---------------------------------------------------------------------------
TEAM = [
    ("1", "Joseph Abey",                              "35720739", "Work-Life Balance & Overwork"),
    ("2", "Chew David Zhi Heng",                      "35655813", "Cost of Living & Inflationary Pressures"),
    ("3", "Noorul Fahima Binte Hajasheik Allaudin",   "35522294", "The Housing Premium Bottleneck"),
    ("4", "Lai Soo Seng",                             "35535456", "Sleep Deprivation & Stress Epidemic"),
    ("5", "Poysollameyyar Parthiban",                 "35608819", "Youth Discontent & Future Anxiety"),
]


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("ICT305 B - Interactive Data Dashboard - Team 1")
st.subheader("Singapore's Happy-City Paradox")

st.write(
    "Singapore is ranked among the happiest and wealthiest cities in the world. "
    "This dashboard asks what that headline hides. Across five linked sections it "
    "follows a single chain - from long working hours, to low real pay, to housing "
    "that keeps climbing, to stalled wellbeing, and finally to a youth mental-health "
    "crisis. Each section lets you explore the data behind one link in that chain."
)

st.write(
    "It is built for **strategic, whole-of-government decision support** - aimed at "
    "policymakers and agencies such as MOM, HDB/MND, MOH/HPB, MSF and MOE, who each "
    "own one part of the problem but not the whole picture."
)

st.divider()

# ---------------------------------------------------------------------------
# The team
# ---------------------------------------------------------------------------
st.header("The team")

rows = "\n".join(
    f"| {no} | {name} | {sid} | {section} |"
    for no, name, sid, section in TEAM
)
st.markdown(
    "| Member | Name | Student ID | Section |\n"
    "|---|---|---|---|\n"
    + rows
)

st.divider()
st.caption("Use the sidebar to open each member's section, then the Conclusion for the combined story.")
