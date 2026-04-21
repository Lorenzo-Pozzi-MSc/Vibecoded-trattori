"""
ui/multi_select_list.py — A list where you can select multiple items

This is a standard multi-selection list - you can hold Ctrl/Cmd and click
multiple items to select them. Currently not used (CheckboxList is preferred).
"""

from PySide6.QtWidgets import (
    QListWidget, QListWidgetItem, QAbstractItemView,
)


class MultiSelectList(QListWidget):
    """
    A list where you can select multiple items.
    
    Hold Ctrl/Cmd and click to select/deselect multiple items.
    
    Note: Currently replaced by CheckboxList, which is easier to use
    since checkboxes are more explicit about what's selected.
    """

    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        """
        Create a multi-select list.
        
        Args:
            items: List of text items to display
        """
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setFixedHeight(min(len(items) * 24 + 8, 120))
        for item in items:
            self.addItem(QListWidgetItem(item))

    def selected_values(self) -> list[str]:
        """
        Get the text of all selected items.
        
        Returns:
            List of text from selected items
        """
        return [item.text() for item in self.selectedItems()]

    def clear_selection(self):
        """
        Deselect all items.
        """
        self.clearSelection()
