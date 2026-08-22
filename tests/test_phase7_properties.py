from __future__ import annotations

from fractions import Fraction

from src.phase7_search import (
    K0,
    LEFT_PARENT,
    Q0,
    RIGHT_PARENT,
    affine_for_word,
    autocorrelation_data,
    contact_paths,
    fixed_q_positions,
    log_data,
    mechanical_factors,
    mixed_block_audit,
    symbolic_boundary_data,
)


def test_first_crossing_and_stern_brocot_certificate() -> None:
    data = log_data()
    candidate = Fraction(K0, Q0)
    left = Fraction(*LEFT_PARENT)
    right = Fraction(*RIGHT_PARENT)
    alpha = data["alpha_log2_3"]
    beta = data["beta_log2_3_plus_1_over_V"]
    alpha_low, alpha_high = (Fraction(*map(int, alpha[key])) for key in ("lower", "upper"))
    beta_low, beta_high = (Fraction(*map(int, beta[key])) for key in ("lower", "upper"))

    assert left < alpha_low < alpha_high < candidate < beta_low < beta_high < right
    assert candidate.numerator == LEFT_PARENT[0] + RIGHT_PARENT[0]
    assert candidate.denominator == LEFT_PARENT[1] + RIGHT_PARENT[1]
    assert data["direct_giant_powers_constructed"] is False


def test_boundary_contact_and_autocorrelation_sanity() -> None:
    logs = log_data()
    boundary = symbolic_boundary_data(logs)
    assert boundary["contact_density"]["minimum_contact_count"] == 31_327_720_462
    assert boundary["contact_density"]["density_exceeds_43_percent"] is True

    autocorrelation = autocorrelation_data(logs, boundary)
    rows = {row["h"]: row for row in autocorrelation["rows"]}
    assert rows[12]["cyclic_contact_pair_count_lower"] == 889_748_841
    assert rows[12]["contact_pair_count_lower"] == 889_748_829
    assert all(row["positive_lower_bound"] for row in rows.values())


def test_exact_mechanical_factor_and_macro_path_counts() -> None:
    logs = log_data()
    alpha = logs["alpha_log2_3"]
    alpha_low = Fraction(*map(int, alpha["lower"]))
    alpha_high = Fraction(*map(int, alpha["upper"]))
    factors = mechanical_factors(alpha_low, alpha_high)
    counts = [len(list(contact_paths(factor["f_values"]))) for factor in factors]

    assert len(factors) == 13
    assert counts == [2652, 2862, 3387, 3733, 4072, 5033, 5393, 8045, 8640, 9690, 10642, 11433, 11433]
    assert sum(counts) == 87_015


def test_selected_fixed_q_counts_and_mixed_family() -> None:
    assert {q: len(list(fixed_q_positions(q))) for q in (1, 3, 5)} == {1: 1, 3: 2, 5: 7}
    assert affine_for_word("11101") == (81, 73, 32)
    assert affine_for_word("1100") == (9, 5, 16)
    assert affine_for_word("111011100") == (729, 817, 512)

    audit = mixed_block_audit(64)
    assert audit["pairs_tested"] == 4096
    assert audit["paradoxical_endpoint_counterexamples"] == []
    assert audit["universal_claim"]["repository_status"] == "OPEN"
