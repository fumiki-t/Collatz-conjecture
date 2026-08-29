#!/usr/bin/env python3
"""Generate exact Phase 18 affine-graph trichotomy evidence.

All acceptance decisions compare integers or Fractions.  Logarithmic
discrepancy is used in the accompanying proof only as notation.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def enc(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_affine(word: str) -> tuple[int, int, int]:
    """Return (L,q,B) for F_w(x)=(3^q*x+B)/2^L."""
    if not word or set(word) - {"0", "1"}:
        raise ValueError("a nonempty binary parity word is required")
    length = odd = affine = 0
    for bit in word:
        if bit == "1":
            affine = 3 * affine + (1 << length)
            odd += 1
        length += 1
    return length, odd, affine


def edge_record(source: int, target: int, word: str, edge_id: int) -> dict[str, object]:
    length, odd, affine = word_affine(word)
    coefficient = Fraction(3**odd, 2**length)
    return {
        "id": edge_id,
        "source": source,
        "target": target,
        "word": word,
        "L": length,
        "q": odd,
        "B": affine,
        "coefficient": enc(coefficient),
        "additive": enc(Fraction(affine, 2**length)),
        "normalized_beta": enc(Fraction(affine, 3**odd)),
    }


def coefficient_sign(odd: int, length: int) -> int:
    left, right = 3**odd, 2**length
    return (left > right) - (left < right)


def path_record(words: list[str]) -> dict[str, object]:
    total_c = Fraction(1)
    beta = Fraction(0)
    affine = 0
    length = odd = 0
    safe = True
    coefficients = []
    beta_terms = []
    for word in words:
        edge_length, edge_odd, edge_affine = word_affine(word)
        edge_c = Fraction(3**edge_odd, 2**edge_length)
        edge_b = Fraction(edge_affine, 3**edge_odd)
        beta_terms.append(edge_b / total_c)
        beta += edge_b / total_c
        affine = 3**edge_odd * affine + (1 << length) * edge_affine
        length += edge_length
        odd += edge_odd
        total_c *= edge_c
        coefficients.append(enc(total_c))
        safe = safe and total_c > 1
    literal_beta = Fraction(affine, 3**odd)
    if beta != literal_beta or sum(beta_terms, Fraction()) != literal_beta:
        raise AssertionError("normalized correction identity")
    modulus = 1 << length
    source_residue = (-affine * pow(3**odd, -1, modulus)) % modulus
    return {
        "word": "".join(words),
        "block_words": words,
        "L": length,
        "q": odd,
        "B": affine,
        "coefficient": enc(total_c),
        "normalized_beta": enc(beta),
        "prefix_coefficients": coefficients,
        "strictly_coefficient_safe": safe,
        "canonical_source_residue_mod_2L": source_residue,
    }


def strongly_connected_components(vertices: int, edges: list[dict[str, object]]) -> list[list[int]]:
    adjacency = [[] for _ in range(vertices)]
    reverse = [[] for _ in range(vertices)]
    for edge in edges:
        a, b = int(edge["source"]), int(edge["target"])
        adjacency[a].append(b)
        reverse[b].append(a)
    seen: set[int] = set()
    order: list[int] = []

    def visit(vertex: int) -> None:
        seen.add(vertex)
        for target in adjacency[vertex]:
            if target not in seen:
                visit(target)
        order.append(vertex)

    for vertex in range(vertices):
        if vertex not in seen:
            visit(vertex)
    seen.clear()
    components: list[list[int]] = []

    def collect(vertex: int, component: list[int]) -> None:
        seen.add(vertex)
        component.append(vertex)
        for target in reverse[vertex]:
            if target not in seen:
                collect(target, component)

    for vertex in reversed(order):
        if vertex not in seen:
            component: list[int] = []
            collect(vertex, component)
            components.append(sorted(component))
    return sorted(components, key=lambda value: value[0])


def simple_cycles(component: list[int], edges: list[dict[str, object]]) -> list[tuple[int, ...]]:
    allowed = set(component)
    adjacency: dict[int, list[dict[str, object]]] = defaultdict(list)
    for edge in edges:
        if int(edge["source"]) in allowed and int(edge["target"]) in allowed:
            adjacency[int(edge["source"])].append(edge)
    found: set[tuple[int, ...]] = set()

    def canonical(ids: tuple[int, ...]) -> tuple[int, ...]:
        rotations = [ids[index:] + ids[:index] for index in range(len(ids))]
        return min(rotations)

    def walk(start: int, vertex: int, used: set[int], path: tuple[int, ...]) -> None:
        for edge in adjacency[vertex]:
            target = int(edge["target"])
            next_path = path + (int(edge["id"]),)
            if target == start:
                found.add(canonical(next_path))
            elif target not in used:
                walk(start, target, used | {target}, next_path)

    for start in component:
        walk(start, start, {start}, ())
    return sorted(found)


def classify_graph(vertices: int, edges: list[dict[str, object]]) -> dict[str, object]:
    components = strongly_connected_components(vertices, edges)
    edge_by_id = {int(edge["id"]): edge for edge in edges}
    component_rows = []
    vertex_component = {}
    for index, component in enumerate(components):
        for vertex in component:
            vertex_component[vertex] = index
        cycles = simple_cycles(component, edges)
        cycle_rows = []
        signs = set()
        for cycle in cycles:
            odd = sum(int(edge_by_id[item]["q"]) for item in cycle)
            length = sum(int(edge_by_id[item]["L"]) for item in cycle)
            sign = coefficient_sign(odd, length)
            signs.add(sign)
            cycle_rows.append({"edge_ids": list(cycle), "q": odd, "L": length, "sign": sign})
        if not signs:
            kind = "acyclic"
        elif signs == {1}:
            kind = "positive"
        elif signs == {-1}:
            kind = "negative"
        else:
            kind = "mixed"
        component_rows.append({"vertices": component, "kind": kind, "simple_cycles": cycle_rows})

    dag = {index: set() for index in range(len(components))}
    for edge in edges:
        source = vertex_component[int(edge["source"])]
        target = vertex_component[int(edge["target"])]
        if source != target:
            dag[source].add(target)

    def reachable(source: int, target: int) -> bool:
        queue = [source]
        seen = {source}
        while queue:
            current = queue.pop()
            if current == target:
                return True
            for item in dag[current]:
                if item not in seen:
                    seen.add(item)
                    queue.append(item)
        return False

    mixed = any(row["kind"] == "mixed" for row in component_rows)
    positive = [i for i, row in enumerate(component_rows) if row["kind"] == "positive"]
    negative = [i for i, row in enumerate(component_rows) if row["kind"] == "negative"]
    witnesses = [[a, b] for a in positive for b in negative if reachable(a, b)]
    graph_type = "III" if mixed else ("II" if witnesses else "I")
    return {
        "type": graph_type,
        "components": component_rows,
        "condensation_edges": sorted([list(pair) for a, targets in dag.items() for pair in ((a, b) for b in targets)]),
        "positive_to_negative_witnesses": witnesses,
    }


def graph_signature(vertices: int, choices: tuple[int, ...]) -> str:
    return f"v{vertices}:" + ",".join(str(value) for value in choices)


def graph_edges(vertices: int, choices: tuple[int, ...]) -> list[dict[str, object]]:
    edges = []
    for source in range(vertices):
        for label_index, word in enumerate(("0", "1")):
            target = choices[2 * source + label_index]
            if target >= 0:
                edges.append(edge_record(source, target, word, len(edges)))
    return edges


def safe_path_counts(vertices: int, edges: list[dict[str, object]], depth: int, cap: int) -> dict[str, object]:
    adjacency: dict[int, list[dict[str, object]]] = defaultdict(list)
    for edge in edges:
        adjacency[int(edge["source"])].append(edge)
    states = [(vertex, 0, 0) for vertex in range(vertices)]
    counts = []
    bounded = []
    for _ in range(depth):
        next_states = []
        for vertex, odd, length in states:
            for edge in adjacency[vertex]:
                new_odd = odd + int(edge["q"])
                new_length = length + int(edge["L"])
                if 3**new_odd > 2**new_length:
                    next_states.append((int(edge["target"]), new_odd, new_length))
        states = next_states
        counts.append(len(states))
        bounded.append(sum(3**odd <= cap * 2**length for _, odd, length in states))
    return {"safe_path_counts": counts, "safe_final_multiplier_at_most_cap": bounded}


def graph_audit(max_vertices: int = 3, depth: int = 12, cap: int = 4) -> dict[str, object]:
    rows = []
    type_counts: Counter[str] = Counter()
    by_vertices: dict[str, Counter[str]] = {}
    for vertices in range(1, max_vertices + 1):
        local: Counter[str] = Counter()
        for choices in itertools.product(range(-1, vertices), repeat=2 * vertices):
            edges = graph_edges(vertices, choices)
            classification = classify_graph(vertices, edges)
            paths = safe_path_counts(vertices, edges, depth, cap)
            graph_type = str(classification["type"])
            type_counts[graph_type] += 1
            local[graph_type] += 1
            rows.append({
                "signature": graph_signature(vertices, choices),
                "type": graph_type,
                "component_kinds": [row["kind"] for row in classification["components"]],
                "positive_to_negative": bool(classification["positive_to_negative_witnesses"]),
                **paths,
            })
        by_vertices[str(vertices)] = local
    return {
        "format": "collatz-phase18-graph-audit-v1",
        "claim": {"E30": "VERIFIED_FINITE"},
        "graph_class": "deterministic partial graphs with labels 0 and 1; each source-label pair is absent or has one target",
        "maximum_vertices": max_vertices,
        "safe_path_depth": depth,
        "final_multiplier_cap": cap,
        "graphs_enumerated": len(rows),
        "type_counts": dict(sorted(type_counts.items())),
        "type_counts_by_vertices": {key: dict(sorted(value.items())) for key, value in by_vertices.items()},
        "row_digest_sha256": digest(rows),
        "row_storage": "omitted; the independent verifier exhaustively reconstructs the canonical rows from the declared graph class",
        "finite_boundary": "Path counts are sanity checks only; the trichotomy proof does not use finite depth.",
        "proves_collatz": False,
    }


def normal_form_counterexample(k: int) -> dict[str, object]:
    if k < 2:
        raise ValueError("k must be at least two")
    first_negative = (3**k).bit_length() - 1 - k
    positive_total = 4 * k + 3
    negative_total = (3**positive_total).bit_length() - 1 - positive_total
    second_negative = negative_total - first_negative
    blocks = ["1" * (2 * k + 1), "0" * first_negative, "1" * (2 * k + 2), "0" * second_negative]
    record = path_record(blocks)
    if first_negative <= 0 or second_negative <= 0 or not record["strictly_coefficient_safe"]:
        raise AssertionError("NG30 construction")
    coefficient = Fraction(3**positive_total, 2 ** (positive_total + negative_total))
    if not 1 < coefficient < 2:
        raise AssertionError("NG30 final coefficient")
    return {
        "k": k,
        "stage_lengths": [2 * k + 1, first_negative, 2 * k + 2, second_negative],
        "stage_signs": ["positive", "negative", "positive", "negative"],
        "path": record,
    }


def theory_artifact() -> dict[str, object]:
    counterexamples = [normal_form_counterexample(k) for k in (2, 3, 4, 8, 16, 32)]
    return {
        "format": "collatz-phase18-theory-v1",
        "claims": {
            "P107": "VERIFIED_THEOREM",
            "P108": "VERIFIED_THEOREM",
            "P109": "VERIFIED_THEOREM",
            "P110": "CONDITIONAL",
            "P111": "VERIFIED_THEOREM",
            "NG30": "REFUTED",
            "H72": "OPEN",
        },
        "edge_identity": "F_e(x)=c_e(x+b_e), c_e=3^q/2^L, b_e=B_e/3^q>0 for an edge containing an odd step",
        "path_identity": "beta(e_1...e_n)=sum_i b(e_i)/C(e_1...e_(i-1))",
        "P107": {
            "statement": "In a finite graph with no mixed SCC, normalized beta is uniformly bounded over every coefficient-safe finite path.",
            "proof_invariant": "Positive SCC prefixes have a uniform linear discrepancy drift modulo bounded simple connectors; negative SCC suffixes have the reverse bound from endpoint safety. The finite condensation path contributes only finitely many geometric sums.",
        },
        "P108": {
            "statement": "With no mixed SCC, bounded-final-discrepancy safe paths have bounded length unless a positive SCC reaches a negative SCC; that reachability also constructs arbitrarily long such paths.",
            "corrected_normal_form": "A path is a bounded collection of connectors and sign-pure cycle packets along the acyclic SCC condensation. The number of sign changes is finite and graph-bounded, but need not be one.",
        },
        "P109": {
            "statement": "A mixed SCC contains a formal infinite coefficient-safe path with multiplier bounded above and below away from zero and with normalized beta growing at least linearly in block count.",
            "construction_repairs": [
                "close positive and negative walks at a common base vertex",
                "rotate the positive closed walk after its last minimum so every nonempty internal prefix is strictly positive",
                "choose an exact rational threshold H>1/(m_B*c_B)",
                "append the positive packet below the threshold and the negative packet above it"
            ],
        },
        "P110": {
            "statement": "Assuming EXT07, the particular balanced P109 itinerary cannot be a positive ordinary nonperiodic shortcut orbit.",
            "reason": "Bounded block-boundary multiplier and beta linear in block count force x=Theta(n) along those boundaries, so reciprocal sums diverge, contrary to EXT07.",
            "scope": "This does not exclude every itinerary through a mixed SCC.",
        },
        "P111": {
            "statement": "For an extended prefix Pe, r2(Pe)=r2(P)+lambda*2^L with integral lambda in the finite lift range; a fixed positive ordinary source has lambda=0 for all sufficiently long prefixes.",
            "reason": "Once 2^L exceeds the fixed source, its canonical least nonnegative residue is the source itself.",
        },
        "NG30": {
            "hypothesis": "Every long critical path in a sign-pure-SCC graph is, up to bounded connectors, one global positive packet followed by one global negative packet.",
            "status": "REFUTED",
            "counterfamily": "1^(2k+1) 0^n1 1^(2k+2) 0^n2 on a positive-negative-positive-negative SCC chain",
            "counterexamples": counterexamples,
            "surviving_statement": "The finite-stage SCC-condensation normal form in P108.",
        },
        "what_this_result_does_not_prove": "It does not prove that the H72 language has a closed finite graph, exclude positive ordinary sources, exclude all mixed itineraries, or prove Collatz.",
        "proves_collatz": False,
    }


def mixed_schedule(blocks: int = 512, threshold: int = 8) -> dict[str, object]:
    words: list[str] = []
    odd = length = affine = 0
    beta = Fraction(0)
    residue_previous = 0
    modulus_previous = 1
    lifts = []
    checkpoints = []
    rows = []
    for index in range(blocks):
        word = "1" if 3**odd <= threshold * 2**length else "0"
        edge_length, edge_odd, edge_affine = word_affine(word)
        old_c = Fraction(3**odd, 2**length)
        beta += Fraction(edge_affine, 3**edge_odd) / old_c
        affine = 3**edge_odd * affine + (1 << length) * edge_affine
        odd += edge_odd
        length += edge_length
        modulus = 1 << length
        residue = (-affine * pow(3**odd, -1, modulus)) % modulus
        lift = (residue - residue_previous) // modulus_previous
        if residue != residue_previous + lift * modulus_previous:
            raise AssertionError("source lift")
        lifts.append(lift)
        words.append(word)
        row = {
            "index": index + 1,
            "word": word,
            "q": odd,
            "L": length,
            "B": affine,
            "source_residue": residue,
            "lift": lift,
            "coefficient": enc(Fraction(3**odd, 2**length)),
            "normalized_beta": enc(beta),
        }
        rows.append(row)
        if index + 1 in {1, 2, 4, 8, 16, 32, 64, 128, 256, blocks}:
            checkpoints.append(row)
        residue_previous, modulus_previous = residue, modulus
    one_count = words.count("1")
    coefficient = Fraction(3**odd, 2**length)
    if not 1 < coefficient <= 12 or beta != Fraction(affine, 3**odd):
        raise AssertionError("mixed schedule invariant")
    return {
        "format": "collatz-phase18-mixed-schedule-v1",
        "claim": {"E30": "VERIFIED_FINITE", "P109": "VERIFIED_THEOREM"},
        "graph": {"vertices": 1, "positive_loop": "1", "negative_loop": "0", "type": "III"},
        "threshold": threshold,
        "selection_rule": "append 1 iff current coefficient is at most H, otherwise append 0",
        "blocks": blocks,
        "positive_blocks": one_count,
        "negative_blocks": blocks - one_count,
        "final": rows[-1],
        "checkpoint_rows": checkpoints,
        "row_digest_sha256": digest(rows),
        "lift_digest_sha256": digest(lifts),
        "nonzero_lifts": sum(value != 0 for value in lifts),
        "symbolic_linear_beta_lower_bound": enc(Fraction(one_count, 3 * threshold)),
        "finite_boundary": "Nonzero finite lifts do not prove that an infinite canonical residue fails to stabilize to a positive integer.",
        "proves_collatz": False,
    }


PROJECT_FILES = [
    "artifacts/phase7_macro12.json",
    "artifacts/phase8_ab_semigroup_search.json",
    "artifacts/phase13_critical_countermodel.json",
    "artifacts/phase14_coalescent_theory.json",
    "artifacts/phase16_theory.json",
    "artifacts/phase17_suffix_code.json",
]


def project_models(root: Path) -> dict[str, object]:
    files = {name: file_digest(root / name) for name in PROJECT_FILES}
    phase7 = json.loads((root / PROJECT_FILES[0]).read_text(encoding="utf-8"))
    phase8 = json.loads((root / PROJECT_FILES[1]).read_text(encoding="utf-8"))
    phase17 = json.loads((root / PROJECT_FILES[-1]).read_text(encoding="utf-8"))
    records = phase7["records"]
    sign_counts = Counter("positive" if int(row[6]) > int(row[8]) else "negative" for row in records)
    macro0 = str(records[0][3])
    macro0_record = path_record([macro0])
    code_signs = Counter()
    for row in phase17["codewords"]:
        multiplier = Fraction(int(row["multiplier"]["numerator"]), int(row["multiplier"]["denominator"]))
        code_signs["positive" if multiplier > 1 else "negative"] += 1
    return {
        "format": "collatz-phase18-project-models-v1",
        "claim": {"E30": "VERIFIED_FINITE", "H72": "OPEN"},
        "source_file_sha256": files,
        "models": [
            {
                "name": "Phase 7 macro alphabet",
                "observed": {"macros": len(records), "coefficient_signs": dict(sign_counts), "macro0": macro0_record},
                "classification": "NOT_AN_EXACT_FINITE_GRAPH",
                "reason": "The artifact is a finite factor alphabet without a closed transition graph. Free one-state concatenation would be a Type III overapproximation only.",
            },
            {
                "name": "Phase 8 A/B coefficient semigroup",
                "observed": {"coordinate": phase8["coordinate"]},
                "classification": "TYPE_III_OVERAPPROXIMATION",
                "reason": "A expands and B contracts in the coefficient coordinate, but literal integer admissibility uses unbounded affine state and guards.",
            },
            {
                "name": "Phase 10/11 two-tail states",
                "classification": "NOT_FIXED_FINITE",
                "reason": "Residues, ordinary heights, and affine margins grow with the horizon.",
            },
            {
                "name": "Phase 13 square-root countermodel",
                "classification": "FORMAL_UNBOUNDED_STATE",
                "reason": "The defect controller tracks an unbounded square-root-scale state; NG22 supplies a coherent 2-adic source but no positive ordinary integer.",
            },
            {
                "name": "Phase 14 coalescent quotient",
                "classification": "NOT_CLOSED",
                "reason": "NG24 refutes left-congruence/prefix closure of the finite endpoint quotient.",
            },
            {
                "name": "Phase 16 local predecessor rules",
                "classification": "NOT_A_CLOSED_AUTOMATON",
                "reason": "The rules are local height-conditioned exclusions, not a complete transition presentation.",
            },
            {
                "name": "Phase 17 suffix code",
                "observed": {"code_size": phase17["code_size"], "coefficient_signs": dict(code_signs)},
                "classification": "TYPE_I_SUBLANGUAGE",
                "reason": "All 11 selected codewords expand and suffix decoding is exact, but the code is only a sublanguage of the critical branch.",
            },
        ],
        "conclusion": "No accepted artifact currently supplies a prefix-complete closed finite graph for all H72 candidates.",
        "proves_collatz": False,
    }


def shortcut_prefix(start: int, horizon: int) -> str:
    value = start
    bits = []
    for _ in range(horizon):
        bit = value & 1
        bits.append(str(bit))
        value = (3 * value + 1) // 2 if bit else value // 2
    return "".join(bits)


def adversarial_words() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for m in range(3, 13):
        horizon = 3 * m + 12
        for label, start in ((f"2^{m}-1", 2**m - 1), (f"8^{m}-5", 8**m - 5)):
            rows.append({"family": label, "kind": "literal_orbit", "start": start, "horizon": horizon, "word": shortcut_prefix(start, horizon)})
    for r in range(1, 7):
        rows.append({"family": f"(110|111)^*:r={r}", "kind": "formal_word", "word": "".join("110" if i % 2 == 0 else "111" for i in range(r))})
        rows.append({"family": f"A^{r}", "kind": "formal_word", "word": "11101" * r})
        rows.append({"family": f"B^{r}", "kind": "formal_word", "word": "1100" * r})
        for s in range(1, 7):
            rows.append({"family": f"A^{r}B^{s}", "kind": "formal_word", "word": "11101" * r + "1100" * s})
    return rows


def adversarial_artifact(project: dict[str, object]) -> dict[str, object]:
    rows = []
    for description in adversarial_words():
        word = str(description["word"])
        record = path_record([word])
        rows.append({**description,
            "coefficient": record["coefficient"],
            "normalized_beta": record["normalized_beta"],
            "strictly_coefficient_safe": record["strictly_coefficient_safe"],
            "source_residue": record["canonical_source_residue_mod_2L"],
        })
    obstruction_scope = {
        "NG02": "finite coefficient alphabets do not by themselves preserve literal integer dynamics",
        "NG17": "coefficient-shadow/ranking information alone is not a universal barrier",
        "NG19": "finite dropping-safe spacing must retain ordinary height",
        "NG21": "mod-6 packing alone cannot improve the 1/9 exponent",
        "NG22": "analytic defect conditions plus a coherent 2-adic source are not contradictory",
        "NG23": "Haar volume does not control canonical representatives coefficient-one",
        "NG24": "coalescent endpoint equivalence is not a two-sided congruence",
        "NG25": "same-Q safe targets do not exhaust surplus reductions",
        "NG26": "useful coalescent targets need not be safe",
        "NG27": "same-Q compression gain is not bounded by three",
        "NG28": "predecessor carry may be negative",
        "NG29": "coefficient-only Haar pressure has a finite ceiling",
    }
    return {
        "format": "collatz-phase18-adversarial-v1",
        "claim": {"E30": "VERIFIED_FINITE", "NG30": "REFUTED"},
        "rows": rows,
        "row_digest_sha256": digest(rows),
        "macro0": project["models"][0]["observed"]["macro0"],
        "preserved_obstruction_scope": obstruction_scope,
        "interpretation": "The families test affine conventions and prevent old shortcuts; passing a finite row is not evidence of a universal theorem.",
        "proves_collatz": False,
    }


def obstruction_report() -> str:
    return """# Phase 18 obstruction report

