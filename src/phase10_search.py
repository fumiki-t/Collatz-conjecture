#!/usr/bin/env python3
"""Generate exact Phase 10 gap-renewal artifacts.

Acceptance decisions use arbitrary-precision integers and rational intervals.
The q0 powers are never constructed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import heapq
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
LEFT_PARENT = (103_768_467_013, 65_470_613_321)
RIGHT_PARENT = (10_439_860_591, 6_586_818_670)
DEFAULT_SPACING_BOUND = 1_500_000
DEFAULT_LAYER_Q = 15
A_WORD = "11101"
B_WORD = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def encode_fraction(value: Fraction) -> list[str]:
    return [str(value.numerator), str(value.denominator)]


def encode_interval(lower: Fraction, upper: Fraction) -> dict[str, list[str]]:
    if not lower < upper:
        raise ValueError("invalid interval")
    return {"lower": encode_fraction(lower), "upper": encode_fraction(upper)}


def outward(lower: Fraction, upper: Fraction, bits: int = 256) -> tuple[Fraction, Fraction]:
    scale = 1 << bits
    low = lower.numerator * scale // lower.denominator
    high = -((-upper.numerator * scale) // upper.denominator)
    return Fraction(low, scale), Fraction(high, scale)


def log_interval(numerator: int, denominator: int = 1, *, terms: int = 240) -> tuple[Fraction, Fraction]:
    if not numerator > denominator > 0:
        raise ValueError("log enclosure requires numerator>denominator>0")
    z = Fraction(numerator - denominator, numerator + denominator)
    z2 = z * z
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += power / (2 * index + 1)
        power *= z2
    low = 2 * total
    high = low + 2 * power / ((2 * terms + 1) * (1 - z2))
    return outward(low, high)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def shortcut_step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def coefficient_stopping_time(start: int, limit: int = 20_000) -> int:
    value = start
    odd_power = 1
    for depth in range(1, limit + 1):
        if value % 2:
            odd_power *= 3
        value = shortcut_step(value)
        if odd_power < 1 << depth:
            return depth
    raise RuntimeError(f"coefficient-stopping limit reached for {start}")


def parity_prefix(start: int, length: int) -> str:
    value = start
    bits: list[str] = []
    for _ in range(length):
        bits.append(str(value & 1))
        value = shortcut_step(value)
    return "".join(bits)


def common_prefix_length(left: str, right: str) -> int:
    for index, (first, second) in enumerate(zip(left, right, strict=True)):
        if first != second:
            return index
    return len(left)


def first_crossing_positions(q: int):
    floors = tuple((3**index).bit_length() - 1 for index in range(q))
    positions = [0] * q

    def visit(index: int, previous: int):
        if index == q:
            yield tuple(positions), floors
            return
        for position in range(previous + 1, floors[index] + 1):
            positions[index] = position
            yield from visit(index + 1, position)

    positions[0] = 0
    yield from visit(1, 0)


def word_and_constant(q: int, k: int, positions: tuple[int, ...]) -> tuple[str, int]:
    position_set = set(positions)
    word = "".join("1" if index in position_set else "0" for index in range(k))
    constant = sum(3 ** (q - 1 - index) * (1 << position) for index, position in enumerate(positions))
    return word, constant


def rational_cycle_check(word: str, total_constant: int, difference: int) -> tuple[int, int, int]:
    prefix_coefficient = 1
    prefix_constant = 0
    prefix_denominator = 1
    minimum_numerator: int | None = None
    strict_above = 0
    for depth, bit in enumerate(word, 1):
        if bit == "1":
            prefix_coefficient *= 3
            prefix_constant = 3 * prefix_constant + prefix_denominator
        prefix_denominator *= 2
        numerator = (prefix_coefficient - prefix_denominator) * total_constant + prefix_constant * difference
        if depth < len(word):
            if prefix_coefficient < prefix_denominator or numerator < 0:
                raise AssertionError("coefficient-safe rational-cycle minimum failed")
            minimum_numerator = numerator if minimum_numerator is None else min(minimum_numerator, numerator)
            strict_above += numerator > 0
        elif numerator != 0:
            raise AssertionError("rational-cycle closure failed")
    return minimum_numerator or 0, strict_above, 0


def finite_gap_cycle_audit(maximum_q: int) -> tuple[list[dict[str, object]], list[dict[str, object]], int]:
    gap_layers: list[dict[str, object]] = []
    cycle_layers: list[dict[str, object]] = []
    grand_total = 0
    for q in range(1, maximum_q + 1):
        power = 3**q
        k = power.bit_length()
        modulus = 1 << k
        difference = modulus - power
        inverse_power_mod_two = pow(power, -1, modulus)
        inverse_power_mod_gap = pow(power, -1, difference)
        gap_digest = hashlib.sha256()
        cycle_digest = hashlib.sha256()
        count = nonnegative = divisible_four = near_box = 0
        min_record = max_record = None
        for positions, _floors in first_crossing_positions(q):
            word, constant = word_and_constant(q, k, positions)
            r2 = (-constant * inverse_power_mod_two) % modulus
            numerator = power * r2 + constant
            if numerator % modulus:
                raise AssertionError("canonical affine equation failed")
            r3 = numerator // modulus
            d = r3 - r2
            rho = constant * inverse_power_mod_gap % difference
            m_numerator = constant - modulus * rho
            if m_numerator % difference:
                raise AssertionError("gap quotient is not integral")
            m = m_numerator // difference
            gcd_value = math.gcd(constant, difference)
            if constant != difference * r2 + modulus * d:
                raise AssertionError("gap identity failed")
            if rho != d % difference or gcd_value != math.gcd(d, difference):
                raise AssertionError("gap residue/gcd identity failed")
            if rho == d and r2 % 4 == r3 % 4 == 3 and rho % 4:
                raise AssertionError("mod-4 gap consequence failed")
            minimum_numerator, strict_above, terminal = rational_cycle_check(word, constant, difference)
            line = (
                f"{q}|{k}|{','.join(map(str, positions))}|{constant}|{difference}|{r2}|{r3}|"
                f"{d}|{rho}|{m}|{gcd_value}\n"
            ).encode("ascii")
            gap_digest.update(line)
            cycle_digest.update(
                f"{q}|{k}|{','.join(map(str, positions))}|{minimum_numerator}|{strict_above}|{terminal}|{gcd_value}\n".encode("ascii")
            )
            record = {
                "parity_word": word,
                "odd_positions": list(positions),
                "B": constant,
                "D": difference,
                "r2": r2,
                "r3": r3,
                "d": d,
                "rho": rho,
                "m": m,
                "gcd_B_D": gcd_value,
            }
            if min_record is None or (d, word) < (min_record["d"], min_record["parity_word"]):
                min_record = record
            if max_record is None or (d, word) > (max_record["d"], max_record["parity_word"]):
                max_record = record
            count += 1
            nonnegative += d >= 0
            divisible_four += r2 % 4 == r3 % 4 == 3
            near_box += V < r2 < 2**72 and 0 <= d <= W and r3 % 36 in (7, 19)
        grand_total += count
        gap_layers.append(
            {
                "q": q,
                "K": k,
                "enumerated_words": count,
                "row_digest_sha256": gap_digest.hexdigest(),
                "nonnegative_gap_count": nonnegative,
                "both_endpoints_3_mod_4_count": divisible_four,
                "phase10_near_box_count": near_box,
                "minimum_d_record": min_record,
                "maximum_d_record": max_record,
            }
        )
        cycle_layers.append(
            {
                "q": q,
                "K": k,
                "enumerated_words": count,
                "cycle_digest_sha256": cycle_digest.hexdigest(),
                "all_formal_cycles_close": True,
                "all_sources_are_cycle_minima": True,
            }
        )
    return gap_layers, cycle_layers, grand_total


def gap_modulus_data(artifact_dir: Path, gap_layers: list[dict[str, object]], total: int) -> dict[str, object]:
    ln2 = log_interval(2)
    ln3 = log_interval(3)
    gap = (K0 * ln2[0] - Q0 * ln3[1], K0 * ln2[1] - Q0 * ln3[0])
    if not 3**44 * gap[0] > W:
        raise AssertionError("D>W certificate failed")
    return {
        "format": "collatz-phase10-gap-modulus-v1",
        "P63": {
            "repository_status": "CONDITIONAL",
            "definitions": ["P=3^q", "Q=2^K", "D=Q-P", "rho=[B*P^(-1)]_D", "m=(B-Q*rho)/D"],
            "exact_identities": ["B=D*r2+Q*d", "B=P*d (mod D)", "d=B*P^(-1) (mod D)"],
            "near_box_conditions": ["q=q0", "K=K0", "V<N<2^72", "0<=d=X-N<=W", "X<2^72"],
            "q0_near_box_equivalence": "under the near-box conditions, D>W gives rho=d; then m=r2=N and X=m+rho. Conversely 0<=rho<=W, 0<m,m+rho<2^72 and P*m+B=Q*(m+rho) reconstruct the canonical residues r2=m, r3=m+rho, hence N=m, d=rho and X=m+rho",
            "least_counterexample_mod_4": "N=3 mod 4 because N=1 mod 4 would give T^2(N)=(3N+1)/4<N",
            "endpoint_mod_4_dependency": "P61 gives X=3 mod 4",
            "rho_mod_4": 0,
            "proves_C04": False,
        },
        "D_gt_W_certificate": {
            "q0_at_least_44": Q0 >= 44,
            "x_Kln2_minus_qln3": encode_interval(*gap),
            "exp_x_minus_1_gt_x": True,
            "three_power_used": 44,
            "three_power_times_x_lower_gt_W": 3**44 * gap[0] > W,
            "direct_q0_powers_constructed": False,
        },
        "canonical_residue_range_certificate": {
            "K0_gt_72": K0 > 72,
            "q0_at_least_46": Q0 >= 46,
            "three_power_46_gt_two_power_72": 3**46 > 2**72,
            "conclusion": "0<m,m+rho<2^72 implies m<Q=2^K0 and m+rho<P=3^q0, so both residues are canonical",
        },
        "finite_first_crossing_audit": {
            "repository_status": "VERIFIED_FINITE",
            "maximum_q": len(gap_layers),
            "total_words": total,
            "row_encoding": "q|K|odd_positions|B|D|r2|r3|d|rho|m|gcd(B,D) newline",
            "layers": gap_layers,
        },
        "dependencies": {
            "phase9_endpoint_sha256": sha256(artifact_dir / "phase9_endpoint_displacement.json"),
            "phase9_two_sided_sha256": sha256(artifact_dir / "phase9_two_sided_residues.json"),
            "X02_reproved": False,
        },
        "what_this_result_does_not_prove": "The gap reduction is exact but supplies no theorem excluding the q0 residue rho or proving C04.",
        "proves_collatz": False,
    }


def renewal_barrier_data(artifact_dir: Path) -> dict[str, object]:
    ln2 = log_interval(2)
    ln3 = log_interval(3)
    ln_upper = log_interval(3 * V + 1, V)
    renewal_log = log_interval(V + W, V, terms=96)
    left = Fraction(*LEFT_PARENT)
    right = Fraction(*RIGHT_PARENT)
    alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    beta = (ln_upper[0] / ln2[1], ln_upper[1] / ln2[0])
    candidate = Fraction(K0, Q0)
    if not left < alpha[0] < alpha[1] < candidate < beta[0] < beta[1] < right:
        raise AssertionError("Phase 7 parent ordering changed")
    determinant = RIGHT_PARENT[0] * LEFT_PARENT[1] - RIGHT_PARENT[1] * LEFT_PARENT[0]
    if determinant != 1 or candidate != Fraction(LEFT_PARENT[0] + RIGHT_PARENT[0], LEFT_PARENT[1] + RIGHT_PARENT[1]):
        raise AssertionError("Stern-Brocot certificate failed")
    parent_gap = (
        RIGHT_PARENT[0] * ln2[0] - RIGHT_PARENT[1] * ln_upper[1],
        RIGHT_PARENT[0] * ln2[1] - RIGHT_PARENT[1] * ln_upper[0],
    )
    q0_gap = (K0 * ln2[0] - Q0 * ln3[1], K0 * ln2[1] - Q0 * ln3[0])
    parent_margin = (parent_gap[0] - renewal_log[1], parent_gap[1] - renewal_log[0])
    unit_margin = (ln2[0] / RIGHT_PARENT[1] - renewal_log[1], ln2[1] / RIGHT_PARENT[1] - renewal_log[0])
    if parent_margin[0] <= 0 or unit_margin[0] <= 0:
        raise AssertionError("renewal parent margin did not close")
    return {
        "format": "collatz-phase10-renewal-barrier-v1",
        "P64": {
            "repository_status": "CONDITIONAL",
            "scope": "least-counterexample orbit point S with N<=S<=N+W and every earlier orbit value at least N>V",
            "necessary_inequality": "V/(V+W)<=(3+1/V)^q/2^K",
            "conclusion": f"no coefficient first crossing with q<{Q0}; S is coefficient-safe through K0-1 steps",
            "distinct_pair_consequence": "if d>0, N and X=N+d are distinct K0-1-step coefficient-safe integers at distance at most W",
        },
        "first_crossing_index_rule": {
            "rule": "for q>0, a coefficient first crossing occurs at K=ceil(q*log2(3)); these indices strictly increase with q",
            "q0_index": [K0, Q0],
            "q0_gap_strictly_between_zero_and_ln2": q0_gap[0] > 0 and q0_gap[1] < ln2[0],
            "strict_increase_reason": "multiplication by 3 raises log2 by more than 1",
            "safe_through": K0 - 1,
        },
        "stern_brocot_certificate": {
            "left_parent": list(LEFT_PARENT),
            "right_upper_parent": list(RIGHT_PARENT),
            "farey_determinant": determinant,
            "mediant": [K0, Q0],
            "ordering": "left<log2(3)<K0/q0<log2(3+1/V)<right",
            "denominator_minimum_inside_parent_interval": Q0,
        },
        "exact_margins": {
            "ln2": encode_interval(*ln2),
            "ln3": encode_interval(*ln3),
            "ln_3_plus_1_over_V": encode_interval(*ln_upper),
            "ln_1_plus_W_over_V": encode_interval(*renewal_log),
            "right_parent_gap": encode_interval(*parent_gap),
            "right_parent_gap_minus_required_margin": encode_interval(*parent_margin),
            "ln2_over_right_denominator_minus_required_margin": encode_interval(*unit_margin),
            "all_lower_bounds_strictly_positive": True,
        },
        "lattice_case_split": {
            "h_definition": "h=q_R*K-K_R*q>=0 for every crossing ratio K/q>=K_R/q_R",
            "h_zero": "coprimality forces (K,q)=t*(K_R,q_R), so the logarithmic gap is at least the right-parent gap",
            "h_positive": "the logarithmic gap is q*g_R/q_R+h*ln(2)/q_R and exceeds ln(1+W/V)",
            "q_zero": "2^(-K)<=1/2<V/(V+W)",
        },
        "dependencies": {
            "phase7_symbolic_sha256": sha256(artifact_dir / "phase7_symbolic_certificate.json"),
            "phase9_endpoint_sha256": sha256(artifact_dir / "phase9_endpoint_displacement.json"),
            "X02_reproved": False,
        },
        "what_this_result_does_not_prove": "P64 is conditional on the least-counterexample orbit and X02; it neither proves that N exists nor excludes a q0 or later crossing.",
        "proves_collatz": False,
    }


def direct_record_rows(path: Path, bound: int) -> list[tuple[int, int]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return [
            (int(row["start"]), int(row["coefficient_stopping_time"]))
            for row in csv.DictReader(stream)
            if int(row["start"]) <= bound
        ]


def spacing_layers(bound: int) -> tuple[list[dict[str, object]], str, list[tuple[int, int]]]:
    times = [0, 0]
    digest = hashlib.sha256()
    records: list[tuple[int, int]] = []
    best = 0
    groups: dict[int, list[int]] = defaultdict(list)
    for start in range(2, bound + 1):
        stopping = coefficient_stopping_time(start)
        times.append(stopping)
        digest.update(f"{start}:{stopping}\n".encode("ascii"))
        groups[stopping].append(start)
        if stopping > best:
            best = stopping
            records.append((start, stopping))
    previous = [index - 1 for index in range(bound + 1)]
    following = [index + 1 for index in range(bound + 1)]
    alive = bytearray(b"\1") * (bound + 1)
    previous[2] = 0
    following[bound] = 0
    heap = [(1, start, start + 1) for start in range(2, bound)]
    heapq.heapify(heap)
    safe_count = bound - 1
    layers: list[dict[str, object]] = []
    for k in range(0, max(times) + 1):
        if k:
            for start in groups.get(k, []):
                left, right = previous[start], following[start]
                alive[start] = 0
                safe_count -= 1
                if left:
                    following[left] = right
                if right:
                    previous[right] = left
                if left and right:
                    heapq.heappush(heap, (right - left, left, right))
        while heap and (
            not alive[heap[0][1]]
            or not alive[heap[0][2]]
            or following[heap[0][1]] != heap[0][2]
        ):
            heapq.heappop(heap)
        row: dict[str, object] = {"k": k, "safe_count": safe_count}
        if heap:
            delta, left, right = heap[0]
            left_word = parity_prefix(left, k)
            right_word = parity_prefix(right, k)
            row.update(
                {
                    "delta": delta,
                    "left": left,
                    "right": right,
                    "left_stopping_time": times[left],
                    "right_stopping_time": times[right],
                    "common_parity_prefix_length": common_prefix_length(left_word, right_word),
                    "left_parity_prefix": left_word,
                    "right_parity_prefix": right_word,
                }
            )
        else:
            row.update({"delta": None, "left": None, "right": None})
        layers.append(row)
    return layers, digest.hexdigest(), records


def adversarial_audit(bound: int) -> dict[str, object]:
    power_rows = []
    for exponent in range(1, 65):
        start = (1 << exponent) - 1
        prefix = parity_prefix(start, exponent)
        if prefix != "1" * exponent:
            raise AssertionError("2^m-1 regression failed")
        if start <= bound:
            power_rows.append([exponent, start, coefficient_stopping_time(start)])
    octave_rows = []
    for exponent in range(1, 33):
        start = (1 << (3 * exponent)) - 5
        prefix = parity_prefix(start, 3 * exponent)
        if prefix != "110" * exponent:
            raise AssertionError("8^m-5 regression failed")
        if start <= bound:
            octave_rows.append([exponent, start, coefficient_stopping_time(start)])
    safe_block_words = 0
    for mask in range(1 << 12):
        word = "".join("111" if (mask >> index) & 1 else "110" for index in range(12))
        odd = 0
        for depth, bit in enumerate(word, 1):
            odd += bit == "1"
            if 3**odd < 1 << depth:
                break
        else:
            safe_block_words += 1
    safe_ab = crossed_ab = 0
    first_crossing_histogram: dict[int, int] = defaultdict(int)
    for r in range(1, 33):
        for s in range(1, 33):
            word = A_WORD * r + B_WORD * s
            odd = 0
            crossing = None
            for depth, bit in enumerate(word, 1):
                odd += bit == "1"
                if 3**odd < 1 << depth:
                    crossing = depth
                    break
            if crossing is None:
                safe_ab += 1
            else:
                crossed_ab += 1
                first_crossing_histogram[crossing] += 1
    if safe_block_words != 1 << 12 or (safe_ab, crossed_ab) != (713, 311):
        raise AssertionError("mandatory adversarial count changed")
    return {
        "2^m_minus_1": {"scope": "1<=m<=64", "prefix": "1^m", "within_spacing_bound": power_rows},
        "8^m_minus_5": {"scope": "1<=m<=32", "prefix": "(110)^m", "within_spacing_bound": octave_rows},
        "(110|111)^star": {"block_count": 12, "words_checked": 1 << 12, "coefficient_safe": safe_block_words},
        "A^rB^s": {
            "scope": "1<=r,s<=32",
            "pairs": 1024,
            "fully_coefficient_safe": safe_ab,
            "first_crossing": crossed_ab,
            "crossing_depth_histogram": [[key, first_crossing_histogram[key]] for key in sorted(first_crossing_histogram)],
        },
    }


def spacing_data(artifact_dir: Path, bound: int) -> dict[str, object]:
    layers, digest, computed_records = spacing_layers(bound)
    stored_records = direct_record_rows(artifact_dir / "M_search_records.csv", bound)
    if computed_records != stored_records:
        raise AssertionError("Phase 6 M-search record dependency mismatch")
    defined = [row for row in layers if row["delta"] is not None]
    deepest = defined[-1]
    spacing_records = []
    previous_delta = object()
    witness_transitions = []
    previous_witness = object()
    for row in layers:
        if row["delta"] != previous_delta:
            spacing_records.append(row)
            previous_delta = row["delta"]
        witness = (row["left"], row["right"])
        if witness != previous_witness:
            witness_transitions.append(row)
            previous_witness = witness
    if bound == DEFAULT_SPACING_BOUND and (
        deepest["k"], deepest["delta"], deepest["left"], deepest["right"]
    ) != (213, 268_416, 1_126_015, 1_394_431):
        raise AssertionError("production spacing obstruction changed")
    return {
        "format": "collatz-phase10-safe-pair-spacing-v1",
        "E15": {
            "repository_status": "VERIFIED_FINITE",
            "definition": "Delta_k(H)=min{m-n:2<=n<m<=H and both coefficient-safe for k steps}",
            "bound_H": bound,
            "maximum_k_audited": layers[-1]["k"],
            "stopping_time_digest_sha256": digest,
            "layers": layers,
            "spacing_records": spacing_records,
            "witness_transitions": witness_transitions,
            "deepest_defined_spacing": deepest,
            "phase6_M_records_reconstructed": [[start, stopping] for start, stopping in computed_records],
        },
        "recursive_difference_rule": {
            "verified_finite": True,
            "nested_sets": "Safe_(k+1) is a subset of Safe_k",
            "deletion_rule": "when an unsafe point is deleted, its two adjacent gaps merge by exact addition",
            "strict_growth_shortcut": {
                "repository_status": "REFUTED",
                "hypothesis": "Delta_(k+1)(H)>Delta_k(H) whenever both values are defined",
                "smallest_production_counterexample": {"H": bound, "k": 2, "Delta_k": layers[2]["delta"], "Delta_k_plus_1": layers[3]["delta"]},
                "surviving_rule": "Delta_(k+1)(H)>=Delta_k(H) whenever both values are defined",
            },
            "target_certificate_found": False,
        },
        "C05": {
            "repository_status": "OPEN",
            "target": f"Delta_(K0-1)(2^72)>{W}",
            "target_evaluated": False,
            "finite_obstruction": "at H=1500000, Delta_213=268416, witnessed by 1126015 and 1394431; at k=214 fewer than two safe starts remain in this finite prefix",
        },
        "mandatory_adversarial_audit": adversarial_audit(bound),
        "dependencies": {"M_search_records_sha256": sha256(artifact_dir / "M_search_records.csv")},
        "what_this_result_does_not_prove": "Finite spacing through H=1500000 gives no lower bound at H=2^72 or depth K0-1; disappearance of pairs in the scanned prefix is not a spacing theorem.",
        "proves_collatz": False,
    }


def rational_cycle_data(cycle_layers: list[dict[str, object]], total: int) -> dict[str, object]:
    return {
        "format": "collatz-phase10-rational-cycle-v1",
        "P65": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For a coefficient-safe first-crossing word, z=B/D is the minimum element of its formal rational affine cycle, and gcd(B,D)=gcd(d,D).",
            "fixed_point_identity": "F_w(B/D)=B/D because D=Q-P",
            "prefix_difference_numerator": "(3^a_j-2^j)*B+B_j*D>=0 for every j<K",
            "minimum_reason": "coefficient safety gives 3^a_j>=2^j and B_j,D>=0",
            "gcd_reason": "B=P*d (mod D) and gcd(P,D)=1",
            "parity_semantics": "formal rational cycle of the prescribed affine branches; no new positive-integer cycle is asserted",
        },
        "finite_audit": {
            "repository_status": "VERIFIED_FINITE",
            "maximum_q": len(cycle_layers),
            "total_words": total,
            "row_encoding": "q|K|odd_positions|min-prefix-numerator|strict-above-count|terminal-numerator|gcd(B,D) newline",
            "layers": cycle_layers,
        },
        "external_context": {
            "Christoffel_extremality_status": "EXTERNAL_CONTEXT",
            "theorem_used": False,
            "claim_of_novelty": False,
        },
        "what_this_result_does_not_prove": "The rational fixed point is not a positive-integer Collatz cycle, and no Christoffel extremality theorem is proved or used.",
        "proves_collatz": False,
    }


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_report(path: Path, gap: dict[str, object], renewal: dict[str, object], spacing: dict[str, object]) -> None:
    deepest = spacing["E15"]["deepest_defined_spacing"]
    lines = [
        "# Phase 10 obstruction report",
        "",
        "This report does not claim a proof or disproof of the Collatz conjecture.",
        "",
        "## Verified reductions",
        "",
        "- P63 reduces the q0 two-sided residue condition to the single gap residue rho, with m=N and X=m+rho in the near box.",
        "- P64 conditionally proves renewal safety through K0-1 for every least-counterexample orbit point in [N,N+W].",
        "- P65 proves the exact formal rational-cycle minimum and gcd identity.",
        "",
        "## Exact finite spacing obstruction",
        "",
        f"- The complete scan through H={spacing['E15']['bound_H']} has deepest defined spacing Delta_{deepest['k']}={deepest['delta']} at ({deepest['left']},{deepest['right']}).",
        "- At the next depth the scanned prefix has fewer than two safe starts. This is absence in a finite prefix, not a lower bound for larger H.",
        "- The deletion/neighbor-gap recursion is exact, but no composable cylinder certificate proving the Phase 10 target was found.",
        "- Strict per-depth spacing growth is false: Delta_2=Delta_3=4 in the production prefix. Only nondecrease survives.",
        "",
        "## Open target",
        "",
        f"- C05 remains OPEN: Delta_(K0-1)(2^72)>{W} was not proved or computationally evaluated.",
        "- The gap reduction does not determine B modulo D for the unknown q0 word, so C04 remains OPEN.",
        "",
        "## What this result does not prove",
        "",
        "Phase 10 does not prove C04, C05, the existence of a least counterexample, or the Collatz conjecture.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(artifact_dir: Path, *, spacing_bound: int, layer_max_q: int) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    gap_layers, cycle_layers, total = finite_gap_cycle_audit(layer_max_q)
    gap = gap_modulus_data(artifact_dir, gap_layers, total)
    renewal = renewal_barrier_data(artifact_dir)
    spacing = spacing_data(artifact_dir, spacing_bound)
    cycle = rational_cycle_data(cycle_layers, total)
    write_json(artifact_dir / "phase10_gap_modulus.json", gap)
    write_json(artifact_dir / "phase10_renewal_barrier.json", renewal)
    write_json(artifact_dir / "phase10_safe_pair_spacing.json", spacing)
    write_json(artifact_dir / "phase10_rational_cycle.json", cycle)
    write_report(artifact_dir / "phase10_obstruction_report.md", gap, renewal, spacing)
    return {
        "P63": "CONDITIONAL",
        "P64": "CONDITIONAL",
        "E15": "VERIFIED_FINITE",
        "P65": "VERIFIED_THEOREM",
        "C04": "OPEN",
        "C05": "OPEN",
        "spacing_bound": spacing_bound,
        "deepest_defined_spacing": spacing["E15"]["deepest_defined_spacing"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--spacing-bound", type=int, default=DEFAULT_SPACING_BOUND)
    parser.add_argument("--layer-max-q", type=int, default=DEFAULT_LAYER_Q)
    arguments = parser.parse_args()
    if arguments.spacing_bound < 3 or arguments.layer_max_q < 1:
        parser.error("bounds are too small")
    result = generate(arguments.artifact_dir, spacing_bound=arguments.spacing_bound, layer_max_q=arguments.layer_max_q)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
