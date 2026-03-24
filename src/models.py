from __future__ import annotations
from dataclasses import dataclass, field
from collections import OrderedDict


@dataclass
class Header:
    filetype: int = 15
    next_id: int = 0
    record_count: int = 0


@dataclass
class Reference:
    name: str = ""
    v0: int = 0
    v1: int = 0
    v2: int = 0


@dataclass
class ReferenceCategory:
    name: str = ""
    references: list[Reference] = field(default_factory=list)


@dataclass
class Instance:
    string_id: str = ""
    target: str = ""
    position: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation: tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)
    states: list[str] = field(default_factory=list)


@dataclass
class Record:
    raw_instance_count: int = 0  # first int, discarded by OCS but kept for round-trip
    typecode: int = 0
    record_id: int = 0
    name: str = ""
    string_id: str = ""
    save_data: int = 0

    bool_fields: OrderedDict[str, bool] = field(default_factory=OrderedDict)
    float_fields: OrderedDict[str, float] = field(default_factory=OrderedDict)
    long_fields: OrderedDict[str, int] = field(default_factory=OrderedDict)
    vec3f_fields: OrderedDict[str, tuple[float, float, float]] = field(default_factory=OrderedDict)
    vec4f_fields: OrderedDict[str, tuple[float, float, float, float]] = field(default_factory=OrderedDict)
    string_fields: OrderedDict[str, str] = field(default_factory=OrderedDict)
    filename_fields: OrderedDict[str, str] = field(default_factory=OrderedDict)

    reference_categories: list[ReferenceCategory] = field(default_factory=list)
    instances: list[Instance] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        return self.name or self.string_id or f"Record #{self.record_id}"

    @property
    def total_fields(self) -> int:
        return (len(self.bool_fields) + len(self.float_fields) +
                len(self.long_fields) + len(self.vec3f_fields) +
                len(self.vec4f_fields) + len(self.string_fields) +
                len(self.filename_fields))


@dataclass
class SaveFile:
    path: str = ""
    header: Header = field(default_factory=Header)
    records: list[Record] = field(default_factory=list)
    tail_data: bytes = b""  # remaining bytes after records (quick.save has ~45k of trailing ints)
