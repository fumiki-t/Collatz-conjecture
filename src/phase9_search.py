#!/usr/bin/env python3
"""Generate exact Phase 9 two-sided-criticality artifacts.

All acceptance decisions use integers or rational intervals.  The large
first-crossing pair is handled through logarithmic and continued-fraction
certificates; ``2^K0`` and ``3^Q0`` are never constructed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from fractions import Fraction
from pathlib import Path


Q0 = 72_057_431_991
K0 = 114_208_327_604
V = 2075 * (1 << 60)
DMAX = 4_142_380_786
OLD_CONTACTS = 31_327_720_462
OCTAVE_EXCEPTIONS = 5
CF_BLOCKS = (6_586_818_670, 65_470_613_321)
A_WORD = "11101"
B_WORD = "1100"
A_MAP = (81, 73, 32)
B_MAP = (9, 5, 16)
PHASE7_MACRO0 = "1111111111110000000"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def encode_interval(lower: Fraction, upper: Fraction) -> dict[str, list[str]]:
    if not lower < upper:
        raise ValueError("invalid interval")
    return {"lower": encode_fraction(lower), "upper": encode_fraction(upper)}


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def outward_dyadic(lower: Fraction, upper: Fraction, bits: int = 256) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    low = lower.numerator * scale // lower.denominator
    high = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(low, scale), Fraction(high, scale)


def log_interval(numerator: int, denominator: int = 1, *, terms: int = 192) -> tuple[Fraction, Fraction]:
    if numerator <= denominator or denominator <= 0:
        raise ValueError("log enclosure requires numerator > denominator > 0")
    z = Fraction(numerator - denominator, numerator + denominator)
    square = z * z
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= square
    lower = 2 * total
    upper = lower + 2 * power / ((2 * terms + 1) * (1 - square))
    return outward_dyadic(lower, upper)


def expm1_interval(lower: Fraction, upper: Fraction, *, terms: int = 24) -> tuple[Fraction, Fraction]:
    if not 0 < lower <= upper < 1:
        raise ValueError("expm1 enclosure outside (0,1)")

    def partial(value: Fraction) -> tuple[Fraction, Fraction]:
        result = Fraction(1)
        term = Fraction(1)
        for index in range(1, terms + 1):
            term = term * value / index
            result += term
        next_term = term * value / (terms + 1)
        return result, result + next_term / (1 - value / (terms + 2))

    low, _ = partial(lower)
    _, high = partial(upper)
    return outward_dyadic(low - 1, high - 1)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def affine_word(word: str) -> tuple[int, int, int]:
    coefficient = 1
    constant = 0
    denominator = 1
    for bit in word:
        if bit not in "01":
            raise ValueError("nonbinary parity word")
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
    return coefficient, constant, denominator


def least_realization(coefficient: int, constant: int, denominator: int) -> tuple[int, int]:
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    source = residue or denominator
    numerator = coefficient * source + constant
    if numerator % denominator:
        raise AssertionError("affine realization is not integral")
    return source, numerator // denominator


def continued_fraction(value: Fraction) -> list[int]:
    terms: list[int] = []
    while value.denominator != 1:
        quotient = value.numerator // value.denominator
        terms.append(quotient)
        value = 1 / (value - quotient)
    terms.append(value.numerator)
    return terms


def common_cf_prefix(lower: Fraction, upper: Fraction) -> tuple[int, ...]:
    left = continued_fraction(lower)
    right = continued_fraction(upper)
    result: list[int] = []
    for first, second in zip(left, right, strict=False):
        if first != second:
            break
        result.append(first)
    return tuple(result)


def convergents(terms: tuple[int, ...] | list[int]) -> list[tuple[int, int]]:
    p2, p1 = 0, 1
    q2, q1 = 1, 0
    result: list[tuple[int, int]] = []
    for term in terms:
        p = term * p1 + p2
        q = term * q1 + q2
        result.append((p, q))
        p2, p1 = p1, p
        q2, q1 = q1, q
    return result


def floor_alpha_multiple(index: int, alpha_low: Fraction, alpha_high: Fraction) -> int:
    if index == 0:
        return 0
    low = index * alpha_low
    high = index * alpha_high
    value = low.numerator // low.denominator
    if high.numerator // high.denominator != value or high == value:
        raise AssertionError(f"log enclosure does not determine floor at {index}")
    return value


def common_arithmetic() -> dict[str, object]:
    ln2_low, ln2_high = log_interval(2, terms=240)
    ln3_low, ln3_high = log_interval(3, terms=240)
    alpha_low = ln3_low / ln2_high
    alpha_high = ln3_high / ln2_low
    gap_low = K0 * ln2_low - Q0 * ln3_high
    gap_high = K0 * ln2_high - Q0 * ln3_low
    delta_low, delta_high = expm1_interval(gap_low, gap_high)
    s0_low = Fraction(Q0, 2) / ln2_high - 2
    s0_high = Fraction(Q0, 2) / ln2_low + 2
    weight_lower = 6 * V * delta_low - s0_high
    if not 0 < gap_low < gap_high < 1 or weight_lower <= 0:
        raise AssertionError("Phase 9 common arithmetic did not close")
    return {
        "ln2": (ln2_low, ln2_high),
        "ln3": (ln3_low, ln3_high),
        "alpha": (alpha_low, alpha_high),
        "log_gap": (gap_low, gap_high),
        "delta": (delta_low, delta_high),
        "S0": (s0_low, s0_high),
        "weight_lower": weight_lower,
    }


def forced_contact_data(common: dict[str, object]) -> dict[str, object]:
    alpha_low, alpha_high = common["alpha"]
    s0_low, _ = common["S0"]
    weight_lower = common["weight_lower"]
    assert isinstance(alpha_low, Fraction) and isinstance(alpha_high, Fraction)
    assert isinstance(s0_low, Fraction) and isinstance(weight_lower, Fraction)
    truth_table: list[dict[str, object]] = []
    for contact in (0, 1):
        for increment in (1, 2):
            for next_contact in (0, 1):
                closure_ok = not (contact == 1 and increment == 1 and next_contact == 0)
                defect = 1 - contact
                next_defect = 1 - next_contact
                odd_gap = increment + defect - next_defect
                truth_table.append(
                    {
                        "c_j": contact,
                        "b_j": increment,
                        "c_next": next_contact,
                        "closure_ok": closure_ok,
                        "e_j": odd_gap,
                        "positive_when_closure_ok": (not closure_ok) or odd_gap >= 1,
                    }
                )
    if not all(bool(row["positive_when_closure_ok"]) for row in truth_table):
        raise AssertionError("contact construction truth table failed")
    if not s0_low > weight_lower:
        raise AssertionError("all-contact no-go witness misses weighted pressure")
    return {
        "format": "collatz-phase9-forced-contact-v1",
        "P59": {
            "repository_status": "CONDITIONAL",
            "symbolic_algebra_valid_for": "every coefficient-safe defect path",
            "least_counterexample_role": "only the Phase 7/8 application is conditional",
            "recurrence": "a_(j+1)=a_j+b_j-e_j",
            "forced_closure": "a_j=0 and b_j=1 imply e_j=1 and a_(j+1)=0",
            "phase_interval": "b_j=1 iff 0<=theta_j<2-alpha",
            "successor_weight_ratio": [2, 3],
        },
        "phase_partition": {
            "alpha_interval": encode_interval(alpha_low, alpha_high),
            "L": "[0,2-alpha)",
            "M": "[2-alpha,alpha-1)",
            "H": "[alpha-1,1)",
            "L_successor_is_H": True,
            "exact_weight_identity": "2^(-(theta+alpha-1))=(2/3)*2^(-theta)",
        },
        "NG17": {
            "repository_status": "REFUTED",
            "statement": "forced-contact closure plus weighted contact pressure alone excludes every finite critical word",
            "corrected_construction_domain": "c_0=1 is required for a zero-indexed parity word; arbitrary later c_j are allowed subject to closure",
            "construction": "a_j=1-c_j; d_j=f_j-a_j; e_j=b_j+a_j-a_(j+1)",
            "truth_table": truth_table,
            "q0_symbolic_witness": {
                "contact_indicator": "c_j=1 for every 0<=j<q0",
                "defects": "a_j=0",
                "odd_positions": "d_j=floor(j*alpha)",
                "weighted_contact_equals": "S0",
                "S0_lower": encode_fraction(s0_low),
                "required_weight_lower": encode_fraction(weight_lower),
                "strictly_satisfies_pressure": True,
                "giant_parity_word_constructed": False,
            },
            "surviving_stronger_targets": [
                "least positive inverse-parity representative",
                "endpoint near-return condition",
                "simultaneous 2-adic/3-adic residue box",
            ],
        },
        "what_this_result_does_not_prove": "NG17 refutes only the contact-only mechanism. It does not refute a theorem that also uses endpoint or least-representative arithmetic.",
        "proves_collatz": False,
    }


def dual_candidate(lam: Fraction, common: dict[str, object]) -> dict[str, object]:
    if not Fraction(2, 3) <= lam < Fraction(3, 4):
        raise ValueError("dual parameter outside certified regime")
    ln2_low, ln2_high = common["ln2"]
    weight_lower = common["weight_lower"]
    assert isinstance(ln2_low, Fraction) and isinstance(ln2_high, Fraction)
    assert isinstance(weight_lower, Fraction)
    first_ratio = Fraction(5, 1) / (6 * lam)
    second_ratio = Fraction(3, 1) / (4 * lam)
    first_low, first_high = log_interval(first_ratio.numerator, first_ratio.denominator, terms=96)
    second_low, second_high = log_interval(second_ratio.numerator, second_ratio.denominator, terms=96)
    constant = Fraction(29, 12) - 3 * lam
    numerator_low = constant - 2 * lam * first_high - lam * second_high
    numerator_high = constant - 2 * lam * first_low - lam * second_low
    integral_low = numerator_low / ln2_high
    integral_high = numerator_high / ln2_low
    variation = Fraction(29, 6) - 6 * lam
    endpoint_damage = 1 - lam
    rotation_upper = Q0 * integral_high + 2 * variation + endpoint_damage
    count_fraction = (weight_lower - rotation_upper) / lam
    count = ceil_fraction(count_fraction)
    return {
        "lambda": encode_fraction(lam),
        "contact_lower": count,
        "integral": encode_interval(integral_low, integral_high),
        "circle_total_variation": encode_fraction(variation),
        "two_block_DK_error": encode_fraction(2 * variation),
        "finite_endpoint_damage": encode_fraction(endpoint_damage),
        "rotation_sum_upper": encode_fraction(rotation_upper),
        "pre_ceiling_count_lower": encode_fraction(count_fraction),
        "support_log_ratios": {
            "L_log_argument": encode_fraction(first_ratio),
            "M_log_argument": encode_fraction(second_ratio),
        },
    }


def contact_dual_data(common: dict[str, object], artifact_dir: Path) -> dict[str, object]:
    candidates: list[dict[str, object]] = []
    for denominator in range(2, 257):
        for numerator in range((2 * denominator + 2) // 3, (3 * denominator - 1) // 4 + 1):
            if math.gcd(numerator, denominator) != 1:
                continue
            lam = Fraction(numerator, denominator)
            if Fraction(2, 3) <= lam < Fraction(3, 4):
                candidate = dual_candidate(lam, common)
                candidates.append(candidate)
    selected = max(
        candidates,
        key=lambda row: (
            int(row["contact_lower"]),
            -int(row["lambda"][1]),
            -int(row["lambda"][0]),
        ),
    )
    if selected["lambda"] != ["143", "199"] or selected["contact_lower"] != 35_251_435_772:
        raise AssertionError("contact dual optimum/sanity value changed")
    phase7_path = artifact_dir / "phase7_boundary_defect.json"
    return {
        "format": "collatz-phase9-contact-dual-v1",
        "repository_status": "CONDITIONAL",
        "optimization_scope": {
            "rational_lambda": "2/3<=lambda<3/4",
            "maximum_denominator": 256,
            "candidate_count": len(candidates),
            "global_optimum_claimed": False,
            "candidate_summary": [
                [int(row["lambda"][0]), int(row["lambda"][1]), int(row["contact_lower"])]
                for row in candidates
            ],
        },
        "pointwise_dual": {
            "L_pair": "max(0,(5/3)*2^(-theta)-2*lambda)",
            "M_single": "max(0,2^(-theta)-lambda)",
            "unpaired_H_nonpositive_because": "lambda>=2/3=max_(theta in H) 2^(-theta)",
            "L_support_endpoint": "log2(5/(6*lambda))",
            "M_support": "[2-alpha,log2(1/lambda))",
        },
        "selected": selected,
        "forced_closure_contact_lower": selected["contact_lower"],
        "previous_phase7_contact_lower": OLD_CONTACTS,
        "strict_improvement": int(selected["contact_lower"]) - OLD_CONTACTS,
        "dependencies": {
            "P59": "forced L-to-H pairing",
            "P57_weight_pressure": "W(C)>=6V*delta-S0",
            "X02": "N>V, not reproved",
            "EXT04": "Denjoy-Koksma, not reproved",
            "phase7_boundary_defect_sha256": sha256(phase7_path),
            "q0_ostrowski_blocks": list(CF_BLOCKS),
        },
        "what_this_result_does_not_prove": "The denominator-256 dual search is not a proof of a globally optimal lambda, and the improved contact count does not constrain the ordinary inverse-parity residue by itself.",
        "proves_collatz": False,
    }


def short_return_data(dual: dict[str, object], artifact_dir: Path) -> dict[str, object]:
    octave = json.loads((artifact_dir / "phase8_octave_bridge.json").read_text(encoding="utf-8"))
    exceptions = int(octave["denjoy_koksma"]["maximum_integer_exception_count"])
    if exceptions != OCTAVE_EXCEPTIONS:
        raise AssertionError("Phase 8 exception count changed")

    def bound(contacts: int) -> dict[str, int]:
        long_gaps = (Q0 - contacts) // 2
        raw = (contacts - 1) - long_gaps
        return {
            "contacts": contacts,
            "maximum_gaps_at_least_3": long_gaps,
            "gap_at_most_2_lower": raw,
            "exception_damage": 2 * exceptions,
            "first_octave_lower": raw - 2 * exceptions,
        }

    baseline = bound(OLD_CONTACTS)
    closure = bound(int(dual["forced_closure_contact_lower"]))
    if baseline["first_octave_lower"] != 10_962_864_687:
        raise AssertionError("baseline improved gap formula changed")
    if closure["first_octave_lower"] != 16_848_437_652:
        raise AssertionError("closure-aware gap formula changed")
    return {
        "format": "collatz-phase9-short-return-v1",
        "E14": {
            "repository_status": "VERIFIED_FINITE",
            "conditional_dependencies": ["P58", "P59/P57", "X02", "EXT04", "Phase 7 contact certificate"],
            "exact_formula": "(M-1)-floor((q0-M)/2)",
            "baseline_phase7_contacts": baseline,
            "forced_closure_contacts": closure,
        },
        "phase8_octave_bridge_sha256": sha256(artifact_dir / "phase8_octave_bridge.json"),
        "what_this_result_does_not_prove": "A large number of short returns does not supply a well-founded rank for their concatenations.",
        "proves_collatz": False,
    }


def endpoint_displacement_data(common: dict[str, object], artifact_dir: Path) -> dict[str, object]:
    ln2_low, ln2_high = common["ln2"]
    ln3_low, ln3_high = common["ln3"]
    gap_low, gap_high = common["log_gap"]
    delta_low, delta_high = common["delta"]
    s0_low, s0_high = common["S0"]
    assert all(
        isinstance(value, Fraction)
        for value in (ln2_low, ln2_high, ln3_low, ln3_high, gap_low, gap_high, delta_low, delta_high, s0_low, s0_high)
    )
    displacement_upper = (s0_high / 3 - V * delta_low) / (1 + delta_low)
    dmax = displacement_upper.numerator // displacement_upper.denominator
    h_upper = s0_high / (3 * delta_low)
    if dmax != DMAX or not h_upper + dmax < 2**72 or not dmax < 2**32:
        raise AssertionError("endpoint displacement bounds changed")
    inequality_checks = {
        "dmax_lt_V": dmax < V,
        "3dmax_plus_1_lt_V": 3 * dmax + 1 < V,
        "2dmax_minus_1_lt_V": 2 * dmax - 1 < V,
        "8dmax_minus_5_lt_V": 8 * dmax - 5 < V,
    }
    if not all(inequality_checks.values()):
        raise AssertionError("endpoint minimality scalar inequality failed")
    short = json.loads((artifact_dir / "phase8_short_excursions.json").read_text(encoding="utf-8"))
    g4 = next(row for row in short["maps"] if row["name"] == "G4")
    if g4["word"] != "1100" or g4["map"] != [9, 5, 16]:
        raise AssertionError("Phase 8 G4 dependency changed")
    return {
        "format": "collatz-phase9-endpoint-displacement-v1",
        "P60": {
            "repository_status": "CONDITIONAL",
            "scope": "only the least-counterexample first-crossing case (q,K)=(q0,K0)",
            "near_return_identity": "S(a)=3*N*delta+3*(1+delta)*d",
            "solved_identity": "d=(S(a)/3-N*delta)/(1+delta)",
            "assumptions": ["X=T^K0(N)=N+d", "S(a)<=S0", "N>V", "d>=0"],
            "displacement_upper_fraction": encode_fraction(displacement_upper),
            "maximum_integer_displacement": dmax,
            "strictly_below_2^32": True,
        },
        "exact_enclosures": {
            "ln2": encode_interval(ln2_low, ln2_high),
            "ln3": encode_interval(ln3_low, ln3_high),
            "K0_ln2_minus_q0_ln3": encode_interval(gap_low, gap_high),
            "delta": encode_interval(delta_low, delta_high),
            "S0": encode_interval(s0_low, s0_high),
            "direct_giant_powers_constructed": False,
        },
        "source_endpoint_size": {
            "Hq0_upper": encode_fraction(h_upper),
            "Hq0_lt_2^72": h_upper < 2**72,
            "Hq0_plus_dmax_lt_2^72": h_upper + dmax < 2**72,
            "conclusion": "V<N<=Hq0 and N<=X=N+d<2^72",
        },
        "P61": {
            "repository_status": "CONDITIONAL",
            "endpoint_congruences": {
                "N_odd": True,
                "X_odd": True,
                "d_even": True,
                "X_mod_4": [3],
                "X_mod_3": [1],
                "X_mod_9": [1, 7],
                "X_mod_36": [7, 19],
            },
            "minimality_inequality_checks": inequality_checks,
            "G4": {
                "word": "1100",
                "map": [9, 5, 16],
                "endpoint_mod_3": 2,
                "predecessor": "z=(2*y-1)/3",
                "T_of_predecessor": "y",
                "upper_bound": "y<(9/8)N+5/16<(3/2)N",
                "conclusion": "G4 is forbidden on a first-octave return of a least counterexample",
            },
        },
        "dependencies": {
            "P54": "V<N<=Hq0 in the q0 first-crossing case",
            "X02": "N>V, not reproved",
            "phase7_boundary_defect_sha256": sha256(artifact_dir / "phase7_boundary_defect.json"),
            "phase8_short_excursions_sha256": sha256(artifact_dir / "phase8_short_excursions.json"),
        },
        "what_this_result_does_not_prove": "P60 and P61 apply only to the q0 least-counterexample first-crossing scenario; they do not assert that such an N exists or cover all q>=q0.",
        "proves_collatz": False,
    }


def reverse_barrier_data(common: dict[str, object], dmax: int) -> dict[str, object]:
    ln2_low, ln2_high = common["ln2"]
    ln3_low, ln3_high = common["ln3"]
    alpha_low, alpha_high = common["alpha"]
    assert all(isinstance(value, Fraction) for value in (ln2_low, ln2_high, ln3_low, ln3_high, alpha_low, alpha_high))
    threshold_log_low, threshold_log_high = log_interval(V + dmax, V, terms=48)
    cf = common_cf_prefix(alpha_low, alpha_high)
    conv = convergents(cf)
    lower_base = (103_768_467_013, 65_470_613_321)
    upper_parent = (217_976_794_617, 137_528_045_312)
    if lower_base not in conv or upper_parent not in conv:
        raise AssertionError("reverse barrier parents missing from CF")
    rows: list[dict[str, object]] = []
    for multiplier in range(1, 6):
        length = lower_base[0] + multiplier * upper_parent[0]
        odd_steps = lower_base[1] + multiplier * upper_parent[1]
        gap_low = odd_steps * ln3_low - length * ln2_high
        gap_high = odd_steps * ln3_high - length * ln2_low
        if gap_low <= 0:
            raise AssertionError("reverse semiconvergent is not below alpha")
        rows.append(
            {
                "t": multiplier,
                "a": odd_steps,
                "L": length,
                "log_gap": encode_interval(gap_low, gap_high),
                "coefficient_below_one": True,
                "meets_uniform_threshold": gap_high < threshold_log_low,
                "certified_insufficient": gap_low > threshold_log_high,
            }
        )
    first = next(row for row in rows if row["meets_uniform_threshold"])
    previous = rows[rows.index(first) - 1]
    if (previous["a"], previous["L"]) != (478_054_749_257, 757_698_850_864):
        raise AssertionError("previous reverse approximation changed")
    if (first["a"], first["L"]) != (615_582_794_569, 975_675_645_481):
        raise AssertionError("first reverse approximation changed")
    determinant = int(previous["L"]) * upper_parent[1] - int(previous["a"]) * upper_parent[0]
    if determinant != -1:
        raise AssertionError("reverse Farey determinant failed")
    return {
        "format": "collatz-phase9-reverse-barrier-v1",
        "P62": {
            "repository_status": "CONDITIONAL",
            "scope": "valid reverse paths from X=N+d in the q0 least-counterexample scenario",
            "uniform_ratio_threshold": encode_fraction(Fraction(V, V + dmax)),
            "equivalent_log_gap_upper": encode_interval(threshold_log_low, threshold_log_high),
            "conclusion": "every valid contracting reverse coefficient before the first possible pair contradicts least-counterexample minimality",
            "valid_path_existence_claimed": False,
        },
        "continued_fraction_certificate": {
            "alpha_prefix": list(cf[:25]),
            "lower_base": list(lower_base),
            "upper_parent": list(upper_parent),
            "next_partial_quotient": 5,
            "lower_semiconvergents": rows,
            "previous_insufficient": previous,
            "first_possible": first,
            "previous_upper_parent_determinant": determinant,
            "first_denominator_sum": int(previous["a"]) + upper_parent[1],
            "unimodular_minimality_argument": "write any smaller positive-gap vector in the basis (previous,upper_parent); denominator<sum and positive gap force a nonpositive upper coefficient, hence gap>=previous gap",
        },
        "exact_log_inputs": {"ln2": encode_interval(ln2_low, ln2_high), "ln3": encode_interval(ln3_low, ln3_high)},
        "direct_giant_powers_constructed": False,
        "what_this_result_does_not_prove": "The barrier is conditional and coefficient-only. It does not produce a valid reverse path or exclude expanding reverse paths.",
        "proves_collatz": False,
    }


def reverse_residue_data(common: dict[str, object], dmax: int, maximum_a: int) -> dict[str, object]:
    alpha_low, alpha_high = common["alpha"]
    assert isinstance(alpha_low, Fraction) and isinstance(alpha_high, Fraction)
    coefficient_rows: list[dict[str, object]] = []
    mechanical_rows: list[dict[str, object]] = []
    for odd_steps in range(1, maximum_a + 1):
        maximum_length = floor_alpha_multiple(odd_steps, alpha_low, alpha_high)
        for length in range(odd_steps, maximum_length + 1):
            numerator = 1 << length
            denominator = 3**odd_steps
            if numerator >= denominator:
                continue
            violates = numerator * (V + dmax) < denominator * V
            coefficient_rows.append(
                {
                    "a": odd_steps,
                    "L": length,
                    "coefficient": [numerator, denominator],
                    "below_uniform_threshold": violates,
                }
            )
            if not violates:
                raise AssertionError("small reverse coefficient unexpectedly reaches threshold")

        floors = [floor_alpha_multiple(index, alpha_low, alpha_high) for index in range(odd_steps + 1)]
        exponents = [floors[index] - floors[index - 1] for index in range(1, odd_steps + 1)]
        constant = 0
        total_length = 0
        for index, exponent in enumerate(exponents):
            constant = (1 << exponent) * constant + 3**index
            total_length += exponent
        modulus = 3**odd_steps
        endpoint_residue = constant * pow(1 << total_length, -1, modulus) % modulus
        endpoint = endpoint_residue
        predecessor = ((1 << total_length) * endpoint - constant) // modulus
        if predecessor <= 0:
            endpoint += modulus
            predecessor = ((1 << total_length) * endpoint - constant) // modulus
        if predecessor <= 0 or ((1 << total_length) * endpoint - constant) % modulus:
            raise AssertionError("reverse residue realization failed")
        mechanical_rows.append(
            {
                "a": odd_steps,
                "L": total_length,
                "exponent_word": exponents,
                "C": constant,
                "endpoint_residue_mod_3a": endpoint_residue,
                "smallest_positive_endpoint": endpoint,
                "smallest_reverse_predecessor": predecessor,
                "contracting_coefficient": (1 << total_length) < modulus,
                "minimality_violation_in_q0_near_return_scenario": True,
                "residue_classification": "FORBIDDEN_IF_PATH_VALID",
            }
        )
    return {
        "format": "collatz-phase9-reverse-residues-v1",
        "repository_status": "VERIFIED_FINITE",
        "maximum_odd_inverse_steps": maximum_a,
        "all_contracting_coefficient_pairs": coefficient_rows,
        "coefficient_pair_count": len(coefficient_rows),
        "mechanical_near_critical_family": mechanical_rows,
        "mechanical_family_count": len(mechanical_rows),
        "surviving_mechanical_residues": [],
        "scope_boundary": "All (a,L) coefficient pairs are audited through a<=maximum. Residue words are the explicitly stated lower-mechanical family, not every composition of L into a positive exponents.",
        "obstruction": "Full arbitrary reverse-exponent residue enumeration grows combinatorially; no recursive forbidden-residue theorem was obtained.",
        "what_this_result_does_not_prove": "Zero survivors in the mechanical subfamily is not an asymptotic reverse-residue theorem and does not cover arbitrary exponent words.",
        "proves_collatz": False,
    }


def row_digest_update(
    digest: hashlib._Hash,
    q: int,
    k: int,
    positions: tuple[int, ...],
    b_value: int,
    difference_power: int,
    r2: int,
    r3: int,
    displacement: int,
    paradoxical: bool,
    congruence: bool,
    contacts: int,
    first_octave: bool,
) -> None:
    digest.update(bytes((q, k)))
    digest.update(bytes(positions))
    digest.update(struct.pack(">QQQQqBBBB", b_value, difference_power, r2, r3, displacement, paradoxical, congruence, contacts, first_octave))


def layer_record(
    q: int,
    k: int,
    positions: tuple[int, ...],
    f_values: tuple[int, ...],
    b_value: int,
    power_three: int,
    modulus_two: int,
    inverse_three: int,
    inverse_two: int,
) -> dict[str, object]:
    r2 = (-b_value * inverse_three) % modulus_two
    numerator = power_three * r2 + b_value
    if numerator % modulus_two:
        raise AssertionError("two-sided layer affine equation failed")
    endpoint = numerator // modulus_two
    r3 = b_value * inverse_two % power_three
    if endpoint != r3:
        raise AssertionError("canonical endpoint is not the least 3-adic residue")
    defects = [f_values[index] - positions[index] for index in range(q)]
    word_set = set(positions)
    word = "".join("1" if index in word_set else "0" for index in range(k))
    displacement = r3 - r2
    return {
        "q": q,
        "K": k,
        "parity_word": word,
        "odd_positions": list(positions),
        "defects": defects,
        "B": b_value,
        "D": modulus_two - power_three,
        "r2": r2,
        "r3": r3,
        "d": displacement,
        "paradoxical_canonical": displacement >= 0,
        "nontrivial_paradoxical": displacement >= 0 and r2 > 2,
        "reverse_minimality_congruence": r3 % 36 in (7, 19),
        "contact_count": sum(value == 0 for value in defects),
        "first_octave_diagnostic": r2 <= r3 < 2 * r2 if r2 else False,
    }


def audit_first_crossing_layer(q: int, dmax: int) -> dict[str, object]:
    power_three = 3**q
    k = power_three.bit_length()
    modulus_two = 1 << k
    inverse_three = pow(power_three, -1, modulus_two)
    inverse_two = pow(modulus_two, -1, power_three)
    f_values = tuple((3**index).bit_length() - 1 for index in range(q))
    contributions = tuple(
        tuple(3 ** (q - 1 - index) * (1 << position) for position in range(f_values[index] + 1))
        for index in range(q)
    )
    digest = hashlib.sha256()
    positions = [0] * q
    total = 0
    paradoxical = 0
    nontrivial = 0
    congruence_count = 0
    first_octave_count = 0
    near_box = 0
    minimum: dict[str, object] | None = None
    maximum: dict[str, object] | None = None
    candidate_records: list[dict[str, object]] = []

    def visit(index: int, previous: int, b_value: int) -> None:
        nonlocal total, paradoxical, nontrivial, congruence_count, first_octave_count, near_box, minimum, maximum
        if index == q:
            position_tuple = tuple(positions)
            r2 = (-b_value * inverse_three) % modulus_two
            numerator = power_three * r2 + b_value
            if numerator % modulus_two:
                raise AssertionError("two-sided layer affine equation failed")
            r3 = numerator // modulus_two
            if r3 != b_value * inverse_two % power_three:
                raise AssertionError("canonical endpoint is not the least 3-adic residue")
            displacement = r3 - r2
            is_paradoxical = displacement >= 0
            is_nontrivial = is_paradoxical and r2 > 2
            has_congruence = r3 % 36 in (7, 19)
            is_first_octave = r2 <= r3 < 2 * r2 if r2 else False
            contact_count = sum(f_values[i] == position_tuple[i] for i in range(q))
            total += 1
            paradoxical += is_paradoxical
            nontrivial += is_nontrivial
            congruence_count += has_congruence
            first_octave_count += is_first_octave
            near_box += bool(
                V < r2 < 2**72
                and 0 <= displacement <= dmax
                and has_congruence
            )
            is_candidate = is_paradoxical or (has_congruence and is_first_octave)
            needs_record = (
                is_candidate
                or minimum is None
                or displacement <= int(minimum["d"])
                or maximum is None
                or displacement >= int(maximum["d"])
            )
            record = None
            if needs_record:
                record = layer_record(
                    q,
                    k,
                    position_tuple,
                    f_values,
                    b_value,
                    power_three,
                    modulus_two,
                    inverse_three,
                    inverse_two,
                )
            if record is not None and (
                minimum is None
                or (int(record["d"]), str(record["parity_word"]))
                < (int(minimum["d"]), str(minimum["parity_word"]))
            ):
                minimum = record
            if record is not None and (
                maximum is None
                or (int(record["d"]), str(record["parity_word"]))
                > (int(maximum["d"]), str(maximum["parity_word"]))
            ):
                maximum = record
            if is_candidate:
                assert record is not None
                candidate_records.append(record)
            row_digest_update(
                digest,
                q,
                k,
                position_tuple,
                b_value,
                modulus_two - power_three,
                r2,
                r3,
                displacement,
                is_paradoxical,
                has_congruence,
                contact_count,
                is_first_octave,
            )
            return
        for position in range(previous + 1, f_values[index] + 1):
            positions[index] = position
            visit(index + 1, position, b_value + contributions[index][position])

    positions[0] = 0
    visit(1, 0, contributions[0][0])
    assert minimum is not None and maximum is not None
    return {
        "q": q,
        "K": k,
        "enumerated_words": total,
        "row_digest_sha256": digest.hexdigest(),
        "paradoxical_canonical_count": paradoxical,
        "nontrivial_paradoxical_count": nontrivial,
        "reverse_minimality_congruence_count": congruence_count,
        "first_octave_diagnostic_count": first_octave_count,
        "q0_near_diagonal_box_count": near_box,
        "minimum_displacement_record": minimum,
        "maximum_displacement_record": maximum,
        "candidate_records": candidate_records,
    }


def mandatory_adversarial_audit(artifact_dir: Path) -> dict[str, object]:
    for exponent in range(1, 65):
        current = (1 << exponent) - 1
        for _ in range(exponent):
            if current % 2 != 1:
                raise AssertionError("2^m-1 adversarial prefix failed")
            current = (3 * current + 1) // 2
    for exponent in range(1, 33):
        current = (1 << (3 * exponent)) - 5
        observed = ""
        for _ in range(3 * exponent):
            observed += str(current % 2)
            current = (3 * current + 1) // 2 if current % 2 else current // 2
        if observed != "110" * exponent:
            raise AssertionError("8^m-5 adversarial prefix failed")
    safe = 0
    for mask in range(1 << 12):
        word = "".join("111" if (mask >> index) & 1 else "110" for index in range(12))
        odd = 0
        for depth, bit in enumerate(word, start=1):
            odd += bit == "1"
            if 3**odd < 2**depth:
                break
        else:
            safe += 1
    if safe != 1 << 12 or affine_word(A_WORD) != A_MAP or affine_word(B_WORD) != B_MAP:
        raise AssertionError("mandatory word regression failed")
    pair_count = contracting = noncontracting = 0
    for r in range(1, 33):
        for s in range(1, 33):
            pair_count += 1
            if 81**r * 9**s < 32**r * 16**s:
                contracting += 1
            else:
                noncontracting += 1
    macro = json.loads((artifact_dir / "phase7_macro12.json").read_text(encoding="utf-8"))
    macro0 = dict(zip(macro["record_schema"], macro["records"][0], strict=True))
    semigroup = json.loads((artifact_dir / "phase8_ab_semigroup_search.json").read_text(encoding="utf-8"))
    schema = semigroup["contracting_search"]["record_schema"]
    bba_row = next(dict(zip(schema, row, strict=True)) for row in semigroup["contracting_search"]["records"] if row[2] == "BBA")
    bba_map = affine_word(B_WORD + B_WORD + A_WORD)
    bba_source, bba_endpoint = least_realization(*bba_map)
    if macro0["binary_parity_word"] != PHASE7_MACRO0 or (bba_source, bba_endpoint) != (
        int(bba_row["least_source"]),
        int(bba_row["endpoint"]),
    ):
        raise AssertionError("Phase 7/8 adversarial dependency changed")
    return {
        "2^m_minus_1": {"scope": "1<=m<=64", "prefix": "1^m"},
        "8^m_minus_5": {"scope": "1<=m<=32", "prefix": "(110)^m"},
        "(110|111)^star": {"block_length": 12, "words_checked": safe},
        "A": {"word": A_WORD, "map": list(A_MAP)},
        "B": {"word": B_WORD, "map": list(B_MAP)},
        "A^rB^s": {"scope": "1<=r,s<=32", "pairs": pair_count, "contracting": contracting, "noncontracting": noncontracting},
        "phase7_macro_0": {"word": macro0["binary_parity_word"], "multiplier": macro0["multiplier"]},
        "phase8_BBA": {
            "word": "BBA",
            "shortcut_word": B_WORD + B_WORD + A_WORD,
            "map": list(bba_map),
            "least_source": bba_source,
            "endpoint": bba_endpoint,
            "descent_margin": bba_source - bba_endpoint,
        },
    }


def two_sided_residue_data(artifact_dir: Path, maximum_q: int, dmax: int) -> dict[str, object]:
    layers = [audit_first_crossing_layer(q, dmax) for q in range(1, maximum_q + 1)]
    total = sum(int(layer["enumerated_words"]) for layer in layers)
    nontrivial = sum(int(layer["nontrivial_paradoxical_count"]) for layer in layers)
    return {
        "format": "collatz-phase9-two-sided-residues-v1",
        "C04": {
            "repository_status": "OPEN",
            "statement": "no q0-critical first-crossing parity word has its canonical 2-adic/3-adic residue pair in the required near-diagonal box",
            "q0_box": {
                "q": Q0,
                "K": K0,
                "r2": "V<r2<=Hq0<2^72",
                "difference": f"0<=r3-r2<={dmax}<2^32",
                "r3_mod_36": [7, 19],
            },
            "proved": False,
        },
        "canonical_residue_identities": {
            "r2": "-B*3^(-q) mod 2^K, least nonnegative residue",
            "r3": "B*2^(-K) mod 3^q, least nonnegative residue",
            "canonical_affine_equation": "3^q*r2+B=2^K*r3",
        },
        "small_layer_audit": {
            "repository_status": "VERIFIED_FINITE",
            "maximum_q": maximum_q,
            "total_words": total,
            "row_digest_encoding": "bytes(q,K,odd_positions) followed by big-endian >QQQQqBBBB for B,D,r2,r3,d,paradoxical,mod36,contacts,first_octave",
            "full_rows_materialized": False,
            "retained_records": "layer summaries, extrema, and every paradoxical or congruence-plus-first-octave candidate",
            "storage_deviation": "The specification requested every row as a stored record; 22475497 rows are instead covered by ordered digests and independent full re-enumeration to avoid a disposable multi-gigabyte artifact.",
            "layers": layers,
            "nontrivial_paradoxical_first_crossing_words": nontrivial,
            "external_A100982_values_used_as_axiom": False,
        },
        "meet_in_the_middle": {
            "repository_status": "VERIFIED_FINITE",
            "lossless_split_identity": "B=B_left+B_right with original powers of 3 and 2 retained",
            "exact_state_fields": ["q_left", "K_boundary", "B_left", "B_right", "prefix_safety", "boundary_defect", "r2_mod_2K", "r3_mod_3q"],
            "carry_information_discarded": False,
            "q0_enumerated": False,
            "exclusion_certificate_found": False,
        },
        "mandatory_adversarial_audit": mandatory_adversarial_audit(artifact_dir),
        "what_this_result_does_not_prove": "The exhaustive q<=maximum audit and lossless state design do not exclude the q0 near-diagonal box or prove C04.",
        "proves_collatz": False,
    }


def paradoxical_tree_data(maximum_length: int) -> dict[str, object]:
    states: list[tuple[int, int, int, int]] = [(0, 1, 0, 0)]
    summaries: list[dict[str, object]] = []
    records: list[dict[str, object]] = []
    for length in range(1, maximum_length + 1):
        denominator = 1 << length
        step_denominator = 1 << (length - 1)
        next_states: list[tuple[int, int, int, int]] = []
        contracting = 0
        paradoxical_cylinders = 0
        paradoxical_realizations = 0
        for word_bits, coefficient, constant, odd_count in states:
            for bit in (0, 1):
                if bit:
                    new_coefficient = 3 * coefficient
                    new_constant = 3 * constant + step_denominator
                    new_odd = odd_count + 1
                else:
                    new_coefficient = coefficient
                    new_constant = constant
                    new_odd = odd_count
                new_word = (word_bits << 1) | bit
                next_states.append((new_word, new_coefficient, new_constant, new_odd))
                if new_coefficient >= denominator:
                    continue
                contracting += 1
                source, endpoint = least_realization(new_coefficient, new_constant, denominator)
                displacement = endpoint - source
                difference_power = denominator - new_coefficient
                if source > 2 and displacement >= 0:
                    realization_count = displacement // difference_power + 1
                    paradoxical_cylinders += 1
                    paradoxical_realizations += realization_count
                    records.append(
                        {
                            "length": length,
                            "q": new_odd,
                            "parity_word": format(new_word, f"0{length}b"),
                            "B": new_constant,
                            "D": difference_power,
                            "canonical_source": source,
                            "canonical_endpoint": endpoint,
                            "canonical_difference": displacement,
                            "positive_paradoxical_realizations": realization_count,
                            "largest_start_in_cylinder": source + denominator * (realization_count - 1),
                        }
                    )
        summaries.append(
            {
                "length": length,
                "all_words": 1 << length,
                "contracting_words": contracting,
                "paradoxical_cylinders": paradoxical_cylinders,
                "paradoxical_realizations": paradoxical_realizations,
            }
        )
        states = next_states
    return {
        "format": "collatz-phase9-paradoxical-tree-v1",
        "repository_status": "VERIFIED_FINITE",
        "maximum_shortcut_length": maximum_length,
        "cylinder_identity": "F(r2+2^K*t)-(r2+2^K*t)=(r3-r2)-(2^K-3^q)*t",
        "necessary_and_sufficient_condition": "a positive paradoxical realization exists iff the least positive canonical realization has nonnegative displacement",
        "summaries": summaries,
        "paradoxical_records": records,
        "new_rank_found": False,
        "exact_counterexample_to_C04_found": False,
        "external_target": {
            "repository_status": "EXTERNAL_EVIDENCE",
            "Rozier_Terracol_Theorem_1_3": "593 paradoxical sequences start at <=4614; any further one starts above 2.8e19; finiteness would imply Collatz",
            "heuristic_conjecture": "no paradoxical sequence starts above 4614",
            "external_results_reproved": False,
            "Winkler_overlap": "finite stopping-time parity/residue trees predate this bounded implementation",
        },
        "what_this_result_does_not_prove": "The length-bounded tree has no asymptotic rank and neither reproduces the external search to 2.8e19 nor proves paradoxical-sequence finiteness.",
        "proves_collatz": False,
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_obstruction_report(path: Path, artifacts: dict[str, dict[str, object]]) -> None:
    dual = artifacts["contact_dual"]
    short = artifacts["short"]
    endpoint = artifacts["endpoint"]
    reverse = artifacts["reverse"]
    two_sided = artifacts["two_sided"]
    tree = artifacts["tree"]
    lines = [
        "# Phase 9 obstruction report",
        "",
        "This report does not claim a proof or disproof of the Collatz conjecture.",
        "",
        "## Verified conditional structure",
        "",
        "- P59: contact at an L-phase forces the next H-phase contact.",
        f"- The denominator-256 rational dual search gives the conditional contact lower bound `{dual['forced_closure_contact_lower']}`.",
        f"- E14 gives `{short['E14']['forced_closure_contacts']['first_octave_lower']}` first-octave short returns under its explicit dependencies.",
        f"- P60 gives `0<=d<={endpoint['P60']['maximum_integer_displacement']}<2^32` only in the q0 first-crossing case.",
        "- P61 forces endpoint residues 7 or 19 modulo 36 and forbids G4 in a least-counterexample first-octave return.",
        f"- P62's first coefficient pair not excluded by the uniform reverse threshold is `(a,L)=({reverse['continued_fraction_certificate']['first_possible']['a']},{reverse['continued_fraction_certificate']['first_possible']['L']})`.",
        "",
        "## Refuted contact-only shortcut",
        "",
        "- NG17: forced closure plus weighted pressure is consistent with a symbolic all-contact critical word. Endpoint and least-residue arithmetic are indispensable.",
        "",
        "## Open two-sided obstruction",
        "",
        f"- C04 remains OPEN after exact first-crossing enumeration through q={two_sided['small_layer_audit']['maximum_q']} ({two_sided['small_layer_audit']['total_words']} words).",
        "- Storage deviation: individual rows are not all materialized; ordered per-layer digests plus extrema/candidates are stored, and the independent verifier re-enumerates every row.",
        f"- The direct paradoxical tree through shortcut length {tree['maximum_shortcut_length']} found no new rank and no C04 counterexample.",
        "- Full arbitrary reverse-exponent residue enumeration through a=30 was not achieved; all coefficient pairs were audited, while residue rows are explicitly limited to the lower-mechanical family.",
        "",
        "## Main bottleneck",
        "",
        "No theorem links the near-diagonal 2-adic/3-adic box to an impossibility at q0. Contact density and reverse coefficient barriers are strong but do not control simultaneous ordinary residue size.",
        "",
        "## What this result does not prove",
        "",
        "Phase 9 does not establish C04, construct the q0 word, prove paradoxical-tree finiteness, or prove/disprove Collatz.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(
    artifact_dir: Path,
    *,
    small_layer_max_q: int = 21,
    reverse_max_a: int = 30,
    paradoxical_max_length: int = 21,
) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    common = common_arithmetic()
    forced = forced_contact_data(common)
    dual = contact_dual_data(common, artifact_dir)
    short = short_return_data(dual, artifact_dir)
    endpoint = endpoint_displacement_data(common, artifact_dir)
    reverse = reverse_barrier_data(common, int(endpoint["P60"]["maximum_integer_displacement"]))
    reverse_residues = reverse_residue_data(common, DMAX, reverse_max_a)
    two_sided = two_sided_residue_data(artifact_dir, small_layer_max_q, DMAX)
    tree = paradoxical_tree_data(paradoxical_max_length)
    payloads = {
        "forced_contact": forced,
        "contact_dual": dual,
        "short": short,
        "endpoint": endpoint,
        "reverse": reverse,
        "reverse_residues": reverse_residues,
        "two_sided": two_sided,
        "tree": tree,
    }
    write_json(artifact_dir / "phase9_forced_contact.json", forced)
    write_json(artifact_dir / "phase9_contact_dual.json", dual)
    write_json(artifact_dir / "phase9_short_return_bound.json", short)
    write_json(artifact_dir / "phase9_endpoint_displacement.json", endpoint)
    write_json(artifact_dir / "phase9_reverse_barrier.json", reverse)
    write_json(artifact_dir / "phase9_reverse_residues.json", reverse_residues)
    write_json(artifact_dir / "phase9_two_sided_residues.json", two_sided)
    write_json(artifact_dir / "phase9_paradoxical_tree.json", tree)
    write_obstruction_report(artifact_dir / "phase9_obstruction_report.md", payloads)
    return {
        "P59": "CONDITIONAL",
        "NG17": "REFUTED",
        "E14": "VERIFIED_FINITE",
        "P60": "CONDITIONAL",
        "P61": "CONDITIONAL",
        "P62": "CONDITIONAL",
        "C04": "OPEN",
        "closure_contact_lower": dual["forced_closure_contact_lower"],
        "first_octave_short_return_lower": short["E14"]["forced_closure_contacts"]["first_octave_lower"],
        "small_layer_words": two_sided["small_layer_audit"]["total_words"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--small-layer-max-q", type=int, default=21)
    parser.add_argument("--reverse-max-a", type=int, default=30)
    parser.add_argument("--paradoxical-max-length", type=int, default=21)
    arguments = parser.parse_args()
    if min(arguments.small_layer_max_q, arguments.reverse_max_a, arguments.paradoxical_max_length) < 1:
        parser.error("all finite bounds must be positive")
    result = generate(
        arguments.artifact_dir,
        small_layer_max_q=arguments.small_layer_max_q,
        reverse_max_a=arguments.reverse_max_a,
        paradoxical_max_length=arguments.paradoxical_max_length,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
