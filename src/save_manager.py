from __future__ import annotations
import shutil
from datetime import datetime
from pathlib import Path

from .binary_parser import parse_file, write_file
from .models import SaveFile, Record
from .constants import TYPECODE_NAMES


class SaveManager:
    def __init__(self):
        self.save_dir: Path | None = None
        self.files: dict[str, SaveFile] = {}  # filename -> SaveFile
        self.modified: set[str] = set()

    @property
    def is_loaded(self) -> bool:
        return self.save_dir is not None and len(self.files) > 0

    def load_save(self, directory: str | Path):
        directory = Path(directory)
        self.save_dir = directory
        self.files.clear()
        self.modified.clear()

        # Parse quick.save
        qs = directory / "quick.save"
        if qs.exists():
            self.files["quick.save"] = parse_file(qs)

        # Parse platoon files
        platoon_dir = directory / "platoon"
        if platoon_dir.exists():
            for pf in sorted(platoon_dir.glob("*.platoon")):
                key = f"platoon/{pf.name}"
                self.files[key] = parse_file(pf)

        # Zone files can be loaded on demand (they're large)

    def get_all_records(self) -> list[tuple[str, Record]]:
        result = []
        for filename, sf in self.files.items():
            for rec in sf.records:
                result.append((filename, rec))
        return result

    def get_records_by_type(self, typecode: int) -> list[tuple[str, Record]]:
        return [(f, r) for f, r in self.get_all_records() if r.typecode == typecode]

    def get_player_characters(self) -> list[tuple[str, Record]]:
        result = []
        for filename, rec in self.get_all_records():
            if rec.typecode == 36 and "name" in rec.string_fields:
                faction_id = rec.string_fields.get("owner faction ID", "")
                if "204-gamedata.base" in faction_id:
                    result.append((filename, rec))
        return result

    def get_factions(self) -> list[tuple[str, Record]]:
        return self.get_records_by_type(37)

    def mark_modified(self, filename: str):
        self.modified.add(filename)

    def create_backup(self):
        if not self.save_dir:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.save_dir.parent / f"{self.save_dir.name}_backup_{timestamp}"
        shutil.copytree(self.save_dir, backup_dir)
        return backup_dir

    def save_all(self):
        if not self.save_dir:
            return

        for filename in self.modified:
            sf = self.files.get(filename)
            if sf is None:
                continue
            out_path = self.save_dir / filename
            out_path.parent.mkdir(parents=True, exist_ok=True)
            write_file(out_path, sf)

        self.modified.clear()

    def save_file(self, filename: str):
        if not self.save_dir:
            return
        sf = self.files.get(filename)
        if sf is None:
            return
        out_path = self.save_dir / filename
        out_path.parent.mkdir(parents=True, exist_ok=True)
        write_file(out_path, sf)
        self.modified.discard(filename)

    def get_typecode_summary(self) -> dict[int, int]:
        from collections import Counter
        counts = Counter()
        for _, sf in self.files.items():
            for rec in sf.records:
                counts[rec.typecode] += 1
        return dict(counts.most_common())

    def typecode_name(self, tc: int) -> str:
        return TYPECODE_NAMES.get(tc, f"TYPE_{tc}")
