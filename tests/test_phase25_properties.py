import itertools
import math
from fractions import Fraction

from src.phase23_search import cyclic_factors, expanded_word
from src.phase24_search import area_three_profiles, critical_length, exponents_of_profile
from src.phase25_search import (
    area_three_type,
    bareiss_determinant,
    conjugate_real_part_intervals,
    critical_support_lower,
    hamming,
    linear_factors,
    polynomial_add,
    quotient_norm,
    resonance_polynomial,
)


def test_linear_and_cyclic_hamming_factor_lemma_exhaustively() -> None:
    for length in range(1, 6):
        words = ["".join(bits) for bits in itertools.product("01", repeat=length)]
        for left in words:
            for right in words:
                distance = hamming(left, right)
                for width in range(1, length + 1):
                    assert len(linear_factors(right, width)) <= len(linear_factors(left, width)) + width * distance
                    assert len(cyclic_factors(right, width)) <= len(cyclic_factors(left, width)) + width * distance


def test_area_three_literal_hamming_classification() -> None:
    expected = {"doubled-root": 2, "root-child-plus-root": 4, "three-roots": 6}
    counts = {key: 0 for key in expected}
    for q in range(2, 31):
        L = critical_length(q)
        if L >= 2 * q or math.gcd(q, L) != 1:
            continue
        baseline = expanded_word(exponents_of_profile(q, L, (0,) * q))
        for profile in area_three_profiles(q, L):
            word = expanded_word(exponents_of_profile(q, L, profile))
            kind = area_three_type(profile, q, L)
            assert hamming(baseline, word) == expected[kind]
            counts[kind] += 1
    assert all(counts.values())


def test_q0_support_integer_arithmetic() -> None:
    assert critical_support_lower(72_057_431_991, 73) == 490_186_612


def test_resonance_norm_and_threshold_are_exact() -> None:
    P = [0, 1, 1, 1]
    assert abs(quotient_norm(polynomial_add(P, [-1]), 7)) == 209
    assert 627 * 25**7 < 2 * 64**7
    outcomes = []
    for Q in range(1, 12):
        left = 2 * 3**7 * 627**Q * 25 ** (7 * Q)
        right = 2**Q * 64 ** (7 * Q)
        outcomes.append(left < right)
        assert quotient_norm(resonance_polynomial(Q, P), 7) != 0
    assert outcomes == [False] * 10 + [True]


def test_exact_conjugate_intervals_select_P_minus_one() -> None:
    intervals = conjugate_real_part_intervals()
    assert set(intervals) == {"1", "2", "3"}
    assert all(Fraction(int(high[0]), int(high[1])) < Fraction(1, 2) for _, high in intervals.values())


def test_bareiss_determinant_with_row_swap() -> None:
    assert bareiss_determinant([[0, 1], [2, 3]]) == -2
