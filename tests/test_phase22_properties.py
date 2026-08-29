import math
from fractions import Fraction

from src.phase22_search import (
    NEGATIVE_Q7,
    affine_correction,
    compositions,
    exponents_of_profile,
    literal_accelerated_cycle,
    minimum_height_rotation,
    multiplication_resultant,
    profile_of,
    profiles_of_area,
    slope_root,
)


def test_affine_cycle_identity_on_small_compositions() -> None:
    for q in range(1, 6):
        for L in range(q, 2 * q + 1):
            for exponents in compositions(L, q):
                B = affine_correction(exponents)
                source = 17
                current = Fraction(source)
                for exponent in exponents:
                    current = Fraction(3 * current + 1, 2**exponent)
                assert current == Fraction(3**q * source + B, 2**L)


def test_coprime_profile_round_trip_and_residue_indexing() -> None:
    for q in range(2, 9):
        for L in range(q + 1, 2 * q + 1):
            if math.gcd(q, L) != 1:
                continue
            for exponents in compositions(L, q):
                canonical = minimum_height_rotation(exponents)
                profile = profile_of(canonical)
                assert profile[0] == 0
                assert exponents_of_profile(q, L, profile) == canonical


def test_area_one_validity_has_required_support() -> None:
    for q in range(2, 20):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q or math.gcd(q, L) != 1:
                continue
            for profile in profiles_of_area(q, 1):
                exponents = exponents_of_profile(q, L, profile)
                if exponents is None:
                    continue
                support = next(index for index, value in enumerate(profile) if value)
                assert 1 <= support <= L - q - 1


def test_slope_root_and_resultant_divisibility_on_integral_rows() -> None:
    for q in range(1, 7):
        for L in range(q + 1, 2 * q + 1):
            D = 2**L - 3**q
            if D <= 1 or math.gcd(q, L) != 1:
                continue
            for exponents in compositions(L, q):
                profile = profile_of(exponents)
                B = affine_correction(minimum_height_rotation(exponents))
                gamma = slope_root(q, L, D)
                polynomial = sum(2**value * pow(gamma, index, D) for index, value in enumerate(profile)) % D
                assert (B % D == 0) == (polynomial == 0)
                if B % D == 0:
                    assert multiplication_resultant(profile) % D == 0


def test_positive_and_negative_cycle_regressions() -> None:
    legal, values = literal_accelerated_cycle(1, (2,))
    assert legal and values == [1, 1]
    legal, values = literal_accelerated_cycle(-5, (1, 2))
    assert legal and values == [-5, -7, -5]
    legal, values = literal_accelerated_cycle(-17, NEGATIVE_Q7)
    assert legal and values == [-17, -25, -37, -55, -41, -61, -91, -17]
