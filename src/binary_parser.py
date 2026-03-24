from __future__ import annotations
import struct
from collections import OrderedDict
from pathlib import Path

from .models import Header, Record, Instance, Reference, ReferenceCategory, SaveFile


class BinaryReader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def read_bytes(self, n: int) -> bytes:
        result = self.data[self.pos:self.pos + n]
        self.pos += n
        return result

    def read_int(self) -> int:
        val = struct.unpack_from('<i', self.data, self.pos)[0]
        self.pos += 4
        return val

    def read_uint(self) -> int:
        val = struct.unpack_from('<I', self.data, self.pos)[0]
        self.pos += 4
        return val

    def read_float(self) -> float:
        val = struct.unpack_from('<f', self.data, self.pos)[0]
        self.pos += 4
        return val

    def read_bool(self) -> bool:
        val = self.data[self.pos]
        self.pos += 1
        return val != 0

    def read_string(self) -> str:
        length = self.read_int()
        if length <= 0:
            return ""
        raw = self.data[self.pos:self.pos + length]
        self.pos += length
        return raw.decode('utf-8', errors='replace')

    def read_vec3(self) -> tuple[float, float, float]:
        x = self.read_float()
        y = self.read_float()
        z = self.read_float()
        return (x, y, z)

    def read_vec4(self, w_first: bool = False) -> tuple[float, float, float, float]:
        if w_first:
            w = self.read_float()
            x = self.read_float()
            y = self.read_float()
            z = self.read_float()
        else:
            x = self.read_float()
            y = self.read_float()
            z = self.read_float()
            w = self.read_float()
        return (w, x, y, z)

    def read_strings(self) -> list[str]:
        count = self.read_int()
        return [self.read_string() for _ in range(count)]

    @property
    def remaining(self) -> int:
        return len(self.data) - self.pos


class BinaryWriter:
    def __init__(self):
        self.buffer = bytearray()

    def write_int(self, val: int):
        self.buffer.extend(struct.pack('<i', val))

    def write_uint(self, val: int):
        self.buffer.extend(struct.pack('<I', val))

    def write_float(self, val: float):
        self.buffer.extend(struct.pack('<f', val))

    def write_bool(self, val: bool):
        self.buffer.append(1 if val else 0)

    def write_string(self, val: str):
        encoded = val.encode('utf-8')
        self.write_int(len(encoded))
        self.buffer.extend(encoded)

    def write_vec3(self, v: tuple[float, float, float]):
        self.write_float(v[0])
        self.write_float(v[1])
        self.write_float(v[2])

    def write_vec4(self, v: tuple[float, float, float, float], w_first: bool = False):
        w, x, y, z = v
        if w_first:
            self.write_float(w)
            self.write_float(x)
            self.write_float(y)
            self.write_float(z)
        else:
            self.write_float(x)
            self.write_float(y)
            self.write_float(z)
            self.write_float(w)

    def write_strings(self, strings: list[str]):
        self.write_int(len(strings))
        for s in strings:
            self.write_string(s)

    def get_bytes(self) -> bytes:
        return bytes(self.buffer)


def parse_record(reader: BinaryReader) -> Record:
    rec = Record()

    # First int is discarded by OCS ("instance count or item length")
    # We keep it for round-trip fidelity
    rec.raw_instance_count = reader.read_int()

    rec.typecode = reader.read_int()
    rec.record_id = reader.read_int()
    rec.name = reader.read_string()
    rec.string_id = reader.read_string()
    rec.save_data = reader.read_uint()

    # 1. Bool fields
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        val = reader.read_bool()
        rec.bool_fields[key] = val

    # 2. Float fields
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        val = reader.read_float()
        rec.float_fields[key] = val

    # 3. Int/Long fields
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        val = reader.read_int()
        rec.long_fields[key] = val

    # 4. Vec3f fields
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        rec.vec3f_fields[key] = reader.read_vec3()

    # 5. Vec4f fields (x, y, z, w order in field sections)
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        rec.vec4f_fields[key] = reader.read_vec4(w_first=False)

    # 6. String fields
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        val = reader.read_string()
        rec.string_fields[key] = val

    # 7. Filename/File fields
    count = reader.read_int()
    for _ in range(count):
        key = reader.read_string()
        val = reader.read_string()
        rec.filename_fields[key] = val

    # Reference categories
    cat_count = reader.read_int()
    for _ in range(cat_count):
        cat_name = reader.read_string()
        ref_count = reader.read_int()
        cat = ReferenceCategory(name=cat_name)
        for _ in range(ref_count):
            ref_name = reader.read_string()
            v0 = reader.read_int()
            v1 = reader.read_int()
            v2 = reader.read_int()
            cat.references.append(Reference(ref_name, v0, v1, v2))
        rec.reference_categories.append(cat)

    # Instances
    inst_count = reader.read_int()
    for _ in range(inst_count):
        inst = Instance()
        inst.string_id = reader.read_string()
        inst.target = reader.read_string()
        inst.position = reader.read_vec3()
        inst.rotation = reader.read_vec4(w_first=True)
        inst.states = reader.read_strings()
        rec.instances.append(inst)

    return rec


