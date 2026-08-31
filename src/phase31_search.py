#!/usr/bin/env python3
"""Generate exact Phase 31 double-hit transport evidence.

The supplied note is an untrusted proposal.  All acceptance decisions use
integers and Fractions; floating point is not used.
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
        transport_data,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 8
EXPECTED_CLAIMS = {
    "P185": "VERIFIED_THEOREM",
    "P186": "VERIFIED_THEOREM",
    "P187": "VERIFIED_THEOREM",
    "P188": "VERIFIED_THEOREM",
    "P189": "VERIFIED_THEOREM",
    "P190": "VERIFIED_THEOREM",
    "E43": "VERIFIED_FINITE",
    "NG40": "REFUTED",
    "H172": "OPEN",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def boundaries(exponents: Sequence[int]) -> tuple[int, ...]:
    result = [0]
    for value in exponents:
        result.append(result[-1] + value)
    return tuple(result)


def cyclic_window(word: str, start: int, width: int) -> str:
    return "".join(word[(start + offset) % len(word)] for offset in range(width))


def profile_components(profile: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (level, start, end)
        for level, intervals in enumerate(level_intervals(profile), start=1)
        for start, end in intervals
    )


def static_inventory(exponents: Sequence[int]) -> dict[str, object]:
    item = transport_data(exponents, check_intervals=False)
    profile = tuple(item["profile"])
    base = tuple(item["baseline"])
    height = int(item["height"])
    peak = profile[:-1].index(height) if height else 0
    components = profile_components(profile)
    spine = {
        row
        for row in components
        if height and row[1] <= peak < row[2]
    }
    if len(spine) != height:
        raise AssertionError("one nested spine component per level")
    extracted = tuple(
        row for row in components if row not in spine and row[2] - row[1] == 1
    )
    exceptional = tuple(row for row in components if row not in extracted)
    residual_profile = list(profile)
    labels = []
    for level, start, end in extracted:
        if end != start + 1 or residual_profile[start] != level:
            raise AssertionError("singleton is not a top cell")
        if profile[start + 1] != level - 1 or base[start] != 2:
            raise AssertionError("singleton descent convention")
        residual_profile[start] -= 1
        labels.append(start)
    if len(labels) != len(set(labels)):
        raise AssertionError("one extracted top cell per label")
    residual_profile_tuple = tuple(residual_profile)
    residual_exponents = profile_to_exponents(base, residual_profile_tuple)
    if set(profile_components(residual_profile_tuple)) != set(exceptional):
        raise AssertionError("residual component inventory")
    residual_word = expanded_word(residual_exponents)
    actual_word = expanded_word(exponents)
    residual_boundaries = boundaries(residual_exponents)
    anchors = tuple((residual_boundaries[label], residual_boundaries[label] + 1) for label in labels)
    used_positions = [position for pair in anchors for position in pair]
    if len(used_positions) != len(set(used_positions)):
        raise AssertionError("static swaps overlap")
    reconstructed = list(residual_word)
    for left, right in anchors:
        if reconstructed[left : right + 1] != ["1", "0"]:
            raise AssertionError("static swap source")
        reconstructed[left], reconstructed[right] = reconstructed[right], reconstructed[left]
    if "".join(reconstructed) != actual_word:
        raise AssertionError("static swap reconstruction")
    area = int(item["area"])
    J = int(item["J"])
    sigma = int(item["descent_slack"])
    E = len(exceptional)
    K = len(extracted)
    if E != J - K or E > height + sigma:
        raise AssertionError("exceptional component bound")
    base_boundaries = boundaries(base)
    residual_span = sum(
        base_boundaries[end] - base_boundaries[start]
        for _, start, end in exceptional
    )
    if residual_span > 2 * area:
        raise AssertionError("residual span")
    return {
        "q": int(item["q"]),
        "L": int(item["L"]),
        "area": area,
        "height": height,
        "J": J,
        "sigma": sigma,
        "E": E,
        "K": K,
        "profile": profile,
        "base": base,
        "residual_profile": residual_profile_tuple,
        "residual_exponents": residual_exponents,
        "residual_span": residual_span,
        "anchors": anchors,
        "base_word": expanded_word(base),
        "residual_word": residual_word,
        "actual_word": actual_word,
    }


def double_hit_audit(
    exponents: Sequence[int], widths: Sequence[int] | None = None
) -> dict[str, object]:
    inventory = static_inventory(exponents)
    length = int(inventory["L"])
    area = int(inventory["area"])
    J = int(inventory["J"])
    E = int(inventory["E"])
    K = int(inventory["K"])
    residual_span = int(inventory["residual_span"])
    base_word = str(inventory["base_word"])
    residual_word = str(inventory["residual_word"])
    actual_word = str(inventory["actual_word"])
    anchors = tuple(inventory["anchors"])
    selected = tuple(range(1, length + 1)) if widths is None else tuple(sorted(set(widths)))
    rows = []
    counts = {
        "context_width_checks": 0,
        "low_type_checks": 0,
        "distinct_factor_checks": 0,
        "grid_bound_checks": 0,
        "grid_recurrence_steps": 0,
        "exact_grid_cases": 0,
    }
    anchor_bits = [0] * length
    for left, _ in anchors:
        anchor_bits[left] = 1
    for width in selected:
        if not 1 <= width <= length:
            raise ValueError("factor width")
        context_width = width + 2
        exceptional_starts = {
            start
            for start in range(length)
            if cyclic_window(residual_word, start, context_width)
            != cyclic_window(base_word, start, context_width)
        }
        context_bound = residual_span + E * (width + 1)
        area_context_bound = 2 * area + E * (width + 1)
        if len(exceptional_starts) > min(length, context_bound) or context_bound > area_context_bound:
            raise AssertionError("exceptional context bound")
        incidence = [0] * length
        for left, right in anchors:
            affected = {
                (position - offset) % length
                for position in (left, right)
                for offset in range(width)
            }
            if len(affected) > min(length, width + 1):
                raise AssertionError("singleton influence size")
            for start in affected:
                incidence[start] += 1
        low_starts = [
            start
            for start in range(length)
            if start not in exceptional_starts and incidence[start] <= 1
        ]
        low_types = {cyclic_window(actual_word, start, width) for start in low_starts}
        B1 = (width + 2) * (width + 3)
        if len(low_types) > B1:
            raise AssertionError("low-hit factor types")
        factor_count = len(cyclic_factors(actual_word, width))
        distinct = factor_count == length
        double_hit_rhs = (J + E) * (width + 1) + 4 * area + 2 * B1
        if distinct and 2 * length > double_hit_rhs:
            raise AssertionError("double-hit factor inequality")
        window_length = width + 1
        grid_counts = [
            sum(anchor_bits[(start + offset) % length] for offset in range(window_length))
            for start in range(length)
        ]
        mismatches = 0
        for start in range(length):
            difference = grid_counts[(start + 1) % length] - grid_counts[start]
            expected = anchor_bits[(start + window_length) % length] - anchor_bits[start]
            if difference != expected:
                raise AssertionError("grid recurrence")
            mismatches += expected != 0
        bad_grid = sum(value != 2 for value in grid_counts)
        if mismatches > 2 * bad_grid:
            raise AssertionError("approximate grid bound")
        exact_grid = bad_grid == 0
        if exact_grid:
            quotient = window_length // math.gcd(length, window_length)
            if quotient not in (1, 2):
                raise AssertionError("exact grid denominator")
        rows.append(
            [
                width,
                len(exceptional_starts),
                context_bound,
                area_context_bound,
                len(low_types),
                B1,
                factor_count,
                int(distinct),
                sum(incidence),
                K * (width + 1),
                double_hit_rhs,
                bad_grid,
                mismatches,
            ]
        )
        counts["context_width_checks"] += 1
        counts["low_type_checks"] += 1
        counts["distinct_factor_checks"] += int(distinct)
        counts["grid_bound_checks"] += 1
        counts["grid_recurrence_steps"] += length
        counts["exact_grid_cases"] += int(exact_grid)
    summary = {
        key: inventory[key]
        for key in (
            "q",
            "L",
            "area",
            "height",
            "J",
            "sigma",
            "E",
            "K",
            "residual_span",
        )
    }
    summary.update(counts)
    summary["factor_rows"] = rows
    return summary


def corpus_audit() -> dict[str, object]:
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "static_reconstructions": 0,
        "extracted_swaps": 0,
        "exceptional_components": 0,
        "context_width_checks": 0,
        "low_type_checks": 0,
        "distinct_factor_checks": 0,
        "grid_bound_checks": 0,
        "grid_recurrence_steps": 0,
        "exact_grid_cases": 0,
    }
    digest_rows = []
    samples = []
    for q in range(1, Q_MAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                counts["noncoprime_classes"] += int(math.gcd(q, length) > 1)
                for rotated in minimum_rotations(values):
                    row = double_hit_audit(rotated)
                    counts["minimum_rotations"] += 1
                    counts["static_reconstructions"] += 1
                    counts["extracted_swaps"] += int(row["K"])
                    counts["exceptional_components"] += int(row["E"])
                    for key in (
                        "context_width_checks",
                        "low_type_checks",
                        "distinct_factor_checks",
                        "grid_bound_checks",
                        "grid_recurrence_steps",
                        "exact_grid_cases",
                    ):
                        counts[key] += int(row[key])
                    digest_rows.append([list(rotated), row])
                    if row["K"] and len(samples) < 10:
                        samples.append([list(rotated), row])
    if counts["cyclic_classes"] != 2214 or counts["minimum_rotations"] != 3101:
        raise AssertionError("Phase 31 corpus regression")
    return {
        "format": "collatz-phase31-double-hit-corpus-v1",
        "maximum_q": Q_MAX,
        "counts": counts,
        "row_digest_sha256": stable_hash(digest_rows),
        "extraction_samples": samples,
        "scope": "Complete positive-D cyclic exponent corpus through q<=8 and every cyclic width; finite rational profiles are structural controls, not asserted integer cycles.",
        "proves_collatz": False,
    }


def hit_constant_cube(slope: Fraction) -> Fraction:
    if not 1 < slope <= 2:
        raise ValueError("slope")
    return Fraction(27, 2) * slope * slope / (slope - 1)


def scalar_audit() -> dict[str, object]:
    ln2 = log_interval(Fraction(2), terms=112)
    ln3 = log_interval(Fraction(3), terms=112)
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    critical_cube = (hit_constant_cube(alpha[1]), hit_constant_cube(alpha[0]))
    phase30_cube = (
        Fraction(27, 8) * alpha[1] * alpha[1] / (alpha[1] - 1),
        Fraction(27, 8) * alpha[0] * alpha[0] / (alpha[0] - 1),
    )
    if critical_cube != tuple(4 * value for value in phase30_cube):
        raise AssertionError("Phase 30 cube improvement")
    noncritical_cube = Fraction(54)
    critical_decimal = decimal_cuberoot_box(*critical_cube)
    noncritical_decimal = decimal_cuberoot_box(noncritical_cube, noncritical_cube)
    if critical_decimal != [["3870329", "1000000"], ["387033", "100000"]]:
        raise AssertionError("critical decimal enclosure")
    if noncritical_decimal != [["3779763", "1000000"], ["944941", "250000"]]:
        raise AssertionError("noncritical decimal enclosure")
    slope_rows = []
    for slope in (Fraction(8, 5), Fraction(5, 3), Fraction(7, 4), Fraction(19, 10), Fraction(2)):
        slope_rows.append([encode_fraction(slope), encode_fraction(hit_constant_cube(slope))])
    return {
        "format": "collatz-phase31-scalar-certificates-v1",
        "log_terms": 112,
        "log2_three_interval": [encode_fraction(value) for value in alpha],
        "critical_constant_cube_interval": [encode_fraction(value) for value in critical_cube],
        "critical_constant_decimal_box": critical_decimal,
        "noncritical_constant_cube": encode_fraction(noncritical_cube),
        "noncritical_constant_decimal_box": noncritical_decimal,
        "phase30_constant_cube_interval": [encode_fraction(value) for value in phase30_cube],
        "exact_improvement": "C_hit(ell)^3=4*C_move(ell)^3, hence C_hit=2^(2/3)*C_move",
        "near_equality": {
            "height_scale_cube": "2*ell*(ell-1)",
            "J_plus_sigma_scale_cube": "4*ell^2/(ell-1)",
            "area_over_J_plus_sigma": encode_fraction(Fraction(3, 2)),
        },
        "slope_rows": slope_rows,
        "proves_collatz": False,
    }


def width_two_profile(q: int, length: int, count: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, length)
    profile = [0] * (q + 1)
    chosen = 0
    for start in range(1, q - 1):
        if chosen == count:
            break
        if base[start + 1] == 2 and not any(profile[max(0, start - 1) : start + 3]):
            profile[start] = profile[start + 1] = 1
            chosen += 1
    if chosen != count:
        raise AssertionError("width-two synthesis")
    profile_to_exponents(base, profile)
    return tuple(profile)


def multi_peak_profile(q: int, length: int, heights: Sequence[int]) -> tuple[int, ...]:
    base = mechanical_baseline(q, length)
    profile = [0]
    remaining = list(heights)
    for index in range(q):
        current = profile[-1]
        if not current and remaining:
            next_value = remaining.pop(0)
        elif current and base[index] == 2:
            next_value = current - 1
        else:
            next_value = current
        profile.append(next_value)
    if profile[-1] or remaining:
        raise AssertionError("multiple peak closure")
    return tuple(profile)


def near_grid_profile(q: int, length: int, modulus: int, count: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, length)
    base_boundaries = boundaries(base)
    profile = [0] * (q + 1)
    candidates = [
        label
        for label in range(1, q)
        if base[label] == 2 and base_boundaries[label] % modulus == 0
    ]
    selected = []
    for label in candidates:
        if all(abs(label - old) > 1 for old in selected):
            selected.append(label)
        if len(selected) == count:
            break
    if len(selected) != count:
        raise AssertionError("near-grid synthesis")
    for label in selected:
        profile[label] = 1
    profile_to_exponents(base, profile)
    return tuple(profile)


def residual_heavy_profile(q: int, length: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, length)
    profile = list(width_two_profile(q, length, 24))
    inserted = 0
    for label in range(1, q):
        if inserted == 24:
            break
        if base[label] == 2 and not any(profile[max(0, label - 1) : label + 2]):
            profile[label] = 1
            inserted += 1
    if inserted != 24:
        raise AssertionError("residual-heavy singleton synthesis")
    profile_to_exponents(base, profile)
    return tuple(profile)


def synthetic_audit() -> dict[str, object]:
    q7, L7, p7 = seven_grid_time_profile()
    q, length = 377, 600
    profiles = [
        ("tall", 125, 199, tall_profile(125, 199, 5)),
        ("plateau", 125, 199, plateau_profile(125, 199, 5)),
        ("isolated", 125, 199, isolated_profile(125, 199, 20)),
        ("near-extremal", 1331, 2110, near_extremal_profile(1331, 2110, 9, 124)),
        ("seven-grid", q7, L7, p7),
        ("width-two", q, length, width_two_profile(q, length, 32)),
        ("multiple-peaks", q, length, multi_peak_profile(q, length, (5, 7, 4, 8, 6))),
        ("near-grid-singletons", q, length, near_grid_profile(q, length, 13, 16)),
        ("residual-heavy", q, length, residual_heavy_profile(q, length)),
    ]
    widths = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
    rows = []
    for name, profile_q, profile_length, profile in profiles:
        exponents = profile_to_exponents(mechanical_baseline(profile_q, profile_length), profile)
        audit = double_hit_audit(exponents, tuple(width for width in widths if width <= profile_length))
        rows.append([name, profile_q, profile_length, list(profile), list(exponents), audit])
    return {
        "format": "collatz-phase31-synthetic-profiles-v1",
        "rows": rows,
        "row_digest_sha256": stable_hash(rows),
        "scope": "Nine exact legal profiles covering tall, plateau, isolated, near-extremal, width-two, multipeak, near-grid, and residual-heavy geometries at ten declared widths.",
        "proves_collatz": False,
    }


def bit_exponents(bits: str) -> tuple[int, ...]:
    positions = [index for index, bit in enumerate(bits) if bit == "1"]
    return tuple(
        (positions[(index + 1) % len(positions)] - position) % len(bits) or len(bits)
        for index, position in enumerate(positions)
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
    family_rows = []
    for name, bits in families:
        exponents = bit_exponents(bits)
        positive_d = 2 ** sum(exponents) > 3 ** len(exponents)
        audit = None
        if positive_d:
            candidates = minimum_rotations(exponents)
            if candidates:
                row = double_hit_audit(candidates[0], (1, min(3, len(bits)), min(5, len(bits))))
                audit = {key: row[key] for key in ("q", "L", "area", "J", "E", "K")}
        family_rows.append([name, bits, list(exponents), positive_d, audit])
    normalized_countermodel = {
        "slope": 2,
        "algebraic_symbol": "y with y^3=4",
        "w": "y^2",
        "x": "y^2/2",
        "z": "y^2/2",
        "e": "y^2/2",
        "k": 0,
        "u_over_q": 2,
        "identities": [
            "(x+z)y=4=2ell",
            "ey=2=ell",
            "x-e=0",
            "w+y^2/2=3y^2/2=C_hit(2)",
        ],
        "interpretation": "The normalized inequality chain can saturate with no singleton anchors and a full-density residual exceptional set. It therefore does not imply global approximate-grid invariance.",
    }
    return {
        "format": "collatz-phase31-regressions-v1",
        "mandatory_families": family_rows,
        "named_controls": {
            "negative_q2": [1, 2],
            "negative_q7": list(NEGATIVE_Q7),
            "NG34_NG39": "preserved by the Phase 29-30 accepted artifacts and required by the Phase 31 acceptance contract",
        },
        "NG40_normalized_countermodel": normalized_countermodel,
        "proposal_repair": "P190 gives exact and defect-count grid identities only. P187/P189 do not force the global bad-window count to be o(L), because the residual exceptional-context set may have positive density.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    statements = {
        "P185": "Every valid reduced profile admits static extraction of all nonspine singleton top cells into pairwise-disjoint 10->01 swaps; the residual has E exceptional components with E<=h+Sigma.",
        "P186": "For every cyclic width n, residual exceptional contexts and low-hit factor types obey the exact stated bounds; if all L factors are distinct then 2L<=(J+E)(n+1)+4A+2(n+2)(n+3).",
        "P187": "Under a fixed inverse-polynomial multiplier gap and limiting slope ell, primitive positive cycles satisfy liminf A/q^(2/3)>=3(2ell)^(2/3)/(2(ell-1)^(1/3)).",
        "P188": "The noncritical constant is 3*2^(1/3); the critical log2(3) specialization uses EXT17 and lies in the certified interval.",
        "P189": "Equality forces the unique h and J+Sigma scales, A/(J+Sigma)->3/2, E-Sigma=o(q^(2/3)), aggregate minimal residual excess, and local exact-two incidence outside the residual exceptional set; it does not force a global near-grid.",
        "P190": "For cyclic anchor counts c_t at window w, c_(t+1)-c_t=chi_(t+w)-chi_t; exact c=2 gives gcd-periodicity and w/gcd(L,w) in {1,2}, while shift mismatches are at most twice the number of c!=2 starts.",
        "E43": "The complete q<=8 corpus, nine synthetic profiles, scalars, normalized obstruction, and mandatory controls are independently reproducible.",
        "NG40": "The P185-P189 inequality chain alone does not force global approximate-grid invariance: a normalized equality countermodel has K=0 and a full-density residual exceptional set.",
        "H172": "A residual-heavy/grid-like arithmetic dichotomy with a strict subleading resultant remains open.",
        "H133": "Arbitrary-area positive cycles remain open.",
    }
    return {
        "format": "collatz-phase31-double-hit-theory-v1",
        "claims": {
            key: {"status": EXPECTED_CLAIMS[key], "statement": statement}
            for key, statement in statements.items()
        },
        "dependencies": {
            "P185": ["P156", "P167", "P184"],
            "P186": ["P125", "P179", "P185"],
            "P187": ["P167", "P180", "P186"],
            "P188": ["P163", "P164", "P187", "EXT17"],
            "P189": ["P167", "P185", "P186", "P187"],
            "P190": ["P185"],
            "NG40": ["P185", "P186", "P187", "P189", "P190"],
        },
        "external_boundary": "Only P188's critical specialization inherits EXT17; extraction, double-hit counting, the noncritical constant, and the grid identities are internal.",
        "proposal_repair": "The note's approximate-grid language is retained only conditionally on the global bad-window count. Equality in the area bound alone allows a residual exceptional set of positive density and does not imply global shift invariance.",
        "proves_collatz": False,
        "what_this_result_does_not_prove": "No grid/residual resultant, arbitrary-area cycle exclusion, nonperiodic exclusion, or Collatz proof follows.",
    }


def obstruction_report(corpus: dict[str, object]) -> str:
    counts = corpus["counts"]
    return f"""# Phase 31 obstruction report

