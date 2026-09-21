from ntfs_mft_parser import MFTEntry, MFT_ENTRY_SIZE


def build_timeline(mft_path, limit=None):
    """Parses an MFT file and builds a chronological or sequential list of file attribute timestamps."""
    timeline = []

    try:
        with open(mft_path, "rb") as f:
            entry_num = 0

            while True:
                raw = f.read(MFT_ENTRY_SIZE)
                if not raw:
                    break

                if len(raw) < MFT_ENTRY_SIZE:
                    # Partial or corrupted trailing record
                    break

                entry = MFTEntry(raw)
                try:
                    entry.parse()
                except Exception:
                    # Skip malformed MFT entries instead of crashing the whole parse
                    entry_num += 1
                    continue

                for attr in entry.attributes:
                    timeline.append({
                        "entry": entry_num,
                        "type": attr.get("type"),
                        "file": attr.get("name", "<no-name>"),
                        "created": attr.get("created"),
                        "modified": attr.get("modified"),
                        "accessed": attr.get("accessed"),
                        "mft_modified": attr.get("mft_modified")
                    })

                entry_num += 1
                if limit and entry_num >= limit:
                    break
    except FileNotFoundError:
        raise FileNotFoundError(f"MFT file not found: {mft_path}")
    except PermissionError:
        raise PermissionError(f"Permission denied accessing MFT file: {mft_path}")

    return timeline


def print_timeline(timeline):
    """Pretty prints the generated timeline events to stdout."""
    if not timeline:
        print("[!] No NTFS artifacts found.")
        return

    for item in timeline:
        print(f"""
Entry #{item['entry']} ({item['type']})
File          : {item['file']}
Created       : {item['created']}
Modified      : {item['modified']}
Accessed      : {item['accessed']}
MFT Modified  : {item['mft_modified']}
""")