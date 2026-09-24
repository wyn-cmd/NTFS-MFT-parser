# Utility functions for NTFS parsing

import datetime
from typing import Optional

# NTFS epoch starts on January 1, 1601
NTFS_EPOCH = datetime.datetime(1601, 1, 1)

# Convert NTFS filetime (100-ns intervals) to a standard datetime object
def filetime_to_dt(filetime: int) -> Optional[datetime.datetime]:
    if not filetime:
        return None
    try:
        return NTFS_EPOCH + datetime.timedelta(microseconds=filetime // 10)
    except (OverflowError, ValueError):
        return None

# Decode UTF-16LE bytes and strip null terminators and padding
def read_utf16le_string(data: bytes) -> str:
    if not data:
        return ""
    try:
        return data.decode("utf-16le").rstrip("\x00")
    except (UnicodeDecodeError, AttributeError):
        return ""