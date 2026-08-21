#!/usr/bin/env python3
"""Independent verifier for Phase 5 artifacts; imports no search/model code."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from math import gcd
from pathlib import Path


MODULUS = 27
UNITS = tuple(residue for residue in range(1, MODULUS) if gcd(residue, 3) == 1)
SECTION = (1, 11, 20, 26)
SECTION_SET = frozenset(SECTION)
FORMS = {"C1": (1, 1), "C7": (1, 7), "C23": (11, 23), "C146": (17, 146)}
DANGEROUS = {
    "1": Fraction(-1, 1),
    "101": Fraction(-7, 1),
    "1101": Fraction(-23, 11),
    "011101": Fraction(-146, 17),
}
MIXED_A = "11101"
MIXED_B = "1100"


def step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def edge(residue: int, bit: int) -> int:
    representative = residue if residue % 2 == bit else residue + MODULUS
    return step(representative) % MODULUS


def graph() -> dict[int, dict[int, int]]:
    return {residue: {bit: edge(residue, bit) for bit in (0, 1)} for residue in UNITS}


def word_map(word: str) -> tuple[int, int, int, int]:
    coefficient = 1
    constant = 0
    denominator = 1
    odd = 0
    for raw in word:
        if raw not in "01":
            raise ValueError("non-binary parity word")
        if raw == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
            odd += 1
        denominator *= 2
    return coefficient, constant, denominator, odd


def apply_map(affine: tuple[int, int, int, int], value: int) -> int:
    coefficient, constant, denominator, _ = affine
    numerator = coefficient * value + constant
    if numerator % denominator:
        raise ValueError("affine map is non-integral")
    return numerator // denominator


def compose(
    first: tuple[int, int, int, int], second: tuple[int, int, int, int]
) -> tuple[int, int, int, int]:
    a1, b1, d1, q1 = first
    a2, b2, d2, q2 = second
    return a2 * a1, a2 * b1 + b2 * d1, d1 * d2, q1 + q2


def parity_class(word: str) -> int:
    result = 0
    coefficient = 1
    constant = 0
    for index, raw in enumerate(word):
        bit = int(raw)
        modulus = 1 << (index + 1)
        result = ((bit << index) - constant) * pow(coefficient, -1, modulus) % modulus
        if bit:
            coefficient *= 3
            constant = 3 * constant + (1 << index)
    return result


def source_family(residue: int, word: str) -> tuple[int, int]:
    power = 1 << len(word)
    binary = parity_class(word)
    parameter = (residue - binary) * pow(power, -1, MODULUS) % MODULUS
    return binary + power * parameter, MODULUS * power


def map_compact(affine: tuple[int, int, int, int]) -> dict[str, object]:
    coefficient, constant, denominator, odd = affine
    difference = denominator - coefficient
    fixed = None if difference == 0 else Fraction(constant, difference)
    return {
        "k": denominator.bit_length() - 1,
        "q": odd,
        "A": coefficient,
        "B": constant,
        "denominator": denominator,
        "multiplier": [coefficient, denominator],
        "fixed_point": None if fixed is None else [fixed.numerator, fixed.denominator],
    }


def expected_templates() -> list[dict[str, object]]:
    edges = graph()
    raw: list[tuple[int, int, str, tuple[int, ...]]] = []
    frontier = [(source, source, "", (source,)) for source in SECTION]
    while frontier:
        source, residue, word, path = frontier.pop(0)
        for bit in (0, 1):
            target = edges[residue][bit]
            next_word = word + str(bit)
            next_path = path + (target,)
            if target in SECTION_SET:
                raw.append((source, target, next_word, next_path))
            else:
                if target in path:
                    raise ValueError("section-deleted graph contains a cycle")
                frontier.append((source, target, next_word, next_path))
    rows: list[dict[str, object]] = []
    for source, target, word, path in raw:
        affine = word_map(word)
        start, stride = source_family(source, word)
        end = apply_map(affine, start)
        row = {
            "name": f"r{source}-to-r{target}-{word}",
            "source_residue": source,
            "target_residue": target,
            "word": word,
            "path": list(path),
            "source_family": [start, stride],
            "target_family": [end, MODULUS * affine[0]],
        }
        row.update(map_compact(affine))
        rows.append(row)
    return sorted(rows, key=lambda row: (row["source_residue"], row["word"], row["target_residue"]))


def verify_dag(stored: object) -> None:
    if not isinstance(stored, dict):
        raise ValueError("graph audit is missing")
    edges = graph()
    internal = set(UNITS) - SECTION_SET
    indegree = {residue: 0 for residue in internal}
    for source in internal:
        for target in edges[source].values():
            if target in internal:
                indegree[target] += 1
    available = sorted(residue for residue, degree in indegree.items() if degree == 0)
    order: list[int] = []
    longest = {residue: 0 for residue in internal}
    while available:
        source = available.pop(0)
        order.append(source)
        for target in edges[source].values():
            if target in internal:
                longest[target] = max(longest[target], longest[source] + 1)
                indegree[target] -= 1
                if indegree[target] == 0:
                    available.append(target)
                    available.sort()
    expected = {
        "deleted_vertices": list(SECTION),
        "remaining_vertices": sorted(internal),
        "topological_order": order,
        "acyclic": len(order) == len(internal),
        "maximum_internal_edges": max(longest.values()),
        "maximum_first_return_length": 9,
    }
    if stored != expected or not expected["acyclic"]:
        raise ValueError("section-deleted DAG audit mismatch")


def direct_first_return(value: int) -> tuple[int, str, tuple[int, ...]]:
    current = value
    word: list[str] = []
    path = [value % MODULUS]
    for _ in range(10):
        word.append(str(current % 2))
        current = step(current)
        path.append(current % MODULUS)
        if current % MODULUS in SECTION_SET:
            return current, "".join(word), tuple(path)
    raise ValueError("first return exceeds length 9")


def direct_audit(bound: int, templates: list[dict[str, object]]) -> dict[str, object]:
    lookup = {(int(row["source_residue"]), str(row["word"])): row for row in templates}
    counts: Counter[str] = Counter()
    digest = hashlib.sha256()
    buffer = bytearray()
    checked = 0
    steps = 0
    for value in range(1, bound):
        source = value % MODULUS
        if source not in SECTION_SET:
            continue
        returned, word, path = direct_first_return(value)
        row = lookup.get((source, word))
        if row is None:
            raise ValueError("direct path is absent from template list")
        affine = word_map(word)
        if apply_map(affine, value) != returned or list(path) != row["path"]:
            raise ValueError("direct template mismatch")
        base, stride = map(int, row["source_family"])
        if (value - base) % stride:
            raise ValueError("direct value outside stored cylinder")
        counts[str(row["name"])] += 1
        checked += 1
        steps += len(word)
        buffer.extend(f"{value}:{returned}:{word}\n".encode("ascii"))
        if len(buffer) >= 1 << 20:
            digest.update(buffer)
            buffer.clear()
    digest.update(buffer)
    return {
        "bound_exclusive": bound,
        "integers_checked": checked,
        "shortcut_steps_checked": steps,
        "per_template_counts": dict(sorted(counts.items())),
        "sha256": digest.hexdigest(),
        "result": "all_direct_first_returns_match_exact_templates",
    }


def cycle_key(nodes: tuple[int, ...], bits: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    rotations = []
    for offset in range(len(bits)):
        rotated_nodes = nodes[offset:] + nodes[:offset]
        rotated_bits = bits[offset:] + bits[:offset]
        rotations.append(tuple(zip(rotated_nodes, rotated_bits, strict=True)))
    return min(rotations)


def independent_cycle_keys() -> set[tuple[tuple[int, int], ...]]:
    edges = graph()
    result: set[tuple[tuple[int, int], ...]] = set()
    for start in UNITS:
        stack = [(start, (start,), ())]
        while stack:
            residue, nodes, bits = stack.pop()
            for bit in (0, 1):
                target = edges[residue][bit]
                if target == start:
                    result.add(cycle_key(nodes, bits + (bit,)))
                elif target not in nodes:
                    stack.append((target, nodes + (target,), bits + (bit,)))
    return result


def verify_cycles(payload: object) -> tuple[list[dict[str, object]], set[tuple[tuple[int, int], ...]]]:
    if not isinstance(payload, dict) or payload.get("format") != "collatz-simple-cycles-mod27-v1":
        raise ValueError("simple-cycle artifact format mismatch")
    rows = payload.get("cycles")
    if not isinstance(rows, list):
        raise ValueError("simple-cycle rows missing")
    expected_keys = independent_cycle_keys()
    stored_keys: set[tuple[tuple[int, int], ...]] = set()
    noncontracting: dict[str, Fraction] = {}
    safe_multipliers: list[Fraction] = []
    edges = graph()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("malformed cycle row")
        nodes = tuple(map(int, row["nodes"]))
        word = str(row["word"])
        bits = tuple(map(int, word))
        if len(nodes) != len(bits) or len(set(nodes)) != len(nodes):
            raise ValueError("stored cycle is not simple")
        for index, (node, bit) in enumerate(zip(nodes, bits, strict=True)):
            if edges[node][bit] != nodes[(index + 1) % len(nodes)]:
                raise ValueError("cycle edge mismatch")
        key = cycle_key(nodes, bits)
        if row["canonical_edge_key"] != [list(pair) for pair in key]:
            raise ValueError("cycle canonical key mismatch")
        if key in stored_keys:
            raise ValueError("duplicate cycle modulo rotation")
        stored_keys.add(key)
        affine = word_map(word)
        for field, expected in map_compact(affine).items():
            if row.get(field) != expected:
                raise ValueError(f"cycle affine field mismatch: {field}")
        multiplier = Fraction(affine[0], affine[2])
        if bool(row["noncontracting"]) != (multiplier >= 1):
            raise ValueError("cycle contraction flag mismatch")
        if multiplier >= 1:
            dangerous = row.get("dangerous_rotation")
            if dangerous not in DANGEROUS:
                raise ValueError("unexpected noncontracting simple cycle")
            noncontracting[str(dangerous)] = DANGEROUS[str(dangerous)]
        else:
            safe_multipliers.append(multiplier)
    if stored_keys != expected_keys or len(rows) != 108:
        raise ValueError("complete simple-cycle set mismatch")
    if set(noncontracting) != set(DANGEROUS) or max(safe_multipliers) != Fraction(27, 32):
        raise ValueError("dangerous-cycle classification mismatch")
    if payload.get("noncontracting_count") != 4 or payload.get("maximum_other_multiplier") != [27, 32]:
        raise ValueError("simple-cycle summary mismatch")
    return rows, expected_keys


def independent_return20_paths() -> dict[str, tuple[int, ...]]:
    edges = graph()
    paths: dict[str, tuple[int, ...]] = {}
    stack = [(20, "", (20,))]
    while stack:
        residue, word, path = stack.pop()
        for bit in (0, 1):
            target = edges[residue][bit]
            next_word = word + str(bit)
            next_path = path + (target,)
            if target == 20:
                paths[next_word] = next_path
            elif target != 26 and target not in path:
                stack.append((target, next_word, next_path))
    return paths


def verify_domination(payload: object, cycle_rows: list[dict[str, object]]) -> None:
    if not isinstance(payload, dict) or payload.get("format") != "collatz-return20-domination-v1":
        raise ValueError("return-20 artifact format mismatch")
    internal = [row for row in cycle_rows if not ({20, 26} & set(map(int, row["nodes"])))]
    if len(internal) != 10:
        raise ValueError("internal-cycle count mismatch")
    for row in internal:
        multiplier = Fraction(int(row["A"]), int(row["denominator"]))
        fixed = Fraction(*map(int, row["fixed_point"]))
        if multiplier > Fraction(3, 4) or fixed > 1:
            raise ValueError("internal cycle cannot be deleted monotonically")
    expected_paths = independent_return20_paths()
    stored = payload.get("simple_paths")
    if not isinstance(stored, list) or {str(row["word"]) for row in stored} != set(expected_paths):
        raise ValueError("return-20 simple-path set mismatch")
    noncontracting: list[str] = []
    for row in stored:
        word = str(row["word"])
        affine = word_map(word)
        if row["path"] != list(expected_paths[word]):
            raise ValueError("return-20 path mismatch")
        for field, expected in map_compact(affine).items():
            if row.get(field) != expected:
                raise ValueError("return-20 affine mismatch")
        start, stride = source_family(20, word)
        if row["source_family"] != [start, stride]:
            raise ValueError("return-20 cylinder mismatch")
        if affine[0] >= affine[2]:
            noncontracting.append(word)
        else:
            slope = 27 * affine[2] - 32 * affine[0]
            constant = 46 * affine[2] - 32 * affine[1]
            if slope < 0 or slope * start + constant < 0:
                raise ValueError("return-20 envelope fails")
    if noncontracting != ["101"] or payload.get("verified") is not True:
        raise ValueError("return-20 theorem summary mismatch")


def valuation(value: int) -> int:
    if value == 0:
        raise ValueError("unexpected zero shadow form")
    value = abs(value)
    return (value & -value).bit_length() - 1


def shadows(value: int) -> dict[str, int]:
    return {name: valuation(d * value + a) for name, (d, a) in FORMS.items()}


def dangerous_repeat_count(source_residue: int, word: str, dangerous: str) -> int:
    edges = graph()
    fixed = DANGEROUS[dangerous]
    dangerous_source = fixed.numerator * pow(fixed.denominator, -1, MODULUS) % MODULUS
    residues = [source_residue]
    current = source_residue
    for raw_bit in word:
        current = edges[current][int(raw_bit)]
        residues.append(current)
    best = 0
    width = len(dangerous)
    for offset in range(len(word)):
        if residues[offset] != dangerous_source:
            continue
        repetitions = 0
        while word.startswith(dangerous, offset + repetitions * width):
            repetitions += 1
        best = max(best, repetitions)
    return best


def verify_transfer(payload: object, templates: list[dict[str, object]]) -> tuple[int, int]:
    if not isinstance(payload, dict) or payload.get("format") != "collatz-shadow-transfer-v1":
        raise ValueError("shadow-transfer artifact format mismatch")
    limit = int(payload["low_precision_limit"])
    stored_rows = payload.get("identity_rows")
    witnesses = payload.get("low_precision_increase_witnesses")
    if not isinstance(stored_rows, list) or not isinstance(witnesses, list):
        raise ValueError("shadow-transfer rows missing")
    expected_rows: list[dict[str, object]] = []
    expected_witnesses: list[dict[str, object]] = []
    for template in templates:
        affine = word_map(str(template["word"]))
        for source_name, (source_d, source_a) in FORMS.items():
            for target_name, (target_d, target_a) in FORMS.items():
                base = {
                    "template": template["name"],
                    "source_form": source_name,
                    "target_form": target_name,
                    "k": affine[2].bit_length() - 1,
                }
                numerator = target_d * affine[0]
                if numerator % source_d:
                    expected_rows.append({**base, "integer_identity_exists": False})
                    continue
                u = numerator // source_d
                constant = target_d * affine[1] + target_a * affine[2] - u * source_a
                expected_rows.append(
                    {
                        **base,
                        "integer_identity_exists": True,
                        "u": u,
                        "C": constant,
                        "heteroclinic": constant == 0,
                        "stabilized_target_precision": (
                            None if constant == 0 else valuation(constant) - base["k"]
                        ),
                    }
                )
                start_base, start_step = map(int, template["source_family"])
                modulus = 1 << (base["k"] + limit + 2)
                for parameter in range(modulus):
                    start = start_base + start_step * parameter
                    end = apply_map(affine, start)
                    source_precision = valuation(source_d * start + source_a)
                    target_precision = valuation(target_d * end + target_a)
                    if source_precision <= limit and target_precision > source_precision:
                        expected_witnesses.append(
                            {
                                "template": template["name"],
                                "source_form": source_name,
                                "target_form": target_name,
                                "start": start,
                                "end": end,
                                "source_precision": source_precision,
                                "target_precision": target_precision,
                                "parameter_residue": parameter,
                                "parameter_modulus": modulus,
                            }
                        )
                        break
    if stored_rows != expected_rows or witnesses != expected_witnesses:
        raise ValueError("shadow-transfer matrix or refill witnesses mismatch")
    smallest = min(
        expected_witnesses,
        key=lambda row: (int(row["start"]), str(row["template"]), str(row["source_form"]), str(row["target_form"])),
    )
    if payload.get("smallest_exact_refill_witness") != smallest:
        raise ValueError("smallest refill witness mismatch")
    smallest_nontrivial = min(
        (
            row for row in expected_witnesses
            if int(row["start"]) > 1 and row["source_form"] != row["target_form"]
        ),
        key=lambda row: (int(row["start"]), str(row["template"]), str(row["source_form"]), str(row["target_form"])),
    )
    if payload.get("smallest_nontrivial_switch_witness") != smallest_nontrivial:
        raise ValueError("smallest nontrivial switch witness mismatch")
    heteroclinic_count = sum(bool(row.get("heteroclinic")) for row in expected_rows)
    return len(expected_rows), heteroclinic_count


def analyze_stored_path(row: dict[str, object], template_map: dict[str, dict[str, object]]) -> None:
    names = row.get("template_names")
    if not isinstance(names, list) or not names:
        raise ValueError("stored switch path lacks templates")
    source = int(row["source_residue"])
    current_residue = source
    word = ""
    affine = (1, 0, 1, 0)
    for name in names:
        template = template_map.get(str(name))
        if template is None or int(template["source_residue"]) != current_residue:
            raise ValueError("stored switch path does not compose")
        current_residue = int(template["target_residue"])
        word += str(template["word"])
        affine = compose(affine, word_map(str(template["word"])))
    if word != row.get("parity_word") or current_residue != int(row["target_residue"]):
        raise ValueError("stored switch path word/endpoint mismatch")
    if row.get("total_map") != map_compact(affine):
        raise ValueError("stored switch path affine map mismatch")
    start, stride = source_family(source, word)
    end = apply_map(affine, start)
    if row.get("starting_cylinder") != [start, stride]:
        raise ValueError("stored switch starting cylinder mismatch")
    if row.get("endpoint_family") != [end, MODULUS * affine[0]]:
        raise ValueError("stored switch endpoint family mismatch")
    if row.get("shadow_start") != shadows(start) or row.get("shadow_final") != shadows(end):
        raise ValueError("stored switch shadow endpoint mismatch")
    current = start
    start_shadows = shadows(start)
    maxima = dict(start_shadows)
    dominant = [max(sorted(start_shadows), key=lambda name: start_shadows[name])]
    prefix = (1, 0, 1, 0)
    minimum_nondecreasing = True
    uniform_nondecreasing = True
    for name in names:
        template = template_map[str(name)]
        template_map_value = word_map(str(template["word"]))
        prefix = compose(prefix, template_map_value)
        current = apply_map(template_map_value, current)
        values = shadows(current)
        for form, precision in values.items():
            maxima[form] = max(maxima[form], precision)
        dominant.append(max(sorted(values), key=lambda form: values[form]))
        minimum_nondecreasing &= current >= start
        uniform_nondecreasing &= current >= start and prefix[0] >= prefix[2]
    switches = sum(left != right for left, right in zip(dominant, dominant[1:]))
    repeats = {
        dangerous: dangerous_repeat_count(source, word, dangerous)
        for dangerous in DANGEROUS
    }
    expected_fields = {
        "depth": len(names),
        "contains_dangerous_cycle": any(repeats.values()),
        "dangerous_repeat_counts": repeats,
        "maximum_dangerous_repeat": max(repeats.values()),
        "shadow_maximum": maxima,
        "dominant_shadow_switches": switches,
        "minimum_representative_path_nondecreasing": minimum_nondecreasing,
        "whole_cylinder_path_nondecreasing": uniform_nondecreasing,
    }
    for field, expected in expected_fields.items():
        if row.get(field) != expected:
            raise ValueError(f"stored switch path analysis mismatch: {field}")


def verify_mixed_block(
    payload: object, template_map: dict[str, dict[str, object]]
) -> tuple[int, int]:
    if not isinstance(payload, dict) or payload.get("format") != "collatz-mixed-block-adversarial-v1":
        raise ValueError("mixed-block adversarial audit is missing")
    map_a = word_map(MIXED_A)
    map_b = word_map(MIXED_B)
    map_w = word_map(MIXED_A + MIXED_B)
    expected_blocks = {
        "A": {"word": MIXED_A, **map_compact(map_a)},
        "B": {"word": MIXED_B, **map_compact(map_b)},
    }
    expected_w = {"word": MIXED_A + MIXED_B, **map_compact(map_w)}
    if payload.get("blocks") != expected_blocks or payload.get("W") != expected_w:
        raise ValueError("A, B, or W affine map mismatch")
    if map_w[:3] != (729, 817, 512) or Fraction(817, 512 - 729) != Fraction(-817, 217):
        raise ValueError("W fixed-point identity mismatch")
    if payload.get("general_multiplier") != "3^(4*r+2*s)/2^(5*r+4*s)":
        raise ValueError("mixed-block general multiplier mismatch")
    expected_parameterization = {
        "u": "2*r+s",
        "q": "5*r+4*s=floor(log2(9^u))",
        "r": "(4*u-q)/3",
        "s": "(2*q-5*u)/3",
    }
    if payload.get("record_parameterization") != expected_parameterization:
        raise ValueError("mixed-block record parameterization mismatch")
    expected_argument = {
        "positive_logs": ["log(81/32)>0", "log(16/9)>0"],
        "irrational_ratio": "log(81/32)/log(16/9)",
        "rationality_contradiction": "3^(4*n+2*m)=2^(5*n+4*m) for positive m,n",
        "number_theory_input": "density of positive linear combinations r*alpha-s*beta when alpha/beta is irrational",
        "conclusion": "there are positive r,s with multiplier>1 arbitrarily close to 1",
        "checker_scope": "exact premises and finite record sequence checked; density theorem named explicitly",
    }
    if payload.get("arbitrary_closeness_argument") != expected_argument:
        raise ValueError("mixed-block arbitrary-closeness scope mismatch")
    expected_implication = {
        "H5_A": "near-neutral nondecreasing families with no long aligned repetition of one canonical dangerous cycle",
        "H5_B": "four-center coordinates are incomplete for near-neutral rational shadows; this does not alone settle the original unquantified switch-cost statement",
        "four_center_ranking": "W has fixed point -817/217 outside the four canonical centers",
    }
    if payload.get("ranking_implication") != expected_implication:
        raise ValueError("mixed-block ranking implication mismatch")
    bound = int(payload["record_u_bound"])
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("mixed-block records missing")
    expected_pairs: list[tuple[int, int, int, int, int]] = []
    power = 1
    best_gap: int | None = None
    best_denominator: int | None = None
    for u in range(1, bound + 1):
        power *= 9
        exponent_two = power.bit_length() - 1
        if exponent_two % 3 != u % 3 or not (5 * u <= 2 * exponent_two <= 8 * u):
            continue
        repetitions_a = (4 * u - exponent_two) // 3
        repetitions_b = (2 * exponent_two - 5 * u) // 3
        if repetitions_a < 1 or repetitions_b < 1:
            continue
        denominator = 1 << exponent_two
        gap = power - denominator
        if gap <= 0:
            continue
        if (
            best_gap is not None
            and best_denominator is not None
            and gap * best_denominator >= best_gap * denominator
        ):
            continue
        best_gap, best_denominator = gap, denominator
        expected_pairs.append((u, repetitions_a, repetitions_b, gap, denominator))
    if len(records) != len(expected_pairs) or payload.get("record_count") != len(expected_pairs):
        raise ValueError("mixed-block record count mismatch")
    previous: tuple[int, int] | None = None
    for row, (u, repetitions_a, repetitions_b, gap, denominator) in zip(
        records, expected_pairs, strict=True
    ):
        if not isinstance(row, dict):
            raise ValueError("malformed mixed-block record")
        word = MIXED_A * repetitions_a + MIXED_B * repetitions_b
        affine = word_map(word)
        fixed = Fraction(affine[1], affine[2] - affine[0])
        precision = 0
        while gap * (1 << (precision + 1)) < denominator:
            precision += 1
        expected_scalars = {
            "u": u,
            "r": repetitions_a,
            "s": repetitions_b,
            "word_length": len(word),
            "odd_steps": affine[3],
            "multiplier": [affine[0], affine[2]],
            "excess_over_one": [gap, denominator],
            "certified_excess_below_power_of_two": precision,
            "fixed_point": [fixed.numerator, fixed.denominator],
            "fixed_point_is_one_of_four_centers": fixed in set(DANGEROUS.values()),
        }
        for field, expected in expected_scalars.items():
            if row.get(field) != expected:
                raise ValueError(f"mixed-block record mismatch: {field}")
        if affine[0] <= affine[2] or row["path"]["parity_word"] != word:
            raise ValueError("mixed-block multiplier is not above one")
        analyze_stored_path(row["path"], template_map)
        if row["path"]["whole_cylinder_path_nondecreasing"] is not True:
            raise ValueError("mixed-block cylinder is not uniformly nondecreasing")
        if previous is not None and gap * previous[1] >= previous[0] * denominator:
            raise ValueError("mixed-block excess records do not improve strictly")
        previous = gap, denominator
    if records[0]["r"] != 1 or records[0]["s"] != 1:
        raise ValueError("W=AB is not the first mixed-block record")
    if payload.get("proves_collatz") is not False:
        raise ValueError("mixed-block audit claims a Collatz proof")
    return len(records), int(records[-1]["certified_excess_below_power_of_two"])


def verify_switches(payload: object, templates: list[dict[str, object]]) -> tuple[int, int, int, int]:
    if not isinstance(payload, dict) or payload.get("format") != "collatz-shadow-switch-search-v1":
        raise ValueError("shadow-switch artifact format mismatch")
    if payload.get("not_exhaustive") is not True or payload.get("proves_collatz") is not False:
        raise ValueError("bounded shadow search overclaims its scope")
    template_map = {str(row["name"]): row for row in templates}
    paths = payload.get("retained_paths")
    adversarial = payload.get("adversarial_repetition_families")
    if not isinstance(paths, list) or not isinstance(adversarial, list):
        raise ValueError("shadow-switch paths missing")
    for row in paths:
        if not isinstance(row, dict):
            raise ValueError("malformed switch path")
        analyze_stored_path(row, template_map)
    expected_depth_counts = []
    for depth in range(1, int(payload["max_return_depth"]) + 1):
        at_depth = [row for row in paths if int(row["depth"]) == depth]
        expected_depth_counts.append(
            {
                "depth": depth,
                "retained": len(at_depth),
                "whole_cylinder_nondecreasing": sum(
                    bool(row["whole_cylinder_path_nondecreasing"]) for row in at_depth
                ),
                "minimum_representative_nondecreasing": sum(
                    bool(row["minimum_representative_path_nondecreasing"]) for row in at_depth
                ),
            }
        )
    if payload.get("depth_counts") != expected_depth_counts:
        raise ValueError("shadow-switch depth summary mismatch")

    h5a_counterexamples = []
    h5b_candidates = []
    for row in paths:
        if int(row["depth"]) >= 20 and row["minimum_representative_path_nondecreasing"]:
            multiplier = Fraction(*map(int, row["total_map"]["multiplier"]))
            switches = int(row["dominant_shadow_switches"])
            charged = multiplier <= Fraction(27, 32) ** switches
            if int(row["maximum_dangerous_repeat"]) < 4 and not charged:
                h5a_counterexamples.append(row)
        for source_form, source_precision in row["shadow_start"].items():
            for target_form, target_precision in row["shadow_final"].items():
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
    expected_h5a = {
        "original_status": "unresolved_unquantified_conjecture",
        "bounded_surrogate": "depth>=20 nondecreasing minimum representative; require dangerous repeat>=4 or total multiplier<=(27/32)^switches",
        "survives_bounded_search": not h5a_counterexamples,
        "minimal_exact_counterexample": h5a_min,
        "counterexample_count": len(h5a_counterexamples),
    }
    expected_h5b = {
        "original_status": "unresolved_unquantified_conjecture",
        "bounded_test": "different start/final forms both have valuation>=8 in retained exact cylinders",
        "survives_bounded_search": not h5b_candidates,
        "minimal_exact_candidate": h5b_min,
        "candidate_count": len(h5b_candidates),
    }
    if payload.get("H5_A") != expected_h5a or payload.get("H5_B") != expected_h5b:
        raise ValueError("bounded H5-A/H5-B result mismatch")
    maximum_repetition = 0
    for row in adversarial:
        word = str(row["dangerous_word"])
        repetitions = int(row["repetitions"])
        maximum_repetition = max(maximum_repetition, repetitions)
        repeated = word * repetitions
        affine = word_map(repeated)
        fixed = DANGEROUS.get(word)
        if fixed is None:
            raise ValueError("unknown dangerous repetition word")
        residue = fixed.numerator * pow(fixed.denominator, -1, MODULUS) % MODULUS
        start, stride = source_family(residue, repeated)
        end = apply_map(affine, start)
        if row.get("source_family") != [start, stride] or row.get("endpoint_family") != [end, MODULUS * affine[0]]:
            raise ValueError("dangerous repetition family mismatch")
        if row.get("total_map") != map_compact(affine):
            raise ValueError("dangerous repetition affine mismatch")
    if maximum_repetition != int(payload["max_return_depth"]):
        raise ValueError("dangerous repetition bound mismatch")
    ranking = payload.get("ranking_synthesis")
    if not isinstance(ranking, dict) or ranking.get("universal_rank_certified") is not False:
        raise ValueError("ranking artifact claims unsupported universality")
    mixed_count, mixed_precision = verify_mixed_block(
        payload.get("mixed_block_adversarial"), template_map
    )
    return len(paths), len(adversarial), mixed_count, mixed_precision


def verify(artifact_dir: Path) -> dict[str, object]:
    section_data = json.loads((artifact_dir / "section4_templates.json").read_text(encoding="utf-8"))
    cycle_data = json.loads((artifact_dir / "simple_cycles_mod27.json").read_text(encoding="utf-8"))
    domination = json.loads((artifact_dir / "return20_domination.json").read_text(encoding="utf-8"))
    transfer = json.loads((artifact_dir / "shadow_transfer_matrix.json").read_text(encoding="utf-8"))
    switches = json.loads((artifact_dir / "shadow_switch_counterexamples.json").read_text(encoding="utf-8"))
    if section_data.get("format") != "collatz-phase5-dangerous-cycles-v1":
        raise ValueError("section-template artifact format mismatch")
    if section_data.get("section") != list(SECTION) or section_data.get("modulus") != MODULUS:
        raise ValueError("section definition mismatch")
    verify_dag(section_data.get("graph_audit"))
    templates = expected_templates()
    if len(templates) != 52 or section_data.get("template_count") != 52:
        raise ValueError("template count is not 52")
    if section_data.get("templates") != templates:
        raise ValueError("stored templates differ from independent enumeration")
    stored_direct = section_data.get("direct_audit")
    if not isinstance(stored_direct, dict):
        raise ValueError("direct audit missing")
    recomputed_direct = direct_audit(int(stored_direct["bound_exclusive"]), templates)
    if recomputed_direct != stored_direct:
        raise ValueError("direct audit mismatch")
    cycle_rows, _ = verify_cycles(cycle_data)
    verify_domination(domination, cycle_rows)
    transfer_rows, heteroclinic = verify_transfer(transfer, templates)
    retained_paths, adversarial, mixed_count, mixed_precision = verify_switches(switches, templates)
    if section_data.get("proves_collatz") is not False or cycle_data.get("proves_collatz") is not False:
        raise ValueError("Phase 5 artifacts claim a Collatz proof")
    return {
        "valid": True,
        "status": "verified_phase5_algebraic_certificates_with_bounded_heuristics_unresolved",
        "section_deleted_graph_acyclic": True,
        "maximum_first_return_length": 9,
        "template_count": 52,
        "direct_audit": recomputed_direct,
        "simple_cycle_count": 108,
        "noncontracting_words": ["1", "101", "1101", "011101"],
        "maximum_other_multiplier": "27/32",
        "return20_domination_verified": True,
        "shadow_identity_rows": transfer_rows,
        "heteroclinic_identity_count": heteroclinic,
        "retained_shadow_paths_checked": retained_paths,
        "dangerous_repetition_families_checked": adversarial,
        "mixed_block_records_checked": mixed_count,
        "best_mixed_block_excess_bound": f"2^-{mixed_precision}",
        "H5_A": switches["H5_A"],
        "H5_B": switches["H5_B"],
        "universal_rank_certified": False,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as error:
        print(f"INVALID: {error}")
        return 1
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
