from __future__ import annotations

from src.phase26_search import compositions, cyclic_class, minimum_rotations
from src.phase31_short_leaf_search import (
    EXPECTED_CLAIMS,
    finite_rows,
    short_leaf_inventory,
    theory_artifact,
)


def small_minimum_profiles(maximum_q: int = 6):
    for q in range(1, maximum_q + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            for representative in sorted({cyclic_class(row) for row in compositions(length, q)}):
                yield from minimum_rotations(representative)


def test_short_leaf_pruning_preserves_exact_inventory() -> None:
    checked = 0
    for exponents in small_minimum_profiles():
        for radius in (1, 2, 3):
            row = short_leaf_inventory(exponents, radius)
            assert row["K"] + row["E"] == row["J"]
            assert row["E"] <= row["height"] + row["sigma"] // radius
            assert row["nonspine_excess"] <= row["sigma"]
            assert row["actual_word"].count("1") == row["q"]
            checked += 1
    assert checked == 867


def test_finite_double_hit_rows_are_exact_integer_certificates() -> None:
    exponents = (2, 1, 2, 1, 1, 4)
    candidates = minimum_rotations(exponents)
    assert candidates
    for rotated in candidates:
        for radius in (1, 2, 3):
            rows, counts = finite_rows(rotated, radius)
            assert counts["width_pruning_cases"] == sum(rotated)
            for row in rows:
                _, _, _, _, exceptional, context_bound, low_types, capacity, _, distinct, _, rhs = row
                assert exceptional <= min(sum(rotated), context_bound)
                assert low_types <= capacity
                if distinct:
                    assert 2 * sum(rotated) <= rhs


def test_every_fixed_radius_quantifier_is_recorded() -> None:
    theory = theory_artifact()
    assert theory["claims"] == EXPECTED_CLAIMS
    assert theory["P191"]["quantifiers"].startswith("every valid reduced profile")
    assert theory["P193"]["limit_order"] == "first q->infinity for each fixed R, then R->infinity"
    assert theory["P193"]["equality"] == "z=lim Sigma/q^(2/3)=0"


def test_h89_and_collatz_are_outside_scope() -> None:
    theory = theory_artifact()
    assert theory["claims"]["H89"] == "OPEN"
    assert "not audited" in theory["excluded_scope"]
    assert theory["proves_collatz"] is False
