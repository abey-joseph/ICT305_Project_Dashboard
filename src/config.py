"""
Central configuration for the ICT305 Project Dashboard.
=======================================================

This is the ONE place the team edits to brand the dashboard.

WHAT TO CHANGE (per member):
  - Open the MEMBERS list below.
  - Find your member id (1-5) and update:
       name        -> your real name
       theme_title -> your sub-topic / theme name
       subtitle    -> one line describing what your section covers
       metrics     -> the numeric columns your dataset will have (see note)
  - That's it. Your page picks up these values automatically.

The `metrics`, `category_col` and `date_col` fields drive BOTH the sample-data
generator (so the app runs before real data exists) AND the real-data loader.
Once you drop a real CSV into  data/memberN/  with matching column names,
the dashboard switches to your real data with no code changes.
"""

# ---------------------------------------------------------------------------
# Project-level identity
# ---------------------------------------------------------------------------
APP_TITLE = "ICT305 — Interactive Data Dashboard"
APP_ICON = "📊"
UNIT_CODE = "ICT305"
GROUP_ID = "GroupID"  # TODO: replace with your real group id for submission

# Project topic for Assignment 2 is still being decided. Update this line once
# the team locks the topic; it shows on the Overview page.
PROJECT_TOPIC = "TODO: Team to confirm Assignment 2 topic"
PROJECT_STAKEHOLDER = "TODO: define primary stakeholder group"
DECISION_CONTEXT = "TODO: Strategic / Tactical / Operational"

# ---------------------------------------------------------------------------
# Shared colour palette (consistent encoding across every member's charts)
# ---------------------------------------------------------------------------
PALETTE = [
    "#2563EB",  # blue
    "#16A34A",  # green
    "#EA580C",  # orange
    "#9333EA",  # purple
    "#DC2626",  # red
    "#0891B2",  # cyan
    "#CA8A04",  # amber
]
ACCENT = "#2563EB"
GOOD = "#16A34A"
WARN = "#EA580C"
BAD = "#DC2626"

# ---------------------------------------------------------------------------
# Member roster  (edit your own entry)
# ---------------------------------------------------------------------------
# Each member's dataset is assumed to be "tidy": one row per observation, with
#   - a date column      (date_col)
#   - a category column  (category_col)  e.g. region / segment / product
#   - one or more numeric metric columns (metrics)
# Adjust these to match whatever your real dataset looks like.

MEMBERS = [
    {
        "id": 1,
        "name": "Member 1",
        "theme_title": "Theme 1",
        "subtitle": "TODO: one-line description of this section's data & purpose",
        "emoji": "📈",
        "color": PALETTE[0],
        "date_col": "date",
        "category_col": "category",
        "metrics": ["metric_a", "metric_b"],
    },
    {
        "id": 2,
        "name": "Member 2",
        "theme_title": "Theme 2",
        "subtitle": "TODO: one-line description of this section's data & purpose",
        "emoji": "📊",
        "color": PALETTE[1],
        "date_col": "date",
        "category_col": "category",
        "metrics": ["metric_a", "metric_b"],
    },
    {
        "id": 3,
        "name": "Member 3",
        "theme_title": "Theme 3",
        "subtitle": "TODO: one-line description of this section's data & purpose",
        "emoji": "🗺️",
        "color": PALETTE[2],
        "date_col": "date",
        "category_col": "category",
        "metrics": ["metric_a", "metric_b"],
    },
    {
        "id": 4,
        "name": "Member 4",
        "theme_title": "Theme 4",
        "subtitle": "TODO: one-line description of this section's data & purpose",
        "emoji": "🔬",
        "color": PALETTE[3],
        "date_col": "date",
        "category_col": "category",
        "metrics": ["metric_a", "metric_b"],
    },
    {
        "id": 5,
        "name": "Member 5",
        "theme_title": "Theme 5",
        "subtitle": "TODO: one-line description of this section's data & purpose",
        "emoji": "🏥",
        "color": PALETTE[4],
        "date_col": "date",
        "category_col": "category",
        "metrics": ["metric_a", "metric_b"],
    },
]


def get_member(member_id: int) -> dict:
    """Return the config dict for a given member id (1-5)."""
    for m in MEMBERS:
        if m["id"] == member_id:
            return m
    raise ValueError(f"No member with id={member_id} in config.MEMBERS")
