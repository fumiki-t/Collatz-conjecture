#!/usr/bin/env python3
"""Generate exact Phase 8 mixed-block and octave-bridge artifacts.

No proof decision uses floating point.  The two external inputs used by the
octave consequences and the one external theorem used by C02 are isolated in
the generated claim records.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterator


Q0 = 72_057_431_991
K0 = 114_208_327_604
V = 2075 * (1 << 60)
CF_DENOMINATORS = (6_586_818_670, 65_470_613_321)
PHASE7_CONTACTS = 31_327_720_462
PHASE7_H12_PAIRS = 889_748_829
BASE_CASES = ((1, 2), (1, 3), (1, 4), (2, 4), (3, 5), (3, 6))
A_WORD = "11101"
B_WORD = "1100"
A_MAP = (81, 73, 32)
B_MAP = (9, 5, 16)
PHASE7_MACRO0 = "1111111111110000000"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def outward_dyadic(lower: Fraction, upper: Fraction, bits: int = 256) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    low_numerator = lower.numerator * scale // lower.denominator
    high_numerator = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(low_numerator, scale), Fraction(high_numerator, scale)


def log_interval(numerator: int, denominator: int = 1, *, terms: int = 160) -> tuple[Fraction, Fraction]:
    """Exact enclosure of log(numerator/denominator) using the atanh series."""
    if denominator <= 0 or numerator <= denominator:
        raise ValueError("log interval requires numerator > denominator > 0")
    z = Fraction(numerator - denominator, numerator + denominator)
    z_squared = z * z
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= z_squared
    remainder = 2 * power / ((2 * terms + 1) * (1 - z_squared))
    return outward_dyadic(2 * total, 2 * total + remainder)


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


def append_affine(
    coefficient: int,
    constant: int,
    denominator: int,
    block: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Apply ``block`` after the current affine map."""
    block_coefficient, block_constant, block_denominator = block
    return (
        block_coefficient * coefficient,
        block_coefficient * constant + block_constant * denominator,
        block_denominator * denominator,
    )


def least_positive_realization(coefficient: int, constant: int, denominator: int) -> tuple[int, int]:
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    source = residue or denominator
    endpoint_numerator = coefficient * source + constant
    if endpoint_numerator % denominator:
        raise AssertionError("least realization is not integral")
    return source, endpoint_numerator // denominator


def direct_word(value: int, word: str) -> int:
    current = value
    for bit in word:
        if current % 2 != int(bit):
            raise AssertionError("source does not realize stored parity word")
        current = current // 2 if bit == "0" else (3 * current + 1) // 2
    return current


def crt_pair(a: int, modulus_a: int, b: int, modulus_b: int) -> int:
    if modulus_a <= 0 or modulus_b <= 0:
        raise ValueError("CRT moduli must be positive")
    result = a % modulus_a
    result += modulus_a * (((b - result) * pow(modulus_a, -1, modulus_b)) % modulus_b)
    modulus = modulus_a * modulus_b
    return result or modulus


def c02_base_case(r: int, s: int) -> dict[str, object]:
    modulus_two = 16**s
    u_mod_two = 108 * pow(81**r, -1, modulus_two) % modulus_two
    u_mod_49 = 73 * pow(32**r, -1, 49) % 49
    u = crt_pair(u_mod_two, modulus_two, u_mod_49, 49)
    source_numerator = u * 32**r - 73
    if source_numerator % 49:
        raise AssertionError("base source congruence failed")
    source = source_numerator // 49
    after_a = (81**r * u - 73) // 49
    endpoint = after_a
    for _ in range(s):
        if (9 * endpoint + 5) % 16:
            raise AssertionError("base case does not realize B")
        endpoint = (9 * endpoint + 5) // 16
    p = 81**r * 9**s
    q = 32**r * 16**s
    margin = u * (q - p) - 108 * (16**s - 9**s)
    if not p < q or margin <= 0 or not endpoint < source:
        raise AssertionError("C02 base case did not descend")
    return {
        "r": r,
        "s": s,
        "u_congruence_mod_16s": u_mod_two,
        "u_congruence_mod_49": u_mod_49,
        "crt_modulus": 49 * modulus_two,
        "least_u": u,
        "least_source": source,
        "after_A_power": after_a,
        "endpoint": endpoint,
        "P": p,
        "Q": q,
        "C02_core_margin": margin,
        "source_descent_margin": source - endpoint,
        "all_realizations": f"u={u}+{49 * modulus_two}*t, t>=0",
    }


