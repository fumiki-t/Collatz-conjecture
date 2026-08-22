#!/usr/bin/env python3
"""Generate exact Phase 7 boundary-defect arithmetic artifacts.

No proof decision in this module uses floating point.  The only asymptotic
input is an explicitly labelled Denjoy--Koksma theorem application whose exact
continued-fraction premises are included in the artifacts.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from math import ceil, factorial, gcd, isqrt
from pathlib import Path
from typing import Iterator


FORMAT = "collatz-phase7-boundary-defect-v1"
V = 2075 * (1 << 60)
Q0 = 72_057_431_991
K0 = 114_208_327_604
LEFT_PARENT = (103_768_467_013, 65_470_613_321)
RIGHT_PARENT = (10_439_860_591, 6_586_818_670)
SHIFTS = (12, 41, 53, 306, 665)
CF_ALPHA = (1, 1, 1, 2, 2, 3, 1, 5, 2, 23, 2, 2, 1, 1, 55, 1, 4, 3, 1, 1, 15, 1, 9)
FRONTIER_Q = (1, 3, 5, 17)
EXPECTED_LAYER_COUNTS = {1: 1, 3: 2, 5: 7, 17: 312_455}
DANGEROUS_WORDS = ("011101", "1101", "101", "1")

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def decodeable_interval(lower: Fraction, upper: Fraction) -> dict[str, object]:
    if not lower < upper:
        raise ValueError("invalid rational interval")
    return {"lower": encode_fraction(lower), "upper": encode_fraction(upper)}


def outward_dyadic(lower: Fraction, upper: Fraction, bits: int = 256) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    low_n = lower.numerator * scale // lower.denominator
    high_n = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(low_n, scale), Fraction(high_n, scale)


def log_interval(numerator: int, denominator: int = 1, *, terms: int = 160) -> tuple[Fraction, Fraction]:
    """Exact atanh-series enclosure for log(numerator/denominator)."""
    if numerator <= denominator or denominator <= 0:
        raise ValueError("log enclosure requires x>1")
    z = Fraction(numerator - denominator, numerator + denominator)
    z2 = z * z
    term = z
    total = Fraction(0)
    for index in range(terms):
        total += term / (2 * index + 1)
        term *= z2
    lower = 2 * total
    remainder = 2 * term / ((2 * terms + 1) * (1 - z2))
    return outward_dyadic(lower, lower + remainder)


def exp_minus_one_interval(lower: Fraction, upper: Fraction, *, terms: int = 18) -> tuple[Fraction, Fraction]:
    """Exact Taylor enclosure for exp(x)-1 on 0<lower<=upper<1."""
    if not 0 < lower <= upper < 1:
        raise ValueError("exp enclosure requires 0<lower<=upper<1")

    def partial(x: Fraction) -> tuple[Fraction, Fraction]:
        value = Fraction(1)
        term = Fraction(1)
        for index in range(1, terms + 1):
            term = term * x / index
            value += term
        next_term = term * x / (terms + 1)
        remainder = next_term / (1 - x / (terms + 2))
        return value, value + remainder

    low_value, _ = partial(lower)
    _, high_value = partial(upper)
    return outward_dyadic(low_value - 1, high_value - 1)


def sqrt_half_interval(bits: int = 256) -> tuple[Fraction, Fraction]:
    """Dyadic enclosure of 1/sqrt(2), certified by integer squares."""
    scale = 1 << bits
    floor_value = isqrt(1 << (2 * bits - 1))
    lower = Fraction(floor_value, scale)
    upper = Fraction(floor_value + 1, scale)
    if not lower * lower <= Fraction(1, 2) < upper * upper:
        raise AssertionError("sqrt enclosure failed")
    return lower, upper


def continued_fraction(value: Fraction) -> list[int]:
    terms: list[int] = []
    while value.denominator != 1:
        quotient = value.numerator // value.denominator
        terms.append(quotient)
        value = 1 / (value - quotient)
    terms.append(value.numerator)
    return terms


def convergents(terms: tuple[int, ...] | list[int]) -> list[tuple[int, int]]:
    p_prev2, p_prev1 = 0, 1
    q_prev2, q_prev1 = 1, 0
    rows: list[tuple[int, int]] = []
    for term in terms:
        p = term * p_prev1 + p_prev2
        q = term * q_prev1 + q_prev2
        rows.append((p, q))
        p_prev2, p_prev1 = p_prev1, p
        q_prev2, q_prev1 = q_prev1, q
    return rows


def common_cf_prefix(lower: Fraction, upper: Fraction) -> tuple[int, ...]:
    left = continued_fraction(lower)
    right = continued_fraction(upper)
    prefix: list[int] = []
    for a, b in zip(left, right, strict=False):
        if a != b:
            break
        prefix.append(a)
    return tuple(prefix)


def floor_from_interval(lower: Fraction, upper: Fraction) -> int:
    low_floor = lower.numerator // lower.denominator
    high_floor = upper.numerator // upper.denominator
    if low_floor != high_floor or upper == high_floor:
        raise ValueError("interval does not determine a unique floor")
    return low_floor


def log_data() -> dict[str, object]:
    ln2_low, ln2_high = log_interval(2)
    ln3_low, ln3_high = log_interval(3)
    ln_upper_low, ln_upper_high = log_interval(3 * V + 1, V)
    alpha_low = ln3_low / ln2_high
    alpha_high = ln3_high / ln2_low
    beta_low = ln_upper_low / ln2_high
    beta_high = ln_upper_high / ln2_low
    candidate = Fraction(K0, Q0)
    left = Fraction(*LEFT_PARENT)
    right = Fraction(*RIGHT_PARENT)
    if not left < alpha_low < alpha_high < candidate < beta_low < beta_high < right:
        raise AssertionError("first-crossing rational enclosure failed")
    if candidate.numerator != LEFT_PARENT[0] + RIGHT_PARENT[0]:
        raise AssertionError("Stern-Brocot numerator decomposition failed")
    if candidate.denominator != LEFT_PARENT[1] + RIGHT_PARENT[1]:
        raise AssertionError("Stern-Brocot denominator decomposition failed")
    if candidate.numerator * LEFT_PARENT[1] - candidate.denominator * LEFT_PARENT[0] != 1:
        raise AssertionError("left Farey determinant failed")
    if candidate.denominator * RIGHT_PARENT[0] - candidate.numerator * RIGHT_PARENT[1] != 1:
        raise AssertionError("right Farey determinant failed")
    shared_cf = common_cf_prefix(alpha_low, alpha_high)
    if shared_cf[: len(CF_ALPHA)] != CF_ALPHA:
        raise AssertionError("continued-fraction prefix mismatch")
    conv = convergents(CF_ALPHA)
    if conv[-2] != RIGHT_PARENT or conv[-1] != LEFT_PARENT:
        raise AssertionError("candidate parents are not the expected consecutive convergents")
    x_low = K0 * ln2_low - Q0 * ln3_high
    x_high = K0 * ln2_high - Q0 * ln3_low
    delta_low, delta_high = exp_minus_one_interval(x_low, x_high)
    return {
        "classification": "EXACT_FINITE_CERTIFICATE",
        "repository_status": "VERIFIED_FINITE",
        "external_computational_input": {
            "classification": "EXTERNAL_COMPUTATIONAL_INPUT",
            "repository_status": "EXTERNAL_EVIDENCE",
            "claim": f"least positive counterexample N exceeds V={V}",
            "minimality_or_provenance_reverified": False,
        },
        "ln2": decodeable_interval(ln2_low, ln2_high),
        "ln3": decodeable_interval(ln3_low, ln3_high),
        "alpha_log2_3": decodeable_interval(alpha_low, alpha_high),
        "beta_log2_3_plus_1_over_V": decodeable_interval(beta_low, beta_high),
        "candidate": {"K": K0, "q": Q0, "fraction": encode_fraction(candidate)},
        "stern_brocot_parents": {
            "left": list(LEFT_PARENT),
            "right": list(RIGHT_PARENT),
            "determinants": [1, 1],
            "denominator_decomposition": [RIGHT_PARENT[1], LEFT_PARENT[1]],
            "minimal_denominator_conclusion": Q0,
        },
        "continued_fraction": {
            "alpha_prefix": list(CF_ALPHA),
            "consecutive_parent_convergents": [list(RIGHT_PARENT), list(LEFT_PARENT)],
        },
        "log_gap_x_Kln2_minus_qln3": decodeable_interval(x_low, x_high),
        "delta_exp_x_minus_1": decodeable_interval(delta_low, delta_high),
        "direct_giant_powers_constructed": False,
        "checker_boundary": "The external verification bound N>V is assumed, not reproved. All rational/logarithmic consequences are exact enclosures.",
    }


def symbolic_boundary_data(logs: dict[str, object]) -> dict[str, object]:
    ln2_data = logs["ln2"]
    delta_data = logs["delta_exp_x_minus_1"]
    assert isinstance(ln2_data, dict) and isinstance(delta_data, dict)
    ln2_low = Fraction(*map(int, ln2_data["lower"]))
    ln2_high = Fraction(*map(int, ln2_data["upper"]))
    delta_low = Fraction(*map(int, delta_data["lower"]))
    delta_high = Fraction(*map(int, delta_data["upper"]))

    mean_low = Fraction(1, 2) / ln2_high
    mean_high = Fraction(1, 2) / ln2_low
    s0_low = Q0 * mean_low - 2
    s0_high = Q0 * mean_high + 2
    weighted_contact_low = 6 * V * delta_low - s0_high
    if weighted_contact_low <= 0:
        raise AssertionError("contact weight lower bound is not positive")

    u_low, u_high = sqrt_half_interval()
    # g_t(x)=(2^-x-u)1_[0,1/2)(x).  Its mean is
    # (1-u)/ln2-(1/2)u and circle variation is 2(1-u).
    g_mean_upper = (1 - u_low) / ln2_low - Fraction(1, 2) * u_low
    g_error_upper = 4 * (1 - u_low)
    contact_count_lower_fraction = (
        weighted_contact_low - Q0 * g_mean_upper - g_error_upper
    ) / u_high
    contact_count_lower = ceil(contact_count_lower_fraction)
    if contact_count_lower * 100 <= 43 * Q0:
        raise AssertionError("rigorous contact density did not exceed 0.43")

    return {
        "format": FORMAT,
        "symbolic_identity": {
            "classification": "VERIFIED_SYMBOLIC",
            "repository_status": "CONDITIONAL",
            "assumptions": [
                "N is the least positive Collatz counterexample",
                "K is its first coefficient crossing and q is the odd-step count",
                "d_j is the zero-indexed position of odd step j",
            ],
            "definitions": {
                "f_j": "floor(j*log2(3))",
                "a_j": "f_j-d_j >= 0",
                "w_j": "2^f_j/3^j = 2^{-fractional_part(j*log2(3))}",
                "S(a)": "sum_{j=0}^{q-1} w_j*2^{-a_j}",
                "delta": "2^K/3^q-1",
                "contact_set": "C={j:a_j=0}",
            },
            "exact_steps": [
                "B=sum_j 3^(q-1-j)*2^d_j",
                "B/3^(q-1)=S(a)",
                "least-counterexample endpoint gives B>=N*(2^K-3^q)",
                "therefore S(a)>=3*N*delta",
                "noncontacts have 2^{-a_j}<=1/2",
                "therefore S(a)<=(S0+W(C))/2",
                "therefore W(C)>=6*N*delta-S0",
            ],
            "external_math_required": False,
            "proves_collatz": False,
        },
        "rotation_sum": {
            "classification": "EXTERNAL_MATH_INPUT",
            "repository_status": "EXTERNAL_THEOREM",
            "input": "DENJOY_KOKSMA",
            "exact_premises_checked": {
                "rotation": "log2(3) modulo 1",
                "q0_ostrowski_decomposition": [RIGHT_PARENT[1], LEFT_PARENT[1]],
                "summands_are_consecutive_cf_denominators": True,
                "circle_variation_of_2^-x": "1",
            },
            "conclusion_used": "|S0-q0/(2*ln(2))|<=2",
            "S0_interval": decodeable_interval(s0_low, s0_high),
            "special_case_reproved_in_repository": False,
        },
        "contact_weight": {
            "classification": "EXACT_FINITE_CERTIFICATE",
            "repository_status": "CONDITIONAL",
            "N_replaced_by_external_lower_bound_V": V,
            "lower_bound": encode_fraction(weighted_contact_low),
        },
        "contact_density": {
            "classification": "EXACT_FINITE_CERTIFICATE",
            "repository_status": "CONDITIONAL",
            "threshold_t": encode_fraction(Fraction(1, 2)),
            "u_2_to_minus_t": decodeable_interval(u_low, u_high),
            "centered_cap_mean_upper": encode_fraction(g_mean_upper),
            "denjoy_koksma_error_upper": encode_fraction(g_error_upper),
            "minimum_contact_count": contact_count_lower,
            "density_lower_bound": encode_fraction(Fraction(contact_count_lower, Q0)),
            "density_exceeds_43_percent": contact_count_lower * 100 > 43 * Q0,
        },
        "what_this_result_does_not_prove": "The contact bounds are conditional on a least counterexample, the external N>V computation, and Denjoy-Koksma. They do not rule out the mechanical boundary path.",
        "proves_collatz": False,
    }


def autocorrelation_data(logs: dict[str, object], boundary: dict[str, object]) -> dict[str, object]:
    ln2_info = logs["ln2"]
    delta_info = logs["delta_exp_x_minus_1"]
    rotation = boundary["rotation_sum"]
    assert isinstance(ln2_info, dict) and isinstance(delta_info, dict)
    assert isinstance(rotation, dict)
    ln2_low = Fraction(*map(int, ln2_info["lower"]))
    delta_low = Fraction(*map(int, delta_info["lower"]))
    s0_interval = rotation["S0_interval"]
    assert isinstance(s0_interval, dict)
    s0_high = Fraction(*map(int, s0_interval["upper"]))
    alpha_info = logs["alpha_log2_3"]
    assert isinstance(alpha_info, dict)
    alpha_low = Fraction(*map(int, alpha_info["lower"]))
    alpha_high = Fraction(*map(int, alpha_info["upper"]))
    rows: list[dict[str, object]] = []
    for h in SHIFTS:
        floor_h = floor_from_interval(h * alpha_low, h * alpha_high)
        u = Fraction(1 << floor_h, 3**h)
        first = (1 - u) * (1 - Fraction(1, 2) / u)
        second = (2 * u - 1) * (Fraction(1, 2) / u - Fraction(1, 2))
        integral_upper = (first + second) / ln2_low
        # Apply DK to the full q0 rotation sum (two denominator blocks).  A
        # cyclic shift modulo q0 differs in its h wrap terms; since every
        # weight lies in [1/2,1], their total variation is at most h/2.
        rotation_vh_upper = Q0 * integral_upper + 4
        cyclic_vh_upper = rotation_vh_upper + Fraction(h, 2)
        cyclic_overlap_weight_lower = 12 * V * delta_low - 3 * s0_high - cyclic_vh_upper
        cyclic_pair_count_lower = max(0, ceil(cyclic_overlap_weight_lower))
        # At most h cyclic pairs cross the endpoint.  Removing them yields a
        # certificate for genuine indices 0<=j<j+h<q0.
        overlap_count_lower = max(0, cyclic_pair_count_lower - h)
        rows.append(
            {
                "h": h,
                "floor_h_log2_3": floor_h,
                "rotation_fraction_u": encode_fraction(u),
                "integral_variation_bound": encode_fraction(integral_upper),
                "V_h_upper": encode_fraction(rotation_vh_upper),
                "cyclic_V_h_upper_including_wrap": encode_fraction(cyclic_vh_upper),
                "cyclic_weighted_overlap_lower": encode_fraction(cyclic_overlap_weight_lower),
                "cyclic_contact_pair_count_lower": cyclic_pair_count_lower,
                "contact_pair_count_lower": overlap_count_lower,
                "positive_lower_bound": overlap_count_lower > 0,
            }
        )
    h12 = next(row for row in rows if row["h"] == 12)
    if int(h12["contact_pair_count_lower"]) < 880_000_000:
        raise AssertionError("h=12 contact-pair sanity bound failed")
    return {
        "format": "collatz-phase7-contact-autocorrelation-v1",
        "classification": "EXACT_FINITE_CERTIFICATE",
        "repository_status": "CONDITIONAL",
        "derivation": [
            "W(C)>=6*V*delta-S0",
            "cyclic W(C-h)>=W(C)-V_h_cyclic",
            "cyclic W(C intersection (C-h))>=W(C)+W(C-h)-S0",
            "V_h_cyclic<=V_h+h/2 because h terms wrap and all weights lie in [1/2,1]",
            "therefore cyclic W(C intersection (C-h))>=12*V*delta-3*S0-V_h-h/2",
            "removing at most h wrap pairs gives the stored nonwrapped contact-pair count",
        ],
        "external_math_input": "DENJOY_KOKSMA for the BV shift-difference function",
        "wrap_rule": "cyclic weight variation adds at most h/2; the genuine j+h<q0 count then removes at most h cyclic pairs",
        "rows": rows,
        "h12_sanity_approximately_8_9e8_reconstructed": True,
        "what_this_result_does_not_prove": "Many contact pairs do not by themselves force descent or an impossible parity word.",
        "proves_collatz": False,
    }


def mechanical_factors(alpha_low: Fraction, alpha_high: Fraction) -> list[dict[str, object]]:
    boundaries: list[dict[str, object]] = [
        {"source_index": 0, "lower": Fraction(0), "upper": Fraction(0)},
        {"source_index": 13, "lower": Fraction(1), "upper": Fraction(1)},
    ]
    for index in range(1, 13):
        floor_value = floor_from_interval(index * alpha_low, index * alpha_high)
        frac_low = index * alpha_low - floor_value
        frac_high = index * alpha_high - floor_value
        boundaries.append(
            {
                "source_index": index,
                "lower": 1 - frac_high,
                "upper": 1 - frac_low,
            }
        )
    boundaries.sort(key=lambda row: row["lower"])
    for left, right in zip(boundaries, boundaries[1:]):
        if left["upper"] >= right["lower"]:
            raise AssertionError("mechanical intercept boundaries overlap")

    factors: list[dict[str, object]] = []
    for factor_id, (left, right) in enumerate(zip(boundaries, boundaries[1:])):
        theta = (left["upper"] + right["lower"]) / 2
        f_values = [
            floor_from_interval(index * alpha_low + theta, index * alpha_high + theta)
            for index in range(13)
        ]
        increments = [f_values[index + 1] - f_values[index] for index in range(12)]
        if any(value not in (1, 2) for value in increments):
            raise AssertionError("unexpected mechanical increment")
        factors.append(
            {
                "id": factor_id,
                "left_boundary_source": left["source_index"],
                "right_boundary_source": right["source_index"],
                "intercept_lower": encode_fraction(left["upper"]),
                "intercept_upper": encode_fraction(right["lower"]),
                "representative_intercept": encode_fraction(theta),
                "f_values": f_values,
                "increments": increments,
            }
        )
    if len(factors) != 13:
        raise AssertionError("mechanical factor count changed")
    return factors


def contact_paths(f_values: list[int]) -> Iterator[tuple[int, ...]]:
    endpoint = f_values[12]

    def visit(index: int, previous: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == 12:
            if previous < endpoint:
                yield prefix + (endpoint,)
            return
        for position in range(previous + 1, f_values[index] + 1):
            yield from visit(index + 1, position, prefix + (position,))

    yield from visit(1, 0, (0,))


def affine_for_word(word: str) -> tuple[int, int, int]:
    coefficient = 1
    constant = 0
    denominator = 1
    for bit in word:
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
    return coefficient, constant, denominator


def parity_residue_from_affine(coefficient: int, constant: int, denominator: int) -> int:
    return (-constant * pow(coefficient, -1, denominator)) % denominator


def dangerous_decomposition(word: str) -> list[str] | None:
    memo: dict[int, list[str] | None] = {len(word): []}
    for index in range(len(word) - 1, -1, -1):
        memo[index] = None
        for block in DANGEROUS_WORDS:
            if word.startswith(block, index) and memo.get(index + len(block)) is not None:
                suffix = memo[index + len(block)]
                assert suffix is not None
                memo[index] = [block, *suffix]
                break
    return memo[0]


MACRO_FIELDS = [
    "id",
    "mechanical_intercept_class",
    "defect_path",
    "binary_parity_word",
    "shortcut_length",
    "odd_count",
    "affine_A",
    "affine_B",
    "affine_denominator",
    "multiplier",
    "affine_intercept",
    "rational_fixed_point",
    "residue_mod_2_power",
    "modulus_2_exponent",
    "endpoint_base",
    "source_residues_mod_9",
    "endpoint_residue_mod_9",
    "source_residues_mod_27",
    "endpoint_residue_mod_27",
    "phase5_dangerous_cycle_decomposition",
]


def expand_macro(row: list[object]) -> dict[str, object]:
    return dict(zip(MACRO_FIELDS, row, strict=True))


def macro12_data(logs: dict[str, object]) -> dict[str, object]:
    alpha_info = logs["alpha_log2_3"]
    assert isinstance(alpha_info, dict)
    alpha_low = Fraction(*map(int, alpha_info["lower"]))
    alpha_high = Fraction(*map(int, alpha_info["upper"]))
    factors = mechanical_factors(alpha_low, alpha_high)
    records: list[list[object]] = []
    counts: list[int] = []
    for factor in factors:
        f_values = factor["f_values"]
        assert isinstance(f_values, list)
        count = 0
        for positions in contact_paths(f_values):
            length = positions[-1]
            odd_positions = set(positions[:-1])
            word = "".join("1" if index in odd_positions else "0" for index in range(length))
            coefficient, constant, denominator = affine_for_word(word)
            if word.count("1") != 12 or coefficient != 3**12:
                raise AssertionError("macro odd count changed")
            residue = parity_residue_from_affine(coefficient, constant, denominator)
            source = residue if residue >= 2 else residue + denominator
            endpoint = (coefficient * source + constant) // denominator
            defects = [f_values[index] - positions[index] for index in range(13)]
            fixed = Fraction(constant, denominator - coefficient)
            records.append(
                [
                    len(records),
                    factor["id"],
                    defects,
                    word,
                    length,
                    12,
                    coefficient,
                    constant,
                    denominator,
                    [coefficient, denominator],
                    [constant, denominator],
                    [fixed.numerator, fixed.denominator],
                    residue,
                    length,
                    endpoint,
                    "ALL",
                    endpoint % 9,
                    "ALL",
                    endpoint % 27,
                    dangerous_decomposition(word),
                ]
            )
            count += 1
        factor["macro_count"] = count
        counts.append(count)
    if len(records) != 87_015:
        raise AssertionError(f"macro count changed: {len(records)}")

    noncontracting = next(row for row in records if int(row[6]) >= int(row[8]))
    nondecomposable = next(row for row in records if row[19] is None)
    first_realizable = records[0]
    return {
        "format": "collatz-phase7-macro12-v1",
        "classification": "EXACT_FINITE_CERTIFICATE",
        "repository_status": "VERIFIED_FINITE",
        "factor_construction": {
            "method": "13 exact intercept intervals cut by 1-{i*log2(3)}, 1<=i<=12",
            "external_sturmian_complexity_theorem_used": False,
            "factors": factors,
        },
        "record_schema": MACRO_FIELDS,
        "records": records,
        "macro_count": len(records),
        "counts_by_factor": counts,
        "cegar": [
            {
                "hypothesis": "every contact-return macro has multiplier < 1",
                "classification": "FAILED_HYPOTHESIS",
                "repository_status": "REFUTED",
                "smallest_exact_counterexample": expand_macro(noncontracting),
            },
            {
                "hypothesis": "every contact-return macro is a concatenation of the four Phase 5 dangerous words",
                "classification": "FAILED_HYPOTHESIS",
                "repository_status": "REFUTED",
                "smallest_exact_counterexample": expand_macro(nondecomposable),
            },
            {
                "hypothesis": "contact-return macros are arithmetically unrealizable over positive integers",
                "classification": "FAILED_HYPOTHESIS",
                "repository_status": "REFUTED",
                "smallest_exact_counterexample": expand_macro(first_realizable),
            },
        ],
        "universal_obstruction_found": False,
        "what_this_result_does_not_prove": "The finite macro alphabet and its exact counterexamples do not decide which macros can concatenate along one positive infinite orbit.",
        "proves_collatz": False,
    }


def fixed_q_positions(q: int) -> Iterator[tuple[int, ...]]:
    f_values = [(3**index).bit_length() - 1 for index in range(q)]

    def visit(index: int, previous: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == q:
            yield prefix
            return
        for position in range(previous + 1, f_values[index] + 1):
            yield from visit(index + 1, position, prefix + (position,))

    if q == 0:
        yield ()
    else:
        yield from visit(1, 0, (0,))


def layer_record(q: int, positions: tuple[int, ...]) -> tuple[object, ...]:
    power_three = 3**q
    k = power_three.bit_length()
    denominator = 1 << k
    constant = sum(3 ** (q - 1 - index) * (1 << position) for index, position in enumerate(positions))
    residue = parity_residue_from_affine(power_three, constant, denominator)
    source = residue if residue >= 2 else residue + denominator
    endpoint = (power_three * source + constant) // denominator
    f_values = [(3**index).bit_length() - 1 for index in range(q)]
    defects = tuple(f_values[index] - positions[index] for index in range(q))
    word = "".join("1" if index in set(positions) else "0" for index in range(k))
    boundary_word = "".join("1" if index in set(f_values) else "0" for index in range(k))
    first_difference = next((index for index, pair in enumerate(zip(word, boundary_word, strict=True)) if pair[0] != pair[1]), None)
    if first_difference is not None:
        boundary_constant = sum(
            3 ** (q - 1 - index) * (1 << position) for index, position in enumerate(f_values)
        )
        boundary_residue = parity_residue_from_affine(power_three, boundary_constant, denominator)
        if residue % (1 << first_difference) != boundary_residue % (1 << first_difference):
            raise AssertionError("2-adic first-difference prefix mismatch")
        if residue % (1 << (first_difference + 1)) == boundary_residue % (1 << (first_difference + 1)):
            raise AssertionError("2-adic rigidity separation failed")
    reverse_residue = endpoint % power_three
    return (
        constant,
        source,
        sum(defects),
        max(defects, default=0),
        sum(value == 0 for value in defects),
        -1 if first_difference is None else first_difference,
        reverse_residue,
        min(reverse_residue, power_three - reverse_residue),
        word,
        list(positions),
        list(defects),
        endpoint,
    )


FRONTIER_FIELDS = [
    "B",
    "smallest_positive_residue_r2",
    "defect_sum",
    "defect_max",
    "contact_count",
    "first_differing_parity_position",
    "reverse_3adic_endpoint_residue",
    "reverse_3adic_height",
    "parity_word",
    "odd_positions",
    "defect_path",
    "endpoint_base",
]


def arithmetic_frontier_data() -> dict[str, object]:
    layers: list[dict[str, object]] = []
    for q in FRONTIER_Q:
        rows = [layer_record(q, positions) for positions in fixed_q_positions(q)]
        if len(rows) != EXPECTED_LAYER_COUNTS[q]:
            raise AssertionError(f"fixed-q layer count changed for q={q}")
        residues = {int(row[1]) for row in rows}
        if len(residues) != len(rows):
            raise AssertionError("fixed-(k,q) 2-adic rigidity collision")
        ordered = sorted(rows, key=lambda row: (-int(row[0]), int(row[1]), str(row[8])))
        pareto: list[tuple[object, ...]] = []
        best_residue: int | None = None
        for row in ordered:
            residue = int(row[1])
            if best_residue is None or residue < best_residue:
                pareto.append(row)
                best_residue = residue
        top_counts = sorted({value for value in (1, 10, 100, 1000, 10_000, len(rows)) if value <= len(rows)})
        separation: list[dict[str, object]] = []
        for count in top_counts:
            prefix = ordered[:count]
            threshold = int(prefix[-1][0])
            minimum_row = min(prefix, key=lambda row: int(row[1]))
            separation.append(
                {
                    "top_B_record_count": count,
                    "B_threshold": threshold,
                    "certified_minimum_r2": int(minimum_row[1]),
                    "witness_word": minimum_row[8],
                    "scope": f"exhaustive fixed layer q={q}",
                }
            )
        layers.append(
            {
                "q": q,
                "K_q": (3**q).bit_length(),
                "enumerated_words": len(rows),
                "expected_A100982_value": EXPECTED_LAYER_COUNTS[q],
                "all_residues_distinct": True,
                "pareto_schema": FRONTIER_FIELDS,
                "pareto_records": [list(row) for row in pareto],
                "finite_separation_certificates": separation,
            }
        )
    return {
        "format": "collatz-phase7-arithmetic-frontier-v1",
        "classification": "EXACT_FINITE_CERTIFICATE",
        "repository_status": "VERIFIED_FINITE",
        "fixed_k_q_rigidity": {
            "classification": "VERIFIED_SYMBOLIC",
            "repository_status": "VERIFIED_THEOREM",
            "statement": "distinct length-k parity words first differing at position i select distinct residues modulo 2^(i+1), hence distinct residues modulo 2^k",
            "proof": "inductively each next parity bit selects exactly one of the two lifts modulo 2^(i+1)",
            "overlap_audit": "This is the internally rederived fixed-(k,q) 2-adic rigidity structure also discussed by Hikawa (2026).",
        },
        "layers": layers,
        "universal_tradeoff_found": False,
        "heuristic_interpretation": {
            "classification": "HEURISTIC",
            "repository_status": "HEURISTIC",
            "statement": "The finite Pareto fronts suggest tension between high B and small r2, but no monotone inequality uniform in q was found.",
        },
        "what_this_result_does_not_prove": "Every separation statement is confined to the enumerated q in {1,3,5,17}; it is not asymptotic.",
        "proves_collatz": False,
    }


def mixed_block_audit(bound: int = 128) -> dict[str, object]:
    tested = 0
    contracting = 0
    counterexamples: list[dict[str, object]] = []
    closest: tuple[int, int, int, int, int, int, int] | None = None
    powers_81 = [1]
    powers_32 = [1]
    powers_9 = [1]
    powers_16 = [1]
    for _ in range(bound):
        powers_81.append(powers_81[-1] * 81)
        powers_32.append(powers_32[-1] * 32)
        powers_9.append(powers_9[-1] * 9)
        powers_16.append(powers_16[-1] * 16)
    for r in range(1, bound + 1):
        a_coefficient = powers_81[r]
        a_denominator = powers_32[r]
        a_constant = 73 * (a_coefficient - a_denominator) // 49
        for s in range(1, bound + 1):
            tested += 1
            b_coefficient = powers_9[s]
            b_denominator = powers_16[s]
            b_constant = 5 * (b_denominator - b_coefficient) // 7
            coefficient = b_coefficient * a_coefficient
            denominator = b_denominator * a_denominator
            if coefficient >= denominator:
                continue
            contracting += 1
            constant = b_coefficient * a_constant + b_constant * a_denominator
            residue = parity_residue_from_affine(coefficient, constant, denominator)
            source = residue if residue >= 2 else residue + denominator
            endpoint = (coefficient * source + constant) // denominator
            fixed_gap = source * (denominator - coefficient) - constant
            row = {
                "r": r,
                "s": s,
                "shortcut_length": 5 * r + 4 * s,
                "source": source,
                "endpoint": endpoint,
                "fixed_point_comparison_gap": fixed_gap,
            }
            if endpoint > source:
                counterexamples.append(row)
            comparison = (fixed_gap, denominator - coefficient, r, s, source, endpoint, constant)
            if closest is None or comparison[0] * closest[1] < closest[0] * comparison[1]:
                closest = comparison
    return {
        "classification": "EXACT_FINITE_CERTIFICATE",
        "repository_status": "VERIFIED_FINITE",
        "family": "A^rB^s with A=11101 and B=1100",
        "scope": {"1<=r<=bound": bound, "1<=s<=bound": bound},
        "pairs_tested": tested,
        "contracting_pairs_tested": contracting,
        "paradoxical_endpoint_counterexamples": counterexamples,
        "finite_candidate_survives": not counterexamples,
        "universal_claim": {
            "classification": "CONJECTURE",
            "repository_status": "OPEN",
            "statement": "a positive integral A^rB^s realization with total multiplier <1 cannot have endpoint greater than its source",
            "proved": False,
        },
        "closest_fixed_point_gap_record": None
        if closest is None
        else {"gap_numerator": closest[0], "gap_denominator": closest[1], "r": closest[2], "s": closest[3], "source": closest[4], "endpoint": closest[5]},
        "what_this_result_does_not_prove": "Absence of a bounded counterexample is not a proof for arbitrary r,s.",
        "proves_collatz": False,
    }


def literature_audit() -> dict[str, object]:
    return {
        "classification": "EXTERNAL_MATH_INPUT",
        "repository_status": "EXTERNAL_THEOREM",
        "items": [
            {
                "source": "Terras (1976), A stopping time problem on the positive integers",
                "relationship": "Introduces coefficient stopping/admissible parity vectors; Phase 6 safe prefixes are the complementary unconverged-prefix language.",
            },
            {
                "source": "Garner (1981), On the Collatz 3n+1 algorithm",
                "relationship": "Already uses continued fractions of log2(3) with an external verification bound. The Phase 7 first-pair certificate is a modern exact-enclosure version, not a novel use of continued fractions.",
            },
            {
                "source": "Rozier--Terracol (2026), Paradoxical behavior in Collatz sequences",
                "relationship": "Coefficient-safe/paradoxical finite words and continued-fraction exceptional ratios substantially overlap the Phase 6/7 setting.",
            },
            {
                "source": "Tong Niu, arXiv:2605.13886v2 (withdrawn 2026)",
                "relationship": "Withdrawn because Rozier--Terracol v4 already enumerated the stated finite paradoxical data; not used as authority.",
            },
            {
                "source": "Hikawa (2026), Finite-Dimensional Combinatorial and Arithmetic Structures of Parity Vectors",
                "relationship": "Preprint explicitly notes substantial overlap with Winkler and identifies its W(d),w(k) with A100982,A076227. Fixed-(k,q) rigidity is independently rederived here.",
            },
            {
                "source": "OEIS A076227",
                "relationship": "Exactly the Phase 1/6 safe-prefix counts a_k, e.g. a_26=1037374; these counts are not new.",
            },
            {
                "source": "OEIS A100982",
                "relationship": "Counts admissible first-crossing sequences by odd-step order; Phase 7 fixed-q layer counts reproduce selected terms.",
            },
        ],
        "q4961_audit": {
            "facts": ["4961=4296+665", "665 is the denominator of convergent 1054/665 to log2(3)", "q=4961 is the next Phase 6 H_q record after q=4296"],
            "interpretation": "The obstacle is continued-fraction structured, consistent with Garner's method; it is not evidence of a new independent phenomenon.",
        },
        "newness_boundary": "New repository contribution is the exact certificate composition and boundary-defect/contact audit, not the classical parity-vector counts or continued-fraction principle.",
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, symbolic: dict[str, object], autocorrelation: dict[str, object], macros: dict[str, object], frontier: dict[str, object], mixed: dict[str, object]) -> None:
    contact = symbolic["contact_density"]
    assert isinstance(contact, dict)
    rows = autocorrelation["rows"]
    assert isinstance(rows, list)
    h12 = next(row for row in rows if row["h"] == 12)
    cegar = macros["cegar"]
    assert isinstance(cegar, list)
    lines = [
        "# Phase 7 boundary-defect obstruction report",
        "",
        "This report does not claim a proof of the Collatz conjecture.",
        "",
        "## VERIFIED_SYMBOLIC",
        "",
        "- Under the least-counterexample and first-crossing assumptions, the independent algebra gives `S(a)>=3*N*delta` and `W(C)>=6*N*delta-S0`.",
        "- This identity uses no external theorem. The substitution `N>V` is explicitly external computational evidence.",
        "",
        "## EXACT_FINITE_CERTIFICATE",
        "",
        f"- Exact logarithm enclosures and Stern--Brocot parents certify the first necessary pair `(q,K)=({Q0},{K0})` without constructing giant powers.",
        f"- With the external inputs separated, the certified contact count is at least `{contact['minimum_contact_count']}`, exceeding 43 percent of q0.",
        f"- For h=12 the certified contact-pair lower bound is `{h12['contact_pair_count_lower']}`.",
        f"- The exact 12-odd contact-return alphabet has `{macros['macro_count']}` macros across 13 mechanical factors.",
        "- Fixed-(k,q) arithmetic layers q=1,3,5,17 reproduce the selected A100982 counts and have distinct 2-adic residues.",
        "",
        "## EXTERNAL_MATH_INPUT",
        "",
        "- `DENJOY_KOKSMA` is used for rotation sums and discrepancy. Its two consecutive continued-fraction denominator premises are checked exactly, but the theorem is not reproved here.",
        "- Terras, Garner, Rozier--Terracol, Hikawa, A076227, and A100982 show substantial prior overlap. Tong Niu's 2026 preprint is withdrawn and is not used as authority.",
        "",
        "## EXTERNAL_COMPUTATIONAL_INPUT",
        "",
        f"- `N>{V}` is assumed only as the supplied external verification bound. Its provenance/global verification is not reproduced.",
        "",
        "## FAILED_HYPOTHESIS",
        "",
        *[f"- {row['hypothesis']}: smallest exact counterexample macro id `{row['smallest_exact_counterexample']['id']}`." for row in cegar],
        "",
        "## HEURISTIC / CONJECTURE",
        "",
        "- Finite Pareto fronts suggest a high-B/small-r2 tension, but no q-uniform monotonicity or separation lemma was found.",
        f"- The contracting `A^rB^s` endpoint candidate has no counterexample in the exact bounded scope, but remains `{mixed['universal_claim']['repository_status']}` rather than a theorem.",
        "",
        "## Main obstruction",
        "",
        "The analytic argument forces many contacts and contact pairs, but the 87,015-macro alphabet contains noncontracting, non-dangerous-decomposable, and positively realizable macros. No theorem links high correction B to a sufficiently large least positive 2-adic representative for unbounded q.",
        "",
        "## What this result does not prove",
        "",
        "It does not exclude a least counterexample, prove an eventual lower bound for M(k), or prove the Collatz conjecture. All huge-q contact conclusions depend on the external N>V computation and the named Denjoy--Koksma theorem.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(artifact_dir: Path, *, mixed_bound: int = 128) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    logs = log_data()
    symbolic = symbolic_boundary_data(logs)
    autocorrelation = autocorrelation_data(logs, symbolic)
    macros = macro12_data(logs)
    frontier = arithmetic_frontier_data()
    mixed = mixed_block_audit(mixed_bound)
    literature = literature_audit()
    symbolic_payload = {
        "format": "collatz-phase7-symbolic-verifier-input-v1",
        "first_crossing": logs,
        "boundary_defect": symbolic["symbolic_identity"],
        "valid": True,
        "proves_collatz": False,
    }
    boundary_payload = {**symbolic, "literature_audit": literature}
    frontier["mixed_block_adversarial_audit"] = mixed
    # This is the search-side certificate input.  The required
    # phase7_symbolic_verifier.json is deliberately written only by the
    # independent verifier in verifier/verify_phase7.py.
    write_json(artifact_dir / "phase7_symbolic_certificate.json", symbolic_payload)
    write_json(artifact_dir / "phase7_boundary_defect.json", boundary_payload)
    write_json(artifact_dir / "phase7_contact_autocorrelation.json", autocorrelation)
    write_json(artifact_dir / "phase7_macro12.json", macros)
    write_json(artifact_dir / "phase7_arithmetic_frontier.json", frontier)
    write_report(
        artifact_dir / "phase7_obstruction_report.md",
        symbolic,
        autocorrelation,
        macros,
        frontier,
        mixed,
    )
    return {
        "first_pair": [Q0, K0],
        "minimum_contact_count": symbolic["contact_density"]["minimum_contact_count"],
        "h12_contact_pairs": next(row["contact_pair_count_lower"] for row in autocorrelation["rows"] if row["h"] == 12),
        "macro_count": macros["macro_count"],
        "frontier_q": list(FRONTIER_Q),
        "mixed_bound": mixed_bound,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--mixed-bound", type=int, default=128)
    args = parser.parse_args()
    if args.mixed_bound < 1:
        parser.error("--mixed-bound must be positive")
    result = generate(args.artifact_dir, mixed_bound=args.mixed_bound)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
