"""
AgriSelector — Tractor & Implement Matching Tool
Run with:  python app.py
"""

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt

from data.loader import load_databases
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AgriSelector")
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)

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
