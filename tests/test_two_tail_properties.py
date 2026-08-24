from __future__ import annotations

from src.two_tail_search import parity_word, step, v2


def advance(start: int, depth: int) -> tuple[int, int]:
    value = start
    odd_count = 0
    for _ in range(depth):
        odd_count += value & 1
        value = step(value)
    return value, odd_count


def test_low_l_bits_determine_next_l_parities() -> None:
    for length in range(1, 9):
        modulus = 1 << length
        for residue in range(modulus):
            expected = parity_word(residue, length)
            for lift in range(1, 5):
                assert parity_word(residue + lift * modulus, length) == expected


def test_exact_branch_gap_formula_on_small_pairs() -> None:
    for n in range(2, 129):
        for m in range(n + 1, min(n + 33, 161)):
            depth = v2(m - n)
            left, left_odd = advance(n, depth)
            right, right_odd = advance(m, depth)
            assert left_odd == right_odd
            assert right - left == 3**left_odd * ((m - n) >> depth)
            assert (right - left) & 1
            assert (left & 1) != (right & 1)
