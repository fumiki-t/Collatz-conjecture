#!/usr/bin/env python3
"""Generate exact Phase 36 root/event-polynomial evidence.

The supplied note is treated as untrusted.  Cycle-root localization is kept
separate from the oppositely oriented P206 decoder profile; a corrected mirror
interval is generated for the latter.
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

try:
    from phase22_search import slope_root
    from phase24_search import reduced_polynomial, sparse_arc_certificate
    from phase26_search import (affine_correction, compositions, cyclic_class,
                                cyclic_factors, expanded_word, minimum_rotations,
                                primitive)
    from phase28_search import level_intervals, transport_data
    from phase35_search import (critical_length, cutoff_certificate,
                                decode_profile, frontier_audit,
                                joint_low_q_audit, safe_position_lists)
except ModuleNotFoundError:
    from src.phase22_search import slope_root
    from src.phase24_search import reduced_polynomial, sparse_arc_certificate
    from src.phase26_search import (affine_correction, compositions, cyclic_class,
                                    cyclic_factors, expanded_word, minimum_rotations,
                                    primitive)
    from src.phase28_search import level_intervals, transport_data
    from src.phase35_search import (critical_length, cutoff_certificate,
                                    decode_profile, frontier_audit,
                                    joint_low_q_audit, safe_position_lists)


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 8
EXPECTED_CLAIMS = {
    "P211": "VERIFIED_THEOREM", "P212": "VERIFIED_THEOREM",
    "P213": "VERIFIED_THEOREM", "P214": "VERIFIED_THEOREM",
    "P215": "VERIFIED_THEOREM", "P216": "VERIFIED_THEOREM",
    "P217": "VERIFIED_THEOREM", "P218": "VERIFIED_THEOREM",
    "E51": "VERIFIED_FINITE", "E52": "VERIFIED_FINITE",
    "NG42": "REFUTED", "H89": "OPEN", "H133": "OPEN", "H172": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True,
                                     separators=(",", ":")).encode("ascii")).hexdigest()


def boundaries(exponents: Sequence[int]) -> tuple[int, ...]:
    result = [0]
    for exponent in exponents:
        result.append(result[-1] + exponent)
    return tuple(result)


def cyclic_window(word: str, start: int, width: int) -> str:
    return "".join(word[(start + offset) % len(word)] for offset in range(width))


def cycle_root_intervals(profile: Sequence[int], base: Sequence[int]) -> tuple[tuple[int, int, int, int], ...]:
    if len(profile) != len(base) + 1:
        raise ValueError("profile/base lengths")
    if max(profile[:-1], default=0) == 0:
        return ()
    base_boundaries = boundaries(base)
    return tuple((start, end, base_boundaries[start], base_boundaries[end])
                 for start, end in level_intervals(profile)[0])


def complement_gaps(intervals: Sequence[tuple[int, int, int, int]], length: int) -> tuple[int, ...]:
    if not intervals:
        return (length,)
    answer = []
    for index, (_, _, _, right) in enumerate(intervals):
        following = intervals[(index + 1) % len(intervals)][2]
        if index + 1 == len(intervals):
            following += length
        answer.append(following - right)
    return tuple(answer)


def root_geometry_row(exponents: Sequence[int]) -> dict[str, object]:
    item = transport_data(exponents, check_intervals=False)
    profile = tuple(item["profile"])
    base = tuple(item["baseline"])
    length = int(item["L"])
    intervals = cycle_root_intervals(profile, base)
    covered = {position for _, _, left, right in intervals for position in range(left, right)}
    actual_word, base_word = expanded_word(exponents), expanded_word(base)
    changed = {index for index, pair in enumerate(zip(actual_word, base_word, strict=True))
               if pair[0] != pair[1]}
    if not changed <= covered:
        raise AssertionError("cycle root localization")
    root_labels = sum(end - start for start, end, _, _ in intervals)
    root_span = sum(right - left for _, _, left, right in intervals)
    if root_span > 2 * root_labels or len(covered) != root_span:
        raise AssertionError("root span/disjointness")
    gaps = complement_gaps(intervals, length)
    rows = []
    distinct_count = 0
    for width in range(1, length + 1):
        p0 = len(cyclic_factors(base_word, width))
        target = len(cyclic_factors(actual_word, width))
        if p0 > width + 1 or target > p0 + root_span + len(intervals) * (width - 1):
            raise AssertionError("root factor bound")
        distinct = target == length
        gap_sum = sum(max(0, gap - width + 1) for gap in gaps)
        if distinct and (gap_sum > width + 1 or max(gaps) > 2 * width):
            raise AssertionError("complement gap bound")
        distinct_count += int(distinct)
        rows.append([width, p0, target, int(distinct), gap_sum])
    return {"q": len(exponents), "L": length, "profile": list(profile),
            "root_intervals": [list(row) for row in intervals],
            "root_count": len(intervals), "root_label_count": root_labels,
            "root_span": root_span, "changed_positions": sorted(changed),
            "complement_gaps": list(gaps), "factor_rows": rows,
            "distinct_factor_widths": distinct_count}


def root_corpus_audit() -> dict[str, object]:
    counts = {"cyclic_classes": 0, "primitive_classes": 0,
              "minimum_rotations": 0, "root_intervals": 0,
              "localized_changed_positions": 0, "factor_width_checks": 0,
              "distinct_factor_checks": 0}
    rows, samples = [], []
    for q in range(1, Q_MAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2 ** length <= 3 ** q:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["cyclic_classes"] += 1
                counts["primitive_classes"] += int(primitive(values))
                for rotated in minimum_rotations(values):
                    row = root_geometry_row(rotated)
                    counts["minimum_rotations"] += 1
                    counts["root_intervals"] += int(row["root_count"])
                    counts["localized_changed_positions"] += len(row["changed_positions"])
                    counts["factor_width_checks"] += int(row["L"])
                    counts["distinct_factor_checks"] += int(row["distinct_factor_widths"])
                    rows.append([list(rotated), row])
                    if row["root_count"] and len(samples) < 10:
                        samples.append([list(rotated), row])
    if (counts["cyclic_classes"], counts["minimum_rotations"],
            counts["factor_width_checks"], counts["distinct_factor_checks"]) != (
            2214, 3101, 45369, 27832):
        raise AssertionError("root corpus regression")
    return {"format": "collatz-phase36-root-corpus-v1", "maximum_q": Q_MAX,
            "counts": counts, "row_digest_sha256": stable_hash(rows),
            "samples": samples,
            "scope": "Complete positive-D cyclic exponent corpus through q<=8 and every cyclic factor width.",
            "proves_collatz": False}


def time_to_residue(q: int, length: int, time_profile: Sequence[int]) -> tuple[int, ...]:
    if math.gcd(q, length) != 1:
        raise ValueError("coprime slope required")
    result = [-1] * q
    for time, value in enumerate(time_profile):
        result[(-length * time) % q] = value
    return tuple(result)


def event_polynomial(exponents: Sequence[int], profile: Sequence[int], base: Sequence[int]) -> dict[str, object]:
    q, length = len(exponents), sum(exponents)
    if math.gcd(q, length) != 1:
        raise ValueError("coprime event polynomial")
    shift = 2 * q - length
    A = [0] * q
    for time, value in enumerate(profile):
        A[(-length * time) % q] = 2 ** value
    coefficients = [0] * q
    for residue, coefficient in enumerate(A):
        coefficients[residue] += 2 * coefficient
        total = residue + shift
        coefficients[total % q] -= coefficient * (2 if total >= q else 1)
    predicted = [0] * q
    for time, exponent in enumerate(exponents):
        coefficient = 2 ** (profile[time] + 2 - base[time]) * (2 ** (exponent - 1) - 1)
        predicted[(-length * (time + 1)) % q] = coefficient
    if coefficients != predicted or min(coefficients) < 0:
        raise AssertionError("positive event coefficients")
    support = sum(value != 0 for value in coefficients)
    norm = sum(coefficients)
    expected_norm = sum(2 ** profile[t] for t in range(q) if base[t] == 2)
    if support != sum(exponent >= 2 for exponent in exponents) or norm != expected_norm:
        raise AssertionError("event support/norm")
    return {"shift": shift, "A_coefficients": A, "coefficients": coefficients,
            "support": support, "l1_norm": norm}


def event_corpus_audit() -> dict[str, object]:
    counts = {"coprime_classes": 0, "minimum_rotations": 0,
              "recurrence_steps": 0, "event_coefficients": 0,
              "positive_arc_checks": 0, "signed_arc_checks": 0,
              "integral_fixed_points": 0, "event_support_smaller": 0}
    rows, samples = [], []
    for q in range(1, Q_MAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2 ** length <= 3 ** q or math.gcd(q, length) != 1:
                continue
            for values in sorted({cyclic_class(row) for row in compositions(length, q)}):
                counts["coprime_classes"] += 1
                for rotated in minimum_rotations(values):
                    data = transport_data(rotated, check_intervals=False)
                    profile = tuple(data["profile"][:-1])
                    base = tuple(data["baseline"])
                    event = event_polynomial(rotated, profile, base)
                    D = 2 ** length - 3 ** q
                    B = affine_correction(rotated)
                    x0 = Fraction(B, D)
                    y0 = (x0 + 1) / 2
                    current = y0
                    period_sum = 0
                    E = 0
                    for index, exponent in enumerate(rotated):
                        correction = 2 ** (exponent - 1) - 1
                        period_sum += correction * 2 ** E * 3 ** (q - 1 - index)
                        current = (3 * current + correction) / 2 ** exponent
                        E += exponent
                    if current != y0 or D * y0 != period_sum:
                        raise AssertionError("positive shifted recurrence")
                    residue_profile = time_to_residue(q, length, profile)
                    signed = reduced_polynomial(residue_profile)
                    positive_arc = sparse_arc_certificate(tuple(event["coefficients"]), q, length)
                    signed_arc = sparse_arc_certificate(signed, q, length)
                    if positive_arc["integer_R"] <= 0 or signed_arc["integer_R"] == 0:
                        raise AssertionError("arc nonvanishing")
                    if D > 1:
                        gamma = slope_root(q, length, D)
                        A_value = sum(coefficient * pow(gamma, residue, D)
                                      for residue, coefficient in enumerate(event["A_coefficients"])) % D
                        P_value = sum(coefficient * pow(gamma, residue, D)
                                      for residue, coefficient in enumerate(event["coefficients"])) % D
                        if (A_value == 0) != (P_value == 0) or (A_value == 0) != (B % D == 0):
                            raise AssertionError("event polynomial modular equivalence")
                    integral = B % D == 0
                    counts["minimum_rotations"] += 1
                    counts["recurrence_steps"] += q
                    counts["event_coefficients"] += int(event["support"])
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
    if counts["coprime_classes"] != 797 or counts["minimum_rotations"] != 797:
        raise AssertionError("event corpus regression")
    return {"format": "collatz-phase36-event-polynomial-v1", "maximum_q": Q_MAX,
            "counts": counts, "row_digest_sha256": stable_hash(rows),
            "samples": samples,
            "scope": "Complete positive-D coprime cyclic exponent corpus through q<=8; formal rational fixed points are not asserted positive integer cycles.",
            "proves_collatz": False}


def actual_t35c_margin(q: int, length: int, area: int, components: int,
                       exceptional: int, width: int, zeroes: int) -> tuple[int, int, int]:
    residual_area = area - components + exceptional
    residual_span = min(2 * residual_area, length * residual_area // q + exceptional)
    rhs = ((components + 2 * exceptional) * (width + 1) + 3 * residual_span
           + (width + 3) * (3 + 2 * zeroes + zeroes * (zeroes - 1) // 2))
    return rhs - 3 * length, residual_area, residual_span


def allowed_height_two_roots() -> list[list[int]]:
    result = []
    for size in (1, 2):
        for mask in range(2 ** size):
            values = tuple(1 + ((mask >> index) & 1) for index in range(size))
            if any(values[index] == 0 for index in range(size)):
                continue
            extended = (0, *values, 0)
            legal = any(all(base[index] + extended[index + 1] - extended[index] >= 1
                            for index in range(size + 1))
                        for base_mask in range(2 ** (size + 1))
                        for base in [tuple(1 + ((base_mask >> index) & 1)
                                           for index in range(size + 1))])
            if legal:
                result.append(list(values))
    return result


def scalar_audit() -> dict[str, object]:
    low = joint_low_q_audit(229)
    if len(low["survivors"]) != 1:
        raise AssertionError("area-229 scalar frontier")
    row = low["survivors"][0]
    q, length, area = row["q"], row["L"], 229
    h, J, sigma, width, zeroes = row["h"], row["J"], row["Sigma"], row["n"], row["Z"]
    upper_E = min(J, h + sigma)
    exceptional_rows = []
    first_passing = None
    for exceptional in range(h, upper_E + 1):
        margin, residual_area, residual_span = actual_t35c_margin(
            q, length, area, J, exceptional, width, zeroes)
        exceptional_rows.append([exceptional, residual_area, residual_span, margin])
        if margin >= 0 and first_passing is None:
            first_passing = exceptional
    if first_passing != upper_E or upper_E != 92:
        raise AssertionError("exceptional equality not forced")
    baseline_excess = sum(level * q // (length - q) for level in range(h))
    root_types = allowed_height_two_roots()
    if baseline_excess != 1 or root_types != [[1], [1, 1], [2, 1]]:
        raise AssertionError("short-root classification")
    root_count_bound, R, C = J - 1, 4, len(root_types)
    one_hit_rhs = (root_count_bound * (width + R - 1) + 2 * (width + 1)
                   + C * (width + R) * (width + R - 1))
    if one_hit_rhs != 6017 or 2 * length != 7294 or not one_hit_rhs < 2 * length:
        raise AssertionError("root obstruction")
    frontier = frontier_audit(263)
    if frontier["candidate_count"] != 1926:
        raise AssertionError("area-229 high frontier")
    next_low = joint_low_q_audit(230)
    return {"format": "collatz-phase36-scalar-audit-v1",
            "area_229_cutoff": cutoff_certificate(),
            "area_229_gcd": {"strict_upper": [405101, 1539], "integer_maximum": 263},
            "area_229_frontier": frontier, "area_229_low_q": low,
            "forced_exceptional_rows": exceptional_rows,
            "forced_exceptional_value": first_passing,
            "baseline_spine_excess": baseline_excess,
            "allowed_root_profiles": root_types,
            "root_capacity": {"U_max": root_count_bound, "R": R, "C": C,
                              "rhs": one_hit_rhs, "two_L": 2 * length,
                              "margin": one_hit_rhs - 2 * length},
            "accepted_consequence": "critical reduced-profile area A>=230",
            "next_area_230_low_q_diagnostic": next_low["survivors"],
            "proves_collatz": False}


def decoder_mirror_intervals(profile: Sequence[int], mechanical: Sequence[int],
                             length: int) -> tuple[tuple[int, int, int, int], ...]:
    closed = tuple(profile) + (0,)
    if max(profile, default=0) == 0:
        return ()
    answer = []
    for start, end in level_intervals(closed)[0]:
        if start == 0:
            raise AssertionError("decoder profile must start at zero")
        right = mechanical[end] if end < len(mechanical) else length
        answer.append((start, end, mechanical[start - 1] + 1, right))
    return tuple(answer)


def decoder_root_audit() -> dict[str, object]:
    counts = {"words": 0, "nonzero_profiles": 0, "mirror_intervals": 0,
              "localized_changed_positions": 0, "naive_cycle_interval_failures": 0}
    digest = hashlib.sha256()
    first_failure = None
    samples = []
    for q in range(1, 19):
        length = critical_length(q)
        mechanical = tuple(critical_length(j) - 1 for j in range(q))
        for positions in safe_position_lists(q):
            expected = tuple(mechanical[j] - positions[j] for j in range(q))
            profile = decode_profile(q, (-sum(3 ** (q - 1 - j) * 2 ** positions[j]
                                                    for j in range(q))
                                         * pow(3 ** q, -1, 2 ** length)) % (2 ** length))
            if profile != expected:
                raise AssertionError("decoder/profile attachment")
            intervals = decoder_mirror_intervals(profile, mechanical, length)
            covered = {position for _, _, left, right in intervals for position in range(left, right)}
            changed = set(mechanical) ^ set(positions)
            if not changed <= covered:
                raise AssertionError("decoder mirror localization")
            closed = profile + (0,)
            naive = () if max(profile, default=0) == 0 else tuple(
                (start, end, mechanical[start], mechanical[end] if end < q else length)
                for start, end in level_intervals(closed)[0])
            naive_covered = {position for _, _, left, right in naive for position in range(left, right)}
            naive_failure = not changed <= naive_covered
            if naive_failure and first_failure is None:
                first_failure = {"q": q, "K": length, "positions": list(positions),
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
    if counts["words"] != 1_166_058 or first_failure is None or first_failure["q"] != 3:
        raise AssertionError("decoder mirror corpus")
    return {"format": "collatz-phase36-decoder-roots-v1", "q_range": [1, 18],
            "counts": counts, "row_digest_sha256": digest.hexdigest(),
            "first_naive_orientation_counterexample": first_failure,
            "samples": samples,
            "boundary": "Mirror intervals localize the decoded word but do not imply a smaller positive ancestor.",
            "proves_collatz": False}


def theory() -> dict[str, object]:
    return {"format": "collatz-phase36-theory-v1", "claims": EXPECTED_CLAIMS,
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


def regressions() -> dict[str, object]:
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


def obstruction_markdown(decoder: dict[str, object], scalar: dict[str, object]) -> str:
    failure = decoder["first_naive_orientation_counterexample"]
    return f"""# Phase 36 obstruction report

