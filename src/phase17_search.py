#!/usr/bin/env python3
"""Generate exact Phase 17 predecessor-pressure evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

WORD_A = "11101"
WORD_B = "1100"
NG24_LEFT = "11101"
NG24_RIGHT = "111100"
NG25_TARGET = "111110100"
NG27_LONG = "11111111111111101110000000001"
NG27_SHORT = "1111111111101111110100100"
NG28_SHORT = "111111111101111110101011110010001001100"
NG28_LONG = "1101101101110011100111011101010101101101"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def enc(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def dec(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def compositions(total: int, parts: int):
    for cuts in combinations(range(1, total), parts - 1):
        points = (0,) + cuts + (total,)
        yield tuple(points[index + 1] - points[index] for index in range(parts))


def inverse_data(exponents: tuple[int, ...]) -> dict[str, object]:
    affine = 0
    exponent_sum = 0
    for exponent in exponents:
        if exponent < 1:
            raise ValueError("positive exponents required")
        affine = 3 * affine + (1 << exponent_sum)
        exponent_sum += exponent
    odd_count = len(exponents)
    modulus = 3**odd_count
    endpoint = affine * pow(1 << exponent_sum, -1, modulus) % modulus
    if endpoint % 3 == 0:
        raise AssertionError("endpoint must be a 3-adic unit")
    return {
        "exponents": list(exponents),
        "r": odd_count,
        "E": exponent_sum,
        "affine_A": affine,
        "endpoint_residue": endpoint,
        "endpoint_modulus": modulus,
        "multiplier": enc(Fraction(modulus, 1 << exponent_sum)),
        "beta": enc(Fraction(affine, modulus)),
    }


def supercritical_words(maximum_r: int = 4) -> list[dict[str, object]]:
    rows = []
    for r in range(1, maximum_r + 1):
        maximum_E = (3**r).bit_length() - 1
        for total in range(r, maximum_E + 1):
            for exponents in compositions(total, r):
                rows.append(inverse_data(exponents))
    return rows


def lifted_multiplier(rows: list[dict[str, object]], modulus: int = 81) -> dict[int, Fraction | None]:
    maxima: dict[int, Fraction | None] = {residue: None for residue in range(1, modulus) if residue % 3}
    for row in rows:
        small_modulus = int(row["endpoint_modulus"])
        endpoint = int(row["endpoint_residue"])
        multiplier = dec(row["multiplier"])
        for residue in maxima:
            if residue % small_modulus == endpoint:
                old = maxima[residue]
                if old is None or multiplier > old:
                    maxima[residue] = multiplier
    return maxima


THRESHOLDS = [
    Fraction(1), Fraction(9, 8), Fraction(81, 64), Fraction(3, 2),
    Fraction(27, 16), Fraction(2), Fraction(9, 4), Fraction(81, 32),
    Fraction(27, 8), Fraction(81, 16),
]
EXPECTED_COUNTS = [51, 66, 72, 117, 129, 172, 192, 204, 212, 216]


def crt_intervals(maxima: dict[int, Fraction | None]) -> list[dict[str, object]]:
    rows = []
    for index, left in enumerate(THRESHOLDS):
        right = THRESHOLDS[index + 1] if index + 1 < len(THRESHOLDS) else None
        allowed = []
        for residue in range(648):
            if residue % 2 == 0 or residue % 3 == 0:
                continue
            multiplier = maxima[residue % 81 or 81]
            # This deliberately adds a class at equality.  Since equality is
            # actually still forbidden by beta>0, the result is a safe
            # right-continuous upper envelope, not the exact boundary set.
            if multiplier is not None and multiplier > left:
                continue
            if left < 2 and residue % 8 == 5:
                continue
            allowed.append(residue)
        if len(allowed) != EXPECTED_COUNTS[index]:
            raise AssertionError("mod-648 count")
        rows.append({
            "left": enc(left), "right": enc(right) if right is not None else None,
            "allowed_residues": allowed, "count": len(allowed),
            "density": enc(Fraction(len(allowed), 648)),
        })
    return rows


def log_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    if value < 1 or terms < 1:
        raise ValueError("log enclosure domain")
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


def reduce_power_two(value: Fraction) -> tuple[int, Fraction]:
    power = 0
    while value >= 2:
        value /= 2
        power += 1
    return power, value


def packing_terms(intervals: list[dict[str, object]], t: Fraction) -> tuple[Fraction, list[tuple[Fraction, Fraction]]]:
    capacity = Fraction()
    terms: list[tuple[Fraction, Fraction]] = []
    for index, row in enumerate(intervals[:-1]):
        left = dec(row["left"])
        right = dec(row["right"])
        density = dec(row["density"])
        capacity += density * (right - left)
        terms.append((density, right / left))
    cutoff = 3 * t + Fraction(81, 16) - 3 * capacity
    terms.append((Fraction(1, 3), cutoff / Fraction(81, 16)))
    return cutoff, terms


def combined_log_upper(terms_data: list[tuple[Fraction, Fraction]], terms: int) -> tuple[Fraction, Fraction, dict[str, object]]:
    log2_lower, log2_upper = log_bounds(Fraction(2), terms)
    log2_coefficient = Fraction()
    remainder_upper = Fraction()
    entries = []
    for coefficient, ratio in terms_data:
        power, reduced = reduce_power_two(ratio)
        lower, upper = log_bounds(reduced, terms)
        log2_coefficient += coefficient * power
        remainder_upper += coefficient * upper
        entries.append({
            "coefficient": enc(coefficient), "ratio": enc(ratio),
            "removed_power_of_two": power, "reduced_ratio": enc(reduced),
            "lower": enc(lower), "upper": enc(upper),
        })
    return log2_coefficient, remainder_upper, {
        "terms": terms,
        "log2_lower": enc(log2_lower), "log2_upper": enc(log2_upper),
        "entries": entries,
    }


def predecessor_artifact(log_terms: int = 12) -> dict[str, object]:
    words = supercritical_words()
    maxima = lifted_multiplier(words)
    distribution: dict[Fraction | None, int] = {}
    for multiplier in maxima.values():
        distribution[multiplier] = distribution.get(multiplier, 0) + 1
    expected_distribution = {
        Fraction(81, 16): 1, Fraction(27, 8): 2, Fraction(81, 32): 3,
        Fraction(9, 4): 5, Fraction(27, 16): 4, Fraction(3, 2): 15,
        Fraction(81, 64): 2, Fraction(9, 8): 5, None: 17,
    }
    if distribution != expected_distribution:
        raise AssertionError("mod-81 multiplier distribution")
    intervals = crt_intervals(maxima)
    capacity = sum(
        dec(row["density"]) * (dec(row["right"]) - dec(row["left"]))
        for row in intervals[:-1]
    )
    error = Fraction(1) + sum(Fraction(int(row["count"]), 1) / dec(row["left"]) for row in intervals)
    if capacity != Fraction(23093, 20736) or error != Fraction(18344, 27):
        raise AssertionError("packing constants")
    cutoff, psi_terms = packing_terms(intervals, Fraction(270))
    if cutoff != Fraction(5610619, 6912):
        raise AssertionError("270 cutoff")
    log2_coefficient, remainder_upper, certificate = combined_log_upper(psi_terms, log_terms)
    log2_lower = dec(certificate["log2_lower"])
    margin = (3 - log2_coefficient) * log2_lower - remainder_upper - Fraction(18344, 27 * 300000)
    if margin <= 0:
        raise AssertionError("270 exact log comparison")
    distribution_rows = []
    for multiplier in [Fraction(81, 16), Fraction(27, 8), Fraction(81, 32), Fraction(9, 4), Fraction(27, 16), Fraction(3, 2), Fraction(81, 64), Fraction(9, 8), None]:
        distribution_rows.append({"multiplier": enc(multiplier) if multiplier is not None else None, "unit_residue_count": distribution[multiplier]})
    return {
        "format": "collatz-phase17-predecessor-sieve-v1",
        "claims": {"P104": "VERIFIED_THEOREM", "E29": "VERIFIED_FINITE", "H104": "OPEN", "H105": "OPEN"},
        "accelerated_inverse_identity": "2^E*y=3^r*x+A and y=(3^r/2^E)*(x+A/3^r)",
        "forbidden_height_rule": "endpoint y in its residue cylinder is forbidden on a least-counterexample orbit when y/N<=c; the table admits equality early and is therefore an upper envelope",
        "maximum_odd_steps": 4,
        "supercritical_word_count": len(words),
        "supercritical_words": words,
        "mod81_distribution": distribution_rows,
        "mod81_maximum_by_unit_residue": [{"residue": residue, "multiplier": enc(multiplier) if multiplier is not None else None} for residue, multiplier in sorted(maxima.items())],
        "crt_modulus": 648,
        "interval_convention": "right-continuous allowed-class upper envelope; at an exact multiplier threshold the true forbidden set can be larger",
        "intervals": intervals,
        "continuous_capacity_below_81N_over_16": enc(capacity),
        "post_capacity_cutoff": "U(t)=3t+11899/6912",
        "discrete_reciprocal_error_coefficient": enc(error),
        "psi_270_cutoff": enc(cutoff),
        "psi_270_log_certificate": {**certificate, "log2_coefficient": enc(log2_coefficient), "remainder_upper": enc(remainder_upper), "exact_positive_margin": enc(margin), "comparison": "Psi_4(270)+18344/(27*300000)<3log(2)"},
        "dichotomy": {
            "G270": "q<=270N implies Y_q<2N and all-prefix same-Q geodesic",
            "H270": "q>270N implies N<q/270, Y_q<q/135, X<q/135, Z<2q/135",
            "hypotheses": ["least positive counterexample", "finite coefficient first crossing", "odd inputs before crossing are distinct", "E28 excludes N<300000"],
            "monotonicity": "2*(U(t)/U(270))^(1/9)/t is strictly decreasing for t>=270",
        },
        "what_this_result_does_not_prove": "Neither G270 nor H270 is excluded; the periodic branch and Collatz remain open.",
        "proves_collatz": False,
    }


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def direct_audit(bound: int) -> dict[str, object]:
    if bound < 2:
        raise ValueError("direct bound")
    memo: dict[int, tuple[int, int]] = {1: (0, 1)}
    digest = hashlib.sha256()
    maximum_steps = (-1, 0)
    maximum_peak = (0, 0)
    for source in range(1, bound):
        value = source
        path = []
        while value not in memo:
            path.append(value)
            value = shortcut(value)
        steps, peak = memo[value]
        for item in reversed(path):
            steps += 1
            peak = max(item, peak)
            memo[item] = (steps, peak)
        source_steps, source_peak = memo[source]
        if source_steps > maximum_steps[0]:
            maximum_steps = (source_steps, source)
        if source_peak > maximum_peak[0]:
            maximum_peak = (source_peak, source)
        digest.update(f"{source}|{source_steps}|{source_peak}\n".encode("ascii"))
    return {
        "format": "collatz-phase17-direct-audit-v1",
        "claim": "E28", "status": "VERIFIED_FINITE",
        "source_interval": [1, bound], "upper_endpoint_exclusive": True,
        "sources_checked": bound - 1, "all_reach_one": True,
        "maximum_shortcut_steps": {"steps": maximum_steps[0], "least_source": maximum_steps[1]},
        "maximum_peak": {"value": maximum_peak[0], "least_source": maximum_peak[1]},
        "row_digest_sha256": digest.hexdigest(),
        "finite_boundary": "This proves only that a least positive counterexample, if one exists, is at least the exclusive bound.",
        "proves_collatz": False,
    }


def ceiling_difference_bounds(U: Fraction, terms: int) -> tuple[Fraction, Fraction, dict[str, object]]:
    # U is in (1024,2048), so log U = 10 log 2 + log(U/1024).
    log2_lower, log2_upper = log_bounds(Fraction(2), terms)
    ratio_lower, ratio_upper = log_bounds(U / 1024, terms)
    rational = -Fraction(1, 4) * (1 - 1 / U**2)
    lower = Fraction(1, 3) * log2_lower + Fraction(1, 3) * ratio_lower + rational
    upper = Fraction(1, 3) * log2_upper + Fraction(1, 3) * ratio_upper + rational
    return lower, upper, {
        "U": enc(U), "U_over_1024": enc(U / 1024),
        "lower_for_Rmin_minus_3log2": enc(lower),
        "upper_for_Rmin_minus_3log2": enc(upper),
    }


def pressure_artifact(log_terms: int = 12) -> dict[str, object]:
    lower_U = Fraction(1083903, 1000)
    upper_U = Fraction(135488, 125)
    lower_lo, lower_hi, lower_record = ceiling_difference_bounds(lower_U, log_terms)
    upper_lo, upper_hi, upper_record = ceiling_difference_bounds(upper_U, log_terms)
    if lower_hi >= 0 or upper_lo <= 0:
        raise AssertionError("ceiling root bracket")
    A_upper = (upper_U - 1) / 3 - Fraction(1, 2) * (1 - 1 / upper_U)
    ceiling = Fraction(360469, 1000)
    if A_upper >= ceiling:
        raise AssertionError("capacity ceiling")
    return {
        "format": "collatz-phase17-pressure-v1",
        "claims": {"P105": "VERIFIED_THEOREM", "NG29": "REFUTED"},
        "single_exponent_probability": "p_e=3/4^e, sum p_e=1",
        "word_identity": "p(e_1,...,e_r)=3^r/4^E=3^(-r)c(e)^2",
        "positive_drift_certificate": {"expectation": "log(3)-(4/3)log(2)>0", "exact_power_comparison": "27>16"},
        "almost_sure_passage_certificate": {"even_time_bad_event": "sum(e_1,...,e_(2m))>=3m", "chernoff_lambda": enc(Fraction(4, 3)), "geometric_bound_base": enc(Fraction(243, 256)), "consequence": "c_(2m)>(9/8)^m eventually almost surely"},
        "first_passage": {
            "definition": "proper prefix coefficient <t and whole coefficient >=t",
            "overshoot": "t<=c<3t/2 because only e=1 can cross upward",
            "second_moment_identity": "sum_(w in F_t) 3^(-|w|)c(w)^2=1",
            "raw_endpoint_mass": "4/(9t^2)<sum_(w in F_t)3^(-|w|)<=1/t^2",
            "union_boundary": "endpoint cylinders may collide, so only the upper union-measure bound survives",
        },
        "coefficient_only_mechanism": {
            "scope": ["forbid only from c(w)>=normalized endpoint height", "bound deletion only by summed 3-adic Haar mass", "discard affine beta, fixed ordinary source, transition dependence, and carry"],
            "ordinary_density_deletion_upper": "1/(2u^2)",
            "A_min": "(U-1)/3-(1/2)(1-1/U)",
            "R_min": "(1/3)log(U)-(1/4)(1-1/U^2)",
            "note": "These are optimistic lower envelopes; near u=1 the formal deletion can exceed the baseline density, which only makes the ceiling more generous.",
            "root_bracket": {"lower": lower_record, "upper": upper_record, "terms": log_terms},
            "A_min_at_upper_root_bracket": enc(A_upper),
            "certified_q_over_N_ceiling": enc(ceiling),
            "status": "REFUTED",
        },
        "what_this_result_does_not_prove": "The ceiling does not apply to affine-correction, fixed-source, transition-aware, carry-aware, or ordinary-representative methods, and it does not refute geodesicity itself.",
        "proves_collatz": False,
    }


def suffix_code_artifact(blocks: int = 3) -> dict[str, object]:
    r = 4
    candidates = [row for row in supercritical_words(r) if int(row["r"]) == r]
    selected: dict[int, dict[str, object]] = {}
    for row in candidates:
        endpoint = int(row["endpoint_residue"])
        key = (int(row["E"]), tuple(row["exponents"]))
        old = selected.get(endpoint)
        if old is None or key < (int(old["E"]), tuple(old["exponents"])):
            selected[endpoint] = row
    code = [selected[key] for key in sorted(selected)]
    if len(code) != 11:
        raise AssertionError("r=4 code size")
    moment2 = sum(Fraction(1, 3**r) * dec(row["multiplier"]) ** 2 for row in code)
    if moment2 != Fraction(1539, 2048):
        raise AssertionError("r=4 second moment")
    counts = {}
    digest = hashlib.sha256()
    exponent_words = [tuple(int(value) for value in row["exponents"]) for row in code]
    for block_count in range(1, blocks + 1):
        endpoints = set()
        for address in product(range(len(code)), repeat=block_count):
            exponents = tuple(value for index in address for value in exponent_words[index])
            combined = inverse_data(exponents)
            endpoint = int(combined["endpoint_residue"])
            if endpoint in endpoints:
                raise AssertionError("suffix code collision")
            endpoints.add(endpoint)
            digest.update(f"{block_count}|{','.join(map(str,address))}|{endpoint}\n".encode("ascii"))
        counts[str(block_count)] = {"addresses": len(code) ** block_count, "distinct_endpoint_residues": len(endpoints), "modulus": 3 ** (r * block_count)}
    return {
        "format": "collatz-phase17-suffix-code-v1",
        "claim": "P106", "status": "VERIFIED_THEOREM",
        "block_odd_steps": r, "selection_rule": "shortest total-supercritical exponent word in each distinct endpoint class; lexicographic tie break",
        "code_size": len(code), "codewords": code,
        "second_moment_at_s_2": enc(moment2),
        "finite_concatenation_audit": counts,
        "address_endpoint_digest_sha256": digest.hexdigest(),
        "theorem": "Distinct last-block residues recover the last block; exact division by 3^r recursively recovers every preceding endpoint and block.",
        "trend_boundary": "No convergence or monotonicity of finite pressure roots is claimed from this one code.",
        "proves_collatz": False,
    }


def word_constant(word: str) -> int:
    result = 0
    power = 1
    for bit in word:
        if bit == "1":
            result = 3 * result + power
        elif bit != "0":
            raise ValueError("binary word")
        power <<= 1
    return result


def word_summary(name: str, word: str) -> dict[str, object]:
    return {"name": name, "word": word, "L": len(word), "Q": word.count("1"), "B": word_constant(word)}


def adversarial_artifact() -> dict[str, object]:
    rows = []
    for m in range(2, 9):
        rows.append({"name": f"2^{m}-1", "source": 2**m - 1})
        rows.append({"name": f"8^{m}-5", "source": 8**m - 5})
    for size in range(1, 5):
        for choice in product(("110", "111"), repeat=size):
            word = "".join(choice)
            rows.append(word_summary(f"(110|111)^*:{word}", word))
    rows.extend([word_summary("A=11101", WORD_A), word_summary("B=1100", WORD_B)])
    for r in range(1, 5):
        for s in range(1, 5):
            rows.append(word_summary(f"A^{r}B^{s}", WORD_A * r + WORD_B * s))
    named = {
        "NG19": "fixed tail windows remain outside the coefficient-only pressure state",
        "NG21": "a mod-6 packing saturator is not claimed to be an orbit",
        "NG22": "formal 2-adic sources are not identified with positive ordinary sources",
        "NG23": "summed Haar mass is used only as an upper union bound, never a representative count",
        "NG24": f"suffix decoding is not left congruence: {NG24_LEFT}~{NG24_RIGHT}",
        "NG25": f"cross-Q ancestor remains required for {NG25_TARGET}",
        "NG26": "unsafe-target valley extraction remains outside this coefficient-only code",
        "NG27": f"no bounded compression gain is inferred from {NG27_LONG} and {NG27_SHORT}",
        "NG28": f"no carry sign is assumed for {NG28_SHORT} and {NG28_LONG}",
    }
    digest = hashlib.sha256()
    for row in rows:
        digest.update((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    for key, value in named.items():
        digest.update(f"{key}|{value}\n".encode("utf-8"))
    return {
        "format": "collatz-phase17-adversarial-v1",
        "mandatory_rows": rows,
        "named_obstruction_boundaries": named,
        "digest_sha256": digest.hexdigest(),
        "interpretation": "The regression matrix checks scope and conventions; bounded survival or rejection is not an asymptotic theorem.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 17 obstruction report

## NG29 — unbounded coefficient-only Haar improvement

`REFUTED` for the precisely scoped mechanism. First-passage exponent words
have summed endpoint mass at most `u^-2`. After parity intersection, deletion
is at most `1/(2u^2)`. Even the optimistic collision-free lower envelopes
reach the reciprocal threshold before normalized count `360.469`.

This is not a theorem that geodesicity fails beyond that point. Affine beta,
fixed positive ordinary sources, actual transition dependence, canonical
representatives, and signed carry are deliberately absent and can evade the
ceiling.

## H104 — G270 ordinary-source branch

`OPEN`. All-prefix same-Q geodesicity does not contradict the finite formal
all-contact branches. A proof must retain eventually zero high lift bits of
one fixed positive ordinary source and survive NG17/P73/NG24--NG29.

## H105 — H270 two-sided box

`OPEN`. The exact bounds `N<q/270`, `X<q/135`, `Z<2q/135` do not yet have a
complete transducer, pumping, or meet-in-the-middle exclusion. Source and
endpoint height, literal safety, and carry distinctions must all remain.

## Finite-code boundary

The r=4 suffix code has 11 words and collision-free concatenations in the
audited three-block range. Suffix decodability is a theorem for all block
counts, but finite pressure-root convergence or monotonicity is not claimed.

## What this result does not prove

It does not exclude H104, H105, a nontrivial cycle, H89, H72, or any Collatz
counterexample. `proves_collatz=false`.
"""


def generate(artifact_dir: Path, direct_bound: int = 300000) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(artifact_dir / "phase17_predecessor_sieve.json", predecessor_artifact())
    write_json(artifact_dir / "phase17_direct_audit.json", direct_audit(direct_bound))
    write_json(artifact_dir / "phase17_pressure.json", pressure_artifact())
    write_json(artifact_dir / "phase17_suffix_code.json", suffix_code_artifact())
    write_json(artifact_dir / "phase17_adversarial.json", adversarial_artifact())
    (artifact_dir / "phase17_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--direct-bound", type=int, default=300000)
    args = parser.parse_args()
    generate(args.artifact_dir, args.direct_bound)
    print(json.dumps({"generated": True, "direct_bound": args.direct_bound, "proves_collatz": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
