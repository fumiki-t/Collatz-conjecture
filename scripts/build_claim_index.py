#!/usr/bin/env python3
"""Build or check the machine-readable index of the Markdown claims ledger."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


COLUMNS = (
    "id",
    "status",
    "claim",
    "dependencies",
    "evidence",
    "first_introduced",
    "last_audited",
    "collatz_implication",
    "notes",
)


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    result.update(path.read_bytes())
    return result.hexdigest()


def split_markdown_row(line: str) -> list[str]:
    """Split a table row without treating pipes inside inline code as cells."""
    cells: list[str] = []
    current: list[str] = []
    in_code = False
    escaped = False
    for character in line.strip()[1:-1]:
        if character == "`" and not escaped:
            in_code = not in_code
        if character == "|" and not in_code and not escaped:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        escaped = character == "\\" and not escaped
        if character != "\\":
            escaped = False
    cells.append("".join(current).strip())
    return cells


def ledger_rows(source: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in source.read_text(encoding="utf-8").splitlines():
        if not re.match(r"^\| [A-Z][A-Z0-9-]* \| `", line):
            continue
        cells = split_markdown_row(line)
        if len(cells) != len(COLUMNS):
            raise ValueError(f"claim row has {len(cells)} cells instead of {len(COLUMNS)}: {line[:80]}")
        row = dict(zip(COLUMNS, cells, strict=True))
        row["status"] = row["status"].strip("`")
        rows.append(row)
    if not rows:
        raise ValueError("no claims found")
    return rows


def build_index(root: Path) -> dict[str, object]:
    source = root / "docs/CLAIMS_LEDGER.md"
    rows = ledger_rows(source)
    known_ids = {row["id"] for row in rows}
    claims = []
    for row in rows:
        dependencies = sorted(
            {
                token
                for token in re.findall(r"\b[A-Z][A-Z0-9-]*\b", row["dependencies"])
                if token in known_ids and token != row["id"]
            }
        )
        claims.append({**row, "dependency_ids": dependencies})
    return {
        "schema_version": 1,
        "generated_from": "docs/CLAIMS_LEDGER.md",
        "source_sha256": sha256(source),
        "claim_count": len(claims),
        "claims": claims,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write research/claims-index.json")
    parser.add_argument("--check", action="store_true", help="fail if the committed index is stale")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root / "research/claims-index.json"
    output = json.dumps(build_index(root), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != output:
            print("research/claims-index.json is stale; run scripts/build_claim_index.py --write", file=sys.stderr)
            return 1
    if args.write:
        target.write_text(output, encoding="utf-8")
    if not args.write and not args.check:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
