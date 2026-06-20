# Contributing guide (for the team)

This dashboard is shared. The **Dashboard Developer** owns `app.py` and the
`src/` framework; **each member owns their own page + data folder**. Following
the conventions below keeps merges clean and the dashboard consistent.

## 1. One-time setup

```bash
git clone <repo-url>
cd ICT305_Project_Dashboard
source "../.venv/bin/activate"     # or create your own: python3 -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

## 2. Your files (don't edit other people's)

You only need to touch:

- `src/config.py` → **your entry only** (your `id` in the `MEMBERS` list).
- `pages/N_Member_N.py` → your page.
- `data/memberN/` → your CSV(s).
- `pages/6_Insights_and_Decision.py` → **only your line** in the `INSIGHTS` dict.

Leave `app.py`, `src/components.py`, `src/data_loader.py`,
`src/page_template.py`, and `src/sample_data.py` to the Dashboard Developer
(raise a request if you need a new shared helper).

## 3. Adding your real data

Put a `.csv` in `data/memberN/`. Make the column names match your `config.py`
entry. Example minimal CSV:

```csv
date,category,metric_a,metric_b
2022-01-01,Group A,123.4,98.1
2022-01-01,Group B,87.0,140.2
```

If your data has different column names, just update `date_col`,
`category_col`, and `metrics` in your `config.py` entry to match — no other code
changes needed.

## 4. Writing insights & decision support

Replace every `TODO` in your page and in the Insights page with real,
evidence-based statements. The rubric rewards findings clearly linked to the
data and to concrete stakeholder decisions.

## 5. Git workflow

```bash
git checkout -b memberN-yourname     # work on your own branch
# ... make changes ...
git add src/config.py pages/N_Member_N.py data/memberN/
git commit -m "memberN: add real data + insights"
git push -u origin memberN-yourname
# open a pull request; Dashboard Developer reviews & merges
```

Avoid committing: the `.venv/`, `__pycache__/`, and `.DS_Store` (already in
`.gitignore`).

## 6. Before submission (checklist)

- [ ] Every section uses real data (no "sample data" banners).
- [ ] All `TODO` placeholders replaced (config, insights, decision support).
- [ ] `GROUP_ID` and topic fields set in `src/config.py`.
- [ ] `streamlit run app.py` works from a clean clone.
- [ ] README instructions verified by someone who didn't build it.
