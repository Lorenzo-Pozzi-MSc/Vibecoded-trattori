"""
ui/main_window.py — The main application window

This is what you see when you open the app. It has two main areas:
  1. Left side: Filter panel where you set your search criteria
  2. Right side: Results panel that shows matching tractors and machines
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QSplitter, QSizePolicy,
)
from PySide6.QtCore import Qt, QThread, Signal, QObject

from data.models import TractorDatabase, MachineDatabase
from ui.styles import APP_STYLE
from ui.filter_panel import FilterPanel
from ui.results_panel import ResultsPanel
from ui.match_worker import MatchWorker
from logic.matcher import run_matching


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    The main application window that displays the search interface.
    
    This window contains:
    - A filter panel on the left (where you set your search criteria)
    - A results panel on the right (where search results are shown)
    - A status bar at the bottom (showing current status messages)
    
    When you adjust filters and click Search, this window coordinates
    the search and displays the results.
    """
    
    def __init__(self, tractor_db: TractorDatabase, machine_db: MachineDatabase):
        super().__init__()
        # Store database objects for potential future use
        self._tractor_db = tractor_db
        self._machine_db = machine_db
        
        # Extract DataFrames for the UI and matcher
        self._db_t = tractor_db.dataframe
        self._db_m = machine_db.dataframe
        self._thread = None

        self.setWindowTitle("AgriSelector 🚜")
        self.resize(1280, 820)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(APP_STYLE)

        self._build_ui()

    def _build_ui(self):
        """
        Construct the visual layout of the window.
        
        This creates:
        1. A left sidebar with the filter panel
        2. A right panel for results
        3. A status bar at the bottom
        4. Proper sizing and spacing
        """
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
        """
        Handle when the user clicks the Search button.
        
        This method:
        1. Shows "Searching..." in the status bar
        2. Disables the Search button (so you can't click it again while searching)
        3. Creates a background worker to run the search
        4. Waits for results without freezing the window
        """
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
        """
        Display the search results when they're ready.
        
        This method:
        1. Shows the matching tractors and machines in the results panel
        2. Re-enables the Search button so you can search again
        3. Updates the status bar to show how many matches were found
        """
        self.results_panel.load_results(results)
        self.filter_panel.btn_search.setEnabled(True)

        n_t = len(results.get("trattori", []))
        n_m = len(results.get("macchine", []))
        self.statusBar().showMessage(
            f"Trovati {n_t} trattori e {n_m} macchine compatibili."
        )
