"""
ui/main_window.py — The main application window

This is what you see when you open the app. It has two main areas:
  1. Left side: Filter panel where you set your search criteria
  2. Right side: Results panel showing tractors and machines side-by-side

The workflow:
1. User sets filters → clicks Search → tractors shown on left
2. User clicks "cerca macchine" → compatible machines shown on right
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter,
)
from PySide6.QtCore import Qt, QThread

from data.models import Tractor, Machine, TractorDatabase, MachineDatabase
from ui.styles import APP_STYLE
from ui.filter_panel import FilterPanel
from ui.results_panel import ResultsPanel
from ui.match_worker import MatchWorker
from logic.filter import filter_machines_by_tractors


class MainWindow(QMainWindow):
    """
    The main application window that displays the search interface.

    Contains:
    - A filter panel on the left (search criteria)
    - A results panel on the right (split view: tractors left, machines right)
    - A status bar at the bottom
    """

    def __init__(self, tractor_db: TractorDatabase, machine_db: MachineDatabase, on_close=None):
        super().__init__()
        self._tractor_db = tractor_db
        self._machine_db = machine_db
        self._thread = None
        self._on_close = on_close
        self._current_filters: dict = {}

        self.setWindowTitle("AgriSelector 🚜")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(APP_STYLE)

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        self.filter_panel = FilterPanel(self._tractor_db, self._machine_db)
        self.filter_panel.search_requested.connect(self._on_search)
        self.filter_panel.reset_requested.connect(self._on_reset)
        splitter.addWidget(self.filter_panel)

        self.results_panel = ResultsPanel()
        self.results_panel.cerca_macchine_clicked.connect(self._on_cerca_macchine)
        splitter.addWidget(self.results_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([290, 990])

        root.addWidget(splitter)

        self.statusBar().showMessage("Pronto — imposta i filtri e clicca Cerca.")
        self.statusBar().setStyleSheet(
            "QStatusBar { background: #eae5d8; color: #7a7a68; "
            "font-size: 11px; border-top: 1px solid #cfc8b8; }"
        )

    # ── Search handler ────────────────────────────────────────────────────────

    def _on_search(self, filters: dict):
        self._current_filters = filters
        self.statusBar().showMessage("Ricerca in corso…")
        self.filter_panel.btn_search.setEnabled(False)

        self._thread = QThread()
        self._worker = MatchWorker(self._tractor_db.tractors, filters)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_tractors_filtered)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    def _on_tractors_filtered(self, tractors: list[Tractor]):
        self.results_panel.load_tractors(tractors)
        self.results_panel.load_machines([])
        self.filter_panel.btn_search.setEnabled(True)

        n = len(tractors)
        self.statusBar().showMessage(
            f"Trovati {n} trattori. Clicca 'cerca macchine' per visualizzare le macchine compatibili."
        )

    def _on_cerca_macchine(self, tractors: list[Tractor]):
        self.statusBar().showMessage("Filtraggio macchine compatibili…")

        operations = self.filter_panel.w_tipo_op.selected_values() or None
        max_width = self._current_filters.get("ingombro_larghezza")

        compatible = filter_machines_by_tractors(
            self._machine_db.machines,
            tractors,
            selected_operations=operations,
            max_width=max_width,
        )

        self.results_panel.load_machines(compatible)

        self.statusBar().showMessage(
            f"Trovate {len(compatible)} macchine compatibili con i {len(tractors)} trattori selezionati."
        )

    def _on_reset(self):
        self.results_panel.clear()
        self._current_filters = {}
        self.statusBar().showMessage("Pronto — imposta i filtri e clicca Cerca.")

    def closeEvent(self, event):
        if self._on_close:
            self._on_close()
        super().closeEvent(event)
