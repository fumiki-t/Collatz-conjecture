#!/usr/bin/env python3
"""Generate exact Phase 22 cycle-profile and resultant evidence.

The supplied Phase 22 note is a proposal, not an authority.  Every finite
acceptance decision below uses integers or fractions.  Decimal values are not
used.
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


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


V = 300_000
A_BITS = "11101"
B_BITS = "1100"
NEGATIVE_Q7 = (1, 1, 1, 2, 1, 1, 4)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_digest(rows: object) -> str:
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def frac(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for cuts in itertools.combinations(range(1, total), parts - 1):
        points = (0,) + cuts + (total,)
        yield tuple(points[index + 1] - points[index] for index in range(parts))


def rotations(values: tuple[int, ...]):
    for offset in range(len(values)):
        yield values[offset:] + values[:offset]


def cyclic_class(values: tuple[int, ...]) -> tuple[int, ...]:
    return min(rotations(values))


def prefix_heights(exponents: tuple[int, ...]) -> tuple[int, ...]:
    q = len(exponents)
    L = sum(exponents)
    height = 0
    answer = []
    for exponent in exponents:
        answer.append(height)
        height += q * exponent - L
    if height != 0:
        raise AssertionError("closed height path")
    return tuple(answer)


def minimum_height_rotation(exponents: tuple[int, ...]) -> tuple[int, ...]:
    candidates = []
    for rotated in rotations(exponents):
        heights = prefix_heights(rotated)
        if min(heights) == 0:
            candidates.append(rotated)
    if not candidates:
        raise AssertionError("cycle lemma found no minimum rotation")
    if math.gcd(len(exponents), sum(exponents)) == 1 and len(candidates) != 1:
        raise AssertionError("coprime minimum rotation is not unique")
    return min(candidates)


def profile_of(exponents: tuple[int, ...]) -> tuple[int, ...]:
    q = len(exponents)
    L = sum(exponents)
    if math.gcd(q, L) != 1:
        raise ValueError("coprime profile requested for noncoprime slope")
    canonical = minimum_height_rotation(exponents)
    answer = [-1] * q
    for height in prefix_heights(canonical):
        residue = height % q
        answer[residue] = (height - residue) // q
    if answer[0] != 0 or min(answer) < 0 or -1 in answer:
        raise AssertionError("invalid canonical profile")
    return tuple(answer)


def exponents_of_profile(q: int, L: int, profile: tuple[int, ...]) -> tuple[int, ...] | None:
    if len(profile) != q or profile[0] != 0 or min(profile) < 0 or math.gcd(q, L) != 1:
        return None
    heights = []
    for index in range(q):
        residue = (-L * index) % q
        heights.append(residue + q * profile[residue])
    answer = []
    for index in range(q):
        next_height = heights[index + 1] if index + 1 < q else 0
        numerator = next_height - heights[index] + L
        if numerator % q:
            return None
        exponent = numerator // q
        if exponent < 1:
            return None
        answer.append(exponent)
    result = tuple(answer)
    if profile_of(result) != profile:
        return None
    return result


def affine_correction(exponents: tuple[int, ...]) -> int:
    affine = 0
    power = 0
    q = len(exponents)
    for index, exponent in enumerate(exponents):
        affine += 3 ** (q - 1 - index) * 2**power
        power += exponent
    return affine


def v2(value: int) -> int:
    if not value:
        raise ValueError("v2(0)")
    value = abs(value)
    return (value & -value).bit_length() - 1


def literal_accelerated_cycle(source: int, exponents: tuple[int, ...]) -> tuple[bool, list[int]]:
    values = [source]
    current = source
    for exponent in exponents:
        numerator = 3 * current + 1
        if v2(numerator) != exponent:
            return False, values
        current = numerator // 2**exponent
        values.append(current)
    return current == source, values


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


def modular_power(base: int, exponent: int, modulus: int) -> int:
    if exponent >= 0:
        return pow(base, exponent, modulus)
    return pow(pow(base, -1, modulus), -exponent, modulus)


def slope_root(q: int, L: int, modulus: int) -> int:
    gcd, u, v = extended_gcd(q, L)
    if gcd != 1 or modulus <= 1:
        raise ValueError("slope root requires coprime slope and modulus > 1")
    return modular_power(2, u, modulus) * modular_power(3, v, modulus) % modulus


def bareiss(matrix: list[list[int]]) -> int:
    work = [row[:] for row in matrix]
    size = len(work)
    sign = 1
    previous = 1
    for pivot_index in range(size - 1):
        pivot_row = next((row for row in range(pivot_index, size) if work[row][pivot_index]), None)
        if pivot_row is None:
            return 0
        if pivot_row != pivot_index:
            work[pivot_index], work[pivot_row] = work[pivot_row], work[pivot_index]
            sign *= -1
        pivot = work[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for column in range(pivot_index + 1, size):
                numerator = work[row][column] * pivot - work[row][pivot_index] * work[pivot_index][column]
                if numerator % previous:
                    raise AssertionError("non-exact Bareiss division")
                work[row][column] = numerator // previous
            work[row][pivot_index] = 0
        previous = pivot
    return sign * work[-1][-1]


def multiplication_resultant(profile: tuple[int, ...]) -> int:
    q = len(profile)
    coefficients = [2**entry for entry in profile]
    matrix = [[0] * q for _ in range(q)]
    for column in range(q):
        for exponent, coefficient in enumerate(coefficients):
            total = exponent + column
            matrix[total % q][column] += coefficient * (2 if total >= q else 1)
    return bareiss(matrix)


def energy_coefficients(profile: tuple[int, ...]) -> tuple[int, ...]:
    b = [2**entry - 1 for entry in profile]
    return (1 + 2 * b[-1],) + tuple(b[index - 1] - b[index] for index in range(1, len(b)))


def upper_qth_root_four(q: int, bits: int = 48) -> Fraction:
    denominator = 1 << bits
    low, high = denominator, 4 * denominator
    target = 4 * denominator**q
    while high - low > 1:
        middle = (low + high) // 2
        if middle**q < target:
            low = middle
        else:
            high = middle
    result = Fraction(high, denominator)
    if result**q < 4 or Fraction(high - 1, denominator) ** q >= 4:
        raise AssertionError("radial root enclosure")
    return result


def certified_energy(profile: tuple[int, ...], D: int) -> tuple[Fraction, bool]:
    upper = upper_qth_root_four(len(profile))
    energy = sum(coefficient * coefficient * upper**index for index, coefficient in enumerate(energy_coefficients(profile)))
    return energy, energy**len(profile) < D * D


def minimum_correction(exponents: tuple[int, ...]) -> int:
    return min(affine_correction(rotated) for rotated in rotations(exponents))


def profile_row(q: int, L: int, profile: tuple[int, ...]) -> list[object]:
    exponents = exponents_of_profile(q, L, profile)
    if exponents is None:
        raise ValueError("invalid profile row")
    D = 2**L - 3**q
    B = affine_correction(exponents)
    c_min = minimum_correction(exponents)
    energy, energy_excluded = certified_energy(profile, D)
    return [
        q, L, list(profile), list(exponents), sum(profile), B, D, B % D == 0,
        c_min, c_min < V * D, energy_excluded, str(energy.numerator), str(energy.denominator),
    ]


def profiles_of_area(q: int, area: int):
    if q == 1:
        if area == 0:
            yield (0,)
        return
    for bars in itertools.combinations_with_replacement(range(1, q), area):
        values = [0] * q
        for index in bars:
            values[index] += 1
        yield tuple(values)


def finite_profiles() -> tuple[dict[str, object], list[tuple[int, int, tuple[int, ...]]]]:
    full_rows = []
    full_raw = 0
    full_coprime = 0
    full_noncoprime = 0
    full_integral = []
    profile_keys: set[tuple[int, int, tuple[int, ...]]] = set()
    full_profile_keys: set[tuple[int, int, tuple[int, ...]]] = set()
    for q in range(1, 9):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            classes = set()
            for exponents in compositions(L, q):
                full_raw += 1
                classes.add(cyclic_class(exponents))
            for exponents in sorted(classes):
                D = 2**L - 3**q
                distinct_rotations = tuple(dict.fromkeys(rotations(exponents)))
                B_values = [affine_correction(rotated) for rotated in distinct_rotations]
                divides = any(value % D == 0 for value in B_values)
                if divides:
                    witnesses = []
                    for rotated, B in zip(distinct_rotations, B_values):
                        if B % D == 0:
                            source = B // D
                            legal, values = literal_accelerated_cycle(source, rotated)
                            witnesses.append([list(rotated), source, legal, values])
                    full_integral.append([q, L, list(exponents), witnesses])
                if math.gcd(q, L) == 1:
                    profile = profile_of(exponents)
                    profile_keys.add((q, L, profile))
                    full_profile_keys.add((q, L, profile))
                    full_coprime += 1
                    full_rows.append([q, L, list(exponents), list(profile), sum(profile), min(B_values), D, divides])
                else:
                    full_noncoprime += 1
                    full_rows.append([q, L, list(exponents), None, None, min(B_values), D, divides])

    area_rows = []
    by_area: dict[int, dict[str, int]] = {}
    for q in range(1, 23):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q or math.gcd(q, L) != 1:
                continue
            for area in range(3):
                for profile in profiles_of_area(q, area):
                    if exponents_of_profile(q, L, profile) is None:
                        continue
                    key = (q, L, profile)
                    profile_keys.add(key)
                    row = profile_row(*key)
                    area_rows.append(row)
                    counters = by_area.setdefault(area, {"valid": 0, "energy_excluded": 0, "source_excluded": 0, "combined_excluded": 0, "uncovered": 0, "integral": 0})
                    counters["valid"] += 1
                    counters["energy_excluded"] += int(row[10])
                    counters["source_excluded"] += int(row[9])
                    counters["combined_excluded"] += int(row[9] or row[10])
                    counters["uncovered"] += int(not row[9] and not row[10])
                    counters["integral"] += int(row[7])

    area_rows.sort(key=lambda row: (row[0], row[1], row[4], row[2]))
    uncovered = [row for row in area_rows if not row[9] and not row[10]]
    unique_keys = sorted(profile_keys)
    larger_keys = sorted(profile_keys - full_profile_keys)
    larger_sample = list(dict.fromkeys(larger_keys[:256] + larger_keys[-256:]))
    sample_keys = sorted(full_profile_keys) + larger_sample
    resultant_rows = []
    for q, L, profile in sample_keys:
        D = 2**L - 3**q
        exponents = exponents_of_profile(q, L, profile)
        if exponents is None:
            raise AssertionError("sample profile invalid")
        B = affine_correction(exponents)
        resultant = multiplication_resultant(profile)
        gamma_checks = None
        if D > 1:
            gamma = slope_root(q, L, D)
            polynomial = sum(2**value * pow(gamma, index, D) for index, value in enumerate(profile)) % D
            gamma_checks = [gamma, pow(gamma, q, D), pow(gamma, L, D), polynomial]
            if gamma_checks[1:3] != [2 % D, 3 % D] or (polynomial == 0) != (B % D == 0):
                raise AssertionError("slope-root equivalence")
        if B % D == 0 and resultant % D:
            raise AssertionError("resultant divisibility")
        resultant_rows.append([q, L, list(profile), B, D, resultant, gamma_checks])

    artifact = {
        "format": "collatz-phase22-finite-profiles-v1",
        "claims": {"E34": "VERIFIED_FINITE", "H133": "OPEN"},
        "full_composition_scope": {"q_maximum": 8, "q_lt_L_le_2q": True, "D_positive": True},
        "full_raw_compositions": full_raw,
        "full_cyclic_classes": len(full_rows),
        "full_coprime_classes": full_coprime,
        "full_noncoprime_classes": full_noncoprime,
        "full_integral_classes": full_integral,
        "full_row_digest_sha256": stable_digest(full_rows),
        "full_row_storage": "omitted; verifier independently rebuilds all exponent compositions and cyclic classes",
        "area_scope": {"q_maximum": 22, "maximum_area": 2, "q_lt_L_le_2q": True, "D_positive": True, "coprime_only": True},
        "area_profile_count": len(area_rows),
        "area_counts": {str(key): value for key, value in sorted(by_area.items())},
        "area_row_digest_sha256": stable_digest(area_rows),
        "area_row_storage": "omitted; verifier independently rebuilds every valid profile",
        "smallest_combined_uncovered_profile": uncovered[0] if uncovered else None,
        "combined_uncovered_count": len(uncovered),
        "resultant_sample_rule": "every coprime class in the complete q<=8 scope, plus the lexicographically first 256 and last 256 additional profiles from the larger area-bounded scope",
        "resultant_sample_count": len(resultant_rows),
        "resultant_samples": resultant_rows,
        "energy_certificate": "If U is the least 48-bit dyadic upper bound for 4^(1/q), E_U=sum d_r^2 U^r and E_U^q<D^2, then E_q(a)^(q/2)<D.",
        "source_certificate": "C_min<300000*D contradicts the verified N<300000 convergence interval for a nontrivial positive cycle minimum.",
        "finite_boundary": "The complete q<=8 and area<=2,q<=22 audits do not cover all positive cycle profiles.",
        "proves_collatz": False,
    }
    return artifact, unique_keys


def log_bounds(value: Fraction, terms: int = 24) -> tuple[Fraction, Fraction]:
    if value < 1:
        raise ValueError("log enclosure domain")
    z = (value - 1) / (value + 1)
    z2 = z * z
    power = z
    partial = Fraction()
    for index in range(terms):
        partial += power / (2 * index + 1)
        power *= z2
    lower = 2 * partial
    upper = lower + 2 * power / ((2 * terms + 1) * (1 - z2))
    return lower, upper


def theory_artifact() -> dict[str, object]:
    ln2_lower, ln2_upper = log_bounds(Fraction(2))
    ln_ratio_lower, ln_ratio_upper = log_bounds(Fraction(511, 256))
    ln511_upper = 8 * ln2_upper + ln_ratio_upper
    g170_margin = ln2_lower - Fraction(1, V) - ln511_upper / 9
    if g170_margin <= 0:
        raise AssertionError("G170 exact logarithm certificate")
    exact_checks = {
        "g170_log_margin": frac(g170_margin),
        "ln2_lower": frac(ln2_lower),
        "ln2_upper": frac(ln2_upper),
        "ln_511_over_256_upper": frac(ln_ratio_upper),
        "critical_root_check": 4 * 8**13 < 9**13,
        "critical_resultant_check": 4 * 115625**13 < 131072**13,
        "noncritical_q4_check": 2 * 11**2 < 18**2,
    }
    if not all(value is True for key, value in exact_checks.items() if key.endswith("_check")):
        raise AssertionError("area-one exact constant")
    return {
        "format": "collatz-phase22-theory-v1",
        "claims": {
            "P133": {"status": "VERIFIED_THEOREM", "statement": "At a primitive positive cycle minimum, every proper full-shortcut prefix coefficient exceeds lambda, and m(1-lambda)<q/3."},
            "P134": {"status": "VERIFIED_THEOREM", "statement": "Every nontrivial primitive positive cycle satisfies q>170m or lambda>1/2 and L=ceil(q log2 3).", "dependencies": ["P72 finite packing argument", "E28"]},
            "P135": {"status": "VERIFIED_THEOREM", "statement": "For gcd(L,q)=1, cyclic exponent classes correspond to valid residue-indexed nonnegative profiles, and D|B iff A_a(gamma)=0 mod D."},
            "P136": {"status": "VERIFIED_THEOREM", "statement": "A coprime area-zero profile yields only (q,L)=(1,2), the trivial positive cycle."},
            "P137": {"status": "VERIFIED_THEOREM", "statement": "D divides the nonzero resultant for every integral coprime profile, while the resultant magnitude is at most the q/2 power of its radial energy."},
            "P138": {"status": "VERIFIED_THEOREM", "statement": "Every positive coprime area-one profile is excluded; the critical q>=13 part depends on EXT05, while noncritical q>=4 is internal and all smaller cases are exact finite checks."},
            "P139": {"status": "CONDITIONAL", "statement": "Under EXT15, every non-Christoffel coprime class has C_min<=C_chr-g with g>3^(q-1)/4."},
            "P140": {"status": "VERIFIED_THEOREM", "statement": "For gcd(L,q)=d>1, D0=2^(L/d)-3^(q/d) divides D and an integral word obeys a grouped degree-(q/d-1) modular polynomial and resultant condition."},
            "H133": {"status": "OPEN", "statement": "Exclude every remaining positive nontrivial cycle profile, including larger-area coprime and general noncoprime profiles."},
        },
        "map": "odd accelerated x_(i+1)=(3*x_i+1)/2^e_i with exact e_i=v2(3*x_i+1)",
        "affine_identity": "2^L*x_q=3^q*x_0+B, B=sum_(j<q)3^(q-1-j)2^E_j, D=2^L-3^q",
        "integrality_legality": "For D>0, D|B makes x=B/D an odd integer; the unique parity cylinder modulo 2^L then forces the literal exponent word. Primitive period is checked separately.",
        "profile_orientation": "Rotate to the unique minimum of H_j=qE_j-Lj; profile indices are residues r=H_j mod q, not time indices j.",
        "slope_root": "For uq+vL=1, gamma=2^u3^v mod D satisfies gamma^q=2 and gamma^L=3; negative powers mean modular inverses.",
        "resultant_convention": "Res(X^q-2,A_a); X^q-2 is Eisenstein at 2, so the resultant is nonzero because deg(A_a)<q.",
        "energy_coefficients": "d_0=1+2(2^a_(q-1)-1), d_r=(2^a_(r-1)-1)-(2^a_r-1)",
        "area_one_validity": "a_s=1 is valid exactly only among recovered positive exponent words; necessarily 1<=s<=L-q-1.",
        "external_bound": "EXT05 is used only on the critical cancellation line q>12; no repository reproof of Lemma B.1 is claimed.",
        "exact_checks": exact_checks,
        "noncoprime_boundary": "P140 is only a weaker necessary condition modulo D0; it is not a bijective coprime profile theorem and does not eliminate the noncoprime branch.",
        "what_this_result_does_not_prove": "It does not exclude all positive nontrivial cycles, H89, H112, H72, or prove Collatz.",
        "proves_collatz": False,
    }


def word_exponents(word: str) -> tuple[int, ...]:
    if not word or set(word) - {"0", "1"} or "1" not in word:
        raise ValueError("nonempty cyclic binary word with a one required")
    offset = word.index("1")
    rotated = word[offset:] + word[:offset]
    positions = [index for index, bit in enumerate(rotated) if bit == "1"]
    return tuple((positions[(index + 1) % len(positions)] - position) % len(word) or len(word) for index, position in enumerate(positions))


def regression_row(name: str, exponents: tuple[int, ...]) -> dict[str, object]:
    q, L = len(exponents), sum(exponents)
    D = 2**L - 3**q
    B = affine_correction(exponents)
    source = B // D if D and B % D == 0 else None
    legal = None
    values = None
    if source is not None:
        legal, values = literal_accelerated_cycle(source, exponents)
    result = None
    profile = None
    if math.gcd(q, L) == 1:
        canonical = minimum_height_rotation(exponents)
        profile = profile_of(canonical)
        result = multiplication_resultant(profile)
    return {
        "name": name, "exponents": list(exponents), "q": q, "L": L, "D": D, "B": B,
        "integral_source": source, "literal_legal": legal, "orbit_values": values,
        "coprime_profile": list(profile) if profile is not None else None,
        "resultant": result, "D_divides_resultant": None if result is None or D == 0 else result % abs(D) == 0,
    }


def regressions_artifact() -> dict[str, object]:
    named = [
        regression_row("trivial-positive", (2,)),
        regression_row("negative-q2-L3", (1, 2)),
        regression_row("negative-q7-L11-D-139", NEGATIVE_Q7),
        regression_row("A=11101", word_exponents(A_BITS)),
        regression_row("B=1100", word_exponents(B_BITS)),
    ]
    for r in range(1, 5):
        for s in range(1, 5):
            named.append(regression_row(f"A^{r}B^{s}", word_exponents(A_BITS * r + B_BITS * s)))
    named.extend([
        regression_row("(110)^4", word_exponents("110" * 4)),
        regression_row("(111)^4", word_exponents("111" * 4)),
        regression_row("mixed-(110|111)", word_exponents("110111110111")),
        regression_row("legacy-macro-id0", word_exponents("1111111111110000000")),
        regression_row("legacy-NG28-short", word_exponents("111111111101111110101011110010001001100")),
        regression_row("legacy-NG28-long", word_exponents("1101101101110011100111011101010101101101")),
        regression_row("legacy-NG30-k2", word_exponents("11111011111100000")),
        regression_row("legacy-NG30-k3", word_exponents("11111110111111110000000")),
        regression_row("legacy-NG30-k4", word_exponents("111111111001111111111000000000")),
    ])
    numeric = []
    for family in ("2^m-1", "8^m-5"):
        for m in range(2, 13):
            source = 2**m - 1 if family == "2^m-1" else 8**m - 5
            current = source
            seen = set()
            steps = 0
            while steps < 256 and current not in seen and current != 1:
                seen.add(current)
                current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2
                steps += 1
            numeric.append([family, m, source, steps, current, current == 1])
    q7 = named[2]
    if q7["D"] != -139 or q7["integral_source"] != -17 or not q7["literal_legal"] or not q7["D_divides_resultant"]:
        raise AssertionError("negative q=7 regression")
    if named[0]["integral_source"] != 1 or not named[0]["literal_legal"]:
        raise AssertionError("trivial positive regression")
    return {
        "format": "collatz-phase22-regressions-v1",
        "named_cycle_words": named,
        "numeric_prefix_controls": numeric,
        "scope_repairs": {
            "negative_cycles": "They test algebraic signs and divisibility only and are never classified as positive cycles.",
            "mandatory_families": "A/B and (110|111) words test cyclic exponent conversion; 2^m-1 and 8^m-5 are finite orbit controls, not proposed cycles.",
            "legacy_controls": "Macro id0 and explicit NG28/NG30 words are converted only as cyclic-algebra diagnostics. Their original noncycle carry/graph meanings remain preserved and they are not classified as odd cycles.",
        },
        "proves_collatz": False,
    }


def literature_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase22-literature-v1",
        "claims": {"EXT15": "EXTERNAL_THEOREM", "EXT16": "EXTERNAL_THEOREM", "EXT05": "EXTERNAL_THEOREM"},
        "sources": [
            {
                "id": "EXT15", "authors": "Carlos Fernández and Santiago Ibáñez", "title": "Christoffel Words as Extremal Structures in Collatz Dynamics", "year": 2026,
                "source": "arXiv:2607.24844v1", "used_result": "Proposition 5.2 local 10-to-01 correction increment and Theorem 7.3 unique Christoffel maximizer of C_min up to cyclic conjugacy.",
                "orientation": "Their word has N positions and r ones; the lower Christoffel representative is d_i=ceil(ir/N)-ceil((i-1)r/N).",
                "dependency": "P139 only; P133-P138 and P140 do not depend on EXT15.",
            },
            {
                "id": "EXT16", "author": "Kevin Knight", "title": "Collatz high cycles do not exist", "journal": "Discrete Mathematics 349 (2026), 114812", "doi": "10.1016/j.disc.2025.114812",
                "used_result": "Novelty and terminology boundary only: a high cycle is an extremal rational-cycle class, not an arbitrary positive Collatz cycle.",
                "dependency": "No Phase 22 theorem depends on EXT16.",
            },
            {
                "id": "EXT05", "authors": "Olivier Rozier and Claude Terracol", "title": "Parity sequences of the 3x+1 map on the 2-adic integers and Euclidean embedding", "year": 2026,
                "source": "arXiv:2502.00948v5; Discrete Mathematics 349, 115167", "used_result": "Lemma B.1 lower bound |2^L-3^q|>(64/25)^q/2 for q>12.",
                "dependency": "Only the critical q>=13 part of P138 and the corresponding critical roughness threshold.",
            },
            {
                "id": "CLASSICAL", "used_result": "Eisenstein irreducibility, Sylvester/Bezout resultant identity, Parseval, AM-GM, and standard Terras/Garner affine cycle formula.",
                "dependency": "All algebraic statements are rederived in the repository audit; classical names are context, not opaque computational inputs.",
            },
        ],
        "novelty_boundary": "No literature-wide novelty claim is made. The repository contribution is an independently checked synthesis and exact finite obstruction audit.",
        "proves_collatz": False,
    }


def obstruction_markdown(finite: dict[str, object]) -> str:
    counts = finite["area_counts"]
    row = finite["smallest_combined_uncovered_profile"]
    return f"""# Phase 22 obstruction report

