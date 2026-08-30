#!/usr/bin/env python3
"""Generate exact Phase 26 reduced-slope cycle-area evidence.

The supplied Phase 26 note is treated as an untrusted proposal.  Acceptance
decisions use integers and Fractions only; floating point is not used.
"""

from __future__ import annotations

import argparse
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


V = 300_000
VX = 2075 * 2**60
PROFILE_Q_MAXIMUM = 8
CRITICAL_CUTOFF = 512
NONCRITICAL_Q_ENDPOINT = 50_000_000
NONCRITICAL_AREA = 100_000
X02_Q_ENDPOINT = 4 * 10**23
X02_AREA = 5 * 10**15
A_BITS = "11101"
B_BITS = "1100"
NEGATIVE_Q7 = (1, 1, 1, 2, 1, 1, 4)


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(rows: object) -> str:
    encoded = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def compositions(total: int, count: int) -> Iterable[tuple[int, ...]]:
    if count == 1:
        yield (total,)
        return
    for cuts in itertools.combinations(range(1, total), count - 1):
        points = (0,) + cuts + (total,)
        yield tuple(points[index + 1] - points[index] for index in range(count))


def rotations(values: Sequence[int]) -> Iterable[tuple[int, ...]]:
    values = tuple(values)
    for offset in range(len(values)):
        yield values[offset:] + values[:offset]


def cyclic_class(values: Sequence[int]) -> tuple[int, ...]:
    return min(rotations(values))


