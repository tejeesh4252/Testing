from __future__ import annotations

import os

import pandas as pd
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit,
    QMessageBox, QVBoxLayout,
)


class CorrectionDialog(QDialog):
    """Correct a single transaction's GL mapping. The 'remember' checkbox
    saves the correction scoped to the current fund only -- it will never
    be suggested for a different fund's identical-looking transaction."""

    def __init__(self, parent, txn: dict, fund_name: str, cashbook_path: str,
                 mapper, on_applied):
        super().__init__(parent)
        self.txn = txn
        self.fund_name = fund_name
        self.mapper = mapper
        self.on_applied = on_applied
        self.coa_map: dict[str, str] = {}

        self.setWindowTitle("Correct GL mapping")
        self.setMinimumWidth(460)

        layout = QVBoxLayout(self)

        desc_lbl = QLabel(f"Description: {txn.get('combined_desc', '')}")
        desc_lbl.setWordWrap(True)
        desc_lbl.setProperty("role", "muted")
        layout.addWidget(desc_lbl)

        current_lbl = QLabel(
            f"Current GL: {txn.get('mapped_gl', 'None')} - "
            f"{txn.get('mapped_name', 'Not mapped')}")
        current_lbl.setStyleSheet("color: #f39c12;")
        layout.addWidget(current_lbl)

        layout.addWidget(QLabel("New GL code:"))
        self.gl_edit = QLineEdit(txn.get("mapped_gl", ""))
        layout.addWidget(self.gl_edit)

        self.match_lbl = QLabel("")
        self.match_lbl.setWordWrap(True)
        layout.addWidget(self.match_lbl)

        layout.addWidget(QLabel("GL name:"))
        self.name_edit = QLineEdit(txn.get("mapped_name", ""))
        layout.addWidget(self.name_edit)

        self.remember_chk = QCheckBox(
            f"Remember this correction for {fund_name} only")
        self.remember_chk.setChecked(True)
        layout.addWidget(self.remember_chk)

        self._load_coa(cashbook_path)
        self.gl_edit.textChanged.connect(self._on_gl_change)
        self._on_gl_change()

        btn_row = QHBoxLayout()
        apply_btn = QDialogButtonBox.StandardButton.Ok
        buttons = QDialogButtonBox(apply_btn | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._apply)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_coa(self, cashbook_path: str) -> None:
        try:
            if cashbook_path and os.path.exists(cashbook_path):
                df = pd.read_excel(cashbook_path, sheet_name="COA", dtype=str, usecols=[0, 1])
                df.columns = ["Account", "Account Name"]
                df = df.dropna(subset=["Account"])
                self.coa_map = dict(zip(df["Account"].str.strip(), df["Account Name"].str.strip()))
        except Exception:
            self.coa_map = {}

    def _on_gl_change(self) -> None:
        code = self.gl_edit.text().strip()
        if code in self.coa_map:
            self.name_edit.setText(self.coa_map[code])
            self.match_lbl.setText(f"Found: {self.coa_map[code]}")
            self.match_lbl.setStyleSheet("color: #00d084;")
        elif code:
            suggestions = [k for k in self.coa_map if k.startswith(code)][:4]
            if suggestions:
                self.match_lbl.setText(f"Suggestions: {', '.join(suggestions)}")
                self.match_lbl.setStyleSheet("color: #f39c12;")
            else:
                self.match_lbl.setText("GL code not found in COA")
                self.match_lbl.setStyleSheet("color: #e74c3c;")
        else:
            self.match_lbl.setText("")

    def _apply(self) -> None:
        new_gl = self.gl_edit.text().strip()
        new_name = self.name_edit.text().strip()
        if not new_gl:
            QMessageBox.warning(self, "Missing GL", "Please enter a GL code.")
            return
        if new_gl not in self.coa_map and self.coa_map:
            reply = QMessageBox.question(
                self, "GL not in COA",
                f"'{new_gl}' was not found in the chart of accounts.\n\n"
                f"Use it anyway?")
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.txn["mapped_gl"] = new_gl
        self.txn["mapped_name"] = new_name
        self.txn["confidence"] = "HIGH"
        self.txn["score"] = 100
        self.txn["status"] = "CORRECTED"

        if self.remember_chk.isChecked():
            self.mapper.save_correction(
                self.fund_name, self.txn.get("combined_desc", ""), new_gl, new_name)

        self.on_applied()
        self.accept()
