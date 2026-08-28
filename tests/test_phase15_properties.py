from __future__ import annotations

from fractions import Fraction

from src.phase15_search import (
    enumerate_safe,
    literal_trace,
    safe_word,
    valley_data,
    word_constant,
)


def coefficient(word: str) -> Fraction:
    return Fraction(3 ** word.count("1"), 2 ** len(word))


def test_named_cross_q_dominators_coalesce_and_have_surplus() -> None:
    examples = (
        ("111110100", 287, "1", 273, 410),
        ("110110", 59, "1110110", 39, 76),
    )
    for target, source, ancestor, smaller, endpoint in examples:
        assert safe_word(target) and safe_word(ancestor)
        assert smaller < source
        assert coefficient(ancestor) >= coefficient(target)
        assert literal_trace(source, target)[-1] == endpoint
        assert literal_trace(smaller, ancestor)[-1] == endpoint


def test_q15_arbitrary_target_has_strict_safe_valley_suffix() -> None:
    target = "11101011111111101000001"
    arbitrary = "1010110111111101011100"
    valley = valley_data(arbitrary)
    assert valley == (4, 2, "110111111101011100")
    cut, _q_prefix, suffix = valley
    source = 937121
    target_source = 1874247
    trace = literal_trace(source, arbitrary)
    valley_source = trace[cut]
    assert valley_source == 527131 < target_source
    assert trace[-1] == literal_trace(target_source, target)[-1] == 3205946
    assert literal_trace(valley_source, suffix)[-1] == 3205946
    assert coefficient(suffix) > coefficient(target)


def test_safe_word_counts_and_gap_decoder_boundary() -> None:
    grouped = enumerate_safe(8)
    assert [len(grouped[q]) for q in range(1, 9)] == [1, 2, 3, 7, 12, 30, 85, 173]
    gap_counts = [sum("00" not in row.word for row in grouped[q]) for q in range(1, 9)]
    assert gap_counts == [1, 2, 3, 6, 10, 20, 40, 75]


def test_word_constant_affine_composition_on_adversarial_blocks() -> None:
    for word in ("1" * 8 + "0" * 3, "11101" * 3 + "1100" * 5, "110111110"):
        source_modulus = 1 << len(word)
        q = word.count("1")
        B = word_constant(word)
        residue = (-B * pow(3**q, -1, source_modulus)) % source_modulus
        source = residue or source_modulus
        endpoint = literal_trace(source, word)[-1]
        assert endpoint * source_modulus == 3**q * source + B


def test_right_suffix_needs_the_safety_qualification() -> None:
    # Surplus domination is preserved when the target plus common suffix stays safe.
    d, b, suffix = "111110100", "1", "1"
    assert safe_word(d + suffix)
    assert safe_word(b + suffix)
    assert coefficient(b + suffix) >= coefficient(d + suffix)
    # The theorem does not claim that every arbitrary suffix keeps d safe.
    assert not safe_word(d + "000000")
