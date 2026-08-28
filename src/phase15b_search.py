#!/usr/bin/env python3
"""Generate exact Phase 15B ancestral-frontier evidence."""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)
getcontext().prec = 40

A_BITS = "11101"
B_BITS = "1100"
MACRO_ZERO = "1111111111110000000"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def word_constant(word: str) -> int:
    value = 0
    for position, bit in enumerate(word):
        if bit == "1":
            value = 3 * value + (1 << position)
        elif bit != "0":
            raise ValueError("binary word required")
    return value


def literal_trace(source: int, word: str) -> list[int]:
    values = [source]
    value = source
    for expected in word:
        if str(value & 1) != expected:
            raise AssertionError("literal parity mismatch")
        value = shortcut(value)
        values.append(value)
    return values


def safe_word(word: str) -> bool:
    three = two = 1
    for bit in word:
        two <<= 1
        if bit == "1":
            three *= 3
        if three <= two:
            return False
    return bool(word)


def renewal_decomposition(word: str) -> list[str]:
    """Cut a finite safe word at successive exact future discrepancy minima."""
    if not safe_word(word):
        raise ValueError("coefficient-safe word required")
    prefix_ones = [0]
    for bit in word:
        prefix_ones.append(prefix_ones[-1] + (bit == "1"))

    cuts = []
    start = 0
    while start < len(word):
        minimum = start + 1
        for position in range(start + 2, len(word) + 1):
            q_position = prefix_ones[position]
            q_minimum = prefix_ones[minimum]
            if 3**q_position * (1 << minimum) < 3**q_minimum * (1 << position):
                minimum = position
        cuts.append(word[start:minimum])
        start = minimum
    return cuts


def canonical(word: str) -> tuple[int, int, int, int, int]:
    length = len(word)
    q = word.count("1")
    B = word_constant(word)
    two = 1 << length
    three = 3**q
    source = (-B * pow(three, -1, two)) % two or two
    endpoint = (B * pow(two, -1, three)) % three or three
    if literal_trace(source, word)[-1] != endpoint:
        raise AssertionError("canonical occurrence")
    return length, q, B, source, endpoint


def safe_path(source: int):
    value = source
    three = two = 1
    word_bits = 0
    for step in range(1, 20_001):
        bit = value & 1
        word_bits = (word_bits << 1) | bit
        if bit:
            three *= 3
        two <<= 1
        value = shortcut(value)
        if three <= two:
            return
        yield step, value, word_bits, three
    raise RuntimeError(f"safe path limit for {source}")


def coefficient_depth(source: int) -> int:
    depth = 0
    for depth, _endpoint, _bits, _three in safe_path(source):
        pass
    return depth


def witness_to(source: int, endpoint: int) -> tuple[int, str]:
    for step, value, bits, _three in safe_path(source):
        if value == endpoint:
            return step, format(bits, f"0{step}b")
    raise AssertionError("minimum source does not reach endpoint safely")


def endpoint_minima(bound: int) -> tuple[dict[int, int], dict[str, int]]:
    minima: dict[int, int] = {}
    occurrences = updates = 0
    maximum_endpoint = 0
    for source in range(1, bound + 1, 2):
        for _step, endpoint, _bits, _three in safe_path(source):
            occurrences += 1
            maximum_endpoint = max(maximum_endpoint, endpoint)
            previous = minima.get(endpoint)
            if previous is None or source < previous:
                minima[endpoint] = source
                updates += 1
    digest = hashlib.sha256()
    for endpoint in sorted(minima):
        digest.update(f"{endpoint}|{minima[endpoint]}\n".encode("ascii"))
    return minima, {
        "odd_sources_scanned": (bound + 1) // 2,
        "safe_occurrence_count": occurrences,
        "endpoint_minimum_count": len(minima),
        "minimum_update_count": updates,
        "maximum_endpoint": maximum_endpoint,
        "endpoint_minima_digest_sha256": digest.hexdigest(),
    }


def ancestral_depth(source: int, minima: dict[int, int]) -> tuple[int, str, int, int | None]:
    if minima.get(source, source) < source:
        return -1, "domination", 0, minima[source]
    safe_depth = 0
    for step, endpoint, _bits, _three in safe_path(source):
        safe_depth = step
        competitor = minima.get(endpoint, endpoint)
        if competitor < source:
            return step - 1, "domination", step, competitor
    return safe_depth, "coefficient_crossing", safe_depth + 1, None


