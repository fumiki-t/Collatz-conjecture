from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.two_tail_search import generate
from verifier.verify_two_tail import verify


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
    os.link(Path("artifacts/branch_point_decomposition.json"), artifacts / "branch_point_decomposition.json")
    generate(artifacts, bound=512, gap_cap=64, horizon=6)

    command = [sys.executable, "verifier/verify_two_tail.py", "--artifact-dir", str(artifacts)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["C05"] == "OPEN"
    assert result["proves_collatz"] is False

    path = artifacts / "two_tail_state_collisions.json"
    original = mutate(path, lambda data: data["P68"].__setitem__("statement", "tampered"))
    rejected(path, original, lambda: verify(path, artifacts), "P68")
    original = mutate(path, lambda data: data["NG19"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(path, original, lambda: verify(path, artifacts), "NG19")
    original = mutate(path, lambda data: data["NG19"]["smallest_collision_for_each_b"][0]["second_pair"].__setitem__("m", 99))
    rejected(path, original, lambda: verify(path, artifacts), "collision")
    original = mutate(path, lambda data: data["mandatory_adversarial_audit"].__setitem__("row_digest_sha256", "0" * 64))
    rejected(path, original, lambda: verify(path, artifacts), "adversarial")
    original = mutate(path, lambda data: data["C05_implication"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(path, original, lambda: verify(path, artifacts), "C05")


def test_verifier_does_not_import_searcher() -> None:
    source = Path("verifier/verify_two_tail.py").read_text(encoding="utf-8")
    assert "two_tail_search" not in source
    assert "from src" not in source
