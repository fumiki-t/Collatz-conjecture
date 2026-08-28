#!/usr/bin/env python3
"""Generate exact Phase 16 critical-dichotomy evidence.

All acceptance decisions use integers or Fraction.  Decimal strings are not
stored because they are not proof inputs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

A_BITS = "11101"
B_BITS = "1100"
NEGATIVE_A = "111111111101111110101011110010001001100"
NEGATIVE_D = "1101101101110011100111011101010101101101"
GAIN_FOUR_D = "11111111111111101110000000001"
GAIN_FOUR_A = "1111111111101111110100100"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def encoded(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def translation(word: str) -> int:
    result = 0
    power = 1
    for bit in word:
        if bit == "1":
            result = 3 * result + power
        elif bit != "0":
            raise ValueError("binary word required")
        power <<= 1
    return result


def trace(source: int, word: str) -> list[int]:
    values = [source]
    value = source
    for expected in word:
        if str(value & 1) != expected:
            raise AssertionError("literal parity mismatch")
        value = shortcut(value)
        values.append(value)
    return values


def is_safe(word: str) -> bool:
    q = 0
    for length, bit in enumerate(word, 1):
        q += bit == "1"
        if 3**q <= 1 << length:
            return False
    return bool(word)


def canonical(word: str) -> dict[str, object]:
    length = len(word)
    q = word.count("1")
    B = translation(word)
    two, three = 1 << length, 3**q
    source = (-B * pow(three, -1, two)) % two or two
    endpoint = (B * pow(two, -1, three)) % three or three
    if trace(source, word)[-1] != endpoint:
        raise AssertionError("canonical affine occurrence")
    return {"word": word, "L": length, "Q": q, "B": B, "source": source, "endpoint": endpoint, "safe": is_safe(word)}


def log_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    """Positive atanh-series enclosure for log(value), value >= 1."""
    if value < 1 or terms < 1:
        raise ValueError("positive ratio and term count required")
    z = (value - 1) / (value + 1)
    z2 = z * z
    power = z
    partial = Fraction()
    for index in range(terms):
        partial += power / (2 * index + 1)
        power *= z2
    lower = 2 * partial
    upper = lower + 2 * power / ((2 * terms + 1) * (1 - z2))
    return lower, upper


def negative_carry() -> dict[str, object]:
    a, d = canonical(NEGATIVE_A), canonical(NEGATIVE_D)
    if a["Q"] != d["Q"] or a["endpoint"] != d["endpoint"] or d["L"] != a["L"] + 1:
        raise AssertionError("negative carry pair boundary")
    difference = 2 * int(a["B"]) - int(d["B"])
    q = int(a["Q"])
    carry = difference // 3**q
    if difference % 3**q or carry != -3 or int(d["source"]) != 2 * int(a["source"]) + carry:
        raise AssertionError("negative carry identity")
    return {
        "claim": "NG28",
        "status": "REFUTED",
        "hypothesis": "Every shorter safe same-Q predecessor of a safe endpoint has positive carry.",
        "a": a,
        "d": d,
        "k": 1,
        "scaled_B_difference": difference,
        "carry": carry,
        "identity": "S_d=2*S_a-3",
    }


def allowed_residues() -> list[dict[str, object]]:
    rows = []
    specifications = [
        ("[N,9N/8)", True, True, True, 6),
        ("[9N/8,3N/2)", True, False, True, 9),
        ("[3N/2,2N)", False, False, True, 15),
        ("[2N,9N/4)", False, False, False, 20),
        ("[9N/4,infinity)", False, False, False, 24),
    ]
    for label, exclude_mod3_two, exclude_mod9_four, exclude_mod8_five, expected in specifications:
        residues = []
        for residue in range(72):
            if residue % 2 == 0 or residue % 3 == 0:
                continue
            if exclude_mod3_two and residue % 3 == 2:
                continue
            if exclude_mod9_four and residue % 9 == 4:
                continue
            if residue % 9 == 8 and label != "[9N/4,infinity)":
                continue
            if exclude_mod8_five and residue % 8 == 5:
                continue
            residues.append(residue)
        if len(residues) != expected:
            raise AssertionError(f"mod-72 count for {label}")
        rows.append({"interval": label, "residues": residues, "count": len(residues), "density": encoded(Fraction(len(residues), 72))})
    return rows


def local_merge_samples() -> dict[str, object]:
    mod3 = []
    mod9_four = []
    mod9_eight = []
    odd_even_even = []
    all_odd = []
    for x in range(5, 500, 2):
        if x % 3 == 2:
            u = (2 * x - 1) // 3
            if trace(u, "1")[-1] != x:
                raise AssertionError("mod-3 merge")
            mod3.append([x, u])
        if x % 9 == 4:
            u = (8 * x - 5) // 9
            if trace(u, "110")[-1] != x:
                raise AssertionError("mod-9 four merge")
            mod9_four.append([x, u])
        if x % 9 == 8:
            u = (4 * x - 5) // 9
            if trace(u, "11")[-1] != x:
                raise AssertionError("mod-9 eight merge")
            mod9_eight.append([x, u])
        if x % 8 == 5:
            y = (x - 1) // 2
            left = trace(y, "01")[-1]
            right = trace(x, "100")[-1]
            if left != right or left != (3 * x + 1) // 8:
                raise AssertionError("odd-even-even merge")
            odd_even_even.append([x, y, left])
    for r in range(1, 7):
        modulus = 3**r
        x = next(value for value in range(modulus - 1, 20 * modulus, modulus) if value > 1 and value & 1)
        u = (2**r * (x + 1)) // modulus - 1
        if trace(u, "1" * r)[-1] != x:
            raise AssertionError("all-odd inverse")
        all_odd.append({"r": r, "x": x, "u": u})
    return {
        "mod3_first_samples": mod3[:8],
        "mod9_four_first_samples": mod9_four[:8],
        "mod9_eight_first_samples": mod9_eight[:8],
        "odd_even_even_first_samples": odd_even_even[:8],
        "all_odd_samples": all_odd,
        "literal_sample_limit": 500,
    }


def theory_artifact(log_terms: int = 12) -> dict[str, object]:
    log2_lower, log2_upper = log_bounds(Fraction(2), log_terms)
    log98_lower, log98_upper = log_bounds(Fraction(9, 8), log_terms)
    reduced_ratio = Fraction(144299, 82944)
    ratio_lower, ratio_upper = log_bounds(reduced_ratio, log_terms)
    # Phi(250) = 13/36 log(9/8) + 8/3 log(2) + 1/3 log(reduced_ratio).
    # Moving 8/3 log(2) to the right leaves the exact comparison below.
    comparison_margin = (
        Fraction(1, 3) * log2_lower
        - Fraction(13, 36) * log98_upper
        - Fraction(1, 3) * ratio_upper
        - Fraction(3, 4000)
    )
    if comparison_margin <= 0:
        raise AssertionError("250 exact log margin")
    intervals = allowed_residues()
    continuous = Fraction(1, 96) + Fraction(3, 64) + Fraction(5, 48) + Fraction(5, 72)
    if continuous != Fraction(133, 576):
        raise AssertionError("packing capacity")
    return {
        "format": "collatz-phase16-theory-v1",
        "claims": {
            "P97": "VERIFIED_THEOREM",
            "P98": "VERIFIED_THEOREM",
            "P99": "VERIFIED_THEOREM",
            "P100": "VERIFIED_THEOREM",
            "P101": "VERIFIED_THEOREM",
            "P102": "VERIFIED_THEOREM",
            "P103": "CONDITIONAL",
            "NG28": "REFUTED",
            "H97": "OPEN",
            "H98": "OPEN"
        },
        "negative_carry": negative_carry(),
        "carry_bound": {
            "safe_correction": "B(w)/3^q=1/3 for q=1; 1/3<B(w)/3^q<q/3 for q>=2",
            "same_Q": "m=(2^k B(a)-B(d))/3^q > -q/3 and > (2^k-q)/3",
            "negative_carry_requires": "2^k<q",
            "proposal_repair": "The proposed strict upper bound is false at q=1 (word 1); no distinct-length safe same-Q pair exists there."
        },
        "normalized_correction": {
            "identity": "Y_j=N+B_j/3^j",
            "first_crossing": "X=(3^q/2^K_q)Y_q<Y_q and Z=2X",
            "geodesic_criterion": "Y_q<2N implies every prefix is shortest in its same-Q safe endpoint class"
        },
        "local_merges": local_merge_samples(),
        "residue_packing": {
            "modulus": 72,
            "intervals": intervals,
            "periodic_error_sum": sum(int(row["count"]) for row in intervals),
            "initial_point_plus_errors": 75,
            "continuous_count_below_9N_over_4": encoded(continuous),
            "cutoff_ratio": "H/N=3t+299/192",
            "Phi": "13/36 log(9/8)+1/3 log(4/3)+1/3 log((3t+299/192)/(9/4))"
        },
        "log_certificate": {
            "method": "log(x)=2*sum(z^(2n+1)/(2n+1)), z=(x-1)/(x+1), with a geometric tail",
            "terms": log_terms,
            "log2": {"lower": encoded(log2_lower), "upper": encoded(log2_upper)},
            "log9_over_8": {"lower": encoded(log98_lower), "upper": encoded(log98_upper)},
            "reduced_large_ratio": {"ratio": encoded(reduced_ratio), "removed_power_of_two": 8, "lower": encoded(ratio_lower), "upper": encoded(ratio_upper)},
            "comparison": "Phi(250)+75/100000<3log(2)",
            "exact_positive_margin_after_reduction": encoded(comparison_margin)
        },
        "dichotomy": {
            "hypotheses": ["least positive counterexample", "finite coefficient first crossing", "N>=100000", "odd inputs before crossing are distinct"],
            "G250": "q<=250N => Y_q<2N => all-prefix same-Q geodesic",
            "H250": "q>250N => N<q/250, X<q/125, Z<2q/125",
            "periodic_boundary": "Without distinctness only q<3N gives all-prefix geodesic; otherwise N<=q/3 and X<2q/3.",
            "q0_consequence": {"q0": 72057431991, "external_lower_bound": "2075*2^60", "q0_less_than_three_times_bound": 72057431991 < 3 * 2075 * 2**60, "status": "CONDITIONAL"}
        },
        "external_literature_role": "Angeltveit Section 2.3 supplies context for the merge sieve; P99 is proved internally and does not depend on it.",
        "what_this_result_does_not_prove": "Neither G250 nor H250 is excluded. The periodic branch, H89, H72, and the Collatz conjecture remain open.",
        "proves_collatz": False
    }


@dataclass(frozen=True, slots=True)
class WordRow:
    bits: int
    length: int
    q: int
    B: int
    source: int
    endpoint: int

    @property
    def word(self) -> str:
        return format(self.bits, f"0{self.length}b")


def row(bits: int, length: int, q: int, B: int) -> WordRow:
    two, three = 1 << length, 3**q
    return WordRow(bits, length, q, B, (-B * pow(three, -1, two)) % two or two, (B * pow(two, -1, three)) % three or three)


def enumerate_safe(maximum_q: int) -> dict[int, list[WordRow]]:
    grouped = {q: [] for q in range(1, maximum_q + 1)}
    frontier = [(0, 0, 0)]
    maximum_length = (3**maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        following = []
        for bits, q, B in frontier:
            if q and 3**q > 1 << length:
                item = row(bits << 1, length, q, B)
                grouped[q].append(item)
                following.append((item.bits, q, B))
            if q < maximum_q and 3 ** (q + 1) > 1 << length:
                item = row((bits << 1) | 1, length, q + 1, 3 * B + (1 << (length - 1)))
                grouped[item.q].append(item)
                following.append((item.bits, item.q, item.B))
        frontier = following
    return grouped


def contact_count(word: str) -> int:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    return sum(position == (3**j).bit_length() - 1 for j, position in enumerate(positions))


def prefix_geodesic(word: str, minimum_lengths: dict[tuple[int, int], int]) -> bool:
    B = q = 0
    for length, bit in enumerate(word, 1):
        if bit == "1":
            B = 3 * B + (1 << (length - 1))
            q += 1
        three = 3**q
        endpoint = (B * pow(1 << length, -1, three)) % three or three
        if minimum_lengths[(q, endpoint)] < length:
            return False
    return True


def finite_layers(maximum_q: int) -> dict[str, object]:
    grouped = enumerate_safe(maximum_q)
    minimum_lengths: dict[tuple[int, int], int] = {}
    for q, rows in grouped.items():
        for item in rows:
            key = (q, item.endpoint)
            minimum_lengths[key] = min(minimum_lengths.get(key, item.length), item.length)
    digest = hashlib.sha256()
    counts = {}
    pair_count = negative_count = 0
    smallest_finite_carry = None
    for q in range(1, maximum_q + 1):
        by_endpoint: dict[int, list[WordRow]] = defaultdict(list)
        for item in grouped[q]:
            by_endpoint[item.endpoint].append(item)
        for rows in by_endpoint.values():
            ordered = sorted(rows, key=lambda value: (value.length, value.word))
            for left_index, a in enumerate(ordered):
                for d in ordered[left_index + 1:]:
                    k = d.length - a.length
                    if k <= 0:
                        continue
                    numerator = (1 << k) * a.B - d.B
                    if numerator % 3**q:
                        raise AssertionError("same-Q carry divisibility")
                    carry = numerator // 3**q
                    pair_count += 1
                    negative_count += carry < 0
                    if smallest_finite_carry is None or carry < smallest_finite_carry:
                        smallest_finite_carry = carry
                    if not (3 * carry > -q and 3 * carry > (1 << k) - q):
                        raise AssertionError("carry lower bound")
        critical_length = (3**q).bit_length() - 1
        critical = sorted((item for item in grouped[q] if item.length == critical_length), key=lambda item: item.word)
        geodesic = all_prefix = rich = rich_geo = 0
        minimum_source = min(critical, key=lambda item: (item.source, item.word))
        minimum_endpoint = min(critical, key=lambda item: (item.endpoint, item.word))
        max_contacts = 0
        for item in critical:
            is_geodesic = minimum_lengths[(q, item.endpoint)] == item.length
            is_all_prefix = prefix_geodesic(item.word, minimum_lengths)
            contacts = contact_count(item.word)
            is_rich = 100 * contacts > 43 * q
            geodesic += is_geodesic
            all_prefix += is_all_prefix
            rich += is_rich
            rich_geo += is_rich and is_geodesic
            max_contacts = max(max_contacts, contacts)
            digest.update(f"{q}|{item.word}|{item.source}|{item.endpoint}|{int(is_geodesic)}|{int(is_all_prefix)}|{contacts}\n".encode("ascii"))
        if geodesic != all_prefix:
            raise AssertionError("finite prefix-closure reconstruction")
        counts[str(q)] = {
            "safe_words_all_lengths": len(grouped[q]),
            "critical_words": len(critical),
            "same_Q_geodesic": geodesic,
            "all_prefix_same_Q_geodesic": all_prefix,
            "contact_rich": rich,
            "contact_rich_geodesic": rich_geo,
            "maximum_contacts": max_contacts,
            "minimum_source": {"value": minimum_source.source, "word": minimum_source.word, "endpoint": minimum_source.endpoint},
            "minimum_endpoint": {"value": minimum_endpoint.endpoint, "word": minimum_endpoint.word, "source": minimum_endpoint.source}
        }
    return {
        "format": "collatz-phase16-finite-layers-v1",
        "maximum_Q": maximum_q,
        "critical_definition": "safe word with Q=q and L=floor(log2(3^q)); appending one zero is the coefficient first crossing",
        "contact_definition": "odd position d_j is a contact iff d_j=floor(log2(3^j)); contact-rich means 100*contacts>43*Q",
        "counts_by_Q": counts,
        "same_Q_endpoint_pair_count": pair_count,
        "negative_carry_pair_count_in_cutoff": negative_count,
        "minimum_carry_in_cutoff": smallest_finite_carry,
        "critical_row_digest_sha256": digest.hexdigest(),
        "finite_boundary": "Complete through Q<=maximum_Q only; no eventual geodesic or contact theorem follows.",
        "proves_collatz": False
    }


def safe_prefix_length(word: str) -> int:
    q = 0
    for length, bit in enumerate(word, 1):
        q += bit == "1"
        if 3**q <= 1 << length:
            return length - 1
    return len(word)


def source_trace_word(source: int, length: int) -> str:
    bits = []
    value = source
    for _ in range(length):
        bits.append(str(value & 1))
        value = shortcut(value)
    return "".join(bits)


def adversarial_artifact() -> dict[str, object]:
    inputs: list[tuple[str, str]] = []
    for m in range(2, 9):
        inputs.append((f"2^{m}-1", source_trace_word(2**m - 1, 32)))
        inputs.append((f"8^{m}-5", source_trace_word(8**m - 5, 32)))
    for block_count in range(1, 5):
        for choice in product(("110", "111"), repeat=block_count):
            inputs.append((f"(110|111)^*:{''.join(choice)}", "".join(choice)))
    inputs.extend([("A=11101", A_BITS), ("B=1100", B_BITS), ("W=AB", A_BITS + B_BITS)])
    for r in range(1, 5):
        for s in range(1, 5):
            inputs.append((f"A^{r}B^{s}", A_BITS * r + B_BITS * s))
    inputs.extend([("Phase7-all-contact-prefix", "1" * 12 + "0" * 7), ("NG27-d", GAIN_FOUR_D), ("NG27-a", GAIN_FOUR_A), ("NG28-a", NEGATIVE_A), ("NG28-d", NEGATIVE_D)])
    digest = hashlib.sha256()
    rows = []
    for name, word in inputs:
        B = translation(word)
        safe_length = safe_prefix_length(word)
        item = {
            "name": name,
            "word": word,
            "L": len(word),
            "Q": word.count("1"),
            "B": B,
            "safe_prefix_length": safe_length,
            "whole_word_safe": safe_length == len(word)
        }
        rows.append(item)
        digest.update(f"{name}|{word}|{B}|{safe_length}\n".encode("ascii"))
    return {
        "format": "collatz-phase16-adversarial-v1",
        "families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s", "Phase 7 all-contact prefixes", "NG27", "NG28"],
        "rows": rows,
        "row_digest_sha256": digest.hexdigest(),
        "interpretation": "These bounded rows are regression tests for conventions and theorem hypotheses, not evidence of asymptotic exclusion.",
        "proves_collatz": False
    }


def obstruction_report() -> str:
    return """# Phase 16 obstruction report