The proposed cycle-root localization is valid for reduced cycle profiles, but
its direct reuse after P206 has the wrong sign.  At `q={failure['q']}` the safe
positions `{failure['positions']}` decode to profile `{failure['profile']}`.
The changed binary positions are `{failure['changed_positions']}`; the naive
cycle interval `{failure['naive_intervals']}` misses one, while the corrected
mirror interval `{failure['mirror_intervals']}` contains both.  This is NG42.

The exact NG41 area-229 scalar row is removed for a different reason. P208
forces `E=92=h+Sigma`, so every level-one cycle root has label length at most
two and binary span at most four. The only legal height-two root profiles are
`[1]`, `[1,1]`, and `[2,1]`. P212 then gives `{scalar['root_capacity']['rhs']}`
against `2L={scalar['root_capacity']['two_L']}`. The complete area-229 frontier
therefore raises the accepted critical floor only to `A>=230`.

## What this result does not prove

It does not close the root-sparse/root-dense dichotomy, exclude arbitrary-area
cycles, turn decoder roots into smaller positive ancestors, close H89/H133/
H172, or prove Collatz. `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    roots = root_corpus_audit()
    events = event_corpus_audit()
    scalar = scalar_audit()
    decoder = decoder_root_audit()
    write_json(args.artifact_dir / "phase36_theory.json", theory())
    write_json(args.artifact_dir / "phase36_root_corpus.json", roots)
    write_json(args.artifact_dir / "phase36_event_polynomial.json", events)
    write_json(args.artifact_dir / "phase36_scalar_audit.json", scalar)
    write_json(args.artifact_dir / "phase36_decoder_roots.json", decoder)
    write_json(args.artifact_dir / "phase36_regressions.json", regressions())
    (args.artifact_dir / "phase36_obstruction_report.md").write_text(
        obstruction_markdown(decoder, scalar), encoding="utf-8")
    print(json.dumps({"valid": True, "claims": EXPECTED_CLAIMS,
                      "root_counts": roots["counts"], "event_counts": events["counts"],
                      "area229_frontier": scalar["area_229_frontier"]["candidate_count"],
                      "area229_root_margin": scalar["root_capacity"]["margin"],
                      "decoder_words": decoder["counts"]["words"],
                      "proves_collatz": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
