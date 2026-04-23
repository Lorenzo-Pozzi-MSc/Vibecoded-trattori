from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
)
from PySide6.QtCore import Qt, Signal

from data.models import Tractor, Machine
from ui.card_grid import CardGrid
from ui.result_card import ResultCard


class ResultTab(QWidget):

    tractors_selected = Signal(list)  # emits list[Tractor]

    def __init__(self, is_tractor: bool = True, parent=None):
        super().__init__(parent)
        self._is_tractor = is_tractor
        self._accent = "#1f3d1a" if is_tractor else "#8b6340"
        self._selected_indices: list[int] = []
        self._current_items: list = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(48)
        header.setStyleSheet("background:#f4f0e8; border-bottom:1px solid #d6e8cc;")
        hlay = QHBoxLayout(header)
        hlay.setContentsMargins(16, 0, 16, 0)
        self.count_label = QLabel("")
        self.count_label.setObjectName("subtitle_label")
        hlay.addWidget(self.count_label)
        hlay.addStretch()
        root.addWidget(header)

        self.card_grid = CardGrid()
        root.addWidget(self.card_grid)

        self.empty_label = QLabel("Nessun risultato — prova ad allargare i filtri.")
        self.empty_label.setObjectName("empty_state")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(self.empty_label)
        self.empty_label.hide()

    def clear(self):
        self.card_grid.set_cards([])
        self.card_grid.hide()
        self.empty_label.show()
        self.count_label.setText("Imposta i filtri e clicca Cerca")
        self._current_items = []
        self._selected_indices = []

    def load(self, items: list):
        if not items:
            self.card_grid.hide()
            self.empty_label.show()
            self.count_label.setText("0 risultati")
            return

        self.card_grid.show()
        self.empty_label.hide()
        n = len(items)
        self.count_label.setText(f"{n} risultat{'o' if n == 1 else 'i'}")

        self._current_items = items
        self._selected_indices = []

        cards = []
        for idx, item in enumerate(items):
            title, subtitle, specs, link = self._extract(item)
            card = ResultCard(title, subtitle, specs, link, self._accent,
                              selectable=self._is_tractor,
                              raw_data=item.raw_data)
            if self._is_tractor and card.checkbox:
                card.checkbox.stateChanged.connect(
                    lambda checked, i=idx: self._on_tractor_toggled(i, checked)
                )
            cards.append(card)
        self.card_grid.set_cards(cards)

    def _on_tractor_toggled(self, idx: int, checked: bool):
        if checked:
            if len(self._selected_indices) < 2:
                self._selected_indices.append(idx)
        else:
            if idx in self._selected_indices:
                self._selected_indices.remove(idx)
        selected = [self._current_items[i] for i in self._selected_indices]
        self.tractors_selected.emit(selected)

    def _extract(self, item) -> tuple:
        if self._is_tractor:
            t: Tractor = item
            title = f"{t.brand} | {t.name}" if t.brand else (t.name or "—")
            subtitle = ""
            specs = []
            if t.power_min_cv is not None:
                specs.append((f"{round(t.power_min_cv)}–{round(t.power_max_cv)} CV", False))
            if t.traction_type:
                specs.append((", ".join(t.traction_type), False))
            if t.pto_speeds:
                specs.append((f"PDP: {', '.join(t.pto_speeds)}", False))
            link = t.link or None
        else:
            m: Machine = item
            title = f"{m.machine_type} | {m.manufacturer} | {m.name}" if m.machine_type and m.manufacturer else (m.name or "—")
            subtitle = m.operation_type
            specs = []
            if m.machine_type:
                specs.append((f"{m.machine_type}", False))
            if m.min_power_required_hp is not None or m.max_power_recommended_hp is not None:
                lo = round(m.min_power_required_hp) if m.min_power_required_hp is not None else "?"
                hi = round(m.max_power_recommended_hp) if m.max_power_recommended_hp is not None else "?"
                specs.append((f"Potenza richiesta: {lo}–{hi} CV", False))
            if m.min_work_width_m is not None or m.max_work_width_m is not None:
                lo = m.min_work_width_m if m.min_work_width_m is not None else "?"
                hi = m.max_work_width_m if m.max_work_width_m is not None else "?"
                specs.append((f"Larghezza di lavoro: {lo}–{hi} m", False))
            if m.attachment_type:
                specs.append((f" {m.attachment_type}", True))
            if m.is_foldable:
                specs.append(("📐 Ripiegabile", True))
            link = m.technical_sheet_url or None

        return title, subtitle, specs, link
