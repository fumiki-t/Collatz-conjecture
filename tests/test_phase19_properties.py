from __future__ import annotations

from fractions import Fraction

from src.phase19_search import (
    adversarial_artifact,
    exponent_affine,
    periodic_record,
    source_lifts,
    stopped_tree,
)


def decode(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def test_accelerated_affine_coordinates_are_exact() -> None:
    row = exponent_affine((2, 1, 1))
    assert row["E"] == 4
    assert row["A"] == 29
    assert decode(row["coefficient"]) == Fraction(27, 16)
    assert decode(row["normalized_beta"]) == Fraction(29, 27)
    assert row["last_minimum_index"] == 1
    assert decode(row["valley_suffix_coefficient"]) == Fraction(9, 4)


def test_bounded_stopping_duality_uses_exact_mass() -> None:
    row = stopped_tree(5, Fraction(2))
    assert decode(row["plus_total_mass"]) == 1
    assert decode(row["minus_total_mass"]) == 1
    assert 3 * decode(row["E_plus_beta_T_cap_R"]) == decode(row["E_minus_T_cap_R"])
    assert row["ordinary_leaves"] > 0
    assert row["collapsed_geometric_tails"] > 0


def test_source_167_is_a_finite_zero_lift_falsifier() -> None:
    word = "11101101111110011110001010"
    row = source_lifts(word)
    assert row["exponents"] == [1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 3, 1, 1, 1, 4, 2, 2]
    assert row["residues"][-12:] == [167] * 12
    assert row["lifts"][-11:] == [0] * 11
    assert row["trailing_zero_lifts"] == 11


def test_periodic_rational_residue_bound_and_positive_exception() -> None:
    negative = periodic_record("1", 12)
    assert decode(negative["fixed_2adic_source"]) == -1
    assert negative["positive_integer_cycle_candidate"] is False
    assert all(
        not row["bound_applies"]
        or row["source_residue"] >= 1 << max(0, row["bits"] - negative["effective_loss_bits"])
        for row in negative["residues"]
    )

    positive = periodic_record("10", 12)
    assert decode(positive["fixed_2adic_source"]) == 1
    assert positive["positive_integer_cycle_candidate"] is True
    assert {row["source_residue"] for row in positive["residues"]} == {1}


def test_mandatory_adversarial_families_are_preserved() -> None:
    artifact = adversarial_artifact()
    names = {row["name"] for row in artifact["rows"]}
    assert {"A=11101", "B=1100", "AB", "A^4B^4"} <= names
    assert len(artifact["rows"]) == 63
    assert artifact["proves_collatz"] is False
