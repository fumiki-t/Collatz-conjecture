from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase13_search import generate
from verifier.verify_phase13 import verify


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


@pytest.fixture()
def phase13_artifacts(tmp_path: Path) -> Path:
    artifacts = tmp_path / "artifacts"
    generate(
        artifacts,
        dp_length=64,
        maximum_q=7,
        maximum_blocks=2,
        height=64,
        critical_steps=128,
    )
    return artifacts


def test_independent_verifier_accepts_and_cli_reports_boundary(phase13_artifacts: Path) -> None:
    command = [
        sys.executable,
        "verifier/verify_phase13.py",
        "--artifact-dir",
        str(phase13_artifacts),
    ]
    completed = subprocess.run(command, check=False, capture_output=True, text=True)
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["P77"] == "VERIFIED_THEOREM"
    assert result["P80"] == "CONDITIONAL"
    assert result["H72"] == "OPEN"
    assert result["proves_collatz"] is False


def test_tamper_rejection_for_theorem_and_finite_fields(phase13_artifacts: Path) -> None:
    renewal = phase13_artifacts / "phase13_renewal_code.json"
    original = mutate(renewal, lambda d: d["P77"].__setitem__("orientation", "w_i=u_i"))
    rejected(renewal, original, phase13_artifacts, "orientation")
    original = mutate(renewal, lambda d: d["P77"].__setitem__("endpoint_bits", "no exception"))
    rejected(renewal, original, phase13_artifacts, "exception")
    original = mutate(renewal, lambda d: d["P77"].__setitem__("code_property", "not checked"))
    rejected(renewal, original, phase13_artifacts, "prefix-free")

    pressure = phase13_artifacts / "phase13_pressure_bounds.json"
    original = mutate(pressure, lambda d: d["P78"].__setitem__("weighted_identity", "0"))
    rejected(pressure, original, phase13_artifacts, "Kraft")
    original = mutate(pressure, lambda d: d["P78"]["bounds"].__setitem__("kappa", "<1"))
    rejected(pressure, original, phase13_artifacts, "bounds")
    original = mutate(
        pressure,
        lambda d: d["E22_pressure_dp"]["final"]["kappa"].__setitem__("numerator", "1"),
    )
    rejected(pressure, original, phase13_artifacts, "finite DP")

    threshold = phase13_artifacts / "phase13_threshold_bridge.json"
    original = mutate(threshold, lambda d: d["finite_block_audit"].__setitem__("R_13_over_9_words", []))
    rejected(threshold, original, phase13_artifacts, "threshold")
    original = mutate(threshold, lambda d: d["finite_block_audit"].__setitem__("q3_count", 1))
    rejected(threshold, original, phase13_artifacts, "threshold")
    original = mutate(threshold, lambda d: d["P79"].__setitem__("positive_source_bridge", "no divisibility"))
    rejected(threshold, original, phase13_artifacts, "divisibility")
    original = mutate(
        threshold,
        lambda d: d["P79"]["normalized_transfer"].__setitem__("valuation", "unknown"),
    )
    rejected(threshold, original, phase13_artifacts, "valuation")

    critical = phase13_artifacts / "phase13_critical_countermodel.json"
    original = mutate(critical, lambda d: d["finite_audit"].__setitem__("row_digest_sha256", "0" * 64))
    rejected(critical, original, phase13_artifacts, "critical recurrence")

    residue = phase13_artifacts / "phase13_residue_audit.json"
    original = mutate(
        residue,
        lambda d: d["NG23"]["least_counterexample"].__setitem__("canonical_count", 0),
    )
    rejected(residue, original, phase13_artifacts, "canonical count")
    original = mutate(
        residue,
        lambda d: d["E22"]["address_families"][0].__setitem__("endpoint_max_plus_one_error", {}),
    )
    rejected(residue, original, phase13_artifacts, "address residue")
    original = mutate(
        residue,
        lambda d: d["E22"]["address_families"][0]["endpoint_cylinders"].__setitem__(
            "compatible_unordered_pairs", 0
        ),
    )
    rejected(residue, original, phase13_artifacts, "cylinder compatibility")

    conditional = phase13_artifacts / "phase13_conditional_pressure.json"
    original = mutate(
        conditional,
        lambda d: d["P80"]["endpoint_factor"].__setitem__("numerator", "1"),
    )
    rejected(conditional, original, phase13_artifacts, "endpoint pressure factor")
    original = mutate(conditional, lambda d: d["H72"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(conditional, original, phase13_artifacts, "H72")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase13.py").read_text(encoding="utf-8")
    assert "phase13_search" not in source
    assert "from src" not in source
    assert "import src" not in source
