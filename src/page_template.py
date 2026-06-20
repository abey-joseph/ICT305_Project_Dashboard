"""
Standard per-member page template.
==================================

This renders ONE member's full section with the four required dashboard
sub-sections, all driven by the same linked filters:

    1. KPIs / snapshot          (Overview)
    2. Exploratory analysis     (compare, distribution, relationship)
    3. Insight highlights       (annotated takeaways)
    4. Decision support         (what to do with it)

Each member's page file (pages/N_Member_N.py) is just two lines:

    from src.page_template import render_member_page
    render_member_page(member_id=N)

WHAT MEMBERS CUSTOMISE:
  - Charts: pick/adjust the chart calls in the Exploratory section to suit
    your data and analytical question.
  - Insights: replace the placeholder bullet text with YOUR real findings.
  - Decision support: write the concrete decisions your section enables.
You can keep using this template, or copy its body into your page file and edit
freely. Either way the shared filters & styling keep the dashboard consistent.
"""
from __future__ import annotations

import streamlit as st

from src import components as ui
from src import config
from src.data_loader import load_member_data


def render_member_page(member_id: int) -> None:
    cfg = config.get_member(member_id)

    st.title(f"{cfg['emoji']} {cfg['theme_title']}")
    st.caption(cfg["subtitle"])

    # ---- Load data (real CSV if present, else sample) --------------------
    df, is_real = load_member_data(member_id)
    if not is_real:
        st.info(
            "📦 Showing **sample data**. Drop your cleaned CSV into "
            f"`data/member{member_id}/` (columns: "
            f"`{cfg['date_col']}`, `{cfg['category_col']}`, "
            f"`{', '.join(cfg['metrics'])}`) to switch to real data.",
            icon="ℹ️",
        )

    # ---- Linked filters (sidebar) ---------------------------------------
    sel = ui.sidebar_filters(df, cfg, key_prefix=f"m{member_id}")
    fdf = ui.apply_filters(df, cfg, sel)
    metric = sel.get("metric", cfg["metrics"][0])

    if fdf.empty:
        st.warning("No data for the current filter selection. Widen your filters.")
        return

    # ---- 1. KPIs / snapshot ---------------------------------------------
    ui.section_header("1 · Snapshot", "Headline numbers for the current selection.")
    total = fdf[metric].sum()
    avg = fdf[metric].mean()
    latest = (
        fdf.sort_values(cfg["date_col"])[metric].iloc[-1]
        if cfg["date_col"] in fdf.columns else fdf[metric].iloc[-1]
    )
    n_cats = fdf[cfg["category_col"]].nunique() if cfg["category_col"] in fdf.columns else 0
    ui.kpi_row([
        {"label": f"Total {metric}", "value": f"{total:,.0f}"},
        {"label": f"Average {metric}", "value": f"{avg:,.1f}"},
        {"label": f"Latest {metric}", "value": f"{latest:,.1f}"},
        {"label": f"{cfg['category_col'].title()} count", "value": n_cats},
    ])

    st.divider()

    # ---- 2. Exploratory analysis ----------------------------------------
    ui.section_header(
        "2 · Exploratory analysis",
        "Trend, comparison, distribution — all respond to the sidebar filters.",
    )
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(ui.line_trend(fdf, cfg, metric), use_container_width=True)
    with c2:
        st.plotly_chart(ui.bar_compare(fdf, cfg, metric), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(ui.distribution_box(fdf, cfg, metric), use_container_width=True)
    with c4:
        metrics_present = [m for m in cfg["metrics"] if m in fdf.columns]
        if len(metrics_present) >= 2:
            x_m, y_m = metrics_present[0], metrics_present[1]
            st.plotly_chart(
                ui.scatter_relationship(fdf, cfg, x_m, y_m), use_container_width=True
            )
        else:
            st.caption("Add a second metric in config.py to enable the relationship view.")

    st.divider()

    # ---- 3. Insight highlights ------------------------------------------
    ui.section_header(
        "3 · Insight highlights",
        "Replace these placeholders with YOUR evidence-based findings.",
    )
    top_cat = (
        fdf.groupby(cfg["category_col"])[metric].mean().idxmax()
        if cfg["category_col"] in fdf.columns else "—"
    )
    st.markdown(
        f"""
- **Leading {cfg['category_col']}:** *{top_cat}* shows the highest average **{metric}** in the current view.
- **TODO — Insight 2:** describe a trend or pattern you observe over time.
- **TODO — Insight 3:** note any outlier, anomaly, or surprising relationship.
"""
    )

    st.divider()

    # ---- 4. Decision support --------------------------------------------
    ui.section_header(
        "4 · Decision support",
        "How a stakeholder should act on this section.",
    )
    st.markdown(
        """
- **Decision enabled:** *TODO — what decision can a stakeholder make from this section?*
- **How to use it:** filter to the relevant period / segment, then read the trend + comparison together.
- **Recommended action:** *TODO — the concrete next step the data points to.*
"""
    )

    with st.expander("ℹ️ Data source & notes"):
        st.write(f"Rows in view: **{len(fdf):,}**  |  Source: "
                 f"{'real CSV' if is_real else 'generated sample data'}")
