from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase9_search import DMAX, generate
from verifier.verify_phase9 import (
    common,
    verify_dual,
    verify_endpoint,
    verify_reverse,
    verify_reverse_residues,
    verify_short,
    verify_two_sided,
)


def link_dependencies(destination: Path) -> None:
    source = Path("artifacts")
    for name in (
        "phase7_boundary_defect.json",
        "phase7_macro12.json",
        "phase8_ab_semigroup_search.json",
        "phase8_octave_bridge.json",
        "phase8_short_excursions.json",
    ):
        os.link(source / name, destination / name)


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> str:
    original = path.read_text(encoding="utf-8")
    payload = json.loads(original)
    change(payload)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return original


def rejected(path: Path, original: str, check: Callable[[], object], message: str) -> None:
    try:
        with pytest.raises(ValueError, match=message):
            check()
    finally:
        path.write_text(original, encoding="utf-8")


def test_phase9_independent_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    link_dependencies(artifacts)
    generate(artifacts, small_layer_max_q=8, reverse_max_a=8, paradoxical_max_length=10)

    command = [sys.executable, "verifier/verify_phase9.py", "--artifact-dir", str(artifacts)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["C04"] == "OPEN"
    assert result["contact_dual"]["contact_lower"] == 35_251_435_772
    assert result["endpoint"]["dmax"] == DMAX
    assert result["proves_collatz"] is False

    arithmetic = common()

    forced_path = artifacts / "phase9_forced_contact.json"
    original = mutate(forced_path, lambda data: data["P59"].__setitem__("forced_closure", "tampered"))
    bad_cli = subprocess.run(command, check=False, capture_output=True, text=True)
    forced_path.write_text(original, encoding="utf-8")
    assert bad_cli.returncode == 1
    assert "closure" in json.loads(bad_cli.stderr)["error"]

    dual_path = artifacts / "phase9_contact_dual.json"
    original = mutate(dual_path, lambda data: data["selected"]["integral"]["upper"].__setitem__(0, "0"))
    rejected(dual_path, original, lambda: verify_dual(dual_path, arithmetic, artifacts), "interval")
    original = mutate(dual_path, lambda data: data["selected"].__setitem__("circle_total_variation", ["1", "1"]))
    rejected(dual_path, original, lambda: verify_dual(dual_path, arithmetic, artifacts), "variation")

    short_path = artifacts / "phase9_short_return_bound.json"
    original = mutate(short_path, lambda data: data["E14"]["forced_closure_contacts"].__setitem__("first_octave_lower", 0))
    rejected(short_path, original, lambda: verify_short(short_path, 35_251_435_772, artifacts), "gap formula")

    endpoint_path = artifacts / "phase9_endpoint_displacement.json"
    original = mutate(endpoint_path, lambda data: data["P60"].__setitem__("near_return_identity", "tampered"))
    rejected(endpoint_path, original, lambda: verify_endpoint(endpoint_path, arithmetic, artifacts), "d identity")
    original = mutate(endpoint_path, lambda data: data["P60"].__setitem__("maximum_integer_displacement", DMAX + 1))
    rejected(endpoint_path, original, lambda: verify_endpoint(endpoint_path, arithmetic, artifacts), "upper-bound")
    original = mutate(endpoint_path, lambda data: data["P61"]["endpoint_congruences"].__setitem__("X_mod_9", [1, 4, 7]))
    rejected(endpoint_path, original, lambda: verify_endpoint(endpoint_path, arithmetic, artifacts), "parity/mod")
    original = mutate(endpoint_path, lambda data: data["P61"]["G4"].__setitem__("predecessor", "z=(2*y+1)/3"))
    rejected(endpoint_path, original, lambda: verify_endpoint(endpoint_path, arithmetic, artifacts), "G4 predecessor")

    reverse_path = artifacts / "phase9_reverse_barrier.json"
    original = mutate(reverse_path, lambda data: data["P62"].__setitem__("uniform_ratio_threshold", ["1", "1"]))
    rejected(reverse_path, original, lambda: verify_reverse(reverse_path, arithmetic), "coefficient threshold")
    original = mutate(reverse_path, lambda data: data["continued_fraction_certificate"].__setitem__("upper_parent", [1, 1]))
    rejected(reverse_path, original, lambda: verify_reverse(reverse_path, arithmetic), "parents")
    original = mutate(reverse_path, lambda data: data["continued_fraction_certificate"]["lower_semiconvergents"][2].__setitem__("L", 1))
    rejected(reverse_path, original, lambda: verify_reverse(reverse_path, arithmetic), "semiconvergent classification")

    reverse_residue_path = artifacts / "phase9_reverse_residues.json"
    original = mutate(reverse_residue_path, lambda data: data["all_contracting_coefficient_pairs"][0].__setitem__("below_uniform_threshold", False))
    rejected(reverse_residue_path, original, lambda: verify_reverse_residues(reverse_residue_path, arithmetic), "coefficient-pair")

    two_sided_path = artifacts / "phase9_two_sided_residues.json"
    original = mutate(two_sided_path, lambda data: data["small_layer_audit"]["layers"][0]["minimum_displacement_record"].__setitem__("r2", 2))
    rejected(two_sided_path, original, lambda: verify_two_sided(two_sided_path, artifacts), "exhaustive parity")
    original = mutate(two_sided_path, lambda data: data["C04"]["q0_box"].__setitem__("difference", "0<=r3-r2<=1"))
    rejected(two_sided_path, original, lambda: verify_two_sided(two_sided_path, artifacts), "near-diagonal")
