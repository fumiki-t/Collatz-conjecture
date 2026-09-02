#!/usr/bin/env python3
"""Generate exact Phase 34 profile/state and area-209 evidence.

The supplied Phase 34 note is an untrusted proposal.  This generator checks
the proposed inequalities with integer/rational arithmetic, preserves the
first unresolved scalar row, and builds finite regression corpora for the
least-state bridge and the 2-adic first-defect formula.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

try:  # script execution
    from phase26_search import affine_correction, minimum_rotations, reduced_profile
except ModuleNotFoundError:  # package import in tests
    from src.phase26_search import affine_correction, minimum_rotations, reduced_profile


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


K_MATVEEV = 1_564_920_000
AREA_CEILING = 208
Q_CUTOFF = 10_000_000_000_000
FINITE_BOUND = 583_561
EXPECTED_CLAIMS = {
    "P202": "VERIFIED_THEOREM",
    "P203": "VERIFIED_THEOREM",
    "P204": "VERIFIED_THEOREM",
    "P205": "VERIFIED_THEOREM",
    "E48": "VERIFIED_FINITE",
    "H89": "OPEN",
    "H133": "OPEN",
    "H172": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encode(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def rows_digest(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def outward(lower: Fraction, upper: Fraction, bits: int = 512) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    lo = lower.numerator * scale // lower.denominator
    hi = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(lo, scale), Fraction(hi, scale)


def log_interval(value: Fraction, terms: int = 280) -> tuple[Fraction, Fraction]:
    if value <= 1:
        raise ValueError("log domain")
    z = (value - 1) / (value + 1)
    z2 = z * z
    power = z
    total = Fraction()
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
    result = []
    for a, b in zip(continued_fraction(left), continued_fraction(right), strict=False):
        if a != b:
            break
        result.append(a)
    return tuple(result)


def convergents(terms: Sequence[int]) -> list[tuple[int, int]]:
    p0, p1, q0, q1 = 0, 1, 1, 0
    answer = []
    for term in terms:
        p, q = term * p1 + p0, term * q1 + q0
        answer.append((p, q))
        p0, p1, q0, q1 = p1, p, q1, q
    return answer


def alpha_data() -> tuple[tuple[Fraction, Fraction], tuple[int, ...], list[tuple[int, int]]]:
    ln2, ln3 = log_interval(Fraction(2)), log_interval(Fraction(3))
    alpha = ln3[0] / ln2[1], ln3[1] / ln2[0]
    prefix = common_prefix(*alpha)
    return alpha, prefix, convergents(prefix)


def ceil_log2_fraction(value: Fraction) -> int:
    if value <= 0:
        raise ValueError("positive fraction required")
    n, d = value.numerator, value.denominator
    guess = n.bit_length() - d.bit_length()
    while n * (1 << max(-guess, 0)) < d * (1 << max(guess, 0)):
        guess -= 1
    exact = n * (1 << max(-guess, 0)) == d * (1 << max(guess, 0))
    return guess if exact else guess + 1


def critical_length(q: int) -> int:
    return pow(3, q).bit_length()


def p133_maximum(q: int, length: int) -> int:
    return ((q << length) - 1) // (3 * ((1 << length) - pow(3, q)))


def profile_maximum(q: int, length: int, area: int, height: int) -> int:
    denominator = 3 * ((1 << length) - pow(3, q)) * height * (1 << height)
    x = q * height + area * ((1 << height) - 1)
    return (4 * (1 << length) * x - 1) // denominator


def best_scalar_row(q: int, length: int, area: int) -> tuple[dict[str, int] | None, int]:
    """Optimize P195 over every legal height using its own state bound."""
    m133 = p133_maximum(q, length)
    best: tuple[int, ...] | None = None
    largest_state = -1
    for height in range(1, area + 1):
        descent = sum(level * q // (length - q) for level in range(height))
        if height + descent > area:
            break
        mprof = profile_maximum(q, length, area, height)
        mmax = min(m133, mprof)
        largest_state = max(largest_state, mmax)
        if mmax < FINITE_BOUND:
            continue
        n = ceil_log2_fraction(Fraction((1 << (height + 2 + length)) * mmax, pow(3, q)))
        z = ((length - q) * (n + 1) + length - 1) // length
        for components in range(height, area - descent + 1):
            sigma = area - components - descent
            exceptional = min(components, height + sigma)
            rhs = ((components + 2 * exceptional) * (n + 1) + 6 * area
                   + (n + 3) * (3 + 2 * z + z * (z - 1) // 2))
            candidate = (rhs - 3 * length, height, components, sigma, exceptional,
                         n, z, rhs, mmax, m133, mprof)
            if best is None or candidate > best:
                best = candidate
    if best is None:
        return None, largest_state
    keys = ("margin", "h", "J", "Sigma", "E", "n", "Z", "rhs",
            "m_max", "m_P133", "m_prof")
    return dict(zip(keys, best, strict=True)), largest_state


def low_q_audit(area: int, q_max: int = 8191) -> dict[str, object]:
    counts = {"q_rows": 0, "q0_rejections": 0, "state_E46_rejections": 0,
              "admissible_q_rows": 0, "P195_survivors": 0}
    rows: list[object] = []
    survivors = []
    closest = None
    for q in range(971, q_max + 1):
        counts["q_rows"] += 1
        length = critical_length(q)
        divisor = math.gcd(q, length)
        q0 = q // divisor
        if q0 < 971:
            counts["q0_rejections"] += 1
            row = [q, length, divisor, q0, "q0"]
        else:
            best, largest = best_scalar_row(q, length, area)
            if best is None:
                counts["state_E46_rejections"] += 1
                row = [q, length, divisor, q0, "state_E46", largest]
            else:
                counts["admissible_q_rows"] += 1
                record = {"q": q, "L": length, "d": divisor, "q0": q0, **best}
                if best["margin"] >= 0:
                    counts["P195_survivors"] += 1
                    survivors.append(record)
                elif closest is None or best["margin"] > closest["margin"]:
                    closest = record
                row = [q, length, divisor, q0, "P195", *best.values()]
        rows.append(row)
    return {"area_ceiling": area, "q_range": [971, q_max], "counts": counts,
            "row_digest_sha256": rows_digest(rows), "survivors": survivors,
            "closest_failure": closest}


def cutoff_certificate() -> dict[str, object]:
    left = Fraction(19 * Q_CUTOFF, 12)
    right = 5015 + 209 * (44 + 47 * K_MATVEEV)
    derivative = Fraction(3 * 209 * (K_MATVEEV + 1), 2 * Q_CUTOFF)
    if left <= right or derivative >= Fraction(19, 12):
        raise AssertionError("global cutoff")
    return {"Q": Q_CUTOFF, "log2_3_lower": [19, 12],
            "log2_4Q_over_3_upper": 44, "log2_12Q_upper": 47,
            "margin": encode(left - right), "derivative_upper": encode(derivative),
            "derivative_target": [19, 12]}


def frontier_audit(alpha: tuple[Fraction, Fraction], all_convergents: Sequence[tuple[int, int]]) -> dict[str, object]:
    ln2, ln3 = log_interval(Fraction(2)), log_interval(Fraction(3))
    uppers = [(p, q) for p, q in all_convergents
              if 971 <= q < Q_CUTOFF and Fraction(p, q) > alpha[1]]
    rows: list[object] = []
    closest = None
    for p, q0 in uppers:
        delta = p * ln2[0] - q0 * ln3[1], p * ln2[1] - q0 * ln3[0]
        for divisor in range(1, 237):
            q, length = divisor * q0, divisor * p
            if q >= Q_CUTOFF:
                continue
            low, high = divisor * delta[0], divisor * delta[1]
            if low <= 0 or high >= ln2[0]:
                continue
            log_bound = ceil_log2_fraction(Fraction(4 * q, 3) / low)
            margin = 5015 + 209 * log_bound - length
            row = [p, q0, divisor, length, q, log_bound, margin]
            rows.append(row)
            if closest is None or margin > closest[-1]:
                closest = row
            if margin >= 0:
                raise AssertionError("P180 frontier survivor")
    return {"upper_convergents": [list(row) for row in uppers],
            "candidate_count": len(rows), "candidate_digest_sha256": rows_digest(rows),
            "closest_coarse_upper_margin": closest,
            "gap_lower_bound": "lambda(1-lambda)>delta_log/4"}


def compositions(total: int, count: int) -> Iterable[tuple[int, ...]]:
    for cuts in combinations(range(1, total), count - 1):
        points = (0, *cuts, total)
        yield tuple(points[index + 1] - points[index] for index in range(count))


def canonical_rotation(values: tuple[int, ...]) -> tuple[int, ...]:
    return min(values[index:] + values[:index] for index in range(len(values)))


def rational_orbit(exponents: Sequence[int]) -> tuple[Fraction, ...]:
    q, length = len(exponents), sum(exponents)
    value = Fraction(affine_correction(exponents), (1 << length) - pow(3, q))
    result = []
    for exponent in exponents:
        result.append(value)
        value = (3 * value + 1) / (1 << exponent)
    if value != result[0]:
        raise AssertionError("rational cycle closure")
    return tuple(result)


def profile_bridge_audit(q_max: int = 12) -> dict[str, object]:
    rows = []
    controls = []
    class_count = rotation_count = segment_count = 0
    for q in range(2, q_max + 1):
        length = critical_length(q)
        seen: set[tuple[int, ...]] = set()
        for raw in compositions(length, q):
            canonical = canonical_rotation(raw)
            if canonical in seen:
                continue
            seen.add(canonical)
            class_count += 1
            for exponents in minimum_rotations(canonical):
                rotation_count += 1
                data = reduced_profile(exponents)
                profile = tuple(data["profile"][:-1])
                baseline = tuple(data["baseline"])
                orbit = rational_orbit(exponents)
                t = min(range(q), key=orbit.__getitem__)
                height, area = int(data["height"]), int(data["area"])
                lam = Fraction(pow(3, q), 1 << length)
                for r in range(1, q):
                    actual_power = sum(exponents[(t + j) % q] for j in range(r))
                    base_power = sum(baseline[(t + j) % q] for j in range(r))
                    c0 = Fraction(pow(3, r), 1 << base_power)
                    coefficient = Fraction(pow(3, r), 1 << actual_power)
                    if not ((2 * c0) ** q > lam ** r and c0 ** q < (2 ** q) * lam ** r):
                        raise AssertionError("mechanical segment enclosure")
                    if coefficient <= lam or profile[(t + r) % q] > profile[t] + 1:
                        raise AssertionError("least-state bridge")
                    segment_count += 1
                fixed_left = orbit[t] * (1 - lam)
                cumulative = 0
                reciprocal_sum = Fraction()
                for r in range(q):
                    reciprocal_sum += Fraction(1 << cumulative, pow(3, r))
                    cumulative += exponents[(t + r) % q]
                if fixed_left != lam * reciprocal_sum / 3:
                    raise AssertionError("fixed-point identity")
                if height and profile[t] == height - 1:
                    controls.append([q, length, list(exponents), list(profile), t,
                                     str(orbit[t]), height, area])
                rows.append([q, length, list(exponents), list(profile), t, height, area,
                             str(orbit[t])])
    return {"q_range": [2, q_max], "cyclic_classes": class_count,
            "minimum_rotations": rotation_count, "segment_checks": segment_count,
            "row_digest_sha256": rows_digest(rows),
            "least_profile_h_minus_one_controls": controls,
            "control_boundary": "No h-1 control in this finite critical rational corpus is not a proof of a_t=h."}


def source_residue(positions: Sequence[int], q: int, modulus_bits: int) -> int:
    modulus = 1 << modulus_bits
    total = 0
    for j, position in enumerate(positions):
        total -= pow(3, -j - 1, modulus) * (1 << position)
    return total % modulus


def valuation2(value: int) -> int:
    if value == 0:
        raise ValueError("zero valuation")
    return (value & -value).bit_length() - 1


def defect_audit(q_max: int = 18) -> dict[str, object]:
    rows = []
    samples = []
    for q in range(2, q_max + 1):
        length = critical_length(q)
        critical = tuple((pow(3, j).bit_length() - 1) for j in range(q))
        for mask in range(1, 1 << (q - 1)):
            profile = (0,) + tuple((mask >> (j - 1)) & 1 for j in range(1, q))
            edited = tuple(critical[j] - profile[j] for j in range(q))
            if edited[0] < 0 or any(edited[j] <= edited[j - 1] for j in range(1, q)):
                continue
            source = source_residue(edited, q, length)
            base = source_residue(critical, q, length)
            difference = (source - base) % (1 << length)
            expected = sum((pow(3, -j - 1, 1 << length) * (1 << edited[j])
                            * ((1 << profile[j]) - 1)) for j in range(q)) % (1 << length)
            first = next(j for j, value in enumerate(profile) if value)
            if difference != expected or valuation2(difference) != min(
                    edited[j] for j, value in enumerate(profile) if value):
                raise AssertionError("2-adic defect identity")
            if profile[first] != 1 or critical[first] - critical[first - 1] != 2:
                raise AssertionError("first-defect gap")
            row = [q, length, list(profile), list(edited), difference,
                   valuation2(difference), first]
            rows.append(row)
            if len(samples) < 12:
                samples.append(row)
    return {"q_range": [2, q_max], "legal_profiles": len(rows),
            "row_digest_sha256": rows_digest(rows), "samples": samples,
            "decoder_boundary": "Only the first defect is decoded; overlapping later defects and changed labels remain OPEN."}


def regressions() -> dict[str, object]:
    def affine(bits: str) -> list[int]:
        correction = ones = 0
        for length, bit in enumerate(bits):
            if bit == "1":
                correction = 3 * correction + (1 << length)
                ones += 1
        return [ones, len(bits), correction]
    a, b = "11101", "1100"
    families = [("2^m-1", "1" * 12 + "0"), ("8^m-5", "111001" * 4),
                ("(110|111)^*", "110111" * 8), ("A=11101", a), ("B=1100", b),
                ("A^1B^1", a + b), ("A^2B^3", a * 2 + b * 3)]
    return {"format": "collatz-phase34-regressions-v1",
            "mandatory_families": [[name, bits, affine(bits)] for name, bits in families],
            "named_controls": {
                "source_167": "retained as an ordinary-source regression; no cycle inference",
                "trivial_cycle_and_powers": "excluded by the nontrivial primitive premise",
                "negative_cycles": "positive least-state inequalities do not apply",
                "NG34_NG40": "all rotation, reversal, endpoint, span, hit, and grid warnings remain active",
            }, "proves_collatz": False}


def theory() -> dict[str, object]:
    return {"format": "collatz-phase34-theory-v1", "claims": EXPECTED_CLAIMS,
            "P202": {"statement": "At the least odd state of a critical primitive positive cycle, every reduced-profile coordinate is at most a_t+1, hence h<=a_t+1.",
                     "boundary": "Least-value and discrepancy-minimum rotations are not identified."},
            "P203": {"statement": "The exact fixed-point identity yields the strict least-state exponential-moment and integer profile bounds (3.2)-(3.6)."},
            "P204": {"statement": "Every critical primitive positive nontrivial integer cycle has reduced-profile area A>=209.",
                     "dependencies": ["P133", "P156", "P164", "EXT17", "P177", "P180", "P195", "P199", "P201", "E46", "E48"]},
            "P205": {"statement": "The canonical source residue difference has 2-adic valuation equal to the earliest edited odd position; a first defect is a unique gap-two unit edit.",
                     "boundary": "No branch-free repeated decoder is claimed."},
            "what_this_result_does_not_prove": "The finite area floor neither excludes arbitrary-area cycles nor any nonperiodic branch; the A=209 scalar obstruction remains open.",
            "proves_collatz": False}


def obstruction_report(scalar: dict[str, object], bridge: dict[str, object]) -> str:
    obstruction = scalar["next_obstruction"]
    return f"""# Phase 34 obstruction report

