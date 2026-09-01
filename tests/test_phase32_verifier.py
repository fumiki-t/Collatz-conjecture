from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase32.py"
NAMES = (
    "phase32_theory.json",
    "phase32_triple_hit_corpus.json",
    "phase32_cofactor_corpus.json",
    "phase32_scalar_certificates.json",
    "phase32_regressions.json",
    "phase32_obstruction_report.md",
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
    assert result["triple_counts"]["capacity_checks"] == 522_870
    assert result["cofactor_counts"]["positive_arc_certificates"] == 2_936
    assert result["proves_collatz"] is False


def test_verifier_rejects_tampered_theory(tmp_path: Path) -> None:
    target = copied_artifacts(tmp_path)
    path = target / "phase32_theory.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["claims"]["H200"] = "VERIFIED_THEOREM"
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_verifier(target)
    assert completed.returncode != 0
    assert "theory artifact mismatch" in completed.stdout


def test_verifier_rejects_tampered_corpus(tmp_path: Path) -> None:
    target = copied_artifacts(tmp_path)
    path = target / "phase32_triple_hit_corpus.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["counts"]["capacity_checks"] -= 1
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_verifier(target)
    assert completed.returncode != 0
    assert "triple declaration" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied_artifacts(tmp_path)
    path = target / "phase32_regressions.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["proves_collatz"] = True
    path.write_text(json.dumps(payload), encoding="utf-8")
    completed = run_verifier(target)
    assert completed.returncode != 0
    assert "regression boundary" in completed.stdout
