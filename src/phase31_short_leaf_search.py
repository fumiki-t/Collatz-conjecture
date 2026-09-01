#!/usr/bin/env python3
"""Generate exact Phase 31 short-leaf pruning evidence.

The supplied v2 note is treated as an untrusted proposal.  The finite audit
uses integers only.  The H89 Hamming-shell proposal is deliberately outside
this experiment and is not promoted by this program.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Sequence

try:
    from phase26_search import compositions, cyclic_class, expanded_word, minimum_rotations
    from phase28_search import level_intervals, profile_to_exponents, transport_data
except ModuleNotFoundError:
    from src.phase26_search import compositions, cyclic_class, expanded_word, minimum_rotations
    from src.phase28_search import level_intervals, profile_to_exponents, transport_data


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


Q_MAX = 9
R_VALUES = (1, 2, 3)
EXPECTED_CLAIMS = {
    "P191": "VERIFIED_THEOREM",
    "P192": "VERIFIED_THEOREM",
    "P193": "VERIFIED_THEOREM",
    "P194": "VERIFIED_THEOREM",
    "E44": "VERIFIED_FINITE",
    "H172": "OPEN",
    "H133": "OPEN",
    "H89": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def boundaries(exponents: Sequence[int]) -> tuple[int, ...]:
    values = [0]
    for exponent in exponents:
        values.append(values[-1] + exponent)
    return tuple(values)


def components(profile: Sequence[int]) -> tuple[tuple[int, int, int], ...]:
    return tuple(
        (level, start, end)
        for level, intervals in enumerate(level_intervals(profile), start=1)
        for start, end in intervals
    )


def window(word: str, start: int, width: int) -> str:
    return "".join(word[(start + offset) % len(word)] for offset in range(width))


def factor_set(word: str, width: int) -> set[str]:
    return {window(word, start, width) for start in range(len(word))}


def segment_affected(length: int, left: int, right: int, width: int) -> set[int]:
    positions = range(left, right)
    return {
        (position - offset) % length
        for position in positions
        for offset in range(width)
    }


def short_leaf_inventory(exponents: Sequence[int], radius: int) -> dict[str, object]:
    if radius < 1:
        raise ValueError("radius")
    item = transport_data(exponents, check_intervals=False)
    original = tuple(int(value) for value in item["profile"])
    base = tuple(int(value) for value in item["baseline"])
    peak = original[:-1].index(max(original[:-1], default=0)) if item["height"] else 0
    current = list(original)
    removed: list[tuple[int, int, int]] = []
    removal_states: list[tuple[int, ...]] = []

    while True:
        candidates = []
        for level, start, end in components(current):
            is_spine = bool(item["height"]) and start <= peak < end
            is_leaf = max(current[start:end], default=0) == level
            if not is_spine and is_leaf and end - start <= radius:
                candidates.append((level, start, end))
        if not candidates:
            break
        chosen = min(candidates, key=lambda row: (-row[0], row[1], row[2]))
        level, start, end = chosen
        before_count = len(components(current))
        removal_states.append(tuple(current))
        for index in range(start, end):
            if current[index] != level:
                raise AssertionError("leaf is not flat")
            current[index] -= 1
        if min(current) < 0 or current[0] or current[-1]:
            raise AssertionError("pruning boundary")
        if len(components(current)) != before_count - 1:
            raise AssertionError("one component per pruning step")
        profile_to_exponents(base, tuple(current))
        removed.append(chosen)

    residual = tuple(current)
    residual_components = components(residual)
    height = int(item["height"])
    J = int(item["J"])
    sigma = int(item["descent_slack"])
    E = len(residual_components)
    K = len(removed)
    if K + E != J:
        raise AssertionError("component conservation")

    residual_nonspine = [
        row for row in residual_components
        if not (height and row[1] <= peak < row[2])
    ]
    if any(row[2] - row[1] <= radius for row in residual_nonspine):
        raise AssertionError("short residual leaf survived")
    nonspine_excess = sum(end - start - 1 for _, start, end in residual_nonspine)
    if nonspine_excess > sigma:
        raise AssertionError("slack charging")
    if E > height + sigma // radius:
        raise AssertionError("short-leaf residual bound")

    replay = list(residual)
    for chosen, expected in zip(reversed(removed), reversed(removal_states), strict=True):
        level, start, end = chosen
        for index in range(start, end):
            replay[index] += 1
        if tuple(replay) != expected:
            raise AssertionError("profile reconstruction")
    if tuple(replay) != original:
        raise AssertionError("profile reconstruction final")

    base_boundaries = boundaries(base)
    residual_exponents = profile_to_exponents(base, residual)
    current_word = expanded_word(residual_exponents)
    operations = []
    for level, start_label, end_label in reversed(removed):
        left = base_boundaries[start_label] + level - 1
        right = base_boundaries[end_label] + level - 1
        segment = current_word[left:right]
        span = right - left
        if not segment or segment[0] != "1" or segment[-1] != "0":
            raise AssertionError("rotation endpoints")
        if span > 2 * radius:
            raise AssertionError("short rotation span")
        current_word = current_word[:left] + segment[-1] + segment[:-1] + current_word[right:]
        operations.append((left, right, end_label - start_label, span))
    actual_word = expanded_word(exponents)
    if current_word != actual_word:
        raise AssertionError("word reconstruction")

    residual_span = sum(
        base_boundaries[end] - base_boundaries[start]
        for _, start, end in residual_components
    )
    if residual_span > 2 * int(item["area"]):
        raise AssertionError("residual transport span")
    return {
        "q": int(item["q"]),
        "L": int(item["L"]),
        "area": int(item["area"]),
        "height": height,
        "J": J,
        "sigma": sigma,
        "R": radius,
        "K": K,
        "E": E,
        "nonspine_excess": nonspine_excess,
        "residual_span": residual_span,
        "base_word": expanded_word(base),
        "residual_word": expanded_word(residual_exponents),
        "actual_word": actual_word,
        "operations": tuple(operations),
        "removed": tuple(removed),
        "residual_profile": residual,
    }


def finite_rows(exponents: Sequence[int], radius: int) -> tuple[list[list[int]], dict[str, int]]:
    inventory = short_leaf_inventory(exponents, radius)
    length = int(inventory["L"])
    area = int(inventory["area"])
    E = int(inventory["E"])
    K = int(inventory["K"])
    base_word = str(inventory["base_word"])
    residual_word = str(inventory["residual_word"])
    actual_word = str(inventory["actual_word"])
    operations = tuple(inventory["operations"])
    rows = []
    counts = {"width_pruning_cases": 0, "distinct_factor_cases": 0, "low_type_checks": 0}
    for width in range(1, length + 1):
        context_width = width + 4 * radius
        exceptional = {
            start for start in range(length)
            if window(residual_word, start, context_width) != window(base_word, start, context_width)
        }
        context_bound = 2 * area + E * (context_width - 1)
        if len(exceptional) > min(length, context_bound):
            raise AssertionError("exceptional context bound")
        incidence = [0] * length
        max_influence = width + 2 * radius - 1
        for left, right, _, span in operations:
            affected = segment_affected(length, left, right, width)
            if len(affected) > min(length, width + span - 1) or len(affected) > min(length, max_influence):
                raise AssertionError("short component influence")
            for start in affected:
                incidence[start] += 1
        low_starts = [
            start for start in range(length)
            if start not in exceptional and incidence[start] <= 1
        ]
        low_types = {window(actual_word, start, width) for start in low_starts}
        B = (context_width + 1) * (1 + radius * (width + 2 * radius))
        if len(low_types) > B:
            raise AssertionError("low-hit type bound")
        factor_count = len(factor_set(actual_word, width))
        distinct = factor_count == length
        rhs = K * max_influence + 4 * area + 2 * E * (context_width - 1) + 2 * B
        if distinct and 2 * length > rhs:
            raise AssertionError("finite short-leaf double-hit inequality")
        rows.append([
            radius, width, K, E, len(exceptional), context_bound,
            len(low_types), B, factor_count, int(distinct), sum(incidence), rhs,
        ])
        counts["width_pruning_cases"] += 1
        counts["distinct_factor_cases"] += int(distinct)
        counts["low_type_checks"] += 1
    return rows, counts


def corpus_audit() -> dict[str, object]:
    counts = {
        "cyclic_classes": 0,
        "minimum_rotations": 0,
        "pruning_reconstructions": 0,
        "removed_components": 0,
        "residual_components": 0,
        "width_pruning_cases": 0,
        "distinct_factor_cases": 0,
        "low_type_checks": 0,
    }
    digest_rows = []
    samples = []
    for q in range(1, Q_MAX + 1):
        for length in range(q + 1, 2 * q + 1):
            if 2**length <= 3**q:
                continue
            classes = sorted({cyclic_class(row) for row in compositions(length, q)})
            for values in classes:
                counts["cyclic_classes"] += 1
                for rotated in minimum_rotations(values):
                    counts["minimum_rotations"] += 1
                    for radius in R_VALUES:
                        inventory = short_leaf_inventory(rotated, radius)
                        rows, local = finite_rows(rotated, radius)
                        counts["pruning_reconstructions"] += 1
                        counts["removed_components"] += int(inventory["K"])
                        counts["residual_components"] += int(inventory["E"])
                        for key, value in local.items():
                            counts[key] += value
                        digest_rows.append([list(rotated), radius, rows])
                        if inventory["K"] and len(samples) < 12:
                            samples.append({
                                "exponents": list(rotated),
                                "R": radius,
                                "K": inventory["K"],
                                "E": inventory["E"],
                                "sigma": inventory["sigma"],
                                "removed": [list(row) for row in inventory["removed"]],
                                "residual_profile": list(inventory["residual_profile"]),
                            })
    if counts["minimum_rotations"] != 10_485 or counts["width_pruning_cases"] != 522_870:
        raise AssertionError(f"private count mismatch: {counts}")
    return {
        "format": "collatz-phase31-short-leaf-corpus-v1",
        "maximum_q": Q_MAX,
        "radii": list(R_VALUES),
        "counts": counts,
        "row_digest_sha256": stable_hash(digest_rows),
        "samples": samples,
        "scope": "Complete positive-D cyclic exponent corpus through q<=9, R in {1,2,3}, and every cyclic width. These are finite structural controls, not asserted positive integer cycles.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase31-short-leaf-theory-v1",
        "claims": EXPECTED_CLAIMS,
        "P191": {
            "residual_bound": "E_R<=h+floor(Sigma/R)",
            "quantifiers": "every valid reduced profile, every integer R>=1, and any fixed maximum-height spine",
            "proof_kernel": "repeatedly delete a flat nonspine leaf of odd-label length at most R; each step deletes exactly one forest node, while every surviving nonspine node has excess at least R and all nonspine excess is charged to Sigma",
        },
        "P192": {
            "context_width": "N_R=n+4R",
            "context_bound": "U_R<=min(L,2A+E_R(N_R-1))",
            "low_type_bound": "B_R(n)=(N_R+1)(1+R(n+2R))",
            "finite_inequality": "2L<=K_R(n+2R-1)+4A+2E_R(n+4R-1)+2B_R(n)",
        },
        "P193": {
            "limit_order": "first q->infinity for each fixed R, then R->infinity",
            "constraint": "xy>=2ell",
            "area_constant": "3(2ell)^(2/3)/(2(ell-1)^(1/3))",
            "equality": "z=lim Sigma/q^(2/3)=0",
        },
        "P194": {
            "statement": "at P193 equality, all but o(J) components are disjoint singleton transports, all but o(L) state-separation windows have exactly two singleton incidences, and the anchor shift-mismatch count is o(L)",
            "identity": "c_(t+1)-c_t=chi_(t+n+1)-chi_t",
            "open_boundary": "no resonant resultant or positive-cycle exclusion is proved",
        },
        "supersession": "P191-P194 replace the old Phase 31 proof route. NG40 remains a valid refutation of the old single-R normalized inference, but it does not satisfy the all-fixed-R short-leaf constraints.",
        "excluded_scope": "The H89 Hamming-shell and q0 numerical candidates in the supplied note are not audited or accepted here.",
        "proves_collatz": False,
    }


def regression_artifact() -> dict[str, object]:
    families = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]
    obstructions = ["NG32", "NG34", "NG35", "NG36", "NG37", "NG38", "NG39", "NG40"]
    return {
        "format": "collatz-phase31-short-leaf-regressions-v1",
        "mandatory_adversarial_families": families,
        "preserved_obstructions": obstructions,
        "scope_checks": {
            "source_167": "finite first-crossing control only; not a positive-cycle witness",
            "rational_shadows": "formal rational profiles are not promoted to ordinary positive cycles",
            "NG40": "preserved against the old one-radius inference; the new theorem uses every fixed R before taking R to infinity",
        },
        "h89_candidates": {
            "status": "OPEN",
            "reason": "the q0 Hamming-shell and ballot counts require an isolated generator/verifier and were intentionally not coupled to this cycle audit",
        },
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 31 short-leaf obstruction report

No finite counterexample to P191 or P192 was found in the declared corpus.
The decisive repair is quantifier-sensitive: for each fixed `R`, first pass to
the cycle asymptotic limit and only then let `R` grow.  A single-radius or
single normalized inequality does not remove residual density, so NG40 remains
a required regression against the obsolete proof route.

The surviving obstruction is arithmetic.  P194 supplies an approximate
low-denominator anchor grid only at equality in the sharp area bound; it does
not supply the nonzero resultant needed by H172 and does not address cycles
whose area lies strictly above that frontier.

The H89 Hamming-shell and `q0` ballot candidates were deliberately deferred to
a separate experiment.  They are not claims or accepted artifacts here.

## What this result does not prove

It does not exclude a positive Collatz cycle, close H172 or H133, audit the H89
numerical candidates, eliminate a nonperiodic branch, or prove or disprove the
Collatz conjecture. `proves_collatz=false`.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    corpus = corpus_audit()
    write_json(args.artifact_dir / "phase31_short_leaf_theory.json", theory_artifact())
    write_json(args.artifact_dir / "phase31_short_leaf_corpus.json", corpus)
    write_json(args.artifact_dir / "phase31_short_leaf_regressions.json", regression_artifact())
    (args.artifact_dir / "phase31_short_leaf_obstruction_report.md").write_text(
        obstruction_report(), encoding="utf-8"
    )
    print(json.dumps({"valid": True, "counts": corpus["counts"], "proves_collatz": False}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
