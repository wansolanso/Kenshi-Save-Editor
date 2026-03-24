"""Tests for SaveManager logic."""
from __future__ import annotations
from collections import OrderedDict
from pathlib import Path

import pytest

from src.save_manager import SaveManager
from src.binary_parser import write_file
from src.models import Header, Record, SaveFile


def _make_character_record(name: str, faction_id: str, record_id: int = 1) -> Record:
    rec = Record()
    rec.typecode = 36  # GAMESTATE_CHARACTER
    rec.record_id = record_id
    rec.name = name
    rec.string_fields = OrderedDict([
        ("name", name),
        ("owner faction ID", faction_id),
    ])
    return rec


def _make_faction_record(name: str, record_id: int = 1) -> Record:
    rec = Record()
    rec.typecode = 37  # GAMESTATE_FACTION
    rec.record_id = record_id
    rec.name = name
    return rec


def _populate_save_dir(base: Path) -> Path:
    """Write a minimal quick.save into base and return the directory."""
    sf = SaveFile(path=str(base / "quick.save"))
    sf.header = Header(filetype=15, next_id=10, record_count=2)
    sf.records.append(_make_character_record("Beep", "204-gamedata.base", 1))
    sf.records.append(_make_character_record("Bandit", "999-other.mod", 2))
    write_file(base / "quick.save", sf)
    return base


@pytest.fixture
def test_save_dir(tmp_path):
    """Provide a temp save directory with a quick.save file (auto-cleaned by pytest)."""
    return _populate_save_dir(tmp_path)


class TestSaveManagerLoad:
    def test_load_creates_file_entries(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        assert mgr.is_loaded
        assert "quick.save" in mgr.files

    def test_is_loaded_false_initially(self):
        mgr = SaveManager()
        assert not mgr.is_loaded

    def test_load_with_platoon_files(self, test_save_dir):
        platoon_dir = test_save_dir / "platoon"
        platoon_dir.mkdir()
        sf = SaveFile(path="")
        sf.header = Header(filetype=15, next_id=1, record_count=0)
        write_file(platoon_dir / "squad1.platoon", sf)

        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        assert "platoon/squad1.platoon" in mgr.files


class TestSaveManagerFiltering:
    def test_get_player_characters(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)

        players = mgr.get_player_characters()
        assert len(players) == 1
        assert players[0][1].string_fields["name"] == "Beep"

    def test_get_factions(self, tmp_path):
        sf = SaveFile(path="")
        sf.header = Header(filetype=15, next_id=5, record_count=1)
        sf.records.append(_make_faction_record("Holy Nation"))
        write_file(tmp_path / "quick.save", sf)

        mgr = SaveManager()
        mgr.load_save(tmp_path)
        factions = mgr.get_factions()
        assert len(factions) == 1
        assert factions[0][1].name == "Holy Nation"

    def test_get_records_by_type(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        chars = mgr.get_records_by_type(36)
        assert len(chars) == 2

    def test_get_all_records(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        all_recs = mgr.get_all_records()
        assert len(all_recs) == 2


class TestSaveManagerModification:
    def test_mark_modified(self):
        mgr = SaveManager()
        mgr.mark_modified("quick.save")
        assert "quick.save" in mgr.modified

    def test_save_all_clears_modified(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        mgr.mark_modified("quick.save")
        mgr.save_all()
        assert len(mgr.modified) == 0

    def test_create_backup(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        backup = mgr.create_backup()
        assert backup is not None
        assert backup.exists()
        assert "_backup_" in backup.name

    def test_typecode_summary(self, test_save_dir):
        mgr = SaveManager()
        mgr.load_save(test_save_dir)
        summary = mgr.get_typecode_summary()
        assert summary[36] == 2  # 2 CHARACTER records

    def test_typecode_name(self):
        mgr = SaveManager()
        assert mgr.typecode_name(36) == "GAMESTATE_CHARACTER"
        assert mgr.typecode_name(9999) == "TYPE_9999"
