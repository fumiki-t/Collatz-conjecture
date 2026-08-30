#!/usr/bin/env python3
"""Generate exact Phase 28 transport-dispersion evidence.

The supplied note is an untrusted proposal.  Mathematical acceptance uses
integers, Fractions, and rigorous rational logarithm enclosures only.
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
        NEGATIVE_Q7,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
        reduced_profile,
    )
except ModuleNotFoundError:
    from src.phase26_search import (
        A_BITS,
        B_BITS,
        NEGATIVE_Q7,
        compositions,
        cyclic_class,
        cyclic_factors,
        encode_fraction,
        expanded_word,
        log_interval,
        minimum_rotations,
        primitive,
        reduced_profile,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 8
EXPECTED_CLAIMS = {
    "P166": "VERIFIED_THEOREM",
    "P167": "VERIFIED_THEOREM",
    "P168": "VERIFIED_THEOREM",
    "P169": "VERIFIED_THEOREM",
    "P170": "VERIFIED_THEOREM",
    "P171": "VERIFIED_THEOREM",
    "E40": "VERIFIED_FINITE",
    "NG37": "REFUTED",
    "NG38": "REFUTED",
    "H172": "OPEN",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def ceil_div(numerator: int, denominator: int) -> int:
    return -(-numerator // denominator)


def ceil_log2_three_power(q: int) -> int:
    value = 3**q
    return value.bit_length()


def mechanical_baseline(q: int, L: int) -> tuple[int, ...]:
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    return tuple(
        ceil_div(L0 * (index + 1), q0) - ceil_div(L0 * index, q0)
        for index in range(q)
    )


def profile_to_exponents(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    if len(profile) != len(base) + 1 or profile[0] or profile[-1] or min(profile) < 0:
        raise ValueError("profile boundary")
    answer = tuple(
        base[index] + profile[index + 1] - profile[index]
        for index in range(len(base))
    )
    if min(answer) < 1:
        raise ValueError("profile violates positive exponents")
    return answer


def level_intervals(profile: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], ...]:
    q = len(profile) - 1
    if profile[0] or profile[-1]:
        raise ValueError("level cut")
    answer = []
    for level in range(1, max(profile[:-1], default=0) + 1):
        intervals = []
        start = None
        for index in range(q + 1):
            active = index < q and profile[index] >= level
            if active and start is None:
                start = index
            if not active and start is not None:
                intervals.append((start, index))
                start = None
        answer.append(tuple(intervals))
    return tuple(answer)


def direct_polynomial(profile: Sequence[int]) -> tuple[int, ...]:
    q = len(profile) - 1
    coefficients = [0] * q
    coefficients[0] = 1
    for index, height in enumerate(profile[:-1]):
        value = 2**height - 1
        coefficients[index] -= value
        if index + 1 == q:
            coefficients[0] += 2 * value
        else:
            coefficients[index + 1] += value
    return tuple(coefficients)


def level_polynomial(profile: Sequence[int]) -> tuple[int, ...]:
    q = len(profile) - 1
    coefficients = [0] * q
    coefficients[0] = 1
    for level, intervals in enumerate(level_intervals(profile), start=1):
        weight = 2 ** (level - 1)
        for start, end in intervals:
            coefficients[start] -= weight
            if end == q:
                coefficients[0] += 2 * weight
            else:
                coefficients[end] += weight
    return tuple(coefficients)


def transport_data(exponents: Sequence[int], check_intervals: bool = True) -> dict[str, object]:
    data = reduced_profile(exponents)
    q, L = data["q"], data["L"]
    q0, L0 = data["q0"], data["L0"]
    profile = tuple(data["profile"])
    base = tuple(data["baseline"])
    if base != mechanical_baseline(q, L):
        raise AssertionError("mechanical baseline formula")
    b = tuple(value - 1 for value in base)
    p = L0 - q0
    if not 0 < p <= q0 or set(b) - {0, 1}:
        raise AssertionError("mechanical slope")

    density_checks = 0
    if check_intervals:
        for start in range(q):
            for width in range(1, q + 1):
                count = sum(b[(start + offset) % q] for offset in range(width))
                if count > ceil_div(p * width, q0):
                    raise AssertionError("cyclic descent density")
                density_checks += 1

    increments = tuple(profile[index + 1] - profile[index] for index in range(q))
    if any(change < -b[index] for index, change in enumerate(increments)):
        raise AssertionError("profile descent legality")
    if any(change < -1 for change in increments):
        raise AssertionError("nonunit descent")
    inserted = sum(max(change, 0) for change in increments)
    deleted = sum(max(-change, 0) for change in increments)
    descent_steps = sum(change == -1 for change in increments)
    if inserted != deleted or deleted != descent_steps:
        raise AssertionError("zero-token balance")
    actual_zeros = tuple(value - 1 for value in exponents)
    scripted = tuple(b[index] + increments[index] for index in range(q))
    if actual_zeros != scripted or min(scripted) < 0:
        raise AssertionError("zero-token edit script")

    levels = level_intervals(profile)
    components = tuple(len(intervals) for intervals in levels)
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    if inserted != sum(components):
        raise AssertionError("level transport identity")
    if area != sum(end - start for intervals in levels for start, end in intervals):
        raise AssertionError("layer cake")
    descent_floor = sum((level * q0) // p for level in range(height))
    if area - inserted < descent_floor:
        raise AssertionError("mechanical descent cost")

    direct = direct_polynomial(profile)
    layered = level_polynomial(profile)
    if direct != layered:
        raise AssertionError("multilevel polynomial")
    support = sum(value != 0 for value in direct)
    weighted_components = sum(
        2 ** (level - 1) * count for level, count in enumerate(components, start=1)
    )
    endpoint_weight = 2 ** profile[-2] - 1
    l1 = sum(abs(value) for value in direct)
    if support > 2 * inserted + 1 or l1 > 1 + 2 * weighted_components + endpoint_weight:
        raise AssertionError("multilevel sparse bound")

    return {
        "q": q,
        "L": L,
        "d": data["d"],
        "q0": q0,
        "L0": L0,
        "profile": profile,
        "baseline": base,
        "area": area,
        "height": height,
        "J": inserted,
        "descent_floor": descent_floor,
        "descent_slack": area - inserted - descent_floor,
        "level_components": components,
        "polynomial": direct,
        "polynomial_support": support,
        "polynomial_l1": l1,
        "weighted_components": weighted_components,
        "endpoint_weight": endpoint_weight,
        "density_checks": density_checks,
        "insertions": tuple((index, change) for index, change in enumerate(increments) if change > 0),
        "deletions": tuple(index for index, change in enumerate(increments) if change < 0),
    }


def corpus_audit() -> dict[str, object]:
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "transport_checks": 0,
        "density_interval_checks": 0,
        "factor_width_checks": 0,
        "polynomial_checks": 0,
    }
    rows = []
    maximum_plateau_ratio = Fraction(0)
    plateau_sample = None
    for q in range(1, Q_MAX + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(L, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                invariants = set()
                representative = None
                for rotated in minimum_rotations(values):
                    item = transport_data(rotated)
                    counts["minimum_rotations"] += 1
                    counts["transport_checks"] += 1
                    counts["density_interval_checks"] += item["density_checks"]
                    counts["polynomial_checks"] += 1
                    base_word = expanded_word(item["baseline"])
                    actual_word = expanded_word(rotated)
                    maximum_ratio = Fraction(0)
                    for width in range(1, L + 1):
                        base_count = len(cyclic_factors(base_word, width))
                        actual_count = len(cyclic_factors(actual_word, width))
                        bound = (2 * item["J"] + 1) * width + 1
                        if base_count > width + 1 or actual_count > bound:
                            raise AssertionError("transport factor complexity")
                        counts["factor_width_checks"] += 1
                        maximum_ratio = max(maximum_ratio, Fraction(actual_count, bound))
                    invariants.add((item["area"], item["height"], item["J"], item["descent_floor"]))
                    representative = (rotated, item, maximum_ratio)
                if representative is None or len(invariants) != 1:
                    raise AssertionError("minimum-rotation transport invariance")
                rotated, item, maximum_ratio = representative
                counts["noncoprime_classes"] += int(item["d"] > 1)
                ratio = Fraction(item["area"], item["J"]) if item["J"] else Fraction(0)
                if ratio > maximum_plateau_ratio:
                    maximum_plateau_ratio = ratio
                    plateau_sample = [list(rotated), item["area"], item["height"], item["J"]]
                rows.append([
                    q, L, list(values), primitive(values), item["d"], item["area"],
                    item["height"], item["J"], item["descent_floor"],
                    item["descent_slack"], item["polynomial_support"],
                    item["polynomial_l1"], encode_fraction(maximum_ratio),
                ])
    if counts["cyclic_classes"] != 2214 or counts["minimum_rotations"] != 3101:
        raise AssertionError("Phase 27 corpus regression")
    return {
        "format": "collatz-phase28-transport-corpus-v1",
        "maximum_q": Q_MAX,
        "counts": counts,
        "row_digest_sha256": stable_hash(rows),
        "maximum_area_over_transport": encode_fraction(maximum_plateau_ratio),
        "maximum_area_over_transport_sample": plateau_sample,
        "scope": "Complete positive-D cyclic exponent corpus through q<=8; valid rational profiles are structural controls, not integer cycles.",
        "proves_collatz": False,
    }


def floor_cuberoot(value: int) -> int:
    if value < 0:
        raise ValueError("cube root")
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


def decimal_cuberoot_box(lower: Fraction, upper: Fraction, digits: int = 6) -> list[list[str]]:
    scale = 10**digits
    low_integer = floor_cuberoot(lower.numerator * scale**3 // lower.denominator)
    while Fraction((low_integer + 1) ** 3, scale**3) <= lower:
        low_integer += 1
    high_integer = floor_cuberoot(upper.numerator * scale**3 // upper.denominator)
    if Fraction(high_integer**3, scale**3) < upper:
        high_integer += 1
    return [encode_fraction(Fraction(low_integer, scale)), encode_fraction(Fraction(high_integer, scale))]


def transport_constant_cube(slope: Fraction) -> Fraction:
    if not 1 < slope <= 2:
        raise ValueError("transport slope")
    return Fraction(27, 32) * slope * slope / (slope - 1)


def scalar_audit() -> dict[str, object]:
    ln2_low, ln2_high = log_interval(Fraction(2), terms=72)
    ln3_low, ln3_high = log_interval(Fraction(3), terms=72)
    alpha_low = ln3_low / ln2_high
    alpha_high = ln3_high / ln2_low
    if not 1 < alpha_low < alpha_high < 2:
        raise AssertionError("log2(3) enclosure")
    critical_cube_low = transport_constant_cube(alpha_high)
    critical_cube_high = transport_constant_cube(alpha_low)
    old_cube_low = alpha_low * alpha_low / 2
    old_cube_high = alpha_high * alpha_high / 2
    if not critical_cube_low > old_cube_high:
        raise AssertionError("critical Phase 27 improvement")
    if not Fraction(27, 8) > old_cube_high:
        raise AssertionError("noncritical Phase 27 improvement")

    slope_rows = []
    for slope in (Fraction(8, 5), Fraction(5, 3), Fraction(7, 4), Fraction(19, 10), Fraction(2)):
        cube = transport_constant_cube(slope)
        slope_rows.append({
            "slope": encode_fraction(slope),
            "constant_cube": encode_fraction(cube),
            "at_least_three_halves": cube >= Fraction(27, 8),
        })
    critical_rows = []
    for q in (10, 100, 1_000, 10_000):
        L = ceil_log2_three_power(q)
        slope = Fraction(L, q)
        critical_rows.append({
            "q": q,
            "L": L,
            "slope": encode_fraction(slope),
            "constant_cube": encode_fraction(transport_constant_cube(slope)),
        })
    return {
        "format": "collatz-phase28-scalar-certificates-v1",
        "log2_three_interval": [encode_fraction(alpha_low), encode_fraction(alpha_high)],
        "critical_constant_cube_interval": [encode_fraction(critical_cube_low), encode_fraction(critical_cube_high)],
        "critical_constant_decimal_box": decimal_cuberoot_box(critical_cube_low, critical_cube_high),
        "phase27_constant_cube_interval": [encode_fraction(old_cube_low), encode_fraction(old_cube_high)],
        "noncritical_constant": encode_fraction(Fraction(3, 2)),
        "noncritical_constant_cube": encode_fraction(Fraction(27, 8)),
        "monotonicity": {
            "function_cube": "27*ell^2/(32*(ell-1))",
            "derivative_sign_numerator": "ell*(ell-2)",
            "strictly_decreasing_on": "1<ell<2",
        },
        "near_extremal_scales": {
            "height_cube": "ell*(ell-1)/2",
            "transport_cube": "ell^2/(4*(ell-1))",
            "area_cube": "27*ell^2/(32*(ell-1))",
        },
        "slope_rows": slope_rows,
        "critical_rows": critical_rows,
        "boundary": "Decimal boxes are diagnostic rational enclosures. The asymptotic theorems are analytic and are not inferred from these finite rows.",
        "proves_collatz": False,
    }


def tall_profile(q: int, L: int, height: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, L)
    profile = [0, height]
    for index in range(1, q):
        current = profile[-1]
        profile.append(current - 1 if current and base[index] == 2 else current)
    if profile[-1]:
        raise AssertionError("tall profile closure")
    return tuple(profile)


def plateau_profile(q: int, L: int, height: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, L)
    descents = {index for index, value in list(enumerate(base))[::-1] if value == 2}
    selected = set(sorted(descents)[-height:])
    profile = [0]
    for index in range(q):
        current = profile[-1]
        if index == 0:
            next_value = height
        elif index in selected and current:
            next_value = current - 1
        else:
            next_value = current
        profile.append(next_value)
    if profile[-1]:
        raise AssertionError("plateau profile closure")
    return tuple(profile)


def isolated_profile(q: int, L: int, excursions: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, L)
    profile = [0]
    started = 0
    for index in range(q):
        current = profile[-1]
        if current and base[index] == 2:
            next_value = 0
        elif current == 0 and started < excursions and any(value == 2 for value in base[index + 1 :]):
            next_value = 1
            started += 1
        else:
            next_value = current
        profile.append(next_value)
    if profile[-1] or started != excursions:
        raise AssertionError("isolated profile closure")
    return tuple(profile)


def near_extremal_profile(q: int, L: int, height: int, target_J: int) -> tuple[int, ...]:
    base = mechanical_baseline(q, L)
    profile = [0]
    isolated_left = target_J - height
    tall_started = False
    for index in range(q):
        current = profile[-1]
        if not tall_started:
            next_value = height
            tall_started = True
        elif current > 1 and base[index] == 2:
            next_value = current - 1
        elif current == 1 and base[index] == 2:
            next_value = 0
        elif current == 0 and isolated_left and any(value == 2 for value in base[index + 1 :]):
            next_value = 1
            isolated_left -= 1
        else:
            next_value = current
        profile.append(next_value)
    if profile[-1] or isolated_left:
        raise AssertionError("near-extremal profile closure")
    return tuple(profile)


def seven_grid_time_profile() -> tuple[int, int, tuple[int, ...]]:
    q, L = 77, 123
    residue_profile = [0] * q
    for residue in (11, 22, 33):
        residue_profile[residue] = 1
    profile = tuple(residue_profile[(-L * index) % q] for index in range(q)) + (0,)
    profile_to_exponents(mechanical_baseline(q, L), profile)
    return q, L, profile


def synthetic_sample(kind: str, q: int, L: int, profile: Sequence[int]) -> dict[str, object]:
    base = mechanical_baseline(q, L)
    exponents = profile_to_exponents(base, profile)
    # The density theorem is proved symbolically and exhaustively regressed in
    # the q<=8 corpus.  Avoid a cubic all-interval scan on large synthetic rows.
    item = transport_data(exponents, check_intervals=False)
    factor_rows = []
    base_word = expanded_word(base)
    actual_word = expanded_word(exponents)
    widths = sorted({1, 2, 3, 5, 8, 13, L})
    for width in widths:
        if width > L:
            continue
        actual_count = len(cyclic_factors(actual_word, width))
        bound = (2 * item["J"] + 1) * width + 1
        if actual_count > bound:
            raise AssertionError("synthetic factor bound")
        factor_rows.append([width, actual_count, bound])
    return {
        "kind": kind,
        "q": q,
        "L": L,
        "area": item["area"],
        "height": item["height"],
        "J": item["J"],
        "descent_floor": item["descent_floor"],
        "descent_slack": item["descent_slack"],
        "level_components": list(item["level_components"]),
        "polynomial_support": item["polynomial_support"],
        "polynomial_l1": item["polynomial_l1"],
        "factor_rows": factor_rows,
        "profile_digest_sha256": stable_hash(list(profile)),
        "exponent_digest_sha256": stable_hash(list(exponents)),
        "valid_positive_exponents": min(exponents) >= 1,
    }


def synthetic_audit() -> dict[str, object]:
    rows = []
    q = 125
    L = ceil_log2_three_power(q)
    rows.append(synthetic_sample("one-tall-excursion", q, L, tall_profile(q, L, 5)))
    rows.append(synthetic_sample("long-constant-plateau", q, L, plateau_profile(q, L, 5)))
    rows.append(synthetic_sample("isolated-unit-excursions", q, L, isolated_profile(q, L, 20)))
    q = 1331
    L = ceil_log2_three_power(q)
    rows.append(synthetic_sample("near-extremal-mixed", q, L, near_extremal_profile(q, L, 9, 124)))
    q, L, profile = seven_grid_time_profile()
    rows.append(synthetic_sample("phase25-seven-grid", q, L, profile))
    return {
        "format": "collatz-phase28-synthetic-profiles-v1",
        "rows": rows,
        "row_digest_sha256": stable_hash(rows),
        "multiple_minimum_control": "isolated-unit-excursions has repeated returns to profile height zero",
        "boundary": "All rows are exact legal reduced profiles, not positive integer cycles and not asymptotic extremizers.",
        "proves_collatz": False,
    }


def bit_exponents(bits: str) -> tuple[int, ...]:
    start = bits.index("1")
    rotated = bits[start:] + bits[:start]
    positions = [index for index, bit in enumerate(rotated) if bit == "1"] + [len(rotated)]
    return tuple(positions[index + 1] - positions[index] for index in range(len(positions) - 1))


def regression_audit() -> dict[str, object]:
    families = []
    for name, bits in (
        ("A=11101", A_BITS), ("B=1100", B_BITS),
        ("(110|111)^*", "110111" * 8), ("A^1B^1", A_BITS + B_BITS),
        ("A^2B^3", A_BITS * 2 + B_BITS * 3),
        ("2^m-1", "1" * 12 + "0"), ("8^m-5", "111001" * 4),
    ):
        values = bit_exponents(bits)
        item = transport_data(minimum_rotations(values)[0])
        families.append([name, bits, list(values), item["area"], item["height"], item["J"]])
    named = []
    for name, source, values in (
        ("trivial-positive", 1, (2,)),
        ("negative-q2", -5, (1, 2)),
        ("negative-q7", -17, NEGATIVE_Q7),
    ):
        current = Fraction(source)
        for exponent in values:
            current = (3 * current + 1) / 2**exponent
        named.append([name, source, list(values), current == source])
    powers = []
    for count in range(2, 7):
        item = transport_data((2,) * count)
        powers.append([count, item["d"], item["area"], item["J"], primitive((2,) * count)])
    strictness = transport_data((3, 1, 1))
    if not (strictness["area"] == strictness["J"] == strictness["height"] == 1 and strictness["descent_floor"] == 0):
        raise AssertionError("finite strictness obstruction")
    return {
        "format": "collatz-phase28-regressions-v1",
        "mandatory_families": families,
        "named_cycles": named,
        "trivial_powers": powers,
        "NG32_control": {"q": 4, "word": "1101100", "width": 2, "factor_count": 4},
        "NG34_control": {"q": 63322, "L": 100363, "roots": [9046, 18092, 27138], "direct_modular_gcd": 1},
        "NG35_control": {"left": str(75**7), "right": str(3 * 64**7), "left_exceeds_right": True},
        "NG36_control": {"exponents": [1, 3], "orbit": [["5", "7"], ["11", "7"]], "rotation_mismatch": True},
        "finite_strictness_obstruction": {
            "q": 3, "L": 5, "exponents": [3, 1, 1], "delta": ["2", "3"],
            "area": 1, "J": 1, "height": 1, "new_bound": 1, "triangular_bound": 1,
            "interpretation": "Refutes universal finite strict improvement, not the asymptotic leading-coefficient improvement.",
        },
        "endpoint_l1_obstruction": {
            "q": 2, "L": 4, "exponents": [3, 1], "profile": [0, 1, 0],
            "polynomial": [3, -1], "l1": 4, "proposed_bound": 3,
            "corrected_bound": 4,
            "interpretation": "X^q=2 makes an interval ending at q cost three endpoint units; the decomposition and support bound survive.",
        },
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase28-transport-theory-v1",
        "claims": {
            "P166": {"status": "VERIFIED_THEOREM", "statement": "The reduced profile gives an exact balanced script of J zero insertions and J zero deletions, with p_cyc(n)<=(2J+1)n+1 and the transport state-separation bound."},
            "P167": {"status": "VERIFIED_THEOREM", "statement": "Level components satisfy J=sum U_k, A=sum |I_k|, and A-J>=sum_(r<h) floor(r/delta)."},
            "P168": {"status": "VERIFIED_THEOREM", "statement": "A fixed polynomial multiplier gap and limiting slope ell force liminf A/q^(2/3)>=3 ell^(2/3)/(2^(5/3)(ell-1)^(1/3))."},
            "P169": {"status": "VERIFIED_THEOREM", "statement": "The noncritical branch has internal constant at least 3/2; the critical branch has the sharper C_crit using external EXT17."},
            "P170": {"status": "VERIFIED_THEOREM", "statement": "Equality at the P168 frontier forces the unique height/transport scales, vanishing normalized descent slack, and asymptotic saturation of transport factor separation."},
            "P171": {"status": "VERIFIED_THEOREM", "statement": "Q_a is an exact sum of dyadic level-interval endpoint binomials, with support at most 2J+1 and corrected l1 bound 1+2 sum 2^(k-1)U_k+(2^a_(q-1)-1)."},
            "E40": {"status": "VERIFIED_FINITE", "statement": "The q<=8 corpus, five synthetic profiles, scalar boxes, mandatory families, and strictness obstruction are independently reproducible."},
            "NG37": {"status": "REFUTED", "statement": "The descent-density lower bound is strictly stronger than the triangular bound for every nonzero finite profile with delta<1."},
            "NG38": {"status": "REFUTED", "statement": "After reducing X^q=2, the multilevel decomposition always has l1 norm at most 1+2 sum 2^(k-1)U_k without an endpoint correction."},
            "H172": {"status": "OPEN", "statement": "Turn near-extremal transport rigidity into a nonzero multilevel resonance/resultant obstruction for both rotations and every gcd class."},
            "H133": {"status": "OPEN", "statement": "Transport dispersion and multilevel sparsity do not exclude arbitrary-area positive cycles."},
        },
        "dependencies": {
            "P166": ["P125", "P133", "P156", "P157"],
            "P167": ["P156"],
            "P168": ["P166", "P167"],
            "P169": ["P163", "P164", "P168", "EXT17"],
            "P170": ["P166", "P167", "P168"],
            "P171": ["P137", "P156", "P167"],
        },
        "transport_definition": "J=sum_j (a_(j+1)-a_j)_+=sum_j (a_j-a_(j+1))_+; every negative increment is -1",
        "sharp_constant": "C(ell)=3*ell^(2/3)/(2^(5/3)*(ell-1)^(1/3))",
        "external_boundary": "Only the critical specialization in P169 depends on EXT17; the noncritical 3/2 bound is internal relative to P133/P134/P157.",
        "finite_strictness_boundary": "P167 improves the leading asymptotic height cost when delta<1, but NG37 shows finite equality with the triangular bound can occur.",
        "polynomial_endpoint_boundary": "NG38 requires the exact endpoint correction 2^a_(q-1)-1 in P171's l1 bound; support <=2J+1 is unchanged.",
        "what_this_result_does_not_prove": "No near-extremal resonance exclusion, arbitrary-area cycle exclusion, nonperiodic branch exclusion, or Collatz proof follows.",
        "proves_collatz": False,
    }


def obstruction_report(corpus: dict[str, object], synthetic: dict[str, object]) -> str:
    return f"""# Phase 28 obstruction report

