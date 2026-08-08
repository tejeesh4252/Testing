"""
Balboa mapping agent -- entry point.

Layering, top to bottom:
    ui/            PyQt6 windows and dialogs -- presentation only
    workers.py      background threads so long operations never freeze the UI
    import_export_service.py   bank import, cashbook GL write-back, ETL export, archiving
    mapping_engine.py           rapidfuzz matching, fund-scoped corrections
    db.py           the only module that opens a SQLite connection
    config.py       absolute path resolution, fund settings
"""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from config import AppConfig
from db import Database
from mapping_engine import MappingEngine
from ui.main_window import MainWindow
from ui.theme import STYLESHEET


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    config = AppConfig()
    db = Database(config)
    mapper = MappingEngine(config, db)

    window = MainWindow(config, db, mapper)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
