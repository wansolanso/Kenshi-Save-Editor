from __future__ import annotations
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QLineEdit, QSpinBox
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QCursor, QColor

from ..models import Record, SaveFile
from ..save_manager import SaveManager
from ..game_data import GameDataResolver
from ..style import (
    BG_LIGHT, BG_CARD, BG_LIGHTER, BORDER, ACCENT, ACCENT_DIM, ACCENT_HOVER,
    TEXT, TEXT_DIM, TEXT_MUTED, INPUT_BG, SELECTION, SEARCH_INPUT_STYLE,
    SUCCESS, WARNING
)

PLAYER_FACTION = "204-gamedata.base"


class MoneyWidget(QFrame):
    """Always-visible money editor at top of sidebar."""
    money_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._record: Record | None = None
        self._updating = False
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_CARD};
                border: 1px solid {BORDER};
                border-radius: 10px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(10)

        icon = QLabel("\U0001f4b0")
        icon.setStyleSheet("font-size: 20px; border: none; background: transparent;")
        layout.addWidget(icon)

        col = QVBoxLayout()
        col.setSpacing(1)
        lbl = QLabel("CATS")
        lbl.setStyleSheet(f"font-size: 9px; font-weight: 700; color: {TEXT_MUTED}; letter-spacing: 2px; border: none; background: transparent;")
        col.addWidget(lbl)

        self.spin = QSpinBox()
        self.spin.setRange(0, 2_000_000_000)
        self.spin.setSingleStep(1000)
        self.spin.setStyleSheet(f"""
            QSpinBox {{
                font-size: 16px;
                font-weight: 700;
                color: {SUCCESS};
                background: transparent;
                border: none;
                padding: 0;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 0; height: 0;
            }}
        """)
        self.spin.valueChanged.connect(self._on_changed)
        col.addWidget(self.spin)
        layout.addLayout(col, 1)

    def load_money(self, record: Record):
        self._updating = True
        self._record = record
        val = record.long_fields.get("player money", 0)
        self.spin.setValue(val)
        self._updating = False

    def _on_changed(self, val):
        if self._updating or not self._record:
            return
        self._record.long_fields["player money"] = val
        self.money_changed.emit(val)


class CharacterCard(QFrame):
    clicked = pyqtSignal(str, object)

    def __init__(self, filename: str, char_rec: Record, stats_rec: Record | None,
                 is_player: bool = False, parent=None):
        super().__init__(parent)
        self._filename = filename
        self._record = char_rec
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(58)
        self._selected = False

        name = char_rec.string_fields.get("name", char_rec.name) or "???"
        stats_text = ""
        if stats_rec:
            atk = stats_rec.float_fields.get("attack", 0)
            def_ = stats_rec.float_fields.get("defence", 0)
            str_ = stats_rec.float_fields.get("strength", 0)
            tough = stats_rec.float_fields.get("toughness2", 0)
            stats_text = f"ATK {atk:.0f}  DEF {def_:.0f}  STR {str_:.0f}  TGH {tough:.0f}"

        self._build_ui(name, stats_text, is_player)
        self._apply_style()

    def _build_ui(self, name: str, stats: str, is_player: bool):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)

        dot = QFrame()
        dot.setFixedSize(4, 32)
        color = ACCENT if is_player else BORDER
        dot.setStyleSheet(f"background: {color}; border-radius: 2px; border: none;")
        layout.addWidget(dot)

        col = QVBoxLayout()
        col.setSpacing(2)
        col.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(name)
        name_lbl.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {TEXT}; border: none; background: transparent;")
        col.addWidget(name_lbl)

        if stats:
            stats_lbl = QLabel(stats)
            stats_lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; font-family: 'Consolas', monospace; border: none; background: transparent;")
            col.addWidget(stats_lbl)

        layout.addLayout(col, 1)

    def set_selected(self, sel: bool):
        self._selected = sel
        self._apply_style()

    def _apply_style(self):
        if self._selected:
            self.setStyleSheet(f"QFrame {{ background-color: {SELECTION}; border: 1px solid {ACCENT_DIM}; border-radius: 8px; }}")
        else:
            self.setStyleSheet(f"QFrame {{ background: transparent; border: 1px solid transparent; border-radius: 8px; }} QFrame:hover {{ background: {BG_LIGHTER}; border: 1px solid {BORDER}; }}")

    def mousePressEvent(self, ev):
        self.clicked.emit(self._filename, self._record)
        super().mousePressEvent(ev)


