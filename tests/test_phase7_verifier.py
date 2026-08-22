from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.phase7_search import generate


def test_phase7_independent_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    generate(artifacts, mixed_bound=8)
    command = [
        sys.executable,
        "verifier/verify_phase7.py",
        "--artifact-dir",
        str(artifacts),
    ]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["macros"]["macro_count"] == 87_015
    assert result["fixed_layers"]["17"]["words"] == 312_455
    assert result["external_inputs_reproved"] == {"DENJOY_KOKSMA": False, "N_gt_V": False}
    assert result["proves_collatz"] is False

    path = artifacts / "phase7_macro12.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["records"][0][7] += 1
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rejected = subprocess.run(command, check=False, capture_output=True, text=True)
    assert rejected.returncode == 1
    rejection = json.loads(rejected.stderr)
    assert rejection["valid"] is False
    assert "affine mismatch" in rejection["error"]