def c02_theorem_data() -> dict[str, object]:
    if affine_word(A_WORD) != A_MAP or affine_word(B_WORD) != B_MAP:
        raise AssertionError("A/B composition convention mismatch")
    bases = [c02_base_case(r, s) for r, s in BASE_CASES]

    exact_checks = {
        "r_ge_2_half_case": 2 * 32**2 > 108,
        "r1_s5_base": 5 * 16**5 > 54 * 9**5,
        "r1_equivalence_coefficients": [4 * 32 - 108, 4 * 81 - 108],
        "s_ge_2r_half_check": 2 * 6561**4 < 8192**4,
        "external_base_check": 2**40 > 7 * 5**16,
        "external_terminal_check": 7**4 > 54,
        "nu_minimum_check": 81**4 * 9**6 > 32**4 * 16**6,
    }
    if not all(value is True for key, value in exact_checks.items() if key.endswith("check") or key.endswith("case") or key.endswith("base")):
        raise AssertionError("C02 exact scalar check failed")
    if exact_checks["r1_equivalence_coefficients"] != [20, 216]:
        raise AssertionError("r=1 inequality equivalence mismatch")

    small_regimes = {
        "r1": {
            "noncontracting_boundary": [1, 1],
            "base_s": [2, 3, 4],
            "monotone_s_from": 5,
        },
        "r2": {
            "noncontracting_through_s": 3,
            "between_half_and_one_s": [4],
            "at_most_half_from_s": 5,
        },
        "r3": {
            "noncontracting_through_s": 4,
            "between_half_and_one_s": [5, 6],
            "at_most_half_from_s": 7,
        },
    }
    boundary_checks = [
        81 * 9 > 32 * 16,
        81**2 * 9**3 > 32**2 * 16**3,
        81**2 * 9**4 < 32**2 * 16**4 < 2 * 81**2 * 9**4,
        2 * 81**2 * 9**5 <= 32**2 * 16**5,
        81**3 * 9**4 > 32**3 * 16**4,
        32**3 * 16**5 < 2 * 81**3 * 9**5,
        32**3 * 16**6 < 2 * 81**3 * 9**6,
        2 * 81**3 * 9**7 <= 32**3 * 16**7,
    ]
    if not all(boundary_checks):
        raise AssertionError("small-r regime partition failed")

    return {
        "format": "collatz-phase8-c02-theorem-v1",
        "claim": {
            "id": "C02",
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For r,s>=1, every positive integral realization x of B^s(A^r(x)) descends whenever 3^(4r+2s)<2^(5r+4s).",
            "dependencies": ["exact affine algebra", "integrality congruences", "EXT05", "six exact base cases"],
        },
        "composition_convention": {
            "block_word": "A^r followed by B^s",
            "function": "F_(r,s)=B^s composed with A^r",
            "A": {"word": A_WORD, "map": list(A_MAP)},
            "B": {"word": B_WORD, "map": list(B_MAP)},
            "P": "81^r*9^s=3^(4r+2s)",
            "Q": "32^r*16^s=2^(5r+4s)",
        },
        "integrality_reduction": {
            "A_identity": "49*A(x)+73=(81/32)*(49*x+73)",
            "u_definition": "u=(49*x+73)/32^r",
            "A_power": "A^r(x)=(81^r*u-73)/49",
            "B_identity": "7*B(x)-5=(9/16)*(7*x-5)",
            "congruences": ["u*81^r=108 mod 16^s", "u*32^r=73 mod 49"],
            "valuation": "v2(u)=2",
            "lower_bound": "u>=4",
        },
        "sign_identity": {
            "left": "49*Q*(F_(r,s)(x)-x)",
            "right": "32^r*(u*(P-Q)+108*(16^s-9^s))",
            "core_equivalence": "F_(r,s)(x)<x iff u*(Q-P)>108*(16^s-9^s)",
        },
        "case_partition": {
            "r_ge_2_P_over_Q_at_most_half": {
                "proof": "u*(Q-P)>=4*(Q/2)=2Q>108*16^s>108*(16^s-9^s)",
                "minimum_scalar_check": [2 * 32**2, 108],
            },
            "r1_s_ge_5": {
                "equivalent_inequality": "20*16^s>216*9^s",
                "base_check_s5": [5 * 16**5, 54 * 9**5],
                "monotone_ratio": [16, 9],
            },
            "six_base_cases": bases,
            "small_regimes": small_regimes,
            "r_ge_4_between_half_and_one": {
                "s_strictly_below_2r": True,
                "s_ge_2r_contradiction": [2 * 6561**4, 8192**4],
                "minimum_nu": 30,
                "nu_minimum_witness_check": [81**4 * 9**6, 32**4 * 16**6],
                "external_lower_bound_after_dividing_16s": "(Q-P)/16^s > (1/2)*(2^40/5^16)^r > 7^r/2 > 27",
                "exact_power_check": [2**40, 7 * 5**16],
                "terminal_check": [7**4, 54],
            },
        },
        "external_input": {
            "id": "EXT05",
            "repository_status": "EXTERNAL_THEOREM",
            "source": "Rozier--Terracol (2026), Paradoxical behavior in Collatz sequences, arXiv:2502.00948v5, Lemma B.1",
            "statement": "for positive k,q with q>12, abs(2^k-3^q)>(64/25)^q/2",
            "application": {"kappa": "5r+4s", "nu": "4r+2s", "nu_greater_than_18": True},
            "finite_13_to_18_part_used": False,
            "paper_derivation": "q>18 case derived from Ellison (1971), Theorem 3",
        },
        "what_this_result_does_not_prove": "C02 does not cover arbitrary words over {A,B}, noncontracting A^rB^s prefixes, H54, H57, or the Collatz conjecture.",
        "proves_collatz": False,
    }


