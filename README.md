# ICT305 — Interactive Data Dashboard

A Python (Streamlit) interactive dashboard for the ICT305 group project. The app
is built as **one integrated dashboard with one section per team member**, so the
five themes combine into a single decision-support tool rather than five separate
charts.

> **Status:** Base scaffold ready. The Assignment 2 topic is still being decided,
> so every section currently runs on **generated sample data** — the app works
> end-to-end today. Each member swaps in their real data when ready (no code
> changes needed).

---

## Quick start

From inside this folder (`ICT305_Project_Dashboard/`):

```bash
# 1. Activate the shared virtual environment (already created one level up)
source "../.venv/bin/activate"        # macOS/Linux
# ..\.venv\Scripts\Activate.ps1       # Windows PowerShell

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Run the dashboard
streamlit run app.py
```

The app opens at <http://localhost:8501>. Use the **left sidebar** to move
between the Overview and each member's section. Each section's filters live in
the sidebar and update all of that section's charts together.

---

## Project structure

```
ICT305_Project_Dashboard/
├── app.py                      # HOME = Overview / Executive Summary (section 1)
├── requirements.txt
├── .streamlit/config.toml      # shared theme (colours, layout)
├── src/                        # shared code — owned by the Dashboard Developer
│   ├── config.py               # ⭐ EVERY member edits their entry here
│   ├── data_loader.py          # loads real CSV, falls back to sample data
│   ├── sample_data.py          # synthetic data so the app always runs
│   ├── components.py           # KPI cards, filters, chart helpers (shared)
│   └── page_template.py        # standard per-member layout
├── pages/                      # one file per section (appear in sidebar)
│   ├── 1_Member_1.py … 5_Member_5.py
│   └── 6_Insights_and_Decision.py   # Insight Highlights + Decision Support (3 & 4)
├── data/
│   └── member1 … member5/      # ⭐ each member drops their cleaned CSV here
└── docs/CONTRIBUTING.md        # step-by-step guide for teammates
```

---

## Each member's checklist

1. **Edit `src/config.py`** → find your `id` (1–5) and set your `name`,
   `theme_title`, `subtitle`, and `metrics` / `category_col` / `date_col`.
2. **Drop your cleaned CSV** into `data/memberN/` with columns matching step 1.
3. **Run the app** and open your section — it now shows your real data.
4. **Write your insights** (section 3) and **decision support** (section 4) by
   replacing the `TODO` placeholders in your page / the Insights page.
5. Customise charts in your `pages/N_Member_N.py` if you want more than the
   template provides.

See `docs/CONTRIBUTING.md` for the detailed walkthrough and git workflow.

---

## How this maps to the assignment requirements

| Requirement | Where it lives |
|---|---|
| Overview / Executive Summary | `app.py` (home) |
| Exploratory Analysis | each member section (trend, comparison, distribution, relationship) |
| Insight Highlights | each member section + `pages/6_Insights_and_Decision.py` |
| Decision Support | each member section + `pages/6_Insights_and_Decision.py` |
| ≥ 3 interactive controls | date-range slider + category multiselect + metric selector (per section) |
| Linked / dynamic visuals | all charts in a section share one filter state |
| Consistency of interaction | shared `components.py` + `page_template.py` |
| Python only (pandas / plotly / streamlit) | `requirements.txt` |

---

## AI Use Statement (placeholder — finalise for the report)

> AI tools were used in a limited, supporting role to scaffold the dashboard
> framework and for code structuring/debugging. All datasets, analysis,
> visualisations, insights, and conclusions are the team's own work.
