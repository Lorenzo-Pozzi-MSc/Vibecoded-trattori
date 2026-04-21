"""
AgriSelector — Tractor & Implement Matching Tool

This is the main starting point for the application. When you run this program,
it loads two databases (one with tractors and one with implements/machines),
then opens a window where you can set filters and search for compatible equipment.

The app helps farmers find which tractors and machines work well together
based on power, size, and other requirements.

Run with:  python app.py
"""

import sys
import warnings
from pathlib import Path

# Suppress openpyxl Data Validation warning
warnings.filterwarnings("ignore", message="Data Validation extension is not supported")

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import Qt

from data.loader import load_databases
from ui.main_window import MainWindow
from ui.styles import get_light_palette, ScrollBlocker


def _cleanup_pycache():
    """
    Remove all __pycache__ directories from the project.
    
    Called when the app exits to keep the workspace clean.
    """
    import shutil
    root = Path(__file__).parent
    for cache_dir in root.rglob("__pycache__"):
        try:
            shutil.rmtree(cache_dir)
        except Exception as e:
            # Silently fail - this is just cleanup
            pass


def main():
    """
    Start the application and show the main window.
    
    This function:
    - Creates the application window
    - Applies the light theme (colors and styling)
    - Loads the tractor and implement databases from Excel files
    - Shows the search window where users can set filters
    - Keeps the app running until the user closes the window
    """
    app = QApplication(sys.argv)
    app.setApplicationName("AgriSelector")
    
    # ── Apply light theme ────────────────────────────────────────────────
    app.setStyle("Fusion")
    app.setPalette(get_light_palette())
    
    # ── Prevent accidental scrolling on unfocused widgets ──────────────────
    app.installEventFilter(ScrollBlocker())

    # ── Load data ────────────────────────────────────────────────────────
    try:
        tractor_db, machine_db = load_databases()
    except FileNotFoundError as e:
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Database non trovato")
        msg.setText(str(e))
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.exec()
        sys.exit(1)

    # ── Launch window ─────────────────────────────────────────────────────
    window = MainWindow(tractor_db, machine_db)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
