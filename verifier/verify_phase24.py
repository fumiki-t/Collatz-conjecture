#!/usr/bin/env python3
"""Independent exact verifier for the Phase 24 artifacts.

This verifier does not import the production generator.  It reconstructs weak
profiles and literal exponents before comparing them with the classified
families, uses a shifted Bezout pair for the slope root, and rechecks sparse
certificates with the last (rather than first) largest-gap tie.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Iterable, Iterator, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


CRITICAL_Q_LIMIT = 60
NONCRITICAL_L_LIMIT = 21
DIRECT_Q_LIMIT = 250
AREA_THREE_Q_LIMIT = 100
FILES = (
    "phase24_theory.json",
    "phase24_area_two_remainder.json",
    "phase24_area_three_diagnostic.json",
    "phase24_regressions.json",
    "phase24_obstruction_report.md",
)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} must contain an object")
    return value


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest_rows(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        update_digest(digest, row)
    return digest.hexdigest()


def update_digest(digest: object, row: object) -> None:
    digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def critical_L(q: int) -> int:
    return pow(3, q).bit_length()


def bezout(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    divisor, x, y = bezout(b, a % b)
    return divisor, y, x - (a // b) * y


def modular_signed(base: int, exponent: int, modulus: int) -> int:
    if exponent < 0:
        return pow(pow(base, -1, modulus), -exponent, modulus)
    return pow(base, exponent, modulus)


def independent_gamma(q: int, L: int, D: int) -> int:
    divisor, u, v = bezout(q, L)
    if divisor != 1 or D <= 1:
        fail("slope-root domain")
    # A different Bezout pair from the generator: (u+L, v-q).
    u += L
    v -= q
    gamma = modular_signed(2, u, D) * modular_signed(3, v, D) % D
    if pow(gamma, q, D) != 2 % D or pow(gamma, L, D) != 3 % D:
        fail("slope-root identities")
    return gamma


def weak_area_profiles(q: int, area: int) -> Iterator[tuple[int, ...]]:
    for cells in itertools.combinations_with_replacement(range(1, q), area):
        profile = [0] * q
        for cell in cells:
            profile[cell] += 1
        yield tuple(profile)


def literal_exponents(q: int, L: int, profile: Sequence[int]) -> tuple[int, ...] | None:
    if (
        len(profile) != q
        or profile[0] != 0
        or any(value < 0 for value in profile)
        or not (q < L < 2 * q)
        or math.gcd(q, L) != 1
    ):
        return None
    path = []
    for time in range(q):
        residue = (-L * time) % q
        path.append(residue + q * profile[residue])
    if min(path) != 0 or len({height % q for height in path}) != q:
        return None
    answer = []
    for time, height in enumerate(path):
        following = path[(time + 1) % q] if time + 1 < q else 0
        exponent, remainder = divmod(following - height + L, q)
        if remainder or exponent <= 0:
            return None
        answer.append(exponent)
    if sum(answer) != L:
        return None
    return tuple(answer)


def recurrence_valid(q: int, L: int, profile: Sequence[int]) -> bool:
    if literal_exponents(q, L, profile) is None:
        return False
    m = L - q
    for residue in range(q):
        predecessor = residue - m if residue >= m else residue - m + q
        bound = profile[residue] if residue >= m else profile[residue] - 1
        if profile[predecessor] < bound:
            fail("literal validity disagrees with recurrence")
    return True


def classified_area_two(q: int, L: int) -> set[tuple[int, ...]]:
    m = L - q
    result = set()
    for root in range(q - m - 1, 0, -1):
        profile = [0] * q
        profile[root] = profile[root + m] = 1
        result.add(tuple(profile))
    for right in range(m - 1, 1, -1):
        for left in range(right - 1, 0, -1):
            profile = [0] * q
            profile[left] = profile[right] = 1
            result.add(tuple(profile))
    return result


def classified_area_three(q: int, L: int) -> set[tuple[int, ...]]:
    m = L - q
    result = set()
    for doubled in range(2 * m - q - 1, 0, -1):
        profile = [0] * q
        profile[doubled] = 2
        profile[doubled + q - m] = 1
        result.add(tuple(profile))
    root_values = list(range(1, m))
    for pair in reversed(list(itertools.combinations(root_values, 2))):
        for parent in reversed(pair):
            if parent < q - m:
                profile = [0] * q
                profile[pair[0]] = profile[pair[1]] = 1
                profile[parent + m] = 1
                result.add(tuple(profile))
    for support in reversed(list(itertools.combinations(root_values, 3))):
        profile = [0] * q
        for residue in support:
            profile[residue] = 1
        result.add(tuple(profile))
    return result


def Q_coefficients(profile: Sequence[int]) -> tuple[int, ...]:
    q = len(profile)
    answer = [0] * q
    answer[0] = 1
    for index, height in enumerate(profile):
        b = pow(2, height) - 1
        answer[index] -= b
        answer[(index + 1) % q] += b * (2 if index + 1 == q else 1)
    return tuple(answer)


def sparse_modular_value(coefficients: Sequence[int], gamma: int, modulus: int) -> int:
    return sum(
        coefficient * pow(gamma, index, modulus)
        for index, coefficient in enumerate(coefficients)
        if coefficient
    ) % modulus


def correction(exponents: Sequence[int]) -> int:
    q = len(exponents)
    answer = 0
    cumulative = 0
    for position, exponent in enumerate(exponents):
        answer += pow(3, q - position - 1) * pow(2, cumulative)
        cumulative += exponent
    return answer


def arc_data(
    coefficients: Sequence[int], q: int, L: int, *, choose_last: bool
) -> dict[str, object]:
    support = [index for index, coefficient in enumerate(coefficients) if coefficient]
    if not support:
        fail("zero sparse polynomial")
    if q == 1:
        residues = {support[0]: 0}
    else:
        inverse = pow(L, -1, q)
        residues = {index: (-index * inverse) % q for index in support}
    ordered = sorted(residues.values())
    gaps = [
        (ordered[(position + 1) % len(ordered)] + (q if position + 1 == len(ordered) else 0)) - point
        for position, point in enumerate(ordered)
    ]
    maximum = max(gaps)
    ties = [position for position, gap in enumerate(gaps) if gap == maximum]
    cut = ties[-1] if choose_last else ties[0]
    start = ordered[(cut + 1) % len(ordered)]
    b = {index: residue if residue >= start else residue + q for index, residue in residues.items()}
    width = max(b.values()) - min(b.values())
    M = len(support)
    if width != q - maximum or width > q - (q + M - 1) // M:
        fail("arc width")
    A = {}
    for index in support:
        numerator = L * b[index] + index
        if numerator % q:
            fail("arc lift congruence")
        A[index] = numerator // q
    if len(set(A.values())) != M:
        fail("arc exponent collision")
    minimum_A = min(A.values())
    maximum_b = max(b.values())
    R = sum(
        coefficients[index]
        * pow(2, A[index] - minimum_A)
        * pow(3, maximum_b - b[index])
        for index in support
    )
    l1 = sum(abs(coefficients[index]) for index in support)
    if pow(abs(R), q) >= pow(2 * l1, q) * pow(2, L * width):
        fail("strict sparse size inequality")
    odd = all(coefficients[index] % 2 for index in support)
    if odd and (R == 0 or R % 2 == 0):
        fail("odd sparse nonvanishing")
    return {
        "support": support,
        "support_count": M,
        "l1_norm": l1,
        "lift_width": width,
        "largest_gap": maximum,
        "b_lifts": [[index, b[index]] for index in support],
        "A_lifts": [[index, A[index]] for index in support],
        "integer_R": R,
        "all_nonzero_coefficients_odd": odd,
    }


def rebuilt_profile_row(q: int, L: int, profile: tuple[int, ...]) -> list[object]:
    exponents = literal_exponents(q, L, profile)
    if exponents is None:
        fail("invalid classified profile")
    D = pow(2, L) - pow(3, q)
    coefficients = Q_coefficients(profile)
    gamma = independent_gamma(q, L, D)
    modular = sparse_modular_value(coefficients, gamma, D)
    B_mod = correction(exponents) % D
    if (modular == 0) != (B_mod == 0):
        fail("Q/A affine equivalence")
    first = arc_data(coefficients, q, L, choose_last=False)
    last = arc_data(coefficients, q, L, choose_last=True)
    if modular == 0 and (first["integer_R"] % D or last["integer_R"] % D):
        fail("arc divisibility")
    return [
        q,
        L,
        [index for index, value in enumerate(profile) if value],
        [[index, value] for index, value in enumerate(coefficients) if value],
        first["support_count"],
        first["l1_norm"],
        first["lift_width"],
        first["integer_R"],
        modular,
        B_mod,
    ]


def verify_theory(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase24-theory-v1" or stored.get("proves_collatz") is not False:
        fail("theory metadata or Collatz boundary")
    claims = stored.get("claims")
    if not isinstance(claims, dict) or {key: value.get("status") for key, value in claims.items()} != {
        "P147": "VERIFIED_THEOREM",
        "P148": "VERIFIED_THEOREM",
        "P149": "VERIFIED_THEOREM",
        "P150": "VERIFIED_THEOREM",
        "H147": "OPEN",
    }:
        fail("theory claim statuses")
    expected_rows = []
    for q in range(61, 66):
        exponent = q - (q + 4) // 5
        left = 48 * pow(3, exponent) * pow(25, q)
        right = pow(64, q)
        if left >= right:
            fail("critical base inequality")
        expected_rows.append([q, exponent, str(left), str(right), str(right - left)])
    critical = stored.get("critical_area_two")
    if not isinstance(critical, dict) or critical.get("base_rows_q_61_to_65") != expected_rows:
        fail("critical base rows")
    ratio = critical.get("five_step_ratio")
    if ratio != {"left": str(pow(3, 4) * pow(25, 5)), "right": str(pow(64, 5)), "strict": True}:
        fail("critical induction ratio")
    noncritical = stored.get("noncritical_area_two")
    if not isinstance(noncritical, dict) or noncritical.get("nonboundary_L22_strict") is not True or noncritical.get("boundary_L19_strict") is not True:
        fail("noncritical strict thresholds")
    if not (pow(10, 5) * pow(2, 4 * 22) < pow(2, 5 * 22 - 5)):
        fail("nonboundary threshold arithmetic")
    if not (pow(12, 4) * pow(2, 3 * 19) < pow(2, 4 * 19 - 4)):
        fail("boundary threshold arithmetic")
    fixed_area = stored.get("fixed_area_noncritical")
    if not isinstance(fixed_area, dict) or "R(Q_a)!=0" not in str(fixed_area.get("boundary")) or "bit_length" not in str(fixed_area.get("effective_threshold")):
        fail("fixed-area nonvanishing boundary")


def verify_finite(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase24-area-two-remainder-v1" or stored.get("proves_collatz") is not False:
        fail("finite metadata or Collatz boundary")
    direct_metadata = stored.get("direct_critical_scan")
    if (
        stored.get("critical_profile_count") != 7057
        or stored.get("noncritical_profile_count") != 204
        or not isinstance(direct_metadata, dict)
        or direct_metadata.get("profile_count") != 544073
    ):
        fail("finite declared counts")
    critical_rows = []
    critical_by_q = []
    for q in range(1, CRITICAL_Q_LIMIT + 1):
        L = critical_L(q)
        valid = set()
        if L < 2 * q and math.gcd(q, L) == 1:
            valid = {profile for profile in weak_area_profiles(q, 2) if recurrence_valid(q, L, profile)}
            if valid != classified_area_two(q, L):
                fail(f"area-two classification q={q},L={L}")
            for profile in valid:
                row = rebuilt_profile_row(q, L, profile)
                if row[8] == 0 or row[9] == 0:
                    fail("critical integral remainder")
                critical_rows.append(row)
        critical_by_q.append([q, L, len(valid)])
    if (
        stored.get("critical_profile_count") != len(critical_rows)
        or stored.get("critical_integral_count") != 0
        or stored.get("critical_by_q") != critical_by_q
        or stored.get("critical_row_digest_sha256") != digest_rows(sorted(critical_rows))
    ):
        fail("critical finite reconstruction")

    noncritical_rows = []
    noncritical_by_length = []
    for L in range(2, NONCRITICAL_L_LIMIT + 1):
        count = 0
        for q in range(1, L):
            if not (q < L < 2 * q) or pow(2, L) <= pow(3, q) or L == critical_L(q) or math.gcd(q, L) != 1:
                continue
            valid = {profile for profile in weak_area_profiles(q, 2) if recurrence_valid(q, L, profile)}
            if valid != classified_area_two(q, L):
                fail(f"noncritical area-two classification q={q},L={L}")
            for profile in valid:
                row = rebuilt_profile_row(q, L, profile)
                if row[8] == 0 or row[9] == 0:
                    fail("noncritical integral remainder")
                noncritical_rows.append(row)
            count += len(valid)
        noncritical_by_length.append([L, count])
    if (
        stored.get("noncritical_profile_count") != len(noncritical_rows)
        or stored.get("noncritical_integral_count") != 0
        or stored.get("noncritical_by_length") != noncritical_by_length
        or stored.get("noncritical_row_digest_sha256") != digest_rows(sorted(noncritical_rows))
    ):
        fail("noncritical finite reconstruction")

    direct_count = 0
    direct_digest = hashlib.sha256()
    direct_by_q = []
    for q in range(1, DIRECT_Q_LIMIT + 1):
        L = critical_L(q)
        valid: set[tuple[int, ...]] = set()
        if L < 2 * q and math.gcd(q, L) == 1:
            valid = classified_area_two(q, L)
            if q <= CRITICAL_Q_LIMIT:
                brute = {profile for profile in weak_area_profiles(q, 2) if recurrence_valid(q, L, profile)}
                if valid != brute:
                    fail(f"direct area-two classification q={q}")
            D = pow(2, L) - pow(3, q)
            gamma = independent_gamma(q, L, D)
            q_rows = []
            for profile in valid:
                modular = sparse_modular_value(Q_coefficients(profile), gamma, D)
                if modular == 0:
                    fail("direct critical integral counterexample")
                support = tuple(index for index, value in enumerate(profile) if value)
                q_rows.append([q, L, support, modular])
            for row in sorted(q_rows):
                update_digest(direct_digest, row)
            direct_count += len(q_rows)
        direct_by_q.append([q, L, len(valid)])
    direct = stored.get("direct_critical_scan")
    if not isinstance(direct, dict) or (
        direct.get("q_maximum") != DIRECT_Q_LIMIT
        or direct.get("profile_count") != direct_count
        or direct.get("integral_count") != 0
        or direct.get("by_q") != direct_by_q
        or direct.get("row_digest_sha256") != direct_digest.hexdigest()
    ):
        fail("direct critical scan reconstruction")

    samples = stored.get("stored_samples")
    if not isinstance(samples, list) or not samples:
        fail("finite samples")
    for sample in samples:
        if not isinstance(sample, list) or len(sample) != 10:
            fail("malformed finite sample")
        q, L = int(sample[0]), int(sample[1])
        profile = [0] * q
        for index in sample[2]:
            profile[int(index)] = 1
        if rebuilt_profile_row(q, L, tuple(profile)) != sample:
            fail("stored finite sample arithmetic")
    return {
        "critical": len(critical_rows),
        "noncritical": len(noncritical_rows),
        "direct": direct_count,
    }


def circular_width(points: Sequence[int], modulus: int) -> int:
    ordered = sorted(points)
    gaps = []
    for position, point in enumerate(ordered):
        following = ordered[(position + 1) % len(ordered)]
        if position + 1 == len(ordered):
            following += modulus
        gaps.append(following - point)
    return modulus - max(gaps)


def diagnostic_row(q: int, L: int, profile: tuple[int, ...]) -> list[object]:
    coefficients = Q_coefficients(profile)
    support = tuple(index for index, value in enumerate(coefficients) if value)
    q_inverse = pow(L, -1, q)
    L_inverse = pow(q, -1, L)
    Wq = circular_width([(-index * q_inverse) % q for index in support], q)
    WL = circular_width([(index * L_inverse) % L for index in support], L)
    return [
        q,
        L,
        tuple(index for index, value in enumerate(profile) if value),
        tuple(profile[index] for index, value in enumerate(profile) if value),
        support,
        Wq,
        WL,
    ]


def verify_area_three(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase24-area-three-diagnostic-v1" or stored.get("proves_collatz") is not False:
        fail("area-three metadata or Collatz boundary")
    if stored.get("valid_profile_count") != 521154:
        fail("area-three declared count")
    row_count = 0
    digest = hashlib.sha256()
    by_q = []
    max_support = 0
    worst_q = (0, 1)
    worst_effective = (0, 1)
    failures = 0
    for q in range(1, AREA_THREE_Q_LIMIT + 1):
        L = critical_L(q)
        profiles: set[tuple[int, ...]] = set()
        if L < 2 * q and math.gcd(q, L) == 1:
            profiles = classified_area_three(q, L)
            for profile in profiles:
                if not recurrence_valid(q, L, profile) or sum(profile) != 3:
                    fail(f"area-three classified validity q={q}")
            # A literal weak-profile audit is cheap enough here and guards the
            # two-shape derivation independently through q<=30.
            if q <= 30:
                brute = {profile for profile in weak_area_profiles(q, 3) if recurrence_valid(q, L, profile)}
                if brute != profiles:
                    fail(f"area-three shape completeness q={q}")
            q_rows = []
            for profile in profiles:
                row = diagnostic_row(q, L, profile)
                q_rows.append(row)
                max_support = max(max_support, len(row[4]))
                if row[5] * worst_q[1] > worst_q[0] * q:
                    worst_q = (row[5], q)
                effective = (row[5], q) if row[5] * L <= row[6] * q else (row[6], L)
                if effective[0] * worst_effective[1] > worst_effective[0] * effective[1]:
                    worst_effective = effective
                if pow(3, effective[0]) * pow(25, effective[1]) >= pow(64, effective[1]):
                    failures += 1
            for row in sorted(q_rows):
                update_digest(digest, row)
            row_count += len(q_rows)
        by_q.append([q, L, len(profiles)])

    if (
        stored.get("valid_profile_count") != row_count
        or stored.get("by_q") != by_q
        or stored.get("maximum_Q_support") != max_support
        or stored.get("row_digest_sha256") != digest.hexdigest()
        or stored.get("threshold_failure_count") != failures
        or stored.get("smallest_threshold_failure") is not None
    ):
        fail("area-three finite reconstruction")
    q_arc = stored.get("worst_q_arc")
    effective_arc = stored.get("worst_two_sided_effective_arc")
    if not isinstance(q_arc, dict) or (q_arc.get("numerator"), q_arc.get("denominator")) != worst_q:
        fail("worst q-arc ratio")
    if not isinstance(effective_arc, dict) or (effective_arc.get("numerator"), effective_arc.get("denominator")) != worst_effective:
        fail("worst effective arc ratio")
    for record, ratio_name in ((q_arc, "q"), (effective_arc, "effective")):
        row = record.get("row")
        if not isinstance(row, list) or len(row) != 7:
            fail(f"stored {ratio_name} witness")
        q, L = int(row[0]), int(row[1])
        profile = [0] * q
        for index, height in zip(row[2], row[3], strict=True):
            profile[int(index)] = int(height)
        rebuilt = json.loads(json.dumps(diagnostic_row(q, L, tuple(profile))))
        if rebuilt != row:
            fail(f"stored {ratio_name} witness arithmetic")
    return {"profiles": row_count, "threshold_failures": failures}


def turns(values: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    for shift in range(len(values)):
        yield values[shift:] + values[:shift]


def height_path(values: tuple[int, ...]) -> tuple[int, ...]:
    q, L = len(values), sum(values)
    height = 0
    answer = []
    for exponent in values:
        answer.append(height)
        height += q * exponent - L
    if height:
        fail("word height closure")
    return tuple(answer)


def word_profile(values: tuple[int, ...]) -> tuple[int, ...] | None:
    q, L = len(values), sum(values)
    if math.gcd(q, L) != 1:
        return None
    candidates = [word for word in turns(values) if min(height_path(word)) == 0]
    if len(candidates) != 1:
        fail("coprime minimum rotation")
    profile = [-1] * q
    for height in height_path(candidates[0]):
        profile[height % q] = height // q
    return tuple(profile)


def exponents_from_bits(bits: str) -> tuple[int, ...]:
    start = bits.index("1")
    rotated = bits[start:] + bits[:start]
    ones = [position for position, bit in enumerate(rotated) if bit == "1"]
    return tuple((ones[(index + 1) % len(ones)] - position) % len(bits) or len(bits) for index, position in enumerate(ones))


def verify_regressions(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase24-regressions-v1" or stored.get("proves_collatz") is not False:
        fail("regression metadata or Collatz boundary")
    words = stored.get("mandatory_word_families")
    if not isinstance(words, list) or len(words) != 14:
        fail("mandatory word family count")
    required = {"A", "B", "(110)^4", "(111)^4", "mixed-(110|111)"}
    names = {row[0] for row in words if isinstance(row, list) and row}
    if not required <= names or not all(f"A^{r}B^{s}" in names for r in range(1, 4) for s in range(1, 4)):
        fail("mandatory word family names")
    for row in words:
        if not isinstance(row, list) or len(row) != 5:
            fail("malformed word regression")
        _, bits, stored_exponents, stored_profile, stored_sparse = row
        exponents = exponents_from_bits(bits)
        if list(exponents) != stored_exponents:
            fail("word exponent regression")
        profile = word_profile(exponents)
        if (list(profile) if profile is not None else None) != stored_profile:
            fail("word profile regression")
        expected_sparse = None
        if profile is not None and pow(2, sum(exponents)) > pow(3, len(exponents)):
            expected_sparse = arc_data(Q_coefficients(profile), len(profile), sum(exponents), choose_last=False)
            arc_data(Q_coefficients(profile), len(profile), sum(exponents), choose_last=True)
        if expected_sparse != stored_sparse:
            fail("word sparse regression")

    numeric = stored.get("numeric_prefix_families")
    if not isinstance(numeric, list) or len(numeric) != 22:
        fail("numeric family count")
    for row in numeric:
        family, m, source, stored_steps, stored_end, stored_one = row
        expected_source = pow(2, m) - 1 if family == "2^m-1" else pow(8, m) - 5
        if source != expected_source:
            fail("numeric source")
        current = source
        seen = set()
        for steps in range(257):
            if current == 1 or current in seen or steps == 256:
                if [steps, current, current == 1] != [stored_steps, stored_end, stored_one]:
                    fail("numeric trace")
                break
            seen.add(current)
            current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2

    edges = stored.get("edge_cases")
    if not isinstance(edges, list) or {row[0] for row in edges} != {
        "largest-gap-tie", "boundary-coefficient-3", "adjacent-root-cancellation"
    }:
        fail("edge regression names")
    for name, wrapped in edges:
        q, L, profile_list, coefficients_list, first, last = wrapped
        profile = tuple(profile_list)
        coefficients = Q_coefficients(profile)
        if list(coefficients) != coefficients_list:
            fail("edge polynomial")
        if first != arc_data(coefficients, q, L, choose_last=False) or last != arc_data(coefficients, q, L, choose_last=True):
            fail("edge arc certificate")
        support = [index for index, value in enumerate(profile) if value]
        if name == "largest-gap-tie" and first["b_lifts"] == last["b_lifts"]:
            fail("largest-gap tie control")
        if name == "boundary-coefficient-3" and not (support[-1] == q - 1 and coefficients[0] == 3):
            fail("boundary coefficient control")
        if name == "adjacent-root-cancellation" and len(first["support"]) >= 5:
            fail("cancellation control")
    controls = stored.get("cycle_controls")
    if not isinstance(controls, dict) or controls.get("trivial_positive", {}).get("D") != 1 or controls.get("negative_q7", {}).get("D") != -139:
        fail("cycle sign controls")


def verify_obstruction(path: Path, area_three_count: int) -> None:
    text = path.read_text(encoding="utf-8")
    required = [
        "Smallest next obstruction",
        f"`{area_three_count}` valid critical coprime area-three",
        "finite diagnostic only",
        "What this result does not prove",
        "proves_collatz=false",
    ]
    if any(fragment not in text for fragment in required):
        fail("obstruction report boundary")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    try:
        theory = load(args.artifact_dir / FILES[0])
        finite = load(args.artifact_dir / FILES[1])
        area_three = load(args.artifact_dir / FILES[2])
        regressions = load(args.artifact_dir / FILES[3])
        verify_theory(theory)
        finite_counts = verify_finite(finite)
        area_three_counts = verify_area_three(area_three)
        verify_regressions(regressions)
        verify_obstruction(args.artifact_dir / FILES[4], area_three_counts["profiles"])
        report = {
            "format": "collatz-phase24-verifier-v1",
            "valid": True,
            "generator_imported": False,
            "verified_files": list(FILES),
            "finite_counts": finite_counts,
            "area_three_counts": area_three_counts,
            "arithmetic": "arbitrary-precision integers only",
            "proves_collatz": False,
        }
        if args.write_report:
            save(args.write_report, report)
        print(json.dumps(report, sort_keys=True))
    except (OSError, TypeError, ValueError, KeyError, IndexError) as exc:
        print(f"phase24 verification failed: {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
