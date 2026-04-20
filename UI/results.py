"""
ui/results.py — Renders matched tractors and implements as cards.
"""

from __future__ import annotations
import streamlit as st
import pandas as pd
from typing import Any


def _tag(text: str, earth: bool = False) -> str:
    cls = "tag tag-earth" if earth else "tag"
    return f"<span class='{cls}'>{text}</span>"


def _card_tractor(row: pd.Series) -> str:
    nome = row.get("Nome serie/modello", "—")
    marchio = row.get("Marchio", "")
    pot_min = row.get("Pot. min (CV)", "")
    pot_max = row.get("Pot. max (CV)", "")
    trazione = row.get("Trazione", "")
    cat_3pt = row.get("Categorie attacco a 3 punti disponibili", "")
    regimi_pdp = row.get("Regimi PDP disponibili", "")
    link = row.get("link", "")
    score = row.get("_score", "")

    tags = ""
    if trazione:
        tags += _tag(f"🔧 {trazione}")
    if pot_min or pot_max:
        tags += _tag(f"⚡ {pot_min}–{pot_max} CV")
    if cat_3pt:
        tags += _tag(f"↕ Cat. {cat_3pt}", earth=True)
    if regimi_pdp:
        tags += _tag(f"PDP: {regimi_pdp}", earth=True)

    score_badge = f"<div class='score-badge'>✓ {score}%</div>" if score else ""
    link_html = f"<a class='card-link' href='{link}' target='_blank'>↗ Scheda tecnica</a>" if link and str(link).startswith("http") else ""

    return f"""
    <div class='card card-tractor'>
        {score_badge}
        <div class='card-title'>🚜 {nome}</div>
        <div class='card-brand'>{marchio}</div>
        <div class='card-meta'>{tags}</div>
        <div style='margin-top:0.6rem'>{link_html}</div>
    </div>
    """


def _card_machine(row: pd.Series) -> str:
    nome = row.get("Nome", "—")
    produttore = row.get("Produttore", "")
    tipo_macchina = row.get("Tipo di macchina", "")
    tipo_op = row.get("Tipo di operazione", "")
    attacco = row.get("Attacco al trattore", "")
    pot_min = row.get("Potenza minima richiesta HP", "")
    pot_max = row.get("Potenza massima consigliata HP", "")
    lar_min = row.get("Larghezza di lavoro min", "")
    lar_max = row.get("Larghezza di lavoro max", "")
    ripiegabile = row.get("Ripiegabile", "")
    link = row.get("URL scheda tecnica produttore/fonte", "")
    score = row.get("_score", "")

    tags = ""
    if tipo_macchina:
        tags += _tag(f"🔩 {tipo_macchina}")
    if pot_min or pot_max:
        tags += _tag(f"⚡ {pot_min}–{pot_max} HP")
    if lar_min or lar_max:
        tags += _tag(f"↔ {lar_min}–{lar_max} m")
    if attacco:
        tags += _tag(f"↕ {attacco}", earth=True)
    if str(ripiegabile).strip().lower() in ("sì", "si", "yes", "true", "1"):
        tags += _tag("📐 Ripiegabile", earth=True)

    score_badge = f"<div class='score-badge'>✓ {score}%</div>" if score else ""
    link_html = f"<a class='card-link' href='{link}' target='_blank'>↗ Scheda tecnica</a>" if link and str(link).startswith("http") else ""
    sub = " · ".join(filter(None, [str(produttore), str(tipo_op)]))

    return f"""
    <div class='card card-machine'>
        {score_badge}
        <div class='card-title'>🔩 {nome}</div>
        <div class='card-brand'>{sub}</div>
        <div class='card-meta'>{tags}</div>
        <div style='margin-top:0.6rem'>{link_html}</div>
    </div>
    """


def _render_detail_table(df: pd.DataFrame):
    """Show a compact dataframe for the detail/table view."""
    display_cols = [c for c in df.columns if not c.startswith("_")]
    st.dataframe(
        df[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


def render_results(results: dict[str, Any], filters: dict[str, Any]):
    """Main result rendering: tabs for tractors and implements."""

    trattori: pd.DataFrame = results.get("trattori", pd.DataFrame())
    macchine: pd.DataFrame = results.get("macchine", pd.DataFrame())

    n_trattori = len(trattori)
    n_macchine = len(macchine)

    tab_trattori, tab_macchine = st.tabs(
        [f"🚜 Trattori ({n_trattori})", f"🔩 Macchine ({n_macchine})"]
    )

    # ── Tractors tab ─────────────────────────────────────────────────────
    with tab_trattori:
        st.markdown("<div class='results-header'>Trattori compatibili</div>", unsafe_allow_html=True)

        if trattori.empty:
            st.markdown(
                "<div class='no-results'>Nessun trattore trovato con i criteri selezionati.<br>"
                "Prova ad allargare i filtri di potenza o trazione.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='results-count'>{n_trattori} risultat{'o' if n_trattori==1 else 'i'} trovato"
                f"{'/' if n_trattori==1 else 'i'}</div>",
                unsafe_allow_html=True,
            )

            view_mode = st.radio(
                "Vista", ["Schede", "Tabella"], horizontal=True, key="view_trattori", label_visibility="collapsed"
            )

            if view_mode == "Schede":
                cols = st.columns(2)
                for i, (_, row) in enumerate(trattori.iterrows()):
                    with cols[i % 2]:
                        st.markdown(_card_tractor(row), unsafe_allow_html=True)
            else:
                _render_detail_table(trattori)

    # ── Implements tab ───────────────────────────────────────────────────
    with tab_macchine:
        st.markdown("<div class='results-header'>Macchine compatibili</div>", unsafe_allow_html=True)

        if macchine.empty:
            st.markdown(
                "<div class='no-results'>Nessuna macchina trovata con i criteri selezionati.<br>"
                "Prova a rimuovere alcuni filtri opzionali.</div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<div class='results-count'>{n_macchine} risultat{'o' if n_macchine==1 else 'i'} trovato"
                f"{'/' if n_macchine==1 else 'i'}</div>",
                unsafe_allow_html=True,
            )

            view_mode = st.radio(
                "Vista", ["Schede", "Tabella"], horizontal=True, key="view_macchine", label_visibility="collapsed"
            )

            if view_mode == "Schede":
                cols = st.columns(2)
                for i, (_, row) in enumerate(macchine.iterrows()):
                    with cols[i % 2]:
                        st.markdown(_card_machine(row), unsafe_allow_html=True)
            else:
                _render_detail_table(macchine)

    # ── Summary note ─────────────────────────────────────────────────────
    if not trattori.empty or not macchine.empty:
        with st.expander("ℹ️ Come leggere i risultati"):
            st.markdown(
                """
                - I **percentuali** (badge verde) indicano la quota di filtri attivi soddisfatti dalla voce.
                - I risultati sono ordinati per **punteggio di compatibilità** decrescente.
                - Usa la vista **Tabella** per esportare o confrontare tutti i campi.
                - I link **↗ Scheda tecnica** aprono la documentazione ufficiale del produttore.
                """
            )
