"""Tests for data models."""
from __future__ import annotations
from collections import OrderedDict

from src.models import Header, Record, Reference, ReferenceCategory, Instance, SaveFile


class TestRecord:
    def test_display_name_prefers_name(self):
        rec = Record(name="Beep", string_id="42-gamedata.base", record_id=42)
        assert rec.display_name == "Beep"

    def test_display_name_falls_back_to_string_id(self):
        rec = Record(name="", string_id="42-gamedata.base", record_id=42)
        assert rec.display_name == "42-gamedata.base"

    def test_display_name_falls_back_to_record_id(self):
        rec = Record(name="", string_id="", record_id=42)
        assert rec.display_name == "Record #42"

    def test_total_fields_empty(self):
        rec = Record()
        assert rec.total_fields == 0

    def test_total_fields_counts_all_types(self):
        rec = Record()
        rec.bool_fields = OrderedDict([("a", True)])
        rec.float_fields = OrderedDict([("b", 1.0), ("c", 2.0)])
        rec.long_fields = OrderedDict([("d", 1)])
        rec.vec3f_fields = OrderedDict([("e", (0, 0, 0))])
        rec.vec4f_fields = OrderedDict([("f", (0, 0, 0, 0))])
        rec.string_fields = OrderedDict([("g", "x")])
        rec.filename_fields = OrderedDict([("h", "y"), ("i", "z")])
        assert rec.total_fields == 9


class TestHeader:
    def test_defaults(self):
        h = Header()
        assert h.filetype == 15
        assert h.next_id == 0
        assert h.record_count == 0


class TestInstance:
    def test_defaults(self):
        inst = Instance()
        assert inst.string_id == ""
        assert inst.target == ""
        assert inst.position == (0.0, 0.0, 0.0)
        assert inst.rotation == (1.0, 0.0, 0.0, 0.0)
        assert inst.states == []


class TestSaveFile:
    def test_defaults(self):
        sf = SaveFile()
        assert sf.path == ""
        assert sf.records == []
        assert sf.tail_data == b""

    def test_independent_instances(self):
        """Each SaveFile should have its own record list."""
        sf1 = SaveFile()
        sf2 = SaveFile()
        sf1.records.append(Record(name="A"))
        assert len(sf2.records) == 0
