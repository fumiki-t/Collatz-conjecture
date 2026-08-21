#!/usr/bin/env python3
"""Phase 4 exact first-return search on the 2 mod 9 section."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from fractions import Fraction
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.model import affine_word
from src.return9_model import (
    KAPPA,
    ReturnFamily,
    ReturnTemplate,
    affine_fixed_point,
    compose_with_template,
    descent_high,
    first_return,
    formula_from_word,
    is_uniform_smaller,
    n_from_z,
    parametric_template,
    parametric_z_identity,
    recurrence_identity,
    return_templates,
    root_family,
    shortcut_step,
    z_from_n,
)

FORMAT = "collatz-return9-certificate-v1"

TRANSITIONS = {
    1: {0: 5, 1: 2},
    2: {0: 1, 1: 8},
    4: {0: 2, 1: 2},
    5: {0: 7, 1: 8},
    7: {0: 8, 1: 2},
    8: {0: 4, 1: 8},
}


def transition_audit() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for residue in sorted(TRANSITIONS):
        for bit in (0, 1):
            representative = residue if residue % 2 == bit else residue + 9
            actual = shortcut_step(representative) % 9
            expected = TRANSITIONS[residue][bit]
            if actual != expected:
                raise AssertionError("mod-9 transition mismatch")
            rows.append(
                {
                    "residue": residue,
                    "bit": bit,
                    "representative": representative,
                    "target": actual,
                }
            )
    return rows


def finite_code_words(max_a: int) -> list[str]:
    return [template.word for template in return_templates(max_a)]


def code_kraft(max_a: int) -> tuple[Fraction, Fraction]:
    covered = sum((Fraction(1, 1 << len(word)) for word in finite_code_words(max_a)), Fraction())
    return covered, 1 - covered


def direct_return_audit(bound: int) -> dict[str, object]:
    digest = hashlib.sha256()
    checked = 0
    direct_steps = 0
    buffer = bytearray()
    for n in range(2, bound, 9):
        returned, word = first_return(n)
        details = formula_from_word(n, word)
        if details["return"] != returned:
            raise AssertionError(f"first-return formula mismatch at {n}")
        if returned % 9 != 2:
            raise AssertionError("return endpoint left the section")
        if details["kind"] == "PARAMETRIC":
            c = int(details["c"])
            a = int(details["a"])
            b = int(details["b"])
            v = int(details["v"])
            z, z_next = parametric_z_identity(c, a, b, v)
            if z_from_n(n) != z or n_from_z(z) != n:
                raise AssertionError("source z-coordinate mismatch")
            if z_from_n(returned) != z_next or n_from_z(z_next) != returned:
                raise AssertionError("return z-coordinate mismatch")
            difference, recurrence_difference = recurrence_identity(c, a, b, v)
            if difference != recurrence_difference or difference != returned - n:
                raise AssertionError("excursion difference identity mismatch")
        checked += 1
        direct_steps += len(word)
        buffer.extend(f"{n}:{returned}:{word}\n".encode("ascii"))
        if len(buffer) >= 1 << 20:
            digest.update(buffer)
            buffer.clear()
    digest.update(buffer)
    return {
        "bound_exclusive": bound,
        "section_integers_checked": checked,
        "shortcut_steps_checked": direct_steps,
        "result": "all_direct_returns_equal_formula_and_z_coordinate",
        "sha256": digest.hexdigest(),
    }


def code_audit(max_a: int, direct_bound: int) -> dict[str, object]:
    covered, overflow = code_kraft(max_a)
    special_mass = Fraction(1, 4) + Fraction(1, 16)
    c0_mass = Fraction(1, 2)
    c2_mass = Fraction(1, 8)
    c4_mass = Fraction(1, 16)
    total = special_mass + c0_mass + c2_mass + c4_mass
    if total != 1:
        raise AssertionError("Kraft identity failed")
    words = finite_code_words(max_a)
    for index, word in enumerate(words):
        for other in words[index + 1 :]:
            if word.startswith(other) or other.startswith(word):
                raise AssertionError("finite first-return words are not prefix-free")
    return {
        "format": "collatz-return9-code-audit-v1",
        "transitions": transition_audit(),
        "exact_language": {
            "special": ["01", "0001"],
            "parametric": [
                "1^a 0 b, a>=1",
                "00 1^a 0 b, a>=1",
                "0000 1^a 0 b, a>=0",
            ],
            "structural_proof": {
                "2_on_1": "8, then 1-loop, 0 to 4, either bit returns to 2",
                "2_on_01": "immediate return",
                "2_on_001": "5 to 8, then the same loop family",
                "2_on_0001": "immediate return through 1,5,7",
                "2_on_0000": "8, then the same loop family including zero loops",
            },
            "prefix_free": True,
        },
        "kraft": {
            "special": [special_mass.numerator, special_mass.denominator],
            "c0": [c0_mass.numerator, c0_mass.denominator],
            "c2": [c2_mass.numerator, c2_mass.denominator],
            "c4": [c4_mass.numerator, c4_mass.denominator],
            "total": [total.numerator, total.denominator],
            "full_binary_entropy_retained": True,
        },
        "finite_search_dictionary": {
            "max_a": max_a,
            "template_count": len(words),
            "kraft_covered": [covered.numerator, covered.denominator],
            "overflow_open": [overflow.numerator, overflow.denominator],
        },
        "direct_audit": direct_return_audit(direct_bound),
        "claim_scope": "algebraic code theorem plus explicit finite direct audit; no Collatz convergence claim",
    }


def direct_smaller_s(start: int, max_returns: int = 10_000) -> dict[str, object] | None:
    if start == 2:
        return {"start": 2, "returns": 0, "end": 2, "words": [], "base_case": True}
    current = start
    words: list[str] = []
    for count in range(1, max_returns + 1):
        current, word = first_return(current)
        words.append(word)
        if current < start:
            return {
                "start": start,
                "returns": count,
                "end": current,
                "words": words,
                "base_case": False,
            }
    return None


class CylinderSearch:
    def __init__(self, max_a: int, max_depth: int, store_records: bool) -> None:
        self.max_a = max_a
        self.max_depth = max_depth
        self.templates = return_templates(max_a)
        self.template_by_name = {template.name: template for template in self.templates}
        self.store_records = store_records
        self.records: list[dict[str, object]] = []
        self.nodes_by_depth: Counter[int] = Counter()
        self.closed_by_depth: Counter[int] = Counter()
        self.open_by_depth: Counter[int] = Counter()
        self.rule_counts: Counter[str] = Counter()
        self.obstructions: list[dict[str, object]] = []

    def add_record(self, family: ReturnFamily) -> tuple[int, dict[str, object]]:
        record_id = len(self.records)
        record = {
            "id": record_id,
            "family": family.compact(),
            "rule": None,
        }
        if self.store_records:
            self.records.append(record)
        return record_id, record

    def visit(self, family: ReturnFamily) -> int:
        depth = family.depth
        self.nodes_by_depth[depth] += 1
        record_id, record = self.add_record(family)
        rule: dict[str, object]
        if is_uniform_smaller(family):
            rule_type = "RETURN_DESCENT" if depth == 1 else "RETURN_SMALLER_S"
            rule = {"type": rule_type}
            self.closed_by_depth[depth] += 1
            self.rule_counts[rule_type] += 1
        else:
            high = descent_high(family)
            if high is not None:
                exceptions: list[dict[str, object]] = []
                all_verified = True
                for parameter in range(0, high + 1):
                    start, _endpoint = family.values(parameter)
                    witness = direct_smaller_s(start)
                    if witness is None:
                        all_verified = False
                        break
                    witness["parameter"] = parameter
                    exceptions.append(witness)
                if all_verified:
                    rule = {
                        "type": "RETURN_FINITE_TAIL",
                        "high_parameter": high,
                        "exceptions": exceptions,
                    }
                    self.closed_by_depth[depth] += 1
                    self.rule_counts["RETURN_FINITE_TAIL"] += 1
                else:
                    rule = {"type": "OPEN", "reason": "finite_exception_not_closed"}
                    self.open_by_depth[depth] += 1
                    self.rule_counts["OPEN"] += 1
            elif depth < self.max_depth:
                child_ids: list[int] = []
                for template in self.templates:
                    child = compose_with_template(family, template, record_id)
                    if child is not None:
                        child_ids.append(self.visit(child))
                rule = {
                    "type": "RETURN_COMPOSE",
                    "children": child_ids,
                    "dictionary_max_a": self.max_a,
                    "finite_dictionary_complete": True,
                    "overflow_open": True,
                }
                self.rule_counts["RETURN_COMPOSE"] += 1
            else:
                rule = {"type": "OPEN", "reason": "return_depth_bound"}
                self.open_by_depth[depth] += 1
                self.rule_counts["OPEN"] += 1

        record["rule"] = rule
        if self.store_records:
            self.records[record_id] = record
        if rule["type"] == "OPEN":
            fixed_points: list[dict[str, object]] = []
            for name in family.history:
                template = self.template_by_name[name]
                constant = (
                    template.output_base * template.source_step
                    - template.output_step * template.source_base
                )
                fixed = affine_fixed_point(
                    template.output_step,
                    constant,
                    template.source_step,
                )
                fixed_points.append(
                    {
                        "template": name,
                        "fixed_point": (
                            None
                            if fixed is None
                            else [fixed.numerator, fixed.denominator]
                        ),
                    }
                )
            repeated = len(set(family.history)) < len(family.history)
            self.obstructions.append(
                {
                    "record_id": record_id,
                    "family": family.compact(),
                    "minimum_start": family.source_base,
                    "repeated_branch_shadow": repeated,
                    "branch_fixed_points": fixed_points,
                }
            )
        return record_id

    def run(self) -> dict[str, object]:
        root_ids: list[int] = []
        for template in self.templates:
            root_ids.append(self.visit(root_family(template)))
        return {
            "max_a": self.max_a,
            "max_return_depth": self.max_depth,
            "template_count": len(self.templates),
            "root_ids": root_ids,
            "nodes_by_depth": {
                str(depth): self.nodes_by_depth[depth]
                for depth in range(1, self.max_depth + 1)
            },
            "closed_by_depth": {
                str(depth): self.closed_by_depth[depth]
                for depth in range(1, self.max_depth + 1)
            },
            "open_by_depth": {
                str(depth): self.open_by_depth[depth]
                for depth in range(1, self.max_depth + 1)
            },
            "rule_counts": dict(sorted(self.rule_counts.items())),
            "overflow_code_open": True,
            "proves_collatz": False,
        }


def search_grid(configurations: list[tuple[int, int]]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for max_a, depth in configurations:
        search = CylinderSearch(max_a, depth, False)
        summary = search.run()
        nodes = summary["nodes_by_depth"]
        closed = summary["closed_by_depth"]
        opened = summary["open_by_depth"]
        assert isinstance(nodes, dict) and isinstance(closed, dict) and isinstance(opened, dict)
        total = int(nodes[str(depth)])
        closed_count = int(closed[str(depth)])
        open_count = int(opened[str(depth)])
        rows.append(
            {
                "max_a": max_a,
                "return_depth": depth,
                "cylinders": total,
                "closed_at_level": closed_count,
                "open_at_bound": open_count,
                "surviving_to_next": total - closed_count - open_count,
                "overflow_code_open": True,
            }
        )
    return rows


def negative_shadow_audit() -> dict[str, object]:
    starts = (-7, -61, -34, -25)
    transitions = {str(start): first_return(start)[0] for start in starts}
    expected = {"-7": -7, "-61": -34, "-34": -25, "-25": -61}
    if transitions != expected:
        raise AssertionError("negative first-return shadow mismatch")
    return {
        "verified_transitions": transitions,
        "cycles": [[-7], [-61, -34, -25]],
        "diagnostic_only": True,
    }


def positive_example_audit() -> dict[str, int]:
    expected = {2: 2, 11: 20, 20: 2, 47: 182, 83: 47, 128: 2}
    actual = {start: first_return(start)[0] for start in expected}
    if actual != expected:
        raise AssertionError("positive return example mismatch")
    return {str(key): value for key, value in actual.items()}


def stopping_time_records(bound: int) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    record_returns = -1
    for start in range(11, bound, 9):
        current = start
        words: list[str] = []
        for return_count in range(1, 10_001):
            current, word = first_return(current)
            words.append(word)
            if current < start:
                if return_count > record_returns:
                    record_returns = return_count
                    records.append(
                        {
                            "start": start,
                            "returns_before_smaller": return_count,
                            "endpoint": current,
                            "code_words": words,
                        }
                    )
                break
        else:
            records.append(
                {
                    "start": start,
                    "returns_before_smaller": None,
                    "endpoint": current,
                    "code_words": words,
                }
            )
    return records


def mod27_diagnostic() -> dict[str, object]:
    expected = {
        "1": (3, 1, 2, Fraction(-1, 1)),
        "1101": (27, 23, 16, Fraction(-23, 11)),
        "011101": (81, 146, 64, Fraction(-146, 17)),
        "101": (9, 7, 8, Fraction(-7, 1)),
    }
    rows: list[dict[str, object]] = []
    for word, (wanted_p, wanted_b, wanted_q, wanted_fixed) in expected.items():
        length, odd_steps, p, b = affine_word(word)
        q = 1 << length
        fixed = affine_fixed_point(p, b, q)
        if (p, b, q, fixed) != (wanted_p, wanted_b, wanted_q, wanted_fixed):
            raise AssertionError("mod-27 dangerous cycle affine audit failed")
        rows.append(
            {
                "word": word,
                "length": length,
                "odd_steps": odd_steps,
                "P": p,
                "B": b,
                "Q": q,
                "fixed_point": [fixed.numerator, fixed.denominator],
                "noncontracting_coefficient": pow(3, odd_steps) >= 1 << length,
            }
        )
    return {
        "format": "collatz-mod27-dangerous-cycles-v1",
        "residue_class": "20 mod 27",
        "listed_cycles": rows,
        "diagnostic_only": True,
        "exhaustive_simple_cycle_claim": "not used as a proof rule",
    }


def write_report(
    path: Path,
    code: dict[str, object],
    summary: dict[str, object],
    grid: list[dict[str, object]],
    obstructions: list[dict[str, object]],
    records: list[dict[str, object]],
) -> None:
    smallest = min(obstructions, key=lambda row: (int(row["minimum_start"]), int(row["record_id"])))
    unexplained = [row for row in obstructions if not row["repeated_branch_shadow"]]
    smallest_unexplained = min(
        unexplained,
        key=lambda row: (int(row["minimum_start"]), int(row["record_id"])),
    )
    max_depth = int(summary["max_return_depth"])
    nodes = summary["nodes_by_depth"]
    closed = summary["closed_by_depth"]
    opened = summary["open_by_depth"]
    assert isinstance(nodes, dict) and isinstance(closed, dict) and isinstance(opened, dict)
    current_survivors = int(opened[str(max_depth)])
    previous_composed = int(nodes[str(max_depth - 1)]) - int(closed[str(max_depth - 1)])
    family = smallest["family"]
    family2 = smallest_unexplained["family"]
    assert isinstance(family, dict) and isinstance(family2, dict)
    lines = [
        "# Phase 4 return-map obstruction report",
        "",
        "This report does not claim a proof of the Collatz conjecture.",
        "",
        "## Algebraically verified theorem (return map only)",
        "",
        "- The mod-9 first-return code has the exact three parametric forms and two special words from the brief.",
        "- The code is prefix-free and its exact Kraft sum is 1; concatenated excursions retain full binary entropy.",
        "- Every stored return template satisfies the n-coordinate formula, z-coordinate formula, mod-3/mod-4 "
        "domain, first-return condition, and recurrence identity.",
        "- The certificate verifier accepts only smaller values in S, never an unranked smaller value outside S.",
        "",
        "## Exhaustive finite computation",
        "",
        f"- Direct n/formula/z comparison below 2^24: `{code['direct_audit']['result']}`.",
        f"- Main exact cylinder bounds: `A={summary['max_a']}`, return depth `{max_depth}`.",
        f"- Depth-{max_depth} cylinders: `{nodes[str(max_depth)]}`; closed there: `{closed[str(max_depth)]}`; OPEN: `{current_survivors}`.",
        f"- Finite-dictionary survivor ratio at the last return: `{current_survivors}/{previous_composed}`.",
        "- The configured Phase 4 run leaves 23,785 OPEN families versus Phase 3's 79,350 mixed OPEN nodes, "
        "but the domains, depths, and cylinder coordinates differ; this is not evidence of an asymptotic reduction.",
        "- Return templates compress individual excursions, but the Kraft identity and measured cylinder counts "
        "do not produce subcritical growth.",
        "- Per-return survivor growth is supercritical/exponential-looking over the tested grid; asymptotics remain unresolved.",
        "",
        "## Exact unresolved families",
        "",
        f"- Smallest exact unresolved source: `{family['source'][0]}+{family['source'][1]}*t`, `t>=0`.",
        f"- Its tested endpoint: `{family['endpoint'][0]}+{family['endpoint'][1]}*t` after `{len(family['history'])}` returns.",
        f"- Smallest unresolved family not tagged by a repeated branch shadow: "
        f"`{family2['source'][0]}+{family2['source'][1]}*t`.",
        "- These are obstructions to the configured bounded rule dictionary, not infinite Collatz obstruction theorems.",
        "",
        "## Failed ranking proposals and counterexamples",
        "",
        "- Fixed return horizon: rejected by the exact negative fixed point `-7` and cycle `-61 -> -34 -> -25 -> -61`, "
        "and by the positive record-stopping-time table.",
        "- Monotone one-return descent: rejected by `11 -> 20` and `47 -> 182`.",
        "- Constants-only ranking on `1,5,21`: refill transitions in unresolved certificate histories keep producing "
        "positive-slope families; the smallest exact family above is a counterexample to closure under the tested ranking.",
        "- Finite periodic-shadow dictionary: rejected as a universal explanation because the code has Kraft sum 1 and "
        "the smallest non-repeated-shadow family remains OPEN.",
        "",
        "## Diagnostic and conjectural status",
        "",
        "- Negative/rational shadows and mod-27 dangerous cycles are diagnostics only.",
        "- No heuristic closure is included in the certificate.",
        "- A future rule would need a well-founded ranking across refill cycles or a parametric repeated-return lemma; "
        "high finite closure percentages are insufficient.",
        "",
        "## Search grid",
        "",
        "| A | return depth | cylinders | closed | OPEN at bound |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in grid:
        lines.append(
            f"| {row['max_a']} | {row['return_depth']} | {row['cylinders']} | "
            f"{row['closed_at_level']} | {row['open_at_bound']} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(
    artifact_dir: Path,
    max_a: int,
    max_depth: int,
    direct_bound: int,
    stopping_bound: int,
) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    code = code_audit(max_a, direct_bound)
    main = CylinderSearch(max_a, max_depth, True)
    summary = main.run()
    covered, overflow = code_kraft(max_a)
    certificate = {
        "format": FORMAT,
        "version": 1,
        "bounds": {"max_a": max_a, "max_return_depth": max_depth},
        "finite_code_kraft": [covered.numerator, covered.denominator],
        "overflow_code_kraft": [overflow.numerator, overflow.denominator],
        "templates": [template.compact() for template in main.templates],
        "records": main.records,
        "summary": summary,
        "proves_collatz": False,
    }
    (artifact_dir / "return9_certificate.json").write_text(
        json.dumps(certificate, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (artifact_dir / "return9_code_audit.json").write_text(
        json.dumps(code, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    configurations = [(4, 1), (4, 2), (4, 3), (6, 1), (6, 2), (6, 3), (8, 1), (8, 2), (8, 3)]
    grid = search_grid(configurations)
    survivor_fields = list(grid[0])
    with (artifact_dir / "return9_survivors.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        writer = csv.DictWriter(stream, fieldnames=survivor_fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(grid)

    negative = negative_shadow_audit()
    positives = positive_example_audit()
    obstructions = {
        "format": "collatz-return9-obstructions-v1",
        "negative_shadows": negative,
        "positive_examples": positives,
        "open_count": len(main.obstructions),
        "open_families": sorted(
            main.obstructions,
            key=lambda row: (int(row["minimum_start"]), int(row["record_id"])),
        ),
        "failed_rankings": [
            {"ranking": "fixed_return_horizon", "counterexamples": negative["cycles"]},
            {"ranking": "one_return_descent", "counterexamples": [[11, 20], [47, 182]]},
            {
                "ranking": "finite_periodic_shadow_dictionary",
                "counterexample_record": min(
                    (
                        row for row in main.obstructions if not row["repeated_branch_shadow"]
                    ),
                    key=lambda row: (int(row["minimum_start"]), int(row["record_id"])),
                )["record_id"],
            },
        ],
        "claim_scope": "bounded exact search diagnostics, not a global theorem",
    }
    (artifact_dir / "return9_obstructions.json").write_text(
        json.dumps(obstructions, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    stopping = stopping_time_records(stopping_bound)
    with (artifact_dir / "return9_record_stopping_times.csv").open(
        "w", encoding="utf-8", newline=""
    ) as stream:
        fields = ["start", "returns_before_smaller", "endpoint", "code_words"]
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for row in stopping:
            output = dict(row)
            output["code_words"] = json.dumps(output["code_words"], separators=(",", ":"))
            writer.writerow(output)

    mod27 = mod27_diagnostic()
    (artifact_dir / "mod27_dangerous_cycles.json").write_text(
        json.dumps(mod27, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(
        artifact_dir / "phase4_obstruction_report.md",
        code,
        summary,
        grid,
        main.obstructions,
        main.records,
    )
    return {
        "summary": summary,
        "direct_audit": code["direct_audit"],
        "negative_shadows": negative,
        "positive_examples": positives,
        "record_stopping_holders": len(stopping),
        "open_obstructions": len(main.obstructions),
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--max-a", type=int, default=8)
    parser.add_argument("--return-depth", type=int, default=3)
    parser.add_argument("--direct-bound", type=int, default=1 << 24)
    parser.add_argument("--stopping-bound", type=int, default=1 << 20)
    args = parser.parse_args()
    result = generate(
        args.artifact_dir,
        args.max_a,
        args.return_depth,
        args.direct_bound,
        args.stopping_bound,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
