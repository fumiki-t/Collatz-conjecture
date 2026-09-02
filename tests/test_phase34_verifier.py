from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase34.py"
NAMES = (
    "phase34_theory.json", "phase34_scalar_audit.json", "phase34_profile_bridge.json",
    "phase34_defect_peeling.json", "phase34_regressions.json", "phase34_obstruction_report.md",
)


def copied(tmp_path: Path) -> Path:
    target = tmp_path / "artifacts"
    target.mkdir()
    for name in NAMES:
        shutil.copy2(ROOT / "artifacts" / name, target / name)
    return target


def run(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(VERIFIER), "--artifact-dir", str(directory)],
                          text=True, capture_output=True, check=False)


def test_independent_verifier_accepts_phase34_artifacts() -> None:
    completed = run(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["frontier_candidates"] == 1725
    assert result["low_q_rows"] == 7221
    assert result["proves_collatz"] is False


def test_verifier_rejects_scalar_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase34_scalar_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["frontier"]["candidate_count"] -= 1
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "frontier reconstruction" in completed.stdout


def test_verifier_rejects_defect_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase34_defect_peeling.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["samples"][0][-2] += 1
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "defect reconstruction" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase34_theory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["proves_collatz"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "theory artifact mismatch" in completed.stdout
