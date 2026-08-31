from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from src.phase31_search import double_hit_audit, hit_constant_cube, static_inventory


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_phase31_static_extraction_is_disjoint_and_exact() -> None:
    inventory = static_inventory((3, 1, 3, 1))
    assert (inventory["J"], inventory["E"], inventory["K"]) == (2, 1, 1)
    assert inventory["residual_word"] == "10011010"
    assert inventory["actual_word"] == "10011001"
    assert inventory["anchors"] == ((6, 7),)


def test_phase31_double_hit_rows_obey_all_exact_bounds() -> None:
    audit = double_hit_audit((3, 1, 2, 1, 1))
    for row in audit["factor_rows"]:
        width, contexts, exact_context, area_context, low_types, b1 = row[:6]
        assert contexts <= exact_context <= area_context
        assert low_types <= b1
        if row[7]:
            assert 2 * audit["L"] <= row[10]
        assert row[12] <= 2 * row[11]
        assert row[9] == audit["K"] * (width + 1)


def test_phase31_complete_corpus_counts() -> None:
    counts = load("phase31_transport_corpus.json")["counts"]
    assert counts == {
        "context_width_checks": 45369,
        "cyclic_classes": 2214,
        "distinct_factor_checks": 27832,
        "exact_grid_cases": 109,
        "exceptional_components": 8218,
        "extracted_swaps": 1280,
        "grid_bound_checks": 45369,
        "grid_recurrence_steps": 673303,
        "low_type_checks": 45369,
        "minimum_rotations": 3101,
        "noncoprime_classes": 1417,
        "primitive_classes": 2186,
        "static_reconstructions": 3101,
    }


def test_phase31_constant_improves_phase30_by_exact_cube_factor_four() -> None:
    scalar = load("phase31_scalar_certificates.json")
    new = [Fraction(*map(int, row)) for row in scalar["critical_constant_cube_interval"]]
    old = [Fraction(*map(int, row)) for row in scalar["phase30_constant_cube_interval"]]
    assert new == [4 * value for value in old]
    assert hit_constant_cube(Fraction(2)) == 54
    assert scalar["near_equality"]["area_over_J_plus_sigma"] == ["3", "2"]


def test_phase31_synthetic_profiles_cover_requested_geometries() -> None:
    rows = load("phase31_synthetic_profiles.json")["rows"]
    assert {row[0] for row in rows} == {
        "tall",
        "plateau",
        "isolated",
        "near-extremal",
        "seven-grid",
        "width-two",
        "multiple-peaks",
        "near-grid-singletons",
        "residual-heavy",
    }
    assert all(len(row[-1]["factor_rows"]) == 10 for row in rows)


def test_phase31_ng40_prevents_global_grid_overclaim() -> None:
    regressions = load("phase31_regressions.json")
    model = regressions["NG40_normalized_countermodel"]
    assert model["slope"] == 2
    assert model["k"] == 0
    assert model["u_over_q"] == 2
    assert "does not imply global approximate-grid invariance" in model["interpretation"]


def test_phase31_status_and_external_boundary() -> None:
    theory = load("phase31_theory.json")
    statuses = {key: row["status"] for key, row in theory["claims"].items()}
    assert statuses["P185"] == statuses["P190"] == "VERIFIED_THEOREM"
    assert statuses["E43"] == "VERIFIED_FINITE"
    assert statuses["NG40"] == "REFUTED"
    assert statuses["H172"] == statuses["H133"] == "OPEN"
    assert "EXT17" in theory["dependencies"]["P188"]
    assert theory["proves_collatz"] is False
