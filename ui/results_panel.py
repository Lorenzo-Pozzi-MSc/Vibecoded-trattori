"""
ui/results_panel.py — Tabbed results area showing tractors and implements.
Supports both a card view (scrollable) and a table view.
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
)

from ui.result_tab import ResultTab

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
