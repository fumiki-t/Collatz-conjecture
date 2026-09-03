from __future__ import annotations

from fractions import Fraction

from src.phase35_search import (
    CUTOFF,
    MATVEEV_K,
    cutoff_certificate,
    decode_profile,
    decoder_audit,
    displayed_area209_rejection,
    frontier_audit,
    joint_low_q_audit,
    safe_position_lists,
)


def test_decoder_small_exhaustion_and_known_source() -> None:
    audit = decoder_audit(12)
    assert audit["total_words"] == 4403
    assert decode_profile(4, 59) == (0, 0, 0, 0)
    for q in range(1, 9):
        assert len(list(safe_position_lists(q))) == audit["counts_by_q"][q - 1][2]


def test_corrected_cutoff_is_exact() -> None:
    result = cutoff_certificate()
    expected = Fraction(19 * CUTOFF, 12) - (5950 + 238 * (44 + 47 * MATVEEV_K))
    assert result["margin"] == [str(expected.numerator), str(expected.denominator)]
    assert expected == Fraction(2_109_414_590_734, 3)
    assert Fraction(*map(int, result["derivative_upper"])) < Fraction(19, 12)


def test_corrected_frontier_counts() -> None:
    assert frontier_audit(261)["candidate_count"] == 1912
    assert frontier_audit(273)["candidate_count"] == 1996


def test_joint_scalar_floor_and_first_obstruction() -> None:
    below = joint_low_q_audit(228)
    assert below["counts"] == {
        "q_rows": 7221,
        "q0_rejections": 1216,
        "state_E46_rejections": 5979,
        "T35C_rejections": 25,
        "T35B_rejections": 1,
        "joint_survivors": 0,
    }
    boundary = joint_low_q_audit(229)
    assert len(boundary["survivors"]) == 1
    row = boundary["survivors"][0]
    assert (row["q"], row["L"], row["A_res"], row["T_res"]) == (2301, 3647, 183, 366)
    assert (row["T35B_margin"], row["T35C_margin"]) == (10, 43)


def test_phase34_area209_tuple_is_rejected_by_refined_factor_bound() -> None:
    row = displayed_area209_rejection()
    assert row["T35B_rhs"] == 2858
    assert row["T35B_margin"] == -789
    assert row["T35C_margin"] == 24
