from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.phase5_search import generate


def test_phase5_independent_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    generate(
        artifacts,
        direct_bound=1 << 14,
        shadow_depth=4,
        beam_width=24,
        low_precision_limit=3,
    )
    command = [
        sys.executable,
        "verifier/verify_phase5.py",
        "--artifact-dir",
        str(artifacts),
    ]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert json.loads(accepted.stdout)["valid"] is True

    section_path = artifacts / "section4_templates.json"
    payload = json.loads(section_path.read_text(encoding="utf-8"))
    payload["templates"][0]["A"] += 3
    section_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rejected = subprocess.run(command, check=False, capture_output=True, text=True)
    assert rejected.returncode == 1
    assert rejected.stdout.startswith("INVALID:")
