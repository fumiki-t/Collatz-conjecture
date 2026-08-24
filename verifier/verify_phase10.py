#!/usr/bin/env python3
"""Independently verify Phase 10 gap-renewal artifacts.

This module deliberately does not import ``src.phase10_search``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


Q0 = 72_057_431_991
K0 = 114_208_327_604
V = 2075 * (1 << 60)
W = 4_142_380_786
LEFT = (103_768_467_013, 65_470_613_321)
RIGHT = (10_439_860_591, 6_586_818_670)
A_BITS = "11101"
B_BITS = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail(f"{path.name} is not an object")
    return value


def digest_file(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest()


def pair(value: object) -> Fraction:
    if not isinstance(value, list) or len(value) != 2:
        fail("invalid rational pair")
    return Fraction(int(value[0]), int(value[1]))


def interval(value: object) -> tuple[Fraction, Fraction]:
    if not isinstance(value, dict):
        fail("invalid rational interval")
    result = pair(value.get("lower")), pair(value.get("upper"))
    if not result[0] < result[1]:
        fail("empty rational interval")
    return result


def dyadic_enclose(low: Fraction, high: Fraction, precision: int = 256) -> tuple[Fraction, Fraction]:
    denominator = 1 << precision
    left = low.numerator * denominator // low.denominator
    right = -((-high.numerator * denominator) // high.denominator)
    return Fraction(left, denominator), Fraction(right, denominator)


def exact_log(num: int, den: int = 1, terms: int = 240) -> tuple[Fraction, Fraction]:
    if num <= den or den <= 0:
        fail("invalid logarithm input")
    ratio = Fraction(num - den, num + den)
    ratio_squared = ratio * ratio
    term = ratio
    accumulator = Fraction(0)
    for order in range(terms):
        accumulator += term / (2 * order + 1)
        term *= ratio_squared
    lower = 2 * accumulator
    remainder = 2 * term / ((2 * terms + 1) * (1 - ratio_squared))
    return dyadic_enclose(lower, lower + remainder)


def step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def coefficient_stop(start: int) -> int:
    value = start
    multiplier = 1
    for depth in range(1, 20_001):
        if value & 1:
            multiplier *= 3
        value = step(value)
        if multiplier < 1 << depth:
            return depth
    fail(f"coefficient stopping overflow at {start}")


def bits_of(start: int, length: int) -> str:
    result = []
    value = start
    for _ in range(length):
        result.append("1" if value & 1 else "0")
        value = step(value)
    return "".join(result)


def prefix_match(left: str, right: str) -> int:
    count = 0
    for first, second in zip(left, right, strict=True):
        if first != second:
            break
        count += 1
    return count


def position_vectors(q: int):
    ceilings = [(3**index).bit_length() - 1 for index in range(q)]
    stack = [0] * q

    def extend(index: int, prior: int):
        if index == q:
            yield tuple(stack)
        else:
            for value in range(prior + 1, ceilings[index] + 1):
                stack[index] = value
                yield from extend(index + 1, value)

    stack[0] = 0
    yield from extend(1, 0)


def independent_cycle(word: str, b_value: int, d_value: int) -> tuple[int, int, int]:
    coefficient = denominator = 1
    constant = 0
    minimum = None
    positive = 0
    for index, bit in enumerate(word, 1):
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
        comparison = (coefficient - denominator) * b_value + constant * d_value
        if index == len(word):
            if comparison:
                fail("formal rational cycle does not close")
        else:
            if coefficient < denominator or comparison < 0:
                fail("formal rational cycle is not source-minimal")
            minimum = comparison if minimum is None else min(minimum, comparison)
            positive += comparison > 0
    return minimum or 0, positive, 0


def rebuild_finite_layers(maximum_q: int) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    gap_result = []
    cycle_result = []
    total_rows = 0
    for q in range(1, maximum_q + 1):
        p_value = 3**q
        k = p_value.bit_length()
        q_value = 1 << k
        d_value = q_value - p_value
        source_inverse = pow(p_value, -1, q_value)
        gap_inverse = pow(p_value, -1, d_value)
        gap_hash = hashlib.sha256()
        cycle_hash = hashlib.sha256()
        row_count = nonnegative = mod_four = box_count = 0
        smallest = largest = None
        for positions in position_vectors(q):
            flags = ["0"] * k
            for position in positions:
                flags[position] = "1"
            word = "".join(flags)
            b_value = sum(3 ** (q - 1 - index) * (1 << position) for index, position in enumerate(positions))
            source = (-b_value * source_inverse) % q_value
            endpoint_numerator = p_value * source + b_value
            if endpoint_numerator % q_value:
                fail("finite gap affine equation mismatch")
            endpoint = endpoint_numerator // q_value
            gap = endpoint - source
            residue = b_value * gap_inverse % d_value
            quotient_numerator = b_value - q_value * residue
            if quotient_numerator % d_value:
                fail("finite gap quotient mismatch")
            quotient = quotient_numerator // d_value
            common_divisor = math.gcd(b_value, d_value)
            if b_value != d_value * source + q_value * gap:
                fail("finite gap identity mismatch")
            if residue != gap % d_value or common_divisor != math.gcd(gap, d_value):
                fail("finite gap congruence/gcd mismatch")
            if residue == gap and source % 4 == endpoint % 4 == 3 and residue % 4:
                fail("finite gap mod-four mismatch")
            minimum, positive, terminal = independent_cycle(word, b_value, d_value)
            gap_hash.update(
                (
                    f"{q}|{k}|{','.join(map(str, positions))}|{b_value}|{d_value}|{source}|{endpoint}|"
                    f"{gap}|{residue}|{quotient}|{common_divisor}\n"
                ).encode("ascii")
            )
            cycle_hash.update(
                f"{q}|{k}|{','.join(map(str, positions))}|{minimum}|{positive}|{terminal}|{common_divisor}\n".encode("ascii")
            )
            record = {
                "parity_word": word,
                "odd_positions": list(positions),
                "B": b_value,
                "D": d_value,
                "r2": source,
                "r3": endpoint,
                "d": gap,
                "rho": residue,
                "m": quotient,
                "gcd_B_D": common_divisor,
            }
            if smallest is None or (gap, word) < (smallest["d"], smallest["parity_word"]):
                smallest = record
            if largest is None or (gap, word) > (largest["d"], largest["parity_word"]):
                largest = record
            row_count += 1
            nonnegative += gap >= 0
            mod_four += source % 4 == endpoint % 4 == 3
            box_count += V < source < 2**72 and 0 <= gap <= W and endpoint % 36 in (7, 19)
        total_rows += row_count
        gap_result.append(
            {
                "q": q,
                "K": k,
                "enumerated_words": row_count,
                "row_digest_sha256": gap_hash.hexdigest(),
                "nonnegative_gap_count": nonnegative,
                "both_endpoints_3_mod_4_count": mod_four,
                "phase10_near_box_count": box_count,
                "minimum_d_record": smallest,
                "maximum_d_record": largest,
            }
        )
        cycle_result.append(
            {
                "q": q,
                "K": k,
                "enumerated_words": row_count,
                "cycle_digest_sha256": cycle_hash.hexdigest(),
                "all_formal_cycles_close": True,
                "all_sources_are_cycle_minima": True,
            }
        )
    return gap_result, cycle_result, total_rows


def verify_gap(path: Path, artifact_dir: Path) -> dict[str, int]:
    data = load(path)
    if data.get("format") != "collatz-phase10-gap-modulus-v1" or data.get("proves_collatz") is not False:
        fail("gap-modulus claim boundary mismatch")
    p63 = data.get("P63")
    if not isinstance(p63, dict) or p63.get("repository_status") != "CONDITIONAL" or p63.get("rho_mod_4") != 0 or p63.get("proves_C04") is not False:
        fail("P63 status/mod-four boundary mismatch")
    if p63.get("exact_identities") != ["B=D*r2+Q*d", "B=P*d (mod D)", "d=B*P^(-1) (mod D)"]:
        fail("P63 gap identity mismatch")
    certificate = data.get("D_gt_W_certificate")
    if not isinstance(certificate, dict) or certificate.get("direct_q0_powers_constructed") is not False:
        fail("D>W certificate boundary mismatch")
    ln2, ln3 = exact_log(2), exact_log(3)
    expected_gap = (K0 * ln2[0] - Q0 * ln3[1], K0 * ln2[1] - Q0 * ln3[0])
    if interval(certificate.get("x_Kln2_minus_qln3")) != expected_gap:
        fail("D>W logarithm mismatch")
    if certificate.get("three_power_used") != 44 or certificate.get("three_power_times_x_lower_gt_W") is not True or not 3**44 * expected_gap[0] > W:
        fail("D>W lower-bound witness mismatch")
    canonical = data.get("canonical_residue_range_certificate")
    if (
        not isinstance(canonical, dict)
        or canonical.get("K0_gt_72") is not True
        or canonical.get("q0_at_least_46") is not True
        or canonical.get("three_power_46_gt_two_power_72") is not True
        or not K0 > 72
        or not Q0 >= 46
        or not 3**46 > 2**72
        or "both residues are canonical" not in str(canonical.get("conclusion"))
    ):
        fail("gap canonical residue range mismatch")
    if p63.get("near_box_conditions") != ["q=q0", "K=K0", "V<N<2^72", "0<=d=X-N<=W", "X<2^72"]:
        fail("P63 near-box conditions mismatch")
    audit = data.get("finite_first_crossing_audit")
    if not isinstance(audit, dict) or audit.get("repository_status") != "VERIFIED_FINITE":
        fail("finite gap audit missing")
    maximum = int(audit.get("maximum_q", 0))
    layers, _cycles, total = rebuild_finite_layers(maximum)
    if audit.get("layers") != layers or audit.get("total_words") != total:
        fail("finite gap layer/digest mismatch")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("phase9_endpoint_sha256") != digest_file(artifact_dir / "phase9_endpoint_displacement.json") or dependencies.get("phase9_two_sided_sha256") != digest_file(artifact_dir / "phase9_two_sided_residues.json"):
        fail("gap Phase 9 dependency hash mismatch")
    return {"maximum_q": maximum, "total_words": total}


def verify_renewal(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase10-renewal-barrier-v1" or data.get("proves_collatz") is not False:
        fail("renewal claim boundary mismatch")
    p64 = data.get("P64")
    if not isinstance(p64, dict) or p64.get("repository_status") != "CONDITIONAL" or "K0-1" not in str(p64.get("conclusion")):
        fail("P64 status/conclusion mismatch")
    crossing_rule = data.get("first_crossing_index_rule")
    q0_log_gap = (K0 * exact_log(2)[0] - Q0 * exact_log(3)[1], K0 * exact_log(2)[1] - Q0 * exact_log(3)[0])
    if (
        not isinstance(crossing_rule, dict)
        or crossing_rule.get("q0_index") != [K0, Q0]
        or crossing_rule.get("q0_gap_strictly_between_zero_and_ln2") is not True
        or crossing_rule.get("safe_through") != K0 - 1
        or "strictly increase" not in str(crossing_rule.get("rule"))
        or not (q0_log_gap[0] > 0 and q0_log_gap[1] < exact_log(2)[0])
    ):
        fail("renewal first-crossing index rule mismatch")
    parents = data.get("stern_brocot_certificate")
    determinant = RIGHT[0] * LEFT[1] - RIGHT[1] * LEFT[0]
    if not isinstance(parents, dict) or parents.get("left_parent") != list(LEFT) or parents.get("right_upper_parent") != list(RIGHT) or parents.get("farey_determinant") != determinant or determinant != 1:
        fail("renewal Stern-Brocot parents mismatch")
    if parents.get("mediant") != [K0, Q0] or Fraction(LEFT[0] + RIGHT[0], LEFT[1] + RIGHT[1]) != Fraction(K0, Q0):
        fail("renewal Stern-Brocot mediant mismatch")
    margins = data.get("exact_margins")
    if not isinstance(margins, dict):
        fail("renewal exact margins missing")
    ln2 = exact_log(2)
    ln3 = exact_log(3)
    upper = exact_log(3 * V + 1, V)
    required = exact_log(V + W, V, 96)
    gap = (RIGHT[0] * ln2[0] - RIGHT[1] * upper[1], RIGHT[0] * ln2[1] - RIGHT[1] * upper[0])
    parent_margin = (gap[0] - required[1], gap[1] - required[0])
    unit_margin = (ln2[0] / RIGHT[1] - required[1], ln2[1] / RIGHT[1] - required[0])
    expected = {
        "ln2": ln2,
        "ln3": ln3,
        "ln_3_plus_1_over_V": upper,
        "ln_1_plus_W_over_V": required,
        "right_parent_gap": gap,
        "right_parent_gap_minus_required_margin": parent_margin,
        "ln2_over_right_denominator_minus_required_margin": unit_margin,
    }
    for key, value in expected.items():
        if interval(margins.get(key)) != value:
            fail(f"renewal {key} interval mismatch")
    if parent_margin[0] <= 0 or unit_margin[0] <= 0 or margins.get("all_lower_bounds_strictly_positive") is not True:
        fail("renewal positive margin failed")
    case_split = data.get("lattice_case_split")
    if not isinstance(case_split, dict) or "h=q_R*K-K_R*q>=0" not in str(case_split.get("h_definition")):
        fail("renewal lattice case split missing")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("phase7_symbolic_sha256") != digest_file(artifact_dir / "phase7_symbolic_certificate.json") or dependencies.get("phase9_endpoint_sha256") != digest_file(artifact_dir / "phase9_endpoint_displacement.json"):
        fail("renewal dependency hash mismatch")
    return {"safe_through": K0 - 1, "right_parent": list(RIGHT), "parent_margin_positive": True}


class Fenwick:
    def __init__(self, size: int) -> None:
        self.values = [0] * (size + 1)

    def add(self, index: int) -> None:
        while index < len(self.values):
            self.values[index] += 1
            index += index & -index

    def prefix(self, index: int) -> int:
        total = 0
        while index:
            total += self.values[index]
            index -= index & -index
        return total

    def select(self, order: int) -> int:
        index = 0
        bit = 1 << (len(self.values).bit_length() - 1)
        while bit:
            candidate = index + bit
            if candidate < len(self.values) and self.values[candidate] < order:
                index = candidate
                order -= self.values[candidate]
            bit >>= 1
        return index + 1


def record_rows(path: Path, bound: int) -> list[list[int]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            [int(row["start"]), int(row["coefficient_stopping_time"])]
            for row in csv.DictReader(stream)
            if int(row["start"]) <= bound
        ]


def independent_spacing(bound: int) -> tuple[list[dict[str, object]], str, list[list[int]]]:
    stopping = [0] * (bound + 1)
    by_time: dict[int, list[int]] = defaultdict(list)
    digest = hashlib.sha256()
    records = []
    record_time = 0
    for start in range(2, bound + 1):
        value = coefficient_stop(start)
        stopping[start] = value
        by_time[value].append(start)
        digest.update(f"{start}:{value}\n".encode("ascii"))
        if value > record_time:
            record_time = value
            records.append([start, value])
    maximum = max(stopping)
    tree = Fenwick(bound)
    active = 0
    best: tuple[int, int, int] | None = None
    reversed_layers = []
    for k in range(maximum, -1, -1):
        if k < maximum:
            for start in by_time.get(k + 1, []):
                before = tree.prefix(start - 1)
                total = active
                left = tree.select(before) if before else None
                right = tree.select(before + 1) if before < total else None
                tree.add(start)
                active += 1
                for first, second in ((left, start), (start, right)):
                    if first is not None and second is not None:
                        candidate = (second - first, first, second)
                        if best is None or candidate < best:
                            best = candidate
        row: dict[str, object] = {"k": k, "safe_count": active}
        if best is None:
            row.update({"delta": None, "left": None, "right": None})
        else:
            delta, left, right = best
            left_word, right_word = bits_of(left, k), bits_of(right, k)
            row.update(
                {
                    "delta": delta,
                    "left": left,
                    "right": right,
                    "left_stopping_time": stopping[left],
                    "right_stopping_time": stopping[right],
                    "common_parity_prefix_length": prefix_match(left_word, right_word),
                    "left_parity_prefix": left_word,
                    "right_parity_prefix": right_word,
                }
            )
        reversed_layers.append(row)
    return list(reversed(reversed_layers)), digest.hexdigest(), records


def independent_adversarial(bound: int) -> dict[str, object]:
    first_family = []
    for exponent in range(1, 65):
        start = (1 << exponent) - 1
        if bits_of(start, exponent) != "1" * exponent:
            fail("2^m-1 adversarial mismatch")
        if start <= bound:
            first_family.append([exponent, start, coefficient_stop(start)])
    second_family = []
    for exponent in range(1, 33):
        start = (1 << (3 * exponent)) - 5
        if bits_of(start, 3 * exponent) != "110" * exponent:
            fail("8^m-5 adversarial mismatch")
        if start <= bound:
            second_family.append([exponent, start, coefficient_stop(start)])
    block_safe = 0
    for mask in range(4096):
        bits = "".join("111" if mask & (1 << index) else "110" for index in range(12))
        odd = 0
        for depth, bit in enumerate(bits, 1):
            odd += bit == "1"
            if 3**odd < 1 << depth:
                break
        else:
            block_safe += 1
    safe = crossed = 0
    histogram: dict[int, int] = defaultdict(int)
    for r in range(1, 33):
        for s in range(1, 33):
            odd = 0
            crossing = None
            for depth, bit in enumerate(A_BITS * r + B_BITS * s, 1):
                odd += bit == "1"
                if 3**odd < 1 << depth:
                    crossing = depth
                    break
            if crossing is None:
                safe += 1
            else:
                crossed += 1
                histogram[crossing] += 1
    return {
        "2^m_minus_1": {"scope": "1<=m<=64", "prefix": "1^m", "within_spacing_bound": first_family},
        "8^m_minus_5": {"scope": "1<=m<=32", "prefix": "(110)^m", "within_spacing_bound": second_family},
        "(110|111)^star": {"block_count": 12, "words_checked": 4096, "coefficient_safe": block_safe},
        "A^rB^s": {"scope": "1<=r,s<=32", "pairs": 1024, "fully_coefficient_safe": safe, "first_crossing": crossed, "crossing_depth_histogram": [[key, histogram[key]] for key in sorted(histogram)]},
    }


def verify_spacing(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase10-safe-pair-spacing-v1" or data.get("proves_collatz") is not False:
        fail("spacing claim boundary mismatch")
    e15 = data.get("E15")
    if not isinstance(e15, dict) or e15.get("repository_status") != "VERIFIED_FINITE":
        fail("E15 status mismatch")
    bound = int(e15.get("bound_H", 0))
    layers, digest, records = independent_spacing(bound)
    if e15.get("layers") != layers or e15.get("stopping_time_digest_sha256") != digest:
        fail("spacing layers/digest mismatch")
    changes = []
    prior_delta = object()
    transitions = []
    prior_pair = object()
    for row in layers:
        if row["delta"] != prior_delta:
            changes.append(row)
            prior_delta = row["delta"]
        pair_value = (row["left"], row["right"])
        if pair_value != prior_pair:
            transitions.append(row)
            prior_pair = pair_value
    defined = [row for row in layers if row["delta"] is not None]
    if not defined or e15.get("deepest_defined_spacing") != defined[-1] or e15.get("spacing_records") != changes or e15.get("witness_transitions") != transitions:
        fail("spacing records/deepest witness mismatch")
    if e15.get("phase6_M_records_reconstructed") != records or records != record_rows(artifact_dir / "M_search_records.csv", bound):
        fail("spacing Phase 6 record reconstruction mismatch")
    if data.get("mandatory_adversarial_audit") != independent_adversarial(bound):
        fail("spacing mandatory adversarial mismatch")
    recursion = data.get("recursive_difference_rule")
    if not isinstance(recursion, dict) or recursion.get("verified_finite") is not True or recursion.get("target_certificate_found") is not False:
        fail("spacing recursive-rule boundary mismatch")
    shortcut = recursion.get("strict_growth_shortcut")
    expected_shortcut = {
        "repository_status": "REFUTED",
        "hypothesis": "Delta_(k+1)(H)>Delta_k(H) whenever both values are defined",
        "smallest_production_counterexample": {"H": bound, "k": 2, "Delta_k": layers[2]["delta"], "Delta_k_plus_1": layers[3]["delta"]},
        "surviving_rule": "Delta_(k+1)(H)>=Delta_k(H) whenever both values are defined",
    }
    if shortcut != expected_shortcut or layers[2]["delta"] != layers[3]["delta"]:
        fail("spacing strict-growth counterexample mismatch")
    c05 = data.get("C05")
    if not isinstance(c05, dict) or c05.get("repository_status") != "OPEN" or c05.get("target_evaluated") is not False:
        fail("C05 was improperly promoted")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, dict) or dependencies.get("M_search_records_sha256") != digest_file(artifact_dir / "M_search_records.csv"):
        fail("spacing dependency hash mismatch")
    return {"bound": bound, "deepest": defined[-1], "target": "OPEN"}


def verify_cycle(path: Path) -> dict[str, int]:
    data = load(path)
    if data.get("format") != "collatz-phase10-rational-cycle-v1" or data.get("proves_collatz") is not False:
        fail("rational-cycle claim boundary mismatch")
    p65 = data.get("P65")
    if not isinstance(p65, dict) or p65.get("repository_status") != "VERIFIED_THEOREM" or "gcd(B,D)=gcd(d,D)" not in str(p65.get("statement")):
        fail("P65 theorem/gcd statement mismatch")
    if not str(p65.get("prefix_difference_numerator")).startswith("(3^a_j-2^j)*B+B_j*D>=0"):
        fail("rational-cycle minimum identity mismatch")
    finite = data.get("finite_audit")
    if not isinstance(finite, dict) or finite.get("repository_status") != "VERIFIED_FINITE":
        fail("rational-cycle finite audit missing")
    maximum = int(finite.get("maximum_q", 0))
    _gap, cycles, total = rebuild_finite_layers(maximum)
    if finite.get("layers") != cycles or finite.get("total_words") != total:
        fail("rational-cycle layer/digest mismatch")
    context = data.get("external_context")
    if not isinstance(context, dict) or context.get("theorem_used") is not False or context.get("claim_of_novelty") is not False:
        fail("Christoffel external-context boundary mismatch")
    return {"maximum_q": maximum, "total_words": total}


def verify(artifact_dir: Path) -> dict[str, object]:
    gap = verify_gap(artifact_dir / "phase10_gap_modulus.json", artifact_dir)
    renewal = verify_renewal(artifact_dir / "phase10_renewal_barrier.json", artifact_dir)
    spacing = verify_spacing(artifact_dir / "phase10_safe_pair_spacing.json", artifact_dir)
    cycle = verify_cycle(artifact_dir / "phase10_rational_cycle.json")
    report = (artifact_dir / "phase10_obstruction_report.md").read_text(encoding="utf-8")
    if "What this result does not prove" not in report or "does not claim a proof or disproof" not in report or "C05 remains OPEN" not in report:
        fail("Phase 10 obstruction report boundary mismatch")
    return {
        "valid": True,
        "gap_modulus": gap,
        "renewal_barrier": renewal,
        "safe_pair_spacing": spacing,
        "rational_cycle": cycle,
        "external_inputs_reproved": {"X02": False, "Christoffel_extremality": False},
        "C04": "OPEN",
        "C05": "OPEN",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    try:
        result = verify(arguments.artifact_dir)
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, sort_keys=True), file=sys.stderr)
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if arguments.output:
        arguments.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
