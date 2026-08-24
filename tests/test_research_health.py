from __future__ import annotations

import json
import subprocess
import sys


def test_repository_research_health() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/research_health.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["latest_phase"] == 12
    assert result["active_focus"]["C04"] == "OPEN"
    assert result["active_focus"]["C05"] == "OPEN"
    assert result["active_focus"]["P69"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P70"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["H70"] == "OPEN"
    assert result["active_focus"]["NG20"] == "REFUTED"
    assert result["active_focus"]["P72"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P73"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E20"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG21"] == "REFUTED"
    assert result["active_focus"]["H72"] == "OPEN"
    assert result["latest_supplemental_verifier"]["valid"] is True
    assert result["proves_collatz"] is False
