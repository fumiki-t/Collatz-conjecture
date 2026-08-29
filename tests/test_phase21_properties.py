from __future__ import annotations

from fractions import Fraction

from src.phase21_search import (
    hq_values,
    literal_cycle,
    literal_lcp,
    previous_lcp_profile,
    shortcut,
    v2_nonzero,
    word_profile,
)
from verifier.verify_phase21 import direct_word_profile


def parity_prefix(value: int, length: int) -> tuple[int, ...]:
    bits = []
    for _ in range(length):
        bits.append(value % 2)
        value = shortcut(value)
    return tuple(bits)


def test_finite_parity_correspondence_for_signed_integers() -> None:
    for left in range(-24, 25):
        for right in range(-24, 25):
            for length in range(1, 9):
                same = parity_prefix(left, length) == parity_prefix(right, length)
                assert same == ((left - right) % (1 << length) == 0)


def test_reversed_key_profile_matches_all_pair_bruteforce() -> None:
    for source in (3, 7, 27, 167, 33019, 230631):
        states, _, _, _ = literal_cycle(source)
        maxima, witnesses = previous_lcp_profile(states, {})
        for later in range(1, len(states)):
            expected = max(v2_nonzero(states[later] - states[earlier]) for earlier in range(later))
            assert maxima[later] == expected
            assert literal_lcp(states[witnesses[later]], states[later]) == expected


def test_repeated_factor_height_is_strict_on_distinct_segments() -> None:
    for source in (3, 7, 27, 167, 33019, 230631):
        states, _, _, _ = literal_cycle(source)
        odd = 0
        for later, state in enumerate(states):
            for earlier in range(later):
                width = v2_nonzero(state - states[earlier])
                if width:
                    assert (1 << (width + odd)) < (source + 1) * 3**odd
            odd += state & 1


def test_generator_and_verifier_word_profiles_agree() -> None:
    for word in ("1", "110", "111011100", "110110110110", "11111111110000"):
        q = max(1, word.count("1"))
        numerator, denominator, _ = hq_values(q)[q]
        assert word_profile(word, numerator, denominator) == direct_word_profile(word, numerator, denominator)


def test_h89_certificate_cross_multiplication() -> None:
    for q in range(1, 18):
        numerator, denominator, _ = hq_values(q)[q]
        for width in range(1, 12):
            for odd in range(0, 8):
                exact = (1 << (width + odd)) * denominator >= (numerator + denominator) * 3**odd
                rational = Fraction(1 << (width + odd), 3**odd) >= Fraction(numerator, denominator) + 1
                assert exact == rational


def test_prefix_power_bound_without_logarithms() -> None:
    for source in (7, 27, 255, 1023, 262143):
        states, _, _, _ = literal_cycle(source)
        odd = 0
        for period in range(1, len(states)):
            odd += states[period - 1] & 1
            common = v2_nonzero(states[period] - source)
            exponent = 1 + common // period
            if exponent >= 2:
                assert 1 << ((exponent - 1) * period + odd) < (source + 1) * 3**odd
