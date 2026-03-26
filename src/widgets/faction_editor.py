from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QAbstractItemView, QHBoxLayout, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from ..models import Record
from ..game_data import GameDataResolver
from ..i18n import t
from ..style import (
    ACCENT, TEXT_DIM, READONLY_CELL_BG, BG_CARD, BORDER
)


class FactionEditor(QWidget):
    record_modified = pyqtSignal(str)

    def __init__(self, resolver: GameDataResolver | None = None, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self._record: Record | None = None
        self._filename: str = ""
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 12, 12)
        layout.setSpacing(10)

        # Header card
        header = QFrame()
        header.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel(t("faction.title"))
        self.title_label.setStyleSheet("font-size: 16px; font-weight: 700; border: none;")

        self.count_badge = QLabel("0")
        self.count_badge.setStyleSheet(f"""
            background-color: {ACCENT};
            color: white;
            border-radius: 10px;
            padding: 2px 10px;
            font-size: 11px;
            font-weight: 700;
            border: none;
        """)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.count_badge)
        layout.addWidget(header)

        # Relations table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([t("faction.col_faction"), t("faction.col_relation"), t("faction.col_trust"), t("faction.col_trust_neg")])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.itemChanged.connect(self._on_value_changed)
        layout.addWidget(self.table)

    def load_faction_data(self, filename: str, record: Record):
        self._updating = True
        self._record = record
        self._filename = filename

        self.title_label.setText(t("faction.relations_of", name=record.name))

        faction_ids = set()
        for key in list(record.long_fields) + list(record.float_fields):
            for prefix in ("relation", "trust", "trustNeg"):
                if key.startswith(prefix):
                    fid = key[len(prefix):]
                    if fid.isdigit():
                        faction_ids.add(fid)

        # Resolve all faction names and filter out mod artifacts
        def _resolve_faction(fid: str) -> tuple[str, bool]:
            """Returns (display_name, is_real_faction)."""
            if not self.resolver:
                return fid, True
            sid_key = f"relationSID{fid}"
            faction_sid = record.string_fields.get(sid_key, "")
            if not faction_sid:
                return fid, True
            resolved = self.resolver.resolve(faction_sid)
            if resolved == faction_sid:
                return fid, True
            up = resolved.upper().strip()
            low = resolved.lower()
            is_artifact = (
                up.startswith("BOOLEAN") or
                up.startswith("ZSPAWNER") or
                up.startswith("DCR ") or up.startswith("DCR_") or
                up.startswith("DEBUG ") or
                up.startswith("DEX") or
                "spawner" in low or
                "template" in low or
                "test" in low or
                "dialogue unlock" in low or
                up in ("FACTION", "NONE", "NULL", "DEFAULT")
            )
            return resolved, not is_artifact

        resolved_factions = []
        for fid in sorted(faction_ids, key=int):
            name, is_real = _resolve_faction(fid)
            if is_real:
                resolved_factions.append((fid, name))

        self.count_badge.setText(str(len(resolved_factions)))
        self.table.setRowCount(len(resolved_factions))

        for row, (fid, faction_display) in enumerate(resolved_factions):
            id_item = QTableWidgetItem(faction_display)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setData(Qt.ItemDataRole.UserRole, fid)  # keep raw ID
            id_item.setBackground(QColor(READONLY_CELL_BG))
            id_item.setForeground(QColor(TEXT_DIM))
            self.table.setItem(row, 0, id_item)

            for col, prefix in [(1, "relation"), (2, "trust"), (3, "trustNeg")]:
                key = f"{prefix}{fid}"
                val = record.long_fields.get(key, record.float_fields.get(key, 0))
                self.table.setItem(row, col, QTableWidgetItem(str(val)))

        self._updating = False

    def _on_value_changed(self):
        if self._updating or not self._record:
            return
        self._apply_changes()
        self.record_modified.emit(self._filename)

    def _apply_changes(self):
        rec = self._record
        if not rec:
            return
        for row in range(self.table.rowCount()):
            id_item = self.table.item(row, 0)
            if not id_item:
                continue
            fid = id_item.data(Qt.ItemDataRole.UserRole) or id_item.text()
            for col, prefix in [(1, "relation"), (2, "trust"), (3, "trustNeg")]:
                key = f"{prefix}{fid}"
                item = self.table.item(row, col)
                if not item:
                    continue
                try:
                    val = int(item.text())
                except ValueError:
                    try:
                        val = float(item.text())
                    except ValueError:
                        continue
                if key in rec.long_fields:
                    rec.long_fields[key] = int(val)
                elif key in rec.float_fields:
                    rec.float_fields[key] = float(val)

    def clear(self):
        self._updating = True
        self._record = None
        self.table.setRowCount(0)
        self.title_label.setText(t("faction.title"))
        self.count_badge.setText("0")
        self._updating = False
