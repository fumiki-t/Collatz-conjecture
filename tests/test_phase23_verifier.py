import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase23.py"
FILES = [
    "phase23_theory.json",
    "phase23_critical_words.json",
    "phase23_cycle_profiles.json",
    "phase23_regressions.json",
    "phase23_obstruction_report.md",
]


def copied_artifacts(tmp_path: Path) -> Path:
    destination = tmp_path / "artifacts"
    destination.mkdir()
    for name in FILES:
        shutil.copy2(ROOT / "artifacts" / name, destination / name)
    return destination


def run_verifier(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), "--artifact-dir", str(directory)],
        text=True,
        capture_output=True,
        check=False,
    )


def test_phase23_verifier_accepts_generated_artifacts(tmp_path: Path) -> None:
    result = run_verifier(copied_artifacts(tmp_path))
    assert result.returncode == 0, result.stderr
    assert '"valid": true' in result.stdout
    assert '"proves_collatz": false' in result.stdout


def test_phase23_verifier_rejects_tampered_area_count(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase23_critical_words.json"
    value = json.loads(path.read_text())
    value["totals"]["area_rejected"] += 1
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "critical reconstruction mismatch" in result.stderr


def test_phase23_verifier_rejects_tampered_cycle_digest(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase23_cycle_profiles.json"
    value = json.loads(path.read_text())
    value["profile_digest_sha256"] = "0" * 64
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "cycle reconstruction mismatch" in result.stderr


def test_phase23_verifier_rejects_removed_counterexample_status(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase23_theory.json"
    value = json.loads(path.read_text())
    value["claims"]["NG32"] = "OPEN"
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "theory claim boundary" in result.stderr


def test_phase23_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase23_theory.json"
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "Collatz boundary" in result.stderr


def test_phase23_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text()
    assert "from src" not in source
    assert "import src" not in source
    assert "phase23_search" not in source
