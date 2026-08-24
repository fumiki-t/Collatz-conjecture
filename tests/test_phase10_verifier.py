from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest

from src.phase10_search import generate
from verifier.verify_phase10 import verify_cycle, verify_gap, verify_renewal, verify_spacing


def link_dependencies(destination: Path) -> None:
    source = Path("artifacts")
    for name in (
        "M_search_records.csv",
        "phase7_symbolic_certificate.json",
        "phase9_endpoint_displacement.json",
        "phase9_two_sided_residues.json",
    ):
        os.link(source / name, destination / name)


def mutate(path: Path, change: Callable[[dict[str, object]], None]) -> str:
    original = path.read_text(encoding="utf-8")
    data = json.loads(original)
    change(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return original


def rejected(path: Path, original: str, check: Callable[[], object], message: str) -> None:
    try:
        with pytest.raises(ValueError, match=message):
            check()
    finally:
        path.write_text(original, encoding="utf-8")


def test_phase10_independent_verifier_and_tamper_rejection(tmp_path: Path) -> None:
    artifacts = tmp_path / "artifacts"
    artifacts.mkdir()
    link_dependencies(artifacts)
    generate(artifacts, spacing_bound=5_000, layer_max_q=8)

    command = [sys.executable, "verifier/verify_phase10.py", "--artifact-dir", str(artifacts)]
    accepted = subprocess.run(command, check=False, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    result = json.loads(accepted.stdout)
    assert result["valid"] is True
    assert result["renewal_barrier"]["safe_through"] == 114_208_327_603
    assert result["C04"] == result["C05"] == "OPEN"
    assert result["proves_collatz"] is False

    gap_path = artifacts / "phase10_gap_modulus.json"
    original = mutate(gap_path, lambda data: data["P63"].__setitem__("rho_mod_4", 2))
    rejected(gap_path, original, lambda: verify_gap(gap_path, artifacts), "mod-four")
    original = mutate(gap_path, lambda data: data["P63"].__setitem__("exact_identities", []))
    rejected(gap_path, original, lambda: verify_gap(gap_path, artifacts), "gap identity")
    original = mutate(gap_path, lambda data: data["D_gt_W_certificate"].__setitem__("three_power_used", 43))
    rejected(gap_path, original, lambda: verify_gap(gap_path, artifacts), "D>W")
    original = mutate(gap_path, lambda data: data["canonical_residue_range_certificate"].__setitem__("K0_gt_72", False))
    rejected(gap_path, original, lambda: verify_gap(gap_path, artifacts), "canonical residue")
    original = mutate(gap_path, lambda data: data["finite_first_crossing_audit"]["layers"][0]["maximum_d_record"].__setitem__("rho", 1))
    rejected(gap_path, original, lambda: verify_gap(gap_path, artifacts), "layer/digest")

    renewal_path = artifacts / "phase10_renewal_barrier.json"
    original = mutate(renewal_path, lambda data: data["stern_brocot_certificate"].__setitem__("right_upper_parent", [1, 1]))
    rejected(renewal_path, original, lambda: verify_renewal(renewal_path, artifacts), "parents")
    original = mutate(renewal_path, lambda data: data["exact_margins"]["right_parent_gap_minus_required_margin"]["lower"].__setitem__(0, "0"))
    rejected(renewal_path, original, lambda: verify_renewal(renewal_path, artifacts), "interval")
    original = mutate(renewal_path, lambda data: data["P64"].__setitem__("conclusion", "tampered"))
    rejected(renewal_path, original, lambda: verify_renewal(renewal_path, artifacts), "conclusion")
    original = mutate(renewal_path, lambda data: data["first_crossing_index_rule"].__setitem__("safe_through", 1))
    rejected(renewal_path, original, lambda: verify_renewal(renewal_path, artifacts), "first-crossing")

    spacing_path = artifacts / "phase10_safe_pair_spacing.json"
    original = mutate(spacing_path, lambda data: data["E15"]["layers"][5].__setitem__("delta", 1))
    rejected(spacing_path, original, lambda: verify_spacing(spacing_path, artifacts), "layers/digest")
    original = mutate(spacing_path, lambda data: data["E15"].__setitem__("stopping_time_digest_sha256", "0" * 64))
    rejected(spacing_path, original, lambda: verify_spacing(spacing_path, artifacts), "layers/digest")
    original = mutate(spacing_path, lambda data: data["mandatory_adversarial_audit"]["A^rB^s"].__setitem__("fully_coefficient_safe", 0))
    rejected(spacing_path, original, lambda: verify_spacing(spacing_path, artifacts), "adversarial")
    original = mutate(spacing_path, lambda data: data["C05"].__setitem__("repository_status", "VERIFIED_THEOREM"))
    rejected(spacing_path, original, lambda: verify_spacing(spacing_path, artifacts), "C05")
    original = mutate(spacing_path, lambda data: data["recursive_difference_rule"]["strict_growth_shortcut"].__setitem__("Delta_k_plus_1", 5))
    rejected(spacing_path, original, lambda: verify_spacing(spacing_path, artifacts), "strict-growth")

    cycle_path = artifacts / "phase10_rational_cycle.json"
    original = mutate(cycle_path, lambda data: data["P65"].__setitem__("prefix_difference_numerator", "tampered"))
    rejected(cycle_path, original, lambda: verify_cycle(cycle_path), "minimum identity")
    original = mutate(cycle_path, lambda data: data["finite_audit"]["layers"][0].__setitem__("cycle_digest_sha256", "0" * 64))
    rejected(cycle_path, original, lambda: verify_cycle(cycle_path), "layer/digest")
