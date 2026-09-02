from __future__ import annotations

from src.phase33_search import (
    TIERS,
    alpha_data,
    best_p195,
    cutoff_certificate,
    frontier_audit,
    low_q_audit,
    maximum_minimum,
)


def test_low_q_audits_reconstruct_proposal_counts() -> None:
    first = low_q_audit(61, 2047)
    second = low_q_audit(117, 4095)
    assert first["counts"] == {
        "q_rows": 1077,
        "reduced_denominator_rejections": 405,
        "P133_E28_rejections": 669,
        "P133_admissible": 3,
        "P195_survivors": 0,
    }
    assert first["closest_failure"]["margin"] == -3
    assert second["counts"] == {
        "q_rows": 3125,
        "reduced_denominator_rejections": 808,
        "P133_E28_rejections": 2305,
        "P133_admissible": 12,
        "P195_survivors": 1,
    }
    assert [row["q"] for row in second["survivors"]] == [971]
    assert second["closest_failure"]["q"] == 1636
    assert second["closest_failure"]["margin"] == -21


def test_cf_frontiers_and_exact_cutoffs() -> None:
    alpha, _, convergents = alpha_data()
    rows = [frontier_audit(tier, alpha, convergents) for tier in TIERS]
    assert [row["candidate_count"] for row in rows] == [461, 915]
    assert all(row["closest_coarse_upper_margin"][-1] < 0 for row in rows)
    assert [cutoff_certificate(tier)["margin"] for tier in TIERS] == [
        ["201619589401", "3"],
        ["641842698055", "3"],
    ]


def test_exact_scalar_obstructions() -> None:
    first = best_p195(971, 1539, 62, maximum_minimum(971, 1539))
    second = best_p195(1636, 2593, 118, maximum_minimum(1636, 2593))
    assert first == {"margin": 31, "h": 6, "J": 23, "Sigma": 16, "E": 22,
                     "n": 27, "Z": 11, "rhs": 4648}
    assert second == {"margin": 45, "h": 7, "J": 46, "Sigma": 39, "E": 46,
                      "n": 29, "Z": 12, "rhs": 7824}
    assert maximum_minimum(971, 1539) == 330_911
    assert maximum_minimum(1636, 2593) == 583_560
