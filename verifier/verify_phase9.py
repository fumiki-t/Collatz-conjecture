#!/usr/bin/env python3
"""Independent exact verifier for Phase 9 artifacts.

This file intentionally does not import the Phase 9 generator.  It rebuilds
every proof-relevant integer, rational interval, finite enumeration, and digest
from primitive definitions and Phase 7/8 dependency files.
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
CF_BLOCKS = [6_586_818_670, 65_470_613_321]
A_BITS = "11101"
B_BITS = "1100"
MACRO0 = "1111111111110000000"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"cannot load {path.name}: {error}")
    if not isinstance(value, dict):
        fail(f"{path.name} must contain an object")
    return value


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pair(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        fail("malformed rational pair")
    return Fraction(int(value[0]), int(value[1]))


def interval(value: object) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict):
        fail("malformed interval")
    lower = pair(value.get("lower"))
    upper = pair(value.get("upper"))
    if not lower < upper:
        fail("empty rational interval")
    return lower, upper


def ceil_fraction(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def log_bounds(numerator: int, denominator: int = 1, terms: int = 256) -> tuple[Fraction, Fraction]:
    if numerator <= denominator or denominator <= 0:
        fail("invalid logarithm input")
    z = Fraction(numerator - denominator, numerator + denominator)
    square = z * z
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= square
    lower = 2 * total
    upper = lower + 2 * power / ((2 * terms + 1) * (1 - square))
    return lower, upper


def expm1_bounds(lower: Fraction, upper: Fraction, terms: int = 30) -> tuple[Fraction, Fraction]:
    if not 0 < lower <= upper < 1:
        fail("invalid expm1 input")

    def one(value: Fraction) -> tuple[Fraction, Fraction]:
        result = Fraction(1)
        term = Fraction(1)
        for index in range(1, terms + 1):
            term = term * value / index
            result += term
        following = term * value / (terms + 1)
        return result, result + following / (1 - value / (terms + 2))

    low, _ = one(lower)
    _, high = one(upper)
    return low - 1, high - 1


def contains(outer: tuple[Fraction, Fraction], inner: tuple[Fraction, Fraction]) -> bool:
    return outer[0] <= inner[0] < inner[1] <= outer[1]


def common() -> dict[str, object]:
    ln2 = log_bounds(2)
    ln3 = log_bounds(3)
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    log_gap = (K0 * ln2[0] - Q0 * ln3[1], K0 * ln2[1] - Q0 * ln3[0])
    delta = expm1_bounds(*log_gap)
    s0 = (Fraction(Q0, 2) / ln2[1] - 2, Fraction(Q0, 2) / ln2[0] + 2)
    weight = 6 * V * delta[0] - s0[1]
    if weight <= 0:
        fail("independent contact weight is not positive")
    return {"ln2": ln2, "ln3": ln3, "alpha": alpha, "log_gap": log_gap, "delta": delta, "S0": s0, "weight": weight}


def affine(word: str) -> tuple[int, int, int]:
    coefficient, constant, denominator = 1, 0, 1
    for bit in word:
        if bit not in "01":
            fail("nonbinary word")
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
    return coefficient, constant, denominator


def realization(coefficient: int, constant: int, denominator: int) -> tuple[int, int]:
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    source = residue or denominator
    numerator = coefficient * source + constant
    if numerator % denominator:
        fail("nonintegral affine realization")
    return source, numerator // denominator


def verify_forced(path: Path, arithmetic: dict[str, object]) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-forced-contact-v1" or data.get("proves_collatz") is not False:
        fail("forced-contact claim boundary mismatch")
    p59 = data.get("P59")
    if not isinstance(p59, dict) or p59.get("repository_status") != "CONDITIONAL":
        fail("P59 status mismatch")
    if p59.get("recurrence") != "a_(j+1)=a_j+b_j-e_j" or p59.get("forced_closure") != "a_j=0 and b_j=1 imply e_j=1 and a_(j+1)=0":
        fail("forced-contact recurrence or closure mismatch")
    if p59.get("successor_weight_ratio") != [2, 3]:
        fail("forced-contact weight ratio mismatch")
    ng17 = data.get("NG17")
    if not isinstance(ng17, dict) or ng17.get("repository_status") != "REFUTED":
        fail("NG17 status mismatch")
    rows = ng17.get("truth_table")
    if not isinstance(rows, list) or len(rows) != 8:
        fail("contact construction truth table missing")
    expected = []
    for c in (0, 1):
        for b in (1, 2):
            for nxt in (0, 1):
                closure = not (c == 1 and b == 1 and nxt == 0)
                e = b + (1 - c) - (1 - nxt)
                expected.append({"c_j": c, "b_j": b, "c_next": nxt, "closure_ok": closure, "e_j": e, "positive_when_closure_ok": (not closure) or e >= 1})
    if rows != expected or "c_0=1" not in str(ng17.get("corrected_construction_domain")):
        fail("contact construction or c0 boundary mismatch")
    witness = ng17.get("q0_symbolic_witness")
    if not isinstance(witness, dict):
        fail("NG17 witness missing")
    s0_low = arithmetic["S0"][0]
    weight = arithmetic["weight"]
    if pair(witness.get("S0_lower")) > s0_low or pair(witness.get("required_weight_lower")) > weight:
        fail("NG17 stored bounds exceed independent bounds")
    if not s0_low > weight or witness.get("strictly_satisfies_pressure") is not True or witness.get("giant_parity_word_constructed") is not False:
        fail("NG17 all-contact witness failed")
    return {"P59": "CONDITIONAL", "NG17": "REFUTED"}


def independent_dual(lam: Fraction, arithmetic: dict[str, object]) -> tuple[int, Fraction, Fraction, Fraction, Fraction]:
    ln2_low, ln2_high = arithmetic["ln2"]
    weight = arithmetic["weight"]
    first = Fraction(5, 1) / (6 * lam)
    second = Fraction(3, 1) / (4 * lam)
    log_first = log_bounds(first.numerator, first.denominator, 128)
    log_second = log_bounds(second.numerator, second.denominator, 128)
    constant = Fraction(29, 12) - 3 * lam
    numerator_high = constant - 2 * lam * log_first[0] - lam * log_second[0]
    integral_high = numerator_high / ln2_low
    variation = Fraction(29, 6) - 6 * lam
    endpoint = 1 - lam
    rotation = Q0 * integral_high + 2 * variation + endpoint
    count = ceil_fraction((weight - rotation) / lam)
    return count, integral_high, variation, endpoint, rotation


def verify_dual(path: Path, arithmetic: dict[str, object], artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-contact-dual-v1" or data.get("proves_collatz") is not False:
        fail("contact-dual claim boundary mismatch")
    scope = data.get("optimization_scope")
    if not isinstance(scope, dict) or scope.get("maximum_denominator") != 256 or scope.get("global_optimum_claimed") is not False:
        fail("contact dual optimization scope mismatch")
    stored_summary = scope.get("candidate_summary")
    expected_summary: list[list[int]] = []
    best: tuple[int, Fraction] | None = None
    for denominator in range(2, 257):
        for numerator in range((2 * denominator + 2) // 3, (3 * denominator - 1) // 4 + 1):
            if math.gcd(numerator, denominator) != 1:
                continue
            lam = Fraction(numerator, denominator)
            if not Fraction(2, 3) <= lam < Fraction(3, 4):
                continue
            count = independent_dual(lam, arithmetic)[0]
            expected_summary.append([numerator, denominator, count])
            candidate = (count, lam)
            if best is None or (count, -denominator, -numerator) > (best[0], -best[1].denominator, -best[1].numerator):
                best = candidate
    if stored_summary != expected_summary or scope.get("candidate_count") != len(expected_summary) or best is None:
        fail("contact dual candidate enumeration mismatch")
    selected = data.get("selected")
    if not isinstance(selected, dict) or pair(selected.get("lambda")) != best[1] or selected.get("contact_lower") != best[0]:
        fail("contact dual selected lambda mismatch")
    count, integral_high, variation, endpoint, rotation = independent_dual(best[1], arithmetic)
    stored_integral = interval(selected.get("integral"))
    if not stored_integral[0] < integral_high <= stored_integral[1]:
        fail("contact dual integral mismatch")
    if pair(selected.get("circle_total_variation")) != variation or pair(selected.get("two_block_DK_error")) != 2 * variation:
        fail("contact dual variation/error mismatch")
    if pair(selected.get("finite_endpoint_damage")) != endpoint or pair(selected.get("rotation_sum_upper")) < rotation:
        fail("contact dual endpoint/rotation mismatch")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("q0_ostrowski_blocks") != CF_BLOCKS:
        fail("contact dual Ostrowski decomposition mismatch")
    if dependencies.get("phase7_boundary_defect_sha256") != file_hash(artifact_dir / "phase7_boundary_defect.json"):
        fail("contact dual Phase 7 dependency hash mismatch")
    if data.get("forced_closure_contact_lower") != count or count != 35_251_435_772:
        fail("contact dual lower bound mismatch")
    return {"lambda": [best[1].numerator, best[1].denominator], "contact_lower": count}


def gap_result(contacts: int, exceptions: int = 5) -> dict[str, int]:
    long_gaps = (Q0 - contacts) // 2
    raw = (contacts - 1) - long_gaps
    return {"contacts": contacts, "maximum_gaps_at_least_3": long_gaps, "gap_at_most_2_lower": raw, "exception_damage": 2 * exceptions, "first_octave_lower": raw - 2 * exceptions}


def verify_short(path: Path, contact_lower: int, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-short-return-v1" or data.get("proves_collatz") is not False:
        fail("short-return claim boundary mismatch")
    e14 = data.get("E14")
    if not isinstance(e14, dict) or e14.get("repository_status") != "VERIFIED_FINITE":
        fail("E14 status mismatch")
    baseline = gap_result(OLD_CONTACTS)
    closure = gap_result(contact_lower)
    if e14.get("exact_formula") != "(M-1)-floor((q0-M)/2)" or e14.get("baseline_phase7_contacts") != baseline or e14.get("forced_closure_contacts") != closure:
        fail("improved gap formula or value mismatch")
    if closure["first_octave_lower"] != 16_848_437_652:
        fail("closure-aware short-return lower bound mismatch")
    if data.get("phase8_octave_bridge_sha256") != file_hash(artifact_dir / "phase8_octave_bridge.json"):
        fail("short-return Phase 8 dependency hash mismatch")
    return {"baseline": baseline["first_octave_lower"], "closure": closure["first_octave_lower"]}


def verify_endpoint(path: Path, arithmetic: dict[str, object], artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-endpoint-displacement-v1" or data.get("proves_collatz") is not False:
        fail("endpoint-displacement claim boundary mismatch")
    p60 = data.get("P60")
    if not isinstance(p60, dict) or p60.get("repository_status") != "CONDITIONAL":
        fail("P60 status mismatch")
    if p60.get("near_return_identity") != "S(a)=3*N*delta+3*(1+delta)*d" or p60.get("solved_identity") != "d=(S(a)/3-N*delta)/(1+delta)":
        fail("endpoint d identity mismatch")
    delta_low = arithmetic["delta"][0]
    s0_high = arithmetic["S0"][1]
    d_upper = (s0_high / 3 - V * delta_low) / (1 + delta_low)
    dmax = d_upper.numerator // d_upper.denominator
    if pair(p60.get("displacement_upper_fraction")) < d_upper or p60.get("maximum_integer_displacement") != dmax or dmax != DMAX:
        fail("endpoint d upper-bound mismatch")
    stored = data.get("exact_enclosures")
    if not isinstance(stored, dict):
        fail("endpoint log enclosures missing")
    for key, independent in (("ln2", arithmetic["ln2"]), ("ln3", arithmetic["ln3"]), ("K0_ln2_minus_q0_ln3", arithmetic["log_gap"]), ("delta", arithmetic["delta"]), ("S0", arithmetic["S0"])):
        if not contains(interval(stored.get(key)), independent):
            fail(f"endpoint {key} enclosure mismatch")
    h_upper = s0_high / (3 * delta_low)
    size = data.get("source_endpoint_size")
    if not isinstance(size, dict) or pair(size.get("Hq0_upper")) < h_upper or not h_upper + dmax < 2**72:
        fail("endpoint Hq0/2^72 bound mismatch")
    p61 = data.get("P61")
    if not isinstance(p61, dict) or p61.get("repository_status") != "CONDITIONAL":
        fail("P61 status mismatch")
    congruences = p61.get("endpoint_congruences")
    expected_congruences = {"N_odd": True, "X_odd": True, "d_even": True, "X_mod_4": [3], "X_mod_3": [1], "X_mod_9": [1, 7], "X_mod_36": [7, 19]}
    if congruences != expected_congruences:
        fail("endpoint parity/mod 3/mod 4/mod 9 mismatch")
    checks = {"dmax_lt_V": dmax < V, "3dmax_plus_1_lt_V": 3 * dmax + 1 < V, "2dmax_minus_1_lt_V": 2 * dmax - 1 < V, "8dmax_minus_5_lt_V": 8 * dmax - 5 < V}
    if p61.get("minimality_inequality_checks") != checks or not all(checks.values()):
        fail("endpoint minimality scalar checks mismatch")
    g4 = p61.get("G4")
    if not isinstance(g4, dict) or g4.get("map") != [9, 5, 16] or g4.get("endpoint_mod_3") != 2 or g4.get("predecessor") != "z=(2*y-1)/3":
        fail("G4 predecessor witness mismatch")
    phase8 = load(artifact_dir / "phase8_short_excursions.json")
    source_g4 = next(row for row in phase8["maps"] if row["name"] == "G4")
    if source_g4["map"] != g4["map"] or source_g4["word"] != g4["word"]:
        fail("G4 Phase 8 reconstruction mismatch")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("phase7_boundary_defect_sha256") != file_hash(artifact_dir / "phase7_boundary_defect.json") or dependencies.get("phase8_short_excursions_sha256") != file_hash(artifact_dir / "phase8_short_excursions.json"):
        fail("endpoint dependency hash mismatch")
    return {"dmax": dmax, "endpoint_mod_36": [7, 19], "G4_forbidden": True}


def cf_terms(value: Fraction) -> list[int]:
    result: list[int] = []
    while value.denominator != 1:
        quotient = value.numerator // value.denominator
        result.append(quotient)
        value = 1 / (value - quotient)
    result.append(value.numerator)
    return result


def shared_cf(lower: Fraction, upper: Fraction) -> list[int]:
    result = []
    for first, second in zip(cf_terms(lower), cf_terms(upper), strict=False):
        if first != second:
            break
        result.append(first)
    return result


def convergent_rows(terms: list[int]) -> list[tuple[int, int]]:
    p2, p1, q2, q1 = 0, 1, 1, 0
    rows = []
    for term in terms:
        p, q = term * p1 + p2, term * q1 + q2
        rows.append((p, q))
        p2, p1, q2, q1 = p1, p, q1, q
    return rows


def verify_reverse(path: Path, arithmetic: dict[str, object]) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-reverse-barrier-v1" or data.get("proves_collatz") is not False:
        fail("reverse-barrier claim boundary mismatch")
    p62 = data.get("P62")
    if not isinstance(p62, dict) or p62.get("repository_status") != "CONDITIONAL" or p62.get("valid_path_existence_claimed") is not False:
        fail("P62 status/existence boundary mismatch")
    if pair(p62.get("uniform_ratio_threshold")) != Fraction(V, V + DMAX):
        fail("reverse coefficient threshold mismatch")
    eta = log_bounds(V + DMAX, V, 64)
    if not contains(interval(p62.get("equivalent_log_gap_upper")), eta):
        fail("reverse threshold logarithm mismatch")
    certificate = data.get("continued_fraction_certificate")
    if not isinstance(certificate, dict):
        fail("reverse CF certificate missing")
    alpha = arithmetic["alpha"]
    prefix = shared_cf(*alpha)
    if certificate.get("alpha_prefix") != prefix[:25]:
        fail("reverse continued-fraction prefix mismatch")
    lower = (103_768_467_013, 65_470_613_321)
    upper = (217_976_794_617, 137_528_045_312)
    if tuple(certificate.get("lower_base", [])) != lower or tuple(certificate.get("upper_parent", [])) != upper or certificate.get("next_partial_quotient") != 5:
        fail("reverse continued-fraction parents/semiconvergent mismatch")
    if lower not in convergent_rows(prefix) or upper not in convergent_rows(prefix):
        fail("reverse parents are not convergents")
    rows = certificate.get("lower_semiconvergents")
    if not isinstance(rows, list) or len(rows) != 5:
        fail("reverse semiconvergent rows missing")
    independent_rows = []
    for t in range(1, 6):
        length = lower[0] + t * upper[0]
        odd = lower[1] + t * upper[1]
        gap = (odd * arithmetic["ln3"][0] - length * arithmetic["ln2"][1], odd * arithmetic["ln3"][1] - length * arithmetic["ln2"][0])
        independent_rows.append((t, odd, length, gap, gap[1] < eta[0], gap[0] > eta[1]))
    for stored, expected in zip(rows, independent_rows, strict=True):
        if (stored.get("t"), stored.get("a"), stored.get("L"), stored.get("meets_uniform_threshold"), stored.get("certified_insufficient")) != (expected[0], expected[1], expected[2], expected[4], expected[5]):
            fail("reverse semiconvergent classification mismatch")
        if not contains(interval(stored.get("log_gap")), expected[3]):
            fail("reverse semiconvergent log gap mismatch")
    previous = independent_rows[2]
    first = independent_rows[3]
    if certificate.get("previous_insufficient") != rows[2] or certificate.get("first_possible") != rows[3]:
        fail("reverse previous/first pair mismatch")
    determinant = previous[2] * upper[1] - previous[1] * upper[0]
    if determinant != -1 or certificate.get("previous_upper_parent_determinant") != determinant or certificate.get("first_denominator_sum") != previous[1] + upper[1]:
        fail("reverse Farey determinant/minimality mismatch")
    return {"previous": [previous[1], previous[2]], "first_possible": [first[1], first[2]]}


def floor_multiple(index: int, alpha: tuple[Fraction, Fraction]) -> int:
    if index == 0:
        return 0
    low, high = index * alpha[0], index * alpha[1]
    result = low.numerator // low.denominator
    if high.numerator // high.denominator != result or high == result:
        fail("alpha floor ambiguous")
    return result


def verify_reverse_residues(path: Path, arithmetic: dict[str, object]) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-reverse-residues-v1" or data.get("proves_collatz") is not False:
        fail("reverse-residue claim boundary mismatch")
    maximum = int(data.get("maximum_odd_inverse_steps", 0))
    coefficients = data.get("all_contracting_coefficient_pairs")
    mechanical = data.get("mechanical_near_critical_family")
    if maximum < 1 or not isinstance(coefficients, list) or not isinstance(mechanical, list):
        fail("reverse-residue finite sections missing")
    expected_coefficients = []
    expected_mechanical = []
    for odd in range(1, maximum + 1):
        max_length = floor_multiple(odd, arithmetic["alpha"])
        for length in range(odd, max_length + 1):
            numerator, denominator = 1 << length, 3**odd
            if numerator < denominator:
                expected_coefficients.append({"a": odd, "L": length, "coefficient": [numerator, denominator], "below_uniform_threshold": numerator * (V + DMAX) < denominator * V})
        floors = [floor_multiple(index, arithmetic["alpha"]) for index in range(odd + 1)]
        exponents = [floors[index] - floors[index - 1] for index in range(1, odd + 1)]
        constant = 0
        length = 0
        for index, exponent in enumerate(exponents):
            constant = (1 << exponent) * constant + 3**index
            length += exponent
        modulus = 3**odd
        residue = constant * pow(1 << length, -1, modulus) % modulus
        endpoint = residue
        predecessor = ((1 << length) * endpoint - constant) // modulus
        if predecessor <= 0:
            endpoint += modulus
            predecessor = ((1 << length) * endpoint - constant) // modulus
        expected_mechanical.append({"a": odd, "L": length, "exponent_word": exponents, "C": constant, "endpoint_residue_mod_3a": residue, "smallest_positive_endpoint": endpoint, "smallest_reverse_predecessor": predecessor, "contracting_coefficient": (1 << length) < modulus, "minimality_violation_in_q0_near_return_scenario": True, "residue_classification": "FORBIDDEN_IF_PATH_VALID"})
    if coefficients != expected_coefficients or data.get("coefficient_pair_count") != len(expected_coefficients):
        fail("reverse coefficient-pair audit mismatch")
    if not all(row["below_uniform_threshold"] for row in expected_coefficients):
        fail("reverse coefficient threshold unexpectedly survives")
    if mechanical != expected_mechanical or data.get("mechanical_family_count") != len(expected_mechanical) or data.get("surviving_mechanical_residues") != []:
        fail("reverse mechanical residue/predecessor mismatch")
    if "not every composition" not in str(data.get("scope_boundary")):
        fail("reverse-residue scope boundary missing")
    return {"maximum_a": maximum, "coefficient_pairs": len(expected_coefficients), "mechanical_rows": len(expected_mechanical)}


def update_digest(digest: object, q: int, k: int, positions: tuple[int, ...], b: int, difference: int, r2: int, r3: int, d: int, paradoxical: bool, congruence: bool, contacts: int, octave: bool) -> None:
    digest.update(bytes((q, k)))
    digest.update(bytes(positions))
    digest.update(struct.pack(">QQQQqBBBB", b, difference, r2, r3, d, paradoxical, congruence, contacts, octave))


def independent_layer(q: int) -> dict[str, object]:
    power = 3**q
    k = power.bit_length()
    modulus = 1 << k
    inverse = pow(power, -1, modulus)
    endpoint_inverse = pow(modulus, -1, power)
    floors = tuple((3**index).bit_length() - 1 for index in range(q))
    contributions = tuple(tuple(3 ** (q - 1 - index) * (1 << pos) for pos in range(floors[index] + 1)) for index in range(q))
    positions = [0] * q
    digest = hashlib.sha256()
    total = paradoxical = nontrivial = congruence_count = octave_count = near = 0
    minimum = maximum = None
    candidates = []

    def materialize(pos_tuple: tuple[int, ...], b: int, r2: int, r3: int) -> dict[str, object]:
        defects = [floors[i] - pos_tuple[i] for i in range(q)]
        word = ["0"] * k
        for pos in pos_tuple:
            word[pos] = "1"
        d = r3 - r2
        return {
            "q": q,
            "K": k,
            "parity_word": "".join(word),
            "odd_positions": list(pos_tuple),
            "defects": defects,
            "B": b,
            "D": modulus - power,
            "r2": r2,
            "r3": r3,
            "d": d,
            "paradoxical_canonical": d >= 0,
            "nontrivial_paradoxical": d >= 0 and r2 > 2,
            "reverse_minimality_congruence": r3 % 36 in (7, 19),
            "contact_count": sum(x == 0 for x in defects),
            "first_octave_diagnostic": r2 <= r3 < 2 * r2 if r2 else False,
        }

    def visit(index: int, previous: int, b: int) -> None:
        nonlocal total, paradoxical, nontrivial, congruence_count, octave_count, near, minimum, maximum
        if index == q:
            pos_tuple = tuple(positions)
            r2 = (-b * inverse) % modulus
            numerator = power * r2 + b
            if numerator % modulus:
                fail("small-layer affine equation mismatch")
            r3 = numerator // modulus
            if r3 != b * endpoint_inverse % power:
                fail("small-layer 3-adic inverse mismatch")
            d = r3 - r2
            has_congruence = r3 % 36 in (7, 19)
            is_octave = r2 <= r3 < 2 * r2 if r2 else False
            contacts = sum(floors[i] == pos_tuple[i] for i in range(q))
            is_candidate = d >= 0 or (has_congruence and is_octave)
            total += 1
            paradoxical += d >= 0
            nontrivial += d >= 0 and r2 > 2
            congruence_count += has_congruence
            octave_count += is_octave
            near += V < r2 < 2**72 and 0 <= d <= DMAX and has_congruence
            record = None
            if (
                is_candidate
                or minimum is None
                or d <= minimum["d"]
                or maximum is None
                or d >= maximum["d"]
            ):
                record = materialize(pos_tuple, b, r2, r3)
            if record is not None and (
                minimum is None or (d, record["parity_word"]) < (minimum["d"], minimum["parity_word"])
            ):
                minimum = record
            if record is not None and (
                maximum is None or (d, record["parity_word"]) > (maximum["d"], maximum["parity_word"])
            ):
                maximum = record
            if is_candidate:
                assert record is not None
                candidates.append(record)
            update_digest(digest, q, k, pos_tuple, b, modulus - power, r2, r3, d, d >= 0, has_congruence, contacts, is_octave)
            return
        for pos in range(previous + 1, floors[index] + 1):
            positions[index] = pos
            visit(index + 1, pos, b + contributions[index][pos])

    positions[0] = 0
    visit(1, 0, contributions[0][0])
    return {"q": q, "K": k, "enumerated_words": total, "row_digest_sha256": digest.hexdigest(), "paradoxical_canonical_count": paradoxical, "nontrivial_paradoxical_count": nontrivial, "reverse_minimality_congruence_count": congruence_count, "first_octave_diagnostic_count": octave_count, "q0_near_diagonal_box_count": near, "minimum_displacement_record": minimum, "maximum_displacement_record": maximum, "candidate_records": candidates}


def verify_adversarial(data: object, artifact_dir: Path) -> None:
    if not isinstance(data, dict):
        fail("mandatory adversarial audit missing")
    for exponent in range(1, 65):
        current = (1 << exponent) - 1
        for _ in range(exponent):
            if current % 2 != 1:
                fail("2^m-1 adversarial failure")
            current = (3 * current + 1) // 2
    for exponent in range(1, 33):
        current = (1 << (3 * exponent)) - 5
        observed = ""
        for _ in range(3 * exponent):
            observed += str(current % 2)
            current = (3 * current + 1) // 2 if current % 2 else current // 2
        if observed != "110" * exponent:
            fail("8^m-5 adversarial failure")
    safe = 0
    for mask in range(1 << 12):
        word = "".join("111" if (mask >> i) & 1 else "110" for i in range(12))
        odd = 0
        for depth, bit in enumerate(word, 1):
            odd += bit == "1"
            if 3**odd < 2**depth:
                break
        else:
            safe += 1
    contracting = sum(81**r * 9**s < 32**r * 16**s for r in range(1, 33) for s in range(1, 33))
    macro = load(artifact_dir / "phase7_macro12.json")
    macro0 = dict(zip(macro["record_schema"], macro["records"][0], strict=True))
    bba_map = affine(B_BITS + B_BITS + A_BITS)
    bba_source, bba_endpoint = realization(*bba_map)
    expected = {"2^m_minus_1": {"scope": "1<=m<=64", "prefix": "1^m"}, "8^m_minus_5": {"scope": "1<=m<=32", "prefix": "(110)^m"}, "(110|111)^star": {"block_length": 12, "words_checked": safe}, "A": {"word": A_BITS, "map": list(affine(A_BITS))}, "B": {"word": B_BITS, "map": list(affine(B_BITS))}, "A^rB^s": {"scope": "1<=r,s<=32", "pairs": 1024, "contracting": contracting, "noncontracting": 1024 - contracting}, "phase7_macro_0": {"word": macro0["binary_parity_word"], "multiplier": macro0["multiplier"]}, "phase8_BBA": {"word": "BBA", "shortcut_word": B_BITS + B_BITS + A_BITS, "map": list(bba_map), "least_source": bba_source, "endpoint": bba_endpoint, "descent_margin": bba_source - bba_endpoint}}
    if data != expected or safe != 1 << 12 or macro0["binary_parity_word"] != MACRO0:
        fail("mandatory adversarial regression mismatch")


def verify_two_sided(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-two-sided-residues-v1" or data.get("proves_collatz") is not False:
        fail("two-sided residue claim boundary mismatch")
    c04 = data.get("C04")
    if not isinstance(c04, dict) or c04.get("repository_status") != "OPEN" or c04.get("proved") is not False:
        fail("C04 was improperly promoted")
    box = c04.get("q0_box")
    if not isinstance(box, dict) or box.get("q") != Q0 or box.get("K") != K0 or box.get("r3_mod_36") != [7, 19] or str(DMAX) not in str(box.get("difference")):
        fail("near-diagonal q0 box mismatch")
    audit = data.get("small_layer_audit")
    if not isinstance(audit, dict) or audit.get("repository_status") != "VERIFIED_FINITE":
        fail("small-layer audit missing")
    maximum = int(audit.get("maximum_q", 0))
    stored_layers = audit.get("layers")
    if maximum < 1 or not isinstance(stored_layers, list) or len(stored_layers) != maximum:
        fail("small-layer bound/list mismatch")
    if audit.get("full_rows_materialized") is not False or "independent full re-enumeration" not in str(audit.get("storage_deviation")):
        fail("small-layer storage scope/deviation mismatch")
    total = 0
    nontrivial = 0
    for q, stored in enumerate(stored_layers, 1):
        independent = independent_layer(q)
        if stored != independent:
            fail(f"small-layer exhaustive parity/digest mismatch at q={q}")
        total += independent["enumerated_words"]
        nontrivial += independent["nontrivial_paradoxical_count"]
    if audit.get("total_words") != total or audit.get("nontrivial_paradoxical_first_crossing_words") != nontrivial or audit.get("external_A100982_values_used_as_axiom") is not False:
        fail("small-layer total/paradoxical boundary mismatch")
    mitm = data.get("meet_in_the_middle")
    if not isinstance(mitm, dict) or mitm.get("carry_information_discarded") is not False or mitm.get("q0_enumerated") is not False or mitm.get("exclusion_certificate_found") is not False:
        fail("meet-in-the-middle scope/carry mismatch")
    verify_adversarial(data.get("mandatory_adversarial_audit"), artifact_dir)
    return {"maximum_q": maximum, "total_words": total, "nontrivial_paradoxical": nontrivial}


def independent_tree(maximum: int) -> tuple[list[dict[str, int]], list[dict[str, object]]]:
    states = [(0, 1, 0, 0)]
    summaries = []
    records = []
    for length in range(1, maximum + 1):
        denominator = 1 << length
        step = 1 << (length - 1)
        following = []
        contracting = cylinders = realization_total = 0
        for bits, coefficient, constant, odd in states:
            for bit in (0, 1):
                if bit:
                    new_coefficient, new_constant, new_odd = 3 * coefficient, 3 * constant + step, odd + 1
                else:
                    new_coefficient, new_constant, new_odd = coefficient, constant, odd
                new_bits = (bits << 1) | bit
                following.append((new_bits, new_coefficient, new_constant, new_odd))
                if new_coefficient >= denominator:
                    continue
                contracting += 1
                source, endpoint = realization(new_coefficient, new_constant, denominator)
                d = endpoint - source
                difference = denominator - new_coefficient
                if source > 2 and d >= 0:
                    count = d // difference + 1
                    cylinders += 1
                    realization_total += count
                    records.append({"length": length, "q": new_odd, "parity_word": format(new_bits, f"0{length}b"), "B": new_constant, "D": difference, "canonical_source": source, "canonical_endpoint": endpoint, "canonical_difference": d, "positive_paradoxical_realizations": count, "largest_start_in_cylinder": source + denominator * (count - 1)})
        summaries.append({"length": length, "all_words": 1 << length, "contracting_words": contracting, "paradoxical_cylinders": cylinders, "paradoxical_realizations": realization_total})
        states = following
    return summaries, records


def verify_tree(path: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase9-paradoxical-tree-v1" or data.get("proves_collatz") is not False:
        fail("paradoxical-tree claim boundary mismatch")
    maximum = int(data.get("maximum_shortcut_length", 0))
    summaries, records = independent_tree(maximum)
    if data.get("summaries") != summaries or data.get("paradoxical_records") != records:
        fail("paradoxical tree/cylinder enumeration mismatch")
    if data.get("cylinder_identity") != "F(r2+2^K*t)-(r2+2^K*t)=(r3-r2)-(2^K-3^q)*t":
        fail("paradoxical cylinder identity mismatch")
    if data.get("new_rank_found") is not False or data.get("exact_counterexample_to_C04_found") is not False:
        fail("paradoxical tree overclaim")
    external = data.get("external_target")
    if not isinstance(external, dict) or external.get("repository_status") != "EXTERNAL_EVIDENCE" or external.get("external_results_reproved") is not False:
        fail("paradoxical external-evidence boundary mismatch")
    return {"maximum_length": maximum, "records": len(records), "new_rank": False}


def verify(artifact_dir: Path) -> dict[str, object]:
    arithmetic = common()
    forced = verify_forced(artifact_dir / "phase9_forced_contact.json", arithmetic)
    dual = verify_dual(artifact_dir / "phase9_contact_dual.json", arithmetic, artifact_dir)
    short = verify_short(artifact_dir / "phase9_short_return_bound.json", int(dual["contact_lower"]), artifact_dir)
    endpoint = verify_endpoint(artifact_dir / "phase9_endpoint_displacement.json", arithmetic, artifact_dir)
    reverse = verify_reverse(artifact_dir / "phase9_reverse_barrier.json", arithmetic)
    reverse_residues = verify_reverse_residues(artifact_dir / "phase9_reverse_residues.json", arithmetic)
    two_sided = verify_two_sided(artifact_dir / "phase9_two_sided_residues.json", artifact_dir)
    tree = verify_tree(artifact_dir / "phase9_paradoxical_tree.json")
    report = (artifact_dir / "phase9_obstruction_report.md").read_text(encoding="utf-8")
    if "What this result does not prove" not in report or "does not claim a proof or disproof" not in report:
        fail("Phase 9 obstruction report lacks claim boundary")
    return {"valid": True, "forced_contact": forced, "contact_dual": dual, "short_returns": short, "endpoint": endpoint, "reverse_barrier": reverse, "reverse_residues": reverse_residues, "two_sided_residues": two_sided, "paradoxical_tree": tree, "external_inputs_reproved": {"EXT04": False, "X02": False, "Rozier_Terracol_Theorem_1_3": False, "Winkler_tree": False}, "C04": "OPEN", "proves_collatz": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    try:
        result = verify(arguments.artifact_dir)
    except (OSError, ValueError, KeyError, TypeError, StopIteration, struct.error) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
