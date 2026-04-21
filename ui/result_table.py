"""
ui/result_table.py — Display results in a table/spreadsheet view

This is an alternative way to view search results - as a detailed spreadsheet
with all the database columns visible. You can scroll horizontally to see
all the data, and each row is a different result.
"""

import pandas as pd
from PySide6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QAbstractItemView, QHeaderView,
)
from PySide6.QtCore import Qt


class ResultTable(QTableWidget):
    """
    Display search results as a detailed table/spreadsheet.
    
    Shows all database columns so you can see complete specs.
    Rows alternate between white and light gray for readability.
    Read-only (you can't edit the data by clicking cells).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        """
        Create an empty results table.
        
        Sets up:
        - Read-only mode (can't edit cells)
        - Alternating row colors (for readability)
        - Proper resizing of columns
        """
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("alternate-background-color: #f8f5ee;")
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    def load(self, df: pd.DataFrame):
        """
        Fill the table with search results.
        
        Takes all columns from the DataFrame and displays them as table columns.
        Hidden columns (starting with _) are not shown.
        
        Args:
            df: A pandas DataFrame containing the search results
        """
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
