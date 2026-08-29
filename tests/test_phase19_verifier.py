from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase19_search import generate
from verifier.verify_phase19 import (
    verify,
    verify_adversarial,
    verify_periodic,
    verify_report,
    verify_source_lifts,
    verify_stopped,
    verify_theory,
)


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> str:
    original = path.read_text(encoding="utf-8")
    value = json.loads(original)
    change(value)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return original


def rejected(
    path: Path,
    original: str,
    check: Callable[[], None],
    message: str,
) -> None:
    try:
        with pytest.raises(ValueError, match=message):
            check()
    finally:
        path.write_text(original, encoding="utf-8")


@pytest.fixture(scope="module")
def phase19_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase19")
    generate(root)
    return root


def test_independent_verifier_accepts(phase19_artifacts: Path) -> None:
    result = verify(phase19_artifacts)
    assert result["valid"] is True
    assert result["claims"]["P112"] == result["claims"]["P116"] == "VERIFIED_THEOREM"
    assert result["claims"]["E31"] == "VERIFIED_FINITE"
    assert result["claims"]["NG31"] == "REFUTED"
    assert result["claims"]["H112"] == result["claims"]["H72"] == "OPEN"
    assert result["proves_collatz"] is False


def test_cli_reports_boundaries_without_repeating_full_reconstruction(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    expected = {
        "format": "collatz-phase19-verifier-v1",
        "valid": True,
        "claims": {"H72": "OPEN"},
        "proves_collatz": False,
    }
    monkeypatch.setattr("verifier.verify_phase19.verify", lambda _: expected)
    monkeypatch.setattr(sys, "argv", ["verify_phase19.py", "--artifact-dir", str(tmp_path)])
    from verifier.verify_phase19 import main

    assert main() == 0
    assert json.loads(capsys.readouterr().out) == expected


def test_tamper_rejection_for_theory_and_stopping(phase19_artifacts: Path) -> None:
    theory = phase19_artifacts / "phase19_theory.json"
    original = mutate(theory, lambda value: value["claims"].__setitem__("H112", "VERIFIED_THEOREM"))
    rejected(theory, original, lambda: verify_theory(phase19_artifacts), "theory claim boundary")

    stopped = phase19_artifacts / "phase19_stopped_duality.json"
    original = mutate(stopped, lambda value: value["rows"][0].__setitem__("plus_total_mass", {"numerator": "0", "denominator": "1"}))
    rejected(stopped, original, lambda: verify_stopped(phase19_artifacts), "stopped tree reconstruction")


def test_tamper_rejection_for_source_and_periodic_lifts(phase19_artifacts: Path) -> None:
    sources = phase19_artifacts / "phase19_source_lifts.json"
    original = mutate(sources, lambda value: value["source_167_falsifier"].__setitem__("trailing_zero_lifts", 12))
    rejected(sources, original, lambda: verify_source_lifts(phase19_artifacts), "source lift reconstruction")

    periodic = phase19_artifacts / "phase19_periodic_lifts.json"
    original = mutate(periodic, lambda value: value["rows"][0]["residues"][0].__setitem__("source_residue", 0))
    rejected(periodic, original, lambda: verify_periodic(phase19_artifacts), "periodic lift reconstruction")


def test_tamper_rejection_for_adversarial_and_report(phase19_artifacts: Path) -> None:
    adversarial = phase19_artifacts / "phase19_adversarial.json"
    original = mutate(adversarial, lambda value: value.__setitem__("row_digest_sha256", "0" * 64))
    rejected(adversarial, original, lambda: verify_adversarial(phase19_artifacts), "adversarial reconstruction")

    report = phase19_artifacts / "phase19_obstruction_report.md"
    original_text = report.read_text(encoding="utf-8")
    try:
        report.write_text(original_text.replace("(`REFUTED`)", "(`VERIFIED_THEOREM`)", 1), encoding="utf-8")
        with pytest.raises(ValueError, match="obstruction report boundary"):
            verify_report(phase19_artifacts)
    finally:
        report.write_text(original_text, encoding="utf-8")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase19.py").read_text(encoding="utf-8")
    assert "phase19_search" not in source
    assert "from src" not in source
    assert "import src" not in source
