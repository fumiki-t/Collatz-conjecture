from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase38.py"
NAMES = (
    "phase38_capacity_certificate.json",
    "phase38_renewal_transfer.json",
    "phase38_regressions.json",
    "phase38_obstruction_report.md",
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


def test_independent_verifier_accepts_phase38_artifacts() -> None:
    completed = run(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["capacity_rows"] == 501
    assert result["private_digest_match"] is False
    assert result["renewal_counts"] == {
        "address_count": 423,
        "codeword_count": 154,
        "nonzero_transfer_count": 717,
        "transition_count": 817,
    }
    assert result["proves_collatz"] is False


def test_verifier_rejects_capacity_row_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase38_capacity_certificate.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["rows"][49][2] = str(int(value["rows"][49][2]) + 1)
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "capacity artifact mismatch" in completed.stdout


def test_verifier_rejects_reciprocal_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase38_capacity_certificate.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["reciprocal_certificate"]["combined_bound"]["numerator"] = "2080"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "capacity artifact mismatch" in completed.stdout


def test_verifier_rejects_renewal_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase38_renewal_transfer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["finite_audit"]["valuation_digest_sha256"] = "0" * 64
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "renewal artifact mismatch" in completed.stdout


def test_verifier_rejects_regression_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase38_regressions.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["mandatory_families"].remove("A^rB^s")
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "regression artifact mismatch" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase38_renewal_transfer.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["proves_collatz"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "renewal artifact mismatch" in completed.stdout


def test_verifier_rejects_obstruction_report_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase38_obstruction_report.md"
    path.write_text(
        path.read_text(encoding="utf-8").replace("does not prove P80", "proves P80"),
        encoding="utf-8",
    )
    completed = run(target)
    assert completed.returncode != 0
    assert "obstruction report mismatch" in completed.stdout
