#!/usr/bin/env python3
"""Generate exact Phase 30 direct-transport evidence.

The supplied note is treated as an untrusted proposal.  Acceptance decisions
use integers and Fractions; floating point is not used.
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
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
    )
    from phase28_search import (
        decimal_cuberoot_box,
        isolated_profile,
        level_intervals,
        mechanical_baseline,
        near_extremal_profile,
        plateau_profile,
        profile_to_exponents,
        seven_grid_time_profile,
        tall_profile,
        transport_constant_cube,
        transport_data,
    )
except ModuleNotFoundError:
    from src.phase26_search import (
        A_BITS,
        B_BITS,
        NEGATIVE_Q7,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
    )
    from src.phase28_search import (
        decimal_cuberoot_box,
        isolated_profile,
        level_intervals,
        mechanical_baseline,
        near_extremal_profile,
        plateau_profile,
        profile_to_exponents,
        seven_grid_time_profile,
        tall_profile,
        transport_constant_cube,
        transport_data,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 8
EXPECTED_CLAIMS = {
    "P179": "VERIFIED_THEOREM",
    "P180": "VERIFIED_THEOREM",
    "P181": "VERIFIED_THEOREM",
    "P182": "VERIFIED_THEOREM",
    "P183": "VERIFIED_THEOREM",
    "P184": "VERIFIED_THEOREM",
    "E42": "VERIFIED_FINITE",
    "NG39": "REFUTED",
    "H172": "OPEN",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def boundaries(exponents: Sequence[int]) -> tuple[int, ...]:
    result = [0]
    for value in exponents:
        result.append(result[-1] + value)
    return tuple(result)


def transport_span(base: Sequence[int], profile: Sequence[int]) -> tuple[int, int]:
    base_boundaries = boundaries(base)
    span = sum(
        base_boundaries[end] - base_boundaries[start]
        for intervals in level_intervals(profile)
        for start, end in intervals
    )
    area = sum(profile[:-1])
    components = sum(len(intervals) for intervals in level_intervals(profile))
    q, length = len(base), sum(base)
    if span > 2 * area or q * span > length * area + q * components:
        raise AssertionError("mechanical transport span")
    return span, components


def rotation_script(base: Sequence[int], profile: Sequence[int]) -> tuple[str, list[dict[str, object]]]:
    q = len(base)
    base_boundaries = boundaries(base)
    current = expanded_word(base)
    operations: list[dict[str, object]] = []
    for level, intervals in enumerate(level_intervals(profile), start=1):
        for start_label, end_label in intervals:
            start = base_boundaries[start_label] + level - 1
            end = base_boundaries[end_label] + level - 1
            segment = current[start:end]
            if not segment or segment[0] != "1" or segment[-1] != "0":
                raise AssertionError("transport segment endpoints")
            before = current
            current = current[:start] + segment[-1] + segment[:-1] + current[end:]
            operations.append(
                {
                    "level": level,
                    "labels": [start_label, end_label],
                    "positions": [start, end],
                    "span": end - start,
                    "before": before,
                    "after": current,
                }
            )
        truncated = tuple(min(value, level) for value in profile)
        expected = expanded_word(profile_to_exponents(base, truncated))
        if current != expected:
            raise AssertionError("level-by-level rotation reconstruction")
    return current, operations


def direct_transport_audit(exponents: Sequence[int], widths: Sequence[int] | None = None) -> dict[str, object]:
    item = transport_data(exponents, check_intervals=False)
    base = tuple(item["baseline"])
    profile = tuple(item["profile"])
    base_word = expanded_word(base)
    actual_word = expanded_word(exponents)
    length = len(actual_word)
    final, operations = rotation_script(base, profile)
    if final != actual_word:
        raise AssertionError("transport final word")
    span, components = transport_span(base, profile)
    if components != item["J"] or span != sum(int(row["span"]) for row in operations):
        raise AssertionError("transport inventory")
    peak = profile[:-1].index(int(item["height"])) if item["height"] else 0
    spine = []
    all_intervals = []
    for intervals in level_intervals(profile):
        all_intervals.extend(intervals)
        if item["height"]:
            candidates = [interval for interval in intervals if interval[0] <= peak < interval[1]]
            if len(candidates) != 1:
                raise AssertionError("nested spine")
            spine.append(candidates[0])
    spine_excess = sum(end - start - 1 for start, end in spine)
    total_excess = int(item["area"]) - int(item["J"])
    nonspine_excess = total_excess - spine_excess
    nonspine_nonsingleton = sum(
        interval not in spine and interval[1] - interval[0] > 1
        for interval in all_intervals
    )
    if spine_excess < int(item["descent_floor"]) or nonspine_excess > int(item["descent_slack"]) or nonspine_nonsingleton > nonspine_excess:
        raise AssertionError("secondary-peak charging")
    selected = tuple(range(1, length + 1)) if widths is None else tuple(sorted(set(widths)))
    rows = []
    equality_widths = []
    affected_checks = 0
    for width in selected:
        if not 1 <= width <= length:
            raise ValueError("factor width")
        base_factors = cyclic_factors(base_word, width)
        actual_factors = cyclic_factors(actual_word, width)
        direct_bound = len(base_factors) + span + components * (width - 1)
        area_bound = (components + 1) * width + 2 * int(item["area"]) + 1
        if len(base_factors) > width + 1 or len(actual_factors) > direct_bound or direct_bound > area_bound:
            raise AssertionError("direct transport factor bound")
        new_total = 0
        for operation in operations:
            before = cyclic_factors(str(operation["before"]), width)
            after = cyclic_factors(str(operation["after"]), width)
            new_count = len(after - before)
            if new_count > min(length, int(operation["span"]) + width - 1):
                raise AssertionError("affected-start bound")
            new_total += new_count
            affected_checks += 1
        if len(actual_factors) > len(base_factors) + new_total:
            raise AssertionError("factor-set telescoping")
        if len(actual_factors) == direct_bound:
            equality_widths.append(width)
        rows.append([width, len(base_factors), len(actual_factors), direct_bound, area_bound, new_total])
    return {
        "q": int(item["q"]),
        "L": int(item["L"]),
        "area": int(item["area"]),
        "height": int(item["height"]),
        "J": int(item["J"]),
        "transport_span": span,
        "descent_floor": int(item["descent_floor"]),
        "descent_slack": int(item["descent_slack"]),
        "spine_excess": spine_excess,
        "nonspine_excess": nonspine_excess,
        "nonspine_nonsingleton": nonspine_nonsingleton,
        "component_rotation_checks": len(operations),
        "affected_start_checks": affected_checks,
        "equality_widths": equality_widths,
        "factor_rows": rows,
    }


def corpus_audit() -> dict[str, object]:
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "factor_width_checks": 0,
        "component_rotation_checks": 0,
        "affected_start_checks": 0,
        "span_checks": 0,
        "spine_charging_checks": 0,
    }
    digest_rows = []
    equality_samples = []
    for q in range(1, Q_MAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                counts["noncoprime_classes"] += int(math.gcd(q, length) > 1)
                for rotated in minimum_rotations(values):
                    audit = direct_transport_audit(rotated)
                    counts["minimum_rotations"] += 1
                    counts["factor_width_checks"] += len(audit["factor_rows"])
                    counts["component_rotation_checks"] += audit["component_rotation_checks"]
                    counts["affected_start_checks"] += audit["affected_start_checks"]
                    counts["span_checks"] += 2
                    counts["spine_charging_checks"] += 3
                    row = [list(rotated), audit]
                    digest_rows.append(row)
                    if audit["equality_widths"] and len(equality_samples) < 8:
                        equality_samples.append(row)
    if counts["cyclic_classes"] != 2214 or counts["minimum_rotations"] != 3101 or counts["factor_width_checks"] != 45369:
        raise AssertionError("Phase 30 corpus regression")
    return {
        "format": "collatz-phase30-direct-transport-corpus-v1",
        "maximum_q": Q_MAX,
        "counts": counts,
        "row_digest_sha256": stable_hash(digest_rows),
        "equality_samples": equality_samples,
        "scope": "Complete positive-D cyclic exponent corpus through q<=8 and every cyclic width; rational structural controls are not asserted to be integer cycles.",
        "proves_collatz": False,
    }


def move_constant_cube(slope: Fraction) -> Fraction:
    if not 1 < slope <= 2:
        raise ValueError("slope")
    return Fraction(27, 8) * slope * slope / (slope - 1)


def scalar_audit() -> dict[str, object]:
    ln2 = log_interval(Fraction(2), terms=96)
    ln3 = log_interval(Fraction(3), terms=96)
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    critical_cube = (move_constant_cube(alpha[1]), move_constant_cube(alpha[0]))
    phase28_cube = (transport_constant_cube(alpha[1]), transport_constant_cube(alpha[0]))
    if critical_cube[0] != 4 * phase28_cube[0] or critical_cube[1] != 4 * phase28_cube[1]:
        raise AssertionError("Phase 28 improvement factor")
    noncritical_cube = Fraction(27, 2)
    critical_decimal = decimal_cuberoot_box(*critical_cube)
    noncritical_decimal = decimal_cuberoot_box(noncritical_cube, noncritical_cube)
    if not Fraction(*map(int, critical_decimal[0])) == Fraction(2_438_154, 1_000_000) < Fraction(*map(int, critical_decimal[1])) == Fraction(2_438_155, 1_000_000):
        raise AssertionError("critical display box")
    slope_rows = []
    for slope in (Fraction(8, 5), Fraction(5, 3), Fraction(7, 4), Fraction(19, 10), Fraction(2)):
        cube = move_constant_cube(slope)
        slope_rows.append([encode_fraction(slope), encode_fraction(cube), cube >= noncritical_cube])
    height_cube = (alpha[0] * (alpha[0] - 1), alpha[1] * (alpha[1] - 1))
    transport_cube = (alpha[0] ** 2 / (alpha[1] - 1), alpha[1] ** 2 / (alpha[0] - 1))
    return {
        "format": "collatz-phase30-scalar-certificates-v1",
        "log_terms": 96,
        "log2_three_interval": [encode_fraction(value) for value in alpha],
        "critical_constant_cube_interval": [encode_fraction(value) for value in critical_cube],
        "critical_constant_decimal_box": critical_decimal,
        "noncritical_constant_cube": encode_fraction(noncritical_cube),
        "noncritical_constant_decimal_box": noncritical_decimal,
        "phase28_constant_cube_interval": [encode_fraction(value) for value in phase28_cube],
        "exact_improvement": "C_move(ell)^3=4*C_phase28(ell)^3, hence C_move=2^(2/3)*C_phase28",
        "near_extremal": {
            "height_scale_cube_interval": [encode_fraction(value) for value in height_cube],
            "transport_scale_cube_interval": [encode_fraction(value) for value in transport_cube],
            "area_over_transport": encode_fraction(Fraction(3, 2)),
            "proved_saturation": "direct factor count and the chosen n_cyc proxy at leading normalized order",
            "not_proved": "No ratio-one saturation of the actual maximum orbit state in P157 follows.",
        },
        "slope_rows": slope_rows,
        "proves_collatz": False,
    }


def synthetic_audit() -> dict[str, object]:
    q7, L7, p7 = seven_grid_time_profile()
    profiles = [
        ("tall", 125, 199, tall_profile(125, 199, 5)),
        ("plateau", 125, 199, plateau_profile(125, 199, 5)),
        ("isolated", 125, 199, isolated_profile(125, 199, 20)),
        ("near-extremal", 1331, 2110, near_extremal_profile(1331, 2110, 9, 124)),
        ("seven-grid", q7, L7, p7),
    ]
    rows = []
    widths = (1, 2, 3, 4, 5, 8, 13, 21, 34, 55)
    for name, q, length, profile in profiles:
        exponents = profile_to_exponents(mechanical_baseline(q, length), profile)
        canonical = transport_data(exponents, check_intervals=False)
        audit = direct_transport_audit(exponents, tuple(width for width in widths if width <= length))
        rows.append([name, q, length, sum(profile[:-1]), max(profile[:-1]), canonical["J"], audit])
    return {
        "format": "collatz-phase30-synthetic-profiles-v1",
        "rows": rows,
        "row_digest_sha256": stable_hash(rows),
        "scope": "Five exact legal Phase 28 profiles at ten declared widths, independently re-audited under the direct bound.",
        "proves_collatz": False,
    }


def bit_exponents(bits: str) -> tuple[int, ...]:
    positions = [index for index, bit in enumerate(bits) if bit == "1"]
    return tuple((positions[(i + 1) % len(positions)] - value) % len(bits) or len(bits) for i, value in enumerate(positions))


def regression_audit() -> dict[str, object]:
    witness = (2, 2, 1, 3, 1, 1)
    witness_audit = direct_transport_audit(witness)
    width_four = next(row for row in witness_audit["factor_rows"] if row[0] == 4)
    if width_four[:5] != [4, 5, 10, 10, 11] or witness_audit["transport_span"] != 2:
        raise AssertionError("no-span witness")
    families = [
        ("2^m-1", "1" * 12 + "0"),
        ("8^m-5", "111001" * 4),
        ("(110|111)^*", "110111" * 8),
        ("A=11101", A_BITS),
        ("B=1100", B_BITS),
        ("A^1B^1", A_BITS + B_BITS),
        ("A^2B^3", A_BITS * 2 + B_BITS * 3),
    ]
    family_rows = []
    for name, bits in families:
        exponents = bit_exponents(bits)
        family_rows.append([name, bits, list(exponents), 2 ** sum(exponents) > 3 ** len(exponents), math.gcd(len(exponents), sum(exponents))])
    trivial_rows = []
    for power in range(1, 9):
        values = (2,) * power
        audit = direct_transport_audit(values)
        trivial_rows.append([power, audit["area"], audit["J"], audit["transport_span"]])
    return {
        "format": "collatz-phase30-regressions-v1",
        "no_span_counterexample": {
            "exponents": list(witness),
            "baseline": [2, 2, 1, 2, 2, 1],
            "profile": [0, 0, 0, 0, 1, 0, 0],
            "width_four": width_four,
            "overstrong_bound": 9,
            "actual": 10,
        },
        "mandatory_families": family_rows,
        "named_controls": {
            "negative_q2": [1, 2],
            "negative_q7": list(NEGATIVE_Q7),
            "trivial_powers": trivial_rows,
            "NG34_NG38": "preserved by Phase 29 regressions and named in the acceptance contract",
        },
        "proposal_repair": "Literal saturation of P157's actual maximum-state upper bound is not derived; only factor-count and n_cyc-proxy leading saturation are accepted.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    statements = {
        "P179": "Direct level rotations give p_cyc(n)<=p_base(n)+T_span+J(n-1), T_span<=min(2A,(L/q)A+J), hence p_cyc(n)<=(J+1)n+2A+1.",
        "P180": "Every primitive positive nontrivial cycle obeys the sharpened direct-transport state-separation inequality with strict ceiling handling.",
        "P181": "Under a fixed inverse-polynomial multiplier gap and slope limit ell, liminf A/q^(2/3)>=3 ell^(2/3)/(2(ell-1)^(1/3)).",
        "P182": "The noncritical constant is at least (3/2)2^(2/3); the critical constant is the stated log2(3) specialization using EXT17.",
        "P183": "Equality forces the unique J,h,A scales, vanishing normalized descent slack, and leading saturation of the direct factor and n_cyc-proxy bounds, but not actual maximum-state saturation.",
        "P184": "At equality all but o(J) level components are singleton intervals; secondary peaks are charged through total excess outside one nested descent spine.",
        "E42": "The complete q<=8 corpus, synthetic profiles, scalars, counterexample, and regressions are independently reproducible.",
        "NG39": "The span-free strengthening p_cyc(n)<=p_base(n)+Jn is false at q=6,L=10,n=4.",
        "H172": "A pair-location-aware strict subleading resonance/resultant gap remains open.",
        "H133": "Arbitrary-area positive cycles remain open.",
    }
    return {
        "format": "collatz-phase30-direct-transport-theory-v1",
        "claims": {key: {"status": EXPECTED_CLAIMS[key], "statement": value} for key, value in statements.items()},
        "dependencies": {
            "P179": ["P156", "P166", "P167"],
            "P180": ["P125", "P133", "P157", "P179"],
            "P181": ["P167", "P180"],
            "P182": ["P163", "P164", "P181", "EXT17"],
            "P183": ["P167", "P180", "P181"],
            "P184": ["P167", "P183"],
        },
        "external_boundary": "Only P182's critical specialization inherits EXT17; the direct factor theorem and noncritical constant are internal.",
        "proposal_repair": "The note's literal actual-state saturation sentence is not accepted because the inequality chain controls n_cyc, not the ratio of the actual maximum state to P157's upper bound.",
        "proves_collatz": False,
        "what_this_result_does_not_prove": "No pair-aware resonance exclusion, arbitrary-area cycle exclusion, nonperiodic exclusion, or Collatz proof follows.",
    }


def obstruction_report(corpus: dict[str, object]) -> str:
    counts = corpus["counts"]
    return f"""# Phase 30 obstruction report

