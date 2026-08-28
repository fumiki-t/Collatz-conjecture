#!/usr/bin/env python3
"""Independent exact verifier for Phase 15B ancestral-frontier evidence.

This module intentionally does not import the Phase 15B generator.  It uses
literal strings and descending source scans to reconstruct the accepted JSON.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
getcontext().prec = 40

ABLOCK = "11101"
BBLOCK = "1100"
MACRO_ZERO = "1111111111110000000"


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} is not an object")
    return value


def step(value: int) -> int:
    if value % 2:
        return (3 * value + 1) // 2
    return value // 2


def translation(word: str) -> int:
    result = 0
    power = 1
    for bit in word:
        if bit == "1":
            result = 3 * result + power
        elif bit != "0":
            fail("non-binary word")
        power *= 2
    return result


def trace(source: int, word: str) -> list[int]:
    values = [source]
    value = source
    for expected in word:
        if str(value % 2) != expected:
            fail("literal parity mismatch")
        value = step(value)
        values.append(value)
    return values


def is_safe(word: str) -> bool:
    q = 0
    for length, bit in enumerate(word, 1):
        q += bit == "1"
        if pow(3, q) <= pow(2, length):
            return False
    return bool(word)


# Tuple: word, L, Q, B, least positive source, least positive endpoint.
def row(word: str) -> tuple[str, int, int, int, int, int]:
    length = len(word)
    q = word.count("1")
    B = translation(word)
    two, three = pow(2, length), pow(3, q)
    source = (-B * pow(three, -1, two)) % two or two
    endpoint = (B * pow(two, -1, three)) % three or three
    if trace(source, word)[-1] != endpoint:
        fail("canonical reconstruction")
    return word, length, q, B, source, endpoint


def record(word: str) -> dict[str, object]:
    data = row(word)
    D = data[3] + pow(2, data[1]) - pow(3, data[2])
    return {
        "word": word,
        "L": data[1],
        "Q": data[2],
        "B": data[3],
        "D": D,
        "source": data[4],
        "endpoint": data[5],
        "safe": is_safe(word),
    }


def safe_steps(source: int):
    """Independent literal iterator; comparison uses fresh integer powers."""
    value = source
    bits = ""
    q = 0
    for length in range(1, 20_001):
        bit = value % 2
        bits += str(bit)
        q += bit
        value = step(value)
        if pow(3, q) <= pow(2, length):
            return
        yield length, value, bits
    fail(f"safe path limit for {source}")


def coefficient_depth(source: int) -> int:
    depth = 0
    for depth, _endpoint, _word in safe_steps(source):
        pass
    return depth


def endpoint_minima_descending(bound: int) -> tuple[dict[int, int], dict[str, int]]:
    minima: dict[int, int] = {}
    occurrences = 0
    maximum_endpoint = 0
    # Descending scan deliberately differs from the generator.  Overwriting
    # makes the last source for an endpoint its least positive tested source.
    start = bound if bound % 2 else bound - 1
    for source in range(start, 0, -2):
        for _length, endpoint, _word in safe_steps(source):
            occurrences += 1
            maximum_endpoint = max(maximum_endpoint, endpoint)
            minima[endpoint] = source
    digest = hashlib.sha256()
    for endpoint in sorted(minima):
        digest.update(f"{endpoint}|{minima[endpoint]}\n".encode("ascii"))
    return minima, {
        "odd_sources_scanned": (bound + 1) // 2,
        "safe_occurrence_count": occurrences,
        "endpoint_minimum_count": len(minima),
        "minimum_update_count": len(minima),
        "maximum_endpoint": maximum_endpoint,
        "endpoint_minima_digest_sha256": digest.hexdigest(),
    }


def witness_to(source: int, endpoint: int) -> tuple[int, str]:
    for length, value, word in safe_steps(source):
        if value == endpoint:
            return length, word
    fail("minimum source does not reach endpoint safely")


def domination(source: int, depth: int, length: int, competitor: int, endpoint: int) -> dict[str, object]:
    source_word = next(word for step_number, value, word in safe_steps(source) if step_number == length and value == endpoint)
    competitor_steps, competitor_word = witness_to(competitor, endpoint)
    return {
        "source": source,
        "ancestral_safe_depth": depth,
        "domination_step": length,
        "endpoint": endpoint,
        "source_word": source_word,
        "competitor": competitor,
        "competitor_steps": competitor_steps,
        "competitor_word": competitor_word,
        "competitor_word_is_safe": is_safe(competitor_word),
        "source_coefficient_safe_depth": coefficient_depth(source),
    }


def expected_ancestral(bound: int) -> dict[str, object]:
    minima, statistics = endpoint_minima_descending(bound)
    maximum = -1
    table = []
    counts: Counter[str] = Counter()
    named_sources = {270271, 381727, 1126015, 1394431}
    named = {}
    digest = hashlib.sha256()
    for source in range(3, bound + 1, 2):
        competitor = minima.get(source, source)
        if competitor < source:
            depth, termination, length = -1, "domination", 0
            endpoint = source
        else:
            depth = 0
            termination = "coefficient_crossing"
            length = 1
            competitor = None
            endpoint = source
            for current_length, value, _word in safe_steps(source):
                depth = current_length
                smaller = minima.get(value, value)
                if smaller < source:
                    depth = current_length - 1
                    termination = "domination"
                    length = current_length
                    competitor = smaller
                    endpoint = value
                    break
                length = current_length + 1
        counts[termination] += 1
        digest.update(f"{source}|{depth}|{termination}|{length}|{competitor or 0}\n".encode("ascii"))
        if depth > maximum:
            item: dict[str, object] = {
                "ancestral_safe_depth": depth,
                "first_source": source,
                "termination": termination,
                "termination_step": length,
                "coefficient_safe_depth": coefficient_depth(source),
            }
            if competitor is not None:
                item["domination"] = domination(source, depth, length, competitor, endpoint)
            table.append(item)
            maximum = depth
        if source in named_sources and competitor is not None:
            named[str(source)] = domination(source, depth, length, competitor, endpoint)
    expected_named = {str(value) for value in named_sources if value <= bound}
    if set(named) != expected_named:
        fail("named domination witnesses")
    result = {
        "format": "collatz-phase15b-ancestral-scan-v1",
        "source_bound": bound,
        "endpoint_height_cutoff": None,
        **statistics,
        "source_depth_digest_sha256": digest.hexdigest(),
        "termination_counts": dict(sorted(counts.items())),
        "record_table": table,
        "maximum_ancestral_safe_depth_in_range": maximum,
        "M_star_210_lower_bound": bound + 1 if maximum < 210 else None,
        "named_domination_witnesses": named,
        "completeness": "Every odd competitor source below each tested n<=bound was scanned through its full coefficient-safe prefix; safe paths cannot start at an even source, and endpoint height was not truncated.",
        "what_this_result_does_not_prove": "The finite source bound gives no eventual lower bound for M_star and does not prove Collatz.",
        "proves_collatz": False,
    }
    del minima
    gc.collect()
    return result


def enumerate_safe(q_cap: int) -> dict[int, list[tuple[str, int, int, int, int, int]]]:
    grouped = {q: [] for q in range(1, q_cap + 1)}
    frontier = [("", 0, 0)]
    final_length = pow(3, q_cap).bit_length() - 1
    for length in range(1, final_length + 1):
        following = []
        for prefix, q, B in frontier:
            if q and pow(3, q) > pow(2, length):
                word = prefix + "0"
                following.append((word, q, B))
                grouped[q].append(row(word))
            if q < q_cap and pow(3, q + 1) > pow(2, length):
                word = prefix + "1"
                new_B = 3 * B + pow(2, length - 1)
                following.append((word, q + 1, new_B))
                item = row(word)
                if item[3] != new_B:
                    fail("translation recurrence")
                grouped[q + 1].append(item)
        frontier = following
    return grouped


def source_at(item: tuple, endpoint: int) -> int | None:
    modulus = pow(3, item[2])
    residue = endpoint % modulus or modulus
    if residue != item[5]:
        return None
    index = (endpoint - residue) // modulus
    return item[4] + index * pow(2, item[1]) if index >= 0 else None


def coefficient_ge(left: tuple, right: tuple) -> bool:
    return pow(3, left[2]) * pow(2, right[1]) >= pow(3, right[2]) * pow(2, left[1])


def run_of_ones(word: str) -> int:
    return len(word) - len(word.lstrip("1"))


def shift_key(item: tuple) -> tuple[int, int, int] | None:
    run = run_of_ones(item[0])
    if run == item[1]:
        return None
    D = item[3] + pow(2, item[1]) - pow(3, item[2])
    if D <= 0 or D % pow(2, run):
        fail("shifted valuation")
    return item[2], item[1] - run, D // pow(2, run)


def expected_frontier(q_cap: int) -> dict[str, object]:
    grouped = enumerate_safe(q_cap)
    indexes = {}
    shortest = {}
    for q, rows in grouped.items():
        index = defaultdict(list)
        for item in rows:
            index[item[5]].append(item)
            key = shift_key(item)
            if key is not None:
                shortest[key] = min(shortest.get(key, item[1]), item[1])
        indexes[q] = index
    digest = hashlib.sha256()
    counts = {}
    for q_target, rows in grouped.items():
        same = uniform = endpoint_specific = jump = 0
        for target in rows:
            has_same = has_uniform = has_specific = False
            for q_ancestor in range(1, q_cap + 1):
                modulus = pow(3, q_ancestor)
                residue = target[5] % modulus or modulus
                for ancestor in indexes[q_ancestor].get(residue, ()):
                    source = source_at(ancestor, target[5])
                    if source is None or source >= target[4] or not coefficient_ge(ancestor, target):
                        continue
                    has_specific = True
                    has_uniform |= q_ancestor <= q_target
                    has_same |= q_ancestor == q_target
            key = shift_key(target)
            has_jump = key is not None and shortest[key] < target[1]
            same += has_same
            uniform += has_uniform
            endpoint_specific += has_specific
            jump += has_jump
            digest.update(f"{target[0]}|{target[4]}|{target[5]}|{int(has_same)}|{int(has_uniform)}|{int(has_specific)}|{int(has_jump)}\n".encode("ascii"))
        counts[str(q_target)] = {
            "safe_words": len(rows),
            "same_Q_uniform_dominated": same,
            "Q_ancestor_le_Q_target_uniform_dominated": uniform,
            "endpoint_specific_Q_le_cutoff_dominated": endpoint_specific,
            "shifted_jump_dominated": jump,
        }
    del grouped
    gc.collect()
    return {
        "format": "collatz-phase15b-frontier-v1",
        "maximum_Q": q_cap,
        "counts_by_target_Q": counts,
        "row_digest_sha256": digest.hexdigest(),
        "classification_boundary": "Uniform dominance uses endpoint-cylinder inclusion and Q_ancestor<=Q_target. Endpoint-specific dominance additionally admits higher-Q cylinders only for the recorded ordinary endpoint and only through the cutoff.",
        "proves_collatz": False,
    }


def first_upcrossings(q_cap: int) -> list[tuple]:
    result = []
    frontier = [("", 0)]
    final_length = pow(3, q_cap).bit_length() - 1
    for length in range(1, final_length + 1):
        following = []
        for prefix, q in frontier:
            following.append((prefix + "0", q))
            if q >= q_cap:
                continue
            candidate = prefix + "1"
            next_q = q + 1
            if pow(3, next_q) > pow(2, length):
                result.append(row(candidate[::-1]))
            else:
                following.append((candidate, next_q))
        frontier = following
    return result


def encoded(value: Fraction) -> dict[str, str]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": f"{Decimal(value.numerator) / Decimal(value.denominator):.24f}",
    }


def expected_renewal(q_cap: int) -> dict[str, object]:
    blocks = first_upcrossings(q_cap)
    residues = defaultdict(set)
    violations = 0
    for item in blocks:
        residues[item[2]].add(item[5])
        if item[0] != "1" and item[1] != pow(3, item[2]).bit_length() - 1:
            violations += 1
    primitives: dict[int, set[int]] = defaultdict(set)
    counts = {}
    mass = Fraction()
    for q in range(1, q_cap + 1):
        for residue in sorted(residues[q]):
            if not any((residue % pow(3, old_q) or pow(3, old_q)) in old for old_q, old in primitives.items()):
                primitives[q].add(residue)
        counts[str(q)] = len(primitives[q])
        mass += Fraction(len(primitives[q]), pow(3, q))
    digest = hashlib.sha256()
    for q in sorted(primitives):
        for residue in sorted(primitives[q]):
            digest.update(f"{q}|{residue}\n".encode("ascii"))
    return {
        "format": "collatz-phase15b-renewal-trie-v1",
        "maximum_Q": q_cap,
        "renewal_block_count": len(blocks),
        "new_primitive_cylinders_by_Q": counts,
        "primitive_digest_sha256": digest.hexdigest(),
        "finite_union_Haar_mass": encoded(mass),
        "finite_conditional_unit_coverage": encoded(Fraction(3, 2) * mass),
        "beatty_length_violation_count": violations,
        "analytic_upper_bound": "The full union has Haar mass at most sigma<7/12 by P78, hence conditional unit complement greater than 1/8.",
        "pointwise_boundary": "A positive-measure 3-adic complement does not imply that any positive ordinary integer is outside the covered set.",
        "proves_collatz": False,
    }


def fixed_q(q_target: int):
    final_length = pow(3, q_target).bit_length() - 1

    def walk(word: str, q: int):
        length = len(word)
        if q == q_target:
            yield row(word)
        if length >= final_length:
            return
        next_length = length + 1
        if q and pow(3, q) > pow(2, next_length):
            yield from walk(word + "0", q)
        if q < q_target and pow(3, q + 1) > pow(2, next_length):
            yield from walk(word + "1", q + 1)

    yield from walk("", 0)


def expected_compression(q_cap: int) -> dict[str, object]:
    maxima = {}
    top_witness = None
    digest = hashlib.sha256()
    for q in range(1, q_cap + 1):
        minimum: dict[int, tuple] = {}
        count = 0
        for item in fixed_q(q):
            count += 1
            old = minimum.get(item[5])
            if old is None or item[1] < old[1]:
                minimum[item[5]] = item
        maximum_gain = -1
        witness = None
        for item in fixed_q(q):
            short = minimum[item[5]]
            gain = item[1] - short[1]
            if gain > maximum_gain or (gain == maximum_gain and (witness is None or item[4] < witness["d_source"])):
                maximum_gain = gain
                witness = {
                    "d": item[0],
                    "a": short[0],
                    "Q": q,
                    "gain": gain,
                    "d_source": item[4],
                    "a_source": short[4],
                    "endpoint": item[5],
                }
        if witness is None:
            fail("compression witness")
        maxima[str(q)] = {
            "safe_words": count,
            "endpoint_classes": len(minimum),
            "maximum_gain": maximum_gain,
            "witness": witness,
        }
        digest.update(f"{q}|{count}|{len(minimum)}|{maximum_gain}|{witness['d']}|{witness['a']}\n".encode("ascii"))
        if q == q_cap:
            top_witness = witness
        del minimum
        gc.collect()
    return {
        "format": "collatz-phase15b-compression-v1",
        "maximum_Q": q_cap,
        "by_Q": maxima,
        "row_digest_sha256": digest.hexdigest(),
        "maximum_layer_witness": top_witness,
        "NG27": {
            "repository_status": "REFUTED",
            "hypothesis": "Same-Q total compression gain is always at most three.",
            "counterexample": top_witness,
        },
        "asymptotic_boundary": "A bounded maximum gain through Q=19 gives no composable or linear gain theorem.",
        "proves_collatz": False,
    }


def expected_theory() -> dict[str, object]:
    return {
        "format": "collatz-phase15b-theory-v1",
        "P89": {"repository_status": "VERIFIED_THEOREM", "statement": "For a least positive Collatz counterexample N, every endpoint along a coefficient-safe prefix has N as its minimum positive coefficient-safe ancestor.", "scope": "Uses only least-counterexample minimality and deterministic shared future; it applies to finite prefixes of cyclic and nonperiodic branches."},
        "P90": {"repository_status": "CONDITIONAL", "statement": "Under P54's finite-first-crossing hypotheses, M_star(K_q-1)<=N<=H_q. An eventual M_star(K_q-1)>H_q theorem plus a finite remainder also excludes a never-crossing least counterexample because P89 gives M_star(k)<=N for every k while Phase 6 proves H_q>q/6.", "missing_target": "H89 is OPEN: no eventual M_star lower bound is proved."},
        "P91": {"repository_status": "VERIFIED_THEOREM", "cross_Q_identity": "If Q(d)=Q(a)+s and L(d)=L(a)+k, then F_d(y)=F_a(x) on 3^s*y=2^k*x+m iff 2^k*B(a)-B(d)=3^Q(a)*m.", "prefix_lift": "A common left prefix p lifts the relation iff 3^Q(p) divides (2^k-3^s)B(p)+2^L(p)m; the quotient is the lifted carry M.", "legality_boundary": "Positivity, literal cylinders, source descent, and safety are separate."},
        "P92": {"repository_status": "VERIFIED_THEOREM", "statement": "If C_d is contained in C_a, c(a)>=c(d), and the positive a-source at d's first positive endpoint is smaller than the d-source, then the a-source stays smaller at every later d occurrence.", "proof": "The source difference g_d(Y)-g_a(Y) is affine with nonnegative slope 1/c(d)-1/c(a)."},
        "P93": {"repository_status": "VERIFIED_THEOREM", "statement": "Every finite coefficient-safe word has a unique decomposition at successive strict future discrepancy minima into coefficient-safe renewal blocks whose reversals are first-upcrossing codewords."},
        "P94": {"repository_status": "VERIFIED_THEOREM", "statement": "A nontrivial renewal block of odd count q exists only when floor(q*beta)=floor((q-1)*beta)+1, beta=log2(3/2), and then L=floor(q*log2(3)).", "exact_decision": "The proof uses only strict comparisons between powers of 2 and 3; decimal logarithms are not certificate inputs."},
        "P95": {"repository_status": "VERIFIED_THEOREM", "statement": "D(w)=B(w)+2^L-3^Q satisfies the shifted affine identity and D(ab)=3^Q(b)D(a)+2^L(a)D(b); if the initial one-run r is followed by zero then v2(D)=r. Same-Q jump coalescence y+1=2^k(x+1) is equivalent to D(d)=2^kD(a).", "closure": "Jump classes (Q,L-r,D/2^r) are preserved by a common right suffix and by a common left all-one prefix."},
        "P96": {"repository_status": "VERIFIED_THEOREM", "statement": "The 3-adic union of endpoints with a nonempty safe predecessor is covered by renewal-block cylinders, so its Haar mass is at most sigma<7/12 by P78; inside the unit space the uncovered conditional proportion exceeds 1/8.", "boundary": "This distributional result does not exclude any specified positive ordinary integer."},
        "cross_Q_example": {"d": record("111110100"), "a": record("1"), "s": 5, "k": 8, "m": -147, "relation": "3^5*287=2^8*273-147"},
        "jump_example": {"d": record("111100"), "a": record("11101"), "k": 1},
        "gap12_dependency": "The finite {1,2}-gap endpoint injectivity theorem is already P88 and is not assigned a new claim ID.",
        "what_this_result_does_not_prove": "H89, P80, H72, a composable linear compression gain, cycle exclusion, and Collatz remain unproved.",
        "proves_collatz": False,
    }


def odd_part(value: int) -> int:
    while value % 2 == 0:
        value //= 2
    return value


def parity_prefix(source: int, length: int) -> str:
    bits = []
    value = source
    for _ in range(length):
        bits.append(str(value % 2))
        value = step(value)
    return "".join(bits)


def seed_rows() -> list[tuple[str, int]]:
    seeds = [("2^m-1", pow(2, exponent) - 1) for exponent in range(3, 25)]
    seeds += [("8^m-5", pow(8, exponent) - 5) for exponent in range(1, 11)]
    for count in range(1, 11):
        for mask in range(pow(2, count)):
            word = "".join("111" if mask & pow(2, index) else "110" for index in range(count))
            seeds.append(("(110|111)^*", int(word, 2)))
    seeds += [("A=11101", int(ABLOCK, 2)), ("B=1100", int(BBLOCK, 2))]
    seeds += [("A^rB^s", int(ABLOCK * r + BBLOCK * s, 2)) for r in range(1, 9) for s in range(1, 9)]
    return seeds


def expected_adversarial() -> dict[str, object]:
    digest = hashlib.sha256()
    counts: Counter[str] = Counter()
    for family, raw in seed_rows():
        source = odd_part(raw)
        word = parity_prefix(source, 24)
        B = translation(word)
        q = word.count("1")
        residue = (-B * pow(pow(3, q), -1, pow(2, 24))) % pow(2, 24)
        if residue != source % pow(2, 24):
            fail("adversarial residue")
        counts[family] += 1
        digest.update(f"{family}|{raw}|{source}|{word}|{B}|{residue}\n".encode("ascii"))
    return {
        "format": "collatz-phase15b-adversarial-v1",
        "prefix_length": 24,
        "instance_count": sum(counts.values()),
        "family_counts": dict(sorted(counts.items())),
        "row_digest_sha256": digest.hexdigest(),
        "phase7_macro_zero": record(MACRO_ZERO),
        "named_boundaries": ["NG19", "NG21", "both NG22 models", "NG23", "NG24", "NG25", "NG26", "all-one prefixes", "{1,2}-gap formal core"],
        "proves_collatz": False,
    }


OBSTRUCTION = """# Phase 15B obstruction report

