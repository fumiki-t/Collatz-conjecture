from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from src.phase27_search import (
    MATVEEV_K,
    cycle_branch,
    envelope_audit,
    least_and_discrepancy_offsets,
    reduced_profile,
    regression_audit,
    synthetic_audit,
)


ROOT = Path(__file__).resolve().parents[1]


def test_matveev_integer_majorant_is_exact() -> None:
    assert 5 * MATVEEV_K == 7 * 30**5 * 23 * 2
    assert 2**9 < 23**2


def test_smallest_rotation_alignment_obstruction_is_exact() -> None:
    least, discrepancy = least_and_discrepancy_offsets((1, 3))
    assert least == (0,)
    assert discrepancy == (1,)

    artifact = json.loads((ROOT / "artifacts" / "phase27_cycle_corpus.json").read_text(encoding="utf-8"))
    obstruction = artifact["smallest_rotation_mismatch"]
    assert obstruction["exponents"] == [1, 3]
    assert obstruction["odd_rational_orbit"] == [["5", "7"], ["11", "7"]]
    assert obstruction["positive_integral"] is False


def test_support_profile_bounds_hold_for_noncoprime_example() -> None:
    data = reduced_profile((3, 1))
    support = sum(value > 0 for value in data["profile"][:-1])
    assert data["d"] == 2
    assert data["area"] == data["height"] == support == 1


def test_exact_envelopes_reconstruct_phase26_controls() -> None:
    data = envelope_audit()
    assert data["matveev_specialization"]["integer_majorant_K"] == MATVEEV_K
    assert data["matveev_specialization"]["exact_majorant_verified"] is True
    assert int(data["noncritical_rows"][0]["excluded_through"]) >= 100_000
    assert int(data["x02_control"]["least_unexcluded_area"]) > 5 * 10**15
    assert all(row["current_positive_margin"] is False for row in data["critical_rows"])


def test_synthetic_profiles_are_exact_structural_controls() -> None:
    data = synthetic_audit()
    assert len(data["rows"]) == 8
    assert {row["kind"] for row in data["rows"]} == {"tall", "diffuse"}
    for row in data["rows"]:
        assert row["support"] >= row["height"]
        assert row["area"] >= row["height"] * (row["height"] + 1) // 2
        assert row["valid_positive_exponents"] is True


def test_mandatory_adversarial_families_are_preserved() -> None:
    corpus = json.loads((ROOT / "artifacts" / "phase27_cycle_corpus.json").read_text(encoding="utf-8"))
    data = regression_audit(corpus)
    labels = {row[0] for row in data["mandatory_adversarial_families"]}
    assert labels == {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}
    assert cycle_branch(6, 11) == "noncritical"
    assert Fraction(int(data["phase26_scalar_obstruction"]["left"]), int(data["phase26_scalar_obstruction"]["right"])) > 1