def domination_record(source: int, depth: int, step: int, competitor: int, endpoint: int) -> dict[str, object]:
    competitor_steps, competitor_word = witness_to(competitor, endpoint)
    source_word = ""
    for current_step, value, bits, _three in safe_path(source):
        if current_step == step:
            if value != endpoint:
                raise AssertionError("domination endpoint")
            source_word = format(bits, f"0{step}b")
            break
    return {
        "source": source,
        "ancestral_safe_depth": depth,
        "domination_step": step,
        "endpoint": endpoint,
        "source_word": source_word,
        "competitor": competitor,
        "competitor_steps": competitor_steps,
        "competitor_word": competitor_word,
        "competitor_word_is_safe": safe_word(competitor_word),
        "source_coefficient_safe_depth": coefficient_depth(source),
    }


def ancestral_scan(bound: int) -> dict[str, object]:
    minima, statistics = endpoint_minima(bound)
    records = []
    maximum = -1
    termination_counts: Counter[str] = Counter()
    named_sources = {270271, 381727, 1126015, 1394431}
    expected_named_sources = {value for value in named_sources if value <= bound}
    named = {}
    depth_digest = hashlib.sha256()
    for source in range(3, bound + 1, 2):
        depth, termination, step, competitor = ancestral_depth(source, minima)
        termination_counts[termination] += 1
        depth_digest.update(f"{source}|{depth}|{termination}|{step}|{competitor or 0}\n".encode("ascii"))
        if depth > maximum:
            row: dict[str, object] = {
                "ancestral_safe_depth": depth,
                "first_source": source,
                "termination": termination,
                "termination_step": step,
                "coefficient_safe_depth": coefficient_depth(source),
            }
            if competitor is not None:
                endpoint = next(value for s, value, _bits, _three in safe_path(source) if s == step)
                row["domination"] = domination_record(source, depth, step, competitor, endpoint)
            records.append(row)
            maximum = depth
        if source in named_sources and termination == "domination" and competitor is not None:
            endpoint = next(value for s, value, _bits, _three in safe_path(source) if s == step)
            named[str(source)] = domination_record(source, depth, step, competitor, endpoint)
    if set(named) != {str(value) for value in expected_named_sources}:
        raise AssertionError("named domination witnesses")
    result = {
        "format": "collatz-phase15b-ancestral-scan-v1",
        "source_bound": bound,
        "endpoint_height_cutoff": None,
        **statistics,
        "source_depth_digest_sha256": depth_digest.hexdigest(),
        "termination_counts": dict(sorted(termination_counts.items())),
        "record_table": records,
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


@dataclass(frozen=True, slots=True)
class Row:
    bits: int
    length: int
    q: int
    B: int
    source: int
    endpoint: int

    @property
    def word(self) -> str:
        return format(self.bits, f"0{self.length}b")


def make_row(bits: int, length: int, q: int, B: int) -> Row:
    two, three = 1 << length, 3**q
    source = (-B * pow(three, -1, two)) % two or two
    endpoint = (B * pow(two, -1, three)) % three or three
    return Row(bits, length, q, B, source, endpoint)


def enumerate_safe(maximum_q: int) -> dict[int, list[Row]]:
    grouped = {q: [] for q in range(1, maximum_q + 1)}
    current = [(0, 0, 0)]
    maximum_length = (3**maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        following = []
        for bits, q, B in current:
            if q and 3**q > 1 << length:
                row = make_row(bits << 1, length, q, B)
                following.append((row.bits, q, B))
                grouped[q].append(row)
            if q < maximum_q and 3 ** (q + 1) > 1 << length:
                row = make_row((bits << 1) | 1, length, q + 1, 3 * B + (1 << (length - 1)))
                following.append((row.bits, row.q, row.B))
                grouped[row.q].append(row)
        current = following
    return grouped


def coefficient_at_least(left: Row, right: Row) -> bool:
    return 3**left.q * (1 << right.length) >= 3**right.q * (1 << left.length)


def occurrence_source(row: Row, endpoint: int) -> int | None:
    modulus = 3**row.q
    residue = endpoint % modulus or modulus
    if residue != row.endpoint:
        return None
    index = (endpoint - residue) // modulus
    return row.source + index * (1 << row.length) if index >= 0 else None


def initial_run(row: Row) -> int:
    run = 0
    for position in range(row.length - 1, -1, -1):
        if row.bits & (1 << position):
            run += 1
        else:
            break
    return run


def shifted_key(row: Row) -> tuple[int, int, int] | None:
    run = initial_run(row)
    if run == row.length:
        return None
    D = row.B + (1 << row.length) - 3**row.q
    if D <= 0 or D % (1 << run):
        raise AssertionError("shifted valuation")
    return row.q, row.length - run, D >> run


def frontier_audit(maximum_q: int) -> dict[str, object]:
    grouped = enumerate_safe(maximum_q)
    indexes = {}
    shifted_min = {}
    for q, rows in grouped.items():
        endpoint_index = defaultdict(list)
        for row in rows:
            endpoint_index[row.endpoint].append(row)
            key = shifted_key(row)
            if key is not None:
                shifted_min[key] = min(shifted_min.get(key, row.length), row.length)
        indexes[q] = endpoint_index
    digest = hashlib.sha256()
    counts = {}
    for qd, rows in grouped.items():
        same = uniform = endpoint_specific = jump = 0
        for target in rows:
            has_same = has_uniform = has_specific = False
            for qa in range(1, maximum_q + 1):
                modulus = 3**qa
                residue = target.endpoint % modulus or modulus
                for ancestor in indexes[qa].get(residue, ()):
                    source = occurrence_source(ancestor, target.endpoint)
                    if source is None or source >= target.source or not coefficient_at_least(ancestor, target):
                        continue
                    has_specific = True
                    has_uniform |= qa <= qd
                    has_same |= qa == qd
            key = shifted_key(target)
            has_jump = key is not None and shifted_min[key] < target.length
            same += has_same
            uniform += has_uniform
            endpoint_specific += has_specific
            jump += has_jump
            digest.update(f"{target.word}|{target.source}|{target.endpoint}|{int(has_same)}|{int(has_uniform)}|{int(has_specific)}|{int(has_jump)}\n".encode("ascii"))
        counts[str(qd)] = {
            "safe_words": len(rows),
            "same_Q_uniform_dominated": same,
            "Q_ancestor_le_Q_target_uniform_dominated": uniform,
            "endpoint_specific_Q_le_cutoff_dominated": endpoint_specific,
            "shifted_jump_dominated": jump,
        }
    return {
        "format": "collatz-phase15b-frontier-v1",
        "maximum_Q": maximum_q,
        "counts_by_target_Q": counts,
        "row_digest_sha256": digest.hexdigest(),
        "classification_boundary": "Uniform dominance uses endpoint-cylinder inclusion and Q_ancestor<=Q_target. Endpoint-specific dominance additionally admits higher-Q cylinders only for the recorded ordinary endpoint and only through the cutoff.",
        "proves_collatz": False,
    }


def first_upcrossing_blocks(maximum_q: int) -> list[Row]:
    blocks = []
    maximum_length = (3**maximum_q).bit_length() - 1
    # Literal code strings keep the reverse convention auditable at this small layer.
    frontier = [("", 0)]
    for length in range(1, maximum_length + 1):
        following = []
        for code, q in frontier:
            following.append((code + "0", q))
            if q >= maximum_q:
                continue
            candidate = code + "1"
            next_q = q + 1
            if 3**next_q > 1 << length:
                forward = candidate[::-1]
                L, Q, B, source, endpoint = canonical(forward)
                blocks.append(Row(int(forward, 2), L, Q, B, source, endpoint))
            else:
                following.append((candidate, next_q))
        frontier = following
    return blocks


def encoded_fraction(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator), "decimal": f"{Decimal(value.numerator) / Decimal(value.denominator):.24f}"}


def renewal_trie(maximum_q: int) -> dict[str, object]:
    blocks = first_upcrossing_blocks(maximum_q)
    by_q = defaultdict(set)
    beatty_violations = 0
    for row in blocks:
        by_q[row.q].add(row.endpoint)
        if row.word != "1":
            if row.length != (3**row.q).bit_length() - 1:
                beatty_violations += 1
    primitives: dict[int, set[int]] = defaultdict(set)
    counts = {}
    union_mass = Fraction()
    for q in range(1, maximum_q + 1):
        for residue in sorted(by_q[q]):
            covered = False
            for earlier_q, earlier in primitives.items():
                reduced = residue % (3**earlier_q) or 3**earlier_q
                if reduced in earlier:
                    covered = True
                    break
            if not covered:
                primitives[q].add(residue)
        counts[str(q)] = len(primitives[q])
        union_mass += Fraction(len(primitives[q]), 3**q)
    digest = hashlib.sha256()
    for q in sorted(primitives):
        for residue in sorted(primitives[q]):
            digest.update(f"{q}|{residue}\n".encode("ascii"))
    return {
        "format": "collatz-phase15b-renewal-trie-v1",
        "maximum_Q": maximum_q,
        "renewal_block_count": len(blocks),
        "new_primitive_cylinders_by_Q": counts,
        "primitive_digest_sha256": digest.hexdigest(),
        "finite_union_Haar_mass": encoded_fraction(union_mass),
        "finite_conditional_unit_coverage": encoded_fraction(Fraction(3, 2) * union_mass),
        "beatty_length_violation_count": beatty_violations,
        "analytic_upper_bound": "The full union has Haar mass at most sigma<7/12 by P78, hence conditional unit complement greater than 1/8.",
        "pointwise_boundary": "A positive-measure 3-adic complement does not imply that any positive ordinary integer is outside the covered set.",
        "proves_collatz": False,
    }


def enumerate_fixed_q(q_target: int):
    maximum_length = (3**q_target).bit_length() - 1

    def walk(bits: int, length: int, q: int, B: int):
        if q == q_target:
            yield make_row(bits, length, q, B)
        if length >= maximum_length:
            return
        next_length = length + 1
        if q and 3**q > 1 << next_length:
            yield from walk(bits << 1, next_length, q, B)
        if q < q_target and 3 ** (q + 1) > 1 << next_length:
            yield from walk((bits << 1) | 1, next_length, q + 1, 3 * B + (1 << length))

    yield from walk(0, 0, 0, 0)


def compression_audit(maximum_q: int) -> dict[str, object]:
    maxima = {}
    global_witness = None
    digest = hashlib.sha256()
    for q in range(1, maximum_q + 1):
        minimum_length: dict[int, tuple[int, int, int, int]] = {}
        rows = 0
        for row in enumerate_fixed_q(q):
            rows += 1
            old = minimum_length.get(row.endpoint)
            if old is None or row.length < old[0]:
                minimum_length[row.endpoint] = (row.length, row.bits, row.B, row.source)
        maximum_gain = -1
        witness = None
        for row in enumerate_fixed_q(q):
            shortest = minimum_length[row.endpoint]
            gain = row.length - shortest[0]
            if gain > maximum_gain or (gain == maximum_gain and (witness is None or row.source < witness["d_source"])):
                short = make_row(shortest[1], shortest[0], q, shortest[2])
                witness = {"d": row.word, "a": short.word, "Q": q, "gain": gain, "d_source": row.source, "a_source": short.source, "endpoint": row.endpoint}
                maximum_gain = gain
        if witness is None:
            raise AssertionError("compression witness")
        maxima[str(q)] = {"safe_words": rows, "endpoint_classes": len(minimum_length), "maximum_gain": maximum_gain, "witness": witness}
        digest.update(f"{q}|{rows}|{len(minimum_length)}|{maximum_gain}|{witness['d']}|{witness['a']}\n".encode("ascii"))
        if q == maximum_q:
            global_witness = witness
        del minimum_length
        gc.collect()
    return {
        "format": "collatz-phase15b-compression-v1",
        "maximum_Q": maximum_q,
        "by_Q": maxima,
        "row_digest_sha256": digest.hexdigest(),
        "maximum_layer_witness": global_witness,
        "NG27": {"repository_status": "REFUTED", "hypothesis": "Same-Q total compression gain is always at most three.", "counterexample": global_witness},
        "asymptotic_boundary": "A bounded maximum gain through Q=19 gives no composable or linear gain theorem.",
        "proves_collatz": False,
    }


def record_word(word: str) -> dict[str, object]:
    L, q, B, source, endpoint = canonical(word)
    D = B + (1 << L) - 3**q
    return {"word": word, "L": L, "Q": q, "B": B, "D": D, "source": source, "endpoint": endpoint, "safe": safe_word(word)}


def theory_artifact() -> dict[str, object]:
    d = record_word("111110100")
    a = record_word("1")
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
        "cross_Q_example": {"d": d, "a": a, "s": 5, "k": 8, "m": -147, "relation": "3^5*287=2^8*273-147"},
        "jump_example": {"d": record_word("111100"), "a": record_word("11101"), "k": 1},
        "gap12_dependency": "The finite {1,2}-gap endpoint injectivity theorem is already P88 and is not assigned a new claim ID.",
        "what_this_result_does_not_prove": "H89, P80, H72, a composable linear compression gain, cycle exclusion, and Collatz remain unproved.",
        "proves_collatz": False,
    }


