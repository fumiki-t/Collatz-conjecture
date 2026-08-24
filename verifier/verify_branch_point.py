#!/usr/bin/env python3
"""Independently verify branch-point decomposition evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path


K0 = 114_208_327_604
W = 4_142_380_786
A_BITS = "11101"
B_BITS = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        fail("artifact is not an object")
    return value


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def collatz_step(value: int) -> int:
    if value & 1:
        return (3 * value + 1) >> 1
    return value >> 1


def coefficient_stop(start: int, limit: int = 20_000) -> int:
    value = start
    threes = 1
    for depth in range(1, limit + 1):
        if value & 1:
            threes *= 3
        value = collatz_step(value)
        if threes < 1 << depth:
            return depth
    fail(f"stopping limit reached for {start}")


def two_order(value: int) -> int:
    if value <= 0:
        fail("nonpositive difference")
    order = 0
    while value % 2 == 0:
        value //= 2
        order += 1
    return order


def orbit_bits(start: int, length: int) -> tuple[str, int]:
    bits = []
    value = start
    for _ in range(length):
        bits.append("1" if value & 1 else "0")
        value = collatz_step(value)
    return "".join(bits), value


def inspect_pair(n: int, m: int) -> dict[str, object]:
    if not 0 < n < m:
        fail("invalid pair")
    difference = m - n
    depth = two_order(difference)
    left_bits, left_value = orbit_bits(n, depth + 1)
    right_bits, right_value = orbit_bits(m, depth + 1)
    if left_bits[:depth] != right_bits[:depth] or left_bits[depth] == right_bits[depth]:
        fail("parity divergence mismatch")
    shared = left_bits[:depth]
    odd_count = shared.count("1")
    normalized = difference >> depth
    _left_prefix, left_after_shared = orbit_bits(n, depth)
    _right_prefix, right_after_shared = orbit_bits(m, depth)
    transformed = right_after_shared - left_after_shared
    if transformed != 3**odd_count * normalized or transformed & 1 == 0:
        fail("affine branch gap mismatch")
    return {
        "n": n,
        "m": m,
        "difference": difference,
        "branch_depth": depth,
        "normalized_odd_gap": normalized,
        "shared_parity_prefix": shared,
        "shared_odd_count": odd_count,
        "branch_bits": left_bits[depth] + right_bits[depth],
        "transformed_gap": transformed,
        "surplus_numerator": 3**odd_count,
        "surplus_denominator": 1 << depth,
    }


def word_residue(word: str) -> int:
    coefficient, addition, divisor = 1, 0, 1
    for symbol in word:
        if symbol == "1":
            coefficient *= 3
            addition = 3 * addition + divisor
        divisor *= 2
    value = (-addition * pow(coefficient, -1, divisor)) % divisor
    return value or divisor


def add_pair_digest(label: str, values: list[int], digest: hashlib._Hash) -> int:
    ordered = sorted(set(values))
    count = 0
    for n, m in zip(ordered, ordered[1:]):
        row = inspect_pair(n, m)
        digest.update(
            (
                f"{label}|{n}|{m}|{row['branch_depth']}|{row['normalized_odd_gap']}|"
                f"{row['shared_odd_count']}|{row['branch_bits']}|{row['transformed_gap']}\n"
            ).encode("ascii")
        )
        count += 1
    return count


def rebuild_adversarial() -> dict[str, object]:
    digest = hashlib.sha256()
    counts = {
        "2^m_minus_1": add_pair_digest("2m", [2**m - 1 for m in range(1, 65)], digest),
        "8^m_minus_5": add_pair_digest("8m", [2 ** (3 * m) - 5 for m in range(1, 33)], digest),
    }
    block_values = []
    for pattern in range(1 << 12):
        word = "".join("111" if pattern >> index & 1 else "110" for index in range(12))
        block_values.append(word_residue(word))
    counts["(110|111)^star"] = add_pair_digest("blocks", block_values, digest)
    mixed = [word_residue(A_BITS * r + B_BITS * s) for r in range(1, 33) for s in range(1, 33)]
    counts["A^rB^s"] = add_pair_digest("mixed", mixed, digest)
    counts["A_and_B"] = add_pair_digest("AB", [word_residue(A_BITS), word_residue(B_BITS)], digest)
    return {
        "repository_status": "VERIFIED_FINITE",
        "scopes": {
            "2^m_minus_1": "1<=m<=64, adjacent family values",
            "8^m_minus_5": "1<=m<=32, adjacent family values",
            "(110|111)^star": "all 4096 twelve-block inverse-parity residues, adjacent sorted values",
            "A^rB^s": "1<=r,s<=32, adjacent sorted inverse-parity residues",
            "A_and_B": "the two individual inverse-parity residues",
        },
        "pairs_checked": counts,
        "total_pairs_checked": sum(counts.values()),
        "row_digest_sha256": digest.hexdigest(),
    }


def rebuild_exhaustive(limit: int) -> dict[str, object]:
    digest = hashlib.sha256()
    count = 0
    for n in range(2, limit + 1):
        for m in range(n + 1, limit + 1):
            row = inspect_pair(n, m)
            digest.update(
                (
                    f"{n}|{m}|{row['branch_depth']}|{row['normalized_odd_gap']}|"
                    f"{row['shared_parity_prefix']}|{row['branch_bits']}|{row['transformed_gap']}\n"
                ).encode("ascii")
            )
            count += 1
    return {"repository_status": "VERIFIED_FINITE", "limit": limit, "pairs_checked": count, "row_digest_sha256": digest.hexdigest()}


def no_deeper_pair(stopping: list[int], branch_depth: int, claimed_depth: int) -> bool:
    threshold = claimed_depth + 1
    sides: dict[int, int] = defaultdict(int)
    mask = (1 << branch_depth) - 1
    for start in range(2, len(stopping)):
        if stopping[start] <= threshold:
            continue
        residue = start & mask
        sides[residue] |= 1 << ((start >> branch_depth) & 1)
        if sides[residue] == 3:
            return False
    return True


def verify(path: Path, artifact_dir: Path) -> dict[str, object]:
    data = load(path)
    if data.get("format") != "collatz-branch-point-decomposition-v1" or data.get("proves_collatz") is not False:
        fail("format or proof boundary mismatch")
    p66 = data.get("P66")
    expected_statement = "For positive n<m and d=m-n, the parity prefixes agree for exactly h=v2(d) steps, then split; after the common prefix the gap is 3^a*(d/2^h), an odd integer."
    if not isinstance(p66, dict) or p66.get("repository_status") != "VERIFIED_THEOREM" or p66.get("statement") != expected_statement:
        fail("P66 theorem statement mismatch")
    p67 = data.get("P67")
    if (
        not isinstance(p67, dict)
        or p67.get("repository_status") != "CONDITIONAL"
        or p67.get("dependencies") != ["P63", "P64"]
        or p67.get("q0_positive_gap_conditions") != ["0<d<=4142380786", "4|d", "N,X are coefficient-safe through K0-1"]
        or p67.get("branch_depth_range") != [2, 31]
        or p67.get("case_count") != 30
        or not W < 2**32
    ):
        fail("P67 conditional boundary mismatch")
    e16 = data.get("E16")
    if not isinstance(e16, dict) or e16.get("repository_status") != "VERIFIED_FINITE":
        fail("E16 missing")
    bound = int(e16.get("bound_H", 0))
    stopping = [0] * (bound + 1)
    digest = hashlib.sha256()
    for start in range(2, bound + 1):
        value = coefficient_stop(start)
        stopping[start] = value
        digest.update(f"{start}:{value}\n".encode("ascii"))
    if e16.get("stopping_time_digest_sha256") != digest.hexdigest():
        fail("stopping digest mismatch")
    profile = e16.get("profile")
    maximum = (bound - 2).bit_length() - 1
    if not isinstance(profile, list) or len(profile) != maximum + 1 or e16.get("maximum_branch_depth_present") != maximum:
        fail("branch profile range mismatch")
    for expected_h, row in enumerate(profile):
        if not isinstance(row, dict):
            fail("branch profile row missing")
        n, m = int(row.get("n", 0)), int(row.get("m", 0))
        expected = inspect_pair(n, m)
        expected.update(
            {
                "n_stopping_time": stopping[n],
                "m_stopping_time": stopping[m],
                "max_joint_safe_depth": min(stopping[n], stopping[m]) - 1,
            }
        )
        if row != expected or row.get("branch_depth") != expected_h:
            fail("branch profile witness mismatch")
        if not no_deeper_pair(stopping, expected_h, int(row["max_joint_safe_depth"])):
            fail("branch profile upper bound mismatch")
    finite = e16.get("exhaustive_pair_audit")
    if not isinstance(finite, dict) or finite != rebuild_exhaustive(int(finite.get("limit", 0))):
        fail("exhaustive pair digest mismatch")
    if data.get("mandatory_adversarial_audit") != rebuild_adversarial():
        fail("mandatory adversarial mismatch")
    dependencies = data.get("dependencies")
    if (
        not isinstance(dependencies, dict)
        or dependencies.get("phase10_gap_modulus_sha256") != file_digest(artifact_dir / "phase10_gap_modulus.json")
        or dependencies.get("phase10_safe_pair_spacing_sha256") != file_digest(artifact_dir / "phase10_safe_pair_spacing.json")
    ):
        fail("dependency hash mismatch")
    c05 = data.get("C05_reformulation")
    if not isinstance(c05, dict) or c05.get("repository_status") != "OPEN" or c05.get("certificate_found") is not False:
        fail("C05 was improperly promoted")
    return {
        "valid": True,
        "P66": "VERIFIED_THEOREM",
        "P67": "CONDITIONAL",
        "E16_bound_H": bound,
        "maximum_branch_depth_present": maximum,
        "C05": "OPEN",
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir / "branch_point_decomposition.json", args.artifact_dir)
    except (OSError, ValueError, ZeroDivisionError) as error:
        print(json.dumps({"valid": False, "error": str(error)}, indent=2, sort_keys=True))
        return 1
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(output, encoding="utf-8")
    print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
