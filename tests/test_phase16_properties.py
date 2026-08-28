from __future__ import annotations

from fractions import Fraction

from src.phase16_search import (
    NEGATIVE_A,
    NEGATIVE_D,
    allowed_residues,
    canonical,
    finite_layers,
    log_bounds,
    negative_carry,
    theory_artifact,
)


def test_q26_negative_carry_is_literal_and_exact() -> None:
    result = negative_carry()
    a, d = canonical(NEGATIVE_A), canonical(NEGATIVE_D)
    assert a["safe"] is d["safe"] is True
    assert a["Q"] == d["Q"] == 26
    assert a["endpoint"] == d["endpoint"] == 716_727_426_419
    assert 2 * a["B"] - d["B"] == -3 * 3**26
    assert d["source"] == 2 * a["source"] - 3
    assert result["carry"] == -3


def test_q1_strict_bound_in_proposal_is_repaired() -> None:
    result = theory_artifact()["carry_bound"]
    assert "q=1" in result["proposal_repair"]
    assert canonical("1")["B"] == 1
    assert Fraction(canonical("1")["B"], 3) == Fraction(1, 3)


def test_mod72_counts_and_packing_capacity_are_exact() -> None:
    rows = allowed_residues()
    assert [row["count"] for row in rows] == [6, 9, 15, 20, 24]
    assert sum(row["count"] for row in rows) == 74
    capacity = Fraction(1, 96) + Fraction(3, 64) + Fraction(5, 48) + Fraction(5, 72)
    assert capacity == Fraction(133, 576)


def test_exact_log_enclosure_has_positive_250_margin() -> None:
    result = theory_artifact()
    margin = result["log_certificate"]["exact_positive_margin_after_reduction"]
    exact = Fraction(int(margin["numerator"]), int(margin["denominator"]))
    assert exact > 0
    lower, upper = log_bounds(Fraction(2), 12)
    assert 0 < lower < upper


def test_finite_geodesic_tree_is_prefix_closed_at_small_cutoff() -> None:
    result = finite_layers(9)
    for row in result["counts_by_Q"].values():
        assert row["same_Q_geodesic"] == row["all_prefix_same_Q_geodesic"]
        assert row["contact_rich_geodesic"] <= row["same_Q_geodesic"]
        assert row["contact_rich_geodesic"] <= row["contact_rich"]
    assert result["negative_carry_pair_count_in_cutoff"] == 0


def test_periodic_and_nonperiodic_branches_remain_separate() -> None:
    result = theory_artifact()["dichotomy"]
    assert "odd inputs before crossing are distinct" in result["hypotheses"]
    assert result["periodic_boundary"].startswith("Without distinctness")
    assert result["q0_consequence"]["status"] == "CONDITIONAL"
    assert theory_artifact()["proves_collatz"] is False
