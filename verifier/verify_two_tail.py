#!/usr/bin/env python3
"""Independently verify finite two-tail state collisions and boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


WORD_A = "11101"
WORD_B = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def reject(message: str) -> None:
    raise ValueError(message)


def read_object(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        reject("artifact is not a JSON object")
    return value


def digest_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def next_value(value: int) -> int:
    return (3 * value + 1) // 2 if value % 2 else value // 2


def coefficient_loss_depth(start: int, cap: int = 20_000) -> int:
    value = start
    numerator = 1
    denominator = 1
    for depth in range(1, cap + 1):
        if value % 2:
            numerator *= 3
        denominator *= 2
        value = next_value(value)
        if numerator < denominator:
            return depth
    reject(f"coefficient loss depth cap reached for {start}")
    raise AssertionError("unreachable")


def order_at_two(number: int) -> int:
    if number <= 0:
        reject("pair difference is not positive")
    order = 0
    while number % 2 == 0:
        number //= 2
        order += 1
    return order


def bits_from(start: int, length: int) -> str:
    result = []
    value = start
    for _ in range(length):
        result.append("1" if value % 2 else "0")
        value = next_value(value)
    return "".join(result)


def tail_after(start: int, depth: int) -> tuple[int, int, str]:
    value = start
    odd_count = 0
    word = []
    for _ in range(depth):
        parity = value % 2
        word.append("1" if parity else "0")
        odd_count += parity
        value = next_value(value)
    return value, odd_count, "".join(word)


def reconstruct_row(n: int, m: int, horizon: int, losses: list[int]) -> dict[str, object]:
    difference = m - n
    depth = order_at_two(difference)
    left, odd_count, shared = tail_after(n, depth)
    right, right_odd_count, right_shared = tail_after(m, depth)
    if shared != right_shared or odd_count != right_odd_count:
        reject("claimed pair does not share its branch prefix")
    normalized = difference // (1 << depth)
    gap = 3**odd_count * normalized
    if right - left != gap or gap % 2 == 0:
        reject("transformed branch gap mismatch")
    left_word = bits_from(left, horizon)
    right_word = bits_from(right, horizon)
    return {
        "n": n,
        "m": m,
        "difference": difference,
        "branch_depth": depth,
        "common_odd_count": odd_count,
        "normalized_odd_gap": normalized,
        "branch_orientation": left_word[0] + right_word[0],
        "left_tail_start": left,
        "right_tail_start": right,
        "left_tail_word": left_word,
        "right_tail_word": right_word,
        "n_stopping_time": losses[n],
        "m_stopping_time": losses[m],
        "joint_safe_through_horizon": losses[n] > depth + horizon and losses[m] > depth + horizon,
        "joint_additional_safe_depth": min(losses[n], losses[m]) - 1 - depth,
    }


def state_key(row: dict[str, object], residue_bits: int) -> tuple[int, int, int, str, int]:
    modulus = 1 << residue_bits
    return (
        int(row["branch_depth"]),
        int(row["common_odd_count"]),
        int(row["normalized_odd_gap"]),
        str(row["branch_orientation"]),
        int(row["left_tail_start"]) % modulus,
    )


def rebuild_collision_scan(bound: int, gap_cap: int, horizon: int) -> tuple[list[dict[str, object]], int, str]:
    losses = [0] * (bound + 1)
    stopping_digest = hashlib.sha256()
    for start in range(2, bound + 1):
        losses[start] = coefficient_loss_depth(start)
        stopping_digest.update(f"{start}:{losses[start]}\n".encode("ascii"))

    first_seen: list[dict[tuple[int, int, int, str, int], tuple[bool, dict[str, object]]]] = [dict() for _ in range(horizon)]
    collisions: list[dict[str, object] | None] = [None] * horizon
    eligible_pairs = 0
    for upper in range(3, bound + 1):
        for difference in range(1, min(gap_cap, upper - 2) + 1):
            lower = upper - difference
            depth = order_at_two(difference)
            if losses[lower] <= depth:
                continue
            eligible_pairs += 1
            if all(collision is not None for collision in collisions):
                continue
            row = reconstruct_row(lower, upper, horizon, losses)
            for residue_bits in range(horizon):
                if collisions[residue_bits] is not None:
                    continue
                key = state_key(row, residue_bits)
                old = first_seen[residue_bits].get(key)
                outcome = bool(row["joint_safe_through_horizon"])
                if old is None:
                    first_seen[residue_bits][key] = (outcome, row)
                elif old[0] != outcome:
                    collisions[residue_bits] = {
                        "residue_bits": residue_bits,
                        "compressed_state": list(key),
                        "first_pair": old[1],
                        "second_pair": row,
                        "minimality_order": "increasing m, then increasing positive difference",
                    }
    if any(collision is None for collision in collisions):
        reject("NG19 collision list is incomplete at the declared bounds")
    return [collision for collision in collisions if collision is not None], eligible_pairs, stopping_digest.hexdigest()


def inverse_parity_residue(word: str) -> int:
    multiplier = 1
    addition = 0
    power_of_two = 1
    for symbol in word:
        if symbol not in "01":
            reject("invalid parity word")
        if symbol == "1":
            multiplier *= 3
            addition = 3 * addition + power_of_two
        power_of_two *= 2
    residue = (-addition * pow(multiplier, -1, power_of_two)) % power_of_two
    return residue if residue else power_of_two


def adversarial_inputs() -> dict[str, list[int]]:
    block_residues = []
    for pattern in range(1 << 12):
        word = "".join("111" if (pattern >> position) & 1 else "110" for position in range(12))
        block_residues.append(inverse_parity_residue(word))
    return {
        "2^m_minus_1": [(1 << exponent) - 1 for exponent in range(1, 65)],
        "8^m_minus_5": [(1 << (3 * exponent)) - 5 for exponent in range(1, 33)],
        "(110|111)^star": block_residues,
        "A^rB^s": [inverse_parity_residue(WORD_A * r + WORD_B * s) for r in range(1, 33) for s in range(1, 33)],
        "A_and_B": [inverse_parity_residue(WORD_A), inverse_parity_residue(WORD_B)],
    }


def independently_audit_families(horizon: int) -> dict[str, object]:
    digest = hashlib.sha256()
    counts: dict[str, int] = {}
    for label, raw_values in adversarial_inputs().items():
        values = sorted(set(raw_values))
        count = 0
        for left_start, right_start in zip(values, values[1:]):
            difference = right_start - left_start
            depth = order_at_two(difference)
            left, odd_count, prefix = tail_after(left_start, depth)
            right, right_odd_count, right_prefix = tail_after(right_start, depth)
            if prefix != right_prefix or odd_count != right_odd_count:
                reject("adversarial branch prefix mismatch")
            gap = 3**odd_count * (difference // (1 << depth))
            if right != left + gap:
                reject("adversarial transformed gap mismatch")
            orientation = ("1" if left % 2 else "0") + ("1" if right % 2 else "0")
            state = (depth, odd_count, difference // (1 << depth), orientation, left % (1 << horizon))
            digest.update(
                f"{label}|{left_start}|{right_start}|{'|'.join(map(str, state))}|{bits_from(left, horizon)}|{bits_from(right, horizon)}\n".encode("ascii")
            )
            count += 1
        counts[label] = count
    return {
        "repository_status": "VERIFIED_FINITE",
        "horizon": horizon,
        "pairs_checked": counts,
        "total_pairs_checked": sum(counts.values()),
        "row_digest_sha256": digest.hexdigest(),
    }


def verify(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = read_object(path)
    if data.get("format") != "collatz-two-tail-state-collisions-v1" or data.get("proves_collatz") is not False:
        reject("format or proof boundary mismatch")

    e17 = data.get("E17")
    if not isinstance(e17, dict) or e17.get("repository_status") != "VERIFIED_FINITE":
        reject("E17 finite claim is missing")
    bound = int(e17.get("bound_H", 0))
    gap_cap = int(e17.get("gap_cap", 0))
    horizon = int(e17.get("horizon_L", 0))
    if not 2 <= horizon <= 20 or not 4 <= gap_cap < bound:
        reject("E17 bounds are invalid")

    p68 = data.get("P68")
    expected_p68 = "For a pair coefficient-safe through its common branch prefix, (h,a,u,orientation,y mod 2^L) determines both next-L parity words and every coefficient-safety decision during those next L steps."
    if (
        not isinstance(p68, dict)
        or p68.get("repository_status") != "VERIFIED_THEOREM"
        or p68.get("statement") != expected_p68
        or p68.get("scope") != "finite horizon L; no fixed L is claimed sufficient for unbounded continuation"
    ):
        reject("P68 theorem boundary mismatch")

    ng19 = data.get("NG19")
    expected_hypothesis = f"For L={horizon}, some truncation b<L in the state (h,a,u,orientation,y mod 2^b) determines joint coefficient safety through the next L steps for every audited pair."
    if not isinstance(ng19, dict) or ng19.get("repository_status") != "REFUTED" or ng19.get("hypothesis") != expected_hypothesis:
        reject("NG19 claim boundary mismatch")

    collisions, eligible_pairs, stopping_digest = rebuild_collision_scan(bound, gap_cap, horizon)
    if ng19.get("smallest_collision_for_each_b") != collisions:
        reject("NG19 minimal collision mismatch")
    if (
        e17.get("eligible_pairs") != eligible_pairs
        or e17.get("stopping_time_digest_sha256") != stopping_digest
        or e17.get("collision_count") != horizon
        or e17.get("full_horizon_state_collision_found") is not False
    ):
        reject("E17 finite scan mismatch")

    if data.get("mandatory_adversarial_audit") != independently_audit_families(horizon):
        reject("mandatory adversarial audit mismatch")
    dependencies = data.get("dependencies")
    if (
        not isinstance(dependencies, dict)
        or dependencies.get("branch_point_decomposition_sha256") != digest_file(artifact_dir / "branch_point_decomposition.json")
    ):
        reject("dependency hash mismatch")
    c05 = data.get("C05_implication")
    if (
        not isinstance(c05, dict)
        or c05.get("repository_status") != "OPEN"
        or c05.get("scalable_certificate_found") is not False
        or data.get("what_this_result_does_not_prove")
        != "Finite-horizon determinacy and bounded collisions do not prove that every unbounded compression needs all residue bits, and do not prove C04, C05, or Collatz."
    ):
        reject("C05 or no-overclaim boundary mismatch")
    return {
        "valid": True,
        "P68": "VERIFIED_THEOREM",
        "NG19": "REFUTED",
        "E17": "VERIFIED_FINITE",
        "bound_H": bound,
        "gap_cap": gap_cap,
        "horizon_L": horizon,
        "eligible_pairs": eligible_pairs,
        "mandatory_pairs_checked": int(data["mandatory_adversarial_audit"]["total_pairs_checked"]),
        "C05": "OPEN",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir / "two_tail_state_collisions.json", args.artifact_dir)
    except (OSError, ValueError, ZeroDivisionError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, indent=2, sort_keys=True))
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
