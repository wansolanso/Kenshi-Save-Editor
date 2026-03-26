from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QHBoxLayout, QFrame, QFormLayout,
    QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QFont

from ..models import Record
from ..constants import TYPECODE_NAMES
from ..style import (
    BG_CARD, BORDER, ACCENT, TEXT_DIM, TEXT_MUTED, READONLY_CELL_BG,
    SECTION_TITLE_STYLE, SUBTITLE_STYLE, ACCENT_LABEL_STYLE, BG_LIGHTER
)


class FieldTable(QTableWidget):
    value_changed = pyqtSignal()

    def __init__(self, columns: list[str], parent=None):
        super().__init__(parent)
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setDefaultSectionSize(160)
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setShowGrid(False)
        self.itemChanged.connect(lambda: self.value_changed.emit())


class RecordInfoCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 12px;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(6)

        # Title row
        title_row = QHBoxLayout()
        self.lbl_name = QLabel("-")
        self.lbl_name.setStyleSheet("font-size: 18px; font-weight: 700; border: none;")
        self.lbl_type_badge = QLabel("")
        self.lbl_type_badge.setStyleSheet(f"""
            background-color: {ACCENT};
            color: white;
            border-radius: 6px;
            padding: 3px 10px;
            font-size: 10px;
            font-weight: 700;
            border: none;
        """)
        title_row.addWidget(self.lbl_name)
        title_row.addStretch()
        title_row.addWidget(self.lbl_type_badge)
        layout.addLayout(title_row)

        # Subtitle row
        self.lbl_subtitle = QLabel("-")
        self.lbl_subtitle.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; border: none;")
        self.lbl_subtitle.setWordWrap(True)
        layout.addWidget(self.lbl_subtitle)

    def set_info(self, name: str, type_name: str, record_id: int, string_id: str, filename: str):
        self.lbl_name.setText(name or "-")
        self.lbl_type_badge.setText(type_name)
        self.lbl_subtitle.setText(f"ID: {record_id}  |  {filename}\n{string_id}")


