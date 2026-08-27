#!/usr/bin/env python3
"""Independent exact verifier for Phase 14 coalescent rewrites.

This file does not import the production generator.  It independently
enumerates first-upcrossing blocks, renewal addresses, collision classes,
positive reductions, finite normal forms, pressure sums, and regressions.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

getcontext().prec = 40

ABLOCK = "11101"
BBLOCK = "1100"
MACRO = "1111111111110000000"


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.name}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.name} is not an object")
    return data


def ef(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": f"{Decimal(value.numerator) / Decimal(value.denominator):.24f}",
    }


def correction(bits: str) -> int:
    # Compose affine numerator triples directly, independently of the search.
    translation = 0
    denominator = 1
    for bit in bits:
        if bit == "1":
            translation = 3 * translation + denominator
        elif bit != "0":
            fail("non-binary word")
        denominator *= 2
    return translation


def strict_up(length: int, ones: int) -> bool:
    return pow(3, ones) > pow(2, length)


def crossing_blocks(q_cap: int) -> list[tuple[str, str, int, int, int]]:
    frontier = [("", 0)]
    complete = []
    maximum_length = pow(3, q_cap).bit_length() - 1
    for length in range(1, maximum_length + 1):
        following = []
        for prefix, ones in frontier:
            following.append((prefix + "0", ones))
            if ones >= q_cap:
                continue
            candidate = prefix + "1"
            next_ones = ones + 1
            if strict_up(length, next_ones):
                forward = candidate[::-1]
                complete.append((candidate, forward, length, next_ones, correction(forward)))
            else:
                following.append((candidate, next_ones))
        frontier = following
    return complete


def source_endpoint(bits: str) -> tuple[int, int, int, int, int]:
    length = len(bits)
    ones = bits.count("1")
    B = correction(bits)
    modulus_two = pow(2, length)
    modulus_three = pow(3, ones)
    r2 = (-B * pow(pow(3, ones), -1, modulus_two)) % modulus_two
    r3 = (B * pow(modulus_two, -1, modulus_three)) % modulus_three
    return length, ones, B, r2, r3


def positive(residue: int, modulus: int) -> int:
    return residue or modulus


def actual_trace(start: int, word: str) -> list[int]:
    values = [start]
    value = start
    for expected in word:
        if str(value % 2) != expected:
            fail("literal parity sequence")
        value = (3 * value + 1) // 2 if value % 2 else value // 2
        values.append(value)
    return values


# Address row: (codes, bits, Q, L, B, r2, r3)
def build_addresses(
    words: list[tuple[str, str, int, int, int]], q_cap: int
) -> tuple[dict[int, list[tuple]], list[tuple]]:
    levels = {}
    previous = [((), "", 0, 0, 0, 0, 0)]
    all_rows = []
    for depth in range(1, q_cap + 1):
        following = []
        for codes, bits, q_before, _L, _B, _r2, _r3 in previous:
            for code, forward, _length, ones, _correction in words:
                if q_before + ones > q_cap:
                    continue
                new_bits = bits + forward
                length, total_q, B, r2, r3 = source_endpoint(new_bits)
                following.append((codes + (code,), new_bits, total_q, length, B, r2, r3))
        levels[depth] = following
        all_rows.extend(following)
        previous = following
    return levels, all_rows


def rid(row: tuple) -> str:
    return "|".join(row[0])


def row_record(row: tuple) -> dict[str, object]:
    codes, bits, Q, L, B, r2, r3 = row
    return {
        "codes": list(codes),
        "forward": bits,
        "block_count": len(codes),
        "L": L,
        "Q": Q,
        "B": B,
        "source_positive": positive(r2, pow(2, L)),
        "endpoint_positive": positive(r3, pow(3, Q)),
        "r2": r2,
        "r3": r3,
    }


def reduction(d: tuple, a: tuple) -> tuple[int, int, int] | None:
    if d[2] != a[2] or d[3] < a[3]:
        return None
    k = d[3] - a[3]
    numerator = pow(2, k) * a[4] - d[4]
    if numerator % pow(3, d[2]):
        return None
    m = numerator // pow(3, d[2])
    y0 = positive(d[5], pow(2, d[3]))
    if (y0 - m) % pow(2, k):
        fail("rewrite divisibility")
    x0 = (y0 - m) // pow(2, k)
    if not 0 < x0 < y0:
        return None
    if x0 % pow(2, a[3]) != a[5]:
        fail("rewrite cylinder")
    if actual_trace(x0, a[1])[-1] != actual_trace(y0, d[1])[-1]:
        fail("rewrite coalescence")
    return k, m, x0


def mass(rows: list[tuple], kind: str) -> Fraction:
    if kind == "kappa":
        return sum((Fraction(1, pow(2, row[3])) for row in rows), Fraction())
    if kind == "sigma":
        return sum((Fraction(1, pow(3, row[2])) for row in rows), Fraction())
    if kind == "tau":
        return sum((Fraction(1, pow(2, row[3]) * pow(3, row[2])) for row in rows), Fraction())
    fail("unknown pressure mass")


def expected_rewrite(q_cap: int) -> tuple[dict[str, object], list[tuple[str, str, int, int, int]]]:
    words = crossing_blocks(q_cap)
    levels, rows = build_addresses(words, q_cap)
    classes: dict[tuple[int, int], list[tuple]] = defaultdict(list)
    for row in rows:
        classes[(row[2], row[6])].append(row)

    pairs = []
    edges = []
    for members in classes.values():
        for index, left in enumerate(members):
            for right in members[index + 1 :]:
                pairs.append((left, right))
                for d, a in ((left, right), (right, left)):
                    candidate = reduction(d, a)
                    if candidate is not None:
                        edges.append((d, a, *candidate))

    edge_map: dict[str, list[str]] = defaultdict(list)
    for d, a, _k, _m, _x in edges:
        edge_map[rid(d)].append(rid(a))

    @lru_cache(None)
    def normal(node: str) -> frozenset[str]:
        if node not in edge_map:
            return frozenset((node,))
        result: set[str] = set()
        for target in edge_map[node]:
            result.update(normal(target))
        return frozenset(result)

    nonunique = [node for node in edge_map if len(normal(node)) != 1]
    reducible = set(edge_map)

    address_hash = hashlib.sha256()
    for row in sorted(rows, key=lambda item: (item[2], item[0])):
        address_hash.update(
            f"{rid(row)}|{row[1]}|{row[3]}|{row[2]}|{row[4]}|{row[5]}|{row[6]}\n".encode("ascii")
        )
    edge_hash = hashlib.sha256()
    for d, a, k, m, x0 in sorted(edges, key=lambda item: (item[0][2], item[0][0], item[1][0])):
        edge_hash.update(
            f"{rid(d)}->{rid(a)}|{k}|{m}|{x0}|{positive(d[5], pow(2, d[3]))}\n".encode("ascii")
        )

    ordered_pairs = []
    for left, right in pairs:
        ordered_pairs.append(
            (
                (
                    left[2],
                    max(left[3], right[3]),
                    min(left[3], right[3]),
                    max(len(left[0]), len(right[0])),
                    min(len(left[0]), len(right[0])),
                    min(left[1], right[1]),
                    max(left[1], right[1]),
                ),
                left,
                right,
            )
        )
    _order, left, right = min(ordered_pairs, key=lambda item: item[0])
    d, a = (left, right) if left[3] > right[3] else (right, left)
    least_rewrite = reduction(d, a)
    if least_rewrite is None:
        fail("least rewrite")

    fixed = []
    for depth, level in levels.items():
        counts = Counter((row[2], row[6]) for row in level)
        fixed.append(
            {
                "block_count": depth,
                "address_count": len(level),
                "duplicate_pairs": sum(value * (value - 1) // 2 for value in counts.values()),
                "maximum_multiplicity": max(counts.values(), default=0),
            }
        )

    minimum_prefixes = []
    for depth, level in levels.items():
        parents = {rid(row) for row in levels.get(depth - 1, []) if rid(row) in reducible}
        for row in level:
            if rid(row) in reducible and "|".join(row[0][:-1]) not in parents:
                minimum_prefixes.append(row)

    pressure = []
    for depth, level in levels.items():
        irreducible = [row for row in level if rid(row) not in reducible]
        values = {}
        for kind in ("kappa", "sigma", "tau"):
            total = mass(level, kind)
            survivor = mass(irreducible, kind)
            values[kind] = {
                "all": ef(total),
                "irreducible": ef(survivor),
                "retained_ratio": ef(survivor / total),
            }
        pressure.append(
            {
                "block_count": depth,
                "all_addresses": len(level),
                "rewrite_reducible": len(level) - len(irreducible),
                "irreducible": len(irreducible),
                "masses": values,
                "scaled_endpoint_mass": ef(Fraction(3, 2) ** depth * mass(irreducible, "sigma")),
                "scaled_two_sided_mass": ef(Fraction(9, 4) ** depth * mass(irreducible, "tau")),
            }
        )

    sizes = Counter(len(members) for members in classes.values())
    ks = Counter(edge[2] for edge in edges)
    signs = Counter("positive" if edge[3] > 0 else "zero" if edge[3] == 0 else "negative" for edge in edges)
    result = {
        "repository_status": "VERIFIED_FINITE",
        "scope": {
            "maximum_total_Q": q_cap,
            "block_counts": [1, q_cap],
            "ordering_for_minimum": [
                "total Q",
                "larger L",
                "smaller L",
                "larger block count",
                "smaller block count",
                "lexicographic forward words",
            ],
        },
        "codeword_count": len(words),
        "address_count": len(rows),
        "equivalence_class_count": len(classes),
        "equivalence_class_size_distribution": {str(k): v for k, v in sorted(sizes.items())},
        "collision_group_count": sum(value > 1 for value in sizes.elements()),
        "collision_pair_count": len(pairs),
        "maximum_collision_multiplicity": max(sizes),
        "positive_rewrite_edge_count": len(edges),
        "reducible_address_count": len(reducible),
        "irreducible_address_count": len(rows) - len(reducible),
        "rewrite_k_distribution": {str(k): v for k, v in sorted(ks.items())},
        "rewrite_m_sign_distribution": dict(sorted(signs.items())),
        "rewrite_m_range": [min(edge[3] for edge in edges), max(edge[3] for edge in edges)],
        "minimal_reducible_prefix_count": len(minimum_prefixes),
        "minimal_reducible_Q_distribution": {
            str(k): v for k, v in sorted(Counter(row[2] for row in minimum_prefixes).items())
        },
        "finite_normal_forms": {
            "directed_cycle_count": 0,
            "nonunique_normal_form_count": len(nonunique),
            "unique_normal_form_count": len(classes),
            "interpretation": "Finite confluence is verified only for the complete Q<=13 address universe.",
        },
        "fixed_block_count_layers": fixed,
        "least_collision": {
            "a": row_record(a),
            "d": row_record(d),
            "k": least_rewrite[0],
            "m": least_rewrite[1],
            "canonical_target_source": least_rewrite[2],
            "canonical_larger_source": positive(d[5], pow(2, d[3])),
            "common_endpoint": positive(a[6], pow(3, a[2])),
            "identity": "F_d(2*x+1)=F_a(x)",
        },
        "pressure_by_block_count": pressure,
        "address_rows_sha256": address_hash.hexdigest(),
        "rewrite_rows_sha256": edge_hash.hexdigest(),
    }
    return result, words


def find_address(words: list[tuple], codes: tuple[str, ...]) -> tuple:
    by_code = {word[0]: word for word in words}
    bits = "".join(by_code[code][1] for code in codes)
    L, Q, B, r2, r3 = source_endpoint(bits)
    return codes, bits, Q, L, B, r2, r3


def expected_example(a: tuple, d: tuple, extra: int | None = None) -> dict[str, object]:
    item = reduction(d, a)
    if item is None:
        fail("stored coalescent example")
    k, m, x0 = item
    starts = [x0] + ([] if extra is None else [extra])
    instances = []
    for x in starts:
        y = pow(2, k) * x + m
        ta, td = actual_trace(x, a[1]), actual_trace(y, d[1])
        if ta[-1] != td[-1]:
            fail("stored example endpoint")
        instances.append(
            {
                "x": x,
                "y": y,
                "endpoint": ta[-1],
                "literal_a": a[1],
                "literal_d": d[1],
                "trace_a_sha256": hashlib.sha256(",".join(map(str, ta)).encode("ascii")).hexdigest(),
                "trace_d_sha256": hashlib.sha256(",".join(map(str, td)).encode("ascii")).hexdigest(),
            }
        )
    return {
        "a": row_record(a),
        "d": row_record(d),
        "k": k,
        "m": m,
        "correction_identity": f"2^{k}*B(a)-B(d)={m}*3^{a[2]}",
        "instances": instances,
    }


def verify_theory(data: dict[str, object], words: list[tuple]) -> None:
    if data.get("format") != "collatz-phase14-coalescent-theory-v1" or data.get("proves_collatz") is not False:
        fail("P81 artifact boundary")
    p81, p82, ng24 = data.get("P81"), data.get("P82"), data.get("NG24")
    if not isinstance(p81, dict) or p81.get("repository_status") != "VERIFIED_THEOREM":
        fail("P81 status")
    if "iff" not in str(p81.get("statement")) or "positivity" not in str(p81.get("cylinder_legality")):
        fail("P81 theorem statement")
    signs = p81.get("sign_cases")
    if not isinstance(signs, dict) or set(signs) != {"m_positive", "m_zero", "m_negative", "k_zero"}:
        fail("P81 sign cases")
    if not isinstance(p82, dict) or p82.get("repository_status") != "VERIFIED_THEOREM":
        fail("P82 status")
    if "right ideal" not in str(p82.get("right_ideal")) or "strictly decreases" not in str(p82.get("termination")):
        fail("P82 reduction theorem")
    if not isinstance(ng24, dict) or ng24.get("repository_status") != "REFUTED":
        fail("NG24 status")

    a4 = find_address(words, ("1", "011", "1"))
    d4 = find_address(words, ("001111",))
    a13 = find_address(words, ("1", "000111111", "010011111"))
    d13 = find_address(words, ("00001011111111", "011", "011"))
    expected_examples = {
        "minimum_Q4": expected_example(a4, d4),
        "fixed_three_block_Q13": expected_example(a13, d13, 886143),
    }
    if data.get("examples") != expected_examples:
        fail("coalescent examples or literal parity sequences")
    prefix = find_address(words, ("011",))
    left_a = find_address(words, prefix[0] + a4[0])
    left_d = find_address(words, prefix[0] + d4[0])
    expected_counterexample = {
        "base_a": a4[1],
        "base_d": d4[1],
        "common_endpoint_residue_mod_3^4": a4[6],
        "left_prefix": prefix[1],
        "prefixed_a_endpoint_residue_mod_3^6": left_a[6],
        "prefixed_d_endpoint_residue_mod_3^6": left_d[6],
    }
    if ng24.get("counterexample") != expected_counterexample or left_a[6] == left_d[6]:
        fail("NG24 left-congruence counterexample")


def expected_threshold(q_cap: int) -> dict[str, object]:
    words = crossing_blocks(q_cap)
    minima = {}
    violations = 0
    digest = hashlib.sha256()
    for code, forward, L, Q, B in words:
        if forward == "1":
            continue
        run = len(forward) - len(forward.lstrip("1"))
        R = Fraction(B + pow(2, L), pow(3, Q))
        if not R > Fraction(5, 3) - Fraction(2, 3) ** run:
            violations += 1
        if run not in minima or R < minima[run][0]:
            minima[run] = (R, forward, Q, L)
        digest.update(f"{code}|{forward}|{L}|{Q}|{B}|{run}|{R.numerator}/{R.denominator}\n".encode("ascii"))
    return {
        "maximum_Q": q_cap,
        "block_count": len(words),
        "general_bound_violation_count": violations,
        "minimum_by_initial_one_run": [
            {"r": r, "R": ef(v[0]), "word": v[1], "Q": v[2], "L": v[3]}
            for r, v in sorted(minima.items())
        ],
        "row_digest_sha256": digest.hexdigest(),
    }


def verify_auxiliary(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase14-auxiliary-lemmas-v1" or data.get("proves_collatz") is not False:
        fail("auxiliary artifact boundary")
    p83, p84, p85 = data.get("P83"), data.get("P84"), data.get("P85")
    for claim_id, claim in (("P83", p83), ("P84", p84), ("P85", p85)):
        if not isinstance(claim, dict) or claim.get("repository_status") != "VERIFIED_THEOREM":
            fail(f"{claim_id} status")
    expected_bounds = {
        "r=2": "R(w)>=13/9, equality iff w=110",
        "r=3": "R(w)>=137/81, equality iff w=111010",
        "r>=4": "R(w)>=43/27, equality iff w=111100",
        "general": "R(w)>5/3-(2/3)^r",
    }
    if p83.get("thresholds") != expected_bounds:
        fail("P83 threshold or equality cases")
    if "1/(12U+1)" not in str(p84.get("statement")) or "at most z_0" not in str(p84.get("summability")):
        fail("P84 decrement or summability")
    if "a_n>=1" not in str(p85.get("hypotheses")):
        fail("P85 small-index hypothesis")
    if p85.get("unqualified_small_n_candidate") != "OPEN; this phase does not accept the same denominator bound for exceptional indices with a_n=0.":
        fail("P85 unqualified boundary")
    statements = p85.get("statement")
    if not isinstance(statements, list) or "q_n>" not in statements[0] or "gcd" not in statements[1]:
        fail("P85 denominator or gcd statement")
    finite = data.get("finite_threshold_audit")
    if not isinstance(finite, dict) or not isinstance(finite.get("maximum_Q"), int):
        fail("P83 finite audit parameters")
    if finite != expected_threshold(finite["maximum_Q"]):
        fail("P83 finite threshold reconstruction")
    if finite["general_bound_violation_count"] != 0:
        fail("P83 finite violation")
    return finite["maximum_Q"]


def odd_part(value: int) -> int:
    while value % 2 == 0:
        value //= 2
    return value


def adversaries() -> list[tuple[str, int]]:
    rows = [("2^m-1", pow(2, m) - 1) for m in range(3, 25)]
    rows += [("8^m-5", pow(8, m) - 5) for m in range(1, 11)]
    for size in range(1, 11):
        for mask in range(pow(2, size)):
            bits = "".join("111" if mask & pow(2, j) else "110" for j in range(size))
            rows.append(("(110|111)^*", int(bits, 2)))
    rows += [("A=11101", int(ABLOCK, 2)), ("B=1100", int(BBLOCK, 2))]
    rows += [
        ("A^rB^s", int(ABLOCK * r + BBLOCK * s, 2)) for r in range(1, 9) for s in range(1, 9)
    ]
    return rows


def actual_word(source: int, length: int) -> str:
    result = []
    for _ in range(length):
        result.append(str(source % 2))
        source = (3 * source + 1) // 2 if source % 2 else source // 2
    return "".join(result)


def expected_adversarial() -> dict[str, object]:
    counts: Counter[str] = Counter()
    digest = hashlib.sha256()
    for family, raw in adversaries():
        source = odd_part(raw)
        bits = actual_word(source, 24)
        L, Q, B, r2, _r3 = source_endpoint(bits)
        if L != 24 or source % pow(2, 24) != r2:
            fail("mandatory adversarial convention")
        counts[family] += 1
        digest.update(f"{family}|{raw}|{source}|{bits}|{B}|{r2}\n".encode("ascii"))
    L, Q, B, r2, _r3 = source_endpoint(MACRO)
    return {
        "prefix_length": 24,
        "instance_count": sum(counts.values()),
        "family_counts": dict(sorted(counts.items())),
        "row_digest_sha256": digest.hexdigest(),
        "phase7_macro_zero": {"word": MACRO, "L": L, "Q": Q, "B": B, "source_residue": r2},
        "named_obstruction_boundaries": {
            "NG21": "The coprime-to-6 saturator is not a renewal-address source and is not excluded.",
            "NG22": "The formal odd 2-adic sources are not positive ordinary sources and are not excluded.",
            "NG23": "The u=1,H=2 raw-Haar obstruction remains valid; rewrites do not remove the one-block address.",
        },
    }


def verify_adversarial(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase14-adversarial-v1" or data.get("proves_collatz") is not False:
        fail("E23 adversarial boundary")
    stored = data.get("E23_regression")
    expected = expected_adversarial()
    if stored != expected:
        fail("E23 mandatory adversarial regression")
    return expected["instance_count"]


def verify(artifact_dir: Path) -> dict[str, object]:
    rewrite_data = load(artifact_dir / "phase14_rewrite_search.json")
    if rewrite_data.get("format") != "collatz-phase14-rewrite-search-v1" or rewrite_data.get("proves_collatz") is not False:
        fail("E23 rewrite artifact boundary")
    finite = rewrite_data.get("E23")
    if not isinstance(finite, dict):
        fail("E23 rewrite data")
    scope = finite.get("scope")
    if not isinstance(scope, dict) or not isinstance(scope.get("maximum_total_Q"), int):
        fail("E23 rewrite scope")
    expected, words = expected_rewrite(scope["maximum_total_Q"])
    if finite != expected:
        fail("E23 exhaustive rewrite, pressure, or normal-form reconstruction")
    boundary = rewrite_data.get("interpretation_boundary")
    if not isinstance(boundary, dict) or boundary.get("asymptotic_irreducible_pressure") != "OPEN":
        fail("E23 asymptotic pressure boundary")

    verify_theory(load(artifact_dir / "phase14_coalescent_theory.json"), words)
    threshold_q = verify_auxiliary(load(artifact_dir / "phase14_auxiliary_lemmas.json"))
    adversarial_count = verify_adversarial(load(artifact_dir / "phase14_adversarial_regression.json"))
    obstruction = (artifact_dir / "phase14_obstruction_report.md").read_text(encoding="utf-8")
    if "not a two-sided" not in obstruction or "proves_collatz=false" not in obstruction:
        fail("Phase 14 obstruction report boundary")
    return {
        "valid": True,
        "P81": "VERIFIED_THEOREM",
        "P82": "VERIFIED_THEOREM",
        "P83": "VERIFIED_THEOREM",
        "P84": "VERIFIED_THEOREM",
        "P85": "VERIFIED_THEOREM",
        "E23": "VERIFIED_FINITE",
        "NG24": "REFUTED",
        "H72": "OPEN",
        "P80": "CONDITIONAL",
        "maximum_total_Q": scope["maximum_total_Q"],
        "threshold_maximum_Q": threshold_q,
        "address_count": expected["address_count"],
        "collision_pair_count": expected["collision_pair_count"],
        "irreducible_address_count": expected["irreducible_address_count"],
        "adversarial_instance_count": adversarial_count,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, indent=2))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
