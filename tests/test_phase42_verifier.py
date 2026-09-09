import copy
import json
from pathlib import Path

import pytest

from verifier.verify_phase42 import (
    BUILDERS, KINDS, VerificationError, load_certificate, verify_directory,
    verify_repeat, verify_repeats, verify_section,
)


@pytest.fixture(scope="module")
def expected():
    return {kind: build() for kind, build in BUILDERS.items()}


@pytest.fixture(scope="module")
def repeats():
    return json.loads(Path("artifacts/phase42_repeats.json").read_text())


def test_all_accepted_evidence_independently_reconstructed():
    result = verify_directory(Path("artifacts"))
    assert result["valid"] and not result["proves_collatz"]
    assert result["repeat_certificates"] == 8 and result["q21_rejections"] == 48
    assert result["finite_capacity_factor_occurrences"] == 0  # Explicit limitation.
    saved = json.loads(Path("artifacts/phase42_verifier.json").read_text())
    assert result == saved


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("mutation", ["proof", "missing", "extra", "format", "type"])
def test_envelope_tampering_rejected(kind, mutation, expected, repeats):
    data = copy.deepcopy(repeats if kind == "repeats" else expected[kind])
    if mutation == "proof":
        data["proves_collatz"] = True
    elif mutation == "missing":
        data.pop("format")
    elif mutation == "extra":
        data["unverified_claim"] = True
    elif mutation == "type":
        data["proves_collatz"] = 0
    else:
        data["format"] = "collatz-proof"
    with pytest.raises(VerificationError):
        verify_section(kind, data, expected.get(kind))


@pytest.mark.parametrize("kind,path", [
    ("capacity", ("maximum_source",)), ("capacity", ("maximum_odd_steps",)),
    ("capacity", ("rows_sha256",)), ("capacity", ("factor_occurrences",)),
    ("capacity", ("hypotheses", 2)), ("capacity", ("samples", 3, "K")),
    ("capacity", ("samples", 4, "blocks", 0, 1)), ("capacity", ("samples", 5, "energy")),
    ("carry", ("minimum_odd_count",)), ("carry", ("q21_patterns",)),
    ("carry", ("q21_checks", 0, 4)), ("carry", ("q21_allowance", 0)),
    ("carry", ("witness", "target_source")), ("carry", ("witness", "carry")),
    ("carry", ("witness", "target_L_Q_B", 2)), ("carry", ("scope",)),
    ("regressions", ("family_words_sha256",)), ("regressions", ("controls", 2, 5)),
    ("regressions", ("cycles", 1, 4)), ("regressions", ("statuses", "H112")),
])
def test_arithmetic_and_hypothesis_tampering(kind, path, expected):
    data = copy.deepcopy(expected[kind])
    obj = data
    for k in path[:-1]:
        obj = obj[k]
    key, old = path[-1], obj[path[-1]]
    obj[key] = not old if type(old) is bool else old+1 if type(old) is int else "TAMPERED"
    with pytest.raises(VerificationError):
        verify_section(kind, data, expected[kind])


@pytest.mark.parametrize("field", [
    "source_bits", "K", "h", "width", "clean_occurrences", "capacity", "first_start", "second_start",
    "lcp", "prefix_length", "generated_odd_steps", "covering_odd_steps", "prefix_sha256", "split_bits", "odd_counts",
])
def test_repeat_witness_tampering(field, repeats):
    row = copy.deepcopy(repeats["certificates"][0])
    if type(row[field]) is int:
        row[field] += 1
    elif field == "split_bits":
        row[field] = row[field][::-1]
    elif field == "odd_counts":
        row[field][0] += 1
    else:
        row[field] = "0"*64
    with pytest.raises(VerificationError):
        verify_repeat(row)


def test_q21_remainder_omission_rejected(expected):
    data = copy.deepcopy(expected["carry"])
    data["q21_checks"].pop()
    with pytest.raises(VerificationError):
        verify_section("carry", data, expected["carry"])


@pytest.mark.parametrize("mutation", ["omit", "duplicate", "scope", "bool", "omit_field"])
def test_repeat_completeness_and_types(mutation, repeats):
    data = copy.deepcopy(repeats)
    if mutation == "omit":
        data["certificates"].pop()
    elif mutation == "duplicate":
        data["certificates"][0] = data["certificates"][1]
    elif mutation == "scope":
        data["source_bounds_bits"].pop()
    elif mutation == "bool":
        data["certificates"][0]["first_start"] = True
    else:
        data["certificates"][0].pop("split_bits")
    with pytest.raises(VerificationError):
        verify_repeats(data)


@pytest.mark.parametrize("text", ['{"valid":true,"valid":false}', '{"x":NaN}', '{"x":Infinity}', '{bad'])
def test_ambiguous_or_invalid_json_rejected(text):
    with pytest.raises(VerificationError):
        load_certificate(text)
