import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase25.py"
FILES = [
    "phase25_theory.json",
    "phase25_critical_support.json",
    "phase25_cycle_support.json",
    "phase25_resonance.json",
    "phase25_regressions.json",
    "phase25_obstruction_report.md",
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


def test_phase25_verifier_accepts_generated_artifacts(tmp_path: Path) -> None:
    result = run_verifier(copied_artifacts(tmp_path))
    assert result.returncode == 0, result.stderr
    assert '"valid": true' in result.stdout
    assert '"generator_imported": false' in result.stdout
    assert '"proves_collatz": false' in result.stdout


def test_phase25_verifier_rejects_tampered_claim_status(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase25_theory.json"
    value = json.loads(path.read_text())
    value["claims"]["P152"]["status"] = "VERIFIED_THEOREM"
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "theory claims" in result.stderr


def test_phase25_verifier_rejects_tampered_q0_width(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase25_theory.json"
    value = json.loads(path.read_text())
    value["critical_support"]["q0_certificate"]["integer_width_n_q0"] = 72
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "q0 width" in result.stderr


def test_phase25_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase25_theory.json"
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "theory metadata" in result.stderr


def test_phase25_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text()
    assert "from src" not in source
    assert "import src" not in source
    assert "phase25_search" not in source
