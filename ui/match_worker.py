"""
ui/match_worker.py — Background worker for search matching.
"""

from PySide6.QtCore import Signal, QObject
from logic.matcher import run_matching


class MatchWorker(QObject):
    """Background worker for running matching logic without freezing UI."""
    
    finished = Signal(dict)

    def __init__(self, db_t, db_m, filters):
        super().__init__()
        self._db_t = db_t
        self._db_m = db_m
        self._filters = filters

    def run(self):
        """Execute the matching and emit results."""
        results = run_matching(self._db_t, self._db_m, self._filters)
        self.finished.emit(results)
