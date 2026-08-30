from __future__ import annotations

from fractions import Fraction

from src.phase26_search import (
    critical_scalar_certificate,
    cyclic_factors,
    expanded_word,
    literal_swap_count,
    minimum_rotations,
    noncritical_scalar_certificate,
    reduced_profile,
)


def test_noncoprime_reduced_profile_is_literal_edit() -> None:
    data = reduced_profile((3, 1))
    assert (data["d"], data["q0"], data["L0"]) == (2, 1, 2)
    assert data["baseline"] == (2, 2)
    assert data["profile"] == (0, 1, 0)
    assert data["area"] == data["height"] == 1
    assert literal_swap_count(expanded_word(data["baseline"]), expanded_word((3, 1))) == 1


def test_all_minimum_rotations_have_same_area_and_height() -> None:
    rotations = minimum_rotations((1, 3, 2, 2))
    invariants = {(reduced_profile(row)["area"], reduced_profile(row)["height"]) for row in rotations}
    assert len(rotations) >= 1
    assert len(invariants) == 1


def test_coprime_profile_reduces_to_phase23_convention() -> None:
    data = reduced_profile((3, 1, 1))
    assert data["d"] == 1
    assert data["baseline"] == (2, 2, 1)
    assert data["area"] == 1
    assert data["height"] == 1


def test_cyclic_factor_perturbation_bound() -> None:
    base = expanded_word((2, 2, 1))
    target = expanded_word((3, 1, 1))
    area = literal_swap_count(base, target)
    for width in range(1, len(base) + 1):
        assert len(cyclic_factors(base, width)) <= width + 1
        assert len(cyclic_factors(target, width)) <= (area + 1) * (width + 1)


def test_critical_scalar_certificate_and_next_area_obstruction() -> None:
    value = critical_scalar_certificate()
    assert value["small_scan"]["passing_q"] == []
    assert value["large_q"]["base_positive"] is True
    assert value["large_q"]["step_positive"] is True
    obstruction = value["area_six_method_obstruction"]
    assert int(obstruction["left"]) > int(obstruction["right"])
    assert obstruction["positive_exponential_margin"] is False


def test_noncritical_and_x02_margins_are_exactly_positive() -> None:
    value = noncritical_scalar_certificate()
    assert Fraction(*map(int, value["noncritical_q_lower"]["direct_log_margin"])) > 0
    assert value["noncritical_q_lower"]["stronger_P134_product"] == 51_000_000
    assert value["internal_area"]["endpoint"]["positive_margin"] is True
    assert value["internal_area"]["endpoint"]["positive_derivative_margin"] is True
    assert value["x02"]["q_product_exceeds_endpoint"] is True
    assert value["x02"]["endpoint"]["positive_margin"] is True
    assert value["x02"]["endpoint"]["positive_derivative_margin"] is True
