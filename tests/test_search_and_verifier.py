from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

from src.model import Node
from src.search import generate


def survivor_counts(depth: int) -> dict[int, int]:
    frontier = [Node(0, 0, 0, 0, "")]
    result: dict[int, int] = {}
    for current_depth in range(depth + 1):
        survivors = [
            node
            for node in frontier
            if not node.has_uniform_descent() and node.finite_tail_high() is None
        ]
        result[current_depth] = len(survivors)
        frontier = [child for node in survivors for child in node.split()]
    return result


def test_descent_only_sanity_counts() -> None:
    counts = survivor_counts(22)
    assert counts[10] == 64
    assert counts[15] == 1295
    assert counts[20] == 27328
    assert counts[22] == 93222


def test_independent_verifier_accepts_and_rejects_tampering(tmp_path: Path) -> None:
    certificate = tmp_path / "certificate.json"
    summary = generate(certificate, depth=10, coverage_bound=1 << 12)
    assert summary["coverage_audit"]["result"] == "all_equal"
    command = [sys.executable, "verifier/verify_certificate.py", str(certificate)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert json.loads(accepted.stdout)["valid"] is True

    lines = certificate.read_text(encoding="utf-8").splitlines()
    first_record = json.loads(lines[1][:-1])
    assert first_record[5] == "SPLIT"
    first_record[2] = 1
    lines[1] = json.dumps(first_record, separators=(",", ":")) + ","
    certificate.write_text("\n".join(lines) + "\n", encoding="utf-8")
    rejected = subprocess.run(command, check=False, capture_output=True, text=True)
    assert rejected.returncode == 1
    assert rejected.stdout.startswith("INVALID:")


def test_rule_counts_are_stable(tmp_path: Path) -> None:
    certificate = tmp_path / "stable.json"
    summary = generate(certificate, depth=10, coverage_bound=256)
    assert summary["rule_counts"] == {"DESCENT": 27, "OPEN": 64, "SPLIT": 90}
    assert summary["survivors_by_depth"]["10"] == 64


def test_certificate_bytes_are_deterministic(tmp_path: Path) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    generate(first, depth=8, coverage_bound=512, audit_workers=1)
    generate(second, depth=8, coverage_bound=512, audit_workers=1)
    assert first.read_bytes() == second.read_bytes()
