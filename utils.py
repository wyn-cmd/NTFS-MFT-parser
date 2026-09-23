import datetime
from typing import Optional

NTFS_EPOCH = datetime.datetime(1601, 1, 1)

# Convert NTFS filetime (100-ns intervals) to datetime
def filetime_to_dt(filetime: int) -> Optional[datetime.datetime]:
    if not filetime:
        return None
    return NTFS_EPOCH + datetime.timedelta(microseconds=filetime // 10)

# Decode UTF-16LE bytes and strip null terminators
def read_utf16le_string(data: bytes) -> str:
    try:
        return data.decode("utf-16le").rstrip("\x00")
    except (UnicodeDecodeError, AttributeError):
        return ""