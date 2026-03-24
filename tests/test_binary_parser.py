"""Tests for the binary parser — the most critical module for data integrity."""
from __future__ import annotations
import struct
import tempfile
from collections import OrderedDict
from pathlib import Path

import pytest

from src.binary_parser import BinaryReader, BinaryWriter, parse_record, write_record, parse_file, write_file
from src.models import Record, Reference, ReferenceCategory, Instance, SaveFile, Header


# ── BinaryReader / BinaryWriter round-trip primitives ──


class TestBinaryReaderWriter:
    def test_int_round_trip(self):
        w = BinaryWriter()
        w.write_int(42)
        w.write_int(-1)
        w.write_int(0)
        r = BinaryReader(w.get_bytes())
        assert r.read_int() == 42
        assert r.read_int() == -1
        assert r.read_int() == 0

    def test_uint_round_trip(self):
        w = BinaryWriter()
        w.write_uint(0)
        w.write_uint(2**32 - 1)
        r = BinaryReader(w.get_bytes())
        assert r.read_uint() == 0
        assert r.read_uint() == 2**32 - 1

    def test_float_round_trip(self):
        w = BinaryWriter()
        w.write_float(3.14)
        w.write_float(0.0)
        w.write_float(-1.5)
        r = BinaryReader(w.get_bytes())
        assert abs(r.read_float() - 3.14) < 1e-5
        assert r.read_float() == 0.0
        assert r.read_float() == -1.5

    def test_bool_round_trip(self):
        w = BinaryWriter()
        w.write_bool(True)
        w.write_bool(False)
        r = BinaryReader(w.get_bytes())
        assert r.read_bool() is True
        assert r.read_bool() is False

    def test_string_round_trip(self):
        w = BinaryWriter()
        w.write_string("hello")
        w.write_string("")
        w.write_string("café ☕")
        r = BinaryReader(w.get_bytes())
        assert r.read_string() == "hello"
        assert r.read_string() == ""
        assert r.read_string() == "café ☕"

    def test_vec3_round_trip(self):
        w = BinaryWriter()
        w.write_vec3((1.0, 2.0, 3.0))
        r = BinaryReader(w.get_bytes())
        assert r.read_vec3() == (1.0, 2.0, 3.0)

    def test_vec4_round_trip_w_last(self):
        w = BinaryWriter()
        w.write_vec4((1.0, 0.0, 0.0, 0.0), w_first=False)
        r = BinaryReader(w.get_bytes())
        assert r.read_vec4(w_first=False) == (1.0, 0.0, 0.0, 0.0)

    def test_vec4_round_trip_w_first(self):
        w = BinaryWriter()
        w.write_vec4((1.0, 0.0, 0.0, 0.0), w_first=True)
        r = BinaryReader(w.get_bytes())
        assert r.read_vec4(w_first=True) == (1.0, 0.0, 0.0, 0.0)

    def test_strings_round_trip(self):
        w = BinaryWriter()
        w.write_strings(["a", "bb", "ccc"])
        r = BinaryReader(w.get_bytes())
        assert r.read_strings() == ["a", "bb", "ccc"]

    def test_strings_empty_list(self):
        w = BinaryWriter()
        w.write_strings([])
        r = BinaryReader(w.get_bytes())
        assert r.read_strings() == []

    def test_remaining_property(self):
        w = BinaryWriter()
        w.write_int(1)
        w.write_int(2)
        r = BinaryReader(w.get_bytes())
        assert r.remaining == 8
        r.read_int()
        assert r.remaining == 4
        r.read_int()
        assert r.remaining == 0

    def test_string_negative_length_returns_empty(self):
        """A string with length <= 0 should return empty string."""
        data = struct.pack('<i', -1)
        r = BinaryReader(data)
        assert r.read_string() == ""

    def test_string_zero_length_returns_empty(self):
        data = struct.pack('<i', 0)
        r = BinaryReader(data)
        assert r.read_string() == ""


# ── Record round-trip ──


