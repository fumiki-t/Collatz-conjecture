#!/usr/bin/env python3
"""Generate exact Phase 35 decoder and corrected joint-scalar evidence.

The supplied note is untrusted.  Its decoder and two finite inequalities are
reconstructed, while its claimed area-238 exhaustion is falsified by an exact
joint scalar tuple.  The strongest consequence of the audited sieve is the
corrected critical area floor A>=229.
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

try:
    from phase34_search import (
        alpha_data, ceil_log2_fraction, critical_length, encode, log_interval,
        p133_maximum, profile_maximum, rows_digest, write_json,
    )
except ModuleNotFoundError:
    from src.phase34_search import (
        alpha_data, ceil_log2_fraction, critical_length, encode, log_interval,
        p133_maximum, profile_maximum, rows_digest, write_json,
    )


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


MATVEEV_K = 1_564_920_000
CUTOFF = 11_500_000_000_000
FINITE_BOUND = 583_561
EXPECTED_CLAIMS = {
    "P206": "VERIFIED_THEOREM", "P207": "VERIFIED_THEOREM",
    "P208": "VERIFIED_THEOREM", "P209": "VERIFIED_THEOREM",
    "P210": "VERIFIED_THEOREM", "E49": "VERIFIED_FINITE",
    "E50": "VERIFIED_FINITE", "NG41": "REFUTED",
    "H89": "OPEN", "H133": "OPEN", "H172": "OPEN",
}


def v2(value: int) -> int:
    if value == 0:
        raise ValueError("zero has no finite 2-adic valuation")
    return (value & -value).bit_length() - 1


def correction(q: int, positions: Sequence[int]) -> int:
    return sum(3 ** (q - 1 - j) * 2 ** position for j, position in enumerate(positions))


def safe_position_lists(q: int) -> Iterable[tuple[int, ...]]:
    bounds = tuple((3 ** j).bit_length() - 1 for j in range(q))

    def extend(prefix: tuple[int, ...], label: int) -> Iterable[tuple[int, ...]]:
        if label == q:
            yield prefix
            return
        for position in range(prefix[-1] + 1, bounds[label] + 1):
            yield from extend(prefix + (position,), label + 1)

    if q == 1:
        yield (0,)
    else:
        yield from extend((0,), 1)


def decode_profile(q: int, source: int) -> tuple[int, ...]:
    length = critical_length(q)
    modulus = 1 << length
    mechanical = tuple((3 ** j).bit_length() - 1 for j in range(q))
    remainder = (correction(q, mechanical) - source * (modulus - 3 ** q)) % modulus
    profile = [0] * q
    cursor = 1
    previous_position = 0
    while remainder:
        position = v2(remainder)
        label = next((j for j in range(cursor, q) if mechanical[j] > position), None)
        if label is None or position <= previous_position:
            raise ValueError("invalid decoder image")
        profile[label] = mechanical[label] - position
        remainder = (remainder - 3 ** (q - 1 - label) * 2 ** position
                     * (2 ** profile[label] - 1)) % modulus
        cursor = label + 1
        previous_position = position
    positions = tuple(mechanical[j] - profile[j] for j in range(q))
    if positions[0] != 0 or any(positions[j] <= positions[j - 1] for j in range(1, q)):
        raise ValueError("decoded positions are not strictly increasing")
    return tuple(profile)


def literal_endpoint(source: int, positions: Sequence[int], length: int) -> int:
    odd = set(positions)
    value = source
    for step in range(length):
        if (value & 1) != (step in odd):
            raise AssertionError("source residue does not realize word")
        value = (3 * value + 1) // 2 if value & 1 else value // 2
    return value


def decoder_audit(q_max: int = 18) -> dict[str, object]:
    digest = hashlib.sha256()
    counts = []
    samples = []
    total = p98_count = 0
    for q in range(1, q_max + 1):
        length = critical_length(q)
        modulus = 1 << length
        mechanical = tuple((3 ** j).bit_length() - 1 for j in range(q))
        bc = correction(q, mechanical)
        inv = pow(3 ** q, -1, modulus)
        q_count = 0
        for positions in safe_position_lists(q):
            b = correction(q, positions)
            source = (-b * inv) % modulus
            expected_profile = tuple(mechanical[j] - positions[j] for j in range(q))
            decoded = decode_profile(q, source)
            if decoded != expected_profile:
                raise AssertionError("decoder mismatch")
            endpoint = literal_endpoint(source, positions, length)
            defect = bc - b
            displacement = endpoint - source
            if bc - source * (modulus - 3 ** q) != defect + modulus * displacement:
                raise AssertionError("endpoint identity")
            p98 = 0 <= 3 * displacement < q
            p98_count += int(p98)
            row = (q, length, positions, source, displacement, decoded, int(p98))
            digest.update(repr(row).encode("ascii") + b"\n")
            if len(samples) < 12:
                samples.append([q, length, list(positions), source, displacement,
                                list(decoded), p98])
            q_count += 1
            total += 1
        counts.append([q, length, q_count])
    if q_max == 18 and total != 1_166_058:
        raise AssertionError("safe word count")
    return {"format": "collatz-phase35-decoder-audit-v1", "q_range": [1, q_max],
            "counts_by_q": counts, "total_words": total, "p98_box_words": p98_count,
            "row_digest_sha256": digest.hexdigest(), "samples": samples,
            "decision_boundary": "The decoder reconstructs a valid word; it does not produce a smaller P89 ancestor.",
            "proves_collatz": False}


def joint_tuples(q: int, length: int, area: int) -> list[dict[str, int]]:
    result = []
    state_p133 = p133_maximum(q, length)
    for height in range(1, area + 1):
        baseline = sum(level * q // (length - q) for level in range(height))
        if height + baseline > area:
            break
        state_profile = profile_maximum(q, length, area, height)
        state = min(state_p133, state_profile)
        if state < FINITE_BOUND:
            continue
        width = ceil_log2_fraction(Fraction((1 << (height + 2 + length)) * state, 3 ** q))
        z = ((length - q) * (width + 1) + length - 1) // length
        for components in range(height, area - baseline + 1):
            sigma = area - components - baseline
            residual_components = min(components, height + sigma)
            residual_area = area - (components - residual_components)
            residual_span = min(2 * residual_area,
                                length * residual_area // q + residual_components)
            triple_rhs = ((components + 2 * residual_components) * (width + 1)
                          + 3 * residual_span
                          + (width + 3) * (3 + 2 * z + z * (z - 1) // 2))
            factor_rhs = (width + 1 + components * (width - 1)
                          + min(2 * area, length * area // q + components))
            result.append({"T35C_margin": triple_rhs - 3 * length,
                           "T35B_margin": factor_rhs - length,
                           "h": height, "J": components, "Sigma": sigma,
                           "E": residual_components, "n": width, "Z": z,
                           "m_max": state, "m_P133": state_p133,
                           "m_prof": state_profile, "A_res": residual_area,
                           "T_res": residual_span, "T35C_rhs": triple_rhs,
                           "T35B_rhs": factor_rhs})
    return result


def joint_low_q_audit(area: int) -> dict[str, object]:
    counts = {"q_rows": 0, "q0_rejections": 0, "state_E46_rejections": 0,
              "T35C_rejections": 0, "T35B_rejections": 0, "joint_survivors": 0}
    rows = []
    survivors = []
    closest = None
    for q in range(971, 8192):
        counts["q_rows"] += 1
        length = critical_length(q)
        divisor = math.gcd(q, length)
        q0 = q // divisor
        if q0 < 971:
            counts["q0_rejections"] += 1
            row = [q, length, divisor, q0, "q0"]
        else:
            tuples = joint_tuples(q, length, area)
            if not tuples:
                counts["state_E46_rejections"] += 1
                row = [q, length, divisor, q0, "state_E46"]
            else:
                pass_c = [item for item in tuples if item["T35C_margin"] >= 0]
                if not pass_c:
                    counts["T35C_rejections"] += 1
                    best = max(tuples, key=lambda item: item["T35C_margin"])
                    row = [q, length, divisor, q0, "T35C", *best.values()]
                else:
                    pass_b = [item for item in pass_c if item["T35B_margin"] >= 0]
                    if not pass_b:
                        counts["T35B_rejections"] += 1
                        best = max(pass_c, key=lambda item: item["T35B_margin"])
                        row = [q, length, divisor, q0, "T35B", *best.values()]
                    else:
                        counts["joint_survivors"] += 1
                        best = max(pass_b, key=lambda item: min(
                            item["T35B_margin"], item["T35C_margin"]))
                        record = {"q": q, "L": length, "d": divisor, "q0": q0, **best}
                        survivors.append(record)
                        row = [q, length, divisor, q0, "survivor", *best.values()]
                if closest is None or min(best["T35B_margin"], best["T35C_margin"]) > min(
                        closest["T35B_margin"], closest["T35C_margin"]):
                    closest = {"q": q, "L": length, "d": divisor, "q0": q0, **best}
        rows.append(row)
    return {"area_ceiling": area, "q_range": [971, 8191], "counts": counts,
            "row_digest_sha256": rows_digest(rows), "survivors": survivors,
            "closest_joint_row": closest}


def cutoff_certificate() -> dict[str, object]:
    left = Fraction(19 * CUTOFF, 12)
    right = 5950 + 238 * (44 + 47 * MATVEEV_K)
    derivative = Fraction(3 * 238 * (MATVEEV_K + 1), 2 * CUTOFF)
    if left <= right or derivative >= Fraction(19, 12):
        raise AssertionError("cutoff inequality")
    return {"Q": CUTOFF, "envelope_constant": 5950, "envelope_coefficient": 238,
            "log2_3_lower": [19, 12], "log2_4Q_over_3_upper": 44,
            "log2_12Q_upper": 47, "margin": encode(left - right),
            "derivative_upper": encode(derivative), "derivative_target": [19, 12]}


def frontier_audit(d_max: int) -> dict[str, object]:
    alpha, prefix, convergents = alpha_data()
    ln2, ln3 = log_interval(Fraction(2)), log_interval(Fraction(3))
    uppers = [(p, q) for p, q in convergents
              if 971 <= q < CUTOFF and Fraction(p, q) > alpha[1]]
    rows = []
    closest = None
    for p, q0 in uppers:
        error = p * ln2[0] - q0 * ln3[1], p * ln2[1] - q0 * ln3[0]
        for divisor in range(1, d_max + 1):
            q, length = divisor * q0, divisor * p
            if q >= CUTOFF:
                continue
            low, high = divisor * error[0], divisor * error[1]
            if low <= 0 or high >= ln2[0]:
                continue
            log_bound = ceil_log2_fraction(Fraction(4 * q, 3) / low)
            margin = 5950 + 238 * log_bound - length
            row = [p, q0, divisor, length, q, log_bound, margin]
            rows.append(row)
            closest = row if closest is None or margin > closest[-1] else closest
            if margin >= 0:
                raise AssertionError("frontier survivor")
    return {"d_max": d_max, "upper_convergents": [list(row) for row in uppers],
            "continued_fraction_prefix": list(prefix), "candidate_count": len(rows),
            "candidate_digest_sha256": rows_digest(rows),
            "closest_coarse_upper_margin": closest}


def displayed_area209_rejection() -> dict[str, int]:
    q, length, area = 2301, 3647, 209
    item = next(row for row in joint_tuples(q, length, area)
                if (row["h"], row["J"], row["Sigma"], row["E"], row["n"], row["Z"])
                == (2, 105, 103, 105, 24, 10))
    return {"q": q, "L": length, "A": area, **item}


def scalar_audit() -> dict[str, object]:
    low_228 = joint_low_q_audit(228)
    low_229 = joint_low_q_audit(229)
    low_237 = joint_low_q_audit(237)
    if low_228["survivors"] or len(low_229["survivors"]) != 1:
        raise AssertionError("corrected scalar boundary")
    return {"format": "collatz-phase35-joint-scalar-audit-v1",
            "cutoff": cutoff_certificate(),
            "legendre": {"threshold_q": 8192, "correct_threshold_exponent": [-535, 357],
                         "proposal_exponent": [-3073, 714], "proposal_matches": False},
            "area_228_gcd": {"strict_upper": [7072, 27], "integer_maximum": 261},
            "area_228_frontier": frontier_audit(261), "area_228_low_q": low_228,
            "next_obstruction": low_229["survivors"][0],
            "proposal_area_237_audit": {"gcd_integer_maximum": 273,
                                         "frontier": frontier_audit(273),
                                         "low_q": low_237},
            "displayed_area209_tuple": displayed_area209_rejection(),
            "proposal_discrepancies": {
                "cutoff_margin_claimed": 651_592_977_457,
                "cutoff_margin_reconstructed": encode(Fraction(19 * CUTOFF, 12)
                    - (5950 + 238 * (44 + 47 * MATVEEV_K))),
                "frontier_candidates_claimed": 1908,
                "frontier_candidates_reconstructed_d273": 1996,
                "area238_conclusion": "REFUTED as a consequence of the stated joint scalar sieve by the A=229 tuple",
            }, "proves_collatz": False}


def regressions() -> dict[str, object]:
    return {"format": "collatz-phase35-regressions-v1",
            "mandatory_families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101",
                                   "B=1100", "A^rB^s"],
            "decoder_controls": ["source 167", "critical mechanical words", "NG24-NG31"],
            "cycle_controls": ["trivial cycle and powers", "negative cycles", "rational shadows", "NG34-NG40"],
            "preserved_boundaries": ["valid decoding does not imply a smaller ancestor",
                                     "scalar feasibility does not imply a realizable positive integer cycle"],
            "proves_collatz": False}


def theory() -> dict[str, object]:
    return {"format": "collatz-phase35-theory-v1", "claims": EXPECTED_CLAIMS,
            "P206": {"statement": "On the valid critical-safe image, the modular valuation algorithm uniquely and completely reconstructs every defect and the endpoint displacement.",
                     "boundary": "It does not produce or prove existence of a smaller P89 ancestor."},
            "P207": {"statement": "P179 sharpens exactly to p_cyc(n)<=n+1+J(n-1)+min(2A,floor(LA/q)+J)."},
            "P208": {"statement": "After K=J-E singleton cells are removed, A_res=A-K and P195 sharpens by replacing 6A with 3 min(2A_res,floor(LA_res/q)+E)."},
            "P209": {"statement": "If the least state has profile h-1 and a later point has height h, a strictly better smaller-denominator upper linear-form approximation exists."},
            "P210": {"statement": "Every critical primitive positive nontrivial integer Collatz cycle has reduced-profile area A>=229.",
                     "dependencies": ["P164", "EXT17", "P177", "P199", "P202", "P203", "P207", "P208", "E46", "E50"]},
            "NG41": {"refuted": "The stated T35-B/T35-C joint scalar sieve proves critical A>=238.",
                     "counterexample": "(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,229,2,138,90,92,24,10), margins (T35B,T35C)=(10,43)."},
            "what_this_result_does_not_prove": "The decoder does not close H89; the corrected finite floor does not exclude area 229 or arbitrary-area cycles.",
            "proves_collatz": False}


def obstruction_report(scalar: dict[str, object]) -> str:
    row = scalar["next_obstruction"]
    return f"""# Phase 35 obstruction report

