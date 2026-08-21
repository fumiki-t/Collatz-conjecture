from __future__ import annotations

from fractions import Fraction

from hypothesis import given, settings, strategies as st

from src.phase4_search import TRANSITIONS, code_kraft, direct_return_audit
from src.return9_model import (
    compose_with_template,
    first_return,
    formula_from_word,
    n_from_z,
    parametric_template,
    parametric_z_identity,
    return_templates,
    root_family,
    shortcut_step,
    z_from_n,
)


def test_mod9_colored_automaton() -> None:
    for residue, edges in TRANSITIONS.items():
        for bit, target in edges.items():
            representative = residue if residue % 2 == bit else residue + 9
            assert shortcut_step(representative) % 9 == target


def test_exact_kraft_identity_and_finite_overflow() -> None:
    covered, overflow = code_kraft(8)
    assert covered + overflow == 1
    assert covered < 1
    assert overflow > 0
    assert Fraction(1, 4) + Fraction(1, 16) + Fraction(1, 2) + Fraction(1, 8) + Fraction(1, 16) == 1


@settings(max_examples=500, deadline=None)
@given(
    c=st.sampled_from((0, 2, 4)),
    a=st.integers(min_value=1, max_value=30),
    b=st.integers(min_value=0, max_value=1),
    parameter=st.integers(min_value=0, max_value=10_000),
)
def test_parametric_return_formula_against_direct(
    c: int, a: int, b: int, parameter: int
) -> None:
    template = parametric_template(c, a, b)
    n, expected = template.values(parameter)
    actual, word = first_return(n)
    assert word == template.word
    assert actual == expected
    details = formula_from_word(n, word)
    assert details["return"] == actual
    v = template.v_residue + 12 * parameter
    z, z_next = parametric_z_identity(c, a, b, v)
    assert z_from_n(n) == z
    assert z_from_n(actual) == z_next
    assert n_from_z(z) == n


def test_c4_zero_run_branch() -> None:
    for b in (0, 1):
        template = parametric_template(4, 0, b)
        n, expected = template.values(7)
        assert first_return(n) == (expected, template.word)


@settings(max_examples=300, deadline=None)
@given(
    first_index=st.integers(min_value=0, max_value=27),
    second_index=st.integers(min_value=0, max_value=27),
    parameter=st.integers(min_value=0, max_value=1000),
)
def test_symbolic_return_composition(
    first_index: int, second_index: int, parameter: int
) -> None:
    dictionary = return_templates(4)
    parent = root_family(dictionary[first_index])
    child = compose_with_template(parent, dictionary[second_index], 0)
    if child is None:
        return
    start, endpoint = child.values(parameter)
    current = start
    words: list[str] = []
    for _ in range(2):
        current, word = first_return(current)
        words.append(word)
    assert current == endpoint
    assert tuple(words) == child.words


def test_required_positive_and_negative_examples() -> None:
    assert {n: first_return(n)[0] for n in (2, 11, 20, 47, 83, 128)} == {
        2: 2,
        11: 20,
        20: 2,
        47: 182,
        83: 47,
        128: 2,
    }
    assert {n: first_return(n)[0] for n in (-7, -61, -34, -25)} == {
        -7: -7,
        -61: -34,
        -34: -25,
        -25: -61,
    }


def test_exhaustive_direct_return_audit_below_2_24() -> None:
    result = direct_return_audit(1 << 24)
    assert result["section_integers_checked"] == 1_864_135
    assert result["result"] == "all_direct_returns_equal_formula_and_z_coordinate"
