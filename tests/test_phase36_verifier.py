from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase36.py"
NAMES = (
    "phase36_theory.json", "phase36_root_corpus.json",
    "phase36_event_polynomial.json", "phase36_scalar_audit.json",
    "phase36_decoder_roots.json", "phase36_regressions.json",
    "phase36_obstruction_report.md",
)


def copied(tmp_path: Path) -> Path:
    target = tmp_path / "artifacts"
    target.mkdir()
    for name in NAMES:
        shutil.copy2(ROOT / "artifacts" / name, target / name)
    return target


def run(directory: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(VERIFIER), "--artifact-dir", str(directory)],
                          text=True, capture_output=True, check=False)


def test_independent_verifier_accepts_phase36_artifacts() -> None:
    completed = run(ROOT / "artifacts")
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["root_classes"] == 2214
    assert result["event_classes"] == 797
    assert result["decoded_words"] == 1_166_058
    assert result["area229_frontier_candidates"] == 1926
    assert result["area229_root_margin"] == -1277
    assert result["proves_collatz"] is False


def test_verifier_rejects_root_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase36_root_corpus.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["format"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "root corpus boundary mismatch" in completed.stdout


def test_verifier_rejects_event_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase36_event_polynomial.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["format"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "event corpus boundary mismatch" in completed.stdout


def test_verifier_rejects_scalar_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase36_scalar_audit.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["format"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "scalar boundary mismatch" in completed.stdout


def test_verifier_rejects_decoder_tamper(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase36_decoder_roots.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["format"] = "tampered"
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "decoder boundary mismatch" in completed.stdout


def test_verifier_rejects_overclaim(tmp_path: Path) -> None:
    target = copied(tmp_path)
    path = target / "phase36_theory.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["proves_collatz"] = True
    path.write_text(json.dumps(value), encoding="utf-8")
    completed = run(target)
    assert completed.returncode != 0
    assert "theory artifact mismatch" in completed.stdout
