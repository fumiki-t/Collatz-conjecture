#!/usr/bin/env python3
"""Generate exact Phase 23 defect-area evidence.

The Phase 23 note is an untrusted proposal.  This generator accepts only the
boundary-correct critical-word and positive-cycle statements documented in the
audit.  All acceptance decisions use integers; no floating point is used.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from collections.abc import Iterable
from pathlib import Path

try:  # direct script execution
    from phase22_search import (
        affine_correction,
        compositions,
        cyclic_class,
        exponents_of_profile,
        literal_accelerated_cycle,
        minimum_height_rotation,
        profile_of,
        profiles_of_area,
    )
except ModuleNotFoundError:  # pytest/package import
    from src.phase22_search import (
        affine_correction,
        compositions,
        cyclic_class,
        exponents_of_profile,
        literal_accelerated_cycle,
        minimum_height_rotation,
        profile_of,
        profiles_of_area,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


CRITICAL_Q_MAXIMUM = 17
FACTOR_Q_MAXIMUM = 12
CYCLE_COMPOSITION_Q_MAXIMUM = 8
CYCLE_PROFILE_Q_MAXIMUM = 22
CYCLE_AREA_MAXIMUM = 2
V = 300_000
NEGATIVE_Q7 = (1, 1, 1, 2, 1, 1, 4)
A_BITS = "11101"
B_BITS = "1100"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest_rows(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii") + b"\n")
    return digest.hexdigest()


def ceil_div(left: int, right: int) -> int:
    return -(-left // right)


def ceil_log2_fraction(numerator: int, denominator: int) -> int:
    if numerator <= 0 or denominator <= 0:
        raise ValueError("positive fraction required")
    estimate = max(0, numerator.bit_length() - denominator.bit_length())
    while (1 << estimate) * denominator < numerator:
        estimate += 1
    while estimate and (1 << (estimate - 1)) * denominator >= numerator:
        estimate -= 1
    return estimate


def hq_rows(maximum_q: int) -> dict[int, tuple[int, int, int, int, int]]:
    result = {}
    three = 1
    maximum_affine = 0
    for q in range(1, maximum_q + 1):
        maximum_affine = 3 * maximum_affine + (1 << (three.bit_length() - 1))
        three *= 3
        K = three.bit_length()
        D = (1 << K) - three
        height_numerator = 3 * maximum_affine + q * D
        n = ceil_log2_fraction(height_numerator, D)
        lower = max(0, ceil_div(K - 2 * n - 1, n + 2))
        result[q] = maximum_affine, D, K, n, lower
    return result


def critical_prefixes(maximum_q: int):
    """Yield all safe prefixes whose following zero is the first crossing."""
    targets = {pow(3, q).bit_length() - 1: q for q in range(1, maximum_q + 1)}
    frontier = [("", 0, 0)]
    for length in range(1, max(targets) + 1):
        following = []
        for word, odd, affine in frontier:
            if odd and pow(3, odd) > 1 << length:
                following.append((word + "0", odd, affine))
            if odd < maximum_q and pow(3, odd + 1) > 1 << length:
                following.append((word + "1", odd + 1, 3 * affine + (1 << (length - 1))))
        frontier = following
        target_q = targets.get(length)
        if target_q is not None:
            for word, odd, affine in frontier:
                if odd == target_q:
                    yield target_q, word + "0", affine


def mechanical_word(q: int) -> tuple[str, tuple[int, ...]]:
    K = pow(3, q).bit_length()
    positions = tuple(pow(3, j).bit_length() - 1 for j in range(q))
    bits = ["0"] * K
    for position in positions:
        bits[position] = "1"
    return "".join(bits), positions


def prefix_ones(word: str) -> list[int]:
    answer = [0]
    for bit in word:
        answer.append(answer[-1] + (bit == "1"))
    return answer


def defect_data(word: str, q: int) -> tuple[int, int, int, tuple[int, ...]]:
    canonical, canonical_positions = mechanical_word(q)
    positions = tuple(index for index, bit in enumerate(word) if bit == "1")
    defects = tuple(base - actual for base, actual in zip(canonical_positions, positions, strict=True))
    if any(value < 0 for value in defects):
        raise AssertionError("critical position dominance")
    area = sum(defects)
    left, right = prefix_ones(word), prefix_ones(canonical)
    gaps = tuple(left[index] - right[index] for index in range(len(word) + 1))
    if min(gaps) < 0 or sum(gaps) != area:
        raise AssertionError("prefix area identity")
    swap_distance = sum(abs(left[index] - right[index]) for index in range(len(word) + 1))
    if swap_distance != area:
        raise AssertionError("adjacent swap distance")
    return area, sum(value > 0 for value in gaps), sum(value == 0 for value in gaps), defects


def factors(word: str, width: int) -> set[str]:
    return {word[start : start + width] for start in range(len(word) - width + 1)}


def p132_rejected(word: str, b_max: int, D: int) -> bool:
    """Direct P132 check on the K_q-1 safe prefix."""
    word = word[:-1]
    counts = prefix_ones(word)
    length = len(word)
    table = [[0] * (length + 1) for _ in range(length + 1)]
    for left in range(length - 1, -1, -1):
        for right in range(length - 1, left, -1):
            if word[left] == word[right]:
                table[left][right] = 1 + table[left + 1][right + 1]
    for later in range(1, length):
        width = max(table[earlier][later] for earlier in range(later))
        if width:
            odd = counts[later]
            if (1 << (width + odd)) * D >= (b_max + D) * pow(3, odd):
                return True
    return False


def source_for(word: str, affine: int) -> int:
    q = word.count("1")
    modulus = 1 << len(word)
    source = (-affine * pow(pow(3, q), -1, modulus)) % modulus
    return source or modulus


def shortcut_trace(source: int, length: int) -> tuple[str, list[int]]:
    word = []
    states = [source]
    current = source
    for _ in range(length):
        word.append("1" if current & 1 else "0")
        current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2
        states.append(current)
    return "".join(word), states


def critical_audit() -> dict[str, object]:
    heights = hq_rows(CRITICAL_Q_MAXIMUM)
    counts = {
        q: {
            "critical_words": 0,
            "area_sum": 0,
            "minimum_area": None,
            "maximum_area": 0,
            "area_lower_bound": heights[q][4],
            "area_rejected": 0,
            "bounded_source_rows": 0,
            "contact_height_checks": 0,
            "factor_width_checks": 0,
            "p132_rejected": 0 if q <= FACTOR_Q_MAXIMUM else None,
            "union_rejected": 0 if q <= FACTOR_Q_MAXIMUM else None,
            "phase23_only": 0 if q <= FACTOR_Q_MAXIMUM else None,
            "phase21_only": 0 if q <= FACTOR_Q_MAXIMUM else None,
        }
        for q in range(1, CRITICAL_Q_MAXIMUM + 1)
    }
    digest_input = []
    factor_maximum_ratio = (0, 1, None)
    for q, word, affine in critical_prefixes(CRITICAL_Q_MAXIMUM):
        b_max, D, K, n, lower = heights[q]
        if len(word) != K or pow(3, q) >= 1 << K:
            raise AssertionError("critical crossing length")
        area, noncontacts, contacts, defects = defect_data(word, q)
        row = counts[q]
        row["critical_words"] += 1
        row["area_sum"] += area
        row["minimum_area"] = area if row["minimum_area"] is None else min(row["minimum_area"], area)
        row["maximum_area"] = max(row["maximum_area"], area)
        area_rejected = area < lower
        row["area_rejected"] += area_rejected

        source = source_for(word, affine)
        if source * D <= b_max:
            literal, states = shortcut_trace(source, K)
            if literal != word:
                raise AssertionError("critical source cylinder")
            row["bounded_source_rows"] += 1
            mechanical, _ = mechanical_word(q)
            gaps = [left - right for left, right in zip(prefix_ones(word), prefix_ones(mechanical), strict=True)]
            for start in range(K):
                if gaps[start] == 0:
                    if not (states[start] * D < 3 * b_max + q * D):
                        raise AssertionError("contact height")
                    row["contact_height_checks"] += 1

        phase21 = False
        if q <= FACTOR_Q_MAXIMUM:
            canonical, _ = mechanical_word(q)
            for width in range(1, K + 1):
                actual_count = len(factors(word, width))
                base_count = len(factors(canonical, width))
                corrected_bound = (area + 1) * (width + 1) + 1
                if base_count > width + 2 or actual_count > corrected_bound:
                    raise AssertionError(
                        f"linear factor perturbation q={q} word={word} width={width} "
                        f"area={area} base={base_count} actual={actual_count} bound={corrected_bound}"
                    )
                row["factor_width_checks"] += 1
                ratio = (actual_count, corrected_bound, [q, word, width])
                if ratio[0] * factor_maximum_ratio[1] > factor_maximum_ratio[0] * ratio[1]:
                    factor_maximum_ratio = ratio
            phase21 = p132_rejected(word, b_max, D)
            row["p132_rejected"] += phase21
            row["union_rejected"] += area_rejected or phase21
            row["phase23_only"] += area_rejected and not phase21
            row["phase21_only"] += phase21 and not area_rejected

        digest_input.append([q, word, affine, source, area, noncontacts, contacts, list(defects), n, lower, int(area_rejected), int(phase21)])

    totals = {
        "critical_words": sum(row["critical_words"] for row in counts.values()),
        "area_rejected": sum(row["area_rejected"] for row in counts.values()),
        "bounded_source_rows": sum(row["bounded_source_rows"] for row in counts.values()),
        "contact_height_checks": sum(row["contact_height_checks"] for row in counts.values()),
        "factor_width_checks": sum(row["factor_width_checks"] for row in counts.values()),
        "p132_rejected_through_q12": sum(row["p132_rejected"] or 0 for row in counts.values()),
        "union_rejected_through_q12": sum(row["union_rejected"] or 0 for row in counts.values()),
    }
    return {
        "format": "collatz-phase23-critical-v1",
        "maximum_q": CRITICAL_Q_MAXIMUM,
        "factor_direct_maximum_q": FACTOR_Q_MAXIMUM,
        "counts_by_q": {str(q): row for q, row in counts.items()},
        "totals": totals,
        "maximum_factor_bound_ratio": {
            "numerator": factor_maximum_ratio[0],
            "denominator": factor_maximum_ratio[1],
            "witness": factor_maximum_ratio[2],
        },
        "row_digest_sha256": digest_rows(digest_input),
        "finite_boundary": "Complete through q<=17 for area/contact aggregates; literal factor and P132 comparison complete through q<=12 only.",
        "proves_collatz": False,
    }


def expanded_word(exponents: tuple[int, ...]) -> str:
    return "".join("1" + "0" * (exponent - 1) for exponent in exponents)


def cyclic_factors(word: str, width: int) -> set[str]:
    repetitions = (width + len(word) - 1) // len(word) + 1
    doubled = word * repetitions
    return {doubled[start : start + width] for start in range(len(word))}


def literal_swap_count(base: str, target: str) -> int:
    work = list(base)
    target_positions = [index for index, bit in enumerate(target) if bit == "1"]
    count = 0
    for rank in range(len(target_positions) - 1, -1, -1):
        current_positions = [index for index, bit in enumerate(work) if bit == "1"]
        position = current_positions[rank]
        target_position = target_positions[rank]
        if position > target_position:
            raise AssertionError("profile moved left of Christoffel")
        while position < target_position:
            if work[position : position + 2] != ["1", "0"]:
                raise AssertionError("literal adjacent swap obstruction")
            work[position], work[position + 1] = "0", "1"
            position += 1
            count += 1
    if "".join(work) != target:
        raise AssertionError("literal swap reconstruction")
    return count


def primitive(values: tuple[int, ...]) -> bool:
    return all(values != values[:period] * (len(values) // period) for period in range(1, len(values)) if len(values) % period == 0)


def cycle_profile_audit() -> dict[str, object]:
    digest_input = []
    area_counts = {str(area): 0 for area in range(CYCLE_AREA_MAXIMUM + 1)}
    factor_checks = triangular_checks = 0
    largest_complexity_ratio = (0, 1, None)
    for q in range(1, CYCLE_PROFILE_Q_MAXIMUM + 1):
        for L in range(q + 1, 2 * q + 1):
            if pow(2, L) <= pow(3, q) or math.gcd(q, L) != 1:
                continue
            baseline = exponents_of_profile(q, L, (0,) * q)
            if baseline is None:
                raise AssertionError("Christoffel baseline")
            base_word = expanded_word(baseline)
            for area in range(CYCLE_AREA_MAXIMUM + 1):
                for profile in profiles_of_area(q, area):
                    exponents = exponents_of_profile(q, L, profile)
                    if exponents is None:
                        continue
                    word = expanded_word(exponents)
                    swaps = literal_swap_count(base_word, word)
                    if swaps != area:
                        raise AssertionError("cycle area/edit identity")
                    height = max(profile)
                    if 2 * area < height * (height + 1):
                        raise AssertionError("triangular height bound")
                    triangular_checks += 1
                    local_max = 0
                    for width in range(1, L + 1):
                        base_count = len(cyclic_factors(base_word, width))
                        actual_count = len(cyclic_factors(word, width))
                        if base_count > width + 1 or actual_count > (area + 1) * (width + 1):
                            raise AssertionError("cyclic factor bound")
                        local_max = max(local_max, actual_count)
                        factor_checks += 1
                        ratio = (actual_count, (area + 1) * (width + 1), [q, L, list(profile), width])
                        if ratio[0] * largest_complexity_ratio[1] > largest_complexity_ratio[0] * ratio[1]:
                            largest_complexity_ratio = ratio
                    area_counts[str(area)] += 1
                    digest_input.append([q, L, list(profile), list(exponents), area, height, swaps, local_max])

    full_classes = integral_classes = primitive_positive = separation_checks = 0
    integral_rows = []
    for q in range(1, CYCLE_COMPOSITION_Q_MAXIMUM + 1):
        for L in range(q + 1, 2 * q + 1):
            D = pow(2, L) - pow(3, q)
            if D <= 0:
                continue
            classes = sorted({cyclic_class(values) for values in compositions(L, q)})
            full_classes += len(classes)
            for values in classes:
                canonical = minimum_height_rotation(values)
                B = affine_correction(canonical)
                if B % D:
                    continue
                integral_classes += 1
                source = B // D
                legal, trace = literal_accelerated_cycle(source, canonical)
                if not legal:
                    raise AssertionError("integral cycle legality")
                row = [q, L, list(canonical), source, primitive(canonical), trace]
                integral_rows.append(row)
                if source <= 0 or not primitive(canonical) or math.gcd(q, L) != 1:
                    continue
                primitive_positive += 1
                profile = profile_of(canonical)
                area, height = sum(profile), max(profile)
                numerator = (1 << (height + 2 + L)) * source
                n_cyc = ceil_log2_fraction(numerator, pow(3, q))
                if L > (area + 1) * (n_cyc + 1):
                    raise AssertionError("positive cycle factor separation")
                separation_checks += 1
    return {
        "format": "collatz-phase23-cycle-v1",
        "profile_maximum_q": CYCLE_PROFILE_Q_MAXIMUM,
        "profile_maximum_area": CYCLE_AREA_MAXIMUM,
        "area_counts": area_counts,
        "profile_count": sum(area_counts.values()),
        "triangular_checks": triangular_checks,
        "cyclic_factor_width_checks": factor_checks,
        "largest_complexity_bound_ratio": {
            "numerator": largest_complexity_ratio[0], "denominator": largest_complexity_ratio[1], "witness": largest_complexity_ratio[2]
        },
        "profile_digest_sha256": digest_rows(sorted(digest_input)),
        "full_composition_q_maximum": CYCLE_COMPOSITION_Q_MAXIMUM,
        "full_cyclic_classes": full_classes,
        "integral_classes": integral_classes,
        "primitive_positive_coprime_classes": primitive_positive,
        "factor_separation_checks": separation_checks,
        "integral_rows": integral_rows,
        "finite_boundary": "The q<=22 profile audit is exhaustive only for area<=2; the full composition audit ends at q<=8.",
        "proves_collatz": False,
    }


def orbit_word(source: int, length: int) -> str:
    return shortcut_trace(source, length)[0]


def regressions_artifact() -> dict[str, object]:
    words = []
    for m in range(3, 9):
        words.append(["2^m-1", m, orbit_word((1 << m) - 1, 64)])
        words.append(["8^m-5", m, orbit_word(pow(8, m) - 5, 64)])
    for r in range(1, 5):
        for s in range(1, 5):
            words.append(["A^rB^s", r, s, A_BITS * r + B_BITS * s])
    words.extend([
        ["A=11101", A_BITS], ["B=1100", B_BITS],
        ["(110|111)^*", "110111" * 16],
        ["source167", orbit_word(167, 96)],
        ["all-contact-q17", mechanical_word(17)[0]],
    ])
    cycles = []
    for source, exponents in ((1, (2,)), (-5, (1, 2)), (-17, NEGATIVE_Q7)):
        legal, trace = literal_accelerated_cycle(source, exponents)
        cycles.append([source, list(exponents), legal, trace, source > 0])
    return {
        "format": "collatz-phase23-regressions-v1",
        "word_controls": words,
        "word_control_digest_sha256": digest_rows(words),
        "cycle_controls": cycles,
        "required_failed_approaches": [f"NG{index}" for index in range(21, 32)],
        "scope": "Negative cycles audit algebra and boundary rejection only; they are not inputs to positive state-height or factor-separation claims.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase23-theory-v1",
        "claims": {
            "P141": "VERIFIED_THEOREM", "P142": "CONDITIONAL", "P143": "CONDITIONAL",
            "P144": "VERIFIED_THEOREM", "P145": "VERIFIED_THEOREM", "P146": "CONDITIONAL",
            "E35": "VERIFIED_FINITE", "NG32": "REFUTED", "H141": "OPEN",
        },
        "critical_area": {
            "identity": "A=sum_j(f_j-d_j)=sum_(0<=t<=K)(h_w(t)-h_c(t))",
            "swap_orientation": "The critical word is obtained from c_q by A swaps 01->10.",
            "factor_bound": "p_w(n)<=(A+1)(n+1)+1 for 1<=n<=K.",
            "factor_proof": "The infinite mechanical prefix has at most n+1 factors; changing its final 1 to the finite critical word's final 0 adds at most one terminal factor. Each internal adjacent swap adds factors at at most n+1 starts.",
            "sharp_proposal_refuted": "NG32: q=4, c_q=1101100, n=2, A=0 has four factors {00,01,10,11}, exceeding n+1=3.",
        },
        "critical_repetition": {
            "height": "At a contact start t, x_t<3N+q; under P54, x_t<3H_q+q.",
            "integer_width": "n_q=min{n:2^n D_q>=3B_q_max+qD_q}.",
            "necessary": "For pairwise-distinct critical states, K_q<=A(w)(n_q+2)+2n_q+1.",
            "scope": "P54 finite-first-crossing, nonperiodic/distinct-state branch only.",
        },
        "conditional_critical": {
            "statement": "If H_q<=C q^mu effectively for all large q, then A(w)>=(log_2(3)/mu+o(1))q/log_2(q).",
            "q0": "The Phase 7 contact count would give a second exact area lower bound once an exact integer n_q0 is certified; this phase does not manufacture that missing bound.",
        },
        "cycle_area": {
            "identity": "For a valid coprime residue profile a, sum a_r is the literal expanded-word adjacent-swap distance from the profile-zero Christoffel representative.",
            "triangular": "A>=h(h+1)/2 because the time-ordered profile can decrease by at most one at a wrap transition.",
            "factor_bound": "p_cyc(n)<=(A+1)(n+1).",
        },
        "cycle_separation": {
            "height": "For a primitive positive integer cycle, M<2^(h+2)m/lambda.",
            "necessary": "With n_cyc=ceil(log_2(2^(h+2)m/lambda)), L<=(A+1)(n_cyc+1).",
            "scope": "Primitive positive integer cycle with gcd(L,q)=1; not a negative cycle or rational noninteger shadow.",
        },
        "conditional_cycle": {
            "statement": "An effective m<=C q^mu for all large coprime positive cycles implies A=Omega(q^(2/3)).",
            "dependencies": "P145 plus the exact cycle product bound; no such polynomial minimum theorem is accepted here.",
        },
        "literature_boundary": "Mechanical/Christoffel terminology is contextual. All accepted Phase 23 identities are derived in the repository; no new external theorem is promoted. EXT15 and EXT16 retain their Phase 22 scopes only.",
        "proves_collatz": False,
    }


def obstruction_markdown(critical: dict[str, object], cycle: dict[str, object]) -> str:
    return f"""# Phase 23 obstruction report

