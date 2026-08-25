#!/usr/bin/env python3
"""Independent verifier for Phase 13 renewal-code evidence.

This module deliberately does not import the Phase 13 generator.  It rebuilds
finite states, affine data, residues, digests, extrema, and obstruction rows
using separate data structures and control flow.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from decimal import Decimal, getcontext
from fractions import Fraction
from math import isqrt
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

getcontext().prec = 50

ABLOCK = "11101"
BBLOCK = "1100"


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read {path.name}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.name} is not an object")
    return data


def ef(value: Fraction) -> dict[str, object]:
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
        "decimal": f"{Decimal(value.numerator) / Decimal(value.denominator):.24f}",
    }


def parsed_fraction(value: object) -> Fraction:
    if not isinstance(value, dict):
        fail("fraction object missing")
    try:
        return Fraction(int(str(value["numerator"])), int(str(value["denominator"])))
    except (KeyError, ValueError, ZeroDivisionError) as exc:
        fail(f"invalid fraction: {exc}")


def strict_up(length: int, ones: int) -> bool:
    return pow(3, ones) > pow(2, length)


def reconstruct_pressure(depth: int) -> dict[str, object]:
    # State index is the number of ones; entries are surviving word counts.
    states = [1]
    totals = [Fraction() for _ in range(5)]  # kappa, weighted, sigma, tau, nu
    selected = []
    crossings_total = 0
    wanted = {x for x in (20, 50, 100, 200, depth) if x <= depth}
    for length in range(1, depth + 1):
        following = [0] * (len(states) + 1)
        crossing_rows = []
        for ones, count in enumerate(states):
            following[ones] += count
            if strict_up(length, ones + 1):
                crossing_rows.append((ones + 1, count))
            else:
                following[ones + 1] += count
        states = following
        for ones, count in crossing_rows:
            crossings_total += count
            totals[0] += Fraction(count, pow(2, length))
            totals[1] += Fraction(count * pow(3, ones), pow(2, 2 * length))
            totals[2] += Fraction(count, pow(3, ones))
            totals[3] += Fraction(count, pow(2, length) * pow(3, ones))
            totals[4] += Fraction(count, pow(4, length))
        if length in wanted:
            selected.append(
                {
                    "length": length,
                    "kappa": ef(totals[0]),
                    "weighted": ef(totals[1]),
                    "sigma": ef(totals[2]),
                    "tau": ef(totals[3]),
                    "nu": ef(totals[4]),
                    "active_state_count": sum(count != 0 for count in states),
                    "active_word_count": str(sum(states)),
                }
            )
    return {
        "depth": depth,
        "crossing_word_count": str(crossings_total),
        "checkpoints": selected,
        "final": selected[-1],
    }


def verify_renewal(data: dict[str, object]) -> None:
    if data.get("format") != "collatz-phase13-renewal-code-v1" or data.get("proves_collatz") is not False:
        fail("P77 artifact boundary")
    claim = data.get("P77")
    if not isinstance(claim, dict) or claim.get("repository_status") != "VERIFIED_THEOREM":
        fail("P77 status")
    if claim.get("orientation") != "w_i=s_[t_i,t_(i+1)) is the forward block and u_i=reverse(w_i)":
        fail("P77 block orientation")
    if "unique argmin" not in str(claim.get("strict_suffix_minimum")):
        fail("P77 uniqueness")
    if "w=u=1" not in str(claim.get("endpoint_bits")):
        fail("P77 length-one exception")
    if claim.get("code_property") != "the first-upcrossing family U is prefix-free":
        fail("P77 prefix-free status")
    if "3B+2^j" not in str(claim.get("affine_recurrence")):
        fail("P77 affine recurrence")


def verify_pressure(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase13-pressure-v1" or data.get("proves_collatz") is not False:
        fail("P78 artifact boundary")
    theorem = data.get("P78")
    if not isinstance(theorem, dict) or theorem.get("repository_status") != "VERIFIED_THEOREM":
        fail("P78 status")
    if theorem.get("weighted_identity") != "sum_(u in U) 2^(-L(u))*c(u)=1":
        fail("P78 weighted Kraft identity")
    bounds = theorem.get("bounds")
    if bounds != {"kappa": "<3/4", "sigma": "<7/12", "tau": "<19/96", "nu": "<9/32"}:
        fail("P78 analytic bounds")
    expected_bounds = {
        "kappa": ef(Fraction(3, 4)),
        "sigma": ef(Fraction(7, 12)),
        "tau": ef(Fraction(19, 96)),
        "nu": ef(Fraction(9, 32)),
    }
    if data.get("exact_upper_bounds") != expected_bounds:
        fail("P78 exact bound encodings")
    stored = data.get("E22_pressure_dp")
    if not isinstance(stored, dict) or not isinstance(stored.get("depth"), int):
        fail("E22 pressure DP parameters")
    expected = reconstruct_pressure(stored["depth"])
    if stored != expected:
        fail("E22 weighted Kraft identity or finite DP")
    final = expected["final"]
    if not parsed_fraction(final["kappa"]) < Fraction(3, 4):
        fail("E22 kappa upper bound")
    if not parsed_fraction(final["sigma"]) < Fraction(7, 12):
        fail("E22 sigma upper bound")
    if not parsed_fraction(final["tau"]) < Fraction(19, 96):
        fail("E22 tau upper bound")
    if not parsed_fraction(final["nu"]) < Fraction(9, 32):
        fail("E22 nu upper bound")
    return stored["depth"]


def correction(bits: str) -> int:
    # Compose affine pairs from the right: (a*x+b)/d.
    multiplier, translation, denominator = 1, 0, 1
    for bit in bits:
        if bit == "1":
            multiplier *= 3
            translation = 3 * translation + denominator
        elif bit != "0":
            fail("non-binary block")
        denominator *= 2
    return translation


def crossing_words(q_cap: int) -> list[tuple[str, str, int, int, int]]:
    maximum_length = pow(3, q_cap).bit_length() - 1
    frontier = [("", 0)]
    complete = []
    for length in range(1, maximum_length + 1):
        following = []
        for prefix, ones in frontier:
            following.append((prefix + "0", ones))
            if ones < q_cap:
                word = prefix + "1"
                if strict_up(length, ones + 1):
                    forward = word[::-1]
                    complete.append((word, forward, length, ones + 1, correction(forward)))
                else:
                    following.append((word, ones + 1))
        frontier = following
    return complete


def vtwo(value: int) -> int:
    if value <= 0:
        fail("positive valuation input required")
    result = 0
    while value % 2 == 0:
        result += 1
        value //= 2
    return result


def expected_threshold(q_cap: int) -> dict[str, object]:
    words = crossing_words(q_cap)
    digest = hashlib.sha256()
    distribution: Counter[int] = Counter()
    equalities = []
    selected = []
    for code, forward, length, ones, B in words:
        distribution[ones] += 1
        R = Fraction(B + pow(2, length), pow(3, ones))
        if forward != "1":
            C, remainder = divmod(B + pow(2, length) - pow(3, ones), 4)
            if remainder or C < pow(2, length - 3):
                fail("P79 C_w integrality or lower bound")
            run = len(forward) - len(forward.lstrip("1"))
            if vtwo(C) != run - 2:
                fail("P79 C_w valuation")
        else:
            C, run = 0, 1
        if R == Fraction(13, 9):
            equalities.append(forward)
        digest.update(
            f"{code}|{forward}|{length}|{ones}|{B}|{R.numerator}/{R.denominator}|{C}|{run}\n".encode(
                "ascii"
            )
        )
        if forward in {"1", "110", "111100", "111010", "111011100"}:
            selected.append(
                {
                    "code": code,
                    "forward": forward,
                    "L": length,
                    "q": ones,
                    "B": B,
                    "R": ef(R),
                    "C": C,
                    "initial_one_run": run,
                }
            )
    return {
        "maximum_q": q_cap,
        "block_count": len(words),
        "q_distribution": {str(key): value for key, value in sorted(distribution.items())},
        "q3_count": distribution[3],
        "R_13_over_9_words": equalities,
        "row_digest_sha256": digest.hexdigest(),
        "selected_rows": selected,
    }


def verify_threshold(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase13-threshold-bridge-v1" or data.get("proves_collatz") is not False:
        fail("P79 artifact boundary")
    claim = data.get("P79")
    if not isinstance(claim, dict) or claim.get("repository_status") != "VERIFIED_THEOREM":
        fail("P79 status")
    if "equality only for w=110" not in str(claim.get("threshold")):
        fail("P79 R=13/9 equality word")
    if "2^r|(S+1)" not in str(claim.get("positive_source_bridge")):
        fail("P79 positive-source divisibility step")
    transfer = claim.get("normalized_transfer")
    if not isinstance(transfer, dict) or "v2(C_w)=r-2" not in str(transfer.get("valuation")):
        fail("P79 normalized valuation")
    finite = data.get("finite_block_audit")
    if not isinstance(finite, dict) or not isinstance(finite.get("maximum_q"), int):
        fail("P79 finite block audit")
    expected = expected_threshold(finite["maximum_q"])
    if finite != expected:
        fail("P79 threshold or valuation reconstruction")
    if expected["R_13_over_9_words"] != ["110"] or expected["q3_count"] != 0:
        fail("P79 equality or q=3 absence")
    return finite["maximum_q"]


def int_hash(value: int) -> str:
    width = max(1, (value.bit_length() + 7) // 8)
    return hashlib.sha256(value.to_bytes(width, byteorder="big")).hexdigest()


def expected_critical(steps: int) -> dict[str, object]:
    f = A = E = B = 0
    previous_b = None
    exponents = []
    A_values = [0]
    residues = [0]
    digest = hashlib.sha256()
    wanted = {x for x in (64, 256, 1024, steps) if x <= steps}
    selected = []
    last_change = 0
    current_equal = longest_equal = 0
    for j in range(steps):
        f_next = pow(3, j + 1).bit_length() - 1
        b = f_next - f
        if previous_b == b == 1:
            fail("NG22 square-root b sequence")
        raise_A = b == 2 and A < isqrt(j + 1)
        A_next = A + int(raise_A)
        e = b - int(raise_A)
        B = 3 * B + pow(2, E)
        E += e
        modulus = pow(2, E)
        inverse = pow(pow(3, j + 1, modulus), -1, modulus)
        residue = (-B * inverse) % modulus
        if residue == residues[-1]:
            current_equal += 1
            longest_equal = max(longest_equal, current_equal)
        else:
            current_equal = 0
            last_change = j + 1
        exponents.append(e)
        A_values.append(A_next)
        residues.append(residue)
        digest.update(f"{j + 1}|{b}|{A_next}|{e}|{E}|{residue}\n".encode("ascii"))
        if j + 1 in wanted:
            selected.append(
                {
                    "odd_index": j + 1,
                    "f": f_next,
                    "A": A_next,
                    "E": E,
                    "residue_bit_length": residue.bit_length(),
                    "residue_sha256_big_endian": int_hash(residue),
                }
            )
        f, A, previous_b = f_next, A_next, b
    partial = sum((Fraction(1, pow(2, a)) for a in A_values), Fraction())
    exclusion = sum(exponents[: last_change - 1]) if last_change else 0
    return {
        "odd_steps": steps,
        "full_shortcut_length": sum(exponents),
        "first_64_exponents": "".join(map(str, exponents[:64])),
        "final_f": f,
        "final_A": A,
        "final_E": E,
        "partial_sum_2_minus_A": ef(partial),
        "row_digest_sha256": digest.hexdigest(),
        "checkpoints": selected,
        "latest_residue_change_index": last_change,
        "maximum_consecutive_unchanged_lifts": longest_equal,
        "last_lift_changed": residues[-1] != residues[-2],
        "finite_source_exclusion": f"no positive ordinary source below 2^{exclusion} realizes the first {last_change} exponents",
        "finite_source_exclusion_power": exclusion,
    }


def verify_critical(data: dict[str, object]) -> int:
    if data.get("format") != "collatz-phase13-critical-countermodel-v1" or data.get("proves_collatz") is not False:
        fail("NG22 critical artifact boundary")
    claim = data.get("NG22_additional_evidence")
    if not isinstance(claim, dict) or claim.get("repository_status") != "REFUTED":
        fail("NG22 status")
    if claim.get("positive_ordinary_source") != "OPEN":
        fail("NG22 positive ordinary source boundary")
    finite = data.get("finite_audit")
    if not isinstance(finite, dict) or not isinstance(finite.get("odd_steps"), int):
        fail("NG22 finite audit")
    expected = expected_critical(finite["odd_steps"])
    if finite != expected:
        fail("NG22 critical recurrence or canonical residue digest")
    return finite["odd_steps"]


def source_endpoint(bits: str) -> tuple[int, int, int, int, int]:
    L = len(bits)
    Q = bits.count("1")
    B = correction(bits)
    m2, m3 = pow(2, L), pow(3, Q)
    r2 = (-B * pow(pow(3, Q), -1, m2)) % m2
    r3 = (B * pow(m2, -1, m3)) % m3
    return L, Q, B, r2, r3


def construct_addresses(words: list[tuple[str, str, int, int, int]], blocks: int, q_cap: int) -> list[tuple]:
    rows = [((), "", 0, 0, 0, 0, 0)]
    for _ in range(blocks):
        following = []
        for codes, bits, q_before, _L_before, _B_before, _r2_before, _r3_before in rows:
            for code, forward, _length, q, _B in words:
                if q_before + q <= q_cap:
                    new_bits = bits + forward
                    L, Q, B, r2, r3 = source_endpoint(new_bits)
                    following.append((codes + (code,), new_bits, Q, L, B, r2, r3))
        rows = following
    return rows


def positive(residue: int, modulus: int) -> int:
    return residue if residue else modulus


def lattice_count(H: int, r: int, modulus: int) -> int:
    least = positive(r, modulus)
    return 0 if H < least else 1 + (H - least) // modulus


def max_ratio(values: list[int], mass: Fraction, squared: bool) -> dict[str, object]:
    champion = Fraction()
    where = amount = 0
    for amount_now, H in enumerate(sorted(values), 1):
        scale = H * H if squared else H
        candidate = Fraction(amount_now, 1) / (scale * mass)
        if candidate > champion:
            champion, where, amount = candidate, H, amount_now
    return {"ratio": ef(champion), "height": where, "count": amount}


def expected_address_metrics(rows: list[tuple], Hmax: int) -> dict[str, object]:
    # row=(codes,bits,Q,L,B,r2,r3)
    endpoint_mass = sum((Fraction(1, pow(3, row[2])) for row in rows), Fraction())
    product_mass = sum((Fraction(1, pow(2, row[3]) * pow(3, row[2])) for row in rows), Fraction())
    digest = hashlib.sha256()
    for codes, _bits, Q, L, B, r2, r3 in sorted(rows, key=lambda row: row[0]):
        digest.update(f"{'/'.join(codes)}|{L}|{Q}|{B}|{r2}|{r3}\n".encode("ascii"))
    endpoint_error = product_error = Fraction()
    endpoint_H = product_H = 0
    for H in range(1, Hmax + 1):
        points3 = sum(lattice_count(H, row[6], pow(3, row[2])) for row in rows)
        error3 = Fraction(points3) - H * endpoint_mass
        if error3 > endpoint_error:
            endpoint_error, endpoint_H = error3, H
        points23 = sum(
            lattice_count(H, row[5], pow(2, row[3])) * lattice_count(H, row[6], pow(3, row[2]))
            for row in rows
        )
        error23 = Fraction(points23) - H * H * product_mass
        if error23 > product_error:
            product_error, product_H = error23, H
    exact = Counter((row[2], row[6]) for row in rows)
    overlaps = 0
    for index, left in enumerate(rows):
        for right in rows[index + 1 :]:
            overlaps += (left[6] - right[6]) % pow(3, min(left[2], right[2])) == 0
    return {
        "address_count": len(rows),
        "q_distribution": {
            str(key): value for key, value in sorted(Counter(row[2] for row in rows).items())
        },
        "row_digest_sha256": digest.hexdigest(),
        "endpoint_mass": ef(endpoint_mass),
        "product_mass": ef(product_mass),
        "canonical_endpoint_max_ratio": max_ratio(
            [positive(row[6], pow(3, row[2])) for row in rows], endpoint_mass, False
        ),
        "canonical_two_sided_max_ratio": max_ratio(
            [max(positive(row[5], pow(2, row[3])), positive(row[6], pow(3, row[2]))) for row in rows],
            product_mass,
            True,
        ),
        "ordinary_height_limit": Hmax,
        "endpoint_max_plus_one_error": ef(endpoint_error),
        "endpoint_error_height": endpoint_H,
        "two_sided_max_plus_one_error": ef(product_error),
        "two_sided_error_height": product_H,
        "endpoint_cylinders": {
            "compatible_unordered_pairs": overlaps,
            "total_unordered_pairs": len(rows) * (len(rows) - 1) // 2,
            "exact_duplicate_unordered_pairs": sum(n * (n - 1) // 2 for n in exact.values()),
            "maximum_exact_multiplicity": max(exact.values(), default=0),
        },
    }


def normalized(value: int) -> int:
    while value % 2 == 0:
        value //= 2
    return value


def adversaries() -> list[tuple[str, int]]:
    result = [("2^m-1", pow(2, m) - 1) for m in range(3, 25)]
    result += [("8^m-5", pow(8, m) - 5) for m in range(1, 11)]
    for size in range(1, 11):
        for mask in range(pow(2, size)):
            word = "".join("111" if mask & pow(2, k) else "110" for k in range(size))
            result.append(("(110|111)^*", int(word, 2)))
    result += [("A=11101", int(ABLOCK, 2)), ("B=1100", int(BBLOCK, 2))]
    result += [
        ("A^rB^s", int(ABLOCK * r + BBLOCK * s, 2)) for r in range(1, 9) for s in range(1, 9)
    ]
    return result


def actual_word(source: int, length: int) -> str:
    result = []
    for _ in range(length):
        result.append(str(source % 2))
        source = (3 * source + 1) // 2 if source % 2 else source // 2
    return "".join(result)


def expected_adversarial() -> dict[str, object]:
    digest = hashlib.sha256()
    families: Counter[str] = Counter()
    for family, raw in adversaries():
        source = normalized(raw)
        word = actual_word(source, 24)
        L, Q, B, r2, _r3 = source_endpoint(word)
        if L != 24 or source % pow(2, 24) != r2:
            fail("E22 adversarial source residue")
        families[family] += 1
        digest.update(f"{family}|{raw}|{source}|{word}|{B}|{r2}\n".encode("ascii"))
    return {
        "prefix_length": 24,
        "instance_count": sum(families.values()),
        "family_counts": dict(sorted(families.items())),
        "row_digest_sha256": digest.hexdigest(),
    }


def verify_residue(data: dict[str, object]) -> tuple[int, int, int]:
    if data.get("format") != "collatz-phase13-residue-audit-v1" or data.get("proves_collatz") is not False:
        fail("E22 residue artifact boundary")
    finite = data.get("E22")
    if not isinstance(finite, dict) or finite.get("repository_status") != "VERIFIED_FINITE":
        fail("E22 status")
    q_cap = finite.get("maximum_total_q")
    block_cap = finite.get("maximum_blocks")
    Hmax = finite.get("ordinary_height_limit")
    if not all(isinstance(x, int) and x > 0 for x in (q_cap, block_cap, Hmax)):
        fail("E22 finite parameters")
    words = crossing_words(q_cap)
    if finite.get("codeword_count") != len(words):
        fail("E22 codeword count")
    expected_distribution = {
        str(key): value for key, value in sorted(Counter(word[3] for word in words).items())
    }
    if finite.get("codeword_q_distribution") != expected_distribution:
        fail("E22 codeword distribution")
    stored_families = finite.get("address_families")
    if not isinstance(stored_families, list) or len(stored_families) != block_cap:
        fail("E22 address families")
    for block_count, stored in enumerate(stored_families, 1):
        rows = construct_addresses(words, block_count, q_cap)
        expected = {"block_count": block_count, **expected_address_metrics(rows, Hmax)}
        if stored != expected:
            fail(f"E22 address residue or cylinder compatibility at block count {block_count}")
    if finite.get("adversarial_conventions") != expected_adversarial():
        fail("E22 mandatory adversarial audit")
    ng23 = data.get("NG23")
    if not isinstance(ng23, dict) or ng23.get("repository_status") != "REFUTED":
        fail("NG23 status")
    counterexample = ng23.get("least_counterexample")
    if not isinstance(counterexample, dict):
        fail("NG23 raw Haar counterexample")
    if counterexample.get("codeword") != "1" or counterexample.get("height") != 2:
        fail("NG23 least counterexample")
    if parsed_fraction(counterexample.get("endpoint_volume_prediction")) != Fraction(2, 3):
        fail("NG23 endpoint volume")
    if parsed_fraction(counterexample.get("two_sided_volume_prediction")) != Fraction(2, 3):
        fail("NG23 two-sided volume")
    if counterexample.get("canonical_count") != 1:
        fail("NG23 canonical count")
    return q_cap, block_cap, Hmax


def verify_conditional(data: dict[str, object]) -> None:
    if data.get("format") != "collatz-phase13-conditional-pressure-v1" or data.get("proves_collatz") is not False:
        fail("P80 artifact boundary")
    claim = data.get("P80")
    h72 = data.get("H72")
    if not isinstance(claim, dict) or claim.get("repository_status") != "CONDITIONAL":
        fail("P80 status")
    if not isinstance(h72, dict) or h72.get("repository_status") != "OPEN":
        fail("H72 status")
    if parsed_fraction(claim.get("endpoint_factor")) != Fraction(7, 8):
        fail("P80 endpoint pressure factor")
    if parsed_fraction(claim.get("two_sided_factor")) != Fraction(57, 128):
        fail("P80 two-sided pressure factor")
    if "neither premise is proved" not in str(claim.get("conclusion")):
        fail("P80 conditional boundary")


def verify(artifact_dir: Path) -> dict[str, object]:
    verify_renewal(load(artifact_dir / "phase13_renewal_code.json"))
    dp_depth = verify_pressure(load(artifact_dir / "phase13_pressure_bounds.json"))
    maximum_q = verify_threshold(load(artifact_dir / "phase13_threshold_bridge.json"))
    critical_steps = verify_critical(load(artifact_dir / "phase13_critical_countermodel.json"))
    q_residue, blocks, height = verify_residue(load(artifact_dir / "phase13_residue_audit.json"))
    verify_conditional(load(artifact_dir / "phase13_conditional_pressure.json"))
    if maximum_q != q_residue:
        fail("Phase 13 q scope mismatch")
    return {
        "valid": True,
        "P77": "VERIFIED_THEOREM",
        "P78": "VERIFIED_THEOREM",
        "P79": "VERIFIED_THEOREM",
        "P80": "CONDITIONAL",
        "E22": "VERIFIED_FINITE",
        "NG23": "REFUTED",
        "NG22": "REFUTED",
        "H72": "OPEN",
        "dp_length": dp_depth,
        "maximum_total_q": maximum_q,
        "maximum_blocks": blocks,
        "ordinary_height": height,
        "critical_odd_steps": critical_steps,
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
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, indent=2))
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
