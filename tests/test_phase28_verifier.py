from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VERIFIER = ROOT / "verifier" / "verify_phase28.py"
FILES = (
    "phase28_theory.json",
    "phase28_transport_corpus.json",
    "phase28_scalar_certificates.json",
    "phase28_synthetic_profiles.json",
    "phase28_regressions.json",
    "phase28_obstruction_report.md",
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


def test_phase28_verifier_accepts_clean_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "clean"
    copy_artifacts(destination)
    result = run_verifier(destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_phase28_verifier_rejects_corpus_digest_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "corpus"
    copy_artifacts(destination)
    mutate_json(destination / "phase28_transport_corpus.json", lambda value: value.update(row_digest_sha256="0" * 64))
    assert run_verifier(destination).returncode != 0


def test_phase28_verifier_rejects_critical_constant_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "constant"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase28_scalar_certificates.json",
        lambda value: value.update(critical_constant_cube_interval=[["1", "1"], ["2", "1"]]),
    )
    assert run_verifier(destination).returncode != 0


def test_phase28_verifier_rejects_external_dependency_removal(tmp_path: Path) -> None:
    destination = tmp_path / "dependency"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase28_theory.json",
        lambda value: value["dependencies"].update(P169=["P163", "P164", "P168"]),
    )
    assert run_verifier(destination).returncode != 0


def test_phase28_verifier_rejects_endpoint_correction_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "endpoint"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase28_regressions.json",
        lambda value: value["endpoint_l1_obstruction"].update(corrected_bound=3),
    )
    assert run_verifier(destination).returncode != 0


def test_phase28_verifier_rejects_strictness_obstruction_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "strictness"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase28_regressions.json",
        lambda value: value["finite_strictness_obstruction"].update(area=2),
    )
    assert run_verifier(destination).returncode != 0


def test_phase28_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "overclaim"
    copy_artifacts(destination)
    mutate_json(destination / "phase28_theory.json", lambda value: value.update(proves_collatz=True))
    assert run_verifier(destination).returncode != 0


def test_phase28_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "phase28_search" not in source
    assert "from src" not in source
    assert "import src" not in source
