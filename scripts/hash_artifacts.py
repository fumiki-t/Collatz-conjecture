#!/usr/bin/env python3
"""Write a deterministic SHA-256 manifest for artifact files."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--write", type=Path)
    args = parser.parse_args()
    excluded = args.write.resolve() if args.write else None
    files = [
        path
        for path in args.directory.iterdir()
        if path.is_file() and (excluded is None or path.resolve() != excluded)
    ]
    lines = [f"{sha256(path)}  {path.name}" for path in sorted(files, key=lambda item: item.name)]
    output = "\n".join(lines) + ("\n" if lines else "")
    if args.write:
        args.write.write_text(output, encoding="ascii")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
