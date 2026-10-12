# ntfs mft parser implementation for reading master file table records

import struct
from utils import filetime_to_dt, read_utf16le_string

MFT_ENTRY_SIZE = 1024

ATTR_STANDARD_INFORMATION = 0x10
ATTR_FILE_NAME = 0x30
ATTR_END = 0xFFFFFFFF


# parses a resident $STANDARD_INFORMATION attribute body into the four core NTFS timestamps
def parse_standard_info(content: bytes) -> dict:
    result = {"type": "STANDARD_INFORMATION"}
    if len(content) < 32:
        return result

    timestamps = struct.unpack("<QQQQ", content[0:32])
    result["created"] = filetime_to_dt(timestamps[0])
    result["modified"] = filetime_to_dt(timestamps[1])
    result["mft_modified"] = filetime_to_dt(timestamps[2])
    result["accessed"] = filetime_to_dt(timestamps[3])
    return result


# parses a resident $FILE_NAME attribute body into its timestamps and the file name
def parse_file_name(content: bytes) -> dict:
    result = {"type": "FILE_NAME"}
    if len(content) < 66:
        return result

    timestamps = struct.unpack("<QQQQ", content[8:40])
    result["created"] = filetime_to_dt(timestamps[0])
    result["modified"] = filetime_to_dt(timestamps[1])
    result["mft_modified"] = filetime_to_dt(timestamps[2])
    result["accessed"] = filetime_to_dt(timestamps[3])

    name_length = content[64]
    name_bytes = content[66 : 66 + name_length * 2]
    result["name"] = read_utf16le_string(name_bytes)
    return result


# represents a single parsed mft record entry
class MFTEntry:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.valid = raw[0:4] == b"FILE"
        self.attributes = []

    def parse(self):
        if not self.valid:
            return

        # attribute offset is stored at offset 20
        attr_offset = struct.unpack("<H", self.raw[20:22])[0]

        while attr_offset < MFT_ENTRY_SIZE - 8:
            header = self.raw[attr_offset : attr_offset + 8]
            attr_type, attr_len = struct.unpack("<II", header)

            if attr_type == ATTR_END:
                break

            # basic bounds and sanity check for attribute length
            if attr_len < 24 or attr_offset + attr_len > MFT_ENTRY_SIZE:
                break

            # check if attribute is resident (0) or non-resident (1)
            is_non_resident = self.raw[attr_offset + 8] != 0

            if not is_non_resident:
                content_len = struct.unpack("<I", self.raw[attr_offset + 16 : attr_offset + 20])[0]
                content_offset = struct.unpack("<H", self.raw[attr_offset + 20 : attr_offset + 22])[0]

                start = attr_offset + content_offset
                end = start + content_len

                if end > MFT_ENTRY_SIZE:
                    break

                content = self.raw[start:end]

                if attr_type == ATTR_STANDARD_INFORMATION:
                    self.attributes.append(parse_standard_info(content))
                elif attr_type == ATTR_FILE_NAME:
                    self.attributes.append(parse_file_name(content))

            attr_offset += attr_len