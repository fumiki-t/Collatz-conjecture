from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from src.phase4_search import generate


def test_independent_return9_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    generate(artifacts, max_a=4, max_depth=2, direct_bound=1 << 14, stopping_bound=1 << 12)
    certificate = artifacts / "return9_certificate.json"
    code_audit = artifacts / "return9_code_audit.json"
    command = [
        sys.executable,
        "verifier/verify_return9.py",
        str(certificate),
        "--code-audit",
        str(code_audit),
    ]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert json.loads(accepted.stdout)["valid"] is True

    payload = json.loads(certificate.read_text(encoding="utf-8"))
    merge_record = next(
        record for record in payload["records"] if record["rule"]["type"] == "RETURN_SMALLER_S"
    )
    merge_record["family"]["endpoint"][0] += 9
    certificate.write_text(
        json.dumps(payload, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    rejected = subprocess.run(command, check=False, capture_output=True, text=True)
    assert rejected.returncode == 1
    assert rejected.stdout.startswith("INVALID:")
