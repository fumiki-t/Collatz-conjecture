from __future__ import annotations

from src.boundary_gap import audit_boundary_gaps, boundary_gap_minimum, coefficient_threshold
from src.phase3_model import coefficient_survivors


def naive_boundary(parent_depth: int) -> tuple[int, str, int, int]:
    q = coefficient_threshold(parent_depth)
    rows: list[tuple[int, str, int, int]] = []
    for node in coefficient_survivors(parent_depth):
        if node.odd_capacity == q and node.t_min == 0:
            rows.append((2 * node.r - node.y, node.parity, node.r, node.y))
    return min(rows)


def test_meet_in_middle_matches_naive_small_depths() -> None:
    for parent_depth in (3, 4, 6, 7, 9, 11, 12, 14):
        row = boundary_gap_minimum(parent_depth)
        assert (
            row["minimum_gap"],
            row["word"],
            row["r"],
            row["y"],
        ) == naive_boundary(parent_depth)


def test_boundary_depth_27_sanity_value() -> None:
    row = boundary_gap_minimum(26)
    assert row["boundary_depth"] == 27
    assert (row["r"], row["y"], row["minimum_gap"]) == (167, 325, 9)


def test_boundary_audit_through_36_is_exact_and_positive() -> None:
    result = audit_boundary_gaps(36)
    assert result["counterexample"] is None
    assert result["exhaustive"] is True
    assert result["uses_beam_search"] is False
    assert all(row["minimum_gap"] > 0 for row in result["minima"])
