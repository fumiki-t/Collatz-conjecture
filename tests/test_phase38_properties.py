from __future__ import annotations

import itertools
from fractions import Fraction

from src.phase38_search import (
    capacity_rows,
    canonical_source,
    fixed_weight_capacity,
    first_upcrossing,
    realize_word,
    renewal_blocks,
    v2,
    word_affine,
)


def test_fixed_weight_capacity_contains_every_small_image() -> None:
    for length in range(1, 9):
        modulus = 1 << length
        for width in sorted({1, 1 << (length // 2), modulus}):
            for start in (1, 10**12 + length):
                buckets: dict[int, set[int]] = {}
                for source in range(start, start + width):
                    for bits in itertools.product("01", repeat=length):
                        word = "".join(bits)
                        valid, endpoint = realize_word(source, word)
                        if valid:
                            buckets.setdefault(word.count("1"), set()).add(endpoint)
                for weight, images in buckets.items():
                    assert len(images) <= fixed_weight_capacity(length, weight, width)
                    assert all(isinstance(value, int) and value > 0 for value in images)
                assert sum(len(values) for values in buckets.values()) <= width
                assert width <= modulus


def test_recursive_capacities_have_selected_exact_rows() -> None:
    general, odd, rows = capacity_rows(50)
    expected = {
        0: (1, 1),
        10: (769, 507),
        20: (454346, 325836),
        30: (267261223, 196144373),
        40: (185532462462, 130669342714),
        49: (58609921347648, 42931358264194),
        50: (114046720881162, 86887448694020),
    }
    for length, pair in expected.items():
        assert (general[length], odd[length]) == pair
        assert rows[length] == [length, str(pair[0]), str(pair[1])]


def test_exact_reciprocal_comparisons() -> None:
    _, odd, _ = capacity_rows(500)
    finite = sum((Fraction(odd[n], 1 << n) for n in range(49, 501)), Fraction())
    tail = Fraction(1440 * 44**501, 45**501)
    assert finite + tail < Fraction(2079, 1000)
    assert 2 * 44**30 > 45**30
    assert 2079 * 405 < 842 * 1000
    assert Fraction(842, 1215) == Fraction(2, 3) + Fraction(2, 81) + Fraction(2, 1215)


def test_renewal_threshold_and_transfer_valuation() -> None:
    blocks = renewal_blocks(14)
    assert len(blocks) == 154
    for block in blocks:
        code = str(block["code"])
        forward = str(block["forward"])
        assert first_upcrossing(code)
        assert code == forward[::-1]
        c_value = Fraction(block["c"])
        r_value = Fraction(block["r"])
        assert 1 < c_value <= Fraction(3, 2)
        if forward == "1":
            assert r_value == 0
        else:
            assert forward.startswith("11") and forward.endswith("0")
            assert r_value >= Fraction(4, 9)
            assert v2(int(block["Cw"])) == int(block["initial_run"]) - 2


def test_mandatory_AB_witness_is_exact() -> None:
    word = "111011100"
    weight, correction = word_affine(word)
    assert (len(word), weight, correction) == (9, 6, 817)
    assert Fraction(-correction, 3**weight - 2 ** len(word)) == Fraction(-817, 217)
    source = canonical_source(word)
    valid, endpoint = realize_word(source, word)
    assert valid
    assert endpoint * 512 == 729 * source + 817
