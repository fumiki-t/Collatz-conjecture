#!/usr/bin/env python3
"""Independent exact verifier for Phase 37 uniform-sparsity artifacts.

This file imports neither the Phase 37 generator nor any ``src`` module.  It
rebuilds the rational induction certificate, affine/parity corpus, renewal
convention corpus, and mandatory regressions with separate enumeration paths.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


CLAIMS = {
    "P219": "VERIFIED_THEOREM",
    "P220": "VERIFIED_THEOREM",
    "P221": "VERIFIED_THEOREM",
    "P222": "VERIFIED_THEOREM",
    "P223": "VERIFIED_THEOREM",
    "P224": "VERIFIED_THEOREM",
    "P225": "VERIFIED_THEOREM",
    "P226": "VERIFIED_THEOREM",
    "E53": "VERIFIED_FINITE",
    "H70": "OPEN",
    "H72": "OPEN",
    "H133": "OPEN",
}
FILES = (
    "phase37_theory.json",
    "phase37_induction_certificate.json",
    "phase37_affine_interval_audit.json",
    "phase37_renewal_audit.json",
    "phase37_regressions.json",
    "phase37_obstruction_report.md",
)


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        fail(f"{path.name} is not an object")
    return value


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(rows: object) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def affine_from_positions(length: int, positions: Sequence[int]) -> tuple[int, int]:
    odd_count = len(positions)
    correction = sum(
        3 ** (odd_count - index - 1) * 2**position
        for index, position in enumerate(positions)
    )
    return odd_count, correction


def bits_from_mask(mask: int, length: int) -> tuple[int, ...]:
    return tuple(1 if mask & (1 << position) else 0 for position in range(length))


def affine_from_bits(bits: Sequence[int]) -> tuple[int, int]:
    positions = tuple(index for index, bit in enumerate(bits) if bit)
    return affine_from_positions(len(bits), positions)


def source_residue(bits: Sequence[int]) -> int:
    odd_count, correction = affine_from_bits(bits)
    modulus = 2 ** len(bits)
    return (-correction * pow(pow(3, odd_count), -1, modulus)) % modulus


def direct_iterate(source: int, steps: int) -> tuple[list[int], tuple[int, ...]]:
    trace = [source]
    parity = []
    for _ in range(steps):
        current = trace[-1]
        parity.append(current % 2)
        trace.append(current // 2 if current % 2 == 0 else (3 * current + 1) // 2)
    return trace, tuple(parity)


def verify_induction(data: dict[str, object]) -> None:
    if data.get("format") != "collatz-phase37-induction-certificate-v1":
        fail("induction format")
    if data.get("proves_collatz") is not False:
        fail("induction overclaim")
    if data.get("floating_point_used_for_acceptance") is not False:
        fail("floating-point acceptance")
    params = data.get("rational_parameters")
    if params != {"theta": [14, 23], "rho": [29, 30], "constant": 32, "N0": 135}:
        fail("induction parameters")
    if not 3**14 < 2**23:
        fail("contraction certificate")
    if not 3**406 < 2**667:
        fail("low-ratio certificate")
    if not 23**690 < 2**667 * 14**420 * 9**270:
        fail("entropy certificate")

    recursive = lambda n: 4**23 * 3 ** (14 * n) < 2 ** (23 * n)
    low = lambda n: 24**690 * 3 ** (406 * n) <= 2 ** (667 * n)
    recursive_minimum = min(n for n in range(1, 136) if recursive(n))
    low_minimum = min(n for n in range(1, 136) if low(n))
    if (recursive_minimum, low_minimum) != (57, 135):
        fail("induction threshold reconstruction")
    if low(134) or not low(135) or not 2**134 < 32**30:
        fail("induction boundary")
    comparisons = data.get("exact_comparisons")
    expected = {
        "contraction": {"left": "3^14", "relation": "<", "right": "2^23"},
        "low_ratio": {"left": "3^406", "relation": "<", "right": "2^667"},
        "entropy": {"left": "23^690", "relation": "<", "right": "2^667*14^420*9^270"},
        "recursive_argument_minimum_N": 57,
        "low_half_minimum_N": 135,
        "low_half_N0_minus_1": False,
        "low_half_N0": True,
        "base_bound": "2^134 < 32^30",
    }
    if comparisons != expected:
        fail("stored induction comparisons")
    bounds = data.get("induction_bounds")
    if not isinstance(bounds, dict):
        fail("induction bounds")
    if bounds.get("explicit_theorem") != "G(X)<32*X^(29/30) for every integer X>=1":
        fail("explicit theorem statement")
    if "rho>H2(1/log2(3))" not in str(data.get("limiting_theorem")):
        fail("limiting theorem statement")


def rebuild_affine() -> dict[str, object]:
    extrema_rows: list[list[object]] = []
    counts = {
        "words": 0,
        "groups": 0,
        "residue_reconstructions": 0,
        "translation_cases": 0,
        "translated_points": 0,
        "diameter_groups": 0,
    }
    for length in range(1, 17):
        modulus = 2**length
        for odd_count in range(length + 1):
            values = []
            for positions in itertools.combinations(range(length), odd_count):
                _, correction = affine_from_positions(length, positions)
                mask = sum(1 << position for position in positions)
                bits = bits_from_mask(mask, length)
                residue = source_residue(bits)
                source = residue if residue else modulus
                trace, observed = direct_iterate(source, length)
                if observed != bits:
                    fail("parity residue reconstruction")
                if trace[-1] * modulus != 3**odd_count * source + correction:
                    fail("affine endpoint reconstruction")
                values.append((correction, mask))
                counts["words"] += 1
                counts["residue_reconstructions"] += 1
            values.sort()
            expected_min = 3**odd_count - 2**odd_count
            expected_max = 2 ** (length - odd_count) * expected_min
            if values[0] != (expected_min, (1 << odd_count) - 1):
                fail("fixed-count minimum")
            if values[-1] != (expected_max, ((1 << odd_count) - 1) << (length - odd_count)):
                fail("fixed-count maximum")
            if len(values) != math.comb(length, odd_count):
                fail("fixed-count cardinality")
            extrema_rows.append([
                length, odd_count, len(values), values[0][0], values[-1][0],
                values[0][1], values[-1][1],
            ])
            counts["groups"] += 1

    translation_rows: list[list[object]] = []
    for length in range(1, 13):
        modulus = pow(2, length)
        starts = [1, modulus + 3, pow(10, 30) + 37 * length, pow(2, 200) + 19 * length]
        widths = sorted(set((1, max(1, pow(2, length // 2)), max(1, pow(2, length - 1)), modulus)))
        for start in starts:
            for width in widths:
                buckets: dict[int, list[int]] = defaultdict(list)
                parity_words = set()
                for offset in range(width):
                    trace, parity = direct_iterate(start + offset, length)
                    if parity in parity_words:
                        fail("translated parity collision")
                    parity_words.add(parity)
                    buckets[sum(parity)].append(trace[-1])
                    counts["translated_points"] += 1
                for odd_count in sorted(buckets):
                    images = buckets[odd_count]
                    bound = 2 * pow(3, odd_count)
                    if max(images) - min(images) >= bound:
                        fail("translated diameter")
                    translation_rows.append([
                        length, str(start), width, odd_count, len(images),
                        str(min(images)), str(max(images)), str(bound),
                    ])
                    counts["diameter_groups"] += 1
                counts["translation_cases"] += 1
    return {
        "format": "collatz-phase37-affine-interval-audit-v1",
        "maximum_word_length": 16,
        "maximum_translation_length": 12,
        "counts": counts,
        "extrema_digest_sha256": stable_hash(extrema_rows),
        "translation_digest_sha256": stable_hash(translation_rows),
        "selected_extrema": extrema_rows[:8] + extrema_rows[-8:],
        "selected_translations": translation_rows[:8] + translation_rows[-8:],
        "scope": "Exhaustive affine/parity audit through N<=16 and exact translated-interval checks through N<=12; the all-N conclusion is the symbolic P219/P220 proof.",
        "proves_collatz": False,
    }


def compare_coefficients(first: tuple[int, int], second: tuple[int, int]) -> int:
    q1, n1 = first
    q2, n2 = second
    left = pow(3, q1) * pow(2, n2)
    right = pow(3, q2) * pow(2, n1)
    return (left > right) - (left < right)


def crossing_words(maximum_length: int) -> list[str]:
    active = [""]
    answer = []
    for length in range(1, maximum_length + 1):
        following = []
        for prefix in active:
            for bit in "01":
                word = prefix + bit
                if pow(3, word.count("1")) > pow(2, length):
                    answer.append(word)
                else:
                    following.append(word)
        active = following
    return sorted(answer, key=lambda word: (len(word), word))


def rebuild_renewal() -> dict[str, object]:
    counts = {
        "orbit_starts": 0,
        "orbit_steps": 0,
        "product_checks": 0,
        "finite_minimum_checks": 0,
        "renewal_codewords": 0,
        "renewal_addresses": 0,
        "renewal_boundaries": 0,
        "companion_transition_checks": 0,
    }
    orbit_hasher = hashlib.sha256()
    selected_orbits = []
    for source in range(1, 4097):
        current = source
        visited = set()
        q = 0
        correction = 0
        product_numerator = Fraction(1)
        coefficient_path = [(0, 0)]
        path = [source]
        for step in range(512):
            if current in visited:
                break
            visited.add(current)
            if current % 2:
                product_numerator *= Fraction(3 * current + 1, 3 * current)
                correction = 3 * correction + pow(2, step)
                q += 1
                current = (3 * current + 1) // 2
            else:
                current //= 2
            path.append(current)
            coefficient_path.append((q, step + 1))
            if current * pow(2, step + 1) != pow(3, q) * source + correction:
                fail("orbit affine check")
            if Fraction(current * pow(2, step + 1), source * pow(3, q)) != product_numerator:
                fail("orbit product check")
            counts["orbit_steps"] += 1
            counts["product_checks"] += 1
        minimum = min(
            range(len(coefficient_path)),
            key=lambda index: Fraction(pow(3, coefficient_path[index][0]), pow(2, coefficient_path[index][1])),
        )
        if minimum + 1 < len(path):
            if path[minimum] % 2 == 0:
                fail("minimum parity")
            for later in range(minimum + 1, len(path)):
                if compare_coefficients(coefficient_path[later], coefficient_path[minimum]) <= 0:
                    fail("minimum uniqueness")
                if path[later] <= path[minimum]:
                    fail("state suffix minimum")
            counts["finite_minimum_checks"] += 1
        row = [source, len(path) - 1, q, correction, current, minimum, path[minimum]]
        orbit_hasher.update(json.dumps(row, separators=(",", ":")).encode("ascii") + b"\n")
        if source in {1, 3, 7, 27, 31, 167, 255, 1023, 2075, 4095}:
            selected_orbits.append(row)
        counts["orbit_starts"] += 1

    codes = crossing_words(16)
    counts["renewal_codewords"] = len(codes)
    for index, left in enumerate(codes):
        if any(right.startswith(left) for right in codes[index + 1:]):
            fail("prefix-free code")
    block_rows = []
    for code in codes:
        forward = code[::-1]
        bits = tuple(map(int, forward))
        odd_count, correction = affine_from_bits(bits)
        length = len(bits)
        residue = source_residue(bits)
        source = residue if residue else pow(2, length)
        trace, observed = direct_iterate(source, length)
        c = Fraction(pow(3, odd_count), pow(2, length))
        threshold = Fraction(correction + pow(2, length), pow(3, odd_count))
        if observed != bits or trace[-1] + 1 != c * (source + threshold):
            fail("renewal positive transition")
        h = threshold + Fraction(1, 3)
        next_h = c * h - Fraction(correction, pow(2, length))
        if next_h <= 1 or (next_h > 1) != (h > threshold):
            fail("renewal companion transition")
        block_rows.append([
            code, forward, length, odd_count, correction, source, trace[-1],
            [threshold.numerator, threshold.denominator],
            [next_h.numerator, next_h.denominator],
        ])
        counts["companion_transition_checks"] += 1

    short = [word for word in codes if len(word) <= 8]
    address_rows = []
    stop = False
    for block_count in range(1, 4):
        for address in itertools.product(short, repeat=block_count):
            if len(address_rows) >= 5000:
                stop = True
                break
            blocks = [word[::-1] for word in address]
            word = "".join(blocks)
            bits = tuple(map(int, word))
            residue = source_residue(bits)
            source = residue if residue else pow(2, len(bits))
            path, observed = direct_iterate(source, len(bits))
            if observed != bits:
                fail("renewal address realization")
            boundaries = [0]
            for block in blocks:
                boundaries.append(boundaries[-1] + len(block))
            odd_prefix = [0]
            for bit in bits:
                odd_prefix.append(odd_prefix[-1] + bit)
            for boundary in boundaries[:-1]:
                for later in range(boundary + 1, len(bits) + 1):
                    relative = (odd_prefix[later] - odd_prefix[boundary], later - boundary)
                    if compare_coefficients(relative, (0, 0)) <= 0:
                        fail("renewal coefficient suffix")
                    if path[later] <= path[boundary]:
                        fail("renewal state suffix")
                counts["renewal_boundaries"] += 1
            address_rows.append([
                list(address), word, source, path[-1], boundaries,
                [path[index] for index in boundaries],
            ])
            counts["renewal_addresses"] += 1
        if stop:
            break
    return {
        "format": "collatz-phase37-renewal-audit-v1",
        "bounds": {"maximum_start": 4096, "step_limit": 512, "renewal_code_length": 16, "address_limit": 5000},
        "counts": counts,
        "orbit_digest_sha256": orbit_hasher.hexdigest(),
        "block_digest_sha256": stable_hash(block_rows),
        "address_digest_sha256": stable_hash(address_rows),
        "selected_orbits": selected_orbits,
        "selected_blocks": block_rows[:8] + block_rows[-8:],
        "selected_addresses": address_rows[:5] + address_rows[-5:],
        "scope": "Finite exact convention checks only; no tested terminating orbit is promoted to a nonperiodic-orbit theorem.",
        "proves_collatz": False,
    }


def rebuild_regressions() -> dict[str, object]:
    sources = {27, 31, 167, 2075}
    for exponent in range(2, 15):
        sources.update((pow(2, exponent) - 1, pow(8, exponent) - 5))
    words = {"110", "111", "11101", "1100", "111011100"}
    words.update("11101" * a + "1100" * b for a in range(1, 5) for b in range(1, 5))
    words.update("".join(choice) for choice in itertools.product(("110", "111"), repeat=4))
    rows = []
    for source in sorted(sources):
        trace, bits = direct_iterate(source, 96)
        odd_count, correction = affine_from_bits(bits)
        if trace[-1] * pow(2, 96) != pow(3, odd_count) * source + correction:
            fail("source regression")
        rows.append(["source", str(source), odd_count, str(correction), str(trace[-1])])
    for word in sorted(words):
        bits = tuple(map(int, word))
        odd_count, correction = affine_from_bits(bits)
        maximum = pow(2, len(bits) - odd_count) * (pow(3, odd_count) - pow(2, odd_count))
        residue = source_residue(bits)
        source = residue if residue else pow(2, len(bits))
        trace, observed = direct_iterate(source, len(bits))
        if observed != bits or correction > maximum:
            fail("word regression")
        rows.append(["word", word, odd_count, str(correction), str(maximum), str(source), str(trace[-1])])
    for cycle in ((-1,), (-5, -7, -10)):
        for index, value in enumerate(cycle):
            following = value // 2 if value % 2 == 0 else (3 * value + 1) // 2
            if following != cycle[(index + 1) % len(cycle)]:
                fail("negative-cycle control")
    return {
        "format": "collatz-phase37-regressions-v1",
        "mandatory_families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"],
        "documented_scope_boundaries": ["NG21-NG42", "rational shadows", "P206/P218 orientation split"],
        "exact_controls": ["source 167", "trivial cycle and powers", "negative cycles"],
        "counts": {"source_rows": len(sources), "word_rows": len(words), "negative_cycles": 2},
        "row_digest_sha256": stable_hash(rows),
        "selected_rows": rows[:8] + rows[-8:],
        "boundary": "Negative cycles and formal words are convention controls, not positive equal-time collision-free evidence.",
        "proves_collatz": False,
    }


def verify_theory(data: dict[str, object]) -> None:
    if data.get("format") != "collatz-phase37-theory-v1" or data.get("claims") != CLAIMS:
        fail("theory claim map")
    if data.get("proves_collatz") is not False:
        fail("theory overclaim")
    for claim in ("P219", "P220", "P221", "P222", "P223", "P224", "P225", "P226"):
        if not isinstance(data.get(claim), str) or not data[claim]:
            fail(f"missing {claim} statement")
    repairs = data.get("scope_repairs")
    if not isinstance(repairs, list) or not any("rho*<rho<1" in str(item).replace(" ", "") for item in repairs):
        fail("rho scope repair")
    boundary = str(data.get("what_this_result_does_not_prove"))
    if "Collatz proof" not in boundary or "P80" not in boundary:
        fail("theory interpretation boundary")


def verify_obstruction(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = (
        "G(X)<32 X^(29/30)",
        "N0=135",
        "P80",
        "NG22",
        "does not prove H72",
        "proves_collatz=false",
    )
    if any(fragment not in text for fragment in required):
        fail("obstruction report boundary")


def verify(artifact_dir: Path) -> dict[str, object]:
    theory = load(artifact_dir / "phase37_theory.json")
    induction = load(artifact_dir / "phase37_induction_certificate.json")
    affine = load(artifact_dir / "phase37_affine_interval_audit.json")
    renewal = load(artifact_dir / "phase37_renewal_audit.json")
    regressions = load(artifact_dir / "phase37_regressions.json")
    verify_theory(theory)
    verify_induction(induction)
    expected_affine = rebuild_affine()
    if affine != expected_affine:
        fail("affine interval artifact mismatch")
    expected_renewal = rebuild_renewal()
    if renewal != expected_renewal:
        fail("renewal artifact mismatch")
    expected_regressions = rebuild_regressions()
    if regressions != expected_regressions:
        fail("regression artifact mismatch")
    verify_obstruction(artifact_dir / "phase37_obstruction_report.md")
    source_text = Path(__file__).read_text(encoding="utf-8")
    forbidden = "phase37_" + "search"
    if forbidden in source_text:
        fail("generator import detected")
    return {
        "format": "collatz-phase37-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "claims": CLAIMS,
        "explicit_constant": 32,
        "induction_N0": 135,
        "affine_counts": expected_affine["counts"],
        "renewal_counts": expected_renewal["counts"],
        "regression_counts": expected_regressions["counts"],
        "input_sha256": {name: digest(artifact_dir / name) for name in FILES},
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (OSError, VerificationError, ValueError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, indent=2))
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
