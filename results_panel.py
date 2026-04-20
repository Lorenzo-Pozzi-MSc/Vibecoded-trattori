"""
ui/results_panel.py — Tabbed results area showing tractors and implements.
Supports both a card view (scrollable) and a table view.
"""

from __future__ import annotations
import webbrowser
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
    QScrollArea, QSizePolicy, QHeaderView, QStackedWidget,
    QButtonGroup, QAbstractItemView,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor


# ── Tag widget ────────────────────────────────────────────────────────────────

def _tag(text: str, earth: bool = False) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("tag_earth" if earth else "tag")
    lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lbl


# ── Single result card ────────────────────────────────────────────────────────

class ResultCard(QFrame):
    def __init__(self, title: str, brand: str, tags: list[tuple[str, bool]],
                 score: int | None, link: str | None, accent: str = "#1f3d1a",
                 parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Left accent bar
        self.setStyleSheet(
            f"QFrame#card {{ border-left: 4px solid {accent}; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)

        # Title row
        title_row = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setObjectName("card_title")
        font = title_lbl.font()
        font.setPointSize(12)
        font.setBold(True)
        title_lbl.setFont(font)
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        if score is not None:
            score_lbl = QLabel(f"✓ {score}%")
            score_lbl.setObjectName("score_badge")
            title_row.addWidget(score_lbl)
        lay.addLayout(title_row)

        # Brand
        if brand:
            brand_lbl = QLabel(brand.upper())
            brand_lbl.setObjectName("card_brand")
            font2 = brand_lbl.font()
            font2.setPointSize(9)
            brand_lbl.setFont(font2)
            lay.addWidget(brand_lbl)

        # Tags row
        if tags:
            tag_row = QHBoxLayout()
            tag_row.setSpacing(5)
            tag_row.setContentsMargins(0, 4, 0, 0)
            for text, earth in tags:
                tag_row.addWidget(_tag(text, earth))
            tag_row.addStretch()
            lay.addLayout(tag_row)

        # Link
        if link and str(link).startswith("http"):
            btn = QPushButton("↗ Scheda tecnica")
            btn.setObjectName("link_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda: webbrowser.open(link))
            lay.addWidget(btn)


# ── Scrollable card grid ──────────────────────────────────────────────────────

class CardGrid(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(10)
        self._layout.addStretch()
        self.setWidget(self._container)

    def set_cards(self, cards: list[ResultCard]):
        # Remove all existing widgets (keep the trailing stretch)
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for card in cards:
            self._layout.insertWidget(self._layout.count() - 1, card)


# ── Results table ─────────────────────────────────────────────────────────────

class ResultTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color: #f8f5ee;")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def load(self, df: pd.DataFrame):
        display_cols = [c for c in df.columns if not c.startswith("_")]
        self.clear()
        self.setColumnCount(len(display_cols))
        self.setRowCount(len(df))
        self.setHorizontalHeaderLabels(display_cols)

        for row_idx, (_, row) in enumerate(df[display_cols].iterrows()):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem("" if pd.isna(val) else str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row_idx, col_idx, item)

        self.resizeColumnsToContents()


# ── One tab (cards + table toggle) ───────────────────────────────────────────

class ResultTab(QWidget):
    def __init__(self, is_tractor: bool = True, parent=None):
        super().__init__(parent)
        self._is_tractor = is_tractor
        self._accent = "#1f3d1a" if is_tractor else "#8b6340"

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ───────────────────────────────────────────────────
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet("background:#f4f0e8; border-bottom:1px solid #d6e8cc;")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 0, 16, 0)

        self.count_label = QLabel("")
        self.count_label.setObjectName("subtitle_label")
        hlay.addWidget(self.count_label)
        hlay.addStretch()

        # View toggle
        self.btn_cards = QPushButton("Schede")
        self.btn_table = QPushButton("Tabella")
        for btn in (self.btn_cards, self.btn_table):
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton { background: transparent; border: 1px solid #cfc8b8;
                              border-radius: 4px; padding: 0 12px; font-size: 12px; color: #4a4a3a; }
                QPushButton:checked { background: #1f3d1a; color: white; border-color: #1f3d1a; }
            """)
        self.btn_cards.setChecked(True)
        self.btn_cards.clicked.connect(lambda: self._switch(0))
        self.btn_table.clicked.connect(lambda: self._switch(1))
        hlay.addWidget(self.btn_cards)
        hlay.addWidget(self.btn_table)
        root.addWidget(header)

        # ── Stacked views ─────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.card_grid = CardGrid()
        self.table_view = ResultTable()
        self.stack.addWidget(self.card_grid)
        self.stack.addWidget(self.table_view)
        root.addWidget(self.stack)

        # ── Empty state ───────────────────────────────────────────────────
        self.empty_label = QLabel("Nessun risultato — prova ad allargare i filtri.")
        self.empty_label.setObjectName("empty_state")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.empty_label)
        self.empty_label.hide()

    def _switch(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self.btn_cards.setChecked(idx == 0)
        self.btn_table.setChecked(idx == 1)

    def load(self, df: pd.DataFrame):
        if df.empty:
            self.stack.hide()
            self.empty_label.show()
            self.count_label.setText("0 risultati")
            return

        self.stack.show()
        self.empty_label.hide()
        n = len(df)
        self.count_label.setText(f"{n} risultat{'o' if n == 1 else 'i'}")

        # Build cards
        cards = []
        for _, row in df.iterrows():
            title, brand, tags, score, link = self._extract(row)
            cards.append(ResultCard(title, brand, tags, score, link, self._accent))
        self.card_grid.set_cards(cards)

        # Load table
        self.table_view.load(df)

    def _extract(self, row: pd.Series):
        score_val = row.get("_score")
        score = int(score_val) if pd.notna(score_val) else None

        def v(col): return row.get(col, "")
        def ok(col): return str(v(col)) not in ("", "nan", "<NA>")

        if self._is_tractor:
            title = str(v("Nome serie/modello") or "—")
            brand = str(v("Marchio")) if ok("Marchio") else ""
            tags = []
            if ok("Trazione"):        tags.append((f"🔧 {v('Trazione')}", False))
            if ok("Pot. min (CV)"):   tags.append((f"⚡ {v('Pot. min (CV)')}–{v('Pot. max (CV)')} CV", False))
            if ok("Categorie attacco a 3 punti disponibili"):
                tags.append((f"↕ Cat. {v('Categorie attacco a 3 punti disponibili')}", True))
            if ok("Regimi PDP disponibili"):
                tags.append((f"PDP: {v('Regimi PDP disponibili')}", True))
            link = str(v("link")) if ok("link") else None
        else:
            title = str(v("Nome") or "—")
            parts = [str(v(c)) for c in ("Produttore", "Tipo di operazione") if ok(c)]
            brand = " · ".join(parts)
            tags = []
            if ok("Tipo di macchina"):             tags.append((f"🔩 {v('Tipo di macchina')}", False))
            if ok("Potenza minima richiesta HP"):  tags.append((f"⚡ {v('Potenza minima richiesta HP')}–{v('Potenza massima consigliata HP')} HP", False))
            if ok("Larghezza di lavoro min"):      tags.append((f"↔ {v('Larghezza di lavoro min')}–{v('Larghezza di lavoro max')} m", False))
            if ok("Attacco al trattore"):          tags.append((f"↕ {v('Attacco al trattore')}", True))
            rip = str(v("Ripiegabile")).strip().lower()
            if rip in ("sì", "si", "yes", "true", "1"): tags.append(("📐 Ripiegabile", True))
            link = str(v("URL scheda tecnica produttore/fonte")) if ok("URL scheda tecnica produttore/fonte") else None

        return title, brand, tags, score, link


# ── Main results panel ────────────────────────────────────────────────────────

class ResultsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.tabs = QTabWidget()
        self.tab_trattori = ResultTab(is_tractor=True)
        self.tab_macchine = ResultTab(is_tractor=False)
        self.tabs.addTab(self.tab_trattori, "🚜  Trattori")
        self.tabs.addTab(self.tab_macchine, "🔩  Macchine")
        lay.addWidget(self.tabs)

        # Initial empty state
        self._show_welcome()

    def _show_welcome(self):
        self.tab_trattori.count_label.setText("Imposta i filtri e clicca Cerca")
        self.tab_macchine.count_label.setText("Imposta i filtri e clicca Cerca")

    def load_results(self, results: dict):
        self.tab_trattori.load(results.get("trattori", pd.DataFrame()))
        self.tab_macchine.load(results.get("macchine", pd.DataFrame()))
        # Switch to the tab with more results
        n_t = len(results.get("trattori", []))
        n_m = len(results.get("macchine", []))
        self.tabs.setTabText(0, f"🚜  Trattori ({n_t})")
        self.tabs.setTabText(1, f"🔩  Macchine ({n_m})")
