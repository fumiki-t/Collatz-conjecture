import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase24.py"
FILES = [
    "phase24_theory.json",
    "phase24_area_two_remainder.json",
    "phase24_area_three_diagnostic.json",
    "phase24_regressions.json",
    "phase24_obstruction_report.md",
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


def test_phase24_verifier_accepts_generated_artifacts(tmp_path: Path) -> None:
    result = run_verifier(copied_artifacts(tmp_path))
    assert result.returncode == 0, result.stderr
    assert '"valid": true' in result.stdout
    assert '"generator_imported": false' in result.stdout
    assert '"proves_collatz": false' in result.stdout


def test_phase24_verifier_rejects_tampered_finite_count(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase24_area_two_remainder.json"
    value = json.loads(path.read_text())
    value["critical_profile_count"] += 1
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "finite declared counts" in result.stderr


def test_phase24_verifier_rejects_weakened_strict_inequality(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase24_theory.json"
    value = json.loads(path.read_text())
    value["critical_area_two"]["five_step_ratio"]["strict"] = False
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "critical induction ratio" in result.stderr


def test_phase24_verifier_rejects_tampered_area_three_count(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase24_area_three_diagnostic.json"
    value = json.loads(path.read_text())
    value["valid_profile_count"] -= 1
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "area-three declared count" in result.stderr


def test_phase24_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase24_theory.json"
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "Collatz boundary" in result.stderr


def test_phase24_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text()
    assert "from src" not in source
    assert "import src" not in source
    assert "phase24_search" not in source
