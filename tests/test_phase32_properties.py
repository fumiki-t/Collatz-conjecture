from __future__ import annotations

from fractions import Fraction

from src.phase32_search import EXPECTED_CLAIMS, c3_cube, cofactor_audit, theory_artifact, triple_hit_audit


def test_triple_hit_rows_are_exact_integer_certificates() -> None:
    audit = triple_hit_audit((4, 2, 1, 2, 1, 1))
    assert audit["widths"] == 11
    assert audit["distinct_widths"] > 0
    for row in audit["rows"]:
        width, _, _, _, _, _, types0, types1, types2, cap0, cap1, cap2, _, distinct, _, rhs = row
        assert types0 <= cap0
        assert types1 <= cap1
        assert types2 <= cap2
        if distinct:
            assert 3 * audit["L"] <= rhs
        assert width >= 1


def test_full_cofactor_and_positive_arc_are_kept_separate_from_integrality() -> None:
    audit = cofactor_audit((3, 1, 1, 3, 1, 1))
    assert audit["d"] == 2
    assert audit["cofactor_hit"] is True
    assert audit["arc"]["divisible"] is True
    assert audit["arc"]["strict_power_bound"] is True
    assert audit["integral_positive"] is False


def test_trivial_cycle_power_is_not_promoted_to_primitive_oscillation() -> None:
    audit = cofactor_audit((2, 2, 2))
    assert audit["integral_positive"] is True
    assert audit["primitive"] is False
    assert audit["oscillation"] is None


def test_noncritical_constant_is_exact() -> None:
    assert c3_cube(Fraction(2)) == Fraction(4725, 64)


def test_open_bounded_grid_boundary_and_no_overclaim() -> None:
    theory = theory_artifact()
    assert theory["claims"] == EXPECTED_CLAIMS
    assert theory["claims"]["H200"] == "OPEN"
    assert "explicit cutoff" in theory["H200"]["status_reason"]
    assert theory["proves_collatz"] is False
