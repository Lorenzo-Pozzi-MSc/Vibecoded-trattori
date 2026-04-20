"""
ui/range_slider.py — Min/max range control widget.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
)


class RangeSlider(QWidget):
    """A min/max range control built from two spin boxes."""

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
        """Return the current (min, max) values."""
        return self.lo_spin.value(), self.hi_spin.value()

    def reset(self, lo: float, hi: float):
        """Reset the range to given values."""
        self.lo_spin.setValue(lo)
        self.hi_spin.setValue(hi)