## NG30 — single-mountain SCC normal form (`REFUTED`)

The proposed statement that every long bounded-final-discrepancy safe path in
a graph without mixed SCCs is, modulo bounded connectors, one positive packet
followed by one negative packet is false.

Take a four-state chain whose successive loop signs are positive, negative,
positive, negative; label the positive loops and connecting edges by `1`, and
the negative loops by `0`.  For every `k>=2`, put

```text
n1 = floor(log2((3/2)^k))
R  = 4k+3
n2 = floor(log2((3/2)^R))-n1
w_k = 1^(2k+1) 0^n1 1^(2k+2) 0^n2.
```

Integer bit lengths compute both floors exactly.  Every prefix has multiplier
strictly greater than one, the final multiplier lies strictly between one and
two, and all four loop packets grow without bound.  Therefore the intervening
negative packet cannot be absorbed into a bounded connector.

What survives is P108's finite-stage normal form: paths traverse the acyclic
SCC condensation, with a graph-bounded number of sign-pure cycle packets and
bounded connectors.  A one-switch order is not guaranteed.

## Smallest stored witness

The generated theory artifact stores the exact `k=2` witness and larger
regressions.  This is a structural counterexample, not a Collatz orbit.

## Open applicability obstruction

The accepted project models are not a prefix-complete closed finite graph for
the full H72 language.  Phase 7/8 free concatenations are overapproximations;
Phase 10/11/13 use growing state; Phase 14 is not left-closed by NG24; Phase 16
is a local sieve; and Phase 17 is an expanding sublanguage.  The finite-state
theorems therefore do not close H72.

## What this result does not prove

It does not construct a positive ordinary Collatz source, exclude all paths in
a mixed SCC, prove H72, exclude cycles, or prove the Collatz conjecture.
`proves_collatz=false`.
"""


def generate(artifact_dir: Path, root: Path | None = None) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    repository = root or Path(__file__).resolve().parents[1]
    theory = theory_artifact()
    graphs = graph_audit()
    mixed = mixed_schedule()
    projects = project_models(repository)
    adversarial = adversarial_artifact(projects)
    values = {
        "phase18_theory.json": theory,
        "phase18_graph_audit.json": graphs,
        "phase18_mixed_schedule.json": mixed,
        "phase18_project_models.json": projects,
        "phase18_adversarial.json": adversarial,
    }
    for name, value in values.items():
        write_json(artifact_dir / name, value)
    (artifact_dir / "phase18_obstruction_report.md").write_text(obstruction_report(), encoding="utf-8")
    return {
        "valid": True,
        "graphs": graphs["graphs_enumerated"],
        "type_counts": graphs["type_counts"],
        "mixed_blocks": mixed["blocks"],
        "adversarial_rows": len(adversarial["rows"]),
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    print(json.dumps(generate(args.artifact_dir), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
