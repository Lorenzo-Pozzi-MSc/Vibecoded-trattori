"""
ui/filter_panel.py — The search settings sidebar on the left

This is where you set your search criteria:
  - What type of operation you're doing
  - What traction type you need
  - Tractor power range (in CV - cavalli vapore, or horsepower)
  - Minimum working width needed
  - Maximum turning radius allowed

When you click Search, this panel sends all your choices to the matching engine.
When you click Reset, it clears all your choices back to defaults.
"""

from __future__ import annotations
import webbrowser
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QDoubleSpinBox, QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.range_slider import RangeSlider
from ui.multi_select_list import MultiSelectList
from ui.checkbox_list import CheckboxList
from ui.helpers import unique_sorted, section_label, field_label


# ── Main filter panel ─────────────────────────────────────────────────────────

class FilterPanel(QFrame):
    """
    The left sidebar where you set search criteria.
    
    Contains controls for:
    - Operation type (plowing, harvesting, etc.)
    - Traction type (2WD, 4WD, tracks)
    - Tractor power range
    - Maximum working width
    - Maximum turning radius
    
    When you click Search, it collects all your choices and sends them
    to the matching engine.
    """
    
    search_requested = Signal(dict)
    reset_requested = Signal()

    def __init__(self, db_trattori: pd.DataFrame, db_macchine: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(290)
        self._db_t = db_trattori
        self._db_m = db_macchine
        """
        Create the filter panel with all search options.
        
        Reads the tractor and machine databases to populate the filter options
        with real choices from your data.
        """
        self._build_ui()

    def _build_ui(self):
        """
        Construct all the visual controls in the filter panel.
        
        Creates and arranges:
        - Section headers
        - Checkboxes and dropdowns for filter options
        - Search and Reset buttons
        - A scroll area so everything fits even on small screens
        """
        # Outer layout holds a scroll area so it works on small screens
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)

        lay = QVBoxLayout(container)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(6)

        # ── Title ────────────────────────────────────────────────────────
        title = QLabel("⚙ Parametri")
        title.setObjectName("title_label")
        font = title.font()
        font.setPointSize(14)
        font.setBold(True)
        title.setFont(font)
        lay.addWidget(title)
        lay.addSpacing(4)

        # ── 1. OPERATIONAL CONTEXT ────────────────────────────────────────
        lay.addWidget(section_label("Contesto operativo"))

        lay.addWidget(field_label("Tipo di operazione"))
        op_opts = unique_sorted(self._db_m.get("Tipo di operazione", pd.Series()))
        self.w_tipo_op = CheckboxList(op_opts)
        lay.addWidget(self.w_tipo_op)

        # ── 2. TRACTOR ────────────────────────────────────────────────────
        lay.addWidget(section_label("Trattore"))

        # Trazione label with help tooltip
        trazione_label_lay = QHBoxLayout()
        trazione_label_lay.setContentsMargins(0, 0, 0, 0)
        trazione_label_lay.setSpacing(4)
        trazione_label_lay.addWidget(field_label("Trazione"))
        
        # Help icon - clickable to open link
        help_btn = QPushButton("?")
        help_btn.setObjectName("help_icon_btn")
        help_btn.setFixedSize(18, 18)
        help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        help_btn.setToolTip("Click to check traction requirements for site slopes")
        help_btn.clicked.connect(
            lambda: webbrowser.open("https://spisal.aulss9.veneto.it/mys/apridoc/iddoc/7359")
        )
        trazione_label_lay.addWidget(help_btn)
        trazione_label_lay.addStretch()
        
        lay.addLayout(trazione_label_lay)
        self.w_trazione = CheckboxList(unique_sorted(self._db_t.get("Trazione", pd.Series())))
        lay.addWidget(self.w_trazione)

        lay.addWidget(field_label("Potenza (CV)"))
        self.w_potenza = RangeSlider(0, 600, 40, 200, step=5, suffix="CV")
        lay.addWidget(self.w_potenza)

        # ── 3. DIMENSIONS ─────────────────────────────────────────────────
        lay.addWidget(section_label("Dimensioni di lavoro"))


        lay.addWidget(field_label("Ingombro larghezza max (m)"))
        self.w_ingombro = QDoubleSpinBox()
        self.w_ingombro.setRange(0, 6)
        self.w_ingombro.setSingleStep(0.1)
        self.w_ingombro.setValue(3.0)
        self.w_ingombro.setSuffix(" m")
        lay.addWidget(self.w_ingombro)

        # ── 4. FIELD ──────────────────────────────────────────────────────
        lay.addWidget(section_label("Campo"))

        lay.addWidget(field_label("Raggio di svolta max (m)"))
        self.w_raggio = QDoubleSpinBox()
        self.w_raggio.setRange(1, 20)
        self.w_raggio.setSingleStep(0.5)
        self.w_raggio.setValue(8.0)
        self.w_raggio.setSuffix(" m")
        lay.addWidget(self.w_raggio)

        # ── Buttons ───────────────────────────────────────────────────────
        lay.addSpacing(12)

        self.btn_search = QPushButton("🔍  Cerca")
        self.btn_search.setObjectName("search_btn")
        self.btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_search.clicked.connect(self._emit_search)
        lay.addWidget(self.btn_search)

        self.btn_reset = QPushButton("↺  Reset filtri")
        self.btn_reset.setObjectName("reset_btn")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset)
        lay.addWidget(self.btn_reset)

        lay.addStretch()

    # ── Collect & emit ────────────────────────────────────────────────────────

    def _emit_search(self):
        """
        Collect all your filter choices and send them to the search engine.
        
        This gets called when you click the Search button.
        It gathers all the values you've selected and sends them as a signal.
        """
        filters = {
            "tipo_operazione":  self.w_tipo_op.selected_values(),
            "trazione":         self.w_trazione.selected_values(),
            "potenza_range":    self.w_potenza.value(),
            "ingombro_larghezza": self.w_ingombro.value(),
            "raggio_svolta":    self.w_raggio.value(),
        }
        self.search_requested.emit(filters)

    def _reset(self):
        self.w_tipo_op.clear_selection()
        self.w_trazione.clear_selection()
        self.w_potenza.reset(40, 200)
        self.w_ingombro.setValue(3.0)
        self.w_raggio.setValue(8.0)
        self.reset_requested.emit()