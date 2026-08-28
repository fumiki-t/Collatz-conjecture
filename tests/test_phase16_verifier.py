from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase16_search import generate
from verifier.verify_phase16 import verify


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
def phase16_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase16")
    generate(root, maximum_q=8)
    return root


def test_independent_verifier_accepts_and_cli_reports_boundaries(phase16_artifacts: Path) -> None:
    result = verify(phase16_artifacts)
    assert result["valid"] is True
    assert result["claims"]["P101"] == "VERIFIED_THEOREM"
    assert result["claims"]["P103"] == "CONDITIONAL"
    assert result["claims"]["NG28"] == "REFUTED"
    assert result["claims"]["H97"] == result["claims"]["H98"] == "OPEN"
    assert result["proves_collatz"] is False

    completed = subprocess.run(
        [sys.executable, "verifier/verify_phase16.py", "--artifact-dir", str(phase16_artifacts)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout)["valid"] is True


def test_tamper_rejection_for_carry_log_and_scope(phase16_artifacts: Path) -> None:
    theory = phase16_artifacts / "phase16_theory.json"
    original = mutate(theory, lambda value: value["negative_carry"].__setitem__("carry", -2))
    rejected(theory, original, phase16_artifacts, "negative carry")

    original = mutate(theory, lambda value: value["log_certificate"]["exact_positive_margin_after_reduction"].__setitem__("numerator", "0"))
    rejected(theory, original, phase16_artifacts, "250 comparison")

    original = mutate(theory, lambda value: value["dichotomy"].__setitem__("periodic_boundary", "G250 also applies"))
    rejected(theory, original, phase16_artifacts, "periodic scope")


def test_tamper_rejection_for_finite_and_adversarial(phase16_artifacts: Path) -> None:
    finite = phase16_artifacts / "phase16_finite_layers.json"
    original = mutate(finite, lambda value: value["counts_by_Q"]["8"].__setitem__("same_Q_geodesic", 0))
    rejected(finite, original, phase16_artifacts, "finite layer")

    adversarial = phase16_artifacts / "phase16_adversarial.json"
    original = mutate(adversarial, lambda value: value.__setitem__("row_digest_sha256", "0" * 64))
    rejected(adversarial, original, phase16_artifacts, "adversarial")


def test_tamper_rejection_for_obstruction_report(phase16_artifacts: Path) -> None:
    path = phase16_artifacts / "phase16_obstruction_report.md"
    original = path.read_text(encoding="utf-8")
    try:
        path.write_text(original.replace("Without distinctness", "With or without distinctness", 1), encoding="utf-8")
        with pytest.raises(ValueError, match="obstruction"):
            verify(phase16_artifacts)
    finally:
        path.write_text(original, encoding="utf-8")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase16.py").read_text(encoding="utf-8")
    assert "phase16_search" not in source
    assert "from src" not in source
    assert "import src" not in source
