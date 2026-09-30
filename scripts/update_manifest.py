#!/usr/bin/env python3
"""Refresh the current snapshot after intentional changes; keep history intact."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def main():
    names = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
    ).decode().split("\0")
    hashes = {}
    for name in sorted(set(names)):
        if not name or name == "FILE_MANIFEST.json":
            continue
        path = ROOT / name
        if path.is_symlink():
            raise SystemExit(f"Refusing to hash a symlink: {name}")
        if path.is_file():
            hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (ROOT / "FILE_MANIFEST.json").write_text(
        json.dumps({"sha256": hashes}, indent=2) + "\n"
    )
    print(f"Recorded {len(hashes)} file hashes.")


if __name__ == "__main__":
    main()