def phase7_dependencies(artifact_dir: Path) -> dict[str, object]:
    boundary_path = artifact_dir / "phase7_boundary_defect.json"
    correlation_path = artifact_dir / "phase7_contact_autocorrelation.json"
    boundary = json.loads(boundary_path.read_text(encoding="utf-8"))
    correlation = json.loads(correlation_path.read_text(encoding="utf-8"))
    contacts = int(boundary["contact_density"]["minimum_contact_count"])
    h12 = next(int(row["contact_pair_count_lower"]) for row in correlation["rows"] if int(row["h"]) == 12)
    if contacts != PHASE7_CONTACTS or h12 != PHASE7_H12_PAIRS:
        raise AssertionError("Phase 7 dependency values changed")
    return {
        "phase7_boundary_defect_sha256": sha256(boundary_path),
        "phase7_contact_autocorrelation_sha256": sha256(correlation_path),
        "minimum_contacts": contacts,
        "h12_nonwrapping_pairs": h12,
    }


def octave_bridge_data(artifact_dir: Path) -> dict[str, object]:
    dependencies = phase7_dependencies(artifact_dir)
    ln2_low, ln2_high = log_interval(2)
    eta_log_low, eta_log_high = log_interval(3 * V + Q0, 3 * V, terms=24)
    eta_low = eta_log_low / ln2_high
    eta_high = eta_log_high / ln2_low
    eta_low, eta_high = outward_dyadic(eta_low, eta_high)
    q_eta_upper = Q0 * eta_high
    if not q_eta_upper < 2:
        raise AssertionError("q0*eta bound did not close")
    maximum_exceptions = 5
    first_octave = PHASE7_CONTACTS - maximum_exceptions
    h12_pairs = PHASE7_H12_PAIRS - 2 * maximum_exceptions
    raw_short_gaps = (PHASE7_CONTACTS - 1) - (Q0 - 1) // 3
    qualified_short_gaps = raw_short_gaps - 2 * maximum_exceptions
    if (first_octave, h12_pairs, raw_short_gaps, qualified_short_gaps) != (
        31_327_720_457,
        889_748_819,
        7_308_576_465,
        7_308_576_455,
    ):
        raise AssertionError("octave numerical consequence changed")
    return {
        "format": "collatz-phase8-octave-bridge-v1",
        "P58": {
            "repository_status": "CONDITIONAL",
            "assumptions": ["least positive counterexample N", "first coefficient crossing", "d_j is the j-th odd position"],
            "definitions": {
                "R_j": "B_j/3^j=(1/3)*sum_(i<j) 2^(-theta_i-a_i)",
                "x_j": "T^(d_j)(N)",
            },
            "identities": [
                "x_j=2^(theta_j+a_j)*(N+R_j)",
                "R_(j+1)=R_j+(1/3)*2^(-theta_j-a_j)",
                "0<=R_j<=j/3",
                "2^a_j*N<=x_j<2^(a_j+1)*(N+j/3)",
            ],
            "proves_collatz": False,
        },
        "constants": {"q0": Q0, "K0": K0, "V": V},
        "eta": {
            "definition": "log2(1+q0/(3V))",
            "lower": encode_fraction(eta_low),
            "upper": encode_fraction(eta_high),
            "q0_times_eta_upper": encode_fraction(q_eta_upper),
            "q0_times_eta_strictly_below_2": True,
        },
        "exception_localization": {
            "statement": "a_j can differ from floor(log2(x_j/N)) only if fractional_part(j*log2(3)) lies in [1-eta,1)",
            "derivation": "x_j>=2^(a_j+1)N implies theta_j>=1-log2(1+R_j/N)>=1-eta",
        },
        "denjoy_koksma": {
            "dependency": "EXT04",
            "continued_fraction_denominator_blocks": list(CF_DENOMINATORS),
            "sum": sum(CF_DENOMINATORS),
            "indicator_circle_variation": 2,
            "error_per_block": 2,
            "total_error": 4,
            "maximum_integer_exception_count": maximum_exceptions,
        },
        "phase7_dependencies": dependencies,
        "E13": {
            "repository_status": "VERIFIED_FINITE",
            "conditional_dependencies": ["P58", "X02", "EXT04", "Phase 7 contact certificates"],
            "first_octave_odd_iterates_lower": first_octave,
            "h12_first_octave_pairs_lower": h12_pairs,
            "raw_consecutive_contact_gap_at_most_2_lower": raw_short_gaps,
            "first_octave_consecutive_contact_gap_at_most_2_lower": qualified_short_gaps,
            "exception_damage": {"contacts": 1, "h12_pairs_per_exception": 2, "adjacent_gaps_per_exception": 2},
        },
        "external_inputs": {
            "X02_N_greater_than_V_reproved": False,
            "EXT04_Denjoy_Koksma_reproved": False,
        },
        "what_this_result_does_not_prove": "The octave counts are conditional numerical consequences. They do not force descent, forbid all short-excursion concatenations, or prove Collatz.",
        "proves_collatz": False,
    }


