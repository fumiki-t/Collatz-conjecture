from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase15_search import generate
from verifier.verify_phase15 import verify


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> str:
    original = path.read_text(encoding="utf-8")
    value = json.loads(original)
    change(value)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return original


def rejected(path: Path, original: str, root: Path, message: str) -> None:
    try:
        with pytest.raises(ValueError, match=message):
            verify(root)
    finally:
        path.write_text(original, encoding="utf-8")


@pytest.fixture(scope="module")
def phase15_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase15")
    generate(root, maximum_q=8)
    return root


def test_independent_verifier_accepts_and_cli_reports_boundaries(phase15_artifacts: Path) -> None:
    completed = subprocess.run(
        [sys.executable, "verifier/verify_phase15.py", "--artifact-dir", str(phase15_artifacts)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["P86"] == "VERIFIED_THEOREM"
    assert result["P87"] == "VERIFIED_THEOREM"
    assert result["P88"] == "VERIFIED_THEOREM"
    assert result["E24"] == "VERIFIED_FINITE"
    assert result["NG25"] == result["NG26"] == "REFUTED"
    assert result["H72"] == "OPEN"
    assert result["proves_collatz"] is False


def test_tamper_rejection_for_theory_and_frontier(phase15_artifacts: Path) -> None:
    theory = phase15_artifacts / "phase15_surplus_theory.json"
    original = mutate(theory, lambda value: value["examples"]["Q6_cross_Q"]["target"].__setitem__("B", 698))
    rejected(theory, original, phase15_artifacts, "surplus theory")

    frontier = phase15_artifacts / "phase15_surplus_frontier.json"
    original = mutate(frontier, lambda value: value["counts_by_target_Q"]["6"].__setitem__("Qb_le_Qd_dominated", 9))
    rejected(frontier, original, phase15_artifacts, "surplus frontier")


def test_tamper_rejection_for_valley_gap_and_adversarial(phase15_artifacts: Path) -> None:
    valley = phase15_artifacts / "phase15_valley_audit.json"
    original = mutate(valley, lambda value: value.__setitem__("certificate_digest_sha256", "0" * 64))
    rejected(valley, original, phase15_artifacts, "valley audit")

    gap = phase15_artifacts / "phase15_gap12_core.json"
    original = mutate(gap, lambda value: value.__setitem__("endpoint_collision_count", 1))
    rejected(gap, original, phase15_artifacts, "gap12 core")

    adversarial = phase15_artifacts / "phase15_adversarial_regression.json"
    original = mutate(adversarial, lambda value: value.__setitem__("row_digest_sha256", "f" * 64))
    rejected(adversarial, original, phase15_artifacts, "adversarial regression")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase15.py").read_text(encoding="utf-8")
    assert "phase15_search" not in source
    assert "from src" not in source
    assert "import src" not in source
