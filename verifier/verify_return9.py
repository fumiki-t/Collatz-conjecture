#!/usr/bin/env python3
"""Independent verifier for Phase 4 first-return certificates.

No source module is imported. All code, template, composition, return, z, and
strict section-descent arithmetic is reconstructed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from math import gcd
from pathlib import Path


TRANSITIONS = {
    1: {0: 5, 1: 2},
    2: {0: 1, 1: 8},
    4: {0: 2, 1: 2},
    5: {0: 7, 1: 8},
    7: {0: 8, 1: 2},
    8: {0: 4, 1: 8},
}
KAPPA = {0: 1, 2: 5, 4: 21}


def step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def first_return(value: int) -> tuple[int, str]:
    if value % 9 != 2:
        raise ValueError("value is outside the section")
    current = value
    bits: list[str] = []
    for _ in range(100_000):
        bits.append(str(current % 2))
        current = step(current)
        if current % 9 == 2:
            return current, "".join(bits)
    raise ValueError("return step limit exceeded")


def ceiling(a: int, b: int) -> int:
    return -((-a) // b)


def residue_for(c: int, a: int, b: int) -> int:
    if c == 0:
        mod3 = 1 if a % 2 == 0 else 2
    elif c == 2:
        mod3 = 2 if a % 2 == 0 else 1
    elif c == 4:
        mod3 = 0
    else:
        raise ValueError("bad c")
    mod4 = 1 if b == 0 else 3
    matches = [
        v
        for v in range(1, 12, 2)
        if v % 3 == mod3 and pow(3, a + 1, 4) * v % 4 == mod4
    ]
    if len(matches) != 1:
        raise ValueError("CRT branch is not unique")
    return matches[0]


@dataclass(frozen=True, slots=True)
class Template:
    name: str
    word: str
    source_base: int
    source_step: int
    output_base: int
    output_step: int
    kind: str
    c: int | None
    a: int | None
    b: int | None
    residue: int | None

    def compact(self) -> dict[str, object]:
        return {
            "name": self.name,
            "word": self.word,
            "source": [self.source_base, self.source_step],
            "output": [self.output_base, self.output_step],
            "kind": self.kind,
            "c": self.c,
            "a": self.a,
            "b": self.b,
            "v_residue_mod_12": self.residue,
        }


def templates(max_a: int) -> list[Template]:
    result = [
        Template("special-01", "01", 2, 36, 2, 27, "SPECIAL", None, None, None, None),
        Template("special-0001", "0001", 56, 144, 11, 27, "SPECIAL", None, None, None, None),
    ]
    for c in (0, 2, 4):
        first_a = 0 if c == 4 else 1
        for a in range(first_a, max_a + 1):
            for b in (0, 1):
                residue = residue_for(c, a, b)
                source_base = (1 << c) * (3 * (1 << a) * residue - 1)
                source_step = (1 << c) * 3 * (1 << a) * 12
                output_numerator = pow(3, a + b + 1) * residue - 1
                if output_numerator % 4:
                    raise ValueError("template output is not integral")
                result.append(
                    Template(
                        f"c{c}-a{a}-b{b}",
                        "0" * c + "1" * a + "0" + str(b),
                        source_base,
                        source_step,
                        output_numerator // 4,
                        pow(3, a + b + 2),
                        "PARAMETRIC",
                        c,
                        a,
                        b,
                        residue,
                    )
                )
    return result


def verify_template(template: Template) -> None:
    constant = template.source_base
    slope = template.source_step
    if constant % 9 != 2 or slope % 9:
        raise ValueError("template source is not in S")
    for index, raw_bit in enumerate(template.word):
        bit = int(raw_bit)
        if constant % 2 != bit or slope % 2:
            raise ValueError("template parity is not fixed on the whole family")
        if bit:
            constant = (3 * constant + 1) // 2
            slope = 3 * slope // 2
        else:
            constant //= 2
            slope //= 2
        if index + 1 < len(template.word):
            if slope % 9 or constant % 9 == 2:
                raise ValueError("template has an early return")
    if (constant, slope) != (template.output_base, template.output_step):
        raise ValueError("template affine return mismatch")
    if constant % 9 != 2 or slope % 9:
        raise ValueError("template endpoint is not in S")
    if template.kind == "PARAMETRIC":
        assert template.c is not None and template.a is not None and template.b is not None
        assert template.residue is not None
        c, a, b, v = template.c, template.a, template.b, template.residue
        n = (1 << c) * (3 * (1 << a) * v - 1)
        returned = (pow(3, a + b + 1) * v - 1) // 4
        if (n, returned) != (template.source_base, template.output_base):
            raise ValueError("n-coordinate formula mismatch")
        z = (4 * n + 1) // 3
        z_next = (4 * returned + 1) // 3
        if z + KAPPA[c] != (1 << (a + c + 2)) * v:
            raise ValueError("source z-coordinate formula mismatch")
        if z_next != pow(3, a + b) * v:
            raise ValueError("return z-coordinate formula mismatch")
        bracket = (pow(3, a + b) - (1 << (a + c + 2))) * v + KAPPA[c]
        if 3 * bracket % 4 or returned - n != 3 * bracket // 4:
            raise ValueError("return difference formula mismatch")


def formula_from_word_independent(n: int, word: str) -> int:
    if word == "01":
        if (n - 2) % 36:
            raise ValueError("bad 01 source")
        return 27 * ((n - 2) // 36) + 2
    if word == "0001":
        if (n - 56) % 144:
            raise ValueError("bad 0001 source")
        return 27 * ((n - 56) // 144) + 11
    if word.startswith("1"):
        c = 0
    elif word.startswith("001"):
        c = 2
    elif word.startswith("0000"):
        c = 4
    else:
        raise ValueError("word outside code")
    cursor = c
    while cursor < len(word) and word[cursor] == "1":
        cursor += 1
    a = cursor - c
    if cursor + 2 != len(word) or word[cursor] != "0":
        raise ValueError("bad parametric word")
    b = int(word[-1])
    denominator = 3 * (1 << a)
    scaled = n // (1 << c)
    if n % (1 << c) or (scaled + 1) % denominator:
        raise ValueError("bad parametric source")
    v = (scaled + 1) // denominator
    if v <= 0 or v % 12 != residue_for(c, a, b):
        raise ValueError("bad parameter domain")
    numerator = pow(3, a + b + 1) * v - 1
    if numerator % 4:
        raise ValueError("non-integral return")
    returned = numerator // 4
    z = (4 * n + 1) // 3
    z_next = (4 * returned + 1) // 3
    if z + KAPPA[c] != (1 << (a + c + 2)) * v or z_next != pow(3, a + b) * v:
        raise ValueError("z cross-check failed")
    return returned


def direct_audit(bound: int) -> dict[str, object]:
    digest = hashlib.sha256()
    buffer = bytearray()
    count = 0
    steps = 0
    for n in range(2, bound, 9):
        returned, word = first_return(n)
        if formula_from_word_independent(n, word) != returned:
            raise ValueError("direct/formula mismatch")
        count += 1
        steps += len(word)
        buffer.extend(f"{n}:{returned}:{word}\n".encode("ascii"))
        if len(buffer) >= 1 << 20:
            digest.update(buffer)
            buffer.clear()
    digest.update(buffer)
    return {
        "bound_exclusive": bound,
        "section_integers_checked": count,
        "shortcut_steps_checked": steps,
        "sha256": digest.hexdigest(),
    }


@dataclass(frozen=True, slots=True)
class Family:
    source_base: int
    source_step: int
    endpoint_base: int
    endpoint_step: int
    history: tuple[str, ...]
    words: tuple[str, ...]
    parent_id: int | None
    composition: tuple[int, int, int, int] | None

    @classmethod
    def from_json(cls, value: object) -> "Family":
        if not isinstance(value, dict):
            raise ValueError("family is not an object")
        source = value.get("source")
        endpoint = value.get("endpoint")
        history = value.get("history")
        words = value.get("words")
        composition = value.get("composition")
        if not (
            isinstance(source, list)
            and len(source) == 2
            and isinstance(endpoint, list)
            and len(endpoint) == 2
            and isinstance(history, list)
            and isinstance(words, list)
            and len(history) == len(words)
        ):
            raise ValueError("malformed family")
        return cls(
            int(source[0]),
            int(source[1]),
            int(endpoint[0]),
            int(endpoint[1]),
            tuple(map(str, history)),
            tuple(map(str, words)),
            value.get("parent_id") if value.get("parent_id") is None else int(value["parent_id"]),
            None if composition is None else tuple(map(int, composition)),
        )

    def compact(self) -> dict[str, object]:
        return {
            "source": [self.source_base, self.source_step],
            "endpoint": [self.endpoint_base, self.endpoint_step],
            "history": list(self.history),
            "words": list(self.words),
            "parent_id": self.parent_id,
            "composition": list(self.composition) if self.composition else None,
        }


def root_from_template(template: Template) -> Family:
    return Family(
        template.source_base,
        template.source_step,
        template.output_base,
        template.output_step,
        (template.name,),
        (template.word,),
        None,
        None,
    )


def compose(parent: Family, template: Template, parent_id: int) -> Family | None:
    common = gcd(parent.endpoint_step, template.source_step)
    difference = template.source_base - parent.endpoint_base
    if difference % common:
        return None
    period = template.source_step // common
    parameter_base = 0 if period == 1 else (
        (difference // common)
        * pow(parent.endpoint_step // common, -1, period)
    ) % period
    template_base = (
        parent.endpoint_base
        + parent.endpoint_step * parameter_base
        - template.source_base
    ) // template.source_step
    template_step = parent.endpoint_step // common
    shift = max(0, ceiling(-template_base, template_step))
    parameter_base += period * shift
    template_base += template_step * shift
    return Family(
        parent.source_base + parent.source_step * parameter_base,
        parent.source_step * period,
        template.output_base + template.output_step * template_base,
        template.output_step * template_step,
        parent.history + (template.name,),
        parent.words + (template.word,),
        parent_id,
        (parameter_base, period, template_base, template_step),
    )


def verify_recurrence_bridge(parent: Family, child: Family, template_map: dict[str, Template]) -> None:
    previous_template = template_map[parent.history[-1]]
    next_template = template_map[child.history[-1]]
    if previous_template.kind != "PARAMETRIC" or next_template.kind != "PARAMETRIC":
        return
    assert previous_template.residue is not None and previous_template.output_step > 0
    assert next_template.residue is not None
    assert previous_template.a is not None and previous_template.b is not None
    assert next_template.a is not None and next_template.c is not None
    assert child.composition is not None
    parameter_base, period, next_u_base, next_u_step = child.composition
    parent_endpoint_base = parent.endpoint_base + parent.endpoint_step * parameter_base
    parent_endpoint_step = parent.endpoint_step * period
    if (
        (parent_endpoint_base - previous_template.output_base)
        % previous_template.output_step
        or parent_endpoint_step % previous_template.output_step
    ):
        raise ValueError("previous v parameter is not affine-integral")
    previous_u_base = (
        parent_endpoint_base - previous_template.output_base
    ) // previous_template.output_step
    previous_u_step = parent_endpoint_step // previous_template.output_step
    previous_v_base = previous_template.residue + 12 * previous_u_base
    previous_v_step = 12 * previous_u_step
    next_v_base = next_template.residue + 12 * next_u_base
    next_v_step = 12 * next_u_step
    left_factor = 1 << (next_template.a + next_template.c + 2)
    right_factor = pow(3, previous_template.a + previous_template.b)
    kappa = KAPPA[next_template.c]
    if left_factor * next_v_base != right_factor * previous_v_base + kappa:
        raise ValueError("recurrence bridge constant mismatch")
    if left_factor * next_v_step != right_factor * previous_v_step:
        raise ValueError("recurrence bridge slope mismatch")


def direct_exception(start: int, witness: object) -> None:
    if not isinstance(witness, dict) or int(witness.get("start", -1)) != start:
        raise ValueError("bad finite-tail witness")
    if start == 2:
        if not witness.get("base_case") or int(witness.get("end", -1)) != 2:
            raise ValueError("bad section base case")
        return
    current = start
    claimed_words = witness.get("words")
    claimed_returns = witness.get("returns")
    if not isinstance(claimed_words, list) or claimed_returns != len(claimed_words):
        raise ValueError("bad direct return count")
    for claimed_word in claimed_words:
        current, actual_word = first_return(current)
        if actual_word != claimed_word:
            raise ValueError("direct witness return word mismatch")
    if current != witness.get("end") or current >= start:
        raise ValueError("direct witness does not reach a smaller S value")


def verify_code_theorem() -> None:
    for residue, edges in TRANSITIONS.items():
        for bit, target in edges.items():
            representative = residue if residue % 2 == bit else residue + 9
            if step(representative) % 9 != target:
                raise ValueError("mod-9 transition audit failed")
    nonreturn_edges = {
        (2, 0): 1,
        (2, 1): 8,
        (1, 0): 5,
        (5, 0): 7,
        (5, 1): 8,
        (7, 0): 8,
        (8, 0): 4,
        (8, 1): 8,
    }
    return_edges = {(1, 1), (4, 0), (4, 1), (7, 1)}
    actual_nonreturn = {
        (residue, bit): target
        for residue, edges in TRANSITIONS.items()
        for bit, target in edges.items()
        if target != 2
    }
    actual_return = {
        (residue, bit)
        for residue, edges in TRANSITIONS.items()
        for bit, target in edges.items()
        if target == 2
    }
    if actual_nonreturn != nonreturn_edges or actual_return != return_edges:
        raise ValueError("first-return language graph differs from the exact grammar")
    if Fraction(1, 4) + Fraction(1, 16) + Fraction(1, 2) + Fraction(1, 8) + Fraction(1, 16) != 1:
        raise ValueError("Kraft identity failed")
    # The finite graph identities above exhaust every first-return path: the
    # only non-returning cycle is the 1-loop at state 8, whose sole exit is
    # 8 --0--> 4; both bits from 4 return.  All other paths from 2 either return
    # at 01/0001 or enter state 8 through exactly one of the three prefixes.


def expected_transition_rows() -> list[dict[str, int]]:
    rows: list[dict[str, int]] = []
    for residue in sorted(TRANSITIONS):
        for bit in (0, 1):
            representative = residue if residue % 2 == bit else residue + 9
            rows.append(
                {
                    "residue": residue,
                    "bit": bit,
                    "representative": representative,
                    "target": TRANSITIONS[residue][bit],
                }
            )
    return rows


def verify(certificate_path: Path, code_audit_path: Path) -> dict[str, object]:
    certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
    code_audit = json.loads(code_audit_path.read_text(encoding="utf-8"))
    if certificate.get("format") != "collatz-return9-certificate-v1" or certificate.get("version") != 1:
        raise ValueError("unsupported return9 certificate")
    bounds = certificate.get("bounds")
    if not isinstance(bounds, dict):
        raise ValueError("missing certificate bounds")
    max_a = int(bounds["max_a"])
    max_depth = int(bounds["max_return_depth"])
    expected_templates = templates(max_a)
    for template in expected_templates:
        verify_template(template)
    if certificate.get("templates") != [template.compact() for template in expected_templates]:
        raise ValueError("template dictionary mismatch")
    for index, left in enumerate(expected_templates):
        for right in expected_templates[index + 1 :]:
            if (right.source_base - left.source_base) % gcd(left.source_step, right.source_step) == 0:
                raise ValueError("finite template source families overlap")
    verify_code_theorem()
    if code_audit.get("format") != "collatz-return9-code-audit-v1":
        raise ValueError("unsupported return-code audit")
    if code_audit.get("transitions") != expected_transition_rows():
        raise ValueError("stored mod-9 transition audit mismatch")
    expected_language = {
        "special": ["01", "0001"],
        "parametric": [
            "1^a 0 b, a>=1",
            "00 1^a 0 b, a>=1",
            "0000 1^a 0 b, a>=0",
        ],
        "prefix_free": True,
        "structural_proof": {
            "2_on_01": "immediate return",
            "2_on_0001": "immediate return through 1,5,7",
            "2_on_1": "8, then 1-loop, 0 to 4, either bit returns to 2",
            "2_on_001": "5 to 8, then the same loop family",
            "2_on_0000": "8, then the same loop family including zero loops",
        },
    }
    if code_audit.get("exact_language") != expected_language:
        raise ValueError("stored exact first-return language mismatch")
    expected_kraft = {
        "special": [5, 16],
        "c0": [1, 2],
        "c2": [1, 8],
        "c4": [1, 16],
        "total": [1, 1],
        "full_binary_entropy_retained": True,
    }
    if code_audit.get("kraft") != expected_kraft:
        raise ValueError("stored exact Kraft audit mismatch")
    finite_kraft = sum(
        (Fraction(1, 1 << len(template.word)) for template in expected_templates),
        Fraction(),
    )
    overflow_kraft = 1 - finite_kraft
    expected_dictionary = {
        "max_a": max_a,
        "template_count": len(expected_templates),
        "kraft_covered": [finite_kraft.numerator, finite_kraft.denominator],
        "overflow_open": [overflow_kraft.numerator, overflow_kraft.denominator],
    }
    if code_audit.get("finite_search_dictionary") != expected_dictionary:
        raise ValueError("stored finite return dictionary audit mismatch")
    if certificate.get("finite_code_kraft") != expected_dictionary["kraft_covered"]:
        raise ValueError("certificate finite Kraft sum mismatch")
    if certificate.get("overflow_code_kraft") != expected_dictionary["overflow_open"]:
        raise ValueError("certificate overflow Kraft sum mismatch")
    stored_direct = code_audit.get("direct_audit")
    if not isinstance(stored_direct, dict):
        raise ValueError("direct audit is missing")
    direct_result = direct_audit(int(stored_direct["bound_exclusive"]))
    expected_direct = dict(direct_result)
    expected_direct["result"] = "all_direct_returns_equal_formula_and_z_coordinate"
    if stored_direct != expected_direct:
        raise ValueError("stored direct audit mismatch")

    raw_records = certificate.get("records")
    if not isinstance(raw_records, list):
        raise ValueError("certificate records missing")
    families: list[Family] = []
    rules: list[dict[str, object]] = []
    by_parent: dict[int, list[int]] = {}
    node_counts: Counter[int] = Counter()
    closed_counts: Counter[int] = Counter()
    open_counts: Counter[int] = Counter()
    rule_counts: Counter[str] = Counter()
    template_map = {template.name: template for template in expected_templates}
    for expected_id, raw in enumerate(raw_records):
        if not isinstance(raw, dict) or raw.get("id") != expected_id:
            raise ValueError("record IDs are not stable sequential integers")
        family = Family.from_json(raw.get("family"))
        rule = raw.get("rule")
        if not isinstance(rule, dict) or not isinstance(rule.get("type"), str):
            raise ValueError("record rule missing")
        if family.source_base % 9 != 2 or family.source_step % 9:
            raise ValueError("family source leaves S")
        if family.endpoint_base % 9 != 2 or family.endpoint_step % 9:
            raise ValueError("family endpoint leaves S")
        if family.parent_id is None:
            if len(family.history) != 1:
                raise ValueError("non-root family lacks a parent")
            expected_root = root_from_template(template_map[family.history[0]])
            if family != expected_root:
                raise ValueError("root family differs from its template")
        else:
            if not 0 <= family.parent_id < expected_id:
                raise ValueError("invalid parent record ID")
            parent = families[family.parent_id]
            expected_child = compose(parent, template_map[family.history[-1]], family.parent_id)
            if expected_child != family:
                raise ValueError("RETURN_COMPOSE child identity mismatch")
            verify_recurrence_bridge(parent, family, template_map)
            by_parent.setdefault(family.parent_id, []).append(expected_id)
        depth = len(family.history)
        node_counts[depth] += 1
        rule_type = str(rule["type"])
        rule_counts[rule_type] += 1
        difference_slope = family.endpoint_step - family.source_step
        difference_base = family.endpoint_base - family.source_base
        if rule_type in ("RETURN_DESCENT", "RETURN_SMALLER_S"):
            if rule_type == "RETURN_DESCENT" and depth != 1:
                raise ValueError("RETURN_DESCENT used after a composition")
            if rule_type == "RETURN_SMALLER_S" and depth < 2:
                raise ValueError("RETURN_SMALLER_S used before composition")
            if difference_slope > 0 or difference_base >= 0:
                raise ValueError("invalid uniform return descent")
            closed_counts[depth] += 1
        elif rule_type == "RETURN_FINITE_TAIL":
            if difference_slope >= 0:
                raise ValueError("finite-tail slope is not negative")
            high = difference_base // (-difference_slope)
            if rule.get("high_parameter") != high:
                raise ValueError("finite-tail high parameter mismatch")
            exceptions = rule.get("exceptions")
            if not isinstance(exceptions, list) or len(exceptions) != high + 1:
                raise ValueError("finite-tail exceptions are not exhaustive")
            for parameter, witness in enumerate(exceptions):
                if not isinstance(witness, dict) or witness.get("parameter") != parameter:
                    raise ValueError("finite-tail parameter mismatch")
                direct_exception(family.source_base + family.source_step * parameter, witness)
            closed_counts[depth] += 1
        elif rule_type == "RETURN_COMPOSE":
            if depth >= max_depth or rule.get("overflow_open") is not True:
                raise ValueError("invalid bounded RETURN_COMPOSE")
        elif rule_type == "OPEN":
            if depth != max_depth and rule.get("reason") != "finite_exception_not_closed":
                raise ValueError("OPEN before configured return depth")
            open_counts[depth] += 1
        else:
            raise ValueError(f"unknown return rule {rule_type}")
        families.append(family)
        rules.append(rule)

    for record_id, (family, rule) in enumerate(zip(families, rules, strict=True)):
        if rule["type"] != "RETURN_COMPOSE":
            if by_parent.get(record_id):
                raise ValueError("non-compose record has children")
            continue
        expected_children = [
            child
            for template in expected_templates
            if (child := compose(family, template, record_id)) is not None
        ]
        actual_ids = by_parent.get(record_id, [])
        if rule.get("children") != actual_ids:
            raise ValueError("RETURN_COMPOSE child ID list mismatch")
        if [families[child_id] for child_id in actual_ids] != expected_children:
            raise ValueError("RETURN_COMPOSE finite dictionary is incomplete")

    summary = certificate.get("summary")
    if not isinstance(summary, dict):
        raise ValueError("certificate summary missing")
    expected_nodes = {str(depth): node_counts[depth] for depth in range(1, max_depth + 1)}
    expected_closed = {str(depth): closed_counts[depth] for depth in range(1, max_depth + 1)}
    expected_open = {str(depth): open_counts[depth] for depth in range(1, max_depth + 1)}
    if summary.get("nodes_by_depth") != expected_nodes:
        raise ValueError("summary node counts mismatch")
    if summary.get("closed_by_depth") != expected_closed:
        raise ValueError("summary closed counts mismatch")
    if summary.get("open_by_depth") != expected_open:
        raise ValueError("summary open counts mismatch")
    if summary.get("rule_counts") != dict(sorted(rule_counts.items())):
        raise ValueError("summary rule counts mismatch")
    root_ids = [index for index, family in enumerate(families) if family.parent_id is None]
    if summary.get("root_ids") != root_ids:
        raise ValueError("summary root IDs mismatch")
    if summary.get("template_count") != len(expected_templates):
        raise ValueError("summary template count mismatch")
    if summary.get("max_a") != max_a or summary.get("max_return_depth") != max_depth:
        raise ValueError("summary search bounds mismatch")
    if summary.get("overflow_code_open") is not True:
        raise ValueError("infinite return-code overflow is not marked OPEN")
    if certificate.get("proves_collatz") is not False or summary.get("proves_collatz") is not False:
        raise ValueError("bounded return certificate claims a proof")
    negative = {value: first_return(value)[0] for value in (-7, -61, -34, -25)}
    if negative != {-7: -7, -61: -34, -34: -25, -25: -61}:
        raise ValueError("negative shadow audit failed")
    return {
        "valid": True,
        "status": "verified_partial_return9_certificate_with_open_and_run_overflow",
        "max_a": max_a,
        "max_return_depth": max_depth,
        "templates": len(expected_templates),
        "records": len(families),
        "closed_records": sum(closed_counts.values()),
        "open_records": sum(open_counts.values()),
        "return_code_prefix_free": True,
        "return_code_kraft": "1/1",
        "direct_audit": direct_result,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path)
    parser.add_argument("--code-audit", type=Path, default=Path("artifacts/return9_code_audit.json"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.certificate, args.code_audit)
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
