#!/usr/bin/env python3
"""Generate the exact finite audit for the Garcia--Tal formal obstruction.

This generator deliberately certifies only a finite prefix of a formal odd
exponent sequence.  It does not assert that the associated 2-adic source is a
positive ordinary integer or that a Collatz counterexample exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


DEFAULT_DEPTH = 1026
CHECKPOINTS = (64, 1024, 1026)


def floor_n_log2_3(index: int) -> int:
    """Return floor(index*log_2(3)) using integer arithmetic only."""

    return (3**index).bit_length() - 1


def exponent_for(state: Fraction) -> int:
    if not Fraction(1) < state <= Fraction(2):
        raise ValueError("formal state left (1,2]")
    return 1 if state <= Fraction(5, 3) else 2


def residue_from_affine_constant(constant: int, index: int, exponent_sum: int) -> int:
    modulus = 1 << exponent_sum
    return (-constant * pow(3**index, -1, modulus)) % modulus


def integer_digest(value: int) -> str:
    width = max(1, (value.bit_length() + 7) // 8)
    return hashlib.sha256(value.to_bytes(width, "big")).hexdigest()


def generate(depth: int = DEFAULT_DEPTH) -> dict[str, object]:
    if depth < max(CHECKPOINTS):
        raise ValueError(f"depth must be at least {max(CHECKPOINTS)}")

    state = Fraction(3, 2)
    exponent_sum = 0
    affine_constant = 0
    word: list[str] = []
    checkpoints: list[dict[str, object]] = []
    residues: dict[int, int] = {}

    for index in range(1, depth + 1):
        exponent = exponent_for(state)
        word.append(str(exponent))
        affine_constant = 3 * affine_constant + (1 << exponent_sum)
        exponent_sum += exponent
        state = (3 * state - 1) / (1 << exponent)
        if index in CHECKPOINTS:
            residue = residue_from_affine_constant(affine_constant, index, exponent_sum)
            residues[index] = residue
            checkpoints.append(
                {
                    "index": index,
                    "exponent_sum": exponent_sum,
                    "defect_a": floor_n_log2_3(index) - exponent_sum,
                    "state_in_open_closed_interval": Fraction(1) < state <= Fraction(2),
                    "canonical_residue_bit_length": residue.bit_length(),
                    "canonical_residue_sha256_big_endian": integer_digest(residue),
                }
            )

    residue_delta = residues[1026] - residues[1024]
    expected_delta = 2 * (1 << 1174)
    if residue_delta != expected_delta:
        raise AssertionError("canonical residue renewal identity failed")

    return {
        "format": "collatz-garcia-tal-formal-obstruction-v1",
        "parameters": {
            "initial_h": {"numerator": 3, "denominator": 2},
            "state_interval": "1<h<=2",
            "policy": "e=1 for 1<h<=5/3; e=2 for 5/3<h<=2",
            "depth": depth,
        },
        "finite_certificate": {
            "first_64_exponents": "".join(word[:64]),
            "checkpoints": checkpoints,
            "residue_1026_minus_residue_1024": str(residue_delta),
            "residue_delta_formula": "2*2^1174",
            "positive_ordinary_source_excluded_below": "2^1174",
        },
        "classification": {
            "NG22": "REFUTED",
            "E21": "VERIFIED_FINITE",
            "refuted_statement": (
                "a_j->infinity, sum(2^-a_j)<infinity, h_j>1, and "
                "sum(1/h_j)=infinity alone yield a contradiction"
            ),
            "finite_statement": (
                "the formal policy has a coherent odd 2-adic source through the audited "
                "prefix, but no positive ordinary source below 2^1174"
            ),
        },
        "what_this_result_does_not_prove": (
            "The formal 2-adic source is not shown to be a positive ordinary integer. "
            "The certificate neither constructs a Collatz counterexample nor proves the conjecture."
        ),
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--depth", type=int, default=DEFAULT_DEPTH)
    args = parser.parse_args()
    data = generate(args.depth)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
