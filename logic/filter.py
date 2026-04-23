"""
logic/filter.py — Machine compatibility filtering

Filters machines based on compatibility with selected tractors.

Compatibility criteria (hard constraints):
1. Operations: Machine operations must match user filter (if specified)
2. Power: Machine power demand must fit within tractor CV range (HP ≈ CV, treated as equivalent)
3. Hitch: Machine 3-point hitch category must match tractor's available categories
4. Weight: Machine weight must be within tractor's lifting capacity
"""

from __future__ import annotations
from typing import Optional

from data.models import Tractor, Machine


def filter_machines_by_tractors(
    machines: list[Machine],
    tractors: list[Tractor],
    selected_operations: Optional[list[str]] = None,
    max_width: Optional[float] = None,
) -> list[Machine]:
    """
    Filter machines based on compatibility with selected tractors.

    A machine is compatible if ALL of these criteria are met:
    1. If operations are specified: machine's operation matches at least one selected
    2. Power: Machine's power demand fits within at least one tractor's CV range
    3. Hitch: Machine's hitch type matches at least one tractor's available categories
    4. Weight: Machine weight is <= at least one tractor's max lifting force

    Args:
        machines: List of all available Machine model instances
        tractors: List of selected Tractor model instances
        selected_operations: Operation types to filter by; None means all operations

    Returns:
        List of compatible Machine instances
    """
    if not machines or not tractors:
        return []

    compatible = []

    for machine in machines:
        # Criterion 1: Operations filter
        if selected_operations and machine.operation_type not in selected_operations:
            continue

        # Criterion 2: Power compatibility (HP ≈ CV, treated as equivalent)
        cv_compatible = False
        for tractor in tractors:
            if tractor.power_min_cv is None or tractor.power_max_cv is None:
                continue
            m_min = machine.min_power_required_hp if machine.min_power_required_hp is not None else tractor.power_min_cv
            m_max = machine.max_power_recommended_hp if machine.max_power_recommended_hp is not None else tractor.power_max_cv
            if m_min <= tractor.power_max_cv and m_max >= tractor.power_min_cv:
                cv_compatible = True
                break

        if not cv_compatible:
            continue

        # Criterion 3: Hitch compatibility
        # Compare machine's hitch categories against tractor's available categories.
        # "Categoria attacco a 3 punti" holds the numeric category (e.g. "2", "2;3"),
        # while "Attacco al trattore" holds attachment style ("Portata posteriore", etc.)
        # which is unrelated to the tractor's category list.
        machine_hitch_raw = machine.raw_data.get("Categoria attacco a 3 punti")
        if not machine_hitch_raw or str(machine_hitch_raw).strip().lower() in ("nan", "na", "", "non fornita"):
            hitch_compatible = True
        else:
            import re
            machine_categories = [v.strip() for v in re.split(r"[;,/]", str(machine_hitch_raw)) if v.strip()]
            hitch_compatible = not machine_categories or any(
                any(cat in tractor.attachment_categories for cat in machine_categories)
                for tractor in tractors
                if tractor.attachment_categories
            )

        if not hitch_compatible:
            continue

        # Criterion 4: Weight compatibility (falls back to raw_data; assume ok if missing)
        machine_weight = _to_float(machine.raw_data.get("Peso max della macchina (kg)"))
        if machine_weight is None:
            weight_compatible = True
        else:
            weight_compatible = any(
                _to_float(t.raw_data.get("Massima forza del sollevatore (kg)")) is None
                or machine_weight <= _to_float(t.raw_data.get("Massima forza del sollevatore (kg)"))
                for t in tractors
            )

        if not weight_compatible:
            continue

        # Criterion 5: Width — pass if no data, otherwise ingombro_min or ingombro_max must be <= limit
        if max_width is not None:
            ing_min = _to_float(machine.raw_data.get("Ingombro larghezza min"))
            ing_max = _to_float(machine.raw_data.get("Ingombro larghezza max"))
            if ing_min is not None or ing_max is not None:
                if not ((ing_min is not None and ing_min <= max_width) or
                        (ing_max is not None and ing_max <= max_width)):
                    continue

        compatible.append(machine)

    return compatible


def _to_float(val) -> Optional[float]:
    """Safely convert value to float, handling European decimal separator (comma)."""
    if val is None:
        return None
    try:
        import pandas as pd
        if pd.isna(val):
            return None
    except (TypeError, ValueError):
        pass
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None
