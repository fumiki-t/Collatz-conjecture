import itertools
import math

from src.phase24_search import (
    area_three_profiles,
    area_two_profiles,
    critical_length,
    exponents_of_profile,
    polynomial_value,
    profile_valid,
    reduced_polynomial,
    slope_root,
    sparse_arc_certificate,
    strict_critical_constant_rows,
)


def weak_profiles(q: int, area: int):
    for cells in itertools.combinations_with_replacement(range(1, q), area):
        profile = [0] * q
        for cell in cells:
            profile[cell] += 1
        yield tuple(profile)


def test_profile_recurrence_and_area_two_classification() -> None:
    critical_count = 0
    for q in range(2, 61):
        L = critical_length(q)
        if L >= 2 * q or math.gcd(q, L) != 1:
            continue
        classified = set(area_two_profiles(q, L))
        brute = {profile for profile in weak_profiles(q, 2) if profile_valid(q, L, profile)}
        assert classified == brute
        assert all(exponents_of_profile(q, L, profile) is not None for profile in classified)
        assert all(max(profile) == 1 for profile in classified)
        critical_count += len(classified)
    assert critical_count == 7057


def test_area_three_shape_classification_on_small_slopes() -> None:
    for q in range(2, 31):
        L = critical_length(q)
        if L >= 2 * q or math.gcd(q, L) != 1:
            continue
        classified = set(area_three_profiles(q, L))
        brute = {profile for profile in weak_profiles(q, 3) if profile_valid(q, L, profile)}
        assert classified == brute


def test_reduced_polynomial_and_slope_root_equivalence() -> None:
    for q in range(3, 18):
        L = critical_length(q)
        D = 2**L - 3**q
        if L >= 2 * q or D <= 1 or math.gcd(q, L) != 1:
            continue
        gamma = slope_root(q, L, D)
        assert pow(gamma, q, D) == 2 % D
        assert pow(gamma, L, D) == 3 % D
        for profile in itertools.islice(area_two_profiles(q, L), 40):
            coefficients = reduced_polynomial(profile)
            reduced = polynomial_value(coefficients, gamma, D)
            original = sum(2**height * pow(gamma, residue, D) for residue, height in enumerate(profile)) % D
            assert (reduced == 0) == (original == 0)


def test_sparse_arc_divisibility_and_odd_nonvanishing() -> None:
    for q, L in ((5, 8), (7, 12), (11, 18), (13, 21)):
        if math.gcd(q, L) != 1:
            continue
        D = 2**L - 3**q
        gamma = slope_root(q, L, D)
        coefficients = [-gamma, 1] + [0] * (q - 2)
        assert polynomial_value(coefficients, gamma, D) == 0
        first = sparse_arc_certificate(coefficients, q, L)
        last = sparse_arc_certificate(coefficients, q, L, last_tie=True)
        assert first["integer_R"] % D == 0
        assert last["integer_R"] % D == 0

        odd = [0] * q
        odd[0], odd[q // 2], odd[-1] = 1, -3, 5
        certificate = sparse_arc_certificate(odd, q, L)
        assert certificate["all_nonzero_coefficients_odd"]
        assert certificate["integer_R"] % 2


def test_exact_threshold_certificates_are_strict() -> None:
    rows = strict_critical_constant_rows()
    assert [row[0] for row in rows] == [61, 62, 63, 64, 65]
    assert all(int(row[2]) < int(row[3]) for row in rows)
    assert 3**4 * 25**5 < 64**5
    assert 10**5 * 2 ** (4 * 22) < 2 ** (5 * 22 - 5)
    assert 12**4 * 2 ** (3 * 19) < 2 ** (4 * 19 - 4)


def test_fixed_area_support_and_norm_bounds() -> None:
    for area in range(1, 6):
        for profile in weak_profiles(9, area):
            coefficients = reduced_polynomial(profile)
            assert sum(value != 0 for value in coefficients) <= 2 * area + 1
            assert sum(abs(value) for value in coefficients) <= 3 * 2**area - 2
