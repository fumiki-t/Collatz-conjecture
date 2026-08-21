from __future__ import annotations

from hypothesis import given, settings, strategies as st

from src.model import Node, affine_word, shortcut_step


def node_from_selectors(selectors: list[int]) -> Node:
    node = Node(0, 0, 0, 0, "")
    for selector in selectors:
        node = node.split()[selector]
    return node


def direct_iterate(n: int, steps: int) -> tuple[int, str]:
    value = n
    word: list[str] = []
    for _ in range(steps):
        word.append(str(value % 2))
        value = shortcut_step(value)
    return value, "".join(word)


@settings(max_examples=500, deadline=None)
@given(
    selectors=st.lists(st.integers(min_value=0, max_value=1), min_size=0, max_size=30),
    offset=st.integers(min_value=0, max_value=10_000),
)
def test_affine_node_semantics(selectors: list[int], offset: int) -> None:
    node = node_from_selectors(selectors)
    t = node.t_min + offset
    n, affine_image = node.value_at(t)
    direct_image, direct_word = direct_iterate(n, node.k)
    assert direct_image == affine_image
    assert direct_word == node.parity


@settings(max_examples=500, deadline=None)
@given(
    selectors=st.lists(st.integers(min_value=0, max_value=1), min_size=0, max_size=29),
    epsilon=st.integers(min_value=0, max_value=1),
    offset=st.integers(min_value=0, max_value=10_000),
)
def test_exact_split_rule(selectors: list[int], epsilon: int, offset: int) -> None:
    parent = node_from_selectors(selectors)
    child = parent.split()[epsilon]
    u = child.t_min + offset
    n, child_image = child.value_at(u)
    parent_t = 2 * u + epsilon
    assert parent_t >= parent.t_min
    parent_n, parent_image = parent.value_at(parent_t)
    assert parent_n == n
    assert shortcut_step(parent_image) == child_image


@settings(max_examples=300, deadline=None)
@given(st.text(alphabet="01", min_size=0, max_size=40), st.integers(min_value=1, max_value=10**12))
def test_affine_word_matches_direct_iteration(word: str, x: int) -> None:
    length, _odd_count, p, b = affine_word(word)
    numerator = p * x + b
    denominator = 1 << length
    if numerator % denominator:
        return
    value = x
    for bit in word:
        assert value % 2 == int(bit)
        value = shortcut_step(value)
    assert value == numerator // denominator
