"""
AgriSelector — Tractor & Implement Matching Tool
Run with:  python app.py
"""

import sys
import warnings
from pathlib import Path

# Suppress openpyxl Data Validation warning
warnings.filterwarnings("ignore", message="Data Validation extension is not supported")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont, QColor, QPalette
from PySide6.QtCore import Qt

from data.loader import load_databases
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AgriSelector")
    
    # ── Force light theme ────────────────────────────────────────────────
    app.setStyle("Fusion")
    
    light_palette = QPalette()
    light_palette.setColor(QPalette.ColorRole.Window, QColor("#f5f7fa"))
    light_palette.setColor(QPalette.ColorRole.WindowText, QColor("#1a1a1a"))
    light_palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#eef1f5"))
    light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor("#2e7d32"))
    light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor("#ffffff"))
    light_palette.setColor(QPalette.ColorRole.Text, QColor("#1a1a1a"))
    light_palette.setColor(QPalette.ColorRole.Button, QColor("#eef1f5"))
    light_palette.setColor(QPalette.ColorRole.ButtonText, QColor("#1a1a1a"))
    light_palette.setColor(QPalette.ColorRole.BrightText, QColor("#ffffff"))
    light_palette.setColor(QPalette.ColorRole.Link, QColor("#43a047"))
    light_palette.setColor(QPalette.ColorRole.Highlight, QColor("#e8f5e9"))
    light_palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#1a1a1a"))
    
    app.setPalette(light_palette)

    # ── Load data ────────────────────────────────────────────────────────
    try:
        db_trattori, db_macchine = load_databases()
    except FileNotFoundError as e:
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Database non trovato")
        msg.setText(str(e))
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()
        sys.exit(1)

    # ── Launch window ─────────────────────────────────────────────────────
    window = MainWindow(db_trattori, db_macchine)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