def parity_residue_bruteforce(word: str) -> int:
    modulus = 1 << len(word)
    matches: list[int] = []
    for source in range(modulus):
        current = source
        valid = True
        for bit in word:
            if current % 2 != int(bit):
                valid = False
                break
            current = current // 2 if bit == "0" else (3 * current + 1) // 2
        if valid:
            matches.append(source)
    if len(matches) != 1:
        raise AssertionError("parity word did not select one residue")
    return matches[0]


def short_excursion_data(octave: dict[str, object]) -> dict[str, object]:
    rows = [
        {
            "name": "G1",
            "odd_gap": 1,
            "defects": [0, 0],
            "mechanical_increments": [1],
            "shortcut_gaps": [1],
            "word": "1",
            "word_with_endpoint_parity": "11",
            "map": [3, 1, 2],
            "source_interval": {"lower": [1, 0, 1, True], "upper": [4, -1, 3, False]},
        },
        {
            "name": "G2",
            "odd_gap": 1,
            "defects": [0, 0],
            "mechanical_increments": [2],
            "shortcut_gaps": [2],
            "word": "10",
            "word_with_endpoint_parity": "101",
            "map": [3, 1, 4],
            "source_interval": {"lower": [4, -1, 3, True], "upper": [2, 0, 1, False]},
        },
        {
            "name": "G3",
            "odd_gap": 2,
            "defects": [0, 1, 0],
            "mechanical_increments": [2, 1],
            "shortcut_gaps": [1, 2],
            "word": "110",
            "word_with_endpoint_parity": "1101",
            "map": [9, 5, 8],
            "source_interval": {"lower": [1, 0, 1, True], "upper": [16, -5, 9, False]},
        },
        {
            "name": "G4",
            "odd_gap": 2,
            "defects": [0, 1, 0],
            "mechanical_increments": [2, 2],
            "shortcut_gaps": [1, 3],
            "word": "1100",
            "word_with_endpoint_parity": "11001",
            "map": [9, 5, 16],
            "source_interval": {"lower": [16, -5, 9, True], "upper": [2, 0, 1, False]},
        },
    ]
    for row in rows:
        word = str(row["word"])
        if list(affine_word(word)) != row["map"]:
            raise AssertionError("short-excursion affine mismatch")
        full_word = str(row["word_with_endpoint_parity"])
        row["source_residue"] = parity_residue_bruteforce(full_word)
        row["source_modulus"] = 1 << len(full_word)
    e13 = octave["E13"]
    assert isinstance(e13, dict)
    return {
        "format": "collatz-phase8-short-excursions-v1",
        "repository_status": "VERIFIED_THEOREM",
        "defect_recurrence": "e_t=b_t+a_t-a_(t+1)",
        "consecutive_contact_gap_logic": {
            "gap_1": "a=(0,0), b in {1,2}",
            "gap_2": "a=(0,1,0), first b=2, second b in {1,2}",
        },
        "maps": rows,
        "first_octave_short_return_lower": e13["first_octave_consecutive_contact_gap_at_most_2_lower"],
        "what_this_result_does_not_prove": "The four exact maps do not provide a well-founded rank for arbitrary concatenations and do not prove Collatz.",
        "proves_collatz": False,
    }


