from __future__ import annotations

import math
from fractions import Fraction

from src.phase12_search import (
    all_contact_artifact,
    floor_j_log2_3,
    inverse_parity_residue,
    parity_word,
    safe_prefix_segment,
)


def test_exact_normalization_recurrence_and_residue_packing() -> None:
    for start in range(3, 5_000, 4):
        row = safe_prefix_segment(start, 64)
        odds = row["odd_values"]
        positions = row["odd_positions"]
        assert len(odds) == len(set(odds))
        y_value = Fraction(start)
        for index, (odd, position) in enumerate(zip(odds, positions)):
            assert y_value == Fraction((1 << position) * odd, 3**index)
            assert floor_j_log2_3(index) >= position
            if index:
                assert math.gcd(odd, 6) == 1
            y_value *= Fraction(3 * odd + 1, 3 * odd)
        ordered = sorted(odds[1:])
        for rank in range(2, len(ordered)):
            assert ordered[rank] >= start + 3 * (rank - 1)


def test_first_crossing_endpoint_is_strictly_below_normalized_height() -> None:
    found = 0
    for start in range(3, 20_000, 4):
        row = safe_prefix_segment(start, 64)
        crossing = row["crossing"]
        if crossing is None:
            continue
        y_q = Fraction(crossing["Y_q"]["numerator"], crossing["Y_q"]["denominator"])
        assert crossing["endpoint"] < y_q
        assert crossing["displacement"] < y_q - start
        found += 1
    assert found > 0


def test_all_contact_finite_prefixes_have_exact_residues() -> None:
    artifact = all_contact_artifact(128)
    assert artifact["P73"]["repository_status"] == "VERIFIED_THEOREM"
    for q in range(1, 65):
        length = floor_j_log2_3(q)
        positions = {floor_j_log2_3(index) for index in range(q)}
        word = "".join("1" if index in positions else "0" for index in range(length))
        residue, _coefficient, _constant = inverse_parity_residue(word)
        representative = residue or 1 << length
        assert parity_word(representative, length) == word
        assert word.count("1") == q


def test_mod_six_density_input_is_exact_and_sharp() -> None:
    for blocks in range(1, 100):
        admissible = [value for value in range(1, 6 * blocks + 1) if math.gcd(value, 6) == 1]
        assert len(admissible) == 2 * blocks
    for start in range(1, 30):
        ordered = [value for value in range(start, start + 300) if math.gcd(value, 6) == 1]
        for rank in range(2, len(ordered)):
            assert ordered[rank] >= start + 3 * (rank - 1)
