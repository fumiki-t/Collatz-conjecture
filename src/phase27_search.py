#!/usr/bin/env python3
"""Generate exact Phase 27 asymptotic cycle-area evidence.

The supplied Phase 27 note is an untrusted proposal.  The generator accepts
only integer, Fraction, or rigorously enclosed logarithmic comparisons.  A
display decimal is never used for a proof decision.
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
        affine_correction,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
        rational_odd_orbit,
        reduced_profile,
        rotations,
    )
except ModuleNotFoundError:
    from src.phase26_search import (
        A_BITS,
        B_BITS,
        affine_correction,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
        rational_odd_orbit,
        reduced_profile,
        rotations,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


PROFILE_Q_MAXIMUM = 8
V = 300_000
VX = 2075 * 2**60
MATVEEV_K = 1_564_920_000
EXPECTED_CLAIMS = {
    "EXT17": "EXTERNAL_THEOREM",
    "P162": "VERIFIED_THEOREM",
    "P163": "VERIFIED_THEOREM",
    "P164": "VERIFIED_THEOREM",
    "P165": "VERIFIED_THEOREM",
    "E39": "VERIFIED_FINITE",
    "NG36": "REFUTED",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(rows: object) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def hamming(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("Hamming words must have equal length")
    return sum(a != b for a, b in zip(left, right, strict=True))


def ceil_log2_three_power(q: int) -> int:
    value = 3**q
    exponent = value.bit_length() - 1
    return exponent if 2**exponent > value else exponent + 1


def cycle_branch(q: int, L: int) -> str:
    critical = ceil_log2_three_power(q)
    if L == critical:
        return "critical"
    if L > critical:
        return "noncritical"
    raise ValueError("positive-D word below critical length")


def least_and_discrepancy_offsets(values: Sequence[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    values = tuple(values)
    orbit = rational_odd_orbit(values)[:-1]
    least = min(orbit)
    least_offsets = tuple(index for index, value in enumerate(orbit) if value == least)
    minimum_words = set(minimum_rotations(values))
    discrepancy_offsets = tuple(
        index for index, rotated in enumerate(rotations(values)) if rotated in minimum_words
    )
    return least_offsets, discrepancy_offsets


def exact_master_margin(q: int, L: int, area: int, height: int) -> tuple[bool, Fraction]:
    """Exponentiated P157 inequality, evaluated as an algebraic shadow check."""
    multiplier = Fraction(3**q, 2**L)
    gap = multiplier * (1 - multiplier)
    left = Fraction(2**L) * (3 * gap) ** (area + 1)
    right = Fraction((2 ** (height + 4) * q) ** (area + 1))
    return left < right, right - left


def corpus_audit() -> dict[str, object]:
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "critical_classes": 0,
        "noncritical_classes": 0,
        "noncoprime_classes": 0,
        "support_hamming_checks": 0,
        "support_factor_checks": 0,
        "support_height_checks": 0,
        "shadow_master_checks": 0,
        "shadow_master_passes": 0,
        "rotation_mismatches": 0,
    }
    rows: list[object] = []
    mismatch_rows: list[object] = []
    for q in range(1, PROFILE_Q_MAXIMUM + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(L, q)}):
                counts["cyclic_classes"] += 1
                is_primitive = primitive(values)
                counts["primitive_classes"] += int(is_primitive)
                branch = cycle_branch(q, L)
                counts[f"{branch}_classes"] += 1
                invariants = set()
                representative = None
                for rotated in minimum_rotations(values):
                    data = reduced_profile(rotated)
                    base = expanded_word(data["baseline"])
                    actual = expanded_word(rotated)
                    support = sum(value > 0 for value in data["profile"][:-1])
                    distance = hamming(base, actual)
                    if distance > 2 * support:
                        raise AssertionError("arbitrary-gcd Hamming support")
                    if data["height"] > support:
                        raise AssertionError("support height")
                    counts["support_hamming_checks"] += 1
                    counts["support_height_checks"] += 1
                    maximum_ratio = Fraction(0)
                    for width in range(1, L + 1):
                        base_count = len(cyclic_factors(base, width))
                        actual_count = len(cyclic_factors(actual, width))
                        bound = (2 * support + 1) * width + 1
                        if base_count > width + 1 or actual_count > base_count + width * distance:
                            raise AssertionError("Hamming factor transport")
                        if actual_count > bound:
                            raise AssertionError("support factor bound")
                        counts["support_factor_checks"] += 1
                        maximum_ratio = max(maximum_ratio, Fraction(actual_count, bound))
                    invariants.add((data["area"], data["height"], support, distance))
                    representative = (rotated, data, support, distance, maximum_ratio)
                if representative is None or len(invariants) != 1:
                    raise AssertionError("support invariance across minimum rotations")
                rotated, data, support, distance, maximum_ratio = representative
                counts["noncoprime_classes"] += int(data["d"] > 1)
                master, margin = exact_master_margin(q, L, data["area"], data["height"])
                counts["shadow_master_checks"] += 1
                counts["shadow_master_passes"] += int(master)
                least_offsets, discrepancy_offsets = least_and_discrepancy_offsets(values)
                mismatch = set(least_offsets).isdisjoint(discrepancy_offsets)
                counts["rotation_mismatches"] += int(mismatch)
                orbit = rational_odd_orbit(values)[:-1]
                row = [
                    q,
                    L,
                    list(values),
                    is_primitive,
                    branch,
                    data["d"],
                    data["area"],
                    data["height"],
                    support,
                    distance,
                    encode_fraction(maximum_ratio),
                    master,
                    encode_fraction(margin),
                    list(least_offsets),
                    list(discrepancy_offsets),
                    mismatch,
                ]
                rows.append(row)
                if mismatch:
                    mismatch_rows.append(
                        [
                            q,
                            L,
                            list(values),
                            [encode_fraction(value) for value in orbit],
                            list(least_offsets),
                            list(discrepancy_offsets),
                        ]
                    )
    if not mismatch_rows or mismatch_rows[0][:3] != [2, 4, [1, 3]]:
        raise AssertionError("smallest rotation-alignment obstruction")
    return {
        "format": "collatz-phase27-cycle-corpus-v1",
        "maximum_q": PROFILE_Q_MAXIMUM,
        "counts": counts,
        "row_digest_sha256": stable_hash(rows),
        "mismatch_digest_sha256": stable_hash(mismatch_rows),
        "smallest_rotation_mismatch": {
            "q": 2,
            "L": 4,
            "exponents": [1, 3],
            "odd_rational_orbit": [["5", "7"], ["11", "7"]],
            "least_value_offsets": [0],
            "discrepancy_minimum_offsets": [1],
            "positive_integral": False,
        },
        "scope": "Complete positive-D cyclic exponent corpus through q<=8. P157's exponentiated margin is a rational-shadow diagnostic only; ordinary-state separation is not promoted for nonintegral shadows.",
        "proves_collatz": False,
    }


def height_bound(area: int) -> int:
    return (math.isqrt(8 * area + 1) - 1) // 2


def floor_cuberoot(value: int) -> int:
    low, high = 0, 1
    while high**3 <= value:
        high *= 2
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**3 <= value:
            low = middle
        else:
            high = middle
    return low


def ceil_cuberoot(value: int) -> int:
    root = floor_cuberoot(value)
    return root if root**3 == value else root + 1


def noncritical_margin(q: int, area: int, minimum: int = V) -> tuple[Fraction, Fraction]:
    ln2_low, ln2_high = log_interval(Fraction(2))
    ln3_low, _ = log_interval(Fraction(3))
    _, log_m_high = log_interval(Fraction(2 * q, 3))
    _, log_pack_high = log_interval(Fraction(minimum + 3 * q, minimum))
    height = height_bound(area)
    left_lower = q * ln3_low
    right_upper = (area + 1) * (
        (height + 4) * ln2_high
        + log_m_high
        + Fraction(1, minimum)
        + log_pack_high / 9
    )
    return left_lower, right_upper


def critical_margin(q: int, area: int) -> tuple[Fraction, Fraction]:
    ln2_low, ln2_high = log_interval(Fraction(2))
    ln3_low, _ = log_interval(Fraction(3))
    _, ln12_high = log_interval(Fraction(12))
    _, ln_q_high = log_interval(Fraction(q))
    _, ln_four_thirds_high = log_interval(Fraction(4, 3))
    height = height_bound(area)
    left_lower = q * ln3_low
    right_upper = (area + 1) * (
        (height + 4) * ln2_high
        + ln_four_thirds_high
        + MATVEEV_K * ln12_high
        + (MATVEEV_K + 1) * ln_q_high
    )
    return left_lower, right_upper


def least_unexcluded(q: int, branch: str, minimum: int = V) -> int:
    margin = critical_margin if branch == "critical" else lambda q0, area: noncritical_margin(q0, area, minimum)
    high = 1
    while margin(q, high)[0] > margin(q, high)[1]:
        high *= 2
    low = 0
    while low < high:
        middle = (low + high) // 2
        if margin(q, middle)[0] > margin(q, middle)[1]:
            low = middle + 1
        else:
            high = middle
    return low


def envelope_row(q: int, branch: str, minimum: int = V) -> dict[str, object]:
    frontier = least_unexcluded(q, branch, minimum)
    margin = critical_margin if branch == "critical" else lambda q0, area: noncritical_margin(q0, area, minimum)
    previous_left, previous_right = margin(q, frontier - 1) if frontier else (Fraction(0), Fraction(0))
    current_left, current_right = margin(q, frontier)
    return {
        "q": str(q),
        "branch": branch,
        "minimum": str(minimum) if branch == "noncritical" else None,
        "least_unexcluded_area": str(frontier),
        "excluded_through": str(frontier - 1),
        "previous_positive_margin": frontier == 0 or previous_left > previous_right,
        "current_positive_margin": current_left > current_right,
        "previous_margin": encode_fraction(previous_left - previous_right),
        "current_margin": encode_fraction(current_left - current_right),
        "cube_ratio": encode_fraction(Fraction(frontier**3, q**2)),
    }


def envelope_audit() -> dict[str, object]:
    matveev_integer_check = 5 * MATVEEV_K == 7 * 30**5 * 23 * 2
    if not matveev_integer_check or 2**9 >= 23**2:
        raise AssertionError("Matveev rational majorant")
    noncritical_q = [50_000_000, 51_000_000, 10**8, 10**10, 10**12, 10**18, 10**24]
    critical_q = [10**12, 10**18, 10**24, 10**30, 10**36, 10**42]
    noncritical_rows = [envelope_row(q, "noncritical") for q in noncritical_q]
    critical_rows = [envelope_row(q, "critical") for q in critical_q]
    x02 = envelope_row(4 * 10**23, "noncritical", VX)
    if int(noncritical_rows[0]["excluded_through"]) < 100_000:
        raise AssertionError("P159 reconstruction")
    if int(x02["excluded_through"]) < 5 * 10**15:
        raise AssertionError("P160 reconstruction")
    ln2_low, ln2_high = log_interval(Fraction(2))
    ln3_low, ln3_high = log_interval(Fraction(3))
    alpha_low = ln3_low / ln2_high
    alpha_high = ln3_high / ln2_low
    return {
        "format": "collatz-phase27-effective-envelopes-v1",
        "matveev_specialization": {
            "paper_constant": "1.4*30^5*2^(9/2)*log(2)*log(3)",
            "integer_majorant_K": MATVEEV_K,
            "majorant_identity": "5*K=7*30^5*23*2",
            "sqrt_bound": "2^(9/2)<23 because 2^9<23^2",
            "log_product_bound": "log(2)*log(3)<2",
            "multiplicative_form": "Xi=2^L*3^(-q)-1>0",
            "coefficient_height": "B=L<2q",
            "gap": "lambda*(1-lambda) > q^(-K)/(4*12^K)",
            "exact_majorant_verified": matveev_integer_check,
        },
        "asymptotic_constants": {
            "area_constant": "((log_2(3))^2/2)^(1/3)",
            "area_constant_cube_interval": [
                encode_fraction(alpha_low * alpha_low / 2),
                encode_fraction(alpha_high * alpha_high / 2),
            ],
            "support_constant": "sqrt(log_2(3)/2)",
            "support_constant_square_interval": [
                encode_fraction(alpha_low / 2),
                encode_fraction(alpha_high / 2),
            ],
        },
        "noncritical_rows": noncritical_rows,
        "critical_rows": critical_rows,
        "x02_control": x02,
        "boundary": "Finite rows are exact scalar sanity checks. The asymptotic theorem is proved analytically and is not inferred from this grid.",
        "proves_collatz": False,
    }


def mechanical_baseline(q: int, L: int) -> tuple[int, ...]:
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    residues = tuple((-L0 * index) % q0 for index in range(q + 1))
    boundaries = tuple((L0 * index + residues[index]) // q0 for index in range(q + 1))
    return tuple(boundaries[index + 1] - boundaries[index] for index in range(q))


def profile_to_exponents(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    if len(profile) != len(base) + 1 or profile[0] or profile[-1] or min(profile) < 0:
        raise ValueError("invalid profile endpoints")
    values = tuple(base[index] + profile[index + 1] - profile[index] for index in range(len(base)))
    if min(values) < 1:
        raise ValueError("profile violates positive exponent recurrence")
    return values


def tall_profile(q: int, L: int, height: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, L)
    profile = [0, height]
    for index in range(1, q):
        current = profile[-1]
        profile.append(current - 1 if current and base[index] == 2 else current)
    if profile[-1]:
        raise AssertionError("tall profile did not descend")
    return tuple(profile)


def diffuse_profile(q: int, L: int, height: int, target_area: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, L)
    profile = [0]
    completed_area = 0
    cooldown = False
    for index in range(q):
        current = profile[-1]
        enough_descent = sum(value == 2 for value in base[index + 1 :]) >= height
        if current == 0 and completed_area < target_area and not cooldown and enough_descent:
            next_value = height
            cooldown = True
        elif current and base[index] == 2:
            next_value = current - 1
            if next_value == 0:
                completed_area = sum(profile)
        else:
            next_value = current
            if current == 0:
                cooldown = False
        profile.append(next_value)
    if profile[-1]:
        raise AssertionError("diffuse profile did not close")
    return tuple(profile)


def profile_sample(kind: str, q: int, profile: Sequence[int]) -> dict[str, object]:
    L = ceil_log2_three_power(q)
    base = mechanical_baseline(q, L)
    exponents = profile_to_exponents(base, profile)
    support = sum(value > 0 for value in profile[:-1])
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    actual = expanded_word(exponents)
    baseline_word = expanded_word(base)
    distance = hamming(actual, baseline_word)
    if distance > 2 * support or height > support:
        raise AssertionError("synthetic support invariant")
    return {
        "kind": kind,
        "q": q,
        "L": L,
        "area": area,
        "height": height,
        "support": support,
        "hamming": distance,
        "area_cube_over_q_squared": encode_fraction(Fraction(area**3, q**2)),
        "height_cube_over_q": encode_fraction(Fraction(height**3, q)),
        "valid_positive_exponents": min(exponents) >= 1,
        "profile_digest_sha256": stable_hash(list(profile)),
        "exponent_digest_sha256": stable_hash(list(exponents)),
    }


def synthetic_audit() -> dict[str, object]:
    rows = []
    for q in (125, 343, 729, 1331):
        L = ceil_log2_three_power(q)
        h_tall = max(2, floor_cuberoot(q))
        tall = tall_profile(q, L, h_tall)
        rows.append(profile_sample("tall", q, tall))
        h_diffuse = max(2, q.bit_length() - 1)
        target = ceil_cuberoot(q**2)
        diffuse = diffuse_profile(q, L, h_diffuse, target)
        rows.append(profile_sample("diffuse", q, diffuse))
    return {
        "format": "collatz-phase27-synthetic-profiles-v1",
        "rows": rows,
        "row_digest_sha256": stable_hash(rows),
        "near_grid_control": {
            "q": 63_322,
            "L": 100_363,
            "roots": [9_046, 18_092, 27_138],
            "q_arc_width": 54_181,
            "L_arc_width": 85_875,
            "direct_modular_gcd": 1,
        },
        "boundary": "These are valid reduced profiles and exact adversarial controls, not positive integer cycles. They do not prove optimality of the two asymptotic exponents for actual cycles.",
        "proves_collatz": False,
    }


def bit_exponents(bits: str) -> tuple[int, ...]:
    if not bits or bits[0] != "1":
        raise ValueError("cyclic bit word must start with one")
    starts = [index for index, bit in enumerate(bits) if bit == "1"]
    return tuple((starts[(index + 1) % len(starts)] - starts[index]) % len(bits) or len(bits) for index in range(len(starts)))


def regression_audit(corpus: dict[str, object]) -> dict[str, object]:
    family_bits = [
        ("A=11101", A_BITS),
        ("B=1100", B_BITS),
        ("(110|111)^*", "110111" * 8),
        ("A^1B^1", A_BITS + B_BITS),
        ("A^2B^3", A_BITS * 2 + B_BITS * 3),
        ("2^m-1", "1" * 12 + "0"),
        ("8^m-5", "111001" * 4),
    ]
    families = []
    for name, bits in family_bits:
        exponents = bit_exponents(bits)
        q, L = len(exponents), sum(exponents)
        families.append([name, bits, list(exponents), q, L, str(2**L - 3**q)])
    mismatch = corpus["smallest_rotation_mismatch"]
    if mismatch["odd_rational_orbit"] != [["5", "7"], ["11", "7"]]:
        raise AssertionError("rotation mismatch regression")
    return {
        "format": "collatz-phase27-regressions-v1",
        "mandatory_adversarial_families": families,
        "rotation_alignment_obstruction": mismatch,
        "negative_and_nonprimitive_scope": "Phase 26 negative cycles and trivial powers remain boundary controls; no positive-state separation or asymptotic cycle conclusion is applied to them.",
        "phase26_scalar_obstruction": {
            "left": str(75**7),
            "right": str(3 * 64**7),
            "left_exceeds_right": 75**7 > 3 * 64**7,
        },
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase27-asymptotic-theory-v1",
        "claims": {
            "EXT17": {"status": "EXTERNAL_THEOREM", "statement": "Matveev's explicit real two-logarithm theorem gives the recorded fixed-2,3 multiplicative lower bound."},
            "P162": {"status": "VERIFIED_THEOREM", "statement": "A polynomial lower bound on lambda(1-lambda) forces liminf A_*/q^(2/3)>=((log_2 3)^2/2)^(1/3)."},
            "P163": {"status": "VERIFIED_THEOREM", "statement": "The noncritical positive-cycle branch has an internal polynomial multiplier gap and therefore the P162 area dispersion."},
            "P164": {"status": "VERIFIED_THEOREM", "statement": "Using EXT17 on the critical branch, every primitive positive nontrivial cycle sequence has the P162 area liminf."},
            "P165": {"status": "VERIFIED_THEOREM", "statement": "Arbitrary-gcd support controls Hamming complexity, h_*<=s_*, and polynomial gap forces liminf s_*/sqrt(q)>=sqrt(log_2 3/2); P163/P164 make this global for positive cycles."},
            "E39": {"status": "VERIFIED_FINITE", "statement": "The declared q<=8 corpus, exact envelopes, synthetic profiles, alignment obstruction, and mandatory controls are independently reproducible."},
            "NG36": {"status": "REFUTED", "statement": "Least-value and discrepancy-minimum rotations universally coincide for positive rational affine cycles."},
            "H133": {"status": "OPEN", "statement": "Asymptotic area and support growth do not exclude arbitrary-area primitive positive cycles."},
        },
        "polynomial_gap_area": {
            "hypothesis": "lambda*(1-lambda)>=c*q^(-kappa) with fixed c>0 and kappa>=0",
            "master": "log_2(3)*q < (A+1)*(sqrt(2A)+(kappa+1)*log_2(q)+O(1))",
            "conclusion": "liminf A/q^(2/3)>=((log_2(3))^2/2)^(1/3)",
        },
        "noncritical_gap": "lambda*(1-lambda)>=(1/2)*exp(-1/3)*(1+q)^(-1/9)",
        "critical_gap": "EXT17 implies lambda*(1-lambda)>q^(-K)/(4*12^K), K=1564920000",
        "support": {
            "definition": "s_*=#{0<=j<q:a_j>0}",
            "hamming": "H(v_a,v_0)<=2s_*",
            "factor": "p_cyc(n)<=(2s_*+1)n+1",
            "height": "h_*<=s_*",
            "conclusion": "liminf s_*/sqrt(q)>=sqrt(log_2(3)/2)",
        },
        "rotation_boundary": "P133 uses a least-value rotation; P156 uses a discrepancy-minimum rotation. They cannot be identified without an additional theorem.",
        "structural_phase_diagram": {
            "tall": "h_* comparable to or above q^(1/3), forcing a descent through every level and valuation-one transitions at baseline-2 positions",
            "diffuse": "h_*=o(q^(1/3)), so area of order q^(2/3) must be spread over many lower defects",
            "status": "strategy split only; neither branch is excluded",
        },
        "dependencies": {
            "P162": ["P156", "P157"],
            "P163": ["P134", "P156", "P157", "E28"],
            "P164": ["P162", "P163", "EXT17"],
            "P165": ["P125", "P151", "P156", "P157", "P163", "P164"],
        },
        "what_this_result_does_not_prove": "No area is excluded asymptotically, neither tall nor diffuse profiles are eliminated, positive-integral rotation alignment is open, and Collatz is not proved.",
        "proves_collatz": False,
    }


def obstruction_report(corpus: dict[str, object], envelopes: dict[str, object]) -> str:
    mismatch = corpus["smallest_rotation_mismatch"]
    return f"""# Phase 27 obstruction report

