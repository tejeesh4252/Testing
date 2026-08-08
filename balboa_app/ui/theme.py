"""Single QSS stylesheet applied at the QApplication level. Colors deliberately
carried over from the original tool so it stays visually familiar."""

BG = "#1e2433"
CARD = "#252d3d"
BORDER = "#323b4f"
TEXT = "#e8ecf3"
MUTED = "#8892a4"
ACCENT = "#3b82f6"
GREEN = "#00d084"
ORANGE = "#f39c12"
RED = "#e74c3c"
PURPLE = "#8e44ad"

STYLESHEET = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
}}
QMainWindow, QDialog {{
    background-color: {BG};
}}
QLabel[role="title"] {{
    font-size: 16px;
    font-weight: 600;
}}
QLabel[role="muted"] {{
    color: {MUTED};
    font-size: 11px;
}}
QLabel[role="stat-value"] {{
    font-size: 22px;
    font-weight: 700;
}}
QFrame[role="card"] {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QPushButton {{
    background-color: {ACCENT};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 14px;
    font-weight: 600;
}}
QPushButton:hover {{ background-color: #2f6fd6; }}
QPushButton:disabled {{ background-color: #3a4256; color: {MUTED}; }}
QPushButton[role="secondary"] {{ background-color: {CARD}; border: 1px solid {BORDER}; }}
QPushButton[role="secondary"]:hover {{ background-color: #2c3547; }}
QPushButton[role="danger"] {{ background-color: {RED}; }}
QPushButton[role="purple"] {{ background-color: {PURPLE}; }}

QLineEdit, QComboBox, QSpinBox {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 6px 8px;
    color: {TEXT};
}}
QComboBox QAbstractItemView {{
    background-color: {CARD};
    color: {TEXT};
    selection-background-color: {ACCENT};
}}

QTableWidget {{
    background-color: {CARD};
    gridline-color: {BORDER};
    border: 1px solid {BORDER};
    border-radius: 6px;
}}
QHeaderView::section {{
    background-color: #2c3547;
    color: {TEXT};
    padding: 6px;
    border: none;
    font-weight: 600;
}}
QTableWidget::item:selected {{
    background-color: #2f6fd6;
}}

QTabWidget::pane {{ border: 1px solid {BORDER}; border-radius: 6px; }}
QTabBar::tab {{
    background-color: {CARD};
    color: {MUTED};
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background-color: {ACCENT};
    color: white;
}}

QPlainTextEdit {{
    background-color: #141924;
    color: #c8d0dc;
    border: 1px solid {BORDER};
    border-radius: 6px;
    font-family: Consolas, monospace;
}}

QStatusBar {{
    background-color: {CARD};
    color: {MUTED};
}}
QProgressBar {{
    background-color: {CARD};
    border: 1px solid {BORDER};
    border-radius: 6px;
    text-align: center;
}}
QProgressBar::chunk {{
    background-color: {ACCENT};
    border-radius: 6px;
}}
"""