## Exact finite boundary

The audit exhausts every positive exponent composition through `q<=8` and
every valid coprime profile with area at most two through `q<=22`.  The second
scope is area-bounded, not a full composition search.

- exhaustive cyclic classes: `{finite['full_cyclic_classes']}`;
- area-bounded valid profiles: `{finite['area_profile_count']}`;
- area counts: `{json.dumps(counts, sort_keys=True)}`;
- combined energy/source survivors: `{finite['combined_uncovered_count']}`.

## Smallest surviving obstruction

`{json.dumps(row, separators=(',', ':')) if row is not None else 'none in the declared finite scope'}`

The row fields are `q,L,profile,exponents,area,B,D,D|B,C_min,source_excluded,
energy_excluded,energy_upper_numerator,energy_upper_denominator`.  A survivor is
not a cycle: it only survives these two necessary-condition filters.  Exact
integrality and literal legality remain separate.

## Missing bridge

The resultant divisibility and energy inequality require a uniform lower bound
on profile roughness, or an alternative source bound, for arbitrary defect
area.  P140 supplies only a weaker modulus for noncoprime slopes.  Neither
finite coverage nor the Christoffel extremal theorem provides this bridge.

## What this result does not prove

It does not eliminate all positive nontrivial cycles, H89, H112, H72, or prove
the Collatz conjecture.  `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    theory = theory_artifact()
    finite, _ = finite_profiles()
    regressions = regressions_artifact()
    literature = literature_artifact()
    write_json(args.artifact_dir / "phase22_theory.json", theory)
    write_json(args.artifact_dir / "phase22_finite_profiles.json", finite)
    write_json(args.artifact_dir / "phase22_regressions.json", regressions)
    write_json(args.artifact_dir / "phase22_literature_audit.json", literature)
    (args.artifact_dir / "phase22_obstruction_report.md").write_text(obstruction_markdown(finite), encoding="utf-8")
    print(json.dumps({"valid": True, "profiles": finite["area_profile_count"], "survivors": finite["combined_uncovered_count"], "proves_collatz": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
