#!/usr/bin/env python3
"""Independent exact verifier for the Phase 8 artifact set.

The verifier rebuilds the affine algebra, CRT cases, rational logarithm
enclosure, short-excursion maps, and both bounded semigroup enumerations.  It
does not import the generator implementation and does not accept floating
point evidence for a proof decision.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path


Q0 = 72_057_431_991
K0 = 114_208_327_604
V = 2075 * (1 << 60)
CONTACTS = 31_327_720_462
H12_PAIRS = 889_748_829
A_BITS = "11101"
B_BITS = "1100"
A_AFFINE = (81, 73, 32)
B_AFFINE = (9, 5, 16)
BASE_PAIRS = ((1, 2), (1, 3), (1, 4), (2, 4), (3, 5), (3, 6))
FIELDS = [
    "id",
    "block_length",
    "block_word",
    "shortcut_word",
    "A_count",
    "B_count",
    "affine_A",
    "affine_B",
    "denominator",
    "least_source",
    "endpoint",
    "descent_margin",
    "source_U",
    "endpoint_U",
]

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


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def rational(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        fail("malformed rational pair")
    return Fraction(int(value[0]), int(value[1]))


def affine(word: str) -> tuple[int, int, int]:
    """Compose shortcut steps directly, independently of block constants."""
    numerator_coefficient = 1
    numerator_constant = 0
    denominator = 1
    for bit in word:
        if bit not in "01":
            fail("nonbinary parity word")
        if bit == "1":
            numerator_coefficient *= 3
            numerator_constant = 3 * numerator_constant + denominator
        denominator *= 2
    return numerator_coefficient, numerator_constant, denominator


def append(
    coefficient: int,
    constant: int,
    denominator: int,
    block: tuple[int, int, int],
) -> tuple[int, int, int]:
    block_coefficient, block_constant, block_denominator = block
    return (
        block_coefficient * coefficient,
        block_coefficient * constant + block_constant * denominator,
        block_denominator * denominator,
    )


def realize(coefficient: int, constant: int, denominator: int) -> tuple[int, int]:
    source_residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    source = source_residue if source_residue else denominator
    endpoint_numerator = coefficient * source + constant
    if endpoint_numerator % denominator:
        fail("CRT realization is not integral")
    return source, endpoint_numerator // denominator


def run_word(source: int, word: str) -> int:
    current = source
    for bit in word:
        if current % 2 != int(bit):
            fail("least source does not realize parity word")
        current = (3 * current + 1) // 2 if bit == "1" else current // 2
    return current


def row(row_id: int, state: tuple[str, str, int, int, int]) -> list[object]:
    block_word, shortcut_word, coefficient, constant, denominator = state
    source, endpoint = realize(coefficient, constant, denominator)
    if run_word(source, shortcut_word) != endpoint:
        fail("direct shortcut reconstruction disagrees with affine map")
    source_u = 49 * source + 73
    endpoint_u = 49 * endpoint + 73
    if source_u % 49 != 73 % 49 or endpoint_u % 49 != 73 % 49:
        fail("U-coordinate invariant failed")
    current_u = source_u
    for block_name in block_word:
        if block_name == "A":
            if current_u % 32:
                fail("U-coordinate does not realize A transition")
            current_u = 81 * (current_u // 32)
        else:
            if (current_u - 108) % 16:
                fail("U-coordinate does not realize B transition")
            current_u = 9 * ((current_u - 108) // 16) + 108
    if current_u != endpoint_u:
        fail("U-coordinate endpoint mismatch")
    return [
        row_id,
        len(block_word),
        block_word,
        shortcut_word,
        block_word.count("A"),
        block_word.count("B"),
        coefficient,
        constant,
        denominator,
        source,
        endpoint,
        source - endpoint,
        source_u,
        endpoint_u,
    ]


def crt(a: int, modulus_a: int, b: int, modulus_b: int) -> int:
    value = a % modulus_a
    value += modulus_a * (((b - value) * pow(modulus_a, -1, modulus_b)) % modulus_b)
    return value or modulus_a * modulus_b


def base_case(r: int, s: int) -> dict[str, object]:
    modulus = 16**s
    residue_two = (108 * pow(81**r, -1, modulus)) % modulus
    residue_49 = (73 * pow(32**r, -1, 49)) % 49
    u = crt(residue_two, modulus, residue_49, 49)
    source_numerator = u * 32**r - 73
    after_numerator = u * 81**r - 73
    if source_numerator % 49 or after_numerator % 49:
        fail("C02 CRT reconstruction failed")
    source = source_numerator // 49
    endpoint = after_numerator // 49
    for _ in range(s):
        value = 9 * endpoint + 5
        if value % 16:
            fail("C02 base case fails B integrality")
        endpoint = value // 16
    p = 81**r * 9**s
    q = 32**r * 16**s
    margin = u * (q - p) - 108 * (16**s - 9**s)
    if not (p < q and margin > 0 and endpoint < source):
        fail("C02 base case fails strict descent")
    return {
        "r": r,
        "s": s,
        "u_congruence_mod_16s": residue_two,
        "u_congruence_mod_49": residue_49,
        "crt_modulus": 49 * modulus,
        "least_u": u,
        "least_source": source,
        "after_A_power": after_numerator // 49,
        "endpoint": endpoint,
        "P": p,
        "Q": q,
        "C02_core_margin": margin,
        "source_descent_margin": source - endpoint,
        "all_realizations": f"u={u}+{49 * modulus}*t, t>=0",
    }


def verify_c02(path: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase8-c02-theorem-v1" or data.get("proves_collatz") is not False:
        fail("C02 claim boundary mismatch")
    claim = data.get("claim")
    if not isinstance(claim, dict) or claim.get("id") != "C02" or claim.get("repository_status") != "VERIFIED_THEOREM":
        fail("C02 theorem status mismatch")
    if claim.get("dependencies") != ["exact affine algebra", "integrality congruences", "EXT05", "six exact base cases"]:
        fail("C02 dependencies mismatch")

    convention = data.get("composition_convention")
    if not isinstance(convention, dict):
        fail("C02 composition convention missing")
    if affine(A_BITS) != A_AFFINE or affine(B_BITS) != B_AFFINE:
        fail("independent A/B affine reconstruction failed")
    if convention.get("A") != {"word": A_BITS, "map": list(A_AFFINE)} or convention.get("B") != {
        "word": B_BITS,
        "map": list(B_AFFINE),
    }:
        fail("C02 A/B composition data mismatch")
    if convention.get("function") != "F_(r,s)=B^s composed with A^r":
        fail("C02 function order mismatch")

    reduction = data.get("integrality_reduction")
    expected_reduction = {
        "A_identity": "49*A(x)+73=(81/32)*(49*x+73)",
        "u_definition": "u=(49*x+73)/32^r",
        "A_power": "A^r(x)=(81^r*u-73)/49",
        "B_identity": "7*B(x)-5=(9/16)*(7*x-5)",
        "congruences": ["u*81^r=108 mod 16^s", "u*32^r=73 mod 49"],
        "valuation": "v2(u)=2",
        "lower_bound": "u>=4",
    }
    if reduction != expected_reduction:
        fail("C02 integrality congruence or valuation mismatch")

    sign = data.get("sign_identity")
    if sign != {
        "left": "49*Q*(F_(r,s)(x)-x)",
        "right": "32^r*(u*(P-Q)+108*(16^s-9^s))",
        "core_equivalence": "F_(r,s)(x)<x iff u*(Q-P)>108*(16^s-9^s)",
    }:
        fail("C02 sign identity mismatch")
    # Independent coefficient expansion: using
    # 49*16^s*F = 35*16^s + 9^s*(81^r*u-108) and
    # 49*x = 32^r*u-73, both u and constant coefficients must agree.
    for r, s in ((1, 1), (2, 4), (4, 7), (11, 13)):
        p, q = 81**r * 9**s, 32**r * 16**s
        left_u = 32**r * 9**s * 81**r - q * 32**r
        left_constant = 32**r * (35 * 16**s - 108 * 9**s) + 73 * q
        if left_u != 32**r * (p - q) or left_constant != 32**r * 108 * (16**s - 9**s):
            fail("C02 symbolic coefficient expansion failed")

    cases = data.get("case_partition")
    if not isinstance(cases, dict):
        fail("C02 case partition missing")
    stored_bases = cases.get("six_base_cases")
    expected_bases = [base_case(r, s) for r, s in BASE_PAIRS]
    if stored_bases != expected_bases:
        fail("C02 CRT base cases or strict margin mismatch")
    if cases.get("r_ge_2_P_over_Q_at_most_half") != {
        "proof": "u*(Q-P)>=4*(Q/2)=2Q>108*16^s>108*(16^s-9^s)",
        "minimum_scalar_check": [2 * 32**2, 108],
    }:
        fail("C02 r>=2 half-multiplier case mismatch")
    if cases.get("r1_s_ge_5") != {
        "equivalent_inequality": "20*16^s>216*9^s",
        "base_check_s5": [5 * 16**5, 54 * 9**5],
        "monotone_ratio": [16, 9],
    }:
        fail("C02 r=1 monotone case mismatch")
    if cases.get("small_regimes") != {
        "r1": {"noncontracting_boundary": [1, 1], "base_s": [2, 3, 4], "monotone_s_from": 5},
        "r2": {"noncontracting_through_s": 3, "between_half_and_one_s": [4], "at_most_half_from_s": 5},
        "r3": {"noncontracting_through_s": 4, "between_half_and_one_s": [5, 6], "at_most_half_from_s": 7},
    }:
        fail("C02 small-regime partition mismatch")
    if not (2 * 32**2 > 108 and 5 * 16**5 > 54 * 9**5):
        fail("C02 elementary cases failed")
    if not (2 * 6561**4 < 8192**4 and 2**40 > 7 * 5**16 and 7**4 > 54):
        fail("C02 external-regime exact inequalities failed")
    external_r_factor = Fraction(2**24, 5**8)
    external_s_factor = Fraction(2**8, 5**4)
    reduced_factor = Fraction(2**40, 5**16)
    if not external_s_factor < 1 or external_r_factor * external_s_factor**2 != reduced_factor:
        fail("C02 external exponent reduction failed")
    for r in range(4, 9):
        if not Fraction(1, 2) * reduced_factor**r > Fraction(7**r, 2) > 27:
            fail("C02 external terminal bound failed")
    # Check that every possible r>=4 case with nu<30 is noncontracting.
    for r in range(4, 8):
        for s in range(1, 15):
            if 4 * r + 2 * s < 30 and 81**r * 9**s < 32**r * 16**s:
                fail("C02 claimed external exponent threshold is false")
    external_case = cases.get("r_ge_4_between_half_and_one")
    if not isinstance(external_case, dict):
        fail("C02 external case missing")
    required_external_case = {
        "s_strictly_below_2r": True,
        "s_ge_2r_contradiction": [2 * 6561**4, 8192**4],
        "minimum_nu": 30,
        "nu_minimum_witness_check": [81**4 * 9**6, 32**4 * 16**6],
        "external_lower_bound_after_dividing_16s": "(Q-P)/16^s > (1/2)*(2^40/5^16)^r > 7^r/2 > 27",
        "exact_power_check": [2**40, 7 * 5**16],
        "terminal_check": [7**4, 54],
    }
    if external_case != required_external_case:
        fail("C02 external gap reduction mismatch")

    external = data.get("external_input")
    if not isinstance(external, dict) or external.get("id") != "EXT05" or external.get("repository_status") != "EXTERNAL_THEOREM":
        fail("EXT05 metadata missing")
    if external.get("statement") != "for positive k,q with q>12, abs(2^k-3^q)>(64/25)^q/2":
        fail("EXT05 statement mismatch")
    if external.get("application") != {"kappa": "5r+4s", "nu": "4r+2s", "nu_greater_than_18": True}:
        fail("EXT05 exponent application mismatch")
    if external.get("finite_13_to_18_part_used") is not False:
        fail("EXT05 finite-range dependency mismatch")
    return {"base_cases": len(expected_bases), "external_minimum_nu": 30}


def log_bounds(numerator: int, denominator: int = 1, terms: int = 192) -> tuple[Fraction, Fraction]:
    if numerator <= denominator or denominator <= 0:
        fail("invalid logarithm input")
    z = Fraction(numerator - denominator, numerator + denominator)
    square = z * z
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= square
    low = 2 * total
    high = low + 2 * power / ((2 * terms + 1) * (1 - square))
    return low, high


def verify_octave(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase8-octave-bridge-v1" or data.get("proves_collatz") is not False:
        fail("octave artifact claim boundary mismatch")
    if data.get("constants") != {"q0": Q0, "K0": K0, "V": V}:
        fail("octave q0, K0, or V mismatch")
    p58 = data.get("P58")
    if not isinstance(p58, dict) or p58.get("repository_status") != "CONDITIONAL" or p58.get("proves_collatz") is not False:
        fail("P58 status mismatch")
    expected_identities = [
        "x_j=2^(theta_j+a_j)*(N+R_j)",
        "R_(j+1)=R_j+(1/3)*2^(-theta_j-a_j)",
        "0<=R_j<=j/3",
        "2^a_j*N<=x_j<2^(a_j+1)*(N+j/3)",
    ]
    if p58.get("identities") != expected_identities:
        fail("P58 exact octave identity mismatch")
    # Rebuild the rational part of the normalization from primitive odd-step
    # positions.  The irrational-looking factor is exactly 3^j/2^d_j because
    # theta_j+a_j=j*log2(3)-d_j.
    for odd_positions in ([0, 1, 3, 4], [0, 2, 3, 5, 6], [0, 1, 2, 4, 5, 7]):
        for j, d_j in enumerate(odd_positions):
            correction = sum(3 ** (j - 1 - i) * 2**odd_positions[i] for i in range(j))
            r_j = Fraction(correction, 3**j)
            reconstructed = Fraction(1, 3) * sum(
                (Fraction(2**odd_positions[i], 3**i) for i in range(j)),
                Fraction(0),
            )
            if r_j != reconstructed:
                fail("P58 correction normalization failed")
            for source in (1, 27, 703):
                x_j = Fraction(3**j * source + correction, 2**d_j)
                if x_j != Fraction(3**j, 2**d_j) * (source + r_j):
                    fail("P58 octave identity coefficient check failed")

    eta = data.get("eta")
    if not isinstance(eta, dict):
        fail("eta certificate missing")
    stored_low, stored_high = rational(eta.get("lower")), rational(eta.get("upper"))
    ln2_low, ln2_high = log_bounds(2)
    eta_log_low, eta_log_high = log_bounds(3 * V + Q0, 3 * V)
    independent_low = eta_log_low / ln2_high
    independent_high = eta_log_high / ln2_low
    if not stored_low <= independent_low < independent_high <= stored_high:
        fail("stored eta interval does not contain independent enclosure")
    if rational(eta.get("q0_times_eta_upper")) != Q0 * stored_high:
        fail("q0 eta product mismatch")
    if not Q0 * stored_high < 2 or eta.get("q0_times_eta_strictly_below_2") is not True:
        fail("q0 eta strict bound failed")

    dk = data.get("denjoy_koksma")
    if not isinstance(dk, dict):
        fail("Denjoy-Koksma certificate missing")
    if dk != {
        "dependency": "EXT04",
        "continued_fraction_denominator_blocks": [6_586_818_670, 65_470_613_321],
        "sum": Q0,
        "indicator_circle_variation": 2,
        "error_per_block": 2,
        "total_error": 4,
        "maximum_integer_exception_count": 5,
    }:
        fail("Denjoy-Koksma variation, error, or exception count mismatch")
    # q0*eta+4<6 and integrality imply at most five exceptions.
    if not Q0 * stored_high + dk["total_error"] < 6:
        fail("integer exception deduction did not close")

    boundary_path = artifact_dir / "phase7_boundary_defect.json"
    correlation_path = artifact_dir / "phase7_contact_autocorrelation.json"
    boundary = load(boundary_path)
    correlation = load(correlation_path)
    contacts = int(boundary["contact_density"]["minimum_contact_count"])
    h12 = next(int(item["contact_pair_count_lower"]) for item in correlation["rows"] if int(item["h"]) == 12)
    if contacts != CONTACTS or h12 != H12_PAIRS:
        fail("Phase 7 numerical dependencies changed")
    dependencies = data.get("phase7_dependencies")
    if dependencies != {
        "phase7_boundary_defect_sha256": digest(boundary_path),
        "phase7_contact_autocorrelation_sha256": digest(correlation_path),
        "minimum_contacts": contacts,
        "h12_nonwrapping_pairs": h12,
    }:
        fail("Phase 7 dependency hash or value mismatch")

    exceptions = int(dk["maximum_integer_exception_count"])
    raw_gaps = (contacts - 1) - (Q0 - 1) // 3
    expected_e13 = {
        "repository_status": "VERIFIED_FINITE",
        "conditional_dependencies": ["P58", "X02", "EXT04", "Phase 7 contact certificates"],
        "first_octave_odd_iterates_lower": contacts - exceptions,
        "h12_first_octave_pairs_lower": h12 - 2 * exceptions,
        "raw_consecutive_contact_gap_at_most_2_lower": raw_gaps,
        "first_octave_consecutive_contact_gap_at_most_2_lower": raw_gaps - 2 * exceptions,
        "exception_damage": {"contacts": 1, "h12_pairs_per_exception": 2, "adjacent_gaps_per_exception": 2},
    }
    if data.get("E13") != expected_e13:
        fail("E13 finite consequence mismatch")
    if data.get("external_inputs") != {"X02_N_greater_than_V_reproved": False, "EXT04_Denjoy_Koksma_reproved": False}:
        fail("octave external-input boundary mismatch")
    return {
        "maximum_exceptions": exceptions,
        "first_octave_odd_iterates": contacts - exceptions,
        "h12_pairs": h12 - 2 * exceptions,
        "short_returns": raw_gaps - 2 * exceptions,
    }


def residue(word: str) -> int:
    modulus = 1 << len(word)
    matches: list[int] = []
    for source in range(modulus):
        current = source
        for bit in word:
            if current % 2 != int(bit):
                break
            current = (3 * current + 1) // 2 if bit == "1" else current // 2
        else:
            matches.append(source)
    if len(matches) != 1:
        fail("parity word does not define one residue")
    return matches[0]


def verify_short(path: Path, short_returns: int) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase8-short-excursions-v1" or data.get("proves_collatz") is not False:
        fail("short-excursion claim boundary mismatch")
    if data.get("repository_status") != "VERIFIED_THEOREM" or data.get("defect_recurrence") != "e_t=b_t+a_t-a_(t+1)":
        fail("short-excursion recurrence/status mismatch")
    specifications = [
        ("G1", 1, [0, 0], [1], [1], "1", "11", [3, 1, 2], [1, 0, 1, True], [4, -1, 3, False]),
        ("G2", 1, [0, 0], [2], [2], "10", "101", [3, 1, 4], [4, -1, 3, True], [2, 0, 1, False]),
        ("G3", 2, [0, 1, 0], [2, 1], [1, 2], "110", "1101", [9, 5, 8], [1, 0, 1, True], [16, -5, 9, False]),
        ("G4", 2, [0, 1, 0], [2, 2], [1, 3], "1100", "11001", [9, 5, 16], [16, -5, 9, True], [2, 0, 1, False]),
    ]
    expected_rows = []
    for name, gap, defects, increments, shortcut_gaps, word, full_word, map_data, lower, upper in specifications:
        if list(affine(word)) != map_data:
            fail("independent short-excursion affine reconstruction failed")
        if [increments[i] + defects[i] - defects[i + 1] for i in range(gap)] != shortcut_gaps:
            fail("defect recurrence does not reconstruct shortcut gaps")
        expected_rows.append(
            {
                "name": name,
                "odd_gap": gap,
                "defects": defects,
                "mechanical_increments": increments,
                "shortcut_gaps": shortcut_gaps,
                "word": word,
                "word_with_endpoint_parity": full_word,
                "map": map_data,
                "source_interval": {"lower": lower, "upper": upper},
                "source_residue": residue(full_word),
                "source_modulus": 1 << len(full_word),
            }
        )
    if data.get("maps") != expected_rows:
        fail("short-excursion word, map, constant, interval, or residue mismatch")
    if data.get("first_octave_short_return_lower") != short_returns:
        fail("short-excursion count dependency mismatch")
    return {"maps": len(expected_rows)}


def verify_records(search: dict[str, object], *, first_crossing: bool) -> tuple[int, list[int], list[object] | None]:
    if search.get("repository_status") != "VERIFIED_FINITE" or search.get("record_schema") != FIELDS:
        fail("semigroup finite-search status or schema mismatch")
    maximum = int(search.get("maximum_block_length", 0))
    if maximum < 1:
        fail("invalid semigroup search bound")
    stored_records = search.get("records")
    if not isinstance(stored_records, list):
        fail("semigroup records missing")
    active: list[tuple[str, str, int, int, int]] = [("", "", 1, 0, 1)]
    counts: list[int] = []
    record_index = 0
    minimum: list[object] | None = None
    for _length in range(1, maximum + 1):
        next_active: list[tuple[str, str, int, int, int]] = []
        count = 0
        for block_word, shortcut_word, coefficient, constant, denominator in active:
            for name, bits, block_map in (("A", A_BITS, A_AFFINE), ("B", B_BITS, B_AFFINE)):
                new_state = (
                    block_word + name,
                    shortcut_word + bits,
                    *append(coefficient, constant, denominator, block_map),
                )
                contracting = new_state[2] < new_state[4]
                if contracting:
                    expected = row(record_index, new_state)
                    if record_index >= len(stored_records) or stored_records[record_index] != expected:
                        fail(f"semigroup record mismatch at id {record_index}")
                    if int(expected[10]) >= int(expected[9]):
                        fail(f"C03 counterexample found at id {record_index}")
                    if minimum is None or (int(expected[11]), int(expected[1]), str(expected[2])) < (
                        int(minimum[11]),
                        int(minimum[1]),
                        str(minimum[2]),
                    ):
                        minimum = expected
                    record_index += 1
                    count += 1
                if not first_crossing or not contracting:
                    next_active.append(new_state)
        counts.append(count)
        active = next_active
    if record_index != len(stored_records) or search.get("total") != record_index:
        fail("semigroup total mismatch")
    if search.get("counts_by_exact_length") != counts:
        fail("semigroup length counts mismatch")
    return record_index, counts, minimum


def verify_adversarial(data: object, artifact_dir: Path) -> None:
    if not isinstance(data, dict):
        fail("mandatory adversarial audit missing")
    for m in range(1, 65):
        current = (1 << m) - 1
        observed = ""
        for _ in range(m):
            observed += str(current % 2)
            if current % 2 == 0:
                fail("2^m-1 prefix unexpectedly became even")
            current = (3 * current + 1) // 2
        if observed != "1" * m:
            fail("2^m-1 adversarial regression failed")
    for m in range(1, 33):
        current = (1 << (3 * m)) - 5
        observed = ""
        for _ in range(3 * m):
            observed += str(current % 2)
            current = (3 * current + 1) // 2 if current % 2 else current // 2
        if observed != "110" * m:
            fail("8^m-5 adversarial regression failed")
    safe_count = 0
    for mask in range(1 << 12):
        word = "".join("111" if (mask >> index) & 1 else "110" for index in range(12))
        odd = 0
        for depth, bit in enumerate(word, start=1):
            odd += bit == "1"
            if 3**odd < 2**depth:
                break
        else:
            safe_count += 1
    pair_count = 0
    contracting_pairs = 0
    noncontracting_safe = 0
    closest_above: tuple[Fraction, int, int] | None = None
    for r in range(1, 65):
        for s in range(1, 65):
            pair_count += 1
            coefficient = 81**r * 9**s
            denominator = 32**r * 16**s
            if coefficient < denominator:
                contracting_pairs += 1
            else:
                noncontracting_safe += 1
                excess = Fraction(coefficient - denominator, denominator)
                if closest_above is None or excess < closest_above[0]:
                    closest_above = (excess, r, s)
    if closest_above is None:
        fail("A^rB^s bounded audit is empty")
    macro = load(artifact_dir / "phase7_macro12.json")
    schema = macro.get("record_schema")
    records = macro.get("records")
    if not isinstance(schema, list) or not isinstance(records, list) or not records:
        fail("Phase 7 macro dependency malformed")
    first = dict(zip(schema, records[0], strict=True))
    expected = {
        "2^m_minus_1": {"scope": "1<=m<=64", "verified_prefix": "1^m"},
        "8^m_minus_5": {"scope": "1<=m<=32", "verified_prefix": "(110)^m"},
        "(110|111)^star": {"block_length": 12, "words_checked": safe_count, "all_coefficient_safe": True},
        "A": {"word": A_BITS, "map": list(A_AFFINE)},
        "B": {"word": B_BITS, "map": list(B_AFFINE)},
        "A^rB^s": {
            "scope": "1<=r,s<=64",
            "pairs_checked": pair_count,
            "contracting_pairs": contracting_pairs,
            "contracting_case": "covered universally by C02",
            "noncontracting_coefficient_safe_prefixes": noncontracting_safe,
            "closest_multiplier_above_one": {
                "r": closest_above[1],
                "s": closest_above[2],
                "excess": [str(closest_above[0].numerator), str(closest_above[0].denominator)],
            },
            "AB_map": [729, 817, 512],
            "AB_fixed_point": [-817, 217],
            "noncontracting_scope": "ADVERSARIAL_ONLY_NOT_COVERED_BY_C02_DESCENT",
        },
        "phase7_macro_0": {
            "word": first["binary_parity_word"],
            "multiplier": first["multiplier"],
            "C03_scope": "OUT_OF_SCOPE_NOT_AN_AB_BLOCK_WORD",
        },
    }
    if data != expected or safe_count != 1 << 12 or first["binary_parity_word"] != "1111111111110000000":
        fail("mandatory adversarial artifact mismatch")


def verify_semigroup(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase8-ab-semigroup-v1" or data.get("proves_collatz") is not False:
        fail("semigroup claim boundary mismatch")
    if data.get("coordinate") != {
        "definition": "U=49x+73",
        "A": "U=32u -> U'=81u",
        "B": "U=16u+108 -> U'=9u+108",
        "invariant": "U=73 mod 49",
    }:
        fail("U-coordinate transition mismatch")
    c03 = data.get("C03")
    if not isinstance(c03, dict) or c03.get("repository_status") != "OPEN" or c03.get("proved") is not False:
        fail("C03 was improperly promoted")
    contracting = data.get("contracting_search")
    crossing = data.get("first_crossing_search")
    if not isinstance(contracting, dict) or not isinstance(crossing, dict):
        fail("semigroup search sections missing")
    contracting_total, _, minimum = verify_records(contracting, first_crossing=False)
    crossing_total, crossing_counts, _ = verify_records(crossing, first_crossing=True)
    if contracting.get("counterexamples") != [] or minimum is None:
        fail("bounded C03 counterexample field mismatch")
    if contracting.get("minimum_descent_margin_record") != dict(zip(FIELDS, minimum, strict=True)):
        fail("minimum C03 descent margin mismatch")
    mixed_total = sum(
        1
        for stored in contracting["records"]
        if int(stored[4]) > 0 and int(stored[5]) > 0
    )
    if contracting.get("mixed_total") != mixed_total:
        fail("mixed contracting count mismatch")
    mixed_minimum = min(
        (stored for stored in contracting["records"] if int(stored[4]) > 0 and int(stored[5]) > 0),
        key=lambda stored: (int(stored[11]), int(stored[1]), str(stored[2])),
    )
    if contracting.get("minimum_mixed_descent_margin_record") != dict(
        zip(FIELDS, mixed_minimum, strict=True)
    ):
        fail("minimum mixed C03 descent margin mismatch")
    if contracting.get("pure_B_words_included") != int(contracting["maximum_block_length"]):
        fail("pure-B contracting-word accounting mismatch")
    if int(contracting["maximum_block_length"]) == 18 and (contracting_total, mixed_total) != (79_184, 79_166):
        fail("length-18 all/mixed contracting count mismatch")
    if int(crossing["maximum_block_length"]) == 22:
        observed = {index + 1: count for index, count in enumerate(crossing_counts) if count}
        expected = {1: 1, 3: 1, 6: 2, 8: 7, 11: 23, 14: 99, 16: 476, 19: 1966, 21: 9690}
        if observed != expected or crossing_total != 12_265:
            fail("length-22 first-crossing count mismatch")
    verify_adversarial(data.get("mandatory_adversarial_audit"), artifact_dir)
    return {
        "contracting_maximum_length": int(contracting["maximum_block_length"]),
        "contracting_words": contracting_total,
        "mixed_contracting_words": mixed_total,
        "minimum_descent_margin": int(minimum[11]),
        "minimum_margin_word": str(minimum[2]),
        "minimum_mixed_descent_margin": int(mixed_minimum[11]),
        "minimum_mixed_margin_word": str(mixed_minimum[2]),
        "crossing_maximum_length": int(crossing["maximum_block_length"]),
        "first_crossings": crossing_total,
        "counterexamples": 0,
    }


def verify(artifact_dir: Path) -> dict[str, object]:
    c02 = verify_c02(artifact_dir / "phase8_c02_theorem.json")
    octave = verify_octave(artifact_dir / "phase8_octave_bridge.json", artifact_dir)
    short = verify_short(artifact_dir / "phase8_short_excursions.json", int(octave["short_returns"]))
    semigroup = verify_semigroup(artifact_dir / "phase8_ab_semigroup_search.json", artifact_dir)
    report_path = artifact_dir / "phase8_obstruction_report.md"
    report = report_path.read_text(encoding="utf-8")
    if "What this result does not prove" not in report or "does not claim a proof of the Collatz conjecture" not in report:
        fail("obstruction report lacks claim boundary")
    return {
        "valid": True,
        "C02": "VERIFIED_THEOREM",
        "C03": "OPEN",
        "c02": c02,
        "octave": octave,
        "short_excursions": short,
        "semigroup": semigroup,
        "external_inputs_reproved": {"EXT04": False, "EXT05": False, "X02": False},
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    try:
        result = verify(arguments.artifact_dir)
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output is not None:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
