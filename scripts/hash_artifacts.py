#!/usr/bin/env python3
"""Write a deterministic SHA-256 manifest for artifact files."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
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
    parser.add_argument(
        "--include-untracked",
        action="store_true",
        help="include every file in the directory instead of only Git-tracked evidence",
    )
    args = parser.parse_args()
    excluded = args.write.resolve() if args.write else None
    if args.include_untracked:
        candidates = list(args.directory.iterdir())
    else:
        repository = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        root = Path(repository.stdout.strip()).resolve()
        tracked = subprocess.run(
            ["git", "ls-files", str(args.directory.resolve().relative_to(root))],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
        candidates = [root / line for line in tracked.stdout.splitlines() if line]
    files = [path for path in candidates if path.is_file() and (excluded is None or path.resolve() != excluded)]
    lines = [f"{sha256(path)}  {path.name}" for path in sorted(files, key=lambda item: item.name)]
    output = "\n".join(lines) + ("\n" if lines else "")
    if args.write:
        args.write.write_text(output, encoding="ascii")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
