"""
ui/styles.py — Custom CSS for AgriSelector
Aesthetic: industrial-agrarian. Earthy greens, warm off-whites, strong typography.
"""

import streamlit as st


CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root variables ─────────────────────────────────────────── */
:root {
    --green-dark:   #1f3d1a;
    --green-mid:    #3a6b2e;
    --green-light:  #6b9c54;
    --green-pale:   #d6e8cc;
    --earth:        #8b6340;
    --wheat:        #e8d5a3;
    --cream:        #f7f3ec;
    --text-dark:    #1a1a14;
    --text-mid:     #4a4a3a;
    --text-light:   #7a7a68;
    --border:       #d0c8b8;
    --shadow:       rgba(31,61,26,0.12);
    --card-bg:      #ffffff;
    --sidebar-bg:   #f0ebe0;
}

/* ── Global reset & base ────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text-dark) !important;
}

.stApp {
    background-color: var(--cream) !important;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%233a6b2e' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* ── Sidebar ────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--sidebar-bg) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.5rem;
}

/* ── Main title ─────────────────────────────────────────────── */
.logo {
    font-size: 3rem;
    padding-top: 0.3rem;
}

h1.main-title {
    font-family: 'Fraunces', serif !important;
    font-size: 2.8rem !important;
    font-weight: 700 !important;
    color: var(--green-dark) !important;
    margin-bottom: 0 !important;
    line-height: 1.1 !important;
}

p.main-subtitle {
    color: var(--text-mid) !important;
    font-size: 1.05rem !important;
    font-weight: 300 !important;
    margin-top: 0.3rem !important;
}

hr.divider {
    border: none !important;
    border-top: 2px solid var(--green-pale) !important;
    margin: 1rem 0 1.5rem 0 !important;
}

/* ── Sidebar section headers ────────────────────────────────── */
.sidebar-section {
    font-family: 'Fraunces', serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--green-mid);
    margin: 1.4rem 0 0.5rem 0;
    padding-bottom: 0.25rem;
    border-bottom: 1px solid var(--green-pale);
}

/* ── Empty state ────────────────────────────────────────────── */
.empty-state {
    text-align: center;
    padding: 5rem 2rem;
    color: var(--text-light);
}

.empty-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 1rem;
    filter: grayscale(30%);
}

.empty-state h3 {
    font-family: 'Fraunces', serif;
    font-size: 1.5rem;
    color: var(--text-mid);
    margin-bottom: 0.5rem;
}

.empty-state p {
    font-size: 0.95rem;
    line-height: 1.6;
}

/* ── Results section headers ────────────────────────────────── */
.results-header {
    font-family: 'Fraunces', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--green-dark);
    margin-bottom: 0.25rem;
}

.results-count {
    font-size: 0.85rem;
    color: var(--text-light);
    margin-bottom: 1.2rem;
    font-weight: 400;
}

/* ── Result cards ───────────────────────────────────────────── */
.card {
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 2px 8px var(--shadow);
    transition: box-shadow 0.2s ease, transform 0.15s ease;
    position: relative;
    overflow: hidden;
}

.card:hover {
    box-shadow: 0 6px 20px var(--shadow);
    transform: translateY(-1px);
}

.card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, var(--green-mid), var(--green-light));
    border-radius: 10px 0 0 10px;
}

.card-tractor::before { background: linear-gradient(180deg, var(--green-dark), var(--green-mid)); }
.card-machine::before { background: linear-gradient(180deg, var(--earth), #c49a6c); }

.card-title {
    font-family: 'Fraunces', serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--green-dark);
    margin-bottom: 0.15rem;
}

.card-brand {
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--green-light);
    margin-bottom: 0.7rem;
}

.card-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin-top: 0.5rem;
}

.tag {
    display: inline-block;
    background: var(--green-pale);
    color: var(--green-dark);
    border-radius: 4px;
    padding: 0.15rem 0.5rem;
    font-size: 0.72rem;
    font-weight: 500;
}

.tag-earth {
    background: #efe0cc;
    color: var(--earth);
}

.card-link {
    font-size: 0.8rem;
    color: var(--green-mid);
    text-decoration: none;
    font-weight: 500;
}

.card-link:hover { text-decoration: underline; }

/* ── Match score badge ──────────────────────────────────────── */
.score-badge {
    position: absolute;
    top: 1rem; right: 1rem;
    background: var(--green-dark);
    color: white;
    border-radius: 20px;
    padding: 0.2rem 0.65rem;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.04em;
}

/* ── No results ─────────────────────────────────────────────── */
.no-results {
    background: #fff8f0;
    border: 1px solid var(--wheat);
    border-radius: 10px;
    padding: 2rem;
    text-align: center;
    color: var(--earth);
}

/* ── Streamlit widget overrides ─────────────────────────────── */
div[data-testid="stSelectbox"] label,
div[data-testid="stMultiSelect"] label,
div[data-testid="stSlider"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stNumberInput"] label {
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    color: var(--text-dark) !important;
}

.stButton > button {
    background: var(--green-dark) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 2rem !important;
    width: 100% !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s ease !important;
}

.stButton > button:hover {
    background: var(--green-mid) !important;
}

/* Reset button */
.stButton.reset > button {
    background: transparent !important;
    color: var(--text-light) !important;
    border: 1px solid var(--border) !important;
}

/* ── Tabs ───────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    border-bottom: 2px solid var(--green-pale) !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
}

.stTabs [aria-selected="true"] {
    color: var(--green-dark) !important;
    border-bottom-color: var(--green-dark) !important;
}

/* ── Info boxes ─────────────────────────────────────────────── */
div[data-testid="stInfo"] {
    background: var(--green-pale) !important;
    border-left-color: var(--green-mid) !important;
}

/* ── Expander ───────────────────────────────────────────────── */
details summary {
    font-weight: 500;
    color: var(--green-mid) !important;
}
"""


def inject_css():
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True)
