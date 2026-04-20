"""
ui/checkbox_list.py — List widget with checkboxes for explicit multi-selection.
"""

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class CheckboxList(QListWidget):
    """A list widget where each item has a checkbox for explicit multi-selection."""

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self.setFixedHeight(min(len(items) * 24 + 8, 120))
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.addItem(item)
        
        # Connect item clicks to toggle checkbox
        self.itemClicked.connect(self._toggle_checkbox)

    def _toggle_checkbox(self, item: QListWidgetItem):
        """Toggle the checkbox state when item is clicked."""
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    def selected_values(self) -> list[str]:
        """Return list of checked item texts."""
        return [
            self.item(i).text()
            for i in range(self.count())
            if self.item(i).checkState() == Qt.CheckState.Checked
        ]

    def clear_selection(self):
        """Uncheck all items."""
        for i in range(self.count()):
            self.item(i).setCheckState(Qt.CheckState.Unchecked)
