#!/usr/bin/env python3
"""Check repository Markdown for missing local targets and private paths."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


INLINE_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
REFERENCE_LINK = re.compile(r"^\s*\[[^\]]+\]:\s*(\S+)")
PRIVATE_TARGETS = ("/Users/", "file://", "vscode://")
IGNORED_SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:")


def tracked_markdown(root: Path) -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files", "*.md"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return [root / row for row in completed.stdout.splitlines() if row]


def destination(raw: str) -> str:
    value = raw.strip()
    if value.startswith("<") and ">" in value:
        return value[1 : value.index(">")]
    return value.split(maxsplit=1)[0]


def audit_markdown(root: Path, paths: list[Path] | None = None) -> list[str]:
    errors: list[str] = []
    for path in paths or tracked_markdown(root):
        relative = path.relative_to(root)
        in_fence = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            if any(marker in line for marker in PRIVATE_TARGETS):
                errors.append(f"{relative}:{number}: private or local-only path")
            raw_targets = INLINE_LINK.findall(line)
            reference = REFERENCE_LINK.match(line)
            if reference:
                raw_targets.append(reference.group(1))
            for raw in raw_targets:
                target = destination(raw)
                if not target or target.startswith("#") or target.startswith(IGNORED_SCHEMES):
                    continue
                local = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not local:
                    continue
                resolved = (path.parent / local).resolve()
                try:
                    resolved.relative_to(root.resolve())
                except ValueError:
                    errors.append(f"{relative}:{number}: local link escapes repository: {target}")
                    continue
                if not resolved.exists():
                    errors.append(f"{relative}:{number}: missing local link target: {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="optional repository-relative Markdown files")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    paths = [root / item for item in args.paths] if args.paths else None
    errors = audit_markdown(root, paths)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Markdown links valid: {len(paths or tracked_markdown(root))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
