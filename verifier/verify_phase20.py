#!/usr/bin/env python3
"""Independent exact verifier for Phase 20 parity-complexity artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from math import isqrt
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


A = "11101"
B = "1100"


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


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def ef(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def next_value(value: int) -> int:
    if value % 2:
        return (3 * value + 1) // 2
    return value // 2


def literal_orbit(source: int, length: int) -> str:
    result = []
    for _ in range(length):
        result.append("1" if source % 2 else "0")
        source = next_value(source)
    return "".join(result)


def expand(values: list[int], length: int) -> str:
    result = "".join("1" + "0" * (value - 1) for value in values)
    if len(result) < length:
        fail("short exponent expansion")
    return result[:length]


def mechanical(length: int) -> str:
    result = ["0"] * length
    q = 0
    while True:
        position = pow(3, q).bit_length() - 1
        if position >= length:
            break
        result[position] = "1"
        q += 1
    return "".join(result)


def square_controller(length: int) -> str:
    f = a = j = 0
    values = []
    total = 0
    while total < length:
        next_f = pow(3, j + 1).bit_length() - 1
        raise_a = next_f - f == 2 and a < isqrt(j + 1)
        e = next_f - f - int(raise_a)
        if e not in (1, 2):
            fail("square controller exponent")
        values.append(e)
        total += e
        a += int(raise_a)
        f = next_f
        j += 1
    return expand(values, length)


def interval_controller(length: int) -> str:
    h = Fraction(3, 2)
    values = []
    total = 0
    while total < length:
        if not Fraction(1) < h <= Fraction(2):
            fail("interval controller state")
        e = 1 if h <= Fraction(5, 3) else 2
        values.append(e)
        total += e
        h = (3 * h - 1) / pow(2, e)
    return expand(values, length)


def balanced_schedule(length: int) -> str:
    bits = []
    q = 0
    for elapsed in range(length):
        bit = pow(3, q) <= 8 * pow(2, elapsed)
        bits.append("1" if bit else "0")
        q += int(bit)
    return "".join(bits)


def repeat(pattern: str, length: int) -> str:
    return "".join(pattern[index % len(pattern)] for index in range(length))


def closed_affine(word: str) -> int:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    q = len(positions)
    return sum(pow(3, q - 1 - rank) * pow(2, position) for rank, position in enumerate(positions))


def residue(word: str) -> int:
    modulus = pow(2, len(word))
    return (-closed_affine(word) * pow(pow(3, word.count("1")), -1, modulus)) % modulus


def lift_rows(word: str) -> tuple[list[int], list[int]]:
    residues = []
    lifts = []
    old = 0
    old_modulus = 1
    for length in range(1, len(word) + 1):
        current = residue(word[:length])
        lift = (current - old) // old_modulus
        if lift not in (0, 1):
            fail("source lift outside bit range")
        residues.append(current)
        lifts.append(lift)
        old = current
        old_modulus *= 2
    return residues, lifts


def relation(length: int, ones: int) -> str:
    left, right = pow(3, ones), pow(2, length)
    if left > right:
        return "above"
    return "below" if left < right else "equal"


def safe_record(word: str) -> dict[str, object]:
    ones = 0
    for length, bit in enumerate(word, 1):
        ones += bit == "1"
        if pow(3, ones) <= pow(2, length):
            return {
                "strict_safe_steps": length - 1,
                "first_failure_step": length,
                "failure_relation": relation(length, ones),
            }
    return {"strict_safe_steps": len(word), "first_failure_step": None, "finite_prefix_only": True}


def direct_metrics(word: str, maximum: int) -> list[dict[str, int]]:
    rows = []
    for width in range(1, maximum + 1):
        factors = {word[start : start + width] for start in range(len(word) - width + 1)}
        counts = {factor.count("1") for factor in factors}
        # Sliding windows change their one count by at most one, so the set is
        # an integer interval; this independently checks abelian=balance+1.
        if len(counts) != max(counts) - min(counts) + 1:
            fail("abelian count interval")
        rows.append(
            {
                "n": width,
                "factor_complexity": len(factors),
                "excess": len(factors) - width,
                "balance": max(counts) - min(counts),
                "abelian_complexity": len(counts),
            }
        )
    return rows


def expected_sequence(name: str, kind: str, word: str, maximum: int) -> dict[str, object]:
    residues, lifts = lift_rows(word)
    checkpoints = []
    for length in (1, 2, 4, 8, 16, 32, 64, 128, 256, len(word)):
        if length > len(word) or length in {row["length"] for row in checkpoints}:
            continue
        ones = word[:length].count("1")
        checkpoints.append(
            {
                "length": length,
                "ones": ones,
                "frequency": ef(Fraction(ones, length)),
                "coefficient_relation": relation(length, ones),
                "source_residue": str(residues[length - 1]),
                "lift": lifts[length - 1],
            }
        )
    trailing = 0
    for item in reversed(lifts):
        if item:
            break
        trailing += 1
    metrics = direct_metrics(word, maximum)
    return {
        "name": name,
        "kind": kind,
        "length": len(word),
        "word": word,
        "word_sha256": hashlib.sha256(word.encode("ascii")).hexdigest(),
        "ones": word.count("1"),
        "empirical_frequency": ef(Fraction(word.count("1"), len(word))),
        "coefficient_safety": safe_record(word),
        "source_lifts": {
            "nonzero": sum(lifts),
            "trailing_zero": trailing,
            "latest_nonzero_step": max((index + 1 for index, bit in enumerate(lifts) if bit), default=None),
            "final_residue": str(residues[-1]),
            "lift_digest_sha256": digest(lifts),
        },
        "prefix_checkpoints": checkpoints,
        "factor_metrics": metrics,
        "factor_metric_digest_sha256": digest(metrics),
    }


def verify_theory(root: Path) -> None:
    value = load(root / "phase20_theory.json")
    expected_claims = {
        "EXT08": "EXTERNAL_THEOREM", "EXT09": "EXTERNAL_THEOREM",
        "EXT10": "EXTERNAL_THEOREM", "EXT11": "EXTERNAL_THEOREM",
        "EXT12": "EXTERNAL_THEOREM", "EXT13": "EXTERNAL_THEOREM",
        "P117": "VERIFIED_THEOREM", "P118": "VERIFIED_THEOREM",
        "P119": "CONDITIONAL", "P120": "VERIFIED_THEOREM",
        "P121": "CONDITIONAL", "P122": "VERIFIED_THEOREM",
        "P123": "CONDITIONAL", "P124": "CONDITIONAL",
        "E32": "VERIFIED_FINITE", "H112": "OPEN", "H72": "OPEN",
    }
    if value.get("format") != "collatz-phase20-theory-v1" or value.get("claims") != expected_claims:
        fail("theory claim graph")
    if value.get("proves_collatz") is not False:
        fail("Collatz boundary")
    if value.get("P117", {}).get("exact_threshold") != "gamma<8/9 iff 1-gamma>1/9":
        fail("P117 threshold")
    if value.get("P117", {}).get("external_dependency") != "none":
        fail("P117 external contamination")
    if value.get("P118", {}).get("dependency") != "EXT09":
        fail("P118 dependency")
    if "natural frequency" not in str(value.get("P119", {}).get("boundary", "")):
        fail("morphic frequency boundary")
    if "subadditive" not in str(value.get("P120", {}).get("proof", "")):
        fail("bounded balance proof")
    if "nonempty" not in str(value.get("P122", {}).get("erasing_audit", "")):
        fail("quasi-Sturmian erasing audit")
    if "superlinear" not in str(value.get("P124", {}).get("boundary", "")):
        fail("complexity interpretation boundary")
    if "P114, not P112" not in str(value.get("phase18_correction", "")):
        fail("Phase 18 attribution repair")


def verify_literature(root: Path) -> int:
    value = load(root / "phase20_literature_audit.json")
    sources = value.get("sources")
    if value.get("format") != "collatz-phase20-literature-audit-v1" or not isinstance(sources, list):
        fail("literature format")
    claims = {str(row.get("claim")) for row in sources if isinstance(row, dict)}
    if not {"EXT08", "EXT09", "EXT10", "EXT11", "EXT12", "EXT13", "overlap-context"} <= claims:
        fail("literature coverage")
    ls = next(row for row in sources if row.get("claim") == "EXT08")
    if "liminf" not in str(ls.get("audited_result")) or "not abstract-only" not in str(ls.get("audit_depth")):
        fail("López-Stoll quantifier audit")
    automatic = next(row for row in sources if row.get("claim") == "EXT11")
    if "lower and upper" not in str(automatic.get("audited_result")):
        fail("automatic density theorem")
    if value.get("proves_collatz") is not False:
        fail("literature Collatz boundary")
    return len(sources)


def verify_complexity(root: Path) -> dict[str, int]:
    value = load(root / "phase20_complexity_audit.json")
    length = int(value.get("prefix_length", 0))
    maximum = int(value.get("maximum_factor_length", 0))
    definitions = [
        ("all_contact", "formal critical upper mechanical word", mechanical(length)),
        ("ng22_square_root", "formal Phase 13 square-root defect controller", square_controller(length)),
        ("ng22_interval", "formal interval controller", interval_controller(length)),
        ("p109_balanced", "formal Phase 18 fixed-packet schedule", balanced_schedule(length)),
        ("source_167", "actual positive shortcut orbit; E31 finite obstruction", literal_orbit(167, length)),
        ("source_1126015", "actual E25 coefficient-depth record source", literal_orbit(1_126_015, length)),
        ("source_1394431", "actual E25 ancestral-depth record source", literal_orbit(1_394_431, length)),
        ("two_power_minus_one", "mandatory source family m=20", literal_orbit(pow(2, 20) - 1, length)),
        ("eight_power_minus_five", "mandatory source family m=8", literal_orbit(pow(8, 8) - 5, length)),
        ("alternating_110_111", "mandatory formal (110|111)^* sample", repeat("110111", length)),
        ("A_periodic", "mandatory formal A=11101 sample", repeat(A, length)),
        ("B_periodic", "mandatory formal B=1100 sample", repeat(B, length)),
        ("A8B8_periodic", "mandatory formal A^rB^s sample", repeat(A * 8 + B * 8, length)),
    ]
    expected = [expected_sequence(*definition, maximum) for definition in definitions]
    if value.get("format") != "collatz-phase20-complexity-audit-v1":
        fail("complexity format")
    if value.get("claim") != {"E32": "VERIFIED_FINITE"} or value.get("proves_collatz") is not False:
        fail("complexity claim boundary")
    if value.get("sequence_count") != len(expected) or value.get("sequences") != expected:
        fail("independent finite complexity reconstruction")
    if value.get("sequence_digest_sha256") != digest(expected):
        fail("complexity row digest")
    if "finite prefix" not in str(value.get("finite_boundary", "")):
        fail("finite-to-asymptotic boundary")
    return {"sequences": len(expected), "factor_rows": len(expected) * maximum}


def verify_adversarial(root: Path) -> dict[str, int]:
    value = load(root / "phase20_adversarial.json")
    maximum = int(value.get("maximum_source_parameter", 0))
    source_rows = []
    for family in ("2^m-1", "8^m-5"):
        for m in range(2, maximum + 1):
            source = pow(2, m) - 1 if family == "2^m-1" else pow(8, m) - 5
            word = literal_orbit(source, 128)
            source_rows.append({
                "family": family, "m": m, "source": str(source),
                "word_sha256": hashlib.sha256(word.encode()).hexdigest(),
                "safety": safe_record(word),
            })
    block_rows = []
    for r in range(1, 9):
        for s in range(1, 9):
            word = A * r + B * s
            q, length = word.count("1"), len(word)
            block_rows.append({
                "r": r, "s": s, "L": length, "q": q,
                "multiplier_relation": relation(length, q),
                "absolute_power_gap": str(abs(pow(3, q) - pow(2, length))),
                "word_sha256": hashlib.sha256(word.encode()).hexdigest(),
            })
    if value.get("format") != "collatz-phase20-adversarial-v1":
        fail("adversarial format")
    if value.get("source_rows") != source_rows or value.get("ArBs_rows") != block_rows:
        fail("adversarial rows")
    if value.get("source_row_digest_sha256") != digest(source_rows) or value.get("ArBs_row_digest_sha256") != digest(block_rows):
        fail("adversarial digests")
    expected_families = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]
    if value.get("families") != expected_families or value.get("proves_collatz") is not False:
        fail("mandatory family boundary")
    return {"source_rows": len(source_rows), "ArBs_rows": len(block_rows)}


def verify_obstruction(root: Path) -> None:
    text = (root / "phase20_obstruction_report.md").read_text(encoding="utf-8")
    for phrase in ("finite zero suffix", "General morphic", "p(n)-n", "What this result does not prove", "proves_collatz=false"):
        if phrase not in text:
            fail(f"obstruction boundary missing: {phrase}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    source = Path(__file__).read_text(encoding="utf-8")
    forbidden = ["src.phase20_" + "search", "from " + "src", "import " + "src"]
    if any(item in source for item in forbidden):
        fail("verifier imports generator")
    verify_theory(args.artifact_dir)
    literature_count = verify_literature(args.artifact_dir)
    complexity = verify_complexity(args.artifact_dir)
    adversarial = verify_adversarial(args.artifact_dir)
    verify_obstruction(args.artifact_dir)
    report = {
        "format": "collatz-phase20-verifier-v1",
        "valid": True,
        "claims": {"P117": "VERIFIED_THEOREM", "P118": "VERIFIED_THEOREM", "P120": "VERIFIED_THEOREM", "P122": "VERIFIED_THEOREM", "E32": "VERIFIED_FINITE", "H112": "OPEN", "H72": "OPEN"},
        "external_sources_audited": literature_count,
        "complexity": complexity,
        "adversarial": adversarial,
        "independence": "direct substring sets and closed affine sums; no generator import",
        "proves_collatz": False,
    }
    if args.write_report:
        args.write_report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"valid=false: {exc}", file=sys.stderr)
        raise SystemExit(1)
