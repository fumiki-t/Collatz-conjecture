#!/usr/bin/env python3
"""Independent exact verifier for Phase 25 artifacts.

This file imports no production search module.  It regenerates critical words,
weak area-three profiles, rational intervals, modular witnesses, and resultants
with independently written routines.  Resultants use a Sylvester determinant,
whereas the generator uses a quotient-ring norm.
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


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q0 = 72_057_431_991
K0 = 114_208_327_604
V = 2_392_312_122_059_207_475_200
CRITICAL_Q_MAXIMUM = 17
CRITICAL_FACTOR_Q_MAXIMUM = 12
CYCLE_Q_MAXIMUM = 50
FILES = (
    "phase25_theory.json",
    "phase25_critical_support.json",
    "phase25_cycle_support.json",
    "phase25_resonance.json",
    "phase25_regressions.json",
    "phase25_obstruction_report.md",
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


def update_digest(digest: object, row: object) -> None:
    digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def fraction(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        fail("invalid fraction encoding")
    return Fraction(int(value[0]), int(value[1]))


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def ceil_log2_ratio(numerator: int, denominator: int) -> int:
    if numerator <= 0 or denominator <= 0:
        fail("positive logarithm ratio required")
    answer = max(0, numerator.bit_length() - denominator.bit_length())
    while (1 << answer) * denominator < numerator:
        answer += 1
    while answer and (1 << (answer - 1)) * denominator >= numerator:
        answer -= 1
    return answer


def critical_heights(maximum: int) -> dict[int, tuple[int, int, int, int]]:
    result = {}
    power3 = 1
    affine = 0
    for q in range(1, maximum + 1):
        affine = 3 * affine + (1 << (power3.bit_length() - 1))
        power3 *= 3
        K = power3.bit_length()
        D = (1 << K) - power3
        n = ceil_log2_ratio(3 * affine + q * D, D)
        result[q] = affine, D, K, n
    return result


def critical_stream(maximum: int) -> Iterator[tuple[int, str, int]]:
    targets = {pow(3, q).bit_length() - 1: q for q in range(1, maximum + 1)}
    active = [("", 0, 0)]
    for length in range(1, max(targets) + 1):
        following = []
        for bits, odd, affine in active:
            if odd and pow(3, odd) > 1 << length:
                following.append((bits + "0", odd, affine))
            if odd < maximum and pow(3, odd + 1) > 1 << length:
                following.append((bits + "1", odd + 1, 3 * affine + (1 << (length - 1))))
        active = following
        target = targets.get(length)
        if target is not None:
            for bits, odd, affine in active:
                if odd == target:
                    yield target, bits + "0", affine


def mechanical(q: int) -> tuple[str, tuple[int, ...]]:
    length = pow(3, q).bit_length()
    positions = tuple(pow(3, rank).bit_length() - 1 for rank in range(q))
    bits = ["0"] * length
    for position in positions:
        bits[position] = "1"
    return "".join(bits), positions


def linear_factors(word: str, width: int) -> set[str]:
    return {word[start : start + width] for start in range(len(word) - width + 1)}


def cyclic_factors(word: str, width: int) -> set[str]:
    repeated = word * ((width + len(word) - 1) // len(word) + 1)
    return {repeated[start : start + width] for start in range(len(word))}


def literal_trace(source: int, length: int) -> tuple[str, list[int]]:
    bits = []
    states = [source]
    current = source
    for _ in range(length):
        bits.append("1" if current & 1 else "0")
        current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2
        states.append(current)
    return "".join(bits), states


def least_source(word: str, affine: int) -> int:
    modulus = 1 << len(word)
    value = (-affine * pow(pow(3, word.count("1")), -1, modulus)) % modulus
    return value or modulus


def support_lower(q: int, n: int) -> int:
    return max(0, ceil_fraction(Fraction(q - 2 * n - 2, 2 * n + 1)))


def verify_critical(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase25-critical-support-v1" or stored.get("proves_collatz") is not False:
        fail("critical metadata")
    expected_claims = {"P151": "VERIFIED_THEOREM", "P152": "CONDITIONAL", "E37": "VERIFIED_FINITE"}
    if stored.get("claims") != expected_claims:
        fail("critical claim statuses")
    heights = critical_heights(CRITICAL_Q_MAXIMUM)
    counts = {
        q: {
            "critical_words": 0, "support_sum": 0, "minimum_support": None,
            "maximum_support": 0, "maximum_hamming": 0, "hamming_equality_count": 0,
            "factor_checks": 0, "bounded_distinct_rows": 0, "support_bound_rejections": 0,
            "support_lower_bound": support_lower(q, heights[q][3]),
        }
        for q in range(1, CRITICAL_Q_MAXIMUM + 1)
    }
    digest = hashlib.sha256()
    best: tuple[int, int, object] = (0, 1, None)
    for q, word, affine in critical_stream(CRITICAL_Q_MAXIMUM):
        base, base_positions = mechanical(q)
        actual_positions = tuple(index for index, bit in enumerate(word) if bit == "1")
        defects = tuple(old - new for old, new in zip(base_positions, actual_positions, strict=True))
        if any(value < 0 for value in defects):
            fail("critical position dominance")
        area = sum(defects)
        support = sum(value > 0 for value in defects)
        distance = sum(left != right for left, right in zip(base, word, strict=True))
        if distance > 2 * support:
            fail("critical Hamming bound")
        row = counts[q]
        row["critical_words"] += 1
        row["support_sum"] += support
        row["minimum_support"] = support if row["minimum_support"] is None else min(row["minimum_support"], support)
        row["maximum_support"] = max(row["maximum_support"], support)
        row["maximum_hamming"] = max(row["maximum_hamming"], distance)
        row["hamming_equality_count"] += distance == 2 * support
        if q <= CRITICAL_FACTOR_Q_MAXIMUM:
            for width in range(1, len(word) + 1):
                actual = len(linear_factors(word, width))
                base_count = len(linear_factors(base, width))
                bound = (2 * support + 1) * width + 2
                if actual > base_count + width * distance or base_count > width + 2 or actual > bound:
                    fail("critical factor bound")
                row["factor_checks"] += 1
                candidate = (actual, bound, [q, word, width, support, distance])
                if candidate[0] * best[1] > best[0] * candidate[1]:
                    best = candidate
        b_max, D, K, n = heights[q]
        source = least_source(word, affine)
        bounded_distinct = False
        rejected = False
        if source * D <= b_max:
            literal, states = literal_trace(source, K)
            if literal != word:
                fail("critical literal source")
            bounded_distinct = len(states) == len(set(states))
            if bounded_distinct:
                row["bounded_distinct_rows"] += 1
                rejected = support < support_lower(q, n)
                row["support_bound_rejections"] += rejected
        update_digest(digest, [q, word, affine, source, area, support, distance, n, int(bounded_distinct), int(rejected)])
    totals = {
        "critical_words": sum(row["critical_words"] for row in counts.values()),
        "factor_checks": sum(row["factor_checks"] for row in counts.values()),
        "bounded_distinct_rows": sum(row["bounded_distinct_rows"] for row in counts.values()),
        "support_bound_rejections": sum(row["support_bound_rejections"] for row in counts.values()),
    }
    if stored.get("counts_by_q") != {str(q): value for q, value in counts.items()} or stored.get("totals") != totals:
        fail("critical finite counts")
    if stored.get("row_digest_sha256") != digest.hexdigest():
        fail("critical row digest")
    if stored.get("maximum_factor_bound_ratio") != {"numerator": best[0], "denominator": best[1], "witness": best[2]}:
        fail("critical factor ratio")
    return totals


def critical_length(q: int) -> int:
    return pow(3, q).bit_length()


def literal_exponents(q: int, L: int, profile: Sequence[int]) -> tuple[int, ...] | None:
    if len(profile) != q or profile[0] != 0 or any(value < 0 for value in profile) or math.gcd(q, L) != 1:
        return None
    heights = [((-L * time) % q) + q * profile[(-L * time) % q] for time in range(q)]
    result = []
    for index, height in enumerate(heights):
        following = heights[index + 1] if index + 1 < q else 0
        exponent, remainder = divmod(following - height + L, q)
        if remainder or exponent <= 0:
            return None
        result.append(exponent)
    return tuple(result) if sum(result) == L else None


def weak_area_three(q: int, L: int) -> Iterator[tuple[int, ...]]:
    for cells in itertools.combinations_with_replacement(range(1, q), 3):
        profile = [0] * q
        for cell in cells:
            profile[cell] += 1
        profile_tuple = tuple(profile)
        if literal_exponents(q, L, profile_tuple) is not None:
            yield profile_tuple


def expanded(exponents: Sequence[int]) -> str:
    return "".join("1" + "0" * (value - 1) for value in exponents)


def profile_type(profile: Sequence[int], q: int, L: int) -> str:
    support = [index for index, value in enumerate(profile) if value]
    if max(profile) == 2:
        return "doubled-root"
    if any(index >= L - q for index in support):
        return "root-child-plus-root"
    return "three-roots"


def verify_cycle(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase25-cycle-support-v1" or stored.get("proves_collatz") is not False:
        fail("cycle metadata")
    expected = {"doubled-root": 2, "root-child-plus-root": 4, "three-roots": 6}
    counts = {key: 0 for key in expected}
    samples = {}
    factor_checks = 0
    rows = []
    total = 0
    for q in range(1, CYCLE_Q_MAXIMUM + 1):
        L = critical_length(q)
        if L >= 2 * q or math.gcd(q, L) != 1:
            continue
        zero = literal_exponents(q, L, (0,) * q)
        if zero is None:
            fail("cycle baseline")
        base = expanded(zero)
        for profile in weak_area_three(q, L):
            word_exponents = literal_exponents(q, L, profile)
            if word_exponents is None:
                fail("cycle weak profile")
            word = expanded(word_exponents)
            kind = profile_type(profile, q, L)
            support = sum(value > 0 for value in profile)
            distance = sum(a != b for a, b in zip(base, word, strict=True))
            if distance != expected[kind] or distance > 2 * support:
                fail("cycle Hamming classification")
            counts[kind] += 1
            total += 1
            if kind not in samples:
                samples[kind] = [q, L, list(profile), list(word_exponents), base, word, distance]
            for width in sorted({1, 2, 3, max(1, L // 2), L}):
                actual = len(cyclic_factors(word, width))
                baseline = len(cyclic_factors(base, width))
                if baseline > width + 1 or actual > baseline + width * distance or actual > (2 * support + 1) * width + 1:
                    fail("cycle factor bound")
                factor_checks += 1
            rows.append([q, L, list(profile), kind, support, distance])
    digest = hashlib.sha256()
    for row in sorted(rows):
        update_digest(digest, row)
    if stored.get("profile_count") != total or stored.get("counts_by_type") != counts:
        fail("cycle counts")
    if stored.get("expected_hamming_by_type") != expected or stored.get("factor_checks") != factor_checks:
        fail("cycle metadata counts")
    if stored.get("samples") != samples or stored.get("row_digest_sha256") != digest.hexdigest():
        fail("cycle samples or digest")
    return counts


def log_bounds(value: int, terms: int = 192) -> tuple[Fraction, Fraction]:
    z = Fraction(value - 1, value + 1)
    z2 = z * z
    term = z
    total = Fraction(0)
    for index in range(terms):
        total += term / (2 * index + 1)
        term *= z2
    lower = 2 * total
    upper = lower + 2 * term / ((2 * terms + 1) * (1 - z2))
    return lower, upper


def exp_minus_one_bounds(lower: Fraction, upper: Fraction, terms: int = 22) -> tuple[Fraction, Fraction]:
    def bound(value: Fraction) -> tuple[Fraction, Fraction]:
        total = Fraction(1)
        term = Fraction(1)
        for index in range(1, terms + 1):
            term *= value / index
            total += term
        following = term * value / (terms + 1)
        return total - 1, total + following / (1 - value / (terms + 2)) - 1
    return bound(lower)[0], bound(upper)[1]


def verify_q0(theory: dict[str, object]) -> None:
    critical = theory.get("critical_support")
    if not isinstance(critical, dict):
        fail("theory critical support")
    q0 = critical.get("q0_certificate")
    if not isinstance(q0, dict) or q0.get("q") != Q0 or q0.get("K") != K0:
        fail("q0 metadata")
    if q0.get("external_dependencies") != ["EXT04", "X02"]:
        fail("q0 dependency boundary")
    ln2 = log_bounds(2)
    ln3 = log_bounds(3)
    delta = exp_minus_one_bounds(K0 * ln2[0] - Q0 * ln3[1], K0 * ln2[1] - Q0 * ln3[0])
    stored_delta = q0.get("delta_interval")
    stored_s0 = q0.get("S0_interval_under_EXT04")
    stored_height = q0.get("height_ratio_interval")
    if not all(isinstance(value, dict) for value in (stored_delta, stored_s0, stored_height)):
        fail("q0 intervals")
    delta_low, delta_high = fraction(stored_delta["lower"]), fraction(stored_delta["upper"])
    if not (delta_low <= delta[0] <= delta[1] <= delta_high):
        fail("q0 delta enclosure")
    s0_independent = (Fraction(Q0, 2) / ln2[1] - 2, Fraction(Q0, 2) / ln2[0] + 2)
    s0_low, s0_high = fraction(stored_s0["lower"]), fraction(stored_s0["upper"])
    if not (s0_low <= s0_independent[0] <= s0_independent[1] <= s0_high):
        fail("q0 S0 enclosure")
    independent_height = (s0_independent[0] / delta[1] + Q0, s0_independent[1] / delta[0] + Q0)
    height_low, height_high = fraction(stored_height["lower"]), fraction(stored_height["upper"])
    if not (height_low <= independent_height[0] <= independent_height[1] <= height_high):
        fail("q0 height enclosure")
    if not 2**72 < height_low <= height_high <= 2**73 or q0.get("integer_width_n_q0") != 73:
        fail("q0 width")
    if q0.get("conditional_support_lower") != support_lower(Q0, 73):
        fail("q0 support lower")
    strict_upper = 4 * (s0_high - 3 * V * delta_low)
    if q0.get("conditional_support_upper_from_X02") != ceil_fraction(strict_upper) - 1:
        fail("q0 support upper")
    if q0.get("squeeze_excludes_q0") is not False:
        fail("q0 overclaim")


def polynomial_add(left: Sequence[int], right: Sequence[int], scale: int = 1) -> list[int]:
    result = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += scale * value
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def polynomial_multiply(left: Sequence[int], right: Sequence[int]) -> list[int]:
    result = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def polynomial_power(base: Sequence[int], exponent: int) -> list[int]:
    result = [1]
    for _ in range(exponent):
        result = polynomial_multiply(result, base)
    return result


def determinant(matrix: Sequence[Sequence[int]]) -> int:
    work = [list(row) for row in matrix]
    n = len(work)
    sign = 1
    divisor = 1
    for pivot_index in range(n - 1):
        if work[pivot_index][pivot_index] == 0:
            swap = next((row for row in range(pivot_index + 1, n) if work[row][pivot_index]), None)
            if swap is None:
                return 0
            work[pivot_index], work[swap] = work[swap], work[pivot_index]
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, n):
            for column in range(pivot_index + 1, n):
                value = work[row][column] * pivot - work[row][pivot_index] * work[pivot_index][column]
                if value % divisor:
                    fail("Sylvester exact division")
                work[row][column] = value // divisor
        divisor = pivot
        for row in range(pivot_index + 1, n):
            work[row][pivot_index] = 0
    return sign * work[-1][-1]


def sylvester_resultant(low_first_f: Sequence[int], low_first_g: Sequence[int]) -> int:
    f = list(reversed(low_first_f))
    g = list(reversed(low_first_g))
    m, n = len(f) - 1, len(g) - 1
    matrix = []
    for shift in range(n):
        matrix.append([0] * shift + f + [0] * (n - 1 - shift))
    for shift in range(m):
        matrix.append([0] * shift + g + [0] * (m - 1 - shift))
    return determinant(matrix)


def extended_gcd(left: int, right: int) -> tuple[int, int, int]:
    if right == 0:
        return left, 1, 0
    divisor, x, y = extended_gcd(right, left % right)
    return divisor, y, x - (left // right) * y


def signed_power(base: int, exponent: int, modulus: int) -> int:
    return pow(pow(base, -1, modulus), -exponent, modulus) if exponent < 0 else pow(base, exponent, modulus)


def gamma(q: int, L: int, D: int) -> int:
    divisor, u, v = extended_gcd(q, L)
    if divisor != 1:
        fail("coprime gamma")
    # Shift the Bezout pair away from the generator's choice.
    u -= L
    v += q
    value = signed_power(2, u, D) * signed_power(3, v, D) % D
    if pow(value, q, D) != 2 % D or pow(value, L, D) != 3 % D:
        fail("gamma identities")
    return value


def reduced_polynomial(profile: Sequence[int]) -> list[int]:
    q = len(profile)
    result = [0] * q
    result[0] = 1
    for index, height in enumerate(profile):
        coefficient = 2**height - 1
        result[index] -= coefficient
        result[(index + 1) % q] += coefficient * (2 if index + 1 == q else 1)
    return result


def circular_width(points: Sequence[int], modulus: int) -> int:
    ordered = sorted(points)
    gaps = [ordered[(i + 1) % len(ordered)] + (modulus if i + 1 == len(ordered) else 0) - value for i, value in enumerate(ordered)]
    return modulus - max(gaps)


def arctan_bounds(value: Fraction, terms: int = 22) -> tuple[Fraction, Fraction]:
    partial = sum(((-1) ** index) * value ** (2 * index + 1) / (2 * index + 1) for index in range(terms))
    following = ((-1) ** terms) * value ** (2 * terms + 1) / (2 * terms + 1)
    return min(partial, partial + following), max(partial, partial + following)


def pi_bounds() -> tuple[Fraction, Fraction]:
    a = arctan_bounds(Fraction(1, 5))
    b = arctan_bounds(Fraction(1, 239))
    return 4 * (4 * a[0] - b[1]), 4 * (4 * a[1] - b[0])


def seventh_root_bounds(steps: int = 48) -> tuple[Fraction, Fraction]:
    lower, upper = Fraction(1), Fraction(2)
    for _ in range(steps):
        middle = (lower + upper) / 2
        if middle**7 < 2:
            lower = middle
        else:
            upper = middle
    return lower, upper


def cosine_point(value: Fraction, terms: int = 22) -> tuple[Fraction, Fraction]:
    partial = sum(((-1) ** index) * value ** (2 * index) / math.factorial(2 * index) for index in range(terms))
    following = ((-1) ** terms) * value ** (2 * terms) / math.factorial(2 * terms)
    return min(partial, partial + following), max(partial, partial + following)


def conjugate_intervals() -> dict[str, tuple[Fraction, Fraction]]:
    pi = pi_bounds()
    theta = seventh_root_bounds()
    powers = {1: theta, 2: (theta[0] ** 2, theta[1] ** 2), 3: (theta[0] ** 3, theta[1] ** 3)}
    cosines = {}
    for r in (1, 2, 3):
        low_angle, high_angle = Fraction(r, 7) * pi[0], Fraction(r, 7) * pi[1]
        cosines[r] = (cosine_point(high_angle)[0], cosine_point(low_angle)[1])
    products = {(power, r): (powers[power][0] * cosines[r][0], powers[power][1] * cosines[r][1]) for power in powers for r in cosines}
    expressions = {
        1: ((1, 2, 1), (-1, 3, 2), (-1, 1, 3)),
        2: ((-1, 3, 1), (-1, 1, 2), (1, 2, 3)),
        3: ((-1, 1, 1), (1, 2, 2), (-1, 3, 3)),
    }
    result = {}
    for key, terms in expressions.items():
        lower = upper = Fraction(0)
        for sign, r, power in terms:
            interval = products[(power, r)]
            if sign > 0:
                lower += interval[0]
                upper += interval[1]
            else:
                lower -= interval[1]
                upper -= interval[0]
        result[str(key)] = lower, upper
    return result


def verify_resonance(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase25-resonance-v1" or stored.get("proves_collatz") is not False:
        fail("resonance metadata")
    seven = stored.get("seven_grid")
    falsifier = stored.get("paired_arc_falsifier")
    if not isinstance(seven, dict) or not isinstance(falsifier, dict):
        fail("resonance sections")
    P = [0, 1, 1, 1]
    f = [-2] + [0] * 6 + [1]
    norm = sylvester_resultant(f, polynomial_add(P, [-1]))
    if abs(norm) != 209 or seven.get("absolute_resultant_Z7_minus_2_P_minus_1") != 209:
        fail("seven-grid norm")
    independent_conjugates = conjugate_intervals()
    stored_conjugates = seven.get("nonreal_Re_P_intervals")
    if not isinstance(stored_conjugates, dict):
        fail("conjugate intervals")
    for key, interval in independent_conjugates.items():
        stored_interval = stored_conjugates.get(key)
        if not isinstance(stored_interval, list) or len(stored_interval) != 2:
            fail("stored conjugate interval")
        low, high = fraction(stored_interval[0]), fraction(stored_interval[1])
        if not (low <= interval[0] <= interval[1] <= high < Fraction(1, 2)):
            fail("conjugate maximum selection")
    if not 627 * 25**7 < 2 * 64**7 or seven.get("M_below_64_over_25") is not True:
        fail("M comparison")
    threshold_rows = []
    for Q in range(1, 12):
        left = 2 * 3**7 * 627**Q * 25 ** (7 * Q)
        right = 2**Q * 64 ** (7 * Q)
        threshold_rows.append([Q, str(left), str(right), left < right])
    if seven.get("threshold_rows_Q_1_to_11") != threshold_rows or seven.get("eventual_threshold_Q") != 11:
        fail("resonance threshold")
    finite_rows = []
    for Q in range(1, 11):
        q, L = 7 * Q, critical_length(7 * Q)
        R = polynomial_add(polynomial_power(polynomial_add(P, [-1]), Q), [0] + polynomial_power(P, Q), scale=-1)
        resultant = sylvester_resultant(f, R)
        row: dict[str, object] = {"Q": Q, "q": q, "L": L, "gcd_q_L": math.gcd(q, L), "resonant_resultant": str(resultant), "resultant_nonzero": resultant != 0}
        if math.gcd(q, L) == 1:
            profile = [0] * q
            for residue in (Q, 2 * Q, 3 * Q):
                profile[residue] = 1
            coefficients = reduced_polynomial(profile)
            D = 2**L - 3**q
            root = gamma(q, L, D)
            modular = sum(coefficient * pow(root, index, D) for index, coefficient in enumerate(coefficients) if coefficient) % D
            row.update({"D": str(D), "direct_modular_gcd": math.gcd(modular, D), "D_divides_resultant": resultant % D == 0, "integral_profile": modular == 0})
        else:
            row["scope_note"] = "noncoprime slope; P154/P155 do not apply"
        finite_rows.append(row)
    if seven.get("finite_rows_Q_1_to_10") != finite_rows:
        fail("finite resonance rows")

    q, L = 63_322, critical_length(63_322)
    profile = [0] * q
    for residue in (q // 7, 2 * q // 7, 3 * q // 7):
        profile[residue] = 1
    coefficients = reduced_polynomial(profile)
    support = [index for index, value in enumerate(coefficients) if value]
    q_points = sorted((-index * pow(L, -1, q)) % q for index in support)
    L_points = sorted((index * pow(q, -1, L)) % L for index in support)
    Wq, WL = circular_width(q_points, q), circular_width(L_points, L)
    D = 2**L - 3**q
    root = gamma(q, L, D)
    modular = sum(coefficient * pow(root, index, D) for index, coefficient in enumerate(coefficients) if coefficient) % D
    rebuilt = {
        "q": q, "L": L, "Q": q // 7, "gcd_q_L": 1,
        "profile_support": [q // 7, 2 * q // 7, 3 * q // 7], "polynomial_support": support,
        "q_arc_points": q_points, "q_arc_width": Wq, "L_arc_points": L_points, "L_arc_width": WL,
        "q_threshold_fails": 3**Wq * 25**q >= 64**q, "L_threshold_fails": 3**WL * 25**L >= 64**L,
        "direct_modular_gcd": math.gcd(modular, D), "integral_profile": modular == 0,
        "proposal_supplied_L_points": [0, 14488, 28675, 43163, 57350, 71838, 86025],
        "proposal_L_points_correct": False,
        "interpretation": "Exact counterexample to the naive two-arc width threshold, not a cycle witness.",
    }
    if falsifier != rebuilt:
        fail("paired arc falsifier")
    return {"norm": abs(norm), "falsifier_q": q, "falsifier_gcd": math.gcd(modular, D)}


def verify_regressions(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase25-regressions-v1" or stored.get("proves_collatz") is not False:
        fail("regression metadata")
    rows = stored.get("mandatory_word_families")
    if not isinstance(rows, list) or len(rows) != 14:
        fail("mandatory word rows")
    names = {row[0] for row in rows}
    required = {"A", "B", "(110|111)^*"} | {f"A^{r}B^{s}" for r in range(1, 4) for s in range(1, 4)}
    if not required <= names:
        fail("mandatory word families")
    for name, word, comparator, distance, checks in rows:
        if distance != sum(a != b for a, b in zip(word, comparator, strict=True)):
            fail(f"regression Hamming {name}")
        expected = []
        for width in range(1, len(word) + 1):
            actual = len(linear_factors(word, width))
            base = len(linear_factors(comparator, width))
            cyc_actual = len(cyclic_factors(word, width))
            cyc_base = len(cyclic_factors(comparator, width))
            if actual > base + width * distance or cyc_actual > cyc_base + width * distance:
                fail("regression factor bound")
            expected.append([width, actual, base, cyc_actual, cyc_base])
        if checks != expected:
            fail("regression stored checks")
    numeric = stored.get("numeric_prefix_families")
    if not isinstance(numeric, list) or {row[0] for row in numeric} != {"2^m-1", "8^m-5"}:
        fail("numeric adversarial families")


def verify_theory(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase25-theory-v1" or stored.get("proves_collatz") is not False:
        fail("theory metadata")
    claims = stored.get("claims")
    expected = {"P151": "VERIFIED_THEOREM", "P152": "CONDITIONAL", "P153": "CONDITIONAL", "P154": "VERIFIED_THEOREM", "P155": "VERIFIED_THEOREM", "E37": "VERIFIED_FINITE", "NG34": "REFUTED", "H147": "OPEN"}
    if not isinstance(claims, dict) or {key: value.get("status") for key, value in claims.items()} != expected:
        fail("theory claims")
    if "does not prove" not in str(stored.get("what_this_result_does_not_prove", "")).lower():
        fail("theory no-overclaim boundary")
    verify_q0(stored)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    theory = load(arguments.artifact_dir / "phase25_theory.json")
    critical = load(arguments.artifact_dir / "phase25_critical_support.json")
    cycle = load(arguments.artifact_dir / "phase25_cycle_support.json")
    resonance = load(arguments.artifact_dir / "phase25_resonance.json")
    regressions = load(arguments.artifact_dir / "phase25_regressions.json")
    verify_theory(theory)
    critical_result = verify_critical(critical)
    cycle_result = verify_cycle(cycle)
    resonance_result = verify_resonance(resonance)
    verify_regressions(regressions)
    report = (arguments.artifact_dir / "phase25_obstruction_report.md").read_text(encoding="utf-8")
    if "What this result does not prove" not in report or "proves_collatz=false" not in report:
        fail("obstruction report boundary")
    hashes = {name: hashlib.sha256((arguments.artifact_dir / name).read_bytes()).hexdigest() for name in FILES}
    result = {
        "format": "collatz-phase25-independent-verifier-v1",
        "valid": True,
        "claims": {"P151": "VERIFIED_THEOREM", "P152": "CONDITIONAL", "P153": "CONDITIONAL", "P154": "VERIFIED_THEOREM", "P155": "VERIFIED_THEOREM", "E37": "VERIFIED_FINITE", "NG34": "REFUTED", "H147": "OPEN"},
        "critical": critical_result,
        "cycle_type_counts": cycle_result,
        "resonance": resonance_result,
        "generator_imported": False,
        "independence": "weak area profiles, shifted Bezout root, rational intervals, and Sylvester resultants reconstructed without production imports",
        "verified_input_sha256": hashes,
        "what_this_result_does_not_prove": "This verifies the declared exact and conditional boundaries; it does not prove H147, H133, H89, H72, or Collatz.",
        "proves_collatz": False,
    }
    if arguments.output:
        save(arguments.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
