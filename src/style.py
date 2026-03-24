"""Kenshi Save Editor — authentic Kenshi UI theme.

Colors and fonts extracted directly from the game's
data/gui/colours/kenshi_colours.xml and data/gui/fonts/.
"""
import os
from pathlib import Path

# ── Load Kenshi fonts ────────────────────────────────────
def _get_font_dir() -> Path:
    """Resolve font directory for both dev and PyInstaller bundle."""
    import sys
    if getattr(sys, '_MEIPASS', None):
        return Path(sys._MEIPASS) / "src"
    return Path(__file__).parent

FONT_DIR = _get_font_dir()

def load_fonts(app):
    """Register Kenshi's actual fonts with Qt."""
    from PyQt6.QtGui import QFontDatabase
    for fname in ["Exo2-SemiBold.ttf", "Exo2-Bold.ttf", "Exo2-Medium.ttf", "Sentencia_1.ttf"]:
        fpath = FONT_DIR / fname
        if fpath.exists():
            QFontDatabase.addApplicationFont(str(fpath))

# ── Kenshi Palette (from kenshi_colours.xml) ─────────────
MAIN        = "#afa68b"   # primary text — warm tan
SECONDARY   = "#140806"   # deepest background — near-black brown
TITLE       = "#492620"   # section headings — dark rust
BAD         = "#59231a"   # negative values (dark)
BAD_BRIGHT  = "#bf4834"   # negative values (bright)
GOOD        = "#a8b774"   # positive values — olive green
GOOD_BRIGHT = "#a8b774"
GREYED      = "#444444"
GREYED_BR   = "#777777"
SPECIAL     = "#14ffdc"   # special/artifact items — cyan

# Item grades
GRADE_STD   = "#e0cccc"
GRADE_ART   = "#0dfceb"   # artifact
GRADE_4     = "#fceb0d"   # masterwork — yellow

# Map/faction markers
MARKER_ALLY   = "#5cb473"
MARKER_ENEMY  = "#e65139"
MARKER_PLAYER = "#8dcdff"

# ── Derived UI colors ────────────────────────────────────
BG           = "#0d0604"   # slightly darker than SECONDARY
BG_LIGHT     = "#140806"   # SECONDARY — main panel bg
BG_LIGHTER   = "#1c0f0b"   # subtle row alternation
BG_CARD      = "#1a0d09"   # card/group bg
SURFACE      = "#221410"   # elevated surface
BORDER       = "#2e1c16"   # warm brown border
BORDER_LIGHT = "#3a2820"

ACCENT       = MAIN       # #afa68b — khaki tan as accent
ACCENT_HOVER = "#c4b99a"
ACCENT_DIM   = "#7a7460"
ACCENT_GLOW  = "rgba(175,166,139,0.10)"

TEXT         = MAIN        # #afa68b
TEXT_DIM     = "#7a7460"
TEXT_MUTED   = "#4a4538"

INPUT_BG     = "#110805"
SELECTION    = "rgba(175,166,139,0.12)"

SUCCESS      = GOOD       # #a8b774
WARNING      = "#d4a24e"
DANGER       = BAD_BRIGHT # #bf4834

READONLY_CELL_BG = BG_LIGHTER

