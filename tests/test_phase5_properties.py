from __future__ import annotations

from fractions import Fraction

from hypothesis import given, settings, strategies as st

from src.phase5_model import (
    DANGEROUS_CYCLES,
    affine_word,
    colored_graph,
    enumerate_return_templates,
    enumerate_simple_cycles,
    first_return_to_section,
    topological_audit,
)
from src.phase5_search import (
    direct_template_audit,
    return20_domination_audit,
    simple_cycle_audit,
)


def test_section_deleted_graph_and_template_count() -> None:
    audit = topological_audit()
    assert audit["acyclic"] is True
    assert audit["maximum_first_return_length"] == 9
    templates = enumerate_return_templates()
    assert len(templates) == 52
    assert len({(row.source_residue, row.word) for row in templates}) == 52


@settings(max_examples=500, deadline=None)
@given(
    template_index=st.integers(min_value=0, max_value=51),
    parameter=st.integers(min_value=0, max_value=10_000),
)
def test_return_template_family_against_direct(
    template_index: int, parameter: int
) -> None:
    template = enumerate_return_templates()[template_index]
    start = template.source_base + template.source_step * parameter
    expected = template.target_base + template.target_step * parameter
    returned, word, path = first_return_to_section(start)
    assert returned == expected
    assert word == template.word
    assert path == template.path


def test_complete_simple_cycle_classification() -> None:
    result = simple_cycle_audit()
    assert result["simple_cycle_count"] == 108
    assert set(result["noncontracting_words"]) == set(DANGEROUS_CYCLES)
    assert result["maximum_other_multiplier"] == [27, 32]
    rows = enumerate_simple_cycles()
    assert max(
        Fraction(row["A"], row["denominator"])
        for row in rows
        if not row["noncontracting"]
    ) == Fraction(27, 32)


def test_return20_domination_exact() -> None:
    cycles = simple_cycle_audit()
    result = return20_domination_audit(cycles["cycles"])
    assert result["verified"] is True
    assert result["simple_path_count"] == 25
    assert result["unique_noncontracting_word"] == "101"
    assert affine_word("101").multiplier == Fraction(9, 8)


def test_exhaustive_direct_phase5_audit_below_2_24() -> None:
    result = direct_template_audit(1 << 24, enumerate_return_templates())
    assert result["integers_checked"] == 2_485_513
    assert result["result"] == "all_direct_first_returns_match_exact_templates"


def test_colored_graph_is_closed_on_units() -> None:
    vertices = set(colored_graph())
    assert all(target in vertices for edges in colored_graph().values() for target in edges.values())
