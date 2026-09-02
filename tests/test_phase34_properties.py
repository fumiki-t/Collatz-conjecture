from __future__ import annotations

from src.phase34_search import (
    alpha_data,
    best_scalar_row,
    cutoff_certificate,
    defect_audit,
    frontier_audit,
    low_q_audit,
    profile_bridge_audit,
    profile_maximum,
)


def test_exact_cutoff_and_cf_frontier() -> None:
    alpha, _, convergents = alpha_data()
    assert cutoff_certificate()["margin"] == ["1383372477367", "3"]
    assert cutoff_certificate()["derivative_upper"] == ["981204840627", "20000000000000"]
    frontier = frontier_audit(alpha, convergents)
    assert frontier["candidate_count"] == 1725
    assert frontier["upper_convergents"][-1] == [8573543875303, 5409303924479]
    assert frontier["closest_coarse_upper_margin"][-1] < 0


def test_low_q_area_208_and_next_obstruction() -> None:
    audit = low_q_audit(208)
    assert audit["counts"] == {
        "q_rows": 7221,
        "q0_rejections": 1216,
        "state_E46_rejections": 5979,
        "admissible_q_rows": 26,
        "P195_survivors": 0,
    }
    assert audit["closest_failure"] == {
        "q": 2301, "L": 3647, "d": 1, "q0": 2301, "margin": -32,
        "h": 2, "J": 105, "Sigma": 102, "E": 104, "n": 24, "Z": 10,
        "rhs": 10909, "m_max": 860946, "m_P133": 860946, "m_prof": 977685,
    }
    obstruction, _ = best_scalar_row(2301, 3647, 209)
    assert obstruction == {
        "margin": 24, "h": 2, "J": 105, "Sigma": 103, "E": 105,
        "n": 24, "Z": 10, "rhs": 10965, "m_max": 860946,
        "m_P133": 860946, "m_prof": 978246,
    }


def test_strict_profile_integer_bound() -> None:
    assert profile_maximum(2301, 3647, 208, 2) == 977685
    assert profile_maximum(2301, 3647, 209, 2) == 978246


def test_bridge_and_defect_corpora() -> None:
    bridge = profile_bridge_audit()
    assert bridge["minimum_rotations"] == 10103
    assert bridge["least_profile_h_minus_one_controls"] == []
    assert bridge["segment_checks"] > 100_000
    defects = defect_audit()
    assert defects["legal_profiles"] == 21766
    assert defects["samples"][0][-2:] == [2, 2]
