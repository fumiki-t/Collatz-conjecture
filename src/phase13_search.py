#!/usr/bin/env python3
"""Generate exact Phase 13 renewal-code and residue evidence.

The accepted theorem boundary is mathematical prose plus independently
reconstructed finite evidence.  This generator never treats a finite scan or
decimal approximation as an asymptotic proof.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from math import isqrt
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

getcontext().prec = 50

A_BITS = "11101"
B_BITS = "1100"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encoded_fraction(value: Fraction) -> dict[str, object]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": f"{Decimal(value.numerator) / Decimal(value.denominator):.24f}",
    }


def integer_digest(value: int) -> str:
    width = max(1, (value.bit_length() + 7) // 8)
    return hashlib.sha256(value.to_bytes(width, "big")).hexdigest()


def above(length: int, odd_count: int) -> bool:
    return 3**odd_count > 1 << length


def word_constant(word: str) -> int:
    correction = 0
    for position, bit in enumerate(word):
        if bit == "1":
            correction = 3 * correction + (1 << position)
        elif bit != "0":
            raise ValueError("binary word required")
    return correction


def realizes_word(source: int, word: str) -> tuple[bool, int]:
    value = source
    for bit in word:
        if (value & 1) != int(bit):
            return False, value
        value = (3 * value + 1) // 2 if bit == "1" else value // 2
    return True, value


def first_crossing(word: str) -> bool:
    odd_count = 0
    for length, bit in enumerate(word, 1):
        odd_count += bit == "1"
        if length < len(word) and above(length, odd_count):
            return False
    return above(len(word), odd_count)


@dataclass(frozen=True)
class Block:
    code: str
    forward: str
    length: int
    odd_count: int
    correction: int


@dataclass(frozen=True)
class Address:
    codes: tuple[str, ...]
    forward: str
    length: int
    odd_count: int
    correction: int
    source_residue: int
    endpoint_residue: int

    @property
    def source_positive(self) -> int:
        return self.source_residue or (1 << self.length)

    @property
    def endpoint_positive(self) -> int:
        return self.endpoint_residue or 3**self.odd_count


def codewords_by_q(maximum_q: int) -> list[Block]:
    maximum_length = (3**maximum_q).bit_length() - 1
    pending: list[tuple[str, int]] = [("", 0)]
    words: list[Block] = []
    for length in range(1, maximum_length + 1):
        next_pending: list[tuple[str, int]] = []
        for prefix, odd_count in pending:
            next_pending.append((prefix + "0", odd_count))
            if odd_count >= maximum_q:
                continue
            candidate = prefix + "1"
            next_odd_count = odd_count + 1
            if above(length, next_odd_count):
                forward = candidate[::-1]
                words.append(
                    Block(candidate, forward, length, next_odd_count, word_constant(forward))
                )
            else:
                next_pending.append((candidate, next_odd_count))
        pending = next_pending
    if any(not first_crossing(item.code) for item in words):
        raise AssertionError("first-upcrossing enumeration failed")
    ordered = sorted(item.code for item in words)
    if any(right.startswith(left) for left, right in zip(ordered, ordered[1:])):
        raise AssertionError("prefix-free check failed")
    return words


def pressure_dynamic_program(depth: int) -> dict[str, object]:
    active = {0: 1}
    kappa = Fraction()
    weighted = Fraction()
    sigma = Fraction()
    tau = Fraction()
    nu = Fraction()
    checkpoints = {value for value in (20, 50, 100, 200, depth) if value <= depth}
    selected = []
    total_crossings = 0
    for length in range(1, depth + 1):
        successors: dict[int, int] = {}
        crossing_states: list[tuple[int, int]] = []
        for odd_count, multiplicity in active.items():
            successors[odd_count] = successors.get(odd_count, 0) + multiplicity
            q_after_one = odd_count + 1
            if above(length, q_after_one):
                crossing_states.append((q_after_one, multiplicity))
            else:
                successors[q_after_one] = successors.get(q_after_one, 0) + multiplicity
        active = successors
        for odd_count, multiplicity in crossing_states:
            total_crossings += multiplicity
            kappa += Fraction(multiplicity, 1 << length)
            weighted += Fraction(multiplicity * 3**odd_count, 1 << (2 * length))
            sigma += Fraction(multiplicity, 3**odd_count)
            tau += Fraction(multiplicity, (1 << length) * 3**odd_count)
            nu += Fraction(multiplicity, 1 << (2 * length))
        if length in checkpoints:
            selected.append(
                {
                    "length": length,
                    "kappa": encoded_fraction(kappa),
                    "weighted": encoded_fraction(weighted),
                    "sigma": encoded_fraction(sigma),
                    "tau": encoded_fraction(tau),
                    "nu": encoded_fraction(nu),
                    "active_state_count": len(active),
                    "active_word_count": str(sum(active.values())),
                }
            )
    return {
        "depth": depth,
        "crossing_word_count": str(total_crossings),
        "checkpoints": selected,
        "final": selected[-1],
    }


def renewal_code_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase13-renewal-code-v1",
        "P77": {
            "repository_status": "VERIFIED_THEOREM",
            "hypotheses": [
                "Delta_n>0 for every n>0",
                "Delta_n tends to positive infinity",
            ],
            "strict_suffix_minimum": "t_0=0 and t_(i+1) is the unique argmin of Delta_n over n>t_i",
            "orientation": "w_i=s_[t_i,t_(i+1)) is the forward block and u_i=reverse(w_i)",
            "first_upcrossing": "every nonempty proper prefix p of u_i has 3^q(p)<2^L(p), while 3^q(u_i)>2^L(u_i)",
            "code_property": "the first-upcrossing family U is prefix-free",
            "endpoint_bits": "every nontrivial forward block starts with 1 and ends with 0; w=u=1 is the unique length-one exception",
            "uniqueness_boundary": "the forward infinite decomposition is unique because the strict suffix-minimum times are unique, not because reverse(U) is prefix-free",
            "affine_recurrence": "scan forward bits at positions j from zero; on bit 1 replace B by 3B+2^j and on bit 0 leave B unchanged",
        },
        "what_this_result_does_not_prove": "P77 supplies a symbolic decomposition under permanent safety and discrepancy escape; it does not prove either hypothesis for every Collatz orbit without P74's external input.",
        "proves_collatz": False,
    }


def pressure_artifact(depth: int) -> dict[str, object]:
    finite = pressure_dynamic_program(depth)
    return {
        "format": "collatz-phase13-pressure-v1",
        "P78": {
            "repository_status": "VERIFIED_THEOREM",
            "multiplier": "c(u)=3^q/2^L and 1<c(u)<=3/2",
            "weighted_identity": "sum_(u in U) 2^(-L(u))*c(u)=1",
            "stopping_justification": [
                "M_n=3^q/2^n is a fair-bit martingale",
                "M_(T wedge n)<=3/2, so bounded convergence applies",
                "on T=infinity the negative logarithmic drift and strong law give M_n->0",
            ],
            "first_bit_split": "u=1 contributes probability 1/2 and weighted mass 3/4; every other codeword starts with 0 and has total weighted mass 1/4",
            "bounds": {
                "kappa": "<3/4",
                "sigma": "<7/12",
                "tau": "<19/96",
                "nu": "<9/32",
            },
            "bound_witnesses": {
                "nontrivial_kappa": "sum_(u!=1)2^-L < sum_(u!=1)2^-L*c = 1/4",
                "nontrivial_sigma": "sum_(u!=1)3^-q = sum 2^-L/c < 1/4",
                "nontrivial_tau": "L>=3 for u!=1, hence tau_other <= sigma_other/8 < 1/32",
                "nontrivial_nu": "L>=3 for u!=1, hence nu_other <= kappa_other/8 < 1/32",
            },
            "factorization": {
                "source_mass": "sum_(a in U^i)2^-L(a)=kappa^i",
                "endpoint_mass": "sum_(a in U^i)3^-Q(a)=sigma^i",
                "product_mass": "sum_(a in U^i)2^-L(a)3^-Q(a)=tau^i",
            },
            "novelty_boundary": "The weighted first-passage and Kraft identities may be standard probability/coding consequences; no literature-wide novelty is claimed.",
        },
        "E22_pressure_dp": finite,
        "exact_upper_bounds": {
            "kappa": encoded_fraction(Fraction(3, 4)),
            "sigma": encoded_fraction(Fraction(7, 12)),
            "tau": encoded_fraction(Fraction(19, 96)),
            "nu": encoded_fraction(Fraction(9, 32)),
        },
        "what_this_result_does_not_prove": "The finite DP is a sanity audit only, and the pressure bounds do not control ordinary least positive representatives.",
        "proves_collatz": False,
    }


def valuation_two(value: int) -> int:
    if value <= 0:
        raise ValueError("positive value required")
    return (value & -value).bit_length() - 1


def threshold_bridge_artifact(blocks: list[Block]) -> dict[str, object]:
    digest = hashlib.sha256()
    equality_words: list[str] = []
    q_counts: Counter[int] = Counter()
    selected = []
    for block in blocks:
        L, q, B = block.length, block.odd_count, block.correction
        ratio = Fraction(B + (1 << L), 3**q)
        q_counts[q] += 1
        if block.forward != "1":
            if ratio < Fraction(13, 9):
                raise AssertionError("threshold failed")
            if not block.forward.startswith("11") or not block.forward.endswith("0"):
                raise AssertionError("nontrivial block endpoint convention failed")
            numerator = B + (1 << L) - 3**q
            if numerator % 4:
                raise AssertionError("C_w is not integral")
            normalized = numerator // 4
            if normalized < 1 << (L - 3):
                raise AssertionError("C_w lower bound failed")
            run = len(block.forward) - len(block.forward.lstrip("1"))
            if valuation_two(normalized) != run - 2:
                raise AssertionError("C_w valuation failed")
            if normalized == 1 << (L - 3) and block.forward != "110":
                raise AssertionError("C_w equality word failed")
        else:
            normalized = 0
            run = 1
        if ratio == Fraction(13, 9):
            equality_words.append(block.forward)
        digest.update(
            f"{block.code}|{block.forward}|{L}|{q}|{B}|{ratio.numerator}/{ratio.denominator}|{normalized}|{run}\n".encode(
                "ascii"
            )
        )
        if block.forward in {"1", "110", "111100", "111010", "111011100"}:
            selected.append(
                {
                    "code": block.code,
                    "forward": block.forward,
                    "L": L,
                    "q": q,
                    "B": B,
                    "R": encoded_fraction(ratio),
                    "C": normalized,
                    "initial_one_run": run,
                }
            )
    return {
        "format": "collatz-phase13-threshold-bridge-v1",
        "P79": {
            "repository_status": "VERIFIED_THEOREM",
            "fixed_type_minimum": "at fixed (L,q), adjacent 01->10 strictly decreases B; the unique minimum is 1^q0^(L-q) with B_min=3^q-2^q",
            "threshold": "for renewal w!=1, R(w)=(B_w+2^L)/3^q>=13/9, with equality only for w=110; q=3 is impossible",
            "companion_legality": "the next renewal companion h' is greater than 1 iff h>R(w)",
            "positive_source_bridge": "h<=13/9 forces w=1; repeated one-blocks give 2^r|(S+1), hence h-1>(4/9)(S+1)^(-log_2(3/2))",
            "ordinary_integrality_use": "the Archimedean comparison 2^r<=S+1 uses that S is a positive ordinary integer",
            "normalized_transfer": {
                "definitions": "U=(S+1)/4, V=(h-1)/4, C_w=(B_w+2^L-3^q)/4",
                "equations": ["2^L U'=3^q U+C_w", "2^L V'=3^q V-C_w"],
                "C_integrality": "C_1=0; for w!=1, C_w is a positive integer and C_w>=2^(L-3), with equality only for 110",
                "valuation": "if r is the initial 1-run of nontrivial w, then v2(C_w)=r-2; if U and U' are integers, v2(U)=r-2",
                "one_block": "w=1 is possible between S=3 mod 4 renewal boundaries iff U is even, and then U'=3U/2",
                "ratio": "for little_u=(h-1)/(S+1), little_u'=(h-R)/(S+R) and little_u-little_u'=(R-1)(S+h)/((S+1)(S+R))",
            },
        },
        "finite_block_audit": {
            "maximum_q": max(block.odd_count for block in blocks),
            "block_count": len(blocks),
            "q_distribution": dict(sorted(q_counts.items())),
            "q3_count": q_counts[3],
            "R_13_over_9_words": equality_words,
            "row_digest_sha256": digest.hexdigest(),
            "selected_rows": selected,
        },
        "H72_transfer_assessment": {
            "status": "OPEN",
            "result": "The valuation-conditioned transfer is exact and orbit-specific, but no subexponential canonical-residue anti-concentration or closed transfer-operator estimate follows from it here.",
        },
        "what_this_result_does_not_prove": "The threshold and monotone companion ratio do not exclude an infinite positive renewal sequence or prove H72.",
        "proves_collatz": False,
    }


def critical_countermodel_artifact(steps: int) -> dict[str, object]:
    floor_log = 0
    defect = 0
    exponent_sum = 0
    correction = 0
    exponents: list[int] = []
    defects = [0]
    exponent_sums = [0]
    residues = [0]
    row_digest = hashlib.sha256()
    checkpoints = {value for value in (64, 256, 1024, steps) if value <= steps}
    selected = []
    latest_change = 0
    unchanged_run = 0
    longest_unchanged = 0
    b_previous = None
    for index in range(steps):
        next_floor = (3 ** (index + 1)).bit_length() - 1
        b_value = next_floor - floor_log
        if b_previous == b_value == 1:
            raise AssertionError("consecutive b=1")
        increment = int(b_value == 2 and defect < isqrt(index + 1))
        next_defect = defect + increment
        exponent = b_value - increment
        if exponent not in (1, 2):
            raise AssertionError("critical exponent escaped {1,2}")
        correction = 3 * correction + (1 << exponent_sum)
        exponent_sum += exponent
        modulus = 1 << exponent_sum
        residue = (-correction * pow(pow(3, index + 1, modulus), -1, modulus)) % modulus
        if residue == residues[-1]:
            unchanged_run += 1
            longest_unchanged = max(longest_unchanged, unchanged_run)
        else:
            unchanged_run = 0
            latest_change = index + 1
        exponents.append(exponent)
        defects.append(next_defect)
        exponent_sums.append(exponent_sum)
        residues.append(residue)
        if exponent_sum != next_floor - next_defect:
            raise AssertionError("E=f-A failed")
        if next_defect not in {isqrt(index + 1) - 1, isqrt(index + 1)}:
            raise AssertionError("square-root tracking failed")
        row_digest.update(
            f"{index + 1}|{b_value}|{next_defect}|{exponent}|{exponent_sum}|{residue}\n".encode("ascii")
        )
        if index + 1 in checkpoints:
            selected.append(
                {
                    "odd_index": index + 1,
                    "f": next_floor,
                    "A": next_defect,
                    "E": exponent_sum,
                    "residue_bit_length": residue.bit_length(),
                    "residue_sha256_big_endian": integer_digest(residue),
                }
            )
        defect = next_defect
        floor_log = next_floor
        b_previous = b_value

    full_word = "".join("1" + "0" * (value - 1) for value in exponents)
    q = 0
    for length, bit in enumerate(full_word, 1):
        q += bit == "1"
        if not above(length, q):
            raise AssertionError("critical full-prefix safety failed")
    partial_defect_sum = sum((Fraction(1, 1 << value) for value in defects), Fraction())
    exclusion_exponent = exponent_sums[latest_change - 1] if latest_change else 0
    return {
        "format": "collatz-phase13-critical-countermodel-v1",
        "NG22_additional_evidence": {
            "repository_status": "REFUTED",
            "relation_to_existing_claim": "This square-root-defect model is additional evidence for existing NG22, not a new claim ID.",
            "properties": [
                "e_j belongs to {1,2}",
                "floor(sqrt(j))-1<=A_j<=floor(sqrt(j))",
                "E_j=floor(j log2 3)-A_j",
                "every positive full shortcut prefix is coefficient-safe",
                "E_j/j tends to log2 3",
                "sum 2^-A_j converges",
                "a coherent odd 2-adic inverse source exists",
                "the real companion satisfies h_j>1 and h_j=O(sqrt(j))",
                "sum 1/h_j diverges",
            ],
            "positive_ordinary_source": "OPEN",
        },
        "finite_audit": {
            "odd_steps": steps,
            "full_shortcut_length": len(full_word),
            "first_64_exponents": "".join(str(value) for value in exponents[:64]),
            "final_f": floor_log,
            "final_A": defect,
            "final_E": exponent_sum,
            "partial_sum_2_minus_A": encoded_fraction(partial_defect_sum),
            "row_digest_sha256": row_digest.hexdigest(),
            "checkpoints": selected,
            "latest_residue_change_index": latest_change,
            "maximum_consecutive_unchanged_lifts": longest_unchanged,
            "last_lift_changed": residues[-1] != residues[-2],
            "finite_source_exclusion": f"no positive ordinary source below 2^{exclusion_exponent} realizes the first {latest_change} exponents",
            "finite_source_exclusion_power": exclusion_exponent,
        },
        "what_this_result_does_not_prove": "Finite late residue changes do not prove eventual non-stabilization, and the coherent 2-adic source is not known to be a positive ordinary integer.",
        "proves_collatz": False,
    }


def append_block(prefix: Address | None, block: Block) -> Address:
    if prefix is None:
        codes = (block.code,)
        forward = block.forward
        length = block.length
        odd_count = block.odd_count
        correction = block.correction
    else:
        codes = prefix.codes + (block.code,)
        forward = prefix.forward + block.forward
        length = prefix.length + block.length
        odd_count = prefix.odd_count + block.odd_count
        correction = 3**block.odd_count * prefix.correction + (1 << prefix.length) * block.correction
    modulus_two = 1 << length
    modulus_three = 3**odd_count
    source = (-correction * pow(3**odd_count, -1, modulus_two)) % modulus_two
    endpoint = (correction * pow(modulus_two, -1, modulus_three)) % modulus_three
    address = Address(codes, forward, length, odd_count, correction, source, endpoint)
    if correction != word_constant(forward):
        raise AssertionError("affine composition failed")
    valid, actual_endpoint = realizes_word(address.source_positive, forward)
    if not valid or actual_endpoint % modulus_three != endpoint:
        raise AssertionError("canonical residue failed")
    return address


def addresses_with_bound(blocks: list[Block], count: int, maximum_q: int) -> list[Address]:
    level: list[Address | None] = [None]
    for _ in range(count):
        next_level = []
        for prefix in level:
            q_before = 0 if prefix is None else prefix.odd_count
            for block in blocks:
                if q_before + block.odd_count <= maximum_q:
                    next_level.append(append_block(prefix, block))
        level = next_level
    return [address for address in level if address is not None]


def progression_count(height: int, least_positive: int, modulus: int) -> int:
    return 0 if height < least_positive else (height - least_positive) // modulus + 1


def maximum_canonical_ratio(values: list[int], mass: Fraction, square: bool = False) -> dict[str, object]:
    best = Fraction()
    best_height = 0
    best_count = 0
    for count, height in enumerate(sorted(values), 1):
        denominator = height * height * mass if square else height * mass
        ratio = Fraction(count, 1) / denominator
        if ratio > best:
            best, best_height, best_count = ratio, height, count
    return {"ratio": encoded_fraction(best), "height": best_height, "count": best_count}


def address_metrics(addresses: list[Address], height_limit: int) -> dict[str, object]:
    endpoint_mass = sum((Fraction(1, 3**a.odd_count) for a in addresses), Fraction())
    product_mass = sum(
        (Fraction(1, (1 << a.length) * 3**a.odd_count) for a in addresses), Fraction()
    )
    row_hash = hashlib.sha256()
    for address in sorted(addresses, key=lambda a: a.codes):
        row_hash.update(
            f"{'/'.join(address.codes)}|{address.length}|{address.odd_count}|{address.correction}|{address.source_residue}|{address.endpoint_residue}\n".encode(
                "ascii"
            )
        )

    endpoint_max_error = Fraction()
    endpoint_error_height = 0
    product_max_error = Fraction()
    product_error_height = 0
    for height in range(1, height_limit + 1):
        endpoint_points = sum(
            progression_count(height, a.endpoint_positive, 3**a.odd_count) for a in addresses
        )
        endpoint_error = Fraction(endpoint_points) - height * endpoint_mass
        if endpoint_error > endpoint_max_error:
            endpoint_max_error, endpoint_error_height = endpoint_error, height
        product_points = 0
        for address in addresses:
            source_points = progression_count(height, address.source_positive, 1 << address.length)
            endpoint_points_for_address = progression_count(
                height, address.endpoint_positive, 3**address.odd_count
            )
            product_points += source_points * endpoint_points_for_address
        product_error = Fraction(product_points) - height * height * product_mass
        if product_error > product_max_error:
            product_max_error, product_error_height = product_error, height

    exact = Counter((a.odd_count, a.endpoint_residue) for a in addresses)
    compatible = 0
    for index, left in enumerate(addresses):
        for right in addresses[index + 1 :]:
            modulus = 3 ** min(left.odd_count, right.odd_count)
            compatible += (left.endpoint_residue - right.endpoint_residue) % modulus == 0
    return {
        "address_count": len(addresses),
        "q_distribution": dict(sorted(Counter(a.odd_count for a in addresses).items())),
        "row_digest_sha256": row_hash.hexdigest(),
        "endpoint_mass": encoded_fraction(endpoint_mass),
        "product_mass": encoded_fraction(product_mass),
        "canonical_endpoint_max_ratio": maximum_canonical_ratio(
            [a.endpoint_positive for a in addresses], endpoint_mass
        ),
        "canonical_two_sided_max_ratio": maximum_canonical_ratio(
            [max(a.source_positive, a.endpoint_positive) for a in addresses], product_mass, True
        ),
        "ordinary_height_limit": height_limit,
        "endpoint_max_plus_one_error": encoded_fraction(endpoint_max_error),
        "endpoint_error_height": endpoint_error_height,
        "two_sided_max_plus_one_error": encoded_fraction(product_max_error),
        "two_sided_error_height": product_error_height,
        "endpoint_cylinders": {
            "compatible_unordered_pairs": compatible,
            "total_unordered_pairs": len(addresses) * (len(addresses) - 1) // 2,
            "exact_duplicate_unordered_pairs": sum(value * (value - 1) // 2 for value in exact.values()),
            "maximum_exact_multiplicity": max(exact.values(), default=0),
        },
    }


def normalized_odd(value: int) -> int:
    return value >> valuation_two(value)


def adversarial_seeds() -> list[tuple[str, int]]:
    rows = [("2^m-1", (1 << exponent) - 1) for exponent in range(3, 25)]
    rows.extend(("8^m-5", 8**exponent - 5) for exponent in range(1, 11))
    for count in range(1, 11):
        for mask in range(1 << count):
            bits = "".join("111" if mask & (1 << j) else "110" for j in range(count))
            rows.append(("(110|111)^*", int(bits, 2)))
    rows.extend([("A=11101", int(A_BITS, 2)), ("B=1100", int(B_BITS, 2))])
    for r in range(1, 9):
        for s in range(1, 9):
            rows.append(("A^rB^s", int(A_BITS * r + B_BITS * s, 2)))
    return rows


def parity_prefix(source: int, length: int) -> str:
    bits = []
    value = source
    for _ in range(length):
        bits.append(str(value & 1))
        value = (3 * value + 1) // 2 if value & 1 else value // 2
    return "".join(bits)


def adversarial_convention_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    families: Counter[str] = Counter()
    for family, raw in adversarial_seeds():
        source = normalized_odd(raw)
        word = parity_prefix(source, 24)
        correction = word_constant(word)
        q = word.count("1")
        residue = (-correction * pow(3**q, -1, 1 << 24)) % (1 << 24)
        if source % (1 << 24) != residue:
            raise AssertionError("adversarial inverse-parity convention failed")
        families[family] += 1
        digest.update(f"{family}|{raw}|{source}|{word}|{correction}|{residue}\n".encode("ascii"))
    return {
        "prefix_length": 24,
        "instance_count": sum(families.values()),
        "family_counts": dict(sorted(families.items())),
        "row_digest_sha256": digest.hexdigest(),
    }


def residue_artifact(blocks: list[Block], maximum_q: int, maximum_blocks: int, height: int) -> dict[str, object]:
    families = []
    for count in range(1, maximum_blocks + 1):
        families.append(
            {"block_count": count, **address_metrics(addresses_with_bound(blocks, count, maximum_q), height)}
        )
    one = next(block for block in blocks if block.code == "1")
    address = append_block(None, one)
    endpoint_prediction = Fraction(2, 3)
    product_prediction = Fraction(2, 3)
    if address.endpoint_positive != 2 or address.source_positive != 1:
        raise AssertionError("raw Haar obstruction convention failed")
    return {
        "format": "collatz-phase13-residue-audit-v1",
        "E22": {
            "repository_status": "VERIFIED_FINITE",
            "maximum_total_q": maximum_q,
            "maximum_blocks": maximum_blocks,
            "ordinary_height_limit": height,
            "codeword_count": len(blocks),
            "codeword_q_distribution": dict(sorted(Counter(block.odd_count for block in blocks).items())),
            "address_families": families,
            "adversarial_conventions": adversarial_convention_audit(),
        },
        "NG23": {
            "repository_status": "REFUTED",
            "hypothesis": "Coefficient-one Haar cylinder volume controls the canonical least positive representative count.",
            "least_counterexample": {
                "codeword": "1",
                "forward_word": "1",
                "L": 1,
                "Q": 1,
                "B": 1,
                "height": 2,
                "source_positive": 1,
                "endpoint_positive": 2,
                "canonical_count": 1,
                "endpoint_volume_prediction": encoded_fraction(endpoint_prediction),
                "two_sided_volume_prediction": encoded_fraction(product_prediction),
            },
            "failure_scope": "This refutes coefficient one and the inference from Haar mass to a designated ordinary representative. It does not refute an unspecified uniform constant or a stronger arithmetic anti-concentration theorem.",
        },
        "canonical_formulas": {
            "source": "r2=[-B*3^(-Q)]_(2^L)",
            "endpoint": "r3=[B*2^(-L)]_(3^Q)",
            "composition": "B(ab)=3^Q(b)B(a)+2^L(a)B(b)",
            "lift_identity": "3^Q r2+B=2^L(r3+k*3^Q) for an integer k",
        },
        "what_this_result_does_not_prove": "Finite ratios, absence of duplicate cylinders, and bounded fluctuation are not general anti-concentration theorems.",
        "proves_collatz": False,
    }


def conditional_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase13-conditional-pressure-v1",
        "P80": {
            "repository_status": "CONDITIONAL",
            "counts": {
                "N3": "number with address multiplicity of a in U^i whose least positive endpoint representative modulo 3^Q(a) is at most H",
                "N23": "number with address multiplicity of a in U^i whose least positive source representative modulo 2^L(a) and endpoint representative modulo 3^Q(a) are both at most H",
            },
            "endpoint_premise": "for every epsilon>0 there is i0(epsilon) such that for every i>=i0 and every ordinary H>=1, N_i^(3)(H)<=exp(epsilon*i)*H*sigma^i",
            "two_sided_premise": "for every epsilon>0 there is i0(epsilon) such that for every i>=i0 and every ordinary H>=1, N_i^(2,3)(H)<=exp(epsilon*i)*H^2*tau^i",
            "orbit_growth": "S_i+h_i=(S_0+h_0)*product_(j<i)c(u_j), hence S_i<(S_0+h_0)*(3/2)^i",
            "endpoint_factor": encoded_fraction(Fraction(3, 2) * Fraction(7, 12)),
            "two_sided_factor": encoded_fraction(Fraction(9, 4) * Fraction(19, 96)),
            "epsilon_choice": "choose epsilon strictly below -log(7/8) for endpoint or -log(57/128) for two-sided; the corresponding exponential upper bound tends to zero although the actual address count is at least one",
            "conclusion": "Either premise excludes a positive permanent-safe nonperiodic orbit and would close H72's branch, but neither premise is proved in Phase 13.",
        },
        "H72": {"repository_status": "OPEN"},
        "Haar_warning": "Standard Haar measure and Tonelli identities average local cylinders but do not exclude one designated positive ordinary integer or absorb one lattice-point error per address.",
        "what_this_result_does_not_prove": "P80 does not prove either anti-concentration premise, eliminate nontrivial cycles, or prove the Collatz conjecture.",
        "proves_collatz": False,
    }


def obstruction_report(path: Path) -> None:
    path.write_text(
        """# Phase 13 obstruction report

