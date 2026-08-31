#!/usr/bin/env python3
"""Independently verify Phase 30 direct-transport artifacts.

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
    "phase30_theory.json",
    "phase30_transport_corpus.json",
    "phase30_scalar_certificates.json",
    "phase30_synthetic_profiles.json",
    "phase30_regressions.json",
    "phase30_obstruction_report.md",
)
EXPECTED = {
    "P179": "VERIFIED_THEOREM",
    "P180": "VERIFIED_THEOREM",
    "P181": "VERIFIED_THEOREM",
    "P182": "VERIFIED_THEOREM",
    "P183": "VERIFIED_THEOREM",
    "P184": "VERIFIED_THEOREM",
    "E42": "VERIFIED_FINITE",
    "NG39": "REFUTED",
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
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def pair(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def fraction(value: Sequence[str]) -> Fraction:
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
    return all(row != row[:period] * (len(row) // period) for period in range(1, len(row)) if len(row) % period == 0)


def reduced_data(values: Sequence[int]) -> dict[str, object]:
    row = tuple(values)
    q, length = len(row), sum(row)
    common = math.gcd(q, length)
    q0, L0 = q // common, length // common
    heights = [0]
    for value in row:
        heights.append(heights[-1] + q0 * value - L0)
    residues = [(-L0 * index) % q0 for index in range(q + 1)]
    profile = []
    for height, residue in zip(heights, residues, strict=True):
        if (height - residue) % q0:
            fail("profile divisibility")
        profile.append((height - residue) // q0)
    boundaries = [(L0 * index + residues[index]) // q0 for index in range(q + 1)]
    base = tuple(boundaries[index + 1] - boundaries[index] for index in range(q))
    if min(profile) < 0 or profile[0] or profile[-1] or set(base) - {1, 2}:
        fail("reduced profile")
    actual = [0]
    for value in row:
        actual.append(actual[-1] + value)
    if actual != [boundaries[index] + profile[index] for index in range(q + 1)]:
        fail("boundary reconstruction")
    return {"q": q, "L": length, "d": common, "q0": q0, "L0": L0, "profile": tuple(profile), "base": base}


def minimum_rotations(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    result = []
    for row in rotations(values):
        data = reduced_data_unshifted(row)
        if min(data) == 0:
            result.append(row)
    return tuple(sorted(set(result)))


def reduced_data_unshifted(values: Sequence[int]) -> tuple[int, ...]:
    q, length = len(values), sum(values)
    common = math.gcd(q, length)
    q0, L0 = q // common, length // common
    answer = [0]
    for value in values:
        answer.append(answer[-1] + q0 * value - L0)
    return tuple(answer)


def expanded(values: Sequence[int]) -> str:
    return "".join("1" + "0" * (value - 1) for value in values)


def factor_set(word: str, width: int) -> set[str]:
    extended = word + word[: width - 1]
    return {extended[index : index + width] for index in range(len(word))}


def level_intervals(profile: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], ...]:
    q = len(profile) - 1
    levels = []
    for level in range(1, max(profile[:-1], default=0) + 1):
        starts = []
        start = None
        for index in range(q + 1):
            active = index < q and profile[index] >= level
            if active and start is None:
                start = index
            if not active and start is not None:
                starts.append((start, index))
                start = None
        levels.append(tuple(starts))
    return tuple(levels)


def exponents_from_profile(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    values = tuple(base[index] + profile[index + 1] - profile[index] for index in range(len(base)))
    if min(values) < 1:
        fail("profile exponent")
    return values


def audit(values: Sequence[int], widths: Sequence[int] | None = None) -> dict[str, object]:
    data = reduced_data(values)
    base = tuple(data["base"])
    profile = tuple(data["profile"])
    q, length = int(data["q"]), int(data["L"])
    boundaries = [0]
    for value in base:
        boundaries.append(boundaries[-1] + value)
    intervals = level_intervals(profile)
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    J = sum(len(rows) for rows in intervals)
    span = sum(boundaries[end] - boundaries[start] for rows in intervals for start, end in rows)
    if span > 2 * area or q * span > length * area + q * J:
        fail("span bounds")
    peak = profile[:-1].index(height) if height else 0
    spine = []
    all_intervals = [interval for rows in intervals for interval in rows]
    for rows in intervals:
        if height:
            candidates = [interval for interval in rows if interval[0] <= peak < interval[1]]
            if len(candidates) != 1:
                fail("nested spine")
            spine.append(candidates[0])
    p = length - q
    descent_floor = sum((level * q) // p for level in range(height))
    descent_slack = area - J - descent_floor
    spine_excess = sum(end - start - 1 for start, end in spine)
    nonspine_excess = area - J - spine_excess
    nonspine_nonsingleton = sum(interval not in spine and interval[1] - interval[0] > 1 for interval in all_intervals)
    if spine_excess < descent_floor or nonspine_excess > descent_slack or nonspine_nonsingleton > nonspine_excess:
        fail("secondary peak charging")
    current_profile = [0] * (q + 1)
    current_word = expanded(base)
    operations = []
    for level, rows in enumerate(intervals, start=1):
        if current_profile != [min(value, level - 1) for value in profile]:
            fail("truncation state")
        for start_label, end_label in rows:
            before = current_word
            for index in range(start_label, end_label):
                current_profile[index] += 1
            current_word = expanded(exponents_from_profile(base, current_profile))
            start = boundaries[start_label] + level - 1
            end = boundaries[end_label] + level - 1
            old_segment = before[start:end]
            if not old_segment or current_word[start:end] != old_segment[-1] + old_segment[:-1]:
                fail("independent block rotation")
            if before[:start] != current_word[:start] or before[end:] != current_word[end:]:
                fail("rotation support")
            operations.append((end - start, before, current_word))
    if current_word != expanded(values) or len(operations) != J:
        fail("final direct transport")
    selected = tuple(range(1, length + 1)) if widths is None else tuple(sorted(set(widths)))
    factor_rows = []
    equalities = []
    affected_checks = 0
    base_word = expanded(base)
    for width in selected:
        baseline = factor_set(base_word, width)
        actual = factor_set(current_word, width)
        direct = len(baseline) + span + J * (width - 1)
        area_bound = (J + 1) * width + 2 * area + 1
        if len(baseline) > width + 1 or len(actual) > direct or direct > area_bound:
            fail("factor bound")
        new_total = 0
        for operation_span, before_word, after_word in operations:
            new = len(factor_set(after_word, width) - factor_set(before_word, width))
            if new > min(length, operation_span + width - 1):
                fail("affected starts")
            new_total += new
            affected_checks += 1
        if len(actual) > len(baseline) + new_total:
            fail("factor telescoping")
        if len(actual) == direct:
            equalities.append(width)
        factor_rows.append([width, len(baseline), len(actual), direct, area_bound, new_total])
    return {
        "q": q,
        "L": length,
        "area": area,
        "height": height,
        "J": J,
        "transport_span": span,
        "descent_floor": descent_floor,
        "descent_slack": descent_slack,
        "spine_excess": spine_excess,
        "nonspine_excess": nonspine_excess,
        "nonspine_nonsingleton": nonspine_nonsingleton,
        "component_rotation_checks": len(operations),
        "affected_start_checks": affected_checks,
        "equality_widths": equalities,
        "factor_rows": factor_rows,
    }


def verify_corpus(stored: dict[str, object]) -> dict[str, int]:
    counts = {key: 0 for key in (
        "cyclic_classes", "primitive_classes", "noncoprime_classes", "minimum_rotations",
        "factor_width_checks", "component_rotation_checks", "affected_start_checks", "span_checks", "spine_charging_checks",
    )}
    rows = []
    samples = []
    for q in range(1, 9):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                counts["noncoprime_classes"] += int(math.gcd(q, length) > 1)
                for rotated in minimum_rotations(values):
                    item = audit(rotated)
                    counts["minimum_rotations"] += 1
                    counts["factor_width_checks"] += len(item["factor_rows"])
                    counts["component_rotation_checks"] += item["component_rotation_checks"]
                    counts["affected_start_checks"] += item["affected_start_checks"]
                    counts["span_checks"] += 2
                    counts["spine_charging_checks"] += 3
                    row = [list(rotated), item]
                    rows.append(row)
                    if item["equality_widths"] and len(samples) < 8:
                        samples.append(row)
    if counts != stored.get("counts") or stable_hash(rows) != stored.get("row_digest_sha256") or samples != stored.get("equality_samples"):
        fail("corpus reconstruction")
    return counts


def outward(lower: Fraction, upper: Fraction, bits: int = 384) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    return Fraction(lower.numerator * scale // lower.denominator, scale), Fraction(-(-upper.numerator * scale // upper.denominator), scale)


def log_box(value: Fraction, terms: int = 160) -> tuple[Fraction, Fraction]:
    z = (value - 1) / (value + 1)
    total = Fraction()
    power = z
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= z * z
    lower = 2 * total
    remainder = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return outward(lower, lower + remainder)


def move_cube(slope: Fraction) -> Fraction:
    return Fraction(27, 8) * slope * slope / (slope - 1)


def phase28_cube(slope: Fraction) -> Fraction:
    return Fraction(27, 32) * slope * slope / (slope - 1)


def verify_scalar(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("log_terms") != 96 or stored.get("proves_collatz") is not False:
        fail("scalar metadata")
    ln2, ln3 = log_box(Fraction(2)), log_box(Fraction(3))
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    stored_alpha = tuple(fraction(row) for row in stored["log2_three_interval"])
    if not stored_alpha[0] <= alpha[0] <= alpha[1] <= stored_alpha[1]:
        fail("alpha enclosure")
    critical = tuple(fraction(row) for row in stored["critical_constant_cube_interval"])
    tight_critical = (move_cube(alpha[1]), move_cube(alpha[0]))
    if not critical[0] <= tight_critical[0] <= tight_critical[1] <= critical[1]:
        fail("critical enclosure")
    old = tuple(fraction(row) for row in stored["phase28_constant_cube_interval"])
    if critical != (4 * old[0], 4 * old[1]):
        fail("exact improvement")
    noncritical = fraction(stored["noncritical_constant_cube"])
    if noncritical != Fraction(27, 2):
        fail("noncritical constant")
    rows = []
    for slope in (Fraction(8, 5), Fraction(5, 3), Fraction(7, 4), Fraction(19, 10), Fraction(2)):
        cube = move_cube(slope)
        rows.append([pair(slope), pair(cube), cube >= noncritical])
    if rows != stored.get("slope_rows"):
        fail("slope rows")
    decimal = [fraction(row) for row in stored["critical_constant_decimal_box"]]
    if decimal != [Fraction(2_438_154, 1_000_000), Fraction(2_438_155, 1_000_000)]:
        fail("critical decimal")
    if not decimal[0] ** 3 <= critical[0] <= critical[1] <= decimal[1] ** 3:
        fail("critical decimal enclosure")
    near = stored.get("near_extremal")
    height = tuple(fraction(row) for row in near["height_scale_cube_interval"])
    transport = tuple(fraction(row) for row in near["transport_scale_cube_interval"])
    tight_height = (alpha[0] * (alpha[0] - 1), alpha[1] * (alpha[1] - 1))
    tight_transport = (alpha[0] ** 2 / (alpha[1] - 1), alpha[1] ** 2 / (alpha[0] - 1))
    if not height[0] <= tight_height[0] <= tight_height[1] <= height[1]:
        fail("height scale")
    if not transport[0] <= tight_transport[0] <= tight_transport[1] <= transport[1]:
        fail("transport scale")
    if fraction(near["area_over_transport"]) != Fraction(3, 2) or "No ratio-one" not in near["not_proved"]:
        fail("rigidity boundary")
    return {"slope_rows": len(rows), "log_terms": 160}


def base_word(q: int, length: int) -> tuple[int, ...]:
    common = math.gcd(q, length)
    q0, L0 = q // common, length // common
    boundaries = [(L0 * index + q0 - 1) // q0 for index in range(q + 1)]
    return tuple(boundaries[index + 1] - boundaries[index] for index in range(q))


def synthetic_profiles() -> list[tuple[str, int, int, tuple[int, ...]]]:
    result = []
    q, length = 125, (3**125).bit_length()
    base = base_word(q, length)
    profile = [0, 5]
    for index in range(1, q):
        profile.append(profile[-1] - 1 if profile[-1] and base[index] == 2 else profile[-1])
    result.append(("tall", q, length, tuple(profile)))
    selected = {index for index, value in list(enumerate(base))[::-1] if value == 2}
    selected = set(sorted(selected)[-5:])
    profile = [0]
    for index in range(q):
        profile.append(5 if index == 0 else profile[-1] - 1 if index in selected and profile[-1] else profile[-1])
    result.append(("plateau", q, length, tuple(profile)))
    profile = [0]
    remaining = 20
    for index in range(q):
        if profile[-1] and base[index] == 2:
            profile.append(0)
        elif not profile[-1] and remaining and 2 in base[index + 1 :]:
            profile.append(1)
            remaining -= 1
        else:
            profile.append(profile[-1])
    result.append(("isolated", q, length, tuple(profile)))
    q, length = 1331, (3**1331).bit_length()
    base = base_word(q, length)
    profile = [0]
    remaining, started = 115, False
    for index in range(q):
        if not started:
            profile.append(9)
            started = True
        elif profile[-1] and base[index] == 2:
            profile.append(profile[-1] - 1)
        elif not profile[-1] and remaining and 2 in base[index + 1 :]:
            profile.append(1)
            remaining -= 1
        else:
            profile.append(profile[-1])
    result.append(("near-extremal", q, length, tuple(profile)))
    q, length = 77, 123
    residue = [0] * q
    for root in (11, 22, 33):
        residue[root] = 1
    profile = tuple(residue[(-length * index) % q] for index in range(q)) + (0,)
    result.append(("seven-grid", q, length, profile))
    return result


def verify_synthetic(stored: dict[str, object]) -> dict[str, int]:
    rows = []
    widths = (1, 2, 3, 4, 5, 8, 13, 21, 34, 55)
    for name, q, length, profile in synthetic_profiles():
        values = exponents_from_profile(base_word(q, length), profile)
        item = audit(values, tuple(width for width in widths if width <= length))
        rows.append([name, q, length, sum(profile[:-1]), max(profile[:-1]), item["J"], item])
    if rows != stored.get("rows") or stable_hash(rows) != stored.get("row_digest_sha256"):
        fail("synthetic reconstruction")
    return {"profiles": len(rows), "factor_width_checks": sum(len(row[-1]["factor_rows"]) for row in rows)}


def bit_exponents(bits: str) -> tuple[int, ...]:
    positions = [index for index, value in enumerate(bits) if value == "1"]
    return tuple((positions[(i + 1) % len(positions)] - position) % len(bits) or len(bits) for i, position in enumerate(positions))


def verify_regressions(stored: dict[str, object]) -> None:
    if stored.get("proves_collatz") is not False:
        fail("regression overclaim")
    witness = audit((2, 2, 1, 3, 1, 1))
    row = next(item for item in witness["factor_rows"] if item[0] == 4)
    expected = stored.get("no_span_counterexample")
    if witness["transport_span"] != 2 or row != [4, 5, 10, 10, 11, 5] or expected.get("overstrong_bound") != 9 or expected.get("actual") != 10:
        fail("NG39")
    labels = {row[0] for row in stored.get("mandatory_families", [])}
    if labels != {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}:
        fail("mandatory families")
    controls = stored.get("named_controls")
    if controls.get("negative_q2") != [1, 2] or controls.get("negative_q7") != [1, 1, 1, 2, 1, 1, 4]:
        fail("negative controls")
    for power, area, J, span in controls.get("trivial_powers", []):
        item = audit((2,) * power)
        if [item["area"], item["J"], item["transport_span"]] != [area, J, span]:
            fail("trivial powers")
    if "not derived" not in stored.get("proposal_repair", ""):
        fail("proposal repair")


def verify_theory(stored: dict[str, object]) -> None:
    if stored.get("proves_collatz") is not False:
        fail("Collatz overclaim")
    claims = stored.get("claims")
    if not isinstance(claims, dict) or {key: value.get("status") for key, value in claims.items()} != EXPECTED:
        fail("claim statuses")
    deps = stored.get("dependencies")
    if deps.get("P182") != ["P163", "P164", "P181", "EXT17"] or deps.get("P184") != ["P167", "P183"]:
        fail("dependency boundary")
    if "Only P182's critical" not in stored.get("external_boundary", ""):
        fail("external boundary")
    if "not accepted" not in stored.get("proposal_repair", "") or "Collatz proof" not in stored.get("what_this_result_does_not_prove", ""):
        fail("interpretation boundary")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    for name in FILES:
        if not (args.artifact_dir / name).is_file():
            fail(f"missing {name}")
    theory = load(args.artifact_dir / "phase30_theory.json")
    scalar = load(args.artifact_dir / "phase30_scalar_certificates.json")
    regressions = load(args.artifact_dir / "phase30_regressions.json")
    report = (args.artifact_dir / "phase30_obstruction_report.md").read_text(encoding="utf-8")
    verify_theory(theory)
    scalar_counts = verify_scalar(scalar)
    verify_regressions(regressions)
    if "45,369 exact factor-width checks" not in report or "proves_collatz=false" not in report:
        fail("obstruction report")
    corpus_counts = verify_corpus(load(args.artifact_dir / "phase30_transport_corpus.json"))
    synthetic_counts = verify_synthetic(load(args.artifact_dir / "phase30_synthetic_profiles.json"))
    result = {
        "format": "collatz-phase30-independent-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "independence": "recursive compositions, direct boundary/profile reconstruction, factor-set differences, separately synthesized profiles, and a 160-term rational logarithm box",
        "claims": EXPECTED,
        "corpus_counts": corpus_counts,
        "scalar_counts": scalar_counts,
        "synthetic_counts": synthetic_counts,
        "verified_input_sha256": {name: sha256(args.artifact_dir / name) for name in FILES},
        "proves_collatz": False,
        "what_this_result_does_not_prove": "This does not prove H172, H133, any nonperiodic exclusion, or Collatz.",
    }
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
