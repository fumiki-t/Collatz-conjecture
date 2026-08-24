from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase11_search import generate
from verifier.verify_phase11 import verify


def dependencies(destination: Path) -> None:
    for name in ("phase10_rational_cycle.json", "two_tail_state_collisions.json"):
        os.link(Path("artifacts") / name, destination / name)


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


def test_independent_phase11_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    dependencies(artifacts)
    generate(artifacts, q_limit=35, pair_bound=8_192, pair_depth=8, gap_cap=16, direct_bound=2_048)

    command = [sys.executable, "verifier/verify_phase11.py", "--artifact-dir", str(artifacts)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["failure_q"] == [17, 22, 27, 29, 32, 34]
    assert result["H70"] == "OPEN"
    assert result["proves_collatz"] is False

    ladder = artifacts / "phase11_renewal_ladder.json"
    original = mutate(ladder, lambda data: data["P69"].__setitem__("repository_status", "CONJECTURE"))
    rejected(ladder, original, lambda: verify(artifacts), "P69")
    original = mutate(ladder, lambda data: data["P70"].__setitem__("eventual_barrier", "tampered"))
    rejected(ladder, original, lambda: verify(artifacts), "P70")
    original = mutate(ladder, lambda data: data["H70"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(ladder, original, lambda: verify(artifacts), "H70")

    audit = artifacts / "phase11_dropping_pair_audit.json"
    original = mutate(audit, lambda data: data["E18"]["failure_q"].append(35))
    rejected(audit, original, lambda: verify(artifacts), "E18/NG20")
    original = mutate(audit, lambda data: data["NG20"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(audit, original, lambda: verify(artifacts), "E18/NG20")

    cylinder = artifacts / "phase11_pair_cylinder.json"
    original = mutate(cylinder, lambda data: data["P71"].__setitem__("transition_one", "tampered"))
    rejected(cylinder, original, lambda: verify(artifacts), "P71")
    original = mutate(
        cylinder,
        lambda data: data["E19"]["production_cylinder_audit"].__setitem__("cylinder_row_digest_sha256", "0" * 64),
    )
    rejected(cylinder, original, lambda: verify(artifacts), "E19")
    original = mutate(cylinder, lambda data: data["scalability_boundary"].__setitem__("target_certificate_found", True))
    rejected(cylinder, original, lambda: verify(artifacts), "scalability")


def test_phase11_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase11.py").read_text(encoding="utf-8")
    assert "phase11_search" not in source
    assert "from src" not in source
