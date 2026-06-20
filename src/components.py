"""
Reusable UI + chart components.
===============================

Shared building blocks so every member's page looks and behaves consistently
(a core marking criterion: "Consistency of Interaction" & "Consistency of
design"). Use these instead of hand-rolling widgets on each page.

Contents:
  - section_header()      : titled section divider
  - kpi_row()             : a row of KPI metric cards
  - sidebar_filters()     : the 3+ linked interactive controls (returns choices)
  - apply_filters()       : apply those choices to a dataframe
  - line_trend()          : time-series line chart (Plotly)
  - bar_compare()         : category comparison bar chart (Plotly)
  - distribution_box()    : distribution / outlier box plot (Plotly)
  - scatter_relationship(): relationship / correlation scatter (Plotly)
"""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src import config
from src.data_loader import get_date_bounds


# ---------------------------------------------------------------------------
# Layout helpers
# ---------------------------------------------------------------------------
def section_header(title: str, description: str = "") -> None:
    st.markdown(f"### {title}")
    if description:
        st.caption(description)


def kpi_row(kpis: list[dict]) -> None:
    """Render a row of KPI cards.

    Each kpi dict: {"label": str, "value": str|number, "delta": optional str}
    """
    cols = st.columns(len(kpis))
    for col, kpi in zip(cols, kpis):
        col.metric(
            label=kpi["label"],
            value=kpi["value"],
            delta=kpi.get("delta"),
        )


# ---------------------------------------------------------------------------
# Interactive controls (the linked filters)  -- REQUIRED: >= 3 controls
# ---------------------------------------------------------------------------
def sidebar_filters(df: pd.DataFrame, cfg: dict, key_prefix: str) -> dict:
    """Render the standard linked filter controls in the sidebar.

    Returns a dict of the user's selections. The SAME selections are applied to
    every chart on the page (via apply_filters), so all visuals update together.

    Controls provided (satisfies the >=3 interactive-control requirement):
      1. Date-range slider        (temporal filtering)
      2. Category multi-select    (categorical filtering)
      3. Metric selector          (radio - choose which measure to analyse)
    """
    date_col = cfg["date_col"]
    cat_col = cfg["category_col"]
    metrics = cfg["metrics"]

    st.sidebar.markdown(f"#### {cfg['emoji']} {cfg['theme_title']} — Filters")

    selections: dict = {}

    # 1) Date range slider
    dmin, dmax = get_date_bounds(df, date_col)
    if dmin and dmax:
        date_range = st.sidebar.slider(
            "Date range",
            min_value=dmin,
            max_value=dmax,
            value=(dmin, dmax),
            format="MMM YYYY",
            key=f"{key_prefix}_date",
        )
        selections["date_range"] = date_range

    # 2) Category multi-select
    if cat_col in df.columns:
        cats = sorted(df[cat_col].dropna().unique().tolist())
        chosen = st.sidebar.multiselect(
            f"{cat_col.title()}",
            options=cats,
            default=cats,
            key=f"{key_prefix}_cats",
        )
        selections["categories"] = chosen

    # 3) Metric selector
    available_metrics = [m for m in metrics if m in df.columns]
    if available_metrics:
        metric = st.sidebar.radio(
            "Metric to analyse",
            options=available_metrics,
            key=f"{key_prefix}_metric",
        )
        selections["metric"] = metric

    return selections


def apply_filters(df: pd.DataFrame, cfg: dict, sel: dict) -> pd.DataFrame:
    """Apply sidebar selections to the dataframe. Used by ALL charts so the
    page behaves as one linked analytical system."""
    out = df.copy()
    date_col = cfg["date_col"]
    cat_col = cfg["category_col"]

    if "date_range" in sel and date_col in out.columns:
        start, end = sel["date_range"]
        out = out[(out[date_col] >= pd.Timestamp(start)) & (out[date_col] <= pd.Timestamp(end))]

    if "categories" in sel and cat_col in out.columns:
        out = out[out[cat_col].isin(sel["categories"])]

    return out


# ---------------------------------------------------------------------------
# Chart helpers  (Plotly = interactive: hover, zoom, legend toggle)
# ---------------------------------------------------------------------------
def _style(fig, color_seq=None):
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=380,
    )
    return fig


def line_trend(df: pd.DataFrame, cfg: dict, metric: str):
    """Trend over time, one line per category."""
    date_col, cat_col = cfg["date_col"], cfg["category_col"]
    g = df.groupby([date_col, cat_col], as_index=False)[metric].mean()
    fig = px.line(
        g, x=date_col, y=metric, color=cat_col,
        color_discrete_sequence=config.PALETTE,
        title=f"{metric} over time",
    )
    return _style(fig)


def bar_compare(df: pd.DataFrame, cfg: dict, metric: str):
    """Compare the metric across categories (mean)."""
    cat_col = cfg["category_col"]
    g = df.groupby(cat_col, as_index=False)[metric].mean().sort_values(metric, ascending=False)
    fig = px.bar(
        g, x=cat_col, y=metric,
        color=cat_col, color_discrete_sequence=config.PALETTE,
        title=f"Average {metric} by {cat_col}",
    )
    fig.update_layout(showlegend=False)
    return _style(fig)


def distribution_box(df: pd.DataFrame, cfg: dict, metric: str):
    """Distribution / outlier view per category."""
    cat_col = cfg["category_col"]
    fig = px.box(
        df, x=cat_col, y=metric, color=cat_col,
        color_discrete_sequence=config.PALETTE,
        title=f"Distribution of {metric} by {cat_col}",
        points="outliers",
    )
    fig.update_layout(showlegend=False)
    return _style(fig)


def scatter_relationship(df: pd.DataFrame, cfg: dict, x_metric: str, y_metric: str):
    """Relationship between two metrics (if the dataset has >=2 metrics)."""
    cat_col = cfg["category_col"]
    fig = px.scatter(
        df, x=x_metric, y=y_metric, color=cat_col,
        color_discrete_sequence=config.PALETTE,
        trendline="ols" if _has_statsmodels() else None,
        title=f"{y_metric} vs {x_metric}",
    )
    return _style(fig)


def _has_statsmodels() -> bool:
    try:
        import statsmodels  # noqa: F401
        return True
    except Exception:
        return False
