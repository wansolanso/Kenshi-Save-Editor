"""Internationalization module. English default, with pt-BR and es-ES."""
from __future__ import annotations
import locale

_current_lang = "en"
_strings: dict[str, dict[str, str]] = {}

TRANSLATIONS = {
    # ── Window / App ──
    "app.title": {
        "en": "Kenshi Save Editor",
        "pt": "Kenshi Save Editor",
        "es": "Kenshi Save Editor",
    },
    "app.subtitle": {
        "en": "SAVE EDITOR",
        "pt": "EDITOR DE SAVES",
        "es": "EDITOR DE GUARDADOS",
    },

    # ── Menu ──
    "menu.file": {
        "en": "  &File  ",
        "pt": "  &Arquivo  ",
        "es": "  &Archivo  ",
    },
    "menu.open": {
        "en": "  Open Save...    Ctrl+O",
        "pt": "  Abrir Save...    Ctrl+O",
        "es": "  Abrir Guardado...    Ctrl+O",
    },
    "menu.save": {
        "en": "  Save    Ctrl+S",
        "pt": "  Salvar    Ctrl+S",
        "es": "  Guardar    Ctrl+S",
    },
    "menu.save_as": {
        "en": "  Save As...",
        "pt": "  Salvar Como...",
        "es": "  Guardar Como...",
    },
    "menu.backup": {
        "en": "  Create Backup",
        "pt": "  Criar Backup",
        "es": "  Crear Backup",
    },
    "menu.quit": {
        "en": "  Quit",
        "pt": "  Sair",
        "es": "  Salir",
    },

    # ── Welcome ──
    "welcome.hint": {
        "en": "Open a save folder or select a record from the sidebar",
        "pt": "Abra uma pasta de save ou selecione um registro na sidebar",
        "es": "Abre una carpeta de guardado o selecciona un registro en la barra lateral",
    },
    "welcome.shortcut": {
        "en": "Ctrl+O to open",
        "pt": "Ctrl+O para abrir",
        "es": "Ctrl+O para abrir",
    },

    # ── Status bar ──
    "status.no_save": {
        "en": "Ctrl+O to open a save folder",
        "pt": "Ctrl+O para abrir uma pasta de save",
        "es": "Ctrl+O para abrir una carpeta de guardado",
    },
    "status.loaded": {
        "en": "Loaded: {name}  |  {files} files  |  {records} records",
        "pt": "Carregado: {name}  |  {files} arquivos  |  {records} registros",
        "es": "Cargado: {name}  |  {files} archivos  |  {records} registros",
    },
    "status.modified": {
        "en": "{n} file(s) modified  |  Ctrl+S to save",
        "pt": "{n} arquivo(s) modificado(s)  |  Ctrl+S para salvar",
        "es": "{n} archivo(s) modificado(s)  |  Ctrl+S para guardar",
    },
    "status.no_changes": {
        "en": "No pending changes.",
        "pt": "Nenhuma alteracao pendente.",
        "es": "Sin cambios pendientes.",
    },
    "status.saved": {
        "en": "Saved successfully!",
        "pt": "Salvo com sucesso!",
        "es": "Guardado con exito!",
    },
    "status.saved_to": {
        "en": "Saved to: {path}",
        "pt": "Salvo em: {path}",
        "es": "Guardado en: {path}",
    },
    "status.game_data": {
        "en": "Game data loaded: {n} items  |  Ctrl+O to open save",
        "pt": "Dados do jogo carregados: {n} itens  |  Ctrl+O para abrir save",
        "es": "Datos del juego cargados: {n} items  |  Ctrl+O para abrir guardado",
    },
    "status.downloading": {
        "en": "Downloading v{v}... {pct}%",
        "pt": "Baixando v{v}... {pct}%",
        "es": "Descargando v{v}... {pct}%",
    },

    # ── Dialogs ──
    "dialog.save_confirm": {
        "en": "Save {n} modified file(s)?\nCreate a backup first if needed.",
        "pt": "Salvar {n} arquivo(s) modificado(s)?\nCrie um backup antes se necessario.",
        "es": "Guardar {n} archivo(s) modificado(s)?\nCrea un backup antes si es necesario.",
    },
    "dialog.backup_ok": {
        "en": "Backup created:\n{path}",
        "pt": "Backup criado:\n{path}",
        "es": "Backup creado:\n{path}",
    },
    "dialog.error": {
        "en": "Error",
        "pt": "Erro",
        "es": "Error",
    },
    "dialog.save": {
        "en": "Save",
        "pt": "Salvar",
        "es": "Guardar",
    },
    "dialog.backup": {
        "en": "Backup",
        "pt": "Backup",
        "es": "Backup",
    },
    "dialog.select_folder": {
        "en": "Select save folder",
        "pt": "Selecione a pasta do save",
        "es": "Selecciona la carpeta del guardado",
    },
    "dialog.save_to": {
        "en": "Save to...",
        "pt": "Salvar em...",
        "es": "Guardar en...",
    },
    "dialog.load_failed": {
        "en": "Failed to load save:\n{e}",
        "pt": "Falha ao carregar save:\n{e}",
        "es": "Error al cargar guardado:\n{e}",
    },
    "dialog.save_failed": {
        "en": "Failed to save:\n{e}",
        "pt": "Falha ao salvar:\n{e}",
        "es": "Error al guardar:\n{e}",
    },

    # ── Update ──
    "update.title": {
        "en": "Update Available",
        "pt": "Atualizacao Disponivel",
        "es": "Actualizacion Disponible",
    },
    "update.message": {
        "en": "A new version is available: v{version}\n(current: v{current})\n\nDownload size: {size:.1f} MB\n",
        "pt": "Nova versao disponivel: v{version}\n(atual: v{current})\n\nTamanho: {size:.1f} MB\n",
        "es": "Nueva version disponible: v{version}\n(actual: v{current})\n\nTamano: {size:.1f} MB\n",
    },
    "update.confirm": {
        "en": "\nUpdate now?",
        "pt": "\nAtualizar agora?",
        "es": "\nActualizar ahora?",
    },
    "update.restart": {
        "en": "The app will restart.",
        "pt": "O app vai reiniciar.",
        "es": "La app se reiniciara.",
    },
    "update.failed": {
        "en": "Update Failed",
        "pt": "Falha na Atualizacao",
        "es": "Error en la Actualizacion",
    },
    "update.source_hint": {
        "en": "Running from source. Pull the latest:\ngit pull && git checkout v{v}",
        "pt": "Rodando do fonte. Atualize:\ngit pull && git checkout v{v}",
        "es": "Ejecutando desde fuente. Actualiza:\ngit pull && git checkout v{v}",
    },

    # ── Tabs ──
    "tab.stats": {
        "en": "  Stats & Health  ",
        "pt": "  Stats & Saude  ",
        "es": "  Stats & Salud  ",
    },
    "tab.inventory": {
        "en": "  Inventory  ",
        "pt": "  Inventario  ",
        "es": "  Inventario  ",
    },
    "tab.raw": {
        "en": "  Raw Fields  ",
        "pt": "  Campos Brutos  ",
        "es": "  Campos Crudos  ",
    },

    # ── Sidebar ──
    "sidebar.search": {
        "en": "\U0001f50d  Search characters...",
        "pt": "\U0001f50d  Buscar personagens...",
        "es": "\U0001f50d  Buscar personajes...",
    },
    "sidebar.my_squad": {
        "en": "My Squad",
        "pt": "Meu Esquadrao",
        "es": "Mi Escuadron",
    },
    "sidebar.npcs": {
        "en": "NPCs",
        "pt": "NPCs",
        "es": "NPCs",
    },
    "sidebar.factions": {
        "en": "Factions",
        "pt": "Faccoes",
        "es": "Facciones",
    },
    "sidebar.records": {
        "en": "Records",
        "pt": "Registros",
        "es": "Registros",
    },

    # ── Character Editor ──
    "char.name": {
        "en": "Name",
        "pt": "Nome",
        "es": "Nombre",
    },
    "char.age": {
        "en": "Age",
        "pt": "Idade",
        "es": "Edad",
    },
    "char.no_stats": {
        "en": "This character has no stats record (may be an animal or robot)",
        "pt": "Este personagem nao tem registro de stats (pode ser animal ou robo)",
        "es": "Este personaje no tiene registro de stats (puede ser animal o robot)",
    },
    "char.blood": {
        "en": "Blood",
        "pt": "Sangue",
        "es": "Sangre",
    },
    "char.hunger": {
        "en": "Hunger",
        "pt": "Fome",
        "es": "Hambre",
    },

    # ── Section Headers ──
    "section.info": {
        "en": "Info",
        "pt": "Info",
        "es": "Info",
    },
    "section.stats": {
        "en": "Stats & Skills",
        "pt": "Stats & Habilidades",
        "es": "Stats & Habilidades",
    },
    "section.health": {
        "en": "Health",
        "pt": "Saude",
        "es": "Salud",
    },
    "section.limbs": {
        "en": "Limbs",
        "pt": "Membros",
        "es": "Extremidades",
    },

    # ── Faction Editor ──
    "faction.title": {
        "en": "Faction Relations",
        "pt": "Relacoes de Faccao",
        "es": "Relaciones de Faccion",
    },
    "faction.relations_of": {
        "en": "Relations: {name}",
        "pt": "Relacoes: {name}",
        "es": "Relaciones: {name}",
    },
    "faction.col_faction": {
        "en": "Faction",
        "pt": "Faccao",
        "es": "Faccion",
    },
    "faction.col_relation": {
        "en": "Relation",
        "pt": "Relacao",
        "es": "Relacion",
    },
    "faction.col_trust": {
        "en": "Trust",
        "pt": "Confianca",
        "es": "Confianza",
    },
    "faction.col_trust_neg": {
        "en": "Trust Negative",
        "pt": "Confianca Negativa",
        "es": "Confianza Negativa",
    },

    # ── Inventory ──
    "inv.title": {
        "en": "Inventory",
        "pt": "Inventario",
        "es": "Inventario",
    },

    # ── Record Tree ──
    "tree.col_name": {
        "en": "Name",
        "pt": "Nome",
        "es": "Nombre",
    },
    "tree.col_type": {
        "en": "Type",
        "pt": "Tipo",
        "es": "Tipo",
    },
}


def set_language(lang: str):
    global _current_lang
    _current_lang = lang


def get_language() -> str:
    return _current_lang


def detect_language() -> str:
    """Detect language from system locale."""
    try:
        loc = locale.getdefaultlocale()[0] or ""
    except Exception:
        loc = ""
    loc = loc.lower()
    if loc.startswith("pt"):
        return "pt"
    if loc.startswith("es"):
        return "es"
    return "en"


def t(key: str, **kwargs) -> str:
    """Translate a key. Falls back to English, then to the key itself."""
    entry = TRANSLATIONS.get(key)
    if not entry:
        return key
    text = entry.get(_current_lang, entry.get("en", key))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
