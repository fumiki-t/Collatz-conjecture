#!/usr/bin/env python3
"""Generate exact Phase 25 Hamming-support and resonance evidence.

The supplied Phase 25 note is an untrusted proposal.  This generator accepts
only statements reconstructed from the Phase 23/24 conventions.  Every proof
decision uses integers or rational intervals; floating point is not used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence

try:  # direct script execution
    from phase7_search import K0, Q0, V, exp_minus_one_interval, log_interval
    from phase23_search import (
        critical_prefixes,
        cyclic_factors,
        defect_data,
        expanded_word,
        factors,
        hq_rows,
        mechanical_word,
        shortcut_trace,
        source_for,
    )
    from phase24_search import (
        area_three_profiles,
        critical_length,
        exponents_of_profile,
        polynomial_value,
        profile_valid,
        reduced_polynomial,
        slope_root,
    )
except ModuleNotFoundError:  # pytest/package import
    from src.phase7_search import K0, Q0, V, exp_minus_one_interval, log_interval
    from src.phase23_search import (
        critical_prefixes,
        cyclic_factors,
        defect_data,
        expanded_word,
        factors,
        hq_rows,
        mechanical_word,
        shortcut_trace,
        source_for,
    )
    from src.phase24_search import (
        area_three_profiles,
        critical_length,
        exponents_of_profile,
        polynomial_value,
        profile_valid,
        reduced_polynomial,
        slope_root,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


CRITICAL_Q_MAXIMUM = 17
CRITICAL_FACTOR_Q_MAXIMUM = 12
CYCLE_Q_MAXIMUM = 50
RESONANCE_D = 7
RESONANCE_FINITE_Q = 10
PROPOSAL_FALSIFIER_Q = 63_322
A_BITS = "11101"
B_BITS = "1100"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_digest(digest: object, row: object) -> None:
    digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def ceil_fraction(value: Fraction) -> int:
    return -(-value.numerator // value.denominator)


def hamming(left: str, right: str) -> int:
    if len(left) != len(right):
        raise ValueError("Hamming distance requires equal lengths")
    return sum(a != b for a, b in zip(left, right, strict=True))


def linear_factors(word: str, width: int) -> set[str]:
    if not 1 <= width <= len(word):
        raise ValueError("linear factor width")
    return {word[start : start + width] for start in range(len(word) - width + 1)}


def critical_support_lower(q: int, n: int) -> int:
    return max(0, ceil_fraction(Fraction(q - 2 * n - 2, 2 * n + 1)))


def critical_support_audit() -> dict[str, object]:
    heights = hq_rows(CRITICAL_Q_MAXIMUM)
    counts = {
        q: {
            "critical_words": 0,
            "support_sum": 0,
            "minimum_support": None,
            "maximum_support": 0,
            "maximum_hamming": 0,
            "hamming_equality_count": 0,
            "factor_checks": 0,
            "bounded_distinct_rows": 0,
            "support_bound_rejections": 0,
            "support_lower_bound": critical_support_lower(q, heights[q][3]),
        }
        for q in range(1, CRITICAL_Q_MAXIMUM + 1)
    }
    digest = hashlib.sha256()
    maximum_ratio: tuple[int, int, object] = (0, 1, None)
    for q, word, affine in critical_prefixes(CRITICAL_Q_MAXIMUM):
        base, _ = mechanical_word(q)
        area, _, _, defects = defect_data(word, q)
        support = sum(value > 0 for value in defects)
        distance = hamming(base, word)
        if distance > 2 * support:
            raise AssertionError("critical Hamming support bound")
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
                bound = base_count + width * distance
                repaired = (2 * support + 1) * width + 2
                if base_count > width + 2 or actual > bound or actual > repaired:
                    raise AssertionError("critical factor perturbation")
                row["factor_checks"] += 1
                ratio = (actual, repaired, [q, word, width, support, distance])
                if ratio[0] * maximum_ratio[1] > maximum_ratio[0] * ratio[1]:
                    maximum_ratio = ratio

        b_max, D, K, n, _ = heights[q]
        source = source_for(word, affine)
        bounded_distinct = False
        rejected = False
        if source * D <= b_max:
            literal, states = shortcut_trace(source, K)
            if literal != word:
                raise AssertionError("critical source reconstruction")
            bounded_distinct = len(states) == len(set(states))
            if bounded_distinct:
                row["bounded_distinct_rows"] += 1
                rejected = support < critical_support_lower(q, n)
                row["support_bound_rejections"] += rejected
        digest_row = [q, word, affine, source, area, support, distance, n, int(bounded_distinct), int(rejected)]
        update_digest(digest, digest_row)

    return {
        "format": "collatz-phase25-critical-support-v1",
        "claims": {"P151": "VERIFIED_THEOREM", "P152": "CONDITIONAL", "E37": "VERIFIED_FINITE"},
        "scope": {
            "q_maximum": CRITICAL_Q_MAXIMUM,
            "literal_factor_q_maximum": CRITICAL_FACTOR_Q_MAXIMUM,
            "first_crossing_words": True,
        },
        "counts_by_q": {str(q): value for q, value in counts.items()},
        "totals": {
            "critical_words": sum(row["critical_words"] for row in counts.values()),
            "factor_checks": sum(row["factor_checks"] for row in counts.values()),
            "bounded_distinct_rows": sum(row["bounded_distinct_rows"] for row in counts.values()),
            "support_bound_rejections": sum(row["support_bound_rejections"] for row in counts.values()),
        },
        "maximum_factor_bound_ratio": {
            "numerator": maximum_ratio[0],
            "denominator": maximum_ratio[1],
            "witness": maximum_ratio[2],
        },
        "row_digest_sha256": digest.hexdigest(),
        "finite_boundary": "Complete through q<=17 for support/Hamming aggregates; literal factor checks through q<=12.",
        "proves_collatz": False,
    }


def q0_certificate() -> dict[str, object]:
    ln2_low, ln2_high = log_interval(2)
    ln3_low, ln3_high = log_interval(3)
    x_low = K0 * ln2_low - Q0 * ln3_high
    x_high = K0 * ln2_high - Q0 * ln3_low
    delta_low, delta_high = exp_minus_one_interval(x_low, x_high)
    # This S0 enclosure is the exact Phase 7 consequence of EXT04.
    s0_low = Fraction(Q0, 2) / ln2_high - 2
    s0_high = Fraction(Q0, 2) / ln2_low + 2
    height_low = s0_low / delta_high + Q0
    height_high = s0_high / delta_low + Q0
    if not (2**72 < height_low <= height_high <= 2**73):
        raise AssertionError("q0 integer width")
    n = 73
    support_lower = critical_support_lower(Q0, n)
    support_upper_strict = 4 * (s0_high - 3 * V * delta_low)
    support_upper_integer = ceil_fraction(support_upper_strict) - 1
    if support_upper_integer < support_lower:
        raise AssertionError("unexpected q0 support exclusion")
    return {
        "q": Q0,
        "K": K0,
        "external_dependencies": ["EXT04", "X02"],
        "delta_interval": {"lower": encode_fraction(delta_low), "upper": encode_fraction(delta_high)},
        "S0_interval_under_EXT04": {"lower": encode_fraction(s0_low), "upper": encode_fraction(s0_high)},
        "height_ratio_interval": {"lower": encode_fraction(height_low), "upper": encode_fraction(height_high)},
        "integer_width_n_q0": n,
        "width_checks": {"2^72_below_lower": True, "upper_at_most_2^73": True},
        "conditional_support_lower": support_lower,
        "conditional_support_upper_from_X02": support_upper_integer,
        "squeeze_excludes_q0": False,
        "boundary": "The lower support bound additionally assumes P54 and pairwise-distinct critical states. The upper support bound assumes P54 and X02. The S0 enclosure uses EXT04.",
    }


def area_three_type(profile: Sequence[int], q: int, L: int) -> str:
    support = [index for index, value in enumerate(profile) if value]
    m = L - q
    if max(profile) == 2:
        return "doubled-root"
    if any(index >= m for index in support):
        return "root-child-plus-root"
    return "three-roots"


def cycle_support_audit() -> dict[str, object]:
    expected_hamming = {"doubled-root": 2, "root-child-plus-root": 4, "three-roots": 6}
    counts = {key: 0 for key in expected_hamming}
    samples: dict[str, object] = {}
    factor_checks = 0
    total = 0
    digest = hashlib.sha256()
    digest_rows = []
    for q in range(1, CYCLE_Q_MAXIMUM + 1):
        L = critical_length(q)
        if L >= 2 * q or math.gcd(q, L) != 1:
            continue
        base_exponents = exponents_of_profile(q, L, (0,) * q)
        if base_exponents is None:
            raise AssertionError("profile-zero baseline")
        base = expanded_word(base_exponents)
        for profile in area_three_profiles(q, L):
            exponents = exponents_of_profile(q, L, profile)
            if exponents is None:
                raise AssertionError("classified area-three profile")
            word = expanded_word(exponents)
            kind = area_three_type(profile, q, L)
            support = sum(value > 0 for value in profile)
            distance = hamming(base, word)
            if distance > 2 * support or distance != expected_hamming[kind]:
                raise AssertionError("area-three literal Hamming classification")
            counts[kind] += 1
            total += 1
            if kind not in samples:
                samples[kind] = [q, L, list(profile), list(exponents), base, word, distance]
            widths = sorted({1, 2, 3, max(1, L // 2), L})
            for width in widths:
                actual = len(cyclic_factors(word, width))
                baseline = len(cyclic_factors(base, width))
                if baseline > width + 1 or actual > baseline + width * distance or actual > (2 * support + 1) * width + 1:
                    raise AssertionError("cycle factor perturbation")
                factor_checks += 1
            digest_rows.append([q, L, list(profile), kind, support, distance])
    for digest_row in sorted(digest_rows):
        update_digest(digest, digest_row)
    return {
        "format": "collatz-phase25-cycle-support-v1",
        "claims": {"P151": "VERIFIED_THEOREM", "E37": "VERIFIED_FINITE"},
        "scope": {"q_maximum": CYCLE_Q_MAXIMUM, "critical": True, "coprime": True, "area": 3},
        "profile_count": total,
        "counts_by_type": counts,
        "expected_hamming_by_type": expected_hamming,
        "factor_checks": factor_checks,
        "samples": samples,
        "row_digest_sha256": digest.hexdigest(),
        "proves_collatz": False,
    }


def polynomial_add(left: Sequence[int], right: Sequence[int], scale: int = 1) -> list[int]:
    answer = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += scale * value
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def polynomial_multiply(left: Sequence[int], right: Sequence[int]) -> list[int]:
    answer = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            answer[i + j] += a * b
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def polynomial_power(base: Sequence[int], exponent: int) -> list[int]:
    answer = [1]
    power = list(base)
    while exponent:
        if exponent & 1:
            answer = polynomial_multiply(answer, power)
        exponent //= 2
        if exponent:
            power = polynomial_multiply(power, power)
    return answer


def resonance_polynomial(Q: int, P: Sequence[int]) -> list[int]:
    minus_one = polynomial_add(P, [-1])
    first = polynomial_power(minus_one, Q)
    second = [0] + polynomial_power(P, Q)
    return polynomial_add(first, second, scale=-1)


def reduce_mod_zd_minus_two(polynomial: Sequence[int], d: int) -> list[int]:
    answer = [0] * d
    for exponent, coefficient in enumerate(polynomial):
        quotient, remainder = divmod(exponent, d)
        answer[remainder] += coefficient * 2**quotient
    return answer


def bareiss_determinant(matrix: Sequence[Sequence[int]]) -> int:
    work = [list(row) for row in matrix]
    n = len(work)
    if any(len(row) != n for row in work):
        raise ValueError("square matrix required")
    sign = 1
    previous = 1
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
                numerator = work[row][column] * pivot - work[row][pivot_index] * work[pivot_index][column]
                if numerator % previous:
                    raise AssertionError("Bareiss exact division")
                work[row][column] = numerator // previous
        previous = pivot
        for row in range(pivot_index + 1, n):
            work[row][pivot_index] = 0
    return sign * work[-1][-1]


def quotient_norm(polynomial: Sequence[int], d: int) -> int:
    reduced = reduce_mod_zd_minus_two(polynomial, d)
    matrix = [[0] * d for _ in range(d)]
    for column in range(d):
        for exponent, coefficient in enumerate(reduced):
            quotient, row = divmod(exponent + column, d)
            matrix[row][column] += coefficient * 2**quotient
    return bareiss_determinant(matrix)


def arctan_interval(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    partial = sum(((-1) ** index) * value ** (2 * index + 1) / (2 * index + 1) for index in range(terms))
    following = ((-1) ** terms) * value ** (2 * terms + 1) / (2 * terms + 1)
    return min(partial, partial + following), max(partial, partial + following)


def pi_interval(terms: int = 18) -> tuple[Fraction, Fraction]:
    a_low, a_high = arctan_interval(Fraction(1, 5), terms)
    b_low, b_high = arctan_interval(Fraction(1, 239), terms)
    return 4 * (4 * a_low - b_high), 4 * (4 * a_high - b_low)


def root_interval_of_two(degree: int, steps: int = 40) -> tuple[Fraction, Fraction]:
    lower, upper = Fraction(1), Fraction(2)
    for _ in range(steps):
        middle = (lower + upper) / 2
        if middle**degree < 2:
            lower = middle
        else:
            upper = middle
    return lower, upper


def cosine_at_rational_interval(value: Fraction, terms: int = 18) -> tuple[Fraction, Fraction]:
    partial = sum(((-1) ** index) * value ** (2 * index) / math.factorial(2 * index) for index in range(terms))
    following = ((-1) ** terms) * value ** (2 * terms) / math.factorial(2 * terms)
    return min(partial, partial + following), max(partial, partial + following)


def cosine_interval(lower: Fraction, upper: Fraction) -> tuple[Fraction, Fraction]:
    # The arguments below lie in (0,3/2), where cosine is decreasing.
    lower_value = cosine_at_rational_interval(upper)[0]
    upper_value = cosine_at_rational_interval(lower)[1]
    return lower_value, upper_value


def multiply_positive_intervals(left: tuple[Fraction, Fraction], right: tuple[Fraction, Fraction]) -> tuple[Fraction, Fraction]:
    if left[0] <= 0 or right[0] <= 0:
        raise ValueError("positive intervals required")
    return left[0] * right[0], left[1] * right[1]


def conjugate_real_part_intervals() -> dict[str, list[list[str]]]:
    pi_low, pi_high = pi_interval()
    theta = root_interval_of_two(7)
    theta2 = multiply_positive_intervals(theta, theta)
    theta3 = multiply_positive_intervals(theta2, theta)
    cosines = {
        r: cosine_interval(Fraction(r, 7) * pi_low, Fraction(r, 7) * pi_high)
        for r in (1, 2, 3)
    }
    products = {
        (power, r): multiply_positive_intervals({1: theta, 2: theta2, 3: theta3}[power], cosines[r])
        for power in (1, 2, 3)
        for r in (1, 2, 3)
    }
    expressions = {
        1: ((1, 2, 1), (-1, 3, 2), (-1, 1, 3)),
        2: ((-1, 3, 1), (-1, 1, 2), (1, 2, 3)),
        3: ((-1, 1, 1), (1, 2, 2), (-1, 3, 3)),
    }
    result = {}
    for conjugate, terms in expressions.items():
        lower = Fraction(0)
        upper = Fraction(0)
        for sign, r, power in terms:
            interval = products[(power, r)]
            if sign > 0:
                lower += interval[0]
                upper += interval[1]
            else:
                lower -= interval[1]
                upper -= interval[0]
        if upper >= Fraction(1, 2):
            raise AssertionError("nonreal conjugate maximum selection")
        denominator = 1_000_000
        coarse_lower = Fraction(lower.numerator * denominator // lower.denominator, denominator)
        coarse_upper = Fraction(ceil_fraction(upper * denominator), denominator)
        if not (coarse_lower <= lower <= upper <= coarse_upper < Fraction(1, 2)):
            raise AssertionError("coarsened conjugate interval")
        result[str(conjugate)] = [encode_fraction(coarse_lower), encode_fraction(coarse_upper)]
    return result


def circular_width(points: Sequence[int], modulus: int) -> int:
    ordered = sorted(points)
    gaps = [
        ordered[(index + 1) % len(ordered)] + (modulus if index + 1 == len(ordered) else 0) - point
        for index, point in enumerate(ordered)
    ]
    return modulus - max(gaps)


def seven_grid_profile(q: int) -> tuple[int, ...]:
    if q % 7:
        raise ValueError("seven-grid q")
    Q = q // 7
    profile = [0] * q
    for residue in (Q, 2 * Q, 3 * Q):
        profile[residue] = 1
    return tuple(profile)


def proposal_falsifier() -> dict[str, object]:
    q = PROPOSAL_FALSIFIER_Q
    L = critical_length(q)
    profile = seven_grid_profile(q)
    coefficients = reduced_polynomial(profile)
    support = [index for index, value in enumerate(coefficients) if value]
    q_points = sorted((-index * pow(L, -1, q)) % q for index in support)
    L_points = sorted((index * pow(q, -1, L)) % L for index in support)
    Wq = circular_width(q_points, q)
    WL = circular_width(L_points, L)
    if not (3**Wq * 25**q >= 64**q and 3**WL * 25**L >= 64**L):
        raise AssertionError("paired arc falsifier threshold")
    D = 2**L - 3**q
    gamma = slope_root(q, L, D)
    modular = polynomial_value(coefficients, gamma, D)
    divisor = math.gcd(modular, D)
    if divisor != 1:
        raise AssertionError("proposal falsifier direct gcd")
    supplied_L_points = [0, 14488, 28675, 43163, 57350, 71838, 86025]
    return {
        "q": q,
        "L": L,
        "Q": q // 7,
        "gcd_q_L": math.gcd(q, L),
        "profile_support": [q // 7, 2 * q // 7, 3 * q // 7],
        "polynomial_support": support,
        "q_arc_points": q_points,
        "q_arc_width": Wq,
        "L_arc_points": L_points,
        "L_arc_width": WL,
        "q_threshold_fails": True,
        "L_threshold_fails": True,
        "direct_modular_gcd": divisor,
        "integral_profile": False,
        "proposal_supplied_L_points": supplied_L_points,
        "proposal_L_points_correct": supplied_L_points == L_points,
        "interpretation": "Exact counterexample to the naive two-arc width threshold, not a cycle witness.",
    }


def resonance_artifact() -> dict[str, object]:
    P = [0, 1, 1, 1]
    norm_P_minus_one = quotient_norm(polynomial_add(P, [-1]), 7)
    if abs(norm_P_minus_one) != 209:
        raise AssertionError("seven-grid norm")
    conjugates = conjugate_real_part_intervals()
    if not 627 * 25**7 < 2 * 64**7:
        raise AssertionError("seven-grid spectral comparison")
    threshold_rows = []
    for Q in range(1, 12):
        left = 2 * 3**7 * 627**Q * 25 ** (7 * Q)
        right = 2**Q * 64 ** (7 * Q)
        threshold_rows.append([Q, str(left), str(right), left < right])
    if [row[0] for row in threshold_rows if row[3]][0] != 11:
        raise AssertionError("resonance threshold")

    finite_rows = []
    for Q in range(1, RESONANCE_FINITE_Q + 1):
        q = 7 * Q
        L = critical_length(q)
        R = resonance_polynomial(Q, P)
        resultant = quotient_norm(R, 7)
        row: dict[str, object] = {
            "Q": Q,
            "q": q,
            "L": L,
            "gcd_q_L": math.gcd(q, L),
            "resonant_resultant": str(resultant),
            "resultant_nonzero": resultant != 0,
        }
        if math.gcd(q, L) == 1:
            profile = seven_grid_profile(q)
            if not profile_valid(q, L, profile):
                raise AssertionError("finite seven-grid validity")
            coefficients = reduced_polynomial(profile)
            D = 2**L - 3**q
            gamma = slope_root(q, L, D)
            modular = polynomial_value(coefficients, gamma, D)
            row.update(
                {
                    "D": str(D),
                    "direct_modular_gcd": math.gcd(modular, D),
                    "D_divides_resultant": resultant % D == 0,
                    "integral_profile": modular == 0,
                }
            )
            if row["integral_profile"] or row["D_divides_resultant"]:
                raise AssertionError("finite seven-grid counterexample")
        else:
            row["scope_note"] = "noncoprime slope; P154/P155 do not apply"
        finite_rows.append(row)

    return {
        "format": "collatz-phase25-resonance-v1",
        "claims": {"P154": "VERIFIED_THEOREM", "P155": "VERIFIED_THEOREM", "E37": "VERIFIED_FINITE", "NG34": "REFUTED", "H147": "OPEN"},
        "resonant_grid": {
            "scope": "q=dQ, gcd(q,L)=1, roots c_i Q with no boundary wrap, D=2^L-3^q>1",
            "P": "sum_i Z^c_i",
            "R": "(P-1)^Q-ZP^Q",
            "divisibility": "integrality implies D divides Res(Z^d-2,R)",
            "nonvanishing": "for Q>=2, the norm equation would require Q*v2(N(alpha))=1",
            "magnitude": "|Res|<=(1+2^(1/d))^d M(d,P)^q",
        },
        "seven_grid": {
            "d": 7,
            "P_coefficients_low_to_high": P,
            "absolute_resultant_Z7_minus_2_P_minus_1": abs(norm_P_minus_one),
            "nonreal_Re_P_intervals": conjugates,
            "M7_upper": "627/2",
            "M_below_64_over_25": True,
            "eventual_threshold_Q": 11,
            "threshold_rows_Q_1_to_11": threshold_rows,
            "finite_rows_Q_1_to_10": finite_rows,
            "external_dependency": "EXT05 for coprime Q>=11; finite coprime Q<=10 are direct",
        },
        "paired_arc_falsifier": proposal_falsifier(),
        "what_this_result_does_not_prove": "It does not exclude near-resonant area-three profiles, arbitrary-area or noncoprime cycles, H89, H72, or Collatz.",
        "proves_collatz": False,
    }


def regression_artifact() -> dict[str, object]:
    pairs = []
    named = [("A", A_BITS), ("B", B_BITS)]
    for r in range(1, 4):
        for s in range(1, 4):
            named.append((f"A^{r}B^{s}", A_BITS * r + B_BITS * s))
    named.extend([("(110)^4", "110" * 4), ("(111)^4", "111" * 4), ("(110|111)^*", "110111110111")])
    for name, word in named:
        comparator = "1" * word.count("1") + "0" * word.count("0")
        distance = hamming(word, comparator)
        checks = []
        for width in range(1, len(word) + 1):
            linear_actual = len(linear_factors(word, width))
            linear_base = len(linear_factors(comparator, width))
            cyclic_actual = len(cyclic_factors(word, width))
            cyclic_base = len(cyclic_factors(comparator, width))
            if linear_actual > linear_base + width * distance or cyclic_actual > cyclic_base + width * distance:
                raise AssertionError("mandatory Hamming regression")
            checks.append([width, linear_actual, linear_base, cyclic_actual, cyclic_base])
        pairs.append([name, word, comparator, distance, checks])

    numeric = []
    for family in ("2^m-1", "8^m-5"):
        for m in range(2, 13):
            source = 2**m - 1 if family == "2^m-1" else 8**m - 5
            current = source
            seen = set()
            for step in range(257):
                if current == 1 or current in seen or step == 256:
                    numeric.append([family, m, source, step, current, current == 1])
                    break
                seen.add(current)
                current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2
    return {
        "format": "collatz-phase25-regressions-v1",
        "mandatory_word_families": pairs,
        "numeric_prefix_families": numeric,
        "tamper_boundaries": ["strict inequalities", "q0 dependency labels", "falsifier residues", "resultant nonvanishing", "proves_collatz=false"],
        "proves_collatz": False,
    }


def theory_artifact(q0: dict[str, object], cycle: dict[str, object]) -> dict[str, object]:
    return {
        "format": "collatz-phase25-theory-v1",
        "claims": {
            "P151": {"status": "VERIFIED_THEOREM", "statement": "Changing H bits adds at most nH linear or cyclic length-n factors; critical and cycle profile supports therefore give the stated support-sensitive linear bounds."},
            "P152": {"status": "CONDITIONAL", "statement": "Under P54 and pairwise-distinct critical states, q<=(2n_q+1)s+2n_q+2. Under EXT04 the q0 width is exactly 73 and the support lower bound is 490186612."},
            "P153": {"status": "CONDITIONAL", "statement": "Each positive critical defect loses more than 1/4 normalized correction, hence s<4(S0-3N delta) under P54."},
            "P154": {"status": "VERIFIED_THEOREM", "statement": "An integral coprime resonant-grid profile forces a nonzero resultant divisible by D, with an exact conjugate-product magnitude bound."},
            "P155": {"status": "VERIFIED_THEOREM", "statement": "The critical coprime seven-grid area-three family with roots Q,2Q,3Q is impossible; Q>=11 uses EXT05 and smaller coprime Q are direct."},
            "E37": {"status": "VERIFIED_FINITE", "statement": "The declared critical/cycle support, q0 interval, paired-arc falsifier, conjugate interval, and finite resonance rows are independently reproducible."},
            "NG34": {"status": "REFUTED", "statement": "Every valid critical Type-C area-three profile satisfies one of the two Phase-24 arc thresholds."},
            "H147": {"status": "OPEN", "statement": "Control all near-resonant Type-C profiles and the collapsed Type-A/B families, then address arbitrary area and noncoprime slopes."},
        },
        "hamming_perturbation": {
            "linear": "p_v(n)<=p_u(n)+n H(u,v)",
            "cyclic": "p_v_cyc(n)<=p_u_cyc(n)+n H(u,v), 1<=n<=L",
            "critical": "H(c_q,w)<=2s and p_w(n)<=(2s+1)n+2",
            "cycle": "H(v_a,v_0)<=2s and p_v_cyc(n)<=(2s+1)n+1",
        },
        "critical_support": {
            "n_q": "min{n:2^n D_q>=3B_q_max+qD_q}",
            "conditional_lower": "s>=max(0,ceil((q-2n_q-2)/(2n_q+1)))",
            "correction_upper": "s<4(S0-3N delta_q)",
            "q0_certificate": q0,
        },
        "cycle_area_three": {
            "literal_hamming": cycle["expected_hamming_by_type"],
            "support_height": "profile height h<=support s",
            "conditional_consequence": "If n_cyc<=h+O(log q), then s=Omega(sqrt(q)); the polynomial cycle-minimum premise is not proved.",
        },
        "resonance_boundary": "P154/P155 require gcd(q,L)=1. EXT05 is an external theorem. Near-resonant and noncoprime profiles remain open.",
        "what_this_result_does_not_prove": "It does not prove H89, H133, H147, H72, or the Collatz conjecture.",
        "proves_collatz": False,
    }


def obstruction_markdown(resonance: dict[str, object], q0: dict[str, object]) -> str:
    falsifier = resonance["paired_arc_falsifier"]
    return f"""# Phase 25 obstruction report

