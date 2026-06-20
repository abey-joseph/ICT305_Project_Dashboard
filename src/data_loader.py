"""
Data loading layer.
===================

One job: hand each member's section a clean DataFrame.

Priority order:
  1. If a CSV exists in  data/memberN/  -> load the real data.
  2. Otherwise -> fall back to generated sample data (so the app always runs).

Loading is cached with st.cache_data, so files are only read once per session
unless they change. Members do NOT need to touch this file — just drop a CSV
named anything ending in .csv into their data/memberN/ folder.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from src import config
from src.sample_data import generate_sample

# Project root = parent of this src/ folder.
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"


def member_data_dir(member_id: int) -> Path:
    return DATA_DIR / f"member{member_id}"


def _find_csv(member_id: int) -> Path | None:
    """Return the first .csv in the member's data folder, or None."""
    folder = member_data_dir(member_id)
    if not folder.exists():
        return None
    csvs = sorted(folder.glob("*.csv"))
    return csvs[0] if csvs else None


@st.cache_data(show_spinner=False)
def load_member_data(member_id: int) -> tuple[pd.DataFrame, bool]:
    """Load a member's dataset.

    Returns:
        (dataframe, is_real)  where is_real is True if a real CSV was loaded
        and False if sample data was generated.
    """
    cfg = config.get_member(member_id)
    csv_path = _find_csv(member_id)

    if csv_path is not None:
        df = pd.read_csv(csv_path)
        # Parse the date column if present.
        if cfg["date_col"] in df.columns:
            df[cfg["date_col"]] = pd.to_datetime(df[cfg["date_col"]], errors="coerce")
        return df, True

    # No real data yet -> sample data.
    df = generate_sample(cfg)
    return df, False


def get_date_bounds(df: pd.DataFrame, date_col: str):
    """Return (min_date, max_date) as python datetimes, or (None, None)."""
    if date_col not in df.columns or df[date_col].isna().all():
        return None, None
    return df[date_col].min().to_pydatetime(), df[date_col].max().to_pydatetime()