## NG28 — positive same-Q carry

`REFUTED`.  The stored Q=26 pair is coefficient-safe, shares canonical
endpoint 716727426419, and has carry -3.  Thus positivity cannot be used as a
prefix recursion invariant.  P97 retains the sharp elementary lower bounds;
in particular a negative carry requires `2^k<q`.

## G250 — contact-rich all-prefix geodesic branch

`OPEN`.  Phase 16 proves geodesicity when `q<=250N`, but high contact density
plus geodesicity is consistent with finite prefixes of the formal all-contact
2-adic word.  A successful exclusion must retain one fixed positive ordinary
source and survive NG17, P73, NG24--NG28, and the mandatory families.

## H250 — ultra-low two-sided height branch

`OPEN`.  When `q>250N`, the exact packing argument gives `X<q/125` and
`Z<2q/125`.  No accepted automaton, transducer, pumping, or meet-in-the-middle
certificate currently proves this two-sided box empty.

## Periodic branch

`OPEN`.  The 250 packing uses distinct odd orbit values.  Without distinctness
Phase 16 retains only `Y_q<N+q/3`, hence the `q<3N` geodesic alternative or
the bounds `N<=q/3`, `X<2q/3`.  It does not eliminate a nontrivial cycle.

## What this result does not prove

It does not exclude G250, H250, the periodic branch, H89, H72, or any Collatz
counterexample.  The Q<=17 layer table is finite.  `proves_collatz=false`.
"""


def generate(artifact_dir: Path, maximum_q: int = 17) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "phase16_theory.json", theory_artifact())
    write_json(artifact_dir / "phase16_finite_layers.json", finite_layers(maximum_q))
    write_json(artifact_dir / "phase16_adversarial.json", adversarial_artifact())
    (artifact_dir / "phase16_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--maximum-q", type=int, default=17)
    args = parser.parse_args()
    generate(args.artifact_dir, args.maximum_q)
    print(json.dumps({"generated": True, "maximum_Q": args.maximum_q, "proves_collatz": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
