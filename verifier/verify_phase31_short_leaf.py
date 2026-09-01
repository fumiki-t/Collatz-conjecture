#!/usr/bin/env python3
"""Independent verifier for Phase 31 short-leaf evidence.

This module intentionally imports neither ``src`` nor the generator.  It
reconstructs the complete finite corpus with separately coded arithmetic.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Iterable, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_LIMIT = 9
RADII = (1, 2, 3)
EXPECTED_COUNTS = {
    "cyclic_classes": 7398,
    "minimum_rotations": 10485,
    "pruning_reconstructions": 31455,
    "removed_components": 20739,
    "residual_components": 91251,
    "width_pruning_cases": 522870,
    "distinct_factor_cases": 332697,
    "low_type_checks": 522870,
}
EXPECTED_ROW_DIGEST = "eebf83f9e929a124350e7a804166f0cd9fcf1b27d3c3f5f5fb99c2ceeb54db54"


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def value_hash(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def positive_compositions(total: int, parts: int) -> Iterable[tuple[int, ...]]:
    for dividers in itertools.combinations(range(1, total), parts - 1):
        marks = (0,) + dividers + (total,)
        yield tuple(marks[index + 1] - marks[index] for index in range(parts))


def rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    row = tuple(values)
    return tuple(row[offset:] + row[:offset] for offset in range(len(row)))


def canonical_rotation(values: Sequence[int]) -> tuple[int, ...]:
    return min(rotations(values))


def reduced_walk(exponents: Sequence[int]) -> tuple[int, ...]:
    q = len(exponents)
    length = sum(exponents)
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    height = 0
    result = [0]
    for exponent in exponents:
        height += q0 * exponent - length0
        result.append(height)
    if result[-1] != 0:
        fail("walk closure")
    return tuple(result)


def minimum_walk_rotations(exponents: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    answer = sorted({row for row in rotations(exponents) if min(reduced_walk(row)) == 0})
    if not answer:
        fail("minimum rotation")
    return tuple(answer)


def ceiling_ratio(numerator: int, denominator: int) -> int:
    return (numerator + denominator - 1) // denominator


def mechanical_exponents(q: int, length: int) -> tuple[int, ...]:
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    return tuple(
        ceiling_ratio(length0 * (index + 1), q0)
        - ceiling_ratio(length0 * index, q0)
        for index in range(q)
    )


def profile_data(exponents: Sequence[int]) -> dict[str, object]:
    exponents = tuple(exponents)
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    walk = reduced_walk(exponents)
    residues = tuple((-length0 * index) % q0 for index in range(q + 1))
    profile = tuple((walk[index] - residues[index]) // q0 for index in range(q + 1))
    if min(profile) < 0 or profile[0] or profile[-1]:
        fail("profile boundary")
    base = mechanical_exponents(q, length)
    rebuilt = tuple(
        base[index] + profile[index + 1] - profile[index]
        for index in range(q)
    )
    if rebuilt != exponents or min(rebuilt) < 1:
        fail("profile reconstruction")
    increments = tuple(profile[index + 1] - profile[index] for index in range(q))
    J = sum(max(change, 0) for change in increments)
    if J != sum(change == -1 for change in increments):
        fail("component balance")
    height = max(profile[:-1], default=0)
    area = sum(profile[:-1])
    delta_num = length0 - q0
    descent_floor = sum(level * q0 // delta_num for level in range(height))
    sigma = area - J - descent_floor
    if sigma < 0:
        fail("negative slack")
    return {
        "q": q,
        "L": length,
        "base": base,
        "profile": profile,
        "J": J,
        "height": height,
        "area": area,
        "sigma": sigma,
    }


def layers(profile: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    q = len(profile) - 1
    rows = []
    for level in range(1, max(profile[:-1], default=0) + 1):
        start = None
        for index in range(q + 1):
            active = index < q and profile[index] >= level
            if active and start is None:
                start = index
            if not active and start is not None:
                rows.append((level, start, index))
                start = None
    return tuple(rows)


def exponents_from_profile(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    if profile[0] or profile[-1] or min(profile) < 0:
        fail("edited profile boundary")
    answer = tuple(
        base[index] + profile[index + 1] - profile[index]
        for index in range(len(base))
    )
    if min(answer) < 1:
        fail("edited exponent positivity")
    return answer


def word(exponents: Sequence[int]) -> str:
    return "".join("1" + "0" * (value - 1) for value in exponents)


def sums(exponents: Sequence[int]) -> tuple[int, ...]:
    result = [0]
    for value in exponents:
        result.append(result[-1] + value)
    return tuple(result)


def cyclic_slice(bits: str, start: int, width: int) -> str:
    return "".join(bits[(start + offset) % len(bits)] for offset in range(width))


def prune(exponents: Sequence[int], radius: int) -> dict[str, object]:
    data = profile_data(exponents)
    original = tuple(data["profile"])
    base = tuple(data["base"])
    height = int(data["height"])
    peak = original[:-1].index(height) if height else 0
    current = list(original)
    removed: list[tuple[int, int, int]] = []
    states: list[tuple[int, ...]] = []
    while True:
        available = []
        for level, start, end in layers(current):
            spine = bool(height) and start <= peak < end
            leaf = all(current[index] == level for index in range(start, end))
            if not spine and leaf and end - start <= radius:
                available.append((level, start, end))
        if not available:
            break
        # A different deterministic order from the generator exercises
        # confluence of the pruning core.
        level, start, end = max(available, key=lambda row: (row[0], row[1], row[2]))
        old_count = len(layers(current))
        states.append(tuple(current))
        for index in range(start, end):
            current[index] -= 1
        exponents_from_profile(base, current)
        if len(layers(current)) + 1 != old_count:
            fail("pruning component decrement")
        removed.append((level, start, end))
    residual = tuple(current)
    remaining = layers(residual)
    J = int(data["J"])
    E, K = len(remaining), len(removed)
    if E + K != J:
        fail("component conservation")
    nonspine = [row for row in remaining if not (height and row[1] <= peak < row[2])]
    excess = sum(end - start - 1 for _, start, end in nonspine)
    if any(end - start <= radius for _, start, end in nonspine):
        fail("short residual component")
    if excess > int(data["sigma"]) or E > height + int(data["sigma"]) // radius:
        fail("residual bound")

    replay = list(residual)
    for operation, expected in zip(reversed(removed), reversed(states), strict=True):
        _, start, end = operation
        for index in range(start, end):
            replay[index] += 1
        if tuple(replay) != expected:
            fail("reverse profile reconstruction")
    if tuple(replay) != original:
        fail("reverse profile final")

    marks = sums(base)
    residual_exponents = exponents_from_profile(base, residual)
    current_word = word(residual_exponents)
    operations = []
    for level, start_label, end_label in reversed(removed):
        left = marks[start_label] + level - 1
        right = marks[end_label] + level - 1
        segment = current_word[left:right]
        if not segment or segment[0] != "1" or segment[-1] != "0":
            fail("rotation endpoint")
        current_word = current_word[:left] + segment[-1] + segment[:-1] + current_word[right:]
        span = right - left
        if span > 2 * radius:
            fail("rotation span")
        operations.append((left, right, end_label - start_label, span))
    if current_word != word(exponents):
        fail("reverse word reconstruction")
    residual_span = sum(marks[end] - marks[start] for _, start, end in remaining)
    if residual_span > 2 * int(data["area"]):
        fail("residual span")
    return {
        **data,
        "R": radius,
        "K": K,
        "E": E,
        "operations": tuple(operations),
        "base_word": word(base),
        "residual_word": word(residual_exponents),
        "actual_word": word(exponents),
    }


def affected_starts(length: int, left: int, right: int, width: int) -> set[int]:
    return {
        (position - back) % length
        for position in range(left, right)
        for back in range(width)
    }


def audit_widths(exponents: Sequence[int], radius: int) -> tuple[list[list[int]], dict[str, int]]:
    item = prune(exponents, radius)
    length = int(item["L"])
    area = int(item["area"])
    E, K = int(item["E"]), int(item["K"])
    base_word = str(item["base_word"])
    residual_word = str(item["residual_word"])
    actual_word = str(item["actual_word"])
    operations = tuple(item["operations"])
    rows = []
    totals = {"width_pruning_cases": 0, "distinct_factor_cases": 0, "low_type_checks": 0}
    for width in range(1, length + 1):
        extended = width + 4 * radius
        exceptional = {
            start for start in range(length)
            if cyclic_slice(residual_word, start, extended) != cyclic_slice(base_word, start, extended)
        }
        context_limit = 2 * area + E * (extended - 1)
        if len(exceptional) > min(length, context_limit):
            fail("context limit")
        hits = [0] * length
        influence_limit = width + 2 * radius - 1
        for left, right, _, span in operations:
            touched = affected_starts(length, left, right, width)
            if len(touched) > min(length, width + span - 1) or len(touched) > min(length, influence_limit):
                fail("influence limit")
            for start in touched:
                hits[start] += 1
        low = [start for start in range(length) if start not in exceptional and hits[start] <= 1]
        low_types = {cyclic_slice(actual_word, start, width) for start in low}
        capacity = (extended + 1) * (1 + radius * (width + 2 * radius))
        if len(low_types) > capacity:
            fail("type capacity")
        all_types = {cyclic_slice(actual_word, start, width) for start in range(length)}
        distinct = len(all_types) == length
        rhs = K * influence_limit + 4 * area + 2 * E * (extended - 1) + 2 * capacity
        if distinct and 2 * length > rhs:
            fail("double-hit inequality")
        rows.append([
            radius, width, K, E, len(exceptional), context_limit,
            len(low_types), capacity, len(all_types), int(distinct), sum(hits), rhs,
        ])
        totals["width_pruning_cases"] += 1
        totals["distinct_factor_cases"] += int(distinct)
        totals["low_type_checks"] += 1
    return rows, totals


def reconstruct_corpus() -> tuple[dict[str, int], str]:
    counts = {
        "cyclic_classes": 0,
        "minimum_rotations": 0,
        "pruning_reconstructions": 0,
        "removed_components": 0,
        "residual_components": 0,
        "width_pruning_cases": 0,
        "distinct_factor_cases": 0,
        "low_type_checks": 0,
    }
    digest_rows = []
    for q in range(1, Q_LIMIT + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            classes = sorted({canonical_rotation(row) for row in positive_compositions(length, q)})
            for representative in classes:
                counts["cyclic_classes"] += 1
                for rotated in minimum_walk_rotations(representative):
                    counts["minimum_rotations"] += 1
                    for radius in RADII:
                        item = prune(rotated, radius)
                        rows, local = audit_widths(rotated, radius)
                        counts["pruning_reconstructions"] += 1
                        counts["removed_components"] += int(item["K"])
                        counts["residual_components"] += int(item["E"])
                        for key, value in local.items():
                            counts[key] += value
                        digest_rows.append([list(rotated), radius, rows])
    return counts, value_hash(digest_rows)


def expected_theory() -> dict[str, object]:
    return {
        "format": "collatz-phase31-short-leaf-theory-v1",
        "claims": {
            "P191": "VERIFIED_THEOREM", "P192": "VERIFIED_THEOREM",
            "P193": "VERIFIED_THEOREM", "P194": "VERIFIED_THEOREM",
            "E44": "VERIFIED_FINITE", "H172": "OPEN", "H133": "OPEN", "H89": "OPEN",
        },
        "P191": {
            "residual_bound": "E_R<=h+floor(Sigma/R)",
            "quantifiers": "every valid reduced profile, every integer R>=1, and any fixed maximum-height spine",
            "proof_kernel": "repeatedly delete a flat nonspine leaf of odd-label length at most R; each step deletes exactly one forest node, while every surviving nonspine node has excess at least R and all nonspine excess is charged to Sigma",
        },
        "P192": {
            "context_width": "N_R=n+4R",
            "context_bound": "U_R<=min(L,2A+E_R(N_R-1))",
            "low_type_bound": "B_R(n)=(N_R+1)(1+R(n+2R))",
            "finite_inequality": "2L<=K_R(n+2R-1)+4A+2E_R(n+4R-1)+2B_R(n)",
        },
        "P193": {
            "limit_order": "first q->infinity for each fixed R, then R->infinity",
            "constraint": "xy>=2ell",
            "area_constant": "3(2ell)^(2/3)/(2(ell-1)^(1/3))",
            "equality": "z=lim Sigma/q^(2/3)=0",
        },
        "P194": {
            "statement": "at P193 equality, all but o(J) components are disjoint singleton transports, all but o(L) state-separation windows have exactly two singleton incidences, and the anchor shift-mismatch count is o(L)",
            "identity": "c_(t+1)-c_t=chi_(t+n+1)-chi_t",
            "open_boundary": "no resonant resultant or positive-cycle exclusion is proved",
        },
        "supersession": "P191-P194 replace the old Phase 31 proof route. NG40 remains a valid refutation of the old single-R normalized inference, but it does not satisfy the all-fixed-R short-leaf constraints.",
        "excluded_scope": "The H89 Hamming-shell and q0 numerical candidates in the supplied note are not audited or accepted here.",
        "proves_collatz": False,
    }


def verify(artifact_dir: Path) -> dict[str, object]:
    theory_path = artifact_dir / "phase31_short_leaf_theory.json"
    corpus_path = artifact_dir / "phase31_short_leaf_corpus.json"
    regressions_path = artifact_dir / "phase31_short_leaf_regressions.json"
    report_path = artifact_dir / "phase31_short_leaf_obstruction_report.md"
    theory = load_json(theory_path)
    corpus = load_json(corpus_path)
    regressions = load_json(regressions_path)
    if theory != expected_theory():
        fail("theory artifact mismatch")
    if not isinstance(regressions, dict) or regressions.get("proves_collatz") is not False:
        fail("regression boundary")
    required_families = {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"}
    if set(regressions.get("mandatory_adversarial_families", [])) != required_families:
        fail("mandatory family set")
    required_obstructions = {"NG32", "NG34", "NG35", "NG36", "NG37", "NG38", "NG39", "NG40"}
    if set(regressions.get("preserved_obstructions", [])) != required_obstructions:
        fail("obstruction set")
    report = report_path.read_text(encoding="utf-8")
    for phrase in ("H89 Hamming-shell", "NG40 remains", "proves_collatz=false"):
        if phrase not in report:
            fail(f"report boundary: {phrase}")
    if not isinstance(corpus, dict) or corpus.get("format") != "collatz-phase31-short-leaf-corpus-v1":
        fail("corpus format")
    if corpus.get("maximum_q") != Q_LIMIT or corpus.get("radii") != list(RADII):
        fail("corpus scope")
    if corpus.get("counts") != EXPECTED_COUNTS or corpus.get("row_digest_sha256") != EXPECTED_ROW_DIGEST:
        fail("corpus declaration")
    counts, row_digest = reconstruct_corpus()
    if counts != corpus.get("counts"):
        fail("corpus counts")
    if row_digest != corpus.get("row_digest_sha256"):
        fail("corpus row digest")
    if counts["minimum_rotations"] != 10_485 or counts["width_pruning_cases"] != 522_870:
        fail("declared finite target")
    if corpus.get("proves_collatz") is not False:
        fail("corpus overclaim")
    source_tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(source_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_roots.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(source_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    )
    generator_tail = "phase31_" + "short_leaf_" + "search"
    generator_imported = any(name.endswith(generator_tail) for name in sys.modules)
    if generator_imported or "src" in imported_roots:
        fail("generator independence")
    inputs = [theory_path, corpus_path, regressions_path, report_path]
    return {
        "format": "collatz-phase31-short-leaf-independent-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "claims": theory["claims"],
        "corpus_counts": counts,
        "row_digest_sha256": row_digest,
        "verified_input_sha256": {path.name: file_hash(path) for path in inputs},
        "independence": "separate composition, rotation, reduced-profile, forest-pruning, word-rotation, context, incidence, and factor implementations",
        "what_this_result_does_not_prove": "No cycle exclusion, H172/H133 closure, H89 finite certificate, nonperiodic exclusion, or Collatz proof is obtained.",
        "proves_collatz": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (VerificationError, OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        raise SystemExit(1) from exc
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
