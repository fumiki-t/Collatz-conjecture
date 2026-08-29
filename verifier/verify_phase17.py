#!/usr/bin/env python3
"""Independent exact verifier for Phase 17 predecessor-pressure evidence.

This program deliberately does not import the artifact generator.  It uses an
explicit affine sum, a different composition iterator, and a descending
finite-orbit pass before serializing audit rows in ascending order.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from itertools import product
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


def exponent_vectors(total: int, length: int):
    """Independent recursive positive-composition enumeration."""
    if length == 1:
        if total >= 1:
            yield (total,)
        return
    for head in range(1, total - length + 2):
        for tail in exponent_vectors(total - head, length - 1):
            yield (head,) + tail


def affine_sum(exponents: tuple[int, ...]) -> int:
    """A=sum_j 3^(r-1-j) 2^(e_0+...+e_(j-1))."""
    if not exponents or min(exponents) < 1:
        fail("invalid exponent word")
    result = 0
    prefix = 0
    r = len(exponents)
    for index, exponent in enumerate(exponents):
        result += pow(3, r - 1 - index) * pow(2, prefix)
        prefix += exponent
    return result


def inverse_record(exponents: tuple[int, ...]) -> dict[str, object]:
    r, total = len(exponents), sum(exponents)
    modulus = pow(3, r)
    affine = affine_sum(exponents)
    endpoint = affine * pow(pow(2, total), -1, modulus) % modulus
    if endpoint == 0 or endpoint % 3 == 0:
        fail("endpoint unit reconstruction")
    return {
        "exponents": list(exponents), "r": r, "E": total,
        "affine_A": affine, "endpoint_residue": endpoint,
        "endpoint_modulus": modulus,
        "multiplier": encoded(Fraction(modulus, pow(2, total))),
        "beta": encoded(Fraction(affine, modulus)),
    }


def all_supercritical(limit: int = 4) -> list[dict[str, object]]:
    rows = []
    for r in range(1, limit + 1):
        largest_total = pow(3, r).bit_length() - 1
        for total in range(r, largest_total + 1):
            rows.extend(inverse_record(word) for word in exponent_vectors(total, r))
    return rows


THRESHOLDS = [
    Fraction(1), Fraction(9, 8), Fraction(81, 64), Fraction(3, 2),
    Fraction(27, 16), Fraction(2), Fraction(9, 4), Fraction(81, 32),
    Fraction(27, 8), Fraction(81, 16),
]
COUNTS = [51, 66, 72, 117, 129, 172, 192, 204, 212, 216]


def maximum_by_unit(words: list[dict[str, object]]) -> dict[int, Fraction | None]:
    answer: dict[int, Fraction | None] = {}
    for residue in range(81):
        if residue % 3 == 0:
            continue
        candidates = [
            frac(row["multiplier"])
            for row in words
            if residue % int(row["endpoint_modulus"]) == int(row["endpoint_residue"])
        ]
        answer[residue] = max(candidates) if candidates else None
    return answer


def interval_rows(maxima: dict[int, Fraction | None]) -> list[dict[str, object]]:
    answer = []
    for index, threshold in enumerate(THRESHOLDS):
        following = THRESHOLDS[index + 1] if index + 1 < len(THRESHOLDS) else None
        residues = []
        for residue in range(1, 648, 2):
            if residue % 3 == 0:
                continue
            multiplier = maxima[residue % 81]
            # Equality is deliberately admitted, producing an upper envelope.
            if multiplier is not None and multiplier > threshold:
                continue
            if threshold < 2 and residue % 8 == 5:
                continue
            residues.append(residue)
        if len(residues) != COUNTS[index]:
            fail("independent mod-648 counts")
        answer.append({
            "left": encoded(threshold),
            "right": encoded(following) if following is not None else None,
            "allowed_residues": residues,
            "count": len(residues),
            "density": encoded(Fraction(len(residues), 648)),
        })
    return answer


def log_series(value: Fraction, count: int) -> tuple[Fraction, Fraction]:
    if value < 1 or count < 1:
        fail("log series domain")
    z = (value - 1) / (value + 1)
    partial = sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(count)), Fraction())
    first = z ** (2 * count + 1)
    return 2 * partial, 2 * partial + 2 * first / ((2 * count + 1) * (1 - z * z))


def split_twos(value: Fraction) -> tuple[int, Fraction]:
    removed = 0
    while value >= 2:
        removed += 1
        value /= 2
    return removed, value


def verify_predecessor(path: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase17-predecessor-sieve-v1" or data.get("proves_collatz") is not False:
        fail("predecessor format or proof boundary")
    if data.get("claims") != {"P104": "VERIFIED_THEOREM", "E29": "VERIFIED_FINITE", "H104": "OPEN", "H105": "OPEN"}:
        fail("predecessor claim boundary")
    if data.get("maximum_odd_steps") != 4:
        fail("predecessor word depth")
    words = all_supercritical()
    if data.get("supercritical_word_count") != 23 or data.get("supercritical_words") != words:
        fail("supercritical word reconstruction")
    maxima = maximum_by_unit(words)
    max_rows = [
        {"residue": residue, "multiplier": encoded(value) if value is not None else None}
        for residue, value in sorted(maxima.items())
    ]
    if data.get("mod81_maximum_by_unit_residue") != max_rows:
        fail("mod-81 maximum reconstruction")
    order = [Fraction(81, 16), Fraction(27, 8), Fraction(81, 32), Fraction(9, 4),
             Fraction(27, 16), Fraction(3, 2), Fraction(81, 64), Fraction(9, 8), None]
    distribution = []
    for value in order:
        distribution.append({
            "multiplier": encoded(value) if value is not None else None,
            "unit_residue_count": sum(item == value for item in maxima.values()),
        })
    if data.get("mod81_distribution") != distribution:
        fail("mod-81 distribution reconstruction")
    rows = interval_rows(maxima)
    if data.get("intervals") != rows or data.get("interval_convention") != "right-continuous allowed-class upper envelope; at an exact multiplier threshold the true forbidden set can be larger":
        fail("CRT upper-envelope reconstruction")
    capacity = sum(
        frac(row["density"]) * (frac(row["right"]) - frac(row["left"]))
        for row in rows[:-1]
    )
    error = Fraction(1) + sum(Fraction(int(row["count"]), 1) / frac(row["left"]) for row in rows)
    if capacity != Fraction(23093, 20736) or frac(data.get("continuous_capacity_below_81N_over_16")) != capacity:
        fail("packing capacity")
    if error != Fraction(18344, 27) or frac(data.get("discrete_reciprocal_error_coefficient")) != error:
        fail("packing reciprocal error")

    cert = data.get("psi_270_log_certificate")
    if not isinstance(cert, dict) or cert.get("terms") != 12:
        fail("270 log certificate header")
    cutoff = 3 * 270 + Fraction(81, 16) - 3 * capacity
    if cutoff != Fraction(5610619, 6912) or frac(data.get("psi_270_cutoff")) != cutoff:
        fail("270 cutoff")
    terms_data = []
    for row in rows[:-1]:
        terms_data.append((frac(row["density"]), frac(row["right"]) / frac(row["left"])))
    terms_data.append((Fraction(1, 3), cutoff / Fraction(81, 16)))
    log2_lo, log2_hi = log_series(Fraction(2), 12)
    expected_entries = []
    log2_coefficient = Fraction()
    remainder_upper = Fraction()
    for coefficient, ratio in terms_data:
        power, reduced = split_twos(ratio)
        lower, upper = log_series(reduced, 12)
        log2_coefficient += coefficient * power
        remainder_upper += coefficient * upper
        expected_entries.append({
            "coefficient": encoded(coefficient), "ratio": encoded(ratio),
            "removed_power_of_two": power, "reduced_ratio": encoded(reduced),
            "lower": encoded(lower), "upper": encoded(upper),
        })
    margin = (3 - log2_coefficient) * log2_lo - remainder_upper - Fraction(18344, 27 * 300000)
    if margin <= 0:
        fail("internal 270 comparison")
    if (frac(cert.get("log2_lower")) != log2_lo or frac(cert.get("log2_upper")) != log2_hi
            or cert.get("entries") != expected_entries or frac(cert.get("log2_coefficient")) != log2_coefficient
            or frac(cert.get("remainder_upper")) != remainder_upper or frac(cert.get("exact_positive_margin")) != margin):
        fail("270 exact log comparison")
    if data.get("forbidden_height_rule") != "endpoint y in its residue cylinder is forbidden on a least-counterexample orbit when y/N<=c; the table admits equality early and is therefore an upper envelope":
        fail("height equality boundary")
    dichotomy = data.get("dichotomy")
    if not isinstance(dichotomy, dict) or dichotomy.get("G270") != "q<=270N implies Y_q<2N and all-prefix same-Q geodesic" or dichotomy.get("H270") != "q>270N implies N<q/270, Y_q<q/135, X<q/135, Z<2q/135":
        fail("270 dichotomy")
    hypotheses = dichotomy.get("hypotheses")
    if not isinstance(hypotheses, list) or "odd inputs before crossing are distinct" not in hypotheses or "E28 excludes N<300000" not in hypotheses:
        fail("dichotomy hypothesis boundary")
    return {"supercritical_words": len(words), "crt_counts": COUNTS, "log_margin": [margin.numerator, margin.denominator]}


def shortcut(value: int) -> int:
    return (3 * value + 1) // 2 if value % 2 else value // 2


def expected_direct(bound: int) -> dict[str, object]:
    if bound < 2:
        fail("direct audit bound")
    memo: dict[int, tuple[int, int]] = {1: (0, 1)}
    # Descending order is intentionally different from the generator.
    for source in range(bound - 1, 0, -1):
        current = source
        path = []
        while current not in memo:
            path.append(current)
            current = shortcut(current)
        steps, peak = memo[current]
        for item in reversed(path):
            steps += 1
            peak = max(item, peak)
            memo[item] = (steps, peak)
    digest = hashlib.sha256()
    maximum_steps = max((memo[source][0], -source) for source in range(1, bound))
    maximum_peak = max((memo[source][1], -source) for source in range(1, bound))
    for source in range(1, bound):
        steps, peak = memo[source]
        digest.update(f"{source}|{steps}|{peak}\n".encode("ascii"))
    return {
        "format": "collatz-phase17-direct-audit-v1", "claim": "E28", "status": "VERIFIED_FINITE",
        "source_interval": [1, bound], "upper_endpoint_exclusive": True,
        "sources_checked": bound - 1, "all_reach_one": True,
        "maximum_shortcut_steps": {"steps": maximum_steps[0], "least_source": -maximum_steps[1]},
        "maximum_peak": {"value": maximum_peak[0], "least_source": -maximum_peak[1]},
        "row_digest_sha256": digest.hexdigest(),
        "finite_boundary": "This proves only that a least positive counterexample, if one exists, is at least the exclusive bound.",
        "proves_collatz": False,
    }


def verify_direct(path: Path) -> dict[str, object]:
    data = load(path)
    interval = data.get("source_interval")
    if not isinstance(interval, list) or len(interval) != 2 or interval[0] != 1 or not isinstance(interval[1], int):
        fail("direct audit interval")
    expected = expected_direct(interval[1])
    if data != expected:
        fail("direct audit reconstruction")
    return {"bound": interval[1], "digest": expected["row_digest_sha256"], "maximum_shortcut_steps": expected["maximum_shortcut_steps"], "maximum_peak": expected["maximum_peak"]}


def ceiling_bounds(U: Fraction, count: int) -> tuple[Fraction, Fraction, dict[str, object]]:
    lo2, hi2 = log_series(Fraction(2), count)
    lor, hir = log_series(U / 1024, count)
    rational = -Fraction(1, 4) * (1 - 1 / U**2)
    lower = Fraction(1, 3) * lo2 + Fraction(1, 3) * lor + rational
    upper = Fraction(1, 3) * hi2 + Fraction(1, 3) * hir + rational
    return lower, upper, {
        "U": encoded(U), "U_over_1024": encoded(U / 1024),
        "lower_for_Rmin_minus_3log2": encoded(lower),
        "upper_for_Rmin_minus_3log2": encoded(upper),
    }


def verify_pressure(path: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-phase17-pressure-v1" or data.get("proves_collatz") is not False:
        fail("pressure format or proof boundary")
    if data.get("claims") != {"P105": "VERIFIED_THEOREM", "NG29": "REFUTED"}:
        fail("pressure claim boundary")
    if data.get("word_identity") != "p(e_1,...,e_r)=3^r/4^E=3^(-r)c(e)^2":
        fail("pressure word identity")
    passage = data.get("first_passage")
    if not isinstance(passage, dict) or passage.get("union_boundary") != "endpoint cylinders may collide, so only the upper union-measure bound survives":
        fail("pressure union boundary")
    if sum(Fraction(3, pow(4, exponent)) for exponent in range(1, 200)) >= 1:
        fail("internal probability partial sum")
    if Fraction(243, 256) >= 1 or pow(3, 3) <= pow(2, 4):
        fail("internal drift certificate")
    mechanism = data.get("coefficient_only_mechanism")
    if not isinstance(mechanism, dict) or mechanism.get("status") != "REFUTED":
        fail("pressure scoped refutation")
    bracket = mechanism.get("root_bracket")
    if not isinstance(bracket, dict) or bracket.get("terms") != 12:
        fail("pressure root bracket")
    lower_U, upper_U = Fraction(1083903, 1000), Fraction(135488, 125)
    lower_lo, lower_hi, lower_record = ceiling_bounds(lower_U, 12)
    upper_lo, upper_hi, upper_record = ceiling_bounds(upper_U, 12)
    if lower_hi >= 0 or upper_lo <= 0:
        fail("internal pressure root signs")
    if bracket.get("lower") != lower_record or bracket.get("upper") != upper_record:
        fail("pressure root enclosure")
    A_upper = (upper_U - 1) / 3 - Fraction(1, 2) * (1 - 1 / upper_U)
    if A_upper >= Fraction(360469, 1000) or frac(mechanism.get("A_min_at_upper_root_bracket")) != A_upper or frac(mechanism.get("certified_q_over_N_ceiling")) != Fraction(360469, 1000):
        fail("pressure capacity ceiling")
    scope = mechanism.get("scope")
    if not isinstance(scope, list) or "discard affine beta, fixed ordinary source, transition dependence, and carry" not in scope:
        fail("pressure scope")
    return {"root_bracket": [encoded(lower_U), encoded(upper_U)], "capacity_upper": encoded(A_upper)}


def expected_suffix(block_limit: int) -> dict[str, object]:
    candidates = [row for row in all_supercritical(4) if row["r"] == 4]
    chosen: dict[int, dict[str, object]] = {}
    for row in reversed(candidates):
        endpoint = int(row["endpoint_residue"])
        key = (int(row["E"]), tuple(row["exponents"]))
        previous = chosen.get(endpoint)
        if previous is None or key < (int(previous["E"]), tuple(previous["exponents"])):
            chosen[endpoint] = row
    code = [chosen[endpoint] for endpoint in sorted(chosen)]
    moment = sum(Fraction(1, 81) * frac(row["multiplier"]) ** 2 for row in code)
    digest = hashlib.sha256()
    counts = {}
    vectors = [tuple(int(value) for value in row["exponents"]) for row in code]
    for count in range(1, block_limit + 1):
        endpoints = set()
        for address in product(range(len(code)), repeat=count):
            word = tuple(value for index in address for value in vectors[index])
            endpoint = int(inverse_record(word)["endpoint_residue"])
            if endpoint in endpoints:
                fail("independent suffix collision")
            endpoints.add(endpoint)
            digest.update(f"{count}|{','.join(map(str, address))}|{endpoint}\n".encode("ascii"))
        counts[str(count)] = {"addresses": len(code) ** count, "distinct_endpoint_residues": len(endpoints), "modulus": pow(3, 4 * count)}
    return {
        "format": "collatz-phase17-suffix-code-v1", "claim": "P106", "status": "VERIFIED_THEOREM",
        "block_odd_steps": 4,
        "selection_rule": "shortest total-supercritical exponent word in each distinct endpoint class; lexicographic tie break",
        "code_size": len(code), "codewords": code, "second_moment_at_s_2": encoded(moment),
        "finite_concatenation_audit": counts, "address_endpoint_digest_sha256": digest.hexdigest(),
        "theorem": "Distinct last-block residues recover the last block; exact division by 3^r recursively recovers every preceding endpoint and block.",
        "trend_boundary": "No convergence or monotonicity of finite pressure roots is claimed from this one code.",
        "proves_collatz": False,
    }


def verify_suffix(path: Path) -> dict[str, object]:
    data = load(path)
    finite = data.get("finite_concatenation_audit")
    if not isinstance(finite, dict) or not finite:
        fail("suffix finite audit")
    try:
        block_limit = max(map(int, finite))
    except ValueError as exc:
        fail(f"suffix block keys: {exc}")
    expected = expected_suffix(block_limit)
    if data != expected:
        fail("suffix code reconstruction")
    return {"code_size": expected["code_size"], "moment": expected["second_moment_at_s_2"], "blocks": block_limit}


def parity_constant(word: str) -> int:
    if any(bit not in "01" for bit in word):
        fail("adversarial binary word")
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    return sum(pow(2, position) * pow(3, len(positions) - 1 - odd_index) for odd_index, position in enumerate(positions))


def word_row(name: str, word: str) -> dict[str, object]:
    return {"name": name, "word": word, "L": len(word), "Q": word.count("1"), "B": parity_constant(word)}


def expected_adversarial() -> dict[str, object]:
    rows = []
    for m in range(2, 9):
        rows.extend(({"name": f"2^{m}-1", "source": pow(2, m) - 1}, {"name": f"8^{m}-5", "source": pow(8, m) - 5}))
    for size in range(1, 5):
        for choice in product(("110", "111"), repeat=size):
            word = "".join(choice)
            rows.append(word_row(f"(110|111)^*:{word}", word))
    A, B = "11101", "1100"
    rows.extend((word_row("A=11101", A), word_row("B=1100", B)))
    for r in range(1, 5):
        for s in range(1, 5):
            rows.append(word_row(f"A^{r}B^{s}", A * r + B * s))
    named = {
        "NG19": "fixed tail windows remain outside the coefficient-only pressure state",
        "NG21": "a mod-6 packing saturator is not claimed to be an orbit",
        "NG22": "formal 2-adic sources are not identified with positive ordinary sources",
        "NG23": "summed Haar mass is used only as an upper union bound, never a representative count",
        "NG24": "suffix decoding is not left congruence: 11101~111100",
        "NG25": "cross-Q ancestor remains required for 111110100",
        "NG26": "unsafe-target valley extraction remains outside this coefficient-only code",
        "NG27": "no bounded compression gain is inferred from 11111111111111101110000000001 and 1111111111101111110100100",
        "NG28": "no carry sign is assumed for 111111111101111110101011110010001001100 and 1101101101110011100111011101010101101101",
    }
    digest = hashlib.sha256()
    for row in rows:
        digest.update((json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8"))
    for key, value in named.items():
        digest.update(f"{key}|{value}\n".encode("utf-8"))
    return {
        "format": "collatz-phase17-adversarial-v1", "mandatory_rows": rows,
        "named_obstruction_boundaries": named, "digest_sha256": digest.hexdigest(),
        "interpretation": "The regression matrix checks scope and conventions; bounded survival or rejection is not an asymptotic theorem.",
        "proves_collatz": False,
    }


def verify_adversarial(path: Path) -> dict[str, object]:
    data, expected = load(path), expected_adversarial()
    if data != expected:
        fail("adversarial reconstruction")
    return {"rows": len(expected["mandatory_rows"]), "digest": expected["digest_sha256"]}


EXPECTED_REPORT = """# Phase 17 obstruction report

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


