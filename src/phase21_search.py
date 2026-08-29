#!/usr/bin/env python3
"""Generate exact Phase 21 repetition-complexity evidence.

The accepted decisions in this module use only integers and exact rationals.
Displayed decimal slopes are explanatory strings, never acceptance inputs.
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


A_BITS = "11101"
B_BITS = "1100"
MASK64 = (1 << 64) - 1


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encoded(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def digest_rows(rows: object) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def v2_nonzero(value: int) -> int:
    value = abs(value)
    if value == 0:
        raise ValueError("v2(0) is outside the distinct-state scope")
    return (value & -value).bit_length() - 1


def reverse64(value: int) -> int:
    if not 0 <= value <= MASK64:
        raise ValueError("direct audit state exceeds the declared 64-bit key scope")
    value = ((value >> 1) & 0x5555555555555555) | ((value & 0x5555555555555555) << 1)
    value = ((value >> 2) & 0x3333333333333333) | ((value & 0x3333333333333333) << 2)
    value = ((value >> 4) & 0x0F0F0F0F0F0F0F0F) | ((value & 0x0F0F0F0F0F0F0F0F) << 4)
    value = ((value >> 8) & 0x00FF00FF00FF00FF) | ((value & 0x00FF00FF00FF00FF) << 8)
    value = ((value >> 16) & 0x0000FFFF0000FFFF) | ((value & 0x0000FFFF0000FFFF) << 16)
    return ((value >> 32) | (value << 32)) & MASK64


def literal_cycle(source: int) -> tuple[list[int], int, int, int]:
    positions: dict[int, int] = {}
    states: list[int] = []
    value = source
    while value not in positions:
        positions[value] = len(states)
        states.append(value)
        value = shortcut(value)
    start = positions[value]
    return states, start, len(states) - start, value


def literal_lcp(left: int, right: int) -> int:
    count = 0
    while (left & 1) == (right & 1):
        left = shortcut(left)
        right = shortcut(right)
        count += 1
    return count


def previous_lcp_profile(states: list[int], reverse_cache: dict[int, int]) -> tuple[list[int], list[int]]:
    keys: list[int] = []
    key_to_index: dict[int, int] = {}
    maxima = [0] * len(states)
    witnesses = [-1] * len(states)
    for later, state in enumerate(states):
        key = reverse_cache.get(state)
        if key is None:
            key = reverse64(state)
            reverse_cache[state] = key
        if key in key_to_index:
            raise AssertionError("distinct direct states share all 64 low bits")
        position = bisect.bisect_left(keys, key)
        candidates = []
        if position:
            candidates.append(key_to_index[keys[position - 1]])
        if position < len(keys):
            candidates.append(key_to_index[keys[position]])
        best = -1
        best_index = -1
        for earlier in candidates:
            valuation = v2_nonzero(state - states[earlier])
            if valuation > best or (valuation == best and earlier < best_index):
                best, best_index = valuation, earlier
        if best >= 0:
            maxima[later] = best
            witnesses[later] = best_index
        keys.insert(position, key)
        key_to_index[key] = later
    return maxima, witnesses


def first_repeat_vector(maxima: list[int], maximum_width: int) -> list[int]:
    result = [0] * maximum_width
    missing = maximum_width
    for second_start, value in enumerate(maxima):
        upto = min(value, maximum_width)
        for width in range(1, upto + 1):
            if result[width - 1] == 0:
                result[width - 1] = second_start
                missing -= 1
        if not missing:
            break
    return result


def direct_orbit_audit(bound: int, maximum_width: int) -> dict[str, object]:
    if bound != 300000 or maximum_width != 64:
        raise ValueError("accepted direct bounds are fixed at N<300000 and n<=64")
    reverse_cache: dict[int, int] = {}
    row_hash = hashlib.sha256()
    cycle_counts: Counter[str] = Counter()
    maximum_distinct = (-1, -1)
    maximum_lcp = (-1, -1, -1, -1)
    minimum_height_margin: tuple[int, int, int, int] | None = None
    total_repeat_widths = 0
    total_prefix_powers = 0
    maximum_prefix_power = (1, -1, -1)
    largest_state = (0, -1)

    for source in range(1, bound):
        states, cycle_start, cycle_length, repeated_state = literal_cycle(source)
        cycle = states[cycle_start:]
        cycle_counts[",".join(map(str, cycle))] += 1
        if set(cycle) != {1, 2} or cycle_length != 2:
            raise AssertionError("unexpected positive cycle in accepted finite interval")
        if len(states) > maximum_distinct[0]:
            maximum_distinct = (len(states), source)
        peak = max(states)
        if peak > largest_state[0]:
            largest_state = (peak, source)

        maxima, witnesses = previous_lcp_profile(states, reverse_cache)
        ones = 0
        source_max = (0, -1, -1)
        for later, state in enumerate(states):
            if (state + 1) * (1 << ones) > (source + 1) * 3**ones:
                raise AssertionError("orbit growth bound")
            width = maxima[later]
            if width:
                earlier = witnesses[later]
                if literal_lcp(states[earlier], state) != width:
                    raise AssertionError("literal LCP identity")
                left = 1 << (width + ones)
                right = (source + 1) * 3**ones
                if left >= right:
                    raise AssertionError("repeated-factor height theorem")
                margin = right - left
                if minimum_height_margin is None or margin < minimum_height_margin[0]:
                    minimum_height_margin = (margin, source, later, width)
                if width > source_max[0]:
                    source_max = (width, earlier, later)
                total_repeat_widths += min(width, maximum_width)
            ones += state & 1

        prefix_powers = []
        prefix_ones = 0
        for period in range(1, len(states)):
            prefix_ones += states[period - 1] & 1
            common = v2_nonzero(states[period] - source)
            exponent = 1 + common // period
            if exponent < 2:
                continue
            repeated = (exponent - 1) * period
            if 1 << (repeated + prefix_ones) >= (source + 1) * 3**prefix_ones:
                raise AssertionError("prefix-power height theorem")
            prefix_powers.append([period, exponent, common, prefix_ones])
            total_prefix_powers += 1
            if exponent > maximum_prefix_power[0]:
                maximum_prefix_power = (exponent, source, period)

        repeat_vector = first_repeat_vector(maxima, maximum_width)
        row = [
            source,
            len(states),
            cycle_start,
            cycle_length,
            repeated_state,
            peak,
            source_max,
            repeat_vector,
            prefix_powers,
        ]
        row_hash.update((json.dumps(row, separators=(",", ":")) + "\n").encode("ascii"))
        if source_max[0] > maximum_lcp[0]:
            maximum_lcp = (source_max[0], source, source_max[1], source_max[2])

    if minimum_height_margin is None:
        raise AssertionError("direct repeat audit found no repeats")
    return {
        "format": "collatz-phase21-direct-orbits-v1",
        "claim": {"P125": "VERIFIED_THEOREM", "P126": "VERIFIED_THEOREM", "E33": "VERIFIED_FINITE"},
        "source_interval": [1, bound],
        "upper_endpoint_exclusive": True,
        "sources_checked": bound - 1,
        "maximum_repeat_width": maximum_width,
        "all_repeats_covered_by": "for each second start j, the largest v2(x_j-x_i) over i<j; checking the largest width implies every smaller repeated width",
        "eventual_cycle_counts": dict(sorted(cycle_counts.items())),
        "maximum_distinct_states": {"count": maximum_distinct[0], "least_source": maximum_distinct[1]},
        "largest_state": {"value": largest_state[0], "least_source": largest_state[1]},
        "maximum_lcp": {"length": maximum_lcp[0], "source": maximum_lcp[1], "earlier_start": maximum_lcp[2], "later_start": maximum_lcp[3]},
        "minimum_strict_height_margin": {"value": minimum_height_margin[0], "source": minimum_height_margin[1], "second_start": minimum_height_margin[2], "repeat_width": minimum_height_margin[3]},
        "covered_repeated_second_start_widths": total_repeat_widths,
        "prefix_power_witnesses": total_prefix_powers,
        "maximum_prefix_power": {"exponent": maximum_prefix_power[0], "source": maximum_prefix_power[1], "period": maximum_prefix_power[2]},
        "row_digest_sha256": row_hash.hexdigest(),
        "row_storage": "omitted; verifier rebuilds every source independently from literal states",
        "periodic_exception": "Every audited positive source enters the 1,2 cycle. The non-eventually-periodic theorems are applied only to the distinct precycle segment for finite sanity checks, never to the periodic tail.",
        "finite_boundary": "The interval audit does not prove that all positive integers converge and is not the proof of P125 or P126.",
        "proves_collatz": False,
    }


@dataclass(frozen=True, slots=True)
class CriticalRow:
    bits: int
    length: int
    q: int
    affine: int
    source: int
    endpoint: int

    @property
    def word(self) -> str:
        return format(self.bits, f"0{self.length}b")


def make_critical_row(bits: int, length: int, q: int, affine: int) -> CriticalRow:
    modulus = 1 << length
    three = 3**q
    source = (-affine * pow(three, -1, modulus)) % modulus or modulus
    endpoint = (three * source + affine) // modulus
    return CriticalRow(bits, length, q, affine, source, endpoint)


def enumerate_safe(maximum_q: int) -> dict[int, list[CriticalRow]]:
    grouped = {q: [] for q in range(1, maximum_q + 1)}
    frontier = [(0, 0, 0)]
    maximum_length = (3**maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        following = []
        for bits, q, affine in frontier:
            if q and 3**q > 1 << length:
                row = make_critical_row(bits << 1, length, q, affine)
                grouped[q].append(row)
                following.append((row.bits, q, affine))
            if q < maximum_q and 3 ** (q + 1) > 1 << length:
                new_affine = 3 * affine + (1 << (length - 1))
                row = make_critical_row((bits << 1) | 1, length, q + 1, new_affine)
                grouped[q + 1].append(row)
                following.append((row.bits, q + 1, new_affine))
        frontier = following
    return grouped


def hq_values(maximum_q: int) -> dict[int, tuple[int, int, int]]:
    result = {}
    power = 1
    b_max = 0
    for q in range(1, maximum_q + 1):
        b_max = 3 * b_max + (1 << (power.bit_length() - 1))
        power *= 3
        k_q = power.bit_length()
        denominator = (1 << k_q) - power
        result[q] = (b_max, denominator, k_q)
    return result


def lcp_table(word: str) -> list[list[int]]:
    length = len(word)
    table = [[0] * (length + 1) for _ in range(length + 1)]
    for left in range(length - 1, -1, -1):
        for right in range(length - 1, left, -1):
            if word[left] == word[right]:
                table[left][right] = 1 + table[left + 1][right + 1]
    return table


def word_profile(word: str, hq_numerator: int, hq_denominator: int) -> dict[str, object]:
    length = len(word)
    table = lcp_table(word)
    prefix_ones = [0]
    for bit in word:
        prefix_ones.append(prefix_ones[-1] + (bit == "1"))
    maxima = [0] * length
    for later in range(1, length):
        maxima[later] = max(table[earlier][later] for earlier in range(later))
    first = first_repeat_vector(maxima, length)

    complexities = []
    code_values = [int(bit) for bit in word]
    for width in range(1, length + 1):
        mask = (1 << width) - 1
        code = 0
        factors = set()
        for index, bit in enumerate(code_values):
            code = ((code << 1) | bit) & mask
            if index + 1 >= width:
                factors.add(code)
        complexities.append(len(factors))

    best_stammer = (1, 1, 0, 0, 1)
    for start in range(length):
        for period in range(1, length - start):
            repeat = table[start][start + period]
            if not repeat:
                continue
            total = start + period + repeat
            denominator = start + period
            if total * best_stammer[1] > best_stammer[0] * denominator:
                best_stammer = (total, denominator, start, period, total)

    best_source = (0, 1, -1, 0)
    excluded = False
    best_margin = None
    for later in range(1, length):
        width = maxima[later]
        if not width:
            continue
        odd = prefix_ones[later]
        numerator = 1 << (width + odd)
        denominator = 3**odd
        if numerator * best_source[1] > best_source[0] * denominator:
            best_source = (numerator, denominator, later, width)
        margin = numerator * hq_denominator - (hq_numerator + hq_denominator) * denominator
        if best_margin is None or margin > best_margin:
            best_margin = margin
        excluded |= margin >= 0

    return {
        "factor_complexity": complexities,
        "first_repeat_second_start": first,
        "maximum_previous_lcp": maxima,
        "best_finite_stammering": {
            "ratio": encoded(Fraction(best_stammer[0], best_stammer[1])),
            "U_length": best_stammer[2],
            "V_length": best_stammer[3],
            "prefix_length": best_stammer[4],
        },
        "strongest_source_lower_expression": {
            "N_plus_1_strictly_greater_than": encoded(Fraction(best_source[0], best_source[1])),
            "second_start": best_source[2],
            "repeat_width": best_source[3],
        },
        "Hq_repetition_excluded": excluded,
        "best_Hq_integer_margin": best_margin,
    }


def contact_count(word: str) -> int:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    return sum(position == (3**rank).bit_length() - 1 for rank, position in enumerate(positions))


def critical_repetition_audit(maximum_q: int) -> dict[str, object]:
    if maximum_q != 17:
        raise ValueError("accepted critical audit is fixed at Q<=17")
    grouped = enumerate_safe(maximum_q)
    minima: dict[tuple[int, int], int] = {}
    for q, rows in grouped.items():
        for row in rows:
            key = (q, row.endpoint)
            minima[key] = min(minima.get(key, row.length), row.length)
    heights = hq_values(maximum_q)
    row_hash = hashlib.sha256()
    counts = {}
    global_best_stammer = (1, 1, None)
    global_best_source = (0, 1, None)
    total_critical = total_geodesic = total_excluded = total_geodesic_excluded = 0
    for q in range(1, maximum_q + 1):
        length = (3**q).bit_length() - 1
        critical = sorted((row for row in grouped[q] if row.length == length), key=lambda row: row.word)
        b_max, d_q, k_q = heights[q]
        geodesic_count = excluded_count = geodesic_excluded = 0
        maximum_contacts = 0
        for row in critical:
            geodesic = minima[(q, row.endpoint)] == row.length
            geodesic_count += geodesic
            profile = word_profile(row.word, b_max, d_q)
            excluded = bool(profile["Hq_repetition_excluded"])
            excluded_count += excluded
            geodesic_excluded += geodesic and excluded
            contacts = contact_count(row.word)
            maximum_contacts = max(maximum_contacts, contacts)
            stammer = profile["best_finite_stammering"]["ratio"]
            stammer_fraction = Fraction(int(stammer["numerator"]), int(stammer["denominator"]))
            if stammer_fraction > Fraction(global_best_stammer[0], global_best_stammer[1]):
                global_best_stammer = (stammer_fraction.numerator, stammer_fraction.denominator, [q, row.word, row.source])
            lower = profile["strongest_source_lower_expression"]["N_plus_1_strictly_greater_than"]
            lower_fraction = Fraction(int(lower["numerator"]), int(lower["denominator"]))
            if lower_fraction > Fraction(global_best_source[0], global_best_source[1]):
                global_best_source = (lower_fraction.numerator, lower_fraction.denominator, [q, row.word, row.source])
            digest_row = [q, row.word, row.source, row.endpoint, int(geodesic), contacts, profile]
            row_hash.update((json.dumps(digest_row, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii"))
        counts[str(q)] = {
            "K_q_minus_1": length,
            "K_q": k_q,
            "H_q": encoded(Fraction(b_max, d_q)),
            "critical_words": len(critical),
            "geodesic_words": geodesic_count,
            "repetition_excluded": excluded_count,
            "geodesic_repetition_excluded": geodesic_excluded,
            "maximum_contacts": maximum_contacts,
        }
        total_critical += len(critical)
        total_geodesic += geodesic_count
        total_excluded += excluded_count
        total_geodesic_excluded += geodesic_excluded
    return {
        "format": "collatz-phase21-critical-repetitions-v1",
        "claim": {"P132": "VERIFIED_THEOREM", "E33": "VERIFIED_FINITE", "H89": "OPEN"},
        "maximum_Q": maximum_q,
        "counts_by_Q": counts,
        "totals": {
            "critical_words": total_critical,
            "geodesic_words": total_geodesic,
            "repetition_excluded": total_excluded,
            "geodesic_repetition_excluded": total_geodesic_excluded,
        },
        "maximum_finite_stammering_ratio": {"value": encoded(Fraction(global_best_stammer[0], global_best_stammer[1])), "witness": global_best_stammer[2]},
        "maximum_source_lower_expression": {"value": encoded(Fraction(global_best_source[0], global_best_source[1])), "witness": global_best_source[2]},
        "row_digest_sha256": row_hash.hexdigest(),
        "row_storage": "omitted; verifier rebuilds every critical word from string recursion",
        "certificate_rule": "reject if 2^(n+h(j))*D_q >= (B_q_max+D_q)*3^h(j)",
        "finite_boundary": "Q<=17 exclusion counts do not prove an eventual H89 repetition theorem.",
        "proves_collatz": False,
    }


def orbit_word(source: int, length: int) -> str:
    bits = []
    for _ in range(length):
        bits.append("1" if source & 1 else "0")
        source = shortcut(source)
    return "".join(bits)


def expand_exponents(exponents: list[int], length: int) -> str:
    word = "".join("1" + "0" * (value - 1) for value in exponents)
    if len(word) < length:
        raise ValueError("short formal exponent word")
    return word[:length]


def all_contact_word(length: int) -> str:
    positions = set()
    q = 0
    while True:
        position = (3**q).bit_length() - 1
        if position >= length:
            break
        positions.add(position)
        q += 1
    return "".join("1" if index in positions else "0" for index in range(length))


def square_root_word(length: int) -> str:
    floor_log = defect = total = 0
    exponents = []
    q = 0
    while total < length:
        next_floor = (3 ** (q + 1)).bit_length() - 1
        increment = int(next_floor - floor_log == 2 and defect < isqrt(q + 1))
        exponent = next_floor - floor_log - increment
        exponents.append(exponent)
        total += exponent
        defect += increment
        floor_log = next_floor
        q += 1
    return expand_exponents(exponents, length)


def interval_controller_word(length: int) -> str:
    state = Fraction(3, 2)
    exponents = []
    total = 0
    while total < length:
        exponent = 1 if state <= Fraction(5, 3) else 2
        exponents.append(exponent)
        total += exponent
        state = (3 * state - 1) / (1 << exponent)
    return expand_exponents(exponents, length)


def p109_word(length: int) -> str:
    odd = 0
    bits = []
    for elapsed in range(length):
        bit = int(3**odd <= 8 * (1 << elapsed))
        bits.append(str(bit))
        odd += bit
    return "".join(bits)


def periodic(pattern: str, length: int) -> str:
    return (pattern * ((length + len(pattern) - 1) // len(pattern)))[:length]


def simple_word_profile(word: str, maximum_width: int) -> dict[str, object]:
    table = lcp_table(word)
    maxima = [0] * len(word)
    witnesses = [-1] * len(word)
    for later in range(1, len(word)):
        best = max((table[earlier][later], -earlier) for earlier in range(later))
        maxima[later] = best[0]
        witnesses[later] = -best[1]
    first = first_repeat_vector(maxima, maximum_width)
    best = (1, 1, 0, 0, 1)
    for start in range(len(word)):
        for period_length in range(1, len(word) - start):
            repeat = table[start][start + period_length]
            if repeat:
                total = start + period_length + repeat
                denominator = start + period_length
                if total * best[1] > best[0] * denominator:
                    best = (total, denominator, start, period_length, total)
    return {
        "first_repeat_second_start": first,
        "maximum_lcp": max(maxima, default=0),
        "best_finite_stammering": {
            "ratio": encoded(Fraction(best[0], best[1])),
            "U_length": best[2],
            "V_length": best[3],
            "prefix_length": best[4],
        },
    }


def control_audit(length: int, maximum_width: int) -> dict[str, object]:
    if length != 512 or maximum_width != 64:
        raise ValueError("accepted control bounds are fixed")
    controls = [
        ("all-contact", "formal", all_contact_word(length)),
        ("NG22-square-root", "formal", square_root_word(length)),
        ("NG22-interval", "formal", interval_controller_word(length)),
        ("P109-balanced", "formal", p109_word(length)),
        ("source-167", "positive-source", orbit_word(167, length)),
        ("source-1126015", "positive-source", orbit_word(1126015, length)),
        ("source-1394431", "positive-source", orbit_word(1394431, length)),
        ("(110|111)*", "formal", periodic("110111", length)),
        ("A-periodic", "formal", periodic(A_BITS, length)),
        ("B-periodic", "formal", periodic(B_BITS, length)),
        ("A8B8-periodic", "formal", periodic(A_BITS * 8 + B_BITS * 8, length)),
    ]
    sequences = []
    for name, kind, word in controls:
        sequences.append({"name": name, "kind": kind, "length": len(word), **simple_word_profile(word, maximum_width)})

    family_rows = []
    for m in range(2, 21):
        for family, source in (("2^m-1", 2**m - 1), ("8^m-5", 8**m - 5)):
            word = orbit_word(source, 128)
            family_rows.append({"family": family, "m": m, "source": str(source), **simple_word_profile(word, 32)})
    for blocks in range(1, 5):
        for selection in itertools.product(("110", "111"), repeat=blocks):
            word = "".join(selection)
            family_rows.append({"family": "(110|111)^*", "word": word, "kind": "formal", **simple_word_profile(word, min(32, len(word)))})
    for r in range(1, 9):
        for s in range(1, 9):
            word = A_BITS * r + B_BITS * s
            family_rows.append({"family": "A^rB^s", "r": r, "s": s, "word": word, "kind": "formal", **simple_word_profile(word, min(32, len(word)))})
    return {
        "format": "collatz-phase21-controls-v1",
        "claim": {"E33": "VERIFIED_FINITE", "H112": "OPEN", "H72": "OPEN"},
        "prefix_length": length,
        "maximum_repeat_width": maximum_width,
        "sequences": sequences,
        "family_rows": family_rows,
        "row_digest_sha256": digest_rows([sequences, family_rows]),
        "scope_boundary": "formal words are repetition falsifiers only; they are not asserted to have one positive ordinary infinite source",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase21-theory-v1",
        "map": "T(x)=x/2 for even x and (3x+1)/2 for odd x; v_t=x_t mod 2; h(t)=sum_(r<t)v_r",
        "claims": {
            "P125": {
                "status": "VERIFIED_THEOREM",
                "statement": "For integers a!=b, LCP(v(a),v(b))=v2(a-b); equivalently equal first n input parities iff a==b mod 2^n.",
                "proof": "At one step, the output difference is an odd multiple of (a-b)/2 when inputs have equal parity; induction gives both directions and the first differing bit.",
            },
            "P126": {
                "status": "VERIFIED_THEOREM",
                "statement": "For a positive non-eventually-periodic orbit, a repeated width-n factor at i<j obeys 2^(n+h(j)) < (N+1)3^h(j).",
                "strictness": "state distinctness gives 2^n<=abs(x_j-x_i)<max(x_i,x_j); replacing < by <= is invalid",
                "growth": "(x_t+1)2^h(t)<=(N+1)3^h(t)",
            },
            "P127": {
                "status": "VERIFIED_THEOREM",
                "statement": "Every positive non-eventually-periodic orbit parity word satisfies p(n)>(n-log2(N+1))/log2(3/2), hence liminf p(n)/n>=1/log2(3/2).",
                "exact_acceptance": "2^(n+h(p(n))) < (N+1)3^h(p(n)); logarithms only restate the exact integer inequality",
            },
            "P128": {
                "status": "CONDITIONAL",
                "statement": "Assuming EXT08, every positive rational noncyclic parity word satisfies limsup p(n)/n>=log(3)/log(3/2).",
                "dependency": "EXT08 supplies only a subsequence h(m_k)/m_k->log(2)/log(3)",
            },
            "P129": {
                "status": "VERIFIED_THEOREM",
                "statement": "The Adamczewski-Bugeaud Diophantine exponent of a positive non-eventually-periodic orbit parity word is at most log2(3).",
                "definition_repair": "Condition (*) uses increasing |V_n^w_n|. Non-eventual periodicity forces |U_nV_n|->infinity along the relevant sequence, so log2(N+1)/|U_nV_n| vanishes.",
            },
            "P130": {
                "status": "VERIFIED_THEOREM",
                "statement": "If a positive non-eventually-periodic orbit begins with W^r, then N+1>2^((r-1)|W|)(2/3)^|W|_1; in particular a square period d has d<log_(4/3)(N+1).",
                "scope": "internal powers require the local source x_i and are not bounded by the original N alone",
            },
            "P131": {
                "status": "VERIFIED_THEOREM",
                "statement": "For distinct first m+1 orbit states with peak H_m, p(n)>=ceil((m+1)/(1+floor((H_m-1)/2^n))); hence p(ceil(log2 H_m))>=m+1.",
                "consequences": "polynomial complexity forces stretched-exponential peaks; zero entropy forces log(H_m)/log(m)->infinity",
            },
            "P132": {
                "status": "VERIFIED_THEOREM",
                "statement": "Under P54, a critical-word repeat is impossible when 2^(n+h(j)) >= (H_q+1)3^h(j); equivalently 2^(n+h(j))D_q >= (B_q_max+D_q)3^h(j).",
                "scope": "an exact finite rejection rule, not an eventual H89 theorem",
            },
        },
        "supersession": "P127 unconditionally strengthens the positive-integer conclusions of conditional P123/P124; their external historical statements remain in the ledger.",
        "open_target": "Force repeats violating P132, or force P115 nonzero lifts from their absence, on every relevant infinite critical branch.",
        "what_this_result_does_not_prove": "No peak upper bound, repeat-forces-lift theorem, eventual H89 certificate, positive-source exclusion, nontrivial-cycle exclusion, or Collatz proof is obtained.",
        "proves_collatz": False,
    }


def literature_artifact() -> dict[str, object]:
    rows = [
        {
            "id": "EXT14",
            "classification": "EXTERNAL_THEOREM",
            "authors": "Daniel J. Bernstein and Jeffrey C. Lagarias",
            "title": "The 3x + 1 Conjugacy Map",
            "year": 1996,
            "doi": "10.4153/CJM-1996-060-x",
            "used_for": "novelty context only; P125 is rederived internally",
        },
        {
            "classification": "DEFINITION_CONTEXT",
            "authors": "Boris Adamczewski and Yann Bugeaud",
            "title": "Dynamics for beta-shifts and Diophantine approximation",
            "year": 2007,
            "doi": "10.1017/S0143385707000223",
            "used_for": "Condition (*) and Diophantine exponent convention in P129",
        },
        {
            "classification": "DEFINITION_CONTEXT",
            "authors": "Yann Bugeaud and Dong Han Kim",
            "title": "A new complexity function, repetitions in Sturmian words, and irrationality exponents of Sturmian numbers",
            "year": 2018,
            "arxiv": "1510.00279",
            "used_for": "r(n,x) smallest-prefix convention; R_v(n)=r(n,v)-n",
        },
        {
            "classification": "DEFINITION_CONTEXT",
            "authors": "Jeremy Nicholson and Narad Rampersad",
            "title": "Initial non-repetitive complexity of infinite words",
            "year": 2016,
            "doi": "10.1016/j.dam.2016.03.010",
            "used_for": "initial nonrepetitive-complexity terminology",
        },
        {
            "classification": "RELATED_CONTEXT",
            "authors": "Tristan Sterin",
            "title": "Binary expression of ancestors in the Collatz graph",
            "year": 2019,
            "arxiv": "1907.00775",
            "used_for": "binary carry and first-source context; not an input to P125-P132",
        },
        {
            "classification": "EXTERNAL_THEOREM",
            "id": "EXT08",
            "authors": "Luis Lopez and Peter Stoll",
            "title": "The 3x+1 function on the rationals",
            "year": 2021,
            "arxiv": "2101.12747",
            "used_for": "the liminf density input to conditional P128 only",
        },
    ]
    return {
        "format": "collatz-phase21-literature-audit-v1",
        "sources": rows,
        "novelty_search": "Targeted searches found the standard parity conjugacy and word-complexity definitions but no primary source for the exact Collatz factor-complexity slopes. Absence from this search is not a literature-wide novelty claim.",
        "dependency_boundary": "P125-P127 and P129-P132 are repository derivations; P128 alone uses EXT08. Terminology citations are not promoted to proof dependencies.",
        "proves_collatz": False,
    }


def obstruction_report(values: dict[str, dict[str, object]]) -> str:
    direct = values["phase21_direct_orbits.json"]
    critical = values["phase21_critical_repetitions.json"]
    totals = critical["totals"]
    return f"""# Phase 21 obstruction report

