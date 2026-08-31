from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from src.phase29_search import (
    arc_nonvanishing,
    coefficient_identity,
    residue_to_time_profile,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"


def load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_phase29_endpoint_identity_and_exact_arc_valuation() -> None:
    # The smallest coprime endpoint profile has the same polynomial 3-x used
    # by the NG38 endpoint regression; here gcd(q,L)=1 as P173 requires.
    q, length = 2, 3
    time_profile = residue_to_time_profile(q, length, (0, 1))
    identity = coefficient_identity(q, length, time_profile)
    assert identity["u"] == 1
    assert identity["c"] == 1
    assert identity["coefficients"] == (3, -1)

    audit = arc_nonvanishing(q, length, time_profile)
    assert audit["largest_gap_ties"] == 2
    assert all(row[4] == row[5] - row[6] for row in audit["cut_rows"])


def test_phase29_arc_counts_include_all_declared_ties() -> None:
    counts = load("phase29_arc_audit.json")["counts"]
    assert counts == {
        "critical_area_three_profiles": 521154,
        "critical_area_two_profiles": 7057,
        "largest_gap_cuts_checked": 93629,
        "largest_gap_tie_profiles": 43470,
        "noncritical_area_two_profiles": 204,
        "nonzero_arc_checks": 93629,
        "valuation_checks": 93629,
    }


def test_phase29_state_bound_covers_non_coprime_classes() -> None:
    state = load("phase29_state_bounds.json")
    counts = state["counts"]
    assert counts["maximum_state_checks"] == 5615
    assert counts["noncoprime_classes"] == 1417
    for row in state["equality_samples"]:
        orbit = Fraction(*map(int, row[6]))
        bound = Fraction(*map(int, row[8]))
        rough = Fraction(*map(int, row[9]))
        assert orbit == bound < rough


def test_phase29_farey_certificates_preserve_external_boundary() -> None:
    farey = load("phase29_farey_certificates.json")
    rows = {row["name"]: row for row in farey["rows"]}
    assert rows["E28"]["q_star"] == "971"
    assert rows["X02"]["q_star"] == "72057431991"
    assert all(Fraction(*map(int, row["upper_margin"])) > 0 for row in rows.values())
    assert farey["claims"] == {"P177": "VERIFIED_THEOREM", "P178": "CONDITIONAL"}


def test_phase29_regressions_retain_every_mandatory_family() -> None:
    regressions = load("phase29_regressions.json")
    labels = {row[0] for row in regressions["mandatory_families"]}
    assert labels == {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}
    assert regressions["named_controls"]["NG38"]["polynomial"] == [3, -1]


def test_phase29_never_promotes_open_or_conditional_claims() -> None:
    theory = load("phase29_theory.json")
    statuses = {key: row["status"] for key, row in theory["claims"].items()}
    assert statuses["H172"] == "OPEN"
    assert statuses["H133"] == "OPEN"
    assert statuses["P178"] == "CONDITIONAL"
    assert theory["proves_collatz"] is False
