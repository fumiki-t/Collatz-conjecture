#!/usr/bin/env python3
"""Generate exact Phase 29 arc-nonvanishing evidence.

The supplied note is treated as an untrusted proposal.  Decisions use only
integers, Fractions, and outward rational logarithm enclosures.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Iterator, Sequence

try:
    from src.phase24_search import (
        area_three_profiles,
        area_two_profiles,
        critical_length,
        exponents_of_profile,
        reduced_polynomial,
    )
    from src.phase26_search import (
        compositions,
        cyclic_class,
        minimum_rotations,
        primitive,
        rational_odd_orbit,
        reduced_profile,
    )
    from src.phase28_search import (
        isolated_profile,
        near_extremal_profile,
        plateau_profile,
        seven_grid_time_profile,
        tall_profile,
    )
except ModuleNotFoundError:
    from phase24_search import (  # type: ignore
        area_three_profiles,
        area_two_profiles,
        critical_length,
        exponents_of_profile,
        reduced_polynomial,
    )
    from phase26_search import (  # type: ignore
        compositions,
        cyclic_class,
        minimum_rotations,
        primitive,
        rational_odd_orbit,
        reduced_profile,
    )
    from phase28_search import (  # type: ignore
        isolated_profile,
        near_extremal_profile,
        plateau_profile,
        seven_grid_time_profile,
        tall_profile,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


PROFILE_Q_MAXIMUM = 8
AREA_TWO_CRITICAL_Q_MAXIMUM = 60
AREA_TWO_NONCRITICAL_L_MAXIMUM = 21
AREA_THREE_CRITICAL_Q_MAXIMUM = 100
V = 300_000
VX = 2075 * 2**60
MATVEEV_K = 1_564_920_000
EXPECTED_CLAIMS = {
    "P173": "VERIFIED_THEOREM",
    "P174": "VERIFIED_THEOREM",
    "P175": "VERIFIED_THEOREM",
    "P176": "VERIFIED_THEOREM",
    "P177": "VERIFIED_THEOREM",
    "P178": "CONDITIONAL",
    "E41": "VERIFIED_FINITE",
    "H172": "OPEN",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def update_hash(digest: object, value: object) -> None:
    digest.update(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def v2(value: int) -> int:
    value = abs(value)
    if not value:
        raise ValueError("v2(0)")
    return (value & -value).bit_length() - 1


def outward_dyadic(lower: Fraction, upper: Fraction, bits: int = 320) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    low = lower.numerator * scale // lower.denominator
    high = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(low, scale), Fraction(high, scale)


def log_interval(value: Fraction, terms: int = 192) -> tuple[Fraction, Fraction]:
    if value <= 1:
        raise ValueError("log interval requires x>1")
    z = (value - 1) / (value + 1)
    z2 = z * z
    term = z
    total = Fraction(0)
    for index in range(terms):
        total += term / (2 * index + 1)
        term *= z2
    lower = 2 * total
    upper = lower + 2 * term / ((2 * terms + 1) * (1 - z2))
    return outward_dyadic(lower, upper)


def time_to_residue_profile(q: int, L: int, time_profile: Sequence[int]) -> tuple[int, ...]:
    if len(time_profile) != q or math.gcd(q, L) != 1:
        raise ValueError("coprime time profile required")
    result = [-1] * q
    for time, value in enumerate(time_profile):
        result[(-L * time) % q] = value
    if min(result) < 0 or result[0] != 0:
        raise AssertionError("time/residue profile conversion")
    return tuple(result)


def residue_to_time_profile(q: int, L: int, profile: Sequence[int]) -> tuple[int, ...]:
    return tuple(profile[(-L * time) % q] for time in range(q))


def e0(q: int, L: int, time: int) -> int:
    return (L * time + (-L * time) % q) // q


def coefficient_identity(q: int, L: int, time_profile: Sequence[int]) -> dict[str, object]:
    residue = time_to_residue_profile(q, L, time_profile)
    coefficients = reduced_polynomial(residue)
    u = pow(L, -1, q)
    c = (L * u - 1) // q
    if coefficients[0] != 2 ** (time_profile[u] + 1) - 1:
        raise AssertionError("endpoint coefficient identity")
    for time in range(1, q):
        index = (-L * time) % q
        if coefficients[index] != 2 ** time_profile[(time + u) % q] - 2 ** time_profile[time]:
            raise AssertionError("coefficient transport identity")
        if e0(q, L, time + u) - e0(q, L, time) != c:
            raise AssertionError("baseline translation identity")
    return {
        "u": u,
        "c": c,
        "residue_profile": residue,
        "coefficients": coefficients,
    }


def cut_indices(coefficients: Sequence[int], q: int, L: int) -> tuple[list[int], dict[int, int], list[int], int]:
    support = [index for index, coefficient in enumerate(coefficients) if coefficient]
    inverse = pow(L, -1, q)
    residues = {index: (-index * inverse) % q for index in support}
    points = sorted(residues.values())
    gaps = [
        points[(index + 1) % len(points)] + (q if index + 1 == len(points) else 0) - point
        for index, point in enumerate(points)
    ]
    largest = max(gaps)
    return support, residues, [index for index, gap in enumerate(gaps) if gap == largest], largest


def arc_nonvanishing(q: int, L: int, time_profile: Sequence[int]) -> dict[str, object]:
    identity = coefficient_identity(q, L, time_profile)
    coefficients = tuple(identity["coefficients"])
    support, residues, cuts, largest = cut_indices(coefficients, q, L)
    points = sorted(residues.values())
    u = int(identity["u"])

    def weight(time: int) -> int:
        if time % q == 0:
            return e0(q, L, time)
        return e0(q, L, time) + min(time_profile[time % q], time_profile[(time + u) % q])

    rows: list[object] = []
    for cut in cuts:
        start = points[(cut + 1) % len(points)]
        lifts = {index: point if point >= start else point + q for index, point in residues.items()}
        A = {index: (L * lifts[index] + index) // q for index in support}
        if any(A[index] != e0(q, L, lifts[index]) for index in support):
            raise AssertionError("arc baseline exponent")
        A_min = min(A.values())
        b_max = max(lifts.values())
        R = sum(
            coefficients[index] * 2 ** (A[index] - A_min) * 3 ** (b_max - lifts[index])
            for index in support
        )
        if not R:
            raise AssertionError("automatic arc nonvanishing")
        term_weights = []
        for index in support:
            time = lifts[index]
            expected = weight(time)
            if A[index] + v2(coefficients[index]) != expected:
                raise AssertionError("coefficient valuation identity")
            term_weights.append(expected)
        if len(set(term_weights)) != len(term_weights):
            raise AssertionError("distinct arc valuations")
        for time in range(start - 1, start + q + 1):
            if not weight(time + 1) > weight(time):
                raise AssertionError("global valuation monotonicity")
        predicted = min(term_weights) - A_min
        if v2(R) != predicted:
            raise AssertionError("exact arc valuation")
        rows.append(
            [
                start,
                q - largest,
                1 if R > 0 else -1,
                abs(R).bit_length(),
                v2(R),
                min(term_weights),
                A_min,
                stable_hash(str(abs(R))),
            ]
        )
    return {
        "support_count": len(support),
        "l1": sum(abs(value) for value in coefficients),
        "largest_gap": largest,
        "largest_gap_ties": len(cuts),
        "cut_rows": rows,
        "coefficient_digest_sha256": stable_hash(coefficients),
    }


def finite_arc_audit() -> dict[str, object]:
    counts = {
        "critical_area_two_profiles": 0,
        "noncritical_area_two_profiles": 0,
        "critical_area_three_profiles": 0,
        "largest_gap_tie_profiles": 0,
        "largest_gap_cuts_checked": 0,
        "nonzero_arc_checks": 0,
        "valuation_checks": 0,
    }
    digest = hashlib.sha256()
    samples: list[object] = []

    def scan(q: int, L: int, profile: Sequence[int], bucket: str) -> None:
        counts[bucket] += 1
        coefficients = reduced_polynomial(profile)
        _, _, cuts, largest = cut_indices(coefficients, q, L)
        if len(cuts) <= 1:
            update_hash(digest, [q, L, sum(profile), largest, 1])
            return
        time_profile = residue_to_time_profile(q, L, profile)
        data = arc_nonvanishing(q, L, time_profile)
        if data["largest_gap_ties"] != len(cuts):
            raise AssertionError("tie enumeration")
        counts["largest_gap_tie_profiles"] += 1
        counts["largest_gap_cuts_checked"] += len(cuts)
        counts["nonzero_arc_checks"] += len(cuts)
        counts["valuation_checks"] += len(cuts)
        row = [q, L, sum(profile), stable_hash(tuple(profile)), data]
        update_hash(digest, row)
        if len(samples) < 8:
            samples.append(row)

    for q in range(1, AREA_TWO_CRITICAL_Q_MAXIMUM + 1):
        L = critical_length(q)
        if q < L < 2 * q and math.gcd(q, L) == 1:
            for profile in area_two_profiles(q, L):
                scan(q, L, profile, "critical_area_two_profiles")
    for L in range(2, AREA_TWO_NONCRITICAL_L_MAXIMUM + 1):
        for q in range(1, L):
            if q < L < 2 * q and 2**L > 3**q and L != critical_length(q) and math.gcd(q, L) == 1:
                for profile in area_two_profiles(q, L):
                    scan(q, L, profile, "noncritical_area_two_profiles")
    for q in range(1, AREA_THREE_CRITICAL_Q_MAXIMUM + 1):
        L = critical_length(q)
        if q < L < 2 * q and math.gcd(q, L) == 1:
            for profile in area_three_profiles(q, L):
                scan(q, L, profile, "critical_area_three_profiles")

    if counts["critical_area_two_profiles"] != 7057 or counts["noncritical_area_two_profiles"] != 204:
        raise AssertionError("Phase 24 area-two count")
    if counts["critical_area_three_profiles"] != 521154:
        raise AssertionError("Phase 24 area-three count")
    return {
        "format": "collatz-phase29-finite-arc-audit-v1",
        "scope": "Every largest-gap tie in the E36 area-two/area-three ranges; non-ties are counted but theorem-level nonvanishing is not inferred from the scan.",
        "counts": counts,
        "tie_row_digest_sha256": digest.hexdigest(),
        "samples": samples,
        "proves_collatz": False,
    }


def coprime_corpus_and_synthetic() -> dict[str, object]:
    counts = {
        "coprime_classes": 0,
        "minimum_rotations": 0,
        "coefficient_identity_checks": 0,
        "largest_gap_cuts_checked": 0,
        "synthetic_profiles": 0,
    }
    rows: list[object] = []
    for q in range(1, PROFILE_Q_MAXIMUM + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q or math.gcd(q, L) != 1:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(L, q)}):
                counts["coprime_classes"] += 1
                for rotated in minimum_rotations(values):
                    data = reduced_profile(rotated)
                    profile = tuple(data["profile"][:-1])
                    audit = arc_nonvanishing(q, L, profile)
                    counts["minimum_rotations"] += 1
                    counts["coefficient_identity_checks"] += q
                    counts["largest_gap_cuts_checked"] += audit["largest_gap_ties"]
                    rows.append([q, L, list(rotated), data["area"], audit])

    q7, L7, p7 = seven_grid_time_profile()
    synthetic = [
        ("tall", 125, 199, tall_profile(125, 199, 5)),
        ("plateau", 125, 199, plateau_profile(125, 199, 5)),
        ("isolated", 125, 199, isolated_profile(125, 199, 20)),
        ("near-extremal", 1331, 2110, near_extremal_profile(1331, 2110, 9, 124)),
        ("seven-grid", q7, L7, p7),
    ]
    synthetic_rows = []
    for name, q, L, profile in synthetic:
        if len(profile) != q + 1 or profile[-1] != 0:
            raise AssertionError("synthetic closed profile")
        audit = arc_nonvanishing(q, L, profile[:-1])
        counts["synthetic_profiles"] += 1
        counts["largest_gap_cuts_checked"] += audit["largest_gap_ties"]
        synthetic_rows.append([name, q, L, sum(profile), max(profile), audit])
    return {
        "format": "collatz-phase29-coprime-corpus-v1",
        "scope": "Complete positive-D coprime cyclic classes through q<=8 plus five exact legal synthetic profiles.",
        "counts": counts,
        "row_digest_sha256": stable_hash(rows),
        "synthetic_rows": synthetic_rows,
        "stored_rows": "digest only; the independent verifier regenerates the complete corpus",
        "proves_collatz": False,
    }


def suffix_coefficient(base: Sequence[int], end: int, length: int) -> Fraction:
    q = len(base)
    exponent_sum = sum(base[(end - offset) % q] for offset in range(1, length + 1))
    return Fraction(3**length, 2**exponent_sum)


def state_bound_audit() -> dict[str, object]:
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "maximum_state_checks": 0,
        "suffix_coefficient_checks": 0,
    }
    digest = hashlib.sha256()
    equality_samples: list[object] = []
    for q in range(1, PROFILE_Q_MAXIMUM + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(L, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                counts["noncoprime_classes"] += int(math.gcd(q, L) > 1)
                for rotated in minimum_rotations(values):
                    counts["minimum_rotations"] += 1
                    data = reduced_profile(rotated)
                    profile = tuple(data["profile"][:-1])
                    base = tuple(data["baseline"])
                    orbit = rational_odd_orbit(rotated)[:-1]
                    q0 = int(data["q0"])
                    L0 = int(data["L0"])
                    lambda0 = Fraction(3**q0, 2**L0)
                    maximum = max(profile)
                    for time, height in enumerate(profile):
                        if height != maximum:
                            continue
                        S0 = sum((suffix_coefficient(base, time, r) for r in range(1, q0 + 1)), Fraction())
                        bound = S0 / (3 * (1 - lambda0))
                        rough = Fraction(2 * q0, 3 * (1 - lambda0))
                        if not orbit[time] <= bound < rough:
                            raise AssertionError("reduced-slope state bound")
                        for r in range(1, q0 + 1):
                            actual = suffix_coefficient(rotated, time, r)
                            baseline = suffix_coefficient(base, time, r)
                            if actual > baseline or baseline >= 2:
                                raise AssertionError("suffix domination")
                            counts["suffix_coefficient_checks"] += 1
                        row = [q, L, list(rotated), time, data["d"], q0, encode_fraction(orbit[time]), encode_fraction(S0), encode_fraction(bound), encode_fraction(rough)]
                        update_hash(digest, row)
                        if orbit[time] == bound and len(equality_samples) < 5:
                            equality_samples.append(row)
                        counts["maximum_state_checks"] += 1
    return {
        "format": "collatz-phase29-state-bounds-v1",
        "scope": "All positive rational affine cyclic classes through q<=8; ordinary E28/X02 consequences apply only to positive integer cycles.",
        "counts": counts,
        "row_digest_sha256": digest.hexdigest(),
        "equality_samples": equality_samples,
        "bound": "x_t<=S_t^(0)/(3(1-lambda0))<2q0/(3(1-lambda0)) at every maximum reduced height",
        "proves_collatz": False,
    }


def farey_row(name: str, height: int, q_star: int, left: tuple[int, int], right: tuple[int, int]) -> dict[str, object]:
    left_f = Fraction(*left)
    right_f = Fraction(*right)
    if right[0] * left[1] - left[0] * right[1] != 1 or left[1] + right[1] != q_star:
        raise AssertionError("Farey neighbors")
    ln2 = log_interval(Fraction(2))
    ln3 = log_interval(Fraction(3))
    epsilon = Fraction(2 * q_star, 3 * height)
    if not 0 < epsilon < 1:
        raise AssertionError("Farey epsilon domain")
    log_ratio = log_interval(1 / (1 - epsilon))
    alpha_low = ln3[0] / ln2[1]
    alpha_high = ln3[1] / ln2[0]
    psi_low = log_ratio[0] / (q_star * ln2[1])
    psi_high = log_ratio[1] / (q_star * ln2[0])
    if not left_f < alpha_low <= alpha_high < right_f:
        raise AssertionError("log2(3) Farey enclosure")
    if not alpha_high + psi_high < right_f:
        raise AssertionError("reduced denominator margin")
    return {
        "name": name,
        "height": str(height),
        "q_star": str(q_star),
        "left_neighbor": [str(left[0]), str(left[1])],
        "right_neighbor": [str(right[0]), str(right[1])],
        "determinant": 1,
        "denominator_sum": str(q_star),
        "epsilon": encode_fraction(epsilon),
        "alpha_interval": [encode_fraction(alpha_low), encode_fraction(alpha_high)],
        "psi_interval": [encode_fraction(psi_low), encode_fraction(psi_high)],
        "upper_margin": encode_fraction(right_f - alpha_high - psi_high),
        "certified": True,
    }


def farey_audit() -> dict[str, object]:
    internal = farey_row("E28", V, 971, (1054, 665), (485, 306))
    external = farey_row(
        "X02",
        VX,
        72_057_431_991,
        (103_768_467_013, 65_470_613_321),
        (10_439_860_591, 6_586_818_670),
    )
    return {
        "format": "collatz-phase29-farey-certificates-v1",
        "log_terms": 192,
        "monotonicity": "psi_V(q)=sum_(n>=1)(2/(3V))^n q^(n-1)/(n ln 2), hence increasing on 0<2q<3V",
        "rows": [internal, external],
        "claims": {"P177": "VERIFIED_THEOREM", "P178": "CONDITIONAL"},
        "external_boundary": "Only the second row uses X02; E28 is internally verified finite input.",
        "proves_collatz": False,
    }


def bit_exponents(bits: str) -> tuple[int, ...]:
    starts = [index for index, bit in enumerate(bits) if bit == "1"]
    return tuple((starts[(i + 1) % len(starts)] - start) % len(bits) or len(bits) for i, start in enumerate(starts))


def regression_audit() -> dict[str, object]:
    A = "11101"
    B = "1100"
    families = [
        ("2^m-1", "1" * 12 + "0"),
        ("8^m-5", "111001" * 4),
        ("(110|111)^*", "110111" * 8),
        ("A=11101", A),
        ("B=1100", B),
        ("A^1B^1", A + B),
        ("A^2B^3", A * 2 + B * 3),
    ]
    rows = []
    for name, bits in families:
        exponents = bit_exponents(bits)
        q, L = len(exponents), sum(exponents)
        applicable = 2**L > 3**q and math.gcd(q, L) == 1
        arc = None
        if applicable:
            minima = minimum_rotations(exponents)
            data = reduced_profile(minima[0])
            arc = arc_nonvanishing(q, L, tuple(data["profile"][:-1]))
        rows.append([name, bits, list(exponents), math.gcd(q, L), applicable, arc])
    return {
        "format": "collatz-phase29-regressions-v1",
        "mandatory_families": rows,
        "named_controls": {
            "trivial_positive": {"exponents": [2], "scope": "D=1 boundary and equality control for P176"},
            "negative_q2": {"exponents": [1, 2], "source": -5, "scope": "positivity failure"},
            "negative_q7": {"exponents": [1, 1, 1, 2, 1, 1, 4], "source": -17, "scope": "positivity failure"},
            "NG34": {"q": 63322, "L": 100363, "roots": [9046, 18092, 27138]},
            "NG35": {"left": str(75**7), "right": str(3 * 64**7), "left_exceeds_right": 75**7 > 3 * 64**7},
            "NG36": {"exponents": [1, 3], "orbit": [["5", "7"], ["11", "7"]], "integral": False},
            "NG37": {"exponents": [3, 1, 1], "finite_bound_equality": 1},
            "NG38": {"exponents": [3, 1], "polynomial": [3, -1], "endpoint_correction": 1},
        },
        "tamper_boundaries": ["X02 must remain conditional", "EXT17 must remain external", "proves_collatz must remain false"],
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase29-arc-nonvanishing-theory-v1",
        "claims": {
            "P173": {"status": "VERIFIED_THEOREM", "statement": "Every P147 circular cut of every valid coprime reduced profile has a nonzero arc integer, with its exact 2-adic valuation determined by the unique least transport weight."},
            "P174": {"status": "VERIFIED_THEOREM", "statement": "Every integral coprime profile obeys the exact critical and noncritical sparse-arc resonance inequalities."},
            "P175": {"status": "VERIFIED_THEOREM", "statement": "For every fixed area A, only finitely many coprime primitive positive cycle profiles can have area at most A; the critical branch uses EXT17."},
            "P176": {"status": "VERIFIED_THEOREM", "statement": "At a maximum reduced height in every positive rational affine cycle, x_t<=S_t^(0)/(3(1-lambda0))<2q0/(3(1-lambda0))."},
            "P177": {"status": "VERIFIED_THEOREM", "statement": "Every primitive positive nontrivial integer cycle has reduced odd period q0>=971, using E28."},
            "P178": {"status": "CONDITIONAL", "statement": "Assuming X02, every primitive positive nontrivial integer cycle has q0>=72057431991."},
            "E41": {"status": "VERIFIED_FINITE", "statement": "The declared arc ties, coprime corpus, all-gcd state corpus, synthetic profiles, Farey boxes, and regressions are independently reproducible."},
            "H172": {"status": "OPEN", "statement": "Growing-area coprime coefficient height and full-D noncoprime arithmetic still prevent cycle exclusion."},
            "H133": {"status": "OPEN", "statement": "Phase 29 does not exclude arbitrary-area positive cycles."},
        },
        "dependencies": {
            "P173": ["P135", "P147", "P156", "P171"],
            "P174": ["P147", "P173", "EXT17"],
            "P175": ["P150", "P173", "P174", "EXT17"],
            "P176": ["P156"],
            "P177": ["P176", "E28"],
            "P178": ["P176", "X02"],
        },
        "automatic_nonvanishing": "W_t=min(E_t,E_(t+u)-c) off qZ, W_(kq)=kL; W_t is strictly increasing, so every arc sum has one least 2-adic valuation.",
        "critical_resonance": "3^ceil(q/M)<4*C*(12q)^K, K=1564920000",
        "noncritical_resonance": "2^(L*ceil(q/M)/q)<4*C",
        "state_bound": "x_t<=S_t^(0)/(3(1-lambda0))<2q0/(3(1-lambda0))",
        "external_boundary": "EXT17 is used only for the critical resonance/fixed-area branch; X02 is used only by conditional P178.",
        "proves_collatz": False,
        "what_this_result_does_not_prove": "No growing-area coprime exclusion, full-D noncoprime resultant, nonperiodic branch exclusion, or Collatz proof follows.",
    }


def obstruction_report(arc: dict[str, object], state: dict[str, object]) -> str:
    counts = arc["counts"]
    state_counts = state["counts"]
    return f"""# Phase 29 obstruction report

