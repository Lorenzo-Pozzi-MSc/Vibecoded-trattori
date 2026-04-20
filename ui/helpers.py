"""
ui/helpers.py — Shared utility functions and helper widgets.
"""

import pandas as pd
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFont


def unique_sorted(series: pd.Series) -> list[str]:
    """Extract unique sorted values from a Series, handling comma/semicolon delimiters."""
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
    """Create a styled section header label."""
    lbl = QLabel(text.upper())
    lbl.setObjectName("section_label")
    return lbl


def field_label(text: str) -> QLabel:
    """Create a styled field label."""
    lbl = QLabel(text)
    font = lbl.font()
    font.setPointSize(10)
    lbl.setFont(font)
    return lbl


def tag(text: str, earth: bool = False) -> QLabel:
    """Create a styled tag label."""
    lbl = QLabel(text)
    lbl.setObjectName("tag_earth" if earth else "tag")
    from PySide6.QtWidgets import QSizePolicy
    lbl.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
    return lbl
