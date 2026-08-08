from __future__ import annotations

from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QVBoxLayout,
)


class SettingsDialog(QDialog):
    """Edits config.json: the database location and each fund's cashbook
    path. Nothing here is inferred from the working directory -- every
    path is explicit and saved."""

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setMinimumWidth(560)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Database file location:"))
        db_row = QHBoxLayout()
        self.db_edit = QLineEdit(str(config.db_path))
        db_row.addWidget(self.db_edit, 1)
        db_browse = QLabel("Browse...")
        db_browse.setStyleSheet("color:#3b82f6; text-decoration:underline;")
        db_browse.mousePressEvent = lambda _e: self._browse_db()
        db_row.addWidget(db_browse)
        layout.addLayout(db_row)
        note = QLabel(
            "If pointing this at a OneDrive/SharePoint synced folder, set that "
            "folder to \"Always keep on this device\" so the file is never a "
            "cloud-only placeholder.")
        note.setWordWrap(True)
        note.setProperty("role", "muted")
        layout.addWidget(note)

        self.fund_edits: dict[str, QLineEdit] = {}
        for fund_name in config.fund_names:
            layout.addWidget(QLabel(f"{fund_name} cashbook file:"))
            row = QHBoxLayout()
            edit = QLineEdit(config.cashbook_path(fund_name))
            self.fund_edits[fund_name] = edit
            row.addWidget(edit, 1)
            browse = QLabel("Browse...")
            browse.setStyleSheet("color:#3b82f6; text-decoration:underline;")
            browse.mousePressEvent = lambda _e, fn=fund_name: self._browse_cashbook(fn)
            row.addWidget(browse)
            layout.addLayout(row)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_db(self) -> None:
        fp, _ = QFileDialog.getSaveFileName(
            self, "Select or create database file", self.db_edit.text(),
            "SQLite database (*.db)")
        if fp:
            self.db_edit.setText(fp)

    def _browse_cashbook(self, fund_name: str) -> None:
        fp, _ = QFileDialog.getOpenFileName(
            self, f"Select {fund_name} cashbook", self.fund_edits[fund_name].text(),
            "Excel files (*.xlsx)")
        if fp:
            self.fund_edits[fund_name].setText(fp)

    def _save(self) -> None:
        if not self.db_edit.text().strip():
            QMessageBox.warning(self, "Missing path", "Database path cannot be empty.")
            return
        self.config.db_path = self.db_edit.text().strip()
        for fund_name, edit in self.fund_edits.items():
            self.config.set_cashbook_path(fund_name, edit.text().strip())
        self.config.save()
        QMessageBox.information(
            self, "Saved",
            "Settings saved. Restart the app for a changed database path to take effect.")
        self.accept()