## Surviving theorem

Every coprime P147 cut is automatically nonzero. The finite audit rebuilds
{counts['largest_gap_tie_profiles']:,} tie profiles and
{counts['largest_gap_cuts_checked']:,} tied largest-gap cuts in the complete
E36 area-two/area-three ranges, with zero cancellation or valuation failures.

## Remaining coprime obstruction

For growing area, the support saving `ceil(q/M)` competes with the coefficient
height `C`. P173 removes cancellation as an excuse but does not prove that
`3^ceil(q/M)` or `2^(L ceil(q/M)/q)` dominates `C`.

## Remaining noncoprime obstruction

P176 is checked at {state_counts['maximum_state_checks']:,} maximum-height
states across the q<=8 all-gcd rational corpus. It forces a close reduced
slope for an integer cycle, but P140 still supplies only the reduced divisor
`D_0`; no full-`D` cyclotomic/Fourier resultant is proved.

## What this result does not prove

The exact arc theorem, finite scans, and reduced-denominator bounds do not
exclude arbitrary-area positive cycles, any nonperiodic counterexample branch,
or the Collatz conjecture. `proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)

    theory = theory_artifact()
    arc = finite_arc_audit()
    corpus = coprime_corpus_and_synthetic()
    state = state_bound_audit()
    farey = farey_audit()
    regressions = regression_audit()
    report = obstruction_report(arc, state)

    write_json(args.artifact_dir / "phase29_theory.json", theory)
    write_json(args.artifact_dir / "phase29_arc_audit.json", arc)
    write_json(args.artifact_dir / "phase29_coprime_corpus.json", corpus)
    write_json(args.artifact_dir / "phase29_state_bounds.json", state)
    write_json(args.artifact_dir / "phase29_farey_certificates.json", farey)
    write_json(args.artifact_dir / "phase29_regressions.json", regressions)
    (args.artifact_dir / "phase29_obstruction_report.md").write_text(report, encoding="utf-8")

    print(json.dumps({
        "valid": True,
        "claims": EXPECTED_CLAIMS,
        "tie_cuts": arc["counts"]["largest_gap_cuts_checked"],
        "coprime_classes": corpus["counts"]["coprime_classes"],
        "state_checks": state["counts"]["maximum_state_checks"],
        "proves_collatz": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