## Rotation alignment is false for positive rational shadows

The lexicographically first complete-corpus obstruction is

```text
q={mismatch['q']}, L={mismatch['L']}, e={tuple(mismatch['exponents'])}
odd orbit: 5/7 -> 11/7 -> 5/7
least-value offset: 0
discrepancy-minimum offset: 1
```

Thus P133's least-value coordinates cannot be combined with P156's
nonnegative reduced profile without an additional alignment theorem.  The
counterexample is positive rational but not integral; alignment for a
hypothetical positive integer cycle remains open.

## The critical external constant is effective but impractical

Matveev's theorem is specialized with the safe integer majorant
`K={MATVEEV_K}`.  It proves a polynomial gap and hence the asymptotic theorem,
but its finite scalar envelope is far weaker than Phase 26's EXT05 bound in
the ranges of practical interest.  Effectiveness is not practical exclusion.

## The exponent boundary is structural, not a cycle construction

The synthetic tall and diffuse rows are valid reduced profiles only.  They
show why P156/P157 plus a polynomial gap naturally meet at area exponent
`2/3` and support exponent `1/2`; they are not positive integer cycles and do
not prove those exponents optimal for actual Collatz cycles.

## What this result does not prove

Phase 27 does not exclude critical area six, large noncritical area, either
tall or diffuse profiles, arbitrary primitive positive cycles, nonperiodic
counterexamples, or the Collatz conjecture. `proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    arguments = parser.parse_args()
    arguments.artifact_dir.mkdir(parents=True, exist_ok=True)

    corpus = corpus_audit()
    envelopes = envelope_audit()
    synthetic = synthetic_audit()
    regressions = regression_audit(corpus)
    theory = theory_artifact()
    if {key: value["status"] for key, value in theory["claims"].items()} != EXPECTED_CLAIMS:
        raise AssertionError("claim status map")

    write_json(arguments.artifact_dir / "phase27_theory.json", theory)
    write_json(arguments.artifact_dir / "phase27_cycle_corpus.json", corpus)
    write_json(arguments.artifact_dir / "phase27_envelopes.json", envelopes)
    write_json(arguments.artifact_dir / "phase27_synthetic_profiles.json", synthetic)
    write_json(arguments.artifact_dir / "phase27_regressions.json", regressions)
    (arguments.artifact_dir / "phase27_obstruction_report.md").write_text(
        obstruction_report(corpus, envelopes), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "critical_K": MATVEEV_K,
                "finite_classes": corpus["counts"]["cyclic_classes"],
                "rotation_mismatch": corpus["smallest_rotation_mismatch"]["exponents"],
                "proves_collatz": False,
                "valid": True,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
