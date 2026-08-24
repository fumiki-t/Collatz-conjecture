from __future__ import annotations

from src.branch_point_search import W, branch_profile, branch_record, parity_prefix, stopping_times, valuation_two


def test_branch_depth_is_exact_two_adic_gap_order() -> None:
    for n in range(2, 80):
        for m in range(n + 1, 96):
            row = branch_record(n, m)
            h = valuation_two(m - n)
            assert row["branch_depth"] == h
            assert parity_prefix(n, h) == parity_prefix(m, h)
            assert parity_prefix(n, h + 1) != parity_prefix(m, h + 1)
            assert row["normalized_odd_gap"] % 2 == 1
            assert row["transformed_gap"] == 3 ** row["shared_odd_count"] * row["normalized_odd_gap"]


def test_q0_positive_gap_has_one_of_thirty_branch_depths() -> None:
    for h in range(2, 32):
        difference = 1 << h
        if difference <= W:
            assert valuation_two(difference) == h
    assert W < 1 << 32
    assert len(range(2, 32)) == 30


def test_finite_profile_witnesses_are_maximal_by_direct_pairs() -> None:
    bound = 120
    stopping, _digest = stopping_times(bound)
    profile = branch_profile(bound, stopping)
    for row in profile:
        h = row["branch_depth"]
        direct = max(
            min(stopping[n], stopping[m]) - 1
            for n in range(2, bound + 1)
            for m in range(n + 1, bound + 1)
            if valuation_two(m - n) == h
        )
        assert row["max_joint_safe_depth"] == direct


def test_branch_search_and_verifier_are_import_independent() -> None:
    source = open("verifier/verify_branch_point.py", encoding="utf-8").read()
    assert "from src.branch_point_search import" not in source
    assert "import src.branch_point_search" not in source
