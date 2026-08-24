from __future__ import annotations

import math
from pathlib import Path

from src.phase10_search import (
    RIGHT_PARENT,
    V,
    W,
    coefficient_stopping_time,
    finite_gap_cycle_audit,
    rational_cycle_check,
    renewal_barrier_data,
    spacing_layers,
)


def test_gap_residue_and_quotient_identity_for_small_layers() -> None:
    layers, cycles, total = finite_gap_cycle_audit(8)
    assert total == 141
    assert sum(row["enumerated_words"] for row in layers) == total
    assert all(row["phase10_near_box_count"] == 0 for row in layers)
    assert all(row["all_sources_are_cycle_minima"] for row in cycles)
    for layer in layers:
        for key in ("minimum_d_record", "maximum_d_record"):
            row = layer[key]
            assert row["B"] == row["D"] * row["r2"] + (row["D"] + 3 ** layer["q"]) * row["d"]
            assert row["rho"] == row["d"] % row["D"]
            assert row["m"] == (row["B"] - (row["D"] + 3 ** layer["q"]) * row["rho"]) // row["D"]
            assert row["gcd_B_D"] == math.gcd(row["d"], row["D"])


def test_near_box_mod_four_consequence() -> None:
    n, x = 7, 19
    rho = x - n
    assert n % 4 == x % 4 == 3
    assert 0 < rho <= W
    assert rho % 4 == 0


def test_right_parent_renewal_margin_is_exactly_positive() -> None:
    data = renewal_barrier_data(Path("artifacts"))
    margins = data["exact_margins"]
    assert margins["all_lower_bounds_strictly_positive"] is True
    assert data["stern_brocot_certificate"]["right_upper_parent"] == list(RIGHT_PARENT)
    assert V > W


def test_spacing_layers_match_direct_definition() -> None:
    bound = 250
    layers, _digest, _records = spacing_layers(bound)
    stopping = {start: coefficient_stopping_time(start) for start in range(2, bound + 1)}
    for row in layers:
        safe = [start for start in range(2, bound + 1) if stopping[start] > row["k"]]
        expected = min((right - left for left, right in zip(safe, safe[1:])), default=None)
        assert row["delta"] == expected


def test_safe_pair_sets_are_nested_and_gaps_merge() -> None:
    layers, _digest, _records = spacing_layers(500)
    assert all(next_row["safe_count"] <= row["safe_count"] for row, next_row in zip(layers, layers[1:]))
    defined = [row for row in layers if row["delta"] is not None]
    assert all(next_row["delta"] >= row["delta"] for row, next_row in zip(defined, defined[1:]))


def test_rational_cycle_minimum_for_B_word() -> None:
    minimum, strict, terminal = rational_cycle_check("1100", total_constant=5, difference=7)
    assert minimum >= 0
    assert strict >= 1
    assert terminal == 0


def test_phase10_search_and_verifier_are_import_independent() -> None:
    source = Path("verifier/verify_phase10.py").read_text(encoding="utf-8")
    assert "from src.phase10_search import" not in source
    assert "import src.phase10_search" not in source