SEMIGROUP_FIELDS = [
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


def semigroup_row(
    row_id: int,
    block_word: str,
    shortcut_word: str,
    coefficient: int,
    constant: int,
    denominator: int,
) -> list[object]:
    source, endpoint = least_positive_realization(coefficient, constant, denominator)
    if direct_word(source, shortcut_word) != endpoint:
        raise AssertionError("semigroup direct realization mismatch")
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
        49 * source + 73,
        49 * endpoint + 73,
    ]


def enumerate_contracting_words(max_length: int) -> tuple[list[list[object]], list[int]]:
    states = [("", "", 1, 0, 1)]
    records: list[list[object]] = []
    counts: list[int] = []
    for _length in range(1, max_length + 1):
        next_states: list[tuple[str, str, int, int, int]] = []
        count = 0
        for block_word, shortcut_word, coefficient, constant, denominator in states:
            for name, bits, block_map in (("A", A_WORD, A_MAP), ("B", B_WORD, B_MAP)):
                new_coefficient, new_constant, new_denominator = append_affine(
                    coefficient, constant, denominator, block_map
                )
                state = (
                    block_word + name,
                    shortcut_word + bits,
                    new_coefficient,
                    new_constant,
                    new_denominator,
                )
                next_states.append(state)
                if new_coefficient < new_denominator:
                    records.append(semigroup_row(len(records), *state))
                    count += 1
        counts.append(count)
        states = next_states
    return records, counts


