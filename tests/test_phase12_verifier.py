from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase12_search import generate
from verifier.verify_phase12 import verify


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


def test_independent_phase12_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    generate(artifacts, start_bound=1_000, maximum_odd=32, contact_q=64)
    command = [sys.executable, "verifier/verify_phase12.py", "--artifact-dir", str(artifacts)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["P72"] == "VERIFIED_THEOREM"
    assert result["P73"] == "VERIFIED_THEOREM"
    assert result["H72"] == "OPEN"
    assert result["proves_collatz"] is False

    theorem = artifacts / "phase12_packing_theorem.json"
    original = mutate(theorem, lambda data: data["P72"].__setitem__("repository_status", "CONJECTURE"))
    rejected(theorem, original, lambda: verify(artifacts), "P72")
    original = mutate(theorem, lambda data: data["P72"].__setitem__("growth_bound", "Y_j<=1"))
    rejected(theorem, original, lambda: verify(artifacts), "P72")
    original = mutate(
        theorem,
        lambda data: data["exact_exponent_arithmetic"]["growth_exponent"].__setitem__("numerator", 2),
    )
    rejected(theorem, original, lambda: verify(artifacts), "P72")

    contact = artifacts / "phase12_all_contact.json"
    original = mutate(contact, lambda data: data["P73"].__setitem__("repository_status", "OPEN"))
    rejected(contact, original, lambda: verify(artifacts), "P73")
    original = mutate(contact, lambda data: data["finite_prefix_regression"].__setitem__("row_digest_sha256", "0" * 64))
    rejected(contact, original, lambda: verify(artifacts), "P73")

    finite = artifacts / "phase12_finite_orbits.json"
    original = mutate(finite, lambda data: data["E20"].__setitem__("row_digest_sha256", "f" * 64))
    rejected(finite, original, lambda: verify(artifacts), "E20")
    original = mutate(finite, lambda data: data["E20"]["adversarial"].__setitem__("instance_count", 0))
    rejected(finite, original, lambda: verify(artifacts), "E20")

    obstruction = artifacts / "phase12_packing_obstruction.json"
    original = mutate(obstruction, lambda data: data["NG21"].__setitem__("repository_status", "OPEN"))
    rejected(obstruction, original, lambda: verify(artifacts), "NG21")
    original = mutate(obstruction, lambda data: data["H72"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(obstruction, original, lambda: verify(artifacts), "H72")


def test_phase12_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase12.py").read_text(encoding="utf-8")
    assert "phase12_search" not in source
    assert "from src" not in source
