# ntfs mft parser implementation for reading master file table records

import struct
from utils import filetime_to_dt, read_utf16le_string

MFT_ENTRY_SIZE = 1024

ATTR_STANDARD_INFORMATION = 0x10
ATTR_FILE_NAME = 0x30
ATTR_END = 0xFFFFFFFF


# represents a single parsed mft record entry
class MFTEntry:
    def __init__(self, raw: bytes):
        self.raw = raw
        self.valid = raw[0:4] == b"FILE"
        self.attributes = []

    def parse(self):
        if not self.valid:
            return

        attr_offset = struct.unpack("<H", self.raw[20:22])[0]

        while attr_offset < MFT_ENTRY_SIZE - 8:
            header = self.raw[attr_offset:attr_offset + 8]
            attr_type, attr_len = struct.unpack("<II", header)

            if attr_type == ATTR_END:
                break

            if attr_len < 24 or attr_offset + attr_len > MFT_ENTRY_SIZE:
                break

            non_res = self.raw[attr_offset + 8]

            if non_res == 0:
                content_len = struct.unpack("<I", self.raw[attr_offset + 16:attr_offset + 20])[0]
                content_offset = struct.unpack("<H", self.raw[attr_offset + 20:attr_offset + 22])[0]

                content_start = attr_offset + content_offset
                content_end = content_start + content_len

                if content_end > MFT_ENTRY_SIZE:
                    break

                content = self.raw[content_start:content_end]

                if attr_type == ATTR_STANDARD_INFORMATION:
                    self.attributes.append(parse_standard_info(content))
                elif attr_type == ATTR_FILE_NAME:
                    self.attributes.append(parse_file_name(content))

            attr_offset += attr_len