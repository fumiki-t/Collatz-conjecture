#!/usr/bin/env python3
"""Generate exact Phase 37 uniform-sparsity evidence.

The supplied Phase 37 note is treated as an untrusted proposal.  The theorem
proof is recorded in the audit report; this generator emits exact induction
certificates and bounded convention checks.  Floating point is never used for
an acceptance decision.
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
from typing import Iterable, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


THETA_NUM = 14
THETA_DEN = 23
RHO_NUM = 29
RHO_DEN = 30
INDUCTION_N0 = 135
EXPLICIT_CONSTANT = 32
AFFINE_MAX_N = 16
TRANSLATION_MAX_N = 12
ORBIT_MAX_START = 4096
ORBIT_STEP_LIMIT = 512

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


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(rows: object) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def word_data(bits: Sequence[int]) -> tuple[int, int]:
    """Return (odd count, affine correction B) for the literal shortcut word."""
    correction = 0
    odd_count = 0
    for position, bit in enumerate(bits):
        if bit not in (0, 1):
            raise ValueError("binary word required")
        if bit:
            correction = 3 * correction + (1 << position)
            odd_count += 1
    return odd_count, correction


def correction_maximum(length: int, odd_count: int) -> int:
    if not 0 <= odd_count <= length:
        raise ValueError("invalid odd count")
    return (1 << (length - odd_count)) * (3**odd_count - 2**odd_count)


def correction_minimum(odd_count: int) -> int:
    return 3**odd_count - 2**odd_count


def canonical_source(bits: Sequence[int]) -> int:
    odd_count, correction = word_data(bits)
    modulus = 1 << len(bits)
    return (-correction * pow(3**odd_count, -1, modulus)) % modulus


def shortcut_trace(source: int, steps: int) -> tuple[list[int], tuple[int, ...]]:
    values = [source]
    bits = []
    for _ in range(steps):
        bit = values[-1] & 1
        bits.append(bit)
        values.append((3 * values[-1] + 1) // 2 if bit else values[-1] // 2)
    return values, tuple(bits)


def realizes(source: int, bits: Sequence[int]) -> tuple[bool, int]:
    value = source
    for bit in bits:
        if value & 1 != bit:
            return False, value
        value = (3 * value + 1) // 2 if bit else value // 2
    return True, value


def induction_certificate() -> dict[str, object]:
    entropy_left = 23**690
    entropy_right = 2**667 * 14**420 * 9**270
    contraction_left = 3**14
    contraction_right = 2**23

    def recursive_ok(n: int) -> bool:
        return 4**23 * 3 ** (14 * n) < 2 ** (23 * n)

    def low_ok(n: int) -> bool:
        return 24**690 * 3 ** (406 * n) <= 2 ** (667 * n)

    recursive_minimum = next(n for n in range(1, INDUCTION_N0 + 1) if recursive_ok(n))
    low_minimum = next(n for n in range(1, INDUCTION_N0 + 1) if low_ok(n))
    if recursive_minimum != 57 or low_minimum != INDUCTION_N0:
        raise AssertionError("induction threshold regression")
    if not contraction_left < contraction_right or not entropy_left < entropy_right:
        raise AssertionError("rational exponent certificate")
    if low_ok(INDUCTION_N0 - 1) or not low_ok(INDUCTION_N0):
        raise AssertionError("low-part minimality")
    # N<N0 implies X<=2^(N0-1), hence X^(1/30)<32.
    if not 2 ** (INDUCTION_N0 - 1) < EXPLICIT_CONSTANT**RHO_DEN:
        raise AssertionError("finite induction base")
    return {
        "format": "collatz-phase37-induction-certificate-v1",
        "rational_parameters": {
            "theta": [THETA_NUM, THETA_DEN],
            "rho": [RHO_NUM, RHO_DEN],
            "constant": EXPLICIT_CONSTANT,
            "N0": INDUCTION_N0,
        },
        "exact_comparisons": {
            "contraction": {"left": "3^14", "relation": "<", "right": "2^23"},
            "low_ratio": {"left": "3^406", "relation": "<", "right": "2^667"},
            "entropy": {
                "left": "23^690",
                "relation": "<",
                "right": "2^667*14^420*9^270",
            },
            "recursive_argument_minimum_N": recursive_minimum,
            "low_half_minimum_N": low_minimum,
            "low_half_N0_minus_1": False,
            "low_half_N0": True,
            "base_bound": "2^134 < 32^30",
        },
        "induction_bounds": {
            "recurrence": "G(X)<=sum_(0<=s<=floor(14N/23)) G(2*3^s)+2^(N*H2(14/23))",
            "recursive_arguments": "2*3^s<X for N>=135",
            "low_part": "<16*X^(29/30) after inserting the induction hypothesis",
            "high_part": "<2*X^(29/30)",
            "closure": "G(X)<18*X^(29/30)<32*X^(29/30)",
            "explicit_theorem": "G(X)<32*X^(29/30) for every integer X>=1",
        },
        "limiting_theorem": "For every rho>H2(1/log2(3)), G(X)=O_rho(X^rho); rho>=1 is trivial and rho<1 uses theta in (1/2,1/log2(3)).",
        "floating_point_used_for_acceptance": False,
        "proves_collatz": False,
    }


def affine_interval_audit() -> dict[str, object]:
    extrema_rows: list[list[object]] = []
    counts = {
        "words": 0,
        "groups": 0,
        "residue_reconstructions": 0,
        "translation_cases": 0,
        "translated_points": 0,
        "diameter_groups": 0,
    }
    samples: list[dict[str, object]] = []
    for length in range(1, AFFINE_MAX_N + 1):
        groups: dict[int, list[tuple[int, int]]] = defaultdict(list)
        modulus = 1 << length
        for mask in range(modulus):
            bits = tuple((mask >> position) & 1 for position in range(length))
            odd_count, correction = word_data(bits)
            residue = canonical_source(bits)
            representative = residue or modulus
            ok, endpoint = realizes(representative, bits)
            expected = (3**odd_count * representative + correction) // modulus
            if not ok or endpoint != expected:
                raise AssertionError("parity-cylinder reconstruction")
            groups[odd_count].append((correction, mask))
            counts["words"] += 1
            counts["residue_reconstructions"] += 1
        for odd_count, values in sorted(groups.items()):
            minimum = min(values)
            maximum = max(values)
            expected_minimum = correction_minimum(odd_count)
            expected_maximum = correction_maximum(length, odd_count)
            minimum_mask = (1 << odd_count) - 1
            maximum_mask = ((1 << odd_count) - 1) << (length - odd_count)
            if minimum != (expected_minimum, minimum_mask):
                raise AssertionError("affine minimum")
            if maximum != (expected_maximum, maximum_mask):
                raise AssertionError("affine maximum")
            if len(values) != math.comb(length, odd_count):
                raise AssertionError("fixed-weight count")
            extrema_rows.append([
                length, odd_count, len(values), minimum[0], maximum[0],
                minimum[1], maximum[1],
            ])
            counts["groups"] += 1

    translation_rows: list[list[object]] = []
    for length in range(1, TRANSLATION_MAX_N + 1):
        modulus = 1 << length
        starts = (1, modulus + 3, 10**30 + 37 * length, (1 << 200) + 19 * length)
        widths = sorted({1, max(1, 1 << (length // 2)), max(1, 1 << (length - 1)), modulus})
        for start, width in itertools.product(starts, widths):
            by_odd: dict[int, list[int]] = defaultdict(list)
            seen_vectors: set[tuple[int, ...]] = set()
            for source in range(start, start + width):
                values, bits = shortcut_trace(source, length)
                if bits in seen_vectors:
                    raise AssertionError("two sources in one parity cylinder")
                seen_vectors.add(bits)
                by_odd[sum(bits)].append(values[-1])
                counts["translated_points"] += 1
            for odd_count, images in sorted(by_odd.items()):
                span = max(images) - min(images)
                bound = 2 * 3**odd_count
                if not span < bound:
                    raise AssertionError("translation-uniform image diameter")
                translation_rows.append([
                    length, str(start), width, odd_count, len(images),
                    str(min(images)), str(max(images)), str(bound),
                ])
                counts["diameter_groups"] += 1
            counts["translation_cases"] += 1
    if counts["words"] != (1 << (AFFINE_MAX_N + 1)) - 2:
        raise AssertionError("word count")
    return {
        "format": "collatz-phase37-affine-interval-audit-v1",
        "maximum_word_length": AFFINE_MAX_N,
        "maximum_translation_length": TRANSLATION_MAX_N,
        "counts": counts,
        "extrema_digest_sha256": stable_hash(extrema_rows),
        "translation_digest_sha256": stable_hash(translation_rows),
        "selected_extrema": extrema_rows[:8] + extrema_rows[-8:],
        "selected_translations": translation_rows[:8] + translation_rows[-8:],
        "scope": "Exhaustive affine/parity audit through N<=16 and exact translated-interval checks through N<=12; the all-N conclusion is the symbolic P219/P220 proof.",
        "proves_collatz": False,
    }


def coefficient_compare(left: tuple[int, int], right: tuple[int, int]) -> int:
    """Compare 3^q/2^n pairs without logarithms."""
    q1, n1 = left
    q2, n2 = right
    a = 3 ** (q1 - min(q1, q2)) * 2 ** (n2 - min(n1, n2))
    b = 3 ** (q2 - min(q1, q2)) * 2 ** (n1 - min(n1, n2))
    return (a > b) - (a < b)


def first_upcrossing(code: str) -> bool:
    odd_count = 0
    for length, bit in enumerate(code, 1):
        odd_count += bit == "1"
        above = 3**odd_count > 2**length
        if length < len(code) and above:
            return False
    return 3**odd_count > 2 ** len(code)


def codewords(maximum_length: int) -> list[str]:
    result = []
    for length in range(1, maximum_length + 1):
        for mask in range(1 << length):
            code = "".join("1" if mask & (1 << position) else "0" for position in range(length))
            if first_upcrossing(code):
                result.append(code)
    return sorted(result, key=lambda word: (len(word), word))


def renewal_audit() -> dict[str, object]:
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
    orbit_digest = hashlib.sha256()
    selected_orbits = []
    for source in range(1, ORBIT_MAX_START + 1):
        value = source
        seen: set[int] = set()
        q = 0
        correction = 0
        product = Fraction(1)
        discrepancy_pairs = [(0, 0)]
        values = [source]
        for step in range(ORBIT_STEP_LIMIT):
            if value in seen:
                break
            seen.add(value)
            bit = value & 1
            if bit:
                product *= Fraction(3 * value + 1, 3 * value)
                correction = 3 * correction + (1 << step)
                q += 1
                value = (3 * value + 1) // 2
            else:
                value //= 2
            values.append(value)
            discrepancy_pairs.append((q, step + 1))
            if value * (1 << (step + 1)) != 3**q * source + correction:
                raise AssertionError("orbit affine identity")
            if Fraction(value * (1 << (step + 1)), source * 3**q) != product:
                raise AssertionError("orbit product identity")
            counts["orbit_steps"] += 1
            counts["product_checks"] += 1
        minimum = 0
        for index in range(1, len(discrepancy_pairs)):
            if coefficient_compare(discrepancy_pairs[index], discrepancy_pairs[minimum]) < 0:
                minimum = index
        if minimum + 1 < len(values):
            if not values[minimum] & 1:
                raise AssertionError("finite discrepancy minimum parity")
            for index in range(minimum + 1, len(values)):
                if coefficient_compare(discrepancy_pairs[index], discrepancy_pairs[minimum]) <= 0:
                    raise AssertionError("finite discrepancy minimum uniqueness")
                if values[index] <= values[minimum]:
                    raise AssertionError("finite suffix state minimum")
            counts["finite_minimum_checks"] += 1
        row = [source, len(values) - 1, q, correction, value, minimum, values[minimum]]
        orbit_digest.update(json.dumps(row, separators=(",", ":")).encode("ascii") + b"\n")
        if source in {1, 3, 7, 27, 31, 167, 255, 1023, 2075, 4095}:
            selected_orbits.append(row)
        counts["orbit_starts"] += 1

    codes = codewords(16)
    if any(right.startswith(left) for left, right in itertools.combinations(sorted(codes), 2)):
        raise AssertionError("renewal code prefix collision")
    counts["renewal_codewords"] = len(codes)
    block_rows = []
    for code in codes:
        forward = code[::-1]
        bits = tuple(int(bit) for bit in forward)
        odd_count, correction = word_data(bits)
        length = len(bits)
        source_residue = canonical_source(bits)
        source = source_residue or (1 << length)
        ok, endpoint = realizes(source, bits)
        c = Fraction(3**odd_count, 1 << length)
        R = Fraction(correction + (1 << length), 3**odd_count)
        if not ok or endpoint + 1 != c * (source + R):
            raise AssertionError("renewal positive transition")
        h = R + Fraction(1, 3)
        next_h = c * h - Fraction(correction, 1 << length)
        if not next_h > 1 or (next_h > 1) != (h > R):
            raise AssertionError("renewal companion threshold")
        block_rows.append([
            code, forward, length, odd_count, correction, source, endpoint,
            [R.numerator, R.denominator], [next_h.numerator, next_h.denominator],
        ])
        counts["companion_transition_checks"] += 1

    # Exhaustively concatenate small codewords.  Reversed first-upcrossing
    # blocks make every boundary a strict minimum of the remaining finite word.
    short = [code for code in codes if len(code) <= 8]
    address_rows = []
    for block_count in range(1, 4):
        for address in itertools.product(short, repeat=block_count):
            if len(address_rows) >= 5000:
                break
            forward_blocks = [code[::-1] for code in address]
            word = "".join(forward_blocks)
            bits = tuple(int(bit) for bit in word)
            source = canonical_source(bits) or (1 << len(bits))
            values, actual = shortcut_trace(source, len(bits))
            if actual != bits:
                raise AssertionError("renewal address source")
            boundaries = [0]
            for block in forward_blocks:
                boundaries.append(boundaries[-1] + len(block))
            q_prefix = [0]
            for bit in bits:
                q_prefix.append(q_prefix[-1] + bit)
            for boundary in boundaries[:-1]:
                base = (q_prefix[boundary], boundary)
                for index in range(boundary + 1, len(bits) + 1):
                    relative = (q_prefix[index] - q_prefix[boundary], index - boundary)
                    if coefficient_compare(relative, (0, 0)) <= 0:
                        raise AssertionError("renewal suffix coefficient")
                    if values[index] <= values[boundary]:
                        raise AssertionError("renewal suffix state")
                counts["renewal_boundaries"] += 1
            row = [list(address), word, source, values[-1], boundaries,
                   [values[index] for index in boundaries]]
            address_rows.append(row)
            counts["renewal_addresses"] += 1
        if len(address_rows) >= 5000:
            break
    return {
        "format": "collatz-phase37-renewal-audit-v1",
        "bounds": {
            "maximum_start": ORBIT_MAX_START,
            "step_limit": ORBIT_STEP_LIMIT,
            "renewal_code_length": 16,
            "address_limit": 5000,
        },
        "counts": counts,
        "orbit_digest_sha256": orbit_digest.hexdigest(),
        "block_digest_sha256": stable_hash(block_rows),
        "address_digest_sha256": stable_hash(address_rows),
        "selected_orbits": selected_orbits,
        "selected_blocks": block_rows[:8] + block_rows[-8:],
        "selected_addresses": address_rows[:5] + address_rows[-5:],
        "scope": "Finite exact convention checks only; no tested terminating orbit is promoted to a nonperiodic-orbit theorem.",
        "proves_collatz": False,
    }


def regression_audit() -> dict[str, object]:
    sources = set()
    for exponent in range(2, 15):
        sources.add((1 << exponent) - 1)
        sources.add(8**exponent - 5)
    sources.update({27, 31, 167, 2075})
    words = {"110", "111", "11101", "1100", "111011100"}
    for repetitions_a in range(1, 5):
        for repetitions_b in range(1, 5):
            words.add("11101" * repetitions_a + "1100" * repetitions_b)
    for choices in itertools.product(("110", "111"), repeat=4):
        words.add("".join(choices))
    rows = []
    for source in sorted(sources):
        values, bits = shortcut_trace(source, 96)
        odd_count, correction = word_data(bits)
        if values[-1] * (1 << 96) != 3**odd_count * source + correction:
            raise AssertionError("adversarial source affine identity")
        rows.append(["source", str(source), odd_count, str(correction), str(values[-1])])
    for word in sorted(words):
        bits = tuple(int(bit) for bit in word)
        odd_count, correction = word_data(bits)
        maximum = correction_maximum(len(bits), odd_count)
        source = canonical_source(bits) or (1 << len(bits))
        ok, endpoint = realizes(source, bits)
        if not ok or correction > maximum:
            raise AssertionError("adversarial word audit")
        rows.append(["word", word, odd_count, str(correction), str(maximum), str(source), str(endpoint)])
    negative_cycles = [[-1], [-5, -7, -10]]
    for cycle in negative_cycles:
        for value in cycle:
            following = (3 * value + 1) // 2 if value & 1 else value // 2
            if following != cycle[(cycle.index(value) + 1) % len(cycle)]:
                raise AssertionError("negative cycle control")
    return {
        "format": "collatz-phase37-regressions-v1",
        "mandatory_families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"],
        "documented_scope_boundaries": ["NG21-NG42", "rational shadows", "P206/P218 orientation split"],
        "exact_controls": ["source 167", "trivial cycle and powers", "negative cycles"],
        "counts": {"source_rows": len(sources), "word_rows": len(words), "negative_cycles": len(negative_cycles)},
        "row_digest_sha256": stable_hash(rows),
        "selected_rows": rows[:8] + rows[-8:],
        "boundary": "Negative cycles and formal words are convention controls, not positive equal-time collision-free evidence.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase37-theory-v1",
        "claims": CLAIMS,
        "P219": "At fixed N and odd count s, B is maximized by 0^(N-s)1^s and is at most 2^(N-s)(3^s-2^s); all images of a length-X interval with X<=2^N fit in an interval of length 2*3^s.",
        "P220": "Every equal-time collision-free positive set obeys a location-uniform G(X)=O_rho(X^rho) for rho>H2(1/log2(3)); explicitly G(X)<32X^(29/30).",
        "P221": "Uniform dyadic shells give every p>rho>rho* tail moment O(S^(rho-p)), including reciprocal summability after choosing rho<1.",
        "P222": "Every non-eventually-periodic positive integer shortcut orbit has discrepancy tending to +infinity and an odd permanent coefficient-safe suffix minimum; the finite-crossing branch is unnecessary for ordinary nonperiodic orbits.",
        "P223": "On such a tail, #{j:a_j<=A}=O(2^(rho*A)), sum 2^(-a_j) converges, a_j tends to infinity, and every c<1/rho* holds on density one.",
        "P224": "At renewal boundaries, h_i=O(S_i^rho) and (h_i-1)/(S_i+1) tends to zero for rho*<rho<1.",
        "P225": "Renewal transitions satisfy limsup S_(i+1)/S_i<=3/2 and S_i=O_epsilon((3/2+epsilon)^i).",
        "P226": "For every rho in (rho*,1), noncritical primitive positive cycles have an effective finite minimum cutoff M_rho.",
        "scope_repairs": ["Every reciprocal, z-limit, and cycle-cutoff use fixes rho*<rho<1.", "P74/P75 and EXT07 remain historical valid entries; P222/P223 remove their necessity for the stated ordinary-orbit consequences."],
        "what_this_result_does_not_prove": "It gives no pointwise last-small-defect bound, P80 multiplicity estimate, irreducible-tree extinction, permanent-safe source exclusion, arbitrary-area cycle exclusion, or Collatz proof.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 37 boundary report

The location-uniform recursion survives exact audit.  Its key operation is
legitimate because, at fixed odd count, every `T^N` image has the same slope
and all affine corrections occupy a translation-independent interval.  The
image of each low-count slice is itself equal-time collision-free.

The rational specialization closes with the fully explicit bound
`G(X)<32 X^(29/30)`.  The exact low-part threshold is `N0=135`; it fails at
`N=134`, so the finite base is not silently omitted.  The general limiting
exponent follows by the same strong-induction argument, not by extrapolating
the finite audit.

One quantifier from the supplied note needs to be made explicit: reciprocal
summability, `z_i -> 0`, and the cycle cutoff choose
`rho_* < rho < 1`.  This is possible because `rho_*<29/30<1` and does not
invalidate the candidate conclusions.

## Live obstruction

Uniform sparsity counts points on one equal-time collision-free set.  P80
requires control of multiplicity across many canonical renewal addresses.
Neither this theorem nor its improved density-one defect exponent supplies a
last-occurrence bound, a positive-source lift obstruction, or extinction of
the P81/P86 irreducible tree.  NG22 therefore remains valid.

The cycle consequence gives only an effective finite range for noncritical
minimum values.  It neither computes a practical optimized cutoff nor
excludes critical or arbitrary-area cycles.

## What this result does not prove

It does not prove H72, H133, or the Collatz conjecture.  Both the nontrivial
positive-cycle branch and the permanent-safe nonperiodic branch remain open.
`proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    induction = induction_certificate()
    affine = affine_interval_audit()
    renewal = renewal_audit()
    regressions = regression_audit()
    write_json(args.artifact_dir / "phase37_theory.json", theory_artifact())
    write_json(args.artifact_dir / "phase37_induction_certificate.json", induction)
    write_json(args.artifact_dir / "phase37_affine_interval_audit.json", affine)
    write_json(args.artifact_dir / "phase37_renewal_audit.json", renewal)
    write_json(args.artifact_dir / "phase37_regressions.json", regressions)
    (args.artifact_dir / "phase37_obstruction_report.md").write_text(
        obstruction_report(), encoding="utf-8"
    )
    print(json.dumps({
        "valid": True,
        "claims": CLAIMS,
        "explicit_constant": EXPLICIT_CONSTANT,
        "induction_N0": INDUCTION_N0,
        "affine_counts": affine["counts"],
        "renewal_counts": renewal["counts"],
        "proves_collatz": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