## Exact finite audit

- critical first-crossing words through `q<={critical['maximum_q']}`: `{critical['totals']['critical_words']}`;
- area-only rejections in that range: `{critical['totals']['area_rejected']}`;
- direct factor-width checks through `q<={critical['factor_direct_maximum_q']}`: `{critical['totals']['factor_width_checks']}`;
- bounded coprime cycle profiles: `{cycle['profile_count']}`;
- cyclic factor-width checks: `{cycle['cyclic_factor_width_checks']}`.

These are exact bounded computations.  They do not imply an eventual area
lower bound beyond the proved conditional inequalities.

## Proposal repairs

1. The critical repetition certificate explicitly retains P54 and pairwise
   state distinctness.  It is not applied to a periodic branch.
2. The cycle edit identity is proved only after converting the residue-indexed
   Phase 22 profile back to time order and then to the literal expanded word.
3. The cycle height/separation result is restricted to primitive positive
   integer cycles.  Rational noninteger fixed points and both stored negative
   cycles are regression controls, not theorem inputs.
4. No exact `n_q0` was certified from the existing Phase 7 symbolic inputs.
   The proposed giant q0 area number therefore remains conditional rather than
   being replaced by floating-point logarithms.
5. The suggested Wu--Wang/polynomial-height and polynomial cycle-minimum inputs
   were not accepted.  P143 and P146 preserve them as explicit hypotheses.

## Remaining obstruction

Area may be concentrated in a small number of deep excursions.  Neither the
linear factor bound nor the triangular height bound forces the correction sum
to be small.  H141 is the exact missing optimization/ordinary-source bridge;
H89 and H133 remain open.

## What this result does not prove

It does not prove the q0 candidate impossible, exclude every nontrivial cycle,
prove H89, H133, H112, H72, or prove the Collatz conjecture.
`proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    theory = theory_artifact()
    critical = critical_audit()
    cycle = cycle_profile_audit()
    regressions = regressions_artifact()
    write_json(args.artifact_dir / "phase23_theory.json", theory)
    write_json(args.artifact_dir / "phase23_critical_words.json", critical)
    write_json(args.artifact_dir / "phase23_cycle_profiles.json", cycle)
    write_json(args.artifact_dir / "phase23_regressions.json", regressions)
    (args.artifact_dir / "phase23_obstruction_report.md").write_text(obstruction_markdown(critical, cycle), encoding="utf-8")
    print(json.dumps({
        "valid": True,
        "critical_words": critical["totals"]["critical_words"],
        "cycle_profiles": cycle["profile_count"],
        "proves_collatz": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
