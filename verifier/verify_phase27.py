#!/usr/bin/env python3
"""Independent verifier for Phase 27 asymptotic cycle-area artifacts.

No Phase 27 production module is imported.  Compositions, rotations, profile
transport, rational traces, logarithm enclosures, envelopes, and synthetic
profiles are reconstructed here from their definitions.
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
V = 300_000
VX = 2075 * 2**60
K = 1_564_920_000
FILES = (
    "phase27_theory.json",
    "phase27_cycle_corpus.json",
    "phase27_envelopes.json",
    "phase27_synthetic_profiles.json",
    "phase27_regressions.json",
    "phase27_obstruction_report.md",
)
CLAIMS = {
    "EXT17": "EXTERNAL_THEOREM",
    "P162": "VERIFIED_THEOREM",
    "P163": "VERIFIED_THEOREM",
    "P164": "VERIFIED_THEOREM",
    "P165": "VERIFIED_THEOREM",
    "E39": "VERIFIED_FINITE",
    "NG36": "REFUTED",
    "H133": "OPEN",
}


def fail(message: str) -> None:
    raise SystemExit(f"phase27 verifier: {message}")


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


def stable_hash(rows: object) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fraction_pair(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def read_fraction(value: object) -> Fraction:
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
    return tuple(values[index:] + values[:index] for index in range(len(values)))


def necklace(values: Sequence[int]) -> tuple[int, ...]:
    return min(turns(values))


def is_primitive(values: Sequence[int]) -> bool:
    values = tuple(values)
    for period in range(1, len(values)):
        if len(values) % period == 0 and values == values[:period] * (len(values) // period):
            return False
    return True


def walk(values: Sequence[int]) -> tuple[int, ...]:
    q, L = len(values), sum(values)
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    answer = [0]
    for exponent in values:
        answer.append(answer[-1] + q0 * exponent - L0)
    if answer[-1]:
        fail("walk does not close")
    return tuple(answer)


def minimum_turns(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    # Scan offsets backwards; the production generator scans rotated tuples.
    answer = []
    values = tuple(values)
    for index in range(len(values) - 1, -1, -1):
        rotated = values[index:] + values[:index]
        if min(walk(rotated)) == 0:
            answer.append(rotated)
    return tuple(sorted(set(answer)))


def reconstruct(values: Sequence[int]) -> dict[str, object]:
    values = tuple(values)
    q, L = len(values), sum(values)
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    heights = walk(values)
    residues = tuple((-L0 * index) % q0 for index in range(q + 1))
    profile = []
    for height, residue in zip(heights, residues, strict=True):
        difference = height - residue
        if difference % q0:
            fail("profile divisibility")
        profile.append(difference // q0)
    if min(profile) < 0 or profile[0] or profile[-1]:
        fail("profile normalization")
    boundaries = tuple((L0 * index + residues[index]) // q0 for index in range(q + 1))
    base = tuple(boundaries[index + 1] - boundaries[index] for index in range(q))
    actual = [0]
    for exponent in values:
        actual.append(actual[-1] + exponent)
    if any(actual[index] != boundaries[index] + profile[index] for index in range(q + 1)):
        fail("profile boundary identity")
    if set(base) - {1, 2} or base != base[:q0] * common:
        fail("mechanical baseline")
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    support = sum(value > 0 for value in profile[:-1])
    if 2 * area < height * (height + 1) or height > support:
        fail("area/support height")
    return {
        "d": common,
        "base": base,
        "profile": tuple(profile),
        "area": area,
        "height": height,
        "support": support,
    }


def word(values: Sequence[int]) -> tuple[int, ...]:
    answer = []
    for exponent in values:
        answer.append(1)
        answer.extend([0] * (exponent - 1))
    return tuple(answer)


def hamming(left: Sequence[int], right: Sequence[int]) -> int:
    if len(left) != len(right):
        fail("Hamming length")
    return sum(a != b for a, b in zip(left, right, strict=True))


def cyclic_factor_count(bits: Sequence[int], width: int) -> int:
    # Encode each cyclic window as an integer, unlike the generator's strings.
    length = len(bits)
    encoded = set()
    for start in range(length):
        value = 0
        for offset in range(width):
            value = 2 * value + bits[(start + offset) % length]
        encoded.add(value)
    return len(encoded)


def correction(values: Sequence[int]) -> int:
    answer, prefix = 0, 0
    q = len(values)
    for index, exponent in enumerate(values):
        answer += 3 ** (q - 1 - index) * 2**prefix
        prefix += exponent
    return answer


def rational_trace(values: Sequence[int]) -> tuple[Fraction, ...]:
    q, L = len(values), sum(values)
    denominator = 2**L - 3**q
    if denominator <= 0:
        fail("rational trace denominator")
    current = Fraction(correction(values), denominator)
    answer = [current]
    for exponent in values:
        current = (3 * current + 1) / 2**exponent
        answer.append(current)
    if answer[-1] != answer[0] or min(answer) <= 0:
        fail("rational trace closure")
    return tuple(answer)


def critical_length(q: int) -> int:
    power = 3**q
    exponent = power.bit_length()
    if 2 ** (exponent - 1) == power:
        fail("impossible power equality")
    return exponent


def branch(q: int, L: int) -> str:
    return "critical" if L == critical_length(q) else "noncritical"


def master_shadow(q: int, L: int, area: int, height: int) -> tuple[bool, Fraction]:
    multiplier = Fraction(3**q, 2**L)
    gap = multiplier * (1 - multiplier)
    left = Fraction(2**L) * (3 * gap) ** (area + 1)
    right = Fraction((2 ** (height + 4) * q) ** (area + 1))
    return left < right, right - left


def verify_corpus(stored: dict[str, object]) -> dict[str, int]:
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "critical_classes": 0,
        "noncritical_classes": 0,
        "noncoprime_classes": 0,
        "support_hamming_checks": 0,
        "support_factor_checks": 0,
        "support_height_checks": 0,
        "shadow_master_checks": 0,
        "shadow_master_passes": 0,
        "rotation_mismatches": 0,
    }
    rows = []
    mismatch_rows = []
    for q in range(1, Q_MAX + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            classes = sorted({necklace(row) for row in recursive_compositions(L, q)})
            for values in classes:
                counts["cyclic_classes"] += 1
                primitive = is_primitive(values)
                counts["primitive_classes"] += int(primitive)
                kind = branch(q, L)
                counts[f"{kind}_classes"] += 1
                invariants = set()
                representative = None
                for rotated in minimum_turns(values):
                    data = reconstruct(rotated)
                    base_bits, actual_bits = word(data["base"]), word(rotated)
                    distance = hamming(base_bits, actual_bits)
                    support = data["support"]
                    if distance > 2 * support:
                        fail("support Hamming bound")
                    counts["support_hamming_checks"] += 1
                    counts["support_height_checks"] += 1
                    maximum = Fraction(0)
                    for width in range(1, L + 1):
                        base_count = cyclic_factor_count(base_bits, width)
                        actual_count = cyclic_factor_count(actual_bits, width)
                        bound = (2 * support + 1) * width + 1
                        if base_count > width + 1 or actual_count > base_count + width * distance or actual_count > bound:
                            fail("support factor bound")
                        maximum = max(maximum, Fraction(actual_count, bound))
                        counts["support_factor_checks"] += 1
                    invariants.add((data["area"], data["height"], support, distance))
                    representative = (data, support, distance, maximum)
                if representative is None or len(invariants) != 1:
                    fail("minimum-turn support invariance")
                data, support, distance, maximum = representative
                counts["noncoprime_classes"] += int(data["d"] > 1)
                passed, margin = master_shadow(q, L, data["area"], data["height"])
                counts["shadow_master_checks"] += 1
                counts["shadow_master_passes"] += int(passed)
                trace = rational_trace(values)[:-1]
                least = min(trace)
                least_offsets = tuple(index for index, value in enumerate(trace) if value == least)
                minimum_set = set(minimum_turns(values))
                discrepancy_offsets = tuple(index for index, row in enumerate(turns(values)) if row in minimum_set)
                mismatch = set(least_offsets).isdisjoint(discrepancy_offsets)
                counts["rotation_mismatches"] += int(mismatch)
                rows.append([
                    q, L, list(values), primitive, kind, data["d"], data["area"], data["height"],
                    support, distance, fraction_pair(maximum), passed, fraction_pair(margin),
                    list(least_offsets), list(discrepancy_offsets), mismatch,
                ])
                if mismatch:
                    mismatch_rows.append([
                        q, L, list(values), [fraction_pair(value) for value in trace],
                        list(least_offsets), list(discrepancy_offsets),
                    ])
    if stored.get("format") != "collatz-phase27-cycle-corpus-v1" or stored.get("maximum_q") != Q_MAX:
        fail("corpus metadata")
    if stored.get("counts") != counts:
        fail("corpus counts")
    if stored.get("row_digest_sha256") != stable_hash(rows):
        fail("corpus row digest")
    if stored.get("mismatch_digest_sha256") != stable_hash(mismatch_rows):
        fail("corpus mismatch digest")
    expected = {
        "q": 2, "L": 4, "exponents": [1, 3],
        "odd_rational_orbit": [["5", "7"], ["11", "7"]],
        "least_value_offsets": [0], "discrepancy_minimum_offsets": [1],
        "positive_integral": False,
    }
    if stored.get("smallest_rotation_mismatch") != expected or stored.get("proves_collatz") is not False:
        fail("rotation mismatch")
    return counts


def raw_log_interval(value: Fraction, terms: int = 84) -> tuple[Fraction, Fraction]:
    if value < 1:
        fail("raw log domain")
    z = (value - 1) / (value + 1)
    total = Fraction(0)
    power = z
    for index in range(terms):
        total += 2 * power / (2 * index + 1)
        power *= z * z
    remainder = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return total, total + remainder


def log_box(value: Fraction) -> tuple[Fraction, Fraction]:
    if value <= 0:
        fail("log domain")
    exponent = 0
    reduced = value
    while reduced >= 2:
        reduced /= 2
        exponent += 1
    while reduced < 1:
        reduced *= 2
        exponent -= 1
    low, high = raw_log_interval(reduced)
    low_two, high_two = raw_log_interval(Fraction(2))
    if exponent >= 0:
        return low + exponent * low_two, high + exponent * high_two
    return low + exponent * high_two, high + exponent * low_two


def height_bound(area: int) -> int:
    return (math.isqrt(8 * area + 1) - 1) // 2


def noncritical_box(q: int, area: int, minimum: int) -> tuple[Fraction, Fraction]:
    _, ln2_high = log_box(Fraction(2))
    ln3_low, _ = log_box(Fraction(3))
    _, log_source = log_box(Fraction(2 * q, 3))
    _, log_pack = log_box(Fraction(minimum + 3 * q, minimum))
    right = (area + 1) * (
        (height_bound(area) + 4) * ln2_high + log_source + Fraction(1, minimum) + log_pack / 9
    )
    return q * ln3_low, right


def critical_box(q: int, area: int) -> tuple[Fraction, Fraction]:
    _, ln2_high = log_box(Fraction(2))
    ln3_low, _ = log_box(Fraction(3))
    _, ln12_high = log_box(Fraction(12))
    _, lnq_high = log_box(Fraction(q))
    _, ln43_high = log_box(Fraction(4, 3))
    right = (area + 1) * (
        (height_bound(area) + 4) * ln2_high + ln43_high + K * ln12_high + (K + 1) * lnq_high
    )
    return q * ln3_low, right


def independent_frontier(q: int, kind: str, minimum: int) -> int:
    compare = critical_box if kind == "critical" else lambda q0, area: noncritical_box(q0, area, minimum)
    high = 1
    while compare(q, high)[0] > compare(q, high)[1]:
        high <<= 1
    low = 0
    while low < high:
        middle = (low + high) // 2
        if compare(q, middle)[0] > compare(q, middle)[1]:
            low = middle + 1
        else:
            high = middle
    return low


def verify_envelope_rows(rows: object, kind: str, minimum: int) -> None:
    if not isinstance(rows, list):
        fail("envelope rows")
    for row in rows:
        if not isinstance(row, dict) or row.get("branch") != kind:
            fail("envelope row metadata")
        q = int(row["q"])
        frontier = independent_frontier(q, kind, minimum)
        if int(row["least_unexcluded_area"]) != frontier or int(row["excluded_through"]) != frontier - 1:
            fail("envelope frontier")
        if row.get("previous_positive_margin") is not True or row.get("current_positive_margin") is not False:
            fail("envelope signs")
        if read_fraction(row["previous_margin"]) <= 0 or read_fraction(row["current_margin"]) >= 0:
            fail("stored envelope rational signs")
        if read_fraction(row["cube_ratio"]) != Fraction(frontier**3, q**2):
            fail("envelope cube ratio")


def verify_envelopes(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase27-effective-envelopes-v1" or stored.get("proves_collatz") is not False:
        fail("envelope metadata")
    spec = stored.get("matveev_specialization")
    if not isinstance(spec, dict) or spec.get("integer_majorant_K") != K:
        fail("Matveev specialization")
    if 5 * K != 7 * 30**5 * 23 * 2 or not 2**9 < 23**2:
        fail("Matveev integer majorant")
    if spec.get("exact_majorant_verified") is not True or spec.get("gap") != "lambda*(1-lambda) > q^(-K)/(4*12^K)":
        fail("Matveev gap metadata")
    verify_envelope_rows(stored.get("noncritical_rows"), "noncritical", V)
    verify_envelope_rows(stored.get("critical_rows"), "critical", V)
    x02 = stored.get("x02_control")
    if not isinstance(x02, dict):
        fail("X02 envelope")
    verify_envelope_rows([x02], "noncritical", VX)
    noncritical_first = stored["noncritical_rows"][0]
    if int(noncritical_first["excluded_through"]) < 100_000 or int(x02["excluded_through"]) < 5 * 10**15:
        fail("Phase 26 envelope regression")
    constants = stored.get("asymptotic_constants")
    if not isinstance(constants, dict):
        fail("asymptotic constants")
    area_box = constants.get("area_constant_cube_interval")
    support_box = constants.get("support_constant_square_interval")
    if not isinstance(area_box, list) or not isinstance(support_box, list):
        fail("constant intervals")
    area_low, area_high = read_fraction(area_box[0]), read_fraction(area_box[1])
    support_low, support_high = read_fraction(support_box[0]), read_fraction(support_box[1])
    if not 0 < area_low < area_high or not 0 < support_low < support_high:
        fail("constant interval order")
    return {
        "critical_rows": len(stored["critical_rows"]),
        "noncritical_rows": len(stored["noncritical_rows"]),
        "matveev_K": K,
    }


def baseline(q: int, L: int) -> tuple[int, ...]:
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    residues = tuple((-L0 * index) % q0 for index in range(q + 1))
    positions = tuple((L0 * index + residues[index]) // q0 for index in range(q + 1))
    return tuple(positions[index + 1] - positions[index] for index in range(q))


def floor_cuberoot(value: int) -> int:
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


def ceil_cuberoot(value: int) -> int:
    root = floor_cuberoot(value)
    return root if root**3 == value else root + 1


def tall(q: int, L: int, height: int) -> tuple[int, ...]:
    base = baseline(q, L)
    profile = [0, height]
    for index in range(1, q):
        profile.append(profile[-1] - 1 if profile[-1] and base[index] == 2 else profile[-1])
    if profile[-1]:
        fail("tall profile closure")
    return tuple(profile)


def diffuse(q: int, L: int, height: int, target: int) -> tuple[int, ...]:
    base = baseline(q, L)
    profile = [0]
    completed = 0
    cooldown = False
    for index in range(q):
        current = profile[-1]
        enough = sum(value == 2 for value in base[index + 1 :]) >= height
        if current == 0 and completed < target and not cooldown and enough:
            next_value = height
            cooldown = True
        elif current and base[index] == 2:
            next_value = current - 1
            if next_value == 0:
                completed = sum(profile)
        else:
            next_value = current
            if current == 0:
                cooldown = False
        profile.append(next_value)
    if profile[-1]:
        fail("diffuse profile closure")
    return tuple(profile)


def sample(kind: str, q: int, profile: Sequence[int]) -> dict[str, object]:
    L = critical_length(q)
    base = baseline(q, L)
    exponents = tuple(base[index] + profile[index + 1] - profile[index] for index in range(q))
    if min(exponents) < 1:
        fail("synthetic exponent recurrence")
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    support = sum(value > 0 for value in profile[:-1])
    distance = hamming(word(base), word(exponents))
    if distance > 2 * support or height > support:
        fail("synthetic support")
    return {
        "kind": kind, "q": q, "L": L, "area": area, "height": height,
        "support": support, "hamming": distance,
        "area_cube_over_q_squared": fraction_pair(Fraction(area**3, q**2)),
        "height_cube_over_q": fraction_pair(Fraction(height**3, q)),
        "valid_positive_exponents": True,
        "profile_digest_sha256": stable_hash(list(profile)),
        "exponent_digest_sha256": stable_hash(list(exponents)),
    }


def verify_synthetic(stored: dict[str, object]) -> int:
    rows = []
    for q in (125, 343, 729, 1331):
        L = critical_length(q)
        rows.append(sample("tall", q, tall(q, L, max(2, floor_cuberoot(q)))))
        rows.append(sample("diffuse", q, diffuse(q, L, max(2, q.bit_length() - 1), ceil_cuberoot(q**2))))
    if stored.get("format") != "collatz-phase27-synthetic-profiles-v1":
        fail("synthetic metadata")
    if stored.get("rows") != rows or stored.get("row_digest_sha256") != stable_hash(rows):
        fail("synthetic rows")
    expected_grid = {"q": 63322, "L": 100363, "roots": [9046, 18092, 27138], "q_arc_width": 54181, "L_arc_width": 85875, "direct_modular_gcd": 1}
    if stored.get("near_grid_control") != expected_grid or stored.get("proves_collatz") is not False:
        fail("synthetic near-grid control")
    return len(rows)


def bit_exponents(bits: str) -> tuple[int, ...]:
    starts = [index for index, bit in enumerate(bits) if bit == "1"]
    return tuple((starts[(index + 1) % len(starts)] - starts[index]) % len(bits) or len(bits) for index in range(len(starts)))


def verify_regressions(stored: dict[str, object]) -> int:
    families = [
        ("A=11101", "11101"), ("B=1100", "1100"),
        ("(110|111)^*", "110111" * 8), ("A^1B^1", "11101" + "1100"),
        ("A^2B^3", "11101" * 2 + "1100" * 3),
        ("2^m-1", "1" * 12 + "0"), ("8^m-5", "111001" * 4),
    ]
    rows = []
    for name, bits in families:
        exponents = bit_exponents(bits)
        rows.append([name, bits, list(exponents), len(exponents), sum(exponents), str(2 ** sum(exponents) - 3 ** len(exponents))])
    if stored.get("format") != "collatz-phase27-regressions-v1" or stored.get("mandatory_adversarial_families") != rows:
        fail("adversarial families")
    obstruction = stored.get("rotation_alignment_obstruction")
    expected_obstruction = {
        "q": 2,
        "L": 4,
        "exponents": [1, 3],
        "least_value_offsets": [0],
        "discrepancy_minimum_offsets": [1],
        "odd_rational_orbit": [["5", "7"], ["11", "7"]],
        "positive_integral": False,
    }
    if obstruction != expected_obstruction:
        fail("alignment obstruction regression")
    scalar = stored.get("phase26_scalar_obstruction")
    if scalar != {"left": str(75**7), "right": str(3 * 64**7), "left_exceeds_right": True}:
        fail("Phase 26 scalar obstruction")
    if stored.get("proves_collatz") is not False:
        fail("regression overclaim")
    return len(rows)


def verify_theory(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase27-asymptotic-theory-v1" or stored.get("proves_collatz") is not False:
        fail("theory metadata")
    claims = stored.get("claims")
    if not isinstance(claims, dict):
        fail("theory claims")
    status_map = {key: value.get("status") for key, value in claims.items() if isinstance(value, dict)}
    if status_map != CLAIMS:
        fail("theory claim statuses")
    dependencies = stored.get("dependencies")
    if not isinstance(dependencies, dict) or "EXT17" not in dependencies.get("P164", []):
        fail("external dependency discipline")
    boundary = stored.get("what_this_result_does_not_prove")
    if not isinstance(boundary, str) or "Collatz is not proved" not in boundary:
        fail("theory no-overclaim boundary")


def verify_report(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = ("5/7 -> 11/7 -> 5/7", f"K={K}", "positive integer cycle remains open", "proves_collatz=false")
    if any(item not in text for item in required):
        fail("obstruction report")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()

    theory = load(arguments.artifact_dir / "phase27_theory.json")
    corpus = load(arguments.artifact_dir / "phase27_cycle_corpus.json")
    envelopes = load(arguments.artifact_dir / "phase27_envelopes.json")
    synthetic = load(arguments.artifact_dir / "phase27_synthetic_profiles.json")
    regressions = load(arguments.artifact_dir / "phase27_regressions.json")

    verify_theory(theory)
    counts = verify_corpus(corpus)
    envelope_counts = verify_envelopes(envelopes)
    synthetic_count = verify_synthetic(synthetic)
    family_count = verify_regressions(regressions)
    verify_report(arguments.artifact_dir / "phase27_obstruction_report.md")

    result = {
        "format": "collatz-phase27-independent-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "independence": "recursive reverse compositions, integer-encoded factors, direct rational traces, 84-term logarithm boxes, and independent profile synthesis",
        "claims": CLAIMS,
        "corpus_counts": counts,
        "envelope_counts": envelope_counts,
        "synthetic_profile_count": synthetic_count,
        "mandatory_family_count": family_count,
        "verified_input_sha256": {
            name: file_hash(arguments.artifact_dir / name) for name in FILES
        },
        "proves_collatz": False,
        "what_this_result_does_not_prove": "This does not exclude arbitrary-area cycles, either structural branch, nonperiodic counterexamples, or Collatz.",
    }
    if arguments.output:
        save(arguments.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
