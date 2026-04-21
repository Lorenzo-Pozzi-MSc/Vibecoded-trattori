"""
ui/styles.py — Application styling and theming

Defines:
  - The light color palette (greens, grays, whites)
  - CSS-like styling for all UI elements (buttons, inputs, etc.)
  - An event filter to prevent accidental scrolling on unfocused widgets

The overall design uses:
  - Green accents for tractors
  - Brown accents for implements
  - A light, modern, agricultural-friendly aesthetic
"""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtCore import Qt, QEvent, QObject


class ScrollBlocker(QObject):
    """
    Prevents accidental mouse wheel scrolling on unfocused widgets.
    
    When you hover your mouse over a list or scrollable area but haven't
    clicked it, don't let the scroll wheel scroll it. This prevents
    accidental scrolling when you're trying to interact with something else.
    
    Works by filtering wheel events and only allowing them on focused widgets.
    """
    def eventFilter(self, obj, event):
        """
        Check mouse wheel events and block them on unfocused widgets.
        
        Args:
            obj: The widget that received the event
            event: The event (wheel, click, etc.)
        
        Returns:
            True if the event should be blocked, False to allow it
        """
        if event.type() == QEvent.Type.Wheel:
            # Block wheel events on any unfocused widget
            if not obj.hasFocus():
                return True
        return False


