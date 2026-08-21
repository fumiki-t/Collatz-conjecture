#!/usr/bin/env python3
"""Generate exact Phase 5 mod-27 audits and bounded shadow diagnostics."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.phase5_model import (
    DANGEROUS_CYCLES,
    DANGEROUS_FORMS,
    MODULUS,
    SECTION,
    SECTION_SET,
    AffineMap,
    ReturnTemplate,
    affine_word,
    colored_graph,
    compose_affine,
    cylinder_family,
    enumerate_return_templates,
    enumerate_simple_cycles,
    first_return_to_section,
    shadow_values,
    topological_audit,
    v2,
)


FORMAT = "collatz-phase5-dangerous-cycles-v1"


def fraction_pair(value: Fraction) -> list[int]:
    return [value.numerator, value.denominator]


def direct_template_audit(bound: int, templates: list[ReturnTemplate]) -> dict[str, object]:
    template_map = {(row.source_residue, row.word): row for row in templates}
    counts: Counter[str] = Counter()
    digest = hashlib.sha256()
    buffer = bytearray()
    checked = 0
    shortcut_steps = 0
    for value in range(1, bound):
        source = value % MODULUS
        if source not in SECTION_SET:
            continue
        returned, word, path = first_return_to_section(value, limit=10)
        template = template_map.get((source, word))
        if template is None:
            raise AssertionError("direct return is missing from the template dictionary")
        if returned != template.affine.apply(value):
            raise AssertionError("direct return differs from the affine template")
        if returned % MODULUS != template.target_residue or path != template.path:
            raise AssertionError("direct return path differs from the graph template")
        if (value - template.source_base) % template.source_step:
            raise AssertionError("direct value is outside its claimed parity cylinder")
        counts[template.name] += 1
        checked += 1
        shortcut_steps += len(word)
        buffer.extend(f"{value}:{returned}:{word}\n".encode("ascii"))
        if len(buffer) >= 1 << 20:
            digest.update(buffer)
            buffer.clear()
    digest.update(buffer)
    if set(counts) != {template.name for template in templates}:
        raise AssertionError("at least one return template has no direct witness")
    return {
        "bound_exclusive": bound,
        "integers_checked": checked,
        "shortcut_steps_checked": shortcut_steps,
        "per_template_counts": dict(sorted(counts.items())),
        "sha256": digest.hexdigest(),
        "result": "all_direct_first_returns_match_exact_templates",
    }


def simple_cycle_audit() -> dict[str, object]:
    cycles = enumerate_simple_cycles()
    noncontracting = [row for row in cycles if row["noncontracting"]]
    dangerous_words = {str(row["dangerous_rotation"]) for row in noncontracting}
    if dangerous_words != set(DANGEROUS_CYCLES):
        raise AssertionError("noncontracting simple cycles differ from the required four")
    safe = [row for row in cycles if not row["noncontracting"]]
    maximum_safe = max(Fraction(int(row["A"]), int(row["denominator"])) for row in safe)
    if maximum_safe != Fraction(27, 32):
        raise AssertionError("safe simple-cycle multiplier bound changed")
    return {
        "format": "collatz-simple-cycles-mod27-v1",
        "unit_vertices": 18,
        "cycle_equivalence": "labeled directed simple cycles modulo cyclic rotation",
        "simple_cycle_count": len(cycles),
        "noncontracting_count": len(noncontracting),
        "noncontracting_words": sorted(dangerous_words, key=lambda word: (len(word), word)),
        "maximum_other_multiplier": fraction_pair(maximum_safe),
        "cycles": cycles,
        "proves_collatz": False,
    }


def simple_return20_paths() -> list[dict[str, object]]:
    graph = colored_graph()
    results: list[dict[str, object]] = []

    def visit(residue: int, word: str, path: tuple[int, ...]) -> None:
        for bit in (0, 1):
            target = graph[residue][bit]
            next_word = word + str(bit)
            next_path = path + (target,)
            if target == 20:
                affine = affine_word(next_word)
                source_base, source_step = cylinder_family(20, next_word)
                envelope_slope = 27 * affine.denominator - 32 * affine.A
                envelope_constant = 46 * affine.denominator - 32 * affine.B
                envelope_at_base = envelope_slope * source_base + envelope_constant
                results.append(
                    {
                        "word": next_word,
                        "path": list(next_path),
                        "source_family": [source_base, source_step],
                        **affine.compact(),
                        "noncontracting": affine.A >= affine.denominator,
                        "envelope_inequality": {
                            "integer_form": "(27*2^k-32*A)*x + (46*2^k-32*B) >= 0",
                            "slope": envelope_slope,
                            "constant": envelope_constant,
                            "value_at_minimum_admissible_x": envelope_at_base,
                            "valid_for_all_positive_admissible_x": (
                                envelope_slope >= 0 and envelope_at_base >= 0
                            ),
                        },
                    }
                )
            elif target != 26 and target not in path:
                visit(target, next_word, next_path)

    visit(20, "", (20,))
    return sorted(results, key=lambda row: (len(str(row["word"])), str(row["word"])))


def return20_domination_audit(cycles: list[dict[str, object]]) -> dict[str, object]:
    internal_cycles = [
        row for row in cycles if not ({20, 26} & set(map(int, row["nodes"])))
    ]
    for row in internal_cycles:
        multiplier = Fraction(int(row["A"]), int(row["denominator"]))
        fixed_raw = row["fixed_point"]
        if not isinstance(fixed_raw, list):
            raise AssertionError("an internal cycle lacks a finite fixed point")
        fixed = Fraction(int(fixed_raw[0]), int(fixed_raw[1]))
        if multiplier > Fraction(3, 4) or fixed > 1:
            raise AssertionError("internal-cycle deletion lemma fails")
    paths = simple_return20_paths()
    noncontracting = [row for row in paths if row["noncontracting"]]
    if [row["word"] for row in noncontracting] != ["101"]:
        raise AssertionError("return-20 has an unexpected noncontracting simple path")
    for row in paths:
        if row["word"] == "101":
            if (row["A"], row["B"], row["denominator"]) != (9, 7, 8):
                raise AssertionError("the exceptional E map changed")
        elif not row["envelope_inequality"]["valid_for_all_positive_admissible_x"]:
            raise AssertionError("a simple return-20 path exceeds the envelope")
    return {
        "format": "collatz-return20-domination-v1",
        "scope": "all positive 20-to-20 paths with no internal 20 or 26",
        "internal_cycle_lemma": {
            "cycle_count": len(internal_cycles),
            "maximum_multiplier": [3, 4],
            "maximum_fixed_point": [1, 1],
            "reason": "for x>=1 each internal cycle map is <=x; later shortcut affine maps are increasing",
            "cycles": [row["canonical_edge_key"] for row in internal_cycles],
        },
        "simple_path_count": len(paths),
        "unique_noncontracting_word": "101",
        "unique_noncontracting_map": {"A": 9, "B": 7, "denominator": 8},
        "other_path_envelope": {
            "upper_bound": "(27*x+46)/32",
            "strictly_below_x_for_positive_20_mod_27": True,
        },
        "simple_paths": paths,
        "verified": True,
    }


def shadow_transfer_audit(
    templates: list[ReturnTemplate], low_precision_limit: int
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    heteroclinic: list[dict[str, object]] = []
    increases: list[dict[str, object]] = []
    for template in templates:
        for source_name, (source_d, source_a) in DANGEROUS_FORMS.items():
            for target_name, (target_d, target_a) in DANGEROUS_FORMS.items():
                numerator = target_d * template.affine.A
                base = {
                    "template": template.name,
                    "source_form": source_name,
                    "target_form": target_name,
                    "k": template.affine.k,
                }
                if numerator % source_d:
                    rows.append({**base, "integer_identity_exists": False})
                    continue
                u = numerator // source_d
                constant = (
                    target_d * template.affine.B
                    + target_a * template.affine.denominator
                    - u * source_a
                )
                identity = {
                    **base,
                    "integer_identity_exists": True,
                    "u": u,
                    "C": constant,
                    "heteroclinic": constant == 0,
                    "stabilized_target_precision": (
                        None if constant == 0 else v2(constant) - template.affine.k
                    ),
                }
                rows.append(identity)
                if constant == 0:
                    heteroclinic.append(identity)

                witness: dict[str, object] | None = None
                # The parameter modulo 2^(k+L+2) is exhaustive for source
                # valuations <=L and for detecting a strict target increase.
                parameter_modulus = 1 << (template.affine.k + low_precision_limit + 2)
                for parameter in range(parameter_modulus):
                    start = template.source_base + template.source_step * parameter
                    end = template.affine.apply(start)
                    source_precision = v2(source_d * start + source_a)
                    target_precision = v2(target_d * end + target_a)
                    if source_precision <= low_precision_limit and target_precision > source_precision:
                        witness = {
                            "template": template.name,
                            "source_form": source_name,
                            "target_form": target_name,
                            "start": start,
                            "end": end,
                            "source_precision": source_precision,
                            "target_precision": target_precision,
                            "parameter_residue": parameter,
                            "parameter_modulus": parameter_modulus,
                        }
                        break
                if witness is not None:
                    increases.append(witness)
    smallest_refill = min(
        increases,
        key=lambda row: (int(row["start"]), str(row["template"]), str(row["source_form"]), str(row["target_form"])),
    )
    smallest_nontrivial_switch = min(
        (
            row for row in increases
            if int(row["start"]) > 1 and row["source_form"] != row["target_form"]
        ),
        key=lambda row: (int(row["start"]), str(row["template"]), str(row["source_form"]), str(row["target_form"])),
    )
    return {
        "format": "collatz-shadow-transfer-v1",
        "forms": {
            name: [coefficient, constant]
            for name, (coefficient, constant) in DANGEROUS_FORMS.items()
        },
        "identity": "d_t*F(x)+a_t = (u*(d_s*x+a_s)+C)/2^k",
        "template_count": len(templates),
        "identity_rows": rows,
        "heteroclinic_cases": heteroclinic,
        "low_precision_limit": low_precision_limit,
        "low_precision_increase_witnesses": increases,
        "smallest_exact_refill_witness": smallest_refill,
        "smallest_nontrivial_switch_witness": smallest_nontrivial_switch,
        "bounded_diagnostic_only": True,
    }


def dangerous_source_residue(fixed_point: Fraction) -> int:
    return (fixed_point.numerator * pow(fixed_point.denominator, -1, MODULUS)) % MODULUS


def split_into_returns(source: int, word: str, templates: list[ReturnTemplate]) -> list[str]:
    lookup = {(row.source_residue, row.word): row for row in templates}
    graph = colored_graph()
    current = source
    segment = ""
    names: list[str] = []
    for raw_bit in word:
        bit = int(raw_bit)
        segment += raw_bit
        current = graph[current][bit]
        if current in SECTION_SET:
            template = lookup.get((source, segment))
            if template is None or template.target_residue != current:
                raise AssertionError("dangerous word does not split into return templates")
            names.append(template.name)
            source = current
            segment = ""
    if segment:
        raise AssertionError("dangerous word ends outside the section")
    return names


@dataclass(frozen=True, slots=True)
class PathState:
    source_residue: int
    target_residue: int
    template_names: tuple[str, ...]
    word: str
    affine: AffineMap


def extend_path(state: PathState, template: ReturnTemplate) -> PathState:
    if state.target_residue != template.source_residue:
        raise ValueError("section endpoints do not compose")
    return PathState(
        state.source_residue,
        template.target_residue,
        state.template_names + (template.name,),
        state.word + template.word,
        compose_affine(state.affine, template.affine),
    )


def dangerous_repeat_count(source_residue: int, word: str, dangerous: str) -> int:
    best = 0
    width = len(dangerous)
    graph = colored_graph()
    residues = [source_residue]
    current = source_residue
    for raw_bit in word:
        current = graph[current][int(raw_bit)]
        residues.append(current)
    dangerous_source = dangerous_source_residue(DANGEROUS_CYCLES[dangerous])
    for offset in range(len(word)):
        if residues[offset] != dangerous_source:
            continue
        repeats = 0
        while word.startswith(dangerous, offset + repeats * width):
            repeats += 1
        best = max(best, repeats)
    return best


def analyze_path(state: PathState, template_map: dict[str, ReturnTemplate]) -> dict[str, object]:
    source_base, source_step = cylinder_family(state.source_residue, state.word)
    current = source_base
    start_values = shadow_values(current)
    maxima = dict(start_values)
    dominant = [max(sorted(start_values), key=lambda name: start_values[name])]
    prefix = AffineMap(1, 0, 0, 0)
    minimum_path_nondecreasing = True
    uniform_path_nondecreasing = True
    for name in state.template_names:
        template = template_map[name]
        prefix = compose_affine(prefix, template.affine)
        current = template.affine.apply(current)
        values = shadow_values(current)
        for form, precision in values.items():
            maxima[form] = max(maxima[form], precision)
        dominant.append(max(sorted(values), key=lambda form: values[form]))
        minimum_path_nondecreasing &= current >= source_base
        uniform_path_nondecreasing &= (
            current >= source_base and prefix.A >= prefix.denominator
        )
    switches = sum(left != right for left, right in zip(dominant, dominant[1:]))
    repeats = {
        word: dangerous_repeat_count(state.source_residue, state.word, word)
        for word in DANGEROUS_CYCLES
    }
    endpoint_step = MODULUS * state.affine.A
    return {
        "depth": len(state.template_names),
        "source_residue": state.source_residue,
        "target_residue": state.target_residue,
        "template_names": list(state.template_names),
        "parity_word": state.word,
        "total_map": state.affine.compact(),
        "starting_cylinder": [source_base, source_step],
        "endpoint_family": [current, endpoint_step],
        "contains_dangerous_cycle": any(count for count in repeats.values()),
        "dangerous_repeat_counts": repeats,
        "maximum_dangerous_repeat": max(repeats.values()),
        "shadow_start": start_values,
        "shadow_maximum": maxima,
        "shadow_final": shadow_values(current),
        "dominant_shadow_switches": switches,
        "minimum_representative_path_nondecreasing": minimum_path_nondecreasing,
        "whole_cylinder_path_nondecreasing": uniform_path_nondecreasing,
    }


def adversarial_shadow_families(
    templates: list[ReturnTemplate], max_repetitions: int
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for word, fixed in sorted(DANGEROUS_CYCLES.items(), key=lambda item: (len(item[0]), item[0])):
        source = dangerous_source_residue(fixed)
        return_names = split_into_returns(source, word, templates)
        form_name = next(
            name
            for name, (coefficient, constant) in DANGEROUS_FORMS.items()
            if Fraction(-constant, coefficient) == fixed
        )
        for repetitions in range(1, max_repetitions + 1):
            repeated_word = word * repetitions
            affine = affine_word(repeated_word)
            source_base, source_step = cylinder_family(source, repeated_word)
            endpoint = affine.apply(source_base)
            rows.append(
                {
                    "dangerous_word": word,
                    "shadow_form": form_name,
                    "repetitions": repetitions,
                    "return_depth": len(return_names) * repetitions,
                    "return_templates_per_cycle": return_names,
                    "source_residue": source,
                    "source_family": [source_base, source_step],
                    "endpoint_family": [endpoint, MODULUS * affine.A],
                    "total_map": affine.compact(),
                    "source_precision": shadow_values(source_base)[form_name],
                    "endpoint_precision": shadow_values(endpoint)[form_name],
                }
            )
    return rows


def shadow_switch_search(
    templates: list[ReturnTemplate], max_depth: int, beam_width: int
) -> dict[str, object]:
    by_source: dict[int, list[ReturnTemplate]] = defaultdict(list)
    template_map = {row.name: row for row in templates}
    for template in templates:
        by_source[template.source_residue].append(template)
    states = [
        PathState(
            template.source_residue,
            template.target_residue,
            (template.name,),
            template.word,
            template.affine,
        )
        for template in templates
    ]
    retained: list[dict[str, object]] = []
    depth_counts: list[dict[str, int]] = []
    h5a_counterexamples: list[dict[str, object]] = []
    h5b_candidates: list[dict[str, object]] = []
    for depth in range(1, max_depth + 1):
        analyzed = [analyze_path(state, template_map) for state in states]
        analyzed.sort(
            key=lambda row: (
                not bool(row["whole_cylinder_path_nondecreasing"]),
                -max(map(int, row["shadow_final"].values())),
                -int(row["dominant_shadow_switches"]),
                -int(row["maximum_dangerous_repeat"]),
                str(row["parity_word"]),
            )
        )
        retained.extend(analyzed)
        long_nondec = [
            row for row in analyzed
            if depth >= 20 and row["minimum_representative_path_nondecreasing"]
        ]
        # Quantified bounded surrogate only: four consecutive dangerous words
        # or a 27/32 charge for every observed dominant-shadow switch.
        for row in long_nondec:
            switches = int(row["dominant_shadow_switches"])
            multiplier = Fraction(*map(int, row["total_map"]["multiplier"]))
            charged = multiplier <= Fraction(27, 32) ** switches
            if int(row["maximum_dangerous_repeat"]) < 4 and not charged:
                h5a_counterexamples.append(row)
        for row in analyzed:
            start = row["shadow_start"]
            final = row["shadow_final"]
            for source_form, source_precision in start.items():
                for target_form, target_precision in final.items():
                    if (
                        source_form != target_form
                        and int(source_precision) >= 8
                        and int(target_precision) >= 8
                    ):
                        h5b_candidates.append(
                            {
                                "source_form": source_form,
                                "target_form": target_form,
                                "source_precision": source_precision,
                                "target_precision": target_precision,
                                "path": row,
                            }
                        )
        depth_counts.append(
            {
                "depth": depth,
                "retained": len(analyzed),
                "whole_cylinder_nondecreasing": sum(
                    bool(row["whole_cylinder_path_nondecreasing"]) for row in analyzed
                ),
                "minimum_representative_nondecreasing": sum(
                    bool(row["minimum_representative_path_nondecreasing"]) for row in analyzed
                ),
            }
        )
        if depth == max_depth:
            break
        candidates: list[PathState] = []
        for state in states:
            candidates.extend(
                extend_path(state, template)
                for template in by_source[state.target_residue]
            )
        scored: list[tuple[tuple[object, ...], PathState]] = []
        seen: set[tuple[object, ...]] = set()
        for state in candidates:
            row = analyze_path(state, template_map)
            signature = (
                state.target_residue,
                tuple(min(12, int(row["shadow_final"][name])) for name in sorted(DANGEROUS_FORMS)),
                bool(row["whole_cylinder_path_nondecreasing"]),
                min(8, int(row["dominant_shadow_switches"])),
                min(8, int(row["maximum_dangerous_repeat"])),
            )
            if signature in seen:
                continue
            seen.add(signature)
            multiplier = state.affine.multiplier
            score = (
                not bool(row["whole_cylinder_path_nondecreasing"]),
                -max(map(int, row["shadow_final"].values())),
                -int(row["dominant_shadow_switches"]),
                -int(row["maximum_dangerous_repeat"]),
                -multiplier,
                state.word,
            )
            scored.append((score, state))
        scored.sort(key=lambda item: item[0])
        states = [state for _, state in scored[:beam_width]]

    adversarial = adversarial_shadow_families(templates, max_depth)
    h5a_min = min(
        h5a_counterexamples,
        key=lambda row: (int(row["depth"]), int(row["starting_cylinder"][0]), str(row["parity_word"])),
        default=None,
    )
    h5b_min = min(
        h5b_candidates,
        key=lambda row: (
            int(row["path"]["depth"]),
            int(row["path"]["starting_cylinder"][0]),
            str(row["source_form"]),
            str(row["target_form"]),
        ),
        default=None,
    )
    return {
        "format": "collatz-shadow-switch-search-v1",
        "search_method": "deterministic counterexample-oriented beam with exact affine states",
        "max_return_depth": max_depth,
        "beam_width": beam_width,
        "not_exhaustive": True,
        "depth_counts": depth_counts,
        "retained_paths": retained,
        "adversarial_repetition_families": adversarial,
        "H5_A": {
            "original_status": "unresolved_unquantified_conjecture",
            "bounded_surrogate": "depth>=20 nondecreasing minimum representative; require dangerous repeat>=4 or total multiplier<=(27/32)^switches",
            "survives_bounded_search": not h5a_counterexamples,
            "minimal_exact_counterexample": h5a_min,
            "counterexample_count": len(h5a_counterexamples),
        },
        "H5_B": {
            "original_status": "unresolved_unquantified_conjecture",
            "bounded_test": "different start/final forms both have valuation>=8 in retained exact cylinders",
            "survives_bounded_search": not h5b_candidates,
            "minimal_exact_candidate": h5b_min,
            "candidate_count": len(h5b_candidates),
        },
        "proves_collatz": False,
    }


def ranking_synthesis(
    switch_result: dict[str, object], transfer: dict[str, object]
) -> dict[str, object]:
    adversarial = switch_result["adversarial_repetition_families"]
    assert isinstance(adversarial, list)
    max_repetitions = max(int(row["repetitions"]) for row in adversarial)
    smallest_refill = transfer["smallest_nontrivial_switch_witness"]
    return {
        "method": "bounded CEGAR over exact coefficient comparisons, section residues, and truncated shadow valuations",
        "candidate_languages": [
            "lexicographic tuples",
            "piecewise-affine truncated valuations",
            "dangerous-cycle macro counters",
            "safe-cycle charges at 27/32",
        ],
        "status": "no_universal_well_founded_rank_synthesized",
        "rejections": [
            {
                "candidate": "strict coefficient descent per return",
                "counterexample": "26+54*t under word 1 has multiplier 3/2",
            },
            {
                "candidate": "fixed-horizon dangerous-shadow truncation",
                "counterexample": f"all four dangerous words have exact repetition families through {max_repetitions} repetitions",
            },
            {
                "candidate": "one-step precision reset",
                "counterexample": smallest_refill,
            },
            {
                "candidate": "safe-cycle charge alone",
                "counterexample": "the four noncontracting simple cycles carry no 27/32 safe-cycle charge",
            },
        ],
        "smallest_exact_refill_or_switch_witness": smallest_refill,
        "universal_rank_certified": False,
    }


def write_report(
    path: Path,
    section_data: dict[str, object],
    cycles: dict[str, object],
    domination: dict[str, object],
    transfer: dict[str, object],
    switches: dict[str, object],
    ranking: dict[str, object],
) -> None:
    direct = section_data["direct_audit"]
    h5a = switches["H5_A"]
    h5b = switches["H5_B"]
    h5a_min = h5a["minimal_exact_counterexample"]
    h5b_min = h5b["minimal_exact_candidate"]
    refill = transfer["smallest_nontrivial_switch_witness"]
    if isinstance(h5a_min, dict):
        h5a_detail = (
            f"- Minimal H5-A surrogate counterexample: return depth `{h5a_min['depth']}`, source family "
            f"`{h5a_min['starting_cylinder'][0]}+{h5a_min['starting_cylinder'][1]}*t`, "
            f"maximum aligned dangerous repetition `{h5a_min['maximum_dangerous_repeat']}`."
        )
    else:
        h5a_detail = "- No H5-A surrogate counterexample was retained at this configured depth."
    if isinstance(h5b_min, dict) and isinstance(h5b_min.get("path"), dict):
        h5b_path = h5b_min["path"]
        h5b_detail = (
            f"- Minimal H5-B bounded candidate: return depth `{h5b_path['depth']}`, "
            f"start `{h5b_path['starting_cylinder'][0]}`, "
            f"`{h5b_min['source_form']}->{h5b_min['target_form']}` with valuations "
            f"`{h5b_min['source_precision']}->{h5b_min['target_precision']}`."
        )
    else:
        h5b_detail = "- No H5-B bounded candidate was retained at this configured depth."
    lines = [
        "# Phase 5 dangerous-cycle obstruction report",
        "",
        "This report does not claim a proof of the Collatz conjecture.",
        "",
        "## Proved by the independent verifier",
        "",
        "- Deleting residues `{1,11,20,26}` from the colored unit graph modulo 27 leaves a DAG.",
        "- Its exact first-return system has 52 templates and maximum return length 9.",
        "- The full unit graph has 108 labeled simple cycles up to rotation. Exactly `1`, `101`, `1101`, and `011101` are noncontracting.",
        "- Every other simple cycle has multiplier at most `27/32`.",
        "- The return-20 domination statement is verified: `101` is the unique noncontracting simple return, and every other path is bounded by `(27x+46)/32<x`.",
        "- All 52 affine maps, fixed points, cylinder domains, shadow-transfer identities, and stored exact paths are reconstructed from parity words.",
        "",
        "## Exhaustive finite computation",
        "",
        f"- Direct template comparison below `2^24`: {direct['integers_checked']} section integers and {direct['shortcut_steps_checked']} shortcut steps.",
        f"- Direct audit digest: `{direct['sha256']}`.",
        f"- Exact low-precision shadow refill transitions were exhaustively searched through source precision {transfer['low_precision_limit']} under the recorded parameter moduli.",
        "",
        "## Heuristic bounded search",
        "",
        f"- Shadow-switch search reached return depth {switches['max_return_depth']} with deterministic beam width {switches['beam_width']}; it is not exhaustive.",
        f"- H5-A bounded surrogate survives: `{h5a['survives_bounded_search']}`; the original unquantified conjecture remains unresolved.",
        h5a_detail,
        f"- H5-B bounded test survives: `{h5b['survives_bounded_search']}`; the original arbitrary-precision conjecture remains unresolved.",
        h5b_detail,
        "- No bounded beam result is promoted to a universal certificate.",
        "",
        "## Exact obstruction and failed ranking synthesis",
        "",
        f"- Smallest nontrivial low-precision switch witness: start `{refill['start']}`, end `{refill['end']}`, `{refill['source_form']}->{refill['target_form']}` with valuations `{refill['source_precision']}->{refill['target_precision']}`.",
        "- Arbitrary repetition families are generated exactly for all four dangerous words; the artifact records repetitions through depth 40.",
        f"- Ranking synthesis result: `{ranking['status']}`.",
        "- This failure rejects only the tested rank languages. It is not a theorem that no ranking exists.",
        "",
        "## Conjectures",
        "",
        "- H5-A and H5-B require quantitative definitions before they can be certificate claims.",
        "- A future proof rule would need a symbolic switch-cost lemma valid for arbitrary precision and repetition count.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(
    artifact_dir: Path,
    direct_bound: int,
    shadow_depth: int,
    beam_width: int,
    low_precision_limit: int,
) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    templates = enumerate_return_templates()
    section_data = {
        "format": FORMAT,
        "section": list(SECTION),
        "modulus": MODULUS,
        "graph_audit": topological_audit(),
        "template_count": len(templates),
        "templates": [row.compact() for row in templates],
        "direct_audit": direct_template_audit(direct_bound, templates),
        "proves_collatz": False,
    }
    cycles = simple_cycle_audit()
    domination = return20_domination_audit(cycles["cycles"])
    transfer = shadow_transfer_audit(templates, low_precision_limit)
    switches = shadow_switch_search(templates, shadow_depth, beam_width)
    ranking = ranking_synthesis(switches, transfer)
    switches["ranking_synthesis"] = ranking

    outputs = {
        "section4_templates.json": section_data,
        "simple_cycles_mod27.json": cycles,
        "return20_domination.json": domination,
        "shadow_transfer_matrix.json": transfer,
        "shadow_switch_counterexamples.json": switches,
    }
    for name, payload in outputs.items():
        (artifact_dir / name).write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    write_report(
        artifact_dir / "phase5_obstruction_report.md",
        section_data,
        cycles,
        domination,
        transfer,
        switches,
        ranking,
    )
    return {
        "template_count": len(templates),
        "maximum_first_return_length": section_data["graph_audit"]["maximum_first_return_length"],
        "simple_cycle_count": cycles["simple_cycle_count"],
        "noncontracting_words": cycles["noncontracting_words"],
        "maximum_other_multiplier": cycles["maximum_other_multiplier"],
        "return20_domination_verified": domination["verified"],
        "direct_audit": section_data["direct_audit"],
        "H5_A": switches["H5_A"],
        "H5_B": switches["H5_B"],
        "ranking_status": ranking["status"],
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--direct-bound", type=int, default=1 << 24)
    parser.add_argument("--shadow-depth", type=int, default=40)
    parser.add_argument("--beam-width", type=int, default=256)
    parser.add_argument("--low-precision-limit", type=int, default=4)
    args = parser.parse_args()
    result = generate(
        args.artifact_dir,
        args.direct_bound,
        args.shadow_depth,
        args.beam_width,
        args.low_precision_limit,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
