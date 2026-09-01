#!/usr/bin/env python3
"""Independent exact verifier for Phase 32 evidence.

This file imports neither ``src`` nor the generator.  It reconstructs the
finite corpus with separately coded profile, extraction, factor, and cofactor
arithmetic.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_LIMIT = 9
EXPECTED_CLAIMS = {
    "P195": "VERIFIED_THEOREM",
    "P196": "VERIFIED_THEOREM",
    "P197": "VERIFIED_THEOREM",
    "P198": "VERIFIED_THEOREM",
    "P199": "VERIFIED_THEOREM",
    "H200": "OPEN",
    "E45": "VERIFIED_FINITE",
    "H172": "OPEN",
    "H133": "OPEN",
}
EXPECTED_TRIPLE_COUNTS = {
    "cyclic_classes": 7398,
    "minimum_rotations": 10485,
    "widths": 174290,
    "distinct_factor_widths": 110899,
    "capacity_checks": 522870,
}


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
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def hash_row(digest: object, value: object) -> None:
    digest.update(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii"))
    digest.update(b"\n")


def positive_compositions(total: int, count: int) -> Iterable[tuple[int, ...]]:
    for cuts in itertools.combinations(range(1, total), count - 1):
        marks = (0,) + cuts + (total,)
        yield tuple(marks[index + 1] - marks[index] for index in range(count))


def rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    row = tuple(values)
    return tuple(row[offset:] + row[:offset] for offset in range(len(row)))


def cyclic_class(values: Sequence[int]) -> tuple[int, ...]:
    return min(rotations(values))


def primitive(values: Sequence[int]) -> bool:
    row = tuple(values)
    return all(
        row != row[:period] * (len(row) // period)
        for period in range(1, len(row))
        if len(row) % period == 0
    )


def reduced_walk(exponents: Sequence[int]) -> tuple[int, ...]:
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    result = [0]
    for exponent in exponents:
        result.append(result[-1] + q0 * exponent - length0)
    if result[-1]:
        fail("walk closure")
    return tuple(result)


def minimum_rotations(exponents: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    answer = sorted({row for row in rotations(exponents) if min(reduced_walk(row)) == 0})
    if not answer:
        fail("minimum rotation")
    return tuple(answer)


def profile_data(exponents: Sequence[int]) -> dict[str, object]:
    exponents = tuple(exponents)
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    walk = reduced_walk(exponents)
    residues = tuple((-length0 * index) % q0 for index in range(q + 1))
    profile = tuple((walk[index] - residues[index]) // q0 for index in range(q + 1))
    base_edges = tuple((length0 * index + residues[index]) // q0 for index in range(q + 1))
    base = tuple(base_edges[index + 1] - base_edges[index] for index in range(q))
    if min(profile) < 0 or profile[0] or profile[-1] or min(base) < 1:
        fail("profile normalization")
    rebuilt = tuple(base[index] + profile[index + 1] - profile[index] for index in range(q))
    if rebuilt != exponents or base != base[:q0] * divisor:
        fail("profile reconstruction")
    return {
        "q": q,
        "L": length,
        "d": divisor,
        "q0": q0,
        "L0": length0,
        "profile": profile,
        "base": base,
        "area": sum(profile[:-1]),
    }


def components(profile: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    rows = []
    for level in range(1, max(profile[:-1], default=0) + 1):
        start = None
        for index in range(len(profile)):
            active = index + 1 < len(profile) and profile[index] >= level
            if active and start is None:
                start = index
            if not active and start is not None:
                rows.append((level, start, index))
                start = None
    return tuple(rows)


def exponents_from_profile(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    answer = tuple(base[index] + profile[index + 1] - profile[index] for index in range(len(base)))
    if profile[0] or profile[-1] or min(profile) < 0 or min(answer) < 1:
        fail("edited profile")
    return answer


def bits(exponents: Sequence[int]) -> str:
    return "".join("1" + "0" * (value - 1) for value in exponents)


def edges(exponents: Sequence[int]) -> tuple[int, ...]:
    result = [0]
    for value in exponents:
        result.append(result[-1] + value)
    return tuple(result)


def cyclic_slice(word: str, start: int, width: int) -> str:
    return "".join(word[(start + offset) % len(word)] for offset in range(width))


def factors(word: str, width: int) -> set[str]:
    return {cyclic_slice(word, start, width) for start in range(len(word))}


def static_extract(exponents: Sequence[int]) -> dict[str, object]:
    data = profile_data(exponents)
    profile = tuple(data["profile"])
    base = tuple(data["base"])
    height = max(profile[:-1], default=0)
    peak = profile[:-1].index(height) if height else 0
    nodes = components(profile)
    spine = {row for row in nodes if height and row[1] <= peak < row[2]}
    extracted = tuple(row for row in nodes if row not in spine and row[2] == row[1] + 1)
    residual = list(profile)
    labels = []
    for level, start, end in extracted:
        if residual[start] != level or profile[end] != level - 1 or base[start] != 2:
            fail("singleton extraction")
        residual[start] -= 1
        labels.append(start)
    residual = tuple(residual)
    residual_exponents = exponents_from_profile(base, residual)
    residual_edges = edges(residual_exponents)
    anchors = tuple((residual_edges[label], residual_edges[label] + 1) for label in labels)
    used = [position for pair in anchors for position in pair]
    if len(used) != len(set(used)):
        fail("overlapping anchors")
    source = list(bits(residual_exponents))
    for left, right in anchors:
        if source[left:right + 1] != ["1", "0"]:
            fail("swap source")
        source[left], source[right] = source[right], source[left]
    if "".join(source) != bits(exponents):
        fail("swap reconstruction")
    exceptional_nodes = tuple(row for row in nodes if row not in extracted)
    if set(components(residual)) != set(exceptional_nodes):
        fail("residual components")
    increments = [profile[index + 1] - profile[index] for index in range(len(exponents))]
    J = sum(max(change, 0) for change in increments)
    E, K = len(exceptional_nodes), len(extracted)
    if J != len(nodes) or E + K != J:
        fail("component count")
    return {
        **data,
        "J": J,
        "E": E,
        "K": K,
        "base_word": bits(base),
        "residual_word": bits(residual_exponents),
        "actual_word": bits(exponents),
        "anchors": anchors,
    }


def triple_rows(exponents: Sequence[int]) -> tuple[list[list[int]], dict[str, int]]:
    item = static_extract(exponents)
    length, q = int(item["L"]), int(item["q"])
    area, J, E, K = (int(item[key]) for key in ("area", "J", "E", "K"))
    rows = []
    distinct_widths = 0
    for width in range(1, length + 1):
        exceptional = {
            start for start in range(length)
            if cyclic_slice(str(item["residual_word"]), start, width + 2)
            != cyclic_slice(str(item["base_word"]), start, width + 2)
        }
        if len(exceptional) > min(length, 2 * area + E * (width + 1)):
            fail("exceptional bound")
        incidence = [0] * length
        for left, right in tuple(item["anchors"]):
            affected = {
                (position - offset) % length
                for position in (left, right)
                for offset in range(width)
            }
            if len(affected) > min(length, width + 1):
                fail("influence bound")
            for start in affected:
                incidence[start] += 1
        if sum(incidence) > K * (width + 1):
            fail("incidence sum")
        z_n = ((length - q) * (width + 1) + length - 1) // length
        capacities = (width + 3, (width + 3) * z_n, (width + 3) * z_n * (z_n - 1) // 2)
        start_counts, type_counts = [], []
        for hit in range(3):
            starts = [start for start in range(length) if start not in exceptional and incidence[start] == hit]
            types = {cyclic_slice(str(item["actual_word"]), start, width) for start in starts}
            if len(types) > capacities[hit]:
                fail("capacity")
            start_counts.append(len(starts))
            type_counts.append(len(types))
        factor_count = len(factors(str(item["actual_word"]), width))
        distinct = factor_count == length
        rhs = (J + 2 * E) * (width + 1) + 6 * area + (width + 3) * (
            3 + 2 * z_n + z_n * (z_n - 1) // 2
        )
        if distinct and 3 * length > rhs:
            fail("triple-hit inequality")
        distinct_widths += int(distinct)
        rows.append([
            width, z_n, len(exceptional), *start_counts, *type_counts,
            *capacities, factor_count, int(distinct), sum(incidence), rhs,
        ])
    return rows, {"widths": length, "distinct_factor_widths": distinct_widths}


def affine_correction(exponents: Sequence[int]) -> int:
    q = len(exponents)
    result = 0
    prefix = 0
    for index, exponent in enumerate(exponents):
        result += 3 ** (q - 1 - index) * 2**prefix
        prefix += exponent
    return result


def mechanical_edges(q: int, length: int) -> tuple[int, ...]:
    return tuple((length * index + q - 1) // q for index in range(q + 1))


def extended_edge(q: int, length: int, time: int) -> int:
    return -((-length * time) // q)


def arc_certificate(q: int, length: int, profile: Sequence[int], modulus: int) -> dict[str, object] | None:
    support = [index for index, value in enumerate(profile[:-1]) if value]
    if not support:
        return None
    gaps = [support[(i + 1) % len(support)] + (q if i + 1 == len(support) else 0) - value for i, value in enumerate(support)]
    cut = gaps.index(max(gaps))
    start = support[(cut + 1) % len(support)]
    lifts = [value if value >= start else value + q for value in support]
    end = max(lifts)
    minimum = min(extended_edge(q, length, time) for time in lifts)
    value = sum(
        (2 ** profile[time % q] - 1)
        * 2 ** (extended_edge(q, length, time) - minimum)
        * 3 ** (end - time)
        for time in lifts
    )
    width = end - start
    area = sum(profile[:-1])
    if value % modulus or value**q >= 2 ** (q * (area + 1) + length * width):
        fail("arc certificate")
    return {
        "support": len(support), "area": area, "largest_gap": max(gaps), "width": width,
        "value_bits": value.bit_length(), "value_digest_sha256": value_hash(str(value)),
        "divisible": True, "strict_power_bound": True,
    }


def cofactor_row(exponents: Sequence[int]) -> dict[str, object]:
    exponents = tuple(exponents)
    data = profile_data(exponents)
    q, length, divisor, q0, length0 = (int(data[key]) for key in ("q", "L", "d", "q0", "L0"))
    profile = tuple(data["profile"])
    base = tuple(data["base"])
    block = base[:q0]
    block_edges = edges(block)
    R, S = 2**length0, 3**q0
    M = sum(R**c * S ** (divisor - 1 - c) for c in range(divisor))
    corrections = [
        sum(3 ** (q0 - 1 - time) * 2 ** (block_edges[time] + profile[c * q0 + time]) for time in range(q0))
        for c in range(divisor)
    ]
    B = affine_correction(exponents)
    if B != sum(R**c * S ** (divisor - 1 - c) * corrections[c] for c in range(divisor)):
        fail("block decomposition")
    delta = B - affine_correction(block) * M
    direct = sum(
        (2 ** profile[index] - 1) * 2 ** mechanical_edges(q, length)[index] * 3 ** (q - 1 - index)
        for index in range(q)
    )
    if delta != direct:
        fail("delta identity")
    denominator = 2**length - 3**q
    integral = denominator > 0 and B % denominator == 0
    hit = delta % M == 0
    if integral and not hit:
        fail("cofactor necessity")
    oscillation = None
    if integral:
        source = B // denominator
        k = (R - S) * source
        if sum((value - k) * R**c * S ** (divisor - 1 - c) for c, value in enumerate(corrections)):
            fail("root identity")
        if primitive(exponents) and divisor > 1:
            if max(corrections) - min(corrections) < R:
                fail("oscillation")
            oscillation = max(corrections) - min(corrections)
    arc = arc_certificate(q, length, profile, M) if hit and any(profile[:-1]) else None
    return {
        "q": q, "L": length, "d": divisor, "q0": q0, "L0": length0,
        "area": sum(profile[:-1]), "support": sum(value > 0 for value in profile[:-1]),
        "primitive": primitive(exponents), "cofactor_bits": M.bit_length(),
        "cofactor_hit": hit, "integral_positive": integral, "oscillation": oscillation, "arc": arc,
        "row_digest_sha256": value_hash([list(exponents), corrections, str(delta), str(M)]),
    }


def reconstruct() -> tuple[dict[str, int], str, dict[str, int], str]:
    triple_counts = {key: 0 for key in EXPECTED_TRIPLE_COUNTS}
    cofactor_counts = {
        "decompositions": 0, "noncoprime_decompositions": 0, "cofactor_hits": 0,
        "positive_integral_cycles": 0, "primitive_noncoprime_integral_cycles": 0,
        "positive_arc_certificates": 0,
    }
    triple_digest = hashlib.sha256()
    cofactor_digest = hashlib.sha256()
    for q in range(1, Q_LIMIT + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            classes = sorted({cyclic_class(row) for row in positive_compositions(length, q)})
            for representative in classes:
                triple_counts["cyclic_classes"] += 1
                for rotated in minimum_rotations(representative):
                    rows, counts = triple_rows(rotated)
                    cofactor = cofactor_row(rotated)
                    triple_counts["minimum_rotations"] += 1
                    triple_counts["widths"] += counts["widths"]
                    triple_counts["distinct_factor_widths"] += counts["distinct_factor_widths"]
                    triple_counts["capacity_checks"] += 3 * counts["widths"]
                    cofactor_counts["decompositions"] += 1
                    cofactor_counts["noncoprime_decompositions"] += int(cofactor["d"] > 1)
                    cofactor_counts["cofactor_hits"] += int(cofactor["cofactor_hit"])
                    cofactor_counts["positive_integral_cycles"] += int(cofactor["integral_positive"])
                    cofactor_counts["primitive_noncoprime_integral_cycles"] += int(
                        cofactor["integral_positive"] and cofactor["primitive"] and cofactor["d"] > 1
                    )
                    cofactor_counts["positive_arc_certificates"] += int(cofactor["arc"] is not None)
                    hash_row(triple_digest, [list(rotated), rows])
                    hash_row(cofactor_digest, [list(rotated), cofactor])
    return triple_counts, triple_digest.hexdigest(), cofactor_counts, cofactor_digest.hexdigest()


def log_box(value: int, terms: int = 512) -> tuple[Fraction, Fraction]:
    z = Fraction(value - 1, value + 1)
    z2 = z * z
    term = z
    total = Fraction(0)
    for index in range(terms):
        total += term / (2 * index + 1)
        term *= z2
    return 2 * total, 2 * total + 2 * term / ((2 * terms + 1) * (1 - z2))


def c3_cube(slope: Fraction) -> Fraction:
    eta = (slope - 1) / slope
    return Fraction(675, 64) * slope * slope * (Fraction(2, 1) / (slope - 1) - eta * eta)


def verify(artifact_dir: Path) -> dict[str, object]:
    names = (
        "phase32_theory.json", "phase32_triple_hit_corpus.json", "phase32_cofactor_corpus.json",
        "phase32_scalar_certificates.json", "phase32_regressions.json", "phase32_obstruction_report.md",
    )
    paths = [artifact_dir / name for name in names]
    theory, triple, cofactor, scalar, regressions = (load_json(path) for path in paths[:-1])
    report = paths[-1].read_text(encoding="utf-8")
    if not isinstance(theory, dict) or theory.get("claims") != EXPECTED_CLAIMS or theory.get("proves_collatz") is not False:
        fail("theory artifact mismatch")
    if theory.get("H200", {}).get("status_reason", "").find("explicit cutoff") < 0:
        fail("H200 boundary")
    for value, label in ((triple, "triple"), (cofactor, "cofactor"), (scalar, "scalar"), (regressions, "regression")):
        if not isinstance(value, dict) or value.get("proves_collatz") is not False:
            fail(f"{label} boundary")
    if triple.get("maximum_q") != Q_LIMIT or cofactor.get("maximum_q") != Q_LIMIT:
        fail("corpus scope")
    if triple.get("counts") != EXPECTED_TRIPLE_COUNTS:
        fail("triple declaration")
    actual_t, digest_t, actual_c, digest_c = reconstruct()
    if actual_t != triple.get("counts") or digest_t != triple.get("row_digest_sha256"):
        fail("triple reconstruction")
    if actual_c != cofactor.get("counts") or digest_c != cofactor.get("row_digest_sha256"):
        fail("cofactor reconstruction")
    ln2, ln3 = log_box(2), log_box(3)
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    recorded_alpha = tuple(Fraction(int(a), int(b)) for a, b in scalar.get("log2_three_interval", []))
    if len(recorded_alpha) != 2 or not (recorded_alpha[0] <= alpha[0] <= alpha[1] <= recorded_alpha[1]):
        fail("scalar logarithm")
    recorded_cube = tuple(Fraction(int(a), int(b)) for a, b in scalar.get("critical_constant_cube_interval", []))
    expected_cube = (c3_cube(recorded_alpha[1]), c3_cube(recorded_alpha[0]))
    if recorded_cube != expected_cube or Fraction(4725, 64) != Fraction(*map(int, scalar["noncritical_constant_cube"])):
        fail("scalar constants")
    required = {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}
    if {row[0] for row in regressions.get("mandatory_families", [])} != required:
        fail("mandatory families")
    for phrase in ("not accepted", "H200 OPEN", "proves_collatz=false"):
        if phrase not in report:
            fail(f"report boundary: {phrase}")
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree) if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported.update(
        node.module.split(".", 1)[0]
        for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module
    )
    generator_tail = "phase32_" + "search"
    generator_imported = any(name.endswith(generator_tail) for name in sys.modules)
    if generator_imported or "src" in imported:
        fail("generator independence")
    return {
        "format": "collatz-phase32-independent-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "claims": EXPECTED_CLAIMS,
        "triple_counts": actual_t,
        "cofactor_counts": actual_c,
        "triple_digest_sha256": digest_t,
        "cofactor_digest_sha256": digest_c,
        "verified_input_sha256": {path.name: file_hash(path) for path in paths},
        "independence": "separate composition, rotation, reduced-profile, singleton extraction, cyclic factor, block correction, and positive arc implementations",
        "what_this_result_does_not_prove": "No area-six class, arbitrary-area cycle, nonperiodic branch, or Collatz proof is excluded.",
        "proves_collatz": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        raise SystemExit(1) from exc
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")


if __name__ == "__main__":
    main()