class RecordEditor(QWidget):
    record_modified = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_record: Record | None = None
        self._current_filename: str = ""
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 12, 12)
        layout.setSpacing(10)

        # Header card
        self.info_card = RecordInfoCard()
        layout.addWidget(self.info_card)

        # Tabs for different field types
        self.tabs = QTabWidget()

        self.bool_table = FieldTable(["Campo", "Valor"])
        self.float_table = FieldTable(["Campo", "Valor"])
        self.long_table = FieldTable(["Campo", "Valor"])
        self.vec3_table = FieldTable(["Campo", "X", "Y", "Z"])
        self.vec4_table = FieldTable(["Campo", "W", "X", "Y", "Z"])
        self.string_table = FieldTable(["Campo", "Valor"])
        self.file_table = FieldTable(["Campo", "Valor"])
        self.ref_table = FieldTable(["Categoria", "Ref Nome", "V0", "V1", "V2"])

        self.tabs.addTab(self.bool_table, "Bool")
        self.tabs.addTab(self.float_table, "Float")
        self.tabs.addTab(self.long_table, "Int")
        self.tabs.addTab(self.vec3_table, "Vec3")
        self.tabs.addTab(self.vec4_table, "Vec4")
        self.tabs.addTab(self.string_table, "String")
        self.tabs.addTab(self.file_table, "File")
        self.tabs.addTab(self.ref_table, "Refs")

        layout.addWidget(self.tabs)

        for table in [self.bool_table, self.float_table, self.long_table,
                      self.vec3_table, self.vec4_table, self.string_table,
                      self.file_table]:
            table.value_changed.connect(self._on_value_changed)

    def load_record(self, filename: str, record: Record):
        self._updating = True
        self._current_record = record
        self._current_filename = filename

        # Header card
        display_name = record.string_fields.get("name", record.name) or record.name
        tname = TYPECODE_NAMES.get(record.typecode, f"TYPE_{record.typecode}")
        self.info_card.set_info(display_name, tname, record.record_id, record.string_id, filename)

        # Load field tables
        self._load_dict_table(self.bool_table, record.bool_fields,
                              lambda v: "True" if v else "False")
        self._load_dict_table(self.float_table, record.float_fields,
                              lambda v: f"{v:.6f}")
        self._load_dict_table(self.long_table, record.long_fields, str)

        # Vec3
        self.vec3_table.setRowCount(len(record.vec3f_fields))
        for i, (key, (x, y, z)) in enumerate(record.vec3f_fields.items()):
            self.vec3_table.setItem(i, 0, self._key_item(key))
            self.vec3_table.setItem(i, 1, QTableWidgetItem(f"{x:.4f}"))
            self.vec3_table.setItem(i, 2, QTableWidgetItem(f"{y:.4f}"))
            self.vec3_table.setItem(i, 3, QTableWidgetItem(f"{z:.4f}"))

        # Vec4
        self.vec4_table.setRowCount(len(record.vec4f_fields))
        for i, (key, (w, x, y, z)) in enumerate(record.vec4f_fields.items()):
            self.vec4_table.setItem(i, 0, self._key_item(key))
            self.vec4_table.setItem(i, 1, QTableWidgetItem(f"{w:.4f}"))
            self.vec4_table.setItem(i, 2, QTableWidgetItem(f"{x:.4f}"))
            self.vec4_table.setItem(i, 3, QTableWidgetItem(f"{y:.4f}"))
            self.vec4_table.setItem(i, 4, QTableWidgetItem(f"{z:.4f}"))

        # String + File
        self._load_dict_table(self.string_table, record.string_fields, str)
        self._load_dict_table(self.file_table, record.filename_fields, str)

        # Refs
        total_refs = sum(len(c.references) for c in record.reference_categories)
        self.ref_table.setRowCount(total_refs)
        row = 0
        for cat in record.reference_categories:
            for ref in cat.references:
                self.ref_table.setItem(row, 0, self._key_item(cat.name))
                self.ref_table.setItem(row, 1, QTableWidgetItem(ref.name))
                self.ref_table.setItem(row, 2, QTableWidgetItem(str(ref.v0)))
                self.ref_table.setItem(row, 3, QTableWidgetItem(str(ref.v1)))
                self.ref_table.setItem(row, 4, QTableWidgetItem(str(ref.v2)))
                row += 1

        # Tab labels with counts
        counts = [
            len(record.bool_fields), len(record.float_fields), len(record.long_fields),
            len(record.vec3f_fields), len(record.vec4f_fields),
            len(record.string_fields), len(record.filename_fields), total_refs
        ]
        names = ["Bool", "Float", "Int", "Vec3", "Vec4", "String", "File", "Refs"]
        for i, (n, c) in enumerate(zip(names, counts)):
            self.tabs.setTabText(i, f"{n} ({c})" if c else n)

        # Select first non-empty tab
        for i, c in enumerate(counts):
            if c > 0:
                self.tabs.setCurrentIndex(i)
                break

        self._updating = False

    def _load_dict_table(self, table: FieldTable, data: dict, formatter):
        table.setRowCount(len(data))
        for i, (key, val) in enumerate(data.items()):
            table.setItem(i, 0, self._key_item(key))
            table.setItem(i, 1, QTableWidgetItem(formatter(val)))

    def _key_item(self, text: str) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        item.setBackground(QColor(READONLY_CELL_BG))
        item.setForeground(QColor(TEXT_DIM))
        return item

    def _on_value_changed(self):
        if self._updating or not self._current_record:
            return
        self._apply_changes()
        self.record_modified.emit(self._current_filename)

    def _apply_changes(self):
        rec = self._current_record
        if not rec:
            return

        for row in range(self.bool_table.rowCount()):
            key_item = self.bool_table.item(row, 0)
            val_item = self.bool_table.item(row, 1)
            if not key_item or not val_item:
                continue
            key = key_item.text()
            val_text = val_item.text().strip().lower()
            rec.bool_fields[key] = val_text in ("true", "1", "yes")

        for row in range(self.float_table.rowCount()):
            key_item = self.float_table.item(row, 0)
            val_item = self.float_table.item(row, 1)
            if not key_item or not val_item:
                continue
            try:
                rec.float_fields[key_item.text()] = float(val_item.text())
            except ValueError:
                pass

        for row in range(self.long_table.rowCount()):
            key_item = self.long_table.item(row, 0)
            val_item = self.long_table.item(row, 1)
            if not key_item or not val_item:
                continue
            try:
                rec.long_fields[key_item.text()] = int(val_item.text())
            except ValueError:
                pass

        keys = list(rec.vec3f_fields.keys())
        for row in range(self.vec3_table.rowCount()):
            if row >= len(keys):
                break
            try:
                x = float(self.vec3_table.item(row, 1).text())
                y = float(self.vec3_table.item(row, 2).text())
                z = float(self.vec3_table.item(row, 3).text())
                rec.vec3f_fields[keys[row]] = (x, y, z)
            except (ValueError, AttributeError):
                pass

        keys = list(rec.vec4f_fields.keys())
        for row in range(self.vec4_table.rowCount()):
            if row >= len(keys):
                break
            try:
                w = float(self.vec4_table.item(row, 1).text())
                x = float(self.vec4_table.item(row, 2).text())
                y = float(self.vec4_table.item(row, 3).text())
                z = float(self.vec4_table.item(row, 4).text())
                rec.vec4f_fields[keys[row]] = (w, x, y, z)
            except (ValueError, AttributeError):
                pass

        for row in range(self.string_table.rowCount()):
            key_item = self.string_table.item(row, 0)
            val_item = self.string_table.item(row, 1)
            if not key_item or not val_item:
                continue
            rec.string_fields[key_item.text()] = val_item.text()

        for row in range(self.file_table.rowCount()):
            key_item = self.file_table.item(row, 0)
            val_item = self.file_table.item(row, 1)
            if not key_item or not val_item:
                continue
            rec.filename_fields[key_item.text()] = val_item.text()

    def clear(self):
        self._current_record = None
        self._current_filename = ""
        self.info_card.set_info("-", "-", 0, "-", "-")
        for i in range(self.tabs.count()):
            table = self.tabs.widget(i)
            if isinstance(table, QTableWidget):
                table.setRowCount(0)
