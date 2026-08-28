from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase15b_search import generate
from verifier.verify_phase15b import verify


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
def phase15b_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    root = tmp_path_factory.mktemp("phase15b")
    generate(root, source_bound=10_000, frontier_maximum_q=8, compression_maximum_q=10)
    return root


def test_independent_verifier_accepts_and_cli_reports_boundaries(phase15b_artifacts: Path) -> None:
    completed = subprocess.run(
        [sys.executable, "verifier/verify_phase15b.py", "--artifact-dir", str(phase15b_artifacts)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["P89"] == result["P96"] == "VERIFIED_THEOREM"
    assert result["P90"] == "CONDITIONAL"
    assert result["H89"] == "OPEN"
    assert result["NG27"] == "REFUTED"
    assert result["proves_collatz"] is False


def test_tamper_rejection_for_theory_ancestral_and_frontier(phase15b_artifacts: Path) -> None:
    theory = phase15b_artifacts / "phase15b_theory.json"
    original = mutate(theory, lambda value: value["cross_Q_example"]["d"].__setitem__("B", 698))
    rejected(theory, original, phase15b_artifacts, "theory")

    ancestral = phase15b_artifacts / "phase15b_ancestral_scan.json"
    original = mutate(ancestral, lambda value: value.__setitem__("source_depth_digest_sha256", "0" * 64))
    rejected(ancestral, original, phase15b_artifacts, "ancestral")

    frontier = phase15b_artifacts / "phase15b_frontier.json"
    original = mutate(frontier, lambda value: value["counts_by_target_Q"]["6"].__setitem__("same_Q_uniform_dominated", 999))
    rejected(frontier, original, phase15b_artifacts, "frontier")


def test_tamper_rejection_for_renewal_compression_and_adversarial(phase15b_artifacts: Path) -> None:
    renewal = phase15b_artifacts / "phase15b_renewal_trie.json"
    original = mutate(renewal, lambda value: value["new_primitive_cylinders_by_Q"].__setitem__("7", 9))
    rejected(renewal, original, phase15b_artifacts, "renewal")

    compression = phase15b_artifacts / "phase15b_compression.json"
    original = mutate(compression, lambda value: value["maximum_layer_witness"].__setitem__("gain", 4))
    rejected(compression, original, phase15b_artifacts, "compression")

    adversarial = phase15b_artifacts / "phase15b_adversarial.json"
    original = mutate(adversarial, lambda value: value.__setitem__("row_digest_sha256", "f" * 64))
    rejected(adversarial, original, phase15b_artifacts, "adversarial")


def test_tamper_rejection_for_obstruction_report(phase15b_artifacts: Path) -> None:
    path = phase15b_artifacts / "phase15b_obstruction_report.md"
    original = path.read_text(encoding="utf-8")
    try:
        path.write_text(original.replace("does not\nprove", "does\nprove", 1), encoding="utf-8")
        with pytest.raises(ValueError, match="obstruction"):
            verify(phase15b_artifacts)
    finally:
        path.write_text(original, encoding="utf-8")


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_phase15b.py").read_text(encoding="utf-8")
    assert "phase15b_search" not in source
    assert "from src" not in source
    assert "import src" not in source
