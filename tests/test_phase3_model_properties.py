from __future__ import annotations

from hypothesis import given, settings, strategies as st

from src.model import shortcut_step
from src.phase3_model import LatticeNode, coefficient_survivors, find_reverse_merge


def direct(value: int, steps: int) -> int:
    for _ in range(steps):
        value = shortcut_step(value)
    return value


@settings(max_examples=300, deadline=None)
@given(
    selectors=st.lists(st.integers(min_value=0, max_value=1), min_size=0, max_size=24),
    offset=st.integers(min_value=0, max_value=10_000),
)
def test_lattice_binary_split_semantics(selectors: list[int], offset: int) -> None:
    node = LatticeNode(0, 0, 1, 0, 1, 2, "", ())
    for selector in selectors:
        node = node.binary_split()[selector]
    t = node.t_min + offset
    n, image = node.values(t)
    assert direct(n, node.steps) == image


@settings(max_examples=300, deadline=None)
@given(
    selectors=st.lists(st.integers(min_value=0, max_value=1), min_size=3, max_size=18),
    offset=st.integers(min_value=0, max_value=1000),
)
def test_ternary_split_is_disjoint_complete_and_exact(selectors: list[int], offset: int) -> None:
    node = LatticeNode(0, 0, 1, 0, 1, 2, "", ())
    for selector in selectors:
        node = node.binary_split()[selector]
    parent_t = node.t_min + offset
    eta = parent_t % 3
    u = (parent_t - eta) // 3
    child = tuple(node.ternary_children())[eta]
    assert u >= child.t_min
    assert child.values(u) == node.values(parent_t)
    assert [candidate.ternary_path[-1] for candidate in node.ternary_children()] == [0, 1, 2]


def test_phase3_preliminary_binary_count_and_merge_count() -> None:
    nodes = coefficient_survivors(20)
    assert len(nodes) == 27328
    assert sum(find_reverse_merge(node) is not None for node in nodes) == 11458


def test_phase3_preliminary_ternary_child_count() -> None:
    nodes = coefficient_survivors(20)
    children = [child for node in nodes for child in node.ternary_children()]
    assert len(children) == 81984
    assert sum(find_reverse_merge(child) is not None for child in children) == 50244
