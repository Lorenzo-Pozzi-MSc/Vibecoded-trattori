"""
ui/results_panel.py — The right-side panel showing search results

When you search, this shows:
  1. A tab for matching tractors (with count)
  2. A tab for matching machines (with count)

Each tab shows results two ways:
  - As attractive cards (default)
  - As a detailed table (if you click the "Table" button)
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget,
)

from ui.result_tab import ResultTab

class ResultsPanel(QWidget):
    """
    The right side of the window showing search results.
    
    Contains two tabs:
    - "Tractors" tab: Shows matching tractors
    - "Machines" tab: Shows matching implements/machines
    
    Each tab can display results as:
    - Cards: Pretty visual cards with key info
    - Table: Detailed spreadsheet-like view
    """
    
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
        """
        Display the initial message asking user to set filters and search.
        
        This message appears before any search is performed.
        """
        self.tab_trattori.count_label.setText("Imposta i filtri e clicca Cerca")
        self.tab_macchine.count_label.setText("Imposta i filtri e clicca Cerca")

    def load_results(self, results: dict):
        """
        Display search results in the tabs.
        
        This method:
        1. Puts tractors in the Tractors tab and machines in the Machines tab
        2. Shows the count of results found
        3. Automatically switches to whichever tab has more results
        
        Args:
            results: Dictionary containing 'trattori' and 'macchine' lists
        """
        self.tab_trattori.load(results.get("trattori", pd.DataFrame()))
        self.tab_macchine.load(results.get("macchine", pd.DataFrame()))
        # Switch to the tab with more results
        n_t = len(results.get("trattori", []))
        n_m = len(results.get("macchine", []))
        self.tabs.setTabText(0, f"🚜  Trattori ({n_t})")
        self.tabs.setTabText(1, f"🔩  Macchine ({n_m})")
