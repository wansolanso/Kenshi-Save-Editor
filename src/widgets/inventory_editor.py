from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QAbstractItemView, QHBoxLayout, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from ..models import Record
from ..game_data import GameDataResolver
from ..constants import SLOT_DISPLAY
from ..style import (
    ACCENT, TEXT_DIM, READONLY_CELL_BG, BG_CARD, BORDER
)


class InventoryEditor(QWidget):
    record_modified = pyqtSignal(str)

    def __init__(self, resolver: GameDataResolver | None = None, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self._items: list[tuple[str, Record]] = []
        self._filename: str = ""
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 12, 12)
        layout.setSpacing(10)

        # Header
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

        self.title_label = QLabel("Inventory")
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

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Item (SID)", "Slot", "Qty", "X", "Y", "Charges", "Quality"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setShowGrid(False)
        self.table.itemChanged.connect(self._on_value_changed)
        layout.addWidget(self.table)

    def load_items(self, filename: str, items: list[Record]):
        self._updating = True
        self._items = [(filename, item) for item in items]
        self._filename = filename

        self.count_badge.setText(str(len(items)))
        self.table.setRowCount(len(items))

        for row, item_rec in enumerate(items):
            # Item name (read-only) - resolve via game data
            sid = item_rec.string_fields.get("base data sid", "")
            if self.resolver and sid:
                display = self.resolver.resolve(sid)
            elif sid:
                display = sid
            else:
                display = item_rec.name or f"#{item_rec.record_id}"
            id_item = QTableWidgetItem(display)
            id_item.setFlags(id_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            id_item.setBackground(QColor(READONLY_CELL_BG))
            id_item.setForeground(QColor(TEXT_DIM))
            self.table.setItem(row, 0, id_item)

            # Slot - display friendly name
            slot_raw = item_rec.string_fields.get("section", "")
            slot_display = SLOT_DISPLAY.get(slot_raw, slot_raw)
            slot_item = QTableWidgetItem(slot_display)
            slot_item.setData(Qt.ItemDataRole.UserRole, slot_raw)  # keep raw for saving
            self.table.setItem(row, 1, slot_item)

            # Quantity
            qty = item_rec.long_fields.get("quantity", 1)
            self.table.setItem(row, 2, QTableWidgetItem(str(qty)))

            # Position
            inv_x = item_rec.long_fields.get("inventory x", 0)
            inv_y = item_rec.long_fields.get("inventory y", 0)
            self.table.setItem(row, 3, QTableWidgetItem(str(inv_x)))
            self.table.setItem(row, 4, QTableWidgetItem(str(inv_y)))

            # Charges
            charges = item_rec.float_fields.get("charges", 0.0)
            self.table.setItem(row, 5, QTableWidgetItem(f"{charges:.1f}"))

            # Quality
            quality = item_rec.float_fields.get("quality", 1.0)
            self.table.setItem(row, 6, QTableWidgetItem(f"{quality:.2f}"))

        self._updating = False

    def _on_value_changed(self):
        if self._updating or not self._items:
            return
        self._apply_changes()
        self.record_modified.emit(self._filename)

    def _apply_changes(self):
        for row, (filename, item_rec) in enumerate(self._items):
            if row >= self.table.rowCount():
                break

            # Slot - use raw value stored in UserRole, not the display name
            slot_item = self.table.item(row, 1)
            if slot_item:
                raw_slot = slot_item.data(Qt.ItemDataRole.UserRole)
                item_rec.string_fields["section"] = raw_slot if raw_slot else slot_item.text()

            # Quantity
            try:
                item_rec.long_fields["quantity"] = int(self.table.item(row, 2).text())
            except (ValueError, AttributeError):
                pass

            # Position
            try:
                item_rec.long_fields["inventory x"] = int(self.table.item(row, 3).text())
            except (ValueError, AttributeError):
                pass
            try:
                item_rec.long_fields["inventory y"] = int(self.table.item(row, 4).text())
            except (ValueError, AttributeError):
                pass

            # Charges
            try:
                item_rec.float_fields["charges"] = float(self.table.item(row, 5).text())
            except (ValueError, AttributeError):
                pass

            # Quality
            try:
                item_rec.float_fields["quality"] = float(self.table.item(row, 6).text())
            except (ValueError, AttributeError):
                pass

    def clear(self):
        self._updating = True
        self._items.clear()
        self.table.setRowCount(0)
        self.count_badge.setText("0")
        self._updating = False
