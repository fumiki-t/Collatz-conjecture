from __future__ import annotations

from fractions import Fraction

from src.phase17_search import (
    EXPECTED_COUNTS,
    THRESHOLDS,
    crt_intervals,
    direct_audit,
    lifted_multiplier,
    predecessor_artifact,
    pressure_artifact,
    suffix_code_artifact,
    supercritical_words,
)


def decode(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def test_inverse_words_and_right_continuous_crt_envelope_are_exact() -> None:
    words = supercritical_words()
    assert len(words) == 23
    for row in words:
        exponents = tuple(row["exponents"])
        assert row["E"] == sum(exponents)
        assert 3 ** row["r"] > 2 ** row["E"]
        assert row["endpoint_residue"] % 3
        assert decode(row["beta"]) > 0
    rows = crt_intervals(lifted_multiplier(words))
    assert [row["count"] for row in rows] == EXPECTED_COUNTS
    # Equality is admitted by design, so the table is a safe upper envelope.
    assert 1 in rows[0]["allowed_residues"]
    assert [decode(row["left"]) for row in rows] == THRESHOLDS


def test_packing_constants_and_270_margin_are_positive() -> None:
    artifact = predecessor_artifact()
    assert decode(artifact["continuous_capacity_below_81N_over_16"]) == Fraction(23093, 20736)
    assert decode(artifact["discrete_reciprocal_error_coefficient"]) == Fraction(18344, 27)
    certificate = artifact["psi_270_log_certificate"]
    assert decode(certificate["log2_coefficient"]) == Fraction(7, 3)
    assert decode(certificate["exact_positive_margin"]) > 0
    assert artifact["proves_collatz"] is False


def test_direct_audit_uses_exclusive_bound_and_finite_claim_only() -> None:
    result = direct_audit(5000)
    assert result["source_interval"] == [1, 5000]
    assert result["sources_checked"] == 4999
    assert result["all_reach_one"] is True
    assert result["maximum_shortcut_steps"] == {"steps": 150, "least_source": 3711}
    assert result["maximum_peak"] == {"value": 4_076_810, "least_source": 4591}
    assert result["proves_collatz"] is False


def test_pressure_ceiling_is_scoped_and_below_360469() -> None:
    result = pressure_artifact()
    mechanism = result["coefficient_only_mechanism"]
    assert mechanism["status"] == "REFUTED"
    assert decode(mechanism["A_min_at_upper_root_bracket"]) < Fraction(360469, 1000)
    assert "fixed ordinary source" in mechanism["scope"][-1]
    assert "does not apply" in result["what_this_result_does_not_prove"]


def test_suffix_code_is_decodable_but_no_pressure_trend_is_claimed() -> None:
    result = suffix_code_artifact(3)
    assert result["code_size"] == 11
    assert decode(result["second_moment_at_s_2"]) == Fraction(1539, 2048)
    for count in range(1, 4):
        row = result["finite_concatenation_audit"][str(count)]
        assert row["addresses"] == row["distinct_endpoint_residues"] == 11**count
    assert result["trend_boundary"].startswith("No convergence or monotonicity")
