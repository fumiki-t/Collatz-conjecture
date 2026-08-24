from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.branch_point_search import generate
from verifier.verify_branch_point import verify


def prepare_dependencies(destination: Path) -> None:
    source = Path("artifacts")
    for name in ("phase10_gap_modulus.json", "phase10_safe_pair_spacing.json"):
        os.link(source / name, destination / name)


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> str:
    original = path.read_text(encoding="utf-8")
    data = json.loads(original)
    change(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return original


def rejected(path: Path, original: str, check: Callable[[], object], message: str) -> None:
    try:
        with pytest.raises(ValueError, match=message):
            check()
    finally:
        path.write_text(original, encoding="utf-8")


def test_independent_verifier_accepts_and_rejects_tampering(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    prepare_dependencies(artifacts)
    generate(artifacts, bound=2_000)

    command = [sys.executable, "verifier/verify_branch_point.py", "--artifact-dir", str(artifacts)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["C05"] == "OPEN"
    assert result["proves_collatz"] is False

    path = artifacts / "branch_point_decomposition.json"
    original = mutate(path, lambda data: data["P66"].__setitem__("statement", "tampered"))
    rejected(path, original, lambda: verify(path, artifacts), "P66")
    original = mutate(path, lambda data: data["P67"].__setitem__("case_count", 29))
    rejected(path, original, lambda: verify(path, artifacts), "P67")
    original = mutate(path, lambda data: data["E16"]["profile"][0].__setitem__("max_joint_safe_depth", 1))
    rejected(path, original, lambda: verify(path, artifacts), "profile witness")
    original = mutate(path, lambda data: data["mandatory_adversarial_audit"].__setitem__("row_digest_sha256", "0" * 64))
    rejected(path, original, lambda: verify(path, artifacts), "adversarial")
    original = mutate(path, lambda data: data["C05_reformulation"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(path, original, lambda: verify(path, artifacts), "C05")
