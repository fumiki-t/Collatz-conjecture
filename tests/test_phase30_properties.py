from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from src.phase30_search import direct_transport_audit, move_constant_cube, rotation_script
from src.phase28_search import transport_data


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_phase30_no_span_counterexample_and_exact_direct_bound() -> None:
    audit = direct_transport_audit((2, 2, 1, 3, 1, 1))
    assert (audit["area"], audit["J"], audit["transport_span"]) == (1, 1, 2)
    assert next(row for row in audit["factor_rows"] if row[0] == 4) == [4, 5, 10, 10, 11, 5]
    assert 5 + 1 * 4 == 9 < 10


def test_phase30_level_rotations_reconstruct_the_target_word() -> None:
    data = transport_data((2, 2, 1, 3, 1, 1), check_intervals=False)
    final, operations = rotation_script(data["baseline"], data["profile"])
    assert final == "1010110011"
    assert len(operations) == 1
    assert operations[0]["span"] == 2


def test_phase30_complete_corpus_counts_and_secondary_peak_checks() -> None:
    counts = load("phase30_transport_corpus.json")["counts"]
    assert counts == {
        "affected_start_checks": 141643,
        "component_rotation_checks": 9498,
        "cyclic_classes": 2214,
        "factor_width_checks": 45369,
        "minimum_rotations": 3101,
        "noncoprime_classes": 1417,
        "primitive_classes": 2186,
        "span_checks": 6202,
        "spine_charging_checks": 9303,
    }


def test_phase30_constant_improves_phase28_by_exact_cube_factor_four() -> None:
    scalar = load("phase30_scalar_certificates.json")
    new = [Fraction(*map(int, row)) for row in scalar["critical_constant_cube_interval"]]
    old = [Fraction(*map(int, row)) for row in scalar["phase28_constant_cube_interval"]]
    assert new == [4 * value for value in old]
    assert move_constant_cube(Fraction(2)) == Fraction(27, 2)
    assert scalar["critical_constant_decimal_box"] == [["1219077", "500000"], ["487631", "200000"]]
    assert scalar["near_extremal"]["area_over_transport"] == ["3", "2"]


def test_phase30_synthetic_profiles_charge_secondary_peaks() -> None:
    synthetic = load("phase30_synthetic_profiles.json")
    assert len(synthetic["rows"]) == 5
    for row in synthetic["rows"]:
        audit = row[-1]
        assert audit["nonspine_excess"] <= audit["descent_slack"]
        assert audit["nonspine_nonsingleton"] <= audit["nonspine_excess"]


def test_phase30_status_and_repair_boundaries() -> None:
    theory = load("phase30_theory.json")
    statuses = {key: row["status"] for key, row in theory["claims"].items()}
    assert statuses["P179"] == statuses["P184"] == "VERIFIED_THEOREM"
    assert statuses["NG39"] == "REFUTED"
    assert statuses["H172"] == statuses["H133"] == "OPEN"
    assert "not accepted" in theory["proposal_repair"]
    assert theory["proves_collatz"] is False


def test_phase30_mandatory_families_are_preserved() -> None:
    regressions = load("phase30_regressions.json")
    assert {row[0] for row in regressions["mandatory_families"]} == {
        "2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"
    }
    assert regressions["named_controls"]["negative_q7"] == [1, 1, 1, 2, 1, 1, 4]