def verify_report(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"cannot load obstruction report: {exc}")
    if text != EXPECTED_REPORT:
        fail("obstruction report mismatch")
    return {"sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()}


def verify(artifact_dir: Path) -> dict[str, object]:
    predecessor = verify_predecessor(artifact_dir / "phase17_predecessor_sieve.json")
    direct = verify_direct(artifact_dir / "phase17_direct_audit.json")
    pressure = verify_pressure(artifact_dir / "phase17_pressure.json")
    suffix = verify_suffix(artifact_dir / "phase17_suffix_code.json")
    adversarial = verify_adversarial(artifact_dir / "phase17_adversarial.json")
    report = verify_report(artifact_dir / "phase17_obstruction_report.md")
    return {
        "format": "collatz-phase17-verifier-v1", "valid": True,
        "claims": {"P104": "VERIFIED_THEOREM", "P105": "VERIFIED_THEOREM", "P106": "VERIFIED_THEOREM", "E28": "VERIFIED_FINITE", "E29": "VERIFIED_FINITE", "NG29": "REFUTED", "H104": "OPEN", "H105": "OPEN"},
        "checks": {"predecessor": predecessor, "direct": direct, "pressure": pressure, "suffix": suffix, "adversarial": adversarial, "obstruction_report": report},
        "independence": "No generator import; explicit affine sums, recursive compositions, descending orbit audit, and independently serialized rows.",
        "what_this_result_does_not_prove": "Verifier acceptance does not exclude either dichotomy branch and is not a proof of Collatz.",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.write_report is not None:
        args.write_report.write_text(text, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
