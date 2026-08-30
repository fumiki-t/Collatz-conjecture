#!/usr/bin/env python3
"""Independent verifier for Phase 28 transport-dispersion artifacts.

No Phase 28 production module is imported.  The verifier uses recursive
composition enumeration, direct boundary subtraction, integer factor encodings,
transition-count level components, and an independent logarithm enclosure.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 8
FILES = (
    "phase28_theory.json",
    "phase28_transport_corpus.json",
    "phase28_scalar_certificates.json",
    "phase28_synthetic_profiles.json",
    "phase28_regressions.json",
    "phase28_obstruction_report.md",
)
CLAIMS = {
    "P166": "VERIFIED_THEOREM",
    "P167": "VERIFIED_THEOREM",
    "P168": "VERIFIED_THEOREM",
    "P169": "VERIFIED_THEOREM",
    "P170": "VERIFIED_THEOREM",
    "P171": "VERIFIED_THEOREM",
    "E40": "VERIFIED_FINITE",
    "NG37": "REFUTED",
    "NG38": "REFUTED",
    "H172": "OPEN",
    "H133": "OPEN",
}
A_BITS = "11101"
B_BITS = "1100"
NEGATIVE_Q7 = (1, 1, 1, 2, 1, 1, 4)


def fail(message: str) -> None:
    raise SystemExit(f"phase28 verifier: {message}")


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} is not an object")
    return value


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def read_pair(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(item, str) for item in value):
        fail("malformed rational pair")
    return Fraction(int(value[0]), int(value[1]))


def recursive_compositions(total: int, slots: int, suffix: tuple[int, ...] = ()) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield (total,) + suffix
        return
    for last in range(total - slots + 1, 0, -1):
        yield from recursive_compositions(total - last, slots - 1, (last,) + suffix)


def turns(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    values = tuple(values)
    return tuple(values[offset:] + values[:offset] for offset in range(len(values)))


def necklace(values: Sequence[int]) -> tuple[int, ...]:
    return min(turns(values))


def is_primitive(values: Sequence[int]) -> bool:
    values = tuple(values)
    for period in range(1, len(values)):
        if len(values) % period == 0 and values == values[:period] * (len(values) // period):
            return False
    return True


def reduced_walk(values: Sequence[int]) -> tuple[int, ...]:
    q, L = len(values), sum(values)
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    answer = [0]
    for exponent in values:
        answer.append(answer[-1] + q0 * exponent - L0)
    if answer[-1]:
        fail("walk closure")
    return tuple(answer)


def minimum_turns(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    answer = []
    values = tuple(values)
    for offset in range(len(values) - 1, -1, -1):
        rotated = values[offset:] + values[:offset]
        if min(reduced_walk(rotated)) == 0:
            answer.append(rotated)
    return tuple(sorted(set(answer)))


def ceil_ratio(numerator: int, denominator: int) -> int:
    quotient, remainder = divmod(numerator, denominator)
    return quotient + bool(remainder)


def reconstruct(values: Sequence[int], density: bool = True) -> dict[str, object]:
    values = tuple(values)
    q, L = len(values), sum(values)
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    boundaries = tuple(ceil_ratio(L0 * index, q0) for index in range(q + 1))
    base = tuple(boundaries[index + 1] - boundaries[index] for index in range(q))
    actual = [0]
    for exponent in values:
        actual.append(actual[-1] + exponent)
    profile = tuple(actual[index] - boundaries[index] for index in range(q + 1))
    if min(profile) < 0 or profile[0] or profile[-1] or set(base) - {1, 2}:
        fail("profile reconstruction")
    if tuple(base[index] + profile[index + 1] - profile[index] for index in range(q)) != values:
        fail("profile exponent identity")

    p = L0 - q0
    if not 0 < p <= q0:
        fail("slope numerator")
    b = tuple(exponent - 1 for exponent in base)
    density_checks = 0
    if density:
        repeated = b + b
        for start in range(q - 1, -1, -1):
            running = 0
            for width in range(1, q + 1):
                running += repeated[start + width - 1]
                if running > ceil_ratio(p * width, q0):
                    fail("density interval")
                density_checks += 1

    changes = tuple(profile[index + 1] - profile[index] for index in range(q))
    if any(change < -b[index] or change < -1 for index, change in enumerate(changes)):
        fail("descent legality")
    positive = sum(change for change in changes if change > 0)
    negative = -sum(change for change in changes if change < 0)
    if positive != negative or negative != sum(change == -1 for change in changes):
        fail("variation balance")
    if tuple(b[index] + changes[index] for index in range(q)) != tuple(value - 1 for value in values):
        fail("token script")

    height = max(profile[:-1], default=0)
    area = sum(profile[:-1])
    components = []
    endpoints = []
    for level in range(1, height + 1):
        starts = []
        ends = []
        for index in range(q):
            active = profile[index] >= level
            previous = index > 0 and profile[index - 1] >= level
            following = index + 1 < q and profile[index + 1] >= level
            if active and not previous:
                starts.append(index)
            if active and not following:
                ends.append(index + 1)
        if len(starts) != len(ends):
            fail("level endpoints")
        components.append(len(starts))
        endpoints.append(tuple(zip(starts, ends, strict=True)))
    if sum(components) != positive:
        fail("component variation")
    if sum(end - start for rows in endpoints for start, end in rows) != area:
        fail("layer cake")
    floor_sum = sum((level * q0) // p for level in range(height))
    if area - positive < floor_sum:
        fail("descent floor")

    direct = [0] * q
    direct[0] = 1
    for index, profile_height in enumerate(profile[:-1]):
        coefficient = 2**profile_height - 1
        direct[index] -= coefficient
        direct[(index + 1) % q] += (2 if index + 1 == q else 1) * coefficient
    layered = [0] * q
    layered[0] = 1
    weighted = 0
    for level, rows in enumerate(endpoints, start=1):
        weight = 2 ** (level - 1)
        weighted += weight * len(rows)
        for start, end in rows:
            layered[start] -= weight
            layered[end % q] += (2 if end == q else 1) * weight
    if direct != layered:
        fail("level polynomial")
    support = sum(value != 0 for value in direct)
    l1 = sum(abs(value) for value in direct)
    endpoint_weight = 2 ** profile[-2] - 1
    if support > 2 * positive + 1 or l1 > 1 + 2 * weighted + endpoint_weight:
        fail("polynomial bounds")
    return {
        "d": common,
        "q0": q0,
        "L0": L0,
        "base": base,
        "profile": profile,
        "area": area,
        "height": height,
        "J": positive,
        "descent_floor": floor_sum,
        "descent_slack": area - positive - floor_sum,
        "components": tuple(components),
        "polynomial": tuple(direct),
        "support": support,
        "l1": l1,
        "weighted": weighted,
        "endpoint_weight": endpoint_weight,
        "density_checks": density_checks,
    }


def bits(values: Sequence[int]) -> tuple[int, ...]:
    answer = []
    for exponent in values:
        answer.append(1)
        answer.extend([0] * (exponent - 1))
    return tuple(answer)


def factor_count(values: Sequence[int], width: int) -> int:
    encoded = set()
    length = len(values)
    for start in range(length):
        number = 0
        for offset in range(width):
            number = (number << 1) | values[(start + offset) % length]
        encoded.add(number)
    return len(encoded)


def verify_corpus(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase28-transport-corpus-v1" or stored.get("maximum_q") != Q_MAX:
        fail("corpus metadata")
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "transport_checks": 0,
        "density_interval_checks": 0,
        "factor_width_checks": 0,
        "polynomial_checks": 0,
    }
    rows = []
    max_ratio = Fraction(0)
    max_sample = None
    for q in range(1, Q_MAX + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            necklaces = sorted({necklace(row) for row in recursive_compositions(L, q)})
            for values in necklaces:
                counts["cyclic_classes"] += 1
                primitive = is_primitive(values)
                counts["primitive_classes"] += int(primitive)
                invariants = set()
                representative = None
                for rotated in minimum_turns(values):
                    item = reconstruct(rotated)
                    counts["minimum_rotations"] += 1
                    counts["transport_checks"] += 1
                    counts["density_interval_checks"] += item["density_checks"]
                    counts["polynomial_checks"] += 1
                    base_bits = bits(item["base"])
                    actual_bits = bits(rotated)
                    ratio = Fraction(0)
                    for width in range(1, L + 1):
                        base_total = factor_count(base_bits, width)
                        actual_total = factor_count(actual_bits, width)
                        bound = (2 * item["J"] + 1) * width + 1
                        if base_total > width + 1 or actual_total > bound:
                            fail("corpus factor bound")
                        counts["factor_width_checks"] += 1
                        ratio = max(ratio, Fraction(actual_total, bound))
                    invariants.add((item["area"], item["height"], item["J"], item["descent_floor"]))
                    representative = (rotated, item, ratio)
                if representative is None or len(invariants) != 1:
                    fail("rotation invariants")
                rotated, item, factor_ratio = representative
                counts["noncoprime_classes"] += int(item["d"] > 1)
                area_ratio = Fraction(item["area"], item["J"]) if item["J"] else Fraction(0)
                if area_ratio > max_ratio:
                    max_ratio = area_ratio
                    max_sample = [list(rotated), item["area"], item["height"], item["J"]]
                rows.append([
                    q, L, list(values), primitive, item["d"], item["area"], item["height"],
                    item["J"], item["descent_floor"], item["descent_slack"], item["support"],
                    item["l1"], pair(factor_ratio),
                ])
    if stored.get("counts") != counts or stored.get("row_digest_sha256") != digest(rows):
        fail("corpus reconstruction")
    if stored.get("maximum_area_over_transport") != pair(max_ratio) or stored.get("maximum_area_over_transport_sample") != max_sample:
        fail("plateau sample")
    if stored.get("proves_collatz") is not False:
        fail("corpus overclaim")
    return counts


def atanh_box(value: Fraction, terms: int = 88) -> tuple[Fraction, Fraction]:
    z = (value - 1) / (value + 1)
    total = Fraction(0)
    power = z
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= z * z
    remainder = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return 2 * total, 2 * total + remainder


def log_box(value: Fraction) -> tuple[Fraction, Fraction]:
    scale = 0
    reduced = value
    while reduced >= 2:
        reduced /= 2
        scale += 1
    while reduced < 1:
        reduced *= 2
        scale -= 1
    low2, high2 = atanh_box(Fraction(2))
    low, high = atanh_box(reduced)
    if scale >= 0:
        return low + scale * low2, high + scale * high2
    return low + scale * high2, high + scale * low2


def transport_cube(slope: Fraction) -> Fraction:
    return Fraction(27, 32) * slope * slope / (slope - 1)


def floor_cube(value: int) -> int:
    low, high = 0, 1
    while high**3 <= value:
        high *= 2
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**3 <= value:
            low = middle
        else:
            high = middle
    return low


def decimal_box(lower: Fraction, upper: Fraction, digits: int = 6) -> list[list[str]]:
    scale = 10**digits
    low = floor_cube(lower.numerator * scale**3 // lower.denominator)
    while Fraction((low + 1) ** 3, scale**3) <= lower:
        low += 1
    high = floor_cube(upper.numerator * scale**3 // upper.denominator)
    if Fraction(high**3, scale**3) < upper:
        high += 1
    return [pair(Fraction(low, scale)), pair(Fraction(high, scale))]


def verify_scalar(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase28-scalar-certificates-v1" or stored.get("proves_collatz") is not False:
        fail("scalar metadata")
    alpha_rows = stored.get("log2_three_interval")
    if not isinstance(alpha_rows, list) or len(alpha_rows) != 2:
        fail("alpha interval")
    alpha_low, alpha_high = map(read_pair, alpha_rows)
    ln2_low, ln2_high = log_box(Fraction(2))
    ln3_low, ln3_high = log_box(Fraction(3))
    independent_low, independent_high = ln3_low / ln2_high, ln3_high / ln2_low
    if not alpha_low <= independent_low <= independent_high <= alpha_high:
        fail("independent log enclosure")
    critical = [read_pair(value) for value in stored.get("critical_constant_cube_interval", [])]
    old = [read_pair(value) for value in stored.get("phase27_constant_cube_interval", [])]
    if critical != [transport_cube(alpha_high), transport_cube(alpha_low)]:
        fail("critical constant")
    if old != [alpha_low * alpha_low / 2, alpha_high * alpha_high / 2]:
        fail("Phase 27 comparison")
    if stored.get("critical_constant_decimal_box") != decimal_box(critical[0], critical[1]):
        fail("critical decimal box")
    if stored.get("noncritical_constant") != ["3", "2"] or stored.get("noncritical_constant_cube") != ["27", "8"]:
        fail("noncritical constant")
    slopes = []
    for slope in (Fraction(8, 5), Fraction(5, 3), Fraction(7, 4), Fraction(19, 10), Fraction(2)):
        cube = transport_cube(slope)
        slopes.append({"slope": pair(slope), "constant_cube": pair(cube), "at_least_three_halves": cube >= Fraction(27, 8)})
    if stored.get("slope_rows") != slopes:
        fail("slope rows")
    critical_rows = []
    for q in (10, 100, 1_000, 10_000):
        L = (3**q).bit_length()
        slope = Fraction(L, q)
        critical_rows.append({"q": q, "L": L, "slope": pair(slope), "constant_cube": pair(transport_cube(slope))})
    if stored.get("critical_rows") != critical_rows:
        fail("critical rows")
    return {"critical_rows": len(critical_rows), "slope_rows": len(slopes)}


def profile_exponents(base: Sequence[int], profile: Sequence[int]) -> tuple[int, ...]:
    answer = tuple(base[index] + profile[index + 1] - profile[index] for index in range(len(base)))
    if min(answer) < 1:
        fail("synthetic exponents")
    return answer


def base_word(q: int, L: int) -> tuple[int, ...]:
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    boundaries = [(L0 * index + q0 - 1) // q0 for index in range(q + 1)]
    return tuple(boundaries[index + 1] - boundaries[index] for index in range(q))


def synthetic_profiles() -> list[tuple[str, int, int, tuple[int, ...]]]:
    rows = []
    q = 125
    L = (3**q).bit_length()
    base = base_word(q, L)
    # Tall: descend at every permitted two after one initial jump.
    profile = [0, 5]
    for index in range(1, q):
        profile.append(profile[-1] - 1 if profile[-1] and base[index] == 2 else profile[-1])
    rows.append(("one-tall-excursion", q, L, tuple(profile)))
    # Plateau: mark the final five permitted descent edges by a reverse scan.
    selected = []
    for index in range(q - 1, 0, -1):
        if base[index] == 2 and len(selected) < 5:
            selected.append(index)
    profile = [0]
    for index in range(q):
        if index == 0:
            profile.append(5)
        elif index in selected and profile[-1]:
            profile.append(profile[-1] - 1)
        else:
            profile.append(profile[-1])
    rows.append(("long-constant-plateau", q, L, tuple(profile)))
    # Unit excursions: alternate an up edge with the next permitted descent.
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
    rows.append(("isolated-unit-excursions", q, L, tuple(profile)))
    # One height-nine excursion followed by 115 unit excursions.
    q = 1331
    L = (3**q).bit_length()
    base = base_word(q, L)
    profile = [0]
    remaining = 115
    started = False
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
    rows.append(("near-extremal-mixed", q, L, tuple(profile)))
    # Convert the q=77 seven-grid residue profile into time coordinates.
    q, L = 77, 123
    residue = [0] * q
    for root in (11, 22, 33):
        residue[root] = 1
    profile = tuple(residue[(-L * index) % q] for index in range(q)) + (0,)
    rows.append(("phase25-seven-grid", q, L, profile))
    return rows


def synthetic_sample(kind: str, q: int, L: int, profile: Sequence[int]) -> dict[str, object]:
    base = base_word(q, L)
    values = profile_exponents(base, profile)
    item = reconstruct(values, density=False)
    factor_rows = []
    base_bits, actual_bits = bits(base), bits(values)
    for width in sorted({1, 2, 3, 5, 8, 13, L}):
        if width <= L:
            total = factor_count(actual_bits, width)
            factor_rows.append([width, total, (2 * item["J"] + 1) * width + 1])
    return {
        "kind": kind, "q": q, "L": L, "area": item["area"], "height": item["height"],
        "J": item["J"], "descent_floor": item["descent_floor"], "descent_slack": item["descent_slack"],
        "level_components": list(item["components"]), "polynomial_support": item["support"],
        "polynomial_l1": item["l1"], "factor_rows": factor_rows,
        "profile_digest_sha256": digest(list(profile)), "exponent_digest_sha256": digest(list(values)),
        "valid_positive_exponents": min(values) >= 1,
    }


def verify_synthetic(stored: dict[str, object]) -> int:
    if stored.get("format") != "collatz-phase28-synthetic-profiles-v1" or stored.get("proves_collatz") is not False:
        fail("synthetic metadata")
    rows = [synthetic_sample(*entry) for entry in synthetic_profiles()]
    if stored.get("rows") != rows or stored.get("row_digest_sha256") != digest(rows):
        fail("synthetic reconstruction")
    return len(rows)


def exponents_from_bits(word: str) -> tuple[int, ...]:
    start = word.index("1")
    word = word[start:] + word[:start]
    positions = [index for index, value in enumerate(word) if value == "1"] + [len(word)]
    return tuple(positions[index + 1] - positions[index] for index in range(len(positions) - 1))


def verify_regressions(stored: dict[str, object]) -> int:
    families = []
    for name, word in (
        ("A=11101", A_BITS), ("B=1100", B_BITS), ("(110|111)^*", "110111" * 8),
        ("A^1B^1", A_BITS + B_BITS), ("A^2B^3", A_BITS * 2 + B_BITS * 3),
        ("2^m-1", "1" * 12 + "0"), ("8^m-5", "111001" * 4),
    ):
        values = exponents_from_bits(word)
        item = reconstruct(minimum_turns(values)[0])
        families.append([name, word, list(values), item["area"], item["height"], item["J"]])
    if stored.get("mandatory_families") != families:
        fail("mandatory families")
    strictness = stored.get("finite_strictness_obstruction")
    expected_strictness = {
        "q": 3, "L": 5, "exponents": [3, 1, 1], "delta": ["2", "3"], "area": 1,
        "J": 1, "height": 1, "new_bound": 1, "triangular_bound": 1,
        "interpretation": "Refutes universal finite strict improvement, not the asymptotic leading-coefficient improvement.",
    }
    endpoint = stored.get("endpoint_l1_obstruction")
    expected_endpoint = {
        "q": 2, "L": 4, "exponents": [3, 1], "profile": [0, 1, 0], "polynomial": [3, -1],
        "l1": 4, "proposed_bound": 3, "corrected_bound": 4,
        "interpretation": "X^q=2 makes an interval ending at q cost three endpoint units; the decomposition and support bound survive.",
    }
    if strictness != expected_strictness or endpoint != expected_endpoint:
        fail("obstruction regression")
    if stored.get("NG35_control") != {"left": str(75**7), "right": str(3 * 64**7), "left_exceeds_right": True}:
        fail("NG35 regression")
    if stored.get("proves_collatz") is not False:
        fail("regression overclaim")
    return len(families)


def verify_theory(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase28-transport-theory-v1" or stored.get("proves_collatz") is not False:
        fail("theory metadata")
    claims = stored.get("claims")
    if not isinstance(claims, dict):
        fail("theory claims")
    statuses = {key: row.get("status") for key, row in claims.items() if isinstance(row, dict)}
    if statuses != CLAIMS:
        fail("claim statuses")
    dependencies = stored.get("dependencies")
    if not isinstance(dependencies, dict) or "EXT17" not in dependencies.get("P169", []):
        fail("external dependency")
    if "endpoint correction" not in str(stored.get("polynomial_endpoint_boundary")):
        fail("NG38 repair boundary")
    if "Collatz proof" not in str(stored.get("what_this_result_does_not_prove")):
        fail("no-overclaim boundary")


def verify_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for required in ("NG37", "NG38", "Q_a=(3,-1)", "H172", "proves_collatz=false"):
        if required not in text:
            fail("obstruction report")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    theory = load(arguments.artifact_dir / "phase28_theory.json")
    corpus = load(arguments.artifact_dir / "phase28_transport_corpus.json")
    scalar = load(arguments.artifact_dir / "phase28_scalar_certificates.json")
    synthetic = load(arguments.artifact_dir / "phase28_synthetic_profiles.json")
    regressions = load(arguments.artifact_dir / "phase28_regressions.json")
    verify_theory(theory)
    counts = verify_corpus(corpus)
    scalar_counts = verify_scalar(scalar)
    synthetic_count = verify_synthetic(synthetic)
    family_count = verify_regressions(regressions)
    verify_report(arguments.artifact_dir / "phase28_obstruction_report.md")
    result = {
        "format": "collatz-phase28-independent-verifier-v1",
        "valid": True,
        "claims": CLAIMS,
        "corpus_counts": counts,
        "scalar_counts": scalar_counts,
        "synthetic_profile_count": synthetic_count,
        "mandatory_family_count": family_count,
        "generator_imported": False,
        "independence": "recursive reverse compositions, direct boundary subtraction, integer factor encodings, transition-count level sets, and an 88-term log box",
        "verified_input_sha256": {name: file_hash(arguments.artifact_dir / name) for name in FILES},
        "what_this_result_does_not_prove": "This does not prove H172, H133, any nonperiodic exclusion, or Collatz.",
        "proves_collatz": False,
    }
    if arguments.output:
        save(arguments.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
