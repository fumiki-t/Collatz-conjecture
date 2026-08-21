#!/usr/bin/env python3
"""Phase 3 mixed-modulus reverse-merge certificate search."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import TextIO

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.boundary_gap import audit_boundary_gaps
from src.phase3_model import (
    LatticeNode,
    ReverseMergeWitness,
    coefficient_survivors,
    find_reverse_merge,
    represented_minimum,
)

FORMAT = "collatz-phase3-mixed-merge-v1"


def coefficient_dp(max_depth: int) -> dict[str, object]:
    states: dict[int, int] = {0: 1}
    survivors = [1]
    first_crossings: list[int] = []
    distributions: list[dict[str, int]] = [{"0": 1}]
    for depth in range(1, max_depth + 1):
        next_states: dict[int, int] = defaultdict(int)
        crossing = 0
        for odd_count, count in states.items():
            for bit in (0, 1):
                next_odds = odd_count + bit
                if pow(3, next_odds) >= 1 << depth:
                    next_states[next_odds] += count
                else:
                    crossing += count
        states = dict(next_states)
        survivors.append(sum(states.values()))
        first_crossings.append(crossing)
        distributions.append({str(q): states[q] for q in sorted(states)})
    expected = {
        10: 64,
        15: 1295,
        20: 27328,
        22: 93222,
        26: 1037374,
    }
    checks = {str(depth): survivors[depth] == count for depth, count in expected.items()}
    checks["split_sum"] = sum(survivors[:26]) == 1227442
    checks["first_crossing_total"] = sum(first_crossings[:26]) == 190069
    return {
        "method": "coefficient_only_dynamic_program_no_collatz_orbits",
        "survivors": survivors,
        "first_crossings": first_crossings,
        "odd_count_distributions": distributions,
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "interpretation": (
            "through depth 26, OPEN is exactly the generalized Ballot language "
            "whose every prefix satisfies 3^q >= 2^k"
        ),
    }


def audit_existing_phase1(path: Path) -> dict[str, object]:
    """Independently extract domain-zero boundary margins from Phase 1 records."""

    first = True
    boundary_count = 0
    minimum: dict[str, object] | None = None
    violations: list[dict[str, object]] = []
    domain_exceptions = 0
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            text = line.rstrip("\n")
            if first:
                first = False
                if ',"records":[' not in text:
                    raise ValueError("invalid Phase 1 certificate header")
                continue
            if text.startswith('null],"summary":'):
                break
            if not text.endswith(","):
                raise ValueError("malformed Phase 1 record")
            record = json.loads(text[:-1])
            k, r, y, q, word, rule = record
            if rule != "DESCENT" or k < 1 or not word.endswith("0"):
                continue
            parent_depth = k - 1
            a = pow(3, q)
            b = 1 << parent_depth
            if not (b <= a < 2 * b):
                continue
            epsilon = 1 if r >= b else 0
            parent_r = r - epsilon * b
            parent_y = 2 * y - epsilon * a
            t_min = max(0, -((parent_r - 2) // b))
            if t_min != 0:
                domain_exceptions += 1
                continue
            expected_epsilon = parent_y % 2
            margin = 2 * parent_r - parent_y + epsilon * (2 * b - a)
            row = {
                "boundary_depth": k,
                "parent_r": parent_r,
                "parent_y": parent_y,
                "q": q,
                "word": word[:-1],
                "epsilon": epsilon,
                "margin": margin,
            }
            boundary_count += 1
            if epsilon != expected_epsilon or margin <= 0:
                violations.append(row)
            if minimum is None or (margin, word) < (int(minimum["margin"]), str(minimum["word"])):
                minimum = row
    return {
        "certificate": str(path),
        "domain": "boundary parents with t_min=0",
        "boundary_descent_records": boundary_count,
        "excluded_positive_t_min_records": domain_exceptions,
        "minimum_margin": minimum,
        "violations": violations,
        "all_margins_positive": not violations,
    }


def no_go_language_audit(blocks: int = 12) -> dict[str, object]:
    words = [""]
    for _ in range(blocks):
        words = [prefix + block for prefix in words for block in ("110", "111")]
    violations: list[str] = []
    periodic = 0
    for word in words:
        odds = 0
        for depth, bit in enumerate(word, start=1):
            odds += bit == "1"
            if pow(3, odds) < 1 << depth:
                violations.append(word)
                break
        if any(
            all(word[index] == word[index % period] for index in range(len(word)))
            for period in range(1, len(word))
        ):
            periodic += 1
    return {
        "language": "(110|111)^*",
        "blocks": blocks,
        "words_exhaustively_checked": len(words),
        "coefficient_violations": violations,
        "strictly_nonperiodic_words": len(words) - periodic,
        "periodic_dictionary_used_for_closure": False,
    }


STATS_FIELDS = [
    "ternary_level",
    "r",
    "M",
    "y",
    "A",
    "t_min",
    "parity_word",
    "ternary_path",
    "status",
    "reverse_odd_steps",
    "reverse_exponent_sum",
    "reverse_exponents",
    "smaller_family_constant",
    "smaller_family_slope",
    "minimum_represented_n",
]


class Phase3Writer:
    def __init__(self, certificate: TextIO, stats: csv.DictWriter, max_ternary: int) -> None:
        self.certificate = certificate
        self.stats = stats
        self.max_ternary = max_ternary
        self.records_by_level: Counter[int] = Counter()
        self.closed_by_level: Counter[int] = Counter()
        self.open_by_level: Counter[int] = Counter()
        self.split_by_level: Counter[int] = Counter()
        self.path_distribution: Counter[tuple[int, int]] = Counter()
        self.mixed_survivors: list[dict[str, object]] = []

    def record(self, node: LatticeNode, rule: object) -> None:
        self.certificate.write(
            json.dumps([*node.compact(), rule], separators=(",", ":")) + ",\n"
        )

    def stats_row(
        self,
        node: LatticeNode,
        status: str,
        witness: ReverseMergeWitness | None,
    ) -> None:
        self.stats.writerow(
            {
                "ternary_level": len(node.ternary_path),
                "r": node.r,
                "M": node.M,
                "y": node.y,
                "A": node.A,
                "t_min": node.t_min,
                "parity_word": node.parity,
                "ternary_path": "".join(map(str, node.ternary_path)),
                "status": status,
                "reverse_odd_steps": witness.odd_steps if witness else "",
                "reverse_exponent_sum": witness.exponent_sum if witness else "",
                "reverse_exponents": (
                    json.dumps(witness.exponents, separators=(",", ":")) if witness else ""
                ),
                "smaller_family_constant": witness.c if witness else "",
                "smaller_family_slope": witness.S if witness else "",
                "minimum_represented_n": represented_minimum(node),
            }
        )

    def visit(self, node: LatticeNode) -> None:
        level = len(node.ternary_path)
        self.records_by_level[level] += 1
        witness = find_reverse_merge(node)
        if witness is not None:
            self.closed_by_level[level] += 1
            self.path_distribution[(witness.odd_steps, witness.exponent_sum)] += 1
            self.record(node, ["REVERSE_MERGE", list(witness.exponents)])
            self.stats_row(node, "REVERSE_MERGE", witness)
            return
        if level < self.max_ternary:
            self.split_by_level[level] += 1
            self.record(node, "TERNARY_SPLIT")
            self.stats_row(node, "TERNARY_SPLIT", None)
            for child in node.ternary_children():
                self.visit(child)
            return
        self.open_by_level[level] += 1
        self.record(node, "OPEN")
        self.stats_row(node, "OPEN", None)
        self.mixed_survivors.append(
            {
                "node": {
                    "steps": node.steps,
                    "r": node.r,
                    "M": node.M,
                    "y": node.y,
                    "A": node.A,
                    "t_min": node.t_min,
                    "parity_word": node.parity,
                    "ternary_path": list(node.ternary_path),
                },
                "minimum_represented_n": represented_minimum(node),
                "obstruction": "no REVERSE_MERGE witness within the exact Phase 3 bounds",
            }
        )

    def summary(self) -> dict[str, object]:
        return {
            "records_by_ternary_level": {
                str(level): self.records_by_level[level]
                for level in range(self.max_ternary + 1)
            },
            "closed_by_ternary_level": {
                str(level): self.closed_by_level[level]
                for level in range(self.max_ternary + 1)
            },
            "split_by_ternary_level": {
                str(level): self.split_by_level[level]
                for level in range(self.max_ternary + 1)
            },
            "open_by_ternary_level": {
                str(level): self.open_by_level[level]
                for level in range(self.max_ternary + 1)
            },
            "reverse_path_distribution": [
                {"odd_steps": key[0], "exponent_sum": key[1], "count": count}
                for key, count in sorted(self.path_distribution.items())
            ],
            "open_count": len(self.mixed_survivors),
            "proves_collatz": False,
            "status": "partial_phase3_certificate_with_mixed_open_frontier",
        }


def preliminary_ternary_audit(binary_nodes: list[LatticeNode]) -> dict[str, object]:
    total = 0
    merged = 0
    for node in binary_nodes:
        for child in node.ternary_children():
            total += 1
            merged += find_reverse_merge(child) is not None
    return {
        "all_binary_parents_included": True,
        "children": total,
        "mergeable_children": merged,
        "expected_approximation_reproduced": total == 81984 and merged == 50244,
    }


def write_open_counts(
    path: Path, structure: dict[str, object], summary: dict[str, object]
) -> None:
    survivors = structure["survivors"]
    assert isinstance(survivors, list)
    with path.open("w", encoding="utf-8", newline="") as stream:
        fields = [
            "kind",
            "level",
            "total",
            "closed",
            "unresolved_at_level",
            "next_level_children",
            "previous_unresolved",
            "unresolved_growth_ratio",
        ]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for depth, count in enumerate(survivors):
            previous = survivors[depth - 1] if depth else ""
            writer.writerow(
                {
                    "kind": "BINARY_DP",
                    "level": depth,
                    "total": count,
                    "closed": "",
                    "unresolved_at_level": count,
                    "next_level_children": "",
                    "previous_unresolved": previous,
                    "unresolved_growth_ratio": f"{count}/{previous}" if depth else "",
                }
            )
        records = summary["records_by_ternary_level"]
        closed = summary["closed_by_ternary_level"]
        split = summary["split_by_ternary_level"]
        opened = summary["open_by_ternary_level"]
        assert all(isinstance(item, dict) for item in (records, closed, split, opened))
        previous_unresolved: int | str = ""
        for level in range(3):
            total = int(records[str(level)])
            closed_count = int(closed[str(level)])
            unresolved = int(split[str(level)]) if level < 2 else int(opened[str(level)])
            next_children = 3 * unresolved if level < 2 else ""
            writer.writerow(
                {
                    "kind": "TERNARY_REFINEMENT",
                    "level": level,
                    "total": total,
                    "closed": closed_count,
                    "unresolved_at_level": unresolved,
                    "next_level_children": next_children,
                    "previous_unresolved": previous_unresolved,
                    "unresolved_growth_ratio": (
                        f"{unresolved}/{previous_unresolved}"
                        if previous_unresolved != ""
                        else ""
                    ),
                }
            )
            previous_unresolved = unresolved


def generate_report(
    path: Path,
    structure: dict[str, object],
    phase1_audit: dict[str, object],
    preliminary: dict[str, object],
    summary: dict[str, object],
    mixed: list[dict[str, object]],
    boundary: dict[str, object],
    no_go: dict[str, object],
) -> None:
    records = summary["records_by_ternary_level"]
    closed = summary["closed_by_ternary_level"]
    split = summary["split_by_ternary_level"]
    assert isinstance(records, dict) and isinstance(closed, dict) and isinstance(split, dict)
    total_closed = sum(int(value) for value in closed.values())
    binary_total = int(records["0"])
    smallest = min(mixed, key=lambda row: (int(row["minimum_represented_n"]), str(row)))
    node = smallest["node"]
    assert isinstance(node, dict)
    minima = boundary["minima"]
    assert isinstance(minima, list)
    minimum_gap = min(minima, key=lambda row: (int(row["minimum_gap"]), int(row["boundary_depth"])))
    lines = [
        "# Phase 3 mixed-modulus obstruction report",
        "",
        "This is an independently checkable finite computation, not a proof of the Collatz conjecture.",
        "",
        "## Proved by the independent verifier",
        "",
        "- Every recorded TERNARY_SPLIT is an exact, disjoint, exhaustive partition of its parent parameter domain.",
        "- Every accepted REVERSE_MERGE has exact divisibility, positivity, strict-smaller-family inequalities, "
        "and an independently reconstructed forward affine path.",
        "- OPEN records are unresolved and carry no proof claim.",
        "",
        "## Exhaustive finite observations",
        "",
        f"- Coefficient DP checks all pass: `{structure['all_checks_pass']}`.",
        f"- Binary depth 20 generalized Ballot nodes: `{records['0']}`.",
        f"- Stage A binary REVERSE_MERGE closures: `{closed['0']}`.",
        f"- Preliminary all-parent ternary audit: `{preliminary['mergeable_children']}/{preliminary['children']}` children merge.",
        f"- Actual Stage B children: `{records['1']}`; closed `{closed['1']}`; refined `{split['1']}`.",
        f"- Actual Stage C children: `{records['2']}`; closed `{closed['2']}`; OPEN `{summary['open_count']}`.",
        f"- Existing Phase 1 domain-zero boundary margins are positive: `{phase1_audit['all_margins_positive']}`.",
        f"- Boundary-gap exact audit reaches boundary depth `{boundary['max_boundary_depth']}`; counterexample: `{boundary['counterexample']}`.",
        f"- Smallest finite-range boundary gap: `{minimum_gap['minimum_gap']}` at boundary depth `{minimum_gap['boundary_depth']}`.",
        f"- `(110|111)^*` words checked: `{no_go['words_exhaustively_checked']}`; coefficient violations: `{len(no_go['coefficient_violations'])}`.",
        "",
        "The Phase 2 OPEN frontier through depth 26 is exactly the coefficient-nonshrinking generalized Ballot "
        "language, not an arithmetically exceptional subcollection. The earlier 88% periodic-shadow statistic is "
        "therefore not a certified macro coverage rate.",
        "",
        "## Exact remaining obstruction",
        "",
        f"- Smallest unresolved represented integer: `{smallest['minimum_represented_n']}`.",
        f"- Family: `n(t)={node['r']}+{node['M']}*t`, `t >= {node['t_min']}`.",
        f"- Endpoint: `T^{node['steps']}(n(t))={node['y']}+{node['A']}*t`.",
        f"- Binary parity word: `{node['parity_word']}`; ternary path: `{node['ternary_path']}`.",
        "- This is an exact obstruction only to the bounded Phase 3 rule search, not an infinite Collatz obstruction theorem.",
        "",
        "## Growth and closure interpretation",
        "",
        f"- Level 0 unresolved parents after closure: `{split['0']}`.",
        f"- Level 1 unresolved children after merge attempts: `{split['1']}` "
        f"(`{split['1']}/{split['0']}`).",
        f"- Level 2 OPEN children: `{summary['open_count']}` "
        f"(`{summary['open_count']}/{split['1']}`).",
        "- The tested mixed-modulus unresolved population is supercritical/exponential-looking, not subcritical; "
        "no asymptotic classification is proved.",
        f"- All accepted closures use REVERSE_MERGE without a periodic-substring dictionary: "
        f"`{total_closed}/{total_closed}` (100% of closures). Stage A alone closes "
        f"`{closed['0']}/{binary_total}` original binary parents; later levels count ternary descendants.",
        "",
        "## Heuristic and conjectural status",
        "",
        "- No beam-search value is included in proof data. The depth-54 beam observation from the brief is not reproduced here.",
        "- The boundary-gap positivity hypothesis has only the finite exhaustive scope recorded in JSON.",
        "- A meaningful next rule must address the exact mixed survivors, likely by a ranked recursive dependency "
        "or a more general reverse-preimage lattice relation; increasing only the split depth is not enough.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(
    artifact_dir: Path,
    phase1_certificate: Path,
    binary_depth: int,
    max_ternary: int,
    boundary_depth: int,
) -> dict[str, object]:
    if max_ternary != 2:
        raise ValueError("the Phase 3 brief requires exactly two ternary refinement levels")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    structure = coefficient_dp(max(26, binary_depth))
    if not structure["all_checks_pass"]:
        raise AssertionError("Phase 1 structure audit failed")
    phase1_audit = audit_existing_phase1(phase1_certificate)
    if not phase1_audit["all_margins_positive"]:
        raise AssertionError("existing Phase 1 boundary margin audit failed")
    binary_nodes = coefficient_survivors(binary_depth)
    preliminary = preliminary_ternary_audit(binary_nodes)
    boundary = audit_boundary_gaps(boundary_depth)
    no_go = no_go_language_audit()

    certificate_path = artifact_dir / "phase3_certificate.json"
    stats_path = artifact_dir / "reverse_merge_stats.csv"
    with certificate_path.open("w", encoding="utf-8", newline="\n") as certificate, stats_path.open(
        "w", encoding="utf-8", newline=""
    ) as stats_stream:
        header = {
            "format": FORMAT,
            "version": 1,
            "binary_depth": binary_depth,
            "max_ternary_refinements": max_ternary,
            "reverse_exponent_sum_limit": binary_depth + 8,
        }
        encoded = json.dumps(header, separators=(",", ":"))
        certificate.write(encoded[:-1] + ',"records":[\n')
        stats_writer = csv.DictWriter(stats_stream, fieldnames=STATS_FIELDS, lineterminator="\n")
        stats_writer.writeheader()
        writer = Phase3Writer(certificate, stats_writer, max_ternary)
        for node in binary_nodes:
            writer.visit(node)
        summary = writer.summary()
        summary["structure_audit"] = structure
        summary["phase1_boundary_audit"] = phase1_audit
        summary["preliminary_ternary_audit"] = preliminary
        summary["no_go_audit"] = no_go
        certificate.write("null],\"summary\":")
        certificate.write(json.dumps(summary, separators=(",", ":"), sort_keys=True))
        certificate.write("}\n")

    mixed_payload = {
        "format": "collatz-phase3-mixed-survivors-v1",
        "count": len(writer.mixed_survivors),
        "survivors": sorted(
            writer.mixed_survivors,
            key=lambda row: (int(row["minimum_represented_n"]), str(row)),
        ),
        "claim_scope": "exact unresolved frontier for the configured bounded search",
    }
    (artifact_dir / "mixed_survivors.json").write_text(
        json.dumps(mixed_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (artifact_dir / "boundary_gap_minima.json").write_text(
        json.dumps(boundary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_open_counts(artifact_dir / "phase3_open_counts.csv", structure, summary)
    generate_report(
        artifact_dir / "phase3_obstruction_report.md",
        structure,
        phase1_audit,
        preliminary,
        summary,
        writer.mixed_survivors,
        boundary,
        no_go,
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument(
        "--phase1-certificate",
        type=Path,
        default=Path("artifacts/baseline_certificate.json"),
    )
    parser.add_argument("--binary-depth", type=int, default=20)
    parser.add_argument("--max-ternary", type=int, default=2)
    parser.add_argument("--boundary-depth", type=int, default=36)
    args = parser.parse_args()
    summary = generate(
        args.artifact_dir,
        args.phase1_certificate,
        args.binary_depth,
        args.max_ternary,
        args.boundary_depth,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
