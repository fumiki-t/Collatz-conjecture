#!/usr/bin/env python3
"""Independent exact verifier for Phase 19 affine/source-lift evidence."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


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


def frac(value: object) -> Fraction:
    if not isinstance(value, dict):
        fail("fraction object missing")
    try:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        fail(f"invalid fraction: {exc}")


def encoded(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def object_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def explicit_constant(word: str) -> int:
    if not word or set(word) - {"0", "1"}:
        fail("invalid binary word")
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    q = len(positions)
    return sum(pow(3, q - 1 - rank) * pow(2, position) for rank, position in enumerate(positions))


def canonical_data(word: str) -> tuple[int, int, int, int]:
    affine, q, length = explicit_constant(word), word.count("1"), len(word)
    modulus, three = pow(2, length), pow(3, q)
    source = (-affine * pow(three, -1, modulus)) % modulus or modulus
    return affine, source, (three * source + affine) // modulus, q


def exponent_record(exponents: tuple[int, ...]) -> dict[str, object]:
    n = len(exponents)
    # Deliberately reconstruct A with the closed sum rather than recurrence.
    prefix_sums = [0]
    for exponent in exponents:
        prefix_sums.append(prefix_sums[-1] + exponent)
    affine = sum(pow(3, n - 1 - index) * pow(2, prefix_sums[index]) for index in range(n))
    coefficients = [Fraction(1)] + [Fraction(pow(3, index), pow(2, prefix_sums[index])) for index in range(1, n + 1)]
    minimum = min(coefficients)
    last = max(index for index, value in enumerate(coefficients) if value == minimum)
    return {
        "exponents": list(exponents), "n": n, "E": prefix_sums[-1], "A": affine,
        "coefficient": encoded(coefficients[-1]),
        "normalized_beta": encoded(Fraction(affine, pow(3, n))),
        "minimum_prefix_coefficient": encoded(minimum), "last_minimum_index": last,
        "valley_suffix_coefficient": encoded(coefficients[-1] / minimum),
    }


def expected_valley(maximum_n: int, maximum_e: int) -> dict[str, object]:
    rows = []
    counts: Counter[str] = Counter()
    for n in range(maximum_n, 0, -1):
        for exponents in itertools.product(range(maximum_e, 0, -1), repeat=n):
            data = exponent_record(exponents)
            total, affine = int(data["E"]), int(data["A"])
            modulus, three = pow(2, total), pow(3, n)
            source = (-affine * pow(three, -1, modulus)) % modulus or modulus
            endpoint = (three * source + affine) // modulus
            if endpoint < source + 1:
                continue
            N, u, c = source + 1, Fraction(endpoint, source + 1), Fraction(three, modulus)
            suffix = frac(data["valley_suffix_coefficient"])
            alternative = "safe_valley" if suffix > u else "affine_length"
            if alternative == "affine_length" and not n > 3 * N * (1 - c / u):
                fail("affine-or-valley finite inequality")
            counts[alternative] += 1
            rows.append({
                "exponents": list(exponents), "source": source, "N": N,
                "endpoint": endpoint, "u": encoded(u), "coefficient": encoded(c),
                "valley_suffix_coefficient": encoded(suffix), "alternative": alternative,
            })
    rows.sort(key=lambda row: (row["exponents"], row["source"]))
    return {
        "maximum_n": maximum_n, "maximum_exponent": maximum_e,
        "eligible_rows": len(rows), "alternative_counts": dict(sorted(counts.items())),
        "row_digest_sha256": object_digest(rows),
        "row_storage": "omitted; verifier reconstructs the complete declared product range",
    }


def verify_theory(root: Path) -> None:
    value = load(root / "phase19_theory.json")
    claims = {
        "P112": "VERIFIED_THEOREM", "P113": "VERIFIED_THEOREM",
        "P114": "VERIFIED_THEOREM", "P115": "VERIFIED_THEOREM",
        "P116": "VERIFIED_THEOREM", "NG31": "REFUTED",
        "H112": "OPEN", "H72": "OPEN",
    }
    if value.get("claims") != claims or value.get("proves_collatz") is not False:
        fail("theory claim boundary")
    finite = value.get("P112", {}).get("finite_audit", {})
    if finite != expected_valley(int(finite.get("maximum_n", 0)), int(finite.get("maximum_exponent", 0))):
        fail("affine-or-valley finite audit")
    if "T_t cap R" not in str(value.get("P113", {}).get("bounded_stopping", "")):
        fail("bounded stopping boundary")
    if "infinity" not in str(value.get("NG31", {}).get("countertheorem", "")):
        fail("critical affine mean")
    if "without EXT07" not in str(value.get("P114", {}).get("phase18_strengthening", "")):
        fail("P72 occupation strengthening")
    if "divisibility, not exactness" not in str(value.get("P115", {}).get("valuation_boundary", "")):
        fail("source lift valuation boundary")
    if "all-zero" not in str(value.get("P116", {}).get("scope_repair", "")):
        fail("periodic zero scope")
    if value.get("H112", {}).get("status") != "OPEN":
        fail("H112 open boundary")


class Totals:
    def __init__(self) -> None:
        self.plus_beta = Fraction()
        self.minus_tau = Fraction()
        self.plus_mass = Fraction()
        self.minus_mass = Fraction()
        self.hit_plus = Fraction()
        self.hit_minus = Fraction()
        self.leaves = 0
        self.tails = 0
        self.nodes = 0
        self.rows: list[list[object]] = []


def expected_stopped(depth: int, threshold: Fraction) -> dict[str, object]:
    totals = Totals()
    stack = [((), 0, 0, Fraction(), Fraction(1), Fraction(1))]
    while stack:
        exponents, odd, total, beta, p_plus, p_minus = stack.pop()
        coefficient = Fraction(pow(3, odd), pow(2, total))
        if odd and coefficient >= threshold:
            totals.plus_beta += p_plus * beta
            totals.minus_tau += p_minus * odd
            totals.plus_mass += p_plus
            totals.minus_mass += p_minus
            totals.hit_plus += p_plus
            totals.hit_minus += p_minus
            totals.leaves += 1
            totals.rows.append([list(exponents), "hit", encoded(p_plus), encoded(p_minus), encoded(beta), odd])
            continue
        if odd == depth:
            totals.plus_beta += p_plus * beta
            totals.minus_tau += p_minus * depth
            totals.plus_mass += p_plus
            totals.minus_mass += p_minus
            totals.leaves += 1
            totals.rows.append([list(exponents), "horizon", encoded(p_plus), encoded(p_minus), encoded(beta), depth])
            continue
        totals.nodes += 1
        remaining = depth - odd - 1
        first_dead = 1
        while coefficient * Fraction(3, pow(2, first_dead)) * Fraction(pow(3, remaining), pow(2, remaining)) >= threshold:
            first_dead += 1
        plus_tail = Fraction(1, pow(4, first_dead - 1))
        minus_tail = Fraction(1, pow(2, first_dead - 1))
        child_beta = beta + Fraction(1, 3) / coefficient
        inverse_tail = Fraction(1, coefficient) * Fraction(1, pow(2, first_dead - 1))
        totals.plus_beta += p_plus * (plus_tail * child_beta + Fraction(remaining, 3) * inverse_tail)
        totals.minus_tau += p_minus * minus_tail * depth
        totals.plus_mass += p_plus * plus_tail
        totals.minus_mass += p_minus * minus_tail
        totals.tails += 1
        totals.rows.append([list(exponents), f"tail_e>={first_dead}", encoded(p_plus * plus_tail), encoded(p_minus * minus_tail), depth])
        # Push in ascending order so the LIFO traversal itself is reversed.
        for exponent in range(1, first_dead):
            stack.append((
                exponents + (exponent,), odd + 1, total + exponent, child_beta,
                p_plus * Fraction(3, pow(4, exponent)), p_minus * Fraction(1, pow(2, exponent)),
            ))
    rows = sorted(totals.rows, key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")))
    if totals.plus_beta * 3 != totals.minus_tau or totals.plus_mass != 1 or totals.minus_mass != 1:
        fail("stopped exact identity")
    return {
        "depth": depth, "threshold": encoded(threshold),
        "E_plus_beta_T_cap_R": encoded(totals.plus_beta), "E_minus_T_cap_R": encoded(totals.minus_tau),
        "duality": "E_plus_beta=(1/3)E_minus_tau",
        "plus_total_mass": encoded(totals.plus_mass), "minus_total_mass": encoded(totals.minus_mass),
        "hit_plus_mass": encoded(totals.hit_plus), "hit_minus_mass": encoded(totals.hit_minus),
        "ordinary_leaves": totals.leaves, "collapsed_geometric_tails": totals.tails,
        "active_nodes": totals.nodes, "leaf_digest_sha256": object_digest(rows),
    }


def verify_stopped(root: Path) -> None:
    value = load(root / "phase19_stopped_duality.json")
    maximum = value.get("maximum_depth")
    threshold = frac(value.get("threshold"))
    if maximum != 12 or threshold != 2:
        fail("stopped bounds")
    expected = [expected_stopped(depth, threshold) for depth in range(1, maximum + 1)]
    if value.get("rows") != expected:
        fail("stopped tree reconstruction")
    if value.get("claim") != {"P113": "VERIFIED_THEOREM", "E31": "VERIFIED_FINITE", "NG31": "REFUTED"}:
        fail("stopped claims")
    if "not extrapolated" not in str(value.get("infinite_tree_boundary", "")) or value.get("proves_collatz") is not False:
        fail("stopped finite boundary")


def enumerate_safe_strings(maximum_q: int) -> dict[int, list[str]]:
    groups = {q: [] for q in range(1, maximum_q + 1)}
    frontier = [""]
    maximum_length = pow(3, maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        following = []
        for prefix in reversed(frontier):
            q = prefix.count("1")
            zero = prefix + "0"
            if q and pow(3, q) > pow(2, length):
                groups[q].append(zero)
                following.append(zero)
            one = prefix + "1"
            if q < maximum_q and pow(3, q + 1) > pow(2, length):
                groups[q + 1].append(one)
                following.append(one)
        frontier = following
    return groups


def endpoint(word: str) -> int:
    q, length, affine = word.count("1"), len(word), explicit_constant(word)
    modulus = pow(3, q)
    return (affine * pow(pow(2, length), -1, modulus)) % modulus or modulus


def source(word: str) -> int:
    q, length, affine = word.count("1"), len(word), explicit_constant(word)
    modulus = pow(2, length)
    return (-affine * pow(pow(3, q), -1, modulus)) % modulus or modulus


def exponent_parts(word: str) -> list[int]:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    ends = positions[1:] + [len(word)]
    return [end - start for start, end in zip(positions, ends)]


def lift_data(word: str) -> dict[str, object]:
    exponents = exponent_parts(word)
    residues, lifts = [], []
    old, old_modulus, length = 0, 1, 0
    for exponent in exponents:
        length += exponent
        residue = source(word[:length])
        lift = (residue - old) // old_modulus
        if not 0 <= lift < pow(2, exponent):
            fail("source lift range")
        residues.append(residue)
        lifts.append(lift)
        old, old_modulus = residue, pow(2, length)
    trailing = 0
    for lift in reversed(lifts):
        if lift:
            break
        trailing += 1
    return {"exponents": exponents, "residues": residues, "lifts": lifts, "trailing_zero_lifts": trailing}


def step(value: int) -> int:
    return (3 * value + 1) // 2 if value % 2 else value // 2


def crossing(source_value: int, word: str) -> dict[str, object]:
    value, q, length = source_value, 0, 0
    for bit in word:
        if str(value % 2) != bit:
            fail("source 167 parity prefix")
        q += value % 2
        length += 1
        value = step(value)
    continuation = []
    for distance in range(1, 257):
        bit = value % 2
        continuation.append(str(bit))
        q += bit
        length += 1
        value = step(value)
        if pow(3, q) <= pow(2, length):
            return {"distance": distance, "continuation": "".join(continuation), "crossing_L": length, "crossing_Q": q, "value_after_crossing": value}
    return {"distance": None, "continuation": "".join(continuation), "limit": 256}


def expected_source_lifts(maximum_q: int) -> dict[str, object]:
    groups = enumerate_safe_strings(maximum_q)
    minima: dict[tuple[int, int], int] = {}
    for q, words in groups.items():
        for word in words:
            key = (q, endpoint(word))
            minima[key] = min(minima.get(key, len(word)), len(word))
    counts = {}
    rows = []
    witness = None
    for q in range(maximum_q, 0, -1):
        critical_length = pow(3, q).bit_length() - 1
        critical = [word for word in groups[q] if len(word) == critical_length]
        geodesic = sorted((word for word in critical if minima[(q, endpoint(word))] == len(word)), reverse=True)
        distribution: Counter[int] = Counter()
        maximum = -1
        least = None
        for word in geodesic:
            r2, r3 = source(word), endpoint(word)
            lifts = lift_data(word)
            trailing = int(lifts["trailing_zero_lifts"])
            distribution[trailing] += 1
            rows.append([q, word, r2, r3, lifts["exponents"], lifts["lifts"], trailing])
            candidate = [r2, word, r3]
            if trailing > maximum or (trailing == maximum and (least is None or candidate[0] < least[0])):
                maximum, least = trailing, candidate
            if q == 17 and r2 == 167:
                witness = {"Q": q, "word": word, "source": r2, "endpoint": r3, **lifts, "coefficient_crossing_after_prefix": crossing(r2, word)}
        counts[str(q)] = {
            "critical_words": len(critical), "geodesic_words": len(geodesic),
            "maximum_trailing_zero_lifts": maximum,
            "least_source_at_maximum": {"source": least[0], "word": least[1], "endpoint": least[2]},
            "trailing_zero_distribution": {str(key): value for key, value in sorted(distribution.items())},
        }
    rows.sort(key=lambda row: (row[0], row[1]))
    return {
        "format": "collatz-phase19-source-lifts-v1",
        "claim": {"P115": "VERIFIED_THEOREM", "E31": "VERIFIED_FINITE", "H112": "OPEN"},
        "maximum_Q": maximum_q, "counts_by_Q": counts,
        "row_digest_sha256": object_digest(rows),
        "row_storage": "omitted; verifier rebuilds every geodesic critical row",
        "source_167_falsifier": witness,
        "finite_boundary": "A long zero-lift suffix is not eventual stabilization. Source 167 crosses coefficient safety three shortcut steps after the stored Q=17 prefix.",
        "proves_collatz": False,
    }


def verify_source_lifts(root: Path) -> None:
    value = load(root / "phase19_source_lifts.json")
    maximum = value.get("maximum_Q")
    if maximum != 17:
        fail("source lift Q bound")
    if value != expected_source_lifts(maximum):
        fail("source lift reconstruction")


def periodic_record(word: str, repetitions: int) -> dict[str, object]:
    length, q, affine = len(word), word.count("1"), explicit_constant(word)
    if q == 0:
        fail("periodic odd-step scope")
    xi = Fraction(affine, pow(2, length) - pow(3, q))
    a, d = xi.numerator, xi.denominator
    positive = xi.denominator == 1 and xi >= 1
    threshold = max(1, (2 * abs(a) - 1).bit_length()) if a else 1
    loss = 1 + (d - 1).bit_length()
    rows = []
    for count in range(repetitions, 0, -1):
        bits, modulus = count * length, pow(2, count * length)
        residue = (a * pow(d, -1, modulus)) % modulus or modulus
        applies = not positive and bits >= threshold
        if applies and residue < pow(2, max(0, bits - loss)):
            fail("periodic exact lower bound")
        rows.append({"repetitions": count, "bits": bits, "source_residue": residue, "bound_applies": applies})
    rows.reverse()
    return {
        "word": word, "L": length, "q": q, "B": affine,
        "fixed_2adic_source": encoded(xi), "positive_integer_cycle_candidate": positive,
        "effective_threshold_bits": threshold, "effective_loss_bits": loss, "residues": rows,
    }


def verify_periodic(root: Path) -> None:
    value = load(root / "phase19_periodic_lifts.json")
    repetitions = value.get("repetitions")
    words = ["1", "10", "110", "111", "11101", "1100", "111011100", "110111"]
    rows = [periodic_record(word, repetitions) for word in words]
    if value.get("rows") != rows or value.get("row_digest_sha256") != object_digest(rows):
        fail("periodic lift reconstruction")
    if "all-zero" not in str(value.get("scope_repair", "")) or value.get("proves_collatz") is not False:
        fail("periodic scope boundary")


def parity_prefix(value: int, length: int) -> str:
    bits = []
    for _ in range(length):
        bits.append(str(value % 2))
        value = step(value)
    return "".join(bits)


def expected_adversarial() -> dict[str, object]:
    inputs = []
    for m in range(2, 9):
        inputs.extend([(f"2^{m}-1", parity_prefix(pow(2, m) - 1, 32)), (f"8^{m}-5", parity_prefix(pow(8, m) - 5, 32))])
    for size in range(1, 5):
        for selection in itertools.product(("110", "111"), repeat=size):
            word = "".join(selection)
            inputs.append((f"(110|111)^*:{word}", word))
    inputs.extend([("A=11101", "11101"), ("B=1100", "1100"), ("AB", "111011100")])
    for r in range(1, 5):
        for s in range(1, 5):
            inputs.append((f"A^{r}B^{s}", "11101" * r + "1100" * s))
    rows = []
    for name, word in inputs:
        affine, r2, r3, q = canonical_data(word)
        rows.append({
            "name": name, "word": word, "L": len(word), "Q": q, "B": affine,
            "source": r2, "endpoint": r3,
            "coefficient": encoded(Fraction(pow(3, q), pow(2, len(word)))),
            "normalized_beta": encoded(Fraction(affine, pow(3, q))),
        })
    return {
        "format": "collatz-phase19-adversarial-v1", "claim": {"E31": "VERIFIED_FINITE"},
        "families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s", "source 167", "NG19", "NG22", "NG23", "NG28", "NG29", "NG30"],
        "rows": rows, "row_digest_sha256": object_digest(rows),
        "preserved_boundaries": {
            "source 167": "eleven trailing zero exponent lifts followed by coefficient crossing; finite zeros are not eventual",
            "NG19": "lossy finite tail state cannot decide joint safety",
            "NG22": "coherent 2-adic source plus analytic conditions need not be a positive integer",
            "NG23": "Haar mass does not count canonical ordinary representatives",
            "NG28": "same-Q carry may be negative", "NG29": "coefficient-only summed-Haar pressure has a finite ceiling",
            "NG30": "sign-pure SCC packets need not have one positive-to-negative switch",
        },
        "finite_boundary": "These exact rows test conventions and old falsifiers; they imply no eventual lift theorem.",
        "proves_collatz": False,
    }


def verify_adversarial(root: Path) -> None:
    if load(root / "phase19_adversarial.json") != expected_adversarial():
        fail("adversarial reconstruction")


def verify_report(root: Path) -> None:
    try:
        text = (root / "phase19_obstruction_report.md").read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"obstruction report: {exc}")
    required = ["NG31", "(`REFUTED`)", "H112", "(`OPEN`)", "source-167", "all-zero", "`proves_collatz=false`"]
    if any(token not in text for token in required) or "NG31 — average-small affine correction (`VERIFIED_THEOREM`)" in text:
        fail("obstruction report boundary")


def verify(artifact_dir: Path) -> dict[str, object]:
    verify_theory(artifact_dir)
    verify_stopped(artifact_dir)
    verify_source_lifts(artifact_dir)
    verify_periodic(artifact_dir)
    verify_adversarial(artifact_dir)
    verify_report(artifact_dir)
    return {
        "format": "collatz-phase19-verifier-v1", "valid": True,
        "claims": {
            "P112": "VERIFIED_THEOREM", "P113": "VERIFIED_THEOREM",
            "P114": "VERIFIED_THEOREM", "P115": "VERIFIED_THEOREM",
            "P116": "VERIFIED_THEOREM", "E31": "VERIFIED_FINITE",
            "NG31": "REFUTED", "H112": "OPEN", "H72": "OPEN",
        },
        "independence": {
            "generator_imported": False, "affine_method": "explicit exponent-position sum",
            "tree_order": "iterative reverse traversal with independently aggregated geometric tails",
            "safe_word_method": "string recursion", "periodic_method": "reduced rational congruence",
        },
        "stopped_depth_recomputed": 12, "maximum_Q_recomputed": 17,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        return 1
    if args.write_report:
        args.write_report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
