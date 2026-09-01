from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase31_short_leaf.py"
NAMES = (
    "phase31_short_leaf_theory.json",
    "phase31_short_leaf_corpus.json",
    "phase31_short_leaf_regressions.json",
    "phase31_short_leaf_obstruction_report.md",
)


def copied_artifacts(tmp_path: Path) -> Path:
    target = tmp_path / "artifacts"
    target.mkdir()
    for name in NAMES:
        shutil.copy2(ROOT / "artifacts" / name, target / name)
    return target


def run_verifier(artifact_dir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), "--artifact-dir", str(artifact_dir)],
        check=False,
        capture_output=True,
        text=True,
    )


def test_independent_verifier_accepts_repository_artifacts() -> None:
    completed = run_verifier(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["corpus_counts"]["minimum_rotations"] == 10_485
    assert result["corpus_counts"]["width_pruning_cases"] == 522_870
    assert result["proves_collatz"] is False


def test_verifier_rejects_tampered_theory(tmp_path: Path) -> None:
    target = copied_artifacts(tmp_path)
    path = target / "phase31_short_leaf_theory.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["P191"]["residual_bound"] = "E_R<=h"
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_verifier(target)
    assert completed.returncode != 0
    assert "theory artifact mismatch" in completed.stdout


def test_verifier_rejects_tampered_corpus(tmp_path: Path) -> None:
    target = copied_artifacts(tmp_path)
    path = target / "phase31_short_leaf_corpus.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["counts"]["minimum_rotations"] -= 1
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_verifier(target)
    assert completed.returncode != 0
    assert "corpus declaration" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied_artifacts(tmp_path)
    path = target / "phase31_short_leaf_regressions.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["proves_collatz"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_verifier(target)
    assert completed.returncode != 0
    assert "regression boundary" in completed.stdout
