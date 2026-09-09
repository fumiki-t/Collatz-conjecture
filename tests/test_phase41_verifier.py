import copy
import json
from pathlib import Path

import pytest

from verifier.verify_phase41 import BUILDERS, KINDS, VerificationError, load_certificate, verify_section


@pytest.fixture(scope="module")
def expected():
    return {kind: build() for kind, build in BUILDERS.items()}


@pytest.mark.parametrize("kind", KINDS)
def test_accepted_artifact_reconstructed(kind, expected):
    data = json.loads(Path(f"artifacts/phase41_{kind}.json").read_text())
    verify_section(kind, data, expected[kind])


@pytest.mark.parametrize("kind", KINDS)
@pytest.mark.parametrize("mutation", ["proof", "missing", "extra", "format", "type"])
def test_envelope_tampering_rejected(kind, mutation, expected):
    data = copy.deepcopy(expected[kind])
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
        verify_section(kind, data, expected[kind])


@pytest.mark.parametrize("kind,path", [
    ("decoder", ("word_count",)), ("decoder", ("fibers", 13, "holes", 0, 1, 2)),
    ("decoder", ("rejected_count",)), ("decoder", ("boundary_sha256",)),
    ("mixed", ("even_rows",)), ("mixed", ("examples", "even_h_equals_R", "z")),
    ("mixed", ("safe_gain_cap_rows",)), ("mixed", ("rows_sha256",)),
    ("formal", ("bound", 0)), ("formal", ("correction", 0)),
    ("formal", ("checkpoints", 9, "source")), ("formal", ("positive_ordinary_source",)),
    ("ancestors", ("all_Q_geodesic_certificate",)), ("ancestors", ("maximum_length",)),
    ("ancestors", ("rows", 30, "hits_sha256")), ("ancestors", ("rows", 30, "source_upper_bound")),
    ("regressions", ("pairs", 5, "competitor", "safe")),
    ("regressions", ("pairs", 4, "competitor", "source")),
    ("regressions", ("source167", 28, 4)), ("regressions", ("statuses", "H112")),
])
def test_arithmetic_and_scope_tampering_rejected(kind, path, expected):
    data = copy.deepcopy(expected[kind])
    obj = data
    for key in path[:-1]:
        obj = obj[key]
    key, old = path[-1], obj[path[-1]]
    obj[key] = not old if isinstance(old, bool) else old+1 if isinstance(old, int) else "TAMPERED"
    with pytest.raises(VerificationError):
        verify_section(kind, data, expected[kind])


@pytest.mark.parametrize("text", ['{"valid":true,"valid":false}', '{"x":NaN}', '{"x":Infinity}'])
def test_ambiguous_json_rejected(text):
    with pytest.raises(VerificationError):
        load_certificate(text)
