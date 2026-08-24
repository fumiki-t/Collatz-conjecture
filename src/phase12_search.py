#!/usr/bin/env python3
"""Generate exact Phase 12 odd-orbit packing evidence.

The mathematical acceptance boundary is deliberately symbolic.  Finite orbit
rows are regression evidence only; the theorem is proved from exact affine
identities, residue packing, and elementary logarithmic inequalities.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


DEFAULT_START_BOUND = 100_000
DEFAULT_MAX_ODD = 96
DEFAULT_CONTACT_Q = 512
A_WORD = "11101"
B_WORD = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode_fraction(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def shortcut_step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def v2(value: int) -> int:
    if value <= 0:
        raise ValueError("v2 expects a positive integer")
    return (value & -value).bit_length() - 1


def floor_j_log2_3(index: int) -> int:
    """Return floor(index*log_2(3)) without floating point."""

    return (3**index).bit_length() - 1


def safe_prefix_segment(start: int, maximum_odd: int) -> dict[str, object]:
    """Follow an odd start until descent, coefficient crossing, cycle, or cap.

    The state at ordinary shortcut time k has coefficient 3^q/2^k, where q
    counts odd inputs already processed.  Y is maintained exactly so that
    state=(3^q/2^k)Y.
    """

    if start <= 0 or start % 2 == 0:
        raise ValueError("safe-prefix segment requires a positive odd start")
    value = start
    step_index = 0
    odd_count = 0
    y_value = Fraction(start)
    odd_values: list[int] = []
    odd_positions: list[int] = []
    y_values: list[Fraction] = []
    seen: set[int] = set()
    reason = "odd_horizon"
    crossing: dict[str, object] | None = None

    while len(odd_values) < maximum_odd:
        if value in seen:
            reason = "cycle"
            break
        seen.add(value)
        if value < start:
            reason = "descent"
            break
        if value % 2:
            if (1 << step_index) > 3**odd_count:
                raise AssertionError("odd state survived after coefficient crossing")
            odd_values.append(value)
            odd_positions.append(step_index)
            y_values.append(y_value)

        was_odd = value % 2 == 1
        old_odd_value = value if was_odd else None
        value = shortcut_step(value)
        step_index += 1
        if was_odd:
            odd_count += 1
            y_value *= Fraction(3 * old_odd_value + 1, 3 * old_odd_value)

        if (1 << step_index) > 3**odd_count:
            reason = "coefficient_crossing"
            crossing = {
                "K": step_index,
                "q": odd_count,
                "endpoint": value,
                "displacement": value - start,
                "Y_q": encode_fraction(y_value),
                "endpoint_below_Y_q": Fraction(value) < y_value,
                "exact_Y_minus_endpoint": encode_fraction(y_value - value),
                "tail_minimum_through_endpoint": value >= start,
            }
            break
        if value < start:
            reason = "descent"
            break

    if len(set(odd_values)) != len(odd_values):
        raise AssertionError("repeated odd iterate was not classified as a cycle")
    for index, (position, odd_value, y_at_index) in enumerate(zip(odd_positions, odd_values, y_values)):
        if y_at_index != Fraction((1 << position) * odd_value, 3**index):
            raise AssertionError("normalization identity failed")
        if index and math.gcd(odd_value, 6) != 1:
            raise AssertionError("post-initial odd iterate is not coprime to six")
        if floor_j_log2_3(index) - position < 0:
            raise AssertionError("recorded odd state is not coefficient-safe")
        if index + 1 < len(y_values):
            expected = y_at_index * Fraction(3 * odd_value + 1, 3 * odd_value)
            if y_values[index + 1] != expected:
                raise AssertionError("Y recurrence failed")

    reciprocal_sum = sum((Fraction(1, value) for value in odd_values), Fraction())
    packing_slots = sorted(odd_values[1:])
    for rank, value in enumerate(packing_slots):
        if rank >= 2 and value < start + 3 * (rank - 1):
            raise AssertionError("mod-six packing rank failed")
    return {
        "start": start,
        "reason": reason,
        "odd_count": len(odd_values),
        "ordinary_steps": step_index,
        "odd_values": odd_values,
        "odd_positions": odd_positions,
        "a_values": [floor_j_log2_3(index) - position for index, position in enumerate(odd_positions)],
        "Y_final": encode_fraction(y_value),
        "reciprocal_sum": encode_fraction(reciprocal_sum),
        "crossing": crossing,
    }


def theorem_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase12-packing-theorem-v1",
        "P72": {
            "repository_status": "VERIFIED_THEOREM",
            "hypotheses": [
                "S is a positive tail minimum of a nonperiodic Collatz orbit",
                "the tail is coefficient-safe at every ordinary shortcut prefix",
                "x_j=T^(d_j)(S) is the j-th odd iterate and d_0=0",
            ],
            "definitions": {
                "theta_j": "fractional_part(j*log2(3))",
                "a_j": "floor(j*log2(3))-d_j",
                "Y_j": "2^d_j*x_j/3^j",
            },
            "exact_identities": [
                "x_j=2^(a_j+theta_j)*Y_j",
                "Y_0=S",
                "Y_(j+1)=Y_j*(1+1/(3*x_j))",
                "a_j>=0",
            ],
            "packing_lemmas": [
                "the x_j are distinct",
                "gcd(x_j,6)=1 for j>=1",
                "the r-th ordered post-initial value z_r satisfies z_r>=S+3*(r-1) for r>=2",
                "sum_(i<j) 1/x_i <= 3/S+(1/3)*log(1+3*j/S)",
            ],
            "growth_bound": "Y_j<=S*exp(1/S)*(1+3*j/S)^(1/9)",
            "counting_bound": "#{i<j:a_i<=A}<=3+(2^(A+1)*S*exp(1/S)/3)*(1+3*j/S)^(1/9)",
            "density_consequence": "for every epsilon>0, a_i>(8/9-epsilon)*log2(i) on a density-one set of positive indices",
            "finite_first_crossing": "d<S*(exp(1/S)*(1+3*q/S)^(1/9)-1)",
            "finite_crossing_derivation": "at first crossing 3^q/2^K<1, so S+d=(3^q/2^K)*Y_q<Y_q",
            "proves_collatz": False,
        },
        "proof_certificate": {
            "log_product_step": "log(Y_j/S)=sum_(i<j) log(1+1/(3*x_i))<=sum_(i<j)1/(3*x_i)",
            "packing_count": "each complete interval of six integers contains exactly two residues coprime to six",
            "integral_step": "sum_(r=1)^m 1/(S+3r)<=integral_0^m dt/(S+3t)",
            "counting_step": "a_i<=A implies x_i<2^(A+1)*Y_i<=2^(A+1)*Y_j",
            "density_step": "with A=floor((8/9-epsilon)log2(j)), the exceptional count is O(j^(1-epsilon))",
        },
        "exact_exponent_arithmetic": {
            "coprime_to_six_harmonic_coefficient": encode_fraction(Fraction(1, 3)),
            "normalized_log_recurrence_coefficient": encode_fraction(Fraction(1, 3)),
            "growth_exponent": encode_fraction(Fraction(1, 9)),
            "density_threshold_coefficient": encode_fraction(Fraction(8, 9)),
            "threshold_plus_growth": encode_fraction(Fraction(1)),
        },
        "literature_overlap": {
            "Lagarias_1985": {
                "result": "a trajectory tending to infinity has lower parity-one density at least ln(2)/ln(3)",
                "overlap": "critical parity density only; no a_j packing bound is imported",
                "url": "https://doi.org/10.2307/2322189",
            },
            "Monks_Yazinski_2004": {
                "result": "the same lower-density restriction holds for divergent rational 2-adic orbits",
                "overlap": "extends the known density domain; Phase 12 uses positive integer odd-value packing instead",
                "url": "https://doi.org/10.1016/S0012-365X(03)00125-0",
            },
            "Lopez_Stoll_2009_2021": {
                "result": "critical-slope Sturmian parity words are studied; the 2021 preprint states equality of lower density for a divergent rational 2-adic orbit",
                "overlap": "the all-contact word is the upper mechanical word of slope ln(2)/ln(3), but positivity is ruled out here by P72 rather than imported",
                "urls": ["https://doi.org/10.1515/INTEG.2009.014", "https://arxiv.org/abs/2101.12747"],
            },
            "novelty_boundary": "No claim of literature-wide novelty is made; the inspected sources do not state the P72 odd-value packing inequality in this notation.",
        },
        "what_this_result_does_not_prove": "P72 constrains but does not exclude an infinite coefficient-safe tail, a nontrivial cycle, the renewal ladder, or a Collatz counterexample.",
        "proves_collatz": False,
    }


def inverse_parity_residue(word: str) -> tuple[int, int, int]:
    coefficient = 1
    constant = 0
    denominator = 1
    for bit in word:
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        elif bit != "0":
            raise ValueError("parity word must be binary")
        denominator *= 2
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    return residue, coefficient, constant


def parity_word(start: int, length: int) -> str:
    value = start
    bits = []
    for _ in range(length):
        bits.append(str(value & 1))
        value = shortcut_step(value)
    return "".join(bits)


def all_contact_artifact(maximum_q: int) -> dict[str, object]:
    digest = hashlib.sha256()
    selected = []
    selected_q = {1, 2, 3, 4, 8, 16, 32, 64, 128, 256, maximum_q}
    for q in range(1, maximum_q + 1):
        length = floor_j_log2_3(q)
        positions = [floor_j_log2_3(index) for index in range(q)]
        position_set = set(positions)
        word = "".join("1" if index in position_set else "0" for index in range(length))
        if word.count("1") != q:
            raise AssertionError("all-contact odd count mismatch")
        residue, coefficient, constant = inverse_parity_residue(word)
        representative = residue if residue else 1 << length
        if parity_word(representative, length) != word:
            raise AssertionError("all-contact inverse residue failed")
        digest.update(f"{q}|{length}|{word}|{residue}|{coefficient}|{constant}\n".encode("ascii"))
        if q in selected_q:
            selected.append(
                {
                    "q": q,
                    "length": length,
                    "word_prefix": word[:96],
                    "word_sha256": hashlib.sha256(word.encode("ascii")).hexdigest(),
                    "canonical_residue": residue,
                }
            )
    return {
        "format": "collatz-phase12-all-contact-v1",
        "P73": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "The all-contact critical mechanical parity word cannot be the infinite forward parity word of a positive integer.",
            "mechanical_identification": "odd positions d_j=floor(j*log2(3)); equivalently the upper mechanical word 1c_alpha with alpha=ln(2)/ln(3)",
            "aperiodicity": "alpha is irrational because 2^p=3^q has no positive integer solution",
            "packing_contradiction": "a_j=0 for every j makes the P72 A=0 counting bound read j=O(j^(1/9))",
            "finite_prefix_warning": "every finite prefix still has one canonical residue modulo its power-of-two length",
        },
        "finite_prefix_regression": {
            "maximum_q": maximum_q,
            "row_digest_sha256": digest.hexdigest(),
            "selected_rows": selected,
        },
        "what_this_result_does_not_prove": "Ruling out one critical mechanical word does not rule out arbitrary infinite coefficient-safe tails.",
        "proves_collatz": False,
    }


def normalized_odd(value: int) -> int:
    if value <= 0:
        raise ValueError("positive adversarial seed required")
    return value >> v2(value)


def adversarial_seeds() -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    rows.extend(("2^m-1", (1 << exponent) - 1) for exponent in range(3, 25))
    rows.extend(("8^m-5", 8**exponent - 5) for exponent in range(1, 11))
    for blocks in range(1, 11):
        for mask in range(1 << blocks):
            word = "".join("111" if mask & (1 << index) else "110" for index in range(blocks))
            rows.append(("(110|111)^*", int(word, 2)))
    rows.extend((("A=11101", int(A_WORD, 2)), ("B=1100", int(B_WORD, 2))))
    for r in range(1, 9):
        for s in range(1, 9):
            rows.append(("A^rB^s", int(A_WORD * r + B_WORD * s, 2)))
    return rows


def adversarial_audit(maximum_odd: int) -> dict[str, object]:
    digest = hashlib.sha256()
    families: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    longest = (0, "", 0, 0)
    for family, raw_start in adversarial_seeds():
        start = normalized_odd(raw_start)
        row = safe_prefix_segment(start, maximum_odd)
        families[family] += 1
        reasons[str(row["reason"])] += 1
        digest.update(
            f"{family}|{raw_start}|{start}|{row['reason']}|{row['odd_count']}|{row['ordinary_steps']}|{row['a_values']}\n".encode(
                "ascii"
            )
        )
        candidate = (int(row["odd_count"]), family, raw_start, start)
        if candidate > longest:
            longest = candidate
    return {
        "families": dict(sorted(families.items())),
        "reason_counts": dict(sorted(reasons.items())),
        "instance_count": sum(families.values()),
        "row_digest_sha256": digest.hexdigest(),
        "longest_safe_prefix": {
            "odd_count": longest[0],
            "family": longest[1],
            "raw_start": longest[2],
            "normalized_odd_start": longest[3],
        },
    }


def finite_orbit_artifact(start_bound: int, maximum_odd: int) -> dict[str, object]:
    digest = hashlib.sha256()
    reasons: Counter[str] = Counter()
    maximum = (0, 0)
    first_crossings = 0
    exact_crossing_slack_minimum: Fraction | None = None
    selected = []
    starts = list(range(3, start_bound + 1, 4))
    for start in starts:
        row = safe_prefix_segment(start, maximum_odd)
        reasons[str(row["reason"])] += 1
        if int(row["odd_count"]) > maximum[0]:
            maximum = (int(row["odd_count"]), start)
        crossing = row["crossing"]
        if isinstance(crossing, dict):
            first_crossings += 1
            y_q = Fraction(crossing["Y_q"]["numerator"], crossing["Y_q"]["denominator"])
            slack = y_q - start - int(crossing["displacement"])
            if not slack > 0:
                raise AssertionError("finite first-crossing exact displacement bound failed")
            if exact_crossing_slack_minimum is None or slack < exact_crossing_slack_minimum:
                exact_crossing_slack_minimum = slack
        digest.update(
            f"{start}|{row['reason']}|{row['odd_count']}|{row['ordinary_steps']}|{row['odd_positions']}|{row['odd_values']}|{row['Y_final']}\n".encode(
                "ascii"
            )
        )
        if start in {3, 7, 27, 31, 703, 1126015} or start == maximum[1]:
            selected.append(row)
    return {
        "format": "collatz-phase12-finite-orbit-audit-v1",
        "E20": {
            "repository_status": "VERIFIED_FINITE",
            "start_definition": "all S<=start_bound with S=3 mod 4",
            "start_bound": start_bound,
            "maximum_odd_horizon": maximum_odd,
            "start_count": len(starts),
            "reason_counts": dict(sorted(reasons.items())),
            "maximum_recorded_odd_count": maximum[0],
            "first_maximum_witness": maximum[1],
            "first_crossing_count": first_crossings,
            "minimum_exact_Yq_minus_endpoint": None
            if exact_crossing_slack_minimum is None
            else encode_fraction(exact_crossing_slack_minimum),
            "row_digest_sha256": digest.hexdigest(),
            "selected_rows": selected,
            "adversarial": adversarial_audit(maximum_odd),
        },
        "what_this_result_does_not_prove": "Finite orbit identities and adversarial agreement do not establish the existence or nonexistence of an infinite safe tail.",
        "proves_collatz": False,
    }


def packing_obstruction(maximum_terms: int = 4096) -> dict[str, object]:
    values = [value for value in range(1, 6 * maximum_terms + 1) if math.gcd(value, 6) == 1][:maximum_terms]
    product = Fraction(1)
    digest = hashlib.sha256()
    selected = []
    checkpoints = {1, 2, 4, 16, 64, 256, 1024, maximum_terms}
    for index, value in enumerate(values, 1):
        product *= Fraction(3 * value + 1, 3 * value)
        digest.update(f"{index}|{value}|{product.numerator}|{product.denominator}\n".encode("ascii"))
        if index in checkpoints:
            selected.append(
                {
                    "terms": index,
                    "last_value": value,
                    "product_numerator_bits": product.numerator.bit_length(),
                    "product_denominator_bits": product.denominator.bit_length(),
                }
            )
    return {
        "format": "collatz-phase12-packing-obstruction-v1",
        "NG21": {
            "repository_status": "REFUTED",
            "hypothesis": "Distinctness, a fixed lower bound, and gcd(x_i,6)=1 alone imply Y_j=O(j^gamma) for some gamma<1/9.",
            "abstract_countermodel": "enumerate the positive integers coprime to six and set Y_(i+1)=Y_i*(1+1/(3*x_i))",
            "sharpness_proof": "two admissible integers per six-number block give sum 1/x_i=(1/3)log(j)+O(1); log(1+1/(3x))=1/(3x)+O(1/x^2), hence log(Y_j)=log(j)/9+O(1)",
            "scope": "This refutes only an improvement using the packing premises alone; actual Collatz transition congruences may still yield a stronger exponent.",
        },
        "finite_regression": {
            "maximum_terms": maximum_terms,
            "row_digest_sha256": digest.hexdigest(),
            "selected_rows": selected,
            "exact_two_per_complete_six_block": True,
        },
        "H72": {
            "repository_status": "OPEN",
            "statement": "Use orbit-specific transition congruences beyond distinctness modulo six to strengthen P72 enough to exclude every infinite coefficient-safe tail.",
        },
        "what_this_result_does_not_prove": "Sharpness of the coarse packing input is not an example of a Collatz orbit and does not show that exponent 1/9 is dynamically optimal.",
        "proves_collatz": False,
    }


def write_obstruction_report(path: Path, finite: dict[str, object], obstruction: dict[str, object]) -> None:
    e20 = finite["E20"]
    adversarial = e20["adversarial"]
    text = f"""# Phase 12 obstruction report

