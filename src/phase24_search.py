#!/usr/bin/env python3
"""Generate exact Phase 24 sparse-arc and area-two evidence.

The Phase 24 note is treated as an untrusted proposal.  Acceptance decisions
use only arbitrary-precision integers.  In particular, no floating-point
approximation to log(3)/log(2) is used.
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


CRITICAL_REMAINDER_Q_MAXIMUM = 60
NONCRITICAL_REMAINDER_L_MAXIMUM = 21
DIRECT_CRITICAL_Q_MAXIMUM = 250
AREA_THREE_Q_MAXIMUM = 100
A_BITS = "11101"
B_BITS = "1100"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def row_digest(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        update_digest(digest, row)
    return digest.hexdigest()


def update_digest(digest: object, row: object) -> None:
    digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def extended_gcd(left: int, right: int) -> tuple[int, int, int]:
    old_r, r = left, right
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def signed_modular_power(base: int, exponent: int, modulus: int) -> int:
    if exponent < 0:
        base = pow(base, -1, modulus)
        exponent = -exponent
    return pow(base, exponent, modulus)


def slope_root(q: int, L: int, modulus: int) -> int:
    divisor, u, v = extended_gcd(q, L)
    if divisor != 1 or modulus <= 1:
        raise ValueError("slope root requires a coprime slope and modulus > 1")
    return signed_modular_power(2, u, modulus) * signed_modular_power(3, v, modulus) % modulus


def critical_length(q: int) -> int:
    """Return ceil(q*log_2(3)) exactly."""
    if q < 1:
        raise ValueError("positive odd-count required")
    return pow(3, q).bit_length()


def profile_valid(q: int, L: int, profile: Sequence[int]) -> bool:
    """Exact residue-profile validity using the Phase 24 recurrence."""
    if (
        len(profile) != q
        or q < 1
        or not (q < L < 2 * q)
        or math.gcd(q, L) != 1
        or profile[0] != 0
        or any(value < 0 for value in profile)
    ):
        return False
    m = L - q
    for residue in range(m, q):
        if profile[residue - m] < profile[residue]:
            return False
    for residue in range(m):
        if profile[residue - m + q] < profile[residue] - 1:
            return False
    return True


def exponents_of_profile(q: int, L: int, profile: Sequence[int]) -> tuple[int, ...] | None:
    if not profile_valid(q, L, profile):
        return None
    heights = []
    for time in range(q):
        residue = (-L * time) % q
        heights.append(residue + q * profile[residue])
    exponents = []
    for time, height in enumerate(heights):
        following = heights[time + 1] if time + 1 < q else 0
        quotient, remainder = divmod(following - height + L, q)
        if remainder or quotient < 1:
            return None
        exponents.append(quotient)
    return tuple(exponents)


def area_two_profiles(q: int, L: int) -> Iterator[tuple[int, ...]]:
    """Generate the complete classified area-two profile family."""
    if not (q < L < 2 * q) or math.gcd(q, L) != 1 or 2**L <= 3**q:
        return
    m = L - q
    for left, right in itertools.combinations(range(1, m), 2):
        profile = [0] * q
        profile[left] = profile[right] = 1
        yield tuple(profile)
    for root in range(1, q - m):
        profile = [0] * q
        profile[root] = profile[root + m] = 1
        yield tuple(profile)


def area_three_profiles(q: int, L: int) -> Iterator[tuple[int, ...]]:
    """Generate all valid area-three profiles from their parent/edge shapes."""
    if not (q < L < 2 * q) or math.gcd(q, L) != 1 or 2**L <= 3**q:
        return
    m = L - q
    roots = range(1, m)
    for support in itertools.combinations(roots, 3):
        profile = [0] * q
        for residue in support:
            profile[residue] = 1
        yield tuple(profile)
    for root_pair in itertools.combinations(roots, 2):
        for parent in root_pair:
            if parent < q - m:
                profile = [0] * q
                profile[root_pair[0]] = profile[root_pair[1]] = 1
                profile[parent + m] = 1
                yield tuple(profile)
    for doubled in range(1, max(1, 2 * m - q)):
        predecessor = doubled + q - m
        profile = [0] * q
        profile[doubled] = 2
        profile[predecessor] = 1
        yield tuple(profile)


def reduced_polynomial(profile: Sequence[int]) -> tuple[int, ...]:
    """Coefficients of 1+(X-1) sum (2^a_r-1)X^r modulo X^q-2."""
    q = len(profile)
    coefficients = [0] * q
    coefficients[0] = 1
    for residue, height in enumerate(profile):
        value = 2**height - 1
        coefficients[residue] -= value
        if residue + 1 < q:
            coefficients[residue + 1] += value
        else:
            coefficients[0] += 2 * value
    return tuple(coefficients)


def polynomial_value(coefficients: Sequence[int], value: int, modulus: int) -> int:
    return sum(
        coefficient * pow(value, exponent, modulus)
        for exponent, coefficient in enumerate(coefficients)
        if coefficient
    ) % modulus


def circular_arc_lifts(
    support: Sequence[int], q: int, L: int, *, last_tie: bool = False
) -> tuple[dict[int, int], int, int]:
    """Lift b residues after deleting one largest circular gap."""
    if not support or q < 1 or math.gcd(q, L) != 1:
        raise ValueError("nonempty support and coprime slope required")
    if q == 1:
        return {support[0]: 0}, 0, 1
    inverse = pow(L, -1, q)
    residues = {index: (-index * inverse) % q for index in support}
    points = sorted(residues.values())
    gaps = []
    for index, point in enumerate(points):
        following = points[(index + 1) % len(points)]
        if index + 1 == len(points):
            following += q
        gaps.append(following - point)
    largest = max(gaps)
    candidates = [index for index, gap in enumerate(gaps) if gap == largest]
    cut = candidates[-1] if last_tie else candidates[0]
    start = points[(cut + 1) % len(points)]
    lifts = {
        index: residue if residue >= start else residue + q
        for index, residue in residues.items()
    }
    width = max(lifts.values()) - min(lifts.values())
    if width != q - largest:
        raise AssertionError("circular arc width")
    return lifts, width, largest


def sparse_arc_certificate(
    coefficients: Sequence[int], q: int, L: int, *, last_tie: bool = False
) -> dict[str, object]:
    support = tuple(index for index, coefficient in enumerate(coefficients) if coefficient)
    if not support:
        raise ValueError("nonzero polynomial required")
    lifts, width, gap = circular_arc_lifts(support, q, L, last_tie=last_tie)
    A_values = {index: (L * lifts[index] + index) // q for index in support}
    if len(set(A_values.values())) != len(support):
        raise AssertionError("distinct sparse powers")
    A_min = min(A_values.values())
    b_max = max(lifts.values())
    integer = sum(
        coefficients[index]
        * 2 ** (A_values[index] - A_min)
        * 3 ** (b_max - lifts[index])
        for index in support
    )
    l1 = sum(abs(coefficients[index]) for index in support)
    support_count = len(support)
    width_limit = q - (q + support_count - 1) // support_count
    if width > width_limit:
        raise AssertionError("pigeonhole arc bound")
    if abs(integer) ** q >= (2 * l1) ** q * 2 ** (L * width):
        raise AssertionError("strict sparse-arc size bound")
    odd_nonzero = all(coefficients[index] % 2 for index in support)
    if odd_nonzero and integer % 2 == 0:
        raise AssertionError("odd coefficient nonvanishing")
    return {
        "support": list(support),
        "support_count": support_count,
        "l1_norm": l1,
        "lift_width": width,
        "largest_gap": gap,
        "b_lifts": [[index, lifts[index]] for index in support],
        "A_lifts": [[index, A_values[index]] for index in support],
        "integer_R": integer,
        "all_nonzero_coefficients_odd": odd_nonzero,
    }


def affine_correction(exponents: Sequence[int]) -> int:
    q = len(exponents)
    answer = 0
    power = 0
    for index, exponent in enumerate(exponents):
        answer += 3 ** (q - 1 - index) * 2**power
        power += exponent
    return answer


def profile_row(q: int, L: int, profile: tuple[int, ...]) -> list[object]:
    D = 2**L - 3**q
    coefficients = reduced_polynomial(profile)
    certificate = sparse_arc_certificate(coefficients, q, L)
    gamma = slope_root(q, L, D)
    modular = polynomial_value(coefficients, gamma, D)
    exponents = exponents_of_profile(q, L, profile)
    if exponents is None:
        raise AssertionError("classified invalid area-two profile")
    B = affine_correction(exponents)
    if (modular == 0) != (B % D == 0):
        raise AssertionError("reduced polynomial equivalence")
    if modular == 0 and certificate["integer_R"] % D:
        raise AssertionError("sparse divisibility")
    return [
        q,
        L,
        [index for index, value in enumerate(profile) if value],
        [[index, value] for index, value in enumerate(coefficients) if value],
        certificate["support_count"],
        certificate["l1_norm"],
        certificate["lift_width"],
        certificate["integer_R"],
        modular,
        B % D,
    ]


def strict_critical_constant_rows() -> list[list[object]]:
    rows = []
    for q in range(61, 66):
        exponent = q - (q + 4) // 5
        left = 48 * 3**exponent * 25**q
        right = 64**q
        if not left < right:
            raise AssertionError("critical base inequality")
        rows.append([q, exponent, str(left), str(right), str(right - left)])
    if not 3**4 * 25**5 < 64**5:
        raise AssertionError("critical five-step induction ratio")
    return rows


def theory_artifact() -> dict[str, object]:
    critical_rows = strict_critical_constant_rows()
    nonboundary_l22 = 10**5 * 2 ** (4 * 22) < 2 ** (5 * 22 - 5)
    boundary_l19 = 12**4 * 2 ** (3 * 19) < 2 ** (4 * 19 - 4)
    if not nonboundary_l22 or not boundary_l19:
        raise AssertionError("noncritical threshold")
    return {
        "format": "collatz-phase24-theory-v1",
        "claims": {
            "P147": {
                "status": "VERIFIED_THEOREM",
                "statement": "A sparse polynomial vanishing at the coprime slope root has an exact circular-arc lift D|R with |R|<2||P||_1*2^(LW/q); if all nonzero coefficients are odd, R is odd and nonzero.",
            },
            "P148": {
                "status": "VERIFIED_THEOREM",
                "statement": "The residue recurrence classifies every valid area-two profile as two roots or one root-edge pair; it also gives the two exact area-three shape families.",
            },
            "P149": {
                "status": "VERIFIED_THEOREM",
                "statement": "Every positive coprime slope profile of defect area at most two is impossible except the area-zero trivial cycle; the critical area-two large-q part depends on EXT05 and E36 supplies the finite remainder.",
            },
            "P150": {
                "status": "VERIFIED_THEOREM",
                "statement": "For fixed area A, support(Q)<=2A+1 and ||Q||_1<=3*2^A-2; every noncritical profile with nonzero sparse lift is excluded beyond an effective A-dependent length.",
            },
            "H147": {
                "status": "OPEN",
                "statement": "Exploit paired area-three support to prove a uniform critical arc gap, then address arbitrary-area coprime and noncoprime cycle profiles.",
            },
        },
        "map": "odd accelerated x_(i+1)=(3*x_i+1)/2^e_i, e_i=v2(3*x_i+1)",
        "slope_domain": "q<L<2q, D=2^L-3^q>0, gcd(q,L)=1",
        "slope_root": "For uq+vL=1, gamma=2^u*3^v mod D and gamma^q=2, gamma^L=3.",
        "reduced_polynomial": "Q_a=1+(X-1)sum_r(2^a_r-1)X^r modulo X^q-2; A_a(gamma)=0 iff Q_a(gamma)=0.",
        "sparse_arc": {
            "lift_congruence": "L*b_j=-j mod q and A_j=(L*b_j+j)/q",
            "width": "W<=q-ceil(q/M) after deleting a largest circular gap",
            "integer": "R=sum_j c_j*2^(A_j-A_min)*3^(b_max-b_j)",
            "divisibility": "P(gamma)=0 mod D implies D|R",
            "strict_bound": "|R|<2*||P||_1*2^(L*W/q)",
            "critical_bound": "if L=ceil(q log_2 3), then |R|<4*||P||_1*3^W",
            "nonvanishing": "distinct A_j and odd nonzero c_j make R odd",
        },
        "profile_recurrence": {
            "m": "L-q",
            "r_at_least_m": "e=1+a_(r-m)-a_r",
            "r_below_m": "e=2+a_(r-m+q)-a_r",
            "validity": "a_(r-m)>=a_r for r>=m and a_(r-m+q)>=a_r-1 for r<m",
        },
        "area_two_classification": {
            "root_root": "support {s,t}, 1<=s<t<m",
            "root_edge": "support {s,s+m}, 1<=s<q-m",
            "height_two": "impossible",
            "nonboundary_Q": "1-X^s+X^(s+1)-X^t+X^(t+1), with cancellations retained",
            "boundary_Q": "3-X^s+X^(s+1)-X^(q-1)",
        },
        "area_three_classification": {
            "three_cells": "three roots, or two roots and one upper cell attached to one of them",
            "doubled_cell": "a_r=2 forces a_(r+q-m)=1 and 1<=r<2m-q",
        },
        "critical_area_two": {
            "scope": "q>=61 and L=ceil(q log_2 3)",
            "external_input": "EXT05: D>(64/25)^q/2 for q>12",
            "upper_bound": "0<|R|<24*3^(q-ceil(q/5))<D",
            "base_rows_q_61_to_65": critical_rows,
            "five_step_ratio": {
                "left": str(3**4 * 25**5),
                "right": str(64**5),
                "strict": True,
            },
        },
        "noncritical_area_two": {
            "scope": "L>=ceil(q log_2 3)+1 and L>=22",
            "D_lower_bound": "D>2^(L-1)",
            "nonboundary": "|R|<10*2^(4L/5)<2^(L-1), checked at L=22 and monotone",
            "boundary": "|R|<12*2^(3L/4)<2^(L-1), checked already at L=19 and monotone",
            "nonboundary_L22_strict": nonboundary_l22,
            "boundary_L19_strict": boundary_l19,
        },
        "fixed_area_noncritical": {
            "support_bound": "M<=2A+1",
            "l1_bound": "||Q_a||_1<=C_A=3*2^A-2",
            "effective_threshold": "L>=(2A+1)*bit_length(4*C_A) implies |R|<2^(L-1)<D whenever R(Q_a)!=0",
            "boundary": "P150 requires R(Q_a)!=0; arbitrary Q_a coefficients need not satisfy the odd-coefficient shortcut used for area two.",
        },
        "what_this_result_does_not_prove": "It does not exclude area at least three, general noncoprime cycles, H89, H112, H72, or prove Collatz.",
        "proves_collatz": False,
    }


def finite_remainder_artifact() -> dict[str, object]:
    critical_rows: list[list[object]] = []
    critical_by_q = []
    samples: list[list[object]] = []
    for q in range(1, CRITICAL_REMAINDER_Q_MAXIMUM + 1):
        L = critical_length(q)
        count = 0
        if L < 2 * q and math.gcd(q, L) == 1:
            for profile in area_two_profiles(q, L):
                row = profile_row(q, L, profile)
                critical_rows.append(row)
                count += 1
                support = row[2]
                coefficient_indices = [entry[0] for entry in row[3]]
                if (
                    len(samples) < 4
                    or support[-1] == q - 1
                    or len(coefficient_indices) < 5
                    or row[6] == q - (q + row[4] - 1) // row[4]
                ):
                    samples.append(row)
        critical_by_q.append([q, L, count])

    noncritical_rows: list[list[object]] = []
    noncritical_by_length = []
    for L in range(2, NONCRITICAL_REMAINDER_L_MAXIMUM + 1):
        count = 0
        for q in range(1, L):
            if (
                not (q < L < 2 * q)
                or 2**L <= 3**q
                or L == critical_length(q)
                or math.gcd(q, L) != 1
            ):
                continue
            for profile in area_two_profiles(q, L):
                row = profile_row(q, L, profile)
                noncritical_rows.append(row)
                count += 1
                if len(samples) < 12:
                    samples.append(row)
        noncritical_by_length.append([L, count])

    if any(row[8] == 0 or row[9] == 0 for row in critical_rows + noncritical_rows):
        raise AssertionError("integral finite area-two profile")

    direct_count = 0
    direct_digest = hashlib.sha256()
    direct_by_q = []
    for q in range(1, DIRECT_CRITICAL_Q_MAXIMUM + 1):
        L = critical_length(q)
        q_rows = []
        if L < 2 * q and math.gcd(q, L) == 1:
            for profile in area_two_profiles(q, L):
                coefficients = reduced_polynomial(profile)
                D = 2**L - 3**q
                gamma = slope_root(q, L, D)
                modular = polynomial_value(coefficients, gamma, D)
                support = tuple(index for index, value in enumerate(profile) if value)
                q_rows.append([q, L, support, modular])
                if modular == 0:
                    raise AssertionError("critical direct-scan counterexample")
        for row in sorted(q_rows):
            update_digest(direct_digest, row)
        direct_count += len(q_rows)
        direct_by_q.append([q, L, len(q_rows)])

    return {
        "format": "collatz-phase24-area-two-remainder-v1",
        "claims": {"P149": "VERIFIED_THEOREM", "E36": "VERIFIED_FINITE", "H147": "OPEN"},
        "critical_scope": {
            "q_maximum": CRITICAL_REMAINDER_Q_MAXIMUM,
            "L": "ceil(q log_2 3)",
            "coprime_only": True,
            "area": 2,
        },
        "critical_profile_count": len(critical_rows),
        "critical_integral_count": 0,
        "critical_by_q": critical_by_q,
        "critical_row_digest_sha256": row_digest(sorted(critical_rows)),
        "noncritical_scope": {
            "L_maximum": NONCRITICAL_REMAINDER_L_MAXIMUM,
            "L_at_least_critical_plus_one": True,
            "coprime_only": True,
            "area": 2,
        },
        "noncritical_profile_count": len(noncritical_rows),
        "noncritical_integral_count": 0,
        "noncritical_by_length": noncritical_by_length,
        "noncritical_row_digest_sha256": row_digest(sorted(noncritical_rows)),
        "direct_critical_scan": {
            "q_maximum": DIRECT_CRITICAL_Q_MAXIMUM,
            "profile_count": direct_count,
            "integral_count": 0,
            "by_q": direct_by_q,
            "row_digest_sha256": direct_digest.hexdigest(),
            "interpretation": "finite falsification only; the q>=61 theorem uses the sparse-arc inequality and EXT05",
        },
        "row_fields": "q,L,profile_support,Q_nonzero_coefficients,M,l1,W,R,Q(gamma) mod D,B mod D",
        "stored_samples": samples[:64],
        "row_storage": "omitted; independent verifier regenerates every declared row",
        "finite_boundary": "The finite remainder is complete only for area two in its declared critical/noncritical ranges.",
        "proves_collatz": False,
    }


def circular_width_of_residues(points: Sequence[int], modulus: int, *, last_tie: bool = False) -> int:
    ordered = sorted(points)
    gaps = []
    for index, point in enumerate(ordered):
        following = ordered[(index + 1) % len(ordered)]
        if index + 1 == len(ordered):
            following += modulus
        gaps.append(following - point)
    largest = max(gaps)
    candidates = [index for index, gap in enumerate(gaps) if gap == largest]
    _ = candidates[-1] if last_tie else candidates[0]
    return modulus - largest


def area_three_diagnostic_artifact() -> dict[str, object]:
    total = 0
    by_q = []
    worst_q: tuple[int, int, object] = (0, 1, None)
    worst_effective: tuple[int, int, object] = (0, 1, None)
    digest = hashlib.sha256()
    threshold_failures = []
    maximum_support = 0
    for q in range(1, AREA_THREE_Q_MAXIMUM + 1):
        L = critical_length(q)
        q_rows = []
        if L < 2 * q and math.gcd(q, L) == 1:
            inverse_q = pow(q, -1, L)
            for profile in area_three_profiles(q, L):
                if not profile_valid(q, L, profile) or sum(profile) != 3:
                    raise AssertionError("area-three classification")
                coefficients = reduced_polynomial(profile)
                support = tuple(index for index, value in enumerate(coefficients) if value)
                maximum_support = max(maximum_support, len(support))
                q_points = [(-index * pow(L, -1, q)) % q for index in support]
                L_points = [(index * inverse_q) % L for index in support]
                Wq = circular_width_of_residues(q_points, q)
                WL = circular_width_of_residues(L_points, L)
                data = [q, L, tuple(index for index, value in enumerate(profile) if value), tuple(profile[index] for index, value in enumerate(profile) if value), support, Wq, WL]
                q_rows.append(data)
                total += 1
                if Wq * worst_q[1] > worst_q[0] * q:
                    worst_q = (Wq, q, data)
                numerator, denominator = (Wq, q) if Wq * L <= WL * q else (WL, L)
                if numerator * worst_effective[1] > worst_effective[0] * denominator:
                    worst_effective = (numerator, denominator, data)
                if 3**numerator * 25**denominator >= 64**denominator:
                    threshold_failures.append(data)
        for row in sorted(q_rows):
            update_digest(digest, row)
        by_q.append([q, L, len(q_rows)])
    return {
        "format": "collatz-phase24-area-three-diagnostic-v1",
        "claims": {"E36": "VERIFIED_FINITE", "H147": "OPEN"},
        "scope": {
            "q_maximum": AREA_THREE_Q_MAXIMUM,
            "critical_only": True,
            "coprime_only": True,
            "area": 3,
        },
        "valid_profile_count": total,
        "by_q": by_q,
        "maximum_Q_support": maximum_support,
        "row_digest_sha256": digest.hexdigest(),
        "worst_q_arc": {
            "numerator": worst_q[0],
            "denominator": worst_q[1],
            "row": worst_q[2],
        },
        "worst_two_sided_effective_arc": {
            "numerator": worst_effective[0],
            "denominator": worst_effective[1],
            "row": worst_effective[2],
        },
        "threshold_comparison": "3^W*25^denominator < 64^denominator, equivalent to W/denominator < log_3(64/25)",
        "threshold_failure_count": len(threshold_failures),
        "smallest_threshold_failure": threshold_failures[0] if threshold_failures else None,
        "interpretation": "finite diagnostic only; no uniform eta or all-q area-three theorem is claimed",
        "proves_collatz": False,
    }


def rotations(values: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
    for offset in range(len(values)):
        yield values[offset:] + values[:offset]


def prefix_heights(exponents: tuple[int, ...]) -> tuple[int, ...]:
    q, L = len(exponents), sum(exponents)
    height = 0
    answer = []
    for exponent in exponents:
        answer.append(height)
        height += q * exponent - L
    if height:
        raise AssertionError("height closure")
    return tuple(answer)


def profile_of_word(exponents: tuple[int, ...]) -> tuple[int, ...] | None:
    q, L = len(exponents), sum(exponents)
    if math.gcd(q, L) != 1:
        return None
    canonical = next((word for word in rotations(exponents) if min(prefix_heights(word)) == 0), None)
    if canonical is None:
        raise AssertionError("minimum rotation")
    profile = [-1] * q
    for height in prefix_heights(canonical):
        profile[height % q] = height // q
    if profile[0] != 0 or min(profile) < 0:
        raise AssertionError("profile from word")
    return tuple(profile)


def word_exponents(bits: str) -> tuple[int, ...]:
    start = bits.index("1")
    word = bits[start:] + bits[:start]
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    return tuple((positions[(index + 1) % len(positions)] - position) % len(word) or len(word) for index, position in enumerate(positions))


def regression_artifact() -> dict[str, object]:
    named_bits = [("A", A_BITS), ("B", B_BITS)]
    for r in range(1, 4):
        for s in range(1, 4):
            named_bits.append((f"A^{r}B^{s}", A_BITS * r + B_BITS * s))
    named_bits.extend([("(110)^4", "110" * 4), ("(111)^4", "111" * 4), ("mixed-(110|111)", "110111110111")])
    word_rows = []
    for name, bits in named_bits:
        exponents = word_exponents(bits)
        profile = profile_of_word(exponents)
        sparse = None
        if profile is not None and 2 ** sum(exponents) > 3 ** len(exponents):
            sparse = sparse_arc_certificate(reduced_polynomial(profile), len(profile), sum(exponents))
        word_rows.append([name, bits, list(exponents), list(profile) if profile is not None else None, sparse])

    numeric = []
    for family in ("2^m-1", "8^m-5"):
        for m in range(2, 13):
            source = 2**m - 1 if family == "2^m-1" else 8**m - 5
            current = source
            seen = set()
            for steps in range(257):
                if current == 1 or current in seen or steps == 256:
                    numeric.append([family, m, source, steps, current, current == 1])
                    break
                seen.add(current)
                current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2

    edge_cases = []
    tie_case = None
    boundary_case = None
    cancellation_case = None
    for q in range(2, 30):
        L = critical_length(q)
        if L >= 2 * q or math.gcd(q, L) != 1:
            continue
        for profile in area_two_profiles(q, L):
            coefficients = reduced_polynomial(profile)
            first = sparse_arc_certificate(coefficients, q, L)
            last = sparse_arc_certificate(coefficients, q, L, last_tie=True)
            row = [q, L, list(profile), list(coefficients), first, last]
            support = [index for index, value in enumerate(profile) if value]
            if tie_case is None and first["largest_gap"] == last["largest_gap"] and first["b_lifts"] != last["b_lifts"]:
                tie_case = row
            if boundary_case is None and support[-1] == q - 1 and coefficients[0] == 3:
                boundary_case = row
            if cancellation_case is None and len(first["support"]) < 5:
                cancellation_case = row
    for name, row in (("largest-gap-tie", tie_case), ("boundary-coefficient-3", boundary_case), ("adjacent-root-cancellation", cancellation_case)):
        if row is None:
            raise AssertionError(f"missing regression {name}")
        edge_cases.append([name, row])

    return {
        "format": "collatz-phase24-regressions-v1",
        "mandatory_word_families": word_rows,
        "numeric_prefix_families": numeric,
        "edge_cases": edge_cases,
        "cycle_controls": {
            "trivial_positive": {"q": 1, "L": 2, "D": 1, "scope": "area zero; slope-root modulus D>1 is intentionally unavailable"},
            "negative_q2": {"exponents": [1, 2], "D": -1, "source": -5, "scope": "sign control only"},
            "negative_q7": {"exponents": [1, 1, 1, 2, 1, 1, 4], "D": -139, "source": -17, "scope": "sign/resultant control only"},
        },
        "tamper_boundaries": ["strict inequalities must not be weakened", "proves_collatz must remain false"],
        "proves_collatz": False,
    }


def obstruction_markdown(area_three: dict[str, object]) -> str:
    worst_q = area_three["worst_q_arc"]
    worst_two = area_three["worst_two_sided_effective_arc"]
    return f"""# Phase 24 obstruction report

