"""Resolves item SIDs to human-readable names by loading Kenshi game data files."""
from __future__ import annotations
import os
from pathlib import Path

from .binary_parser import BinaryReader


def find_kenshi_data() -> Path | None:
    """Auto-detect Kenshi data folder via Steam library folders."""
    # Check Steam libraryfolders.vdf for library paths
    steam_default = Path(r"C:\Program Files (x86)\Steam")
    vdf = steam_default / "steamapps" / "libraryfolders.vdf"
    library_paths = [steam_default]

    if vdf.exists():
        try:
            text = vdf.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                if '"path"' in line:
                    parts = line.strip().split('"')
                    if len(parts) >= 4:
                        library_paths.append(Path(parts[3].replace("\\\\", "\\")))
        except Exception:
            pass

    for lib in library_paths:
        candidate = lib / "steamapps" / "common" / "Kenshi" / "data"
        if candidate.exists() and (candidate / "gamedata.base").exists():
            return candidate

    return None


def _parse_mod_file_names(path: Path) -> dict[str, str]:
    """Parse a type 16 (mod/base) file and extract id→name mapping.
    Returns dict mapping 'ID-filename' → record name.
    """
    data = path.read_bytes()
    reader = BinaryReader(data)

    filetype = reader.read_int()
    filename = path.name

    if filetype != 15:
        # Type 17+ has merge data: extra int at start giving header end offset
        header_end = 0
        if filetype >= 17:
            merge_size = reader.read_int()
            header_end = merge_size + reader.pos

        _version = reader.read_int()
        _author = reader.read_string()
        _desc = reader.read_string()
        _deps = reader.read_string()  # comma-separated
        _refs = reader.read_string()  # comma-separated

        # Skip remaining header/merge data if present
        if header_end > 0 and reader.pos < header_end:
            reader.pos = header_end

    last_id = reader.read_int()
    record_count = reader.read_int()

    names: dict[str, str] = {}

    for _ in range(record_count):
        try:
            _raw_ic = reader.read_int()  # discarded
            typecode = reader.read_int()
            record_id = reader.read_int()
            name = reader.read_string()
            string_id = reader.read_string()
            _save_data = reader.read_uint()

            # Use the record's own string_id as the key (e.g. "42243-rebirth.mod")
            if name and string_id:
                names[string_id] = name

            # Skip all field sections without fully parsing them
            # Bool fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                reader.pos += 1  # bool = 1 byte

            # Float fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                reader.pos += 4

            # Int fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                reader.pos += 4

            # Vec3 fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                reader.pos += 12

            # Vec4 fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                reader.pos += 16

            # String fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                _skip_string(reader)

            # File fields
            count = reader.read_int()
            for _ in range(count):
                _skip_string(reader)
                _skip_string(reader)

            # Reference categories
            cat_count = reader.read_int()
            for _ in range(cat_count):
                _skip_string(reader)
                ref_count = reader.read_int()
                for _ in range(ref_count):
                    _skip_string(reader)
                    reader.pos += 12  # 3 ints

            # Instances
            inst_count = reader.read_int()
            for _ in range(inst_count):
                _skip_string(reader)
                _skip_string(reader)
                reader.pos += 28  # vec3 + vec4
                # strings array
                str_count = reader.read_int()
                for _ in range(str_count):
                    _skip_string(reader)

        except Exception:
            break

    return names


def _skip_string(reader: BinaryReader):
    length = reader.read_int()
    if length > 0:
        reader.pos += length


class GameDataResolver:
    def __init__(self):
        self._names: dict[str, str] = {}
        self._loaded = False
        self._data_dir: Path | None = None

    @property
    def is_loaded(self) -> bool:
        return self._loaded

    def load(self, data_dir: Path | None = None):
        if data_dir is None:
            data_dir = find_kenshi_data()
        if data_dir is None:
            return False

        self._data_dir = data_dir
        self._names.clear()

        # Load gamedata.base + all .mod files in data/
        for f in sorted(data_dir.iterdir()):
            if f.suffix in ('.base', '.mod'):
                try:
                    names = _parse_mod_file_names(f)
                    self._names.update(names)
                except Exception as e:
                    pass  # Skip unparseable files

        # Also try mods/ folder
        mods_dir = data_dir.parent / "mods"
        if mods_dir.exists():
            for f in sorted(mods_dir.iterdir()):
                if f.suffix == '.mod':
                    try:
                        names = _parse_mod_file_names(f)
                        self._names.update(names)
                    except Exception:
                        pass

        # Load Steam Workshop mods (Kenshi app ID = 233860)
        # data_dir = .../steamapps/common/Kenshi/data → go up to steamapps
        steamapps_dir = data_dir.parent.parent.parent  # steamapps
        workshop_dir = steamapps_dir / "workshop" / "content" / "233860"
        if workshop_dir.exists():
            for workshop_item in workshop_dir.iterdir():
                if workshop_item.is_dir():
                    for f in workshop_item.iterdir():
                        if f.suffix == '.mod':
                            try:
                                names = _parse_mod_file_names(f)
                                self._names.update(names)
                            except Exception:
                                pass

        self._loaded = len(self._names) > 0
        return self._loaded

    def resolve(self, sid: str) -> str:
        """Resolve a SID like '42243-rebirth.mod' to a human-readable name."""
        if not sid:
            return ""
        name = self._names.get(sid)
        if name:
            return name
        # Fallback: just show the ID part
        return sid

    def resolve_or_sid(self, sid: str) -> tuple[str, bool]:
        """Returns (display_name, was_resolved)."""
        if not sid:
            return ("", False)
        name = self._names.get(sid)
        if name:
            return (name, True)
        return (sid, False)

    def resolve_by_id(self, numeric_id: str) -> str:
        """Try to resolve a numeric ID by checking all known source files."""
        for sid, name in self._names.items():
            if sid.startswith(f"{numeric_id}-"):
                return name
        return numeric_id

    @property
    def total_names(self) -> int:
        return len(self._names)