## Strongest surviving result

Exact parity LCP gives an unconditional linear factor-complexity slope for every
positive non-eventually-periodic integer orbit.  EXT08 sharpens only a limsup
subsequence.  These are lower bounds on symbolic diversity, not upper bounds on
orbit height.

## Finite H89 obstruction

Through `Q<={critical['maximum_Q']}`, the audit rebuilt
`{totals['critical_words']}` critical words and `{totals['geodesic_words']}`
same-Q geodesic words.  The repetition certificate excluded
`{totals['repetition_excluded']}` critical and
`{totals['geodesic_repetition_excluded']}` geodesic rows.  Whatever these
finite counts are, they are not an eventual theorem.

## Direct-orbit boundary

All `{direct['sources_checked']}` sources in the declared interval entered the
`1,2` cycle.  Their distinct precycle states audit strict separation, but the
nonperiodic theorems are not applied across a repeated state or periodic tail.

## Exact missing bridge

The current results do not force sufficiently long repeats.  An H112/H89
advance needs a theorem that either forces a P132-violating repeat on every
critical branch, or turns sustained repeat avoidance into infinitely many
nonzero P115 source lifts while retaining positive ordinary height.

## What this result does not prove

It does not prove H89, H112, H72, eliminate nontrivial cycles, or prove the
Collatz conjecture.  `proves_collatz=false`.
"""


def generate(artifact_dir: Path, direct_bound: int, maximum_width: int, maximum_q: int, control_length: int) -> dict[str, dict[str, object]]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    values = {
        "phase21_theory.json": theory_artifact(),
        "phase21_direct_orbits.json": direct_orbit_audit(direct_bound, maximum_width),
        "phase21_critical_repetitions.json": critical_repetition_audit(maximum_q),
        "phase21_controls.json": control_audit(control_length, maximum_width),
        "phase21_literature_audit.json": literature_artifact(),
    }
    for name, value in values.items():
        write_json(artifact_dir / name, value)
    (artifact_dir / "phase21_obstruction_report.md").write_text(obstruction_report(values), encoding="utf-8")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--direct-bound", type=int, default=300000)
    parser.add_argument("--maximum-repeat-width", type=int, default=64)
    parser.add_argument("--maximum-q", type=int, default=17)
    parser.add_argument("--control-length", type=int, default=512)
    args = parser.parse_args()
    values = generate(args.artifact_dir, args.direct_bound, args.maximum_repeat_width, args.maximum_q, args.control_length)
    print(json.dumps({
        "valid": True,
        "direct_sources": values["phase21_direct_orbits.json"]["sources_checked"],
        "critical_totals": values["phase21_critical_repetitions.json"]["totals"],
        "controls": len(values["phase21_controls.json"]["sequences"]),
        "proves_collatz": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
