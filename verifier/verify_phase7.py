#!/usr/bin/env python3
"""Independent exact verifier for the Phase 7 artifact set.

This module intentionally does not import ``src.phase7_search``.  It rebuilds
the logarithmic enclosures, all macro arithmetic, the fixed-layer frontiers,
and the bounded mixed-block audit from the primitive certificate fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from math import ceil, isqrt
from pathlib import Path
from typing import Iterator


V = 2075 * (1 << 60)
Q0 = 72_057_431_991
K0 = 114_208_327_604
LEFT = (103_768_467_013, 65_470_613_321)
RIGHT = (10_439_860_591, 6_586_818_670)
SHIFTS = (12, 41, 53, 306, 665)
LAYER_COUNTS = {1: 1, 3: 2, 5: 7, 17: 312_455}
DANGEROUS = ("011101", "1101", "101", "1")
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

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def fail(message: str) -> None:
    raise ValueError(message)


def fraction(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        fail("malformed rational pair")
    return Fraction(int(value[0]), int(value[1]))


def interval(value: object) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict):
        fail("malformed interval")
    low = fraction(value.get("lower"))
    high = fraction(value.get("upper"))
    if not low < high:
        fail("empty rational interval")
    return low, high


def log_bounds(numerator: int, denominator: int = 1, terms: int = 192) -> tuple[Fraction, Fraction]:
    """Independent rational enclosure from log(x)=2*atanh((x-1)/(x+1))."""
    if denominator <= 0 or numerator <= denominator:
        fail("invalid logarithm input")
    z = Fraction(numerator - denominator, numerator + denominator)
    square = z * z
    power = z
    partial = Fraction(0)
    for n in range(terms):
        partial += power / (2 * n + 1)
        power *= square
    low = 2 * partial
    high = low + 2 * power / ((2 * terms + 1) * (1 - square))
    return low, high


def expm1_bounds(low: Fraction, high: Fraction, terms: int = 24) -> tuple[Fraction, Fraction]:
    if not 0 < low <= high < 1:
        fail("invalid exponential input")

    def one_side(x: Fraction) -> tuple[Fraction, Fraction]:
        total = Fraction(1)
        term = Fraction(1)
        for n in range(1, terms + 1):
            term = term * x / n
            total += term
        next_term = term * x / (terms + 1)
        return total, total + next_term / (1 - x / (terms + 2))

    return one_side(low)[0] - 1, one_side(high)[1] - 1


def contains(outer: tuple[Fraction, Fraction], inner: tuple[Fraction, Fraction]) -> bool:
    return outer[0] <= inner[0] < inner[1] <= outer[1]


def unique_floor(low: Fraction, high: Fraction) -> int:
    result = low.numerator // low.denominator
    if high.numerator // high.denominator != result or high == result:
        fail("interval does not determine one floor")
    return result


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.name} must contain an object")
    return value


def verify_first_crossing(certificate: dict[str, object]) -> dict[str, object]:
    if certificate.get("format") != "collatz-phase7-symbolic-verifier-input-v1":
        fail("symbolic certificate format mismatch")
    data = certificate.get("first_crossing")
    if not isinstance(data, dict):
        fail("first-crossing certificate missing")
    ln2 = interval(data.get("ln2"))
    ln3 = interval(data.get("ln3"))
    independent_ln2 = log_bounds(2)
    independent_ln3 = log_bounds(3)
    if not contains(ln2, independent_ln2) or not contains(ln3, independent_ln3):
        fail("stored log enclosure does not contain independent enclosure")
    alpha = interval(data.get("alpha_log2_3"))
    if alpha != (ln3[0] / ln2[1], ln3[1] / ln2[0]):
        fail("alpha interval was not reconstructed from ln2 and ln3")
    beta = interval(data.get("beta_log2_3_plus_1_over_V"))
    independent_upper = log_bounds(3 * V + 1, V)
    independent_beta = (independent_upper[0] / independent_ln2[1], independent_upper[1] / independent_ln2[0])
    if not contains(beta, independent_beta):
        fail("beta interval does not contain independent enclosure")

    candidate_data = data.get("candidate")
    parents = data.get("stern_brocot_parents")
    if not isinstance(candidate_data, dict) or not isinstance(parents, dict):
        fail("candidate or parent data missing")
    if candidate_data.get("K") != K0 or candidate_data.get("q") != Q0:
        fail("candidate pair mismatch")
    candidate = fraction(candidate_data.get("fraction"))
    if candidate != Fraction(K0, Q0):
        fail("candidate rational mismatch")
    if parents.get("left") != list(LEFT) or parents.get("right") != list(RIGHT):
        fail("Stern-Brocot parent mismatch")
    left, right = Fraction(*LEFT), Fraction(*RIGHT)
    if LEFT[0] * RIGHT[1] - LEFT[1] * RIGHT[0] != -1:
        fail("parents are not Farey neighbors")
    if candidate.numerator != LEFT[0] + RIGHT[0] or candidate.denominator != LEFT[1] + RIGHT[1]:
        fail("candidate is not the parent mediant")
    if not left < alpha[0] < alpha[1] < candidate < beta[0] < beta[1] < right:
        fail("first-crossing order is not certified")
    # Farey neighbors bound every interior denominator by q_left+q_right.
    if parents.get("minimal_denominator_conclusion") != Q0:
        fail("minimal denominator conclusion mismatch")

    x_interval = interval(data.get("log_gap_x_Kln2_minus_qln3"))
    expected_x = (K0 * ln2[0] - Q0 * ln3[1], K0 * ln2[1] - Q0 * ln3[0])
    if x_interval != expected_x:
        fail("log-gap interval mismatch")
    delta = interval(data.get("delta_exp_x_minus_1"))
    independent_delta = expm1_bounds(*x_interval)
    if not contains(delta, independent_delta):
        fail("delta interval does not contain independent exponential enclosure")
    if data.get("direct_giant_powers_constructed") is not False:
        fail("certificate claims direct giant-power construction")
    return {"ln2": ln2, "ln3": ln3, "alpha": alpha, "delta": delta}


def verify_boundary(path: Path, primitives: dict[str, object]) -> tuple[dict[str, object], Fraction]:
    data = load(path)
    if data.get("format") != "collatz-phase7-boundary-defect-v1" or data.get("proves_collatz") is not False:
        fail("boundary artifact claim boundary mismatch")
    symbolic = data.get("symbolic_identity")
    if not isinstance(symbolic, dict) or symbolic.get("classification") != "VERIFIED_SYMBOLIC":
        fail("symbolic boundary identity missing")
    required_steps = {
        "B=sum_j 3^(q-1-j)*2^d_j",
        "B/3^(q-1)=S(a)",
        "therefore S(a)>=3*N*delta",
        "therefore W(C)>=6*N*delta-S0",
    }
    if not required_steps.issubset(set(symbolic.get("exact_steps", []))):
        fail("boundary-defect derivation is incomplete")
    if symbolic.get("external_math_required") is not False or symbolic.get("proves_collatz") is not False:
        fail("symbolic result overclaims its status")

    ln2_low, ln2_high = primitives["ln2"]
    delta_low, _ = primitives["delta"]
    rotation = data.get("rotation_sum")
    if not isinstance(rotation, dict) or rotation.get("input") != "DENJOY_KOKSMA":
        fail("external Denjoy-Koksma input not isolated")
    premises = rotation.get("exact_premises_checked")
    if not isinstance(premises, dict) or premises.get("q0_ostrowski_decomposition") != [RIGHT[1], LEFT[1]]:
        fail("Ostrowski decomposition mismatch")
    s0 = interval(rotation.get("S0_interval"))
    expected_s0 = (Fraction(Q0, 2) / ln2_high - 2, Fraction(Q0, 2) / ln2_low + 2)
    if s0 != expected_s0:
        fail("S0 interval mismatch")
    weight = data.get("contact_weight")
    if not isinstance(weight, dict) or weight.get("N_replaced_by_external_lower_bound_V") != V:
        fail("external V substitution mismatch")
    weighted_lower = fraction(weight.get("lower_bound"))
    if weighted_lower != 6 * V * delta_low - s0[1]:
        fail("contact weight lower bound mismatch")

    density = data.get("contact_density")
    if not isinstance(density, dict):
        fail("contact-density certificate missing")
    u_interval = interval(density.get("u_2_to_minus_t"))
    scale = 1 << 256
    root = isqrt(1 << 511)
    expected_u = (Fraction(root, scale), Fraction(root + 1, scale))
    if u_interval != expected_u or not u_interval[0] ** 2 <= Fraction(1, 2) < u_interval[1] ** 2:
        fail("sqrt-half enclosure mismatch")
    mean = (1 - u_interval[0]) / ln2_low - Fraction(1, 2) * u_interval[0]
    error = 4 * (1 - u_interval[0])
    if fraction(density.get("centered_cap_mean_upper")) != mean:
        fail("centered cap mean mismatch")
    if fraction(density.get("denjoy_koksma_error_upper")) != error:
        fail("contact-density DK error mismatch")
    count = ceil((weighted_lower - Q0 * mean - error) / u_interval[1])
    if density.get("minimum_contact_count") != count or count * 100 <= 43 * Q0:
        fail("contact-density count mismatch")
    if fraction(density.get("density_lower_bound")) != Fraction(count, Q0):
        fail("contact-density rational mismatch")
    return data, s0[1]


def verify_autocorrelation(path: Path, primitives: dict[str, object], s0_high: Fraction) -> list[int]:
    data = load(path)
    if data.get("format") != "collatz-phase7-contact-autocorrelation-v1" or data.get("proves_collatz") is not False:
        fail("autocorrelation claim boundary mismatch")
    rows = data.get("rows")
    if not isinstance(rows, list) or [row.get("h") for row in rows if isinstance(row, dict)] != list(SHIFTS):
        fail("autocorrelation shift list mismatch")
    alpha_low, alpha_high = primitives["alpha"]
    ln2_low, _ = primitives["ln2"]
    delta_low, _ = primitives["delta"]
    results: list[int] = []
    for row, h in zip(rows, SHIFTS, strict=True):
        if not isinstance(row, dict):
            fail("autocorrelation row malformed")
        floor_h = unique_floor(h * alpha_low, h * alpha_high)
        u = Fraction(1 << floor_h, 3**h)
        integral = ((1 - u) * (1 - Fraction(1, 2) / u) + (2 * u - 1) * (Fraction(1, 2) / u - Fraction(1, 2))) / ln2_low
        rotation_variation = Q0 * integral + 4
        cyclic_variation = rotation_variation + Fraction(h, 2)
        overlap = 12 * V * delta_low - 3 * s0_high - cyclic_variation
        cyclic_count = max(0, ceil(overlap))
        count = max(0, cyclic_count - h)
        if row.get("floor_h_log2_3") != floor_h or fraction(row.get("rotation_fraction_u")) != u:
            fail(f"shift-{h} rotation mismatch")
        if fraction(row.get("integral_variation_bound")) != integral or fraction(row.get("V_h_upper")) != rotation_variation:
            fail(f"shift-{h} variation mismatch")
        if fraction(row.get("cyclic_V_h_upper_including_wrap")) != cyclic_variation:
            fail(f"shift-{h} cyclic variation mismatch")
        if fraction(row.get("cyclic_weighted_overlap_lower")) != overlap or row.get("cyclic_contact_pair_count_lower") != cyclic_count:
            fail(f"shift-{h} cyclic contact-pair mismatch")
        if row.get("contact_pair_count_lower") != count:
            fail(f"shift-{h} contact-pair mismatch")
        results.append(count)
    if results[0] < 880_000_000:
        fail("h=12 sanity lower bound failed")
    return results


def affine(word: str) -> tuple[int, int, int]:
    odd_total = word.count("1")
    constant = 0
    odd_seen = 0
    for position, bit in enumerate(word):
        if bit == "1":
            constant += 3 ** (odd_total - 1 - odd_seen) * (1 << position)
            odd_seen += 1
    return 3**odd_total, constant, 1 << len(word)


def decompose(word: str) -> list[str] | None:
    result: list[str] = []
    index = 0
    while index < len(word):
        chosen = next((block for block in DANGEROUS if word.startswith(block, index)), None)
        if chosen is None:
            return None
        result.append(chosen)
        index += len(chosen)
    return result


def verify_macros(path: Path, primitives: dict[str, object]) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase7-macro12-v1" or data.get("record_schema") != MACRO_FIELDS:
        fail("macro artifact format/schema mismatch")
    factors_data = data.get("factor_construction")
    if not isinstance(factors_data, dict) or factors_data.get("external_sturmian_complexity_theorem_used") is not False:
        fail("macro factor-construction boundary mismatch")
    factors = factors_data.get("factors")
    if not isinstance(factors, list) or len(factors) != 13:
        fail("expected 13 mechanical factors")
    alpha_low, alpha_high = primitives["alpha"]
    f_values_by_id: dict[int, list[int]] = {}
    for expected_id, factor_row in enumerate(factors):
        if not isinstance(factor_row, dict) or factor_row.get("id") != expected_id:
            fail("mechanical factor id mismatch")
        theta = fraction(factor_row.get("representative_intercept"))
        values = [unique_floor(i * alpha_low + theta, i * alpha_high + theta) for i in range(13)]
        increments = [values[i + 1] - values[i] for i in range(12)]
        if factor_row.get("f_values") != values or factor_row.get("increments") != increments:
            fail("mechanical factor reconstruction mismatch")
        f_values_by_id[expected_id] = values

    records = data.get("records")
    if not isinstance(records, list) or data.get("macro_count") != 87_015 or len(records) != 87_015:
        fail("macro count mismatch")
    counts = [0] * 13
    first_noncontracting: list[object] | None = None
    first_nondecomposable: list[object] | None = None
    for expected_id, row in enumerate(records):
        if not isinstance(row, list) or len(row) != len(MACRO_FIELDS) or row[0] != expected_id:
            fail(f"macro row {expected_id} schema/id mismatch")
        factor_id = int(row[1])
        if factor_id not in f_values_by_id:
            fail(f"macro row {expected_id} has unknown factor")
        f_values = f_values_by_id[factor_id]
        defects = [int(value) for value in row[2]]
        if len(defects) != 13 or any(value < 0 for value in defects):
            fail(f"macro row {expected_id} has invalid defects")
        positions = [f_values[i] - defects[i] for i in range(13)]
        if positions[0] != 0 or any(a >= b for a, b in zip(positions, positions[1:])):
            fail(f"macro row {expected_id} has invalid contact-return path")
        length = positions[-1]
        odd_positions = set(positions[:-1])
        word = "".join("1" if i in odd_positions else "0" for i in range(length))
        if row[3] != word or row[4] != length or row[5] != 12:
            fail(f"macro row {expected_id} word metadata mismatch")
        coefficient, constant, denominator = affine(word)
        if row[6:9] != [coefficient, constant, denominator]:
            fail(f"macro row {expected_id} affine mismatch")
        if row[9] != [coefficient, denominator] or row[10] != [constant, denominator]:
            fail(f"macro row {expected_id} rational map mismatch")
        fixed = Fraction(constant, denominator - coefficient)
        if fraction(row[11]) != fixed:
            fail(f"macro row {expected_id} fixed point mismatch")
        residue = (-constant * pow(coefficient, -1, denominator)) % denominator
        source = residue if residue >= 2 else residue + denominator
        endpoint = (coefficient * source + constant) // denominator
        if row[12] != residue or row[13] != length or row[14] != endpoint:
            fail(f"macro row {expected_id} residue/endpoint mismatch")
        if row[15] != "ALL" or row[16] != endpoint % 9 or row[17] != "ALL" or row[18] != endpoint % 27:
            fail(f"macro row {expected_id} odd-modulus data mismatch")
        decomposition = decompose(word)
        if row[19] != decomposition:
            fail(f"macro row {expected_id} dangerous decomposition mismatch")
        if coefficient >= denominator and first_noncontracting is None:
            first_noncontracting = row
        if decomposition is None and first_nondecomposable is None:
            first_nondecomposable = row
        counts[factor_id] += 1
    if data.get("counts_by_factor") != counts or sum(counts) != 87_015:
        fail("macro factor counts mismatch")
    for factor_row, count in zip(factors, counts, strict=True):
        if factor_row.get("macro_count") != count:
            fail("stored factor macro count mismatch")
    cegar = data.get("cegar")
    if not isinstance(cegar, list) or len(cegar) != 3 or first_noncontracting is None or first_nondecomposable is None:
        fail("macro CEGAR records missing")
    expected_counterexamples = [first_noncontracting, first_nondecomposable, records[0]]
    for item, raw in zip(cegar, expected_counterexamples, strict=True):
        if not isinstance(item, dict) or item.get("repository_status") != "REFUTED":
            fail("failed macro hypothesis is not labelled REFUTED")
        if item.get("smallest_exact_counterexample") != dict(zip(MACRO_FIELDS, raw, strict=True)):
            fail("macro CEGAR counterexample mismatch")
    if data.get("universal_obstruction_found") is not False or data.get("proves_collatz") is not False:
        fail("macro artifact overclaims its conclusion")
    return {"macro_count": len(records), "counts_by_factor": counts}


def positions_for_q(q: int) -> Iterator[tuple[int, ...]]:
    bounds = [(3**j).bit_length() - 1 for j in range(q)]

    def walk(index: int, previous: int, prefix: tuple[int, ...]) -> Iterator[tuple[int, ...]]:
        if index == q:
            yield prefix
            return
        for position in range(previous + 1, bounds[index] + 1):
            yield from walk(index + 1, position, prefix + (position,))

    yield from walk(1, 0, (0,))


def frontier_row(q: int, positions: tuple[int, ...]) -> tuple[object, ...]:
    coefficient = 3**q
    k = coefficient.bit_length()
    denominator = 1 << k
    constant = sum(3 ** (q - 1 - j) * (1 << position) for j, position in enumerate(positions))
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    source = residue if residue >= 2 else residue + denominator
    endpoint = (coefficient * source + constant) // denominator
    boundary_positions = [(3**j).bit_length() - 1 for j in range(q)]
    defects = tuple(boundary_positions[j] - positions[j] for j in range(q))
    position_set, boundary_set = set(positions), set(boundary_positions)
    word = "".join("1" if i in position_set else "0" for i in range(k))
    boundary_word = "".join("1" if i in boundary_set else "0" for i in range(k))
    first = next((i for i, (a, b) in enumerate(zip(word, boundary_word, strict=True)) if a != b), None)
    if first is not None:
        boundary_constant = sum(3 ** (q - 1 - j) * (1 << position) for j, position in enumerate(boundary_positions))
        boundary_residue = (-boundary_constant * pow(coefficient, -1, denominator)) % denominator
        if residue % (1 << first) != boundary_residue % (1 << first):
            fail("2-adic common-prefix rigidity failed")
        if residue % (1 << (first + 1)) == boundary_residue % (1 << (first + 1)):
            fail("2-adic first-difference rigidity failed")
    reverse = endpoint % coefficient
    return (
        constant,
        source,
        sum(defects),
        max(defects, default=0),
        sum(value == 0 for value in defects),
        -1 if first is None else first,
        reverse,
        min(reverse, coefficient - reverse),
        word,
        list(positions),
        list(defects),
        endpoint,
    )


def verify_frontier(path: Path) -> tuple[dict[str, object], dict[str, object]]:
    data = load(path)
    if data.get("format") != "collatz-phase7-arithmetic-frontier-v1" or data.get("proves_collatz") is not False:
        fail("arithmetic-frontier boundary mismatch")
    rigidity = data.get("fixed_k_q_rigidity")
    if not isinstance(rigidity, dict) or rigidity.get("repository_status") != "VERIFIED_THEOREM":
        fail("fixed-layer rigidity claim missing")
    layers = data.get("layers")
    if not isinstance(layers, list) or len(layers) != len(LAYER_COUNTS):
        fail("fixed-layer list mismatch")
    checked: dict[str, object] = {}
    for layer, (q, expected_count) in zip(layers, LAYER_COUNTS.items(), strict=True):
        if not isinstance(layer, dict) or layer.get("q") != q or layer.get("pareto_schema") != FRONTIER_FIELDS:
            fail(f"q={q} layer metadata mismatch")
        rows = [frontier_row(q, item) for item in positions_for_q(q)]
        if len(rows) != expected_count or layer.get("enumerated_words") != expected_count:
            fail(f"q={q} exhaustive count mismatch")
        if len({int(row[1]) for row in rows}) != expected_count or layer.get("all_residues_distinct") is not True:
            fail(f"q={q} residue rigidity collision")
        ordered = sorted(rows, key=lambda row: (-int(row[0]), int(row[1]), str(row[8])))
        pareto: list[tuple[object, ...]] = []
        best: int | None = None
        for row in ordered:
            if best is None or int(row[1]) < best:
                pareto.append(row)
                best = int(row[1])
        if layer.get("pareto_records") != [list(row) for row in pareto]:
            fail(f"q={q} Pareto frontier mismatch")
        counts = sorted({value for value in (1, 10, 100, 1000, 10_000, len(rows)) if value <= len(rows)})
        certificates: list[dict[str, object]] = []
        for count in counts:
            prefix = ordered[:count]
            witness = min(prefix, key=lambda row: int(row[1]))
            certificates.append(
                {
                    "top_B_record_count": count,
                    "B_threshold": int(prefix[-1][0]),
                    "certified_minimum_r2": int(witness[1]),
                    "witness_word": witness[8],
                    "scope": f"exhaustive fixed layer q={q}",
                }
            )
        if layer.get("finite_separation_certificates") != certificates:
            fail(f"q={q} separation certificate mismatch")
        checked[str(q)] = {"words": len(rows), "pareto_records": len(pareto)}
    if data.get("universal_tradeoff_found") is not False:
        fail("finite frontier is promoted to a universal claim")
    mixed = data.get("mixed_block_adversarial_audit")
    if not isinstance(mixed, dict):
        fail("mixed-block audit missing")
    return checked, mixed


def verify_mixed(data: dict[str, object]) -> dict[str, int]:
    scope = data.get("scope")
    if not isinstance(scope, dict):
        fail("mixed-block scope missing")
    bound = int(scope.get("1<=r<=bound", 0))
    if bound < 1 or scope.get("1<=s<=bound") != bound:
        fail("mixed-block bound mismatch")
    counterexamples: list[dict[str, object]] = []
    contracting = 0
    for r in range(1, bound + 1):
        coefficient_a, denominator_a = 81**r, 32**r
        constant_a = 73 * (coefficient_a - denominator_a) // 49
        for s in range(1, bound + 1):
            coefficient_b, denominator_b = 9**s, 16**s
            constant_b = 5 * (denominator_b - coefficient_b) // 7
            coefficient = coefficient_b * coefficient_a
            denominator = denominator_b * denominator_a
            if coefficient >= denominator:
                continue
            contracting += 1
            constant = coefficient_b * constant_a + constant_b * denominator_a
            residue = (-constant * pow(coefficient, -1, denominator)) % denominator
            source = residue if residue >= 2 else residue + denominator
            endpoint = (coefficient * source + constant) // denominator
            if endpoint > source:
                counterexamples.append(
                    {
                        "r": r,
                        "s": s,
                        "shortcut_length": 5 * r + 4 * s,
                        "source": source,
                        "endpoint": endpoint,
                        "fixed_point_comparison_gap": source * (denominator - coefficient) - constant,
                    }
                )
    if data.get("pairs_tested") != bound * bound or data.get("contracting_pairs_tested") != contracting:
        fail("mixed-block finite count mismatch")
    if data.get("paradoxical_endpoint_counterexamples") != counterexamples:
        fail("mixed-block counterexample list mismatch")
    universal = data.get("universal_claim")
    if not isinstance(universal, dict) or universal.get("repository_status") != "OPEN" or universal.get("proved") is not False:
        fail("mixed-block universal claim is not OPEN")
    return {"bound": bound, "pairs": bound * bound, "contracting_pairs": contracting}


def artifact_hashes(artifact_dir: Path) -> dict[str, str]:
    names = [
        "phase7_symbolic_certificate.json",
        "phase7_boundary_defect.json",
        "phase7_contact_autocorrelation.json",
        "phase7_macro12.json",
        "phase7_arithmetic_frontier.json",
        "phase7_obstruction_report.md",
    ]
    return {name: hashlib.sha256((artifact_dir / name).read_bytes()).hexdigest() for name in names}


def verify_artifacts(artifact_dir: Path) -> dict[str, object]:
    certificate = load(artifact_dir / "phase7_symbolic_certificate.json")
    primitives = verify_first_crossing(certificate)
    _, s0_high = verify_boundary(artifact_dir / "phase7_boundary_defect.json", primitives)
    pairs = verify_autocorrelation(artifact_dir / "phase7_contact_autocorrelation.json", primitives, s0_high)
    macro = verify_macros(artifact_dir / "phase7_macro12.json", primitives)
    frontier, mixed_artifact = verify_frontier(artifact_dir / "phase7_arithmetic_frontier.json")
    mixed = verify_mixed(mixed_artifact)
    report = (artifact_dir / "phase7_obstruction_report.md").read_text(encoding="utf-8")
    if "What this result does not prove" not in report or "does not claim a proof" not in report:
        fail("obstruction report lacks mandatory non-proof boundary")
    return {
        "format": "collatz-phase7-independent-verifier-v1",
        "valid": True,
        "classification": "EXACT_FINITE_CERTIFICATE",
        "repository_status": "VERIFIED_FINITE",
        "independent_search_imports": [],
        "first_crossing_pair": [Q0, K0],
        "contact_pair_lower_bounds": dict(zip(map(str, SHIFTS), pairs, strict=True)),
        "macros": macro,
        "fixed_layers": frontier,
        "mixed_block_audit": mixed,
        "verified_input_sha256": artifact_hashes(artifact_dir),
        "external_inputs_reproved": {"N_gt_V": False, "DENJOY_KOKSMA": False},
        "proves_collatz": False,
        "what_this_result_does_not_prove": "This verifier checks exact finite and symbolic certificate arithmetic; it does not establish the external N>V computation, reprove Denjoy-Koksma, or prove Collatz.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_artifacts(args.artifact_dir)
    except (OSError, ValueError, json.JSONDecodeError, ZeroDivisionError) as error:
        print(json.dumps({"valid": False, "error": str(error), "proves_collatz": False}, indent=2), file=sys.stderr)
        return 1
    output = args.output or args.artifact_dir / "phase7_symbolic_verifier.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
