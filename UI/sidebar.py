"""
ui/sidebar.py — Filter panel rendered in the Streamlit sidebar.
Returns a `filters` dict consumed by the matching logic.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import Any


def _section(label: str):
    st.markdown(f"<div class='sidebar-section'>{label}</div>", unsafe_allow_html=True)


def _unique_sorted(series: pd.Series) -> list:
    """Explode comma-separated values and return sorted unique non-null entries."""
    values = (
        series.dropna()
        .astype(str)
        .str.split(r"[,;/]")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
    )
    return sorted(values)


def render_sidebar(db_trattori: pd.DataFrame, db_macchine: pd.DataFrame) -> dict[str, Any]:
    """Render all filter widgets and return the collected filter dict."""

    with st.sidebar:
        st.markdown(
            "<h2 style='font-family:Fraunces,serif;font-size:1.4rem;"
            "color:#1f3d1a;margin-bottom:0'>⚙️ Parametri di ricerca</h2>",
            unsafe_allow_html=True,
        )

        # ── 1. OPERATIONAL CONTEXT ────────────────────────────────────────
        _section("Contesto operativo")

        colture_options = _unique_sorted(db_macchine.get("Colture di riferimento", pd.Series()))
        colture = st.multiselect(
            "Colture di riferimento",
            options=colture_options,
            placeholder="Tutte le colture",
            help="Seleziona una o più colture. Lascia vuoto per non filtrare.",
        )

        tipo_op_options = _unique_sorted(db_macchine.get("Tipo di operazione", pd.Series()))
        tipo_operazione = st.multiselect(
            "Tipo di operazione",
            options=tipo_op_options,
            placeholder="Tutte le operazioni",
        )

        tipo_macchina_options = _unique_sorted(db_macchine.get("Tipo di macchina", pd.Series()))
        tipo_macchina = st.multiselect(
            "Tipo di macchina",
            options=tipo_macchina_options,
            placeholder="Tutti i tipi",
        )

        # ── 2. TRACTOR REQUIREMENTS ───────────────────────────────────────
        _section("Requisiti trattore")

        trazione_options = ["Qualsiasi"] + _unique_sorted(db_trattori.get("Trazione", pd.Series()))
        trazione = st.selectbox("Trazione", options=trazione_options)

        marchio_options = ["Qualsiasi"] + _unique_sorted(db_trattori.get("Marchio", pd.Series()))
        marchio = st.selectbox("Marchio trattore", options=marchio_options)

        potenza_range = st.slider(
            "Potenza (CV)",
            min_value=0,
            max_value=600,
            value=(40, 200),
            step=5,
            help="Range di potenza del trattore cercato.",
        )

        # ── 3. IMPLEMENT / COUPLING ───────────────────────────────────────
        _section("Attacco e PDP")

        attacco_options = ["Qualsiasi"] + _unique_sorted(
            db_macchine.get("Attacco al trattore", pd.Series())
        )
        attacco = st.selectbox("Attacco al trattore", options=attacco_options)

        cat_3pt_options = ["Qualsiasi"] + _unique_sorted(
            db_macchine.get("Categoria attacco a 3 punti", pd.Series())
        )
        cat_3pt = st.selectbox("Categoria attacco a 3 punti", options=cat_3pt_options)

        pdp_required = st.checkbox("Richiede PDP", value=False)

        # ── 4. WORKING DIMENSIONS ─────────────────────────────────────────
        _section("Dimensioni di lavoro")

        larghezza_lavoro = st.slider(
            "Larghezza di lavoro desiderata (m)",
            min_value=0.0,
            max_value=20.0,
            value=(1.0, 6.0),
            step=0.1,
        )

        with st.expander("Profondità e ingombri (opzionale)"):
            profondita = st.slider(
                "Profondità di lavoro desiderata (cm)",
                min_value=0,
                max_value=80,
                value=(0, 40),
                step=1,
            )
            ingombro_larghezza = st.slider(
                "Ingombro larghezza max (m)",
                min_value=0.0,
                max_value=6.0,
                value=3.0,
                step=0.1,
                help="Larghezza massima ammissibile durante il trasporto su strada.",
            )

        # ── 5. FIELD / TERRAIN ────────────────────────────────────────────
        _section("Campo e terreno")

        raggio_svolta = st.slider(
            "Raggio di svolta max accettabile (m)",
            min_value=1.0,
            max_value=15.0,
            value=8.0,
            step=0.5,
            help="Utile per campi piccoli o con ostacoli.",
        )

        ripiegabile = st.checkbox(
            "Ripiegabile / compattabile",
            value=False,
            help="Mostra solo macchine che si ripiegano per il trasporto.",
        )

        # ── 6. SEARCH BUTTON ──────────────────────────────────────────────
        st.markdown("<br/>", unsafe_allow_html=True)
        search_triggered = st.button("🔍 Cerca", type="primary", use_container_width=True)

        if st.button("↺ Reset filtri", use_container_width=True):
            st.rerun()

    return {
        # operational
        "colture": colture,
        "tipo_operazione": tipo_operazione,
        "tipo_macchina": tipo_macchina,
        # tractor
        "trazione": None if trazione == "Qualsiasi" else trazione,
        "marchio": None if marchio == "Qualsiasi" else marchio,
        "potenza_range": potenza_range,
        # coupling
        "attacco": None if attacco == "Qualsiasi" else attacco,
        "cat_3pt": None if cat_3pt == "Qualsiasi" else cat_3pt,
        "pdp_required": pdp_required,
        # dimensions
        "larghezza_lavoro": larghezza_lavoro,
        "profondita": profondita,
        "ingombro_larghezza": ingombro_larghezza,
        # field
        "raggio_svolta": raggio_svolta,
        "ripiegabile": ripiegabile,
        # control
        "search_triggered": search_triggered,
    }
