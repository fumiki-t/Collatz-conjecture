from __future__ import annotations

from src.phase35_search import critical_length, decode_profile, safe_position_lists
from src.phase36_search import (decoder_mirror_intervals, event_polynomial,
                                root_geometry_row, scalar_audit)
from src.phase28_search import transport_data


def test_cycle_roots_localize_literal_changes_and_control_gaps() -> None:
    row = root_geometry_row((2, 1, 2, 1, 1))
    covered = {position for _, _, left, right in row["root_intervals"]
               for position in range(left, right)}
    assert set(row["changed_positions"]) <= covered
    for width, p0, target, distinct, gap_sum in row["factor_rows"]:
        assert p0 <= width + 1
        assert target <= p0 + row["root_span"] + row["root_count"] * (width - 1)
        if distinct:
            assert gap_sum <= width + 1
            assert max(row["complement_gaps"]) <= 2 * width


def test_positive_event_polynomial_exact_coefficients() -> None:
    exponents = (2, 1, 2, 1, 1)
    data = transport_data(exponents, check_intervals=False)
    event = event_polynomial(exponents, data["profile"][:-1], data["baseline"])
    assert min(event["coefficients"]) >= 0
    assert event["support"] == sum(value >= 2 for value in exponents)
    assert event["l1_norm"] == sum(
        2 ** data["profile"][index]
        for index, value in enumerate(data["baseline"]) if value == 2)


def test_decoder_cycle_orientation_counterexample_and_mirror_repair() -> None:
    q = 3
    length = critical_length(q)
    mechanical = tuple(critical_length(j) - 1 for j in range(q))
    positions = (0, 1, 2)
    source = (-sum(3 ** (q - 1 - j) * 2 ** positions[j] for j in range(q))
              * pow(3 ** q, -1, 2 ** length)) % (2 ** length)
    profile = decode_profile(q, source)
    assert profile == (0, 0, 1)
    assert decoder_mirror_intervals(profile, mechanical, length) == ((2, 3, 2, 5),)
    changed = set(mechanical) ^ set(positions)
    assert changed == {2, 3}
    assert changed <= set(range(2, 5))
    assert not changed <= set(range(3, 5))


def test_scalar_boundary_forces_short_roots_and_area_230_floor() -> None:
    audit = scalar_audit()
    assert audit["area_229_frontier"]["candidate_count"] == 1926
    assert audit["forced_exceptional_value"] == 92
    assert audit["allowed_root_profiles"] == [[1], [1, 1], [2, 1]]
    assert audit["root_capacity"] == {
        "U_max": 137, "R": 4, "C": 3,
        "rhs": 6017, "two_L": 7294, "margin": -1277,
    }
    assert audit["accepted_consequence"] == "critical reduced-profile area A>=230"
    assert audit["proves_collatz"] is False


def test_safe_position_enumerator_still_has_expected_small_boundary() -> None:
    assert len(list(safe_position_lists(8))) == 85
