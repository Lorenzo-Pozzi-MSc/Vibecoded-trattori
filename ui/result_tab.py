"""
ui/result_tab.py — A single results tab (tractors or machines)

Each result tab can display search results in two different ways:
  1. Card view: Pretty visual cards with key information (default)
  2. Table view: Detailed spreadsheet showing all columns

You can switch between these views with buttons at the top of the tab.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
)
from PySide6.QtCore import Qt

from ui.card_grid import CardGrid
from ui.result_table import ResultTable
from ui.result_card import ResultCard


class ResultTab(QWidget):
    """
    A single results tab displaying tractors or machines.
    
    Features:
    - Shows results as cards or table (you can toggle with buttons)
    - Displays the number of results found
    - Shows an "empty state" message if no results
    - Automatically selects relevant info to display for each type
    """

    def __init__(self, is_tractor: bool = True, parent=None):
        super().__init__(parent)
        """
        Create a results tab.
        
        Args:
            is_tractor: True if this tab is for tractors, False if for machines
                       This affects which fields are displayed and the accent color
        """
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
        """
        Switch between card and table views.
        
        Args:
            idx: 0 for card view, 1 for table view
        """
        self.stack.setCurrentIndex(idx)
        self.btn_cards.setChecked(idx == 0)
        self.btn_table.setChecked(idx == 1)

    def load(self, df: pd.DataFrame):
        """
        Display search results from a data table.
        
        This method:
        1. Shows the result count
        2. Creates cards from each result
        3. Loads the data into the table view
        4. Shows empty state if no results
        
        Args:
            df: A pandas DataFrame containing the search results
        """
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
        """
        Pull out the important fields from a result row to display.
        
        This method selects which database columns to show and formats them nicely
        for display on a result card. Different fields are shown for tractors vs machines.
        
        Args:
            row: A single result row from the database
        
        Returns:
            A tuple of (title, brand, tags, score, link) ready for display
        """
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
