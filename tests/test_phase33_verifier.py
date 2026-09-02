from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase33.py"
NAMES = (
    "phase33_theory.json", "phase33_scalar_audit.json", "phase33_descent_summary.json",
    "phase33_descent_certificate.csv", "phase33_regressions.json", "phase33_obstruction_report.md",
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


def test_independent_verifier_accepts_phase33_artifacts() -> None:
    completed = run(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["frontier_counts"] == [461, 915]
    assert result["descent"]["odd_sources"] == 141_780
    assert result["proves_collatz"] is False


def test_verifier_rejects_scalar_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase33_scalar_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["tiers"][1]["frontier"]["candidate_count"] -= 1
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "frontier reconstruction" in completed.stdout


def test_verifier_rejects_descent_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase33_descent_certificate.csv"
    lines = path.read_text(encoding="ascii").splitlines()
    source, steps, lower = lines[1].split(",")
    lines[1] = f"{source},{int(steps) + 1},{lower}"
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    completed = run(target)
    assert completed.returncode != 0
    assert "trajectory reconstruction" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase33_theory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["proves_collatz"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "theory artifact mismatch" in completed.stdout