Phase 13 does not prove or disprove the Collatz conjecture.

## Exact failed mechanism

The raw coefficient-one Haar-volume estimate fails for the first codeword
`u=1`.  Its source representative is 1 modulo 2, its endpoint representative
is 2 modulo 3, and at ordinary height `H=2` the canonical count is 1 while
both raw volume predictions equal `2/3`.

This is a local obstruction to coefficient one and a fundamental obstruction
to identifying local Haar mass with control of one designated positive
integer.  It does not refute an estimate with an unspecified fixed constant.

## Surviving conditional route

An endpoint count bounded by `exp(epsilon*i) H sigma^i`, or a two-sided count
bounded by `exp(epsilon*i) H^2 tau^i`, would combine with renewal growth to
exclude a permanent-safe positive orbit.  Phase 13 proves only this
implication.  The anti-concentration premise remains open.

## Additional exact structure

For a nontrivial renewal block, the normalized correction
`C_w=(B_w+2^L-3^q)/4` is integral, satisfies `C_w>=2^(L-3)`, and has
`v2(C_w)=r-2`, where `r` is the initial run of ones.  This produces a genuine
ordinary-integrality transition rule but no closed anti-concentration bound.

## What this result does not prove

- the endpoint or two-sided anti-concentration theorem;
- nonexistence of a positive ordinary permanent-safe source;
- H72;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
""",
        encoding="utf-8",
    )


def generate(
    artifact_dir: Path,
    dp_length: int,
    maximum_q: int,
    maximum_blocks: int,
    height: int,
    critical_steps: int,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    blocks = codewords_by_q(maximum_q)
    write_json(artifact_dir / "phase13_renewal_code.json", renewal_code_artifact())
    write_json(artifact_dir / "phase13_pressure_bounds.json", pressure_artifact(dp_length))
    write_json(artifact_dir / "phase13_threshold_bridge.json", threshold_bridge_artifact(blocks))
    write_json(
        artifact_dir / "phase13_critical_countermodel.json",
        critical_countermodel_artifact(critical_steps),
    )
    write_json(
        artifact_dir / "phase13_residue_audit.json",
        residue_artifact(blocks, maximum_q, maximum_blocks, height),
    )
    write_json(artifact_dir / "phase13_conditional_pressure.json", conditional_artifact())
    obstruction_report(artifact_dir / "phase13_obstruction_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--dp-length", type=int, default=512)
    parser.add_argument("--max-total-q", type=int, default=12)
    parser.add_argument("--max-blocks", type=int, default=4)
    parser.add_argument("--height", type=int, default=2048)
    parser.add_argument("--critical-steps", type=int, default=4096)
    args = parser.parse_args()
    if min(args.dp_length, args.max_total_q, args.max_blocks, args.height, args.critical_steps) < 1:
        raise SystemExit("all finite bounds must be positive")
    generate(
        args.artifact_dir,
        args.dp_length,
        args.max_total_q,
        args.max_blocks,
        args.height,
        args.critical_steps,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
