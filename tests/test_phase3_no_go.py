from __future__ import annotations

from itertools import product

from src.phase3_search import no_go_language_audit


def test_long_110_or_111_language_is_coefficient_nonshrinking() -> None:
    for choices in product(("110", "111"), repeat=8):
        word = "".join(choices)
        odd_count = 0
        for depth, bit in enumerate(word, start=1):
            odd_count += bit == "1"
            assert 3**odd_count >= 2**depth


def test_no_go_audit_does_not_use_periodic_dictionary() -> None:
    result = no_go_language_audit(10)
    assert result["words_exhaustively_checked"] == 1024
    assert result["coefficient_violations"] == []
    assert result["strictly_nonperiodic_words"] > 0
    assert result["periodic_dictionary_used_for_closure"] is False
