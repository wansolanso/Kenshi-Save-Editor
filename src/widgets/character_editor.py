from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLabel, QDoubleSpinBox, QLineEdit, QScrollArea,
    QGridLayout, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor

from ..models import Record
from ..game_data import GameDataResolver
from ..i18n import t
from ..constants import (
    CHARACTER_STATS, STAT_DISPLAY, BODY_PART_NAMES,
    MEDICAL_FIELD_DISPLAY, LIMB_NAMES, LIMB_STATUS
)
from ..style import (
    BG_CARD, BORDER, ACCENT, TEXT_DIM, TEXT_MUTED,
    READONLY_CELL_BG, WARNING, BG_LIGHTER
)


PROGRESS_STYLE = f"""
    QProgressBar {{
        background-color: {BG_LIGHTER};
        border: none;
        border-radius: 1px;
        height: 3px;
        text-align: center;
    }}
    QProgressBar::chunk {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {READONLY_CELL_BG}, stop:0.5 {ACCENT}, stop:1 {ACCENT});
        border-radius: 1px;
    }}
"""


class CharacterEditor(QWidget):
    record_modified = pyqtSignal(str)

    def __init__(self, resolver: GameDataResolver | None = None, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self._char_record: Record | None = None
        self._stats_record: Record | None = None
        self._medical_record: Record | None = None
        self._filename: str = ""
        self._stats_filename: str = ""
        self._medical_filename: str = ""
        self._updating = False
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        main = QVBoxLayout(scroll_content)
        main.setContentsMargins(8, 8, 12, 12)
        main.setSpacing(12)

        # ---- Info Card ----
        info_card = QFrame()
        info_card.setStyleSheet(f"QFrame {{ background-color: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 12px; }}")
        info_layout = QHBoxLayout(info_card)
        info_layout.setContentsMargins(16, 14, 16, 14)
        info_layout.setSpacing(16)

        info_col = QVBoxLayout()
        info_col.setSpacing(4)

        name_row = QHBoxLayout()
        name_row.setSpacing(10)
        lbl = QLabel(t("char.name"))
        lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none;")
        self.name_edit = QLineEdit()
        self.name_edit.setMinimumWidth(200)
        self.name_edit.editingFinished.connect(self._on_changed)
        name_row.addWidget(lbl)
        name_row.addWidget(self.name_edit)
        name_row.addStretch()

        lbl2 = QLabel(t("char.age"))
        lbl2.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none;")
        self.age_spin = QDoubleSpinBox()
        self.age_spin.setRange(0, 100)
        self.age_spin.setDecimals(2)
        self.age_spin.setFixedWidth(80)
        self.age_spin.valueChanged.connect(self._on_changed)
        name_row.addWidget(lbl2)
        name_row.addWidget(self.age_spin)
        info_col.addLayout(name_row)

        self.faction_label = QLabel("-")
        self.faction_label.setStyleSheet(f"color: {ACCENT}; font-size: 12px; font-weight: 600; border: none;")
        info_col.addWidget(self.faction_label)

        info_layout.addLayout(info_col, 1)
        main.addWidget(info_card)

        # ---- No Stats Warning ----
        self.no_stats_label = QLabel(t("char.no_stats"))
        self.no_stats_label.setStyleSheet(f"""
            color: {WARNING};
            font-size: 12px;
            padding: 8px 14px;
            background-color: {BG_CARD};
            border: 1px solid {WARNING};
            border-radius: 8px;
        """)
        self.no_stats_label.setVisible(False)
        main.addWidget(self.no_stats_label)

        # ---- Stats ----
        stats_group = QGroupBox(t("section.stats"))
        stats_layout = QGridLayout()
        stats_layout.setContentsMargins(12, 24, 12, 12)
        stats_layout.setSpacing(6)
        stats_layout.setColumnStretch(1, 0)
        stats_layout.setColumnStretch(2, 1)
        stats_layout.setColumnStretch(4, 0)
        stats_layout.setColumnStretch(5, 1)

        self.stat_spins: dict[str, QDoubleSpinBox] = {}
        self.stat_bars: dict[str, QProgressBar] = {}

        for i, key in enumerate(CHARACTER_STATS):
            display = STAT_DISPLAY.get(key, key.title())
            row = i // 2
            col_offset = (i % 2) * 3

            lbl = QLabel(display)
            lbl.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; background: transparent;")
            lbl.setFixedWidth(110)

            spin = QDoubleSpinBox()
            spin.setRange(0, 10000)
            spin.setDecimals(1)
            spin.setSingleStep(1.0)
            spin.setFixedWidth(80)
            spin.valueChanged.connect(self._on_stat_changed)
            self.stat_spins[key] = spin

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setFixedHeight(6)
            bar.setTextVisible(False)
            bar.setStyleSheet(PROGRESS_STYLE)
            self.stat_bars[key] = bar

            sub = QVBoxLayout()
            sub.setSpacing(3)
            row_h = QHBoxLayout()
            row_h.setSpacing(6)
            row_h.addWidget(lbl)
            row_h.addWidget(spin)
            sub.addLayout(row_h)
            sub.addWidget(bar)

            stats_layout.addLayout(sub, row, col_offset, 1, 1)

        stats_group.setLayout(stats_layout)
        self.stats_group = stats_group
        main.addWidget(stats_group)

        # ---- Health ----
        health_group = QGroupBox(t("section.health"))
        health_layout = QVBoxLayout()
        health_layout.setContentsMargins(12, 24, 12, 12)
        health_layout.setSpacing(10)

        vitals = QHBoxLayout()
        vitals.setSpacing(20)
        for label_text, attr, max_v in [(t("char.blood"), "blood_spin", 300), (t("char.hunger"), "hunger_spin", 300)]:
            v = QVBoxLayout()
            v.setSpacing(2)
            l = QLabel(label_text)
            l.setStyleSheet(f"color: {TEXT_DIM}; font-size: 11px; font-weight: 600; background: transparent;")
            s = QDoubleSpinBox()
            s.setRange(0, max_v)
            s.setDecimals(1)
            s.setFixedWidth(100)
            s.valueChanged.connect(self._on_changed)
            setattr(self, attr, s)
            v.addWidget(l)
            v.addWidget(s)
            vitals.addLayout(v)
        vitals.addStretch()
        health_layout.addLayout(vitals)

        self.health_table = QTableWidget()
        self.health_table.setColumnCount(7)
        health_headers = ["Body Part"] + [MEDICAL_FIELD_DISPLAY.get(f, f) for f in ["flesh", "hit", "bandage", "stun", "rig", "wear"]]
        self.health_table.setHorizontalHeaderLabels(health_headers)
        self.health_table.setRowCount(7)
        self.health_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.health_table.verticalHeader().setVisible(False)
        self.health_table.setAlternatingRowColors(True)
        self.health_table.setShowGrid(False)
        self.health_table.setFixedHeight(240)
        self.health_table.itemChanged.connect(self._on_health_changed)
        health_layout.addWidget(self.health_table)

        health_group.setLayout(health_layout)
        self.health_group = health_group
        main.addWidget(health_group)

        # ---- Limbs ----
        limbs_group = QGroupBox(t("section.limbs"))
        limbs_layout = QGridLayout()
        limbs_layout.setContentsMargins(12, 24, 12, 12)
        limbs_layout.setSpacing(10)
        self.limb_combos: dict[str, QComboBox] = {}
        for i, limb in enumerate(LIMB_NAMES):
            l = QLabel(limb.title())
            l.setStyleSheet(f"color: {TEXT_DIM}; font-size: 12px; background: transparent;")
            combo = QComboBox()
            for sv, sn in LIMB_STATUS.items():
                combo.addItem(sn, sv)
            combo.currentIndexChanged.connect(self._on_changed)
            self.limb_combos[limb] = combo
            limbs_layout.addWidget(l, i, 0)
            limbs_layout.addWidget(combo, i, 1)
        limbs_group.setLayout(limbs_layout)
        main.addWidget(limbs_group)

        main.addStretch()
        scroll.setWidget(scroll_content)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def load_character(self, filename: str, char_rec: Record,
                       stats_rec: Record | None, medical_rec: Record | None,
                       stats_filename: str = "", medical_filename: str = ""):
        self._updating = True
        self._char_record = char_rec
        self._stats_record = stats_rec
        self._medical_record = medical_rec
        self._filename = filename
        self._stats_filename = stats_filename or filename
        self._medical_filename = medical_filename or filename

        # Info
        self.name_edit.setText(char_rec.string_fields.get("name", ""))
        faction_sid = char_rec.string_fields.get("owner faction ID", "")
        faction_display = faction_sid
        if self.resolver and faction_sid:
            resolved = self.resolver.resolve(faction_sid)
            if resolved != faction_sid:
                faction_display = resolved
        self.faction_label.setText(faction_display or "-")
        self.age_spin.setValue(char_rec.float_fields.get("age", 1.0))

        # Stats
        has_stats = stats_rec is not None
        self.no_stats_label.setVisible(not has_stats)
        self.stats_group.setVisible(has_stats)

        if stats_rec:
            for key, spin in self.stat_spins.items():
                val = stats_rec.float_fields.get(key, 0.0)
                spin.setValue(val)
                bar = self.stat_bars[key]
                bar.setValue(min(100, int(val)))

        # Health
        has_medical = medical_rec is not None
        self.health_group.setVisible(has_medical)

        if medical_rec:
            self.blood_spin.setValue(medical_rec.float_fields.get("blood", 100.0))
            self.hunger_spin.setValue(medical_rec.float_fields.get("hung", 0.0))

            for idx in range(7):
                part = BODY_PART_NAMES.get(idx, f"Part {idx}")
                name_item = QTableWidgetItem(part)
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                name_item.setBackground(QColor(READONLY_CELL_BG))
                name_item.setForeground(QColor(TEXT_DIM))
                self.health_table.setItem(idx, 0, name_item)

                for col, field in enumerate(["flesh", "hit", "bandage", "stun", "rig", "wear"], 1):
                    val = medical_rec.float_fields.get(f"{field}{idx}", 0.0)
                    self.health_table.setItem(idx, col, QTableWidgetItem(f"{val:.1f}"))

        # Limbs
        limb_val = char_rec.long_fields.get("limbs", 0)
        for i, limb in enumerate(LIMB_NAMES):
            status = (limb_val >> (i * 2)) & 0x3
            combo = self.limb_combos[limb]
            idx = combo.findData(status)
            if idx >= 0:
                combo.setCurrentIndex(idx)

        self._updating = False

    def load_record(self, filename: str, record: Record):
        self.load_character(filename, record, None, None)

    def _on_stat_changed(self):
        if self._updating:
            return
        # Update bars
        for key, spin in self.stat_spins.items():
            self.stat_bars[key].setValue(min(100, int(spin.value())))
        self._apply_changes()
        self.record_modified.emit(self._filename)
        # Stats may be in a different file than the character
        if self._stats_filename and self._stats_filename != self._filename:
            self.record_modified.emit(self._stats_filename)

    def _on_changed(self):
        if self._updating:
            return
        self._apply_changes()
        self.record_modified.emit(self._filename)

    def _on_health_changed(self):
        if self._updating:
            return
        self._apply_health()
        self.record_modified.emit(self._filename)
        # Medical may be in a different file than the character
        if self._medical_filename and self._medical_filename != self._filename:
            self.record_modified.emit(self._medical_filename)

    def _apply_changes(self):
        rec = self._char_record
        if not rec:
            return
        rec.string_fields["name"] = self.name_edit.text()
        rec.float_fields["age"] = self.age_spin.value()

        if self._stats_record:
            for key, spin in self.stat_spins.items():
                self._stats_record.float_fields[key] = spin.value()

        limb_val = 0
        for i, limb in enumerate(LIMB_NAMES):
            s = self.limb_combos[limb].currentData()
            if s is not None:
                limb_val |= (s & 0x3) << (i * 2)
        rec.long_fields["limbs"] = limb_val

        self._apply_health()

    def _apply_health(self):
        med = self._medical_record
        if not med:
            return
        med.float_fields["blood"] = self.blood_spin.value()
        med.float_fields["hung"] = self.hunger_spin.value()
        for idx in range(7):
            for col, field in enumerate(["flesh", "hit", "bandage", "stun", "rig", "wear"], 1):
                item = self.health_table.item(idx, col)
                if item:
                    try:
                        med.float_fields[f"{field}{idx}"] = float(item.text())
                    except ValueError:
                        pass

    def clear(self):
        self._updating = True
        self._char_record = None
        self._stats_record = None
        self._medical_record = None
        self._stats_filename = ""
        self._medical_filename = ""
        self.name_edit.clear()
        self.faction_label.setText("-")
        self.age_spin.setValue(1.0)
        for spin in self.stat_spins.values():
            spin.setValue(0.0)
        for bar in self.stat_bars.values():
            bar.setValue(0)
        self.blood_spin.setValue(100.0)
        self.hunger_spin.setValue(0.0)
        self.health_table.clearContents()
        for combo in self.limb_combos.values():
            combo.setCurrentIndex(0)
        self.no_stats_label.setVisible(False)
        self.stats_group.setVisible(True)
        self.health_group.setVisible(True)
        self._updating = False
