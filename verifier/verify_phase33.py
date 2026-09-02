#!/usr/bin/env python3
"""Independent exact verifier for Phase 33 artifacts.

This module imports neither ``src`` nor the Phase 33 generator.  It rebuilds
the logarithm/continued-fraction frontier, every low-q decision, and every
shortcut first-descent row with separately coded arithmetic.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


K = 1_564_920_000
OLD_BOUND = 300_000
NEW_BOUND = 583_561
EXPECTED_CLAIMS = {
    "P200": "VERIFIED_THEOREM", "P201": "VERIFIED_THEOREM",
    "E46": "VERIFIED_FINITE", "E47": "VERIFIED_FINITE",
    "H200": "RETRACTED", "H172": "OPEN", "H133": "OPEN",
}
CONFIGS = (
    (61, 929, 62, 2_800_000_000_000, 63, 2048, 2047),
    (117, 2241, 118, 5_500_000_000_000, 125, 4096, 4095),
)


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest_rows(rows: list[object]) -> str:
    answer = hashlib.sha256()
    for row in rows:
        answer.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
        answer.update(b"\n")
    return answer.hexdigest()


def fraction(pair: object) -> Fraction:
    if not isinstance(pair, list) or len(pair) != 2:
        fail("fraction encoding")
    return Fraction(int(pair[0]), int(pair[1]))


def raw_log(value: Fraction, terms: int = 384) -> tuple[Fraction, Fraction]:
    """Exact interval without the generator's dyadic rounding step."""
    if value <= 1:
        fail("log domain")
    z = (value - 1) / (value + 1)
    power = z
    total = Fraction(0)
    for index in range(terms):
        total += 2 * power / (2 * index + 1)
        power *= z * z
    remainder = 2 * power / ((2 * terms + 1) * (1 - z * z))
    return total, total + remainder


def rational_cf(value: Fraction) -> list[int]:
    result = []
    while value.denominator > 1:
        quotient, remainder = divmod(value.numerator, value.denominator)
        result.append(quotient)
        value = Fraction(value.denominator, remainder)
    result.append(value.numerator)
    return result


def shared_terms(left: Fraction, right: Fraction) -> tuple[int, ...]:
    result = []
    for first, second in zip(rational_cf(left), rational_cf(right), strict=False):
        if first != second:
            return tuple(result)
        result.append(first)
    return tuple(result)


def convergent_rows(terms: tuple[int, ...]) -> list[tuple[int, int]]:
    previous2, previous = (0, 1), (1, 0)
    answer = []
    for term in terms:
        current = (term * previous[0] + previous2[0], term * previous[1] + previous2[1])
        answer.append(current)
        previous2, previous = previous, current
    return answer


def ceiling_binary_log(value: Fraction) -> int:
    numerator, denominator = value.numerator, value.denominator
    guess = numerator.bit_length() - denominator.bit_length()
    while (numerator << max(-guess, 0)) < (denominator << max(guess, 0)):
        guess -= 1
    equality = (numerator << max(-guess, 0)) == (denominator << max(guess, 0))
    return guess if equality else guess + 1


def critical(q: int) -> int:
    return (3 ** q).bit_length()


def m_upper(q: int, length: int) -> int:
    top = q * (2 ** length)
    bottom = 3 * (2 ** length - 3 ** q)
    return (top - 1) // bottom


