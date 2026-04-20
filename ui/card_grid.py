"""
ui/card_grid.py — Scrollable card grid container.
"""

from PySide6.QtWidgets import (
    QScrollArea, QWidget, QVBoxLayout, QFrame,
)
from PySide6.QtCore import Qt


class CardGrid(QScrollArea):
    """A scrollable container for displaying ResultCard widgets."""

    def __init__(self, parent=None):
        super().__init__(parent)
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
        """Replace displayed cards with a new list."""
        # Remove all existing widgets (keep the trailing stretch)
        while self._layout.count() > 1:
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for card in cards:
            self._layout.insertWidget(self._layout.count() - 1, card)
