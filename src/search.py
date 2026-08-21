#!/usr/bin/env python3
"""Phase 1 deterministic exact affine-cylinder search."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import sys
from collections import Counter
from pathlib import Path
from typing import TextIO

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.model import Node, direct_witness, shortcut_step

FORMAT = "collatz-affine-certificate-v1"


class CertificateWriter:
    def __init__(self, stream: TextIO, max_depth: int) -> None:
        self.stream = stream
        self.max_depth = max_depth
        self.nodes_by_depth: Counter[int] = Counter()
        self.survivors_by_depth: Counter[int] = Counter()
        self.rule_counts: Counter[str] = Counter()

    def write_record(self, node: Node, rule: str | list[object]) -> None:
        record: list[object] = [*node.compact(), rule]
        self.stream.write(json.dumps(record, separators=(",", ":"), ensure_ascii=True))
        self.stream.write(",\n")

    def visit(self, node: Node) -> None:
        self.nodes_by_depth[node.k] += 1
        if node.has_uniform_descent():
            self.rule_counts["DESCENT"] += 1
            self.write_record(node, "DESCENT")
            return

        high = node.finite_tail_high()
        if high is not None:
            exceptions: list[list[int]] = []
            for t in range(node.t_min, high + 1):
                n, _image = node.value_at(t)
                steps, endpoint = direct_witness(n)
                exceptions.append([n, steps, endpoint])
                self.rule_counts["DIRECT"] += 1
            self.rule_counts["FINITE_TAIL"] += 1
            self.write_record(node, ["FINITE_TAIL", high, exceptions])
            return

        self.survivors_by_depth[node.k] += 1
        if node.k == self.max_depth:
            self.rule_counts["OPEN"] += 1
            self.write_record(node, "OPEN")
            return

        self.rule_counts["SPLIT"] += 1
        self.write_record(node, "SPLIT")
        left, right = node.split()
        self.visit(left)
        self.visit(right)

    def summary(self, coverage: dict[str, object]) -> dict[str, object]:
        return {
            "nodes_by_depth": {
                str(depth): self.nodes_by_depth[depth]
                for depth in range(self.max_depth + 1)
            },
            "survivors_by_depth": {
                str(depth): self.survivors_by_depth[depth]
                for depth in range(self.max_depth + 1)
            },
            "rule_counts": dict(sorted(self.rule_counts.items())),
            "coverage_audit": coverage,
            "status": "partial_certificate_with_open_frontier",
            "proves_collatz": False,
        }


def _audit_range(start: int, stop: int, max_depth: int) -> tuple[int, int, int, str]:
    """Scalar worker for an exhaustive direct/affine comparison chunk."""

    powers_of_three = [pow(3, exponent) for exponent in range(max_depth + 1)]
    digest = hashlib.sha256()
    checked_steps = 0
    digest_buffer = bytearray()
    for n in range(start, stop):
        k = 0
        r = 0
        y = 0
        q = 0
        value = n
        while True:
            stride = 1 << k
            if (n - r) % stride:
                raise AssertionError(f"cylinder k={k}, r={r} does not represent {n}")
            t = (n - r) // stride
            multiplier = powers_of_three[q]
            expected = y + multiplier * t
            if value != expected:
                raise AssertionError(
                    f"direct/affine mismatch for n={n}, k={k}: "
                    f"{value} != {expected}"
                )
            t_min = max(0, -((r - 2) // stride))
            slope = multiplier - stride
            intercept = y - r
            descent = slope < 0 and intercept + slope * t_min < 0
            finite_tail = stride > multiplier and not descent
            if descent or finite_tail or k == max_depth:
                code = "D" if descent else "F" if finite_tail else "O"
                digest_buffer.extend(f"{n}:{k}:{value}:{code}\n".encode("ascii"))
                if len(digest_buffer) >= 1 << 20:
                    digest.update(digest_buffer)
                    digest_buffer.clear()
                break
            epsilon = t % 2
            z = y + epsilon * multiplier
            affine_parity = z % 2
            if value % 2 != affine_parity:
                raise AssertionError(f"parity mismatch for n={n}, k={k}")
            value = value // 2 if affine_parity == 0 else (3 * value + 1) // 2
            checked_steps += 1
            r += epsilon * stride
            if affine_parity == 0:
                y = z // 2
            else:
                y = (3 * z + 1) // 2
                q += 1
            k += 1
    digest.update(digest_buffer)
    return start, stop, checked_steps, digest.hexdigest()


def audit_below(bound: int, max_depth: int, workers: int | None = None) -> dict[str, object]:
    """Compare every represented n in [2,bound) with literal direct iteration."""

    if bound < 2:
        raise ValueError("coverage bound must be at least 2")
    chunk_size = 1 << 18
    ranges = [
        (start, min(start + chunk_size, bound), max_depth)
        for start in range(2, bound, chunk_size)
    ]
    if workers is None:
        workers = min(8, os.cpu_count() or 1)
    if bound <= 1 << 16:
        workers = 1
    if workers < 1:
        raise ValueError("audit workers must be positive")
    if workers == 1:
        results = [_audit_range(*arguments) for arguments in ranges]
    else:
        try:
            with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
                results = list(executor.map(_audit_range_star, ranges))
        except (OSError, PermissionError):
            # Some sandboxes disallow POSIX semaphore inspection.  The exact
            # ordered chunks and final digest remain identical in this fallback.
            results = [_audit_range(*arguments) for arguments in ranges]
    combined = hashlib.sha256()
    checked_steps = 0
    for start, stop, steps, chunk_digest in results:
        checked_steps += steps
        combined.update(f"{start}:{stop}:{steps}:{chunk_digest}\n".encode("ascii"))
    return {
        "bound_exclusive": bound,
        "integers_checked": max(0, bound - 2),
        "direct_steps_checked": checked_steps,
        "result": "all_equal",
        "sha256": combined.hexdigest(),
        "digest_scheme": "sha256-of-ordered-2^18-chunk-digests-v1",
    }


def _audit_range_star(arguments: tuple[int, int, int]) -> tuple[int, int, int, str]:
    return _audit_range(*arguments)


def generate(
    output: Path, depth: int, coverage_bound: int, audit_workers: int | None = None
) -> dict[str, object]:
    if depth < 1:
        raise ValueError("depth must be positive")
    output.parent.mkdir(parents=True, exist_ok=True)
    coverage = audit_below(coverage_bound, depth, audit_workers)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        header = {"format": FORMAT, "version": 1, "max_depth": depth}
        encoded = json.dumps(header, separators=(",", ":"))
        stream.write(encoded[:-1] + ',"records":[\n')
        writer = CertificateWriter(stream, depth)
        writer.visit(Node(0, 0, 0, 0, ""))
        summary = writer.summary(coverage)
        stream.write("null],\"summary\":")
        stream.write(json.dumps(summary, separators=(",", ":"), sort_keys=True))
        stream.write("}\n")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--depth", type=int, default=26)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--coverage-bound",
        type=int,
        default=1 << 24,
        help="exclusive exhaustive direct-comparison bound (default: 2^24)",
    )
    parser.add_argument(
        "--audit-workers",
        type=int,
        default=None,
        help="parallel exhaustive-audit workers (default: min(8, CPU count))",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    summary = generate(args.output, args.depth, args.coverage_bound, args.audit_workers)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
