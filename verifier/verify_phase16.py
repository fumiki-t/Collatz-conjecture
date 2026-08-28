#!/usr/bin/env python3
"""Independent exact verifier for Phase 16 critical-dichotomy evidence.

The verifier intentionally does not import the generator.  It reconstructs
affine constants as explicit odd-position sums and enumerates safe words as
literal strings rather than packed integer rows.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

WORD_A = "11101"
WORD_B = "1100"
BAD_A = "111111111101111110101011110010001001100"
BAD_D = "1101101101110011100111011101010101101101"
GAIN_D = "11111111111111101110000000001"
GAIN_A = "1111111111101111110100100"


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} is not an object")
    return value


def fraction(value: object) -> Fraction:
    if not isinstance(value, dict):
        fail("fraction object missing")
    try:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        fail(f"invalid fraction: {exc}")


def step(value: int) -> int:
    return (3 * value + 1) // 2 if value % 2 else value // 2


def explicit_constant(word: str) -> int:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    result = 0
    q = len(positions)
    for odd_index, position in enumerate(positions):
        result += (1 << position) * 3 ** (q - 1 - odd_index)
    if any(bit not in "01" for bit in word):
        fail("nonbinary word")
    return result


def literal_trace(source: int, word: str) -> list[int]:
    values = [source]
    current = source
    for expected in word:
        if str(current % 2) != expected:
            fail("literal parity mismatch")
        current = step(current)
        values.append(current)
    return values


def safe(word: str) -> bool:
    ones = 0
    for length, bit in enumerate(word, 1):
        ones += bit == "1"
        if pow(3, ones) <= pow(2, length):
            return False
    return bool(word)


def canonical(word: str) -> dict[str, object]:
    length, q = len(word), word.count("1")
    B = explicit_constant(word)
    two, three = pow(2, length), pow(3, q)
    source = (-B * pow(three, -1, two)) % two or two
    endpoint = (B * pow(two, -1, three)) % three or three
    if literal_trace(source, word)[-1] != endpoint:
        fail("canonical word reconstruction")
    return {"word": word, "L": length, "Q": q, "B": B, "source": source, "endpoint": endpoint, "safe": safe(word)}


def series_enclosure(value: Fraction, count: int) -> tuple[Fraction, Fraction]:
    if value < 1 or count < 1:
        fail("log enclosure domain")
    z = (value - 1) / (value + 1)
    terms = [z ** (2 * n + 1) / (2 * n + 1) for n in range(count)]
    low = 2 * sum(terms, Fraction())
    first_omitted = z ** (2 * count + 1)
    high = low + 2 * first_omitted / ((2 * count + 1) * (1 - z * z))
    return low, high


def expected_residues(label: str) -> list[int]:
    result = []
    for residue in range(72):
        if residue % 2 == 0 or residue % 3 == 0:
            continue
        if label in {"[N,9N/8)", "[9N/8,3N/2)"} and residue % 3 == 2:
            continue
        if label == "[N,9N/8)" and residue % 9 == 4:
            continue
        if label != "[9N/4,infinity)" and residue % 9 == 8:
            continue
        if label in {"[N,9N/8)", "[9N/8,3N/2)", "[3N/2,2N)"} and residue % 8 == 5:
            continue
        result.append(residue)
    return result


def verify_theory(path: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase16-theory-v1" or data.get("proves_collatz") is not False:
        fail("theory format or proof boundary")
    claims = data.get("claims")
    expected_claims = {
        "P97": "VERIFIED_THEOREM", "P98": "VERIFIED_THEOREM", "P99": "VERIFIED_THEOREM",
        "P100": "VERIFIED_THEOREM", "P101": "VERIFIED_THEOREM", "P102": "VERIFIED_THEOREM",
        "P103": "CONDITIONAL", "NG28": "REFUTED", "H97": "OPEN", "H98": "OPEN"
    }
    if claims != expected_claims:
        fail("theory claim status boundary")

    negative = data.get("negative_carry")
    if not isinstance(negative, dict):
        fail("negative carry missing")
    left, right = canonical(BAD_A), canonical(BAD_D)
    numerator = 2 * int(left["B"]) - int(right["B"])
    carry = numerator // pow(3, 26)
    if numerator % pow(3, 26) or carry != -3:
        fail("internal negative carry reconstruction")
    expected_negative = {
        "claim": "NG28", "status": "REFUTED",
        "hypothesis": "Every shorter safe same-Q predecessor of a safe endpoint has positive carry.",
        "a": left, "d": right, "k": 1, "scaled_B_difference": numerator,
        "carry": -3, "identity": "S_d=2*S_a-3"
    }
    if negative != expected_negative or left["endpoint"] != right["endpoint"]:
        fail("negative carry artifact mismatch")
    carry_bound = data.get("carry_bound")
    if carry_bound != {
        "safe_correction": "B(w)/3^q=1/3 for q=1; 1/3<B(w)/3^q<q/3 for q>=2",
        "same_Q": "m=(2^k B(a)-B(d))/3^q > -q/3 and > (2^k-q)/3",
        "negative_carry_requires": "2^k<q",
        "proposal_repair": "The proposed strict upper bound is false at q=1 (word 1); no distinct-length safe same-Q pair exists there."
    } or Fraction(explicit_constant("1"), 3) != Fraction(1, 3):
        fail("carry theorem or q=1 repair")

    packing = data.get("residue_packing")
    if not isinstance(packing, dict) or packing.get("modulus") != 72:
        fail("residue packing header")
    intervals = packing.get("intervals")
    labels = ["[N,9N/8)", "[9N/8,3N/2)", "[3N/2,2N)", "[2N,9N/4)", "[9N/4,infinity)"]
    if not isinstance(intervals, list) or len(intervals) != len(labels):
        fail("residue interval table")
    counts = []
    for row, label in zip(intervals, labels, strict=True):
        if not isinstance(row, dict):
            fail("residue interval row")
        residues = expected_residues(label)
        counts.append(len(residues))
        if row.get("interval") != label or row.get("residues") != residues or row.get("count") != len(residues) or fraction(row.get("density")) != Fraction(len(residues), 72):
            fail("residue packing reconstruction")
    if counts != [6, 9, 15, 20, 24] or packing.get("periodic_error_sum") != 74 or packing.get("initial_point_plus_errors") != 75:
        fail("residue error constants")
    capacity = Fraction(1, 12) * Fraction(1, 8) + Fraction(1, 8) * Fraction(3, 8) + Fraction(5, 24) * Fraction(1, 2) + Fraction(5, 18) * Fraction(1, 4)
    if capacity != Fraction(133, 576) or fraction(packing.get("continuous_count_below_9N_over_4")) != capacity:
        fail("packing continuous capacity")

    certificate = data.get("log_certificate")
    if not isinstance(certificate, dict):
        fail("log certificate missing")
    terms = certificate.get("terms")
    if not isinstance(terms, int):
        fail("log term count")
    lo2, hi2 = series_enclosure(Fraction(2), terms)
    lo98, hi98 = series_enclosure(Fraction(9, 8), terms)
    ratio = Fraction(144299, 82944)
    lor, hir = series_enclosure(ratio, terms)
    if fraction(certificate.get("log2", {}).get("lower") if isinstance(certificate.get("log2"), dict) else None) != lo2:
        fail("log2 lower enclosure")
    if fraction(certificate.get("log2", {}).get("upper") if isinstance(certificate.get("log2"), dict) else None) != hi2:
        fail("log2 upper enclosure")
    log98 = certificate.get("log9_over_8")
    if not isinstance(log98, dict) or fraction(log98.get("lower")) != lo98 or fraction(log98.get("upper")) != hi98:
        fail("log9/8 enclosure")
    large = certificate.get("reduced_large_ratio")
    if not isinstance(large, dict) or fraction(large.get("ratio")) != ratio or large.get("removed_power_of_two") != 8 or fraction(large.get("lower")) != lor or fraction(large.get("upper")) != hir:
        fail("large log enclosure")
    margin = Fraction(1, 3) * lo2 - Fraction(13, 36) * hi98 - Fraction(1, 3) * hir - Fraction(3, 4000)
    if margin <= 0 or fraction(certificate.get("exact_positive_margin_after_reduction")) != margin:
        fail("exact 250 comparison")

    merges = data.get("local_merges")
    if not isinstance(merges, dict) or merges.get("literal_sample_limit") != 500:
        fail("local merge samples")
    sample_specs = [
        ("mod3_first_samples", "1", lambda x: (2 * x - 1) // 3),
        ("mod9_four_first_samples", "110", lambda x: (8 * x - 5) // 9),
        ("mod9_eight_first_samples", "11", lambda x: (4 * x - 5) // 9)
    ]
    for key, word, source_formula in sample_specs:
        rows = merges.get(key)
        if not isinstance(rows, list) or len(rows) != 8:
            fail("local merge sample count")
        for pair in rows:
            if not isinstance(pair, list) or len(pair) != 2:
                fail("local merge sample row")
            x, source = map(int, pair)
            if source != source_formula(x) or literal_trace(source, word)[-1] != x:
                fail("local merge literal trace")
    oee = merges.get("odd_even_even_first_samples")
    if not isinstance(oee, list) or len(oee) != 8:
        fail("odd-even-even sample count")
    for sample in oee:
        x, source, endpoint = map(int, sample)
        if x % 8 != 5 or source != (x - 1) // 2 or literal_trace(source, "01")[-1] != endpoint or literal_trace(x, "100")[-1] != endpoint:
            fail("odd-even-even literal trace")
    all_odd = merges.get("all_odd_samples")
    if not isinstance(all_odd, list) or [row.get("r") for row in all_odd if isinstance(row, dict)] != list(range(1, 7)):
        fail("all-odd sample rows")
    for sample in all_odd:
        if not isinstance(sample, dict):
            fail("all-odd row")
        r, x, source = int(sample["r"]), int(sample["x"]), int(sample["u"])
        if x % pow(3, r) != pow(3, r) - 1 or source != pow(2, r) * (x + 1) // pow(3, r) - 1 or literal_trace(source, "1" * r)[-1] != x:
            fail("all-odd inverse")

    dichotomy = data.get("dichotomy")
    if not isinstance(dichotomy, dict):
        fail("dichotomy missing")
    hypotheses = dichotomy.get("hypotheses")
    if not isinstance(hypotheses, list) or "odd inputs before crossing are distinct" not in hypotheses:
        fail("nonperiodic scope boundary")
    if dichotomy.get("periodic_boundary") != "Without distinctness only q<3N gives all-prefix geodesic; otherwise N<=q/3 and X<2q/3.":
        fail("periodic scope boundary")
    q0 = dichotomy.get("q0_consequence")
    if not isinstance(q0, dict) or q0.get("status") != "CONDITIONAL" or q0.get("q0_less_than_three_times_bound") is not True:
        fail("q0 conditional boundary")
    if int(q0.get("q0", 0)) >= 3 * 2075 * pow(2, 60):
        fail("q0 exact comparison")
    return {"log_margin": [margin.numerator, margin.denominator], "residue_counts": counts, "negative_carry": carry}


def enumerate_safe_strings(maximum_q: int) -> dict[int, list[str]]:
    groups = {q: [] for q in range(1, maximum_q + 1)}
    frontier = [("", 0)]
    last_length = pow(3, maximum_q).bit_length() - 1
    for length in range(1, last_length + 1):
        following = []
        for prefix, q in reversed(frontier):
            one = prefix + "1"
            if q < maximum_q and pow(3, q + 1) > pow(2, length):
                groups[q + 1].append(one)
                following.append((one, q + 1))
            zero = prefix + "0"
            if q > 0 and pow(3, q) > pow(2, length):
                groups[q].append(zero)
                following.append((zero, q))
        frontier = following
    return groups


def endpoint(word: str) -> int:
    q = word.count("1")
    modulus = pow(3, q)
    value = explicit_constant(word) * pow(pow(2, len(word)), -1, modulus) % modulus
    return value or modulus


def source(word: str) -> int:
    modulus = pow(2, len(word))
    q = word.count("1")
    value = -explicit_constant(word) * pow(pow(3, q), -1, modulus) % modulus
    return value or modulus


def contacts(word: str) -> int:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    return sum(position == pow(3, j).bit_length() - 1 for j, position in enumerate(positions))


def all_prefix_geodesic(word: str, minima: dict[tuple[int, int], int]) -> bool:
    for length in range(1, len(word) + 1):
        prefix = word[:length]
        if minima[(prefix.count("1"), endpoint(prefix))] < length:
            return False
    return True


def expected_finite(maximum_q: int) -> dict[str, object]:
    groups = enumerate_safe_strings(maximum_q)
    minima = {}
    for q, words in groups.items():
        for word in words:
            key = (q, endpoint(word))
            minima[key] = min(minima.get(key, len(word)), len(word))
    digest = hashlib.sha256()
    counts_by_q = {}
    pairs = negatives = 0
    minimum_carry = None
    for q in range(1, maximum_q + 1):
        cylinders: dict[int, list[str]] = defaultdict(list)
        for word in groups[q]:
            cylinders[endpoint(word)].append(word)
        for words in cylinders.values():
            ordered = sorted(words, key=lambda word: (len(word), word))
            for index, a in enumerate(ordered):
                for d in ordered[index + 1:]:
                    k = len(d) - len(a)
                    if k <= 0:
                        continue
                    numerator = pow(2, k) * explicit_constant(a) - explicit_constant(d)
                    if numerator % pow(3, q):
                        fail("finite carry divisibility")
                    carry = numerator // pow(3, q)
                    if not (3 * carry > -q and 3 * carry > pow(2, k) - q):
                        fail("finite carry bound")
                    pairs += 1
                    negatives += carry < 0
                    minimum_carry = carry if minimum_carry is None else min(minimum_carry, carry)
        critical_length = pow(3, q).bit_length() - 1
        critical = sorted(word for word in groups[q] if len(word) == critical_length)
        geodesic = prefix_count = rich = rich_geodesic = maximum_contacts = 0
        source_values = [(source(word), word, endpoint(word)) for word in critical]
        endpoint_values = [(endpoint(word), word, source(word)) for word in critical]
        for word in critical:
            r3, r2 = endpoint(word), source(word)
            geo = minima[(q, r3)] == len(word)
            prefix_geo = all_prefix_geodesic(word, minima)
            count = contacts(word)
            contact_rich = 100 * count > 43 * q
            geodesic += geo
            prefix_count += prefix_geo
            rich += contact_rich
            rich_geodesic += contact_rich and geo
            maximum_contacts = max(maximum_contacts, count)
            digest.update(f"{q}|{word}|{r2}|{r3}|{int(geo)}|{int(prefix_geo)}|{count}\n".encode("ascii"))
        if geodesic != prefix_count:
            fail("finite prefix closure")
        min_source, source_word, source_endpoint = min(source_values)
        min_endpoint, endpoint_word, endpoint_source = min(endpoint_values)
        counts_by_q[str(q)] = {
            "safe_words_all_lengths": len(groups[q]), "critical_words": len(critical),
            "same_Q_geodesic": geodesic, "all_prefix_same_Q_geodesic": prefix_count,
            "contact_rich": rich, "contact_rich_geodesic": rich_geodesic,
            "maximum_contacts": maximum_contacts,
            "minimum_source": {"value": min_source, "word": source_word, "endpoint": source_endpoint},
            "minimum_endpoint": {"value": min_endpoint, "word": endpoint_word, "source": endpoint_source}
        }
    return {
        "format": "collatz-phase16-finite-layers-v1", "maximum_Q": maximum_q,
        "critical_definition": "safe word with Q=q and L=floor(log2(3^q)); appending one zero is the coefficient first crossing",
        "contact_definition": "odd position d_j is a contact iff d_j=floor(log2(3^j)); contact-rich means 100*contacts>43*Q",
        "counts_by_Q": counts_by_q, "same_Q_endpoint_pair_count": pairs,
        "negative_carry_pair_count_in_cutoff": negatives, "minimum_carry_in_cutoff": minimum_carry,
        "critical_row_digest_sha256": digest.hexdigest(),
        "finite_boundary": "Complete through Q<=maximum_Q only; no eventual geodesic or contact theorem follows.",
        "proves_collatz": False
    }


def verify_finite(path: Path) -> dict[str, object]:
    data = load(path)
    maximum_q = data.get("maximum_Q")
    if not isinstance(maximum_q, int) or maximum_q < 1 or maximum_q > 20:
        fail("finite maximum Q")
    expected = expected_finite(maximum_q)
    if data != expected:
        fail("finite layer reconstruction mismatch")
    last = expected["counts_by_Q"][str(maximum_q)]
    return {"maximum_Q": maximum_q, "critical_words_at_maximum_Q": last["critical_words"], "geodesic_at_maximum_Q": last["same_Q_geodesic"]}


def prefix_length(word: str) -> int:
    q = 0
    for length, bit in enumerate(word, 1):
        q += bit == "1"
        if pow(3, q) <= pow(2, length):
            return length - 1
    return len(word)


def parity_word(value: int, length: int) -> str:
    bits = []
    for _ in range(length):
        bits.append(str(value % 2))
        value = step(value)
    return "".join(bits)


def expected_adversarial() -> dict[str, object]:
    inputs = []
    for m in range(2, 9):
        inputs.append((f"2^{m}-1", parity_word(pow(2, m) - 1, 32)))
        inputs.append((f"8^{m}-5", parity_word(pow(8, m) - 5, 32)))
    for size in range(1, 5):
        for selection in product(("110", "111"), repeat=size):
            word = "".join(selection)
            inputs.append((f"(110|111)^*:{word}", word))
    inputs.extend([("A=11101", WORD_A), ("B=1100", WORD_B), ("W=AB", WORD_A + WORD_B)])
    for r in range(1, 5):
        for s in range(1, 5):
            inputs.append((f"A^{r}B^{s}", WORD_A * r + WORD_B * s))
    inputs.extend([("Phase7-all-contact-prefix", "1" * 12 + "0" * 7), ("NG27-d", GAIN_D), ("NG27-a", GAIN_A), ("NG28-a", BAD_A), ("NG28-d", BAD_D)])
    rows = []
    digest = hashlib.sha256()
    for name, word in inputs:
        B = explicit_constant(word)
        safe_length = prefix_length(word)
        rows.append({"name": name, "word": word, "L": len(word), "Q": word.count("1"), "B": B, "safe_prefix_length": safe_length, "whole_word_safe": safe_length == len(word)})
        digest.update(f"{name}|{word}|{B}|{safe_length}\n".encode("ascii"))
    return {
        "format": "collatz-phase16-adversarial-v1",
        "families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s", "Phase 7 all-contact prefixes", "NG27", "NG28"],
        "rows": rows, "row_digest_sha256": digest.hexdigest(),
        "interpretation": "These bounded rows are regression tests for conventions and theorem hypotheses, not evidence of asymptotic exclusion.",
        "proves_collatz": False
    }


def verify_adversarial(path: Path) -> int:
    data = load(path)
    expected = expected_adversarial()
    if data != expected:
        fail("adversarial reconstruction mismatch")
    return len(expected["rows"])


def verify_report(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"obstruction report missing: {exc}")
    required = [
        "NG28 — positive same-Q carry", "`REFUTED`", "## G250", "`OPEN`",
        "## H250", "## Periodic branch", "Without distinctness",
        "## What this result does not prove", "`proves_collatz=false`"
    ]
    if any(token not in text for token in required) or "proves the Collatz conjecture" in text:
        fail("obstruction report boundary")


def verify(artifact_dir: Path) -> dict[str, object]:
    theory = verify_theory(artifact_dir / "phase16_theory.json")
    finite = verify_finite(artifact_dir / "phase16_finite_layers.json")
    adversarial = verify_adversarial(artifact_dir / "phase16_adversarial.json")
    verify_report(artifact_dir / "phase16_obstruction_report.md")
    return {
        "format": "collatz-phase16-verifier-v1", "valid": True,
        "claims": {"P97": "VERIFIED_THEOREM", "P98": "VERIFIED_THEOREM", "P99": "VERIFIED_THEOREM", "P100": "VERIFIED_THEOREM", "P101": "VERIFIED_THEOREM", "P102": "VERIFIED_THEOREM", "P103": "CONDITIONAL", "E27": "VERIFIED_FINITE", "NG28": "REFUTED", "H97": "OPEN", "H98": "OPEN"},
        "theory": theory, "finite": finite, "adversarial_rows": adversarial,
        "independence": "literal-string enumeration and explicit odd-position affine sums; no generator import",
        "proves_collatz": False
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        return 1
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