## NG37: finite strictness overstatement

For `q=3`, `L=5`, `e=(3,1,1)`, the reduced profile has
`A=J=h=1`, `delta=2/3`, and descent-floor sum zero.  Therefore both the new
finite bound and the triangular bound equal one.  The asymptotic leading
coefficient in P167/P168 remains stronger.

## NG38: missing `X^q=2` endpoint cost

For `q=2`, `L=4`, `e=(3,1)`, the profile `(0,1,0)` gives
`Q_a=(3,-1)` and `||Q_a||_1=4`, while the proposed bound is three.  The
corrected P171 bound adds `2^a_(q-1)-1=1`.  The endpoint-binomial
decomposition and support bound `<=2J+1` survive.

## Surviving structural regimes

The exact synthetic corpus contains `{len(synthetic['rows'])}` legal profiles:
one tall excursion, a long plateau with `A` much larger than `J`, isolated
unit excursions, a near-frontier mixed profile, and the Phase 25 seven-grid
control.  They are not integer cycles.

## Rotation boundary

NG36 remains active.  P133's least-value rotation and P156's discrepancy
minimum cannot be identified from rational-shadow algebra alone.  P166--P171
are stated in reduced-profile coordinates; any ordinary-source application
must transport rotations explicitly.

## First open obstruction

