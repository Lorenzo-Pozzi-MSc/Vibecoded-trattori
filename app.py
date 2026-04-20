"""
AgriSelector — Tractor & Implement Matching Tool
Entry point. Run with: streamlit run app.py
"""

import streamlit as st
from pathlib import Path

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="AgriSelector",
    page_icon="🚜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Local imports ────────────────────────────────────────────────────────────
from ui.styles import inject_css
from ui.sidebar import render_sidebar
from ui.results import render_results
from data.loader import load_databases
from logic.matcher import run_matching

# ── Boot ─────────────────────────────────────────────────────────────────────
inject_css()

# ── Load data (cached) ───────────────────────────────────────────────────────
db_trattori, db_macchine = load_databases()

# ── Sidebar: user inputs ─────────────────────────────────────────────────────
filters = render_sidebar(db_trattori, db_macchine)

# ── Main area header ─────────────────────────────────────────────────────────
col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.markdown("<div class='logo'>🚜</div>", unsafe_allow_html=True)
with col_title:
    st.markdown("<h1 class='main-title'>AgriSelector</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='main-subtitle'>Trova il trattore e le macchine agricole giusti per la tua azienda</p>",
        unsafe_allow_html=True,
    )

st.markdown("<hr class='divider'/>", unsafe_allow_html=True)

# ── Run matching & render results ────────────────────────────────────────────
if filters.get("search_triggered"):
    with st.spinner("Analisi in corso…"):
        results = run_matching(db_trattori, db_macchine, filters)
    render_results(results, filters)
else:
    st.markdown(
        """
        <div class='empty-state'>
            <span class='empty-icon'>🌾</span>
            <h3>Imposta i tuoi criteri nel pannello laterale</h3>
            <p>Seleziona coltura, tipo di operazione e parametri del terreno,<br>
            poi clicca <strong>Cerca</strong> per trovare i mezzi più adatti.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
