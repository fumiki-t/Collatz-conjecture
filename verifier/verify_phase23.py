#!/usr/bin/env python3
"""Independent exact verifier for Phase 23 defect-area artifacts.

This verifier deliberately imports no generator module.  It rebuilds critical
words from integer prefix states and cycle profiles from literal height walks.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


FILES = (
    "phase23_theory.json",
    "phase23_critical_words.json",
    "phase23_cycle_profiles.json",
    "phase23_regressions.json",
    "phase23_obstruction_report.md",
)
QMAX = 17
DIRECT_QMAX = 12
PROFILE_QMAX = 22
PROFILE_AMAX = 2
COMPOSITION_QMAX = 8
A_BITS = "11101"
B_BITS = "1100"
NEGATIVE_Q7 = (1, 1, 1, 2, 1, 1, 4)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} must contain an object")
    return value


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def row_hash(rows) -> str:
    value = hashlib.sha256()
    for row in rows:
        value.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n")
    return value.hexdigest()


def ceiling_ratio_log2(top: int, bottom: int) -> int:
    if top <= 0 or bottom <= 0:
        fail("log fraction domain")
    answer = 0
    power = bottom
    while power < top:
        power *= 2
        answer += 1
    return answer


def height_table(maximum: int) -> dict[int, tuple[int, int, int, int, int]]:
    output = {}
    three, correction = 1, 0
    for odd in range(1, maximum + 1):
        correction = 3 * correction + 2 ** (three.bit_length() - 1)
        three *= 3
        length = three.bit_length()
        gap = 2**length - three
        width = ceiling_ratio_log2(3 * correction + odd * gap, gap)
        numerator = length - 2 * width
        numerator -= 1
        lower = 0 if numerator <= 0 else (numerator + width + 1) // (width + 2)
        output[odd] = correction, gap, length, width, lower
    return output


def critical_words(maximum: int):
    endpoints = {(3**odd).bit_length() - 1: odd for odd in range(1, maximum + 1)}
    layer = [(0, 0, 0, 0)]  # bit integer, length, odd count, affine correction
    for length in range(1, max(endpoints) + 1):
        next_layer = []
        for bits, _, odd, affine in layer:
            if odd and 3**odd > 2**length:
                next_layer.append((bits << 1, length, odd, affine))
            if odd < maximum and 3 ** (odd + 1) > 2**length:
                next_layer.append(((bits << 1) | 1, length, odd + 1, 3 * affine + 2 ** (length - 1)))
        layer = next_layer
        target = endpoints.get(length)
        if target is not None:
            for bits, _, odd, affine in layer:
                if odd == target:
                    prefix = format(bits, f"0{length}b")
                    yield target, prefix + "0", affine


def base_word(odd: int) -> tuple[str, tuple[int, ...]]:
    size = (3**odd).bit_length()
    locations = tuple((3**rank).bit_length() - 1 for rank in range(odd))
    result = ["0"] * size
    for place in locations:
        result[place] = "1"
    return "".join(result), locations


def cumulative(word: str) -> list[int]:
    result = [0]
    for symbol in word:
        result.append(result[-1] + int(symbol == "1"))
    return result


def area_record(word: str, odd: int) -> tuple[int, int, int, tuple[int, ...]]:
    base, base_locations = base_word(odd)
    locations = tuple(i for i, symbol in enumerate(word) if symbol == "1")
    defects = tuple(a - b for a, b in zip(base_locations, locations, strict=True))
    if min(defects, default=0) < 0:
        fail("negative critical defect")
    differences = [a - b for a, b in zip(cumulative(word), cumulative(base), strict=True)]
    if min(differences) < 0 or sum(differences) != sum(defects):
        fail("critical area identity")
    # Independently reconstruct the actual 01->10 swap chain, left to right.
    work = list(base)
    swaps = 0
    targets = list(locations)
    for rank, target in enumerate(targets):
        current = [index for index, bit in enumerate(work) if bit == "1"][rank]
        while current > target:
            if work[current - 1 : current + 1] != ["0", "1"]:
                fail("critical literal swap")
            work[current - 1], work[current] = "1", "0"
            current -= 1
            swaps += 1
    if "".join(work) != word or swaps != sum(defects):
        fail("critical swap count")
    return sum(defects), sum(x > 0 for x in differences), sum(x == 0 for x in differences), defects


def linear_factors(word: str, width: int) -> set[str]:
    return {word[index : index + width] for index in range(0, len(word) - width + 1)}


def old_repeat_rejection(word: str, bmax: int, gap: int) -> bool:
    safe = word[:-1]
    prefix = cumulative(safe)
    for later in range(1, len(safe)):
        best = 0
        for earlier in range(later):
            width = 0
            while later + width < len(safe) and safe[earlier + width] == safe[later + width]:
                width += 1
            best = max(best, width)
        if best:
            ones = prefix[later]
            if 2 ** (best + ones) * gap >= (bmax + gap) * 3**ones:
                return True
    return False


def cylinder_source(word: str, correction: int) -> int:
    modulus = 2 ** len(word)
    odd = word.count("1")
    value = (-correction * pow(3**odd, -1, modulus)) % modulus
    return value if value else modulus


def shortcut(source: int, length: int) -> tuple[str, list[int]]:
    states = [source]
    symbols = []
    value = source
    for _ in range(length):
        symbols.append(str(value & 1))
        value = (3 * value + 1) // 2 if value & 1 else value // 2
        states.append(value)
    return "".join(symbols), states


def expected_critical() -> dict[str, object]:
    heights = height_table(QMAX)
    counts = {}
    for q in range(1, QMAX + 1):
        counts[q] = {
            "critical_words": 0, "area_sum": 0, "minimum_area": None, "maximum_area": 0,
            "area_lower_bound": heights[q][4], "area_rejected": 0, "bounded_source_rows": 0,
            "contact_height_checks": 0, "factor_width_checks": 0,
            "p132_rejected": 0 if q <= DIRECT_QMAX else None,
            "union_rejected": 0 if q <= DIRECT_QMAX else None,
            "phase23_only": 0 if q <= DIRECT_QMAX else None,
            "phase21_only": 0 if q <= DIRECT_QMAX else None,
        }
    rows = []
    best = (0, 1, None)
    for q, word, correction in critical_words(QMAX):
        bmax, gap, length, width_limit, lower = heights[q]
        area, noncontacts, contacts, defects = area_record(word, q)
        record = counts[q]
        record["critical_words"] += 1
        record["area_sum"] += area
        record["minimum_area"] = area if record["minimum_area"] is None else min(record["minimum_area"], area)
        record["maximum_area"] = max(record["maximum_area"], area)
        area_bad = area < lower
        record["area_rejected"] += area_bad
        source = cylinder_source(word, correction)
        if source * gap <= bmax:
            literal, states = shortcut(source, length)
            if literal != word:
                fail("critical literal cylinder")
            record["bounded_source_rows"] += 1
            base, _ = base_word(q)
            differences = [a - b for a, b in zip(cumulative(word), cumulative(base), strict=True)]
            for start in range(length):
                if differences[start] == 0:
                    if states[start] * gap >= 3 * bmax + q * gap:
                        fail("contact state height")
                    record["contact_height_checks"] += 1
        p132 = False
        if q <= DIRECT_QMAX:
            base, _ = base_word(q)
            for width in range(1, length + 1):
                actual = len(linear_factors(word, width))
                baseline = len(linear_factors(base, width))
                corrected = (area + 1) * (width + 1) + 1
                if baseline > width + 2 or actual > corrected:
                    fail("factor perturbation")
                record["factor_width_checks"] += 1
                if actual * best[1] > best[0] * corrected:
                    best = (actual, corrected, [q, word, width])
            p132 = old_repeat_rejection(word, bmax, gap)
            record["p132_rejected"] += p132
            record["union_rejected"] += area_bad or p132
            record["phase23_only"] += area_bad and not p132
            record["phase21_only"] += p132 and not area_bad
        rows.append([q, word, correction, source, area, noncontacts, contacts, list(defects), width_limit, lower, int(area_bad), int(p132)])
    totals = {
        "critical_words": sum(x["critical_words"] for x in counts.values()),
        "area_rejected": sum(x["area_rejected"] for x in counts.values()),
        "bounded_source_rows": sum(x["bounded_source_rows"] for x in counts.values()),
        "contact_height_checks": sum(x["contact_height_checks"] for x in counts.values()),
        "factor_width_checks": sum(x["factor_width_checks"] for x in counts.values()),
        "p132_rejected_through_q12": sum(x["p132_rejected"] or 0 for x in counts.values()),
        "union_rejected_through_q12": sum(x["union_rejected"] or 0 for x in counts.values()),
    }
    return {
        "format": "collatz-phase23-critical-v1", "maximum_q": QMAX,
        "factor_direct_maximum_q": DIRECT_QMAX,
        "counts_by_q": {str(q): row for q, row in counts.items()}, "totals": totals,
        "maximum_factor_bound_ratio": {"numerator": best[0], "denominator": best[1], "witness": best[2]},
        "row_digest_sha256": row_hash(rows),
        "finite_boundary": "Complete through q<=17 for area/contact aggregates; literal factor and P132 comparison complete through q<=12 only.",
        "proves_collatz": False,
    }


def positive_compositions(total: int, parts: int):
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for rest in positive_compositions(total - first, parts - 1):
            yield (first,) + rest


def turns(values: tuple[int, ...]):
    for start in range(len(values)):
        yield values[start:] + values[:start]


def canonical_class(values: tuple[int, ...]) -> tuple[int, ...]:
    return min(turns(values))


def walk(values: tuple[int, ...]) -> tuple[int, ...]:
    q, length = len(values), sum(values)
    current = 0
    output = []
    for exponent in values:
        output.append(current)
        current += q * exponent - length
    if current:
        fail("open cycle height walk")
    return tuple(output)


def minimum_turn(values: tuple[int, ...]) -> tuple[int, ...]:
    candidates = [row for row in turns(values) if min(walk(row)) == 0]
    if not candidates:
        fail("cycle minimum turn")
    return min(candidates)


def residue_profile(values: tuple[int, ...]) -> tuple[int, ...]:
    q, length = len(values), sum(values)
    if math.gcd(q, length) != 1:
        fail("noncoprime residue profile")
    result: list[int | None] = [None] * q
    for height in walk(minimum_turn(values)):
        residue = height % q
        result[residue] = height // q
    if result[0] != 0 or any(value is None or value < 0 for value in result):
        fail("invalid residue profile")
    return tuple(int(value) for value in result)


def recover_profile(q: int, length: int, profile: tuple[int, ...]) -> tuple[int, ...] | None:
    if len(profile) != q or profile[0] != 0 or min(profile) < 0 or math.gcd(q, length) != 1:
        return None
    heights = []
    for time in range(q):
        residue = (-length * time) % q
        heights.append(residue + q * profile[residue])
    answer = []
    for time, height in enumerate(heights):
        following = heights[time + 1] if time + 1 < q else 0
        value, remainder = divmod(following - height + length, q)
        if remainder or value <= 0:
            return None
        answer.append(value)
    result = tuple(answer)
    return result if residue_profile(result) == profile else None


def profiles(q: int, area: int):
    def visit(index: int, remaining: int, prefix: tuple[int, ...]):
        if index == q:
            if remaining == 0:
                yield prefix
            return
        for value in range(remaining + 1):
            yield from visit(index + 1, remaining - value, prefix + (value,))
    if q == 1:
        if area == 0:
            yield (0,)
        return
    yield from visit(1, area, (0,))


def binary_period(values: tuple[int, ...]) -> str:
    return "".join("1" + "0" * (value - 1) for value in values)


def circular_factors(word: str, width: int) -> set[str]:
    extended = word * ((width + len(word) - 1) // len(word) + 1)
    return {extended[start : start + width] for start in range(len(word))}


def adjacent_distance(left: str, right: str) -> int:
    if left.count("1") != right.count("1"):
        fail("word weight mismatch")
    return sum(abs(a - b) for a, b in zip(cumulative(left), cumulative(right), strict=True))


def correction(values: tuple[int, ...]) -> int:
    q, power, answer = len(values), 0, 0
    for index, exponent in enumerate(values):
        answer += 3 ** (q - 1 - index) * 2**power
        power += exponent
    return answer


def valuation2(value: int) -> int:
    if value == 0:
        fail("zero 2-adic valuation")
    value = abs(value)
    answer = 0
    while value % 2 == 0:
        answer += 1
        value //= 2
    return answer


def literal_cycle(source: int, values: tuple[int, ...]) -> tuple[bool, list[int]]:
    result = [source]
    current = source
    for exponent in values:
        numerator = 3 * current + 1
        if valuation2(numerator) != exponent:
            return False, result
        current = numerator // 2**exponent
        result.append(current)
    return current == source, result


def is_primitive(values: tuple[int, ...]) -> bool:
    for period in range(1, len(values)):
        if len(values) % period == 0 and values == values[:period] * (len(values) // period):
            return False
    return True


def expected_cycle() -> dict[str, object]:
    rows = []
    counts = {str(area): 0 for area in range(PROFILE_AMAX + 1)}
    triangular = factor_checks = 0
    best = (0, 1, None)
    for q in range(1, PROFILE_QMAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q or math.gcd(q, length) != 1:
                continue
            baseline = recover_profile(q, length, (0,) * q)
            if baseline is None:
                fail("missing zero profile")
            base = binary_period(baseline)
            for area in range(PROFILE_AMAX + 1):
                for profile in profiles(q, area):
                    values = recover_profile(q, length, profile)
                    if values is None:
                        continue
                    word = binary_period(values)
                    distance = adjacent_distance(base, word)
                    if distance != area:
                        fail("cycle edit area")
                    height = max(profile)
                    if 2 * area < height * (height + 1):
                        fail("cycle triangular area")
                    triangular += 1
                    local = 0
                    for width in range(1, length + 1):
                        actual = len(circular_factors(word, width))
                        base_count = len(circular_factors(base, width))
                        if base_count > width + 1 or actual > (area + 1) * (width + 1):
                            fail("cycle factor complexity")
                        factor_checks += 1
                        local = max(local, actual)
                        if actual * best[1] > best[0] * (area + 1) * (width + 1):
                            best = (actual, (area + 1) * (width + 1), [q, length, list(profile), width])
                    counts[str(area)] += 1
                    rows.append([q, length, list(profile), list(values), area, height, distance, local])

    class_count = integral_count = positive_primitive = separation = 0
    integral_rows = []
    for q in range(1, COMPOSITION_QMAX + 1):
        for length in range(q + 1, 2 * q + 1):
            gap = 2**length - 3**q
            if gap <= 0:
                continue
            classes = sorted({canonical_class(values) for values in positive_compositions(length, q)})
            class_count += len(classes)
            for values in classes:
                canonical = minimum_turn(values)
                affine = correction(canonical)
                if affine % gap:
                    continue
                integral_count += 1
                source = affine // gap
                legal, trace = literal_cycle(source, canonical)
                if not legal:
                    fail("integral cycle literal legality")
                integral_rows.append([q, length, list(canonical), source, is_primitive(canonical), trace])
                if source <= 0 or not is_primitive(canonical) or math.gcd(q, length) != 1:
                    continue
                positive_primitive += 1
                profile = residue_profile(canonical)
                area, height = sum(profile), max(profile)
                ncyc = ceiling_ratio_log2(2 ** (height + 2 + length) * source, 3**q)
                if length > (area + 1) * (ncyc + 1):
                    fail("cycle state separation")
                separation += 1
    return {
        "format": "collatz-phase23-cycle-v1", "profile_maximum_q": PROFILE_QMAX,
        "profile_maximum_area": PROFILE_AMAX, "area_counts": counts,
        "profile_count": sum(counts.values()), "triangular_checks": triangular,
        "cyclic_factor_width_checks": factor_checks,
        "largest_complexity_bound_ratio": {"numerator": best[0], "denominator": best[1], "witness": best[2]},
        "profile_digest_sha256": row_hash(sorted(rows)), "full_composition_q_maximum": COMPOSITION_QMAX,
        "full_cyclic_classes": class_count, "integral_classes": integral_count,
        "primitive_positive_coprime_classes": positive_primitive,
        "factor_separation_checks": separation, "integral_rows": integral_rows,
        "finite_boundary": "The q<=22 profile audit is exhaustive only for area<=2; the full composition audit ends at q<=8.",
        "proves_collatz": False,
    }


def expected_regressions() -> dict[str, object]:
    controls = []
    for m in range(3, 9):
        controls.append(["2^m-1", m, shortcut(2**m - 1, 64)[0]])
        controls.append(["8^m-5", m, shortcut(8**m - 5, 64)[0]])
    for r in range(1, 5):
        for s in range(1, 5):
            controls.append(["A^rB^s", r, s, A_BITS * r + B_BITS * s])
    controls.extend([
        ["A=11101", A_BITS], ["B=1100", B_BITS], ["(110|111)^*", "110111" * 16],
        ["source167", shortcut(167, 96)[0]], ["all-contact-q17", base_word(17)[0]],
    ])
    cycles = []
    for source, values in ((1, (2,)), (-5, (1, 2)), (-17, NEGATIVE_Q7)):
        legal, trace = literal_cycle(source, values)
        cycles.append([source, list(values), legal, trace, source > 0])
    return {
        "format": "collatz-phase23-regressions-v1", "word_controls": controls,
        "word_control_digest_sha256": row_hash(controls), "cycle_controls": cycles,
        "required_failed_approaches": [f"NG{index}" for index in range(21, 32)],
        "scope": "Negative cycles audit algebra and boundary rejection only; they are not inputs to positive state-height or factor-separation claims.",
        "proves_collatz": False,
    }


def verify_theory(value: dict[str, object]) -> None:
    expected_claims = {
        "P141": "VERIFIED_THEOREM", "P142": "CONDITIONAL", "P143": "CONDITIONAL",
        "P144": "VERIFIED_THEOREM", "P145": "VERIFIED_THEOREM", "P146": "CONDITIONAL",
        "E35": "VERIFIED_FINITE", "NG32": "REFUTED", "H141": "OPEN",
    }
    if value.get("format") != "collatz-phase23-theory-v1" or value.get("claims") != expected_claims:
        fail("theory claim boundary")
    if value.get("proves_collatz") is not False:
        fail("Collatz boundary")
    serialized = json.dumps(value, sort_keys=True)
    for required in ("pairwise-distinct", "Primitive positive integer", "residue profile", "P54", "no such polynomial minimum theorem"):
        if required not in serialized:
            fail(f"theory scope missing: {required}")


def verify_obstruction(path: Path, critical: dict[str, object], cycle: dict[str, object]) -> None:
    text = path.read_text(encoding="utf-8")
    for required in ("pairwise", "negative", "q0", "floating-point", "H89", "H133", "proves_collatz=false"):
        if required not in text:
            fail(f"obstruction boundary: {required}")
    for count in (critical["totals"]["critical_words"], critical["totals"]["area_rejected"], cycle["profile_count"]):
        if str(count) not in text:
            fail("obstruction finite count")


def verify(directory: Path) -> dict[str, object]:
    for name in FILES:
        if not (directory / name).is_file():
            fail(f"missing {name}")
    theory = load(directory / FILES[0])
    critical = load(directory / FILES[1])
    cycle = load(directory / FILES[2])
    regressions = load(directory / FILES[3])
    verify_theory(theory)
    rebuilt_critical = expected_critical()
    if critical != rebuilt_critical:
        fail("critical reconstruction mismatch")
    rebuilt_cycle = expected_cycle()
    if cycle != rebuilt_cycle:
        fail("cycle reconstruction mismatch")
    if regressions != expected_regressions():
        fail("regression reconstruction mismatch")
    verify_obstruction(directory / FILES[4], critical, cycle)
    return {
        "valid": True,
        "claims": theory["claims"],
        "critical_words": critical["totals"]["critical_words"],
        "cycle_profiles": cycle["profile_count"],
        "generator_imported": False,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (OSError, ValueError) as exc:
        print(f"phase23 verification failed: {exc}", file=sys.stderr)
        return 1
    if args.write_report:
        save(args.write_report, result)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
