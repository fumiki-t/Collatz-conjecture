from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

from src.phase8_search import generate


def run_verifier(artifacts: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "verifier/verify_phase8.py", "--artifact-dir", str(artifacts)],
        check=False,
        capture_output=True,
        text=True,
    )


def link_phase7_dependencies(artifacts: Path) -> None:
    source = Path("artifacts")
    for name in (
        "phase7_boundary_defect.json",
        "phase7_contact_autocorrelation.json",
        "phase7_macro12.json",
    ):
        os.link(source / name, artifacts / name)


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    change(payload)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_phase8_independent_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    link_phase7_dependencies(artifacts)
    generate(artifacts, contracting_max_length=6, crossing_max_length=8)

    accepted = run_verifier(artifacts)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["C02"] == "VERIFIED_THEOREM"
    assert result["C03"] == "OPEN"
    assert result["octave"]["maximum_exceptions"] == 5
    assert result["semigroup"]["counterexamples"] == 0
    assert result["proves_collatz"] is False

    c02 = artifacts / "phase8_c02_theorem.json"
    octave = artifacts / "phase8_octave_bridge.json"
    short = artifacts / "phase8_short_excursions.json"
    semigroup = artifacts / "phase8_ab_semigroup_search.json"
    cases: list[tuple[Path, Callable[[dict[str, object]], None], str]] = [
        (
            c02,
            lambda data: data["integrality_reduction"]["congruences"].__setitem__(0, "u*81^r=109 mod 16^s"),
            "integrality congruence",
        ),
        (
            c02,
            lambda data: data["sign_identity"].__setitem__("right", "tampered"),
            "sign identity",
        ),
        (
            c02,
            lambda data: data["external_input"]["application"].__setitem__("nu", "4r+3s"),
            "exponent application",
        ),
        (
            octave,
            lambda data: data["constants"].__setitem__("q0", 72_057_431_992),
            "q0",
        ),
        (
            octave,
            lambda data: data["constants"].__setitem__("V", int(data["constants"]["V"]) + 1),
            "V",
        ),
        (
            octave,
            lambda data: data["denjoy_koksma"].__setitem__("indicator_circle_variation", 1),
            "variation",
        ),
        (
            octave,
            lambda data: data["denjoy_koksma"].__setitem__("total_error", 3),
            "error",
        ),
        (
            octave,
            lambda data: data["denjoy_koksma"].__setitem__("maximum_integer_exception_count", 4),
            "exception count",
        ),
        (
            short,
            lambda data: data["maps"][0]["map"].__setitem__(1, 2),
            "short-excursion",
        ),
        (
            semigroup,
            lambda data: data["contracting_search"]["records"][0].__setitem__(10, 0),
            "semigroup record",
        ),
    ]
    for path, change, expected_error in cases:
        original = path.read_text(encoding="utf-8")
        mutate(path, change)
        rejected = run_verifier(artifacts)
        path.write_text(original, encoding="utf-8")
        assert rejected.returncode == 1
        rejection = json.loads(rejected.stderr)
        assert rejection["valid"] is False
        assert expected_error in rejection["error"], rejection
