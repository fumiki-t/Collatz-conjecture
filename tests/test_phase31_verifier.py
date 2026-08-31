from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VERIFIER = ROOT / "verifier" / "verify_phase31.py"
FILES = (
    "phase31_theory.json",
    "phase31_transport_corpus.json",
    "phase31_scalar_certificates.json",
    "phase31_synthetic_profiles.json",
    "phase31_regressions.json",
    "phase31_obstruction_report.md",
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


def test_phase31_verifier_accepts_clean_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "clean"
    copy_artifacts(destination)
    result = run_verifier(destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_phase31_verifier_rejects_corpus_digest_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "corpus"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_transport_corpus.json", lambda value: value.update(row_digest_sha256="0" * 64))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_rejects_static_count_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "static"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_transport_corpus.json", lambda value: value["counts"].update(extracted_swaps=1279))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_rejects_constant_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "constant"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_scalar_certificates.json", lambda value: value.update(noncritical_constant_cube=["53", "1"]))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_rejects_external_dependency_removal(tmp_path: Path) -> None:
    destination = tmp_path / "dependency"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_theory.json", lambda value: value["dependencies"].update(P188=["P163", "P164", "P187"]))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_rejects_global_grid_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "grid"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_theory.json", lambda value: value.update(proposal_repair="Equality forces global shift invariance."))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_rejects_ng40_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "ng40"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_regressions.json", lambda value: value["NG40_normalized_countermodel"].update(k=1))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "overclaim"
    copy_artifacts(destination)
    mutate_json(destination / "phase31_theory.json", lambda value: value.update(proves_collatz=True))
    assert run_verifier(destination).returncode != 0


def test_phase31_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "phase31_search" not in source
    assert "from src" not in source
    assert "import src" not in source
