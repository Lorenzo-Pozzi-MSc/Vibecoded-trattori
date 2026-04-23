"""
ui/result_card.py — A single result card

Each result (tractor or machine) is displayed as an attractive card showing:
  - The name/model
  - The brand/manufacturer
  - Key specs (power, width, traction, etc.) as small tags
  - A compatibility score (0-100%)
  - A link to the technical sheet if available
"""

import webbrowser
from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
)
from PySide6.QtCore import Qt, Signal


class ResultCard(QFrame):
    """
    A visual card displaying a single tractor or machine result.
    
    Shows:
    - Product name/model at the top
    - Brand name
    - Key specifications as colored tags
    - Match score (percentage) showing how well it matches your criteria
    - A link button to the technical sheet if available
    
    Has a colored accent bar on the left (green for tractors, brown for machines).
    """
    
    selection_changed = Signal(bool)  # Emitted when checkbox state changes (for tractors)

    def __init__(self, title: str, brand: str, tags: list[tuple[str, bool]],
                 link: str | None, accent: str = "#1f3d1a",
                 selectable: bool = False, parent=None):
        super().__init__(parent)
        """
        Create a result card.
        
        Args:
            title: The product name/model
            brand: The manufacturer/brand name
            tags: List of (tag_text, is_special) tuples showing specs
            score: Match percentage (0-100) or None
            link: URL to technical sheet or None
            accent: Color code for the left accent bar
            selectable: If True, add a checkbox for selection (for tractors)
        """
        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Left accent bar
        self.setStyleSheet(
            f"QFrame#card {{ border-left: 4px solid {accent}; }}"
        )

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)

        # Title row
        title_row = QHBoxLayout()
        
        # Add checkbox if selectable
        if selectable:
            self.checkbox = QCheckBox()
            self.checkbox.setFixedWidth(24)
            self.checkbox.stateChanged.connect(lambda: self.selection_changed.emit(self.checkbox.isChecked()))
            title_row.addWidget(self.checkbox)
        else:
            self.checkbox = None
        
        title_lbl = QLabel(title)
        title_lbl.setObjectName("card_title")
        font = title_lbl.font()
        font.setPointSize(12)
        font.setBold(True)
        title_lbl.setFont(font)
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        lay.addLayout(title_row)

        # Brand
        if brand:
            brand_lbl = QLabel(brand.upper())
            brand_lbl.setObjectName("card_brand")
            font2 = brand_lbl.font()
            font2.setPointSize(9)
            brand_lbl.setFont(font2)
            lay.addWidget(brand_lbl)

        # Tags row
        if tags:
            from ui.helpers import tag
            tag_row = QHBoxLayout()
            tag_row.setSpacing(5)
            tag_row.setContentsMargins(0, 4, 0, 0)
            for text, earth in tags:
                tag_row.addWidget(tag(text, earth))
            tag_row.addStretch()
            lay.addLayout(tag_row)

        # Link
        if link and str(link).startswith("http"):
            btn = QPushButton("↗ Scheda tecnica")
            btn.setObjectName("link_btn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda: webbrowser.open(link))
            lay.addWidget(btn)