def p195_optimum(q: int, length: int, area: int, minimum: int) -> dict[str, int]:
    winner: tuple[int, ...] | None = None
    for h in range(1, area + 1):
        baseline = sum((r * q) // (length - q) for r in range(h))
        if h + baseline > area:
            break
        n = ceiling_binary_log(Fraction((2 ** (h + 2 + length)) * minimum, 3 ** q))
        z = ((length - q) * (n + 1) + length - 1) // length
        for j in range(h, area - baseline + 1):
            sigma = area - j - baseline
            e = min(j, h + sigma)
            right = (j + 2 * e) * (n + 1) + 6 * area
            right += (n + 3) * (3 + 2 * z + z * (z - 1) // 2)
            candidate = (right - 3 * length, h, j, sigma, e, n, z, right)
            winner = candidate if winner is None or candidate > winner else winner
    if winner is None:
        fail("P195 empty optimization")
    return dict(zip(("margin", "h", "J", "Sigma", "E", "n", "Z", "rhs"), winner, strict=True))


def reconstruct_low(area: int, maximum_q: int) -> dict[str, object]:
    counts = {"q_rows": 0, "reduced_denominator_rejections": 0,
              "P133_E28_rejections": 0, "P133_admissible": 0, "P195_survivors": 0}
    rows: list[object] = []
    survivors = []
    closest = None
    for q in range(971, maximum_q + 1):
        counts["q_rows"] += 1
        length = critical(q)
        divisor = math.gcd(q, length)
        reduced = q // divisor
        if reduced < 971:
            counts["reduced_denominator_rejections"] += 1
            row = [q, length, divisor, reduced, "q0"]
        else:
            minimum = m_upper(q, length)
            if minimum < OLD_BOUND:
                counts["P133_E28_rejections"] += 1
                row = [q, length, divisor, reduced, "P133_E28", minimum]
            else:
                counts["P133_admissible"] += 1
                best = p195_optimum(q, length, area, minimum)
                record = {"q": q, "L": length, "d": divisor, "q0": reduced,
                          "m_max": minimum, **best}
                if best["margin"] >= 0:
                    counts["P195_survivors"] += 1
                    survivors.append(record)
                elif closest is None or best["margin"] > closest["margin"]:
                    closest = record
                row = [q, length, divisor, reduced, "P195", minimum, *best.values()]
        rows.append(row)
    return {"area_ceiling": area, "q_range": [971, maximum_q], "counts": counts,
            "row_digest_sha256": digest_rows(rows), "survivors": survivors,
            "closest_failure": closest}


def cutoff(area: int, constant: int, coefficient: int, Q: int) -> dict[str, object]:
    power_q, power_12q = (42, 45) if area == 61 else (43, 46)
    margin = Fraction(19 * Q, 12) - (constant + coefficient * (power_q + power_12q * K))
    derivative = Fraction(3 * coefficient * (K + 1), 2 * Q)
    if margin <= 0 or derivative >= Fraction(19, 12):
        fail("cutoff inequality")
    return {"Q": Q, "alpha_lower": [19, 12], "log2_4Q_over_3_upper": power_q,
            "log2_12Q_upper": power_12q, "margin": [str(margin.numerator), str(margin.denominator)],
            "derivative_upper": [str(derivative.numerator), str(derivative.denominator)],
            "derivative_target": [19, 12]}


def reconstruct_frontier(config: tuple[int, ...], alpha: tuple[Fraction, Fraction],
                         convergents: list[tuple[int, int]]) -> dict[str, object]:
    area, constant, coefficient, Q, dmax, _, _ = config
    ln2, ln3 = raw_log(Fraction(2)), raw_log(Fraction(3))
    uppers = [(p, q) for p, q in convergents if 971 <= q < Q and Fraction(p, q) > alpha[1]]
    next_upper = next((p, q) for p, q in convergents if q >= Q and Fraction(p, q) > alpha[1])
    rows = []
    closest = None
    for p, q0 in uppers:
        error_low = p * ln2[0] - q0 * ln3[1]
        error_high = p * ln2[1] - q0 * ln3[0]
        for d in range(1, dmax + 1):
            q, length = d * q0, d * p
            if q >= Q:
                continue
            low, high = d * error_low, d * error_high
            if low <= 0 or high >= ln2[0]:
                continue
            log_bound = ceiling_binary_log(Fraction(4 * q, 3) / low)
            margin = constant + coefficient * log_bound - length
            row = [p, q0, d, length, q, log_bound, margin]
            rows.append(row)
            closest = row if closest is None or margin > closest[-1] else closest
            if margin >= 0:
                fail("frontier survivor")
    return {"area_ceiling": area, "upper_convergents": [list(value) for value in uppers],
            "next_upper_convergent": list(next_upper), "candidate_count": len(rows),
            "candidate_digest_sha256": digest_rows(rows), "closest_coarse_upper_margin": closest,
            "gap_lower_bound": "lambda(1-lambda)>delta_log/4"}


def verify_scalar(stored: dict[str, object]) -> list[int]:
    ln2, ln3 = raw_log(Fraction(2)), raw_log(Fraction(3))
    tight_alpha = (ln3[0] / ln2[1], ln3[1] / ln2[0])
    recorded = tuple(fraction(item) for item in stored.get("log2_three_interval", []))
    if len(recorded) != 2 or not recorded[0] <= tight_alpha[0] <= tight_alpha[1] <= recorded[1]:
        fail("scalar alpha enclosure")
    terms = shared_terms(*recorded)
    if list(terms) != stored.get("continued_fraction_prefix"):
        fail("continued fraction prefix")
    convergents = convergent_rows(terms)
    tiers = stored.get("tiers")
    if not isinstance(tiers, list) or len(tiers) != 2:
        fail("scalar tiers")
    frontier_counts = []
    for configuration, actual in zip(CONFIGS, tiers, strict=True):
        area, constant, coefficient, Q, dmax, legendre, qmax = configuration
        expected_configuration = {"area": area, "constant": constant, "coefficient": coefficient,
                                  "cutoff": Q, "d_max": dmax, "legendre_q": legendre,
                                  "low_q_max": qmax}
        if actual.get("configuration") != expected_configuration:
            fail("tier configuration")
        if actual.get("cutoff") != cutoff(area, constant, coefficient, Q):
            fail("cutoff reconstruction")
        frontier = reconstruct_frontier(configuration, recorded, convergents)
        if actual.get("frontier") != frontier:
            fail("continued fraction frontier reconstruction")
        low = reconstruct_low(area, qmax)
        if actual.get("low_q") != low:
            fail("low-q reconstruction")
        frontier_counts.append(frontier["candidate_count"])
    expected_obstructions = [
        {"q": 971, "L": 1539, "A": 62, "m_max": m_upper(971, 1539),
         **p195_optimum(971, 1539, 62, m_upper(971, 1539))},
        {"q": 1636, "L": 2593, "A": 118, "m_max": m_upper(1636, 2593),
         **p195_optimum(1636, 2593, 118, m_upper(1636, 2593))},
    ]
    if stored.get("obstructions") != expected_obstructions or stored.get("proves_collatz") is not False:
        fail("scalar obstruction boundary")
    return frontier_counts


def iterate_first_lower(source: int) -> tuple[int, int]:
    value = source
    for count in range(1, 10_000):
        value = (3 * value + 1) // 2 if value % 2 else value // 2
        if value < source:
            return count, value
    fail("trajectory did not descend")


def verify_descent(csv_path: Path, summary: dict[str, object]) -> dict[str, object]:
    digest = hashlib.sha256()
    first_max = (-1, -1, -1)
    second_max = (-1, -1, -1)
    count = 0
    expected_source = OLD_BOUND + 1
    with csv_path.open("r", encoding="ascii", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["source", "steps", "first_lower"]:
            fail("descent header")
        for item in reader:
            source, steps, lower = int(item["source"]), int(item["steps"]), int(item["first_lower"])
            if source != expected_source:
                fail("descent source sequence")
            rebuilt = iterate_first_lower(source)
            if rebuilt != (steps, lower):
                fail("descent trajectory reconstruction")
            digest.update(f"{source},{steps},{lower}\n".encode("ascii"))
            record = (steps, source, lower)
            if source <= 330_911 and record > first_max:
                first_max = record
            if source >= 330_913 and record > second_max:
                second_max = record
            count += 1
            expected_source += 2
    expected = {
        "format": "collatz-phase33-descent-summary-v1", "certificate": csv_path.name,
        "prior_verified_bound": OLD_BOUND, "new_verified_bound_exclusive": NEW_BOUND,
        "odd_sources": count, "row_digest_sha256": digest.hexdigest(),
        "first_interval": {"range": [300_000, 330_911], "maximum": list(first_max)},
        "second_interval": {"range": [330_912, 583_560], "maximum": list(second_max)},
        "induction": "E28 plus one-step parity reduction for even values and certified first-lower iterates for odd values proves convergence below 583561 by strong induction.",
        "proves_collatz": False,
    }
    if expected_source != NEW_BOUND or summary != expected:
        fail("descent summary reconstruction")
    return {"odd_sources": count, "first_maximum": list(first_max), "second_maximum": list(second_max)}


def verify(directory: Path) -> dict[str, object]:
    names = ("phase33_theory.json", "phase33_scalar_audit.json", "phase33_descent_summary.json",
             "phase33_descent_certificate.csv", "phase33_regressions.json", "phase33_obstruction_report.md")
    paths = [directory / name for name in names]
    theory, scalar, descent, regressions = (load(paths[index]) for index in (0, 1, 2, 4))
    report = paths[5].read_text(encoding="utf-8")
    if not isinstance(theory, dict) or theory.get("claims") != EXPECTED_CLAIMS or theory.get("proves_collatz") is not False:
        fail("theory artifact mismatch")
    if "retracted" not in theory.get("H200", {}).get("closure", ""):
        fail("H200 closure boundary")
    if not isinstance(scalar, dict) or scalar.get("format") != "collatz-phase33-scalar-audit-v1":
        fail("scalar artifact")
    frontier_counts = verify_scalar(scalar)
    if not isinstance(descent, dict):
        fail("descent artifact")
    descent_result = verify_descent(paths[3], descent)
    required = {"2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^1B^1", "A^2B^3"}
    if not isinstance(regressions, dict) or regressions.get("proves_collatz") is not False:
        fail("regression boundary")
    if {row[0] for row in regressions.get("mandatory_families", [])} != required:
        fail("mandatory adversarial families")
    for phrase in ("next scalar survivor", "does not", "proves_collatz=false"):
        if phrase not in report:
            fail("obstruction report boundary")
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    roots = {alias.name.split(".", 1)[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".", 1)[0] for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module)
    generator_tail = "phase33_" + "search"
    imported_generator = any(name.endswith(generator_tail) for name in sys.modules)
    if imported_generator or "src" in roots:
        fail("generator independence")
    return {
        "format": "collatz-phase33-independent-verifier-v1", "valid": True,
        "generator_imported": False, "claims": EXPECTED_CLAIMS,
        "frontier_counts": frontier_counts, "descent": descent_result,
        "verified_input_sha256": {path.name: digest_file(path) for path in paths},
        "independence": "separate rational log series, CF reconstruction, scalar optimizer, and trajectory iterator",
        "what_this_result_does_not_prove": "Finite area floors do not exclude arbitrary-area cycles, nonperiodic orbits, or prove Collatz.",
        "proves_collatz": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (VerificationError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        raise SystemExit(1) from exc
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")


if __name__ == "__main__":
    main()
