"""
Synthetic sample-data generator.
================================

Purpose: let the dashboard run end-to-end BEFORE any real data exists, so the
whole team can develop layout and interactions immediately.

Each member's section calls `generate_sample(member_cfg)` and gets back a tidy
DataFrame whose columns match what that member declared in config.py
(date_col, category_col, metrics). When a member drops a real CSV into
data/memberN/, the loader uses that instead and this module is ignored.

The data is deterministic per member (seeded) so charts don't flicker on every
rerun, but each member gets a different-looking dataset.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

# A small generic set of categories so charts have something to segment by.
DEFAULT_CATEGORIES = ["Group A", "Group B", "Group C", "Group D"]


def generate_sample(member_cfg: dict, n_months: int = 84) -> pd.DataFrame:
    """Build a reproducible tidy dataframe for one member.

    Args:
        member_cfg: a member dict from config.MEMBERS
        n_months:   length of the monthly time series (default 84 = 7 years)
    """
    rng = np.random.default_rng(seed=member_cfg["id"] * 100 + 7)

    date_col = member_cfg["date_col"]
    cat_col = member_cfg["category_col"]
    metrics = member_cfg["metrics"]

    dates = pd.date_range("2018-01-01", periods=n_months, freq="MS")
    categories = DEFAULT_CATEGORIES

    rows = []
    for cat_i, cat in enumerate(categories):
        # Each category gets its own baseline level and seasonal strength.
        base = rng.uniform(40, 120) * (1 + 0.25 * cat_i)
        trend = rng.uniform(-0.4, 0.8)          # per-month drift
        season_amp = rng.uniform(5, 25)
        for t, d in enumerate(dates):
            season = season_amp * np.sin(2 * np.pi * (d.month / 12.0))
            noise = rng.normal(0, base * 0.06)
            level = base + trend * t + season + noise
            record = {date_col: d, cat_col: cat}
            for m_i, metric in enumerate(metrics):
                # Give each metric a slightly different scale/shape.
                factor = 1.0 + 0.6 * m_i
                value = max(0.0, level * factor + rng.normal(0, 3))
                record[metric] = round(value, 2)
            rows.append(record)

    df = pd.DataFrame(rows)
    return df
