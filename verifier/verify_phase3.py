#!/usr/bin/env python3
"""Independent verifier for Phase 3 mixed-modulus certificates.

This file imports no search/model code. Split identities, reverse arithmetic,
forward paths, domains, and strict inequalities are reconstructed here.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


def ceiling(a: int, b: int) -> int:
    return -((-a) // b)


def three_adic_exponent(value: int) -> int:
    exponent = 0
    while value > 0 and value % 3 == 0:
        exponent += 1
        value //= 3
    return exponent


@dataclass(frozen=True, slots=True)
class Expected:
    steps: int
    residue: int
    input_coefficient: int
    image_constant: int
    image_coefficient: int
    parameter_minimum: int
    parity_word: str
    ternary_digits: tuple[int, ...]

    def compact(self) -> list[object]:
        return [
            self.steps,
            self.residue,
            self.input_coefficient,
            self.image_constant,
            self.image_coefficient,
            self.parameter_minimum,
            self.parity_word,
            list(self.ternary_digits),
        ]


def binary_children(parent: Expected) -> tuple[Expected, Expected]:
    children: list[Expected] = []
    for selector in (0, 1):
        residue = parent.residue + selector * parent.input_coefficient
        before_step = parent.image_constant + selector * parent.image_coefficient
        bit = before_step % 2
        if bit:
            constant = (3 * before_step + 1) // 2
            coefficient = 3 * parent.image_coefficient
        else:
            constant = before_step // 2
            coefficient = parent.image_coefficient
        children.append(
            Expected(
                parent.steps + 1,
                residue,
                2 * parent.input_coefficient,
                constant,
                coefficient,
                ceiling(parent.parameter_minimum - selector, 2),
                parent.parity_word + str(bit),
                parent.ternary_digits,
            )
        )
    return children[0], children[1]


def ternary_children(parent: Expected) -> tuple[Expected, Expected, Expected]:
    result: list[Expected] = []
    for selector in (0, 1, 2):
        result.append(
            Expected(
                parent.steps,
                parent.residue + selector * parent.input_coefficient,
                3 * parent.input_coefficient,
                parent.image_constant + selector * parent.image_coefficient,
                3 * parent.image_coefficient,
                ceiling(parent.parameter_minimum - selector, 3),
                parent.parity_word,
                parent.ternary_digits + (selector,),
            )
        )
    return result[0], result[1], result[2]


def binary_frontier(depth: int) -> Iterator[Expected]:
    def visit(node: Expected) -> Iterator[Expected]:
        if node.steps == depth:
            yield node
            return
        for child in binary_children(node):
            if child.image_coefficient >= child.input_coefficient:
                yield from visit(child)

    yield from visit(Expected(0, 0, 1, 0, 1, 2, "", ()))


def parse_stream(path: Path) -> tuple[dict[str, object], Iterator[list[object]], dict[str, object]]:
    stream = path.open("r", encoding="utf-8")
    first = stream.readline().rstrip("\n")
    marker = ',"records":['
    if not first.endswith(marker):
        stream.close()
        raise ValueError("invalid Phase 3 certificate header")
    header = json.loads(first[: -len(marker)] + "}")
    footer: dict[str, object] = {}

    def records() -> Iterator[list[object]]:
        try:
            for line_number, line in enumerate(stream, start=2):
                text = line.rstrip("\n")
                if text.startswith('null],"summary":'):
                    payload = text[len('null],"summary":') :]
                    if not payload.endswith("}"):
                        raise ValueError("malformed certificate footer")
                    footer.update(json.loads(payload[:-1]))
                    if stream.read(1):
                        raise ValueError("trailing certificate data")
                    return
                if not text.endswith(","):
                    raise ValueError(f"bad record framing on line {line_number}")
                record = json.loads(text[:-1])
                if not isinstance(record, list) or len(record) != 9:
                    raise ValueError(f"bad record on line {line_number}")
                yield record
            raise ValueError("certificate footer missing")
        finally:
            stream.close()

    return header, records(), footer


def check_reverse_merge(node: Expected, exponents: object, exponent_limit: int) -> tuple[int, int]:
    if not isinstance(exponents, list) or not exponents:
        raise ValueError("REVERSE_MERGE exponent list must be non-empty")
    if any(not isinstance(b, int) or b <= 0 for b in exponents):
        raise ValueError("REVERSE_MERGE exponents must be positive integers")
    if len(exponents) > three_adic_exponent(node.image_coefficient):
        raise ValueError("too many reverse odd steps")
    if sum(exponents) > exponent_limit:
        raise ValueError("reverse exponent-sum bound exceeded")

    constant = node.image_constant
    slope = node.image_coefficient
    for b in exponents:
        numerator = (1 << b) * constant - 1
        if numerator % 3 or slope % 3:
            raise ValueError("non-integral reverse predecessor")
        constant = numerator // 3
        slope = (1 << b) * slope // 3
        if constant <= 0:
            raise ValueError("non-positive reverse predecessor")

    if slope > node.input_coefficient:
        raise ValueError("smaller-family slope exceeds source slope")
    if constant + slope * node.parameter_minimum <= 0:
        raise ValueError("reverse family is not positive on the full domain")
    difference_at_minimum = (
        constant
        - node.residue
        + (slope - node.input_coefficient) * node.parameter_minimum
    )
    if difference_at_minimum >= 0:
        raise ValueError("reverse family is not strictly smaller")

    # Independently compose the claimed forward parity path. The b blocks are
    # traversed in reverse certificate order.
    forward_constant = constant
    forward_slope = slope
    for b in reversed(exponents):
        if forward_constant % 2 != 1 or forward_slope % 2 != 0:
            raise ValueError("claimed forward odd step is not fixed over the family")
        forward_constant = (3 * forward_constant + 1) // 2
        forward_slope = 3 * forward_slope // 2
        for _ in range(b - 1):
            if forward_constant % 2 or forward_slope % 2:
                raise ValueError("claimed forward even step is not fixed over the family")
            forward_constant //= 2
            forward_slope //= 2
    if (forward_constant, forward_slope) != (
        node.image_constant,
        node.image_coefficient,
    ):
        raise ValueError("forward affine reconstruction misses the source endpoint")
    return len(exponents), sum(exponents)


class Checker:
    def __init__(self, records: Iterator[list[object]], max_ternary: int, exponent_limit: int) -> None:
        self.records = records
        self.max_ternary = max_ternary
        self.exponent_limit = exponent_limit
        self.record_counts: Counter[int] = Counter()
        self.closed_counts: Counter[int] = Counter()
        self.split_counts: Counter[int] = Counter()
        self.open_counts: Counter[int] = Counter()
        self.path_distribution: Counter[tuple[int, int]] = Counter()

    def next_record(self) -> list[object]:
        try:
            return next(self.records)
        except StopIteration as error:
            raise ValueError("certificate tree ended early") from error

    def subtree(self, expected: Expected) -> None:
        record = self.next_record()
        if record[:8] != expected.compact():
            raise ValueError(f"unexpected lattice node {record[:8]} != {expected.compact()}")
        level = len(expected.ternary_digits)
        self.record_counts[level] += 1
        rule = record[8]
        if isinstance(rule, list) and len(rule) == 2 and rule[0] == "REVERSE_MERGE":
            key = check_reverse_merge(expected, rule[1], self.exponent_limit)
            self.closed_counts[level] += 1
            self.path_distribution[key] += 1
            return
        if rule == "TERNARY_SPLIT":
            if level >= self.max_ternary:
                raise ValueError("TERNARY_SPLIT exceeds configured depth")
            self.split_counts[level] += 1
            children = ternary_children(expected)
            # The distinct parameter residues 0,1,2 mod 3 prove disjointness;
            # the exact three-child recursion proves exhaustive coverage.
            for child in children:
                self.subtree(child)
            return
        if rule == "OPEN":
            if level != self.max_ternary:
                raise ValueError("OPEN before the final ternary level")
            self.open_counts[level] += 1
            return
        raise ValueError(f"unknown Phase 3 rule {rule!r}")


def coefficient_counts(max_depth: int) -> tuple[list[int], list[int]]:
    states: dict[int, int] = {0: 1}
    survivors = [1]
    crossings: list[int] = []
    for depth in range(1, max_depth + 1):
        next_states: dict[int, int] = defaultdict(int)
        failed = 0
        for odd_count, count in states.items():
            for bit in (0, 1):
                next_odds = odd_count + bit
                if pow(3, next_odds) >= 1 << depth:
                    next_states[next_odds] += count
                else:
                    failed += count
        states = dict(next_states)
        survivors.append(sum(states.values()))
        crossings.append(failed)
    return survivors, crossings


def verify_phase1_margins(path: Path) -> tuple[int, int]:
    checked = 0
    excluded = 0
    with path.open("r", encoding="utf-8") as stream:
        stream.readline()
        for line in stream:
            text = line.rstrip("\n")
            if text.startswith('null],"summary":'):
                break
            record = json.loads(text[:-1])
            k, r, y, q, word, rule = record
            if rule != "DESCENT" or k < 1 or not word.endswith("0"):
                continue
            parent_modulus = 1 << (k - 1)
            multiplier = pow(3, q)
            if not (parent_modulus <= multiplier < 2 * parent_modulus):
                continue
            selector = int(r >= parent_modulus)
            parent_r = r - selector * parent_modulus
            parent_y = 2 * y - selector * multiplier
            parameter_minimum = max(0, -((parent_r - 2) // parent_modulus))
            if parameter_minimum:
                excluded += 1
                continue
            margin = (
                2 * parent_r
                - parent_y
                + selector * (2 * parent_modulus - multiplier)
            )
            if selector != parent_y % 2 or margin <= 0:
                raise ValueError("Phase 1 boundary margin audit failed")
            checked += 1
    return checked, excluded


def compare_summary(checker: Checker, footer: dict[str, object]) -> None:
    mappings = [
        ("records_by_ternary_level", checker.record_counts),
        ("closed_by_ternary_level", checker.closed_counts),
        ("split_by_ternary_level", checker.split_counts),
        ("open_by_ternary_level", checker.open_counts),
    ]
    for field, actual in mappings:
        expected = {str(level): actual[level] for level in range(checker.max_ternary + 1)}
        if footer.get(field) != expected:
            raise ValueError(f"summary mismatch: {field}")
    distribution = [
        {"odd_steps": key[0], "exponent_sum": key[1], "count": count}
        for key, count in sorted(checker.path_distribution.items())
    ]
    if footer.get("reverse_path_distribution") != distribution:
        raise ValueError("summary reverse path distribution mismatch")
    if footer.get("open_count") != sum(checker.open_counts.values()):
        raise ValueError("summary OPEN count mismatch")
    if footer.get("proves_collatz") is not False:
        raise ValueError("partial Phase 3 certificate must not claim a proof")


def verify(certificate: Path, phase1_certificate: Path) -> dict[str, object]:
    header, records, footer = parse_stream(certificate)
    if header.get("format") != "collatz-phase3-mixed-merge-v1" or header.get("version") != 1:
        raise ValueError("unsupported Phase 3 certificate")
    binary_depth = header.get("binary_depth")
    max_ternary = header.get("max_ternary_refinements")
    exponent_limit = header.get("reverse_exponent_sum_limit")
    if not all(isinstance(value, int) for value in (binary_depth, max_ternary, exponent_limit)):
        raise ValueError("invalid Phase 3 bounds")
    assert isinstance(binary_depth, int)
    assert isinstance(max_ternary, int)
    assert isinstance(exponent_limit, int)
    checker = Checker(records, max_ternary, exponent_limit)
    binary_count = 0
    for node in binary_frontier(binary_depth):
        checker.subtree(node)
        binary_count += 1
    try:
        extra = next(records)
    except StopIteration:
        extra = None
    if extra is not None:
        raise ValueError("extra record after expected forest")
    compare_summary(checker, footer)

    survivors, crossings = coefficient_counts(max(26, binary_depth))
    if not (
        survivors[10] == 64
        and survivors[15] == 1295
        and survivors[20] == 27328
        and survivors[22] == 93222
        and survivors[26] == 1037374
        and sum(survivors[:26]) == 1227442
        and sum(crossings[:26]) == 190069
        and binary_count == survivors[binary_depth]
    ):
        raise ValueError("independent coefficient DP audit failed")
    margin_count, domain_exceptions = verify_phase1_margins(phase1_certificate)
    return {
        "valid": True,
        "status": "verified_partial_phase3_certificate_with_mixed_open_frontier",
        "binary_depth": binary_depth,
        "binary_frontier_nodes": binary_count,
        "records_by_ternary_level": {
            str(level): checker.record_counts[level] for level in range(max_ternary + 1)
        },
        "closed_by_reverse_merge": sum(checker.closed_counts.values()),
        "mixed_open_nodes": sum(checker.open_counts.values()),
        "phase1_domain_zero_boundary_margins_checked": margin_count,
        "phase1_positive_t_min_exceptions": domain_exceptions,
        "coefficient_dp_valid": True,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument(
        "--phase1-certificate",
        type=Path,
        default=Path("artifacts/baseline_certificate.json"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.certificate, args.phase1_certificate)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}")
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
