from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from src.phase28_search import (
    direct_polynomial,
    regression_audit,
    scalar_audit,
    synthetic_audit,
    transport_data,
)


ROOT = Path(__file__).resolve().parents[1]


def test_exact_transport_script_and_endpoint_correction() -> None:
    data = transport_data((3, 1))
    assert data["profile"] == (0, 1, 0)
    assert data["J"] == len(data["insertions"]) == len(data["deletions"]) == 1
    assert data["area"] == data["height"] == 1
    assert direct_polynomial(data["profile"]) == (3, -1)
    uncorrected = 1 + 2 * data["weighted_components"]
    corrected = uncorrected + data["endpoint_weight"]
    assert data["polynomial_l1"] == corrected == 4
    assert uncorrected == 3


def test_smallest_finite_strictness_obstruction_is_preserved() -> None:
    data = transport_data((3, 1, 1))
    assert data["profile"] == (0, 1, 0, 0)
    assert Fraction(data["L"] - data["q"], data["q"]) == Fraction(2, 3)
    triangular = data["height"] * (data["height"] + 1) // 2
    assert data["area"] == triangular == data["J"] + data["descent_floor"] == 1


def test_synthetic_profiles_separate_area_from_transport() -> None:
    rows = {row["kind"]: row for row in synthetic_audit()["rows"]}
    tall = rows["one-tall-excursion"]
    plateau = rows["long-constant-plateau"]
    assert (tall["area"], tall["height"], tall["J"]) == (23, 5, 5)
    assert (plateau["area"], plateau["height"], plateau["J"]) == (597, 5, 5)
    assert rows["isolated-unit-excursions"]["J"] == 20
    assert all(row["valid_positive_exponents"] is True for row in rows.values())


def test_scalar_certificates_are_exact_and_improve_phase27() -> None:
    data = scalar_audit()
    assert data["noncritical_constant"] == ["3", "2"]
    assert all(row["at_least_three_halves"] for row in data["slope_rows"])
    low = Fraction(*map(int, data["critical_constant_decimal_box"][0]))
    high = Fraction(*map(int, data["critical_constant_decimal_box"][1]))
    assert Fraction(1535941, 1_000_000) == low < high == Fraction(767971, 500_000)
    phase27_high = Fraction(*map(int, data["phase27_constant_cube_interval"][1]))
    phase28_low = Fraction(*map(int, data["critical_constant_cube_interval"][0]))
    assert phase28_low > phase27_high


def test_mandatory_families_and_both_refutations_are_preserved() -> None:
    data = regression_audit()
    labels = {row[0] for row in data["mandatory_families"]}
    assert labels == {
        "2^m-1",
        "8^m-5",
        "(110|111)^*",
        "A=11101",
        "B=1100",
        "A^1B^1",
        "A^2B^3",
    }
    assert data["finite_strictness_obstruction"]["new_bound"] == 1
    assert data["endpoint_l1_obstruction"]["l1"] == 4
    assert data["endpoint_l1_obstruction"]["proposed_bound"] == 3


def test_theory_artifact_never_claims_collatz() -> None:
    theory = json.loads((ROOT / "artifacts" / "phase28_theory.json").read_text(encoding="utf-8"))
    assert theory["proves_collatz"] is False
    assert theory["claims"]["H172"]["status"] == "OPEN"
    assert theory["claims"]["NG37"]["status"] == "REFUTED"
    assert theory["claims"]["NG38"]["status"] == "REFUTED"
    assert "Collatz proof" in theory["what_this_result_does_not_prove"]
