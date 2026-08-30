#!/usr/bin/env python3
"""Independent verifier for Phase 26 reduced-slope cycle-area artifacts.

This file deliberately does not import the production generator.  It rebuilds
the bounded necklace corpus, edit/factor data, rational shadows, scalar scans,
and logarithmic certificates from the underlying definitions.
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


V = 300_000
VX = 2075 * 2**60
Q_MAX = 8
FILES = (
    "phase26_theory.json",
    "phase26_reduced_profiles.json",
    "phase26_scalar_certificates.json",
    "phase26_regressions.json",
    "phase26_obstruction_report.md",
)


def fail(message: str) -> None:
    raise SystemExit(f"phase26 verifier: {message}")


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path} is not an object")
    return value


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(rows: object) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def decode_fraction(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2 or not all(isinstance(item, str) for item in value):
        fail("malformed rational")
    return Fraction(int(value[0]), int(value[1]))


def ordered_compositions(total: int, slots: int, prefix: tuple[int, ...] = ()) -> Iterable[tuple[int, ...]]:
    if slots == 1:
        yield prefix + (total,)
        return
    for first in range(1, total - slots + 2):
        yield from ordered_compositions(total - first, slots - 1, prefix + (first,))


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


def reduced_walk(values: Sequence[int]) -> tuple[int, ...]:
    q = len(values)
    L = sum(values)
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    prefix = [0]
    for exponent in values:
        prefix.append(prefix[-1] + q0 * exponent - L0)
    if prefix[-1]:
        fail("height walk closure")
    return tuple(prefix)


def minimum_turns(values: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    answer = sorted({turn for turn in turns(values) if min(reduced_walk(turn)) == 0})
    if not answer:
        fail("no minimum turn")
    return tuple(answer)


def reconstruct(turn: Sequence[int]) -> dict[str, object]:
    turn = tuple(turn)
    q, L = len(turn), sum(turn)
    common = math.gcd(q, L)
    q0, L0 = q // common, L // common
    heights = reduced_walk(turn)
    residues = tuple((-L0 * time) % q0 for time in range(q + 1))
    a = []
    for height, residue in zip(heights, residues, strict=True):
        difference = height - residue
        if difference % q0:
            fail("profile divisibility")
        a.append(difference // q0)
    if min(a) < 0 or a[0] or a[-1]:
        fail("profile normalization")
    base_boundaries = tuple((L0 * time + residues[time]) // q0 for time in range(q + 1))
    base = tuple(base_boundaries[index + 1] - base_boundaries[index] for index in range(q))
    actual_boundaries = [0]
    for exponent in turn:
        actual_boundaries.append(actual_boundaries[-1] + exponent)
    if any(actual_boundaries[index] != base_boundaries[index] + a[index] for index in range(q + 1)):
        fail("boundary identity")
    if set(base) - {1, 2} or base != base[:q0] * common:
        fail("repeated baseline")
    area = sum(a[:-1])
    height = max(a[:-1], default=0)
    if area * 2 < height * (height + 1):
        fail("triangular area")
    return {"q": q, "L": L, "d": common, "q0": q0, "L0": L0, "a": tuple(a), "base": base, "area": area, "height": height}


def word(values: Sequence[int]) -> str:
    pieces = []
    for exponent in values:
        if exponent < 1:
            fail("nonpositive exponent")
        pieces.append("1")
        pieces.append("0" * (exponent - 1))
    return "".join(pieces)


def one_positions(value: str) -> tuple[int, ...]:
    return tuple(index for index, bit in enumerate(value) if bit == "1")


def independent_swap_distance(base: str, target: str) -> int:
    left = one_positions(base)
    right = one_positions(target)
    if len(left) != len(right) or any(source > destination for source, destination in zip(left, right, strict=True)):
        fail("ordered-one transport")
    return sum(destination - source for source, destination in zip(left, right, strict=True))


def factor_count(value: str, width: int) -> int:
    extended = value + value[: width - 1]
    return len({extended[index : index + width] for index in range(len(value))})


def correction(values: Sequence[int]) -> int:
    q = len(values)
    answer = 0
    prefix = 0
    for index, exponent in enumerate(values):
        answer += 3 ** (q - index - 1) * 2**prefix
        prefix += exponent
    return answer


def rational_trace(values: Sequence[int]) -> tuple[Fraction, ...]:
    q, L = len(values), sum(values)
    D = 2**L - 3**q
    if D <= 0:
        fail("nonpositive rational denominator")
    current = Fraction(correction(values), D)
    trace = [current]
    for exponent in values:
        current = (3 * current + 1) / 2**exponent
        trace.append(current)
    if trace[0] != trace[-1] or min(trace) <= 0:
        fail("rational trace")
    return tuple(trace)


def verify_profiles(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase26-reduced-profiles-v1" or stored.get("maximum_q") != Q_MAX or stored.get("proves_collatz") is not False:
        fail("reduced-profile metadata")
    rows = []
    counts = {
        "cyclic_classes": 0,
        "primitive_classes": 0,
        "coprime_classes": 0,
        "noncoprime_classes": 0,
        "minimum_rotations": 0,
        "factor_width_checks": 0,
        "rational_height_checks": 0,
        "coprime_reproduction_checks": 0,
    }
    samples: dict[str, object] = {}
    for q in range(1, Q_MAX + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            classes = sorted({necklace(item) for item in ordered_compositions(L, q)})
            for values in classes:
                counts["cyclic_classes"] += 1
                primitive = is_primitive(values)
                counts["primitive_classes"] += int(primitive)
                minima = minimum_turns(values)
                counts["minimum_rotations"] += len(minima)
                invariant = set()
                last = None
                for turn in minima:
                    data = reconstruct(turn)
                    base_word, actual_word = word(data["base"]), word(turn)
                    swaps = independent_swap_distance(base_word, actual_word)
                    if swaps != data["area"]:
                        fail("edit distance")
                    local_max = 0
                    for width in range(1, L + 1):
                        p0 = factor_count(base_word, width)
                        p1 = factor_count(actual_word, width)
                        if p0 > width + 1 or p1 > (data["area"] + 1) * (width + 1):
                            fail("factor bound")
                        counts["factor_width_checks"] += 1
                        local_max = max(local_max, p1)
                    invariant.add((data["area"], data["height"], data["base"], swaps))
                    last = (turn, data, swaps, local_max)
                if len(invariant) != 1 or last is None:
                    fail("minimum-turn invariance")
                turn, data, swaps, local_max = last
                if data["d"] == 1:
                    counts["coprime_classes"] += 1
                    residue_profile = [-1] * q
                    walk = reduced_walk(turn)
                    for height in walk[:-1]:
                        residue_profile[height % q] = height // q
                    if min(residue_profile) < 0 or sum(residue_profile) != data["area"] or max(residue_profile) != data["height"]:
                        fail("coprime P144 reproduction")
                    counts["coprime_reproduction_checks"] += 1
                else:
                    counts["noncoprime_classes"] += 1
                trace = rational_trace(turn)
                multiplier = Fraction(3**q, 2**L)
                if not max(trace[:-1]) < 2 ** (data["height"] + 1) * min(trace[:-1]) / multiplier:
                    fail("odd height")
                counts["rational_height_checks"] += 1
                rows.append([q, L, data["d"], list(values), len(minima), primitive, data["area"], data["height"], swaps, local_max])
                key = "coprime" if data["d"] == 1 else "noncoprime"
                if key not in samples and primitive and data["area"]:
                    samples[key] = {
                        "q": q, "L": L, "d": data["d"], "exponents": list(turn),
                        "baseline": list(data["base"]), "time_profile": list(data["a"]),
                        "area": data["area"], "height": data["height"], "swaps": swaps,
                    }
    if stored.get("counts") != counts or stored.get("samples") != samples or stored.get("row_digest_sha256") != stable_hash(rows):
        fail("reduced-profile reconstruction mismatch")
    return counts


def log_bounds_unit(value: Fraction, terms: int = 72) -> tuple[Fraction, Fraction]:
    z = (value - 1) / (value + 1)
    low = Fraction(0)
    power = z
    square = z * z
    for index in range(terms):
        low += 2 * power / (2 * index + 1)
        power *= square
    high = low + 2 * power / ((2 * terms + 1) * (1 - square))
    return low, high


def log_bounds(value: Fraction, terms: int = 72) -> tuple[Fraction, Fraction]:
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
    lo, hi = log_bounds_unit(reduced, terms)
    lo2, hi2 = log_bounds_unit(Fraction(2), terms)
    if exponent >= 0:
        return lo + exponent * lo2, hi + exponent * hi2
    return lo + exponent * hi2, hi + exponent * lo2


def triangular_height(area: int) -> int:
    height = math.isqrt(2 * area)
    while (height + 1) * (height + 2) <= 2 * area:
        height += 1
    while height * (height + 1) > 2 * area:
        height -= 1
    return height


def endpoint(q: int, area: int, height: int, minimum: int) -> dict[str, object]:
    ln2_lo, ln2_hi = log_bounds(Fraction(2))
    ln3_lo, _ = log_bounds(Fraction(3))
    _, lnm_hi = log_bounds(Fraction(2 * q, 3))
    _, lnp_hi = log_bounds(Fraction(minimum + 3 * q, minimum))
    left = q * ln3_lo
    right = (area + 1) * ((height + 4) * ln2_hi + lnm_hi + Fraction(1, minimum) + lnp_hi / 9)
    derivative = 9 * q * ln3_lo - 10 * (area + 1)
    return {
        "q": str(q), "area_assumption": str(area), "height_bound": height,
        "left_lower": [str(left.numerator), str(left.denominator)],
        "right_upper": [str(right.numerator), str(right.denominator)],
        "margin_lower": [str((left - right).numerator), str((left - right).denominator)],
        "positive_margin": left > right,
        "derivative_margin_lower": [str(derivative.numerator), str(derivative.denominator)],
        "positive_derivative_margin": derivative > 0,
    }


def verify_scalars(stored: dict[str, object]) -> dict[str, object]:
    if stored.get("format") != "collatz-phase26-scalar-certificates-v1" or stored.get("proves_collatz") is not False:
        fail("scalar metadata")
    critical = stored.get("critical")
    noncritical = stored.get("noncritical")
    if not isinstance(critical, dict) or not isinstance(noncritical, dict):
        fail("scalar sections")

    scan_rows = []
    passing = []
    closest = None
    for q in range(1, 512):
        K = (3**q).bit_length()
        D = 2**K - 3**q
        left, right = 3 * V * D, q * 2**K
        scan_rows.append([q, K, str(D), str(left - right)])
        if left < right:
            passing.append(q)
        if closest is None or left * closest[2] < closest[1] * right:
            closest = (q, left, right)
    small = critical.get("small_scan")
    if not isinstance(small, dict):
        fail("critical scan")
    expected_closest = {"q": closest[0], "left": str(closest[1]), "right": str(closest[2])}
    if small.get("passing_q") != passing or small.get("closest_ratio") != expected_closest or small.get("row_digest_sha256") != stable_hash(scan_rows):
        fail("critical finite scan mismatch")

    q = 512
    base_left = 3**q * 64 ** (6 * q)
    base_right = (96 * q) ** 6 * 75 ** (6 * q)
    step_left, step_right = 3 * 64**6 * q**6, 75**6 * (q + 1) ** 6
    large = critical.get("large_q")
    expected_large = {
        "base_left": str(base_left), "base_right": str(base_right), "base_margin": str(base_left - base_right), "base_positive": base_left > base_right,
        "step_left": str(step_left), "step_right": str(step_right), "step_margin": str(step_left - step_right), "step_positive": step_left > step_right,
        "conclusion": "A_*>=6 for every critical positive nontrivial primitive cycle",
    }
    if not isinstance(large, dict) or any(large.get(key) != value for key, value in expected_large.items()):
        fail("critical large-q certificate")
    obstruction = critical.get("area_six_method_obstruction")
    if not isinstance(obstruction, dict) or obstruction.get("left") != str(75**7) or obstruction.get("right") != str(3 * 64**7) or obstruction.get("positive_exponential_margin") is not False:
        fail("area-six obstruction")

    qdata = noncritical.get("noncritical_q_lower")
    if not isinstance(qdata, dict):
        fail("noncritical q lower")
    ln2_lo, _ = log_bounds(Fraction(2))
    _, ln501_hi = log_bounds(Fraction(501))
    packing_margin = ln2_lo - Fraction(1, V) - ln501_hi / 9
    if decode_fraction(qdata.get("direct_log_margin")) != packing_margin or qdata.get("direct_log_positive") is not True or qdata.get("stronger_P134_product") != 170 * V:
        fail("noncritical packing certificate")
    internal = noncritical.get("internal_area")
    if not isinstance(internal, dict) or internal.get("endpoint") != endpoint(50_000_000, 100_000, triangular_height(100_000), V):
        fail("internal endpoint certificate")
    x02 = noncritical.get("x02")
    if not isinstance(x02, dict) or x02.get("P134_product") != str(170 * VX) or x02.get("q_product_exceeds_endpoint") is not True:
        fail("X02 q certificate")
    if x02.get("endpoint") != endpoint(4 * 10**23, 5 * 10**15, triangular_height(5 * 10**15), VX):
        fail("X02 endpoint certificate")
    return {"critical_scan_rows": len(scan_rows), "critical_area_lower": 6, "noncritical_area_strict_lower": 100_000, "x02_area_strict_lower": 5 * 10**15}


def bits_to_exponents(value: str) -> tuple[int, ...]:
    pivot = value.index("1")
    shifted = value[pivot:] + value[:pivot]
    ones = [index for index, bit in enumerate(shifted) if bit == "1"]
    ones.append(len(shifted))
    return tuple(ones[index + 1] - ones[index] for index in range(len(ones) - 1))


def verify_regressions(stored: dict[str, object]) -> None:
    if stored.get("format") != "collatz-phase26-regressions-v1" or stored.get("proves_collatz") is not False:
        fail("regression metadata")
    cycles = stored.get("named_cycles")
    if not isinstance(cycles, list) or len(cycles) != 3:
        fail("named cycles")
    for row in cycles:
        source = Fraction(row["source"])
        current = source
        for exponent in row["exponents"]:
            current = (3 * current + 1) / 2**exponent
        if row.get("returns") != (current == source):
            fail("cycle return")
        if row["source"] <= 1 and row.get("positive_nontrivial_eligible") is not False:
            fail("positive-boundary eligibility")
    powers = stored.get("nonprimitive_trivial_powers")
    expected_powers = []
    for count in range(2, 7):
        data = reconstruct((2,) * count)
        expected_powers.append([count, data["d"], data["q0"], data["L0"], data["area"], is_primitive((2,) * count)])
    if powers != expected_powers:
        fail("trivial powers")
    families = stored.get("adversarial_families")
    if not isinstance(families, list):
        fail("families")
    for row in families:
        exponents = bits_to_exponents(row[1])
        if row[2:] != [list(exponents), len(exponents), sum(exponents), str(2 ** sum(exponents) - 3 ** len(exponents))]:
            fail("family reconstruction")
    if stored.get("phase25_resonance_control") != {"q": 63322, "L": 100363, "roots": [9046, 18092, 27138], "direct_modular_gcd": 1}:
        fail("Phase 25 control")
    ng32 = stored.get("NG32_control")
    if ng32 != {"q": 4, "word": "1101100", "width": 2, "factor_count": 4} or len({"1101100"[i : i + 2] for i in range(6)}) != 4:
        fail("NG32 control")


def verify_theory(stored: dict[str, object]) -> dict[str, str]:
    if stored.get("format") != "collatz-phase26-theory-v1" or stored.get("proves_collatz") is not False:
        fail("theory metadata")
    claims = stored.get("claims")
    if not isinstance(claims, dict):
        fail("theory claims")
    expected = {
        "P156": "VERIFIED_THEOREM", "P157": "VERIFIED_THEOREM", "P158": "VERIFIED_THEOREM",
        "P159": "VERIFIED_THEOREM", "P160": "CONDITIONAL", "P161": "VERIFIED_THEOREM",
        "E38": "VERIFIED_FINITE", "NG35": "REFUTED", "H147": "VERIFIED_THEOREM", "H133": "OPEN",
    }
    for claim, status in expected.items():
        row = claims.get(claim)
        if not isinstance(row, dict) or row.get("status") != status:
            fail(f"claim status {claim}")
    boundary = stored.get("what_this_result_does_not_prove")
    if not isinstance(boundary, str) or "Collatz" not in boundary or "critical area six" not in boundary:
        fail("no-overclaim boundary")
    return expected


def verify_obstruction(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for token in ("75^7", "13348388671875", "13194139533312", "does not construct", "proves_collatz=false"):
        if token not in text:
            fail("obstruction report")


def verify(directory: Path) -> dict[str, object]:
    for name in FILES:
        if not (directory / name).is_file():
            fail(f"missing {name}")
    theory = load(directory / "phase26_theory.json")
    profiles = load(directory / "phase26_reduced_profiles.json")
    scalars = load(directory / "phase26_scalar_certificates.json")
    regressions = load(directory / "phase26_regressions.json")
    claims = verify_theory(theory)
    counts = verify_profiles(profiles)
    scalar_counts = verify_scalars(scalars)
    verify_regressions(regressions)
    verify_obstruction(directory / "phase26_obstruction_report.md")
    hashes = {name: hashlib.sha256((directory / name).read_bytes()).hexdigest() for name in FILES}
    return {
        "format": "collatz-phase26-independent-verifier-v1",
        "claims": claims,
        "generator_imported": False,
        "profile_counts": counts,
        "scalar_counts": scalar_counts,
        "verified_input_sha256": hashes,
        "independence": "recursive compositions, ordered-one displacement, direct rational traces, separately coded atanh intervals, and exact integer scans",
        "what_this_result_does_not_prove": "This does not exclude critical area six or above, arbitrary-area cycles, nonperiodic counterexamples, or Collatz.",
        "proves_collatz": False,
        "valid": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.artifact_dir)
    if args.output:
        save(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
