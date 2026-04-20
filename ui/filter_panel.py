"""
ui/filter_panel.py — Left-hand sidebar with all filter controls.
Emits `search_requested` signal with a filters dict when the user clicks Search.
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QScrollArea, QDoubleSpinBox, QCheckBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ui.range_slider import RangeSlider
from ui.multi_select_list import MultiSelectList
from ui.helpers import unique_sorted, section_label, field_label


# ── Main filter panel ─────────────────────────────────────────────────────────

class FilterPanel(QFrame):
    search_requested = Signal(dict)

    def __init__(self, db_trattori: pd.DataFrame, db_macchine: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(290)
        self._db_t = db_trattori
        self._db_m = db_macchine
        self._build_ui()

    def _build_ui(self):
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

        lay.addWidget(field_label("Colture di riferimento"))
        colture_opts = unique_sorted(self._db_m.get("Colture di riferimento", pd.Series()))
        self.w_colture = QComboBox()
        self.w_colture.addItem("Qualsiasi")
        self.w_colture.addItems(colture_opts)
        lay.addWidget(self.w_colture)

        lay.addWidget(field_label("Tipo di operazione"))
        op_opts = unique_sorted(self._db_m.get("Tipo di operazione", pd.Series()))
        self.w_tipo_op = QComboBox()
        self.w_tipo_op.addItem("Qualsiasi")
        self.w_tipo_op.addItems(op_opts)
        lay.addWidget(self.w_tipo_op)

        lay.addWidget(field_label("Tipo di macchina"))
        tm_opts = unique_sorted(self._db_m.get("Tipo di macchina", pd.Series()))
        self.w_tipo_macchina = QComboBox()
        self.w_tipo_macchina.addItem("Qualsiasi")
        self.w_tipo_macchina.addItems(tm_opts)
        lay.addWidget(self.w_tipo_macchina)

        # ── 2. TRACTOR ────────────────────────────────────────────────────
        lay.addWidget(section_label("Trattore"))

        lay.addWidget(field_label("Marchio"))
        self.w_marchio = QComboBox()
        self.w_marchio.addItem("Qualsiasi")
        self.w_marchio.addItems(unique_sorted(self._db_t.get("Marchio", pd.Series())))
        lay.addWidget(self.w_marchio)

        lay.addWidget(field_label("Trazione"))
        self.w_trazione = QComboBox()
        self.w_trazione.addItem("Qualsiasi")
        self.w_trazione.addItems(unique_sorted(self._db_t.get("Trazione", pd.Series())))
        lay.addWidget(self.w_trazione)

        lay.addWidget(field_label("Potenza (CV)"))
        self.w_potenza = RangeSlider(0, 600, 40, 200, step=5, suffix="CV")
        lay.addWidget(self.w_potenza)

        # ── 3. COUPLING ───────────────────────────────────────────────────
        lay.addWidget(section_label("Attacco e PDP"))

        lay.addWidget(field_label("Attacco al trattore"))
        self.w_attacco = QComboBox()
        self.w_attacco.addItem("Qualsiasi")
        self.w_attacco.addItems(unique_sorted(self._db_m.get("Attacco al trattore", pd.Series())))
        lay.addWidget(self.w_attacco)

        lay.addWidget(field_label("Categoria attacco a 3 punti"))
        self.w_cat3pt = QComboBox()
        self.w_cat3pt.addItem("Qualsiasi")
        self.w_cat3pt.addItems(unique_sorted(self._db_m.get("Categoria attacco a 3 punti", pd.Series())))
        lay.addWidget(self.w_cat3pt)

        self.w_pdp = QCheckBox("Richiede PDP")
        lay.addWidget(self.w_pdp)

        # ── 4. DIMENSIONS ─────────────────────────────────────────────────
        lay.addWidget(section_label("Dimensioni di lavoro"))

        lay.addWidget(field_label("Larghezza di lavoro (m)"))
        self.w_larghezza = RangeSlider(0, 20, 1, 6, step=0.1, suffix="m")
        lay.addWidget(self.w_larghezza)

        lay.addWidget(field_label("Profondità di lavoro (cm)"))
        self.w_profondita = RangeSlider(0, 80, 0, 40, step=1, suffix="cm")
        lay.addWidget(self.w_profondita)

        lay.addWidget(field_label("Ingombro larghezza max (m)"))
        self.w_ingombro = QDoubleSpinBox()
        self.w_ingombro.setRange(0, 6)
        self.w_ingombro.setSingleStep(0.1)
        self.w_ingombro.setValue(3.0)
        self.w_ingombro.setSuffix(" m")
        lay.addWidget(self.w_ingombro)

        # ── 5. FIELD ──────────────────────────────────────────────────────
        lay.addWidget(section_label("Campo"))

        lay.addWidget(field_label("Raggio di svolta max (m)"))
        self.w_raggio = QDoubleSpinBox()
        self.w_raggio.setRange(1, 20)
        self.w_raggio.setSingleStep(0.5)
        self.w_raggio.setValue(8.0)
        self.w_raggio.setSuffix(" m")
        lay.addWidget(self.w_raggio)

        self.w_ripiegabile = QCheckBox("Solo macchine ripiegabili")
        lay.addWidget(self.w_ripiegabile)

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
        colture = self.w_colture.currentText()
        tipo_op = self.w_tipo_op.currentText()
        tipo_mach = self.w_tipo_macchina.currentText()
        trazione = self.w_trazione.currentText()
        marchio  = self.w_marchio.currentText()
        cat3pt   = self.w_cat3pt.currentText()
        attacco  = self.w_attacco.currentText()

        filters = {
            "colture":          [] if colture == "Qualsiasi" else [colture],
            "tipo_operazione":  [] if tipo_op == "Qualsiasi" else [tipo_op],
            "tipo_macchina":    [] if tipo_mach == "Qualsiasi" else [tipo_mach],
            "trazione":         None if trazione == "Qualsiasi" else trazione,
            "marchio":          None if marchio  == "Qualsiasi" else marchio,
            "potenza_range":    self.w_potenza.value(),
            "attacco":          None if attacco  == "Qualsiasi" else attacco,
            "cat_3pt":          None if cat3pt   == "Qualsiasi" else cat3pt,
            "pdp_required":     self.w_pdp.isChecked(),
            "larghezza_lavoro": self.w_larghezza.value(),
            "profondita":       self.w_profondita.value(),
            "ingombro_larghezza": self.w_ingombro.value(),
            "raggio_svolta":    self.w_raggio.value(),
            "ripiegabile":      self.w_ripiegabile.isChecked(),
        }
        self.search_requested.emit(filters)

    def _reset(self):
        self.w_colture.setCurrentIndex(0)
        self.w_tipo_op.setCurrentIndex(0)
        self.w_tipo_macchina.setCurrentIndex(0)
        self.w_marchio.setCurrentIndex(0)
        self.w_trazione.setCurrentIndex(0)
        self.w_potenza.reset(40, 200)
        self.w_attacco.setCurrentIndex(0)
        self.w_cat3pt.setCurrentIndex(0)
        self.w_pdp.setChecked(False)
        self.w_larghezza.reset(1, 6)
        self.w_profondita.reset(0, 40)
        self.w_ingombro.setValue(3.0)
        self.w_raggio.setValue(8.0)
        self.w_ripiegabile.setChecked(False)
