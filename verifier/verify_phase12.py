#!/usr/bin/env python3
"""Independently verify Phase 12 odd-orbit packing artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


A_BITS = "11101"
B_BITS = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot load {path}: {error}") from error
    if not isinstance(value, dict):
        fail(f"{path} is not a JSON object")
    return value


def fraction(row: object) -> Fraction:
    if not isinstance(row, dict) or set(row) != {"numerator", "denominator"}:
        fail("invalid rational encoding")
    numerator, denominator = row["numerator"], row["denominator"]
    if not isinstance(numerator, int) or not isinstance(denominator, int) or denominator <= 0:
        fail("invalid rational components")
    result = Fraction(numerator, denominator)
    if result.numerator != numerator or result.denominator != denominator:
        fail("non-reduced rational encoding")
    return result


def encoded(value: Fraction) -> dict[str, int]:
    return {"numerator": value.numerator, "denominator": value.denominator}


def collatz(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def valuation_two(value: int) -> int:
    return (value & -value).bit_length() - 1


def lower_power_index(index: int) -> int:
    return (3**index).bit_length() - 1


def independently_trace(start: int, cap: int) -> dict[str, object]:
    if start <= 0 or start % 2 == 0:
        fail("finite audit has a nonpositive or even start")
    state = start
    elapsed = 0
    odd_used = 0
    normalized = Fraction(start)
    odds: list[int] = []
    locations: list[int] = []
    normalized_rows: list[Fraction] = []
    visited: set[int] = set()
    stop = "odd_horizon"
    crossing: dict[str, object] | None = None
    while len(odds) < cap:
        if state in visited:
            stop = "cycle"
            break
        visited.add(state)
        if state < start:
            stop = "descent"
            break
        if state & 1:
            odds.append(state)
            locations.append(elapsed)
            normalized_rows.append(normalized)
        odd_input = state & 1
        prior = state
        state = collatz(state)
        elapsed += 1
        if odd_input:
            odd_used += 1
            normalized *= Fraction(3 * prior + 1, 3 * prior)
        if (1 << elapsed) > 3**odd_used:
            stop = "coefficient_crossing"
            crossing = {
                "K": elapsed,
                "q": odd_used,
                "endpoint": state,
                "displacement": state - start,
                "Y_q": encoded(normalized),
                "endpoint_below_Y_q": Fraction(state) < normalized,
                "exact_Y_minus_endpoint": encoded(normalized - state),
                "tail_minimum_through_endpoint": state >= start,
            }
            break
        if state < start:
            stop = "descent"
            break

    if len(set(odds)) != len(odds):
        fail("odd iterates are not distinct before classified stopping")
    for i, (location, odd, y_i) in enumerate(zip(locations, odds, normalized_rows)):
        if Fraction((1 << location) * odd, 3**i) != y_i:
            fail("P72 normalization reconstruction failed")
        if i and math.gcd(odd, 6) != 1:
            fail("P72 mod-six property failed")
        if lower_power_index(i) < location:
            fail("P72 coefficient-safety index failed")
        if i + 1 < len(normalized_rows):
            if normalized_rows[i + 1] != y_i * Fraction(3 * odd + 1, 3 * odd):
                fail("P72 normalized recurrence failed")
    ordered = sorted(odds[1:])
    for rank in range(2, len(ordered)):
        if ordered[rank] < start + 3 * (rank - 1):
            fail("P72 residue packing rank failed")
    reciprocals = sum((Fraction(1, item) for item in odds), Fraction())
    return {
        "start": start,
        "reason": stop,
        "odd_count": len(odds),
        "ordinary_steps": elapsed,
        "odd_values": odds,
        "odd_positions": locations,
        "a_values": [lower_power_index(i) - location for i, location in enumerate(locations)],
        "Y_final": encoded(normalized),
        "reciprocal_sum": encoded(reciprocals),
        "crossing": crossing,
    }


def verify_symbolic_theorem(data: dict[str, object]) -> None:
    if data.get("format") != "collatz-phase12-packing-theorem-v1" or data.get("proves_collatz") is not False:
        fail("P72 theorem artifact boundary mismatch")
    p72 = data.get("P72")
    if not isinstance(p72, dict) or p72.get("repository_status") != "VERIFIED_THEOREM":
        fail("P72 status mismatch")
    expected_identities = [
        "x_j=2^(a_j+theta_j)*Y_j",
        "Y_0=S",
        "Y_(j+1)=Y_j*(1+1/(3*x_j))",
        "a_j>=0",
    ]
    if p72.get("exact_identities") != expected_identities:
        fail("P72 exact identities mismatch")
    if p72.get("growth_bound") != "Y_j<=S*exp(1/S)*(1+3*j/S)^(1/9)":
        fail("P72 growth exponent mismatch")
    if (
        p72.get("counting_bound")
        != "#{i<j:a_i<=A}<=3+(2^(A+1)*S*exp(1/S)/3)*(1+3*j/S)^(1/9)"
    ):
        fail("P72 counting bound mismatch")
    if (
        p72.get("density_consequence")
        != "for every epsilon>0, a_i>(8/9-epsilon)*log2(i) on a density-one set of positive indices"
    ):
        fail("P72 density consequence mismatch")
    if p72.get("finite_first_crossing") != "d<S*(exp(1/S)*(1+3*q/S)^(1/9)-1)":
        fail("P72 finite crossing mismatch")
    overlap = data.get("literature_overlap")
    if not isinstance(overlap, dict) or set(overlap) != {
        "Lagarias_1985",
        "Monks_Yazinski_2004",
        "Lopez_Stoll_2009_2021",
        "novelty_boundary",
    }:
        fail("P72 literature audit mismatch")
    if "No claim of literature-wide novelty" not in str(overlap.get("novelty_boundary")):
        fail("P72 novelty boundary missing")
    if data.get("what_this_result_does_not_prove") is None:
        fail("P72 limitation missing")
    arithmetic = data.get("exact_exponent_arithmetic")
    if not isinstance(arithmetic, dict):
        fail("P72 exact exponent arithmetic missing")
    packing_coefficient = fraction(arithmetic.get("coprime_to_six_harmonic_coefficient"))
    recurrence_coefficient = fraction(arithmetic.get("normalized_log_recurrence_coefficient"))
    growth_exponent = fraction(arithmetic.get("growth_exponent"))
    density_threshold = fraction(arithmetic.get("density_threshold_coefficient"))
    if packing_coefficient != Fraction(1, 3) or recurrence_coefficient != Fraction(1, 3):
        fail("P72 primitive exponent coefficient mismatch")
    if growth_exponent != packing_coefficient * recurrence_coefficient or growth_exponent != Fraction(1, 9):
        fail("P72 growth exponent arithmetic failed")
    if density_threshold != 1 - growth_exponent or fraction(arithmetic.get("threshold_plus_growth")) != 1:
        fail("P72 density threshold arithmetic failed")

    # Independent algebraic regression on actual parity words.  This does not
    # infer the theorem from samples; it checks the normalization conventions.
    for source in (3, 7, 27, 31, 703, 6171):
        independently_trace(source, 48)
    # Independently verify the local count used in the general packing proof.
    for left in range(1, 80):
        for right in range(left, left + 80):
            actual = sum(math.gcd(value, 6) == 1 for value in range(left, right + 1))
            if actual > 2 + (right - left) // 3:
                fail("P72 local mod-six packing regression failed")


def affine_residue(word: str) -> tuple[int, int, int]:
    multiplier = 1
    translation = 0
    power = 1
    for symbol in word:
        if symbol == "1":
            multiplier *= 3
            translation = 3 * translation + power
        power *= 2
    residue = (-translation * pow(multiplier, -1, power)) % power
    return residue, multiplier, translation


def word_from_source(source: int, length: int) -> str:
    symbols = []
    for _ in range(length):
        symbols.append(str(source & 1))
        source = collatz(source)
    return "".join(symbols)


def expected_contact(maximum_q: int) -> tuple[str, list[dict[str, object]]]:
    digest = hashlib.sha256()
    selected = []
    wanted = {1, 2, 3, 4, 8, 16, 32, 64, 128, 256, maximum_q}
    for q in range(1, maximum_q + 1):
        length = lower_power_index(q)
        occupied = {lower_power_index(index) for index in range(q)}
        word = "".join("1" if k in occupied else "0" for k in range(length))
        residue, multiplier, translation = affine_residue(word)
        representative = residue or 1 << length
        if word.count("1") != q or word_from_source(representative, length) != word:
            fail("P73 finite mechanical prefix failed")
        digest.update(f"{q}|{length}|{word}|{residue}|{multiplier}|{translation}\n".encode("ascii"))
        if q in wanted:
            selected.append(
                {
                    "q": q,
                    "length": length,
                    "word_prefix": word[:96],
                    "word_sha256": hashlib.sha256(word.encode("ascii")).hexdigest(),
                    "canonical_residue": residue,
                }
            )
    return digest.hexdigest(), selected


def verify_all_contact(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase12-all-contact-v1" or data.get("proves_collatz") is not False:
        fail("P73 artifact boundary mismatch")
    p73 = data.get("P73")
    if not isinstance(p73, dict) or p73.get("repository_status") != "VERIFIED_THEOREM":
        fail("P73 status mismatch")
    if (
        p73.get("mechanical_identification")
        != "odd positions d_j=floor(j*log2(3)); equivalently the upper mechanical word 1c_alpha with alpha=ln(2)/ln(3)"
    ):
        fail("P73 mechanical word mismatch")
    if p73.get("packing_contradiction") != "a_j=0 for every j makes the P72 A=0 counting bound read j=O(j^(1/9))":
        fail("P73 packing contradiction mismatch")
    regression = data.get("finite_prefix_regression")
    if not isinstance(regression, dict) or not isinstance(regression.get("maximum_q"), int):
        fail("P73 finite regression missing")
    maximum_q = regression["maximum_q"]
    digest, selected = expected_contact(maximum_q)
    if regression.get("row_digest_sha256") != digest or regression.get("selected_rows") != selected:
        fail("P73 finite prefix digest mismatch")
    return maximum_q


def odd_normal_form(value: int) -> int:
    return value >> valuation_two(value)


def independent_adversaries() -> list[tuple[str, int]]:
    seeds: list[tuple[str, int]] = []
    for exponent in range(3, 25):
        seeds.append(("2^m-1", (1 << exponent) - 1))
    for exponent in range(1, 11):
        seeds.append(("8^m-5", 8**exponent - 5))
    for blocks in range(1, 11):
        for mask in range(1 << blocks):
            bits = "".join("111" if mask & (1 << index) else "110" for index in range(blocks))
            seeds.append(("(110|111)^*", int(bits, 2)))
    seeds.append(("A=11101", int(A_BITS, 2)))
    seeds.append(("B=1100", int(B_BITS, 2)))
    for r in range(1, 9):
        for s in range(1, 9):
            seeds.append(("A^rB^s", int(A_BITS * r + B_BITS * s, 2)))
    return seeds


def expected_adversarial(cap: int) -> dict[str, object]:
    digest = hashlib.sha256()
    families: Counter[str] = Counter()
    stops: Counter[str] = Counter()
    longest = (0, "", 0, 0)
    for family, raw in independent_adversaries():
        start = odd_normal_form(raw)
        row = independently_trace(start, cap)
        families[family] += 1
        stops[str(row["reason"])] += 1
        digest.update(
            f"{family}|{raw}|{start}|{row['reason']}|{row['odd_count']}|{row['ordinary_steps']}|{row['a_values']}\n".encode(
                "ascii"
            )
        )
        longest = max(longest, (int(row["odd_count"]), family, raw, start))
    return {
        "families": dict(sorted(families.items())),
        "reason_counts": dict(sorted(stops.items())),
        "instance_count": sum(families.values()),
        "row_digest_sha256": digest.hexdigest(),
        "longest_safe_prefix": {
            "odd_count": longest[0],
            "family": longest[1],
            "raw_start": longest[2],
            "normalized_odd_start": longest[3],
        },
    }


def expected_finite(bound: int, cap: int) -> dict[str, object]:
    digest = hashlib.sha256()
    stops: Counter[str] = Counter()
    maximum = (0, 0)
    crossing_count = 0
    least_slack: Fraction | None = None
    selected = []
    starts = list(range(3, bound + 1, 4))
    for start in starts:
        row = independently_trace(start, cap)
        stops[str(row["reason"])] += 1
        if int(row["odd_count"]) > maximum[0]:
            maximum = (int(row["odd_count"]), start)
        crossing = row["crossing"]
        if isinstance(crossing, dict):
            crossing_count += 1
            slack = fraction(crossing["Y_q"]) - int(crossing["endpoint"])
            if slack <= 0:
                fail("E20 finite first-crossing bound failed")
            least_slack = slack if least_slack is None else min(least_slack, slack)
        digest.update(
            f"{start}|{row['reason']}|{row['odd_count']}|{row['ordinary_steps']}|{row['odd_positions']}|{row['odd_values']}|{row['Y_final']}\n".encode(
                "ascii"
            )
        )
        if start in {3, 7, 27, 31, 703, 1126015} or start == maximum[1]:
            selected.append(row)
    return {
        "repository_status": "VERIFIED_FINITE",
        "start_definition": "all S<=start_bound with S=3 mod 4",
        "start_bound": bound,
        "maximum_odd_horizon": cap,
        "start_count": len(starts),
        "reason_counts": dict(sorted(stops.items())),
        "maximum_recorded_odd_count": maximum[0],
        "first_maximum_witness": maximum[1],
        "first_crossing_count": crossing_count,
        "minimum_exact_Yq_minus_endpoint": None if least_slack is None else encoded(least_slack),
        "row_digest_sha256": digest.hexdigest(),
        "selected_rows": selected,
        "adversarial": expected_adversarial(cap),
    }


def verify_finite(data: dict[str, object]) -> tuple[int, int]:
    if data.get("format") != "collatz-phase12-finite-orbit-audit-v1" or data.get("proves_collatz") is not False:
        fail("E20 artifact boundary mismatch")
    stored = data.get("E20")
    if not isinstance(stored, dict):
        fail("E20 audit missing")
    bound, cap = stored.get("start_bound"), stored.get("maximum_odd_horizon")
    if not isinstance(bound, int) or not isinstance(cap, int) or bound < 3 or cap < 1:
        fail("E20 audit parameters invalid")
    expected = expected_finite(bound, cap)
    if stored != expected:
        fail("E20 finite orbit or adversarial audit mismatch")
    return bound, expected["adversarial"]["instance_count"]


def expected_obstruction(terms: int) -> tuple[str, list[dict[str, int]]]:
    candidates = []
    value = 1
    while len(candidates) < terms:
        if math.gcd(value, 6) == 1:
            candidates.append(value)
        value += 1
    product = Fraction(1)
    digest = hashlib.sha256()
    selected = []
    checkpoints = {1, 2, 4, 16, 64, 256, 1024, terms}
    for index, candidate in enumerate(candidates, 1):
        product *= Fraction(3 * candidate + 1, 3 * candidate)
        digest.update(f"{index}|{candidate}|{product.numerator}|{product.denominator}\n".encode("ascii"))
        if index in checkpoints:
            selected.append(
                {
                    "terms": index,
                    "last_value": candidate,
                    "product_numerator_bits": product.numerator.bit_length(),
                    "product_denominator_bits": product.denominator.bit_length(),
                }
            )
    return digest.hexdigest(), selected


def verify_obstruction(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase12-packing-obstruction-v1" or data.get("proves_collatz") is not False:
        fail("NG21 artifact boundary mismatch")
    ng21, h72 = data.get("NG21"), data.get("H72")
    if not isinstance(ng21, dict) or ng21.get("repository_status") != "REFUTED":
        fail("NG21 status mismatch")
    if not isinstance(h72, dict) or h72.get("repository_status") != "OPEN":
        fail("H72 status mismatch")
    if "not an example of a Collatz orbit" not in str(data.get("what_this_result_does_not_prove")):
        fail("NG21 scope boundary missing")
    finite = data.get("finite_regression")
    if not isinstance(finite, dict) or not isinstance(finite.get("maximum_terms"), int):
        fail("NG21 finite regression missing")
    terms = finite["maximum_terms"]
    digest, selected = expected_obstruction(terms)
    expected = {
        "maximum_terms": terms,
        "row_digest_sha256": digest,
        "selected_rows": selected,
        "exact_two_per_complete_six_block": True,
    }
    if finite != expected:
        fail("NG21 obstruction digest mismatch")
    return terms


def verify(artifact_dir: Path) -> dict[str, object]:
    theorem = load(artifact_dir / "phase12_packing_theorem.json")
    contact = load(artifact_dir / "phase12_all_contact.json")
    finite = load(artifact_dir / "phase12_finite_orbits.json")
    obstruction = load(artifact_dir / "phase12_packing_obstruction.json")
    verify_symbolic_theorem(theorem)
    contact_q = verify_all_contact(contact)
    start_bound, adversarial_count = verify_finite(finite)
    obstruction_terms = verify_obstruction(obstruction)
    return {
        "valid": True,
        "P72": "VERIFIED_THEOREM",
        "P73": "VERIFIED_THEOREM",
        "E20": "VERIFIED_FINITE",
        "NG21": "REFUTED",
        "H72": "OPEN",
        "start_bound": start_bound,
        "all_contact_q": contact_q,
        "packing_obstruction_terms": obstruction_terms,
        "adversarial_instances": adversarial_count,
        "remaining_P69_branches": ["nontrivial cycle", "infinite coefficient-safe tail", "finite-crossing renewal ladder"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except ValueError as error:
        print(json.dumps({"valid": False, "error": str(error), "proves_collatz": False}, indent=2, sort_keys=True))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
