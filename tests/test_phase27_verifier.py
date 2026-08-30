from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VERIFIER = ROOT / "verifier" / "verify_phase27.py"
FILES = (
    "phase27_theory.json",
    "phase27_cycle_corpus.json",
    "phase27_envelopes.json",
    "phase27_synthetic_profiles.json",
    "phase27_regressions.json",
    "phase27_obstruction_report.md",
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


def test_phase27_verifier_accepts_clean_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "clean"
    copy_artifacts(destination)
    result = run_verifier(destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_phase27_verifier_rejects_corpus_digest_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "corpus"
    copy_artifacts(destination)
    mutate_json(destination / "phase27_cycle_corpus.json", lambda value: value.update(row_digest_sha256="0" * 64))
    assert run_verifier(destination).returncode != 0


def test_phase27_verifier_rejects_matveev_constant_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "constant"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase27_envelopes.json",
        lambda value: value["matveev_specialization"].update(integer_majorant_K=1),
    )
    assert run_verifier(destination).returncode != 0


def test_phase27_verifier_rejects_external_input_promotion(tmp_path: Path) -> None:
    destination = tmp_path / "claim"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase27_theory.json",
        lambda value: value["claims"]["EXT17"].update(status="VERIFIED_THEOREM"),
    )
    assert run_verifier(destination).returncode != 0


def test_phase27_verifier_rejects_rotation_obstruction_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "rotation"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase27_regressions.json",
        lambda value: value["rotation_alignment_obstruction"].update(least_value_offsets=[1]),
    )
    assert run_verifier(destination).returncode != 0


def test_phase27_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "overclaim"
    copy_artifacts(destination)
    mutate_json(destination / "phase27_theory.json", lambda value: value.update(proves_collatz=True))
    assert run_verifier(destination).returncode != 0


def test_phase27_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "phase27_search" not in source
    assert "from src" not in source
    assert "import src" not in source
