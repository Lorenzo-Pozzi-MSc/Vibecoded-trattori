"""
ui/results_panel.py — The right-side panel showing search results

Layout (split-pane):
  - Left: Tractor search results with a "cerca macchine" button at bottom
  - Right: Machine compatibility results (populated after clicking "cerca macchine")
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QSplitter,
)
from PySide6.QtCore import Qt, Signal

from data.models import Tractor, Machine
from ui.result_tab import ResultTab


class ResultsPanel(QWidget):
    """
    The right side of the window showing search results (split-pane layout).

    Layout:
    - Left (50%): Tractor results with "cerca macchine" button at bottom
    - Right (50%): Machine compatibility results (populated on demand)
    """

    cerca_macchine_clicked = Signal(list)  # emits list[Tractor]

    def __init__(self, parent=None):
        super().__init__(parent)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        # Left panel: Tractors + button
        left_container = QWidget()
        left_lay = QVBoxLayout(left_container)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(0)

        self.tab_trattori = ResultTab(is_tractor=True)
        left_lay.addWidget(self.tab_trattori)

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
            QPushButton:hover { background: #2a5723; }
            QPushButton:pressed { background: #152d11; }
            QPushButton:disabled { background: #a0a090; color: #6a6a5a; }
        """)
        self.btn_cerca_macchine.clicked.connect(self._on_cerca_clicked)
        self.btn_cerca_macchine.setEnabled(False)
        left_lay.addWidget(self.btn_cerca_macchine)

        # Right panel: Machines
        self.tab_macchine = ResultTab(is_tractor=False)

        splitter.addWidget(left_container)
        splitter.addWidget(self.tab_macchine)
        splitter.setSizes([640, 640])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        lay.addWidget(splitter)

        self._current_tractors: list[Tractor] = []
        self._selected_tractors: list[Tractor] = []
        self.tab_trattori.tractors_selected.connect(self._on_tractors_selected)
        self._show_welcome()

    def _show_welcome(self):
        self.tab_trattori.count_label.setText("Imposta i filtri e clicca Cerca")
        self.tab_macchine.count_label.setText("")

    def _on_tractors_selected(self, tractors: list[Tractor]):
        self._selected_tractors = tractors

    def _on_cerca_clicked(self):
        tractors = self._selected_tractors if self._selected_tractors else self._current_tractors
        self.cerca_macchine_clicked.emit(tractors)

    def clear(self):
        self.tab_trattori.clear()
        self.tab_macchine.clear()
        self.btn_cerca_macchine.setEnabled(False)
        self._current_tractors = []
        self._selected_tractors = []
        self._show_welcome()

    def load_tractors(self, tractors: list[Tractor]):
        self.tab_trattori.load(tractors)
        self._current_tractors = tractors
        self._selected_tractors = []
        self.btn_cerca_macchine.setEnabled(bool(tractors))

    def load_machines(self, machines: list[Machine]):
        self.tab_macchine.load(machines)
        n = len(machines)
        self.tab_macchine.count_label.setText(f"{n} risultat{'o' if n == 1 else 'i'}")
