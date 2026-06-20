# ICT305 — Interactive Data Dashboard

Base Streamlit template for the group project. It's intentionally empty — each
member fills in their own section.

## Run

```bash
source ../.venv/bin/activate      # or your own venv
pip install -r requirements.txt   # first time only
streamlit run app.py
```

## Structure

```
app.py                 # Home — team & project intro
pages/
  1_Member_1.py ... 5_Member_5.py   # one section per member
  6_Conclusion.py                   # combined insights & conclusion
data/member1 ... member5/           # each member's dataset files
```

## Who does what

- **Home (`app.py`)** — team intro (shared).
- **Your page (`pages/N_Member_N.py`)** — add your own filters, controls, charts.
- **Your data (`data/memberN/`)** — drop your dataset files here.
- **Conclusion (`pages/6_Conclusion.py`)** — team writes the combined conclusion.
