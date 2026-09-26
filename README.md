# NTFS Artifact Correlation Tool

A lightweight forensic tool that parses raw NTFS `$MFT` entries & correlates file system timestamps into a readable timeline.

Designed for digital forensics & incident response (DFIR) work.

---

## Features

- Parses raw `$MFT` files
- Extracts `STANDARD_INFORMATION` timestamps
- Extracts `FILE_NAME` timestamps
- Builds a basic forensic timeline
- No external dependencies

---

## Usage

1. Extract the `$MFT` file from an NTFS volume using a forensic tool  
2. Place the file as `MFT.raw` in the project directory  
3. Run:

```bash
python main.py
```

## Tests

```bash
python3 -m unittest discover tests
```

Six tests build a synthetic $MFT entry in memory and confirm STANDARD_INFORMATION and FILE_NAME parse correctly, including the filename and all four timestamps, plus the filetime overflow guard.
