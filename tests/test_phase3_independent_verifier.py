from __future__ import annotations

import pytest

from src.phase3_model import coefficient_survivors, find_reverse_merge
from verifier.verify_phase3 import Expected, check_reverse_merge, ternary_children


def as_expected(node) -> Expected:
    return Expected(
        node.steps,
        node.r,
        node.M,
        node.y,
        node.A,
        node.t_min,
        node.parity,
        node.ternary_path,
    )


def test_independent_forward_reconstruction_accepts_search_witness() -> None:
    node = next(
        node for node in coefficient_survivors(10) if find_reverse_merge(node) is not None
    )
    witness = find_reverse_merge(node)
    assert witness is not None
    assert check_reverse_merge(as_expected(node), list(witness.exponents), 18) == (
        witness.odd_steps,
        witness.exponent_sum,
    )


def test_independent_checker_rejects_bad_reverse_path() -> None:
    node = coefficient_survivors(10)[0]
    with pytest.raises(ValueError):
        check_reverse_merge(as_expected(node), [18], 18)


def test_independent_ternary_split_matches_exact_semantics() -> None:
    node = coefficient_survivors(10)[7]
    search_children = tuple(node.ternary_children())
    checker_children = ternary_children(as_expected(node))
    assert [child.compact() for child in checker_children] == [
        child.compact() for child in search_children
    ]
