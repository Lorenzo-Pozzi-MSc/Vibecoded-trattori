"""
ui/helpers.py — Shared utility functions and helper widgets

Contains reusable components and functions used throughout the UI:
  - Functions to extract and format data from databases
  - Helper functions to create styled labels and tags
  - Small UI components that appear in multiple places
"""

import pandas as pd
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont


def unique_sorted(series: pd.Series) -> list[str]:
    """
    Extract unique sorted values from a database column.
    
    Handles cases where a cell contains multiple values separated by
    commas, semicolons, or slashes (e.g., "2WD, 4WD, Tracks").
    
    Returns a clean, sorted list of all unique values.
    
    Args:
        series: A pandas Series (database column) to extract from
    
    Returns:
        A sorted list of unique values with no duplicates
    """
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


def section_label(text: str) -> QLabel:
    """
    Create a styled section header label.
    
    Used to separate different filter groups in the sidebar.
    Example: "CONTESTO OPERATIVO", "TRATTORE", "DIMENSIONI"
    
    Args:
        text: The text to display
    
    Returns:
        A styled QLabel widget ready to use
    """
    lbl = QLabel(text.upper())
    lbl.setObjectName("section_label")
    return lbl


def field_label(text: str) -> QLabel:
    """
    Create a styled field label for filter options.
    
    Used for labels like "Trazione", "Potenza (CV)", etc.
    
    Args:
        text: The text to display
    
    Returns:
        A styled QLabel widget ready to use
    """
    lbl = QLabel(text)
    font = lbl.font()
    font.setPointSize(10)
    lbl.setFont(font)
    return lbl


def tag(text: str, earth: bool = False) -> QLabel:
    """
    Create a small styled tag label for displaying specs.
    
    Tags are small colored boxes showing key info like:
    - "⚡ 50-100 CV" (power range)
    - "↕ Cat. 2" (attachment category)
    - "🔧 2WD" (traction type)
    
    Args:
        text: The text to display
        earth: If True, uses an "earth-toned" style (brown) for implements.
               If False, uses the default style (green) for tractors.
    
    Returns:
        A styled QLabel widget ready to use
    """
    lbl = QLabel(text)
    lbl.setObjectName("tag_earth" if earth else "tag")
    from PySide6.QtWidgets import QSizePolicy
    lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lbl
