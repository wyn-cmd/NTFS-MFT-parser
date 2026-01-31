from ntfs_mft_parser import MFTEntry, MFT_ENTRY_SIZE


def build_timeline(mft_path, limit=None):
    timeline = []

    with open(mft_path, "rb") as f:
        entry_num = 0

        while True:
            raw = f.read(MFT_ENTRY_SIZE)
            if not raw:
                break

            entry = MFTEntry(raw)
            entry.parse()

            for attr in entry.attributes:
                timeline.append({
                    "entry": entry_num,
                    "type": attr["type"],
                    "file": attr.get("name", "<no-name>"),
                    "created": attr.get("created"),
                    "modified": attr.get("modified"),
                    "accessed": attr.get("accessed"),
                    "mft_modified": attr.get("mft_modified")
                })

            entry_num += 1
            if limit and entry_num >= limit:
                break

    return timeline


def print_timeline(timeline):
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