class TestRecordRoundTrip:
    def test_empty_record_round_trip(self, empty_record):
        w = BinaryWriter()
        write_record(w, empty_record)
        r = BinaryReader(w.get_bytes())
        parsed = parse_record(r)
        assert parsed.typecode == 0
        assert parsed.name == ""
        assert len(parsed.bool_fields) == 0
        assert len(parsed.float_fields) == 0
        assert len(parsed.long_fields) == 0
        assert len(parsed.reference_categories) == 0
        assert len(parsed.instances) == 0

    def test_populated_record_round_trip(self, populated_record):
        w = BinaryWriter()
        write_record(w, populated_record)
        r = BinaryReader(w.get_bytes())
        parsed = parse_record(r)

        assert parsed.raw_instance_count == populated_record.raw_instance_count
        assert parsed.typecode == populated_record.typecode
        assert parsed.record_id == populated_record.record_id
        assert parsed.name == populated_record.name
        assert parsed.string_id == populated_record.string_id
        assert parsed.save_data == populated_record.save_data

        # Fields
        assert dict(parsed.bool_fields) == dict(populated_record.bool_fields)
        assert dict(parsed.long_fields) == dict(populated_record.long_fields)
        assert dict(parsed.string_fields) == dict(populated_record.string_fields)
        assert dict(parsed.filename_fields) == dict(populated_record.filename_fields)

        # Float fields (approximate)
        for key in populated_record.float_fields:
            assert abs(parsed.float_fields[key] - populated_record.float_fields[key]) < 1e-5

        # Vec3/Vec4
        assert parsed.vec3f_fields == populated_record.vec3f_fields
        assert parsed.vec4f_fields == populated_record.vec4f_fields

        # References
        assert len(parsed.reference_categories) == 1
        cat = parsed.reference_categories[0]
        assert cat.name == "inventory"
        assert len(cat.references) == 2
        assert cat.references[0].name == "item1"
        assert cat.references[0].v0 == 1

        # Instances
        assert len(parsed.instances) == 1
        inst = parsed.instances[0]
        assert inst.string_id == "inst-1"
        assert inst.target == "target-1"
        assert inst.states == ["idle", "standing"]


# ── File round-trip ──


class TestFileRoundTrip:
    def test_save_file_round_trip(self, sample_save_file):
        with tempfile.NamedTemporaryFile(suffix=".save", delete=False) as f:
            tmp = Path(f.name)

        try:
            write_file(tmp, sample_save_file)
            loaded = parse_file(tmp)

            assert loaded.header.filetype == 15
            assert loaded.header.next_id == 100
            assert loaded.header.record_count == 1
            assert len(loaded.records) == 1
            assert loaded.records[0].name == "Test Character"
        finally:
            tmp.unlink(missing_ok=True)

    def test_tail_data_preserved(self):
        """Tail data (extra bytes after records) must survive round-trip."""
        sf = SaveFile(path="")
        sf.header = Header(filetype=15, next_id=1, record_count=0)
        sf.tail_data = b"\xde\xad\xbe\xef" * 10

        with tempfile.NamedTemporaryFile(suffix=".save", delete=False) as f:
            tmp = Path(f.name)

        try:
            write_file(tmp, sf)
            loaded = parse_file(tmp)
            assert loaded.tail_data == sf.tail_data
        finally:
            tmp.unlink(missing_ok=True)

    def test_multiple_records_round_trip(self):
        sf = SaveFile(path="")
        sf.header = Header(filetype=15, next_id=200, record_count=3)
        for i in range(3):
            rec = Record()
            rec.typecode = 36
            rec.record_id = i
            rec.name = f"Char_{i}"
            rec.string_id = f"{i}-gamedata.base"
            sf.records.append(rec)

        with tempfile.NamedTemporaryFile(suffix=".save", delete=False) as f:
            tmp = Path(f.name)

        try:
            write_file(tmp, sf)
            loaded = parse_file(tmp)
            assert len(loaded.records) == 3
            for i, rec in enumerate(loaded.records):
                assert rec.name == f"Char_{i}"
        finally:
            tmp.unlink(missing_ok=True)
