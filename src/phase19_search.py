#!/usr/bin/env python3
"""Generate exact Phase 19 affine-valley and source-lift evidence."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def enc(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def translation(word: str) -> int:
    if not word or set(word) - {"0", "1"}:
        raise ValueError("nonempty binary word required")
    affine = 0
    for index, bit in enumerate(word):
        if bit == "1":
            affine = 3 * affine + (1 << index)
    return affine


def canonical(word: str) -> tuple[int, int, int, int]:
    length, odd = len(word), word.count("1")
    affine = translation(word)
    modulus, three = 1 << length, 3**odd
    source = (-affine * pow(three, -1, modulus)) % modulus or modulus
    endpoint = (three * source + affine) // modulus
    return affine, source, endpoint, odd


def exponent_affine(exponents: tuple[int, ...]) -> dict[str, object]:
    if not exponents or min(exponents) < 1:
        raise ValueError("positive exponent word required")
    affine = total = 0
    beta_sum = Fraction()
    coefficients = [Fraction(1)]
    for index, exponent in enumerate(exponents):
        beta_sum += Fraction(1 << total, 3 ** (index + 1))
        affine = 3 * affine + (1 << total)
        total += exponent
        coefficients.append(Fraction(3 ** (index + 1), 1 << total))
    beta = Fraction(affine, 3 ** len(exponents))
    if beta != beta_sum:
        raise AssertionError("accelerated beta identity")
    minimum = min(coefficients)
    last_minimum = max(index for index, value in enumerate(coefficients) if value == minimum)
    suffix = coefficients[-1] / minimum
    return {
        "exponents": list(exponents), "n": len(exponents), "E": total,
        "A": affine, "coefficient": enc(coefficients[-1]),
        "normalized_beta": enc(beta), "minimum_prefix_coefficient": enc(minimum),
        "last_minimum_index": last_minimum, "valley_suffix_coefficient": enc(suffix),
    }


def affine_valley_finite(maximum_n: int = 6, maximum_e: int = 4) -> dict[str, object]:
    rows = []
    alternatives: Counter[str] = Counter()
    for n in range(1, maximum_n + 1):
        for exponents in itertools.product(range(1, maximum_e + 1), repeat=n):
            data = exponent_affine(exponents)
            total, odd, affine = int(data["E"]), n, int(data["A"])
            modulus, three = 1 << total, 3**odd
            source = (-affine * pow(three, -1, modulus)) % modulus or modulus
            endpoint = (three * source + affine) // modulus
            if endpoint < source + 1:
                continue
            N = source + 1
            u = Fraction(endpoint, N)
            c = Fraction(three, modulus)
            suffix = Fraction(
                int(data["valley_suffix_coefficient"]["numerator"]),
                int(data["valley_suffix_coefficient"]["denominator"]),
            )
            if suffix > u:
                alternative = "safe_valley"
            else:
                alternative = "affine_length"
                if not n > 3 * N * (1 - c / u):
                    raise AssertionError("affine-or-valley inequality")
            alternatives[alternative] += 1
            rows.append({
                "exponents": list(exponents), "source": source, "N": N,
                "endpoint": endpoint, "u": enc(u), "coefficient": enc(c),
                "valley_suffix_coefficient": enc(suffix), "alternative": alternative,
            })
    return {
        "maximum_n": maximum_n, "maximum_exponent": maximum_e,
        "eligible_rows": len(rows), "alternative_counts": dict(sorted(alternatives.items())),
        "row_digest_sha256": digest(sorted(rows, key=lambda row: (row["exponents"], row["source"]))),
        "row_storage": "omitted; verifier reconstructs the complete declared product range",
    }


@dataclass(slots=True)
class StoppedTotals:
    plus_beta: Fraction = Fraction()
    minus_tau: Fraction = Fraction()
    plus_mass: Fraction = Fraction()
    minus_mass: Fraction = Fraction()
    hit_plus_mass: Fraction = Fraction()
    hit_minus_mass: Fraction = Fraction()
    ordinary_leaves: int = 0
    collapsed_tails: int = 0
    active_nodes: int = 0


def stopped_tree(depth: int, threshold: Fraction = Fraction(2)) -> dict[str, object]:
    totals = StoppedTotals()
    leaf_rows = []

    def add_leaf(exponents: tuple[int, ...], beta: Fraction, p_plus: Fraction, p_minus: Fraction, hit: bool) -> None:
        tau = len(exponents) if hit else depth
        totals.plus_beta += p_plus * beta
        totals.minus_tau += p_minus * tau
        totals.plus_mass += p_plus
        totals.minus_mass += p_minus
        totals.hit_plus_mass += p_plus * hit
        totals.hit_minus_mass += p_minus * hit
        totals.ordinary_leaves += 1
        leaf_rows.append([list(exponents), "hit" if hit else "horizon", enc(p_plus), enc(p_minus), enc(beta), tau])

    def walk(exponents: tuple[int, ...], odd: int, total: int, beta: Fraction, p_plus: Fraction, p_minus: Fraction) -> None:
        coefficient = Fraction(3**odd, 1 << total)
        if odd and coefficient >= threshold:
            add_leaf(exponents, beta, p_plus, p_minus, True)
            return
        if odd == depth:
            add_leaf(exponents, beta, p_plus, p_minus, False)
            return
        totals.active_nodes += 1
        remaining_after_child = depth - odd - 1
        exponent = 1
        while True:
            child_c = coefficient * Fraction(3, 1 << exponent)
            maximum_future = child_c * Fraction(3**remaining_after_child, 2**remaining_after_child)
            if maximum_future < threshold:
                break
            child_beta = beta + Fraction(1, 3) / coefficient
            walk(
                exponents + (exponent,), odd + 1, total + exponent, child_beta,
                p_plus * Fraction(3, 4**exponent), p_minus * Fraction(1, 2**exponent),
            )
            exponent += 1
        # Every exponent e>=exponent is unable to hit before the horizon.
        plus_tail = Fraction(1, 4 ** (exponent - 1))
        minus_tail = Fraction(1, 2 ** (exponent - 1))
        child_beta = beta + Fraction(1, 3) / coefficient
        future = remaining_after_child
        inverse_child_tail = Fraction(1, coefficient) * Fraction(1, 2 ** (exponent - 1))
        totals.plus_beta += p_plus * (plus_tail * child_beta + Fraction(future, 3) * inverse_child_tail)
        totals.minus_tau += p_minus * minus_tail * depth
        totals.plus_mass += p_plus * plus_tail
        totals.minus_mass += p_minus * minus_tail
        totals.collapsed_tails += 1
        leaf_rows.append([list(exponents), f"tail_e>={exponent}", enc(p_plus * plus_tail), enc(p_minus * minus_tail), depth])

    walk((), 0, 0, Fraction(), Fraction(1), Fraction(1))
    if totals.plus_mass != 1 or totals.minus_mass != 1:
        raise AssertionError("stopped tree total mass")
    if totals.plus_beta * 3 != totals.minus_tau:
        raise AssertionError("stopped duality")
    return {
        "depth": depth, "threshold": enc(threshold),
        "E_plus_beta_T_cap_R": enc(totals.plus_beta),
        "E_minus_T_cap_R": enc(totals.minus_tau),
        "duality": "E_plus_beta=(1/3)E_minus_tau",
        "plus_total_mass": enc(totals.plus_mass), "minus_total_mass": enc(totals.minus_mass),
        "hit_plus_mass": enc(totals.hit_plus_mass), "hit_minus_mass": enc(totals.hit_minus_mass),
        "ordinary_leaves": totals.ordinary_leaves, "collapsed_geometric_tails": totals.collapsed_tails,
        "active_nodes": totals.active_nodes,
        "leaf_digest_sha256": digest(sorted(leaf_rows, key=lambda row: json.dumps(row, sort_keys=True, separators=(",", ":")))),
    }


def stopped_artifact(maximum_depth: int = 12) -> dict[str, object]:
    rows = [stopped_tree(depth) for depth in range(1, maximum_depth + 1)]
    return {
        "format": "collatz-phase19-stopped-duality-v1",
        "claim": {"P113": "VERIFIED_THEOREM", "E31": "VERIFIED_FINITE", "NG31": "REFUTED"},
        "law_minus": "P(e)=2^-e", "law_plus": "P(e)=3/4^e",
        "threshold": enc(Fraction(2)), "maximum_depth": maximum_depth,
        "rows": rows,
        "infinite_tree_boundary": "Finite rows audit bounded stopping only. Infinite mean is proved symbolically from Doob's bound and monotone convergence, not extrapolated from these rows.",
        "proves_collatz": False,
    }


@dataclass(frozen=True, slots=True)
class WordRow:
    bits: int
    length: int
    q: int
    affine: int
    source: int
    endpoint: int

    @property
    def word(self) -> str:
        return format(self.bits, f"0{self.length}b")


def make_row(bits: int, length: int, q: int, affine: int) -> WordRow:
    modulus, three = 1 << length, 3**q
    source = (-affine * pow(three, -1, modulus)) % modulus or modulus
    endpoint = (three * source + affine) // modulus
    return WordRow(bits, length, q, affine, source, endpoint)


def enumerate_safe(maximum_q: int) -> dict[int, list[WordRow]]:
    grouped = {q: [] for q in range(1, maximum_q + 1)}
    frontier = [(0, 0, 0)]
    maximum_length = (3**maximum_q).bit_length() - 1
    for length in range(1, maximum_length + 1):
        following = []
        for bits, q, affine in frontier:
            if q and 3**q > 1 << length:
                item = make_row(bits << 1, length, q, affine)
                grouped[q].append(item)
                following.append((item.bits, q, affine))
            if q < maximum_q and 3 ** (q + 1) > 1 << length:
                new_affine = 3 * affine + (1 << (length - 1))
                item = make_row((bits << 1) | 1, length, q + 1, new_affine)
                grouped[item.q].append(item)
                following.append((item.bits, item.q, item.affine))
        frontier = following
    return grouped


def exponent_blocks(word: str) -> list[int]:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    if not positions or positions[0] != 0:
        raise ValueError("odd-source parity word required")
    ends = positions[1:] + [len(word)]
    return [end - start for start, end in zip(positions, ends)]


def source_lifts(word: str) -> dict[str, object]:
    exponents = exponent_blocks(word)
    residues, lifts = [], []
    old_residue, old_modulus, length = 0, 1, 0
    for exponent in exponents:
        length += exponent
        _, residue, _, _ = canonical(word[:length])
        lift = (residue - old_residue) // old_modulus
        if not 0 <= lift < 1 << exponent:
            raise AssertionError("source lift range")
        residues.append(residue)
        lifts.append(lift)
        old_residue, old_modulus = residue, 1 << length
    trailing = 0
    for value in reversed(lifts):
        if value:
            break
        trailing += 1
    return {"exponents": exponents, "residues": residues, "lifts": lifts, "trailing_zero_lifts": trailing}


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def crossing_after(source: int, word: str, limit: int = 256) -> dict[str, object]:
    value, q, length = source, 0, 0
    for expected in word:
        if str(value & 1) != expected:
            raise AssertionError("literal source word")
        q += value & 1
        length += 1
        value = shortcut(value)
    continuation = []
    for distance in range(1, limit + 1):
        bit = value & 1
        continuation.append(str(bit))
        q += bit
        length += 1
        value = shortcut(value)
        if 3**q <= 1 << length:
            return {"distance": distance, "continuation": "".join(continuation), "crossing_L": length, "crossing_Q": q, "value_after_crossing": value}
    return {"distance": None, "continuation": "".join(continuation), "limit": limit}


def source_lift_artifact(maximum_q: int = 17) -> dict[str, object]:
    grouped = enumerate_safe(maximum_q)
    minima: dict[tuple[int, int], int] = {}
    for q, rows in grouped.items():
        for item in rows:
            key = (q, item.endpoint)
            minima[key] = min(minima.get(key, item.length), item.length)
    counts = {}
    audit_rows = []
    source_167 = None
    for q in range(1, maximum_q + 1):
        critical_length = (3**q).bit_length() - 1
        critical = [item for item in grouped[q] if item.length == critical_length]
        geodesic = sorted((item for item in critical if minima[(q, item.endpoint)] == item.length), key=lambda item: item.word)
        trailing_counts: Counter[int] = Counter()
        maximum_trailing = -1
        least_maximum = None
        for item in geodesic:
            lift = source_lifts(item.word)
            trailing = int(lift["trailing_zero_lifts"])
            trailing_counts[trailing] += 1
            record = [q, item.word, item.source, item.endpoint, lift["exponents"], lift["lifts"], trailing]
            audit_rows.append(record)
            if trailing > maximum_trailing or (trailing == maximum_trailing and (least_maximum is None or item.source < least_maximum[0])):
                maximum_trailing = trailing
                least_maximum = [item.source, item.word, item.endpoint]
            if item.source == 167 and q == 17:
                source_167 = {
                    "Q": q, "word": item.word, "source": item.source, "endpoint": item.endpoint,
                    **lift, "coefficient_crossing_after_prefix": crossing_after(item.source, item.word),
                }
        counts[str(q)] = {
            "critical_words": len(critical), "geodesic_words": len(geodesic),
            "maximum_trailing_zero_lifts": maximum_trailing,
            "least_source_at_maximum": {"source": least_maximum[0], "word": least_maximum[1], "endpoint": least_maximum[2]},
            "trailing_zero_distribution": {str(key): value for key, value in sorted(trailing_counts.items())},
        }
    if source_167 is None or source_167["trailing_zero_lifts"] != 11:
        raise AssertionError("source 167 falsifier")
    return {
        "format": "collatz-phase19-source-lifts-v1",
        "claim": {"P115": "VERIFIED_THEOREM", "E31": "VERIFIED_FINITE", "H112": "OPEN"},
        "maximum_Q": maximum_q, "counts_by_Q": counts,
        "row_digest_sha256": digest(sorted(audit_rows, key=lambda row: (row[0], row[1]))),
        "row_storage": "omitted; verifier rebuilds every geodesic critical row",
        "source_167_falsifier": source_167,
        "finite_boundary": "A long zero-lift suffix is not eventual stabilization. Source 167 crosses coefficient safety three shortcut steps after the stored Q=17 prefix.",
        "proves_collatz": False,
    }


def periodic_record(word: str, repetitions: int) -> dict[str, object]:
    length, q, affine = len(word), word.count("1"), translation(word)
    if q == 0:
        raise ValueError("periodic audit requires an odd step")
    xi = Fraction(affine, (1 << length) - 3**q)
    a, d = xi.numerator, xi.denominator
    positive_integer = xi.denominator == 1 and xi >= 1
    threshold_bits = max(1, (2 * abs(a) - 1).bit_length()) if a else 1
    loss_bits = 1 + (d - 1).bit_length()
    residues = []
    for count in range(1, repetitions + 1):
        bits = count * length
        modulus = 1 << bits
        residue = (a * pow(d, -1, modulus)) % modulus or modulus
        bound_applies = not positive_integer and bits >= threshold_bits
        if bound_applies and residue < 1 << max(0, bits - loss_bits):
            raise AssertionError("periodic residue lower bound")
        residues.append({"repetitions": count, "bits": bits, "source_residue": residue, "bound_applies": bound_applies})
    return {
        "word": word, "L": length, "q": q, "B": affine,
        "fixed_2adic_source": enc(xi), "positive_integer_cycle_candidate": positive_integer,
        "effective_threshold_bits": threshold_bits, "effective_loss_bits": loss_bits,
        "residues": residues,
    }


def periodic_artifact(repetitions: int = 16) -> dict[str, object]:
    words = ["1", "10", "110", "111", "11101", "1100", "111011100", "110111"]
    rows = [periodic_record(word, repetitions) for word in words]
    return {
        "format": "collatz-phase19-periodic-lifts-v1",
        "claim": {"P116": "VERIFIED_THEOREM", "E31": "VERIFIED_FINITE"},
        "repetitions": repetitions, "rows": rows, "row_digest_sha256": digest(rows),
        "scope_repair": "The repeating block must contain an odd step. The all-zero block has fixed point zero and is not a positive odd cycle candidate.",
        "bound": "For xi=a/d reduced with d odd and xi not a positive integer, r_K>=2^(K-P), P=1+ceil(log2 d), once 2^K>=2|a|.",
        "novelty_boundary": "This is an elementary rational 2-adic congruence bound consistent with standard eventual periodicity; no novelty over that structure is claimed.",
        "proves_collatz": False,
    }


def parity_prefix(source: int, length: int) -> str:
    bits = []
    for _ in range(length):
        bits.append(str(source & 1))
        source = shortcut(source)
    return "".join(bits)


def adversarial_artifact() -> dict[str, object]:
    inputs: list[tuple[str, str]] = []
    for m in range(2, 9):
        inputs.append((f"2^{m}-1", parity_prefix(2**m - 1, 32)))
        inputs.append((f"8^{m}-5", parity_prefix(8**m - 5, 32)))
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
        affine, source, endpoint, q = canonical(word)
        rows.append({
            "name": name, "word": word, "L": len(word), "Q": q, "B": affine,
            "source": source, "endpoint": endpoint,
            "coefficient": enc(Fraction(3**q, 1 << len(word))),
            "normalized_beta": enc(Fraction(affine, 3**q)),
        })
    return {
        "format": "collatz-phase19-adversarial-v1",
        "claim": {"E31": "VERIFIED_FINITE"},
        "families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s", "source 167", "NG19", "NG22", "NG23", "NG28", "NG29", "NG30"],
        "rows": rows, "row_digest_sha256": digest(rows),
        "preserved_boundaries": {
            "source 167": "eleven trailing zero exponent lifts followed by coefficient crossing; finite zeros are not eventual",
            "NG19": "lossy finite tail state cannot decide joint safety",
            "NG22": "coherent 2-adic source plus analytic conditions need not be a positive integer",
            "NG23": "Haar mass does not count canonical ordinary representatives",
            "NG28": "same-Q carry may be negative",
            "NG29": "coefficient-only summed-Haar pressure has a finite ceiling",
            "NG30": "sign-pure SCC packets need not have one positive-to-negative switch"
        },
        "finite_boundary": "These exact rows test conventions and old falsifiers; they imply no eventual lift theorem.",
        "proves_collatz": False,
    }


def theory_artifact() -> dict[str, object]:
    finite_valley = affine_valley_finite()
    return {
        "format": "collatz-phase19-theory-v1",
        "claims": {
            "P112": "VERIFIED_THEOREM", "P113": "VERIFIED_THEOREM",
            "P114": "VERIFIED_THEOREM", "P115": "VERIFIED_THEOREM",
            "P116": "VERIFIED_THEOREM", "NG31": "REFUTED",
            "H112": "OPEN", "H72": "OPEN",
        },
        "P112": {
            "statement": "For a positive predecessor x<N of y=uN, the suffix after the last minimum coefficient is strictly safe. Either its coefficient exceeds u and gives a smaller safe valley ancestor, or n>3N(1-c/u).",
            "identities": ["beta=sum_(j<n)1/(3c_j)", "m>=c/u in the affine-only case", "beta<=nu/(3c)", "beta>N(u/c-1)"],
            "finite_audit": finite_valley,
        },
        "P113": {
            "source_tilt": "P_minus(e)=2^-e; c_n and c_n*beta_n-n/3 are martingales",
            "endpoint_tilt": "P_plus(e)=3/4^e; 1/c_n and beta_n-n/(3c_n) are martingales",
            "bounded_stopping": "E_plus beta_(T_t cap R)=(1/3)E_minus(T_t cap R)",
            "critical_moments": "E_plus beta_T=infinity; E_plus beta_T^s<=3^-s/(1-R(s)) for 0<s<1, R(s)=3^(1-s)/(2^(2-s)-1)<1",
            "haar_tail": "sum_{w in F_t,beta>=B}3^-|w| <= 3^-s/((1-R(s))*t^2*B^s)",
            "proof_boundary": "T_t is almost surely finite under P_plus by the Phase 17 finite Chernoff argument; Doob is proved from bounded stopping before limits are taken.",
        },
        "NG31": {
            "hypothesis": "The first-passage affine correction has finite mean and may be treated as a uniformly average-small error under the endpoint tilt.",
            "status": "REFUTED", "countertheorem": "P113 proves E_plus beta_T=infinity for every t>1.",
            "surviving_statement": "Every fractional moment of order 0<s<1 is finite, with the explicit P113 bound.",
        },
        "P114": {
            "identity": "sum_(i<j)exp(-D_i)=3(Y_j-S)",
            "bound": "R_H(j)<=3*exp(H)*S*(exp(1/S)*(1+3j/S)^(1/9)-1)",
            "phase18_strengthening": "A fixed-packet balanced mixed-SCC itinerary has linearly many bounded-strip returns if positively realized, contradicting P72 without EXT07.",
            "alignment": "Fixed parity packets move a block boundary by only a bounded number of full steps from an accelerated odd boundary, and positive packets occur with positive frequency.",
        },
        "P115": {
            "lift": "r_(n+1)=r_n+lambda_n*2^E_n, 0<=lambda_n<2^e_n",
            "congruence": "3^(n+1)*lambda_n == -(3*y_n+1) mod 2^e_n",
            "characterization": "A positive ordinary source N exists iff r_n=N eventually iff lambda_n=0 eventually.",
            "valuation_boundary": "Exact valuations follow for every sufficiently late exponent only after the entire infinite tail is realized; one terminal finite congruence alone gives divisibility, not exactness.",
        },
        "P116": {
            "periodic_source": "xi_w=B/(2^L-3^q)",
            "effective_bound": "If xi=a/d in lowest terms is not a positive integer, r_K>=2^(K-P), P=1+ceil(log2 d), once 2^K>=2|a|.",
            "ultimately_periodic": "Apply the same rational congruence to the affine preimage through the finite prefix; a positive integer exception enters the represented cycle.",
            "scope_repair": "The repeating block contains an odd step; the all-zero fixed point is zero and not a positive odd cycle.",
        },
        "H112": {
            "status": "OPEN",
            "statement": "Every infinite coefficient-safe all-prefix same-Q-geodesic branch has infinitely many nonzero canonical source lifts.",
            "implication": "Together with P115 this would exclude a positive ordinary source in that exact sublanguage.",
        },
        "what_this_result_does_not_prove": "It does not prove H112, remove the near-diagonal affine-only band, exclude every aperiodic escaping-discrepancy path, prove H72, exclude cycles, or prove Collatz.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 19 obstruction report

## NG31 — average-small affine correction (`REFUTED`)

Under the endpoint tilt `P_+(e)=3/4^e`, the coefficient first-passage
correction has infinite first moment for every threshold `t>1`.  The proof is
not a tail fit: bounded stopping gives

```text
E_+ beta_(T_t cap R) = (1/3) E_- (T_t cap R),
```

while the source-tilt nonnegative coefficient martingale has
`P_-(T_t=infinity)>=1-1/t`.  Monotone convergence forces the mean to diverge.
Fractional moments below one remain finite.  Thus averaged affine correction
cannot be inserted as a uniformly small error into a Haar-volume argument.

## H112 — infinite geodesic nonzero lifts (`OPEN`)

P115 characterizes positive ordinary realizability by eventual zero source
lifts, but does not prove that every infinite all-prefix same-Q-geodesic safe
branch has infinitely many nonzero lifts.  The exact source-167 Q=17 word has
eleven trailing zero exponent lifts and then crosses coefficient safety three
shortcut steps later.  It prevents any finite zero-run rule from being
promoted to eventual stabilization.

## Remaining affine-only band

P112 finds a smaller safe valley ancestor unless

```text
n > 3N(1-c/u).
```

This localizes short predecessors to a near-diagonal coefficient band but does
not empty the band.  H104/H105/H89 still need ordinary source, endpoint,
carry, and height information.

## Periodic scope repair

P116 applies to a repeating block containing an odd step.  The all-zero block
has fixed point zero; it is not a positive odd cycle candidate.  For a reduced
rational 2-adic fixed source that is not a positive integer, the elementary
congruence already gives exponential canonical-residue growth.

## What this result does not prove

It does not prove H112, H72, H89, H104, H105, exclude the nontrivial-cycle
branch, or prove the Collatz conjecture. `proves_collatz=false`.
"""


def generate(artifact_dir: Path) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    values = {
        "phase19_theory.json": theory_artifact(),
        "phase19_stopped_duality.json": stopped_artifact(),
        "phase19_source_lifts.json": source_lift_artifact(),
        "phase19_periodic_lifts.json": periodic_artifact(),
        "phase19_adversarial.json": adversarial_artifact(),
    }
    for name, value in values.items():
        write_json(artifact_dir / name, value)
    (artifact_dir / "phase19_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")
    return {
        "valid": True,
        "stopped_depth": values["phase19_stopped_duality.json"]["maximum_depth"],
        "maximum_Q": values["phase19_source_lifts.json"]["maximum_Q"],
        "adversarial_rows": len(values["phase19_adversarial.json"]["rows"]),
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    print(json.dumps(generate(args.artifact_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
