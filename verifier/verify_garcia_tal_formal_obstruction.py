#!/usr/bin/env python3
"""Independently verify the Garcia--Tal formal-obstruction certificate.

The verifier reconstructs canonical residues from the inverse 2-adic series;
it does not import or reuse the generator's affine-constant implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


EXPECTED_FIRST_64 = "1211111121111111121111211111121111211112111111112111112111112111"
EXPECTED_CHECKPOINTS = {
    64: (74, 27, 71, "e2a41d2308bc2e35c818c2a81379e338366db6f1ce8084c8e623e82fe1d15840"),
    1024: (1174, 449, 1172, "a0cd4f2a2fe7583b916ce674299893ad6daec01b933739878b7c18aa49c1ac65"),
    1026: (1176, 450, 1176, "068447aa2534b43f468e288d16ccfe5cf164886d9d8f409811b007974b242953"),
}


def fail(message: str) -> None:
    raise ValueError(message)


def digest_integer(value: int) -> str:
    width = max(1, (value.bit_length() + 7) // 8)
    return hashlib.sha256(value.to_bytes(width, "big")).hexdigest()


def reconstruct(depth: int) -> tuple[str, dict[int, tuple[int, int, int, str, int]], list[int]]:
    """Use the inverse series -sum 2^E_j/3^(j+1), modulo 2^E_n."""

    h = Fraction(3, 2)
    exponent_sum = 0
    exponents: list[int] = []
    exponent_prefixes: list[int] = [0]
    for _ in range(depth):
        if not Fraction(1) < h <= Fraction(2):
            fail("state interval is not invariant")
        exponent = 1 if h <= Fraction(5, 3) else 2
        exponents.append(exponent)
        exponent_sum += exponent
        exponent_prefixes.append(exponent_sum)
        h = (3 * h - 1) / (1 << exponent)

    rows: dict[int, tuple[int, int, int, str, int]] = {}
    residues: list[int] = []
    for index in EXPECTED_CHECKPOINTS:
        total = exponent_prefixes[index]
        modulus = 1 << total
        inverse_series = 0
        inverse_three = 1
        for j in range(index):
            inverse_three = (inverse_three * pow(3, -1, modulus)) % modulus
            inverse_series = (inverse_series + (1 << exponent_prefixes[j]) * inverse_three) % modulus
        residue = (-inverse_series) % modulus
        defect = (3**index).bit_length() - 1 - total
        rows[index] = (total, defect, residue.bit_length(), digest_integer(residue), residue)
        residues.append(residue)

    # A deeper canonical residue must realize all earlier exact valuations.
    source = rows[1026][4]
    state = source
    for position, exponent in enumerate(exponents[:1024]):
        numerator = 3 * state + 1
        valuation = (numerator & -numerator).bit_length() - 1
        if valuation != exponent:
            fail(f"2-adic exponent mismatch at position {position}")
        state = numerator >> exponent

    return "".join(str(value) for value in exponents[:64]), rows, exponents


def verify(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load certificate: {error}") from error
    if not isinstance(data, dict):
        fail("certificate is not an object")
    if data.get("format") != "collatz-garcia-tal-formal-obstruction-v1":
        fail("format mismatch")
    if data.get("proves_collatz") is not False:
        fail("proves_collatz boundary mismatch")
    parameters = data.get("parameters")
    if parameters != {
        "initial_h": {"numerator": 3, "denominator": 2},
        "state_interval": "1<h<=2",
        "policy": "e=1 for 1<h<=5/3; e=2 for 5/3<h<=2",
        "depth": 1026,
    }:
        fail("formal policy parameters mismatch")
    classification = data.get("classification")
    if not isinstance(classification, dict) or classification.get("NG22") != "REFUTED":
        fail("NG22 status mismatch")
    if classification.get("E21") != "VERIFIED_FINITE":
        fail("E21 status mismatch")
    if data.get("what_this_result_does_not_prove") is None:
        fail("limitation boundary missing")

    first_64, rows, _ = reconstruct(1026)
    finite = data.get("finite_certificate")
    if not isinstance(finite, dict) or finite.get("first_64_exponents") != first_64:
        fail("first-64 exponent word mismatch")
    if first_64 != EXPECTED_FIRST_64:
        fail("independent first-64 regression mismatch")
    stored_rows = finite.get("checkpoints")
    if not isinstance(stored_rows, list) or len(stored_rows) != 3:
        fail("checkpoint shape mismatch")
    for stored in stored_rows:
        if not isinstance(stored, dict) or stored.get("index") not in rows:
            fail("checkpoint index mismatch")
        index = stored["index"]
        total, defect, bit_length, digest, _ = rows[index]
        expected = EXPECTED_CHECKPOINTS[index]
        if (total, defect, bit_length, digest) != expected:
            fail(f"independent checkpoint regression mismatch at {index}")
        if stored != {
            "index": index,
            "exponent_sum": total,
            "defect_a": defect,
            "state_in_open_closed_interval": True,
            "canonical_residue_bit_length": bit_length,
            "canonical_residue_sha256_big_endian": digest,
        }:
            fail(f"stored checkpoint mismatch at {index}")

    delta = rows[1026][4] - rows[1024][4]
    if delta != 2 * (1 << 1174):
        fail("residue renewal identity mismatch")
    if finite.get("residue_1026_minus_residue_1024") != str(delta):
        fail("stored residue delta mismatch")
    if finite.get("residue_delta_formula") != "2*2^1174":
        fail("residue delta formula mismatch")
    if finite.get("positive_ordinary_source_excluded_below") != "2^1174":
        fail("ordinary-height exclusion mismatch")

    return {
        "valid": True,
        "NG22": "REFUTED",
        "E21": "VERIFIED_FINITE",
        "verified_depth": 1026,
        "ordinary_source_exclusion": "no positive ordinary source below 2^1174",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.certificate)
    except ValueError as error:
        print(json.dumps({"valid": False, "error": str(error), "proves_collatz": False}, sort_keys=True))
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
