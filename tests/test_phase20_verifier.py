import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase20.py"
FILES = [
    "phase20_theory.json",
    "phase20_complexity_audit.json",
    "phase20_literature_audit.json",
    "phase20_adversarial.json",
    "phase20_obstruction_report.md",
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


def test_phase20_verifier_accepts_generated_artifacts(tmp_path: Path) -> None:
    result = run_verifier(copied_artifacts(tmp_path))
    assert result.returncode == 0, result.stderr
    assert '"valid": true' in result.stdout


def test_phase20_verifier_rejects_tampered_complexity(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase20_complexity_audit.json"
    value = json.loads(path.read_text())
    value["sequences"][0]["factor_metrics"][0]["factor_complexity"] += 1
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "finite complexity" in result.stderr


def test_phase20_verifier_rejects_tampered_liminf(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase20_literature_audit.json"
    value = json.loads(path.read_text())
    value["sources"][0]["audited_result"] = value["sources"][0]["audited_result"].replace("liminf", "limit")
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "López-Stoll" in result.stderr


def test_phase20_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    directory = copied_artifacts(tmp_path)
    path = directory / "phase20_theory.json"
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    result = run_verifier(directory)
    assert result.returncode != 0
    assert "Collatz boundary" in result.stderr


def test_phase20_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text()
    assert "from src" not in source
    assert "import src" not in source
    assert "src.phase20_search" not in source
