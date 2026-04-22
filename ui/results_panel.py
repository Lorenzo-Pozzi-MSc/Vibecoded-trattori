"""
ui/results_panel.py — The right-side panel showing search results

New layout (split-pane):
  - Left: Tractor search results with a "cerca macchine" button at bottom
  - Right: Machine compatibility results (populated after clicking "cerca macchine")

The user can see both tractors and machines side-by-side.
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSplitter, QLabel,
)
from PySide6.QtCore import Qt, Signal

from ui.result_tab import ResultTab


class ResultsPanel(QWidget):
    """
    The right side of the window showing search results (split-pane layout).
    
    Layout:
    - Left (50%): Tractor results with "cerca macchine" button at bottom
    - Right (50%): Machine compatibility results (populated on demand)
    """
    
    cerca_macchine_clicked = Signal(pd.DataFrame)  # Emits tractors DataFrame
    
    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Create split view (left: tractors, right: machines)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        
        # Left panel: Tractors with button
        left_container = QWidget()
        left_lay = QVBoxLayout(left_container)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(0)
        
        self.tab_trattori = ResultTab(is_tractor=True)
        left_lay.addWidget(self.tab_trattori)
        
        # "Cerca macchine" button at bottom of left panel
        self.btn_cerca_macchine = QPushButton("Cerca macchine")
        self.btn_cerca_macchine.setFixedHeight(40)
        self.btn_cerca_macchine.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cerca_macchine.setStyleSheet("""
            QPushButton {
                background: #1f3d1a;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
                font-weight: 600;
                padding: 8px;
                margin: 8px;
            }
            QPushButton:hover {
                background: #2a5723;
            }
            QPushButton:pressed {
                background: #152d11;
            }
            QPushButton:disabled {
                background: #a0a090;
                color: #6a6a5a;
            }
        """)
        self.btn_cerca_macchine.clicked.connect(self._on_cerca_clicked)
        self.btn_cerca_macchine.setEnabled(False)
        left_lay.addWidget(self.btn_cerca_macchine)
        
        # Right panel: Machines
        self.tab_macchine = ResultTab(is_tractor=False)
        
        # Add both to splitter
        splitter.addWidget(left_container)
        splitter.addWidget(self.tab_macchine)
        splitter.setSizes([640, 640])  # Equal split
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)
        
        lay.addWidget(splitter)

        # Initial empty state
        self._show_welcome()
        self._current_tractors_df = pd.DataFrame()

    def _show_welcome(self):
        """
        Display the initial message asking user to set filters and search.
        """
        self.tab_trattori.count_label.setText("Imposta i filtri e clicca Cerca")
        self.tab_macchine.count_label.setText("")

    def _on_cerca_clicked(self):
        """Emit signal when 'cerca macchine' button is clicked."""
        self.cerca_macchine_clicked.emit(self._current_tractors_df)

    def clear(self):
        """
        Clear all results in both panels and reset to initial state.
        
        Called when user clicks the Reset button.
        """
        self.tab_trattori.clear()
        self.tab_macchine.clear()
        self.btn_cerca_macchine.setEnabled(False)
        self._current_tractors_df = pd.DataFrame()
        self._show_welcome()

    def load_tractors(self, df: pd.DataFrame):
        """
        Display filtered tractor results in the left panel.
        
        Args:
            df: DataFrame of filtered tractors
        """
        self.tab_trattori.load(df)
        self._current_tractors_df = df.copy()
        self.btn_cerca_macchine.setEnabled(not df.empty)

    def load_machines(self, df: pd.DataFrame):
        """
        Display compatible machines in the right panel.
        
        Args:
            df: DataFrame of compatible machines
        """
        self.tab_macchine.load(df)
        n_m = len(df)
        self.tab_macchine.count_label.setText(f"{n_m} risultat{'o' if n_m == 1 else 'i'}")
