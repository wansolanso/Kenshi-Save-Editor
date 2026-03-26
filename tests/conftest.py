"""Shared fixtures for Kenshi Save Editor tests."""
from __future__ import annotations
import pytest
from collections import OrderedDict

from src.models import Header, Record, Reference, ReferenceCategory, Instance, SaveFile


@pytest.fixture
def empty_record():
    """A Record with default (empty) values."""
    return Record()


@pytest.fixture
def populated_record():
    """A Record populated with all field types for round-trip testing."""
    rec = Record()
    rec.raw_instance_count = 3
    rec.typecode = 36
    rec.record_id = 42
    rec.name = "Test Character"
    rec.string_id = "42-gamedata.base"
    rec.save_data = 1

    rec.bool_fields = OrderedDict([("is_alive", True), ("is_sleeping", False)])
    rec.float_fields = OrderedDict([("strength", 50.5), ("toughness2", 30.0)])
    rec.long_fields = OrderedDict([("money", 1000), ("age", 25)])
    rec.vec3f_fields = OrderedDict([("position", (100.0, 200.0, 300.0))])
    rec.vec4f_fields = OrderedDict([("rotation", (1.0, 0.0, 0.0, 0.0))])
    rec.string_fields = OrderedDict([("name", "Beep"), ("owner faction ID", "204-gamedata.base")])
    rec.filename_fields = OrderedDict([("mesh", "characters/beep.mesh")])

    cat = ReferenceCategory(name="inventory")
    cat.references.append(Reference(name="item1", v0=1, v1=2, v2=3))
    cat.references.append(Reference(name="item2", v0=4, v1=5, v2=6))
    rec.reference_categories.append(cat)

    inst = Instance()
    inst.string_id = "inst-1"
    inst.target = "target-1"
    inst.position = (10.0, 20.0, 30.0)
    inst.rotation = (1.0, 0.0, 0.0, 0.0)
    inst.states = ["idle", "standing"]
    rec.instances.append(inst)

    return rec


@pytest.fixture
def sample_save_file(populated_record):
    """A SaveFile with a header and one record."""
    sf = SaveFile(path="/tmp/test.save")
    sf.header = Header(filetype=15, next_id=100, record_count=1)
    sf.records.append(populated_record)
    return sf