def normalized_odd(value: int) -> int:
    return value // (value & -value)


def parity_prefix(source: int, length: int) -> str:
    output = []
    value = source
    for _ in range(length):
        output.append(str(value & 1))
        value = shortcut(value)
    return "".join(output)


def adversarial_seeds() -> list[tuple[str, int]]:
    rows = [("2^m-1", (1 << exponent) - 1) for exponent in range(3, 25)]
    rows.extend(("8^m-5", 8**exponent - 5) for exponent in range(1, 11))
    for count in range(1, 11):
        for mask in range(1 << count):
            word = "".join("111" if mask & (1 << index) else "110" for index in range(count))
            rows.append(("(110|111)^*", int(word, 2)))
    rows.extend((("A=11101", int(A_BITS, 2)), ("B=1100", int(B_BITS, 2))))
    rows.extend(("A^rB^s", int(A_BITS * r + B_BITS * s, 2)) for r in range(1, 9) for s in range(1, 9))
    return rows


def adversarial_artifact() -> dict[str, object]:
    digest = hashlib.sha256()
    counts = Counter()
    for family, raw in adversarial_seeds():
        source = normalized_odd(raw)
        word = parity_prefix(source, 24)
        B = word_constant(word)
        q = word.count("1")
        residue = (-B * pow(3**q, -1, 1 << 24)) % (1 << 24)
        if residue != source % (1 << 24):
            raise AssertionError("adversarial residue")
        counts[family] += 1
        digest.update(f"{family}|{raw}|{source}|{word}|{B}|{residue}\n".encode("ascii"))
    return {
        "format": "collatz-phase15b-adversarial-v1",
        "prefix_length": 24,
        "instance_count": sum(counts.values()),
        "family_counts": dict(sorted(counts.items())),
        "row_digest_sha256": digest.hexdigest(),
        "phase7_macro_zero": record_word(MACRO_ZERO),
        "named_boundaries": ["NG19", "NG21", "both NG22 models", "NG23", "NG24", "NG25", "NG26", "all-one prefixes", "{1,2}-gap formal core"],
        "proves_collatz": False,
    }


