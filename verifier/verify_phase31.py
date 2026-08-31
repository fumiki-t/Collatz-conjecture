#!/usr/bin/env python3
"""Independently verify Phase 31 double-hit transport artifacts.

This module deliberately imports no generator or ``src`` implementation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterator, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


FILES = (
    "phase31_theory.json",
    "phase31_transport_corpus.json",
    "phase31_scalar_certificates.json",
    "phase31_synthetic_profiles.json",
    "phase31_regressions.json",
    "phase31_obstruction_report.md",
)
EXPECTED = {
    "P185": "VERIFIED_THEOREM",
    "P186": "VERIFIED_THEOREM",
    "P187": "VERIFIED_THEOREM",
    "P188": "VERIFIED_THEOREM",
    "P189": "VERIFIED_THEOREM",
    "P190": "VERIFIED_THEOREM",
    "E43": "VERIFIED_FINITE",
    "NG40": "REFUTED",
    "H172": "OPEN",
    "H133": "OPEN",
}


def fail(message: str) -> None:
    raise SystemExit(f"verification failed: {message}")


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(path.name)
    return value


def stable_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def decode(value: Sequence[str]) -> Fraction:
    return Fraction(int(value[0]), int(value[1]))


def compositions(total: int, parts: int, prefix: tuple[int, ...] = ()) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        yield prefix + (total,)
        return
    for first in range(1, total - parts + 2):
        yield from compositions(total - first, parts - 1, prefix + (first,))


def rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    row = tuple(values)
    return tuple(row[index:] + row[:index] for index in range(len(row)))


def cyclic_class(values: Sequence[int]) -> tuple[int, ...]:
    return min(rotations(values))


def primitive(values: Sequence[int]) -> bool:
    row = tuple(values)
    return all(
        row != row[:period] * (len(row) // period)
        for period in range(1, len(row))
        if len(row) % period == 0
    )


def unshifted_heights(values: Sequence[int]) -> tuple[int, ...]:
    q, length = len(values), sum(values)
    common = math.gcd(q, length)
    q0, L0 = q // common, length // common
    result = [0]
    for value in values:
        result.append(result[-1] + q0 * value - L0)
    return tuple(result)


def minimum_rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted({row for row in rotations(values) if min(unshifted_heights(row)) == 0}))


def reduced_data(values: Sequence[int]) -> dict[str, object]:
    row = tuple(values)
    q, length = len(row), sum(row)
    common = math.gcd(q, length)
    q0, L0 = q // common, length // common
    raw = [0]
    for value in row:
        raw.append(raw[-1] + q0 * value - L0)
    residues = [(-L0 * index) % q0 for index in range(q + 1)]
    profile = []
    for height, residue in zip(raw, residues, strict=True):
        if (height - residue) % q0:
            fail("reduced profile divisibility")
        profile.append((height - residue) // q0)
    boundary = [(L0 * index + residues[index]) // q0 for index in range(q + 1)]
    base = tuple(boundary[index + 1] - boundary[index] for index in range(q))
    if min(profile) < 0 or profile[0] or profile[-1] or set(base) - {1, 2}:
        fail("reduced profile convention")
    return {"q": q, "L": length, "q0": q0, "L0": L0, "profile": tuple(profile), "base": base}


def expanded(values: Sequence[int]) -> str:
    return "".join("1" + "0" * (value - 1) for value in values)


def factor_set(word: str, width: int) -> set[str]:
    return {
        "".join(word[(start + offset) % len(word)] for offset in range(width))
        for start in range(len(word))
    }


def window(word: str, start: int, width: int) -> str:
    return "".join(word[(start + offset) % len(word)] for offset in range(width))


def boundaries(values: Sequence[int]) -> tuple[int, ...]:
    result = [0]
    for value in values:
        result.append(result[-1] + value)
    return tuple(result)


def level_intervals(profile: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], ...]:
    q = len(profile) - 1
    levels = []
    for level in range(1, max(profile[:-1], default=0) + 1):
        intervals = []
        start = None
        for index in range(q + 1):
            active = index < q and profile[index] >= level
            if active and start is None:
                start = index
            if not active and start is not None:
                intervals.append((start, index))
                start = None
        levels.append(tuple(intervals))
    return tuple(levels)


def components(profile: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (level, start, end)
        for level, intervals in enumerate(level_intervals(profile), start=1)
        for start, end in intervals
    )


def exponents_from_profile(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    result = tuple(
        base[index] + profile[index + 1] - profile[index]
        for index in range(len(base))
    )
    if len(profile) != len(base) + 1 or profile[0] or profile[-1] or min(result) < 1:
        fail("profile exponent reconstruction")
    return result


def inventory(values: Sequence[int]) -> dict[str, object]:
    data = reduced_data(values)
    q, length = int(data["q"]), int(data["L"])
    profile = tuple(data["profile"])
    base = tuple(data["base"])
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    all_components = components(profile)
    J = len(all_components)
    peak = profile[:-1].index(height) if height else 0
    spine = {row for row in all_components if height and row[1] <= peak < row[2]}
    if len(spine) != height:
        fail("spine")
    extracted = tuple(row for row in all_components if row not in spine and row[2] - row[1] == 1)
    exceptional = tuple(row for row in all_components if row not in extracted)
    residual = list(profile)
    labels = []
    for level, start, end in extracted:
        if end != start + 1 or residual[start] != level:
            fail("top singleton")
        if profile[start + 1] != level - 1 or base[start] != 2:
            fail("singleton convention")
        residual[start] -= 1
        labels.append(start)
    if len(labels) != len(set(labels)):
        fail("duplicate extraction")
    residual_tuple = tuple(residual)
    residual_values = exponents_from_profile(base, residual_tuple)
    if set(components(residual_tuple)) != set(exceptional):
        fail("residual components")
    residual_word = expanded(residual_values)
    actual_word = expanded(values)
    residual_boundaries = boundaries(residual_values)
    anchors = tuple((residual_boundaries[label], residual_boundaries[label] + 1) for label in labels)
    positions = [position for pair in anchors for position in pair]
    if len(positions) != len(set(positions)):
        fail("overlapping swaps")
    rebuilt = list(residual_word)
    for left, right in anchors:
        if rebuilt[left : right + 1] != ["1", "0"]:
            fail("swap source")
        rebuilt[left], rebuilt[right] = rebuilt[right], rebuilt[left]
    if "".join(rebuilt) != actual_word:
        fail("static reconstruction")
    p = length - q
    descent_floor = sum((level * q) // p for level in range(height))
    sigma = area - J - descent_floor
    E, K = len(exceptional), len(extracted)
    if sigma < 0 or E != J - K or E > height + sigma:
        fail("exception bound")
    base_boundaries = boundaries(base)
    residual_span = sum(base_boundaries[end] - base_boundaries[start] for _, start, end in exceptional)
    if residual_span > 2 * area:
        fail("residual span")
    return {
        "q": q,
        "L": length,
        "area": area,
        "height": height,
        "J": J,
        "sigma": sigma,
        "E": E,
        "K": K,
        "residual_span": residual_span,
        "anchors": anchors,
        "base_word": expanded(base),
        "residual_word": residual_word,
        "actual_word": actual_word,
    }


def audit(values: Sequence[int], widths: Sequence[int] | None = None) -> dict[str, object]:
    item = inventory(values)
    length = int(item["L"])
    area, J, E, K = (int(item[key]) for key in ("area", "J", "E", "K"))
    span = int(item["residual_span"])
    base_word = str(item["base_word"])
    residual_word = str(item["residual_word"])
    actual_word = str(item["actual_word"])
    anchors = tuple(item["anchors"])
    selected = tuple(range(1, length + 1)) if widths is None else tuple(sorted(set(widths)))
    rows = []
    totals = {
        "context_width_checks": 0,
        "low_type_checks": 0,
        "distinct_factor_checks": 0,
        "grid_bound_checks": 0,
        "grid_recurrence_steps": 0,
        "exact_grid_cases": 0,
    }
    indicator = [0] * length
    for left, _ in anchors:
        indicator[left] = 1
    for width in selected:
        context = width + 2
        U = {start for start in range(length) if window(residual_word, start, context) != window(base_word, start, context)}
        exact_bound = span + E * (width + 1)
        area_bound = 2 * area + E * (width + 1)
        if len(U) > min(length, exact_bound) or exact_bound > area_bound:
            fail("context bound")
        incidence = [0] * length
        for left, right in anchors:
            affected = {
                (position - offset) % length
                for position in (left, right)
                for offset in range(width)
            }
            if len(affected) > min(length, width + 1):
                fail("influence size")
            for start in affected:
                incidence[start] += 1
        low = [start for start in range(length) if start not in U and incidence[start] <= 1]
        low_types = {window(actual_word, start, width) for start in low}
        B1 = (width + 2) * (width + 3)
        if len(low_types) > B1:
            fail("low types")
        factor_count = len(factor_set(actual_word, width))
        distinct = factor_count == length
        rhs = (J + E) * (width + 1) + 4 * area + 2 * B1
        if distinct and 2 * length > rhs:
            fail("double hit")
        w = width + 1
        counts = [sum(indicator[(start + offset) % length] for offset in range(w)) for start in range(length)]
        mismatches = 0
        for start in range(length):
            expected = indicator[(start + w) % length] - indicator[start]
            if counts[(start + 1) % length] - counts[start] != expected:
                fail("grid recurrence")
            mismatches += expected != 0
        bad = sum(value != 2 for value in counts)
        if mismatches > 2 * bad:
            fail("grid defect")
        exact = bad == 0
        if exact and w // math.gcd(length, w) not in (1, 2):
            fail("grid denominator")
        rows.append([width, len(U), exact_bound, area_bound, len(low_types), B1, factor_count, int(distinct), sum(incidence), K * (width + 1), rhs, bad, mismatches])
        totals["context_width_checks"] += 1
        totals["low_type_checks"] += 1
        totals["distinct_factor_checks"] += int(distinct)
        totals["grid_bound_checks"] += 1
        totals["grid_recurrence_steps"] += length
        totals["exact_grid_cases"] += int(exact)
    result = {key: item[key] for key in ("q", "L", "area", "height", "J", "sigma", "E", "K", "residual_span")}
    result.update(totals)
    result["factor_rows"] = rows
    return result


def corpus() -> tuple[dict[str, int], str]:
    totals = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "static_reconstructions": 0,
        "extracted_swaps": 0,
        "exceptional_components": 0,
        "context_width_checks": 0,
        "low_type_checks": 0,
        "distinct_factor_checks": 0,
        "grid_bound_checks": 0,
        "grid_recurrence_steps": 0,
        "exact_grid_cases": 0,
    }
    digest_rows = []
    for q in range(1, 9):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            classes = sorted({cyclic_class(row) for row in compositions(length, q)})
            for values in classes:
                totals["cyclic_classes"] += 1
                totals["primitive_classes"] += int(primitive(values))
                totals["noncoprime_classes"] += int(math.gcd(q, length) > 1)
                for rotated in minimum_rotations(values):
                    row = audit(rotated)
                    totals["minimum_rotations"] += 1
                    totals["static_reconstructions"] += 1
                    totals["extracted_swaps"] += int(row["K"])
                    totals["exceptional_components"] += int(row["E"])
                    for key in ("context_width_checks", "low_type_checks", "distinct_factor_checks", "grid_bound_checks", "grid_recurrence_steps", "exact_grid_cases"):
                        totals[key] += int(row[key])
                    digest_rows.append([list(rotated), row])
    return totals, stable_hash(digest_rows)


def mechanical(q: int, length: int) -> tuple[int, ...]:
    common = math.gcd(q, length)
    q0, L0 = q // common, length // common
    def ceil_div(value: int) -> int:
        return -(-value // q0)
    return tuple(
        ceil_div(L0 * (index + 1)) - ceil_div(L0 * index)
        for index in range(q)
    )


def synth_profiles() -> dict[str, tuple[int, int, tuple[int, ...]]]:
    def tall(q: int, length: int, height: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        answer = [0, height]
        for index in range(1, q):
            answer.append(answer[-1] - int(bool(answer[-1]) and base[index] == 2))
        return tuple(answer)

    def plateau(q: int, length: int, height: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        descents = sorted(index for index, value in enumerate(base) if value == 2)[-height:]
        answer = [0]
        for index in range(q):
            if index == 0:
                answer.append(height)
            else:
                answer.append(answer[-1] - int(index in descents and answer[-1] > 0))
        return tuple(answer)

    def isolated(q: int, length: int, count: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        answer = [0]
        started = 0
        for index in range(q):
            current = answer[-1]
            if current and base[index] == 2:
                answer.append(0)
            elif current == 0 and started < count and 2 in base[index + 1 :]:
                answer.append(1)
                started += 1
            else:
                answer.append(current)
        return tuple(answer)

    def near_extremal(q: int, length: int, height: int, target: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        answer = [0]
        isolated_left = target - height
        started = False
        for index in range(q):
            current = answer[-1]
            if not started:
                answer.append(height)
                started = True
            elif current and base[index] == 2:
                answer.append(current - 1)
            elif current == 0 and isolated_left and 2 in base[index + 1 :]:
                answer.append(1)
                isolated_left -= 1
            else:
                answer.append(current)
        return tuple(answer)

    def width_two(q: int, length: int, count: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        answer = [0] * (q + 1)
        for start in range(1, q - 1):
            if count == 0:
                break
            if base[start + 1] == 2 and not any(answer[max(0, start - 1) : start + 3]):
                answer[start : start + 2] = [1, 1]
                count -= 1
        return tuple(answer)

    def multipeak(q: int, length: int, heights: Sequence[int]) -> tuple[int, ...]:
        base = mechanical(q, length)
        pending = list(heights)
        answer = [0]
        for index in range(q):
            current = answer[-1]
            if current == 0 and pending:
                answer.append(pending.pop(0))
            elif current and base[index] == 2:
                answer.append(current - 1)
            else:
                answer.append(current)
        return tuple(answer)

    def near_grid(q: int, length: int, modulus: int, count: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        boundary = boundaries(base)
        answer = [0] * (q + 1)
        selected = []
        for label in range(1, q):
            if base[label] == 2 and boundary[label] % modulus == 0 and all(abs(label - old) > 1 for old in selected):
                selected.append(label)
            if len(selected) == count:
                break
        for label in selected:
            answer[label] = 1
        return tuple(answer)

    def residual_heavy(q: int, length: int) -> tuple[int, ...]:
        base = mechanical(q, length)
        answer = list(width_two(q, length, 24))
        left = 24
        for label in range(1, q):
            if left == 0:
                break
            if base[label] == 2 and not any(answer[max(0, label - 1) : label + 2]):
                answer[label] = 1
                left -= 1
        return tuple(answer)

    residue = [0] * 77
    for index in (11, 22, 33):
        residue[index] = 1
    seven = tuple(residue[(-123 * index) % 77] for index in range(77)) + (0,)
    return {
        "tall": (125, 199, tall(125, 199, 5)),
        "plateau": (125, 199, plateau(125, 199, 5)),
        "isolated": (125, 199, isolated(125, 199, 20)),
        "near-extremal": (1331, 2110, near_extremal(1331, 2110, 9, 124)),
        "seven-grid": (77, 123, seven),
        "width-two": (377, 600, width_two(377, 600, 32)),
        "multiple-peaks": (377, 600, multipeak(377, 600, (5, 7, 4, 8, 6))),
        "near-grid-singletons": (377, 600, near_grid(377, 600, 13, 16)),
        "residual-heavy": (377, 600, residual_heavy(377, 600)),
    }


def logarithm(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    # log(value)=2*sum z^(2k+1)/(2k+1), z=(value-1)/(value+1).
    z = (value - 1) / (value + 1)
    total = Fraction(0)
    power = z
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= z * z
    low = 2 * total
    remainder = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return low, low + remainder


def hit_cube(slope: Fraction) -> Fraction:
    return Fraction(27, 2) * slope * slope / (slope - 1)


def verify(directory: Path) -> dict[str, object]:
    for name in FILES:
        if not (directory / name).is_file():
            fail(f"missing {name}")
    theory = load(directory / FILES[0])
    corpus_artifact = load(directory / FILES[1])
    scalar = load(directory / FILES[2])
    synthetic = load(directory / FILES[3])
    regressions = load(directory / FILES[4])
    report = (directory / FILES[5]).read_text(encoding="utf-8")

    statuses = {key: row["status"] for key, row in theory.get("claims", {}).items()}
    if statuses != EXPECTED or theory.get("proves_collatz") is not False:
        fail("claim statuses")
    if "does not imply global shift invariance" not in str(theory.get("proposal_repair", "")):
        fail("grid repair")
    if "EXT17" not in theory.get("dependencies", {}).get("P188", []):
        fail("critical dependency")

    counts, digest = corpus()
    if corpus_artifact.get("counts") != counts or corpus_artifact.get("row_digest_sha256") != digest:
        fail("corpus reconstruction")
    if counts["context_width_checks"] != 45369 or counts["distinct_factor_checks"] != 27832:
        fail("corpus count regression")

    expected_profiles = synth_profiles()
    widths = (1, 2, 3, 5, 8, 13, 21, 34, 55, 89)
    rebuilt_rows = []
    for row in synthetic.get("rows", []):
        name, q, length, stored_profile, stored_values, stored_audit = row
        if name not in expected_profiles or expected_profiles[name] != (q, length, tuple(stored_profile)):
            fail("synthetic profile")
        values = exponents_from_profile(mechanical(q, length), stored_profile)
        if list(values) != stored_values:
            fail("synthetic exponents")
        checked = audit(values, tuple(width for width in widths if width <= length))
        if checked != stored_audit:
            fail("synthetic audit")
        rebuilt_rows.append([name, q, length, stored_profile, stored_values, checked])
    if len(rebuilt_rows) != 9 or synthetic.get("row_digest_sha256") != stable_hash(rebuilt_rows):
        fail("synthetic digest")

    alpha_stored = tuple(decode(row) for row in scalar.get("log2_three_interval", []))
    ln2 = logarithm(Fraction(2), 176)
    ln_three_halves = logarithm(Fraction(3, 2), 176)
    ln3 = (ln2[0] + ln_three_halves[0], ln2[1] + ln_three_halves[1])
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    if len(alpha_stored) != 2 or not alpha_stored[0] <= alpha[0] < alpha[1] <= alpha_stored[1]:
        fail("log enclosure")
    critical = tuple(decode(row) for row in scalar.get("critical_constant_cube_interval", []))
    if len(critical) != 2 or not critical[0] <= hit_cube(alpha[1]) < hit_cube(alpha[0]) <= critical[1]:
        fail("critical constant")
    old = tuple(decode(row) for row in scalar.get("phase30_constant_cube_interval", []))
    if critical != tuple(4 * value for value in old):
        fail("cube factor")
    if decode(scalar.get("noncritical_constant_cube", [])) != 54:
        fail("noncritical constant")

    expected_names = {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}
    if {row[0] for row in regressions.get("mandatory_families", [])} != expected_names:
        fail("mandatory families")
    model = regressions.get("NG40_normalized_countermodel", {})
    if model.get("slope") != 2 or model.get("k") != 0 or model.get("u_over_q") != 2:
        fail("NG40 normalized model")
    if "does not imply global approximate-grid invariance" not in str(model.get("interpretation", "")):
        fail("NG40 interpretation")
    if "45,369 exact widths" not in report or "H172 and H133 remain OPEN" not in report or "proves_collatz=false" not in report:
        fail("obstruction report")

    hashes = {name: sha256(directory / name) for name in FILES}
    return {
        "format": "collatz-phase31-independent-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "independence": "recursive compositions, direct residual-profile reconstruction, same-position context differences, literal static swaps, independent profile recurrences, and a 176-term rational logarithm box",
        "claims": EXPECTED,
        "corpus_counts": counts,
        "scalar_counts": {"log_terms": 176, "slope_rows": len(scalar.get("slope_rows", []))},
        "synthetic_counts": {"profiles": len(rebuilt_rows), "factor_width_checks": sum(len(row[-1]["factor_rows"]) for row in rebuilt_rows)},
        "verified_input_sha256": hashes,
        "proves_collatz": False,
        "what_this_result_does_not_prove": "This does not prove H172, H133, any nonperiodic exclusion, or Collatz.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.artifact_dir)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
