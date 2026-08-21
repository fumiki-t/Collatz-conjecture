#!/usr/bin/env python3
"""Independent streaming verifier for affine Collatz certificates.

No model or search module is imported.  Every split, pruning inequality, and
direct exception witness is reconstructed here with separate code.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True, slots=True)
class Expected:
    level: int
    residue: int
    image_constant: int
    odd_count: int
    word: str


def lower_parameter(node: Expected) -> int:
    modulus = 1 << node.level
    return max(0, -((node.residue - 2) // modulus))


def checker_step(value: int) -> int:
    if value <= 0:
        raise ValueError("non-positive direct witness value")
    if value & 1:
        return (value * 3 + 1) // 2
    return value // 2


def checker_children(parent: Expected) -> tuple[Expected, Expected]:
    multiplier = pow(3, parent.odd_count)
    modulus = 1 << parent.level
    result: list[Expected] = []
    for selector in (0, 1):
        residue = parent.residue + selector * modulus
        pre_step = parent.image_constant + selector * multiplier
        bit = pre_step & 1
        if bit:
            constant = (3 * pre_step + 1) // 2
            odds = parent.odd_count + 1
        else:
            constant = pre_step // 2
            odds = parent.odd_count
        result.append(
            Expected(
                parent.level + 1,
                residue,
                constant,
                odds,
                parent.word + str(bit),
            )
        )
    return result[0], result[1]


def parse_record_lines(path: Path) -> tuple[dict[str, object], Iterator[list[object]], dict[str, object]]:
    stream = path.open("r", encoding="utf-8")
    first = stream.readline().rstrip("\n")
    marker = ',"records":['
    if not first.endswith(marker):
        stream.close()
        raise ValueError("invalid certificate header")
    header = json.loads(first[: -len(marker)] + "}")
    footer_box: dict[str, object] = {}

    def records() -> Iterator[list[object]]:
        try:
            for line_number, line in enumerate(stream, start=2):
                text = line.rstrip("\n")
                if text.startswith('null],"summary":'):
                    payload = text[len('null],"summary":') :]
                    if not payload.endswith("}"):
                        raise ValueError(f"invalid footer on line {line_number}")
                    footer_box.update(json.loads(payload[:-1]))
                    if stream.read(1):
                        raise ValueError("trailing data after certificate footer")
                    return
                if not text.endswith(","):
                    raise ValueError(f"invalid record framing on line {line_number}")
                value = json.loads(text[:-1])
                if not isinstance(value, list) or len(value) != 6:
                    raise ValueError(f"invalid record on line {line_number}")
                yield value
            raise ValueError("missing certificate footer")
        finally:
            stream.close()

    return header, records(), footer_box


class Verification:
    def __init__(self, records: Iterator[list[object]], max_depth: int) -> None:
        self.records = records
        self.max_depth = max_depth
        self.nodes_by_depth: Counter[int] = Counter()
        self.survivors_by_depth: Counter[int] = Counter()
        self.rules: Counter[str] = Counter()

    def next_record(self) -> list[object]:
        try:
            return next(self.records)
        except StopIteration as error:
            raise ValueError("certificate ended before the recursive tree") from error

    def subtree(self, expected: Expected) -> None:
        record = self.next_record()
        raw_node = record[:5]
        if raw_node != [
            expected.level,
            expected.residue,
            expected.image_constant,
            expected.odd_count,
            expected.word,
        ]:
            raise ValueError(f"unexpected node: got {raw_node}, expected {expected}")
        if not (0 <= expected.residue < (1 << expected.level)):
            raise ValueError("residue outside canonical range")
        if len(expected.word) != expected.level:
            raise ValueError("parity metadata length mismatch")

        self.nodes_by_depth[expected.level] += 1
        multiplier = pow(3, expected.odd_count)
        modulus = 1 << expected.level
        parameter_min = lower_parameter(expected)
        slope = multiplier - modulus
        intercept = expected.image_constant - expected.residue
        descent = slope < 0 and intercept + slope * parameter_min < 0
        finite_high = None
        if modulus > multiplier:
            finite_high = intercept // (modulus - multiplier)

        rule = record[5]
        if rule == "DESCENT":
            if not descent:
                raise ValueError(f"invalid DESCENT at {expected}")
            self.rules["DESCENT"] += 1
            return

        if isinstance(rule, list) and len(rule) == 3 and rule[0] == "FINITE_TAIL":
            if descent or finite_high is None:
                raise ValueError(f"invalid FINITE_TAIL applicability at {expected}")
            if rule[1] != finite_high:
                raise ValueError("incorrect FINITE_TAIL high parameter")
            witnesses = rule[2]
            wanted_parameters = list(range(parameter_min, finite_high + 1))
            if not isinstance(witnesses, list) or len(witnesses) != len(wanted_parameters):
                raise ValueError("FINITE_TAIL exceptions are not exact and exhaustive")
            for parameter, witness in zip(wanted_parameters, witnesses, strict=True):
                n = expected.residue + modulus * parameter
                if not isinstance(witness, list) or len(witness) != 3 or witness[0] != n:
                    raise ValueError("incorrect DIRECT exception integer")
                steps, claimed_end = witness[1], witness[2]
                if not isinstance(steps, int) or steps <= 0:
                    raise ValueError("invalid DIRECT step count")
                value = n
                for _ in range(steps):
                    value = checker_step(value)
                if value != claimed_end or not (value < n or value == 1):
                    raise ValueError(f"invalid DIRECT witness for {n}")
                self.rules["DIRECT"] += 1
            self.rules["FINITE_TAIL"] += 1
            return

        if descent or finite_high is not None:
            raise ValueError(f"unpruned node at {expected}")
        self.survivors_by_depth[expected.level] += 1

        if rule == "OPEN":
            if expected.level != self.max_depth:
                raise ValueError("OPEN is allowed only at max_depth")
            self.rules["OPEN"] += 1
            return
        if rule != "SPLIT":
            raise ValueError(f"unknown or misplaced rule {rule!r}")
        if expected.level >= self.max_depth:
            raise ValueError("SPLIT exceeds max_depth")
        self.rules["SPLIT"] += 1
        left, right = checker_children(expected)
        self.subtree(left)
        self.subtree(right)


def verify(path: Path) -> dict[str, object]:
    header, records, footer = parse_record_lines(path)
    if header.get("format") != "collatz-affine-certificate-v1" or header.get("version") != 1:
        raise ValueError("unsupported certificate format")
    max_depth = header.get("max_depth")
    if not isinstance(max_depth, int) or max_depth < 1:
        raise ValueError("invalid max_depth")
    check = Verification(records, max_depth)
    check.subtree(Expected(0, 0, 0, 0, ""))
    try:
        extra = next(records)
    except StopIteration:
        extra = None
    if extra is not None:
        raise ValueError("extra record after recursive tree")

    expected_nodes = {str(i): check.nodes_by_depth[i] for i in range(max_depth + 1)}
    expected_survivors = {str(i): check.survivors_by_depth[i] for i in range(max_depth + 1)}
    expected_rules = dict(sorted(check.rules.items()))
    if footer.get("nodes_by_depth") != expected_nodes:
        raise ValueError("summary nodes_by_depth mismatch")
    if footer.get("survivors_by_depth") != expected_survivors:
        raise ValueError("summary survivors_by_depth mismatch")
    if footer.get("rule_counts") != expected_rules:
        raise ValueError("summary rule_counts mismatch")
    if footer.get("proves_collatz") is not False:
        raise ValueError("a finite-depth certificate must not claim a proof")
    return {
        "valid": True,
        "status": "verified_partial_certificate_with_open_frontier",
        "max_depth": max_depth,
        "open_nodes": check.rules["OPEN"],
        "rule_counts": expected_rules,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.certificate)
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}")
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
