"""
Member 1's section.
=====================

This page renders the standard 4-part layout (Snapshot, Exploratory analysis,
Insight highlights, Decision support) for Member 1's theme.

HOW TO MAKE IT YOURS
  1. Edit your entry (id=1) in  src/config.py  (name, theme_title, metrics...).
  2. Drop your cleaned CSV into  data/member1/ .
  3. Customise charts/insights below if you want more than the template gives.

The template keeps shared filters + styling so the whole dashboard stays
consistent. To go fully custom, copy the body of
src/page_template.render_member_page() into this file and edit freely.
"""
import streamlit as st

from src import config
from src.page_template import render_member_page

_cfg = config.get_member(1)
st.set_page_config(page_title=_cfg["theme_title"], page_icon=_cfg["emoji"], layout="wide")

render_member_page(member_id=1)
