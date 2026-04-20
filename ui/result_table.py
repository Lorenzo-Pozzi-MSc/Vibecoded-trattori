"""
ui/result_table.py — Results table widget.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
)
from PySide6.QtCore import Qt


class ResultTable(QTableWidget):
    """A table widget for displaying search results."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color: #f8f5ee;")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def load(self, df: pd.DataFrame):
        """Populate table from a DataFrame."""
        display_cols = [c for c in df.columns if not c.startswith("_")]
        self.clear()
        self.setColumnCount(len(display_cols))
        self.setRowCount(len(df))
        self.setHorizontalHeaderLabels(display_cols)

        for row_idx, (_, row) in enumerate(df[display_cols].iterrows()):
            for col_idx, val in enumerate(row):
                item = QTableWidgetItem("" if pd.isna(val) else str(val))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row_idx, col_idx, item)

        self.resizeColumnsToContents()
