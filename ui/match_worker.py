"""
ui/match_worker.py — Runs searches in the background without freezing the window

When you click "Search", this module runs the matching logic in the background.
That way the window stays responsive and doesn't freeze while it's searching.
When the search is done, it sends the results back to be displayed.
"""

from PySide6.QtCore import Signal, QObject
from logic.matcher import run_matching


class MatchWorker(QObject):
    """
    A background task that runs the search and sends back the results.
    
    When you click the Search button, the app creates a MatchWorker,
    starts it running in the background, and the window stays responsive.
    When the search finishes, the MatchWorker sends a signal with the results.
    
    This prevents the window from "freezing" during a search.
    """
    
    finished = Signal(dict)

    def __init__(self, db_t, db_m, filters):
        super().__init__()
        self._db_t = db_t
        self._db_m = db_m
        self._filters = filters

    def run(self):
        """
        Perform the search using your filters and send back the results.
        
        This method:
        1. Takes your filter settings
        2. Runs the matching logic against the databases
        3. Emits a signal with the results so the app can display them
        """
        results = run_matching(self._db_t, self._db_m, self._filters)
        self.finished.emit(results)
