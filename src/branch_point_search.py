#!/usr/bin/env python3
"""Generate exact branch-point evidence for Phase 10 safe pairs."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


K0 = 114_208_327_604
Q0 = 72_057_431_991
W = 4_142_380_786
DEFAULT_BOUND = 1_500_000
A_WORD = "11101"
B_WORD = "1100"

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def shortcut_step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def coefficient_stopping_time(start: int, limit: int = 20_000) -> int:
    value = start
    odd_count = 0
    for depth in range(1, limit + 1):
        if value % 2:
            odd_count += 1
        value = shortcut_step(value)
        if 3**odd_count < 1 << depth:
            return depth
    raise RuntimeError(f"coefficient-stopping limit reached for {start}")


def parity_prefix(start: int, length: int) -> str:
    bits = []
    value = start
    for _ in range(length):
        bits.append(str(value & 1))
        value = shortcut_step(value)
    return "".join(bits)


def valuation_two(value: int) -> int:
    if value <= 0:
        raise ValueError("2-adic valuation requires a positive integer")
    return (value & -value).bit_length() - 1


def iterate(start: int, length: int) -> int:
    value = start
    for _ in range(length):
        value = shortcut_step(value)
    return value


def branch_record(n: int, m: int, stopping: list[int] | None = None) -> dict[str, object]:
    if not 0 < n < m:
        raise ValueError("branch pair must be ordered and positive")
    difference = m - n
    branch_depth = valuation_two(difference)
    word_n = parity_prefix(n, branch_depth + 1)
    word_m = parity_prefix(m, branch_depth + 1)
    if word_n[:branch_depth] != word_m[:branch_depth] or word_n[branch_depth] == word_m[branch_depth]:
        raise AssertionError("branch-depth identity failed")
    shared_word = word_n[:branch_depth]
    odd_count = shared_word.count("1")
    normalized = difference >> branch_depth
    transformed_n = iterate(n, branch_depth)
    transformed_m = iterate(m, branch_depth)
    transformed_gap = transformed_m - transformed_n
    if transformed_gap != 3**odd_count * normalized or transformed_gap % 2 != 1:
        raise AssertionError("transformed-gap identity failed")
    result: dict[str, object] = {
        "n": n,
        "m": m,
        "difference": difference,
        "branch_depth": branch_depth,
        "normalized_odd_gap": normalized,
        "shared_parity_prefix": shared_word,
        "shared_odd_count": odd_count,
        "branch_bits": word_n[branch_depth] + word_m[branch_depth],
        "transformed_gap": transformed_gap,
        "surplus_numerator": 3**odd_count,
        "surplus_denominator": 1 << branch_depth,
    }
    if stopping is not None:
        result.update(
            {
                "n_stopping_time": stopping[n],
                "m_stopping_time": stopping[m],
                "max_joint_safe_depth": min(stopping[n], stopping[m]) - 1,
            }
        )
    return result


def stopping_times(bound: int) -> tuple[list[int], str]:
    values = [0] * (bound + 1)
    digest = hashlib.sha256()
    for start in range(2, bound + 1):
        value = coefficient_stopping_time(start)
        values[start] = value
        digest.update(f"{start}:{value}\n".encode("ascii"))
    return values, digest.hexdigest()


def better(candidate: tuple[int, int], existing: tuple[int, int] | None) -> bool:
    return existing is None or candidate[0] > existing[0] or (candidate[0] == existing[0] and candidate[1] < existing[1])


def branch_profile(bound: int, stopping: list[int]) -> list[dict[str, object]]:
    maximum_h = (bound - 2).bit_length() - 1
    profile = []
    for branch_depth in range(maximum_h + 1):
        mask = (1 << branch_depth) - 1
        buckets: dict[int, list[tuple[int, int] | None]] = {}
        for start in range(2, bound + 1):
            residue = start & mask
            side = (start >> branch_depth) & 1
            bucket = buckets.setdefault(residue, [None, None])
            candidate = (stopping[start], start)
            if better(candidate, bucket[side]):
                bucket[side] = candidate
        best_key: tuple[int, int, int] | None = None
        best_pair: tuple[int, int] | None = None
        for sides in buckets.values():
            if sides[0] is None or sides[1] is None:
                continue
            first, second = sides[0][1], sides[1][1]
            n, m = sorted((first, second))
            depth = min(sides[0][0], sides[1][0]) - 1
            key = (-depth, m - n, n)
            if best_key is None or key < best_key:
                best_key = key
                best_pair = (n, m)
        if best_pair is None:
            raise AssertionError(f"missing pair for branch depth {branch_depth}")
        record = branch_record(*best_pair, stopping=stopping)
        if record["branch_depth"] != branch_depth:
            raise AssertionError("profile selected the wrong valuation class")
        profile.append(record)
    return profile


def affine_constant(word: str) -> tuple[int, int]:
    coefficient = 1
    constant = 0
    denominator = 1
    for bit in word:
        if bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
        denominator *= 2
    return constant, coefficient


def inverse_parity_residue(word: str) -> int:
    constant, odd_power = affine_constant(word)
    modulus = 1 << len(word)
    residue = (-constant * pow(odd_power, -1, modulus)) % modulus
    return residue or modulus


def digest_pairs(label: str, values: list[int], digest: hashlib._Hash) -> int:
    unique = sorted(set(values))
    count = 0
    for n, m in zip(unique, unique[1:]):
        record = branch_record(n, m)
        digest.update(
            (
                f"{label}|{n}|{m}|{record['branch_depth']}|{record['normalized_odd_gap']}|"
                f"{record['shared_odd_count']}|{record['branch_bits']}|{record['transformed_gap']}\n"
            ).encode("ascii")
        )
        count += 1
    return count


def adversarial_audit() -> dict[str, object]:
    digest = hashlib.sha256()
    counts = {
        "2^m_minus_1": digest_pairs("2m", [(1 << exponent) - 1 for exponent in range(1, 65)], digest),
        "8^m_minus_5": digest_pairs("8m", [(1 << (3 * exponent)) - 5 for exponent in range(1, 33)], digest),
    }
    block_values = []
    for mask in range(4096):
        word = "".join("111" if mask & (1 << index) else "110" for index in range(12))
        block_values.append(inverse_parity_residue(word))
    counts["(110|111)^star"] = digest_pairs("blocks", block_values, digest)
    mixed_values = [inverse_parity_residue(A_WORD * r + B_WORD * s) for r in range(1, 33) for s in range(1, 33)]
    counts["A^rB^s"] = digest_pairs("mixed", mixed_values, digest)
    counts["A_and_B"] = digest_pairs("AB", [inverse_parity_residue(A_WORD), inverse_parity_residue(B_WORD)], digest)
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


def exhaustive_audit(limit: int = 256) -> dict[str, object]:
    digest = hashlib.sha256()
    count = 0
    for n in range(2, limit + 1):
        for m in range(n + 1, limit + 1):
            record = branch_record(n, m)
            digest.update(
                (
                    f"{n}|{m}|{record['branch_depth']}|{record['normalized_odd_gap']}|"
                    f"{record['shared_parity_prefix']}|{record['branch_bits']}|{record['transformed_gap']}\n"
                ).encode("ascii")
            )
            count += 1
    return {"repository_status": "VERIFIED_FINITE", "limit": limit, "pairs_checked": count, "row_digest_sha256": digest.hexdigest()}


def generate(artifact_dir: Path, bound: int = DEFAULT_BOUND) -> dict[str, object]:
    if bound < 4:
        raise ValueError("bound must be at least 4")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    times, digest = stopping_times(bound)
    profile = branch_profile(bound, times)
    data = {
        "format": "collatz-branch-point-decomposition-v1",
        "P66": {
            "repository_status": "VERIFIED_THEOREM",
            "statement": "For positive n<m and d=m-n, the parity prefixes agree for exactly h=v2(d) steps, then split; after the common prefix the gap is 3^a*(d/2^h), an odd integer.",
            "residue_equivalence": "the first j parity bits agree iff n=m (mod 2^j)",
            "induction_step": "each prescribed shortcut branch is an odd-affine bijection modulo the next power of two",
            "affine_gap_identity": "T^h(m)-T^h(n)=3^a*(m-n)/2^h",
        },
        "P67": {
            "repository_status": "CONDITIONAL",
            "dependencies": ["P63", "P64"],
            "q0_positive_gap_conditions": ["0<d<=4142380786", "4|d", "N,X are coefficient-safe through K0-1"],
            "branch_depth_range": [2, 31],
            "case_count": 30,
            "conclusion": "a positive q0 near-return pair shares exactly h parity steps for one of 2<=h<=31, then enters opposite parity branches with odd transformed gap",
            "remaining_obligation": "exclude simultaneous continuation of both budgeted coefficient-safe tails in every one of the 30 cases",
        },
        "E16": {
            "repository_status": "VERIFIED_FINITE",
            "bound_H": bound,
            "stopping_time_digest_sha256": digest,
            "definition": "R_h(H)=max min(tau(n),tau(m))-1 over 2<=n<m<=H with v2(m-n)=h",
            "maximum_branch_depth_present": len(profile) - 1,
            "profile": profile,
            "exhaustive_pair_audit": exhaustive_audit(),
        },
        "mandatory_adversarial_audit": adversarial_audit(),
        "dependencies": {
            "phase10_gap_modulus_sha256": sha256(artifact_dir / "phase10_gap_modulus.json"),
            "phase10_safe_pair_spacing_sha256": sha256(artifact_dir / "phase10_safe_pair_spacing.json"),
        },
        "C05_reformulation": {
            "repository_status": "OPEN",
            "scope": "the q0-specific positive gaps 0<d<=W, not every pair quantified by global C05",
            "statement": "the positive-gap q0 consequence needed from C05 can instead be obtained by excluding all 30 branch-depth cases h=2,...,31 below 2^72; global C05 is stronger",
            "certificate_found": False,
        },
        "what_this_result_does_not_prove": "The branch decomposition is exact, but the finite profile supplies no q0 continuation bound and does not prove C04, C05, or Collatz.",
        "proves_collatz": False,
    }
    output = artifact_dir / "branch_point_decomposition.json"
    output.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary = {
        "artifact": str(output),
        "bound_H": bound,
        "maximum_branch_depth_present": len(profile) - 1,
        "largest_finite_joint_safe_depth": max(row["max_joint_safe_depth"] for row in profile),
        "P66": "VERIFIED_THEOREM",
        "P67": "CONDITIONAL",
        "C05": "OPEN",
        "proves_collatz": False,
    }
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--bound", type=int, default=DEFAULT_BOUND)
    args = parser.parse_args()
    print(json.dumps(generate(args.artifact_dir, args.bound), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
