"""
ui/checkbox_list.py — A list where each item has a checkbox

Each item in the list has a checkbox next to it. Click to check/uncheck.
Click the checkbox text to also toggle it. Much clearer than Ctrl+click selection.
"""

from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt


class CheckboxList(QListWidget):
    """
    A list where each item has a checkbox for easy selection.
    
    Click any item or its checkbox to toggle it on/off.
    Much more obvious than Ctrl+click multi-selection.
    """

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        """
        Create a checkbox list.
        
        Args:
            items: List of text items to display with checkboxes
        """
        self.setFixedHeight(min(len(items) * 24 + 8, 120))
        for item_text in items:
            item = QListWidgetItem(item_text)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.addItem(item)
        
        # Connect item clicks to toggle checkbox
        self.itemClicked.connect(self._toggle_checkbox)

    def _toggle_checkbox(self, item: QListWidgetItem):
        """
        Toggle a checkbox when its item is clicked.
        
        Switches the checkbox between checked and unchecked.
        
        Args:
            item: The item that was clicked
        """
        if item.checkState() == Qt.CheckState.Checked:
            item.setCheckState(Qt.CheckState.Unchecked)
        else:
            item.setCheckState(Qt.CheckState.Checked)

    def selected_values(self) -> list[str]:
        """
        Get the text of all checked items.
        
        Returns:
            List of text from checked items
        """
        return [
            self.item(i).text()
            for i in range(self.count())
            if self.item(i).checkState() == Qt.CheckState.Checked
        ]

    def clear_selection(self):
        """
        Uncheck all items.
        """
        for i in range(self.count()):
            self.item(i).setCheckState(Qt.CheckState.Unchecked)