class SectionHeader(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, title: str, count: int = 0, expanded: bool = True, parent=None):
        super().__init__(parent)
        self._expanded = expanded
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setFixedHeight(28)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 0, 6, 0)
        layout.setSpacing(6)

        self.arrow = QLabel("\u25bc" if expanded else "\u25b6")
        self.arrow.setStyleSheet(f"font-size: 8px; color: {TEXT_MUTED}; background: transparent;")
        self.arrow.setFixedWidth(12)
        layout.addWidget(self.arrow)

        self.title_lbl = QLabel(title.upper())
        self.title_lbl.setStyleSheet(f"font-size: 10px; font-weight: 700; color: {TEXT_MUTED}; letter-spacing: 1px; background: transparent;")
        layout.addWidget(self.title_lbl)

        if count:
            cnt = QLabel(str(count))
            cnt.setStyleSheet(f"font-size: 9px; color: {TEXT_MUTED}; background: {BG_LIGHTER}; border-radius: 7px; padding: 1px 6px; border: none;")
            layout.addWidget(cnt)

        layout.addStretch()

    def mousePressEvent(self, ev):
        self._expanded = not self._expanded
        self.arrow.setText("\u25bc" if self._expanded else "\u25b6")
        self.toggled.emit(self._expanded)
        super().mousePressEvent(ev)


