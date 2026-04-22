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
from logic.filter import filter_machines_by_tractors


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    The main application window that displays the search interface.
    
    This window contains:
    - A filter panel on the left (where you set your search criteria)
    - A results panel on the right (split view: tractors left, machines right)
    - A status bar at the bottom (showing current status messages)
    
    When you adjust filters and click Search, this window coordinates
    the search and displays the tractors. Then when you click "cerca macchine",
    it filters and displays compatible machines.
    """
    
    def __init__(self, tractor_db: TractorDatabase, machine_db: MachineDatabase, on_close=None):
        super().__init__()
        # Store database objects
        self._tractor_db = tractor_db
        self._machine_db = machine_db
        
        # Extract DataFrames for the UI
        self._db_t = tractor_db.dataframe
        self._db_m = machine_db.dataframe
        self._thread = None
        self._on_close = on_close
        self._current_filters = {}  # Store current filters for machine filtering

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
        2. A right panel with split view (tractors left, machines right)
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
        self.filter_panel.reset_requested.connect(self._on_reset)
        splitter.addWidget(self.filter_panel)

        self.results_panel = ResultsPanel()
        # Connect "cerca macchine" button to filter machines
        self.results_panel.cerca_macchine_clicked.connect(self._on_cerca_macchine)
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
        1. Stores the filters for later machine filtering
        2. Shows "Searching..." in the status bar
        3. Disables the Search button (so you can't click it while searching)
        4. Creates a background worker to filter tractors
        5. Waits for results without freezing the window
        """
        self._current_filters = filters
        self.statusBar().showMessage("Ricerca in corso…")
        self.filter_panel.btn_search.setEnabled(False)

        self._thread = QThread()
        self._worker = MatchWorker(self._db_t, filters)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_tractors_filtered)
        self._worker.finished.connect(self._thread.quit)
        self._thread.start()

    def _on_tractors_filtered(self, filtered_tractors: pd.DataFrame):
        """
        Display the filtered tractors when the search is complete.
        
        This method:
        1. Shows the matching tractors in the left panel
        2. Re-enables the Search button
        3. Updates the status bar with the tractor count
        4. Clears the machines panel
        """
        self.results_panel.load_tractors(filtered_tractors)
        self.results_panel.load_machines(pd.DataFrame())  # Clear machines initially
        self.filter_panel.btn_search.setEnabled(True)

        n_t = len(filtered_tractors)
        self.statusBar().showMessage(
            f"Trovati {n_t} trattori. Clicca 'cerca macchine' per visualizzare le macchine compatibili."
        )

    def _on_cerca_macchine(self, tractors_df: pd.DataFrame):
        """
        Handle when the user clicks "cerca macchine" button.
        
        Filters machines based on compatibility with the shown tractors.
        
        Args:
            tractors_df: DataFrame of currently shown tractors (all filtered tractors)
        """
        self.statusBar().showMessage("Filtraggio macchine compatibili…")
        
        # Extract operation types from current filters if available
        operations = self._current_filters.get("operation_type")
        
        # Filter machines by tractor compatibility
        compatible_machines = filter_machines_by_tractors(
            self._db_m,
            tractors_df,
            selected_operations=operations
        )
        
        self.results_panel.load_machines(compatible_machines)
        
        n_m = len(compatible_machines)
        self.statusBar().showMessage(
            f"Trovate {n_m} macchine compatibili con i {len(tractors_df)} trattori selezionati."
        )

    def _on_reset(self):
        """
        Handle when the user clicks the Reset button.
        
        This clears all results and returns to the welcome state.
        """
        self.results_panel.clear()
        self._current_filters = {}
        self.statusBar().showMessage("Pronto — imposta i filtri e clicca Cerca.")

    def closeEvent(self, event):
        """
        Handle window close event and run cleanup.
        """
        if self._on_close:
            self._on_close()
        super().closeEvent(event)
