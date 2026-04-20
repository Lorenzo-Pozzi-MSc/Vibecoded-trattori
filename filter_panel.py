"""
ui/filter_panel.py — Left-hand sidebar with all filter controls.
Emits `search_requested` signal with a filters dict when the user clicks Search.
"""

from __future__ import annotations
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QFrame, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QListWidget, QListWidgetItem, QSlider,
    QCheckBox, QPushButton, QScrollArea, QDoubleSpinBox,
    QAbstractItemView, QSizePolicy,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


# ── Helpers ──────────────────────────────────────────────────────────────────

def _unique_sorted(series: pd.Series) -> list[str]:
    values = (
        series.dropna()
        .astype(str)
        .str.split(r"[,;/]")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
    )
    return sorted(values)


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text.upper())
    lbl.setObjectName("section_label")
    return lbl


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    font = lbl.font()
    font.setPointSize(10)
    lbl.setFont(font)
    return lbl


# ── Range slider (two handles via two QSliders) ───────────────────────────────

class RangeSlider(QWidget):
    """A min/max range control built from two sliders + spin boxes."""

    def __init__(self, minimum: float, maximum: float, lo: float, hi: float,
                 step: float = 1.0, suffix: str = "", parent=None):
        super().__init__(parent)
        self._min = minimum
        self._max = maximum
        self._suffix = suffix

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Spin boxes row
        spin_row = QHBoxLayout()
        self.lo_spin = QDoubleSpinBox()
        self.hi_spin = QDoubleSpinBox()
        for sp in (self.lo_spin, self.hi_spin):
            sp.setRange(minimum, maximum)
            sp.setSingleStep(step)
            sp.setSuffix(f" {suffix}" if suffix else "")
            sp.setDecimals(1 if step < 1 else 0)
        self.lo_spin.setValue(lo)
        self.hi_spin.setValue(hi)

        spin_row.addWidget(self.lo_spin)
        spin_row.addWidget(QLabel("–"))
        spin_row.addWidget(self.hi_spin)
        layout.addLayout(spin_row)

        # Cross-link: lo ≤ hi
        self.lo_spin.valueChanged.connect(
            lambda v: self.hi_spin.setValue(max(v, self.hi_spin.value()))
        )
        self.hi_spin.valueChanged.connect(
            lambda v: self.lo_spin.setValue(min(v, self.lo_spin.value()))
        )

    def value(self) -> tuple[float, float]:
        return self.lo_spin.value(), self.hi_spin.value()

    def reset(self, lo: float, hi: float):
        self.lo_spin.setValue(lo)
        self.hi_spin.setValue(hi)


# ── Multi-select list ─────────────────────────────────────────────────────────

class MultiSelectList(QListWidget):
    def __init__(self, items: list[str], parent=None):
        super().__init__(parent)
        self.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.setFixedHeight(min(len(items) * 24 + 8, 120))
        for item in items:
            self.addItem(QListWidgetItem(item))

    def selected_values(self) -> list[str]:
        return [item.text() for item in self.selectedItems()]

    def clear_selection(self):
        self.clearSelection()


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
        lay.addWidget(_section_label("Contesto operativo"))

        lay.addWidget(_field_label("Colture di riferimento"))
        colture_opts = _unique_sorted(self._db_m.get("Colture di riferimento", pd.Series()))
        self.w_colture = MultiSelectList(colture_opts)
        lay.addWidget(self.w_colture)

        lay.addWidget(_field_label("Tipo di operazione"))
        op_opts = _unique_sorted(self._db_m.get("Tipo di operazione", pd.Series()))
        self.w_tipo_op = MultiSelectList(op_opts)
        lay.addWidget(self.w_tipo_op)

        lay.addWidget(_field_label("Tipo di macchina"))
        tm_opts = _unique_sorted(self._db_m.get("Tipo di macchina", pd.Series()))
        self.w_tipo_macchina = MultiSelectList(tm_opts)
        lay.addWidget(self.w_tipo_macchina)

        # ── 2. TRACTOR ────────────────────────────────────────────────────
        lay.addWidget(_section_label("Trattore"))

        lay.addWidget(_field_label("Marchio"))
        self.w_marchio = QComboBox()
        self.w_marchio.addItem("Qualsiasi")
        self.w_marchio.addItems(_unique_sorted(self._db_t.get("Marchio", pd.Series())))
        lay.addWidget(self.w_marchio)

        lay.addWidget(_field_label("Trazione"))
        self.w_trazione = QComboBox()
        self.w_trazione.addItem("Qualsiasi")
        self.w_trazione.addItems(_unique_sorted(self._db_t.get("Trazione", pd.Series())))
        lay.addWidget(self.w_trazione)

        lay.addWidget(_field_label("Potenza (CV)"))
        self.w_potenza = RangeSlider(0, 600, 40, 200, step=5, suffix="CV")
        lay.addWidget(self.w_potenza)

        # ── 3. COUPLING ───────────────────────────────────────────────────
        lay.addWidget(_section_label("Attacco e PDP"))

        lay.addWidget(_field_label("Attacco al trattore"))
        self.w_attacco = QComboBox()
        self.w_attacco.addItem("Qualsiasi")
        self.w_attacco.addItems(_unique_sorted(self._db_m.get("Attacco al trattore", pd.Series())))
        lay.addWidget(self.w_attacco)

        lay.addWidget(_field_label("Categoria attacco a 3 punti"))
        self.w_cat3pt = QComboBox()
        self.w_cat3pt.addItem("Qualsiasi")
        self.w_cat3pt.addItems(_unique_sorted(self._db_m.get("Categoria attacco a 3 punti", pd.Series())))
        lay.addWidget(self.w_cat3pt)

        self.w_pdp = QCheckBox("Richiede PDP")
        lay.addWidget(self.w_pdp)

        # ── 4. DIMENSIONS ─────────────────────────────────────────────────
        lay.addWidget(_section_label("Dimensioni di lavoro"))

        lay.addWidget(_field_label("Larghezza di lavoro (m)"))
        self.w_larghezza = RangeSlider(0, 20, 1, 6, step=0.1, suffix="m")
        lay.addWidget(self.w_larghezza)

        lay.addWidget(_field_label("Profondità di lavoro (cm)"))
        self.w_profondita = RangeSlider(0, 80, 0, 40, step=1, suffix="cm")
        lay.addWidget(self.w_profondita)

        lay.addWidget(_field_label("Ingombro larghezza max (m)"))
        self.w_ingombro = QDoubleSpinBox()
        self.w_ingombro.setRange(0, 6)
        self.w_ingombro.setSingleStep(0.1)
        self.w_ingombro.setValue(3.0)
        self.w_ingombro.setSuffix(" m")
        lay.addWidget(self.w_ingombro)

        # ── 5. FIELD ──────────────────────────────────────────────────────
        lay.addWidget(_section_label("Campo"))

        lay.addWidget(_field_label("Raggio di svolta max (m)"))
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
        trazione = self.w_trazione.currentText()
        marchio  = self.w_marchio.currentText()
        cat3pt   = self.w_cat3pt.currentText()
        attacco  = self.w_attacco.currentText()

        filters = {
            "colture":          self.w_colture.selected_values(),
            "tipo_operazione":  self.w_tipo_op.selected_values(),
            "tipo_macchina":    self.w_tipo_macchina.selected_values(),
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
        self.w_colture.clear_selection()
        self.w_tipo_op.clear_selection()
        self.w_tipo_macchina.clear_selection()
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
