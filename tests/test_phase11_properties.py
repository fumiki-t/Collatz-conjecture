from __future__ import annotations

from src.phase11_search import (
    affine_prefixes,
    cylinder_interval,
    direct_orbit,
    first_source_for_residue,
    height_free_no_go,
    hq_parameters,
    step,
)


def test_tail_minimum_residue_filter() -> None:
    for value in range(2, 2_000):
        if value % 2 == 0:
            assert step(value) < value
        elif value % 4 == 1:
            assert step(step(value)) < value


def test_height_free_witnesses_and_closed_forms() -> None:
    result = height_free_no_go(96)
    assert result["repository_status"] == "REFUTED"
    for k in range(3, 97):
        low = (1 << k) - 5
        high = (1 << k) - 1
        low_word, low_margins = direct_orbit(low, k)
        high_word, high_margins = direct_orbit(high, k)
        assert low_word == ("110" * ((k + 2) // 3))[:k]
        assert high_word == "1" * k
        assert min(low_margins) >= 0
        assert min(high_margins) >= 0
        assert high - low == 4


def test_exact_hq_endpoint_and_margin_interval_closure() -> None:
    final = hq_parameters(4_961)[-1]
    assert final["q"] == 4_961
    assert final["K_q"] == 7_863
    assert final["height_bound"] == 1_666_251

    depth = 6
    modulus = 1 << depth
    bound = 512
    for gap in range(1, 9):
        for residue in range(modulus):
            first = first_source_for_residue(residue, modulus)
            if first > bound - gap:
                continue
            last_t = (bound - gap - first) // modulus
            low, high, left_word, right_word, _positive, _negative, _zero = cylinder_interval(
                first, gap, last_t, depth, modulus
            )
            for parameter in range(last_t + 1):
                left = first + modulus * parameter
                right = left + gap
                actual_left_word, left_margins = direct_orbit(left, depth)
                actual_right_word, right_margins = direct_orbit(right, depth)
                assert actual_left_word == left_word
                assert actual_right_word == right_word
                assert (min(left_margins) >= 0 and min(right_margins) >= 0) == (low <= parameter <= high)
                for source, margins in ((left, left_margins), (right, right_margins)):
                    _word, prefixes = affine_prefixes(source, depth)
                    rebuilt = [((a - q) * source + b) // q for a, b, q in prefixes]
                    assert rebuilt == margins
