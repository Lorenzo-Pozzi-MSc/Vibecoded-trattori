"""
ui/styles.py — Application-wide QSS stylesheet.
"""

APP_STYLE = """
/* ── Palette ────────────────────────────────────────────────────────────────
   --green-dark  : #1f3d1a
   --green-mid   : #3a6b2e
   --green-light : #6b9c54
   --green-pale  : #d6e8cc
   --earth       : #8b6340
   --wheat       : #e8d5a3
   --cream       : #f4f0e8
   --border      : #cfc8b8
   --text-dark   : #1a1a14
   --text-mid    : #4a4a3a
   --text-light  : #7a7a68
*/

QMainWindow, QDialog {
    background-color: #f4f0e8;
}

/* ── Sidebar panel ───────────────────────────────────────────────────────── */
QFrame#sidebar {
    background-color: #eae5d8;
    border-right: 1px solid #cfc8b8;
}

/* ── Section labels in sidebar ───────────────────────────────────────────── */
QLabel#section_label {
    color: #3a6b2e;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2px;
    padding-top: 10px;
    padding-bottom: 2px;
    border-bottom: 1px solid #d6e8cc;
}

/* ── Regular labels ──────────────────────────────────────────────────────── */
QLabel {
    color: #1a1a14;
    font-size: 13px;
}

QLabel#title_label {
    color: #1f3d1a;
    font-size: 26px;
    font-weight: 700;
}

QLabel#subtitle_label {
    color: #4a4a3a;
    font-size: 13px;
}

/* ── Inputs ──────────────────────────────────────────────────────────────── */
QComboBox, QLineEdit, QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    border: 1px solid #cfc8b8;
    border-radius: 5px;
    padding: 5px 8px;
    font-size: 13px;
    color: #1a1a14;
    min-height: 28px;
}

QComboBox:focus, QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 1px solid #3a6b2e;
}

QComboBox::drop-down {
    border: none;
    padding-right: 6px;
}

QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #cfc8b8;
    selection-background-color: #d6e8cc;
    selection-color: #1f3d1a;
    font-size: 13px;
}

/* ── List widget (multi-select) ──────────────────────────────────────────── */
QListWidget {
    background-color: #ffffff;
    border: 1px solid #cfc8b8;
    border-radius: 5px;
    font-size: 13px;
    color: #1a1a14;
}

QListWidget::item {
    padding: 4px 8px;
}

QListWidget::item:selected {
    background-color: #d6e8cc;
    color: #1f3d1a;
}

QListWidget::item:hover {
    background-color: #eef6e8;
}

/* ── Sliders ──────────────────────────────────────────────────────────────── */
QSlider::groove:horizontal {
    height: 4px;
    background: #cfc8b8;
    border-radius: 2px;
}

QSlider::sub-page:horizontal {
    background: #3a6b2e;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    background: #1f3d1a;
    border: 2px solid #ffffff;
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #3a6b2e;
}

/* ── Checkboxes ──────────────────────────────────────────────────────────── */
QCheckBox {
    font-size: 13px;
    color: #1a1a14;
    spacing: 6px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 1px solid #cfc8b8;
    border-radius: 3px;
    background: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #1f3d1a;
    border-color: #1f3d1a;
    image: none;
}

QCheckBox::indicator:checked {
    background-color: #1f3d1a;
}

/* ── Buttons ─────────────────────────────────────────────────────────────── */
QPushButton#search_btn {
    background-color: #1f3d1a;
    color: #ffffff;
    border: none;
    border-radius: 7px;
    font-size: 14px;
    font-weight: 600;
    padding: 10px 20px;
    min-height: 38px;
}

QPushButton#search_btn:hover {
    background-color: #3a6b2e;
}

QPushButton#search_btn:pressed {
    background-color: #162d12;
}

QPushButton#reset_btn {
    background-color: transparent;
    color: #7a7a68;
    border: 1px solid #cfc8b8;
    border-radius: 7px;
    font-size: 13px;
    padding: 7px 20px;
    min-height: 32px;
}

QPushButton#reset_btn:hover {
    background-color: #e8e3d8;
    color: #1a1a14;
}

/* ── Tab bar ─────────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #cfc8b8;
    border-radius: 7px;
    background: #ffffff;
    top: -1px;
}

QTabBar::tab {
    background: transparent;
    color: #7a7a68;
    font-size: 13px;
    font-weight: 500;
    padding: 8px 20px;
    border-bottom: 2px solid transparent;
    margin-right: 4px;
}

QTabBar::tab:selected {
    color: #1f3d1a;
    border-bottom: 2px solid #1f3d1a;
    font-weight: 600;
}

QTabBar::tab:hover:!selected {
    color: #3a6b2e;
}

/* ── Results table ────────────────────────────────────────────────────────── */
QTableWidget {
    background-color: #ffffff;
    border: none;
    gridline-color: #ece8e0;
    font-size: 12px;
    color: #1a1a14;
    selection-background-color: #d6e8cc;
    selection-color: #1f3d1a;
}

QTableWidget QHeaderView::section {
    background-color: #eae5d8;
    color: #4a4a3a;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    padding: 6px 10px;
    border: none;
    border-right: 1px solid #cfc8b8;
    border-bottom: 2px solid #cfc8b8;
}

QTableWidget::item {
    padding: 6px 10px;
    border-bottom: 1px solid #ece8e0;
}

QTableWidget::item:selected {
    background-color: #d6e8cc;
    color: #1f3d1a;
}

/* ── Scroll bars ─────────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #f4f0e8;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #cfc8b8;
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover {
    background: #3a6b2e;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background: #f4f0e8;
    height: 8px;
    border-radius: 4px;
}

QScrollBar::handle:horizontal {
    background: #cfc8b8;
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover { background: #3a6b2e; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Splitter ────────────────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #cfc8b8;
    width: 1px;
}

/* ── Empty state label ───────────────────────────────────────────────────── */
QLabel#empty_state {
    color: #7a7a68;
    font-size: 14px;
}

/* ── Score badge label ───────────────────────────────────────────────────── */
QLabel#score_badge {
    background-color: #1f3d1a;
    color: #ffffff;
    border-radius: 10px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
}

/* ── Card widget ─────────────────────────────────────────────────────────── */
QFrame#card {
    background-color: #ffffff;
    border: 1px solid #ddd8ce;
    border-radius: 8px;
}

QFrame#card:hover {
    border: 1px solid #3a6b2e;
}

QLabel#card_title {
    color: #1f3d1a;
    font-size: 14px;
    font-weight: 700;
}

QLabel#card_brand {
    color: #6b9c54;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
}

QLabel#tag {
    background-color: #d6e8cc;
    color: #1f3d1a;
    border-radius: 4px;
    font-size: 11px;
    padding: 2px 7px;
}

QLabel#tag_earth {
    background-color: #efe0cc;
    color: #8b6340;
    border-radius: 4px;
    font-size: 11px;
    padding: 2px 7px;
}

QPushButton#link_btn {
    background: transparent;
    color: #3a6b2e;
    border: none;
    font-size: 12px;
    font-weight: 500;
    text-decoration: underline;
    padding: 0;
    text-align: left;
}

QPushButton#link_btn:hover {
    color: #1f3d1a;
}

/* ── Toolbar / header area ───────────────────────────────────────────────── */
QFrame#header {
    background-color: #f4f0e8;
    border-bottom: 2px solid #d6e8cc;
}

/* ── Tooltip ─────────────────────────────────────────────────────────────── */
QToolTip {
    background-color: #1f3d1a;
    color: #ffffff;
    border: none;
    font-size: 12px;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