def parse_file(path: str | Path) -> SaveFile:
    path = Path(path)
    data = path.read_bytes()
    reader = BinaryReader(data)

    sf = SaveFile(path=str(path))
    sf.header.filetype = reader.read_int()
    sf.header.next_id = reader.read_int()
    sf.header.record_count = reader.read_int()

    for _ in range(sf.header.record_count):
        rec = parse_record(reader)
        sf.records.append(rec)

    # Capture any remaining tail data (quick.save has trailing int stream)
    if reader.remaining > 0:
        sf.tail_data = reader.read_bytes(reader.remaining)

    return sf


def write_record(writer: BinaryWriter, rec: Record):
    writer.write_int(rec.raw_instance_count)
    writer.write_int(rec.typecode)
    writer.write_int(rec.record_id)
    writer.write_string(rec.name)
    writer.write_string(rec.string_id)
    writer.write_uint(rec.save_data)

    # 1. Bool
    writer.write_int(len(rec.bool_fields))
    for key, val in rec.bool_fields.items():
        writer.write_string(key)
        writer.write_bool(val)

    # 2. Float
    writer.write_int(len(rec.float_fields))
    for key, val in rec.float_fields.items():
        writer.write_string(key)
        writer.write_float(val)

    # 3. Int/Long
    writer.write_int(len(rec.long_fields))
    for key, val in rec.long_fields.items():
        writer.write_string(key)
        writer.write_int(val)

    # 4. Vec3f
    writer.write_int(len(rec.vec3f_fields))
    for key, v in rec.vec3f_fields.items():
        writer.write_string(key)
        writer.write_vec3(v)

    # 5. Vec4f (x, y, z, w order in field sections)
    writer.write_int(len(rec.vec4f_fields))
    for key, v in rec.vec4f_fields.items():
        writer.write_string(key)
        writer.write_vec4(v, w_first=False)

    # 6. String
    writer.write_int(len(rec.string_fields))
    for key, val in rec.string_fields.items():
        writer.write_string(key)
        writer.write_string(val)

    # 7. Filename
    writer.write_int(len(rec.filename_fields))
    for key, val in rec.filename_fields.items():
        writer.write_string(key)
        writer.write_string(val)

    # Reference categories
    writer.write_int(len(rec.reference_categories))
    for cat in rec.reference_categories:
        writer.write_string(cat.name)
        writer.write_int(len(cat.references))
        for ref in cat.references:
            writer.write_string(ref.name)
            writer.write_int(ref.v0)
            writer.write_int(ref.v1)
            writer.write_int(ref.v2)

    # Instances
    writer.write_int(len(rec.instances))
    for inst in rec.instances:
        writer.write_string(inst.string_id)
        writer.write_string(inst.target)
        writer.write_vec3(inst.position)
        writer.write_vec4(inst.rotation, w_first=True)
        writer.write_strings(inst.states)


def write_file(path: str | Path, save_file: SaveFile):
    path = Path(path)
    writer = BinaryWriter()

    writer.write_int(save_file.header.filetype)
    writer.write_int(save_file.header.next_id)
    writer.write_int(len(save_file.records))

    for rec in save_file.records:
        write_record(writer, rec)

    if save_file.tail_data:
        writer.buffer.extend(save_file.tail_data)

    path.write_bytes(writer.get_bytes())