The direct token-transport theorem passed {counts['factor_width_checks']:,} exact factor-width checks over {counts['minimum_rotations']:,} discrepancy-minimum rotations.  The span-free strengthening fails at `(q,L,n)=(6,10,4)`: `p_base+Jn=9<10=p_actual`.

The new area constant is necessary, not contradictory.  At equality almost every level component is singleton, but no theorem currently converts their paired locations into a nonzero low-dimensional resultant with a strict subleading gap.  Literal ratio-one saturation of the actual P157 maximum-state upper bound is not derived.

H172 and H133 remain OPEN.  `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    corpus = corpus_audit()
    scalar = scalar_audit()
    synthetic = synthetic_audit()
    regressions = regression_audit()
    theory = theory_artifact()
    write_json(args.artifact_dir / "phase30_theory.json", theory)
    write_json(args.artifact_dir / "phase30_transport_corpus.json", corpus)
    write_json(args.artifact_dir / "phase30_scalar_certificates.json", scalar)
    write_json(args.artifact_dir / "phase30_synthetic_profiles.json", synthetic)
    write_json(args.artifact_dir / "phase30_regressions.json", regressions)
    (args.artifact_dir / "phase30_obstruction_report.md").write_text(obstruction_report(corpus), encoding="utf-8")
    print(json.dumps({"valid": True, "claims": EXPECTED_CLAIMS, "counts": corpus["counts"], "proves_collatz": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
