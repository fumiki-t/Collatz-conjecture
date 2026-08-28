#!/usr/bin/env python3
"""Generate exact Phase 15 surplus-dominance evidence.

All mathematical decisions use arbitrary-precision integer arithmetic.  The
independent verifier reimplements the enumeration and does not import this
module.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

A_BITS = "11101"
B_BITS = "1100"


@dataclass(frozen=True, slots=True)
class SafeWord:
    bits: int
    length: int
    odd_count: int
    correction: int
    source: int
    endpoint: int

    @property
    def word(self) -> str:
        return format(self.bits, f"0{self.length}b")


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
    for bit in word:
        if str(value & 1) != bit:
            raise AssertionError("source does not realize word")
        value = (3 * value + 1) // 2 if value & 1 else value // 2
        values.append(value)
    return values


def safe_word(word: str) -> bool:
    q = 0
    for length, bit in enumerate(word, 1):
        q += bit == "1"
        if 3**q <= 1 << length:
            return False
    return bool(word)


def make_row(bits: int, length: int, q: int, correction: int) -> SafeWord:
    modulus_two = 1 << length
    modulus_three = 3**q
    r2 = (-correction * pow(modulus_three, -1, modulus_two)) % modulus_two
    source = r2 or modulus_two
    r3 = (correction * pow(modulus_two, -1, modulus_three)) % modulus_three
    endpoint = r3 or modulus_three
    row = SafeWord(bits, length, q, correction, source, endpoint)
    if literal_trace(source, row.word)[-1] != endpoint:
        raise AssertionError("canonical endpoint")
    return row


def enumerate_safe(maximum_q: int) -> dict[int, list[SafeWord]]:
    """Enumerate every nonempty strict coefficient-safe word with Q<=cap."""
    grouped: dict[int, list[SafeWord]] = {q: [] for q in range(1, maximum_q + 1)}
    # State is (bits, q, B); every state is already strictly safe.
    current: list[tuple[int, int, int]] = [(0, 0, 0)]
    maximum_length = (3**maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        position = length - 1
        following: list[tuple[int, int, int]] = []
        for bits, q, correction in current:
            if q and 3**q > 1 << length:
                candidate = (bits << 1, q, correction)
                following.append(candidate)
                grouped[q].append(make_row(candidate[0], length, q, candidate[2]))
            if q < maximum_q and 3 ** (q + 1) > 1 << length:
                next_bits = (bits << 1) | 1
                next_q = q + 1
                next_correction = 3 * correction + (1 << position)
                following.append((next_bits, next_q, next_correction))
                grouped[next_q].append(make_row(next_bits, length, next_q, next_correction))
        current = following
    return grouped


def row_record(row: SafeWord) -> dict[str, object]:
    return {
        "word": row.word,
        "L": row.length,
        "Q": row.odd_count,
        "B": row.correction,
        "source": row.source,
        "endpoint": row.endpoint,
        "coefficient": {"numerator": 3**row.odd_count, "denominator": 1 << row.length},
    }


def row_id(row: SafeWord) -> tuple[int, int]:
    return row.length, row.bits


def reaches(row: SafeWord, endpoint: int) -> int | None:
    modulus = 3**row.odd_count
    endpoint_residue = endpoint % modulus or modulus
    if endpoint_residue != row.endpoint:
        return None
    multiple = (endpoint - endpoint_residue) // modulus
    if multiple < 0:
        return None
    return row.source + multiple * (1 << row.length)


def coefficient_at_least(left: SafeWord, right: SafeWord) -> bool:
    return 3**left.odd_count * (1 << right.length) >= 3**right.odd_count * (1 << left.length)


def better_certificate(candidate: tuple[SafeWord, int], best: tuple[SafeWord, int] | None) -> bool:
    if best is None:
        return True
    row, source = candidate
    old, old_source = best
    if source != old_source:
        return source < old_source
    return Fraction(3**row.odd_count, 1 << row.length) > Fraction(3**old.odd_count, 1 << old.length)


def frontier_audit(grouped: dict[int, list[SafeWord]], maximum_q: int) -> tuple[dict[str, object], dict[int, set[tuple[int, int]]]]:
    endpoint_index: dict[int, dict[int, list[SafeWord]]] = {}
    for q, rows in grouped.items():
        index: dict[int, list[SafeWord]] = defaultdict(list)
        for row in rows:
            index[row.endpoint].append(row)
        endpoint_index[q] = index

    counts: dict[str, dict[str, int]] = {}
    same_q_dominated: dict[int, set[tuple[int, int]]] = defaultdict(set)
    certificate_digest = hashlib.sha256()
    safe_digest = hashlib.sha256()
    least_examples: dict[str, dict[str, object]] = {}
    global_front_sizes: Counter[int] = Counter()

    for qd in range(1, maximum_q + 1):
        same_count = leq_count = global_count = 0
        for target in grouped[qd]:
            safe_digest.update(
                f"{target.word}|{target.length}|{qd}|{target.correction}|{target.source}|{target.endpoint}\n".encode("ascii")
            )
            best_same = best_leq = best_global = None
            all_candidates: list[tuple[SafeWord, int]] = []
            for qb in range(1, maximum_q + 1):
                modulus = 3**qb
                residue = target.endpoint % modulus or modulus
                for ancestor in endpoint_index[qb].get(residue, ()):
                    source = reaches(ancestor, target.endpoint)
                    if source is None:
                        raise AssertionError("indexed reachability")
                    all_candidates.append((ancestor, source))
                    if source >= target.source or not coefficient_at_least(ancestor, target):
                        continue
                    item = (ancestor, source)
                    if better_certificate(item, best_global):
                        best_global = item
                    if qb <= qd and better_certificate(item, best_leq):
                        best_leq = item
                    if qb == qd and better_certificate(item, best_same):
                        best_same = item
            if best_same is not None:
                same_count += 1
                same_q_dominated[qd].add(row_id(target))
            if best_leq is not None:
                leq_count += 1
            if best_global is not None:
                global_count += 1

            # Pareto frontier: increasing source and strictly increasing coefficient.
            front: list[tuple[SafeWord, int]] = []
            for ancestor, source in sorted(all_candidates, key=lambda item: (item[1], item[0].length, item[0].bits)):
                if any(old_source <= source and coefficient_at_least(old, ancestor) for old, old_source in front):
                    continue
                front = [
                    (old, old_source)
                    for old, old_source in front
                    if not (source <= old_source and coefficient_at_least(ancestor, old))
                ]
                front.append((ancestor, source))
            global_front_sizes[len(front)] += 1

            fields = []
            for label, best in (("same", best_same), ("leq", best_leq), ("global", best_global)):
                if best is None:
                    fields.append(f"{label}=-")
                    continue
                ancestor, source = best
                fields.append(f"{label}={ancestor.word},{source}")
                key = f"{label}_Q{qd}"
                if key not in least_examples:
                    least_examples[key] = {
                        "target": row_record(target),
                        "ancestor": row_record(ancestor),
                        "ancestor_source_at_target_endpoint": source,
                    }
            certificate_digest.update(
                f"{target.word}|{target.source}|{target.endpoint}|{'|'.join(fields)}\n".encode("ascii")
            )
        counts[str(qd)] = {
            "safe_words": len(grouped[qd]),
            "same_Q_dominated": same_count,
            "Qb_le_Qd_dominated": leq_count,
            "Qb_le_cutoff_dominated": global_count,
            "Qb_le_Qd_survivors": len(grouped[qd]) - leq_count,
            "Qb_le_cutoff_survivors": len(grouped[qd]) - global_count,
        }

    return (
        {
            "format": "collatz-phase15-surplus-frontier-v1",
            "maximum_Q": maximum_q,
            "counts_by_target_Q": counts,
            "safe_row_digest_sha256": safe_digest.hexdigest(),
            "certificate_digest_sha256": certificate_digest.hexdigest(),
            "global_pareto_front_size_distribution": {str(k): v for k, v in sorted(global_front_sizes.items())},
            "least_certificate_examples": least_examples,
            "cutoff_boundary": "Qb<=maximum_Q is a finite search cutoff, not an all-depth dominance theorem.",
            "proves_collatz": False,
        },
        same_q_dominated,
    )


def bits_and_constant(length: int, positions: tuple[int, ...]) -> tuple[int, int]:
    bits = 0
    correction = 0
    for position in positions:
        bits |= 1 << (length - 1 - position)
        correction = 3 * correction + (1 << position)
    return bits, correction


def valley_data(word: str) -> tuple[int, int, str] | None:
    q = 0
    minimum_q = 0
    minimum_length = 0
    for length, bit in enumerate(word, 1):
        q += bit == "1"
        if 3**q * (1 << minimum_length) < 3**minimum_q * (1 << length):
            minimum_q, minimum_length = q, length
    if minimum_length == 0 or minimum_length == len(word):
        return None
    suffix = word[minimum_length:]
    if not safe_word(suffix):
        raise AssertionError("strict valley suffix")
    return minimum_length, minimum_q, suffix


def valley_audit(
    grouped: dict[int, list[SafeWord]], same_q_dominated: dict[int, set[tuple[int, int]]], maximum_q: int
) -> dict[str, object]:
    target_index: dict[int, dict[int, list[SafeWord]]] = {}
    for q, rows in grouped.items():
        index: dict[int, list[SafeWord]] = defaultdict(list)
        for row in rows:
            index[row.endpoint].append(row)
        target_index[q] = index

    counts: dict[str, dict[str, int]] = {}
    digest = hashlib.sha256()
    examples: dict[str, object] = {}
    for q in range(4, maximum_q + 1):
        additions: dict[tuple[int, int], dict[str, object]] = {}
        arbitrary_count = unsafe_proper_valley_count = 0
        maximum_length = (3**q).bit_length() - 1
        modulus_three = 3**q
        for length in range(q, maximum_length):
            modulus_two = 1 << length
            inverse_two = pow(modulus_two, -1, modulus_three)
            for positions in itertools.combinations(range(length), q):
                arbitrary_count += 1
                bits, correction = bits_and_constant(length, positions)
                word = format(bits, f"0{length}b")
                valley = valley_data(word)
                if valley is None:
                    continue
                unsafe_proper_valley_count += 1
                t, q_prefix, suffix = valley
                endpoint_residue = (correction * inverse_two) % modulus_three or modulus_three
                targets = target_index[q].get(endpoint_residue, ())
                if not targets:
                    continue
                source_residue = (-correction * pow(modulus_three, -1, modulus_two)) % modulus_two
                source = source_residue or modulus_two
                prefix_values = literal_trace(source, word[:t])
                valley_source = prefix_values[-1]
                suffix_q = q - q_prefix
                suffix_length = length - t
                suffix_correction = word_constant(suffix)
                suffix_row = make_row(int(suffix, 2), suffix_length, suffix_q, suffix_correction)
                if suffix_row.source != valley_source % (1 << suffix_length) and not (
                    suffix_row.source == 1 << suffix_length and valley_source % (1 << suffix_length) == 0
                ):
                    raise AssertionError("valley cylinder")
                for target in targets:
                    if target.length <= length or row_id(target) in same_q_dominated[q]:
                        continue
                    endpoint = literal_trace(source, word)[-1]
                    if endpoint != target.endpoint or literal_trace(valley_source, suffix)[-1] != endpoint:
                        raise AssertionError("valley coalescence")
                    if valley_source >= target.source or not coefficient_at_least(suffix_row, target):
                        continue
                    key = row_id(target)
                    certificate = {
                        "target": row_record(target),
                        "arbitrary_target": {
                            "word": word,
                            "L": length,
                            "Q": q,
                            "B": correction,
                            "source": source,
                            "endpoint": endpoint,
                        },
                        "valley_prefix_length": t,
                        "valley_suffix": row_record(suffix_row),
                        "valley_source": valley_source,
                    }
                    if key not in additions or (valley_source, word) < (
                        int(additions[key]["valley_source"]),
                        str(additions[key]["arbitrary_target"]["word"]),
                    ):
                        additions[key] = certificate
        for key, cert in sorted(additions.items()):
            digest.update(
                f"{q}|{key[0]}|{key[1]}|{cert['arbitrary_target']['word']}|{cert['valley_prefix_length']}|{cert['valley_suffix']['word']}|{cert['valley_source']}\n".encode("ascii")
            )
        counts[str(q)] = {
            "arbitrary_shorter_words_examined": arbitrary_count,
            "unsafe_words_with_proper_valley": unsafe_proper_valley_count,
            "additional_reductions_beyond_same_Q_safe_targets": len(additions),
        }
        if additions:
            examples[f"Q{q}"] = next(iter(sorted(additions.values(), key=lambda item: (item["target"]["source"], item["target"]["word"]))))
    return {
        "format": "collatz-phase15-valley-audit-v1",
        "maximum_Q": maximum_q,
        "counts_by_Q": counts,
        "certificate_digest_sha256": digest.hexdigest(),
        "least_examples": examples,
        "finite_boundary": "These counts enumerate shorter same-Q arbitrary targets only through the stated Q cutoff.",
        "proves_collatz": False,
    }


def gap12_audit(grouped: dict[int, list[SafeWord]], maximum_q: int) -> dict[str, object]:
    counts = {}
    dominated_counts = {}
    digest = hashlib.sha256()
    total = 0
    endpoint_index: dict[int, dict[int, list[SafeWord]]] = {}
    for q, all_rows in grouped.items():
        index: dict[int, list[SafeWord]] = defaultdict(list)
        for candidate in all_rows:
            index[candidate.endpoint].append(candidate)
        endpoint_index[q] = index
    for q in range(1, maximum_q + 1):
        rows = [row for row in grouped[q] if "00" not in row.word]
        residues: dict[int, SafeWord] = {}
        dominated = 0
        for row in rows:
            if row.endpoint in residues:
                raise AssertionError("gap-{1,2} endpoint collision")
            residues[row.endpoint] = row
            # Decode backward: residue mod 3 identifies the last exponent.
            value = row.endpoint % (3**q)
            exponents = []
            for level in range(q, 0, -1):
                mod3 = value % 3
                exponent = 1 if mod3 == 2 else 2 if mod3 == 1 else 0
                if not exponent:
                    raise AssertionError("gap decoder residue")
                exponents.append(exponent)
                numerator = (1 << exponent) * value - 1
                if numerator % 3:
                    raise AssertionError("gap decoder division")
                value = (numerator // 3) % (3 ** (level - 1)) if level > 1 else 0
            decoded = "".join("1" + "0" * (e - 1) for e in reversed(exponents))
            if decoded != row.word:
                raise AssertionError("gap decoder word")
            is_dominated = False
            for qb in range(1, q + 1):
                modulus = 3**qb
                endpoint_residue = row.endpoint % modulus or modulus
                for ancestor in endpoint_index[qb].get(endpoint_residue, ()):
                    ancestor_source = reaches(ancestor, row.endpoint)
                    if ancestor_source is not None and ancestor_source < row.source and coefficient_at_least(ancestor, row):
                        is_dominated = True
                        break
                if is_dominated:
                    break
            dominated += is_dominated
            digest.update(f"{q}|{row.word}|{row.endpoint}|{','.join(map(str, reversed(exponents)))}\n".encode("ascii"))
        counts[str(q)] = len(rows)
        dominated_counts[str(q)] = dominated
        total += len(rows)
    return {
        "format": "collatz-phase15-gap12-v1",
        "maximum_Q": maximum_q,
        "counts_by_Q": counts,
        "Qb_le_Qd_dominated_counts_by_Q": dominated_counts,
        "total_word_count": total,
        "endpoint_collision_count": 0,
        "row_digest_sha256": digest.hexdigest(),
        "theorem_boundary": "Injectivity holds for every fixed finite Q in the {1,2}-gap language; positivity of one ordinary infinite source is not implied.",
        "proves_collatz": False,
    }


def normalized_odd(value: int) -> int:
    return value // (value & -value)


def parity_prefix(source: int, length: int) -> str:
    bits = []
    value = source
    for _ in range(length):
        bits.append(str(value & 1))
        value = (3 * value + 1) // 2 if value & 1 else value // 2
    return "".join(bits)


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


def adversarial_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    counts: Counter[str] = Counter()
    for family, raw in adversarial_seeds():
        source = normalized_odd(raw)
        word = parity_prefix(source, 24)
        correction = word_constant(word)
        q = word.count("1")
        residue = (-correction * pow(3**q, -1, 1 << 24)) % (1 << 24)
        if source % (1 << 24) != residue:
            raise AssertionError("adversarial source residue")
        counts[family] += 1
        digest.update(f"{family}|{raw}|{source}|{word}|{correction}|{residue}\n".encode("ascii"))
    return {
        "format": "collatz-phase15-adversarial-v1",
        "prefix_length": 24,
        "instance_count": sum(counts.values()),
        "family_counts": dict(sorted(counts.items())),
        "row_digest_sha256": digest.hexdigest(),
        "preserved_boundaries": {
            "NG19": "Literal fixed-gap pairs survive without an ordinary-height bridge.",
            "NG21": "Mod-6 packing alone cannot improve the Phase 12 exponent.",
            "NG22": "Formal coherent 2-adic sources need not be positive ordinary integers.",
            "NG23": "Haar volume does not bound an individual canonical representative.",
            "NG24": "Left concatenation is not a coalescent congruence."
        },
        "proves_collatz": False,
    }


def exact_example(word: str) -> dict[str, object]:
    q = word.count("1")
    return row_record(make_row(int(word, 2), len(word), q, word_constant(word)))


def theory_artifact() -> dict[str, object]:
    examples = {
        "Q6_cross_Q": {"target": exact_example("111110100"), "ancestor": exact_example("1")},
        "Q4_higher_Q": {"target": exact_example("110110"), "ancestor": exact_example("1110110")},
        "Q15_unsafe_target": {
            "target": exact_example("11101011111111101000001"),
            "arbitrary_target_word": "1010110111111101011100",
            "strict_valley_prefix": "1010",
            "safe_suffix": exact_example("110111111101011100"),
        },
    }
    # Independent literal checks for the named examples.
    for key in ("Q6_cross_Q", "Q4_higher_Q"):
        target = examples[key]["target"]
        ancestor = examples[key]["ancestor"]
        source = int(target["source"])
        endpoint = int(target["endpoint"])
        modulus = 3 ** int(ancestor["Q"])
        residue = int(ancestor["endpoint"])
        shifted = int(ancestor["source"]) + ((endpoint - residue) // modulus) * (1 << int(ancestor["L"]))
        if literal_trace(source, str(target["word"]))[-1] != endpoint or literal_trace(shifted, str(ancestor["word"]))[-1] != endpoint:
            raise AssertionError("named cross-Q example")
        examples[key]["ancestor_source_at_target_endpoint"] = shifted
    unsafe = examples["Q15_unsafe_target"]
    arbitrary = str(unsafe["arbitrary_target_word"])
    q = arbitrary.count("1")
    B = word_constant(arbitrary)
    source = (-B * pow(3**q, -1, 1 << len(arbitrary))) % (1 << len(arbitrary)) or 1 << len(arbitrary)
    trace = literal_trace(source, arbitrary)
    unsafe["arbitrary_target_B"] = B
    unsafe["arbitrary_target_source"] = source
    unsafe["common_endpoint"] = trace[-1]
    unsafe["valley_source"] = trace[len(str(unsafe["strict_valley_prefix"]))]

    return {
        "format": "collatz-phase15-surplus-theory-v1",
        "P86": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "Let S be the least positive source in any shared-future counterexample class whose full shortcut discrepancy is positive at every nonempty prefix and tends to infinity. If an initial safe word d from S reaches Y and a smaller positive V reaches Y through a coefficient-safe word b with c(b)>=c(d), then b followed by the common future has the same two discrepancy properties, contradicting minimality of S.",
            "quantifier_boundary": "The internal least-source theorem is exact. Applying it to every nonperiodic Collatz counterexample uses EXT07/P74; nontrivial cycles are separate.",
        },
        "P87": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For an arbitrary coalescent target a, cut after its unique proper global discrepancy minimum. The nonempty suffix b is strictly coefficient-safe. If a has negative minimum and c(a)>c(d), then c(b)>c(d); positivity, V<S, and literal coalescence remain separate checks.",
            "right_ideal_boundary": "A dominated d remains dominated after a common suffix u whenever d|u is coefficient-safe. The unqualified all-suffix statement is not asserted.",
        },
        "P88": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For odd-to-odd gaps e_j in {1,2}, r_j=B_j*2^(-E_j) mod 3^j determines the last exponent from r_j mod 3 and recursively determines the entire finite exponent word; hence the endpoint map is injective at fixed Q.",
            "decoder": "e_j=1 when r_j=2 mod 3, e_j=2 when r_j=1 mod 3, and r_(j-1)=(2^e_j*r_j-1)/3 mod 3^(j-1).",
            "boundary": "No coefficient-safety assumption is needed for injectivity, and no positive ordinary infinite source follows.",
        },
        "examples": examples,
        "what_this_result_does_not_prove": "Surplus dominance does not show every safe prefix has a dominating ancestor, convert the Q<=17 cutoff into an eventual theorem, prove P80 or H72, exclude cycles, or prove the Collatz conjecture.",
        "proves_collatz": False,
    }


def obstruction_report(path: Path) -> None:
    path.write_text(
        """# Phase 15 obstruction report