Static extraction and the double-hit inequality passed {counts['context_width_checks']:,} exact widths over {counts['minimum_rotations']:,} discrepancy-minimum rotations.  The audit reconstructed {counts['extracted_swaps']:,} disjoint singleton swaps and checked {counts['grid_recurrence_steps']:,} grid-recurrence positions.

The stronger area constant is a necessary condition, not a contradiction.  Moreover, equality in the normalized inequality chain does not by itself give a global near-grid: at `ell=2`, let `y^3=4` and `x=z=e=y^2/2`.  Then every leading inequality saturates while `K=x-e=0` and the residual exceptional set may cover all starts.  P190 therefore records only the exact grid identity and its defect-count consequence.

H172 still requires a strict arithmetic dichotomy: a low-denominator resultant on the genuinely grid-like subcase and a separate residual-component resultant when exceptional contexts have positive density.  H172 and H133 remain OPEN.  `proves_collatz=false`.
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
    write_json(args.artifact_dir / "phase31_theory.json", theory)
    write_json(args.artifact_dir / "phase31_transport_corpus.json", corpus)
    write_json(args.artifact_dir / "phase31_scalar_certificates.json", scalar)
    write_json(args.artifact_dir / "phase31_synthetic_profiles.json", synthetic)
    write_json(args.artifact_dir / "phase31_regressions.json", regressions)
    (args.artifact_dir / "phase31_obstruction_report.md").write_text(
        obstruction_report(corpus), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "valid": True,
                "claims": EXPECTED_CLAIMS,
                "counts": corpus["counts"],
                "proves_collatz": False,
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
