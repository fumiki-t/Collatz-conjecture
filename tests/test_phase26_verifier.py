from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
VERIFIER = ROOT / "verifier" / "verify_phase26.py"
FILES = (
    "phase26_theory.json",
    "phase26_reduced_profiles.json",
    "phase26_scalar_certificates.json",
    "phase26_regressions.json",
    "phase26_obstruction_report.md",
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


def test_phase26_verifier_accepts_clean_artifacts(tmp_path: Path) -> None:
    destination = tmp_path / "clean"
    copy_artifacts(destination)
    result = run_verifier(destination)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["valid"] is True


def test_phase26_verifier_rejects_profile_digest_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "profile"
    copy_artifacts(destination)
    mutate_json(destination / "phase26_reduced_profiles.json", lambda value: value.update(row_digest_sha256="0" * 64))
    assert run_verifier(destination).returncode != 0


def test_phase26_verifier_rejects_scalar_margin_tamper(tmp_path: Path) -> None:
    destination = tmp_path / "scalar"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase26_scalar_certificates.json",
        lambda value: value["noncritical"]["internal_area"]["endpoint"].update(positive_margin=False),
    )
    assert run_verifier(destination).returncode != 0


def test_phase26_verifier_rejects_conditional_promotion(tmp_path: Path) -> None:
    destination = tmp_path / "claim"
    copy_artifacts(destination)
    mutate_json(
        destination / "phase26_theory.json",
        lambda value: value["claims"]["P160"].update(status="VERIFIED_THEOREM"),
    )
    assert run_verifier(destination).returncode != 0


def test_phase26_verifier_rejects_collatz_overclaim(tmp_path: Path) -> None:
    destination = tmp_path / "overclaim"
    copy_artifacts(destination)
    mutate_json(destination / "phase26_theory.json", lambda value: value.update(proves_collatz=True))
    assert run_verifier(destination).returncode != 0


def test_phase26_verifier_does_not_import_generator() -> None:
    source = VERIFIER.read_text(encoding="utf-8")
    assert "phase26_search" not in source
    assert "from src" not in source
    assert "import src" not in source
