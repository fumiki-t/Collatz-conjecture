#!/usr/bin/env python3
"""Independent exact verifier for Phase 34 artifacts.

This verifier imports neither ``src`` nor the generator.  It reconstructs the
continued-fraction/scalar audit, the rational profile corpus, and the 2-adic
defect corpus using separately implemented arithmetic.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import sys
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


K = 1_564_920_000
Q = 10_000_000_000_000
BOUND = 583_561
CLAIMS = {"P202": "VERIFIED_THEOREM", "P203": "VERIFIED_THEOREM",
          "P204": "VERIFIED_THEOREM", "P205": "VERIFIED_THEOREM",
          "E48": "VERIFIED_FINITE", "H89": "OPEN", "H133": "OPEN", "H172": "OPEN"}


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_rows(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def pair(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def as_fraction(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        fail("fraction encoding")
    return Fraction(int(value[0]), int(value[1]))


def raw_log(value: Fraction, terms: int = 384) -> tuple[Fraction, Fraction]:
    if value <= 1:
        fail("log domain")
    z = (value - 1) / (value + 1)
    power = z
    total = Fraction()
    for index in range(terms):
        total += 2 * power / (2 * index + 1)
        power *= z * z
    return total, total + 2 * power / ((2 * terms + 1) * (1 - z * z))


def cf(value: Fraction) -> list[int]:
    answer = []
    while value.denominator > 1:
        quotient, remainder = divmod(value.numerator, value.denominator)
        answer.append(quotient)
        value = Fraction(value.denominator, remainder)
    answer.append(value.numerator)
    return answer


def shared_cf(left: Fraction, right: Fraction) -> tuple[int, ...]:
    answer = []
    for a, b in zip(cf(left), cf(right), strict=False):
        if a != b:
            break
        answer.append(a)
    return tuple(answer)


def convs(terms: Sequence[int]) -> list[tuple[int, int]]:
    p2, p1, q2, q1 = 0, 1, 1, 0
    result = []
    for term in terms:
        p, q = term * p1 + p2, term * q1 + q2
        result.append((p, q))
        p2, p1, q2, q1 = p1, p, q1, q
    return result


def ceil_log2(value: Fraction) -> int:
    n, d = value.numerator, value.denominator
    guess = n.bit_length() - d.bit_length()
    while n * 2 ** max(-guess, 0) < d * 2 ** max(guess, 0):
        guess -= 1
    return guess if n * 2 ** max(-guess, 0) == d * 2 ** max(guess, 0) else guess + 1


def critical(q: int) -> int:
    return (3 ** q).bit_length()


def m133(q: int, length: int) -> int:
    return (q * 2 ** length - 1) // (3 * (2 ** length - 3 ** q))


def mprofile(q: int, length: int, area: int, height: int) -> int:
    x = q * height + area * (2 ** height - 1)
    return (4 * 2 ** length * x - 1) // (3 * (2 ** length - 3 ** q) * height * 2 ** height)


def optimize(q: int, length: int, area: int) -> tuple[dict[str, int] | None, int]:
    p133 = m133(q, length)
    winner = None
    largest = -1
    for h in range(1, area + 1):
        base = sum((level * q) // (length - q) for level in range(h))
        if h + base > area:
            break
        prof = mprofile(q, length, area, h)
        state = min(p133, prof)
        largest = max(largest, state)
        if state < BOUND:
            continue
        n = ceil_log2(Fraction(2 ** (h + 2 + length) * state, 3 ** q))
        z = ((length - q) * (n + 1) + length - 1) // length
        for j in range(h, area - base + 1):
            sigma = area - j - base
            exceptional = min(j, h + sigma)
            rhs = ((j + 2 * exceptional) * (n + 1) + 6 * area
                   + (n + 3) * (3 + 2 * z + z * (z - 1) // 2))
            candidate = (rhs - 3 * length, h, j, sigma, exceptional, n, z,
                         rhs, state, p133, prof)
            if winner is None or candidate > winner:
                winner = candidate
    if winner is None:
        return None, largest
    names = ("margin", "h", "J", "Sigma", "E", "n", "Z", "rhs",
             "m_max", "m_P133", "m_prof")
    return dict(zip(names, winner, strict=True)), largest


def rebuild_low() -> dict[str, object]:
    counts = {"q_rows": 0, "q0_rejections": 0, "state_E46_rejections": 0,
              "admissible_q_rows": 0, "P195_survivors": 0}
    rows = []
    survivors = []
    closest = None
    for q in range(971, 8192):
        counts["q_rows"] += 1
        length = critical(q)
        divisor = math.gcd(q, length)
        reduced = q // divisor
        if reduced < 971:
            counts["q0_rejections"] += 1
            row = [q, length, divisor, reduced, "q0"]
        else:
            best, largest = optimize(q, length, 208)
            if best is None:
                counts["state_E46_rejections"] += 1
                row = [q, length, divisor, reduced, "state_E46", largest]
            else:
                counts["admissible_q_rows"] += 1
                record = {"q": q, "L": length, "d": divisor, "q0": reduced, **best}
                if best["margin"] >= 0:
                    counts["P195_survivors"] += 1
                    survivors.append(record)
                elif closest is None or best["margin"] > closest["margin"]:
                    closest = record
                row = [q, length, divisor, reduced, "P195", *best.values()]
        rows.append(row)
    return {"area_ceiling": 208, "q_range": [971, 8191], "counts": counts,
            "row_digest_sha256": digest_rows(rows), "survivors": survivors,
            "closest_failure": closest}


def rebuild_frontier(recorded_alpha: tuple[Fraction, Fraction], terms: Sequence[int]) -> dict[str, object]:
    ln2, ln3 = raw_log(Fraction(2)), raw_log(Fraction(3))
    uppers = [(p, q) for p, q in convs(terms) if 971 <= q < Q and Fraction(p, q) > recorded_alpha[1]]
    rows = []
    closest = None
    for p, q0 in uppers:
        low0, high0 = p * ln2[0] - q0 * ln3[1], p * ln2[1] - q0 * ln3[0]
        for divisor in range(1, 237):
            q, length = divisor * q0, divisor * p
            if q >= Q:
                continue
            low, high = divisor * low0, divisor * high0
            if low <= 0 or high >= ln2[0]:
                continue
            power = ceil_log2(Fraction(4 * q, 3) / low)
            margin = 5015 + 209 * power - length
            row = [p, q0, divisor, length, q, power, margin]
            rows.append(row)
            closest = row if closest is None or margin > closest[-1] else closest
            if margin >= 0:
                fail("frontier survivor")
    return {"upper_convergents": [list(row) for row in uppers], "candidate_count": len(rows),
            "candidate_digest_sha256": digest_rows(rows), "closest_coarse_upper_margin": closest,
            "gap_lower_bound": "lambda(1-lambda)>delta_log/4"}


def verify_scalar(stored: dict[str, object]) -> None:
    ln2, ln3 = raw_log(Fraction(2)), raw_log(Fraction(3))
    tight = ln3[0] / ln2[1], ln3[1] / ln2[0]
    recorded = tuple(as_fraction(item) for item in stored.get("log2_three_interval", []))
    if len(recorded) != 2 or not recorded[0] <= tight[0] <= tight[1] <= recorded[1]:
        fail("alpha interval")
    terms = shared_cf(*recorded)
    if list(terms) != stored.get("continued_fraction_prefix"):
        fail("continued fraction prefix")
    cutoff_margin = Fraction(19 * Q, 12) - (5015 + 209 * (44 + 47 * K))
    derivative = Fraction(3 * 209 * (K + 1), 2 * Q)
    cutoff = {"Q": Q, "log2_3_lower": [19, 12], "log2_4Q_over_3_upper": 44,
              "log2_12Q_upper": 47, "margin": pair(cutoff_margin),
              "derivative_upper": pair(derivative), "derivative_target": [19, 12]}
    if cutoff_margin <= 0 or derivative >= Fraction(19, 12) or stored.get("cutoff") != cutoff:
        fail("cutoff reconstruction")
    if stored.get("gcd_bound") != {"strict_upper": [19136, 81], "integer_maximum": 236}:
        fail("gcd bound")
    if stored.get("legendre") != {"threshold_q": 8192, "threshold_exponent": [-6311, 627]}:
        fail("Legendre threshold")
    if stored.get("frontier") != rebuild_frontier(recorded, terms):
        fail("frontier reconstruction")
    if stored.get("low_q") != rebuild_low():
        fail("low-q reconstruction")
    best, _ = optimize(2301, 3647, 209)
    expected = {"q": 2301, "L": 3647, "A": 209, **(best or {}),
                "least_state_interval": [583561, 860946]}
    if stored.get("next_obstruction") != expected or stored.get("proves_collatz") is not False:
        fail("area-209 obstruction")


def compositions(total: int, count: int) -> Iterable[tuple[int, ...]]:
    for cuts in combinations(range(1, total), count - 1):
        points = (0, *cuts, total)
        yield tuple(points[i + 1] - points[i] for i in range(count))


def rotations(values: tuple[int, ...]) -> Iterable[tuple[int, ...]]:
    return (values[i:] + values[:i] for i in range(len(values)))


def normalized_rotations(exponents: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, l0 = q // divisor, length // divisor
    answer = set()
    for rotated in rotations(exponents):
        height = 0
        minimum = 0
        for exponent in rotated:
            height += q0 * exponent - l0
            minimum = min(minimum, height)
        if minimum == 0:
            answer.add(rotated)
    if not answer:
        fail("minimum rotation")
    return tuple(sorted(answer))


def profile_data(exponents: tuple[int, ...]) -> tuple[tuple[int, ...], tuple[int, ...], int, int]:
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, l0 = q // divisor, length // divisor
    heights = [0]
    boundaries = [0]
    for exponent in exponents:
        heights.append(heights[-1] + q0 * exponent - l0)
        boundaries.append(boundaries[-1] + exponent)
    residues = [(-l0 * j) % q0 for j in range(q + 1)]
    profile = tuple((heights[j] - residues[j]) // q0 for j in range(q + 1))
    baseline_boundaries = tuple((l0 * j + residues[j]) // q0 for j in range(q + 1))
    baseline = tuple(baseline_boundaries[j + 1] - baseline_boundaries[j] for j in range(q))
    if any(boundaries[j] != baseline_boundaries[j] + profile[j] for j in range(q + 1)):
        fail("profile reconstruction")
    return profile[:-1], baseline, max(profile[:-1], default=0), sum(profile[:-1])


def correction(exponents: Sequence[int]) -> int:
    result = power = 0
    q = len(exponents)
    for j, exponent in enumerate(exponents):
        result += 3 ** (q - 1 - j) * 2 ** power
        power += exponent
    return result


def rebuild_bridge(qmax: int = 12) -> dict[str, object]:
    rows = []
    controls = []
    classes = rotations_count = segments = 0
    for q in range(2, qmax + 1):
        length = critical(q)
        seen = set()
        for raw in compositions(length, q):
            canonical = min(rotations(raw))
            if canonical in seen:
                continue
            seen.add(canonical)
            classes += 1
            for exponents in normalized_rotations(canonical):
                rotations_count += 1
                profile, baseline, height, area = profile_data(exponents)
                lam = Fraction(3 ** q, 2 ** length)
                value = Fraction(correction(exponents), 2 ** length - 3 ** q)
                orbit = []
                for exponent in exponents:
                    orbit.append(value)
                    value = (3 * value + 1) / 2 ** exponent
                if value != orbit[0]:
                    fail("rational closure")
                t = min(range(q), key=orbit.__getitem__)
                for r in range(1, q):
                    actual = sum(exponents[(t + j) % q] for j in range(r))
                    base = sum(baseline[(t + j) % q] for j in range(r))
                    c0 = Fraction(3 ** r, 2 ** base)
                    c = Fraction(3 ** r, 2 ** actual)
                    if not ((2 * c0) ** q > lam ** r and c0 ** q < 2 ** q * lam ** r):
                        fail("mechanical coefficient")
                    if c <= lam or profile[(t + r) % q] > profile[t] + 1:
                        fail("least-state bridge")
                    segments += 1
                left = orbit[t] * (1 - lam)
                reciprocal = Fraction()
                cumulative = 0
                for r in range(q):
                    reciprocal += Fraction(2 ** cumulative, 3 ** r)
                    cumulative += exponents[(t + r) % q]
                if left != lam * reciprocal / 3:
                    fail("fixed identity")
                if height and profile[t] == height - 1:
                    controls.append([q, length, list(exponents), list(profile), t,
                                     str(orbit[t]), height, area])
                rows.append([q, length, list(exponents), list(profile), t, height, area,
                             str(orbit[t])])
    return {"q_range": [2, qmax], "cyclic_classes": classes,
            "minimum_rotations": rotations_count, "segment_checks": segments,
            "row_digest_sha256": digest_rows(rows),
            "least_profile_h_minus_one_controls": controls,
            "control_boundary": "No h-1 control in this finite critical rational corpus is not a proof of a_t=h."}


def residue(positions: Sequence[int], bits: int) -> int:
    modulus = 2 ** bits
    return (-sum(pow(3, -j - 1, modulus) * 2 ** position
                 for j, position in enumerate(positions))) % modulus


def v2(value: int) -> int:
    return (value & -value).bit_length() - 1


def rebuild_defects(qmax: int = 18) -> dict[str, object]:
    rows = []
    samples = []
    for q in range(2, qmax + 1):
        length = critical(q)
        base_positions = tuple((3 ** j).bit_length() - 1 for j in range(q))
        for mask in range(1, 2 ** (q - 1)):
            profile = (0,) + tuple((mask >> (j - 1)) & 1 for j in range(1, q))
            positions = tuple(base_positions[j] - profile[j] for j in range(q))
            if positions[0] < 0 or any(positions[j] <= positions[j - 1] for j in range(1, q)):
                continue
            difference = (residue(positions, length) - residue(base_positions, length)) % 2 ** length
            expected = sum(pow(3, -j - 1, 2 ** length) * 2 ** positions[j]
                           * (2 ** profile[j] - 1) for j in range(q)) % 2 ** length
            first = next(j for j, item in enumerate(profile) if item)
            if difference != expected or v2(difference) != min(
                    positions[j] for j, item in enumerate(profile) if item):
                fail("defect identity")
            if profile[first] != 1 or base_positions[first] - base_positions[first - 1] != 2:
                fail("first defect")
            row = [q, length, list(profile), list(positions), difference, v2(difference), first]
            rows.append(row)
            if len(samples) < 12:
                samples.append(row)
    return {"q_range": [2, qmax], "legal_profiles": len(rows),
            "row_digest_sha256": digest_rows(rows), "samples": samples,
            "decoder_boundary": "Only the first defect is decoded; overlapping later defects and changed labels remain OPEN."}


def verify(directory: Path) -> dict[str, object]:
    names = ("phase34_theory.json", "phase34_scalar_audit.json", "phase34_profile_bridge.json",
             "phase34_defect_peeling.json", "phase34_regressions.json", "phase34_obstruction_report.md")
    paths = [directory / name for name in names]
    theory, scalar, bridge, defects, regressions = (load(paths[i]) for i in range(5))
    report = paths[5].read_text(encoding="utf-8")
    if not isinstance(theory, dict) or theory.get("claims") != CLAIMS or theory.get("proves_collatz") is not False:
        fail("theory artifact mismatch")
    if "not identified" not in theory.get("P202", {}).get("boundary", ""):
        fail("rotation boundary")
    if "branch-free" not in theory.get("P205", {}).get("boundary", ""):
        fail("decoder boundary")
    if not isinstance(scalar, dict) or scalar.get("format") != "collatz-phase34-scalar-audit-v1":
        fail("scalar artifact")
    verify_scalar(scalar)
    if bridge != rebuild_bridge():
        fail("profile bridge reconstruction")
    if defects != rebuild_defects():
        fail("defect reconstruction")
    required = {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}
    if not isinstance(regressions, dict) or regressions.get("proves_collatz") is not False:
        fail("regressions artifact")
    if {row[0] for row in regressions.get("mandatory_families", [])} != required:
        fail("mandatory families")
    for phrase in ("area-209", "not promoted", "does not prove", "proves_collatz=false"):
        if phrase not in report:
            fail("obstruction report boundary")
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    roots = {alias.name.split(".", 1)[0] for node in ast.walk(tree)
             if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".", 1)[0] for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module)
    generator_tail = "phase34_" + "search"
    if "src" in roots or any(name.endswith(generator_tail) for name in sys.modules):
        fail("generator independence")
    return {"format": "collatz-phase34-independent-verifier-v1", "valid": True,
            "generator_imported": False, "claims": CLAIMS,
            "frontier_candidates": scalar["frontier"]["candidate_count"],
            "low_q_rows": scalar["low_q"]["counts"]["q_rows"],
            "bridge_rotations": bridge["minimum_rotations"],
            "defect_profiles": defects["legal_profiles"],
            "verified_input_sha256": {path.name: digest_file(path) for path in paths},
            "independence": "separate log series, CF/scalar optimizer, profile reconstruction, and residue implementation",
            "what_this_result_does_not_prove": "A finite area floor does not exclude arbitrary-area cycles, nonperiodic orbits, or prove Collatz.",
            "proves_collatz": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        raise SystemExit(1) from exc
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
