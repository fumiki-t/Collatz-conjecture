#!/usr/bin/env python3
"""Independent exact verifier for Phase 21 repetition evidence."""

from __future__ import annotations

import argparse
import bisect
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from math import isqrt
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


A = "11101"
B = "1100"
REV8 = tuple(int(f"{value:08b}"[::-1], 2) for value in range(256))


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} must contain an object")
    return value


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ef(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def object_hash(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def valuation(value: int) -> int:
    value = abs(value)
    if not value:
        fail("state equality omitted from periodic exception")
    count = 0
    while value % 2 == 0:
        count += 1
        value //= 2
    return count


def reversed_low_bits(value: int) -> int:
    if value < 0 or value >= pow(2, 64):
        fail("64-bit direct state scope")
    little = value.to_bytes(8, "little")
    return int.from_bytes(bytes(REV8[byte] for byte in little), "big")


def trace_to_repeat(source: int) -> tuple[list[int], int, int, int]:
    seen = {}
    values = []
    current = source
    while current not in seen:
        seen[current] = len(values)
        values.append(current)
        current = step(current)
    start = seen[current]
    return values, start, len(values) - start, current


def compare_parity_tails(left: int, right: int) -> int:
    length = 0
    while left % 2 == right % 2:
        left, right = step(left), step(right)
        length += 1
    return length


def online_repeat_data(values: list[int], key_cache: dict[int, int]) -> tuple[list[int], list[int]]:
    ordered: list[int] = []
    owner: dict[int, int] = {}
    lengths = [0] * len(values)
    witnesses = [-1] * len(values)
    for later, value in enumerate(values):
        key = key_cache.setdefault(value, reversed_low_bits(value))
        location = bisect.bisect_left(ordered, key)
        candidates = []
        if location > 0:
            candidates.append(owner[ordered[location - 1]])
        if location < len(ordered):
            candidates.append(owner[ordered[location]])
        if candidates:
            scored = [(valuation(value - values[earlier]), -earlier) for earlier in candidates]
            best_length, negative_earlier = max(scored)
            lengths[later] = best_length
            witnesses[later] = -negative_earlier
        if key in owner:
            fail("two direct states have the same 64-bit reversed key")
        ordered.insert(location, key)
        owner[key] = later
    return lengths, witnesses


def earliest_repeats(lengths: list[int], maximum: int) -> list[int]:
    answer = []
    for width in range(1, maximum + 1):
        answer.append(next((index for index, value in enumerate(lengths) if value >= width), 0))
    return answer


def expected_direct(bound: int, maximum: int) -> dict[str, object]:
    if bound != 300000 or maximum != 64:
        fail("direct accepted bounds")
    key_cache = {}
    rows = hashlib.sha256()
    cycles: Counter[str] = Counter()
    maximum_distinct = (-1, -1)
    largest = (0, -1)
    maximum_lcp = (-1, -1, -1, -1)
    minimum_margin = None
    covered = 0
    power_count = 0
    maximum_power = (1, -1, -1)
    for source in range(1, bound):
        states, cycle_start, cycle_length, repeated = trace_to_repeat(source)
        cycle = states[cycle_start:]
        cycles[",".join(str(value) for value in cycle)] += 1
        if cycle_length != 2 or set(cycle) != {1, 2}:
            fail("unexpected finite cycle")
        if len(states) > maximum_distinct[0]:
            maximum_distinct = (len(states), source)
        peak = max(states)
        if peak > largest[0]:
            largest = (peak, source)

        lcps, witnesses = online_repeat_data(states, key_cache)
        ones = 0
        source_maximum = (0, -1, -1)
        for later, state in enumerate(states):
            if (state + 1) * pow(2, ones) > (source + 1) * pow(3, ones):
                fail("growth inequality")
            width = lcps[later]
            if width:
                earlier = witnesses[later]
                if compare_parity_tails(states[earlier], state) != width:
                    fail("LCP arithmetic")
                left = pow(2, width + ones)
                right = (source + 1) * pow(3, ones)
                if left >= right:
                    fail("strict repeat-height inequality")
                candidate = (right - left, source, later, width)
                if minimum_margin is None or candidate[0] < minimum_margin[0]:
                    minimum_margin = candidate
                if width > source_maximum[0]:
                    source_maximum = (width, earlier, later)
                covered += min(width, maximum)
            ones += state % 2

        prefix_powers = []
        prefix_ones = 0
        for period in range(1, len(states)):
            prefix_ones += states[period - 1] % 2
            common = valuation(states[period] - source)
            exponent = 1 + common // period
            if exponent >= 2:
                repeated_length = (exponent - 1) * period
                if pow(2, repeated_length + prefix_ones) >= (source + 1) * pow(3, prefix_ones):
                    fail("prefix power inequality")
                prefix_powers.append([period, exponent, common, prefix_ones])
                power_count += 1
                if exponent > maximum_power[0]:
                    maximum_power = (exponent, source, period)
        repeat_vector = earliest_repeats(lcps, maximum)
        row = [source, len(states), cycle_start, cycle_length, repeated, peak, source_maximum, repeat_vector, prefix_powers]
        rows.update((json.dumps(row, separators=(",", ":")) + "\n").encode("ascii"))
        if source_maximum[0] > maximum_lcp[0]:
            maximum_lcp = (source_maximum[0], source, source_maximum[1], source_maximum[2])
    if minimum_margin is None:
        fail("empty direct repeat audit")
    return {
        "format": "collatz-phase21-direct-orbits-v1",
        "claim": {"P125": "VERIFIED_THEOREM", "P126": "VERIFIED_THEOREM", "E33": "VERIFIED_FINITE"},
        "source_interval": [1, bound],
        "upper_endpoint_exclusive": True,
        "sources_checked": bound - 1,
        "maximum_repeat_width": maximum,
        "all_repeats_covered_by": "for each second start j, the largest v2(x_j-x_i) over i<j; checking the largest width implies every smaller repeated width",
        "eventual_cycle_counts": dict(sorted(cycles.items())),
        "maximum_distinct_states": {"count": maximum_distinct[0], "least_source": maximum_distinct[1]},
        "largest_state": {"value": largest[0], "least_source": largest[1]},
        "maximum_lcp": {"length": maximum_lcp[0], "source": maximum_lcp[1], "earlier_start": maximum_lcp[2], "later_start": maximum_lcp[3]},
        "minimum_strict_height_margin": {"value": minimum_margin[0], "source": minimum_margin[1], "second_start": minimum_margin[2], "repeat_width": minimum_margin[3]},
        "covered_repeated_second_start_widths": covered,
        "prefix_power_witnesses": power_count,
        "maximum_prefix_power": {"exponent": maximum_power[0], "source": maximum_power[1], "period": maximum_power[2]},
        "row_digest_sha256": rows.hexdigest(),
        "row_storage": "omitted; verifier rebuilds every source independently from literal states",
        "periodic_exception": "Every audited positive source enters the 1,2 cycle. The non-eventually-periodic theorems are applied only to the distinct precycle segment for finite sanity checks, never to the periodic tail.",
        "finite_boundary": "The interval audit does not prove that all positive integers converge and is not the proof of P125 or P126.",
        "proves_collatz": False,
    }


def affine_from_positions(word: str) -> int:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    q = len(positions)
    return sum(pow(3, q - 1 - rank) * pow(2, position) for rank, position in enumerate(positions))


def source_of(word: str) -> int:
    modulus = pow(2, len(word))
    q = word.count("1")
    return (-affine_from_positions(word) * pow(pow(3, q), -1, modulus)) % modulus or modulus


def endpoint_of(word: str) -> int:
    q = word.count("1")
    modulus = pow(3, q)
    return (affine_from_positions(word) * pow(pow(2, len(word)), -1, modulus)) % modulus or modulus


def safe_words(maximum_q: int) -> dict[int, list[str]]:
    grouped = {q: [] for q in range(1, maximum_q + 1)}
    frontier = [""]
    maximum_length = pow(3, maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        next_frontier = []
        for prefix in reversed(frontier):
            q = prefix.count("1")
            zero = prefix + "0"
            if q and pow(3, q) > pow(2, length):
                grouped[q].append(zero)
                next_frontier.append(zero)
            one = prefix + "1"
            if q < maximum_q and pow(3, q + 1) > pow(2, length):
                grouped[q + 1].append(one)
                next_frontier.append(one)
        frontier = next_frontier
    return grouped


def height_rows(maximum_q: int) -> dict[int, tuple[int, int, int]]:
    result = {}
    three = 1
    maximum_affine = 0
    for q in range(1, maximum_q + 1):
        maximum_affine = 3 * maximum_affine + pow(2, three.bit_length() - 1)
        three *= 3
        K = three.bit_length()
        result[q] = (maximum_affine, pow(2, K) - three, K)
    return result


def direct_common(word: str, left: int, right: int) -> int:
    count = 0
    while left + count < len(word) and right + count < len(word) and word[left + count] == word[right + count]:
        count += 1
    return count


def direct_word_profile(word: str, h_num: int, h_den: int) -> dict[str, object]:
    length = len(word)
    maxima = [0] * length
    for later in range(1, length):
        maxima[later] = max(direct_common(word, earlier, later) for earlier in range(later))
    first = earliest_repeats(maxima, length)
    complexities = [len({word[start : start + width] for start in range(length - width + 1)}) for width in range(1, length + 1)]
    prefix = [0]
    for bit in word:
        prefix.append(prefix[-1] + int(bit))
    best_stammer = Fraction(1)
    best_stammer_data = (0, 0, 1)
    for start in range(length):
        for period in range(1, length - start):
            repeat = direct_common(word, start, start + period)
            if repeat:
                total = start + period + repeat
                ratio = Fraction(total, start + period)
                if ratio > best_stammer:
                    best_stammer = ratio
                    best_stammer_data = (start, period, total)
    best_source = Fraction(0)
    best_source_data = (-1, 0)
    excluded = False
    best_margin = None
    for later in range(1, length):
        width = maxima[later]
        if not width:
            continue
        odd = prefix[later]
        value = Fraction(pow(2, width + odd), pow(3, odd))
        if value > best_source:
            best_source = value
            best_source_data = (later, width)
        margin = pow(2, width + odd) * h_den - (h_num + h_den) * pow(3, odd)
        excluded |= margin >= 0
        if best_margin is None or margin > best_margin:
            best_margin = margin
    return {
        "factor_complexity": complexities,
        "first_repeat_second_start": first,
        "maximum_previous_lcp": maxima,
        "best_finite_stammering": {
            "ratio": ef(best_stammer),
            "U_length": best_stammer_data[0],
            "V_length": best_stammer_data[1],
            "prefix_length": best_stammer_data[2],
        },
        "strongest_source_lower_expression": {
            "N_plus_1_strictly_greater_than": ef(best_source),
            "second_start": best_source_data[0],
            "repeat_width": best_source_data[1],
        },
        "Hq_repetition_excluded": excluded,
        "best_Hq_integer_margin": best_margin,
    }


def contacts(word: str) -> int:
    positions = [position for position, bit in enumerate(word) if bit == "1"]
    return sum(position == pow(3, rank).bit_length() - 1 for rank, position in enumerate(positions))


def expected_critical(maximum_q: int) -> dict[str, object]:
    if maximum_q != 17:
        fail("critical accepted bound")
    grouped = safe_words(maximum_q)
    minima = {}
    for q, words in grouped.items():
        for word in words:
            key = (q, endpoint_of(word))
            minima[key] = min(minima.get(key, len(word)), len(word))
    heights = height_rows(maximum_q)
    stream = hashlib.sha256()
    counts = {}
    best_stammer = (Fraction(1), None)
    best_source = (Fraction(0), None)
    totals = Counter()
    for q in range(1, maximum_q + 1):
        length = pow(3, q).bit_length() - 1
        critical = sorted(word for word in grouped[q] if len(word) == length)
        h_num, h_den, K = heights[q]
        geodesic_count = excluded_count = geo_excluded = maximum_contacts = 0
        for word in critical:
            endpoint = endpoint_of(word)
            source = source_of(word)
            geodesic = minima[(q, endpoint)] == len(word)
            geodesic_count += geodesic
            profile = direct_word_profile(word, h_num, h_den)
            excluded = bool(profile["Hq_repetition_excluded"])
            excluded_count += excluded
            geo_excluded += geodesic and excluded
            contact = contacts(word)
            maximum_contacts = max(maximum_contacts, contact)
            stammer_data = profile["best_finite_stammering"]["ratio"]
            stammer = Fraction(int(stammer_data["numerator"]), int(stammer_data["denominator"]))
            if stammer > best_stammer[0]:
                best_stammer = (stammer, [q, word, source])
            lower_data = profile["strongest_source_lower_expression"]["N_plus_1_strictly_greater_than"]
            lower = Fraction(int(lower_data["numerator"]), int(lower_data["denominator"]))
            if lower > best_source[0]:
                best_source = (lower, [q, word, source])
            row = [q, word, source, endpoint, int(geodesic), contact, profile]
            stream.update((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii"))
        counts[str(q)] = {
            "K_q_minus_1": length,
            "K_q": K,
            "H_q": ef(Fraction(h_num, h_den)),
            "critical_words": len(critical),
            "geodesic_words": geodesic_count,
            "repetition_excluded": excluded_count,
            "geodesic_repetition_excluded": geo_excluded,
            "maximum_contacts": maximum_contacts,
        }
        totals["critical_words"] += len(critical)
        totals["geodesic_words"] += geodesic_count
        totals["repetition_excluded"] += excluded_count
        totals["geodesic_repetition_excluded"] += geo_excluded
    return {
        "format": "collatz-phase21-critical-repetitions-v1",
        "claim": {"P132": "VERIFIED_THEOREM", "E33": "VERIFIED_FINITE", "H89": "OPEN"},
        "maximum_Q": maximum_q,
        "counts_by_Q": counts,
        "totals": dict(totals),
        "maximum_finite_stammering_ratio": {"value": ef(best_stammer[0]), "witness": best_stammer[1]},
        "maximum_source_lower_expression": {"value": ef(best_source[0]), "witness": best_source[1]},
        "row_digest_sha256": stream.hexdigest(),
        "row_storage": "omitted; verifier rebuilds every critical word from string recursion",
        "certificate_rule": "reject if 2^(n+h(j))*D_q >= (B_q_max+D_q)*3^h(j)",
        "finite_boundary": "Q<=17 exclusion counts do not prove an eventual H89 repetition theorem.",
        "proves_collatz": False,
    }


def parity_word(source: int, length: int) -> str:
    result = []
    for _ in range(length):
        result.append(str(source % 2))
        source = step(source)
    return "".join(result)


def expand(values: list[int], length: int) -> str:
    result = "".join("1" + "0" * (value - 1) for value in values)
    if len(result) < length:
        fail("formal exponent expansion")
    return result[:length]


def mechanical(length: int) -> str:
    result = ["0"] * length
    q = 0
    while True:
        position = pow(3, q).bit_length() - 1
        if position >= length:
            break
        result[position] = "1"
        q += 1
    return "".join(result)


def square_controller(length: int) -> str:
    floor_value = defect = total = q = 0
    values = []
    while total < length:
        next_floor = pow(3, q + 1).bit_length() - 1
        raise_defect = next_floor - floor_value == 2 and defect < isqrt(q + 1)
        exponent = next_floor - floor_value - int(raise_defect)
        values.append(exponent)
        total += exponent
        defect += int(raise_defect)
        floor_value = next_floor
        q += 1
    return expand(values, length)


def interval_controller(length: int) -> str:
    state = Fraction(3, 2)
    values = []
    total = 0
    while total < length:
        exponent = 1 if state <= Fraction(5, 3) else 2
        values.append(exponent)
        total += exponent
        state = (3 * state - 1) / pow(2, exponent)
    return expand(values, length)


def mixed_schedule(length: int) -> str:
    q = 0
    bits = []
    for elapsed in range(length):
        bit = pow(3, q) <= 8 * pow(2, elapsed)
        bits.append(str(int(bit)))
        q += int(bit)
    return "".join(bits)


def repeat(pattern: str, length: int) -> str:
    return "".join(pattern[index % len(pattern)] for index in range(length))


def small_profile(word: str, maximum: int) -> dict[str, object]:
    maxima = [0] * len(word)
    for later in range(1, len(word)):
        maxima[later] = max(direct_common(word, earlier, later) for earlier in range(later))
    first = earliest_repeats(maxima, maximum)
    best = (Fraction(1), 0, 0, 1)
    for start in range(len(word)):
        for period in range(1, len(word) - start):
            common = direct_common(word, start, start + period)
            if common:
                total = start + period + common
                ratio = Fraction(total, start + period)
                if ratio > best[0]:
                    best = (ratio, start, period, total)
    return {
        "first_repeat_second_start": first,
        "maximum_lcp": max(maxima, default=0),
        "best_finite_stammering": {"ratio": ef(best[0]), "U_length": best[1], "V_length": best[2], "prefix_length": best[3]},
    }


def expected_controls(length: int, maximum: int) -> dict[str, object]:
    if length != 512 or maximum != 64:
        fail("control accepted bounds")
    definitions = [
        ("all-contact", "formal", mechanical(length)),
        ("NG22-square-root", "formal", square_controller(length)),
        ("NG22-interval", "formal", interval_controller(length)),
        ("P109-balanced", "formal", mixed_schedule(length)),
        ("source-167", "positive-source", parity_word(167, length)),
        ("source-1126015", "positive-source", parity_word(1126015, length)),
        ("source-1394431", "positive-source", parity_word(1394431, length)),
        ("(110|111)*", "formal", repeat("110111", length)),
        ("A-periodic", "formal", repeat(A, length)),
        ("B-periodic", "formal", repeat(B, length)),
        ("A8B8-periodic", "formal", repeat(A * 8 + B * 8, length)),
    ]
    sequences = [{"name": name, "kind": kind, "length": len(word), **small_profile(word, maximum)} for name, kind, word in definitions]
    family_rows = []
    for m in range(2, 21):
        for family, source in (("2^m-1", pow(2, m) - 1), ("8^m-5", pow(8, m) - 5)):
            family_rows.append({"family": family, "m": m, "source": str(source), **small_profile(parity_word(source, 128), 32)})
    for blocks in range(1, 5):
        for selection in itertools.product(("110", "111"), repeat=blocks):
            word = "".join(selection)
            family_rows.append({"family": "(110|111)^*", "word": word, "kind": "formal", **small_profile(word, min(32, len(word)))})
    for r in range(1, 9):
        for s in range(1, 9):
            word = A * r + B * s
            family_rows.append({"family": "A^rB^s", "r": r, "s": s, "word": word, "kind": "formal", **small_profile(word, min(32, len(word)))})
    return {
        "format": "collatz-phase21-controls-v1",
        "claim": {"E33": "VERIFIED_FINITE", "H112": "OPEN", "H72": "OPEN"},
        "prefix_length": length,
        "maximum_repeat_width": maximum,
        "sequences": sequences,
        "family_rows": family_rows,
        "row_digest_sha256": object_hash([sequences, family_rows]),
        "scope_boundary": "formal words are repetition falsifiers only; they are not asserted to have one positive ordinary infinite source",
        "proves_collatz": False,
    }


def expected_theory() -> dict[str, object]:
    return {
        "format": "collatz-phase21-theory-v1",
        "map": "T(x)=x/2 for even x and (3x+1)/2 for odd x; v_t=x_t mod 2; h(t)=sum_(r<t)v_r",
        "claims": {
            "P125": {"status": "VERIFIED_THEOREM", "statement": "For integers a!=b, LCP(v(a),v(b))=v2(a-b); equivalently equal first n input parities iff a==b mod 2^n.", "proof": "At one step, the output difference is an odd multiple of (a-b)/2 when inputs have equal parity; induction gives both directions and the first differing bit."},
            "P126": {"status": "VERIFIED_THEOREM", "statement": "For a positive non-eventually-periodic orbit, a repeated width-n factor at i<j obeys 2^(n+h(j)) < (N+1)3^h(j).", "strictness": "state distinctness gives 2^n<=abs(x_j-x_i)<max(x_i,x_j); replacing < by <= is invalid", "growth": "(x_t+1)2^h(t)<=(N+1)3^h(t)"},
            "P127": {"status": "VERIFIED_THEOREM", "statement": "Every positive non-eventually-periodic orbit parity word satisfies p(n)>(n-log2(N+1))/log2(3/2), hence liminf p(n)/n>=1/log2(3/2).", "exact_acceptance": "2^(n+h(p(n))) < (N+1)3^h(p(n)); logarithms only restate the exact integer inequality"},
            "P128": {"status": "CONDITIONAL", "statement": "Assuming EXT08, every positive rational noncyclic parity word satisfies limsup p(n)/n>=log(3)/log(3/2).", "dependency": "EXT08 supplies only a subsequence h(m_k)/m_k->log(2)/log(3)"},
            "P129": {"status": "VERIFIED_THEOREM", "statement": "The Adamczewski-Bugeaud Diophantine exponent of a positive non-eventually-periodic orbit parity word is at most log2(3).", "definition_repair": "Condition (*) uses increasing |V_n^w_n|. Non-eventual periodicity forces |U_nV_n|->infinity along the relevant sequence, so log2(N+1)/|U_nV_n| vanishes."},
            "P130": {"status": "VERIFIED_THEOREM", "statement": "If a positive non-eventually-periodic orbit begins with W^r, then N+1>2^((r-1)|W|)(2/3)^|W|_1; in particular a square period d has d<log_(4/3)(N+1).", "scope": "internal powers require the local source x_i and are not bounded by the original N alone"},
            "P131": {"status": "VERIFIED_THEOREM", "statement": "For distinct first m+1 orbit states with peak H_m, p(n)>=ceil((m+1)/(1+floor((H_m-1)/2^n))); hence p(ceil(log2 H_m))>=m+1.", "consequences": "polynomial complexity forces stretched-exponential peaks; zero entropy forces log(H_m)/log(m)->infinity"},
            "P132": {"status": "VERIFIED_THEOREM", "statement": "Under P54, a critical-word repeat is impossible when 2^(n+h(j)) >= (H_q+1)3^h(j); equivalently 2^(n+h(j))D_q >= (B_q_max+D_q)3^h(j).", "scope": "an exact finite rejection rule, not an eventual H89 theorem"},
        },
        "supersession": "P127 unconditionally strengthens the positive-integer conclusions of conditional P123/P124; their external historical statements remain in the ledger.",
        "open_target": "Force repeats violating P132, or force P115 nonzero lifts from their absence, on every relevant infinite critical branch.",
        "what_this_result_does_not_prove": "No peak upper bound, repeat-forces-lift theorem, eventual H89 certificate, positive-source exclusion, nontrivial-cycle exclusion, or Collatz proof is obtained.",
        "proves_collatz": False,
    }


def expected_literature() -> dict[str, object]:
    rows = [
        {"id": "EXT14", "classification": "EXTERNAL_THEOREM", "authors": "Daniel J. Bernstein and Jeffrey C. Lagarias", "title": "The 3x + 1 Conjugacy Map", "year": 1996, "doi": "10.4153/CJM-1996-060-x", "used_for": "novelty context only; P125 is rederived internally"},
        {"classification": "DEFINITION_CONTEXT", "authors": "Boris Adamczewski and Yann Bugeaud", "title": "Dynamics for beta-shifts and Diophantine approximation", "year": 2007, "doi": "10.1017/S0143385707000223", "used_for": "Condition (*) and Diophantine exponent convention in P129"},
        {"classification": "DEFINITION_CONTEXT", "authors": "Yann Bugeaud and Dong Han Kim", "title": "A new complexity function, repetitions in Sturmian words, and irrationality exponents of Sturmian numbers", "year": 2018, "arxiv": "1510.00279", "used_for": "r(n,x) smallest-prefix convention; R_v(n)=r(n,v)-n"},
        {"classification": "DEFINITION_CONTEXT", "authors": "Jeremy Nicholson and Narad Rampersad", "title": "Initial non-repetitive complexity of infinite words", "year": 2016, "doi": "10.1016/j.dam.2016.03.010", "used_for": "initial nonrepetitive-complexity terminology"},
        {"classification": "RELATED_CONTEXT", "authors": "Tristan Sterin", "title": "Binary expression of ancestors in the Collatz graph", "year": 2019, "arxiv": "1907.00775", "used_for": "binary carry and first-source context; not an input to P125-P132"},
        {"classification": "EXTERNAL_THEOREM", "id": "EXT08", "authors": "Luis Lopez and Peter Stoll", "title": "The 3x+1 function on the rationals", "year": 2021, "arxiv": "2101.12747", "used_for": "the liminf density input to conditional P128 only"},
    ]
    return {
        "format": "collatz-phase21-literature-audit-v1",
        "sources": rows,
        "novelty_search": "Targeted searches found the standard parity conjugacy and word-complexity definitions but no primary source for the exact Collatz factor-complexity slopes. Absence from this search is not a literature-wide novelty claim.",
        "dependency_boundary": "P125-P127 and P129-P132 are repository derivations; P128 alone uses EXT08. Terminology citations are not promoted to proof dependencies.",
        "proves_collatz": False,
    }


def verify_metadata(root: Path) -> tuple[dict[str, object], dict[str, object]]:
    theory = load(root / "phase21_theory.json")
    if theory != expected_theory():
        fail("theory reconstruction or scope boundary")
    literature = load(root / "phase21_literature_audit.json")
    if literature != expected_literature():
        fail("literature dependency audit")
    return theory, literature


def verify_all(root: Path) -> dict[str, object]:
    _, literature = verify_metadata(root)

    direct = load(root / "phase21_direct_orbits.json")
    interval = direct.get("source_interval")
    maximum = direct.get("maximum_repeat_width")
    if not isinstance(interval, list) or interval != [1, 300000] or maximum != 64:
        fail("direct artifact bounds")
    if direct != expected_direct(interval[1], maximum):
        fail("direct orbit reconstruction")

    critical = load(root / "phase21_critical_repetitions.json")
    maximum_q = critical.get("maximum_Q")
    if maximum_q != 17 or critical != expected_critical(maximum_q):
        fail("critical repetition reconstruction")

    controls = load(root / "phase21_controls.json")
    if controls != expected_controls(512, 64):
        fail("adversarial control reconstruction")

    obstruction = (root / "phase21_obstruction_report.md").read_text(encoding="utf-8")
    for required in ("502523", "406353", "160429", "120982", "proves_collatz=false"):
        if required not in obstruction:
            fail("obstruction report mismatch")
    return {
        "format": "collatz-phase21-verifier-v1",
        "valid": True,
        "independence": "literal states, byte-table reversed keys, string-recursive critical words, direct substring tuples; no generator import",
        "claims": {
            "P125": "VERIFIED_THEOREM", "P126": "VERIFIED_THEOREM", "P127": "VERIFIED_THEOREM",
            "P128": "CONDITIONAL", "P129": "VERIFIED_THEOREM", "P130": "VERIFIED_THEOREM",
            "P131": "VERIFIED_THEOREM", "P132": "VERIFIED_THEOREM", "E33": "VERIFIED_FINITE",
            "H89": "OPEN", "H112": "OPEN", "H72": "OPEN",
        },
        "direct_sources": direct["sources_checked"],
        "critical_totals": critical["totals"],
        "control_sequences": len(controls["sequences"]),
        "adversarial_rows": len(controls["family_rows"]),
        "external_sources_audited": len(literature["sources"]),
        "proves_collatz": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    report = verify_all(args.artifact_dir)
    if args.write_report:
        save(args.write_report, report)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