def primitive(values: Sequence[int]) -> bool:
    values = tuple(values)
    return all(
        values != values[:period] * (len(values) // period)
        for period in range(1, len(values))
        if len(values) % period == 0
    )


def reduced_parameters(exponents: Sequence[int]) -> tuple[int, int, int, int, int]:
    q = len(exponents)
    L = sum(exponents)
    divisor = math.gcd(q, L)
    return q, L, divisor, q // divisor, L // divisor


def reduced_heights(exponents: Sequence[int]) -> tuple[int, ...]:
    q, _, _, q0, L0 = reduced_parameters(exponents)
    height = 0
    answer = [0]
    for exponent in exponents:
        height += q0 * exponent - L0
        answer.append(height)
    if len(answer) != q + 1 or height != 0:
        raise AssertionError("reduced height walk does not close")
    return tuple(answer)


def minimum_rotations(exponents: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    candidates = {
        rotated for rotated in rotations(exponents) if min(reduced_heights(rotated)) == 0
    }
    if not candidates:
        raise AssertionError("cycle lemma found no minimum rotation")
    return tuple(sorted(candidates))


def reduced_profile(exponents: Sequence[int]) -> dict[str, object]:
    exponents = tuple(exponents)
    q, L, divisor, q0, L0 = reduced_parameters(exponents)
    heights = reduced_heights(exponents)
    residues = tuple((-L0 * index) % q0 for index in range(q + 1))
    profile = tuple((height - residue) // q0 for height, residue in zip(heights, residues, strict=True))
    if any(height != residue + q0 * value for height, residue, value in zip(heights, residues, profile, strict=True)):
        raise AssertionError("reduced profile reconstruction")
    if min(profile) < 0 or profile[0] or profile[-1]:
        raise AssertionError("reduced profile normalization")
    baseline_boundaries = tuple((L0 * index + residues[index]) // q0 for index in range(q + 1))
    actual_boundaries = [0]
    for exponent in exponents:
        actual_boundaries.append(actual_boundaries[-1] + exponent)
    if tuple(actual_boundaries) != tuple(
        baseline + value for baseline, value in zip(baseline_boundaries, profile, strict=True)
    ):
        raise AssertionError("boundary edit identity")
    baseline = tuple(
        baseline_boundaries[index + 1] - baseline_boundaries[index] for index in range(q)
    )
    if any(value not in (1, 2) for value in baseline):
        raise AssertionError("reduced baseline increment")
    if baseline != baseline[:q0] * divisor:
        raise AssertionError("repeated reduced baseline")
    area = sum(profile[:-1])
    height = max(profile[:-1], default=0)
    if 2 * area < height * (height + 1):
        raise AssertionError("triangular reduced-profile bound")
    return {
        "q": q,
        "L": L,
        "d": divisor,
        "q0": q0,
        "L0": L0,
        "heights": heights,
        "residues": residues,
        "profile": profile,
        "baseline": baseline,
        "area": area,
        "height": height,
    }


def expanded_word(exponents: Sequence[int]) -> str:
    return "".join("1" + "0" * (exponent - 1) for exponent in exponents)


def cyclic_factors(word: str, width: int) -> set[str]:
    if not 1 <= width <= len(word):
        raise ValueError("cyclic factor width")
    doubled = word + word[: width - 1]
    return {doubled[start : start + width] for start in range(len(word))}


def literal_swap_count(base: str, target: str) -> int:
    if len(base) != len(target) or base.count("1") != target.count("1"):
        raise ValueError("incompatible words")
    work = list(base)
    target_positions = [index for index, bit in enumerate(target) if bit == "1"]
    count = 0
    for rank in range(len(target_positions) - 1, -1, -1):
        current_positions = [index for index, bit in enumerate(work) if bit == "1"]
        position = current_positions[rank]
        target_position = target_positions[rank]
        if position > target_position:
            raise AssertionError("reduced profile moved a one left")
        while position < target_position:
            if work[position : position + 2] != ["1", "0"]:
                raise AssertionError("adjacent swap obstruction")
            work[position], work[position + 1] = "0", "1"
            position += 1
            count += 1
    if "".join(work) != target:
        raise AssertionError("adjacent swap reconstruction")
    return count


def affine_correction(exponents: Sequence[int]) -> int:
    q = len(exponents)
    power = 0
    answer = 0
    for index, exponent in enumerate(exponents):
        answer += 3 ** (q - 1 - index) * 2**power
        power += exponent
    return answer


def rational_odd_orbit(exponents: Sequence[int]) -> tuple[Fraction, ...]:
    q = len(exponents)
    L = sum(exponents)
    denominator = 2**L - 3**q
    if denominator <= 0:
        raise ValueError("positive rational cycle requires D>0")
    current = Fraction(affine_correction(exponents), denominator)
    answer = [current]
    for exponent in exponents:
        current = (3 * current + 1) / 2**exponent
        answer.append(current)
    if answer[-1] != answer[0] or min(answer) <= 0:
        raise AssertionError("positive rational affine cycle")
    return tuple(answer)


def coprime_profile(exponents: Sequence[int]) -> tuple[int, ...]:
    q, L, divisor, _, _ = reduced_parameters(exponents)
    if divisor != 1:
        raise ValueError("coprime profile requested at noncoprime slope")
    data = reduced_profile(exponents)
    answer = [-1] * q
    for residue, value in zip(data["residues"][:-1], data["profile"][:-1], strict=True):
        answer[residue] = value
    if min(answer) < 0 or answer[0] != 0:
        raise AssertionError("coprime profile")
    return tuple(answer)


def reduced_profile_audit() -> dict[str, object]:
    rows: list[object] = []
    samples: dict[str, object] = {}
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
    for q in range(1, PROFILE_Q_MAXIMUM + 1):
        for L in range(q + 1, 2 * q + 1):
            if 2**L <= 3**q:
                continue
            classes = sorted({cyclic_class(values) for values in compositions(L, q)})
            for values in classes:
                counts["cyclic_classes"] += 1
                is_primitive = primitive(values)
                counts["primitive_classes"] += int(is_primitive)
                rotations_at_minimum = minimum_rotations(values)
                counts["minimum_rotations"] += len(rotations_at_minimum)
                invariants = set()
                representative = None
                for rotated in rotations_at_minimum:
                    data = reduced_profile(rotated)
                    base_word = expanded_word(data["baseline"])
                    word = expanded_word(rotated)
                    swaps = literal_swap_count(base_word, word)
                    if swaps != data["area"]:
                        raise AssertionError("reduced edit area")
                    local_maximum = 0
                    for width in range(1, L + 1):
                        base_count = len(cyclic_factors(base_word, width))
                        actual_count = len(cyclic_factors(word, width))
                        if base_count > width + 1 or actual_count > (data["area"] + 1) * (width + 1):
                            raise AssertionError("reduced cyclic factor bound")
                        counts["factor_width_checks"] += 1
                        local_maximum = max(local_maximum, actual_count)
                    invariants.add((data["area"], data["height"], tuple(data["baseline"]), swaps))
                    representative = (rotated, data, swaps, local_maximum)
                if len(invariants) != 1 or representative is None:
                    raise AssertionError("minimum-rotation invariance")
                rotated, data, swaps, local_maximum = representative
                if data["d"] == 1:
                    counts["coprime_classes"] += 1
                    profile = coprime_profile(rotated)
                    if sum(profile) != data["area"] or max(profile) != data["height"]:
                        raise AssertionError("P144 reproduction")
                    counts["coprime_reproduction_checks"] += 1
                else:
                    counts["noncoprime_classes"] += 1
                orbit = rational_odd_orbit(rotated)
                least = min(orbit[:-1])
                largest = max(orbit[:-1])
                multiplier = Fraction(3**q, 2**L)
                if not largest < Fraction(2 ** (data["height"] + 1), 1) * least / multiplier:
                    raise AssertionError("odd state-height bound")
                counts["rational_height_checks"] += 1
                row = [
                    q, L, data["d"], list(values), len(rotations_at_minimum), is_primitive,
                    data["area"], data["height"], swaps, local_maximum,
                ]
                rows.append(row)
                key = "coprime" if data["d"] == 1 else "noncoprime"
                if key not in samples and is_primitive and data["area"]:
                    samples[key] = {
                        "q": q,
                        "L": L,
                        "d": data["d"],
                        "exponents": list(rotated),
                        "baseline": list(data["baseline"]),
                        "time_profile": list(data["profile"]),
                        "area": data["area"],
                        "height": data["height"],
                        "swaps": swaps,
                    }
    return {
        "format": "collatz-phase26-reduced-profiles-v1",
        "maximum_q": PROFILE_Q_MAXIMUM,
        "counts": counts,
        "samples": samples,
        "row_digest_sha256": digest(rows),
        "scope": "All positive-D cyclic exponent classes through q<=8; structural checks include every minimum-height rotation. Rational affine shadows are used only for the algebraic odd-height check.",
        "proves_collatz": False,
    }


def atanh_log_interval(value: Fraction, terms: int = 72) -> tuple[Fraction, Fraction]:
    if value < 1:
        raise ValueError("unit log interval expects value>=1")
    z = (value - 1) / (value + 1)
    total = sum(2 * z ** (2 * index + 1) / (2 * index + 1) for index in range(terms))
    tail = 2 * z ** (2 * terms + 1) / ((2 * terms + 1) * (1 - z * z))
    return total, total + tail


def log_interval(value: Fraction, terms: int = 72) -> tuple[Fraction, Fraction]:
    if value <= 0:
        raise ValueError("log interval")
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    power = Fraction(2**exponent, 1) if exponent >= 0 else Fraction(1, 2 ** (-exponent))
    while value < power:
        exponent -= 1
        power /= 2
    while value >= 2 * power:
        exponent += 1
        power *= 2
    reduced = value / power
    low_reduced, high_reduced = atanh_log_interval(reduced, terms)
    low_two, high_two = atanh_log_interval(Fraction(2), terms)
    if exponent >= 0:
        return low_reduced + exponent * low_two, high_reduced + exponent * high_two
    return low_reduced + exponent * high_two, high_reduced + exponent * low_two


def largest_triangular_height(area: int) -> int:
    return (math.isqrt(1 + 8 * area) - 1) // 2


def endpoint_margin(q: int, area: int, height: int, minimum: int) -> dict[str, object]:
    ln2_low, ln2_high = log_interval(Fraction(2))
    ln3_low, _ = log_interval(Fraction(3))
    _, log_m_high = log_interval(Fraction(2 * q, 3))
    _, log_pack_high = log_interval(Fraction(minimum + 3 * q, minimum))
    left_lower = q * ln3_low
    right_upper = (area + 1) * (
        (height + 4) * ln2_high + log_m_high + Fraction(1, minimum) + log_pack_high / 9
    )
    derivative_lower = 9 * q * ln3_low - 10 * (area + 1)
    return {
        "q": str(q),
        "area_assumption": str(area),
        "height_bound": height,
        "left_lower": encode_fraction(left_lower),
        "right_upper": encode_fraction(right_upper),
        "margin_lower": encode_fraction(left_lower - right_upper),
        "positive_margin": left_lower > right_upper,
        "derivative_margin_lower": encode_fraction(derivative_lower),
        "positive_derivative_margin": derivative_lower > 0,
    }


def critical_scalar_certificate() -> dict[str, object]:
    scan_rows = []
    closest = None
    passing = []
    for q in range(1, CRITICAL_CUTOFF):
        K = (3**q).bit_length()
        D = 2**K - 3**q
        left = 3 * V * D
        right = q * 2**K
        row = [q, K, str(D), str(left - right)]
        scan_rows.append(row)
        if left < right:
            passing.append(q)
        if closest is None or left * closest[2] < closest[1] * right:
            closest = (q, left, right)
    q = CRITICAL_CUTOFF
    base_left = 3**q * 64 ** (6 * q)
    base_right = (96 * q) ** 6 * 75 ** (6 * q)
    step_left = 3 * 64**6 * q**6
    step_right = 75**6 * (q + 1) ** 6
    return {
        "critical_q_cutoff": q,
        "small_scan": {
            "range": [1, q - 1],
            "necessary": "3*300000*(2^K_q-3^q)<q*2^K_q",
            "passing_q": passing,
            "closest_ratio": {"q": closest[0], "left": str(closest[1]), "right": str(closest[2])},
            "row_digest_sha256": digest(scan_rows),
        },
        "large_q": {
            "base_left": str(base_left),
            "base_right": str(base_right),
            "base_margin": str(base_left - base_right),
            "base_positive": base_left > base_right,
            "step_left": str(step_left),
            "step_right": str(step_right),
            "step_margin": str(step_left - step_right),
            "step_positive": step_left > step_right,
            "conclusion": "A_*>=6 for every critical positive nontrivial primitive cycle",
        },
        "area_six_method_obstruction": {
            "left": str(75**7),
            "right": str(3 * 64**7),
            "positive_exponential_margin": 3 * 64**7 > 75**7,
            "statement": "The EXT05/factor-separation coefficient reverses at A_*=6, so this scalar method cannot prove A_*>=7.",
        },
    }


def noncritical_scalar_certificate() -> dict[str, object]:
    ln2_low, _ = log_interval(Fraction(2))
    _, ln501_high = log_interval(Fraction(501))
    packing_margin = ln2_low - Fraction(1, V) - ln501_high / 9
    internal_endpoint = endpoint_margin(
        NONCRITICAL_Q_ENDPOINT,
        NONCRITICAL_AREA,
        largest_triangular_height(NONCRITICAL_AREA),
        V,
    )
    x02_endpoint = endpoint_margin(
        X02_Q_ENDPOINT,
        X02_AREA,
        largest_triangular_height(X02_AREA),
        VX,
    )
    return {
        "finite_minimum": V,
        "noncritical_q_lower": {
            "direct_log_margin": encode_fraction(packing_margin),
            "direct_log_positive": packing_margin > 0,
            "note_endpoint": NONCRITICAL_Q_ENDPOINT,
            "stronger_P134_product": 170 * V,
            "conclusion": "noncriticality implies q>51000000 by P134; the q=50000000 endpoint is retained for a conservative monotone area certificate",
        },
        "internal_area": {
            "endpoint": internal_endpoint,
            "conclusion": "A_*>100000",
        },
        "x02": {
            "minimum": str(VX),
            "q_endpoint": str(X02_Q_ENDPOINT),
            "P134_product": str(170 * VX),
            "q_product_exceeds_endpoint": 170 * VX > X02_Q_ENDPOINT,
            "endpoint": x02_endpoint,
            "conclusion": "conditional on X02, A_*>5000000000000000",
        },
    }


def scalar_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase26-scalar-certificates-v1",
        "critical": critical_scalar_certificate(),
        "noncritical": noncritical_scalar_certificate(),
        "arithmetic": "All comparisons use integers or rational atanh-series log enclosures.",
        "proves_collatz": False,
    }


def exponents_from_cyclic_bits(word: str) -> tuple[int, ...]:
    if not word or set(word) - {"0", "1"} or "1" not in word:
        raise ValueError("cyclic word")
    start = word.index("1")
    rotated = word[start:] + word[:start]
    positions = [index for index, bit in enumerate(rotated) if bit == "1"] + [len(rotated)]
    return tuple(positions[index + 1] - positions[index] for index in range(len(positions) - 1))


def regression_artifact() -> dict[str, object]:
    named_cycles = []
    for name, source, exponents in (
        ("trivial-positive", 1, (2,)),
        ("negative-q2", -5, (1, 2)),
        ("negative-q7", -17, NEGATIVE_Q7),
    ):
        current = Fraction(source)
        orbit = [current]
        for exponent in exponents:
            current = (3 * current + 1) / 2**exponent
            orbit.append(current)
        named_cycles.append({
            "name": name,
            "source": source,
            "exponents": list(exponents),
            "returns": orbit[-1] == orbit[0],
            "positive_nontrivial_eligible": source > 1 and min(orbit) > 0,
        })
    powers = []
    for count in range(2, 7):
        values = (2,) * count
        data = reduced_profile(values)
        powers.append([count, data["d"], data["q0"], data["L0"], data["area"], primitive(values)])
    families = []
    for name, word in (
        ("A=11101", A_BITS),
        ("B=1100", B_BITS),
        ("(110|111)^*", "110111" * 8),
        ("A^1B^1", A_BITS + B_BITS),
        ("A^2B^3", A_BITS * 2 + B_BITS * 3),
        ("2^m-1-control", "1" * 12 + "0"),
        ("8^m-5-control", "111001" * 4),
    ):
        exponents = exponents_from_cyclic_bits(word)
        q = len(exponents)
        L = sum(exponents)
        families.append([name, word, list(exponents), q, L, str(2**L - 3**q)])
    return {
        "format": "collatz-phase26-regressions-v1",
        "named_cycles": named_cycles,
        "nonprimitive_trivial_powers": powers,
        "adversarial_families": families,
        "phase25_resonance_control": {"q": 63322, "L": 100363, "roots": [9046, 18092, 27138], "direct_modular_gcd": 1},
        "NG32_control": {"q": 4, "word": "1101100", "width": 2, "factor_count": 4},
        "scope": "Negative cycles and nonprimitive powers are boundary controls only. Positive-cycle minimum and state-separation conclusions are not applied to them.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase26-theory-v1",
        "claims": {
            "P156": {"status": "VERIFIED_THEOREM", "statement": "Every primitive positive-cycle exponent word has the reduced-slope time profile, exact adjacent-swap area, cyclic factor bound, and triangular height bound."},
            "P157": {"status": "VERIFIED_THEOREM", "statement": "Every primitive positive nontrivial cycle obeys the arbitrary-slope state-height and master factor-separation inequalities."},
            "P158": {"status": "VERIFIED_THEOREM", "statement": "Every critical primitive positive nontrivial cycle has reduced-slope area A_*>=6."},
            "P159": {"status": "VERIFIED_THEOREM", "statement": "Every noncritical primitive positive nontrivial cycle has reduced-slope area A_*>100000."},
            "P160": {"status": "CONDITIONAL", "statement": "Assuming X02, every noncritical primitive positive cycle has A_*>5*10^15."},
            "P161": {"status": "VERIFIED_THEOREM", "statement": "Every noncritical cycle with A_*>0 obeys the exact slope/area phase inequality."},
            "E38": {"status": "VERIFIED_FINITE", "statement": "The reduced profile, edit identity, factor bound, and odd state-height bound are independently checked on the complete q<=8 positive-D cyclic exponent corpus."},
            "NG35": {"status": "REFUTED", "statement": "The Phase 26 EXT05/factor-separation scalar mechanism can also exclude critical area six."},
            "H147": {"status": "VERIFIED_THEOREM", "statement": "Critical coprime area-three positive cycles are excluded, now as a consequence of the stronger arbitrary-slope P158 barrier."},
            "H133": {"status": "OPEN", "statement": "Critical area at least six, enormous noncritical area, and all noncoprime profiles still require a complete cycle exclusion."},
        },
        "reduced_profile": {
            "height": "H_j=q0*E_j-L0*j=r_j+q0*a_j after a minimum-height rotation",
            "baseline": "E_j^(0)=(L0*j+r_j)/q0; its exponent period q0 repeats d times",
            "edit": "A_*=sum_(j<q)a_j is the exact number of adjacent swaps 10->01",
            "factor": "p_cyc(n)<=(A_*+1)(n+1)",
            "triangular": "A_*>=h_*(h_*+1)/2",
        },
        "master": {
            "odd_height": "M_odd<2^(h_*+1)m/lambda",
            "shortcut_height": "M<2^(h_*+2)m/lambda",
            "separation": "L<=(A_*+1)(ceil(log2(2^(h_*+2)m/lambda))+1)",
            "strict": "L<(A_*+1)[h_*+4+log2(q/(3lambda(1-lambda)))]",
        },
        "phase_diagram": "For noncritical t=L-q*log2(3)>1 and A_*>0: t>(log2(3)/A_*)q-((A_*+1)/A_*)(log2(q)+h_*+5-log2(3)).",
        "dependencies": {
            "P158": ["P133", "P157", "E28", "EXT05"],
            "P159": ["P133", "P134", "P156", "P157", "E28"],
            "P160": ["P159 method", "X02"],
        },
        "what_this_result_does_not_prove": "It does not exclude critical area six or above, arbitrary-area positive cycles, any nonperiodic branch, or Collatz.",
        "proves_collatz": False,
    }


def obstruction_markdown(scalar: dict[str, object], profile: dict[str, object]) -> str:
    counts = profile["counts"]
    obstruction = scalar["critical"]["area_six_method_obstruction"]
    return f"""# Phase 26 obstruction report

## Exact finite audit

- positive-D cyclic exponent classes through `q<={profile['maximum_q']}`: `{counts['cyclic_classes']}`;
- primitive classes: `{counts['primitive_classes']}`;
- noncoprime classes: `{counts['noncoprime_classes']}`;
- cyclic factor-width checks: `{counts['factor_width_checks']}`;
- positive rational odd-height checks: `{counts['rational_height_checks']}`.

These are bounded structural checks, not a search proving that all integer
cycles have been enumerated.

## Exact obstruction to the next critical area

The Phase 26 scalar argument excludes `A_*<=5`, but at `A_*=6` its
exponential comparison reverses:

```text
75^7 = {obstruction['left']}
3*64^7 = {obstruction['right']}
75^7 > 3*64^7
```

Thus EXT05 plus factor separation alone cannot exclude critical area six.
This does not construct an area-six cycle.  Critical area six is the first
remaining periodic target.

## What this result does not prove

Phase 26 does not eliminate all positive cycles, nonperiodic counterexamples,
or the Collatz conjecture. `proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)

    profile = reduced_profile_audit()
    scalar = scalar_artifact()
    regressions = regression_artifact()
    theory = theory_artifact()

    write_json(args.artifact_dir / "phase26_reduced_profiles.json", profile)
    write_json(args.artifact_dir / "phase26_scalar_certificates.json", scalar)
    write_json(args.artifact_dir / "phase26_regressions.json", regressions)
    write_json(args.artifact_dir / "phase26_theory.json", theory)
    (args.artifact_dir / "phase26_obstruction_report.md").write_text(
        obstruction_markdown(scalar, profile), encoding="utf-8"
    )

    print(json.dumps({
        "critical_area_lower": 6,
        "finite_classes": profile["counts"]["cyclic_classes"],
        "noncritical_area_strict_lower": NONCRITICAL_AREA,
        "proves_collatz": False,
        "valid": True,
        "x02_area_strict_lower": str(X02_AREA),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