class Sidebar(QWidget):
    character_selected = pyqtSignal(str, object)
    section_changed = pyqtSignal(str)
    money_modified = pyqtSignal(str)  # filename

    def __init__(self, resolver: GameDataResolver | None = None, parent=None):
        super().__init__(parent)
        self.resolver = resolver
        self.manager: SaveManager | None = None
        self._cards: list[CharacterCard] = []
        self._section_widgets: dict[str, list[QWidget]] = {}
        self._money_widget: MoneyWidget | None = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 10)
        layout.setSpacing(6)

        # Search
        self.search = QLineEdit()
        self.search.setPlaceholderText("\U0001f50d  Search characters...")
        self.search.setStyleSheet(SEARCH_INPUT_STYLE)
        self.search.textChanged.connect(self._rebuild)
        layout.addWidget(self.search)

        # Money widget
        self.money = MoneyWidget()
        self.money.money_changed.connect(self._on_money_changed)
        layout.addWidget(self.money)

        # Scrollable content
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 4, 0, 4)
        self.content_layout.setSpacing(2)
        self.content_layout.addStretch()
        self.scroll.setWidget(self.content)
        layout.addWidget(self.scroll, 1)

    def load_data(self, manager: SaveManager):
        self.manager = manager
        self._load_money()
        self._rebuild()

    def _load_money(self):
        if not self.manager:
            return
        qs = self.manager.files.get("quick.save")
        if not qs:
            return
        for rec in qs.records:
            if rec.typecode == 56:  # MAP_FEATURES
                self.money.load_money(rec)
                return

    def _on_money_changed(self, val):
        if self.manager:
            self.manager.mark_modified("quick.save")
            self.money_modified.emit("quick.save")

    def _rebuild(self, filter_text: str = ""):
        self._clear()
        if not self.manager:
            return

        filt = filter_text.lower()

        # Categorize platoons
        player_squads: dict[str, list] = {}   # player faction platoons
        npc_squads: dict[str, list] = {}      # everything else

        for fname, sf in sorted(self.manager.files.items()):
            if not fname.endswith(".platoon"):
                continue
            chars_data = []
            for i, rec in enumerate(sf.records):
                if rec.typecode != 36 or "name" not in rec.string_fields:
                    continue
                name = rec.string_fields.get("name", "")
                if filt and filt not in name.lower():
                    continue
                # Find stats
                stats = None
                for r2 in sf.records[i+1:]:
                    if r2.typecode == 36:
                        break
                    if r2.typecode == 25:
                        stats = r2
                        break
                chars_data.append((fname, rec, stats))

            if not chars_data:
                continue

            platoon_name = fname.replace("platoon/", "").replace(".platoon", "")
            faction = chars_data[0][1].string_fields.get("owner faction ID", "")

            if PLAYER_FACTION in faction:
                player_squads[platoon_name] = chars_data
            else:
                npc_squads[platoon_name] = chars_data

        # Also check for player-named platoons in quick.save (they appear as PLATOON records)
        player_platoon_names = set()
        qs = self.manager.files.get("quick.save")
        if qs:
            for rec in qs.records:
                if rec.typecode == 34:  # PLATOON
                    # Check if it's faction 204
                    fid = rec.string_fields.get("owner faction ID", "")
                    if PLAYER_FACTION in fid or rec.name in [k for k in player_squads]:
                        player_platoon_names.add(rec.name)

        # ---- BUILD UI ----

        # 1. My Characters (player faction)
        total_player = sum(len(v) for v in player_squads.values())
        if total_player:
            self._add_section("My Squad", total_player, True, player_squads, is_player=True)

        # 2. NPCs
        total_npc = sum(len(v) for v in npc_squads.values())
        if total_npc:
            self._add_section("NPCs & World", total_npc, False, npc_squads, is_player=False)

        # 3. Factions (from quick.save)
        if not filt or filt in "factions":
            factions = [(f, r) for f, r in self.manager.get_factions()
                        if not filt or filt in r.name.lower()]
            if factions:
                header = SectionHeader("Factions", len(factions), expanded=False)
                self.content_layout.insertWidget(self.content_layout.count()-1, header)
                container = QWidget()
                container_layout = QVBoxLayout(container)
                container_layout.setContentsMargins(0, 0, 0, 0)
                container_layout.setSpacing(2)
                container.setVisible(False)
                header.toggled.connect(container.setVisible)

                for fname, rec in sorted(factions, key=lambda x: x[1].name):
                    card = CharacterCard(fname, rec, None)
                    card.clicked.connect(self._on_card_clicked)
                    self._cards.append(card)
                    container_layout.addWidget(card)

                self.content_layout.insertWidget(self.content_layout.count()-1, container)

        self.content_layout.addStretch()

    def _add_section(self, title: str, count: int, expanded: bool,
                     squads: dict[str, list], is_player: bool):
        header = SectionHeader(title, count, expanded=expanded)
        self.content_layout.insertWidget(self.content_layout.count()-1, header)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)
        container.setVisible(expanded)
        header.toggled.connect(container.setVisible)

        for squad_name, chars in sorted(squads.items()):
            # Sub-header per squad
            squad_lbl = QLabel(f"  {squad_name}")
            squad_lbl.setStyleSheet(f"font-size: 10px; color: {TEXT_MUTED}; font-weight: 600; padding: 6px 0 2px 2px; background: transparent;")
            container_layout.addWidget(squad_lbl)

            for fname, rec, stats in chars:
                card = CharacterCard(fname, rec, stats, is_player=is_player)
                card.clicked.connect(self._on_card_clicked)
                self._cards.append(card)
                container_layout.addWidget(card)

        self.content_layout.insertWidget(self.content_layout.count()-1, container)

    def _on_card_clicked(self, filename: str, record: Record):
        for c in self._cards:
            c.set_selected(c._record is record)
        self.character_selected.emit(filename, record)

    def _clear(self):
        self._cards.clear()
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()