def obstruction_report(path: Path) -> None:
    path.write_text(
        """# Phase 15B obstruction report

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
""",
        encoding="utf-8",
    )


def generate(artifact_dir: Path, source_bound: int, frontier_maximum_q: int, compression_maximum_q: int) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "phase15b_theory.json", theory_artifact())
    write_json(artifact_dir / "phase15b_ancestral_scan.json", ancestral_scan(source_bound))
    write_json(artifact_dir / "phase15b_frontier.json", frontier_audit(frontier_maximum_q))
    write_json(artifact_dir / "phase15b_renewal_trie.json", renewal_trie(frontier_maximum_q))
    write_json(artifact_dir / "phase15b_compression.json", compression_audit(compression_maximum_q))
    write_json(artifact_dir / "phase15b_adversarial.json", adversarial_artifact())
    obstruction_report(artifact_dir / "phase15b_obstruction_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--source-bound", type=int, default=5_000_000)
    parser.add_argument("--frontier-max-q", type=int, default=17)
    parser.add_argument("--compression-max-q", type=int, default=19)
    args = parser.parse_args()
    if args.source_bound < 3 or args.frontier_max_q < 4 or args.compression_max_q < args.frontier_max_q:
        parser.error("invalid Phase 15B bounds")
    generate(args.artifact_dir, args.source_bound, args.frontier_max_q, args.compression_max_q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
