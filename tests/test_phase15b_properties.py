from __future__ import annotations

from fractions import Fraction

from src.phase15b_search import (
    canonical,
    endpoint_minima,
    enumerate_safe,
    first_upcrossing_blocks,
    literal_trace,
    renewal_decomposition,
    safe_path,
    safe_word,
    shifted_key,
    word_constant,
)


def coefficient(word: str) -> Fraction:
    return Fraction(3 ** word.count("1"), 2 ** len(word))


def defect(word: str) -> int:
    length, q, B, _source, _endpoint = canonical(word)
    return B + 2**length - 3**q


def test_cross_q_witness_coalesces_and_dominates_uniformly() -> None:
    target, ancestor = "111110100", "1"
    Ld, Qd, Bd, yd, endpoint = canonical(target)
    La, Qa, Ba, xa, endpoint_a = canonical(ancestor)
    assert (Qd - Qa, Ld - La) == (5, 8)
    assert 2 ** (Ld - La) * Ba - Bd == 3**Qa * -147
    assert literal_trace(yd, target)[-1] == endpoint == 410

    occurrence = xa + ((endpoint - endpoint_a) // 3**Qa) * 2**La
    assert occurrence == 273 < yd
    assert 3 ** (Qd - Qa) * yd == 2 ** (Ld - La) * occurrence - 147
    assert coefficient(ancestor) >= coefficient(target)
    for index in range(8):
        later_endpoint = endpoint + index * 3**Qd
        target_source = yd + index * 2**Ld
        ancestor_source = xa + ((later_endpoint - endpoint_a) // 3**Qa) * 2**La
        assert ancestor_source < target_source
        assert literal_trace(target_source, target)[-1] == later_endpoint
        assert literal_trace(ancestor_source, ancestor)[-1] == later_endpoint


def test_shifted_defect_composition_valuation_and_jump() -> None:
    for left, right in (("11101", "1100"), ("1", "111100"), ("1110", "1")):
        combined = left + right
        assert defect(combined) == 3 ** right.count("1") * defect(left) + 2 ** len(left) * defect(right)

    grouped = enumerate_safe(8)
    for rows in grouped.values():
        for item in rows:
            if "0" not in item.word:
                continue
            run = len(item.word) - len(item.word.lstrip("1"))
            D = defect(item.word)
            assert D % 2**run == 0
            assert (D // 2**run) % 2 == 1
            assert shifted_key(item) == (item.q, item.length - run, D // 2**run)

    assert defect("111100") == 2 * defect("11101")
    assert literal_trace(15, "111100")[-1] == literal_trace(7, "11101")[-1] == 20
    assert 15 + 1 == 2 * (7 + 1)


def test_first_upcrossing_reversals_and_exact_beatty_support() -> None:
    blocks = first_upcrossing_blocks(17)
    for item in blocks:
        reverse = item.word[::-1]
        for length in range(1, len(reverse)):
            assert 3 ** reverse[:length].count("1") <= 2**length
        assert 3 ** reverse.count("1") > 2 ** len(reverse)
        assert safe_word(item.word)
        if item.word != "1":
            assert item.length == (3**item.q).bit_length() - 1

    supported = {item.q for item in blocks if item.word != "1"}
    expected = {
        q
        for q in range(2, 18)
        if (3**q).bit_length() - (3 ** (q - 1)).bit_length() == 2
    }
    assert supported == expected

    for rows in enumerate_safe(10).values():
        for item in rows:
            pieces = renewal_decomposition(item.word)
            assert "".join(pieces) == item.word
            for piece in pieces:
                reverse = piece[::-1]
                assert safe_word(piece)
                assert 3 ** reverse.count("1") > 2 ** len(reverse)
                assert all(3 ** reverse[:length].count("1") <= 2**length for length in range(1, len(reverse)))


def test_small_source_scan_has_no_endpoint_height_truncation() -> None:
    minima, stats = endpoint_minima(10_000)
    assert stats["odd_sources_scanned"] == 5_000
    assert stats["maximum_endpoint"] > 10_000
    for endpoint, source in list(sorted(minima.items()))[:200]:
        assert source <= 10_000
        assert any(value == endpoint for _step, value, _bits, _three in safe_path(source))


def test_affine_constant_on_mandatory_mixed_family() -> None:
    for r in range(1, 5):
        for s in range(1, 5):
            word = "11101" * r + "1100" * s
            B = word_constant(word)
            q = word.count("1")
            modulus = 2 ** len(word)
            source = (-B * pow(3**q, -1, modulus)) % modulus or modulus
            endpoint = literal_trace(source, word)[-1]
            assert endpoint * modulus == 3**q * source + B
