"""
ui/multi_select_list.py — Multi-select list widget.
"""

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QAbstractItemView,
)


class MultiSelectList(QListWidget):
    """A list widget with multi-selection support."""

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setFixedHeight(min(len(items) * 24 + 8, 120))
        for item in items:
            self.addItem(QListWidgetItem(item))

    def selected_values(self) -> list[str]:
        """Return list of selected item texts."""
        return [item.text() for item in self.selectedItems()]

    def clear_selection(self):
        """Clear all selections."""
        self.clearSelection()