This report does not claim a proof or disproof of the Collatz conjecture.

## Finite orbit audit

- Starts: {e20['start_count']} values S=3 mod 4 through {e20['start_bound']}.
- Longest recorded coefficient-safe tail-minimum prefix: {e20['maximum_recorded_odd_count']} odd iterates at S={e20['first_maximum_witness']}.
- Finite coefficient first crossings: {e20['first_crossing_count']}.
- Mandatory adversarial instances: {adversarial['instance_count']}.

## Exponent obstruction

The residue-packing input is sharp at exponent 1/9.  The abstract sequence of
all positive integers coprime to six has two members in each complete block of
six, so its reciprocal sum has leading coefficient 1/3.  Combined with the
factor 1/3 in log(1+1/(3x)), this gives Y_j of order j^(1/9).  Therefore a
stronger exponent cannot follow from distinctness and gcd(x_i,6)=1 alone.

This abstract saturator is not a Collatz orbit.  H72 remains open: exploit
transition congruences or multi-step exclusions that actual odd orbits obey.

## All-contact word

The critical upper mechanical word is impossible as an infinite positive
integer trajectory by P72, even though every finite prefix has a canonical
2-adic residue.  This removes one extremal word, not the full safe language.

## What this result does not prove

Phase 12 does not exclude arbitrary infinite coefficient-safe tails,
nontrivial cycles, the renewal ladder, or the Collatz conjecture.
"""
    path.write_text(text, encoding="utf-8")


def generate(artifact_dir: Path, start_bound: int, maximum_odd: int, contact_q: int) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    theorem = theorem_artifact()
    all_contact = all_contact_artifact(contact_q)
    finite = finite_orbit_artifact(start_bound, maximum_odd)
    obstruction = packing_obstruction()
    write_json(artifact_dir / "phase12_packing_theorem.json", theorem)
    write_json(artifact_dir / "phase12_all_contact.json", all_contact)
    write_json(artifact_dir / "phase12_finite_orbits.json", finite)
    write_json(artifact_dir / "phase12_packing_obstruction.json", obstruction)
    write_obstruction_report(artifact_dir / "phase12_obstruction_report.md", finite, obstruction)
    return {
        "P72": "VERIFIED_THEOREM",
        "P73": "VERIFIED_THEOREM",
        "E20": "VERIFIED_FINITE",
        "NG21": "REFUTED",
        "H72": "OPEN",
        "start_count": finite["E20"]["start_count"],
        "adversarial_instances": finite["E20"]["adversarial"]["instance_count"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--start-bound", type=int, default=DEFAULT_START_BOUND)
    parser.add_argument("--max-odd", type=int, default=DEFAULT_MAX_ODD)
    parser.add_argument("--contact-q", type=int, default=DEFAULT_CONTACT_Q)
    args = parser.parse_args()
    if args.start_bound < 3 or args.max_odd < 1 or args.contact_q < 1:
        parser.error("bounds must be positive")
    result = generate(args.artifact_dir, args.start_bound, args.max_odd, args.contact_q)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
