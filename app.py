"""
ICT305 — Interactive Data Dashboard | Home

Run from this folder:
    streamlit run app.py

Other sections live in pages/ and appear in the left sidebar.
"""
import streamlit as st

st.set_page_config(page_title="ICT305 Dashboard", page_icon="📊", layout="wide")

st.title("ICT305 — Interactive Data Dashboard")

st.header("About the team")
st.write("TODO: introduce the team and member roles.")

st.header("About this project")
st.write("TODO: describe the topic, stakeholders, and what this dashboard does.")

st.divider()
st.caption("Use the sidebar to open each member's section.")
