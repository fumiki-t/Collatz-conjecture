#!/usr/bin/env python3
"""Independent exact verifier for Phase 35 artifacts.

No generator or ``src`` module is imported.  The verifier reconstructs the
complete critical-safe decoder corpus and both corrected joint scalar audits.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Iterable, Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


MATVEEV = 1_564_920_000
CUTOFF = 11_500_000_000_000
FINITE_BOUND = 583_561
CLAIMS = {"P206": "VERIFIED_THEOREM", "P207": "VERIFIED_THEOREM",
          "P208": "VERIFIED_THEOREM", "P209": "VERIFIED_THEOREM",
          "P210": "VERIFIED_THEOREM", "E49": "VERIFIED_FINITE",
          "E50": "VERIFIED_FINITE", "NG41": "REFUTED",
          "H89": "OPEN", "H133": "OPEN", "H172": "OPEN"}
FILES = ("phase35_theory.json", "phase35_decoder_audit.json",
         "phase35_joint_scalar_audit.json", "phase35_regressions.json",
         "phase35_obstruction_report.md")


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows_digest(rows: Iterable[object]) -> str:
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def critical_length(q: int) -> int:
    return (3 ** q).bit_length()


def safe_positions(q: int) -> Iterable[tuple[int, ...]]:
    ceilings = tuple(critical_length(j) - 1 for j in range(q))

    def visit(items: tuple[int, ...], j: int) -> Iterable[tuple[int, ...]]:
        if j == q:
            yield items
            return
        for value in range(items[-1] + 1, ceilings[j] + 1):
            yield from visit(items + (value,), j + 1)

    if q == 1:
        yield (0,)
    else:
        yield from visit((0,), 1)


def affine_b(q: int, positions: Sequence[int]) -> int:
    answer = 0
    for label, position in enumerate(positions):
        answer += 3 ** (q - label - 1) * 2 ** position
    return answer


def valuation2(value: int) -> int:
    if value == 0:
        fail("zero decoder remainder")
    exponent = 0
    while value % 2 == 0:
        exponent += 1
        value //= 2
    return exponent


def reconstruct_profile(q: int, source: int) -> tuple[int, ...]:
    length = critical_length(q)
    modulus = 2 ** length
    mechanical = tuple(critical_length(j) - 1 for j in range(q))
    remainder = (affine_b(q, mechanical) - source * (modulus - 3 ** q)) % modulus
    profile = [0] * q
    least_label = 1
    prior = 0
    while remainder:
        position = valuation2(remainder)
        label = q
        for candidate in range(least_label, q):
            if mechanical[candidate] > position:
                label = candidate
                break
        if label == q or position <= prior:
            fail("decoder label/position")
        amount = mechanical[label] - position
        profile[label] = amount
        remainder = (remainder - 3 ** (q - label - 1) * 2 ** position
                     * (2 ** amount - 1)) % modulus
        least_label = label + 1
        prior = position
    return tuple(profile)


def orbit_endpoint(source: int, positions: Sequence[int], length: int) -> int:
    positions_set = set(positions)
    value = source
    for index in range(length):
        if bool(value % 2) != (index in positions_set):
            fail("literal parity cylinder")
        value = (3 * value + 1) // 2 if value % 2 else value // 2
    return value


def rebuild_decoder() -> dict[str, object]:
    digest = hashlib.sha256()
    counts, samples = [], []
    total = box_count = 0
    for q in range(1, 19):
        length = critical_length(q)
        modulus = 2 ** length
        mechanical = tuple(critical_length(j) - 1 for j in range(q))
        mechanical_b = affine_b(q, mechanical)
        inverse = pow(3 ** q, -1, modulus)
        count = 0
        for positions in safe_positions(q):
            word_b = affine_b(q, positions)
            source = (-word_b * inverse) % modulus
            expected = tuple(mechanical[j] - positions[j] for j in range(q))
            decoded = reconstruct_profile(q, source)
            if decoded != expected:
                fail("decoder reconstruction")
            endpoint = orbit_endpoint(source, positions, length)
            displacement = endpoint - source
            if mechanical_b - source * (modulus - 3 ** q) != (
                    mechanical_b - word_b + modulus * displacement):
                fail("endpoint displacement identity")
            in_box = 0 <= 3 * displacement < q
            row = (q, length, positions, source, displacement, decoded, int(in_box))
            digest.update(repr(row).encode("ascii") + b"\n")
            if len(samples) < 12:
                samples.append([q, length, list(positions), source, displacement,
                                list(decoded), in_box])
            count += 1
            total += 1
            box_count += int(in_box)
        counts.append([q, length, count])
    if total != 1_166_058:
        fail("decoder word total")
    return {"format": "collatz-phase35-decoder-audit-v1", "q_range": [1, 18],
            "counts_by_q": counts, "total_words": total, "p98_box_words": box_count,
            "row_digest_sha256": digest.hexdigest(), "samples": samples,
            "decision_boundary": "The decoder reconstructs a valid word; it does not produce a smaller P89 ancestor.",
            "proves_collatz": False}


def ceil_log2(value: Fraction) -> int:
    numerator, denominator = value.numerator, value.denominator
    exponent = numerator.bit_length() - denominator.bit_length()

    def power_is_at_least(power: int) -> bool:
        if power >= 0:
            return (denominator << power) >= numerator
        return denominator >= (numerator << -power)

    while not power_is_at_least(exponent):
        exponent += 1
    while power_is_at_least(exponent - 1):
        exponent -= 1
    return exponent


def p133_max(q: int, length: int) -> int:
    return (q * 2 ** length - 1) // (3 * (2 ** length - 3 ** q))


def profile_max(q: int, length: int, area: int, height: int) -> int:
    numerator = 4 * 2 ** length * (q * height + area * (2 ** height - 1))
    denominator = 3 * (2 ** length - 3 ** q) * height * 2 ** height
    return (numerator - 1) // denominator


def candidates(q: int, length: int, area: int) -> list[dict[str, int]]:
    answer = []
    p133 = p133_max(q, length)
    for height in range(1, area + 1):
        baseline = sum(level * q // (length - q) for level in range(height))
        if height + baseline > area:
            break
        prof = profile_max(q, length, area, height)
        state = min(p133, prof)
        if state < FINITE_BOUND:
            continue
        width = ceil_log2(Fraction(2 ** (height + 2 + length) * state, 3 ** q))
        zeroes = ((length - q) * (width + 1) + length - 1) // length
        for components in range(height, area - baseline + 1):
            surplus = area - components - baseline
            exceptional = min(components, height + surplus)
            residual_area = area - components + exceptional
            residual_span = min(2 * residual_area,
                                length * residual_area // q + exceptional)
            triple = ((components + 2 * exceptional) * (width + 1)
                      + 3 * residual_span
                      + (width + 3) * (3 + 2 * zeroes + zeroes * (zeroes - 1) // 2))
            factor = (width + 1 + components * (width - 1)
                      + min(2 * area, length * area // q + components))
            answer.append({"T35C_margin": triple - 3 * length,
                           "T35B_margin": factor - length,
                           "h": height, "J": components, "Sigma": surplus,
                           "E": exceptional, "n": width, "Z": zeroes,
                           "m_max": state, "m_P133": p133, "m_prof": prof,
                           "A_res": residual_area, "T_res": residual_span,
                           "T35C_rhs": triple, "T35B_rhs": factor})
    return answer


def rebuild_low(area: int) -> dict[str, object]:
    counts = {"q_rows": 0, "q0_rejections": 0, "state_E46_rejections": 0,
              "T35C_rejections": 0, "T35B_rejections": 0, "joint_survivors": 0}
    rows, survivors = [], []
    closest = None
    for q in range(971, 8192):
        counts["q_rows"] += 1
        length = critical_length(q)
        divisor = math.gcd(q, length)
        reduced = q // divisor
        if reduced < 971:
            counts["q0_rejections"] += 1
            row = [q, length, divisor, reduced, "q0"]
        else:
            available = candidates(q, length, area)
            if not available:
                counts["state_E46_rejections"] += 1
                row = [q, length, divisor, reduced, "state_E46"]
            else:
                pass_c = [item for item in available if item["T35C_margin"] >= 0]
                if not pass_c:
                    counts["T35C_rejections"] += 1
                    best = max(available, key=lambda x: x["T35C_margin"])
                    row = [q, length, divisor, reduced, "T35C", *best.values()]
                else:
                    pass_b = [item for item in pass_c if item["T35B_margin"] >= 0]
                    if not pass_b:
                        counts["T35B_rejections"] += 1
                        best = max(pass_c, key=lambda x: x["T35B_margin"])
                        row = [q, length, divisor, reduced, "T35B", *best.values()]
                    else:
                        counts["joint_survivors"] += 1
                        best = max(pass_b, key=lambda x: min(x["T35B_margin"], x["T35C_margin"]))
                        survivors.append({"q": q, "L": length, "d": divisor,
                                          "q0": reduced, **best})
                        row = [q, length, divisor, reduced, "survivor", *best.values()]
                score = min(best["T35B_margin"], best["T35C_margin"])
                if closest is None or score > min(closest["T35B_margin"],
                                                   closest["T35C_margin"]):
                    closest = {"q": q, "L": length, "d": divisor,
                               "q0": reduced, **best}
        rows.append(row)
    return {"area_ceiling": area, "q_range": [971, 8191], "counts": counts,
            "row_digest_sha256": rows_digest(rows), "survivors": survivors,
            "closest_joint_row": closest}


def raw_log(value: Fraction, terms: int = 384) -> tuple[Fraction, Fraction]:
    z = (value - 1) / (value + 1)
    power, total = z, Fraction()
    for index in range(terms):
        total += 2 * power / (2 * index + 1)
        power *= z * z
    return total, total + 2 * power / ((2 * terms + 1) * (1 - z * z))


def continued_fraction(value: Fraction) -> list[int]:
    result = []
    while value.denominator != 1:
        quotient, remainder = divmod(value.numerator, value.denominator)
        result.append(quotient)
        value = Fraction(value.denominator, remainder)
    result.append(value.numerator)
    return result


def shared_prefix(left: Fraction, right: Fraction) -> tuple[int, ...]:
    result = []
    for a, b in zip(continued_fraction(left), continued_fraction(right), strict=False):
        if a != b:
            break
        result.append(a)
    return tuple(result)


def convergents(terms: Sequence[int]) -> list[tuple[int, int]]:
    p2, p1, q2, q1 = 0, 1, 1, 0
    result = []
    for term in terms:
        p, q = term * p1 + p2, term * q1 + q2
        result.append((p, q))
        p2, p1, q2, q1 = p1, p, q1, q
    return result


def rebuild_frontier(d_max: int) -> dict[str, object]:
    ln2, ln3 = raw_log(Fraction(2)), raw_log(Fraction(3))
    alpha = ln3[0] / ln2[1], ln3[1] / ln2[0]
    prefix = shared_prefix(*alpha)
    uppers = [(p, q) for p, q in convergents(prefix)
              if 971 <= q < CUTOFF and Fraction(p, q) > alpha[1]]
    rows, closest = [], None
    for p, reduced in uppers:
        base_low = p * ln2[0] - reduced * ln3[1]
        base_high = p * ln2[1] - reduced * ln3[0]
        for divisor in range(1, d_max + 1):
            q, length = divisor * reduced, divisor * p
            if q >= CUTOFF:
                continue
            low, high = divisor * base_low, divisor * base_high
            if low <= 0 or high >= ln2[0]:
                continue
            log_bound = ceil_log2(Fraction(4 * q, 3) / low)
            margin = 5950 + 238 * log_bound - length
            row = [p, reduced, divisor, length, q, log_bound, margin]
            rows.append(row)
            if closest is None or margin > closest[-1]:
                closest = row
            if margin >= 0:
                fail("unexpected frontier survivor")
    return {"d_max": d_max, "upper_convergents": [list(x) for x in uppers],
            "continued_fraction_prefix": list(prefix), "candidate_count": len(rows),
            "candidate_digest_sha256": rows_digest(rows),
            "closest_coarse_upper_margin": closest}


def expected_scalar() -> dict[str, object]:
    margin = Fraction(19 * CUTOFF, 12) - (5950 + 238 * (44 + 47 * MATVEEV))
    derivative = Fraction(3 * 238 * (MATVEEV + 1), 2 * CUTOFF)
    low228, low229, low237 = rebuild_low(228), rebuild_low(229), rebuild_low(237)
    if low228["survivors"] or len(low229["survivors"]) != 1:
        fail("corrected scalar boundary")
    displayed = next(item for item in candidates(2301, 3647, 209)
                     if (item["h"], item["J"], item["Sigma"], item["E"],
                         item["n"], item["Z"]) == (2, 105, 103, 105, 24, 10))
    return {"format": "collatz-phase35-joint-scalar-audit-v1",
            "cutoff": {"Q": CUTOFF, "envelope_constant": 5950,
                       "envelope_coefficient": 238, "log2_3_lower": [19, 12],
                       "log2_4Q_over_3_upper": 44, "log2_12Q_upper": 47,
                       "margin": [str(margin.numerator), str(margin.denominator)],
                       "derivative_upper": [str(derivative.numerator), str(derivative.denominator)],
                       "derivative_target": [19, 12]},
            "legendre": {"threshold_q": 8192,
                         "correct_threshold_exponent": [-535, 357],
                         "proposal_exponent": [-3073, 714], "proposal_matches": False},
            "area_228_gcd": {"strict_upper": [7072, 27], "integer_maximum": 261},
            "area_228_frontier": rebuild_frontier(261),
            "area_228_low_q": low228, "next_obstruction": low229["survivors"][0],
            "proposal_area_237_audit": {"gcd_integer_maximum": 273,
                                          "frontier": rebuild_frontier(273),
                                          "low_q": low237},
            "displayed_area209_tuple": {"q": 2301, "L": 3647, "A": 209, **displayed},
            "proposal_discrepancies": {
                "cutoff_margin_claimed": 651_592_977_457,
                "cutoff_margin_reconstructed": [str(margin.numerator), str(margin.denominator)],
                "frontier_candidates_claimed": 1908,
                "frontier_candidates_reconstructed_d273": 1996,
                "area238_conclusion": "REFUTED as a consequence of the stated joint scalar sieve by the A=229 tuple"},
            "proves_collatz": False}


def verify(artifact_dir: Path) -> dict[str, object]:
    theory = load(artifact_dir / FILES[0])
    decoder = load(artifact_dir / FILES[1])
    scalar = load(artifact_dir / FILES[2])
    regressions = load(artifact_dir / FILES[3])
    report = (artifact_dir / FILES[4]).read_text(encoding="utf-8")
    if not isinstance(theory, dict) or theory.get("claims") != CLAIMS or theory.get("proves_collatz") is not False:
        fail("theory artifact mismatch")
    if not isinstance(decoder, dict) or decoder.get("format") != "collatz-phase35-decoder-audit-v1" or decoder.get("proves_collatz") is not False:
        fail("decoder boundary mismatch")
    if not isinstance(scalar, dict) or scalar.get("format") != "collatz-phase35-joint-scalar-audit-v1" or scalar.get("proves_collatz") is not False:
        fail("scalar boundary mismatch")
    if not isinstance(regressions, dict) or regressions.get("proves_collatz") is not False:
        fail("regression boundary mismatch")
    if "A>=229" not in report or "proves_collatz=false" not in report:
        fail("obstruction report boundary")
    if decoder != rebuild_decoder():
        fail("decoder reconstruction mismatch")
    reconstructed_scalar = expected_scalar()
    for path in (("area_228_frontier",), ("proposal_area_237_audit", "frontier")):
        stored_frontier = scalar
        rebuilt_frontier = reconstructed_scalar
        for key in path:
            stored_frontier = stored_frontier[key]
            rebuilt_frontier = rebuilt_frontier[key]
        stored_prefix = stored_frontier.get("continued_fraction_prefix")
        rebuilt_prefix = rebuilt_frontier.get("continued_fraction_prefix")
        if (not isinstance(stored_prefix, list)
                or stored_prefix != rebuilt_prefix[:len(stored_prefix)]
                or stored_frontier.get("upper_convergents") != rebuilt_frontier.get("upper_convergents")):
            fail("continued fraction enclosure mismatch")
        rebuilt_frontier["continued_fraction_prefix"] = stored_prefix
    if scalar != reconstructed_scalar:
        fail("joint scalar reconstruction mismatch")
    generator_tail = "phase35_" + "search"
    imported = generator_tail in Path(__file__).read_text(encoding="utf-8")
    if imported:
        fail("generator reference")
    return {"valid": True, "claims": CLAIMS, "generator_imported": False,
            "decoded_words": decoder["total_words"],
            "area228_frontier_candidates": scalar["area_228_frontier"]["candidate_count"],
            "low_q_rows": scalar["area_228_low_q"]["counts"]["q_rows"],
            "next_obstruction": scalar["next_obstruction"],
            "verified_sha256": {name: file_digest(artifact_dir / name) for name in FILES},
            "proves_collatz": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except VerificationError as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}))
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
