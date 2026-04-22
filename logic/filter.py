"""
logic/filter.py — Machine compatibility filtering

Filters machines based on compatibility with selected tractors.

Compatibility criteria (hard constraints):
1. Operations: Machine operations must match user filter (if specified)
2. CV Power: Machine power demand must fit within tractor CV range
3. Hitch Type: Machine 3-point hitch category must match tractor's available categories
4. Weight: Machine weight must be within tractor's lifting capacity
"""

from __future__ import annotations
import pandas as pd
from typing import Optional


def filter_machines_by_tractors(
    machines_df: pd.DataFrame,
    tractors_df: pd.DataFrame,
    selected_operations: Optional[list[str]] = None,
) -> pd.DataFrame:
    """
    Filter machines based on compatibility with selected tractors.
    
    A machine is compatible if ALL of these criteria are met:
    1. If operations are specified: machine's operation matches at least one selected
    2. CV Power: Machine's power demand fits within the tractors' CV ranges
    3. Hitch: Machine's hitch type matches at least one tractor's available types
    4. Weight: Machine weight is <= at least one tractor's max lifting force
    
    Args:
        machines_df: DataFrame of all available machines
        tractors_df: DataFrame of selected tractors (all returned tractors are considered)
        selected_operations: List of operation types to filter by (e.g., ["Aratura", "Fresatura"])
                           If None, all operations are considered
    
    Returns:
        DataFrame of compatible machines
    """
    
    if machines_df.empty or tractors_df.empty:
        return pd.DataFrame()
    
    compatible_machines = []
    
    # Extract tractor specs
    tractor_cv_mins = tractors_df.get("Pot. min (CV)", pd.Series(dtype=float))
    tractor_cv_maxs = tractors_df.get("Pot. max (CV)", pd.Series(dtype=float))
    tractor_attachments = tractors_df.get("Categorie attacco a 3 punti disponibili", pd.Series(dtype=str))
    tractor_max_weights = tractors_df.get("Massima forza del sollevatore (kg)", pd.Series(dtype=float))
    
    # If max weights don't exist, try alternative field names
    if tractor_max_weights.isna().all():
        # Try raw_data if available, or use a very high default
        tractor_max_weights = pd.Series([float('inf')] * len(tractors_df))
    
    # Process each machine
    for _, machine in machines_df.iterrows():
        # Criterion 1: Operations filter (if specified)
        if selected_operations:
            machine_op = str(machine.get("Tipo di operazione", "")).strip()
            if machine_op not in selected_operations:
                continue
        
        # Get machine specs
        machine_min_power = _to_float(machine.get("Potenza minima richiesta HP"))
        machine_max_power = _to_float(machine.get("Potenza massima consigliata HP"))
        machine_hitch = str(machine.get("Categoria attacco a 3 punti", "")).strip()
        machine_weight = _to_float(machine.get("Peso max della macchina (kg)"))
        
        # Criterion 2: CV Power compatibility
        # Machine's power demand must fit within at least one tractor's range
        cv_compatible = False
        for t_min, t_max in zip(tractor_cv_mins, tractor_cv_maxs):
            t_min = _to_float(t_min)
            t_max = _to_float(t_max)
            
            if t_min is None or t_max is None:
                continue
            
            # Check if machine's power demand overlaps with tractor's range
            # machine_min_power <= t_max AND machine_max_power >= t_min
            m_min = machine_min_power if machine_min_power is not None else t_min
            m_max = machine_max_power if machine_max_power is not None else t_max
            
            if m_min <= t_max and m_max >= t_min:
                cv_compatible = True
                break
        
        if not cv_compatible:
            continue
        
        # Criterion 3: Hitch type compatibility
        # Machine's hitch must match at least one tractor's available attachments
        hitch_compatible = False
        for t_attachment in tractor_attachments:
            t_attach_str = str(t_attachment).strip()
            if not t_attach_str:
                continue
            # Check if machine hitch is in tractor's available categories
            # Categories are typically comma-separated like "1, 2, 3"
            if machine_hitch in t_attach_str or _is_hitch_compatible(machine_hitch, t_attach_str):
                hitch_compatible = True
                break
        
        if not hitch_compatible:
            continue
        
        # Criterion 4: Weight compatibility
        # Machine weight must be within at least one tractor's lifting capacity
        weight_compatible = False
        if machine_weight is None:
            # If machine weight not specified, assume compatible
            weight_compatible = True
        else:
            for t_weight in tractor_max_weights:
                t_weight = _to_float(t_weight)
                if t_weight is None or t_weight == float('inf'):
                    weight_compatible = True
                    break
                if machine_weight <= t_weight:
                    weight_compatible = True
                    break
        
        if not weight_compatible:
            continue
        
        # All criteria met - add machine to compatible list
        compatible_machines.append(machine)
    
    if not compatible_machines:
        return pd.DataFrame()
    
    return pd.DataFrame(compatible_machines)


def _to_float(val) -> Optional[float]:
    """Safely convert value to float, handling European decimal separator (comma)."""
    if pd.isna(val):
        return None
    try:
        return float(str(val).replace(",", ".").strip())
    except (ValueError, TypeError):
        return None


def _is_hitch_compatible(machine_hitch: str, tractor_categories: str) -> bool:
    """
    Check if machine hitch is compatible with tractor categories.
    
    Handles various formats like "1", "2", "3", "1, 2, 3", etc.
    """
    if not machine_hitch or not tractor_categories:
        return False
    
    # Parse categories from comma-separated string
    machine_cat = machine_hitch.strip()
    tractor_cats = [cat.strip() for cat in tractor_categories.split(",")]
    
    return machine_cat in tractor_cats
