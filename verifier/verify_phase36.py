#!/usr/bin/env python3
"""Independent exact verifier for Phase 36 artifacts.

The verifier imports no generator or ``src`` module.  It independently
rebuilds the root/event corpora, the Phase 35 scalar boundary, and every
bounded decoder mirror-root row.  Previously accepted Phase 35 arithmetic is
reused only through its independent verifier implementation.
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

from verify_phase35 import (CUTOFF, MATVEEV, critical_length, rebuild_frontier,
                            rebuild_low, reconstruct_profile, safe_positions)


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


CLAIMS = {
    "P211": "VERIFIED_THEOREM", "P212": "VERIFIED_THEOREM",
    "P213": "VERIFIED_THEOREM", "P214": "VERIFIED_THEOREM",
    "P215": "VERIFIED_THEOREM", "P216": "VERIFIED_THEOREM",
    "P217": "VERIFIED_THEOREM", "P218": "VERIFIED_THEOREM",
    "E51": "VERIFIED_FINITE", "E52": "VERIFIED_FINITE",
    "NG42": "REFUTED", "H89": "OPEN", "H133": "OPEN", "H172": "OPEN",
}
FILES = (
    "phase36_theory.json", "phase36_root_corpus.json",
    "phase36_event_polynomial.json", "phase36_scalar_audit.json",
    "phase36_decoder_roots.json", "phase36_regressions.json",
    "phase36_obstruction_report.md",
)


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(",", ":")).encode("ascii")).hexdigest()


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
    return all(values != values[:period] * (len(values) // period)
               for period in range(1, len(values)) if len(values) % period == 0)


def reduced_heights(exponents: Sequence[int]) -> tuple[int, ...]:
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    answer, value = [0], 0
    for exponent in exponents:
        value += q0 * exponent - length0
        answer.append(value)
    if value:
        fail("nonclosed height walk")
    return tuple(answer)


def minimum_rotations(exponents: Sequence[int]) -> tuple[tuple[int, ...], ...]:
    answer = {row for row in rotations(exponents) if min(reduced_heights(row)) == 0}
    if not answer:
        fail("no minimum rotation")
    return tuple(sorted(answer))


def profile_data(exponents: Sequence[int]) -> tuple[tuple[int, ...], tuple[int, ...]]:
    q, length = len(exponents), sum(exponents)
    divisor = math.gcd(q, length)
    q0, length0 = q // divisor, length // divisor
    heights = reduced_heights(exponents)
    residues = tuple((-length0 * index) % q0 for index in range(q + 1))
    profile = tuple((height - residue) // q0
                    for height, residue in zip(heights, residues, strict=True))
    baseline_boundaries = tuple((length0 * index + residues[index]) // q0
                                for index in range(q + 1))
    baseline = tuple(baseline_boundaries[index + 1] - baseline_boundaries[index]
                     for index in range(q))
    if min(profile) < 0 or profile[0] or profile[-1] or set(baseline) - {1, 2}:
        fail("invalid reduced profile")
    return profile, baseline


def level_intervals(profile: Sequence[int]) -> tuple[tuple[tuple[int, int], ...], ...]:
    if profile[0] or profile[-1]:
        fail("level-cut boundary")
    q, answer = len(profile) - 1, []
    for level in range(1, max(profile[:-1], default=0) + 1):
        rows, start = [], None
        for index in range(q + 1):
            active = index < q and profile[index] >= level
            if active and start is None:
                start = index
            if not active and start is not None:
                rows.append((start, index))
                start = None
        answer.append(tuple(rows))
    return tuple(answer)


def boundaries(exponents: Sequence[int]) -> tuple[int, ...]:
    answer = [0]
    for exponent in exponents:
        answer.append(answer[-1] + exponent)
    return tuple(answer)


def expanded_word(exponents: Sequence[int]) -> str:
    return "".join("1" + "0" * (value - 1) for value in exponents)


def cyclic_factors(word: str, width: int) -> set[str]:
    doubled = word + word[:width - 1]
    return {doubled[index:index + width] for index in range(len(word))}


def root_geometry(exponents: Sequence[int]) -> dict[str, object]:
    profile, baseline = profile_data(exponents)
    length = sum(exponents)
    base_boundaries = boundaries(baseline)
    intervals = tuple((start, end, base_boundaries[start], base_boundaries[end])
                      for start, end in (level_intervals(profile)[0]
                                         if max(profile[:-1], default=0) else ()))
    covered = {position for _, _, left, right in intervals for position in range(left, right)}
    actual_word, base_word = expanded_word(exponents), expanded_word(baseline)
    changed = {index for index, (a, b) in enumerate(zip(actual_word, base_word, strict=True))
               if a != b}
    if not changed <= covered:
        fail("cycle root localization")
    root_labels = sum(end - start for start, end, _, _ in intervals)
    root_span = sum(right - left for _, _, left, right in intervals)
    gaps = []
    if intervals:
        for index, (_, _, _, right) in enumerate(intervals):
            following = intervals[(index + 1) % len(intervals)][2]
            if index + 1 == len(intervals):
                following += length
            gaps.append(following - right)
    else:
        gaps.append(length)
    factor_rows, distinct_count = [], 0
    for width in range(1, length + 1):
        p0, target = len(cyclic_factors(base_word, width)), len(cyclic_factors(actual_word, width))
        if p0 > width + 1 or target > p0 + root_span + len(intervals) * (width - 1):
            fail("cycle root factor bound")
        distinct = target == length
        gap_sum = sum(max(0, gap - width + 1) for gap in gaps)
        if distinct and (gap_sum > width + 1 or max(gaps) > 2 * width):
            fail("cycle root gap bound")
        distinct_count += int(distinct)
        factor_rows.append([width, p0, target, int(distinct), gap_sum])
    return {"q": len(exponents), "L": length, "profile": list(profile),
            "root_intervals": [list(row) for row in intervals],
            "root_count": len(intervals), "root_label_count": root_labels,
            "root_span": root_span, "changed_positions": sorted(changed),
            "complement_gaps": gaps, "factor_rows": factor_rows,
            "distinct_factor_widths": distinct_count}


def expected_root_corpus() -> dict[str, object]:
    counts = {"cyclic_classes": 0, "primitive_classes": 0,
              "minimum_rotations": 0, "root_intervals": 0,
              "localized_changed_positions": 0, "factor_width_checks": 0,
              "distinct_factor_checks": 0}
    rows, samples = [], []
    for q in range(1, 9):
        for length in range(q + 1, 2 * q + 1):
            if 2 ** length <= 3 ** q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                for rotated in minimum_rotations(values):
                    row = root_geometry(rotated)
                    counts["minimum_rotations"] += 1
                    counts["root_intervals"] += row["root_count"]
                    counts["localized_changed_positions"] += len(row["changed_positions"])
                    counts["factor_width_checks"] += row["L"]
                    counts["distinct_factor_checks"] += row["distinct_factor_widths"]
                    rows.append([list(rotated), row])
                    if row["root_count"] and len(samples) < 10:
                        samples.append([list(rotated), row])
    return {"format": "collatz-phase36-root-corpus-v1", "maximum_q": 8,
            "counts": counts, "row_digest_sha256": stable_hash(rows),
            "samples": samples,
            "scope": "Complete positive-D cyclic exponent corpus through q<=8 and every cyclic factor width.",
            "proves_collatz": False}


def affine_correction(exponents: Sequence[int]) -> int:
    answer = power = 0
    q = len(exponents)
    for index, exponent in enumerate(exponents):
        answer += 3 ** (q - 1 - index) * 2 ** power
        power += exponent
    return answer


def reduced_polynomial(profile: Sequence[int]) -> tuple[int, ...]:
    q, answer = len(profile), [0] * len(profile)
    answer[0] = 1
    for residue, height in enumerate(profile):
        value = 2 ** height - 1
        answer[residue] -= value
        answer[(residue + 1) % q] += value * (2 if residue + 1 == q else 1)
    return tuple(answer)


def extended_gcd(left: int, right: int) -> tuple[int, int, int]:
    old_r, r, old_s, s, old_t, t = left, right, 1, 0, 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    return old_r, old_s, old_t


def slope_root(q: int, length: int, modulus: int) -> int:
    divisor, u, v = extended_gcd(q, length)
    if divisor != 1 or modulus <= 1:
        fail("slope-root boundary")
    def signed(base: int, exponent: int) -> int:
        return pow(pow(base, -1, modulus), -exponent, modulus) if exponent < 0 else pow(base, exponent, modulus)
    return signed(2, u) * signed(3, v) % modulus


def sparse_arc(coefficients: Sequence[int], q: int, length: int) -> dict[str, object]:
    support = tuple(index for index, value in enumerate(coefficients) if value)
    if not support:
        fail("zero sparse polynomial")
    if q == 1:
        lifts, width, gap = {support[0]: 0}, 0, 1
    else:
        inverse = pow(length, -1, q)
        residues = {index: (-index * inverse) % q for index in support}
        points = sorted(residues.values())
        gaps = [((points[(index + 1) % len(points)] + (q if index + 1 == len(points) else 0))
                 - point) for index, point in enumerate(points)]
        gap = max(gaps)
        cut = gaps.index(gap)
        start = points[(cut + 1) % len(points)]
        lifts = {index: residue if residue >= start else residue + q
                 for index, residue in residues.items()}
        width = max(lifts.values()) - min(lifts.values())
    powers = {index: (length * lifts[index] + index) // q for index in support}
    least, largest = min(powers.values()), max(lifts.values())
    integer = sum(coefficients[index] * 2 ** (powers[index] - least)
                  * 3 ** (largest - lifts[index]) for index in support)
    l1 = sum(abs(coefficients[index]) for index in support)
    return {"support": list(support), "support_count": len(support), "l1_norm": l1,
            "lift_width": width, "largest_gap": gap,
            "b_lifts": [[index, lifts[index]] for index in support],
            "A_lifts": [[index, powers[index]] for index in support],
            "integer_R": integer,
            "all_nonzero_coefficients_odd": all(coefficients[index] % 2 for index in support)}


def event_polynomial(exponents: Sequence[int], profile: Sequence[int], baseline: Sequence[int]) -> dict[str, object]:
    q, length = len(exponents), sum(exponents)
    shift, A = 2 * q - length, [0] * q
    for time, value in enumerate(profile):
        A[(-length * time) % q] = 2 ** value
    coefficients = [0] * q
    for residue, coefficient in enumerate(A):
        coefficients[residue] += 2 * coefficient
        total = residue + shift
        coefficients[total % q] -= coefficient * (2 if total >= q else 1)
    predicted = [0] * q
    for time, exponent in enumerate(exponents):
        predicted[(-length * (time + 1)) % q] = (
            2 ** (profile[time] + 2 - baseline[time]) * (2 ** (exponent - 1) - 1))
    if coefficients != predicted or min(coefficients) < 0:
        fail("event coefficient identity")
    return {"shift": shift, "A_coefficients": A, "coefficients": coefficients,
            "support": sum(value != 0 for value in coefficients),
            "l1_norm": sum(coefficients)}


def expected_event_corpus() -> dict[str, object]:
    counts = {"coprime_classes": 0, "minimum_rotations": 0,
              "recurrence_steps": 0, "event_coefficients": 0,
              "positive_arc_checks": 0, "signed_arc_checks": 0,
              "integral_fixed_points": 0, "event_support_smaller": 0}
    rows, samples = [], []
    for q in range(1, 9):
        for length in range(q + 1, 2 * q + 1):
            if 2 ** length <= 3 ** q or math.gcd(q, length) != 1:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["coprime_classes"] += 1
                for rotated in minimum_rotations(values):
                    profile_closed, baseline = profile_data(rotated)
                    profile = profile_closed[:-1]
                    event = event_polynomial(rotated, profile, baseline)
                    divisor, B = 2 ** length - 3 ** q, affine_correction(rotated)
                    x0, current = Fraction(B, divisor), Fraction(B + divisor, 2 * divisor)
                    period_sum = power = 0
                    for index, exponent in enumerate(rotated):
                        correction = 2 ** (exponent - 1) - 1
                        period_sum += correction * 2 ** power * 3 ** (q - 1 - index)
                        current = (3 * current + correction) / 2 ** exponent
                        power += exponent
                    if current != (x0 + 1) / 2 or divisor * (x0 + 1) / 2 != period_sum:
                        fail("shifted positive recurrence")
                    residue_profile = [-1] * q
                    for time, value in enumerate(profile):
                        residue_profile[(-length * time) % q] = value
                    signed = reduced_polynomial(residue_profile)
                    positive_arc, signed_arc = sparse_arc(event["coefficients"], q, length), sparse_arc(signed, q, length)
                    if positive_arc["integer_R"] <= 0 or signed_arc["integer_R"] == 0:
                        fail("event arc nonvanishing")
                    if divisor > 1:
                        gamma = slope_root(q, length, divisor)
                        A_value = sum(value * pow(gamma, residue, divisor)
                                      for residue, value in enumerate(event["A_coefficients"])) % divisor
                        P_value = sum(value * pow(gamma, residue, divisor)
                                      for residue, value in enumerate(event["coefficients"])) % divisor
                        if (A_value == 0) != (P_value == 0) or (A_value == 0) != (B % divisor == 0):
                            fail("event modular equivalence")
                    integral = B % divisor == 0
                    counts["minimum_rotations"] += 1
                    counts["recurrence_steps"] += q
                    counts["event_coefficients"] += event["support"]
                    counts["positive_arc_checks"] += 1
                    counts["signed_arc_checks"] += 1
                    counts["integral_fixed_points"] += int(integral)
                    counts["event_support_smaller"] += int(event["support"] < signed_arc["support_count"])
                    row = [q, length, list(rotated), list(profile), event,
                           positive_arc["support_count"], positive_arc["lift_width"],
                           str(positive_arc["integer_R"]), signed_arc["support_count"],
                           signed_arc["lift_width"], str(signed_arc["integer_R"]), int(integral)]
                    rows.append(row)
                    if len(samples) < 10:
                        samples.append(row)
    return {"format": "collatz-phase36-event-polynomial-v1", "maximum_q": 8,
            "counts": counts, "row_digest_sha256": stable_hash(rows),
            "samples": samples,
            "scope": "Complete positive-D coprime cyclic exponent corpus through q<=8; formal rational fixed points are not asserted positive integer cycles.",
            "proves_collatz": False}


def expected_scalar() -> dict[str, object]:
    margin = Fraction(19 * CUTOFF, 12) - (5950 + 238 * (44 + 47 * MATVEEV))
    derivative = Fraction(3 * 238 * (MATVEEV + 1), 2 * CUTOFF)
    cutoff = {"Q": CUTOFF, "envelope_constant": 5950,
              "envelope_coefficient": 238, "log2_3_lower": [19, 12],
              "log2_4Q_over_3_upper": 44, "log2_12Q_upper": 47,
              "margin": [str(margin.numerator), str(margin.denominator)],
              "derivative_upper": [str(derivative.numerator), str(derivative.denominator)],
              "derivative_target": [19, 12]}
    low = rebuild_low(229)
    if len(low["survivors"]) != 1:
        fail("area-229 survivor")
    row = low["survivors"][0]
    q, length, area = row["q"], row["L"], 229
    h, components, surplus = row["h"], row["J"], row["Sigma"]
    width, zeroes = row["n"], row["Z"]
    upper_E, forced_rows, first = min(components, h + surplus), [], None
    for exceptional in range(h, upper_E + 1):
        residual_area = area - components + exceptional
        residual_span = min(2 * residual_area, length * residual_area // q + exceptional)
        rhs = ((components + 2 * exceptional) * (width + 1) + 3 * residual_span
               + (width + 3) * (3 + 2 * zeroes + zeroes * (zeroes - 1) // 2))
        margin = rhs - 3 * length
        forced_rows.append([exceptional, residual_area, residual_span, margin])
        if margin >= 0 and first is None:
            first = exceptional
    allowed = [[1], [1, 1], [2, 1]]
    U, R, C = components - 1, 4, len(allowed)
    capacity = U * (width + R - 1) + 2 * (width + 1) + C * (width + R) * (width + R - 1)
    return {"format": "collatz-phase36-scalar-audit-v1",
            "area_229_cutoff": cutoff,
            "area_229_gcd": {"strict_upper": [405101, 1539], "integer_maximum": 263},
            "area_229_frontier": rebuild_frontier(263), "area_229_low_q": low,
            "forced_exceptional_rows": forced_rows, "forced_exceptional_value": first,
            "baseline_spine_excess": sum(level * q // (length - q) for level in range(h)),
            "allowed_root_profiles": allowed,
            "root_capacity": {"U_max": U, "R": R, "C": C, "rhs": capacity,
                              "two_L": 2 * length, "margin": capacity - 2 * length},
            "accepted_consequence": "critical reduced-profile area A>=230",
            "next_area_230_low_q_diagnostic": rebuild_low(230)["survivors"],
            "proves_collatz": False}


def decoder_intervals(profile: Sequence[int], mechanical: Sequence[int], length: int) -> tuple[tuple[int, int, int, int], ...]:
    if not max(profile, default=0):
        return ()
    answer = []
    for start, end in level_intervals(tuple(profile) + (0,))[0]:
        if start == 0:
            fail("decoder root starts at zero")
        answer.append((start, end, mechanical[start - 1] + 1,
                       mechanical[end] if end < len(mechanical) else length))
    return tuple(answer)


def expected_decoder() -> dict[str, object]:
    counts = {"words": 0, "nonzero_profiles": 0, "mirror_intervals": 0,
              "localized_changed_positions": 0, "naive_cycle_interval_failures": 0}
    digest, first, samples = hashlib.sha256(), None, []
    for q in range(1, 19):
        length = critical_length(q)
        mechanical = tuple(critical_length(j) - 1 for j in range(q))
        inverse = pow(3 ** q, -1, 2 ** length)
        for positions in safe_positions(q):
            source = (-sum(3 ** (q - 1 - j) * 2 ** positions[j] for j in range(q))
                      * inverse) % (2 ** length)
            profile = reconstruct_profile(q, source)
            expected = tuple(mechanical[j] - positions[j] for j in range(q))
            if profile != expected:
                fail("decoder profile")
            intervals = decoder_intervals(profile, mechanical, length)
            covered = {position for _, _, left, right in intervals for position in range(left, right)}
            changed = set(mechanical) ^ set(positions)
            if not changed <= covered:
                fail("decoder mirror localization")
            naive = () if not max(profile, default=0) else tuple(
                (start, end, mechanical[start], mechanical[end] if end < q else length)
                for start, end in level_intervals(profile + (0,))[0])
            naive_covered = {position for _, _, left, right in naive for position in range(left, right)}
            naive_failure = not changed <= naive_covered
            if naive_failure and first is None:
                first = {"q": q, "K": length, "positions": list(positions),
                         "profile": list(profile), "changed_positions": sorted(changed),
                         "naive_intervals": [list(row) for row in naive],
                         "mirror_intervals": [list(row) for row in intervals]}
            counts["words"] += 1
            counts["nonzero_profiles"] += int(bool(intervals))
            counts["mirror_intervals"] += len(intervals)
            counts["localized_changed_positions"] += len(changed)
            counts["naive_cycle_interval_failures"] += int(naive_failure)
            row = [q, length, list(positions), list(profile), [list(x) for x in intervals],
                   sorted(changed), int(naive_failure)]
            digest.update(json.dumps(row, separators=(",", ":")).encode("ascii") + b"\n")
            if intervals and len(samples) < 10:
                samples.append(row)
    return {"format": "collatz-phase36-decoder-roots-v1", "q_range": [1, 18],
            "counts": counts, "row_digest_sha256": digest.hexdigest(),
            "first_naive_orientation_counterexample": first, "samples": samples,
            "boundary": "Mirror intervals localize the decoded word but do not imply a smaller positive ancestor.",
            "proves_collatz": False}


def expected_theory() -> dict[str, object]:
    return {"format": "collatz-phase36-theory-v1", "claims": CLAIMS,
            "P211": "Cycle profile root intervals localize every binary change; p_cyc and complementary gaps obey T36-A/B.",
            "P212": "For U disjoint roots of span at most R with C legal replacements per context/placement, distinct factors imply the exact one-root-hit inequality.",
            "P213": "No primitive positive cycle profile realizes the exact NG41 area-229 scalar tuple.",
            "P214": "Every critical primitive positive nontrivial integer cycle has reduced-profile area A>=230.",
            "P215": "The shift y=(x+1)/2 gives the positive Mersenne recurrence and exact period divisor identity.",
            "P216": "For coprime slope, (2-X^(2q-L))A_a has nonnegative event coefficients, exact support, norm, and modular equivalence.",
            "P217": "P147 applied to the positive event polynomial gives the exact critical/noncritical event-arc inequalities.",
            "P218": "For P206's oppositely oriented decoder profile, mirror root intervals [f_(u-1)+1,f_v) localize every binary change.",
            "NG42": "Directly reusing cycle root intervals [f_u,f_v) for the P206 decoder is refuted at q=3.",
            "what_this_result_does_not_prove": "No uniform root/event dichotomy, arbitrary-area cycle exclusion, decoder-to-ancestor theorem, or Collatz proof is obtained.",
            "proves_collatz": False}


def expected_regressions() -> dict[str, object]:
    return {"format": "collatz-phase36-regressions-v1",
            "mandatory_families": ["2^m-1", "8^m-5", "(110|111)^*",
                                   "A=11101", "B=1100", "A^rB^s"],
            "cycle_controls": ["trivial cycle and powers", "both negative cycles",
                               "NG34-NG42", "Phase 28 synthetic profiles"],
            "decoder_controls": ["source 167", "E49 complete image", "NG24-NG31"],
            "boundaries": ["cycle and decoder profile orientations are distinct",
                           "formal rational fixed points are not positive integral cycles",
                           "positive event support is coprime-slope only"],
            "proves_collatz": False}


def verify(artifact_dir: Path) -> dict[str, object]:
    theory, roots, events = (load(artifact_dir / name) for name in FILES[:3])
    scalar, decoder, regressions = (load(artifact_dir / name) for name in FILES[3:6])
    report = (artifact_dir / FILES[6]).read_text(encoding="utf-8")
    if theory != expected_theory():
        fail("theory artifact mismatch")
    if not isinstance(roots, dict) or roots.get("format") != "collatz-phase36-root-corpus-v1" or roots.get("proves_collatz") is not False:
        fail("root corpus boundary mismatch")
    if not isinstance(events, dict) or events.get("format") != "collatz-phase36-event-polynomial-v1" or events.get("proves_collatz") is not False:
        fail("event corpus boundary mismatch")
    if not isinstance(scalar, dict) or scalar.get("format") != "collatz-phase36-scalar-audit-v1" or scalar.get("proves_collatz") is not False:
        fail("scalar boundary mismatch")
    if not isinstance(decoder, dict) or decoder.get("format") != "collatz-phase36-decoder-roots-v1" or decoder.get("proves_collatz") is not False:
        fail("decoder boundary mismatch")
    if regressions != expected_regressions():
        fail("regression artifact mismatch")
    if "proves_collatz=false" not in report or "A>=230" not in report or "NG42" not in report:
        fail("obstruction report boundary")
    if roots != expected_root_corpus():
        fail("root corpus reconstruction mismatch")
    if events != expected_event_corpus():
        fail("event corpus reconstruction mismatch")
    rebuilt_scalar = expected_scalar()
    stored_prefix = scalar["area_229_frontier"].get("continued_fraction_prefix")
    rebuilt_prefix = rebuilt_scalar["area_229_frontier"].get("continued_fraction_prefix")
    if not isinstance(stored_prefix, list) or stored_prefix != rebuilt_prefix[:len(stored_prefix)]:
        fail("scalar logarithm enclosure mismatch")
    rebuilt_scalar["area_229_frontier"]["continued_fraction_prefix"] = stored_prefix
    if scalar != rebuilt_scalar:
        fail("scalar reconstruction mismatch")
    if decoder != expected_decoder():
        fail("decoder reconstruction mismatch")
    forbidden = "phase36_" + "search"
    if forbidden in Path(__file__).read_text(encoding="utf-8"):
        fail("generator reference")
    return {"valid": True, "claims": CLAIMS, "generator_imported": False,
            "root_classes": roots["counts"]["cyclic_classes"],
            "event_classes": events["counts"]["coprime_classes"],
            "area229_frontier_candidates": scalar["area_229_frontier"]["candidate_count"],
            "area229_root_margin": scalar["root_capacity"]["margin"],
            "low_q_rows": scalar["area_229_low_q"]["counts"]["q_rows"],
            "decoded_words": decoder["counts"]["words"],
            "verified_sha256": {name: file_digest(artifact_dir / name) for name in FILES},
            "proves_collatz": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (VerificationError, KeyError, TypeError, ValueError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}))
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
