from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase17_search import generate
from verifier.verify_phase17 import verify


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
def phase17_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase17")
    generate(root, direct_bound=5000)
    return root


def test_independent_verifier_accepts_and_cli_reports_boundaries(phase17_artifacts: Path) -> None:
    result = verify(phase17_artifacts)
    assert result["valid"] is True
    assert result["claims"]["P104"] == result["claims"]["P105"] == result["claims"]["P106"] == "VERIFIED_THEOREM"
    assert result["claims"]["E28"] == result["claims"]["E29"] == "VERIFIED_FINITE"
    assert result["claims"]["NG29"] == "REFUTED"
    assert result["claims"]["H104"] == result["claims"]["H105"] == "OPEN"
    assert result["proves_collatz"] is False

    completed = subprocess.run(
        [sys.executable, "verifier/verify_phase17.py", "--artifact-dir", str(phase17_artifacts)],
        check=False, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout)["valid"] is True


def test_tamper_rejection_for_predecessor_table_and_log(phase17_artifacts: Path) -> None:
    path = phase17_artifacts / "phase17_predecessor_sieve.json"
    original = mutate(path, lambda value: value["intervals"][0].__setitem__("count", 52))
    rejected(path, original, phase17_artifacts, "CRT upper-envelope")

    original = mutate(path, lambda value: value["psi_270_log_certificate"]["exact_positive_margin"].__setitem__("numerator", "0"))
    rejected(path, original, phase17_artifacts, "270 exact log")

    original = mutate(path, lambda value: value.__setitem__("forbidden_height_rule", "y/N<c"))
    rejected(path, original, phase17_artifacts, "height equality")


def test_tamper_rejection_for_direct_pressure_and_suffix(phase17_artifacts: Path) -> None:
    direct = phase17_artifacts / "phase17_direct_audit.json"
    original = mutate(direct, lambda value: value.__setitem__("row_digest_sha256", "0" * 64))
    rejected(direct, original, phase17_artifacts, "direct audit")

    pressure = phase17_artifacts / "phase17_pressure.json"
    original = mutate(pressure, lambda value: value["first_passage"].__setitem__("union_boundary", "cylinders are disjoint"))
    rejected(pressure, original, phase17_artifacts, "pressure union")

    suffix = phase17_artifacts / "phase17_suffix_code.json"
    original = mutate(suffix, lambda value: value.__setitem__("address_endpoint_digest_sha256", "f" * 64))
    rejected(suffix, original, phase17_artifacts, "suffix code")


def test_tamper_rejection_for_adversarial_and_obstruction(phase17_artifacts: Path) -> None:
    adversarial = phase17_artifacts / "phase17_adversarial.json"
    original = mutate(adversarial, lambda value: value.__setitem__("digest_sha256", "0" * 64))
    rejected(adversarial, original, phase17_artifacts, "adversarial")

    report = phase17_artifacts / "phase17_obstruction_report.md"
    original_text = report.read_text(encoding="utf-8")
    try:
        report.write_text(original_text.replace("`OPEN`", "`VERIFIED_THEOREM`", 1), encoding="utf-8")
        with pytest.raises(ValueError, match="obstruction"):
            verify(phase17_artifacts)
    finally:
        report.write_text(original_text, encoding="utf-8")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase17.py").read_text(encoding="utf-8")
    assert "phase17_search" not in source
    assert "from src" not in source
    assert "import src" not in source