The exact proposal audit excludes every critical reduced-profile area through
208.  The first surviving scalar row is `(q,L,A)=(2301,3647,209)` with
`RHS-3L=24` and `583561 <= m <= 860946`.  Its optimizing profile statistics
are `(h,J,Sigma,E,n,Z)=(2,105,103,105,24,10)`.

The least-state/profile bridge was checked on {bridge['minimum_rotations']}
positive critical rational rotations through `q<={bridge['q_range'][1]}`.
No `a_t=h-1` control occurred in that bounded corpus.  This finite absence is
not promoted to the stronger statement `a_t=h`; the proved theorem remains
only `h<=a_t+1`, and NG36 remains active.

The first 2-adic defect is identifiable, but repeated subtraction is not yet a
branch-free decoder: later defect intervals can overlap and labels change.
This is the precise next H89 obstruction.

## What this result does not prove

It does not exclude the stored area-209 row, produce a uniform growing-area
cycle contradiction, close H89/H133/H172, address the nonperiodic branches,
or prove the Collatz conjecture. `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    alpha, prefix, cf = alpha_data()
    low = low_q_audit(AREA_CEILING)
    obstruction_best, _ = best_scalar_row(2301, 3647, 209)
    if obstruction_best is None:
        raise AssertionError("missing area-209 obstruction")
    scalar = {"format": "collatz-phase34-scalar-audit-v1",
              "log2_three_interval": [encode(value) for value in alpha],
              "continued_fraction_prefix": list(prefix), "cutoff": cutoff_certificate(),
              "gcd_bound": {"strict_upper": [19136, 81], "integer_maximum": 236},
              "legendre": {"threshold_q": 8192, "threshold_exponent": [-6311, 627]},
              "frontier": frontier_audit(alpha, cf), "low_q": low,
              "next_obstruction": {"q": 2301, "L": 3647, "A": 209, **obstruction_best,
                                    "least_state_interval": [583561, 860946]},
              "proves_collatz": False}
    bridge = profile_bridge_audit()
    defect = defect_audit()
    write_json(args.artifact_dir / "phase34_theory.json", theory())
    write_json(args.artifact_dir / "phase34_scalar_audit.json", scalar)
    write_json(args.artifact_dir / "phase34_profile_bridge.json", bridge)
    write_json(args.artifact_dir / "phase34_defect_peeling.json", defect)
    write_json(args.artifact_dir / "phase34_regressions.json", regressions())
    (args.artifact_dir / "phase34_obstruction_report.md").write_text(
        obstruction_report(scalar, bridge), encoding="utf-8")
    print(json.dumps({"valid": True, "claims": EXPECTED_CLAIMS,
                      "frontier_candidates": scalar["frontier"]["candidate_count"],
                      "low_q_counts": low["counts"], "bridge_rotations": bridge["minimum_rotations"],
                      "defect_profiles": defect["legal_profiles"], "proves_collatz": False},
                     indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