def enumerate_first_crossings(max_length: int) -> tuple[list[list[object]], list[int]]:
    active = [("", "", 1, 0, 1)]
    records: list[list[object]] = []
    counts: list[int] = []
    for _length in range(1, max_length + 1):
        next_active: list[tuple[str, str, int, int, int]] = []
        count = 0
        for block_word, shortcut_word, coefficient, constant, denominator in active:
            for name, bits, block_map in (("A", A_WORD, A_MAP), ("B", B_WORD, B_MAP)):
                state = (
                    block_word + name,
                    shortcut_word + bits,
                    *append_affine(coefficient, constant, denominator, block_map),
                )
                if int(state[2]) < int(state[4]):
                    records.append(semigroup_row(len(records), *state))
                    count += 1
                else:
                    next_active.append(state)
        counts.append(count)
        active = next_active
    return records, counts


def adversarial_audit(phase7_macro_path: Path) -> dict[str, object]:
    minus_one = []
    for m in range(1, 65):
        source = (1 << m) - 1
        current = source
        bits = []
        for _ in range(m):
            bits.append(str(current % 2))
            current = (3 * current + 1) // 2
        if "".join(bits) != "1" * m:
            raise AssertionError("2^m-1 regression failed")
        minus_one.append(m)
    minus_five = []
    for m in range(1, 33):
        source = (1 << (3 * m)) - 5
        current = source
        bits = []
        for _ in range(3 * m):
            bits.append(str(current % 2))
            current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2
        if "".join(bits) != "110" * m:
            raise AssertionError("8^m-5 regression failed")
        minus_five.append(m)
    safe_language = 0
    for mask in range(1 << 12):
        word = "".join("111" if (mask >> index) & 1 else "110" for index in range(12))
        odd = 0
        safe = True
        for depth, bit in enumerate(word, start=1):
            odd += bit == "1"
            if 3**odd < 2**depth:
                safe = False
                break
        safe_language += safe
    if safe_language != 1 << 12:
        raise AssertionError("(110|111)^* regression failed")
    mixed_pairs = 0
    contracting_pairs = 0
    noncontracting_safe_prefixes = 0
    closest_above: tuple[Fraction, int, int] | None = None
    for r in range(1, 65):
        for s in range(1, 65):
            mixed_pairs += 1
            coefficient = 81**r * 9**s
            denominator = 32**r * 16**s
            if coefficient < denominator:
                contracting_pairs += 1
            else:
                # A raises the coefficient at every block boundary; each B
                # lowers it.  If the final boundary is still at least one,
                # every earlier block boundary and every interior shortcut
                # prefix is coefficient-safe.
                noncontracting_safe_prefixes += 1
                excess = Fraction(coefficient - denominator, denominator)
                if closest_above is None or excess < closest_above[0]:
                    closest_above = (excess, r, s)
    if mixed_pairs != 4096 or closest_above is None:
        raise AssertionError("A^rB^s bounded adversarial audit failed")
    macro = json.loads(phase7_macro_path.read_text(encoding="utf-8"))
    schema = macro["record_schema"]
    first = dict(zip(schema, macro["records"][0], strict=True))
    if first["binary_parity_word"] != PHASE7_MACRO0:
        raise AssertionError("Phase 7 macro id 0 changed")
    return {
        "2^m_minus_1": {"scope": "1<=m<=64", "verified_prefix": "1^m"},
        "8^m_minus_5": {"scope": "1<=m<=32", "verified_prefix": "(110)^m"},
        "(110|111)^star": {"block_length": 12, "words_checked": safe_language, "all_coefficient_safe": True},
        "A": {"word": A_WORD, "map": list(A_MAP)},
        "B": {"word": B_WORD, "map": list(B_MAP)},
        "A^rB^s": {
            "scope": "1<=r,s<=64",
            "pairs_checked": mixed_pairs,
            "contracting_pairs": contracting_pairs,
            "contracting_case": "covered universally by C02",
            "noncontracting_coefficient_safe_prefixes": noncontracting_safe_prefixes,
            "closest_multiplier_above_one": {
                "r": closest_above[1],
                "s": closest_above[2],
                "excess": encode_fraction(closest_above[0]),
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


def semigroup_data(artifact_dir: Path, contracting_max_length: int, crossing_max_length: int) -> dict[str, object]:
    contracting, contracting_counts = enumerate_contracting_words(contracting_max_length)
    crossings, crossing_counts = enumerate_first_crossings(crossing_max_length)
    counterexamples = [row for row in contracting if int(row[10]) >= int(row[9])]
    mixed = [row for row in contracting if int(row[4]) > 0 and int(row[5]) > 0]
    minimum = min(contracting, key=lambda row: (int(row[11]), int(row[1]), str(row[2])))
    mixed_minimum = min(mixed, key=lambda row: (int(row[11]), int(row[1]), str(row[2])))
    if contracting_max_length == 18 and (len(contracting), len(mixed)) != (79_184, 79_166):
        raise AssertionError(
            f"contracting-word sanity count changed: all={len(contracting)}, mixed={len(mixed)}"
        )
    expected_crossing = {1: 1, 3: 1, 6: 2, 8: 7, 11: 23, 14: 99, 16: 476, 19: 1966, 21: 9690}
    if crossing_max_length == 22:
        observed = {index + 1: count for index, count in enumerate(crossing_counts) if count}
        if observed != expected_crossing or len(crossings) != 12_265:
            raise AssertionError(f"block-boundary crossing counts changed: {observed}")
    return {
        "format": "collatz-phase8-ab-semigroup-v1",
        "coordinate": {
            "definition": "U=49x+73",
            "A": "U=32u -> U'=81u",
            "B": "U=16u+108 -> U'=9u+108",
            "invariant": "U=73 mod 49",
        },
        "C03": {
            "repository_status": "OPEN",
            "statement": "Every positive integral realization of every finite W in {A,B}* with multiplier below one has endpoint below its source.",
            "proved": False,
        },
        "contracting_search": {
            "repository_status": "VERIFIED_FINITE",
            "maximum_block_length": contracting_max_length,
            "record_schema": SEMIGROUP_FIELDS,
            "counts_by_exact_length": contracting_counts,
            "records": contracting,
            "total": len(contracting),
            "mixed_total": len(mixed),
            "pure_B_words_included": contracting_max_length,
            "counterexamples": counterexamples,
            "minimum_descent_margin_record": dict(zip(SEMIGROUP_FIELDS, minimum, strict=True)),
            "minimum_mixed_descent_margin_record": dict(
                zip(SEMIGROUP_FIELDS, mixed_minimum, strict=True)
            ),
        },
        "first_crossing_search": {
            "repository_status": "VERIFIED_FINITE",
            "scope_note": "safe only at A/B block boundaries, not every shortcut step",
            "maximum_block_length": crossing_max_length,
            "record_schema": SEMIGROUP_FIELDS,
            "counts_by_exact_length": crossing_counts,
            "records": crossings,
            "total": len(crossings),
        },
        "mandatory_adversarial_audit": adversarial_audit(artifact_dir / "phase7_macro12.json"),
        "what_this_result_does_not_prove": "No counterexample in a bounded A/B search does not prove C03, does not identify block-boundary safety with shortcut safety, and does not prove Collatz.",
        "proves_collatz": False,
    }


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_obstruction_report(
    path: Path,
    c02: dict[str, object],
    octave: dict[str, object],
    short: dict[str, object],
    semigroup: dict[str, object],
) -> None:
    c03_search = semigroup["contracting_search"]
    crossing = semigroup["first_crossing_search"]
    e13 = octave["E13"]
    assert isinstance(c03_search, dict) and isinstance(crossing, dict) and isinstance(e13, dict)
    minimum = c03_search["minimum_descent_margin_record"]
    mixed_minimum = c03_search["minimum_mixed_descent_margin_record"]
    assert isinstance(minimum, dict) and isinstance(mixed_minimum, dict)
    lines = [
        "# Phase 8 obstruction report",
        "",
        "This report does not claim a proof of the Collatz conjecture.",
        "",
        "## VERIFIED_THEOREM",
        "",
        "- C02 is closed for every r,s>=1 by exact algebra, six CRT base cases, and EXT05 in the remaining Diophantine regime.",
        "- The four consecutive-contact short-excursion maps are reconstructed exactly.",
        "",
        "## CONDITIONAL / VERIFIED_FINITE consequences",
        "",
        f"- At most `{octave['denjoy_koksma']['maximum_integer_exception_count']}` defect/octave exceptions occur under P58, X02, and EXT04.",
        f"- At least `{e13['first_octave_odd_iterates_lower']}` odd iterates, `{e13['h12_first_octave_pairs_lower']}` h=12 pairs, and `{e13['first_octave_consecutive_contact_gap_at_most_2_lower']}` short consecutive returns lie in the first octave.",
        "",
        "## EXTERNAL_THEOREM / EXTERNAL_EVIDENCE",
        "",
        "- EXT05 is Rozier--Terracol v5, Lemma B.1; its q>18 derivation uses Ellison. Phase 8 does not use the paper's finite q=13..18 check.",
        "- EXT04 (Denjoy--Koksma) and X02 (N>V) remain external and are not reproved.",
        "",
        "## OPEN",
        "",
        f"- C03 has no counterexample among `{c03_search['total']}` contracting A/B words through block length `{c03_search['maximum_block_length']}`; `{c03_search['mixed_total']}` of them contain both A and B.",
        f"- The all-word minimum descent margin is `{minimum['descent_margin']}` at pure word `{minimum['block_word']}`; the mixed-word minimum is `{mixed_minimum['descent_margin']}` at `{mixed_minimum['block_word']}`.",
        f"- The separate block-boundary first-crossing search retains `{crossing['total']}` words through length `{crossing['maximum_block_length']}`.",
        "",
        "## Main obstruction",
        "",
        "C02 closes the ordered A^rB^s family, but no common well-founded potential or transition theorem was found for arbitrary interleavings in {A,B}*. The octave bridge forces many short returns inside [N,2N), yet the four-map alphabet alone has no proved global frequency or rank constraint.",
        "",
        "## What this result does not prove",
        "",
        "It does not prove C03, H54, H57, exclude all hypothetical least-counterexample paths, or prove the Collatz conjecture.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(
    artifact_dir: Path,
    *,
    contracting_max_length: int = 18,
    crossing_max_length: int = 22,
) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    c02 = c02_theorem_data()
    octave = octave_bridge_data(artifact_dir)
    short = short_excursion_data(octave)
    semigroup = semigroup_data(artifact_dir, contracting_max_length, crossing_max_length)
    write_json(artifact_dir / "phase8_c02_theorem.json", c02)
    write_json(artifact_dir / "phase8_octave_bridge.json", octave)
    write_json(artifact_dir / "phase8_short_excursions.json", short)
    write_json(artifact_dir / "phase8_ab_semigroup_search.json", semigroup)
    write_obstruction_report(artifact_dir / "phase8_obstruction_report.md", c02, octave, short, semigroup)
    return {
        "C02": "VERIFIED_THEOREM",
        "C03": "OPEN",
        "maximum_octave_exceptions": octave["denjoy_koksma"]["maximum_integer_exception_count"],
        "first_octave_odd_iterates": octave["E13"]["first_octave_odd_iterates_lower"],
        "contracting_words": semigroup["contracting_search"]["total"],
        "crossing_words": semigroup["first_crossing_search"]["total"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--contracting-max-length", type=int, default=18)
    parser.add_argument("--crossing-max-length", type=int, default=22)
    args = parser.parse_args()
    if args.contracting_max_length < 1 or args.crossing_max_length < 1:
        parser.error("search lengths must be positive")
    result = generate(
        args.artifact_dir,
        contracting_max_length=args.contracting_max_length,
        crossing_max_length=args.crossing_max_length,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
