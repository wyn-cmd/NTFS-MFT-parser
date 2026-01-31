import struct
import datetime

NTFS_EPOCH = datetime.datetime(1601, 1, 1)

def filetime_to_dt(filetime):
    if filetime == 0:
        return None
    return NTFS_EPOCH + datetime.timedelta(microseconds=filetime // 10)

def read_utf16le_string(data):
    try:
        return data.decode("utf-16le").rstrip("\x00")
    except:
        return ""
