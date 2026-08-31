from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VERIFIER = ROOT / "verifier" / "verify_phase29.py"
FILES = (
    "phase29_theory.json",
    "phase29_arc_audit.json",
    "phase29_coprime_corpus.json",
    "phase29_state_bounds.json",
    "phase29_farey_certificates.json",
    "phase29_regressions.json",
    "phase29_obstruction_report.md",
)


def copy_artifacts(destination: Path) -> None:
    destination.mkdir()
    for name in FILES:
        shutil.copy2(ARTIFACTS / name, destination / name)


def run_verifier(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VERIFIER), "--artifact-dir", str(directory)],
        check=False,
        capture_output=True,
        text=True,
    )


def mutate_json(path: Path, callback) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    callback(value)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_phase29_verifier_accepts_clean_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "clean"
    copy_artifacts(destination)
    result = run_verifier(destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_phase29_verifier_rejects_arc_digest_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "arc"
    copy_artifacts(destination)
    mutate_json(destination / "phase29_arc_audit.json", lambda value: value.update(tie_row_digest_sha256="0" * 64))
    assert run_verifier(destination).returncode != 0


def test_phase29_verifier_rejects_farey_margin_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "farey"
    copy_artifacts(destination)
    mutate_json(destination / "phase29_farey_certificates.json", lambda value: value["rows"][0].update(upper_margin=["0", "1"]))
    assert run_verifier(destination).returncode != 0


def test_phase29_verifier_rejects_conditional_promotion(tmp_path: Path) -> None:
    destination = tmp_path / "promotion"
    copy_artifacts(destination)
    mutate_json(destination / "phase29_theory.json", lambda value: value["claims"]["P178"].update(status="VERIFIED_THEOREM"))
    assert run_verifier(destination).returncode != 0


def test_phase29_verifier_rejects_external_dependency_removal(tmp_path: Path) -> None:
    destination = tmp_path / "dependency"
    copy_artifacts(destination)
    mutate_json(destination / "phase29_theory.json", lambda value: value["dependencies"].update(P175=["P150", "P173", "P174"]))
    assert run_verifier(destination).returncode != 0


def test_phase29_verifier_rejects_endpoint_control_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "endpoint"
    copy_artifacts(destination)
    mutate_json(destination / "phase29_regressions.json", lambda value: value["named_controls"]["NG38"].update(endpoint_correction=0))
    assert run_verifier(destination).returncode != 0


def test_phase29_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "overclaim"
    copy_artifacts(destination)
    mutate_json(destination / "phase29_theory.json", lambda value: value.update(proves_collatz=True))
    assert run_verifier(destination).returncode != 0


def test_phase29_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "phase29_search" not in source
    assert "from src" not in source
    assert "import src" not in source
