"""
ui/range_slider.py — A min/max range control for filter settings

Let's you set a range (like "50-200 CV") with two spin boxes.
Makes sure the minimum is never higher than the maximum.
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDoubleSpinBox,
)


class RangeSlider(QWidget):
    """
    A control for setting a min/max range.
    
    Has two spin boxes:
    - Left box: Minimum value
    - Right box: Maximum value
    - A dash (–) between them
    
    Example: [50] – [200] CV
    
    The boxes are linked: if you set min higher than max (or vice versa),
    they automatically adjust to stay valid.
    """

    def __init__(self, minimum: float, maximum: float, lo: float, hi: float,
                 step: float = 1.0, suffix: str = "", parent=None):
        super().__init__(parent)
        """
        Create a range slider.
        
        Args:
            minimum: The smallest allowed value
            maximum: The largest allowed value
            lo: The initial minimum value (default for left box)
            hi: The initial maximum value (default for right box)
            step: How much to increment/decrement when clicking up/down
            suffix: Unit to display (e.g., "CV", "m", etc.)
        """
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
        """
        Get the current min and max values.
        
        Returns:
            A tuple (minimum_value, maximum_value)
        """
        return self.lo_spin.value(), self.hi_spin.value()

    def reset(self, lo: float, hi: float):
        """
        Change the range to new values.
        
        Args:
            lo: New minimum value
            hi: New maximum value
        """
        self.lo_spin.setValue(lo)
        self.hi_spin.setValue(hi)
