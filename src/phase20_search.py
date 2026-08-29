#!/usr/bin/env python3
"""Generate exact Phase 20 parity-complexity evidence.

Finite word statistics are diagnostics only.  The mathematical claims live in
the Phase 20 report and theory artifact with their external dependencies made
explicit.  No floating-point value is used for an acceptance decision.
"""

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


A_BITS = "11101"
B_BITS = "1100"


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def object_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def encoded(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def shortcut_step(value: int) -> int:
    return (3 * value + 1) // 2 if value & 1 else value // 2


def orbit_word(source: int, length: int) -> str:
    if source <= 0:
        raise ValueError("positive source required")
    bits: list[str] = []
    value = source
    for _ in range(length):
        bits.append(str(value & 1))
        value = shortcut_step(value)
    return "".join(bits)


def expand_exponents(exponents: list[int], length: int) -> str:
    word = "".join("1" + "0" * (exponent - 1) for exponent in exponents)
    if len(word) < length:
        raise ValueError("not enough exponent data")
    return word[:length]


def all_contact_word(length: int) -> str:
    positions: set[int] = set()
    odd_index = 0
    while True:
        position = (3**odd_index).bit_length() - 1
        if position >= length:
            break
        positions.add(position)
        odd_index += 1
    return "".join("1" if index in positions else "0" for index in range(length))


def square_root_word(length: int) -> str:
    floor_log = defect = 0
    exponents: list[int] = []
    index = 0
    while sum(exponents) < length:
        next_floor = (3 ** (index + 1)).bit_length() - 1
        increment = int(next_floor - floor_log == 2 and defect < isqrt(index + 1))
        exponent = next_floor - floor_log - increment
        if exponent not in (1, 2):
            raise AssertionError("square-root exponent")
        exponents.append(exponent)
        defect += increment
        floor_log = next_floor
        index += 1
    return expand_exponents(exponents, length)


def interval_controller_word(length: int) -> str:
    state = Fraction(3, 2)
    exponents: list[int] = []
    while sum(exponents) < length:
        if not 1 < state <= 2:
            raise AssertionError("interval controller escaped")
        exponent = 1 if state <= Fraction(5, 3) else 2
        exponents.append(exponent)
        state = (3 * state - 1) / (1 << exponent)
    return expand_exponents(exponents, length)


def p109_word(length: int, threshold: int = 8) -> str:
    odd = elapsed = 0
    bits: list[str] = []
    while elapsed < length:
        bit = int(3**odd <= threshold * (1 << elapsed))
        bits.append(str(bit))
        odd += bit
        elapsed += 1
    return "".join(bits)


def periodic_word(pattern: str, length: int) -> str:
    if not pattern or set(pattern) - {"0", "1"}:
        raise ValueError("binary pattern required")
    return (pattern * ((length + len(pattern) - 1) // len(pattern)))[:length]


def affine_constant(word: str) -> int:
    value = 0
    for position, bit in enumerate(word):
        if bit == "1":
            value = 3 * value + (1 << position)
        elif bit != "0":
            raise ValueError("binary word required")
    return value


def source_residue(word: str) -> int:
    modulus = 1 << len(word)
    odd = word.count("1")
    return (-affine_constant(word) * pow(3**odd, -1, modulus)) % modulus


def source_lifts(word: str) -> tuple[list[int], list[int]]:
    residues: list[int] = []
    lifts: list[int] = []
    affine = odd = 0
    old_residue = 0
    old_modulus = 1
    for position, bit in enumerate(word):
        if bit == "1":
            affine = 3 * affine + (1 << position)
            odd += 1
        modulus = 1 << (position + 1)
        residue = (-affine * pow(3**odd, -1, modulus)) % modulus
        lift = (residue - old_residue) // old_modulus
        if lift not in (0, 1):
            raise AssertionError("binary source lift")
        residues.append(residue)
        lifts.append(lift)
        old_residue, old_modulus = residue, modulus
    return residues, lifts


def coefficient_relation(length: int, odd: int) -> str:
    left, right = 3**odd, 1 << length
    return "above" if left > right else ("below" if left < right else "equal")


def safety_horizon(word: str) -> dict[str, object]:
    odd = 0
    for length, bit in enumerate(word, 1):
        odd += bit == "1"
        if 3**odd <= 1 << length:
            return {
                "strict_safe_steps": length - 1,
                "first_failure_step": length,
                "failure_relation": coefficient_relation(length, odd),
            }
    return {
        "strict_safe_steps": len(word),
        "first_failure_step": None,
        "finite_prefix_only": True,
    }


def rolling_factor_metrics(word: str, maximum_factor: int) -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for width in range(1, min(maximum_factor, len(word)) + 1):
        mask = (1 << width) - 1
        code = int(word[:width], 2)
        factors = {code}
        counts = {code.bit_count()}
        for end in range(width, len(word)):
            code = ((code << 1) & mask) | int(word[end])
            factors.add(code)
            counts.add(code.bit_count())
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


def sequence_record(name: str, kind: str, word: str, maximum_factor: int) -> dict[str, object]:
    residues, lifts = source_lifts(word)
    checkpoints = []
    for length in (1, 2, 4, 8, 16, 32, 64, 128, 256, len(word)):
        if length > len(word) or any(row["length"] == length for row in checkpoints):
            continue
        odd = word[:length].count("1")
        checkpoints.append(
            {
                "length": length,
                "ones": odd,
                "frequency": encoded(Fraction(odd, length)),
                "coefficient_relation": coefficient_relation(length, odd),
                "source_residue": str(residues[length - 1]),
                "lift": lifts[length - 1],
            }
        )
    trailing = 0
    for lift in reversed(lifts):
        if lift:
            break
        trailing += 1
    metrics = rolling_factor_metrics(word, maximum_factor)
    return {
        "name": name,
        "kind": kind,
        "length": len(word),
        "word": word,
        "word_sha256": hashlib.sha256(word.encode("ascii")).hexdigest(),
        "ones": word.count("1"),
        "empirical_frequency": encoded(Fraction(word.count("1"), len(word))),
        "coefficient_safety": safety_horizon(word),
        "source_lifts": {
            "nonzero": sum(lifts),
            "trailing_zero": trailing,
            "latest_nonzero_step": max((index + 1 for index, bit in enumerate(lifts) if bit), default=None),
            "final_residue": str(residues[-1]),
            "lift_digest_sha256": object_digest(lifts),
        },
        "prefix_checkpoints": checkpoints,
        "factor_metrics": metrics,
        "factor_metric_digest_sha256": object_digest(metrics),
    }


def theory_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase20-theory-v1",
        "claims": {
            "EXT08": "EXTERNAL_THEOREM",
            "EXT09": "EXTERNAL_THEOREM",
            "EXT10": "EXTERNAL_THEOREM",
            "EXT11": "EXTERNAL_THEOREM",
            "EXT12": "EXTERNAL_THEOREM",
            "EXT13": "EXTERNAL_THEOREM",
            "P117": "VERIFIED_THEOREM",
            "P118": "VERIFIED_THEOREM",
            "P119": "CONDITIONAL",
            "P120": "VERIFIED_THEOREM",
            "P121": "CONDITIONAL",
            "P122": "VERIFIED_THEOREM",
            "P123": "CONDITIONAL",
            "P124": "CONDITIONAL",
            "E32": "VERIFIED_FINITE",
            "H112": "OPEN",
            "H72": "OPEN",
        },
        "map_convention": "T(x)=x/2 for even x and T(x)=(3x+1)/2 for odd x; v_l is the parity of the input to shortcut step l",
        "critical_density": "rho_c=ln(2)/ln(3)",
        "P117": {
            "hypotheses": "positive nonperiodic permanent coefficient-safe shortcut orbit covered by P72",
            "bounded_case": "If 0<h(l)-rho_c*l<=K for all l>=1, then beta_q>=q/3^(K+1), contradicting P72 beta_q=O_S(q^(1/9)).",
            "quantitative_case": "If D_j=ln(3^j/2^E_j)<=gamma*ln(j+2)+K globally for gamma<8/9, then beta_q grows at least as q^(1-gamma), contradicting P72.",
            "exact_threshold": "gamma<8/9 iff 1-gamma>1/9",
            "external_dependency": "none",
        },
        "P118": {
            "statement": "rho_c is transcendental",
            "proof": "rho_c is irrational by unique factorization; if it were algebraic irrational, EXT09 would make 3^rho_c transcendental, contrary to 3^rho_c=2 on the positive real branch.",
            "dependency": "EXT09",
        },
        "P119": {
            "dependency": "EXT08, P118, and the class-specific EXT10/EXT11/EXT13 input",
            "statement": "A rational 2-adic noncyclic shortcut orbit cannot have an algebraic natural parity-one frequency; consequently it cannot have a frequency-bearing morphic, pure binary morphic, primitive substitutive, or k-automatic parity word under the recorded external theorems.",
            "automatic_repair": "EXT11 supplies rational lower density, so no natural-density existence assumption is needed for k-automatic words.",
            "boundary": "General morphic words can lack natural frequency; logarithmic frequency is not substituted.",
        },
        "P120": {
            "statement": "For a K-balanced binary word the natural one-frequency rho exists and every length-n factor u satisfies ||u|_1-rho*n|<=K.",
            "proof": "The maximum factor count A_n is subadditive and the minimum B_n is superadditive. Their Fekete limits agree because 0<=A_n-B_n<=K; B_n<=rho*n<=A_n gives the bound.",
            "external_dependency": "none beyond the elementary subadditive/superadditive lemma proved in the report",
        },
        "P121": {
            "statement": "Under EXT08, every positive ordinary permanent-safe nonperiodic candidate has unbounded balance and unbounded binary abelian factor complexity.",
            "dependencies": ["P117", "P120", "EXT08"],
        },
        "P122": {
            "statement": "A non-erasing morphic image of a Sturmian word has a natural output frequency and uniformly bounded prefix discrepancy about it.",
            "proof": "Sturmian letter counts differ from slope times block count by at most one; complete image blocks are affine functions of that count, and one partial image block contributes a fixed error.",
            "erasing_audit": "The Cassaigne condition phi(ab)!=phi(ba) forces both binary letter images to be nonempty.",
            "external_dependency": "the defining Sturmian balance property only; the algebraic derivation is internal",
        },
        "P123": {
            "statement": "Under EXT08 and EXT12, no positive ordinary permanent-safe nonperiodic candidate is quasi-Sturmian.",
            "dependencies": ["P117", "P122", "EXT08", "EXT12"],
        },
        "P124": {
            "statement": "Under EXT08 and P116, every such candidate satisfies p_v(n)-n -> infinity.",
            "proof": "Non-eventual-periodicity gives p(n+1)>p(n), hence p(n)-n is nondecreasing; bounded excess would be eventually constant and therefore quasi-Sturmian, contrary to P123.",
            "dependencies": ["P116", "P123", "EXT08", "EXT12"],
            "boundary": "This does not imply superlinear complexity, positive entropy, or randomness.",
        },
        "phase18_correction": "The fixed-packet P109 schedule is excluded internally by P114, not P112. Phase 20 adds class exclusions but no closed full-language automaton.",
        "what_this_result_does_not_prove": "The results do not exclude all permanent-safe words, prove H112 or H72, eliminate nontrivial cycles, or prove the Collatz conjecture.",
        "proves_collatz": False,
    }


def literature_artifact() -> dict[str, object]:
    return {
        "format": "collatz-phase20-literature-audit-v1",
        "sources": [
            {
                "claim": "EXT08",
                "authors": "Josefina Lopez and Peter Stoll",
                "title": "The 3x+1 Periodicity Conjeture in R",
                "year": 2021,
                "identifier": "arXiv:2101.12747v1",
                "url": "https://arxiv.org/abs/2101.12747",
                "audited_result": "Theorem aperiodic: if zeta in Q_odd has an infinite orbit, liminf h(l)/l=ln(2)/ln(3).",
                "audit_depth": "arXiv TeX source The3xinR.tex, theorem and proof; not abstract-only",
                "map_match": "exact shortcut map T(x)=x/2 or (3x+1)/2 and input-parity convention",
            },
            {
                "claim": "EXT09",
                "authors": "A. O. Gelfond and Theodor Schneider",
                "title": "Gelfond-Schneider theorem",
                "year": 1934,
                "identifier": "classical transcendence theorem",
                "audited_result": "If algebraic alpha is neither 0 nor 1 and algebraic beta is irrational, every value of alpha^beta is transcendental.",
                "repository_use": "alpha=3, beta=ln(2)/ln(3), positive real value 2",
            },
            {
                "claim": "EXT10",
                "authors": "Jean-Paul Allouche and Jeffrey Shallit; Kalle Saari",
                "title": "Automatic Sequences, Theorem 8.4.5; On the Frequency of Letters in Pure Binary Morphic Sequences",
                "year": "2003; 2005",
                "identifier": "ISBN 9780521823326; DOI 10.1007/11505877_35",
                "audited_result": "An existing morphic letter frequency is algebraic; every pure binary morphic word has letter frequencies.",
                "boundary": "The first statement does not assert existence for every general morphic word.",
            },
            {
                "claim": "EXT11",
                "authors": "Jason P. Bell",
                "title": "The upper density of an automatic set is rational",
                "year": 2020,
                "identifier": "DOI 10.5802/jtnb.1135",
                "url": "https://doi.org/10.5802/jtnb.1135",
                "audited_result": "The lower and upper asymptotic densities of every k-automatic set are recursively computable rational numbers.",
            },
            {
                "claim": "EXT12",
                "authors": "Julien Cassaigne",
                "title": "Sequences with grouped factors",
                "year": 1997,
                "identifier": "Developments in Language Theory III, pp. 211-222",
                "audited_result": "A quasi-Sturmian word is a finite prefix followed by a morphic image of a Sturmian word, with phi(ab)!=phi(ba).",
                "hypothesis_audit": "The inequality rules out erasing either of the two source letters.",
            },
            {
                "claim": "EXT13",
                "authors": "Classical Perron-Frobenius/substitution theory",
                "title": "Primitive substitution frequency theorem",
                "identifier": "standard primitive incidence-matrix theorem",
                "audited_result": "Primitive substitutive words have letter frequencies given by a normalized positive Perron eigenvector; these coordinates are algebraic.",
            },
            {
                "claim": "overlap-context",
                "authors": "Thomas Sterin",
                "title": "A tree-based exploration of the Collatz conjecture",
                "year": 2020,
                "identifier": "arXiv:1907.00775",
                "repository_role": "source-bit, first-occurrence, and regular-ancestor context; no Phase 20 novelty claim is based on it",
            },
        ],
        "external_boundary": "EXT08-EXT13 are cited inputs, not independently reproved by code. Repository consequences keep their dependency labels.",
        "proves_collatz": False,
    }


def complexity_artifact(prefix_length: int, maximum_factor: int) -> dict[str, object]:
    definitions = [
        ("all_contact", "formal critical upper mechanical word", all_contact_word(prefix_length)),
        ("ng22_square_root", "formal Phase 13 square-root defect controller", square_root_word(prefix_length)),
        ("ng22_interval", "formal interval controller", interval_controller_word(prefix_length)),
        ("p109_balanced", "formal Phase 18 fixed-packet schedule", p109_word(prefix_length)),
        ("source_167", "actual positive shortcut orbit; E31 finite obstruction", orbit_word(167, prefix_length)),
        ("source_1126015", "actual E25 coefficient-depth record source", orbit_word(1_126_015, prefix_length)),
        ("source_1394431", "actual E25 ancestral-depth record source", orbit_word(1_394_431, prefix_length)),
        ("two_power_minus_one", "mandatory source family m=20", orbit_word((1 << 20) - 1, prefix_length)),
        ("eight_power_minus_five", "mandatory source family m=8", orbit_word(8**8 - 5, prefix_length)),
        ("alternating_110_111", "mandatory formal (110|111)^* sample", periodic_word("110111", prefix_length)),
        ("A_periodic", "mandatory formal A=11101 sample", periodic_word(A_BITS, prefix_length)),
        ("B_periodic", "mandatory formal B=1100 sample", periodic_word(B_BITS, prefix_length)),
        ("A8B8_periodic", "mandatory formal A^rB^s sample", periodic_word(A_BITS * 8 + B_BITS * 8, prefix_length)),
    ]
    records = [sequence_record(name, kind, word, maximum_factor) for name, kind, word in definitions]
    return {
        "format": "collatz-phase20-complexity-audit-v1",
        "claim": {"E32": "VERIFIED_FINITE"},
        "prefix_length": prefix_length,
        "maximum_factor_length": maximum_factor,
        "sequence_count": len(records),
        "sequences": records,
        "sequence_digest_sha256": object_digest(records),
        "finite_boundary": "Every statistic concerns only the stored finite prefix. No row certifies morphicity, automaticity, quasi-Sturmian structure, balance, or an asymptotic complexity law.",
        "proves_collatz": False,
    }


def adversarial_artifact(maximum_parameter: int = 20) -> dict[str, object]:
    source_rows = []
    for family in ("2^m-1", "8^m-5"):
        for m in range(2, maximum_parameter + 1):
            source = (1 << m) - 1 if family == "2^m-1" else 8**m - 5
            word = orbit_word(source, 128)
            source_rows.append(
                {
                    "family": family,
                    "m": m,
                    "source": str(source),
                    "word_sha256": hashlib.sha256(word.encode()).hexdigest(),
                    "safety": safety_horizon(word),
                }
            )
    block_rows = []
    for r in range(1, 9):
        for s in range(1, 9):
            word = A_BITS * r + B_BITS * s
            q, length = word.count("1"), len(word)
            block_rows.append(
                {
                    "r": r,
                    "s": s,
                    "L": length,
                    "q": q,
                    "multiplier_relation": coefficient_relation(length, q),
                    "absolute_power_gap": str(abs(3**q - (1 << length))),
                    "word_sha256": hashlib.sha256(word.encode()).hexdigest(),
                }
            )
    return {
        "format": "collatz-phase20-adversarial-v1",
        "claim": {"E32": "VERIFIED_FINITE"},
        "families": ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"],
        "maximum_source_parameter": maximum_parameter,
        "source_rows": source_rows,
        "ArBs_rows": block_rows,
        "source_row_digest_sha256": object_digest(source_rows),
        "ArBs_row_digest_sha256": object_digest(block_rows),
        "boundary": "Finite regression preserves known adversaries; it is not evidence for a universal complexity lower bound.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 20 obstruction report

- Finite low excess is not an asymptotic classification: any stored prefix can
  be followed by a word of much larger factor complexity.
- The all-contact word and P109 schedule are formal symbolic controls, not
  positive ordinary counterexamples. P109 is excluded by P114, not P112.
- Both NG22 controllers satisfy strong analytic conditions at the formal/2-adic
  level; neither has a known positive ordinary source.
- Source 167 retains its long finite zero-lift warning and then loses
  coefficient safety. A finite zero suffix is not eventual stabilization.
- General morphic words may lack natural letter frequency. EXT10 is used only
  when frequency exists, except for the separately audited pure binary case.
- Unbounded balance and `p(n)-n -> infinity` still permit zero entropy and
  complexity `n+o(n)`. Randomness and a linear excess are not proved.

## What this result does not prove

Phase 20 does not prove H112 or H72, exclude every infinite coefficient-safe
tail, eliminate nontrivial cycles, or prove the Collatz conjecture.

`proves_collatz=false`
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--prefix-length", type=int, default=512)
    parser.add_argument("--maximum-factor", type=int, default=64)
    args = parser.parse_args()
    if args.prefix_length < 256 or not 1 <= args.maximum_factor <= args.prefix_length:
        raise ValueError("invalid finite audit bounds")
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.artifact_dir / "phase20_theory.json", theory_artifact())
    write_json(args.artifact_dir / "phase20_literature_audit.json", literature_artifact())
    write_json(
        args.artifact_dir / "phase20_complexity_audit.json",
        complexity_artifact(args.prefix_length, args.maximum_factor),
    )
    write_json(args.artifact_dir / "phase20_adversarial.json", adversarial_artifact())
    (args.artifact_dir / "phase20_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")
    print("valid=true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
