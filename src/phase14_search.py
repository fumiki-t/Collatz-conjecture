#!/usr/bin/env python3
"""Generate exact Phase 14 coalescent-rewrite evidence.

All acceptance decisions use integers and ``Fraction``.  Decimal strings are
reporting fields only.  The independent verifier deliberately reimplements
the enumeration and arithmetic.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

getcontext().prec = 40

A_BITS = "11101"
B_BITS = "1100"
MACRO_ZERO = "1111111111110000000"


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
        return self.source_residue or 1 << self.length

    @property
    def endpoint_positive(self) -> int:
        return self.endpoint_residue or 3**self.odd_count


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encoded_fraction(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": f"{Decimal(value.numerator) / Decimal(value.denominator):.24f}",
    }


def above(length: int, odd_count: int) -> bool:
    return 3**odd_count > 1 << length


def word_constant(word: str) -> int:
    value = 0
    for position, bit in enumerate(word):
        if bit == "1":
            value = 3 * value + (1 << position)
        elif bit != "0":
            raise ValueError("binary word required")
    return value


def literal_trace(source: int, word: str) -> tuple[list[int], str]:
    values = [source]
    bits = []
    value = source
    for expected in word:
        bit = str(value & 1)
        bits.append(bit)
        if bit != expected:
            raise ValueError("source does not realize word")
        value = (3 * value + 1) // 2 if bit == "1" else value // 2
        values.append(value)
    return values, "".join(bits)


def first_upcrossing(code: str) -> bool:
    odd_count = 0
    for length, bit in enumerate(code, 1):
        odd_count += bit == "1"
        if length < len(code) and above(length, odd_count):
            return False
    return above(len(code), odd_count)


def codewords(maximum_q: int) -> list[Block]:
    maximum_length = (3**maximum_q).bit_length() - 1
    pending: list[tuple[str, int]] = [("", 0)]
    complete: list[Block] = []
    for length in range(1, maximum_length + 1):
        following: list[tuple[str, int]] = []
        for prefix, odd_count in pending:
            following.append((prefix + "0", odd_count))
            if odd_count >= maximum_q:
                continue
            candidate = prefix + "1"
            q_next = odd_count + 1
            if above(length, q_next):
                forward = candidate[::-1]
                complete.append(
                    Block(candidate, forward, length, q_next, word_constant(forward))
                )
            else:
                following.append((candidate, q_next))
        pending = following
    if any(not first_upcrossing(block.code) for block in complete):
        raise AssertionError("first-upcrossing enumeration")
    return complete


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
        correction = (
            3**block.odd_count * prefix.correction
            + (1 << prefix.length) * block.correction
        )
    modulus_two = 1 << length
    modulus_three = 3**odd_count
    source = (-correction * pow(3**odd_count, -1, modulus_two)) % modulus_two
    endpoint = (correction * pow(modulus_two, -1, modulus_three)) % modulus_three
    result = Address(codes, forward, length, odd_count, correction, source, endpoint)
    if correction != word_constant(forward):
        raise AssertionError("address composition")
    values, _ = literal_trace(result.source_positive, forward)
    if values[-1] % modulus_three != endpoint:
        raise AssertionError("endpoint residue")
    return result


def enumerate_addresses(
    blocks: list[Block], maximum_q: int
) -> tuple[dict[int, list[Address]], list[Address]]:
    levels: dict[int, list[Address]] = {}
    previous: list[Address | None] = [None]
    all_rows: list[Address] = []
    for depth in range(1, maximum_q + 1):
        current: list[Address] = []
        for prefix in previous:
            q_before = 0 if prefix is None else prefix.odd_count
            for block in blocks:
                if q_before + block.odd_count <= maximum_q:
                    current.append(append_block(prefix, block))
        levels[depth] = current
        all_rows.extend(current)
        previous = current
    return levels, all_rows


def address_id(address: Address) -> str:
    return "|".join(address.codes)


def address_record(address: Address) -> dict[str, object]:
    return {
        "codes": list(address.codes),
        "forward": address.forward,
        "block_count": len(address.codes),
        "L": address.length,
        "Q": address.odd_count,
        "B": address.correction,
        "source_positive": address.source_positive,
        "endpoint_positive": address.endpoint_positive,
        "r2": address.source_residue,
        "r3": address.endpoint_residue,
    }


def pair_rewrite(d: Address, a: Address) -> tuple[int, int, int] | None:
    """Return (k,m,x0) when every positive d-source rewrites downward to a."""
    if d.odd_count != a.odd_count or d.length < a.length:
        return None
    k = d.length - a.length
    numerator = (1 << k) * a.correction - d.correction
    modulus = 3**d.odd_count
    if numerator % modulus:
        return None
    m = numerator // modulus
    source_numerator = d.source_positive - m
    if source_numerator % (1 << k):
        raise AssertionError("rewrite source congruence")
    x0 = source_numerator // (1 << k)
    if x0 <= 0 or x0 >= d.source_positive:
        return None
    if x0 % (1 << a.length) != a.source_residue:
        raise AssertionError("rewrite target cylinder")
    if literal_trace(x0, a.forward)[0][-1] != literal_trace(d.source_positive, d.forward)[0][-1]:
        raise AssertionError("rewrite endpoint")
    return k, m, x0


def fraction_mass(rows: list[Address], kind: str) -> Fraction:
    if kind == "kappa":
        return sum((Fraction(1, 1 << row.length) for row in rows), Fraction())
    if kind == "sigma":
        return sum((Fraction(1, 3**row.odd_count) for row in rows), Fraction())
    if kind == "tau":
        return sum(
            (Fraction(1, (1 << row.length) * 3**row.odd_count) for row in rows),
            Fraction(),
        )
    raise ValueError(kind)


def rewrite_audit(maximum_q: int) -> tuple[dict[str, object], list[Block]]:
    blocks = codewords(maximum_q)
    levels, addresses = enumerate_addresses(blocks, maximum_q)
    grouped: dict[tuple[int, int], list[Address]] = defaultdict(list)
    for row in addresses:
        grouped[(row.odd_count, row.endpoint_residue)].append(row)

    edges: list[tuple[Address, Address, int, int, int]] = []
    collision_pairs: list[tuple[Address, Address]] = []
    for group in grouped.values():
        for left_index, left in enumerate(group):
            for right in group[left_index + 1 :]:
                collision_pairs.append((left, right))
                for d, a in ((left, right), (right, left)):
                    rewrite = pair_rewrite(d, a)
                    if rewrite is not None:
                        edges.append((d, a, *rewrite))

    edge_map: dict[str, list[str]] = defaultdict(list)
    for d, a, _k, _m, _x0 in edges:
        source, target = address_id(d), address_id(a)
        edge_map[source].append(target)

    @lru_cache(None)
    def normal_forms(node: str) -> frozenset[str]:
        if node not in edge_map:
            return frozenset((node,))
        result: set[str] = set()
        for target in edge_map[node]:
            result.update(normal_forms(target))
        return frozenset(result)

    nonconfluent = [node for node in edge_map if len(normal_forms(node)) != 1]
    if nonconfluent:
        raise AssertionError("finite nonconfluence found")
    reducible = set(edge_map)

    address_digest = hashlib.sha256()
    for row in sorted(addresses, key=lambda item: (item.odd_count, item.codes)):
        address_digest.update(
            f"{address_id(row)}|{row.forward}|{row.length}|{row.odd_count}|{row.correction}|{row.source_residue}|{row.endpoint_residue}\n".encode(
                "ascii"
            )
        )
    rewrite_digest = hashlib.sha256()
    for d, a, k, m, x0 in sorted(
        edges, key=lambda item: (item[0].odd_count, item[0].codes, item[1].codes)
    ):
        rewrite_digest.update(
            f"{address_id(d)}->{address_id(a)}|{k}|{m}|{x0}|{d.source_positive}\n".encode(
                "ascii"
            )
        )

    pair_candidates = []
    for left, right in collision_pairs:
        pair_candidates.append(
            (
                (
                    left.odd_count,
                    max(left.length, right.length),
                    min(left.length, right.length),
                    max(len(left.codes), len(right.codes)),
                    min(len(left.codes), len(right.codes)),
                    min(left.forward, right.forward),
                    max(left.forward, right.forward),
                ),
                left,
                right,
            )
        )
    _, first_left, first_right = min(pair_candidates, key=lambda item: item[0])
    if first_left.length > first_right.length:
        first_d, first_a = first_left, first_right
    else:
        first_d, first_a = first_right, first_left
    first_rewrite = pair_rewrite(first_d, first_a)
    if first_rewrite is None:
        raise AssertionError("least collision is not a positive rewrite")

    fixed_block_rows = []
    for depth, rows in levels.items():
        counts = Counter((row.odd_count, row.endpoint_residue) for row in rows)
        fixed_block_rows.append(
            {
                "block_count": depth,
                "address_count": len(rows),
                "duplicate_pairs": sum(value * (value - 1) // 2 for value in counts.values()),
                "maximum_multiplicity": max(counts.values(), default=0),
            }
        )

    minimal_reducible = []
    for depth, rows in levels.items():
        parent_reducible = {
            address_id(row) for row in levels.get(depth - 1, []) if address_id(row) in reducible
        }
        for row in rows:
            if address_id(row) in reducible and "|".join(row.codes[:-1]) not in parent_reducible:
                minimal_reducible.append(row)

    pressure_rows = []
    for depth, rows in levels.items():
        irreducible = [row for row in rows if address_id(row) not in reducible]
        masses = {}
        for kind in ("kappa", "sigma", "tau"):
            all_mass = fraction_mass(rows, kind)
            irreducible_mass = fraction_mass(irreducible, kind)
            masses[kind] = {
                "all": encoded_fraction(all_mass),
                "irreducible": encoded_fraction(irreducible_mass),
                "retained_ratio": encoded_fraction(irreducible_mass / all_mass),
            }
        pressure_rows.append(
            {
                "block_count": depth,
                "all_addresses": len(rows),
                "rewrite_reducible": len(rows) - len(irreducible),
                "irreducible": len(irreducible),
                "masses": masses,
                "scaled_endpoint_mass": encoded_fraction(
                    Fraction(3, 2) ** depth * fraction_mass(irreducible, "sigma")
                ),
                "scaled_two_sided_mass": encoded_fraction(
                    Fraction(9, 4) ** depth * fraction_mass(irreducible, "tau")
                ),
            }
        )

    class_sizes = Counter(len(group) for group in grouped.values())
    k_distribution = Counter(edge[2] for edge in edges)
    m_signs = Counter("positive" if edge[3] > 0 else "zero" if edge[3] == 0 else "negative" for edge in edges)
    report = {
        "format": "collatz-phase14-rewrite-search-v1",
        "E23": {
            "repository_status": "VERIFIED_FINITE",
            "scope": {
                "maximum_total_Q": maximum_q,
                "block_counts": [1, maximum_q],
                "ordering_for_minimum": [
                    "total Q",
                    "larger L",
                    "smaller L",
                    "larger block count",
                    "smaller block count",
                    "lexicographic forward words",
                ],
            },
            "codeword_count": len(blocks),
            "address_count": len(addresses),
            "equivalence_class_count": len(grouped),
            "equivalence_class_size_distribution": {
                str(key): value for key, value in sorted(class_sizes.items())
            },
            "collision_group_count": sum(value > 1 for value in class_sizes.elements()),
            "collision_pair_count": len(collision_pairs),
            "maximum_collision_multiplicity": max(class_sizes),
            "positive_rewrite_edge_count": len(edges),
            "reducible_address_count": len(reducible),
            "irreducible_address_count": len(addresses) - len(reducible),
            "rewrite_k_distribution": {str(key): value for key, value in sorted(k_distribution.items())},
            "rewrite_m_sign_distribution": dict(sorted(m_signs.items())),
            "rewrite_m_range": [min(edge[3] for edge in edges), max(edge[3] for edge in edges)],
            "minimal_reducible_prefix_count": len(minimal_reducible),
            "minimal_reducible_Q_distribution": {
                str(key): value
                for key, value in sorted(Counter(row.odd_count for row in minimal_reducible).items())
            },
            "finite_normal_forms": {
                "directed_cycle_count": 0,
                "nonunique_normal_form_count": len(nonconfluent),
                "unique_normal_form_count": len(grouped),
                "interpretation": "Finite confluence is verified only for the complete Q<=13 address universe.",
            },
            "fixed_block_count_layers": fixed_block_rows,
            "least_collision": {
                "a": address_record(first_a),
                "d": address_record(first_d),
                "k": first_rewrite[0],
                "m": first_rewrite[1],
                "canonical_target_source": first_rewrite[2],
                "canonical_larger_source": first_d.source_positive,
                "common_endpoint": first_a.endpoint_positive,
                "identity": "F_d(2*x+1)=F_a(x)",
            },
            "pressure_by_block_count": pressure_rows,
            "address_rows_sha256": address_digest.hexdigest(),
            "rewrite_rows_sha256": rewrite_digest.hexdigest(),
        },
        "interpretation_boundary": {
            "general_confluence": "OPEN",
            "asymptotic_irreducible_pressure": "OPEN",
            "transfer_operator": "No finite closed transfer operator is accepted; right closure alone changes a finite prefix mass, not an asymptotic exponent.",
        },
        "proves_collatz": False,
    }
    return report, blocks


def example_address(blocks: list[Block], codes: tuple[str, ...]) -> Address:
    by_code = {block.code: block for block in blocks}
    result: Address | None = None
    for code in codes:
        result = append_block(result, by_code[code])
    if result is None:
        raise AssertionError("empty example")
    return result


def theory_artifact(blocks: list[Block]) -> dict[str, object]:
    a4 = example_address(blocks, ("1", "011", "1"))
    d4 = example_address(blocks, ("001111",))
    a13 = example_address(blocks, ("1", "000111111", "010011111"))
    d13 = example_address(blocks, ("00001011111111", "011", "011"))

    def coalescent_example(a: Address, d: Address, supplied_x: int | None = None) -> dict[str, object]:
        rewrite = pair_rewrite(d, a)
        if rewrite is None:
            raise AssertionError("example rewrite")
        k, m, canonical_x = rewrite
        starts = [canonical_x]
        if supplied_x is not None:
            starts.append(supplied_x)
        rows = []
        for x in starts:
            y = (1 << k) * x + m
            trace_a, bits_a = literal_trace(x, a.forward)
            trace_d, bits_d = literal_trace(y, d.forward)
            if trace_a[-1] != trace_d[-1]:
                raise AssertionError("example coalescence")
            rows.append(
                {
                    "x": x,
                    "y": y,
                    "endpoint": trace_a[-1],
                    "literal_a": bits_a,
                    "literal_d": bits_d,
                    "trace_a_sha256": hashlib.sha256(",".join(map(str, trace_a)).encode("ascii")).hexdigest(),
                    "trace_d_sha256": hashlib.sha256(",".join(map(str, trace_d)).encode("ascii")).hexdigest(),
                }
            )
        return {
            "a": address_record(a),
            "d": address_record(d),
            "k": k,
            "m": m,
            "correction_identity": f"2^{k}*B(a)-B(d)={m}*3^{a.odd_count}",
            "instances": rows,
        }

    # The minimum collision is not a left congruence under the block 110.
    prefix = example_address(blocks, ("011",))
    left_a = example_address(blocks, prefix.codes + a4.codes)
    left_d = example_address(blocks, prefix.codes + d4.codes)
    if left_a.endpoint_residue == left_d.endpoint_residue:
        raise AssertionError("left-congruence obstruction disappeared")

    return {
        "format": "collatz-phase14-coalescent-theory-v1",
        "P81": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "F_d(2^k*x+m)=F_a(x) identically iff Q(a)=Q(d), L(d)=L(a)+k, and 2^k*B(a)-B(d)=m*3^Q.",
            "cylinder_legality": "Under the identity, every integer x in the a-cylinder maps to 2^k*x+m in the d-cylinder; positivity and source descent are separate inequalities.",
            "sign_cases": {
                "m_positive": "For k>=1 and x>0, y=2^k*x+m is positive and larger.",
                "m_zero": "For k>=1 this is the leading-zero lift y=2^k*x; it is affine-legal but a renewal forward address cannot start with zero.",
                "m_negative": "Require y>0 and (2^k-1)*x>-m; affine equality alone supplies neither condition.",
                "k_zero": "The relation becomes the translation identity B(a)-B(d)=m*3^Q.",
            },
            "safety_boundary": "Affine equality does not imply renewal legality. If a and d are renewal addresses, a is coefficient-safe; after coalescence its coefficient surplus is k*log(2) above d, so a safe common future remains safe.",
        },
        "P82": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "If positive counterexample sources with Delta_n>0 for all n and Delta_n->infinity exist, the least such source has no initial renewal address admitting a uniform positive downward coalescent rewrite.",
            "right_ideal": "If d rewrites to a, then d|b rewrites to a|b for every common renewal suffix b; reducibility is a right ideal.",
            "termination": "Every accepted edge strictly decreases the least positive source representative, so directed rewrite cycles are impossible.",
            "external_boundary": "Applying this reduction to every nonperiodic counterexample uses EXT07/P74 to supply a permanent-safe discrepancy-escaping source.",
        },
        "examples": {
            "minimum_Q4": coalescent_example(a4, d4),
            "fixed_three_block_Q13": coalescent_example(a13, d13, supplied_x=886143),
        },
        "NG24": {
            "repository_status": "REFUTED",
            "hypothesis": "Coalescent endpoint equivalence is a two-sided congruence under renewal-block concatenation.",
            "counterexample": {
                "base_a": a4.forward,
                "base_d": d4.forward,
                "common_endpoint_residue_mod_3^4": a4.endpoint_residue,
                "left_prefix": prefix.forward,
                "prefixed_a_endpoint_residue_mod_3^6": left_a.endpoint_residue,
                "prefixed_d_endpoint_residue_mod_3^6": left_d.endpoint_residue,
            },
            "surviving_statement": "Right concatenation is exact; left concatenation can destroy equivalence.",
        },
        "what_this_result_does_not_prove": "The rewrite reduction does not prove that every renewal address is reducible, establish global confluence, prove P80, exclude H72, or address nontrivial cycles.",
        "proves_collatz": False,
    }


def threshold_audit(maximum_q: int) -> dict[str, object]:
    blocks = codewords(maximum_q)
    minima: dict[int, tuple[Fraction, Block]] = {}
    digest = hashlib.sha256()
    violations = 0
    for block in blocks:
        if block.forward == "1":
            continue
        run = len(block.forward) - len(block.forward.lstrip("1"))
        ratio = Fraction(block.correction + (1 << block.length), 3**block.odd_count)
        general = Fraction(5, 3) - Fraction(2, 3) ** run
        if not ratio > general:
            violations += 1
        if run not in minima or ratio < minima[run][0]:
            minima[run] = (ratio, block)
        digest.update(
            f"{block.code}|{block.forward}|{block.length}|{block.odd_count}|{block.correction}|{run}|{ratio.numerator}/{ratio.denominator}\n".encode(
                "ascii"
            )
        )
    return {
        "maximum_Q": maximum_q,
        "block_count": len(blocks),
        "general_bound_violation_count": violations,
        "minimum_by_initial_one_run": [
            {
                "r": run,
                "R": encoded_fraction(value),
                "word": block.forward,
                "Q": block.odd_count,
                "L": block.length,
            }
            for run, (value, block) in sorted(minima.items())
        ],
        "row_digest_sha256": digest.hexdigest(),
    }


def auxiliary_artifact(maximum_q: int) -> dict[str, object]:
    return {
        "format": "collatz-phase14-auxiliary-lemmas-v1",
        "P83": {
            "repository_status": "VERIFIED_THEOREM",
            "thresholds": {
                "r=2": "R(w)>=13/9, equality iff w=110",
                "r=3": "R(w)>=137/81, equality iff w=111010",
                "r>=4": "R(w)>=43/27, equality iff w=111100",
                "general": "R(w)>5/3-(2/3)^r",
            },
            "proof_boundary": "The proof minimizes B by adjacent exchange at fixed initial run. For Q>r it obtains R>5/3+(2/3)^r-2(2/3)^Q, an increasing bound in Q; Q=3,5 are impossible and the exact boundary cases Q=2,4,6 give the stated unique equalities.",
        },
        "P84": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For a legal nontrivial renewal block, z-z'>1/(12U+1), where z=(h-1)/(S+1), U=(S+1)/4.",
            "summability": "Along an infinite legal renewal orbit, sum over nontrivial blocks of 1/(12U_i+1) is at most z_0 and hence finite.",
            "proof_boundary": "Use R>=13/9, h>R, the exact Phase 13 decrement, and 4/[9(S+1)]>1/(3S+4).",
            "H72_boundary": "This is compatible with rapidly growing U_i and supplies no divergent lower bound, so it does not exclude H72.",
        },
        "P85": {
            "repository_status": "VERIFIED_THEOREM",
            "hypotheses": "P76 positive nonperiodic permanent-safe odd orbit with sum 1/x_n finite; n>=1 and a_n>=1.",
            "statement": [
                "If H_n=b_n/q_n is reduced, then q_n>2^(E_n+1)/(x_0+2h_0).",
                "gcd(B_n,3^n-2^E_n)<(x_0+2h_0)2^a_n.",
            ],
            "proof_boundary": "a_n>=1 gives lambda_n<1/2 and H_n<2h_0. The positive integer q_n(H_n+x_0) is divisible by 2^(E_n+1). The gcd bound follows from D_n/q_n and 2^(a_n+theta_n)-1<2^(a_n+1).",
            "eventual_scope": "Under the reciprocal-summability hypothesis, a_n tends to infinity, so the inequalities hold for every sufficiently large n.",
            "unqualified_small_n_candidate": "OPEN; this phase does not accept the same denominator bound for exceptional indices with a_n=0.",
            "diophantine_boundary": "The bound is only exponential in E_n with an orbit-dependent constant and gives neither algebraicity nor a height exponent exceeding two; Roth, Ridout, and the subspace theorem still do not yield a contradiction.",
        },
        "finite_threshold_audit": threshold_audit(maximum_q),
        "proves_collatz": False,
    }


def normalized_odd(value: int) -> int:
    return value // (value & -value)


def parity_prefix(source: int, length: int) -> str:
    bits = []
    value = source
    for _ in range(length):
        bits.append(str(value & 1))
        value = (3 * value + 1) // 2 if value & 1 else value // 2
    return "".join(bits)


def adversarial_seeds() -> list[tuple[str, int]]:
    rows = [("2^m-1", (1 << exponent) - 1) for exponent in range(3, 25)]
    rows.extend(("8^m-5", 8**exponent - 5) for exponent in range(1, 11))
    for count in range(1, 11):
        for mask in range(1 << count):
            word = "".join("111" if mask & (1 << index) else "110" for index in range(count))
            rows.append(("(110|111)^*", int(word, 2)))
    rows.extend((("A=11101", int(A_BITS, 2)), ("B=1100", int(B_BITS, 2))))
    rows.extend(
        ("A^rB^s", int(A_BITS * r + B_BITS * s, 2))
        for r in range(1, 9)
        for s in range(1, 9)
    )
    return rows


def adversarial_artifact() -> dict[str, object]:
    digest = hashlib.sha256()
    counts: Counter[str] = Counter()
    for family, raw in adversarial_seeds():
        source = normalized_odd(raw)
        word = parity_prefix(source, 24)
        correction = word_constant(word)
        q = word.count("1")
        residue = (-correction * pow(3**q, -1, 1 << 24)) % (1 << 24)
        if source % (1 << 24) != residue:
            raise AssertionError("adversarial source residue")
        counts[family] += 1
        digest.update(f"{family}|{raw}|{source}|{word}|{correction}|{residue}\n".encode("ascii"))
    macro_B = word_constant(MACRO_ZERO)
    macro_Q = MACRO_ZERO.count("1")
    macro_r2 = (-macro_B * pow(3**macro_Q, -1, 1 << len(MACRO_ZERO))) % (
        1 << len(MACRO_ZERO)
    )
    return {
        "format": "collatz-phase14-adversarial-v1",
        "E23_regression": {
            "prefix_length": 24,
            "instance_count": sum(counts.values()),
            "family_counts": dict(sorted(counts.items())),
            "row_digest_sha256": digest.hexdigest(),
            "phase7_macro_zero": {
                "word": MACRO_ZERO,
                "L": len(MACRO_ZERO),
                "Q": macro_Q,
                "B": macro_B,
                "source_residue": macro_r2,
            },
            "named_obstruction_boundaries": {
                "NG21": "The coprime-to-6 saturator is not a renewal-address source and is not excluded.",
                "NG22": "The formal odd 2-adic sources are not positive ordinary sources and are not excluded.",
                "NG23": "The u=1,H=2 raw-Haar obstruction remains valid; rewrites do not remove the one-block address.",
            },
        },
        "proves_collatz": False,
    }


def obstruction_report(path: Path) -> None:
    path.write_text(
        """# Phase 14 obstruction report