# ── Stylesheet ───────────────────────────────────────────
STYLESHEET = f"""

/* ===== GLOBAL ===== */
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-family: 'Exo 2', 'Segoe UI', sans-serif;
    font-size: 13px;
    selection-background-color: {ACCENT_DIM};
    selection-color: white;
}}

/* ===== MENU ===== */
QMenuBar {{
    background: {BG_LIGHT};
    border-bottom: 1px solid {BORDER};
    padding: 1px 0;
    font-family: 'Exo 2';
}}
QMenuBar::item {{
    background: transparent;
    padding: 7px 16px;
    border-radius: 2px;
    margin: 2px;
    color: {TEXT_DIM};
}}
QMenuBar::item:selected {{
    background: {SURFACE};
    color: {TEXT};
}}
QMenu {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    padding: 4px;
}}
QMenu::item {{
    padding: 8px 28px 8px 14px;
    border-radius: 2px;
    margin: 1px 3px;
}}
QMenu::item:selected {{
    background: {SURFACE};
    color: {ACCENT_HOVER};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 4px 10px;
}}

/* ===== STATUS BAR ===== */
QStatusBar {{
    background: {BG_LIGHT};
    border-top: 1px solid {BORDER};
    color: {TEXT_MUTED};
    font-size: 11px;
    padding: 3px 12px;
}}

/* ===== SCROLLBAR ===== */
QScrollBar:vertical {{
    background: {BG_LIGHT};
    width: 8px;
    border: none;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_LIGHT};
    border-radius: 4px;
    min-height: 24px;
    margin: 1px;
}}
QScrollBar::handle:vertical:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    height: 0; background: transparent;
}}
QScrollBar:horizontal {{
    background: {BG_LIGHT};
    height: 8px;
    border: none;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER_LIGHT};
    border-radius: 4px;
    min-width: 24px;
    margin: 1px;
}}
QScrollBar::handle:horizontal:hover {{ background: {TEXT_MUTED}; }}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
    width: 0; background: transparent;
}}

QScrollArea {{ border: none; background: transparent; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}

/* ===== SPLITTER ===== */
QSplitter::handle {{ background: {BORDER}; width: 1px; }}

/* ===== GROUP BOX ===== */
QGroupBox {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 2px;
    margin-top: 20px;
    padding: 22px 14px 12px 14px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 0px; top: 4px;
    padding: 3px 12px;
    background: {TITLE};
    color: {MAIN};
    border-radius: 0px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    font-family: 'Exo 2';
}}

/* ===== INPUT ===== */
QLineEdit {{
    background: {INPUT_BG};
    border: 1px solid {BORDER};
    border-radius: 2px;
    padding: 7px 11px;
    color: {TEXT};
    font-family: 'Exo 2';
}}
QLineEdit:focus {{ border-color: {ACCENT_DIM}; }}

/* ===== SPIN BOX ===== */
QSpinBox, QDoubleSpinBox {{
    background: {INPUT_BG};
    border: 1px solid {BORDER};
    border-radius: 2px;
    padding: 5px 8px;
    color: {TEXT};
    min-width: 70px;
    font-family: 'Exo 2';
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {ACCENT_DIM}; }}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid {BORDER};
    background: {BG_LIGHTER};
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid {BORDER};
    background: {BG_LIGHTER};
}}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {{
    width: 0; height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-bottom: 4px solid {TEXT_MUTED};
}}
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {{
    width: 0; height: 0;
    border-left: 3px solid transparent;
    border-right: 3px solid transparent;
    border-top: 4px solid {TEXT_MUTED};
}}

/* ===== COMBO BOX ===== */
QComboBox {{
    background: {INPUT_BG};
    border: 1px solid {BORDER};
    border-radius: 2px;
    padding: 5px 10px;
    color: {TEXT};
    min-width: 90px;
}}
QComboBox:hover {{ border-color: {ACCENT_DIM}; }}
QComboBox::drop-down {{
    subcontrol-position: top right;
    width: 22px;
    border-left: 1px solid {BORDER};
    background: {BG_LIGHTER};
}}
QComboBox::down-arrow {{
    width: 0; height: 0;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {TEXT_MUTED};
}}
QComboBox QAbstractItemView {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    padding: 2px;
    selection-background-color: {SURFACE};
    outline: none;
}}

/* ===== TAB WIDGET ===== */
QTabWidget::pane {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-top: 2px solid {TITLE};
    border-radius: 0px;
    top: -1px;
}}
QTabBar::tab {{
    background: {BG_LIGHT};
    border: 1px solid {BORDER};
    border-bottom: none;
    border-radius: 0px;
    padding: 8px 22px;
    margin-right: 1px;
    color: {TEXT_MUTED};
    font-weight: 600;
    font-size: 11px;
    letter-spacing: 0.5px;
    font-family: 'Exo 2';
}}
QTabBar::tab:selected {{
    background: {TITLE};
    color: {MAIN};
    font-weight: 700;
}}
QTabBar::tab:hover:!selected {{
    background: {SURFACE};
    color: {TEXT_DIM};
}}
QTabBar::tab:disabled {{
    color: {TEXT_MUTED};
    background: {BG};
}}

/* ===== TABLE ===== */
QTableWidget, QTableView {{
    background: {BG_LIGHT};
    alternate-background-color: {BG_LIGHTER};
    border: 1px solid {BORDER};
    border-radius: 0px;
    gridline-color: {BORDER};
    selection-background-color: {SELECTION};
    selection-color: {TEXT};
    outline: none;
    font-family: 'Exo 2';
}}
QTableWidget::item {{
    padding: 3px 8px;
}}
QTableWidget::item:selected {{
    background: {SELECTION};
}}
QHeaderView {{ background: transparent; }}
QHeaderView::section {{
    background: {TITLE};
    color: {MAIN};
    border: none;
    border-right: 1px solid {BORDER};
    border-bottom: 1px solid {BORDER};
    padding: 7px 10px;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 0.5px;
    font-family: 'Exo 2';
}}
QHeaderView::section:last {{ border-right: none; }}

/* ===== TREE ===== */
QTreeWidget {{
    background: {BG_LIGHT};
    alternate-background-color: {BG_LIGHTER};
    border: 1px solid {BORDER};
    border-radius: 0px;
    outline: none;
    font-family: 'Exo 2';
}}
QTreeWidget::item {{
    padding: 4px;
    margin: 1px 2px;
}}
QTreeWidget::item:selected {{ background: {SELECTION}; }}
QTreeWidget::item:hover:!selected {{ background: {BG_LIGHTER}; }}
QTreeWidget::branch {{ background: transparent; }}
QTreeWidget QHeaderView::section {{
    background: {TITLE};
    color: {MAIN};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 6px 8px;
    font-weight: 700;
    font-size: 10px;
}}

/* ===== LABEL ===== */
QLabel {{ background: transparent; }}

/* ===== BUTTON ===== */
QPushButton {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 2px;
    padding: 7px 18px;
    color: {TEXT};
    font-weight: 600;
    min-width: 70px;
    font-family: 'Exo 2';
}}
QPushButton:hover {{
    background: {TITLE};
    color: {ACCENT_HOVER};
}}
QPushButton:pressed {{ background: {ACCENT_DIM}; }}

/* ===== PROGRESS BAR ===== */
QProgressBar {{
    background: {BG_LIGHTER};
    border: none;
    border-radius: 1px;
    height: 4px;
    text-align: center;
}}
QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {TITLE}, stop:1 {ACCENT_DIM});
    border-radius: 1px;
}}

/* ===== TOOLTIP ===== */
QToolTip {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    color: {TEXT};
    padding: 5px 9px;
    font-size: 12px;
}}
QMessageBox {{ background: {BG_CARD}; }}
QMessageBox QPushButton {{ min-width: 80px; }}
"""

# ── Widget-specific styles ───────────────────────────────

SEARCH_INPUT_STYLE = f"""
    QLineEdit {{
        background: {INPUT_BG};
        border: 1px solid {BORDER};
        border-radius: 2px;
        padding: 9px 12px;
        font-size: 13px;
        color: {TEXT};
        font-family: 'Exo 2';
    }}
    QLineEdit:focus {{ border-color: {ACCENT_DIM}; }}
"""

COUNT_LABEL_STYLE = f"color: {TEXT_MUTED}; font-size: 11px; padding: 2px 6px;"
SECTION_TITLE_STYLE = f"font-size: 15px; font-weight: 700; color: {TEXT}; padding: 6px 0;"
SUBTITLE_STYLE = f"font-size: 12px; color: {TEXT_DIM}; padding: 0 4px 6px 4px;"
ACCENT_LABEL_STYLE = f"color: {ACCENT}; font-weight: 600;"
