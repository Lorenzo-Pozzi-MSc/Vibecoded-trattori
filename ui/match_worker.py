"""
ui/match_worker.py — Runs tractor filtering in the background

When you click "Search", this module filters tractors based on your criteria.
It runs in the background so the window stays responsive.
"""

from PySide6.QtCore import Signal, QObject
import pandas as pd


class MatchWorker(QObject):
    """
    A background task that filters tractors based on search criteria.
    
    When you click the Search button, the app creates a MatchWorker,
    starts it running in the background, and the window stays responsive.
    When the search finishes, the MatchWorker sends back the filtered tractors.
    """
    
    finished = Signal(pd.DataFrame)  # Emits DataFrame of filtered tractors

    def __init__(self, tractors_df: pd.DataFrame, filters: dict):
        super().__init__()
        self._tractors_df = tractors_df
        self._filters = filters

    def run(self):
        """
        Filter tractors based on the provided filter criteria.
        
        This method:
        1. Takes filter settings (operation types, power range, etc.)
        2. Filters the tractors DataFrame
        3. Emits the filtered tractors DataFrame
        """
        filtered = self._apply_filters(self._tractors_df, self._filters)
        self.finished.emit(filtered)
    
    def _apply_filters(self, df: pd.DataFrame, filters: dict) -> pd.DataFrame:
        """
        Apply all filter criteria to the tractors DataFrame.
        
        Supported filters:
        - operation_type: str or list of operation types
        - traction: str or list of traction types
        - power_range: tuple (min_cv, max_cv)
        - work_width_range: tuple (min_m, max_m)
        - turning_radius_range: tuple (min_m, max_m)
        """
        result = df.copy()
        
        # Filter by operation type (if specified)
        if "operation_type" in filters and filters["operation_type"]:
            ops = filters["operation_type"]
            if isinstance(ops, str):
                ops = [ops]
            # Note: For tractors, operation filtering would typically be done
            # based on available attachments and categories
            # This is a placeholder for now
        
        # Filter by traction type (if specified)
        if "traction" in filters and filters["traction"]:
            tractions = filters["traction"]
            if isinstance(tractions, str):
                tractions = [tractions]
            result = result[result.get("Trazione", "").isin(tractions)]
        
        # Filter by power range (if specified)
        if "power_range" in filters and filters["power_range"]:
            min_power, max_power = filters["power_range"]
            if min_power is not None:
                # Check if tractor's max power is >= min requirement
                result = result[result.get("Pot. max (CV)", 0) >= min_power]
            if max_power is not None:
                # Check if tractor's min power is <= max requirement
                result = result[result.get("Pot. min (CV)", float('inf')) <= max_power]
        
        # Filter by work width (if specified)
        if "work_width_range" in filters and filters["work_width_range"]:
            min_width, max_width = filters["work_width_range"]
            # Note: Tractors don't typically have work width, skip this
        
        # Filter by turning radius (if specified)
        if "turning_radius_range" in filters and filters["turning_radius_range"]:
            min_radius, max_radius = filters["turning_radius_range"]
            if min_radius is not None:
                result = result[result.get("Raggio di Sterzata min (m)", 0) >= min_radius]
            if max_radius is not None:
                result = result[result.get("Raggio di Sterzata min (m)", float('inf')) <= max_radius]
        
        return result.reset_index(drop=True)
