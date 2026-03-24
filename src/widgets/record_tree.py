from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeWidget, QTreeWidgetItem,
    QLineEdit, QLabel, QHBoxLayout, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont, QColor, QIcon

from ..models import Record
from ..constants import TYPECODE_NAMES
from ..style import (
    SEARCH_INPUT_STYLE, COUNT_LABEL_STYLE, ACCENT, TEXT_DIM,
    BG_CARD, BORDER, TEXT_MUTED
)

# Icons for typecodes (unicode)
TYPE_ICONS = {
    36: "\u2694",   # swords - character
    25: "\u2b50",   # star - stats
    42: "\U0001f392",  # backpack - inventory
    37: "\u2696",   # scales - faction
    34: "\u26e8",   # shield - platoon
    57: "\u2764",   # heart - medical
    67: "\U0001f916",  # robot - AI
    41: "\U0001f3ad",  # masks - appearance
    94: "\U0001f3d8",  # city - town
}


class RecordTree(QWidget):
    record_selected = pyqtSignal(str, object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._records: list[tuple[str, Record]] = []
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 6, 12)
        layout.setSpacing(8)

        # Title
        title = QLabel("Records")
        title.setStyleSheet("font-size: 16px; font-weight: 700; padding: 4px 0;")
        layout.addWidget(title)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("\U0001f50d  Buscar records...")
        self.search_input.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search_input.textChanged.connect(self._filter)
        layout.addWidget(self.search_input)

        # Count label
        self.count_label = QLabel("0 records")
        self.count_label.setStyleSheet(COUNT_LABEL_STYLE)
        layout.addWidget(self.count_label)

        # Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Nome", "Tipo", "ID"])
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 80)
        self.tree.setIndentation(16)
        self.tree.setAnimated(True)
        self.tree.setRootIsDecorated(True)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.setAlternatingRowColors(True)
        layout.addWidget(self.tree)

    def load_records(self, records: list[tuple[str, Record]]):
        self._records = records
        self._rebuild_tree()

    def _rebuild_tree(self, filter_text: str = ""):
        self.tree.clear()
        filter_lower = filter_text.lower()

        groups: dict[int, list[tuple[str, Record]]] = {}
        for filename, rec in self._records:
            if filter_lower:
                name = rec.string_fields.get("name", rec.name)
                searchable = f"{name} {rec.name} {rec.string_id} {filename}".lower()
                if filter_lower not in searchable:
                    continue
            groups.setdefault(rec.typecode, []).append((filename, rec))

        total = 0
        for tc in sorted(groups.keys()):
            recs = groups[tc]
            total += len(recs)
            tname = TYPECODE_NAMES.get(tc, f"TYPE_{tc}")
            icon = TYPE_ICONS.get(tc, "\u25cf")
            group_item = QTreeWidgetItem([f"{icon} {tname} ({len(recs)})", "", ""])
            group_item.setFlags(group_item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            font = group_item.font(0)
            font.setBold(True)
            font.setPointSize(10)
            group_item.setFont(0, font)
            group_item.setForeground(0, QColor(TEXT_DIM))

            for filename, rec in recs:
                display = rec.string_fields.get("name", rec.name) or rec.name
                child = QTreeWidgetItem([display, str(rec.typecode), str(rec.record_id)])
                child.setData(0, Qt.ItemDataRole.UserRole, (filename, rec))
                child.setToolTip(0, f"{filename}\n{rec.string_id}")
                group_item.addChild(child)

            self.tree.addTopLevelItem(group_item)
            if filter_lower:
                group_item.setExpanded(True)

        self.count_label.setText(f"{total} records")

    def _filter(self, text: str):
        self._rebuild_tree(text)

    def _on_item_clicked(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            filename, rec = data
            self.record_selected.emit(filename, rec)
