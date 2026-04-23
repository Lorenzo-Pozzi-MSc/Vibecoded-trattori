import webbrowser
import pandas as pd

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QCheckBox,
    QDialog, QScrollArea, QWidget, QFormLayout, QDialogButtonBox,
)
from PySide6.QtCore import Qt, Signal


class ResultCard(QFrame):

    selection_changed = Signal(bool)

    def __init__(self, title: str, subtitle: str, specs: list[tuple[str, bool]],
                 link: str | None, accent: str = "#1f3d1a",
                 selectable: bool = False, raw_data: dict | None = None,
                 parent=None):
        super().__init__(parent)
        self._title = title
        self._raw_data = raw_data or {}

        self.setObjectName("card")
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"QFrame#card {{ border-left: 4px solid {accent}; }}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(4)

        # Title row
        title_row = QHBoxLayout()
        if selectable:
            self.checkbox = QCheckBox()
            self.checkbox.setFixedWidth(24)
            self.checkbox.stateChanged.connect(
                lambda: self.selection_changed.emit(self.checkbox.isChecked())
            )
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

        # Subtitle
        if subtitle:
            subtitle_lbl = QLabel(subtitle.upper())
            subtitle_lbl.setObjectName("card_brand")
            font2 = subtitle_lbl.font()
            font2.setPointSize(9)
            subtitle_lbl.setFont(font2)
            lay.addWidget(subtitle_lbl)

        # Specs
        if specs:
            from ui.helpers import tag
            tag_row = QHBoxLayout()
            tag_row.setSpacing(5)
            tag_row.setContentsMargins(0, 4, 0, 0)
            for text, earth in specs:
                tag_row.addWidget(tag(text, earth))
            tag_row.addStretch()
            lay.addLayout(tag_row)

        # Buttons row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(6)
        btn_row.setContentsMargins(0, 4, 0, 0)

        detail_btn = QPushButton("Dettagli")
        detail_btn.setObjectName("link_btn")
        detail_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        detail_btn.clicked.connect(self._open_detail)
        btn_row.addWidget(detail_btn)

        if link and str(link).startswith("http"):
            link_btn = QPushButton("Scheda tecnica")
            link_btn.setObjectName("link_btn")
            link_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            link_btn.clicked.connect(lambda: webbrowser.open(link))
            btn_row.addWidget(link_btn)

        btn_row.addStretch()
        lay.addLayout(btn_row)

    def _open_detail(self):
        dlg = QDialog(self)
        dlg.setWindowTitle(self._title)
        dlg.setMinimumWidth(460)
        dlg.setMinimumHeight(400)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(0, 0, 0, 12)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        form = QFormLayout(container)
        form.setContentsMargins(16, 16, 16, 8)
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        for key, val in self._raw_data.items():
            try:
                if pd.isna(val):
                    continue
            except (TypeError, ValueError):
                pass
            text = str(val).strip()
            if not text or text.lower() in ("nan", "na", "none"):
                continue
            key_lbl = QLabel(str(key))
            key_lbl.setStyleSheet("color: #7a7a68; font-size: 11px;")
            val_lbl = QLabel(text)
            val_lbl.setWordWrap(True)
            val_lbl.setStyleSheet("font-size: 12px;")
            form.addRow(key_lbl, val_lbl)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(dlg.reject)
        outer.addWidget(buttons)

        dlg.exec()
