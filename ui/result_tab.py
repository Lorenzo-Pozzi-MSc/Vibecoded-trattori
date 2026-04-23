"""
ui/result_tab.py — A single results tab (tractors or machines)

Each result tab can display search results in two different ways:
  1. Card view: Pretty visual cards with key information (default)
  2. Table view: Detailed spreadsheet showing all columns

You can switch between these views with buttons at the top of the tab.
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
)
from PySide6.QtCore import Qt, Signal

from data.models import Tractor, Machine
from ui.card_grid import CardGrid
from ui.result_table import ResultTable
from ui.result_card import ResultCard


class ResultTab(QWidget):
    """
    A single results tab displaying tractors or machines.

    Features:
    - Shows results as cards or table (toggle with buttons)
    - Displays the number of results found
    - Shows an "empty state" message if no results
    - Automatically selects relevant info to display for each type
    - For tractors: allows selection with checkboxes (max 2)
    """

    tractors_selected = Signal(list)  # emits list[Tractor]

    def __init__(self, is_tractor: bool = True, parent=None):
        super().__init__(parent)
        self._is_tractor = is_tractor
        self._accent = "#1f3d1a" if is_tractor else "#8b6340"
        self._selected_indices: list[int] = []
        self._current_items: list = []

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

    def clear(self):
        self.card_grid.set_cards([])
        self.table_view.load(pd.DataFrame())
        self.stack.hide()
        self.empty_label.show()
        self.count_label.setText("Imposta i filtri e clicca Cerca")
        self.btn_cards.setChecked(True)
        self.btn_table.setChecked(False)
        self.stack.setCurrentIndex(0)
        self._current_items = []
        self._selected_indices = []

    def _switch(self, idx: int):
        self.stack.setCurrentIndex(idx)
        self.btn_cards.setChecked(idx == 0)
        self.btn_table.setChecked(idx == 1)

    def load(self, items: list):
        """
        Display results from a list of Tractor or Machine model instances.

        Args:
            items: list[Tractor] or list[Machine]
        """
        if not items:
            self.stack.hide()
            self.empty_label.show()
            self.count_label.setText("0 risultati")
            return

        self.stack.show()
        self.empty_label.hide()
        n = len(items)
        self.count_label.setText(f"{n} risultat{'o' if n == 1 else 'i'}")

        self._current_items = items
        self._selected_indices = []

        # Build cards
        cards = []
        for idx, item in enumerate(items):
            title, brand, tags, link = self._extract(item)
            card = ResultCard(title, brand, tags, link, self._accent,
                              selectable=self._is_tractor)
            if self._is_tractor and card.checkbox:
                card.checkbox.stateChanged.connect(
                    lambda checked, i=idx: self._on_tractor_toggled(i, checked)
                )
            cards.append(card)
        self.card_grid.set_cards(cards)

        # Rebuild DataFrame from raw_data for the table view
        self.table_view.load(pd.DataFrame([item.raw_data for item in items]))

    def _on_tractor_toggled(self, idx: int, checked: bool):
        if checked:
            if len(self._selected_indices) < 2:
                self._selected_indices.append(idx)
        else:
            if idx in self._selected_indices:
                self._selected_indices.remove(idx)
        selected = [self._current_items[i] for i in self._selected_indices]
        self.tractors_selected.emit(selected)

    def _extract(self, item) -> tuple:
        """
        Pull the display fields out of a Tractor or Machine model instance.

        Returns:
            (title, brand, tags, link)
        """
        if self._is_tractor:
            t: Tractor = item
            title = f"{t.brand} | {t.name}" if t.brand else (t.name or "—")
            brand = ""
            tags = []
            if t.traction_type:
                tags.append((", ".join(t.traction_type), False))
            if t.power_min_cv is not None:
                tags.append((f"{round(t.power_min_cv)}–{round(t.power_max_cv)} CV", False))
            if t.pto_speeds:
                tags.append((", ".join(t.pto_speeds), False))
            link = t.link or None
        else:
            m: Machine = item
            title = m.name or "—"
            brand = " · ".join(filter(None, [m.manufacturer, m.operation_type]))
            tags = []
            if m.machine_type:
                tags.append((f"🔩 {m.machine_type}", False))
            if m.min_power_required_hp is not None:
                tags.append((f"⚡ {m.min_power_required_hp}–{m.max_power_recommended_hp} HP", False))
            if m.min_work_width_m is not None:
                tags.append((f"↔ {m.min_work_width_m}–{m.max_work_width_m} m", False))
            if m.attachment_type:
                tags.append((f"↕ {m.attachment_type}", True))
            if m.is_foldable:
                tags.append(("📐 Ripiegabile", True))
            link = m.technical_sheet_url or None

        return title, brand, tags, link
