from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase37.py"
NAMES = (
    "phase37_theory.json",
    "phase37_induction_certificate.json",
    "phase37_affine_interval_audit.json",
    "phase37_renewal_audit.json",
    "phase37_regressions.json",
    "phase37_obstruction_report.md",
)


def copied(tmp_path: Path) -> Path:
    target = tmp_path / "artifacts"
    target.mkdir()
    for name in NAMES:
        shutil.copy2(ROOT / "artifacts" / name, target / name)
    return target


def run(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), "--artifact-dir", str(directory)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_independent_verifier_accepts_phase37_artifacts() -> None:
    completed = run(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["explicit_constant"] == 32
    assert result["induction_N0"] == 135
    assert result["affine_counts"]["words"] == 131_070
    assert result["renewal_counts"]["product_checks"] == 209_868
    assert result["proves_collatz"] is False


def test_verifier_rejects_induction_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase37_induction_certificate.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["rational_parameters"]["N0"] = 134
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "induction parameters" in completed.stdout


def test_verifier_rejects_affine_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase37_affine_interval_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["counts"]["words"] += 1
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "affine interval artifact mismatch" in completed.stdout


def test_verifier_rejects_renewal_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase37_renewal_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["orbit_digest_sha256"] = "0" * 64
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "renewal artifact mismatch" in completed.stdout


def test_verifier_rejects_regression_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase37_regressions.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["mandatory_families"].remove("A^rB^s")
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "regression artifact mismatch" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase37_theory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["proves_collatz"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "theory overclaim" in completed.stdout


def test_verifier_rejects_boundary_report_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase37_obstruction_report.md"
    path.write_text(path.read_text(encoding="utf-8").replace("does not prove H72", "proves H72"), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "obstruction report boundary" in completed.stdout