## Missing eventual theorem

The exact ancestral-minimality theorem strengthens the least-counterexample
state, and the source-5,000,000 scan may raise finite lower bounds. It does not
prove the eventual H89 inequality. Finite record growth is not extrapolated.

## Distributional/pointwise boundary

The renewal endpoint union occupies less than 7/12 of Z_3 and leaves more than
1/8 of the 3-adic unit space uncovered conditionally. A countable set of all
positive ordinary integers can nevertheless lie inside a smaller-measure
3-adic set. The measure theorem is not a pointwise least-counterexample
exclusion and does not prove P80 or H72.

## Compression obstruction NG27

The bounded guess that same-Q total compression gain never exceeds three
fails at Q=19. The exact jump witness has source relation
`44466175=16*2779135+15`, equivalently `y+1=16(x+1)`. A gain of four at one
finite layer gives no linear or composable gain theorem.

## What this result does not prove

- H89 or any eventual M_star lower bound;
- a uniform all-depth cross-Q frontier contraction;
- P80, H72, or exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
"""


def verify(artifact_dir: Path) -> dict[str, object]:
    theory = load(artifact_dir / "phase15b_theory.json")
    ancestral = load(artifact_dir / "phase15b_ancestral_scan.json")
    frontier = load(artifact_dir / "phase15b_frontier.json")
    renewal = load(artifact_dir / "phase15b_renewal_trie.json")
    compression = load(artifact_dir / "phase15b_compression.json")
    adversarial = load(artifact_dir / "phase15b_adversarial.json")
    try:
        obstruction = (artifact_dir / "phase15b_obstruction_report.md").read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot read phase15b_obstruction_report.md: {exc}")

    source_bound = ancestral.get("source_bound")
    frontier_q = frontier.get("maximum_Q")
    compression_q = compression.get("maximum_Q")
    if not isinstance(source_bound, int) or source_bound < 3:
        fail("ancestral source bound")
    if not isinstance(frontier_q, int) or frontier_q < 4:
        fail("frontier maximum Q")
    if not isinstance(compression_q, int) or compression_q < frontier_q:
        fail("compression maximum Q")

    if theory != expected_theory():
        fail("phase15b theory mismatch")
    if ancestral != expected_ancestral(source_bound):
        fail("phase15b ancestral scan mismatch")
    if frontier != expected_frontier(frontier_q):
        fail("phase15b frontier mismatch")
    if renewal != expected_renewal(frontier_q):
        fail("phase15b renewal trie mismatch")
    if compression != expected_compression(compression_q):
        fail("phase15b compression mismatch")
    if adversarial != expected_adversarial():
        fail("phase15b adversarial mismatch")
    if obstruction != OBSTRUCTION:
        fail("phase15b obstruction report mismatch")

    return {
        "format": "collatz-phase15b-verifier-v1",
        "valid": True,
        "source_bound": source_bound,
        "frontier_maximum_Q": frontier_q,
        "compression_maximum_Q": compression_q,
        "P89": "VERIFIED_THEOREM",
        "P90": "CONDITIONAL",
        "P91": "VERIFIED_THEOREM",
        "P92": "VERIFIED_THEOREM",
        "P93": "VERIFIED_THEOREM",
        "P94": "VERIFIED_THEOREM",
        "P95": "VERIFIED_THEOREM",
        "P96": "VERIFIED_THEOREM",
        "H89": "OPEN",
        "E25": "VERIFIED_FINITE",
        "E26": "VERIFIED_FINITE",
        "NG27": "REFUTED",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
