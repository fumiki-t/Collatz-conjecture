from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from src.phase8_search import (
    BASE_CASES,
    affine_word,
    c02_base_case,
    enumerate_contracting_words,
    enumerate_first_crossings,
    parity_residue_bruteforce,
)


def test_c02_sign_identity_property() -> None:
    for r in range(1, 7):
        for s in range(1, 9):
            for u in (4, 12, 28, 100):
                p = 81**r * 9**s
                q = 32**r * 16**s
                x = Fraction(32**r * u - 73, 49)
                after_a = Fraction(81**r * u - 73, 49)
                endpoint = after_a
                for _ in range(s):
                    endpoint = Fraction(9 * endpoint + 5, 16)
                left = 49 * q * (endpoint - x)
                right = 32**r * (u * (p - q) + 108 * (16**s - 9**s))
                assert left == right


def test_c02_crt_base_cases_are_reconstructed() -> None:
    expected = [
        (1, 2, 10_156, 6_631, 5_312),
        (1, 3, 47_788, 31_207, 14_060),
        (1, 4, 3_058_348, 1_997_287, 506_135),
        (2, 4, 1_663_212, 34_757_735, 22_295_216),
        (3, 5, 13_460_268, 9_001_348_199, 8_221_012_670),
        (3, 6, 681_403_180, 455_677_946_983, 234_098_318_018),
    ]
    observed = []
    for r, s in BASE_CASES:
        case = c02_base_case(r, s)
        assert case["C02_core_margin"] > 0
        assert case["least_u"] * 81**r % 16**s == 108 % 16**s
        assert case["least_u"] * 32**r % 49 == 73 % 49
        observed.append((r, s, case["least_u"], case["least_source"], case["endpoint"]))
    assert observed == expected


def test_exact_octave_normalization_on_a_real_prefix() -> None:
    source = 27
    current = source
    odd_positions: list[int] = []
    additive = 0
    odd_count = 0
    for position in range(20):
        if current % 2:
            odd_positions.append(position)
            # Before the odd shortcut step at position d_j,
            # T^d(N)=(3^j*N+B_j)/2^d.
            lhs = Fraction(3**odd_count * source + additive, 2**position)
            assert lhs == current
            current = (3 * current + 1) // 2
            additive = 3 * additive + 2**position
            odd_count += 1
        else:
            current //= 2
    assert odd_positions[:4] == [0, 1, 3, 4]


def test_short_excursion_affines_and_endpoint_parity_residues() -> None:
    rows = [
        ("1", "11", (3, 1, 2)),
        ("10", "101", (3, 1, 4)),
        ("110", "1101", (9, 5, 8)),
        ("1100", "11001", (9, 5, 16)),
    ]
    for word, full_word, expected_map in rows:
        assert affine_word(word) == expected_map
        residue = parity_residue_bruteforce(full_word)
        assert 0 <= residue < 2 ** len(full_word)


def test_bounded_ab_enumerations_have_expected_small_counts() -> None:
    contracting, contracting_counts = enumerate_contracting_words(6)
    crossings, crossing_counts = enumerate_first_crossings(8)
    assert len(contracting) == 39
    assert sum(1 for record in contracting if int(record[4]) > 0 and int(record[5]) > 0) == 33
    assert len(crossings) == 11
    assert contracting_counts == [1, 1, 4, 5, 6, 22]
    assert {index + 1: count for index, count in enumerate(crossing_counts) if count} == {
        1: 1,
        3: 1,
        6: 2,
        8: 7,
    }
    assert all(int(record[10]) < int(record[9]) for record in contracting)


def test_search_and_verifier_are_import_independent() -> None:
    verifier = Path("verifier/verify_phase8.py").read_text(encoding="utf-8")
    assert "from src.phase8_search import" not in verifier
    assert "import src.phase8_search" not in verifier
