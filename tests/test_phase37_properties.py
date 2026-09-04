from __future__ import annotations

import itertools

from src.phase37_search import (
    canonical_source,
    coefficient_compare,
    correction_maximum,
    induction_certificate,
    realizes,
    shortcut_trace,
    word_data,
)


def test_fixed_odd_count_correction_maximum_is_right_justified() -> None:
    for length in range(1, 10):
        for odd_count in range(length + 1):
            rows = []
            for positions in itertools.combinations(range(length), odd_count):
                bits = tuple(int(index in positions) for index in range(length))
                rows.append((word_data(bits)[1], bits))
            maximum, word = max(rows)
            assert maximum == correction_maximum(length, odd_count)
            assert word == (0,) * (length - odd_count) + (1,) * odd_count


def test_parity_vector_has_one_exact_residue() -> None:
    for length in range(1, 9):
        modulus = 1 << length
        residues = set()
        for bits in itertools.product((0, 1), repeat=length):
            residue = canonical_source(bits)
            source = residue or modulus
            valid, endpoint = realizes(source, bits)
            odd_count, correction = word_data(bits)
            assert valid
            assert endpoint * modulus == 3**odd_count * source + correction
            residues.add(residue)
        assert residues == set(range(modulus))


def test_image_diameter_is_uniform_at_large_translations() -> None:
    for length in range(2, 10):
        width = 1 << length
        for start in (1, 10**40 + length, (1 << 240) + 7 * length):
            groups: dict[int, list[int]] = {}
            for source in range(start, start + width):
                values, bits = shortcut_trace(source, length)
                groups.setdefault(sum(bits), []).append(values[-1])
            for odd_count, endpoints in groups.items():
                assert max(endpoints) - min(endpoints) < 2 * 3**odd_count


def test_explicit_induction_certificate_has_exact_boundary() -> None:
    certificate = induction_certificate()
    assert certificate["rational_parameters"] == {
        "theta": [14, 23], "rho": [29, 30], "constant": 32, "N0": 135,
    }
    assert 24**690 * 3 ** (406 * 134) > 2 ** (667 * 134)
    assert 24**690 * 3 ** (406 * 135) <= 2 ** (667 * 135)
    assert certificate["proves_collatz"] is False


def test_reversed_first_upcrossing_blocks_are_strictly_safe() -> None:
    codes = ("1", "011", "001111", "010111")
    word = "".join(code[::-1] for code in codes)
    bits = tuple(map(int, word))
    odd_prefix = [0]
    for bit in bits:
        odd_prefix.append(odd_prefix[-1] + bit)
    boundaries = [0]
    for code in codes:
        boundaries.append(boundaries[-1] + len(code))
    for boundary in boundaries[:-1]:
        for later in range(boundary + 1, len(bits) + 1):
            assert coefficient_compare(
                (odd_prefix[later] - odd_prefix[boundary], later - boundary),
                (0, 0),
            ) > 0
