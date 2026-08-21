#!/usr/bin/env python3
"""Phase 2 exact obstruction mining for an affine certificate frontier."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Iterator

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.model import affine_word


def certificate_records(path: Path) -> tuple[dict[str, object], Iterator[list[object]], dict[str, object]]:
    stream = path.open("r", encoding="utf-8")
    first = stream.readline().rstrip("\n")
    marker = ',"records":['
    if not first.endswith(marker):
        stream.close()
        raise ValueError("invalid certificate header")
    header = json.loads(first[: -len(marker)] + "}")
    summary: dict[str, object] = {}

    def iterator() -> Iterator[list[object]]:
        try:
            for line in stream:
                text = line.rstrip("\n")
                if text.startswith('null],"summary":'):
                    payload = text[len('null],"summary":') :]
                    summary.update(json.loads(payload[:-1]))
                    return
                if not text.endswith(","):
                    raise ValueError("malformed certificate record")
                yield json.loads(text[:-1])
            raise ValueError("certificate footer is missing")
        finally:
            stream.close()

    return header, iterator(), summary


def shortest_period(word: str) -> int:
    if not word:
        return 0
    for period in range(1, len(word) + 1):
        if all(word[index] == word[index % period] for index in range(len(word))):
            return period
    raise AssertionError("the full word is always a period")


def best_repeat(word: str, side: str, max_block: int = 16) -> tuple[str, int]:
    if not word:
        return "", 0
    candidates: list[tuple[tuple[int, int, int], str, int]] = []
    for length in range(1, min(max_block, len(word)) + 1):
        if side == "prefix":
            block = word[:length]
            count = 0
            while word[count * length : (count + 1) * length] == block:
                count += 1
        elif side == "suffix":
            block = word[-length:]
            count = 0
            end = len(word) - count * length
            while end - length >= 0 and word[end - length : end] == block:
                count += 1
                end -= length
        else:
            raise ValueError("side must be prefix or suffix")
        candidates.append(((count, count * length, -length), block, count))
    _score, block, count = max(candidates)
    return block, count


def coefficient_comparisons(word: str) -> str:
    odd_count = 0
    result: list[str] = []
    for depth, bit in enumerate(word, start=1):
        odd_count += bit == "1"
        left = pow(3, odd_count)
        right = 1 << depth
        result.append("<" if left < right else ">" if left > right else "=")
    return "".join(result)


def sign(value: int) -> str:
    return "negative" if value < 0 else "positive" if value > 0 else "zero"


def v2(value: int) -> int | str:
    if value == 0:
        return "infinity"
    value = abs(value)
    exponent = 0
    while value % 2 == 0:
        exponent += 1
        value //= 2
    return exponent


def block_facts(block: str) -> dict[str, object]:
    length, odd_count, p, b = affine_word(block)
    q = 1 << length
    denominator = q - p
    if denominator == 0:
        fixed = None
    else:
        fraction = Fraction(b, denominator)
        fixed = {
            "numerator": fraction.numerator,
            "denominator": fraction.denominator,
            "numerator_bits": abs(fraction.numerator).bit_length(),
            "denominator_bits": fraction.denominator.bit_length(),
        }
    return {"L": length, "q_w": odd_count, "P": p, "Q": q, "B_w": b, "fixed_point": fixed}


def repeat_details(word: str, side: str) -> dict[str, object]:
    block, count = best_repeat(word, side)
    facts = block_facts(block)
    if side == "prefix":
        exit_word = word[len(block) * count :]
        entry_word = ""
    else:
        exit_word = ""
        entry_word = word[: len(word) - len(block) * count]
    exit_length, exit_odds, exit_p, exit_b = affine_word(exit_word)
    return {
        "side": side,
        "block": block,
        "count": count,
        **facts,
        "entry_word_before_repetition": entry_word,
        "exit_parity_word": exit_word,
        "exit_affine_map": {
            "length": exit_length,
            "odd_steps": exit_odds,
            "P": exit_p,
            "Q": 1 << exit_length,
            "B": exit_b,
        },
    }


def explained_by_short_shadow(word: str) -> bool:
    # Two copies would make the universal survivor prefix ``11`` a vacuous
    # explanation.  Three copies is the explicit Phase 2 dictionary threshold;
    # all one- and two-copy candidates are still recorded in the artifacts.
    return best_repeat(word, "prefix")[1] >= 3 or best_repeat(word, "suffix")[1] >= 3


def represented_minimum(k: int, r: int) -> int:
    if r >= 2:
        return r
    modulus = 1 << k
    return r + modulus * max(0, -((r - 2) // modulus))


def canonical_key(
    q: int,
    slope: int,
    intercept: int,
    period: int,
    prefix: dict[str, object],
    suffix: dict[str, object],
) -> tuple[object, ...]:
    return (
        q,
        sign(slope),
        sign(intercept),
        period,
        prefix["block"],
        prefix["count"],
        suffix["block"],
        suffix["count"],
        False,
    )


def fixed_columns(details: dict[str, object]) -> tuple[object, object, object, object]:
    fixed = details["fixed_point"]
    if fixed is None:
        return "", "", "", ""
    assert isinstance(fixed, dict)
    return (
        fixed["numerator"],
        fixed["denominator"],
        fixed["numerator_bits"],
        fixed["denominator_bits"],
    )


def update_candidate(
    candidates: dict[tuple[str, str], dict[str, object]],
    details: dict[str, object],
    node: tuple[int, int, int, int, str],
) -> None:
    k, r, y, q, word = node
    side = str(details["side"])
    block = str(details["block"])
    key = (side, block)
    facts = {name: details[name] for name in ("L", "q_w", "P", "Q", "B_w", "fixed_point")}
    valuation = v2((int(details["Q"]) - int(details["P"])) * r - int(details["B_w"]))
    representative = {
        "node": {"k": k, "r": r, "y": y, "q": q, "parity_word": word},
        "v2_Q_minus_P_times_r_minus_B": valuation,
        "entry_word_before_repetition": details["entry_word_before_repetition"],
        "exit_parity_word": details["exit_parity_word"],
        "exit_affine_map": details["exit_affine_map"],
    }
    current = candidates.get(key)
    count = int(details["count"])
    if current is None:
        candidates[key] = {
            "side": side,
            "block": block,
            **facts,
            "occurrences_as_best": 1,
            "longest_repetition_count": count,
            "representative_at_longest": representative,
        }
        return
    current["occurrences_as_best"] = int(current["occurrences_as_best"]) + 1
    old_count = int(current["longest_repetition_count"])
    old_node = current["representative_at_longest"]
    assert isinstance(old_node, dict)
    old_min = represented_minimum(
        int(old_node["node"]["k"]), int(old_node["node"]["r"])  # type: ignore[index]
    )
    new_min = represented_minimum(k, r)
    if count > old_count or (count == old_count and new_min < old_min):
        current["longest_repetition_count"] = count
        current["representative_at_longest"] = representative


CSV_FIELDS = [
    "parity_prefix",
    "prefix_coefficient_comparisons",
    "k",
    "r",
    "y",
    "q",
    "descent_slope",
    "descent_intercept",
    "shortest_exact_period",
    "prefix_block",
    "prefix_repetitions",
    "prefix_fixed_numerator",
    "prefix_fixed_denominator",
    "prefix_fixed_numerator_bits",
    "prefix_fixed_denominator_bits",
    "suffix_block",
    "suffix_repetitions",
    "suffix_fixed_numerator",
    "suffix_fixed_denominator",
    "suffix_fixed_numerator_bits",
    "suffix_fixed_denominator_bits",
    "earlier_uniform_descent",
    "generic_smaller_preimage_merge_found",
    "short_shadow_explained",
    "canonical_signature",
]


def mine(certificate: Path, artifact_dir: Path) -> dict[str, object]:
    header, records, certificate_summary = certificate_records(certificate)
    if header.get("format") != "collatz-affine-certificate-v1":
        raise ValueError("unsupported certificate format")
    max_depth = int(header["max_depth"])
    artifact_dir.mkdir(parents=True, exist_ok=True)

    total_survivors: Counter[int] = Counter()
    explained: Counter[int] = Counter()
    smallest_unexplained: dict[int, tuple[int, tuple[int, int, int, int, str]]] = {}
    signatures: Counter[tuple[object, ...]] = Counter()
    signature_example: dict[tuple[object, ...], tuple[int, int, int, int, str]] = {}
    candidates: dict[tuple[str, str], dict[str, object]] = {}

    stats_path = artifact_dir / "survivor_stats.csv"
    with stats_path.open("w", encoding="utf-8", newline="") as csv_stream:
        writer = csv.DictWriter(csv_stream, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in records:
            k, r, y, q, word, rule = record
            if not isinstance(word, str) or rule not in ("SPLIT", "OPEN"):
                continue
            node = (int(k), int(r), int(y), int(q), word)
            total_survivors[int(k)] += 1
            is_explained = explained_by_short_shadow(word)
            if is_explained:
                explained[int(k)] += 1
            else:
                minimum = represented_minimum(int(k), int(r))
                old = smallest_unexplained.get(int(k))
                if old is None or minimum < old[0]:
                    smallest_unexplained[int(k)] = (minimum, node)
            if rule != "OPEN":
                continue

            prefix = repeat_details(word, "prefix")
            suffix = repeat_details(word, "suffix")
            slope = pow(3, int(q)) - (1 << int(k))
            intercept = int(y) - int(r)
            period = shortest_period(word)
            key = canonical_key(int(q), slope, intercept, period, prefix, suffix)
            signatures[key] += 1
            current_example = signature_example.get(key)
            if current_example is None or represented_minimum(int(k), int(r)) < represented_minimum(
                current_example[0], current_example[1]
            ):
                signature_example[key] = node
            update_candidate(candidates, prefix, node)
            update_candidate(candidates, suffix, node)
            prefix_fixed = fixed_columns(prefix)
            suffix_fixed = fixed_columns(suffix)
            writer.writerow(
                {
                    "parity_prefix": word,
                    "prefix_coefficient_comparisons": coefficient_comparisons(word),
                    "k": k,
                    "r": r,
                    "y": y,
                    "q": q,
                    "descent_slope": slope,
                    "descent_intercept": intercept,
                    "shortest_exact_period": period,
                    "prefix_block": prefix["block"],
                    "prefix_repetitions": prefix["count"],
                    "prefix_fixed_numerator": prefix_fixed[0],
                    "prefix_fixed_denominator": prefix_fixed[1],
                    "prefix_fixed_numerator_bits": prefix_fixed[2],
                    "prefix_fixed_denominator_bits": prefix_fixed[3],
                    "suffix_block": suffix["block"],
                    "suffix_repetitions": suffix["count"],
                    "suffix_fixed_numerator": suffix_fixed[0],
                    "suffix_fixed_denominator": suffix_fixed[1],
                    "suffix_fixed_numerator_bits": suffix_fixed[2],
                    "suffix_fixed_denominator_bits": suffix_fixed[3],
                    "earlier_uniform_descent": "false",
                    "generic_smaller_preimage_merge_found": "false",
                    "short_shadow_explained": str(is_explained).lower(),
                    "canonical_signature": json.dumps(key, separators=(",", ":")),
                }
            )

    signature_rows: list[dict[str, object]] = []
    for key, count in sorted(signatures.items(), key=lambda item: (-item[1], repr(item[0]))):
        example = signature_example[key]
        signature_rows.append(
            {
                "signature": {
                    "q": key[0],
                    "slope_sign": key[1],
                    "intercept_sign": key[2],
                    "shortest_exact_period": key[3],
                    "prefix_block": key[4],
                    "prefix_repetitions": key[5],
                    "suffix_block": key[6],
                    "suffix_repetitions": key[7],
                    "generic_merge_found": key[8],
                },
                "count": count,
                "smallest_represented_example": {
                    "n": represented_minimum(example[0], example[1]),
                    "k": example[0],
                    "r": example[1],
                    "y": example[2],
                    "q": example[3],
                    "parity_word": example[4],
                },
            }
        )

    canonical_payload = {
        "format": "collatz-canonical-signatures-v1",
        "exact_discrete_signature_fields": [
            "q",
            "slope_sign",
            "intercept_sign",
            "shortest_exact_period",
            "best_prefix_block_and_count",
            "best_suffix_block_and_count",
            "generic_merge_found",
        ],
        "clusters": signature_rows,
    }
    (artifact_dir / "canonical_signatures.json").write_text(
        json.dumps(canonical_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    candidate_rows = [
        value for _key, value in sorted(candidates.items(), key=lambda item: item[0])
    ]
    repeated_payload = {
        "format": "collatz-repeated-blocks-v1",
        "selection": "best prefix and best suffix blocks, length at most 16",
        "explanation_test": "prefix or suffix repetition count at least 3",
        "candidates": candidate_rows,
    }
    (artifact_dir / "repeated_blocks.json").write_text(
        json.dumps(repeated_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    tested_depths: list[dict[str, object]] = []
    for depth in range(max_depth + 1):
        total = total_survivors[depth]
        covered = explained[depth]
        item: dict[str, object] = {
            "depth": depth,
            "survivors": total,
            "explained": covered,
            "unexplained": total - covered,
            "coverage_fraction": f"{covered}/{total}" if total else "0/0",
        }
        if depth in smallest_unexplained:
            minimum, node = smallest_unexplained[depth]
            item["smallest_unexplained"] = {
                "n": minimum,
                "k": node[0],
                "r": node[1],
                "y": node[2],
                "q": node[3],
                "parity_word": node[4],
            }
        if depth and total_survivors[depth - 1]:
            item["survivor_growth_ratio_from_previous_depth"] = (
                f"{total}/{total_survivors[depth - 1]}"
            )
            item["unexplained_growth_ratio_from_previous_depth"] = (
                f"{total - covered}/{total_survivors[depth - 1] - explained[depth - 1]}"
                if total_survivors[depth - 1] != explained[depth - 1]
                else "undefined"
            )
        tested_depths.append(item)

    final = tested_depths[-1]
    smallest = final.get("smallest_unexplained")
    top = signature_rows[:10]
    report_lines = [
        "# Phase 2 obstruction report",
        "",
        "This is a finite exact computation, not a proof of the Collatz conjecture or of asymptotic growth.",
        "",
        "## Checker-proved facts",
        "",
        "The independent verifier checks SPLIT, DESCENT, FINITE_TAIL, and DIRECT arithmetic. "
        "It leaves the depth-limited OPEN frontier unresolved.",
        "",
        "## Computational observations",
        "",
        f"- Search depth: {max_depth}",
        f"- OPEN survivors: {total_survivors[max_depth]}",
        f"- Short-shadow coverage at depth {max_depth}: {explained[max_depth]}/{total_survivors[max_depth]}",
        f"- Unexplained survivors at depth {max_depth}: {total_survivors[max_depth] - explained[max_depth]}",
        "- The tested survivor counts grow at an exponential-looking finite-range rate; asymptotic "
        "classification remains unresolved.",
        "- A non-vanishing asymptotic short-shadow fraction is unresolved; only the displayed finite-depth fraction was observed.",
        "- No generic smaller-preimage/path-merge rule is claimed or accepted in Phase 1-2.",
        "",
        "## Failed hypothesis",
        "",
        "The finite dictionary consisting of every prefix/suffix block of length at most 16, with at least three "
        "consecutive repetitions, does not explain every tested surviving branch. This is a finite-depth counterexample "
        "to that precise dictionary test, not a theorem about all possible macro dictionaries.",
        "",
    ]
    if isinstance(smallest, dict):
        report_lines.extend(
            [
                f"Smallest unexplained represented integer: `{smallest['n']}`.",
                "",
                f"Exact counterexample parity word: `{smallest['parity_word']}`.",
                "",
            ]
        )
    report_lines.extend(
        [
            "### Exact growth table",
            "",
            "| depth | survivors | explained | unexplained | survivor ratio | unexplained ratio |",
            "|---:|---:|---:|---:|:---|:---|",
        ]
    )
    for item in tested_depths:
        report_lines.append(
            f"| {item['depth']} | {item['survivors']} | {item['explained']} | {item['unexplained']} | "
            f"{item.get('survivor_growth_ratio_from_previous_depth', '-')} | "
            f"{item.get('unexplained_growth_ratio_from_previous_depth', '-')} |"
        )
    report_lines.extend(
        [
            "",
            "## Dominant exact signatures",
            "",
            "The JSON artifact contains all clusters. The ten largest exact discrete clusters are:",
            "",
        ]
    )
    for row in top:
        report_lines.append(
            f"- count `{row['count']}`: `{json.dumps(row['signature'], separators=(',', ':'), sort_keys=True)}`"
        )
    report_lines.extend(
        [
            "",
            "## Conjectural next extension",
            "",
            "Add a parametric repeated-block MACRO carrying an exact repetition parameter and an independently checked "
            "well-founded MERGE dependency rank. It should encode divisibility and exit maps explicitly; empirical path "
            "coincidence is insufficient.",
            "",
            "## Method notes",
            "",
            "- All clustering keys and coverage decisions are exact discrete values.",
            "- `generic_smaller_preimage_merge_found=false` means the Phase 1-2 rule language contains no accepted MERGE; "
            "it is not evidence that no merge exists.",
            "- Prefix coefficient comparisons use exact integer comparisons of `3^q_i` with `2^i`.",
        ]
    )
    (artifact_dir / "obstruction_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    return {
        "max_depth": max_depth,
        "open_survivors": total_survivors[max_depth],
        "explained_by_short_shadow": explained[max_depth],
        "unexplained": total_survivors[max_depth] - explained[max_depth],
        "smallest_unexplained": smallest,
        "canonical_signature_count": len(signature_rows),
        "candidate_block_count": len(candidate_rows),
        "certificate_summary_loaded": bool(certificate_summary),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    result = mine(args.certificate, args.artifact_dir)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