def get_light_palette():
    """
    Create and return the application's color palette.
    
    Sets up all the colors used throughout the app:
    - Background colors (light grays, whites)
    - Text colors (dark grays, blacks)
    - Accent colors (greens for tractors, etc.)
    - Special colors for highlights and tooltips
    
    Returns:
        A QPalette object with all the colors defined
    """
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#f5f7fa"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#eef1f5"))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2e7d32"))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#eef1f5"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1a1a1a"))
    palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.Link, QColor("#43a047"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#e8f5e9"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1a1a1a"))
    return palette


# CSS-like styling for all visual elements
APP_STYLE = """
/* ── Palette ────────────────────────────────────────────────────────────────
   --white       : #ffffff
   --surface     : #f5f7fa
   --surface-2   : #eef1f5
   --border      : #dde1e7
   --accent      : #2e7d32
   --accent-mid  : #43a047
   --accent-pale : #e8f5e9
   --text-dark   : #1a1a1a
   --text-mid    : #4a4a4a
   --text-light  : #888888
*/

QMainWindow, QDialog {
    background-color: #f5f7fa;
}

/* ── Sidebar panel ───────────────────────────────────────────────────────── */
QFrame#sidebar {
    background-color: #eef1f5;
    border-right: 1px solid #dde1e7;
}

/* ── Section labels in sidebar ───────────────────────────────────────────── */
QLabel#section_label {
    color: #2e7d32;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    padding-top: 10px;
    padding-bottom: 2px;
    border-bottom: 1px solid #c8e6c9;
}

/* ── Regular labels ──────────────────────────────────────────────────────── */
QLabel {
    color: #1a1a1a;
    font-size: 13px;
}

QLabel#title_label {
    color: #1a1a1a;
    font-size: 26px;
    font-weight: 700;
}

QLabel#subtitle_label {
    color: #4a4a4a;
    font-size: 13px;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #dde1e7;
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 13px;
    color: #1a1a1a;
    min-height: 28px;
}

QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #43a047;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #dde1e7;
    selection-background-color: #e8f5e9;
    selection-color: #1a1a1a;
    font-size: 13px;
}

/* ── List widget (multi-select) ──────────────────────────────────────────── */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #dde1e7;
    border-radius: 5px;
    font-size: 13px;
    color: #1a1a1a;
}

QListWidget::item {
    padding: 4px 8px;
}

QListWidget::item:selected {
    background-color: #e8f5e9;
    color: #1a1a1a;
}

QListWidget::item:hover {
    background-color: #f1f8f1;
}

/* ── Sliders ──────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    height: 4px;
    background: #dde1e7;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #43a047;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #2e7d32;
    border: 2px solid #ffffff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #43a047;
}

/* ── Checkboxes ──────────────────────────────────────────────────────────── */
QCheckBox {
    font-size: 13px;
    color: #1a1a1a;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #dde1e7;
    border-radius: 3px;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #43a047;
    border-color: #43a047;
    image: none;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
QPushButton#search_btn {
    background-color: #2e7d32;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 20px;
    min-height: 38px;
}

/* ── Help icon button ────────────────────────────────────────────────────── */
QPushButton#help_icon_btn {
    background-color: #43a047;
    color: #ffffff;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    font-size: 11px;
    padding: 0px;
}

QPushButton#help_icon_btn:hover {
    background-color: #2e7d32;
}

QPushButton#help_icon_btn:pressed {
    background-color: #1b5e20;
}

/* ── Tooltip styling with better contrast ───────────────────────────────── */
QToolTip {
    background-color: #2e7d32;
    color: #ffffff;
    border: 2px solid #1b5e20;
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 12px;
    font-weight: 500;
}

QPushButton#search_btn:hover {
    background-color: #43a047;
}

QPushButton#search_btn:pressed {
    background-color: #1b5e20;
}

QPushButton#reset_btn {
    background-color: transparent;
    color: #888888;
    border: 1px solid #dde1e7;
    border-radius: 7px;
    font-size: 13px;
    padding: 7px 20px;
    min-height: 32px;
}

QPushButton#reset_btn:hover {
    background-color: #eef1f5;
    color: #1a1a1a;
}

/* ── Tab bar ─────────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #dde1e7;
    border-radius: 7px;
    background: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: transparent;
    color: #888888;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 20px;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}

QTabBar::tab:selected {
    color: #2e7d32;
    border-bottom: 2px solid #2e7d32;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    color: #43a047;
}

/* ── Results table ────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #ffffff;
    border: none;
    gridline-color: #eef1f5;
    font-size: 12px;
    color: #1a1a1a;
    selection-background-color: #e8f5e9;
    selection-color: #1a1a1a;
}

QTableWidget QHeaderView::section {
    background-color: #f5f7fa;
    color: #4a4a4a;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 6px 10px;
    border: none;
    border-right: 1px solid #dde1e7;
    border-bottom: 2px solid #dde1e7;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #eef1f5;
}

QTableWidget::item:selected {
    background-color: #e8f5e9;
    color: #1a1a1a;
}

/* ── Scroll bars ─────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #f5f7fa;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #dde1e7;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #43a047;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: #f5f7fa;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #dde1e7;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover { background: #43a047; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #dde1e7;
    width: 1px;
}

/* ── Empty state label ───────────────────────────────────────────────────── */
QLabel#empty_state {
    color: #888888;
    font-size: 14px;
}

/* ── Score badge label ───────────────────────────────────────────────────── */
QLabel#score_badge {
    background-color: #43a047;
    color: #ffffff;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
}

/* ── Card widget ─────────────────────────────────────────────────────────── */
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #dde1e7;
    border-radius: 8px;
}

QFrame#card:hover {
    border: 1px solid #43a047;
}

QLabel#card_title {
    color: #1a1a1a;
    font-size: 14px;
    font-weight: 700;
}

QLabel#card_brand {
    color: #43a047;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}

QLabel#tag {
    background-color: #e8f5e9;
    color: #2e7d32;
    border-radius: 4px;
    font-size: 11px;
    padding: 2px 7px;
}

QLabel#tag_earth {
    background-color: #fff3e0;
    color: #e65100;
    border-radius: 4px;
    font-size: 11px;
    padding: 2px 7px;
}

QPushButton#link_btn {
    background: transparent;
    color: #43a047;
    border: none;
    font-size: 12px;
    font-weight: 500;
    text-decoration: underline;
    padding: 0;
    text-align: left;
}

QPushButton#link_btn:hover {
    color: #2e7d32;
}

/* ── Toolbar / header area ───────────────────────────────────────────────── */
QFrame#header {
    background-color: #ffffff;
    border-bottom: 2px solid #e8f5e9;
}

/* ── Tooltip ─────────────────────────────────────────────────────────────── */
QToolTip {
    background-color: #2e7d32;
    color: #ffffff;
    border: none;
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
