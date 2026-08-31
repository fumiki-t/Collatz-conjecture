#!/usr/bin/env python3
"""Independent verifier for Phase 29 arc-nonvanishing artifacts."""

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


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


FILES = (
    "phase29_theory.json",
    "phase29_arc_audit.json",
    "phase29_coprime_corpus.json",
    "phase29_state_bounds.json",
    "phase29_farey_certificates.json",
    "phase29_regressions.json",
    "phase29_obstruction_report.md",
)
EXPECTED = {
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


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def update_hash(digest: object, value: object) -> None:
    digest.update(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def fraction(row: Sequence[str]) -> Fraction:
    return Fraction(int(row[0]), int(row[1]))


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def valuation_two(value: int) -> int:
    value = abs(value)
    if value == 0:
        fail("zero valuation")
    count = 0
    while value % 2 == 0:
        value //= 2
        count += 1
    return count


def compositions(total: int, parts: int, prefix: tuple[int, ...] = ()) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        if total >= 1:
            yield prefix + (total,)
        return
    for first in range(1, total - parts + 2):
        yield from compositions(total - first, parts - 1, prefix + (first,))


def rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    row = tuple(values)
    return tuple(row[offset:] + row[:offset] for offset in range(len(row)))


def cyclic_class(values: Sequence[int]) -> tuple[int, ...]:
    return min(rotations(values))


def primitive(values: Sequence[int]) -> bool:
    row = tuple(values)
    return all(row != row[:p] * (len(row) // p) for p in range(1, len(row)) if len(row) % p == 0)


def minimum_rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    row = tuple(values)
    q = len(row)
    L = sum(row)
    d = math.gcd(q, L)
    q0, L0 = q // d, L // d
    accepted = set()
    for rotated in rotations(row):
        height = 0
        minimum = 0
        for exponent in rotated:
            height += q0 * exponent - L0
            minimum = min(minimum, height)
        if height != 0:
            fail("height closure")
        if minimum == 0:
            accepted.add(rotated)
    if not accepted:
        fail("minimum rotation")
    return tuple(sorted(accepted))


def reduced_data(values: Sequence[int]) -> dict[str, object]:
    row = tuple(values)
    q, L = len(row), sum(row)
    d = math.gcd(q, L)
    q0, L0 = q // d, L // d
    heights = [0]
    for exponent in row:
        heights.append(heights[-1] + q0 * exponent - L0)
    residues = [(-L0 * index) % q0 for index in range(q + 1)]
    profile = []
    baseline_boundaries = []
    for index in range(q + 1):
        difference = heights[index] - residues[index]
        if difference % q0:
            fail("profile divisibility")
        profile.append(difference // q0)
        baseline_boundaries.append((L0 * index + residues[index]) // q0)
    baseline = tuple(baseline_boundaries[i + 1] - baseline_boundaries[i] for i in range(q))
    if min(profile) < 0 or profile[0] or profile[-1] or set(baseline) - {1, 2}:
        fail("reduced profile")
    return {"q": q, "L": L, "d": d, "q0": q0, "L0": L0, "profile": tuple(profile), "baseline": baseline}


def rational_orbit(values: Sequence[int]) -> tuple[Fraction, ...]:
    row = tuple(values)
    q, L = len(row), sum(row)
    B = 0
    power = 0
    for index, exponent in enumerate(row):
        B += 3 ** (q - 1 - index) * 2**power
        power += exponent
    D = 2**L - 3**q
    if D <= 0:
        fail("positive rational denominator")
    current = Fraction(B, D)
    orbit = [current]
    for exponent in row:
        current = (3 * current + 1) / 2**exponent
        orbit.append(current)
    if orbit[-1] != orbit[0] or min(orbit) <= 0:
        fail("rational orbit")
    return tuple(orbit)


def critical_length(q: int) -> int:
    return (3**q).bit_length()


def valid_profile(q: int, L: int, profile: Sequence[int]) -> bool:
    if len(profile) != q or profile[0] or min(profile) < 0 or math.gcd(q, L) != 1:
        return False
    m = L - q
    for r in range(m, q):
        if profile[r - m] < profile[r]:
            return False
    for r in range(m):
        if profile[r - m + q] < profile[r] - 1:
            return False
    return True


def area_two_profiles(q: int, L: int) -> Iterator[tuple[int, ...]]:
    if not (q < L < 2 * q) or math.gcd(q, L) != 1 or 2**L <= 3**q:
        return
    m = L - q
    for support in itertools.combinations(range(1, m), 2):
        row = [0] * q
        for index in support:
            row[index] = 1
        yield tuple(row)
    for root in range(1, q - m):
        row = [0] * q
        row[root] = row[root + m] = 1
        yield tuple(row)


def area_three_profiles(q: int, L: int) -> Iterator[tuple[int, ...]]:
    if not (q < L < 2 * q) or math.gcd(q, L) != 1 or 2**L <= 3**q:
        return
    m = L - q
    for support in itertools.combinations(range(1, m), 3):
        row = [0] * q
        for index in support:
            row[index] = 1
        yield tuple(row)
    for roots in itertools.combinations(range(1, m), 2):
        for parent in roots:
            if parent < q - m:
                row = [0] * q
                row[roots[0]] = row[roots[1]] = row[parent + m] = 1
                yield tuple(row)
    for root in range(1, max(1, 2 * m - q)):
        row = [0] * q
        row[root] = 2
        row[root + q - m] = 1
        yield tuple(row)


def coefficients(profile: Sequence[int]) -> tuple[int, ...]:
    q = len(profile)
    result = [0] * q
    result[0] = 1
    for index, height in enumerate(profile):
        value = 2**height - 1
        result[index] -= value
        result[(index + 1) % q] += value * (2 if index + 1 == q else 1)
    return tuple(result)


def e0(q: int, L: int, time: int) -> int:
    return (L * time + (-L * time) % q) // q


def time_profile_from_residue(q: int, L: int, profile: Sequence[int]) -> tuple[int, ...]:
    return tuple(profile[(-L * time) % q] for time in range(q))


def time_profile_to_coefficients(q: int, L: int, profile: Sequence[int]) -> tuple[int, ...]:
    residue = [-1] * q
    for time, height in enumerate(profile):
        residue[(-L * time) % q] = height
    if min(residue) < 0:
        fail("time profile permutation")
    return coefficients(residue)


def arc_data(q: int, L: int, time_profile: Sequence[int]) -> dict[str, object]:
    coeff = time_profile_to_coefficients(q, L, time_profile)
    u = pow(L, -1, q)
    c = (L * u - 1) // q
    if coeff[0] != 2 ** (time_profile[u] + 1) - 1:
        fail("endpoint identity")
    for time in range(1, q):
        if coeff[(-L * time) % q] != 2 ** time_profile[(time + u) % q] - 2 ** time_profile[time]:
            fail("coefficient identity")
        if e0(q, L, time + u) - e0(q, L, time) != c:
            fail("translation identity")

    support = [index for index, value in enumerate(coeff) if value]
    residues = {index: (-index * pow(L, -1, q)) % q for index in support}
    points = sorted(residues.values())
    gaps = [points[(i + 1) % len(points)] + (q if i + 1 == len(points) else 0) - point for i, point in enumerate(points)]
    largest = max(gaps)
    cuts = [i for i, gap in enumerate(gaps) if gap == largest]

    def weight(time: int) -> int:
        if time % q == 0:
            return e0(q, L, time)
        return e0(q, L, time) + min(time_profile[time % q], time_profile[(time + u) % q])

    rows = []
    for cut in cuts:
        start = points[(cut + 1) % len(points)]
        lifts = {index: point if point >= start else point + q for index, point in residues.items()}
        A = {index: (L * lifts[index] + index) // q for index in support}
        A_min = min(A.values())
        b_max = max(lifts.values())
        R = sum(coeff[index] * 2 ** (A[index] - A_min) * 3 ** (b_max - lifts[index]) for index in support)
        if R == 0:
            fail("arc cancellation")
        weights = []
        for index in support:
            time = lifts[index]
            if A[index] != e0(q, L, time):
                fail("baseline lift")
            expected = A[index] + valuation_two(coeff[index])
            if expected != weight(time):
                fail("term weight")
            weights.append(expected)
        if len(set(weights)) != len(weights):
            fail("weight collision")
        for time in range(start - 1, start + q + 1):
            if weight(time + 1) <= weight(time):
                fail("weight monotonicity")
        if valuation_two(R) != min(weights) - A_min:
            fail("arc valuation")
        rows.append([start, q - largest, 1 if R > 0 else -1, abs(R).bit_length(), valuation_two(R), min(weights), A_min, stable_hash(str(abs(R)))])
    return {
        "support_count": len(support),
        "l1": sum(abs(value) for value in coeff),
        "largest_gap": largest,
        "largest_gap_ties": len(cuts),
        "cut_rows": rows,
        "coefficient_digest_sha256": stable_hash(coeff),
    }


def verify_finite_arc(stored: dict[str, object]) -> dict[str, int]:
    counts = {key: 0 for key in (
        "critical_area_two_profiles", "noncritical_area_two_profiles", "critical_area_three_profiles",
        "largest_gap_tie_profiles", "largest_gap_cuts_checked", "nonzero_arc_checks", "valuation_checks",
    )}
    digest = hashlib.sha256()
    samples = []

    def scan(q: int, L: int, profile: Sequence[int], bucket: str) -> None:
        counts[bucket] += 1
        coeff = coefficients(profile)
        support = [index for index, value in enumerate(coeff) if value]
        points = sorted((-index * pow(L, -1, q)) % q for index in support)
        gaps = [points[(i + 1) % len(points)] + (q if i + 1 == len(points) else 0) - point for i, point in enumerate(points)]
        largest = max(gaps)
        ties = gaps.count(largest)
        if ties == 1:
            update_hash(digest, [q, L, sum(profile), largest, 1])
            return
        data = arc_data(q, L, time_profile_from_residue(q, L, profile))
        counts["largest_gap_tie_profiles"] += 1
        counts["largest_gap_cuts_checked"] += ties
        counts["nonzero_arc_checks"] += ties
        counts["valuation_checks"] += ties
        row = [q, L, sum(profile), stable_hash(tuple(profile)), data]
        update_hash(digest, row)
        if len(samples) < 8:
            samples.append(row)

    for q in range(1, 61):
        L = critical_length(q)
        if q < L < 2 * q and math.gcd(q, L) == 1:
            for profile in area_two_profiles(q, L):
                scan(q, L, profile, "critical_area_two_profiles")
    for L in range(2, 22):
        for q in range(1, L):
            if q < L < 2 * q and 2**L > 3**q and L != critical_length(q) and math.gcd(q, L) == 1:
                for profile in area_two_profiles(q, L):
                    scan(q, L, profile, "noncritical_area_two_profiles")
    for q in range(1, 101):
        L = critical_length(q)
        if q < L < 2 * q and math.gcd(q, L) == 1:
            for profile in area_three_profiles(q, L):
                if not valid_profile(q, L, profile):
                    fail("classified profile")
                scan(q, L, profile, "critical_area_three_profiles")
    if stored.get("counts") != counts or stored.get("tie_row_digest_sha256") != digest.hexdigest() or stored.get("samples") != samples:
        fail("finite arc artifact")
    return counts


def mechanical_baseline(q: int, L: int) -> tuple[int, ...]:
    return tuple((L * (i + 1) + (-L * (i + 1)) % q) // q - (L * i + (-L * i) % q) // q for i in range(q))


def synthetic_profiles() -> list[tuple[str, int, int, tuple[int, ...]]]:
    def tall(q: int, L: int, h: int) -> tuple[int, ...]:
        base = mechanical_baseline(q, L)
        p = [0, h]
        for i in range(1, q):
            p.append(p[-1] - 1 if p[-1] and base[i] == 2 else p[-1])
        return tuple(p[:-1])

    def plateau(q: int, L: int, h: int) -> tuple[int, ...]:
        base = mechanical_baseline(q, L)
        chosen = set([i for i, value in enumerate(base) if value == 2][-h:])
        p = [0]
        for i in range(q):
            p.append(h if i == 0 else p[-1] - 1 if i in chosen and p[-1] else p[-1])
        return tuple(p[:-1])

    def isolated(q: int, L: int, count: int) -> tuple[int, ...]:
        base = mechanical_baseline(q, L)
        p = [0]
        started = 0
        for i in range(q):
            if p[-1] and base[i] == 2:
                nxt = 0
            elif p[-1] == 0 and started < count and 2 in base[i + 1 :]:
                nxt = 1
                started += 1
            else:
                nxt = p[-1]
            p.append(nxt)
        return tuple(p[:-1])

    def near(q: int, L: int, h: int, J: int) -> tuple[int, ...]:
        base = mechanical_baseline(q, L)
        p = [0]
        left = J - h
        started = False
        for i in range(q):
            if not started:
                nxt, started = h, True
            elif p[-1] > 1 and base[i] == 2:
                nxt = p[-1] - 1
            elif p[-1] == 1 and base[i] == 2:
                nxt = 0
            elif p[-1] == 0 and left and 2 in base[i + 1 :]:
                nxt, left = 1, left - 1
            else:
                nxt = p[-1]
            p.append(nxt)
        return tuple(p[:-1])

    residue = [0] * 77
    for index in (11, 22, 33):
        residue[index] = 1
    seven = time_profile_from_residue(77, 123, residue)
    return [
        ("tall", 125, 199, tall(125, 199, 5)),
        ("plateau", 125, 199, plateau(125, 199, 5)),
        ("isolated", 125, 199, isolated(125, 199, 20)),
        ("near-extremal", 1331, 2110, near(1331, 2110, 9, 124)),
        ("seven-grid", 77, 123, seven),
    ]


def verify_coprime_corpus(stored: dict[str, object]) -> dict[str, int]:
    counts = {"coprime_classes": 0, "minimum_rotations": 0, "coefficient_identity_checks": 0, "largest_gap_cuts_checked": 0, "synthetic_profiles": 0}
    rows = []
    for q in range(1, 9):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q or math.gcd(q, L) != 1:
                continue
            classes = sorted({cyclic_class(row) for row in compositions(L, q)})
            for values in classes:
                counts["coprime_classes"] += 1
                for rotated in minimum_rotations(values):
                    data = reduced_data(rotated)
                    profile = tuple(data["profile"][:-1])
                    audit = arc_data(q, L, profile)
                    counts["minimum_rotations"] += 1
                    counts["coefficient_identity_checks"] += q
                    counts["largest_gap_cuts_checked"] += audit["largest_gap_ties"]
                    rows.append([q, L, list(rotated), sum(profile), audit])
    synthetic_rows = []
    for name, q, L, profile in synthetic_profiles():
        audit = arc_data(q, L, profile)
        counts["synthetic_profiles"] += 1
        counts["largest_gap_cuts_checked"] += audit["largest_gap_ties"]
        synthetic_rows.append([name, q, L, sum(profile), max(profile), audit])
    if stored.get("counts") != counts or stored.get("row_digest_sha256") != stable_hash(rows) or stored.get("synthetic_rows") != synthetic_rows:
        fail("coprime corpus artifact")
    return counts


def suffix(base: Sequence[int], end: int, length: int) -> Fraction:
    exponent = sum(base[(end - offset) % len(base)] for offset in range(1, length + 1))
    return Fraction(3**length, 2**exponent)


def verify_state_bounds(stored: dict[str, object]) -> dict[str, int]:
    counts = {"cyclic_classes": 0, "primitive_classes": 0, "noncoprime_classes": 0, "minimum_rotations": 0, "maximum_state_checks": 0, "suffix_coefficient_checks": 0}
    digest = hashlib.sha256()
    equality = []
    for q in range(1, 9):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(L, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                counts["noncoprime_classes"] += int(math.gcd(q, L) > 1)
                for rotated in minimum_rotations(values):
                    counts["minimum_rotations"] += 1
                    data = reduced_data(rotated)
                    profile = tuple(data["profile"][:-1])
                    base = tuple(data["baseline"])
                    orbit = rational_orbit(rotated)[:-1]
                    q0, L0 = int(data["q0"]), int(data["L0"])
                    lambda0 = Fraction(3**q0, 2**L0)
                    for time, height in enumerate(profile):
                        if height != max(profile):
                            continue
                        S0 = sum((suffix(base, time, r) for r in range(1, q0 + 1)), Fraction())
                        bound = S0 / (3 * (1 - lambda0))
                        rough = Fraction(2 * q0, 3 * (1 - lambda0))
                        if not orbit[time] <= bound < rough:
                            fail("state bound")
                        for r in range(1, q0 + 1):
                            if suffix(rotated, time, r) > suffix(base, time, r) or suffix(base, time, r) >= 2:
                                fail("suffix coefficient")
                            counts["suffix_coefficient_checks"] += 1
                        row = [q, L, list(rotated), time, data["d"], q0, encode_fraction(orbit[time]), encode_fraction(S0), encode_fraction(bound), encode_fraction(rough)]
                        update_hash(digest, row)
                        if orbit[time] == bound and len(equality) < 5:
                            equality.append(row)
                        counts["maximum_state_checks"] += 1
    if stored.get("counts") != counts or stored.get("row_digest_sha256") != digest.hexdigest() or stored.get("equality_samples") != equality:
        fail("state artifact")
    return counts


def outward(lower: Fraction, upper: Fraction, bits: int = 384) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    lo = lower.numerator * scale // lower.denominator
    hi = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(lo, scale), Fraction(hi, scale)


def log_box(value: Fraction, terms: int = 224) -> tuple[Fraction, Fraction]:
    z = (value - 1) / (value + 1)
    square = z * z
    term = z
    total = Fraction()
    for index in range(terms):
        total += term / (2 * index + 1)
        term *= square
    lo = 2 * total
    hi = lo + 2 * term / ((2 * terms + 1) * (1 - square))
    return outward(lo, hi)


def verify_farey(stored: dict[str, object]) -> None:
    if stored.get("log_terms") != 192 or stored.get("claims") != {"P177": "VERIFIED_THEOREM", "P178": "CONDITIONAL"}:
        fail("Farey metadata")
    expected = [
        ("E28", 300000, 971, (1054, 665), (485, 306)),
        ("X02", 2075 * 2**60, 72057431991, (103768467013, 65470613321), (10439860591, 6586818670)),
    ]
    rows = stored.get("rows")
    if not isinstance(rows, list) or len(rows) != 2:
        fail("Farey rows")
    ln2 = log_box(Fraction(2))
    ln3 = log_box(Fraction(3))
    for row, (name, V, q, left, right) in zip(rows, expected, strict=True):
        if row.get("name") != name or int(row.get("height")) != V or int(row.get("q_star")) != q:
            fail("Farey row identity")
        if right[0] * left[1] - left[0] * right[1] != 1 or left[1] + right[1] != q:
            fail("Farey determinant")
        epsilon = Fraction(2 * q, 3 * V)
        log_ratio = log_box(1 / (1 - epsilon))
        alpha_low, alpha_high = ln3[0] / ln2[1], ln3[1] / ln2[0]
        psi_low, psi_high = log_ratio[0] / (q * ln2[1]), log_ratio[1] / (q * ln2[0])
        if not Fraction(*left) < alpha_low <= alpha_high < Fraction(*right):
            fail("independent alpha box")
        if not alpha_high + psi_high < Fraction(*right):
            fail("independent Farey margin")
        stored_alpha = row.get("alpha_interval")
        stored_psi = row.get("psi_interval")
        if fraction(stored_alpha[0]) > alpha_low or fraction(stored_alpha[1]) < alpha_high:
            fail("stored alpha enclosure")
        if fraction(stored_psi[0]) > psi_low or fraction(stored_psi[1]) < psi_high:
            fail("stored psi enclosure")
        margin = Fraction(*right) - fraction(stored_alpha[1]) - fraction(stored_psi[1])
        if encode_fraction(margin) != row.get("upper_margin") or margin <= 0 or row.get("certified") is not True:
            fail("stored Farey margin")


def verify_theory(stored: dict[str, object]) -> None:
    if stored.get("proves_collatz") is not False:
        fail("Collatz overclaim")
    claims = stored.get("claims")
    if not isinstance(claims, dict) or {key: value.get("status") for key, value in claims.items()} != EXPECTED:
        fail("claim statuses")
    deps = stored.get("dependencies")
    if deps.get("P175") != ["P150", "P173", "P174", "EXT17"] or deps.get("P178") != ["P176", "X02"]:
        fail("dependency boundary")
    if "X02 is used only by conditional P178" not in stored.get("external_boundary", ""):
        fail("external boundary")
    if "Collatz proof" not in stored.get("what_this_result_does_not_prove", ""):
        fail("interpretation boundary")


def verify_regressions(stored: dict[str, object]) -> None:
    if stored.get("proves_collatz") is not False:
        fail("regression overclaim")
    labels = {row[0] for row in stored.get("mandatory_families", [])}
    if labels != {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}:
        fail("mandatory families")
    controls = stored.get("named_controls")
    if controls.get("NG35", {}).get("left_exceeds_right") is not True:
        fail("NG35")
    if controls.get("NG36", {}).get("integral") is not False:
        fail("NG36")
    if controls.get("NG38", {}).get("endpoint_correction") != 1:
        fail("NG38")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    directory = args.artifact_dir
    for name in FILES:
        if not (directory / name).is_file():
            fail(f"missing {name}")

    theory = load(directory / "phase29_theory.json")
    arc = load(directory / "phase29_arc_audit.json")
    corpus = load(directory / "phase29_coprime_corpus.json")
    state = load(directory / "phase29_state_bounds.json")
    farey = load(directory / "phase29_farey_certificates.json")
    regressions = load(directory / "phase29_regressions.json")
    report = (directory / "phase29_obstruction_report.md").read_text(encoding="utf-8")
    verify_theory(theory)
    verify_farey(farey)
    verify_regressions(regressions)
    if "93,629 tied largest-gap cuts" not in report or "proves_collatz=false" not in report:
        fail("obstruction report")
    arc_counts = verify_finite_arc(arc)
    corpus_counts = verify_coprime_corpus(corpus)
    state_counts = verify_state_bounds(state)

    result = {
        "format": "collatz-phase29-independent-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "independence": "recursive compositions, direct time/residue permutation, repeated-division valuations, suffix products, 224-term logarithm boxes, and separately synthesized profiles",
        "claims": EXPECTED,
        "arc_counts": arc_counts,
        "corpus_counts": corpus_counts,
        "state_counts": state_counts,
        "verified_input_sha256": {name: sha256(directory / name) for name in FILES},
        "proves_collatz": False,
        "what_this_result_does_not_prove": "This does not prove H172, H133, any nonperiodic exclusion, or Collatz.",
    }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