## Naive paired-arc threshold is false

The exact valid Type-C row `q={falsifier['q']}`, `L={falsifier['L']}` with
roots `{falsifier['profile_support']}` has q-arc width
`{falsifier['q_arc_width']}` and L-arc width `{falsifier['L_arc_width']}`.
Both exact EXT05 threshold comparisons fail.  Direct modular evaluation has
gcd `{falsifier['direct_modular_gcd']}` with `D`, so this is not an integral
cycle witness.  It refutes only the proposed uniform two-arc gap.

The proposal's displayed L-arc residue list was not exact.  The independently
reconstructed list is `{falsifier['L_arc_points']}`; the width remains
`{falsifier['L_arc_width']}`, so the falsification itself survives.

## Exact resonance covers one family, not a neighbourhood

The resultant certificate excludes the exact seven-grid coprime family.  It
does not provide an inverse theorem saying that every two-arc failure is an
exact or controlled near-grid.  Near-resonant Type-C triples are the smallest
remaining H147 obstruction.

## Critical support squeeze remains open

Under its explicit P54/distinct-state/EXT04 assumptions, the q0 lower bound is
`{q0['conditional_support_lower']}`.  The X02 correction upper bound is
`{q0['conditional_support_upper_from_X02']}`, so the exact squeeze does not
exclude q0.