Phase 14 does not prove or disprove the Collatz conjecture.

## Quotient obstruction

Coalescent equivalence is preserved by appending the same renewal suffix, but
not by prepending an arbitrary renewal block.  The minimum collision
`11101 ~ 111100` has common endpoint residue 20 modulo `3^4`; prepending
`110` gives endpoint residues 263 and 587 modulo `3^6`.  Therefore a quotient
that remembers only the coalescent class is not a two-sided block transfer
operator.  This is NG24.

## Finite pressure boundary

The exhaustive `Q<=13` graph has unique finite normal forms and fewer
irreducible addresses at every audited block depth.  This is finite evidence.
Right-ideal closure of a finite rewrite list changes only a prefix mass; no
closed all-depth recursion or asymptotic irreducible pressure was proved.

## Moving-shadow boundary

The proposed reduced-denominator and gcd bounds are proved once `a_n>=1`,
and hence eventually under P76's reciprocal-summability hypothesis.  The
unqualified small-index case `a_n=0` is not accepted.

## What this result does not prove

- global rewrite confluence or a unique normal form at every `Q`;
- either anti-concentration premise in P80;
- exclusion of every positive permanent-safe source;
- H72 or exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
""",
        encoding="utf-8",
    )


def generate(artifact_dir: Path, maximum_q: int, threshold_q: int) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    rewrite, blocks = rewrite_audit(maximum_q)
    write_json(artifact_dir / "phase14_coalescent_theory.json", theory_artifact(blocks))
    write_json(artifact_dir / "phase14_rewrite_search.json", rewrite)
    write_json(artifact_dir / "phase14_auxiliary_lemmas.json", auxiliary_artifact(threshold_q))
    write_json(artifact_dir / "phase14_adversarial_regression.json", adversarial_artifact())
    obstruction_report(artifact_dir / "phase14_obstruction_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--max-total-q", type=int, default=13)
    parser.add_argument("--threshold-q", type=int, default=14)
    args = parser.parse_args()
    if args.max_total_q < 4 or args.threshold_q < args.max_total_q:
        parser.error("require threshold-q>=max-total-q>=4")
    generate(args.artifact_dir, args.max_total_q, args.threshold_q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