The corpus contains {corpus['counts']['cyclic_classes']} exact cyclic classes,
but no theorem turns near-extremal `h,J,A` saturation or the multilevel
endpoint polynomial into an all-area nonzero resultant.  This is H172.

## What this result does not prove

Phase 28 does not exclude arbitrary-area positive cycles, either nonperiodic
counterexample branch, or the Collatz conjecture. `proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    arguments = parser.parse_args()
    arguments.artifact_dir.mkdir(parents=True, exist_ok=True)

    theory = theory_artifact()
    corpus = corpus_audit()
    scalar = scalar_audit()
    synthetic = synthetic_audit()
    regressions = regression_audit()
    if {key: value["status"] for key, value in theory["claims"].items()} != EXPECTED_CLAIMS:
        raise AssertionError("claim discipline")
    write_json(arguments.artifact_dir / "phase28_theory.json", theory)
    write_json(arguments.artifact_dir / "phase28_transport_corpus.json", corpus)
    write_json(arguments.artifact_dir / "phase28_scalar_certificates.json", scalar)
    write_json(arguments.artifact_dir / "phase28_synthetic_profiles.json", synthetic)
    write_json(arguments.artifact_dir / "phase28_regressions.json", regressions)
    (arguments.artifact_dir / "phase28_obstruction_report.md").write_text(
        obstruction_report(corpus, synthetic), encoding="utf-8"
    )
    print(json.dumps({
        "valid": True,
        "cyclic_classes": corpus["counts"]["cyclic_classes"],
        "minimum_rotations": corpus["counts"]["minimum_rotations"],
        "synthetic_profiles": len(synthetic["rows"]),
        "claims": EXPECTED_CLAIMS,
        "proves_collatz": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
