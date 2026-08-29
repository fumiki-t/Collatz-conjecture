from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase18_search import generate
from verifier.verify_phase18 import verify


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
def phase18_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase18")
    generate(root)
    return root


def test_independent_verifier_accepts_and_cli_reports_boundaries(phase18_artifacts: Path) -> None:
    result = verify(phase18_artifacts)
    assert result["valid"] is True
    assert result["claims"]["P107"] == result["claims"]["P108"] == "VERIFIED_THEOREM"
    assert result["claims"]["P110"] == "CONDITIONAL"
    assert result["claims"]["E30"] == "VERIFIED_FINITE"
    assert result["claims"]["NG30"] == "REFUTED"
    assert result["claims"]["H72"] == "OPEN"
    assert result["proves_collatz"] is False

    completed = subprocess.run(
        [sys.executable, "verifier/verify_phase18.py", "--artifact-dir", str(phase18_artifacts)],
        check=False, capture_output=True, text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert json.loads(completed.stdout)["valid"] is True


def test_tamper_rejection_for_theory_and_graph(phase18_artifacts: Path) -> None:
    theory = phase18_artifacts / "phase18_theory.json"
    original = mutate(theory, lambda value: value["claims"].__setitem__("P110", "VERIFIED_THEOREM"))
    rejected(theory, original, phase18_artifacts, "theory claim")

    graph = phase18_artifacts / "phase18_graph_audit.json"
    original = mutate(graph, lambda value: value.__setitem__("row_digest_sha256", "0" * 64))
    rejected(graph, original, phase18_artifacts, "graph audit digest")


def test_tamper_rejection_for_mixed_project_and_adversarial(phase18_artifacts: Path) -> None:
    mixed = phase18_artifacts / "phase18_mixed_schedule.json"
    original = mutate(mixed, lambda value: value["final"].__setitem__("source_residue", 0))
    rejected(mixed, original, phase18_artifacts, "mixed schedule")

    projects = phase18_artifacts / "phase18_project_models.json"
    original = mutate(projects, lambda value: value["source_file_sha256"].__setitem__("artifacts/phase7_macro12.json", "f" * 64))
    rejected(projects, original, phase18_artifacts, "project model source")

    adversarial = phase18_artifacts / "phase18_adversarial.json"
    original = mutate(adversarial, lambda value: value.__setitem__("row_digest_sha256", "0" * 64))
    rejected(adversarial, original, phase18_artifacts, "adversarial digest")


def test_tamper_rejection_for_obstruction_report(phase18_artifacts: Path) -> None:
    path = phase18_artifacts / "phase18_obstruction_report.md"
    original = path.read_text(encoding="utf-8")
    try:
        path.write_text(original.replace("(`REFUTED`)", "(`VERIFIED_THEOREM`)", 1), encoding="utf-8")
        with pytest.raises(ValueError, match="obstruction report"):
            verify(phase18_artifacts)
    finally:
        path.write_text(original, encoding="utf-8")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase18.py").read_text(encoding="utf-8")
    assert "phase18_search" not in source
    assert "from src" not in source
    assert "import src" not in source
