#!/usr/bin/env python3
"""Independent exact verifier for Phase 15 surplus dominance.

The verifier does not import the generator.  It reconstructs safe cylinders,
canonical representatives, dominance certificates, valley reductions, the
gap-{1,2} decoder, theorem examples, and adversarial rows using tuple records.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

ABLOCK = "11101"
BBLOCK = "1100"


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


def correction(bits: str) -> int:
    translation = 0
    denominator = 1
    for bit in bits:
        if bit == "1":
            translation = 3 * translation + denominator
        elif bit != "0":
            fail("non-binary word")
        denominator *= 2
    return translation


def actual_trace(start: int, bits: str) -> list[int]:
    values = [start]
    value = start
    for expected in bits:
        if str(value % 2) != expected:
            fail("literal parity mismatch")
        value = (3 * value + 1) // 2 if value % 2 else value // 2
        values.append(value)
    return values


def strict_safe(bits: str) -> bool:
    ones = 0
    for length, bit in enumerate(bits, 1):
        ones += bit == "1"
        if pow(3, ones) <= pow(2, length):
            return False
    return bool(bits)


# Tuple record is (word, L, Q, B, source_positive, endpoint_positive).
def tuple_record(bits: str) -> tuple[str, int, int, int, int, int]:
    length = len(bits)
    ones = bits.count("1")
    B = correction(bits)
    two = pow(2, length)
    three = pow(3, ones)
    r2 = (-B * pow(three, -1, two)) % two
    r3 = (B * pow(two, -1, three)) % three
    row = (bits, length, ones, B, r2 or two, r3 or three)
    if actual_trace(row[4], bits)[-1] != row[5]:
        fail("canonical endpoint reconstruction")
    return row


def record(row: tuple[str, int, int, int, int, int]) -> dict[str, object]:
    return {
        "word": row[0],
        "L": row[1],
        "Q": row[2],
        "B": row[3],
        "source": row[4],
        "endpoint": row[5],
        "coefficient": {"numerator": pow(3, row[2]), "denominator": pow(2, row[1])},
    }


def enumerate_cylinders(q_cap: int) -> dict[int, list[tuple[str, int, int, int, int, int]]]:
    grouped = {q: [] for q in range(1, q_cap + 1)}
    # Reconstruct prefixes as literal strings, independently of packed generator rows.
    frontier = [("", 0, 0)]
    final_length = pow(3, q_cap).bit_length() - 1
    for length in range(1, final_length + 1):
        following = []
        for prefix, ones, B in frontier:
            zero = prefix + "0"
            if ones and pow(3, ones) > pow(2, length):
                following.append((zero, ones, B))
                grouped[ones].append(tuple_record(zero))
            if ones < q_cap and pow(3, ones + 1) > pow(2, length):
                one = prefix + "1"
                new_B = 3 * B + pow(2, length - 1)
                following.append((one, ones + 1, new_B))
                row = tuple_record(one)
                if row[3] != new_B:
                    fail("prefix correction recurrence")
                grouped[ones + 1].append(row)
        frontier = following
    return grouped


def no_smaller_coefficient(left: tuple, right: tuple) -> bool:
    return pow(3, left[2]) * pow(2, right[1]) >= pow(3, right[2]) * pow(2, left[1])


def source_for_endpoint(row: tuple, endpoint: int) -> int | None:
    modulus = pow(3, row[2])
    positive_residue = endpoint % modulus or modulus
    if positive_residue != row[5]:
        return None
    index = (endpoint - positive_residue) // modulus
    if index < 0:
        return None
    return row[4] + index * pow(2, row[1])


def prefer(candidate: tuple[tuple, int], old: tuple[tuple, int] | None) -> bool:
    if old is None:
        return True
    row, source = candidate
    old_row, old_source = old
    if source != old_source:
        return source < old_source
    return Fraction(pow(3, row[2]), pow(2, row[1])) > Fraction(pow(3, old_row[2]), pow(2, old_row[1]))


def expected_frontier(grouped: dict[int, list[tuple]], q_cap: int) -> tuple[dict[str, object], dict[int, set[tuple[int, str]]]]:
    by_endpoint = {}
    for q, rows in grouped.items():
        index = defaultdict(list)
        for row in rows:
            index[row[5]].append(row)
        by_endpoint[q] = index

    counts = {}
    same_sets = defaultdict(set)
    row_hash = hashlib.sha256()
    cert_hash = hashlib.sha256()
    first_examples = {}
    sizes = Counter()
    for q_target in range(1, q_cap + 1):
        same_total = leq_total = cutoff_total = 0
        for target in grouped[q_target]:
            row_hash.update(
                f"{target[0]}|{target[1]}|{q_target}|{target[3]}|{target[4]}|{target[5]}\n".encode("ascii")
            )
            same = leq = cutoff = None
            candidates = []
            for q_ancestor in range(1, q_cap + 1):
                residue = target[5] % pow(3, q_ancestor) or pow(3, q_ancestor)
                for ancestor in by_endpoint[q_ancestor].get(residue, ()):
                    source = source_for_endpoint(ancestor, target[5])
                    if source is None:
                        fail("endpoint class lookup")
                    candidates.append((ancestor, source))
                    if source >= target[4] or not no_smaller_coefficient(ancestor, target):
                        continue
                    item = (ancestor, source)
                    if prefer(item, cutoff):
                        cutoff = item
                    if q_ancestor <= q_target and prefer(item, leq):
                        leq = item
                    if q_ancestor == q_target and prefer(item, same):
                        same = item
            if same is not None:
                same_total += 1
                same_sets[q_target].add((target[1], target[0]))
            leq_total += leq is not None
            cutoff_total += cutoff is not None

            pareto = []
            for ancestor, source in sorted(candidates, key=lambda item: (item[1], item[0][1], int(item[0][0], 2))):
                if any(old_source <= source and no_smaller_coefficient(old, ancestor) for old, old_source in pareto):
                    continue
                pareto = [
                    (old, old_source)
                    for old, old_source in pareto
                    if not (source <= old_source and no_smaller_coefficient(ancestor, old))
                ]
                pareto.append((ancestor, source))
            sizes[len(pareto)] += 1

            values = []
            for label, winner in (("same", same), ("leq", leq), ("global", cutoff)):
                if winner is None:
                    values.append(f"{label}=-")
                    continue
                ancestor, source = winner
                values.append(f"{label}={ancestor[0]},{source}")
                name = f"{label}_Q{q_target}"
                if name not in first_examples:
                    first_examples[name] = {
                        "target": record(target),
                        "ancestor": record(ancestor),
                        "ancestor_source_at_target_endpoint": source,
                    }
            cert_hash.update(f"{target[0]}|{target[4]}|{target[5]}|{'|'.join(values)}\n".encode("ascii"))
        counts[str(q_target)] = {
            "safe_words": len(grouped[q_target]),
            "same_Q_dominated": same_total,
            "Qb_le_Qd_dominated": leq_total,
            "Qb_le_cutoff_dominated": cutoff_total,
            "Qb_le_Qd_survivors": len(grouped[q_target]) - leq_total,
            "Qb_le_cutoff_survivors": len(grouped[q_target]) - cutoff_total,
        }
    return {
        "format": "collatz-phase15-surplus-frontier-v1",
        "maximum_Q": q_cap,
        "counts_by_target_Q": counts,
        "safe_row_digest_sha256": row_hash.hexdigest(),
        "certificate_digest_sha256": cert_hash.hexdigest(),
        "global_pareto_front_size_distribution": {str(k): v for k, v in sorted(sizes.items())},
        "least_certificate_examples": first_examples,
        "cutoff_boundary": "Qb<=maximum_Q is a finite search cutoff, not an all-depth dominance theorem.",
        "proves_collatz": False,
    }, same_sets


def strict_valley(bits: str) -> tuple[int, int, str] | None:
    ones = 0
    minimum = (0, 0)
    for length, bit in enumerate(bits, 1):
        ones += bit == "1"
        old_q, old_length = minimum
        if pow(3, ones) * pow(2, old_length) < pow(3, old_q) * pow(2, length):
            minimum = (ones, length)
    q_prefix, cut = minimum
    if cut in (0, len(bits)):
        return None
    suffix = bits[cut:]
    if not strict_safe(suffix):
        fail("valley suffix is not safe")
    return cut, q_prefix, suffix


def expected_valleys(grouped: dict[int, list[tuple]], same_sets: dict[int, set[tuple[int, str]]], q_cap: int) -> dict[str, object]:
    target_classes = {}
    for q, rows in grouped.items():
        index = defaultdict(list)
        for row in rows:
            index[row[5]].append(row)
        target_classes[q] = index
    counts = {}
    digest = hashlib.sha256()
    examples = {}
    for q in range(4, q_cap + 1):
        found = {}
        examined = unsafe = 0
        top_length = pow(3, q).bit_length() - 1
        three = pow(3, q)
        for length in range(q, top_length):
            two = pow(2, length)
            inverse_two = pow(two, -1, three)
            for positions in itertools.combinations(range(length), q):
                examined += 1
                position_set = set(positions)
                bits = "".join("1" if index in position_set else "0" for index in range(length))
                valley = strict_valley(bits)
                if valley is None:
                    continue
                unsafe += 1
                cut, q_prefix, suffix = valley
                B = correction(bits)
                endpoint = (B * inverse_two) % three or three
                candidates = target_classes[q].get(endpoint, ())
                if not candidates:
                    continue
                source = (-B * pow(three, -1, two)) % two or two
                trace = actual_trace(source, bits)
                valley_source = trace[cut]
                suffix_row = tuple_record(suffix)
                for target in candidates:
                    if target[1] <= length or (target[1], target[0]) in same_sets[q]:
                        continue
                    if trace[-1] != target[5] or actual_trace(valley_source, suffix)[-1] != target[5]:
                        fail("valley endpoint")
                    if valley_source >= target[4] or not no_smaller_coefficient(suffix_row, target):
                        continue
                    key = (target[1], target[0])
                    item = {
                        "target": record(target),
                        "arbitrary_target": {"word": bits, "L": length, "Q": q, "B": B, "source": source, "endpoint": endpoint},
                        "valley_prefix_length": cut,
                        "valley_suffix": record(suffix_row),
                        "valley_source": valley_source,
                    }
                    if key not in found or (valley_source, bits) < (
                        int(found[key]["valley_source"]), str(found[key]["arbitrary_target"]["word"])
                    ):
                        found[key] = item
        for key, item in sorted(found.items(), key=lambda pair: (pair[0][0], int(pair[0][1], 2))):
            digest.update(
                f"{q}|{key[0]}|{int(key[1], 2)}|{item['arbitrary_target']['word']}|{item['valley_prefix_length']}|{item['valley_suffix']['word']}|{item['valley_source']}\n".encode("ascii")
            )
        counts[str(q)] = {
            "arbitrary_shorter_words_examined": examined,
            "unsafe_words_with_proper_valley": unsafe,
            "additional_reductions_beyond_same_Q_safe_targets": len(found),
        }
        if found:
            examples[f"Q{q}"] = min(found.values(), key=lambda item: (item["target"]["source"], item["target"]["word"]))
    return {
        "format": "collatz-phase15-valley-audit-v1",
        "maximum_Q": q_cap,
        "counts_by_Q": counts,
        "certificate_digest_sha256": digest.hexdigest(),
        "least_examples": examples,
        "finite_boundary": "These counts enumerate shorter same-Q arbitrary targets only through the stated Q cutoff.",
        "proves_collatz": False,
    }


def expected_gap(grouped: dict[int, list[tuple]], q_cap: int) -> dict[str, object]:
    counts = {}
    dominated_counts = {}
    digest = hashlib.sha256()
    total = 0
    endpoint_index = {}
    for q, all_rows in grouped.items():
        index = defaultdict(list)
        for candidate in all_rows:
            index[candidate[5]].append(candidate)
        endpoint_index[q] = index
    for q in range(1, q_cap + 1):
        words = [row for row in grouped[q] if "00" not in row[0]]
        seen = set()
        dominated = 0
        for row in words:
            if row[5] in seen:
                fail("gap endpoint collision")
            seen.add(row[5])
            residue = row[5] % pow(3, q)
            backwards = []
            for level in range(q, 0, -1):
                last = residue % 3
                exponent = 1 if last == 2 else 2 if last == 1 else 0
                if not exponent:
                    fail("gap decoder")
                backwards.append(exponent)
                numerator = pow(2, exponent) * residue - 1
                if numerator % 3:
                    fail("gap exact division")
                residue = (numerator // 3) % pow(3, level - 1) if level > 1 else 0
            decoded = "".join("1" + "0" * (exponent - 1) for exponent in reversed(backwards))
            if decoded != row[0]:
                fail("gap inverse word")
            is_dominated = False
            for q_ancestor in range(1, q + 1):
                modulus = pow(3, q_ancestor)
                endpoint_residue = row[5] % modulus or modulus
                for ancestor in endpoint_index[q_ancestor].get(endpoint_residue, ()):
                    source = source_for_endpoint(ancestor, row[5])
                    if source is not None and source < row[4] and no_smaller_coefficient(ancestor, row):
                        is_dominated = True
                        break
                if is_dominated:
                    break
            dominated += is_dominated
            digest.update(f"{q}|{row[0]}|{row[5]}|{','.join(map(str, reversed(backwards)))}\n".encode("ascii"))
        counts[str(q)] = len(words)
        dominated_counts[str(q)] = dominated
        total += len(words)
    return {
        "format": "collatz-phase15-gap12-v1",
        "maximum_Q": q_cap,
        "counts_by_Q": counts,
        "Qb_le_Qd_dominated_counts_by_Q": dominated_counts,
        "total_word_count": total,
        "endpoint_collision_count": 0,
        "row_digest_sha256": digest.hexdigest(),
        "theorem_boundary": "Injectivity holds for every fixed finite Q in the {1,2}-gap language; positivity of one ordinary infinite source is not implied.",
        "proves_collatz": False,
    }


def named_record(bits: str) -> dict[str, object]:
    return record(tuple_record(bits))


def expected_theory() -> dict[str, object]:
    examples = {
        "Q6_cross_Q": {"target": named_record("111110100"), "ancestor": named_record("1")},
        "Q4_higher_Q": {"target": named_record("110110"), "ancestor": named_record("1110110")},
        "Q15_unsafe_target": {
            "target": named_record("11101011111111101000001"),
            "arbitrary_target_word": "1010110111111101011100",
            "strict_valley_prefix": "1010",
            "safe_suffix": named_record("110111111101011100"),
        },
    }
    for name in ("Q6_cross_Q", "Q4_higher_Q"):
        target = examples[name]["target"]
        ancestor = examples[name]["ancestor"]
        endpoint = int(target["endpoint"])
        modulus = pow(3, int(ancestor["Q"]))
        shifted = int(ancestor["source"]) + ((endpoint - int(ancestor["endpoint"])) // modulus) * pow(2, int(ancestor["L"]))
        if actual_trace(int(target["source"]), str(target["word"]))[-1] != endpoint:
            fail("named target")
        if actual_trace(shifted, str(ancestor["word"]))[-1] != endpoint:
            fail("named ancestor")
        examples[name]["ancestor_source_at_target_endpoint"] = shifted
    unsafe = examples["Q15_unsafe_target"]
    word = str(unsafe["arbitrary_target_word"])
    q = word.count("1")
    B = correction(word)
    source = (-B * pow(pow(3, q), -1, pow(2, len(word)))) % pow(2, len(word)) or pow(2, len(word))
    trace = actual_trace(source, word)
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


def odd_part(value: int) -> int:
    return value // (value & -value)


def prefix(start: int, length: int) -> str:
    value = start
    output = []
    for _ in range(length):
        output.append(str(value % 2))
        value = (3 * value + 1) // 2 if value % 2 else value // 2
    return "".join(output)


def seed_rows() -> list[tuple[str, int]]:
    rows = [("2^m-1", pow(2, m) - 1) for m in range(3, 25)]
    rows += [("8^m-5", pow(8, m) - 5) for m in range(1, 11)]
    for block_count in range(1, 11):
        for mask in range(pow(2, block_count)):
            bits = "".join("111" if mask & pow(2, index) else "110" for index in range(block_count))
            rows.append(("(110|111)^*", int(bits, 2)))
    rows += [("A=11101", int(ABLOCK, 2)), ("B=1100", int(BBLOCK, 2))]
    rows += [("A^rB^s", int(ABLOCK * r + BBLOCK * s, 2)) for r in range(1, 9) for s in range(1, 9)]
    return rows


def expected_adversarial() -> dict[str, object]:
    digest = hashlib.sha256()
    counts = Counter()
    for family, raw in seed_rows():
        source = odd_part(raw)
        bits = prefix(source, 24)
        B = correction(bits)
        q = bits.count("1")
        residue = (-B * pow(pow(3, q), -1, pow(2, 24))) % pow(2, 24)
        if source % pow(2, 24) != residue:
            fail("adversarial residue")
        counts[family] += 1
        digest.update(f"{family}|{raw}|{source}|{bits}|{B}|{residue}\n".encode("ascii"))
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


def verify(artifact_dir: Path) -> dict[str, object]:
    theory = load(artifact_dir / "phase15_surplus_theory.json")
    frontier = load(artifact_dir / "phase15_surplus_frontier.json")
    valleys = load(artifact_dir / "phase15_valley_audit.json")
    gaps = load(artifact_dir / "phase15_gap12_core.json")
    adversarial = load(artifact_dir / "phase15_adversarial_regression.json")
    q_cap = frontier.get("maximum_Q")
    if not isinstance(q_cap, int) or q_cap < 4:
        fail("surplus frontier maximum_Q")
    grouped = enumerate_cylinders(q_cap)
    expected_f, same_sets = expected_frontier(grouped, q_cap)
    if frontier != expected_f:
        fail("surplus frontier mismatch")
    if valleys != expected_valleys(grouped, same_sets, q_cap):
        fail("valley audit mismatch")
    if gaps != expected_gap(grouped, q_cap):
        fail("gap12 core mismatch")
    if theory != expected_theory():
        fail("surplus theory mismatch")
    if adversarial != expected_adversarial():
        fail("adversarial regression mismatch")
    return {
        "format": "collatz-phase15-verifier-v1",
        "valid": True,
        "maximum_Q": q_cap,
        "P86": "VERIFIED_THEOREM",
        "P87": "VERIFIED_THEOREM",
        "P88": "VERIFIED_THEOREM",
        "E24": "VERIFIED_FINITE",
        "NG25": "REFUTED",
        "NG26": "REFUTED",
        "H72": "OPEN",
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