Phase 15 does not prove or disprove the Collatz conjecture.

## Cross-Q obstruction to same-layer completeness

The safe target `111110100` has `(Q,L,B,S,Y)=(6,9,697,287,410)`.
The one-bit safe ancestor `1` reaches the same endpoint from 273 and has
coefficient `3/2 > 3^6/2^9`.  Therefore same-Q coalescent rewrites are not a
complete surplus-dominance test.  A second example has a Q=5 ancestor
dominating a Q=4 target.

## Unsafe-target obstruction

The Q=15 arbitrary target `1010110111111101011100` is not coefficient-safe.
Cutting after its strict discrepancy valley `1010` yields the safe suffix
`110111111101011100`, which coalesces below the named safe target and has
larger terminal surplus.  Thus a search may not discard arbitrary targets
before the valley extraction.

## Cutoff obstruction

The finite frontier is complete only for competitor odd count `Q_b<=17`.
Survivors in the top layers can still be dominated by an unenumerated
higher-Q ancestor.  Finite survivor counts are not an asymptotic theorem.

## What this result does not prove

- eventual extinction of the surplus-undominated frontier;
- either anti-concentration premise in P80;
- exclusion of a positive permanent-safe source or H72;
- exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
""",
        encoding="utf-8",
    )


def generate(artifact_dir: Path, maximum_q: int) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    grouped = enumerate_safe(maximum_q)
    frontier, same_q_dominated = frontier_audit(grouped, maximum_q)
    write_json(artifact_dir / "phase15_surplus_theory.json", theory_artifact())
    write_json(artifact_dir / "phase15_surplus_frontier.json", frontier)
    write_json(artifact_dir / "phase15_valley_audit.json", valley_audit(grouped, same_q_dominated, maximum_q))
    write_json(artifact_dir / "phase15_gap12_core.json", gap12_audit(grouped, maximum_q))
    write_json(artifact_dir / "phase15_adversarial_regression.json", adversarial_audit())
    obstruction_report(artifact_dir / "phase15_obstruction_report.md")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--max-q", type=int, default=17)
    args = parser.parse_args()
    if args.max_q < 4:
        parser.error("require max-q>=4")
    generate(args.artifact_dir, args.max_q)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
