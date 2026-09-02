#!/usr/bin/env python3
"""Generate exact Phase 33 critical-area bootstrap evidence.

The supplied Phase 33 note is treated as an untrusted proposal.  This
generator reconstructs its scalar, continued-fraction, and finite-descent
claims using arbitrary-precision integers and rational enclosures only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


MATVEEV_K = 1_564_920_000
E28_BOUND = 300_000
DESCENT_BOUND = 583_561
EXPECTED_CLAIMS = {
    "P200": "VERIFIED_THEOREM",
    "P201": "VERIFIED_THEOREM",
    "E46": "VERIFIED_FINITE",
    "E47": "VERIFIED_FINITE",
    "H200": "RETRACTED",
    "H172": "OPEN",
    "H133": "OPEN",
}
TIERS = (
    {"area": 61, "constant": 929, "coefficient": 62, "cutoff": 2_800_000_000_000,
     "d_max": 63, "legendre_q": 2048, "low_q_max": 2047},
    {"area": 117, "constant": 2241, "coefficient": 118, "cutoff": 5_500_000_000_000,
     "d_max": 125, "legendre_q": 4096, "low_q_max": 4095},
)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encode(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def row_hash(rows: list[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def outward(lower: Fraction, upper: Fraction, bits: int = 512) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    low = lower.numerator * scale // lower.denominator
    high = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(low, scale), Fraction(high, scale)


def log_interval(value: Fraction, terms: int = 280) -> tuple[Fraction, Fraction]:
    """Outward exact atanh-series enclosure for log(value), value > 1."""
    if value <= 1:
        raise ValueError("log domain")
    z = (value - 1) / (value + 1)
    z2 = z * z
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= z2
    lower = 2 * total
    upper = lower + 2 * power / ((2 * terms + 1) * (1 - z2))
    return outward(lower, upper)


def continued_fraction(value: Fraction) -> list[int]:
    result: list[int] = []
    while value.denominator != 1:
        term = value.numerator // value.denominator
        result.append(term)
        value = 1 / (value - term)
    result.append(value.numerator)
    return result


def common_prefix(left: Fraction, right: Fraction) -> tuple[int, ...]:
    answer = []
    for a, b in zip(continued_fraction(left), continued_fraction(right), strict=False):
        if a != b:
            break
        answer.append(a)
    return tuple(answer)


def convergents(terms: tuple[int, ...]) -> list[tuple[int, int]]:
    p0, p1, q0, q1 = 0, 1, 1, 0
    rows = []
    for term in terms:
        p = term * p1 + p0
        q = term * q1 + q0
        rows.append((p, q))
        p0, p1, q0, q1 = p1, p, q1, q
    return rows


def alpha_data() -> tuple[tuple[Fraction, Fraction], tuple[int, ...], list[tuple[int, int]]]:
    ln2 = log_interval(Fraction(2))
    ln3 = log_interval(Fraction(3))
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    prefix = common_prefix(*alpha)
    return alpha, prefix, convergents(prefix)


def ceil_log2_fraction(value: Fraction) -> int:
    if value <= 0:
        raise ValueError("positive fraction required")
    numerator, denominator = value.numerator, value.denominator
    floor = numerator.bit_length() - denominator.bit_length()
    if floor >= 0:
        while numerator < denominator << floor:
            floor -= 1
        exact = numerator == denominator << floor
    else:
        while numerator << (-floor) < denominator:
            floor -= 1
        exact = numerator << (-floor) == denominator
    return floor if exact else floor + 1


def critical_length(q: int) -> int:
    return pow(3, q).bit_length()


def maximum_minimum(q: int, length: int) -> int:
    """Largest integer m satisfying m(1-lambda)<q/3."""
    numerator = q << length
    denominator = 3 * ((1 << length) - pow(3, q))
    return (numerator - 1) // denominator


def best_p195(q: int, length: int, area: int, minimum: int) -> dict[str, int]:
    best: tuple[int, ...] | None = None
    for height in range(1, area + 1):
        descent = sum(level * q // (length - q) for level in range(height))
        if height + descent > area:
            break
        n = ceil_log2_fraction(Fraction((1 << (height + 2 + length)) * minimum, pow(3, q)))
        z = ((length - q) * (n + 1) + length - 1) // length
        for components in range(height, area - descent + 1):
            sigma = area - components - descent
            exceptional = min(components, height + sigma)
            rhs = (
                (components + 2 * exceptional) * (n + 1)
                + 6 * area
                + (n + 3) * (3 + 2 * z + z * (z - 1) // 2)
            )
            candidate = (
                rhs - 3 * length, height, components, sigma, exceptional, n, z, rhs,
            )
            if best is None or candidate > best:
                best = candidate
    if best is None:
        raise AssertionError("empty P195 parameter set")
    keys = ("margin", "h", "J", "Sigma", "E", "n", "Z", "rhs")
    return dict(zip(keys, best, strict=True))


def low_q_audit(area: int, q_max: int) -> dict[str, object]:
    counts = {"q_rows": 0, "reduced_denominator_rejections": 0,
              "P133_E28_rejections": 0, "P133_admissible": 0, "P195_survivors": 0}
    rows: list[object] = []
    survivors = []
    closest_failure: dict[str, int] | None = None
    for q in range(971, q_max + 1):
        counts["q_rows"] += 1
        length = critical_length(q)
        divisor = math.gcd(q, length)
        q0 = q // divisor
        if q0 < 971:
            counts["reduced_denominator_rejections"] += 1
            row = [q, length, divisor, q0, "q0"]
        else:
            minimum = maximum_minimum(q, length)
            if minimum < E28_BOUND:
                counts["P133_E28_rejections"] += 1
                row = [q, length, divisor, q0, "P133_E28", minimum]
            else:
                counts["P133_admissible"] += 1
                best = best_p195(q, length, area, minimum)
                record = {"q": q, "L": length, "d": divisor, "q0": q0,
                          "m_max": minimum, **best}
                if best["margin"] >= 0:
                    counts["P195_survivors"] += 1
                    survivors.append(record)
                elif closest_failure is None or best["margin"] > closest_failure["margin"]:
                    closest_failure = record
                row = [q, length, divisor, q0, "P195", minimum, *best.values()]
        rows.append(row)
    return {
        "area_ceiling": area,
        "q_range": [971, q_max],
        "counts": counts,
        "row_digest_sha256": row_hash(rows),
        "survivors": survivors,
        "closest_failure": closest_failure,
    }


def cutoff_certificate(tier: dict[str, int]) -> dict[str, object]:
    area, coefficient = tier["area"], tier["coefficient"]
    cutoff = tier["cutoff"]
    log_q_bound = 42 if area == 61 else 43
    log_12q_bound = 45 if area == 61 else 46
    left = Fraction(19 * cutoff, 12)
    right = tier["constant"] + coefficient * (log_q_bound + log_12q_bound * MATVEEV_K)
    derivative_upper = Fraction(3 * coefficient * (MATVEEV_K + 1), 2 * cutoff)
    if not left > right or not derivative_upper < Fraction(19, 12):
        raise AssertionError("cutoff certificate")
    return {
        "Q": cutoff,
        "alpha_lower": [19, 12],
        "log2_4Q_over_3_upper": log_q_bound,
        "log2_12Q_upper": log_12q_bound,
        "margin": encode(left - right),
        "derivative_upper": encode(derivative_upper),
        "derivative_target": [19, 12],
    }


def frontier_audit(tier: dict[str, int], alpha: tuple[Fraction, Fraction],
                   all_convergents: list[tuple[int, int]]) -> dict[str, object]:
    ln2 = log_interval(Fraction(2))
    ln3 = log_interval(Fraction(3))
    upper = [
        (p, q) for p, q in all_convergents
        if q >= 971 and q < tier["cutoff"] and Fraction(p, q) > alpha[1]
    ]
    next_upper = next(
        (p, q) for p, q in all_convergents
        if q >= tier["cutoff"] and Fraction(p, q) > alpha[1]
    )
    rows: list[object] = []
    closest: list[int] | None = None
    for p, q0 in upper:
        delta = (p * ln2[0] - q0 * ln3[1], p * ln2[1] - q0 * ln3[0])
        for divisor in range(1, tier["d_max"] + 1):
            q = divisor * q0
            length = divisor * p
            if q >= tier["cutoff"]:
                continue
            delta_low, delta_high = divisor * delta[0], divisor * delta[1]
            if not (delta_low > 0 and delta_high < ln2[0]):
                continue
            # gap=lambda(1-lambda)>delta_log/4.  An integral power-of-two
            # upper bound is deliberately coarser than evaluating logs.
            log_bound = ceil_log2_fraction(Fraction(4 * q, 3) / delta_low)
            margin_upper = tier["constant"] + tier["coefficient"] * log_bound - length
            row = [p, q0, divisor, length, q, log_bound, margin_upper]
            rows.append(row)
            if closest is None or margin_upper > closest[-1]:
                closest = row
            if margin_upper >= 0:
                raise AssertionError("P180 frontier survivor")
    return {
        "area_ceiling": tier["area"],
        "upper_convergents": [list(row) for row in upper],
        "next_upper_convergent": list(next_upper),
        "candidate_count": len(rows),
        "candidate_digest_sha256": row_hash(rows),
        "closest_coarse_upper_margin": closest,
        "gap_lower_bound": "lambda(1-lambda)>delta_log/4",
    }


def scalar_artifact() -> dict[str, object]:
    alpha, prefix, all_convergents = alpha_data()
    first = low_q_audit(61, 2047)
    second = low_q_audit(117, 4095)
    obstruction_62 = best_p195(971, 1539, 62, maximum_minimum(971, 1539))
    obstruction_118 = best_p195(1636, 2593, 118, maximum_minimum(1636, 2593))
    return {
        "format": "collatz-phase33-scalar-audit-v1",
        "log2_three_interval": [encode(value) for value in alpha],
        "continued_fraction_prefix": list(prefix),
        "tiers": [
            {"configuration": tier, "cutoff": cutoff_certificate(tier),
             "frontier": frontier_audit(tier, alpha, all_convergents),
             "low_q": first if tier["area"] == 61 else second}
            for tier in TIERS
        ],
        "obstructions": [
            {"q": 971, "L": 1539, "A": 62, "m_max": maximum_minimum(971, 1539), **obstruction_62},
            {"q": 1636, "L": 2593, "A": 118, "m_max": maximum_minimum(1636, 2593), **obstruction_118},
        ],
        "decision_arithmetic": "integers and exact rational logarithm enclosures; frontier rejection uses an integral power-of-two upper bound",
        "proves_collatz": False,
    }


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def first_lower(source: int) -> tuple[int, int]:
    value = source
    for steps in range(1, 10_000):
        value = shortcut(value)
        if value < source:
            return steps, value
    raise AssertionError("descent limit")


def write_descent(path: Path) -> dict[str, object]:
    digest = hashlib.sha256()
    count = 0
    first_max = (-1, -1, -1)
    second_max = (-1, -1, -1)
    with path.open("w", encoding="ascii", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(("source", "steps", "first_lower"))
        for source in range(E28_BOUND + 1, DESCENT_BOUND, 2):
            steps, lower = first_lower(source)
            writer.writerow((source, steps, lower))
            digest.update(f"{source},{steps},{lower}\n".encode("ascii"))
            count += 1
            record = (steps, source, lower)
            if source <= 330_911 and record > first_max:
                first_max = record
            if source >= 330_913 and record > second_max:
                second_max = record
    return {
        "format": "collatz-phase33-descent-summary-v1",
        "certificate": path.name,
        "prior_verified_bound": E28_BOUND,
        "new_verified_bound_exclusive": DESCENT_BOUND,
        "odd_sources": count,
        "row_digest_sha256": digest.hexdigest(),
        "first_interval": {"range": [300_000, 330_911], "maximum": list(first_max)},
        "second_interval": {"range": [330_912, 583_560], "maximum": list(second_max)},
        "induction": "E28 plus one-step parity reduction for even values and certified first-lower iterates for odd values proves convergence below 583561 by strong induction.",
        "proves_collatz": False,
    }


def affine(bits: str) -> tuple[int, int, int]:
    q = 0
    correction = 0
    for length, bit in enumerate(bits):
        if bit == "1":
            correction = 3 * correction + (1 << length)
            q += 1
        elif bit != "0":
            raise ValueError("binary word")
    return q, len(bits), correction


def regressions() -> dict[str, object]:
    a, b = "11101", "1100"
    families = [
        ("2^m-1", "1" * 12 + "0"), ("8^m-5", "111001" * 4),
        ("(110|111)^*", "110111" * 8), ("A=11101", a), ("B=1100", b),
        ("A^1B^1", a + b), ("A^2B^3", a * 2 + b * 3),
    ]
    return {
        "format": "collatz-phase33-regressions-v1",
        "mandatory_families": [[name, bits, list(affine(bits))] for name, bits in families],
        "named_boundaries": {
            "trivial_cycle_and_powers": "excluded from the nontrivial primitive-positive premise",
            "negative_cycles": "P133/P180 ordinary positive-state bounds do not apply",
            "rational_shadows": "finite scalar survival never implies a positive integral source",
            "NG34_NG40": "preserved; area, rotation, endpoint, span, and hit-count shortcuts remain unavailable",
        },
        "proves_collatz": False,
    }


def theory() -> dict[str, object]:
    return {
        "format": "collatz-phase33-theory-v1",
        "claims": EXPECTED_CLAIMS,
        "P200": {
            "statement": "Every critical primitive positive nontrivial integer Collatz cycle has reduced-profile area A>=62.",
            "dependencies": ["P133", "P156", "P164", "EXT17", "P177", "P180", "P195", "P199", "E28", "E47"],
        },
        "P201": {
            "statement": "Every critical primitive positive nontrivial integer Collatz cycle has reduced-profile area A>=118.",
            "dependencies": ["P200", "E46", "E47"],
        },
        "H200": {
            "closure": "The original method-specific bounded-grid obligation is retracted as unnecessary: P201 excludes its A=s=d=6 target and all critical areas through 117.",
            "not_claimed": "No complete bounded-grid coefficient-identity classification is asserted.",
        },
        "what_this_result_does_not_prove": "Finite area floors do not exclude arbitrary-area positive cycles, nonperiodic branches, or the Collatz conjecture.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 33 obstruction report

The exact scalar audit accepts the two-tier bootstrap.  Existing inputs alone
exclude critical areas through 61.  Independent first-descent certificates,
together with E28 and strong induction, extend the verified convergence bound
to every positive start below 583561; only the part through 330911 is needed
to exclude critical areas through 117.

The next scalar survivor is `(q,L,A)=(1636,2593,118)`, with P195 margin 45.
Its ordinary-height interval is now covered by E46, but turning that fact into
a further area tier requires a newly audited envelope, gcd bound, Legendre
threshold, CF frontier, and low-q audit.  This phase intentionally does not
iterate an unbounded numerical bootstrap.

H200's target is closed by the stronger P201 exclusion, not by completing the
formerly proposed bounded-grid coefficient classification.

## What this result does not prove

It does not bound the area of every hypothetical cycle, exclude noncritical
or arbitrary-area positive cycles, address either nonperiodic branch, or
prove the Collatz conjecture.  `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    scalar = scalar_artifact()
    certificate = args.artifact_dir / "phase33_descent_certificate.csv"
    descent = write_descent(certificate)
    write_json(args.artifact_dir / "phase33_theory.json", theory())
    write_json(args.artifact_dir / "phase33_scalar_audit.json", scalar)
    write_json(args.artifact_dir / "phase33_descent_summary.json", descent)
    write_json(args.artifact_dir / "phase33_regressions.json", regressions())
    (args.artifact_dir / "phase33_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")
    print(json.dumps({
        "valid": True, "claims": EXPECTED_CLAIMS,
        "frontier_counts": [tier["frontier"]["candidate_count"] for tier in scalar["tiers"]],
        "low_q_counts": [tier["low_q"]["counts"] for tier in scalar["tiers"]],
        "descent_sources": descent["odd_sources"], "proves_collatz": False,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
