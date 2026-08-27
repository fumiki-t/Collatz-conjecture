from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase14_search import generate
from verifier.verify_phase14 import verify


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> str:
    original = path.read_text(encoding="utf-8")
    data = json.loads(original)
    change(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return original


def rejected(path: Path, original: str, artifacts: Path, message: str) -> None:
    try:
        with pytest.raises(ValueError, match=message):
            verify(artifacts)
    finally:
        path.write_text(original, encoding="utf-8")


@pytest.fixture(scope="module")
def phase14_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    artifacts = tmp_path_factory.mktemp("phase14")
    generate(artifacts, maximum_q=13, threshold_q=14)
    return artifacts


def test_independent_verifier_accepts_and_cli_reports_boundary(phase14_artifacts: Path) -> None:
    command = [
        sys.executable,
        "verifier/verify_phase14.py",
        "--artifact-dir",
        str(phase14_artifacts),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["P81"] == "VERIFIED_THEOREM"
    assert result["E23"] == "VERIFIED_FINITE"
    assert result["NG24"] == "REFUTED"
    assert result["H72"] == "OPEN"
    assert result["proves_collatz"] is False


def test_tamper_rejection_for_theory_and_finite_search(phase14_artifacts: Path) -> None:
    theory = phase14_artifacts / "phase14_coalescent_theory.json"
    original = mutate(
        theory,
        lambda data: data["examples"]["minimum_Q4"]["a"].__setitem__("B", 72),
    )
    rejected(theory, original, phase14_artifacts, "coalescent examples")

    search = phase14_artifacts / "phase14_rewrite_search.json"
    original = mutate(search, lambda data: data["E23"].__setitem__("collision_pair_count", 0))
    rejected(search, original, phase14_artifacts, "exhaustive rewrite")


def test_tamper_rejection_for_lemmas_and_adversaries(phase14_artifacts: Path) -> None:
    lemmas = phase14_artifacts / "phase14_auxiliary_lemmas.json"
    original = mutate(
        lemmas,
        lambda data: data["P83"]["thresholds"].__setitem__("r=3", "R>=1"),
    )
    rejected(lemmas, original, phase14_artifacts, "threshold")

    adversarial = phase14_artifacts / "phase14_adversarial_regression.json"
    original = mutate(
        adversarial,
        lambda data: data["E23_regression"].__setitem__("row_digest_sha256", "0" * 64),
    )
    rejected(adversarial, original, phase14_artifacts, "adversarial")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase14.py").read_text(encoding="utf-8")
    assert "phase14_search" not in source
    assert "from src" not in source
    assert "import src" not in source
