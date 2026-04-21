"""
ui/card_grid.py — A scrollable container for result cards

This holds multiple result cards stacked vertically.
You can scroll up and down to see all results.
"""

from PySide6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QFrame,
)
from PySide6.QtCore import Qt


class CardGrid(QScrollArea):
    """
    A scrollable container for displaying result cards vertically.
    
    Cards are stacked on top of each other, and you can scroll
    to see them all. Works like a list of pretty cards.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        """
        Create an empty scrollable card container.
        
        Sets up scrolling and the space where cards will be added.
        """
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(16, 16, 16, 16)
        self._layout.setSpacing(10)
        self._layout.addStretch()
        self.setWidget(self._container)

    def set_cards(self, cards: list):
        """
        Replace all displayed cards with a new list.
        
        Removes the old cards and displays new ones.
        Useful when updating results after a search.
        
        Args:
            cards: A list of ResultCard widgets to display
        """
        # Remove all existing widgets (keep the trailing stretch)
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for card in cards:
            self._layout.insertWidget(self._layout.count() - 1, card)
