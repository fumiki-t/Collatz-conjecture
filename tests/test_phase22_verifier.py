import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase22.py"
FILES = [
    "phase22_theory.json",
    "phase22_finite_profiles.json",
    "phase22_regressions.json",
    "phase22_literature_audit.json",
    "phase22_obstruction_report.md",
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


def test_phase22_verifier_accepts_generated_artifacts(tmp_path: Path) -> None:
    result = run_verifier(copied_artifacts(tmp_path))
    assert result.returncode == 0, result.stderr
    assert '"valid": true' in result.stdout
    assert '"proves_collatz": false' in result.stdout


def test_phase22_verifier_rejects_tampered_resultant(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase22_finite_profiles.json"
    value = json.loads(path.read_text())
    value["resultant_samples"][0][5] += 1
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "Sylvester resultants" in result.stderr


def test_phase22_verifier_rejects_tampered_negative_cycle(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase22_regressions.json"
    value = json.loads(path.read_text())
    value["named_cycle_words"][2]["integral_source"] = -19
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "regression arithmetic" in result.stderr


def test_phase22_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase22_theory.json"
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "Collatz boundary" in result.stderr


def test_phase22_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text()
    assert "from src" not in source
    assert "import src" not in source
    assert "phase22_search" not in source