The full modular defect decoder is valid on the critical-safe image, but it
does not construct a smaller ancestor. H89 remains open at arithmetic
dominance, not parity-word reconstruction.

The proposed `A>=238` joint scalar conclusion is not accepted. Exact
reconstruction gives cutoff margin `2109414590734/3`, Legendre exponent
`-535/357`, and 1,996 high-frontier rows for the proposal's `d<=273`, rather
than its three quoted values. More importantly, the stated simultaneous
conditions admit

```text
(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,229,2,138,90,92,24,10)
T35-B margin = 10
T35-C margin = 43
```

The corrected relaxed audit has no survivor through `A=228`, so the accepted
finite theorem is only `A>=229`. Scalar feasibility does not assert that the
stored area-229 tuple is a realizable positive integer cycle.

## What this result does not prove

It does not close H89, realize or exclude the area-229 tuple, provide a
uniform growing-area cycle theorem, address nonperiodic infinite tails, or
prove Collatz. `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    decoder = decoder_audit()
    scalar = scalar_audit()
    write_json(args.artifact_dir / "phase35_theory.json", theory())
    write_json(args.artifact_dir / "phase35_decoder_audit.json", decoder)
    write_json(args.artifact_dir / "phase35_joint_scalar_audit.json", scalar)
    write_json(args.artifact_dir / "phase35_regressions.json", regressions())
    (args.artifact_dir / "phase35_obstruction_report.md").write_text(
        obstruction_report(scalar), encoding="utf-8")
    print(json.dumps({"valid": True, "claims": EXPECTED_CLAIMS,
                      "decoded_words": decoder["total_words"],
                      "area228_frontier": scalar["area_228_frontier"]["candidate_count"],
                      "area228_counts": scalar["area_228_low_q"]["counts"],
                      "next_obstruction": scalar["next_obstruction"],
                      "proves_collatz": False}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
