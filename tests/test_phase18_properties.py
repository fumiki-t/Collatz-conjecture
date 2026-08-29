from __future__ import annotations

from fractions import Fraction

from src.phase18_search import (
    classify_graph,
    edge_record,
    graph_audit,
    mixed_schedule,
    normal_form_counterexample,
    path_record,
    word_affine,
)


def decode(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def test_affine_composition_and_normalized_beta_identity() -> None:
    length, odd, affine = word_affine("111011100")
    assert (length, odd, affine) == (9, 6, 817)
    row = path_record(["11101", "1100"])
    assert row["word"] == "111011100"
    assert row["B"] == 817
    assert decode(row["coefficient"]) == Fraction(729, 512)
    assert decode(row["normalized_beta"]) == Fraction(817, 729)


def test_all_three_graph_types_have_exact_small_witnesses() -> None:
    type_i = classify_graph(1, [edge_record(0, 0, "1", 0)])
    assert type_i["type"] == "I"
    assert type_i["components"][0]["kind"] == "positive"

    type_ii_edges = [
        edge_record(0, 0, "1", 0),
        edge_record(0, 1, "1", 1),
        edge_record(1, 1, "0", 2),
    ]
    type_ii = classify_graph(2, type_ii_edges)
    assert type_ii["type"] == "II"
    assert type_ii["positive_to_negative_witnesses"]

    type_iii = classify_graph(1, [edge_record(0, 0, "0", 0), edge_record(0, 0, "1", 1)])
    assert type_iii["type"] == "III"
    assert type_iii["components"][0]["kind"] == "mixed"


def test_ng30_counterfamily_refutes_only_the_single_switch_form() -> None:
    for k in (2, 4, 16):
        row = normal_form_counterexample(k)
        assert row["stage_signs"] == ["positive", "negative", "positive", "negative"]
        assert min(row["stage_lengths"]) > 0
        assert row["path"]["strictly_coefficient_safe"] is True
        assert 1 < decode(row["path"]["coefficient"]) < 2


def test_mixed_schedule_is_exact_and_does_not_claim_integrality() -> None:
    result = mixed_schedule(128, 8)
    assert result["positive_blocks"] + result["negative_blocks"] == 128
    assert decode(result["final"]["coefficient"]) > 1
    assert decode(result["final"]["normalized_beta"]) >= decode(result["symbolic_linear_beta_lower_bound"])
    assert "do not prove" in result["finite_boundary"]
    assert result["proves_collatz"] is False


def test_complete_small_graph_counts_are_stable() -> None:
    result = graph_audit(max_vertices=2, depth=6, cap=4)
    assert result["graphs_enumerated"] == 85
    assert sum(result["type_counts"].values()) == 85
    assert result["type_counts_by_vertices"]["1"] == {"I": 3, "III": 1}
    assert result["proves_collatz"] is False
