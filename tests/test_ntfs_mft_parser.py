import os
import sys
import struct
import unittest
import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ntfs_mft_parser import MFTEntry, MFT_ENTRY_SIZE
from utils import filetime_to_dt

NTFS_EPOCH = datetime.datetime(1601, 1, 1)


def _dt_to_filetime(dt):
    delta = dt - NTFS_EPOCH
    return int(delta.total_seconds() * 10_000_000)


def _build_entry(filename="hello.txt"):
    raw = bytearray(MFT_ENTRY_SIZE)
    raw[0:4] = b"FILE"
    attr_offset = 56
    struct.pack_into("<H", raw, 20, attr_offset)

    si_content_len = 32
    si_content_offset = 24
    si_attr_len = si_content_offset + si_content_len
    struct.pack_into("<II", raw, attr_offset, 0x10, si_attr_len)
    raw[attr_offset + 8] = 0
    struct.pack_into("<I", raw, attr_offset + 16, si_content_len)
    struct.pack_into("<H", raw, attr_offset + 20, si_content_offset)
    created = _dt_to_filetime(datetime.datetime(2020, 1, 1))
    modified = _dt_to_filetime(datetime.datetime(2021, 1, 1))
    mft_mod = _dt_to_filetime(datetime.datetime(2021, 1, 2))
    accessed = _dt_to_filetime(datetime.datetime(2021, 1, 3))
    struct.pack_into("<QQQQ", raw, attr_offset + si_content_offset, created, modified, mft_mod, accessed)

    next_offset = attr_offset + si_attr_len

    name_utf16 = filename.encode("utf-16le")
    fn_content_len = 66 + len(name_utf16)
    fn_content_offset = 24
    fn_attr_len = fn_content_offset + fn_content_len
    struct.pack_into("<II", raw, next_offset, 0x30, fn_attr_len)
    raw[next_offset + 8] = 0
    struct.pack_into("<I", raw, next_offset + 16, fn_content_len)
    struct.pack_into("<H", raw, next_offset + 20, fn_content_offset)

    content_start = next_offset + fn_content_offset
    struct.pack_into("<QQQQ", raw, content_start + 8, created, modified, mft_mod, accessed)
    raw[content_start + 64] = len(filename)
    raw[content_start + 66:content_start + 66 + len(name_utf16)] = name_utf16

    next_offset += fn_attr_len
    struct.pack_into("<I", raw, next_offset, 0xFFFFFFFF)

    return bytes(raw)


class MFTEntryParseTests(unittest.TestCase):

    def test_a_real_entry_yields_standard_info_and_file_name(self):
        entry = MFTEntry(_build_entry("hello.txt"))
        entry.parse()
        types = [a["type"] for a in entry.attributes]
        self.assertEqual(types, ["STANDARD_INFORMATION", "FILE_NAME"])

    def test_the_file_name_attribute_decodes_the_name(self):
        entry = MFTEntry(_build_entry("report.docx"))
        entry.parse()
        file_name_attr = [a for a in entry.attributes if a["type"] == "FILE_NAME"][0]
        self.assertEqual(file_name_attr["name"], "report.docx")

    def test_timestamps_round_trip_through_filetime(self):
        entry = MFTEntry(_build_entry())
        entry.parse()
        std_info = entry.attributes[0]
        self.assertEqual(std_info["created"], datetime.datetime(2020, 1, 1))
        self.assertEqual(std_info["accessed"], datetime.datetime(2021, 1, 3))

    def test_an_entry_without_the_file_magic_is_not_valid(self):
        entry = MFTEntry(b"XXXX" + bytes(MFT_ENTRY_SIZE - 4))
        entry.parse()
        self.assertFalse(entry.valid)
        self.assertEqual(entry.attributes, [])


class FiletimeOverflowTests(unittest.TestCase):

    def test_a_wildly_out_of_range_filetime_returns_none_not_a_crash(self):
        self.assertIsNone(filetime_to_dt(2**63 - 1))

    def test_zero_returns_none(self):
        self.assertIsNone(filetime_to_dt(0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