## What this result does not prove

It does not exclude all area-three coprime cycles, noncoprime or arbitrary-area
cycles, a least counterexample, or the Collatz conjecture.
`proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    arguments = parser.parse_args()
    arguments.artifact_dir.mkdir(parents=True, exist_ok=True)

    critical = critical_support_audit()
    q0 = q0_certificate()
    cycle = cycle_support_audit()
    resonance = resonance_artifact()
    regressions = regression_artifact()
    theory = theory_artifact(q0, cycle)

    write_json(arguments.artifact_dir / "phase25_theory.json", theory)
    write_json(arguments.artifact_dir / "phase25_critical_support.json", critical)
    write_json(arguments.artifact_dir / "phase25_cycle_support.json", cycle)
    write_json(arguments.artifact_dir / "phase25_resonance.json", resonance)
    write_json(arguments.artifact_dir / "phase25_regressions.json", regressions)
    (arguments.artifact_dir / "phase25_obstruction_report.md").write_text(obstruction_markdown(resonance, q0), encoding="utf-8")

    print(json.dumps({
        "valid": True,
        "critical_words": critical["totals"]["critical_words"],
        "cycle_profiles": cycle["profile_count"],
        "q0_n": q0["integer_width_n_q0"],
        "q0_support_lower": q0["conditional_support_lower"],
        "seven_grid_threshold_Q": resonance["seven_grid"]["eventual_threshold_Q"],
        "paired_arc_falsifier_q": resonance["paired_arc_falsifier"]["q"],
        "proves_collatz": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
