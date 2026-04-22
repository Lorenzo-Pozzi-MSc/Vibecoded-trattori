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
    QWidget, QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QScrollArea, QDoubleSpinBox, QLabel,
)
from PySide6.QtCore import Qt, Signal

from data.models import TractorDatabase, MachineDatabase
from ui.range_slider import RangeSlider
from ui.checkbox_list import CheckboxList
from ui.helpers import unique_sorted, section_label, field_label


class FilterPanel(QFrame):
    """
    The left sidebar where you set search criteria.

    Reads unique values from the typed database objects to populate
    filter options with real choices from your data.
    """

    search_requested = Signal(dict)
    reset_requested = Signal()

    def __init__(self, tractor_db: TractorDatabase, machine_db: MachineDatabase, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(290)
        self._tractor_db = tractor_db
        self._machine_db = machine_db
        self._build_ui()

    def _build_ui(self):
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
        op_opts = unique_sorted(self._machine_db.dataframe.get("Tipo di operazione", pd.Series(dtype=str)))
        self.w_tipo_op = CheckboxList(op_opts)
        lay.addWidget(self.w_tipo_op)

        # ── 2. TRACTOR ────────────────────────────────────────────────────
        lay.addWidget(section_label("Trattore"))

        trazione_label_lay = QHBoxLayout()
        trazione_label_lay.setContentsMargins(0, 0, 0, 0)
        trazione_label_lay.setSpacing(4)
        trazione_label_lay.addWidget(field_label("Trazione"))

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

        traction_opts = unique_sorted(self._tractor_db.dataframe.get("Trazione", pd.Series(dtype=str)))
        self.w_trazione = CheckboxList(traction_opts)
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

        self.btn_reset = QPushButton("↺  Reset")
        self.btn_reset.setObjectName("reset_btn")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self._reset)
        lay.addWidget(self.btn_reset)

        lay.addStretch()

    def _emit_search(self):
        filters = {
            "tipo_operazione":    self.w_tipo_op.selected_values(),
            "trazione":           self.w_trazione.selected_values(),
            "potenza_range":      self.w_potenza.value(),
            "ingombro_larghezza": self.w_ingombro.value(),
            "raggio_svolta":      self.w_raggio.value(),
        }
        self.search_requested.emit(filters)

    def _reset(self):
        self.w_tipo_op.clear_selection()
        self.w_trazione.clear_selection()
        self.w_potenza.reset(40, 200)
        self.w_ingombro.setValue(3.0)
        self.w_raggio.setValue(8.0)
        self.reset_requested.emit()
