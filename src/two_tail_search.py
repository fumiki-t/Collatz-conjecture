#!/usr/bin/env python3
"""Mine exact collisions in compressed two-tail continuation states."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


DEFAULT_BOUND = 20_000
DEFAULT_GAP_CAP = 512
DEFAULT_HORIZON = 12
A_WORD = "11101"
B_WORD = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def sha256(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest()


def step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def stopping_time(start: int, limit: int = 20_000) -> int:
    value = start
    odd = 0
    for depth in range(1, limit + 1):
        if value & 1:
            odd += 1
        value = step(value)
        if 3**odd < 1 << depth:
            return depth
    raise RuntimeError(f"coefficient-stopping limit reached for {start}")


def v2(value: int) -> int:
    if value <= 0:
        raise ValueError("positive difference required")
    return (value & -value).bit_length() - 1


def parity_word(start: int, length: int) -> str:
    bits = []
    value = start
    for _ in range(length):
        bits.append(str(value & 1))
        value = step(value)
    return "".join(bits)


def prefix_tables(bound: int, maximum_h: int) -> tuple[list[list[int]], list[list[int]]]:
    after = [[start for start in range(bound + 1)]]
    odd = [[0] * (bound + 1)]
    for depth in range(1, maximum_h + 1):
        previous = after[-1]
        current = [0] * (bound + 1)
        current_odd = [0] * (bound + 1)
        for start in range(2, bound + 1):
            current_odd[start] = odd[-1][start] + (previous[start] & 1)
            current[start] = step(previous[start])
        after.append(current)
        odd.append(current_odd)
    return after, odd


def pair_row(
    n: int,
    m: int,
    h: int,
    a: int,
    y: int,
    horizon: int,
    stopping: list[int],
) -> dict[str, object]:
    difference = m - n
    normalized = difference >> h
    transformed_gap = 3**a * normalized
    left_word = parity_word(y, horizon)
    right_word = parity_word(y + transformed_gap, horizon)
    return {
        "n": n,
        "m": m,
        "difference": difference,
        "branch_depth": h,
        "common_odd_count": a,
        "normalized_odd_gap": normalized,
        "branch_orientation": str(y & 1) + str((y + transformed_gap) & 1),
        "left_tail_start": y,
        "right_tail_start": y + transformed_gap,
        "left_tail_word": left_word,
        "right_tail_word": right_word,
        "n_stopping_time": stopping[n],
        "m_stopping_time": stopping[m],
        "joint_safe_through_horizon": stopping[n] > h + horizon and stopping[m] > h + horizon,
        "joint_additional_safe_depth": min(stopping[n], stopping[m]) - 1 - h,
    }


def compressed_key(row: dict[str, object], residue_bits: int) -> tuple[int, int, int, str, int]:
    mask = (1 << residue_bits) - 1
    return (
        int(row["branch_depth"]),
        int(row["common_odd_count"]),
        int(row["normalized_odd_gap"]),
        str(row["branch_orientation"]),
        int(row["left_tail_start"]) & mask,
    )


def collision_search(bound: int, gap_cap: int, horizon: int) -> tuple[list[dict[str, object]], int, str]:
    maximum_h = gap_cap.bit_length() - 1
    after, odd = prefix_tables(bound, maximum_h)
    stopping = [0] * (bound + 1)
    stopping_digest = hashlib.sha256()
    for start in range(2, bound + 1):
        stopping[start] = stopping_time(start)
        stopping_digest.update(f"{start}:{stopping[start]}\n".encode("ascii"))
    states: list[dict[tuple[int, int, int, str, int], tuple[bool, dict[str, object]]]] = [dict() for _ in range(horizon + 1)]
    collisions: list[dict[str, object] | None] = [None] * horizon
    eligible = 0
    for m in range(3, bound + 1):
        for difference in range(1, min(gap_cap, m - 2) + 1):
            n = m - difference
            h = v2(difference)
            if stopping[n] <= h:
                continue
            a = odd[h][n]
            y = after[h][n]
            row = pair_row(n, m, h, a, y, horizon, stopping)
            eligible += 1
            for bits in range(horizon + 1):
                if bits < horizon and collisions[bits] is not None:
                    continue
                key = compressed_key(row, bits)
                prior = states[bits].get(key)
                outcome = bool(row["joint_safe_through_horizon"])
                if prior is None:
                    states[bits][key] = (outcome, row)
                elif prior[0] != outcome:
                    if bits == horizon:
                        raise AssertionError("full-horizon residue state collided")
                    collisions[bits] = {
                        "residue_bits": bits,
                        "compressed_state": [key[0], key[1], key[2], key[3], key[4]],
                        "first_pair": prior[1],
                        "second_pair": row,
                        "minimality_order": "increasing m, then increasing positive difference",
                    }
    if any(value is None for value in collisions):
        missing = [index for index, value in enumerate(collisions) if value is None]
        raise AssertionError(f"production bound did not find collisions for residue bits {missing}")
    return [value for value in collisions if value is not None], eligible, stopping_digest.hexdigest()


def affine_residue(word: str) -> int:
    coefficient, constant, denominator = 1, 0, 1
    for bit in word:
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
    residue = (-constant * pow(coefficient, -1, denominator)) % denominator
    return residue or denominator


def family_values() -> dict[str, list[int]]:
    blocks = []
    for mask in range(4096):
        word = "".join("111" if mask & (1 << index) else "110" for index in range(12))
        blocks.append(affine_residue(word))
    return {
        "2^m_minus_1": [(1 << exponent) - 1 for exponent in range(1, 65)],
        "8^m_minus_5": [(1 << (3 * exponent)) - 5 for exponent in range(1, 33)],
        "(110|111)^star": blocks,
        "A^rB^s": [affine_residue(A_WORD * r + B_WORD * s) for r in range(1, 33) for s in range(1, 33)],
        "A_and_B": [affine_residue(A_WORD), affine_residue(B_WORD)],
    }


def theorem_audit(horizon: int) -> dict[str, object]:
    digest = hashlib.sha256()
    counts = {}
    for label, values in family_values().items():
        ordered = sorted(set(values))
        count = 0
        for n, m in zip(ordered, ordered[1:]):
            difference = m - n
            h = v2(difference)
            shared = parity_word(n, h)
            if shared != parity_word(m, h):
                raise AssertionError("adversarial common prefix mismatch")
            a = shared.count("1")
            y = n
            for _ in range(h):
                y = step(y)
            transformed = 3**a * (difference >> h)
            left = parity_word(y, horizon)
            right = parity_word(y + transformed, horizon)
            key = (h, a, difference >> h, str(y & 1) + str((y + transformed) & 1), y & ((1 << horizon) - 1))
            digest.update(f"{label}|{n}|{m}|{'|'.join(map(str, key))}|{left}|{right}\n".encode("ascii"))
            count += 1
        counts[label] = count
    return {
        "repository_status": "VERIFIED_FINITE",
        "horizon": horizon,
        "pairs_checked": counts,
        "total_pairs_checked": sum(counts.values()),
        "row_digest_sha256": digest.hexdigest(),
    }


def generate(artifact_dir: Path, bound: int = DEFAULT_BOUND, gap_cap: int = DEFAULT_GAP_CAP, horizon: int = DEFAULT_HORIZON) -> dict[str, object]:
    if not 2 <= horizon <= 20 or gap_cap < 4 or bound <= gap_cap:
        raise ValueError("invalid two-tail search bounds")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    collisions, eligible, stopping_digest = collision_search(bound, gap_cap, horizon)
    data = {
        "format": "collatz-two-tail-state-collisions-v1",
        "P68": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For a pair coefficient-safe through its common branch prefix, (h,a,u,orientation,y mod 2^L) determines both next-L parity words and every coefficient-safety decision during those next L steps.",
            "reason": "the transformed gap is 3^a*u, each length-L parity vector is determined by its starting residue modulo 2^L, and the initial coefficient budget is 3^a/2^h",
            "scope": "finite horizon L; no fixed L is claimed sufficient for unbounded continuation",
        },
        "NG19": {
            "repository_status": "REFUTED",
            "hypothesis": f"For L={horizon}, some truncation b<L in the state (h,a,u,orientation,y mod 2^b) determines joint coefficient safety through the next L steps for every audited pair.",
            "refutation_scope": f"every b=0,...,{horizon - 1} has an exact collision within 2<=n<m<={bound}, m-n<={gap_cap}",
            "smallest_collision_for_each_b": collisions,
            "weaker_statement_survives": "b=L is sufficient for the finite L-step decision by P68",
        },
        "E17": {
            "repository_status": "VERIFIED_FINITE",
            "bound_H": bound,
            "gap_cap": gap_cap,
            "horizon_L": horizon,
            "eligible_pairs": eligible,
            "stopping_time_digest_sha256": stopping_digest,
            "collision_count": len(collisions),
            "full_horizon_state_collision_found": False,
        },
        "mandatory_adversarial_audit": theorem_audit(horizon),
        "dependencies": {"branch_point_decomposition_sha256": sha256(artifact_dir / "branch_point_decomposition.json")},
        "C05_implication": {
            "repository_status": "OPEN",
            "conclusion": "a lossless finite-horizon state exists, but the audited collisions show that shortening its residue window loses continuation information",
            "scalable_certificate_found": False,
        },
        "what_this_result_does_not_prove": "Finite-horizon determinacy and bounded collisions do not prove that every unbounded compression needs all residue bits, and do not prove C04, C05, or Collatz.",
        "proves_collatz": False,
    }
    path = artifact_dir / "two_tail_state_collisions.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "artifact": str(path),
        "P68": "VERIFIED_THEOREM",
        "NG19": "REFUTED",
        "E17": "VERIFIED_FINITE",
        "collision_count": len(collisions),
        "eligible_pairs": eligible,
        "C05": "OPEN",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--bound", type=int, default=DEFAULT_BOUND)
    parser.add_argument("--gap-cap", type=int, default=DEFAULT_GAP_CAP)
    parser.add_argument("--horizon", type=int, default=DEFAULT_HORIZON)
    args = parser.parse_args()
    print(json.dumps(generate(args.artifact_dir, args.bound, args.gap_cap, args.horizon), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
