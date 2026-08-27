from __future__ import annotations

from fractions import Fraction

from src.phase14_search import (
    codewords,
    literal_trace,
    pair_rewrite,
    rewrite_audit,
    threshold_audit,
    word_constant,
)


def affine_value(word: str, value: int) -> Fraction:
    return Fraction(3 ** word.count("1") * value + word_constant(word), 2 ** len(word))


def test_reported_coalescent_identities_and_literal_sequences() -> None:
    examples = (
        ("11101", "111100", 7, 15, 20, 4),
        ("1111111000111110010", "11111111010000110110", 886143, 1772287, 2694703, 13),
    )
    for a, d, x, y, endpoint, q in examples:
        assert a.count("1") == d.count("1") == q
        assert len(d) == len(a) + 1
        assert 2 * word_constant(a) - word_constant(d) == 3**q
        assert affine_value(d, 2 * x + 1) == affine_value(a, x) == endpoint
        assert literal_trace(x, a)[-1] == a
        assert literal_trace(y, d)[-1] == d


def test_general_m_sign_cases_are_affine_not_positivity_claims() -> None:
    # m=0 leading-zero lift.
    assert affine_value("01", 2 * 5) == affine_value("1", 5)
    # m<0 is legal only above its positivity/descent threshold.
    assert affine_value("0001", 2 * 5 - 2) == affine_value("100", 5)
    assert 2 * 5 - 2 > 5 > 0


def test_complete_q7_rewrites_coalesce_and_decrease() -> None:
    artifact, _blocks = rewrite_audit(7)
    finite = artifact["E23"]
    assert finite["least_collision"]["a"]["forward"] == "11101"
    assert finite["least_collision"]["d"]["forward"] == "111100"
    assert finite["finite_normal_forms"]["directed_cycle_count"] == 0
    assert finite["finite_normal_forms"]["nonunique_normal_form_count"] == 0


def test_initial_run_thresholds_and_decrement() -> None:
    finite = threshold_audit(9)
    assert finite["general_bound_violation_count"] == 0
    minima = {row["r"]: row for row in finite["minimum_by_initial_one_run"]}
    assert (minima[2]["R"]["numerator"], minima[2]["R"]["denominator"]) == ("13", "9")
    assert (minima[3]["R"]["numerator"], minima[3]["R"]["denominator"]) == ("137", "81")
    assert (minima[4]["R"]["numerator"], minima[4]["R"]["denominator"]) == ("43", "27")

    for S in (3, 11, 27, 59):
        U = Fraction(S + 1, 4)
        for block in codewords(9):
            if block.forward == "1":
                continue
            R = Fraction(block.correction + 2**block.length, 3**block.odd_count)
            h = R + Fraction(1, 17)
            z = (h - 1) / (S + 1)
            z_prime = (h - R) / (S + R)
            assert z - z_prime > Fraction(1, 12 * U + 1)


def test_shadow_denominator_integer_step_when_a_is_positive() -> None:
    # The proof uses only H<2h0 and the exact 2-adic numerator divisibility.
    # These exact synthetic rows test that final integer implication.
    for E, x0, h0, q in (
        (8, 27, Fraction(7, 4), 18),
        (12, 59, Fraction(13, 9), 140),
        (16, 123, Fraction(3, 2), 1100),
    ):
        assert q * (x0 + 2 * h0) > 2 ** (E + 1)
