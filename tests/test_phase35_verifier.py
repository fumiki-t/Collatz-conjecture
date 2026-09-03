from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase35.py"
NAMES = (
    "phase35_theory.json", "phase35_decoder_audit.json",
    "phase35_joint_scalar_audit.json", "phase35_regressions.json",
    "phase35_obstruction_report.md",
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


def test_independent_verifier_accepts_phase35_artifacts() -> None:
    completed = run(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["decoded_words"] == 1_166_058
    assert result["area228_frontier_candidates"] == 1912
    assert result["proves_collatz"] is False


def test_verifier_rejects_decoder_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase35_decoder_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["format"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "decoder boundary mismatch" in completed.stdout


def test_verifier_rejects_scalar_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase35_joint_scalar_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["format"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "scalar boundary mismatch" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase35_theory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["proves_collatz"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "theory artifact mismatch" in completed.stdout
