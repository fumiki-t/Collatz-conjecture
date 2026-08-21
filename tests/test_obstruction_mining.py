from __future__ import annotations

from fractions import Fraction

from src.mine_obstructions import (
    best_repeat,
    block_facts,
    coefficient_comparisons,
    explained_by_short_shadow,
    shortest_period,
)


def test_exact_period_and_repeat_selection() -> None:
    assert shortest_period("110110110") == 3
    assert best_repeat("11011011001", "prefix") == ("110", 3)
    assert best_repeat("00110110110", "suffix") == ("110", 3)
    assert explained_by_short_shadow("11011011001")
    assert not explained_by_short_shadow("11011001")


def test_rational_fixed_point_of_110() -> None:
    facts = block_facts("110")
    assert facts["P"] == 9
    assert facts["Q"] == 8
    assert facts["B_w"] == 5
    fixed = facts["fixed_point"]
    assert fixed is not None
    assert Fraction(fixed["numerator"], fixed["denominator"]) == -5


def test_prefix_comparisons_are_exact() -> None:
    assert coefficient_comparisons("110") == ">>>"
    assert coefficient_comparisons("000") == "<<<"
