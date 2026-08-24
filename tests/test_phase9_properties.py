from __future__ import annotations

from fractions import Fraction
from pathlib import Path

from src.phase9_search import (
    DMAX,
    Q0,
    affine_word,
    audit_first_crossing_layer,
    paradoxical_tree_data,
)


def test_forced_contact_recurrence_and_closure_property() -> None:
    for contact in (0, 1):
        for increment in (1, 2):
            for next_contact in (0, 1):
                defect = 1 - contact
                next_defect = 1 - next_contact
                odd_gap = increment + defect - next_defect
                closure_ok = not (contact == 1 and increment == 1 and next_contact == 0)
                if closure_ok:
                    assert odd_gap >= 1
                if contact == 1 and increment == 1 and closure_ok:
                    assert next_contact == 1
                    assert odd_gap == 1


def test_improved_gap_formula_exactly() -> None:
    contacts = 31_327_720_462
    long_gaps = (Q0 - contacts) // 2
    raw = (contacts - 1) - long_gaps
    assert raw == 10_962_864_697
    assert raw - 10 == 10_962_864_687

    closure_contacts = 35_251_435_772
    closure_raw = (closure_contacts - 1) - (Q0 - closure_contacts) // 2
    assert closure_raw == 16_848_437_662
    assert closure_raw - 10 == 16_848_437_652


def test_near_return_displacement_identity() -> None:
    for source in (27, 703, 10_000):
        for displacement in (0, 2, 100):
            delta = Fraction(7, 1000)
            s_value = 3 * source * delta + 3 * (1 + delta) * displacement
            rebuilt = (s_value / 3 - source * delta) / (1 + delta)
            assert rebuilt == displacement


def test_endpoint_congruence_crt_classes() -> None:
    allowed = [value for value in range(36) if value % 4 == 3 and value % 9 in (1, 7)]
    assert allowed == [7, 19]
    assert DMAX < 2**32


def test_g4_reverse_predecessor_witness() -> None:
    # G4's full endpoint-parity word is 11001.  Search one exact source in a
    # generic first-octave interval and verify the forbidden predecessor.
    coefficient, constant, denominator = affine_word("1100")
    found = False
    source_scale = 10_000
    for source in range(source_scale, 2 * source_scale):
        numerator = coefficient * source + constant
        if numerator % denominator:
            continue
        endpoint = numerator // denominator
        if endpoint % 2 != 1 or endpoint % 3 != 2:
            continue
        predecessor = (2 * endpoint - 1) // 3
        assert (3 * predecessor + 1) // 2 == endpoint
        assert predecessor < source_scale
        found = True
        break
    assert found


def test_small_layer_modular_inverse_and_digest_is_stable() -> None:
    first = audit_first_crossing_layer(7, DMAX)
    second = audit_first_crossing_layer(7, DMAX)
    assert first == second
    assert first["enumerated_words"] == 30
    assert first["q0_near_diagonal_box_count"] == 0


def test_paradoxical_cylinder_identity_property() -> None:
    tree = paradoxical_tree_data(8)
    assert len(tree["paradoxical_records"]) == 5
    for record in tree["paradoxical_records"]:
        denominator = 1 << int(record["length"])
        coefficient = 3 ** int(record["q"])
        difference_power = denominator - coefficient
        source = int(record["canonical_source"])
        endpoint = int(record["canonical_endpoint"])
        for parameter in range(4):
            left = (endpoint + coefficient * parameter) - (source + denominator * parameter)
            right = (endpoint - source) - difference_power * parameter
            assert left == right


def test_phase9_search_and_verifier_are_import_independent() -> None:
    source = Path("verifier/verify_phase9.py").read_text(encoding="utf-8")
    assert "from src.phase9_search import" not in source
    assert "import src.phase9_search" not in source
