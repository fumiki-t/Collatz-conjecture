from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VERIFIER = ROOT / "verifier" / "verify_phase30.py"
FILES = (
    "phase30_theory.json",
    "phase30_transport_corpus.json",
    "phase30_scalar_certificates.json",
    "phase30_synthetic_profiles.json",
    "phase30_regressions.json",
    "phase30_obstruction_report.md",
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


def test_phase30_verifier_accepts_clean_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "clean"
    copy_artifacts(destination)
    result = run_verifier(destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_phase30_verifier_rejects_corpus_digest_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "corpus"
    copy_artifacts(destination)
    mutate_json(destination / "phase30_transport_corpus.json", lambda value: value.update(row_digest_sha256="0" * 64))
    assert run_verifier(destination).returncode != 0


def test_phase30_verifier_rejects_constant_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "constant"
    copy_artifacts(destination)
    mutate_json(destination / "phase30_scalar_certificates.json", lambda value: value.update(noncritical_constant_cube=["27", "8"]))
    assert run_verifier(destination).returncode != 0


def test_phase30_verifier_rejects_external_dependency_removal(tmp_path: Path) -> None:
    destination = tmp_path / "dependency"
    copy_artifacts(destination)
    mutate_json(destination / "phase30_theory.json", lambda value: value["dependencies"].update(P182=["P163", "P164", "P181"]))
    assert run_verifier(destination).returncode != 0


def test_phase30_verifier_rejects_state_saturation_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "repair"
    copy_artifacts(destination)
    mutate_json(destination / "phase30_theory.json", lambda value: value.update(proposal_repair="The actual maximum state is asymptotically saturated."))
    assert run_verifier(destination).returncode != 0


def test_phase30_verifier_rejects_ng39_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "ng39"
    copy_artifacts(destination)
    mutate_json(destination / "phase30_regressions.json", lambda value: value["no_span_counterexample"].update(overstrong_bound=10))
    assert run_verifier(destination).returncode != 0


def test_phase30_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "overclaim"
    copy_artifacts(destination)
    mutate_json(destination / "phase30_theory.json", lambda value: value.update(proves_collatz=True))
    assert run_verifier(destination).returncode != 0


def test_phase30_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "phase30_search" not in source
    assert "from src" not in source
    assert "import src" not in source
