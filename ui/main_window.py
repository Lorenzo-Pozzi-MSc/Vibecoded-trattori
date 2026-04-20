"""
ui/main_window.py — Top-level application window.
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QSplitter, QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal, QObject

from ui.styles import APP_STYLE
from ui.filter_panel import FilterPanel
from ui.results_panel import ResultsPanel
from ui.match_worker import MatchWorker
from logic.matcher import run_matching


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self, db_trattori: pd.DataFrame, db_macchine: pd.DataFrame):
        super().__init__()
        self._db_t = db_trattori
        self._db_m = db_macchine
        self._thread = None

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

        # ── Body: sidebar + results ───────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)

        self.filter_panel = FilterPanel(self._db_t, self._db_m)
        self.filter_panel.search_requested.connect(self._on_search)
        splitter.addWidget(self.filter_panel)

        self.results_panel = ResultsPanel()
        splitter.addWidget(self.results_panel)

        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([290, 990])

        root.addWidget(splitter)

        # ── Status bar ────────────────────────────────────────────────────
        self.statusBar().showMessage("Pronto — imposta i filtri e clicca Cerca.")
        self.statusBar().setStyleSheet(
            "QStatusBar { background: #eae5d8; color: #7a7a68; "
            "font-size: 11px; border-top: 1px solid #cfc8b8; }"
        )

    # ── Search handler ────────────────────────────────────────────────────────

    def _on_search(self, filters: dict):
        self.statusBar().showMessage("Ricerca in corso…")
        self.filter_panel.btn_search.setEnabled(False)

        self._thread = QThread()
        self._worker = MatchWorker(self._db_t, self._db_m, filters)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_results)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    def _on_results(self, results: dict):
        self.results_panel.load_results(results)
        self.filter_panel.btn_search.setEnabled(True)

        n_t = len(results.get("trattori", []))
        n_m = len(results.get("macchine", []))
        self.statusBar().showMessage(
            f"Trovati {n_t} trattori e {n_m} macchine compatibili."
        )