## Exact result at area two

The sparse circular-arc certificate and the exact residue-profile recurrence
exclude every coprime area-two positive cycle profile.  The critical large-q
step uses EXT05; the critical `q<=60` and noncritical `L<=21` remainders are
independently exhaustive.

## Smallest next obstruction

At area three the reduced polynomial can have seven nonzero terms.  The generic
largest-gap estimate gives only `W/q<=6/7`, while
`3^6*25^7 > 64^7`; cardinality alone therefore misses the EXT05 exponent.

The bounded diagnostic through `q<={AREA_THREE_Q_MAXIMUM}` reconstructed
`{area_three['valid_profile_count']}` valid critical coprime area-three
profiles.  Its worst one-sided q-arc ratio is
`{worst_q['numerator']}/{worst_q['denominator']}`.  Allowing the diagnostic
q/L symmetric choice gives worst effective ratio
`{worst_two['numerator']}/{worst_two['denominator']}`.  There were
`{area_three['threshold_failure_count']}` failures of the exact comparison
`3^W*25^d<64^d` in this finite scope.

This is a finite diagnostic only (`VERIFIED_FINITE`), not an all-q theorem.
The missing step is a uniform
paired-support gap for the valid area-three shapes, followed by a mechanism for
arbitrary area.  General noncoprime profiles remain outside the coprime slope
root bijection.

## What this result does not prove

It does not exclude area-three or arbitrary-area coprime cycles, noncoprime
cycles, any nonperiodic counterexample branch, or the Collatz conjecture.
`proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)

    theory = theory_artifact()
    finite = finite_remainder_artifact()
    area_three = area_three_diagnostic_artifact()
    regressions = regression_artifact()
    obstruction = obstruction_markdown(area_three)

    write_json(args.artifact_dir / "phase24_theory.json", theory)
    write_json(args.artifact_dir / "phase24_area_two_remainder.json", finite)
    write_json(args.artifact_dir / "phase24_area_three_diagnostic.json", area_three)
    write_json(args.artifact_dir / "phase24_regressions.json", regressions)
    (args.artifact_dir / "phase24_obstruction_report.md").write_text(obstruction, encoding="utf-8")
    print(json.dumps({
        "valid": True,
        "critical_remainder_profiles": finite["critical_profile_count"],
        "noncritical_remainder_profiles": finite["noncritical_profile_count"],
        "direct_critical_profiles": finite["direct_critical_scan"]["profile_count"],
        "area_three_profiles": area_three["valid_profile_count"],
        "proves_collatz": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
