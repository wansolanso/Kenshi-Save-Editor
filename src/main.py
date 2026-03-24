from __future__ import annotations
import sys
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QFileDialog, QMessageBox, QStatusBar, QTabWidget,
    QLabel, QFrame, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QPalette, QColor

from .save_manager import SaveManager
from .models import Record
from .constants import TYPECODE_NAMES
from .game_data import GameDataResolver
from .style import STYLESHEET, BG, BG_LIGHT, BORDER, ACCENT, TEXT_DIM, TEXT_MUTED, TITLE, MAIN, load_fonts
from .widgets.sidebar import Sidebar
from .widgets.record_editor import RecordEditor
from .widgets.character_editor import CharacterEditor
from .widgets.inventory_editor import InventoryEditor
from .widgets.faction_editor import FactionEditor


class WelcomePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("\u2694")
        icon.setStyleSheet(f"font-size: 48px; color: {TEXT_MUTED}; background: transparent;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Kenshi Save Editor")
        title.setStyleSheet(f"font-size: 22px; font-weight: 700; color: {TEXT_DIM}; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        hint = QLabel("Open a save folder or select a record from the sidebar")
        hint.setStyleSheet(f"font-size: 13px; color: {TEXT_MUTED}; background: transparent;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        shortcut = QLabel("Ctrl+O to open")
        shortcut.setStyleSheet(f"""
            font-size: 11px; color: {ACCENT}; background: transparent;
            padding: 6px 16px;
            border: 1px solid {ACCENT};
            border-radius: 6px;
        """)
        shortcut.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(icon)
        layout.addSpacing(8)
        layout.addWidget(title)
        layout.addSpacing(4)
        layout.addWidget(hint)
        layout.addSpacing(16)
        layout.addWidget(shortcut)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = SaveManager()
        self.resolver = GameDataResolver()
        self.setWindowTitle("Kenshi Save Editor")
        self.resize(1500, 900)
        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()
        self._load_game_data()

    def _setup_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu("  &File  ")

        open_action = QAction("  Open Save...    Ctrl+O", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_save)
        file_menu.addAction(open_action)
        file_menu.addSeparator()

        save_action = QAction("  Save    Ctrl+S", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save)
        file_menu.addAction(save_action)

        save_as_action = QAction("  Save As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self._save_as)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()

        backup_action = QAction("  Create Backup", self)
        backup_action.triggered.connect(self._create_backup)
        file_menu.addAction(backup_action)
        file_menu.addSeparator()

        quit_action = QAction("  Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---- LEFT: Sidebar ----
        sidebar_container = QWidget()
        sidebar_container.setStyleSheet(f"background-color: {BG_LIGHT};")
        sidebar_outer = QVBoxLayout(sidebar_container)
        sidebar_outer.setContentsMargins(0, 0, 0, 0)
        sidebar_outer.setSpacing(0)

        # App title
        title_bar = QFrame()
        title_bar.setFixedHeight(56)
        title_bar.setStyleSheet(f"""
            QFrame {{
                background-color: {BG_LIGHT};
                border-bottom: 2px solid {TITLE};
            }}
        """)
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 16, 0)
        title_col = QVBoxLayout()
        title_col.setSpacing(0)
        app_title = QLabel("KENSHI")
        app_title.setStyleSheet(f"font-size: 22px; font-weight: 800; color: {MAIN}; letter-spacing: 5px; font-family: 'Exo 2';")
        app_sub = QLabel("SAVE EDITOR")
        app_sub.setStyleSheet(f"font-size: 9px; font-weight: 600; color: {TEXT_MUTED}; letter-spacing: 3px; font-family: 'Exo 2';")
        title_col.addWidget(app_title)
        title_col.addWidget(app_sub)
        title_layout.addLayout(title_col)
        title_layout.addStretch()
        sidebar_outer.addWidget(title_bar)

        self.sidebar = Sidebar(resolver=self.resolver)
        self.sidebar.character_selected.connect(self._on_record_selected)
        self.sidebar.money_modified.connect(self._on_modified)
        sidebar_outer.addWidget(self.sidebar)
        splitter.addWidget(sidebar_container)

        # ---- RIGHT: Content area ----
        self.content_stack = QStackedWidget()

        # Page 0: Welcome
        self.welcome_panel = WelcomePanel()
        self.content_stack.addWidget(self.welcome_panel)

        # Page 1: Character view (tabs: Character, Inventory, Raw Fields)
        self.char_page = QWidget()
        char_layout = QVBoxLayout(self.char_page)
        char_layout.setContentsMargins(0, 0, 0, 0)
        self.char_tabs = QTabWidget()

        self.character_editor = CharacterEditor(resolver=self.resolver)
        self.character_editor.record_modified.connect(self._on_modified)
        self.char_tabs.addTab(self.character_editor, "  Stats & Health  ")

        self.inventory_editor = InventoryEditor(resolver=self.resolver)
        self.inventory_editor.record_modified.connect(self._on_modified)
        self.char_tabs.addTab(self.inventory_editor, "  Inventory  ")

        self.char_fields_editor = RecordEditor()
        self.char_fields_editor.record_modified.connect(self._on_modified)
        self.char_tabs.addTab(self.char_fields_editor, "  Raw Fields  ")

        char_layout.addWidget(self.char_tabs)
        self.content_stack.addWidget(self.char_page)

        # Page 2: Faction view
        self.faction_page = QWidget()
        faction_layout = QVBoxLayout(self.faction_page)
        faction_layout.setContentsMargins(0, 0, 0, 0)
        self.faction_editor = FactionEditor(resolver=self.resolver)
        self.faction_editor.record_modified.connect(self._on_modified)
        faction_layout.addWidget(self.faction_editor)
        self.content_stack.addWidget(self.faction_page)

        # Page 3: Generic record view
        self.generic_page = QWidget()
        generic_layout = QVBoxLayout(self.generic_page)
        generic_layout.setContentsMargins(0, 0, 0, 0)
        self.record_editor = RecordEditor()
        self.record_editor.record_modified.connect(self._on_modified)
        generic_layout.addWidget(self.record_editor)
        self.content_stack.addWidget(self.generic_page)

        splitter.addWidget(self.content_stack)
        splitter.setSizes([340, 1160])
        splitter.setHandleWidth(1)
        layout.addWidget(splitter)

    def _setup_statusbar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ctrl+O to open a save folder")

    def _load_game_data(self):
        ok = self.resolver.load()
        if ok:
            self.statusbar.showMessage(
                f"Game data loaded: {self.resolver.total_names} items  |  Ctrl+O to open save"
            )

    def _open_save(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select save folder",
            str(Path.home() / "AppData" / "Local" / "kenshi" / "save")
        )
        if not directory:
            return
        self._load_directory(directory)

    def _load_directory(self, directory: str):
        try:
            self.manager.load_save(directory)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load save:\n{e}")
            return

        self.sidebar.load_data(self.manager)

        total = sum(len(sf.records) for sf in self.manager.files.values())
        files = len(self.manager.files)
        self.statusbar.showMessage(
            f"Loaded: {Path(directory).name}  |  {files} files  |  {total} records"
        )
        self.setWindowTitle(f"Kenshi Save Editor  -  {Path(directory).name}")

    def _on_record_selected(self, filename: str, record: Record):
        if record.typecode == 36 and "name" in record.string_fields:
            # CHARACTER → show character page
            assoc = self._find_associated_records(filename, record)
            self.character_editor.load_character(
                filename, record,
                assoc.get("stats"), assoc.get("medical")
            )
            inv_items = assoc.get("inventory", [])
            self.inventory_editor.load_items(filename, inv_items)
            self.char_fields_editor.load_record(filename, record)
            self.content_stack.setCurrentWidget(self.char_page)

        elif record.typecode == 37:
            # FACTION
            self.faction_editor.load_faction_data(filename, record)
            self.content_stack.setCurrentWidget(self.faction_page)

        else:
            # Everything else → generic editor
            self.record_editor.load_record(filename, record)

            # Also try faction view if it has relation data
            has_relations = any(
                k.startswith("relation") or k.startswith("trust")
                for k in record.long_fields
            )
            if has_relations:
                self.faction_editor.load_faction_data(filename, record)

            self.content_stack.setCurrentWidget(self.generic_page)

    def _find_associated_records(self, filename: str, character: Record) -> dict:
        sf = self.manager.files.get(filename)
        if not sf:
            return {}

        char_idx = None
        for i, rec in enumerate(sf.records):
            if rec is character:
                char_idx = i
                break
        if char_idx is None:
            return {}

        result: dict = {"inventory": []}
        for rec in sf.records[char_idx + 1:]:
            if rec.typecode == 36:
                break
            elif rec.typecode == 25:
                result["stats"] = rec
            elif rec.typecode == 57:
                result["medical"] = rec
            elif rec.typecode == 42:
                result["inventory"].append(rec)
            elif rec.typecode == 41:
                result["appearance"] = rec
            elif rec.typecode == 67:
                result["ai"] = rec
            elif rec.typecode == 66:
                result["detail"] = rec
        return result

    def _on_modified(self, filename: str):
        self.manager.mark_modified(filename)
        n = len(self.manager.modified)
        self.statusbar.showMessage(f"{n} file(s) modified  |  Ctrl+S to save")

    def _save(self):
        if not self.manager.is_loaded:
            return
        if not self.manager.modified:
            self.statusbar.showMessage("No pending changes.")
            return
        reply = QMessageBox.question(
            self, "Save",
            f"Save {len(self.manager.modified)} modified file(s)?\nCreate a backup first if needed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        try:
            self.manager.save_all()
            self.statusbar.showMessage("Saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

    def _save_as(self):
        if not self.manager.is_loaded:
            return
        directory = QFileDialog.getExistingDirectory(self, "Save to...")
        if not directory:
            return
        for f in self.manager.files:
            self.manager.mark_modified(f)
        old_dir = self.manager.save_dir
        self.manager.save_dir = Path(directory)
        try:
            self.manager.save_all()
            self.statusbar.showMessage(f"Saved to: {directory}")
        except Exception as e:
            self.manager.save_dir = old_dir
            QMessageBox.critical(self, "Error", f"Failed to save:\n{e}")

    def _create_backup(self):
        if not self.manager.is_loaded:
            return
        try:
            backup_path = self.manager.create_backup()
            QMessageBox.information(self, "Backup", f"Backup created:\n{backup_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed:\n{e}")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Load Kenshi's actual fonts
    load_fonts(app)

    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(MAIN))
    palette.setColor(QPalette.ColorRole.Base, QColor(BG_LIGHT))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#1c0f0b"))
    palette.setColor(QPalette.ColorRole.Text, QColor(MAIN))
    palette.setColor(QPalette.ColorRole.Button, QColor("#221410"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(MAIN))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(TITLE))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(MAIN))
    app.setPalette(palette)
    app.setStyleSheet(STYLESHEET)

    window = MainWindow()
    if len(sys.argv) > 1:
        window._load_directory(sys.argv[1])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
