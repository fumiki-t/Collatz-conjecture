from __future__ import annotations

from itertools import combinations

from src.phase6_search import (
    SANITY_RECORD_Q,
    build_certificate,
    coefficient_stopping_time,
    scan_hq,
    stopping_times,
)


def test_exact_hq_sanity_records() -> None:
    records, _ = scan_hq(1000)
    assert tuple(record.q for record in records) == SANITY_RECORD_Q
    assert [(row.q, row.K, row.floor) for row in records[:6]] == [
        (1, 2, 1),
        (3, 5, 4),
        (5, 8, 24),
        (17, 27, 108),
        (29, 46, 281),
        (41, 65, 867),
    ]


def test_p54_critical_word_inequalities_for_small_q() -> None:
    for q in range(1, 9):
        power = 3**q
        k_q = power.bit_length()
        b_max = sum(
            3 ** (q - 1 - j) * (1 << ((3**j).bit_length() - 1))
            for j in range(q)
        )
        for odd_positions in combinations(range(k_q), q):
            prefix_odd = 0
            safe = True
            for depth in range(1, k_q):
                if depth - 1 in odd_positions:
                    prefix_odd += 1
                safe = safe and 3**prefix_odd >= (1 << depth)
            if not safe or 3**q >= (1 << k_q):
                continue
            assert odd_positions[-1] != k_q - 1
            assert all(position <= (3**j).bit_length() - 1 for j, position in enumerate(odd_positions))
            affine_constant = sum(
                3 ** (q - 1 - j) * (1 << position)
                for j, position in enumerate(odd_positions)
            )
            assert affine_constant <= b_max


def test_stopping_time_and_exact_certificate_examples() -> None:
    assert stopping_times(703) == (81, 81)
    assert coefficient_stopping_time(27) == 59
    certificate = build_certificate(k=148, bound=2419, direct_threshold=16)
    assert certificate is not None
    assert certificate["claim"] == "M(148)>2419"
    assert certificate["rule_counts"]["BINARY_SPLIT"] > 0
    assert certificate["rule_counts"]["COEFF_CROSS"] > 0
