#!/usr/bin/env python3
"""Independently verify Phase 11 renewal-ladder evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path


WORD_A = "11101"
WORD_B = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail("artifact is not an object")
    return value


def file_hash(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest()


def collatz(value: int) -> int:
    return (3 * value + 1) >> 1 if value & 1 else value >> 1


def first_drop(start: int, cap: int = 20_000) -> int:
    current = start
    for index in range(1, cap + 1):
        current = collatz(current)
        if current < start:
            return index
    fail(f"dropping-time cap reached for {start}")
    raise AssertionError("unreachable")


def rebuild_hq(limit: int) -> list[tuple[int, int, int, int, int, int, int]]:
    three = 1
    b_value = 0
    result = []
    for q in range(1, limit + 1):
        greatest_two_below = 1 << (three.bit_length() - 1)
        b_value = 3 * b_value + greatest_two_below
        three *= 3
        k = three.bit_length()
        d_value = (1 << k) - three
        floor_h = b_value // d_value
        allowance = (q - 1) // 3
        result.append((q, k, b_value, d_value, floor_h, allowance, floor_h + allowance))
    return result


def rebuild_drops(bound: int) -> tuple[list[int], str, int, int]:
    table = [0] * (bound + 1)
    digest = hashlib.sha256()
    record_time = 0
    record_start = 0
    for start in range(2, bound + 1):
        time = first_drop(start)
        table[start] = time
        digest.update(f"{start}:{time}\n".encode("ascii"))
        if time > record_time:
            record_time, record_start = time, start
    return table, digest.hexdigest(), record_time, record_start


def spacing(table: list[int], k: int, height: int) -> tuple[int, int | None, int | None, int | None]:
    survivors = 0
    previous = None
    minimum = None
    witness_left = witness_right = None
    for candidate in range(2, height + 1):
        if table[candidate] <= k:
            continue
        survivors += 1
        if previous is not None and (minimum is None or candidate - previous < minimum):
            minimum = candidate - previous
            witness_left, witness_right = previous, candidate
        previous = candidate
    return survivors, minimum, witness_left, witness_right


def intervals(flags: list[bool]) -> list[list[int]]:
    result = []
    opening = None
    for index, flag in enumerate(flags, 1):
        if flag and opening is None:
            opening = index
        if not flag and opening is not None:
            result.append([opening, index - 1])
            opening = None
    if opening is not None:
        result.append([opening, len(flags)])
    return result


def orbit_data(start: int, length: int) -> tuple[str, list[int]]:
    value = start
    symbols = []
    margins = []
    for _ in range(length):
        symbols.append("1" if value & 1 else "0")
        value = collatz(value)
        margins.append(value - start)
    return "".join(symbols), margins


def no_height_expected(maximum_k: int) -> dict[str, object]:
    digest = hashlib.sha256()
    for k in range(3, maximum_k + 1):
        low = (1 << k) - 5
        high = (1 << k) - 1
        low_word, low_margin = orbit_data(low, k)
        high_word, high_margin = orbit_data(high, k)
        if high - low != 4 or min(low_margin) < 0 or min(high_margin) < 0:
            fail("NG20 direct regression failed")
        for j in range(k + 1):
            r, s = divmod(j, 3)
            if s == 0:
                closed = 9**r * (1 << (k - 3 * r)) - 5
            elif s == 1:
                closed = 3 * 9**r * (1 << (k - 3 * r - 1)) - 7
            else:
                closed = 9 ** (r + 1) * (1 << (k - 3 * r - 2)) - 10
            actual = low
            for _ in range(j):
                actual = collatz(actual)
            if actual != closed:
                fail("NG20 symbolic left formula failed")
            right_closed = 3**j * (1 << (k - j)) - 1
            actual_right = high
            for _ in range(j):
                actual_right = collatz(actual_right)
            if actual_right != right_closed:
                fail("NG20 symbolic right formula failed")
        digest.update(f"{k}|{low}|{high}|{low_word}|{high_word}|{min(low_margin)}|{min(high_margin)}\n".encode("ascii"))
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
        "regression_maximum_k": maximum_k,
        "regression_digest_sha256": digest.hexdigest(),
        "surviving_requirement": "ordinary height must remain coupled to depth in every spacing argument",
    }


def expected_audit(q_limit: int, maximum_k: int) -> dict[str, object]:
    q_rows = rebuild_hq(q_limit)
    maximum_height = max(row[6] for row in q_rows)
    drops, stop_digest, record_time, record_start = rebuild_drops(maximum_height)
    digest = hashlib.sha256()
    failed = []
    flags = []
    selected_set = {1, 16, 17, 22, 27, 29, 32, 34, 35, 94, q_limit - 1, q_limit}
    selected = []
    first_vacuous = None
    for q, k, b_value, d_value, floor_h, allowance, height in q_rows:
        count, delta, left, right = spacing(drops, k, height)
        passed = delta is None or delta > allowance
        row = {
            "q": q,
            "K_q": k,
            "H_floor": floor_h,
            "renewal_gap_cap": allowance,
            "height_bound": height,
            "dropping_safe_count": count,
            "delta_down": delta,
            "left": left,
            "right": right,
            "passes_barrier": passed,
        }
        digest.update(
            f"{q}|{k}|{b_value}|{d_value}|{floor_h}|{allowance}|{height}|{count}|{delta}|{left}|{right}|{passed}\n".encode(
                "ascii"
            )
        )
        flags.append(passed)
        if not passed:
            failed.append(row)
        if q in selected_set:
            selected.append(row)
        if count == 0 and first_vacuous is None and k >= record_time:
            first_vacuous = q
    expected = {
        "repository_status": "VERIFIED_FINITE",
        "q_limit": q_limit,
        "definition": "D_k(H)={n:2<=n<=H and T^j(n)>=n for 1<=j<=k}; Delta_down is its least pair gap, with +infinity when fewer than two members exist",
        "maximum_height_audited": maximum_height,
        "stopping_time_digest_sha256": stop_digest,
        "maximum_dropping_time_in_scanned_height": record_time,
        "maximum_dropping_time_first_witness": record_start,
        "all_q_row_digest_sha256": digest.hexdigest(),
        "failure_q": [row["q"] for row in failed],
        "failure_rows": failed,
        "pass_intervals": intervals(flags),
        "selected_rows": selected,
        "all_35_through_limit_pass": q_limit < 35 or all(flags[34:]),
        "first_structurally_vacuous_q": first_vacuous,
        "vacuous_reason": "when K_q is at least the maximum dropping time in the scanned height, D_Kq(H) is empty",
    }
    return {
        "format": "collatz-phase11-dropping-pair-audit-v1",
        "E18": expected,
        "NG20": no_height_expected(maximum_k),
        "what_this_result_does_not_prove": "Finite passes, including vacuous empty-set passes, do not prove the eventual dropping-pair barrier or exclude any infinite Collatz orbit.",
        "proves_collatz": False,
    }


def affine_trace(start: int, length: int) -> tuple[str, list[tuple[int, int, int]]]:
    current = start
    a_value = q_value = 1
    b_value = 0
    word = []
    rows = []
    for _ in range(length):
        odd = current & 1
        word.append("1" if odd else "0")
        current = collatz(current)
        if odd:
            a_value *= 3
            b_value = 3 * b_value + q_value
        q_value *= 2
        rows.append((a_value, b_value, q_value))
    return "".join(word), rows


def ceiling_ratio(a: int, b: int) -> int:
    return -((-a) // b)


def initial_in_class(residue: int, modulus: int) -> int:
    return residue if residue >= 2 else residue + modulus


def solve_cylinder(start: int, gap: int, last_t: int, length: int, modulus: int) -> tuple[int, int, str, str, int, int, int]:
    lower, upper = 0, last_t
    words = []
    positives = negatives = zeros = 0
    for source in (start, start + gap):
        word, rows = affine_trace(source, length)
        words.append(word)
        for a_value, b_value, q_value in rows:
            base_num = (a_value - q_value) * source + b_value
            step_num = (a_value - q_value) * modulus
            if base_num % q_value or step_num % q_value:
                fail("nonintegral verifier cylinder margin")
            base = base_num // q_value
            slope = step_num // q_value
            if slope > 0:
                positives += 1
                lower = max(lower, ceiling_ratio(-base, slope))
            elif slope < 0:
                negatives += 1
                upper = min(upper, base // (-slope))
            else:
                zeros += 1
                if base < 0:
                    lower, upper = 1, 0
    return max(0, lower), min(last_t, upper), words[0], words[1], positives, negatives, zeros


def expected_cylinders(bound: int, length: int, gap_limit: int) -> dict[str, object]:
    modulus = 1 << length
    digest = hashlib.sha256()
    cylinders = represented = safe = all_safe = empty = partial = 0
    pos_total = neg_total = zero_total = 0
    first_partial = None
    for gap in range(1, gap_limit + 1):
        last_source = bound - gap
        for residue in range(modulus):
            first = initial_in_class(residue, modulus)
            if first > last_source:
                continue
            last_t = (last_source - first) // modulus
            low, high, left_word, right_word, pos, neg, zeros = solve_cylinder(first, gap, last_t, length, modulus)
            safe_count = max(0, high - low + 1)
            available = last_t + 1
            cylinders += 1
            represented += available
            safe += safe_count
            pos_total += pos
            neg_total += neg
            zero_total += zeros
            if safe_count == 0:
                empty += 1
            elif safe_count == available:
                all_safe += 1
            else:
                partial += 1
                candidate = {
                    "gap": gap,
                    "residue": residue,
                    "first_source": first,
                    "maximum_parameter": last_t,
                    "safe_parameter_interval": [low, high],
                    "left_word": left_word,
                    "right_word": right_word,
                }
                if first_partial is None or (first, gap, residue) < (
                    first_partial["first_source"],
                    first_partial["gap"],
                    first_partial["residue"],
                ):
                    first_partial = candidate
            digest.update(
                f"{gap}|{residue}|{first}|{last_t}|{low}|{high}|{left_word}|{right_word}|{pos}|{neg}|{zeros}\n".encode(
                    "ascii"
                )
            )
    return {
        "bound_H": bound,
        "depth_L": length,
        "gap_cap": gap_limit,
        "residue_modulus": modulus,
        "nonempty_input_cylinders": cylinders,
        "represented_pairs": represented,
        "dropping_safe_pairs": safe,
        "all_safe_cylinders": all_safe,
        "empty_safe_cylinders": empty,
        "partially_safe_cylinders": partial,
        "first_partially_safe_cylinder": first_partial,
        "positive_slope_constraints": pos_total,
        "negative_slope_constraints": neg_total,
        "zero_slope_constraints": zero_total,
        "cylinder_row_digest_sha256": digest.hexdigest(),
    }


def expected_literal(bound: int, length: int, gap_limit: int) -> dict[str, object]:
    modulus = 1 << length
    cached: dict[tuple[int, int], tuple[int, int, int]] = {}
    digest = hashlib.sha256()
    checked = safe_count = 0
    for left in range(2, bound + 1):
        for gap in range(1, min(gap_limit, bound - left) + 1):
            right = left + gap
            left_word, left_margins = orbit_data(left, length)
            right_word, right_margins = orbit_data(right, length)
            literal = all(value >= 0 for value in left_margins) and all(value >= 0 for value in right_margins)
            residue = left % modulus
            key = gap, residue
            item = cached.get(key)
            if item is None:
                first = initial_in_class(residue, modulus)
                last_t = (bound - gap - first) // modulus
                low, high, _lw, _rw, _p, _n, _z = solve_cylinder(first, gap, last_t, length, modulus)
                item = first, low, high
                cached[key] = item
            first, low, high = item
            parameter = (left - first) // modulus
            if literal != (low <= parameter <= high):
                fail("independent literal/cylinder disagreement")
            checked += 1
            safe_count += literal
            digest.update(f"{left}|{right}|{left_word}|{right_word}|{literal}\n".encode("ascii"))
    return {
        "bound_H": bound,
        "depth_L": length,
        "gap_cap": gap_limit,
        "pairs_checked": checked,
        "dropping_safe_pairs": safe_count,
        "row_digest_sha256": digest.hexdigest(),
        "cylinder_rule_agrees": True,
    }


def inverse_word(word: str) -> int:
    a_value = q_value = 1
    b_value = 0
    for symbol in word:
        if symbol == "1":
            a_value *= 3
            b_value = 3 * b_value + q_value
        q_value *= 2
    residue = (-b_value * pow(a_value, -1, q_value)) % q_value
    return residue or q_value


def families() -> dict[str, list[int]]:
    block_values = []
    for mask in range(1 << 12):
        block_values.append(inverse_word("".join("111" if mask >> index & 1 else "110" for index in range(12))))
    return {
        "2^m_minus_1": [(1 << exponent) - 1 for exponent in range(1, 65)],
        "8^m_minus_5": [(1 << (3 * exponent)) - 5 for exponent in range(1, 33)],
        "(110|111)^star": block_values,
        "A^rB^s": [inverse_word(WORD_A * r + WORD_B * s) for r in range(1, 33) for s in range(1, 33)],
        "A_and_B": [inverse_word(WORD_A), inverse_word(WORD_B)],
    }


def expected_mandatory(length: int) -> dict[str, object]:
    digest = hashlib.sha256()
    counts = {}
    for label, raw in families().items():
        ordered = sorted(set(raw))
        count = 0
        for left, right in zip(ordered, ordered[1:]):
            left_word, left_margin = orbit_data(left, length)
            right_word, right_margin = orbit_data(right, length)
            for source, margins in ((left, left_margin), (right, right_margin)):
                _word, trace = affine_trace(source, length)
                rebuilt = [((a - q) * source + b) // q for a, b, q in trace]
                if rebuilt != margins:
                    fail("independent mandatory affine margin mismatch")
            digest.update(
                f"{label}|{left}|{right}|{left_word}|{right_word}|{','.join(map(str,left_margin))}|{','.join(map(str,right_margin))}\n".encode(
                    "ascii"
                )
            )
            count += 1
        counts[label] = count
    return {
        "repository_status": "VERIFIED_FINITE",
        "depth": length,
        "pairs_checked": counts,
        "total_pairs_checked": sum(counts.values()),
        "row_digest_sha256": digest.hexdigest(),
    }


def position_tuples(odd_steps: int):
    ceilings = [(3**index).bit_length() - 1 for index in range(odd_steps)]
    values = [0] * odd_steps

    def visit(index: int, last: int):
        if index == odd_steps:
            yield tuple(values)
        else:
            for position in range(last + 1, ceilings[index] + 1):
                values[index] = position
                yield from visit(index + 1, position)

    values[0] = 0
    yield from visit(1, 0)


def expected_symbolic_regression(maximum_q: int) -> dict[str, object]:
    digest = hashlib.sha256()
    total = 0
    b_max = 0
    previous_three = 1
    counts = []
    for q in range(1, maximum_q + 1):
        b_max = 3 * b_max + (1 << (previous_three.bit_length() - 1))
        previous_three *= 3
        count = 0
        for positions in position_tuples(q):
            correction = 0
            for index, position in enumerate(positions):
                correction += 3 ** (q - index - 1) * (1 << position)
                if (1 << position) > 3**index:
                    fail("P69 coefficient-safe position premise failed")
            if correction > b_max or 3 * correction > q * previous_three:
                fail("P69 affine correction inequality failed")
            digest.update(
                f"{q}|{previous_three.bit_length()}|{','.join(map(str,positions))}|{correction}|{b_max}\n".encode("ascii")
            )
            count += 1
        counts.append(count)
        total += count
    return {
        "repository_status": "VERIFIED_FINITE",
        "role": "regression of the exact P69 position argument; the theorem is not inferred from this finite audit",
        "maximum_q": maximum_q,
        "layer_counts": counts,
        "total_words": total,
        "row_digest_sha256": digest.hexdigest(),
    }


def audit_symbolic_ladder() -> None:
    for residue in range(2, 500):
        if residue % 2 == 0 and collatz(residue) >= residue:
            fail("even tail-minimum residue audit failed")
        if residue % 4 == 1 and residue > 1 and collatz(collatz(residue)) >= residue:
            fail("1 mod 4 tail-minimum residue audit failed")
    for q in range(13, 300):
        p_value = 3**q
        d_value = (1 << p_value.bit_length()) - p_value
        for displacement in range(1, (q - 1) // 3 + 1):
            reduced_denominator = d_value // math.gcd(displacement, d_value)
            if not reduced_denominator * q > 3 * d_value:
                fail("formal rational denominator inequality failed")


def verify_ladder(path: Path, artifact_dir: Path) -> None:
    data = load(path)
    if data.get("format") != "collatz-phase11-renewal-ladder-v1" or data.get("proves_collatz") is not False:
        fail("renewal ladder format or proof boundary mismatch")
    p69 = data.get("P69")
    if (
        not isinstance(p69, dict)
        or p69.get("repository_status") != "VERIFIED_THEOREM"
        or p69.get("statement")
        != "Every Collatz counterexample falls into a nontrivial cycle, an infinite coefficient-safe tail, or a finite-crossing renewal ladder of successive tail minima."
        or p69.get("odd_count_clarification") != "q_i counts odd shortcut steps; q_i is not asserted to be an odd-valued integer"
        or "den(B/D)=D/gcd(d,D)>3D/q because 0<d<q/3" not in p69.get("exact_identities", [])
    ):
        fail("P69 theorem boundary mismatch")
    regression = p69.get("symbolic_regression")
    if not isinstance(regression, dict) or regression != expected_symbolic_regression(int(regression.get("maximum_q", 0))):
        fail("P69 symbolic regression mismatch")
    p70 = data.get("P70")
    if (
        not isinstance(p70, dict)
        or p70.get("repository_status") != "VERIFIED_THEOREM"
        or p70.get("eventual_barrier")
        != "Delta_down_Kq(floor(H_q)+floor((q-1)/3))>floor((q-1)/3)"
        or p70.get("remaining_branches") != ["nontrivial cycle", "infinite coefficient-safe tail"]
    ):
        fail("P70 implication boundary mismatch")
    h70 = data.get("H70")
    if (
        not isinstance(h70, dict)
        or h70.get("repository_status") != "OPEN"
        or h70.get("eventual_threshold_found") is not False
        or h70.get("statement")
        != "Delta_down_Kq(floor(H_q)+floor((q-1)/3))>floor((q-1)/3) for every sufficiently large q"
    ):
        fail("H70 was improperly promoted")
    dependencies = data.get("dependencies")
    if (
        not isinstance(dependencies, dict)
        or dependencies.get("phase10_rational_cycle_sha256") != file_hash(artifact_dir / "phase10_rational_cycle.json")
        or dependencies.get("two_tail_state_collisions_sha256") != file_hash(artifact_dir / "two_tail_state_collisions.json")
    ):
        fail("Phase 11 dependency mismatch")
    audit_symbolic_ladder()


def verify_pair_cylinder(path: Path) -> tuple[int, int]:
    data = load(path)
    if data.get("format") != "collatz-phase11-pair-cylinder-v1" or data.get("proves_collatz") is not False:
        fail("pair-cylinder format or proof boundary mismatch")
    p71 = data.get("P71")
    if (
        not isinstance(p71, dict)
        or p71.get("repository_status") != "VERIFIED_THEOREM"
        or p71.get("parameter_slope") != "(3^a_j-2^j)*2^(L-j)"
        or p71.get("transition_one") != "(A,B,Q)->(3A,3B+Q,2Q)"
        or not str(p71.get("scope", "")).startswith("fixed finite parity cylinders")
    ):
        fail("P71 recurrence or scope mismatch")
    e19 = data.get("E19")
    if not isinstance(e19, dict) or e19.get("repository_status") != "VERIFIED_FINITE":
        fail("E19 finite audit missing")
    production = e19.get("production_cylinder_audit")
    direct = e19.get("literal_cross_check")
    if not isinstance(production, dict) or not isinstance(direct, dict):
        fail("E19 audit sections missing")
    expected_production = expected_cylinders(
        int(production.get("bound_H", 0)), int(production.get("depth_L", 0)), int(production.get("gap_cap", 0))
    )
    if production != expected_production:
        fail("E19 cylinder digest or counts mismatch")
    expected_direct = expected_literal(int(direct.get("bound_H", 0)), int(direct.get("depth_L", 0)), int(direct.get("gap_cap", 0)))
    if direct != expected_direct:
        fail("E19 literal cross-check mismatch")
    if data.get("mandatory_adversarial_audit") != expected_mandatory(int(production["depth_L"])):
        fail("Phase 11 mandatory adversarial mismatch")
    boundary = data.get("scalability_boundary")
    if not isinstance(boundary, dict) or boundary.get("target_certificate_found") is not False or "NG19" not in str(boundary.get("reason")):
        fail("pair-cylinder scalability boundary mismatch")
    return int(production["represented_pairs"]), int(production["nonempty_input_cylinders"])


def verify(artifact_dir: Path) -> dict[str, object]:
    verify_ladder(artifact_dir / "phase11_renewal_ladder.json", artifact_dir)
    audit = load(artifact_dir / "phase11_dropping_pair_audit.json")
    if audit.get("format") != "collatz-phase11-dropping-pair-audit-v1" or audit.get("proves_collatz") is not False:
        fail("dropping audit format or proof boundary mismatch")
    e18 = audit.get("E18")
    ng20 = audit.get("NG20")
    if not isinstance(e18, dict) or not isinstance(ng20, dict):
        fail("E18 or NG20 missing")
    rebuilt = expected_audit(int(e18.get("q_limit", 0)), int(ng20.get("regression_maximum_k", 0)))
    if audit != rebuilt:
        fail("E18/NG20 independent reconstruction mismatch")
    if int(e18["q_limit"]) == 4_961:
        if e18.get("failure_q") != [17, 22, 27, 29, 32, 34]:
            fail("Phase 11 production failure list mismatch")
        if e18.get("all_35_through_limit_pass") is not True:
            fail("Phase 11 production pass range mismatch")
        selected = {int(row["q"]): row for row in e18["selected_rows"]}
        if selected[4_961]["height_bound"] != 1_666_251:
            fail("Phase 11 q=4961 height mismatch")
    represented, cylinders = verify_pair_cylinder(artifact_dir / "phase11_pair_cylinder.json")
    report = (artifact_dir / "phase11_obstruction_report.md").read_text(encoding="utf-8")
    if (
        "What this result does not prove" not in report
        or "does not claim a proof or disproof" not in report
        or "Height-free no-go" not in report
        or "does not prove the eventual dropping-safe barrier" not in report
    ):
        fail("Phase 11 obstruction report boundary mismatch")
    return {
        "valid": True,
        "P69": "VERIFIED_THEOREM",
        "P70": "VERIFIED_THEOREM",
        "H70": "OPEN",
        "P71": "VERIFIED_THEOREM",
        "E18": "VERIFIED_FINITE",
        "E19": "VERIFIED_FINITE",
        "NG20": "REFUTED",
        "q_limit": int(e18["q_limit"]),
        "failure_q": e18["failure_q"],
        "represented_pairs": represented,
        "pair_cylinders": cylinders,
        "remaining_branches": ["nontrivial cycle", "infinite coefficient-safe tail", "eventual dropping-pair barrier"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, indent=2, sort_keys=True))
        return 1
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
