#!/usr/bin/env python3
"""Generate exact Phase 11 renewal-ladder and dropping-pair evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


DEFAULT_Q_LIMIT = 4_961
DEFAULT_PAIR_BOUND = 262_144
DEFAULT_PAIR_DEPTH = 12
DEFAULT_GAP_CAP = 64
DEFAULT_DIRECT_BOUND = 16_384
A_WORD = "11101"
B_WORD = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def dropping_time(start: int, limit: int = 20_000) -> int:
    value = start
    for depth in range(1, limit + 1):
        value = step(value)
        if value < start:
            return depth
    raise RuntimeError(f"dropping-time limit reached for {start}")


def hq_parameters(limit: int) -> list[dict[str, int]]:
    power_three = 1
    maximum_constant = 0
    rows = []
    for q in range(1, limit + 1):
        maximum_constant = 3 * maximum_constant + (1 << (power_three.bit_length() - 1))
        power_three *= 3
        k_q = power_three.bit_length()
        difference = (1 << k_q) - power_three
        gap_cap = (q - 1) // 3
        height = maximum_constant // difference + gap_cap
        rows.append(
            {
                "q": q,
                "K_q": k_q,
                "B_q_max": maximum_constant,
                "D_q": difference,
                "H_floor": maximum_constant // difference,
                "renewal_gap_cap": gap_cap,
                "height_bound": height,
            }
        )
    return rows


def stopping_table(bound: int) -> tuple[list[int], str, int, int]:
    values = [0] * (bound + 1)
    digest = hashlib.sha256()
    maximum = 0
    witness = 0
    for start in range(2, bound + 1):
        value = dropping_time(start)
        values[start] = value
        digest.update(f"{start}:{value}\n".encode("ascii"))
        if value > maximum:
            maximum = value
            witness = start
    return values, digest.hexdigest(), maximum, witness


def minimum_gap(stopping: list[int], depth: int, height: int) -> tuple[int, int | None, int | None, int | None]:
    count = 0
    prior = None
    best_gap = None
    best_left = None
    best_right = None
    for start in range(2, height + 1):
        if stopping[start] <= depth:
            continue
        count += 1
        if prior is not None:
            gap = start - prior
            if best_gap is None or gap < best_gap:
                best_gap, best_left, best_right = gap, prior, start
        prior = start
    return count, best_gap, best_left, best_right


def pass_intervals(outcomes: list[bool]) -> list[list[int]]:
    result = []
    start = None
    for q, passed in enumerate(outcomes, 1):
        if passed and start is None:
            start = q
        if not passed and start is not None:
            result.append([start, q - 1])
            start = None
    if start is not None:
        result.append([start, len(outcomes)])
    return result


def dropping_pair_audit(q_rows: list[dict[str, int]]) -> dict[str, object]:
    maximum_height = max(row["height_bound"] for row in q_rows)
    stopping, stopping_digest, maximum_stop, maximum_witness = stopping_table(maximum_height)
    row_digest = hashlib.sha256()
    failures = []
    outcomes = []
    selected_q = {1, 16, 17, 22, 27, 29, 32, 34, 35, 94, len(q_rows) - 1, len(q_rows)}
    selected = []
    first_vacuous = None
    for source in q_rows:
        q = source["q"]
        count, delta, left, right = minimum_gap(stopping, source["K_q"], source["height_bound"])
        passed = delta is None or delta > source["renewal_gap_cap"]
        row = {
            "q": q,
            "K_q": source["K_q"],
            "H_floor": source["H_floor"],
            "renewal_gap_cap": source["renewal_gap_cap"],
            "height_bound": source["height_bound"],
            "dropping_safe_count": count,
            "delta_down": delta,
            "left": left,
            "right": right,
            "passes_barrier": passed,
        }
        row_digest.update(
            (
                f"{q}|{source['K_q']}|{source['B_q_max']}|{source['D_q']}|{source['H_floor']}|"
                f"{source['renewal_gap_cap']}|{source['height_bound']}|{count}|{delta}|{left}|{right}|{passed}\n"
            ).encode("ascii")
        )
        outcomes.append(passed)
        if not passed:
            failures.append(row)
        if q in selected_q:
            selected.append(row)
        if count == 0 and first_vacuous is None and source["K_q"] >= maximum_stop:
            first_vacuous = q
    failure_q = [row["q"] for row in failures]
    if len(q_rows) == DEFAULT_Q_LIMIT:
        if failure_q != [17, 22, 27, 29, 32, 34]:
            raise AssertionError("production failure indices changed")
        if any((row["left"], row["right"], row["delta_down"]) != (27, 31, 4) for row in failures):
            raise AssertionError("production minimal failure pair changed")
        if not all(outcomes[34:]):
            raise AssertionError("production q>=35 pass range changed")
        if q_rows[-1]["height_bound"] != 1_666_251:
            raise AssertionError("production q=4961 height changed")
    return {
        "format": "collatz-phase11-dropping-pair-audit-v1",
        "E18": {
            "repository_status": "VERIFIED_FINITE",
            "q_limit": len(q_rows),
            "definition": "D_k(H)={n:2<=n<=H and T^j(n)>=n for 1<=j<=k}; Delta_down is its least pair gap, with +infinity when fewer than two members exist",
            "maximum_height_audited": maximum_height,
            "stopping_time_digest_sha256": stopping_digest,
            "maximum_dropping_time_in_scanned_height": maximum_stop,
            "maximum_dropping_time_first_witness": maximum_witness,
            "all_q_row_digest_sha256": row_digest.hexdigest(),
            "failure_q": failure_q,
            "failure_rows": failures,
            "pass_intervals": pass_intervals(outcomes),
            "selected_rows": selected,
            "all_35_through_limit_pass": len(q_rows) < 35 or all(outcomes[34:]),
            "first_structurally_vacuous_q": first_vacuous,
            "vacuous_reason": "when K_q is at least the maximum dropping time in the scanned height, D_Kq(H) is empty",
        },
        "NG20": height_free_no_go(),
        "what_this_result_does_not_prove": "Finite passes, including vacuous empty-set passes, do not prove the eventual dropping-pair barrier or exclude any infinite Collatz orbit.",
        "proves_collatz": False,
    }


def direct_orbit(start: int, depth: int) -> tuple[str, list[int]]:
    value = start
    word = []
    margins = []
    for _ in range(depth):
        word.append(str(value & 1))
        value = step(value)
        margins.append(value - start)
    return "".join(word), margins


def height_free_no_go(maximum_regression_k: int = 256) -> dict[str, object]:
    digest = hashlib.sha256()
    for k in range(3, maximum_regression_k + 1):
        left = (1 << k) - 5
        right = (1 << k) - 1
        left_word, left_margins = direct_orbit(left, k)
        right_word, right_margins = direct_orbit(right, k)
        if min(left_margins) < 0 or min(right_margins) < 0 or right - left != 4:
            raise AssertionError("height-free witness regression failed")
        digest.update(f"{k}|{left}|{right}|{left_word}|{right_word}|{min(left_margins)}|{min(right_margins)}\n".encode("ascii"))
    return {
        "repository_status": "REFUTED",
        "hypothesis": "A height-free lower bound forces the spacing between all k-step dropping-safe integers to exceed 4 for sufficiently large k.",
        "universal_counterexample": ["2^k-5", "2^k-1"],
        "range": "every integer k>=3",
        "gap": 4,
        "left_orbit_formula": {
            "j=3r": "T^j(2^k-5)=9^r*2^(k-3r)-5",
            "j=3r+1": "T^j(2^k-5)=3*9^r*2^(k-3r-1)-7",
            "j=3r+2": "T^j(2^k-5)=9^(r+1)*2^(k-3r-2)-10",
        },
        "right_orbit_formula": "T^j(2^k-1)=3^j*2^(k-j)-1",
        "regression_maximum_k": maximum_regression_k,
        "regression_digest_sha256": digest.hexdigest(),
        "surviving_requirement": "ordinary height must remain coupled to depth in every spacing argument",
    }


def affine_prefixes(start: int, depth: int) -> tuple[str, list[tuple[int, int, int]]]:
    value = start
    coefficient = 1
    constant = 0
    denominator = 1
    word = []
    rows = []
    for _ in range(depth):
        odd = value & 1
        word.append(str(odd))
        value = step(value)
        if odd:
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
        rows.append((coefficient, constant, denominator))
    return "".join(word), rows


def ceil_div(numerator: int, denominator: int) -> int:
    return -((-numerator) // denominator)


def cylinder_interval(
    first_source: int,
    gap: int,
    maximum_parameter: int,
    depth: int,
    modulus: int,
) -> tuple[int, int, str, str, int, int, int]:
    lower = 0
    upper = maximum_parameter
    words = []
    positive = negative = zero = 0
    for source in (first_source, first_source + gap):
        word, prefixes = affine_prefixes(source, depth)
        words.append(word)
        for coefficient, constant, denominator in prefixes:
            numerator = (coefficient - denominator) * source + constant
            slope_numerator = (coefficient - denominator) * modulus
            if numerator % denominator or slope_numerator % denominator:
                raise AssertionError("cylinder affine margin is not integral")
            base_margin = numerator // denominator
            slope = slope_numerator // denominator
            if slope > 0:
                positive += 1
                lower = max(lower, ceil_div(-base_margin, slope))
            elif slope < 0:
                negative += 1
                upper = min(upper, base_margin // (-slope))
            else:
                zero += 1
                if base_margin < 0:
                    lower, upper = 1, 0
    return max(lower, 0), min(upper, maximum_parameter), words[0], words[1], positive, negative, zero


def first_source_for_residue(residue: int, modulus: int) -> int:
    return residue if residue >= 2 else residue + modulus


def cylinder_summary(bound: int, depth: int, gap_cap: int) -> dict[str, object]:
    modulus = 1 << depth
    digest = hashlib.sha256()
    cylinders = total_pairs = safe_pairs = all_safe = empty = partial = 0
    positive = negative = zero = 0
    first_partial = None
    for gap in range(1, gap_cap + 1):
        maximum_source = bound - gap
        for residue in range(modulus):
            first_source = first_source_for_residue(residue, modulus)
            if first_source > maximum_source:
                continue
            maximum_parameter = (maximum_source - first_source) // modulus
            lower, upper, left_word, right_word, pos, neg, zer = cylinder_interval(
                first_source, gap, maximum_parameter, depth, modulus
            )
            count = max(0, upper - lower + 1)
            available = maximum_parameter + 1
            cylinders += 1
            total_pairs += available
            safe_pairs += count
            positive += pos
            negative += neg
            zero += zer
            if count == 0:
                empty += 1
            elif count == available:
                all_safe += 1
            else:
                partial += 1
                candidate = {
                    "gap": gap,
                    "residue": residue,
                    "first_source": first_source,
                    "maximum_parameter": maximum_parameter,
                    "safe_parameter_interval": [lower, upper],
                    "left_word": left_word,
                    "right_word": right_word,
                }
                if first_partial is None or (first_source, gap, residue) < (
                    first_partial["first_source"],
                    first_partial["gap"],
                    first_partial["residue"],
                ):
                    first_partial = candidate
            digest.update(
                f"{gap}|{residue}|{first_source}|{maximum_parameter}|{lower}|{upper}|{left_word}|{right_word}|{pos}|{neg}|{zer}\n".encode(
                    "ascii"
                )
            )
    return {
        "bound_H": bound,
        "depth_L": depth,
        "gap_cap": gap_cap,
        "residue_modulus": modulus,
        "nonempty_input_cylinders": cylinders,
        "represented_pairs": total_pairs,
        "dropping_safe_pairs": safe_pairs,
        "all_safe_cylinders": all_safe,
        "empty_safe_cylinders": empty,
        "partially_safe_cylinders": partial,
        "first_partially_safe_cylinder": first_partial,
        "positive_slope_constraints": positive,
        "negative_slope_constraints": negative,
        "zero_slope_constraints": zero,
        "cylinder_row_digest_sha256": digest.hexdigest(),
    }


def literal_pair_audit(bound: int, depth: int, gap_cap: int) -> dict[str, object]:
    modulus = 1 << depth
    interval_cache: dict[tuple[int, int], tuple[int, int, int]] = {}
    digest = hashlib.sha256()
    total = safe = 0
    for left in range(2, bound + 1):
        for gap in range(1, min(gap_cap, bound - left) + 1):
            right = left + gap
            left_word, left_margins = direct_orbit(left, depth)
            right_word, right_margins = direct_orbit(right, depth)
            literal = min(left_margins) >= 0 and min(right_margins) >= 0
            residue = left % modulus
            key = (gap, residue)
            cached = interval_cache.get(key)
            if cached is None:
                first_source = first_source_for_residue(residue, modulus)
                maximum_parameter = (bound - gap - first_source) // modulus
                low, high, _lw, _rw, _p, _n, _z = cylinder_interval(first_source, gap, maximum_parameter, depth, modulus)
                cached = (first_source, low, high)
                interval_cache[key] = cached
            first_source, low, high = cached
            parameter = (left - first_source) // modulus
            predicted = low <= parameter <= high
            if predicted != literal:
                raise AssertionError("pair-cylinder closure disagrees with literal orbit")
            total += 1
            safe += literal
            digest.update(f"{left}|{right}|{left_word}|{right_word}|{literal}\n".encode("ascii"))
    return {
        "bound_H": bound,
        "depth_L": depth,
        "gap_cap": gap_cap,
        "pairs_checked": total,
        "dropping_safe_pairs": safe,
        "row_digest_sha256": digest.hexdigest(),
        "cylinder_rule_agrees": True,
    }


def affine_residue(word: str) -> int:
    coefficient = 1
    constant = 0
    denominator = 1
    for bit in word:
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    return residue or denominator


def family_values() -> dict[str, list[int]]:
    blocks = []
    for mask in range(4096):
        word = "".join("111" if mask & (1 << index) else "110" for index in range(12))
        blocks.append(affine_residue(word))
    return {
        "2^m_minus_1": [(1 << exponent) - 1 for exponent in range(1, 65)],
        "8^m_minus_5": [(1 << (3 * exponent)) - 5 for exponent in range(1, 33)],
        "(110|111)^star": blocks,
        "A^rB^s": [affine_residue(A_WORD * r + B_WORD * s) for r in range(1, 33) for s in range(1, 33)],
        "A_and_B": [affine_residue(A_WORD), affine_residue(B_WORD)],
    }


def mandatory_margin_audit(depth: int) -> dict[str, object]:
    digest = hashlib.sha256()
    counts = {}
    for label, raw in family_values().items():
        values = sorted(set(raw))
        count = 0
        for left, right in zip(values, values[1:]):
            left_word, left_margins = direct_orbit(left, depth)
            right_word, right_margins = direct_orbit(right, depth)
            for source, margins in ((left, left_margins), (right, right_margins)):
                _word, prefixes = affine_prefixes(source, depth)
                rebuilt = [((a - q) * source + b) // q for a, b, q in prefixes]
                if rebuilt != margins:
                    raise AssertionError("mandatory affine margin mismatch")
            digest.update(
                f"{label}|{left}|{right}|{left_word}|{right_word}|{','.join(map(str,left_margins))}|{','.join(map(str,right_margins))}\n".encode(
                    "ascii"
                )
            )
            count += 1
        counts[label] = count
    return {
        "repository_status": "VERIFIED_FINITE",
        "depth": depth,
        "pairs_checked": counts,
        "total_pairs_checked": sum(counts.values()),
        "row_digest_sha256": digest.hexdigest(),
    }


def coefficient_safe_positions(q: int):
    maximum_positions = tuple((3**index).bit_length() - 1 for index in range(q))
    positions = [0] * q

    def extend(index: int, previous: int):
        if index == q:
            yield tuple(positions)
            return
        for position in range(previous + 1, maximum_positions[index] + 1):
            positions[index] = position
            yield from extend(index + 1, position)

    positions[0] = 0
    yield from extend(1, 0)


def renewal_symbolic_regression(maximum_q: int = 12) -> dict[str, object]:
    digest = hashlib.sha256()
    total = 0
    maximum_constant = 0
    prior_power = 1
    layer_counts = []
    for q in range(1, maximum_q + 1):
        maximum_constant = 3 * maximum_constant + (1 << (prior_power.bit_length() - 1))
        prior_power *= 3
        count = 0
        for positions in coefficient_safe_positions(q):
            constant = sum(3 ** (q - 1 - index) * (1 << position) for index, position in enumerate(positions))
            if constant > maximum_constant or 3 * constant > q * 3**q:
                raise AssertionError("renewal affine-correction bound failed")
            digest.update(
                f"{q}|{prior_power.bit_length()}|{','.join(map(str,positions))}|{constant}|{maximum_constant}\n".encode("ascii")
            )
            count += 1
        layer_counts.append(count)
        total += count
    return {
        "repository_status": "VERIFIED_FINITE",
        "role": "regression of the exact P69 position argument; the theorem is not inferred from this finite audit",
        "maximum_q": maximum_q,
        "layer_counts": layer_counts,
        "total_words": total,
        "row_digest_sha256": digest.hexdigest(),
    }


def pair_cylinder_data(bound: int, depth: int, gap_cap: int, direct_bound: int) -> dict[str, object]:
    summary = cylinder_summary(bound, depth, gap_cap)
    direct = literal_pair_audit(direct_bound, depth, min(gap_cap, 32))
    return {
        "format": "collatz-phase11-pair-cylinder-v1",
        "P71": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "On a fixed length-L parity cylinder x=r+2^L*t, every exact margin T^j(x)-x is affine in t; all k-step dropping-safety inequalities therefore close to one exact integer interval in t.",
            "affine_margin": "((3^a_j-2^j)*x+B_j)/2^j",
            "parameter_slope": "(3^a_j-2^j)*2^(L-j)",
            "endpoint_dominance": "use the lower t endpoint for positive slope and the upper t endpoint for negative slope",
            "transition_zero": "(A,B,Q)->(A,B,2Q)",
            "transition_one": "(A,B,Q)->(3A,3B+Q,2Q)",
            "pair_rule": "intersect the two tails' exact integer t intervals",
            "scope": "fixed finite parity cylinders; no cross-cylinder merge or eventual closure is claimed",
        },
        "E19": {
            "repository_status": "VERIFIED_FINITE",
            "production_cylinder_audit": summary,
            "literal_cross_check": direct,
        },
        "mandatory_adversarial_audit": mandatory_margin_audit(depth),
        "scalability_boundary": {
            "target_certificate_found": False,
            "reason": "the exact rule closes each fixed cylinder but retains all 2^L residue classes; NG19 forbids replacing the L-bit residue by any literal b<L truncation at L=12",
            "next_required_mechanism": "a sound cross-cylinder dominance, carry interval, or recursive quotient state that separates all stored NG19 collisions",
        },
        "what_this_result_does_not_prove": "Finite cylinder compression does not prove the eventual dropping-pair barrier, C04, C05, H54, or Collatz.",
        "proves_collatz": False,
    }


def renewal_ladder_data(artifact_dir: Path) -> dict[str, object]:
    return {
        "format": "collatz-phase11-renewal-ladder-v1",
        "P69": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "Every Collatz counterexample falls into a nontrivial cycle, an infinite coefficient-safe tail, or a finite-crossing renewal ladder of successive tail minima.",
            "tail_minimum_definition": "the successive distinct values of min{x_t:t>=r} along an injective positive orbit",
            "nonperiodic_properties": [
                "S_0<S_1<...",
                "S_i=3 (mod 4)",
                "every future iterate of S_i is at least S_i",
            ],
            "finite_crossing_properties": [
                "K_q=bitlength(3^q)",
                "S_i<=H_q=B_q_max/D_q",
                "4<=S_(i+1)-S_i<=d_i=T^Kq(S_i)-S_i<=floor((q_i-1)/3)",
                "q_i tends to infinity",
                "reduced denominator of B_i/D_q is greater than 3*D_q/q_i",
            ],
            "exact_identities": [
                "T^K(S)=(3^q*S+B)/2^K=S+d",
                "B=D*S+2^K*d",
                "B/3^q=(1/3)*sum_r 2^p_r/3^r<=q/3",
                "d=(3^q/2^K)*(B/3^q)-(1-3^q/2^K)*S<B/3^q",
                "gcd(B,D)=gcd(d,D)",
                "den(B/D)=D/gcd(d,D)>3D/q because 0<d<q/3",
            ],
            "odd_count_clarification": "q_i counts odd shortcut steps; q_i is not asserted to be an odd-valued integer",
            "symbolic_regression": renewal_symbolic_regression(),
        },
        "P70": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "If the displayed dropping-safe spacing inequality holds for every sufficiently large q, then no finite-crossing renewal ladder exists.",
            "eventual_barrier": "Delta_down_Kq(floor(H_q)+floor((q-1)/3))>floor((q-1)/3)",
            "proof": [
                "q_i tends to infinity, so an eventual bound applies to some ladder rung",
                "both S_i and S_(i+1) lie in D_Kq at the displayed height",
                "their gap is at most floor((q_i-1)/3), contradicting the spacing bound",
            ],
            "remaining_branches": ["nontrivial cycle", "infinite coefficient-safe tail"],
            "relation_to_C05": "a separate renewal-ladder target; it does not by itself settle the cycle or infinite coefficient-safe-tail alternatives",
        },
        "H70": {
            "repository_status": "OPEN",
            "statement": "Delta_down_Kq(floor(H_q)+floor((q-1)/3))>floor((q-1)/3) for every sufficiently large q",
            "eventual_threshold_found": False,
        },
        "dependencies": {
            "phase10_rational_cycle_sha256": sha256(artifact_dir / "phase10_rational_cycle.json"),
            "two_tail_state_collisions_sha256": sha256(artifact_dir / "two_tail_state_collisions.json"),
        },
        "what_this_result_does_not_prove": "The trichotomy is a reduction. Neither remaining alternative nor the eventual dropping-safe spacing inequality is proved here.",
        "proves_collatz": False,
    }


def obstruction_report(audit: dict[str, object], cylinder: dict[str, object]) -> str:
    e18 = audit["E18"]
    production = cylinder["E19"]["production_cylinder_audit"]
    return "\n".join(
        [
            "# Phase 11 obstruction report",
            "",
            "This report does not claim a proof or disproof of the Collatz conjecture.",
            "",
            "## Exact finite barrier audit",
            "",
            f"- Failure q values: {e18['failure_q']}.",
            "- Every failure has least pair (27,31) and gap 4.",
            f"- Every 35<=q<={e18['q_limit']} passes in the audited finite height.",
            f"- The first structurally vacuous q is {e18['first_structurally_vacuous_q']}; later finite passes do not contain a dropping-safe point once K_q reaches the scanned maximum dropping time.",
            "",
            "## Height-free no-go",
            "",
            "For every k>=3, 2^k-5 and 2^k-1 are k-step dropping-safe and have gap 4. Any spacing strategy that discards ordinary height is therefore refuted.",
            "",
            "## Pair-cylinder result",
            "",
            f"- {production['represented_pairs']} pairs are represented by {production['nonempty_input_cylinders']} exact affine cylinders.",
            f"- The exact interval rule finds {production['dropping_safe_pairs']} dropping-safe pairs at depth {production['depth_L']}.",
            "- This is a genuine endpoint-dominance/interval-closure rule, but it retains all 2^L residue classes and does not close the eventual target.",
            "- NG19 prevents silently truncating those residue classes at L=12.",
            "",
            "## What this result does not prove",
            "",
            "Phase 11 does not prove the eventual dropping-safe barrier, eliminate nontrivial cycles, eliminate infinite coefficient-safe tails, prove C04/C05/H54, or prove the Collatz conjecture.",
            "",
        ]
    )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate(
    artifact_dir: Path,
    q_limit: int = DEFAULT_Q_LIMIT,
    pair_bound: int = DEFAULT_PAIR_BOUND,
    pair_depth: int = DEFAULT_PAIR_DEPTH,
    gap_cap: int = DEFAULT_GAP_CAP,
    direct_bound: int = DEFAULT_DIRECT_BOUND,
) -> dict[str, object]:
    if q_limit < 35 or pair_depth < 3 or pair_bound <= 1 << pair_depth or not 1 <= gap_cap < pair_bound:
        raise ValueError("invalid Phase 11 bounds")
    if not (1 << pair_depth) <= direct_bound <= pair_bound:
        raise ValueError("direct bound must lie between the cylinder modulus and pair bound")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    ladder = renewal_ladder_data(artifact_dir)
    audit = dropping_pair_audit(hq_parameters(q_limit))
    cylinder = pair_cylinder_data(pair_bound, pair_depth, gap_cap, direct_bound)
    write_json(artifact_dir / "phase11_renewal_ladder.json", ladder)
    write_json(artifact_dir / "phase11_dropping_pair_audit.json", audit)
    write_json(artifact_dir / "phase11_pair_cylinder.json", cylinder)
    (artifact_dir / "phase11_obstruction_report.md").write_text(obstruction_report(audit, cylinder), encoding="utf-8")
    return {
        "P69": "VERIFIED_THEOREM",
        "P70": "VERIFIED_THEOREM",
        "H70": "OPEN",
        "P71": "VERIFIED_THEOREM",
        "E18": "VERIFIED_FINITE",
        "E19": "VERIFIED_FINITE",
        "NG20": "REFUTED",
        "failure_q": audit["E18"]["failure_q"],
        "q_limit": q_limit,
        "pair_cylinders": cylinder["E19"]["production_cylinder_audit"]["nonempty_input_cylinders"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--q-limit", type=int, default=DEFAULT_Q_LIMIT)
    parser.add_argument("--pair-bound", type=int, default=DEFAULT_PAIR_BOUND)
    parser.add_argument("--pair-depth", type=int, default=DEFAULT_PAIR_DEPTH)
    parser.add_argument("--gap-cap", type=int, default=DEFAULT_GAP_CAP)
    parser.add_argument("--direct-bound", type=int, default=DEFAULT_DIRECT_BOUND)
    args = parser.parse_args()
    result = generate(args.artifact_dir, args.q_limit, args.pair_bound, args.pair_depth, args.gap_cap, args.direct_bound)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
