from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.phase6_search import generate


def test_phase6_independent_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    generate(
        artifacts,
        hq_limit=1000,
        m_search_bound=5000,
        certificate_max_x=3000,
        direct_threshold=16,
    )
    command = [
        sys.executable,
        "verifier/verify_phase6.py",
        "--artifact-dir",
        str(artifacts),
    ]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["symbolic_theorem_verified"] is True
    assert result["external_minimality_verified"] is False

    path = artifacts / "M_lower_bound_certificates.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    cross = next(
        node
        for certificate in payload["certificates"]
        for node in certificate["nodes"]
        if node["rule"] == "COEFF_CROSS"
    )
    cross["strict_gap"] += 1
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    rejected = subprocess.run(command, check=False, capture_output=True, text=True)
    assert rejected.returncode == 1
    assert rejected.stdout.startswith("INVALID:")
