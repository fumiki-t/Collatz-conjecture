#!/usr/bin/env python3
"""Generate exact Phase 32 triple-hit and full-cofactor evidence.

The supplied Phase 32 note is an untrusted proposal.  All acceptance
decisions use arbitrary-precision integers or exact rational intervals.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Sequence

try:
    from phase26_search import (
        A_BITS,
        B_BITS,
        NEGATIVE_Q7,
        affine_correction,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
        reduced_profile,
    )
    from phase28_search import decimal_cuberoot_box
    from phase31_search import cyclic_window, static_inventory
except ModuleNotFoundError:
    from src.phase26_search import (
        A_BITS,
        B_BITS,
        NEGATIVE_Q7,
        affine_correction,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
        reduced_profile,
    )
    from src.phase28_search import decimal_cuberoot_box
    from src.phase31_search import cyclic_window, static_inventory


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 9
EXPECTED_CLAIMS = {
    "P195": "VERIFIED_THEOREM",
    "P196": "VERIFIED_THEOREM",
    "P197": "VERIFIED_THEOREM",
    "P198": "VERIFIED_THEOREM",
    "P199": "VERIFIED_THEOREM",
    "H200": "OPEN",
    "E45": "VERIFIED_FINITE",
    "H172": "OPEN",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def update_hash(digest: object, value: object) -> None:
    digest.update(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def boundaries(exponents: Sequence[int]) -> tuple[int, ...]:
    answer = [0]
    for exponent in exponents:
        answer.append(answer[-1] + exponent)
    return tuple(answer)


def affected_starts(length: int, left: int, right: int, width: int) -> set[int]:
    return {
        (position - offset) % length
        for position in (left, right)
        for offset in range(width)
    }


def triple_hit_audit(exponents: Sequence[int]) -> dict[str, object]:
    """Audit P195 at every cyclic width for one discrepancy-minimum word."""
    item = static_inventory(exponents)
    length = int(item["L"])
    q = int(item["q"])
    zeros = length - q
    area = int(item["area"])
    J = int(item["J"])
    E = int(item["E"])
    K = int(item["K"])
    base_word = str(item["base_word"])
    residual_word = str(item["residual_word"])
    actual_word = str(item["actual_word"])
    anchors = tuple(item["anchors"])
    rows: list[list[int]] = []
    distinct_count = 0
    for width in range(1, length + 1):
        exceptional = {
            start
            for start in range(length)
            if cyclic_window(residual_word, start, width + 2)
            != cyclic_window(base_word, start, width + 2)
        }
        if len(exceptional) > min(length, 2 * area + E * (width + 1)):
            raise AssertionError("triple-hit exceptional bound")
        incidence = [0] * length
        for left, right in anchors:
            affected = affected_starts(length, left, right, width)
            if len(affected) > min(length, width + 1):
                raise AssertionError("singleton influence")
            for start in affected:
                incidence[start] += 1
        if sum(incidence) > K * (width + 1):
            raise AssertionError("incidence total")
        z_n = (zeros * (width + 1) + length - 1) // length
        capacities = (
            width + 3,
            (width + 3) * z_n,
            (width + 3) * z_n * (z_n - 1) // 2,
        )
        type_counts = []
        start_counts = []
        for hits in range(3):
            starts = [
                start for start in range(length)
                if start not in exceptional and incidence[start] == hits
            ]
            types = {cyclic_window(actual_word, start, width) for start in starts}
            if len(types) > capacities[hits]:
                raise AssertionError("triple-hit capacity")
            type_counts.append(len(types))
            start_counts.append(len(starts))
        factor_count = len(cyclic_factors(actual_word, width))
        distinct = factor_count == length
        rhs = (
            (J + 2 * E) * (width + 1)
            + 6 * area
            + (width + 3) * (3 + 2 * z_n + z_n * (z_n - 1) // 2)
        )
        if distinct and 3 * length > rhs:
            raise AssertionError("finite triple-hit inequality")
        distinct_count += int(distinct)
        rows.append([
            width, z_n, len(exceptional), *start_counts, *type_counts,
            *capacities, factor_count, int(distinct), sum(incidence), rhs,
        ])
    return {
        "q": q,
        "L": length,
        "area": area,
        "J": J,
        "E": E,
        "K": K,
        "widths": length,
        "distinct_widths": distinct_count,
        "rows": rows,
    }


def mechanical_boundaries(q: int, length: int) -> tuple[int, ...]:
    return tuple((length * index + q - 1) // q for index in range(q + 1))


def extended_mechanical_boundary(q: int, length: int, time: int) -> int:
    return -((-length * time) // q)


def support_arc_certificate(q: int, length: int, profile: Sequence[int], modulus: int) -> dict[str, object] | None:
    support = [index for index, value in enumerate(profile[:-1]) if value]
    if not support:
        return None
    gaps = [
        support[(index + 1) % len(support)]
        + (q if index + 1 == len(support) else 0)
        - value
        for index, value in enumerate(support)
    ]
    cut = gaps.index(max(gaps))
    start = support[(cut + 1) % len(support)]
    lifts = [value if value >= start else value + q for value in support]
    end = max(lifts)
    e_values = [extended_mechanical_boundary(q, length, time) for time in lifts]
    e_min = min(e_values)
    terms = [
        (2 ** profile[time % q] - 1)
        * 2 ** (extended_mechanical_boundary(q, length, time) - e_min)
        * 3 ** (end - time)
        for time in lifts
    ]
    value = sum(terms)
    width = end - start
    # Exact integer form of value < 2^(A+1+(L/q)W): raise to q.
    area = sum(profile[:-1])
    if value**q >= 2 ** (q * (area + 1) + length * width):
        raise AssertionError("positive support-arc size bound")
    if value % modulus:
        raise AssertionError("positive support-arc divisibility")
    return {
        "support": len(support),
        "area": area,
        "largest_gap": max(gaps),
        "width": width,
        "value_bits": value.bit_length(),
        "value_digest_sha256": stable_hash(str(value)),
        "divisible": True,
        "strict_power_bound": True,
    }


def cofactor_audit(exponents: Sequence[int]) -> dict[str, object]:
    exponents = tuple(exponents)
    data = reduced_profile(exponents)
    q = int(data["q"])
    length = int(data["L"])
    divisor = int(data["d"])
    q0 = int(data["q0"])
    length0 = int(data["L0"])
    profile = tuple(int(value) for value in data["profile"])
    baseline = tuple(int(value) for value in data["baseline"])
    base_block = baseline[:q0]
    base_edges = boundaries(base_block)
    R = 2**length0
    S = 3**q0
    M = sum(R**c * S ** (divisor - 1 - c) for c in range(divisor))
    C = []
    for block in range(divisor):
        C.append(sum(
            3 ** (q0 - 1 - time)
            * 2 ** (base_edges[time] + profile[block * q0 + time])
            for time in range(q0)
        ))
    correction = affine_correction(exponents)
    rebuilt = sum(
        R**block * S ** (divisor - 1 - block) * C[block]
        for block in range(divisor)
    )
    if rebuilt != correction:
        raise AssertionError("block correction decomposition")
    base_correction = affine_correction(base_block)
    delta = correction - base_correction * M
    base_full_edges = mechanical_boundaries(q, length)
    direct_delta = sum(
        (2 ** profile[index] - 1)
        * 2 ** base_full_edges[index]
        * 3 ** (q - 1 - index)
        for index in range(q)
    )
    if delta != direct_delta:
        raise AssertionError("full cofactor delta")
    denominator = 2**length - 3**q
    integral_positive = denominator > 0 and correction % denominator == 0
    cofactor_hit = delta % M == 0
    if integral_positive and not cofactor_hit:
        raise AssertionError("full cofactor necessity")
    oscillation = None
    arc = None
    if integral_positive:
        source = correction // denominator
        k = (R - S) * source
        if sum((value - k) * R**c * S ** (divisor - 1 - c) for c, value in enumerate(C)):
            raise AssertionError("block polynomial root")
        if primitive(exponents) and divisor > 1:
            if max(C) - min(C) < R:
                raise AssertionError("primitive block oscillation")
            oscillation = max(C) - min(C)
    # M|Delta is the exact premise needed by the positive arc construction;
    # full integrality is a sufficient but not necessary finite test source.
    if cofactor_hit and any(profile[:-1]):
        arc = support_arc_certificate(q, length, profile, M)
    return {
        "q": q,
        "L": length,
        "d": divisor,
        "q0": q0,
        "L0": length0,
        "area": sum(profile[:-1]),
        "support": sum(value > 0 for value in profile[:-1]),
        "primitive": primitive(exponents),
        "cofactor_bits": M.bit_length(),
        "cofactor_hit": cofactor_hit,
        "integral_positive": integral_positive,
        "oscillation": oscillation,
        "arc": arc,
        "row_digest_sha256": stable_hash([list(exponents), C, str(delta), str(M)]),
    }


def corpus_audit() -> tuple[dict[str, object], dict[str, object]]:
    triple_counts = {
        "cyclic_classes": 0,
        "minimum_rotations": 0,
        "widths": 0,
        "distinct_factor_widths": 0,
        "capacity_checks": 0,
    }
    cofactor_counts = {
        "decompositions": 0,
        "noncoprime_decompositions": 0,
        "cofactor_hits": 0,
        "positive_integral_cycles": 0,
        "primitive_noncoprime_integral_cycles": 0,
        "positive_arc_certificates": 0,
    }
    triple_digest = hashlib.sha256()
    cofactor_digest = hashlib.sha256()
    triple_samples: list[object] = []
    cofactor_samples: list[object] = []
    for q in range(1, Q_MAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            for representative in sorted({cyclic_class(row) for row in compositions(length, q)}):
                triple_counts["cyclic_classes"] += 1
                for rotated in minimum_rotations(representative):
                    triple = triple_hit_audit(rotated)
                    cofactor = cofactor_audit(rotated)
                    triple_counts["minimum_rotations"] += 1
                    triple_counts["widths"] += int(triple["widths"])
                    triple_counts["distinct_factor_widths"] += int(triple["distinct_widths"])
                    triple_counts["capacity_checks"] += 3 * int(triple["widths"])
                    cofactor_counts["decompositions"] += 1
                    cofactor_counts["noncoprime_decompositions"] += int(cofactor["d"] > 1)
                    cofactor_counts["cofactor_hits"] += int(cofactor["cofactor_hit"])
                    cofactor_counts["positive_integral_cycles"] += int(cofactor["integral_positive"])
                    cofactor_counts["primitive_noncoprime_integral_cycles"] += int(
                        cofactor["integral_positive"] and cofactor["primitive"] and cofactor["d"] > 1
                    )
                    cofactor_counts["positive_arc_certificates"] += int(cofactor["arc"] is not None)
                    update_hash(triple_digest, [list(rotated), triple["rows"]])
                    update_hash(cofactor_digest, [list(rotated), cofactor])
                    if triple["K"] and len(triple_samples) < 10:
                        triple_samples.append({key: triple[key] for key in ("q", "L", "area", "J", "E", "K")})
                    if cofactor["d"] > 1 and len(cofactor_samples) < 10:
                        cofactor_samples.append(cofactor)
    return (
        {
            "format": "collatz-phase32-triple-hit-corpus-v1",
            "maximum_q": Q_MAX,
            "counts": triple_counts,
            "row_digest_sha256": triple_digest.hexdigest(),
            "samples": triple_samples,
            "scope": "Complete positive-D cyclic exponent corpus through q<=9, every discrepancy-minimum rotation, and every cyclic width.",
            "proves_collatz": False,
        },
        {
            "format": "collatz-phase32-full-cofactor-corpus-v1",
            "maximum_q": Q_MAX,
            "counts": cofactor_counts,
            "row_digest_sha256": cofactor_digest.hexdigest(),
            "samples": cofactor_samples,
            "scope": "The same finite rational-profile corpus; integral-cycle premises are checked explicitly and rational shadows are not promoted.",
            "proves_collatz": False,
        },
    )


def c3_cube(slope: Fraction) -> Fraction:
    if not 1 < slope <= 2:
        raise ValueError("slope")
    eta = (slope - 1) / slope
    return Fraction(675, 64) * slope * slope * (Fraction(2, 1) / (slope - 1) - eta * eta)


def scalar_audit() -> dict[str, object]:
    ln2 = log_interval(Fraction(2), terms=128)
    ln3 = log_interval(Fraction(3), terms=128)
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    critical_cube = (c3_cube(alpha[1]), c3_cube(alpha[0]))
    critical_box = decimal_cuberoot_box(*critical_cube)
    noncritical = Fraction(4725, 64)
    noncritical_box = decimal_cuberoot_box(noncritical, noncritical)
    if critical_box != [["4430667", "1000000"], ["1107667", "250000"]]:
        raise AssertionError(f"critical C3 box: {critical_box}")
    if noncritical_box != [["4195083", "1000000"], ["1048771", "250000"]]:
        raise AssertionError(f"noncritical C3 box: {noncritical_box}")
    rows = []
    for slope in (Fraction(8, 5), Fraction(5, 3), Fraction(7, 4), Fraction(19, 10), Fraction(2)):
        eta = (slope - 1) / slope
        denominator = Fraction(2, 1) / (slope - 1) - eta * eta
        y_cube = 5 * slope / denominator
        z_positive = 4 * slope > 7 * eta * eta * (slope - 1) * slope
        if not z_positive:
            raise AssertionError("interior optimizer")
        rows.append([encode_fraction(slope), encode_fraction(y_cube), encode_fraction(c3_cube(slope))])
    return {
        "format": "collatz-phase32-scalar-certificates-v1",
        "log2_three_interval": [encode_fraction(value) for value in alpha],
        "critical_constant_cube_interval": [encode_fraction(value) for value in critical_cube],
        "critical_constant_decimal_box": critical_box,
        "noncritical_constant_cube": encode_fraction(noncritical),
        "noncritical_constant_decimal_box": noncritical_box,
        "optimizer": "x=2ell/y, z=(ell-eta^2*y^3/2)/(2y), y^3=5ell/(2/(ell-1)-eta^2)",
        "optimizer_scope": "1<ell<=2; z>0 and c3_cube is decreasing on this interval",
        "rows": rows,
        "proves_collatz": False,
    }


def bit_exponents(bits: str) -> tuple[int, ...]:
    positions = [index for index, bit in enumerate(bits) if bit == "1"]
    return tuple(
        (positions[(index + 1) % len(positions)] - value) % len(bits) or len(bits)
        for index, value in enumerate(positions)
    )


def regression_audit() -> dict[str, object]:
    families = [
        ("2^m-1", "1" * 12 + "0"),
        ("8^m-5", "111001" * 4),
        ("(110|111)^*", "110111" * 8),
        ("A=11101", A_BITS),
        ("B=1100", B_BITS),
        ("A^1B^1", A_BITS + B_BITS),
        ("A^2B^3", A_BITS * 2 + B_BITS * 3),
    ]
    rows = []
    for name, bits in families:
        exponents = bit_exponents(bits)
        positive_d = 2 ** sum(exponents) > 3 ** len(exponents)
        row = None
        if positive_d:
            rotated = minimum_rotations(exponents)[0]
            triple = triple_hit_audit(rotated)
            cofactor = cofactor_audit(rotated)
            row = {
                "exponents": list(rotated),
                "triple_distinct_widths": triple["distinct_widths"],
                "d": cofactor["d"],
                "cofactor_hit": cofactor["cofactor_hit"],
                "integral_positive": cofactor["integral_positive"],
            }
        rows.append([name, bits, positive_d, row])
    return {
        "format": "collatz-phase32-regressions-v1",
        "mandatory_families": rows,
        "named_controls": {
            "trivial_cycle": [2],
            "trivial_power": [2, 2, 2],
            "negative_q2": [1, 2],
            "negative_q7": list(NEGATIVE_Q7),
            "NG34_NG40": "preserved; Phase 32 does not identify reduced-modulus, coefficient reversal, rational rotation, or grid proxies with an integral full-cofactor contradiction",
        },
        "rational_shadow_boundary": "M_d divisibility and the positive weighted-average step are checked separately; nonintegral rational shadows are negative controls.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase32-theory-v1",
        "claims": EXPECTED_CLAIMS,
        "P195": {
            "statement": "For every valid P185 extraction and cyclic width n with distinct factors, 3L<=(J+2E)(n+1)+6A+(n+3)(3+2Z_n+binom(Z_n,2)), where Z_n=ceil((L-q)(n+1)/L).",
            "proof_kernel": "mechanical balance bounds candidate zero anchors; starts with 0,1,2 hits have the stated capacities; total singleton incidence is at most K(n+1)",
        },
        "P196": {
            "statement": "In the P193 cycle regime, P195 and P167 imply liminf A/q^(2/3)>=C3(ell), with the exact formula recorded in the audit.",
            "critical_dependency": "Only the critical specialization uses EXT17.",
        },
        "P197": {
            "statement": "The exact reduced-block decomposition B=sum R^c S^(d-1-c) C_c holds and every integral cycle satisfies M_d|Delta.",
        },
        "P198": {
            "statement": "A primitive positive integral noncoprime cycle has max(C_c)-min(C_c)>=R; equality of all block corrections would repeat the exponent block.",
        },
        "P199": {
            "statement": "A largest-support-gap cut gives a positive M_d-divisible time-arc integer below 2^(A+1+(L/q)W), hence (L/q)ceil(q/s)<L0+A+1 and critical area six has d<=s<=6.",
        },
        "H200": {
            "statement": "Classify bounded-grid coefficient identities sufficiently to make the proposed d=s=6 eventual exclusion effective and independently auditable.",
            "status_reason": "The supplied compactness argument does not provide an explicit cutoff or a completed finite offset-polynomial classification.",
        },
        "what_this_result_does_not_prove": "No area-six class, arbitrary-area cycle family, nonperiodic branch, or Collatz conjecture is excluded.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 32 obstruction report

The triple-hit inequality, its optimized area constant, the full-cofactor
decomposition, primitive block oscillation, and positive support-arc divisor
survive exact audit in their stated scopes.

The supplied `d=s=6` argument is not accepted as a theorem.  It proves a
bounded-offset compactness reduction, but the note does not enumerate the
finite offset-polynomial set, bound the first exceptional reduced pair, or
classify every possible fixed coefficient identity.  Calling the conclusion
"effective in principle" is not an independently checkable cutoff.  This
remaining obligation is recorded as H200 OPEN.  The exact largest-gap
certificate behind P199 is retained, so future work starts from a bounded
six-column grid rather than re-deriving the coarse gcd bound.

## What this result does not prove

It does not exclude the `d=s=6` class, any other area-six class, arbitrary-area
positive cycles, either nonperiodic branch, or the Collatz conjecture.
`proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    triple, cofactor = corpus_audit()
    write_json(args.artifact_dir / "phase32_theory.json", theory_artifact())
    write_json(args.artifact_dir / "phase32_triple_hit_corpus.json", triple)
    write_json(args.artifact_dir / "phase32_cofactor_corpus.json", cofactor)
    write_json(args.artifact_dir / "phase32_scalar_certificates.json", scalar_audit())
    write_json(args.artifact_dir / "phase32_regressions.json", regression_audit())
    (args.artifact_dir / "phase32_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")
    print(json.dumps({
        "valid": True,
        "claims": EXPECTED_CLAIMS,
        "triple_counts": triple["counts"],
        "cofactor_counts": cofactor["counts"],
        "proves_collatz": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
