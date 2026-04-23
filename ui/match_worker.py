"""
ui/match_worker.py — Runs tractor filtering in the background

When you click "Search", this module filters tractors based on your criteria.
It runs in the background so the window stays responsive.
"""

from PySide6.QtCore import Signal, QObject

from data.models import Tractor
from logic.filter import _to_float


class MatchWorker(QObject):
    """
    A background task that filters tractors based on search criteria.

    Receives the full list of Tractor model instances and a filters dict,
    returns the matching subset as a list via the finished signal.
    """

    finished = Signal(list)  # emits list[Tractor]

    def __init__(self, tractors: list[Tractor], filters: dict):
        super().__init__()
        self._tractors = tractors
        self._filters = filters

    def run(self):
        filtered = self._apply_filters(self._tractors, self._filters)
        self.finished.emit(filtered)

    def _apply_filters(self, tractors: list[Tractor], filters: dict) -> list[Tractor]:
        """
        Apply all filter criteria to the tractor list.

        Supported filter keys:
        - trazione: list[str] — traction types to include
        - potenza_range: tuple(min_cv, max_cv)
        """
        result = list(tractors)

        # Filter by traction type
        tractions = filters.get("trazione") or []
        if tractions:
            result = [
                t for t in result
                if any(tr in t.traction_type for tr in tractions)
            ]

        # Filter by power range — tractors with no power data are not excluded
        power_range = filters.get("potenza_range")
        if power_range:
            min_cv, max_cv = power_range
            if min_cv is not None:
                result = [t for t in result if t.power_min_cv is None or t.power_min_cv >= min_cv]
            if max_cv is not None:
                result = [t for t in result if t.power_max_cv is None or t.power_max_cv <= max_cv]

        # Filter by width — pass if no width data, otherwise w_min or w_max must be <= limit
        max_width = filters.get("ingombro_larghezza")
        if max_width is not None:
            def _width_ok(t: Tractor) -> bool:
                w_min = _to_float(t.raw_data.get("w min (m)"))
                w_max = _to_float(t.raw_data.get("w max (m)"))
                if w_min is None and w_max is None:
                    return True
                return (w_min is not None and w_min <= max_width) or \
                       (w_max is not None and w_max <= max_width)
            result = [t for t in result if _width_ok(t)]

        return result
