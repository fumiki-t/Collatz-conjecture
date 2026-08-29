#!/usr/bin/env python3
"""Independent exact verifier for Phase 18 affine-trichotomy artifacts.

The verifier does not import the generator.  It reconstructs affine constants
by an explicit odd-position sum, finds SCCs by mutual reachability, and
enumerates the finite graph space in reverse before canonical sorting.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


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


def fraction(value: object) -> Fraction:
    if not isinstance(value, dict):
        fail("fraction object missing")
    try:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        fail(f"invalid fraction: {exc}")


def encoded(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def object_digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def explicit_affine(word: str) -> tuple[int, int, int]:
    if not word or set(word) - {"0", "1"}:
        fail("invalid parity word")
    odd_positions = [index for index, bit in enumerate(word) if bit == "1"]
    odd = len(odd_positions)
    affine = sum(
        pow(3, odd - 1 - rank) * pow(2, position)
        for rank, position in enumerate(odd_positions)
    )
    return len(word), odd, affine


def path_from_blocks(blocks: list[str]) -> dict[str, object]:
    word = "".join(blocks)
    length, odd, affine = explicit_affine(word)
    prefix = ""
    coefficients = []
    safe = True
    for block in blocks:
        prefix += block
        pre_length, pre_odd, _ = explicit_affine(prefix)
        coefficient = Fraction(pow(3, pre_odd), pow(2, pre_length))
        coefficients.append(encoded(coefficient))
        safe = safe and coefficient > 1
    modulus = pow(2, length)
    return {
        "word": word,
        "block_words": blocks,
        "L": length,
        "q": odd,
        "B": affine,
        "coefficient": encoded(Fraction(pow(3, odd), modulus)),
        "normalized_beta": encoded(Fraction(affine, pow(3, odd))),
        "prefix_coefficients": coefficients,
        "strictly_coefficient_safe": safe,
        "canonical_source_residue_mod_2L": (-affine * pow(pow(3, odd), -1, modulus)) % modulus,
    }


def reachable(vertices: int, edges: list[tuple[int, int, str]]) -> list[list[bool]]:
    matrix = [[a == b for b in range(vertices)] for a in range(vertices)]
    for source, target, _ in edges:
        matrix[source][target] = True
    for middle in range(vertices):
        for source in range(vertices):
            for target in range(vertices):
                matrix[source][target] = matrix[source][target] or (
                    matrix[source][middle] and matrix[middle][target]
                )
    return matrix


def components_by_reach(vertices: int, edges: list[tuple[int, int, str]]) -> list[list[int]]:
    matrix = reachable(vertices, edges)
    unused = set(range(vertices))
    components = []
    while unused:
        first = min(unused)
        component = sorted(item for item in unused if matrix[first][item] and matrix[item][first])
        unused.difference_update(component)
        components.append(component)
    return components


def cycle_signs(component: list[int], edges: list[tuple[int, int, str]]) -> set[int]:
    allowed = set(component)
    adjacency: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for source, target, word in edges:
        if source in allowed and target in allowed:
            adjacency[source].append((target, word))
    signs: set[int] = set()

    def visit(start: int, current: int, used: frozenset[int], words: tuple[str, ...]) -> None:
        for target, word in adjacency[current]:
            next_words = words + (word,)
            if target == start:
                length = odd = 0
                for item in next_words:
                    item_length, item_odd, _ = explicit_affine(item)
                    length += item_length
                    odd += item_odd
                signs.add(1 if pow(3, odd) > pow(2, length) else -1)
            elif target not in used:
                visit(start, target, used | {target}, next_words)

    for start in component:
        visit(start, start, frozenset({start}), ())
    return signs


def classify(vertices: int, edges: list[tuple[int, int, str]]) -> tuple[str, list[str], bool]:
    components = components_by_reach(vertices, edges)
    kinds = []
    vertex_component = {}
    for index, component in enumerate(components):
        for vertex in component:
            vertex_component[vertex] = index
        signs = cycle_signs(component, edges)
        if not signs:
            kinds.append("acyclic")
        elif signs == {1}:
            kinds.append("positive")
        elif signs == {-1}:
            kinds.append("negative")
        else:
            kinds.append("mixed")
    matrix = reachable(vertices, edges)
    witness = any(
        kinds[a] == "positive" and kinds[b] == "negative" and
        any(matrix[u][v] for u in components[a] for v in components[b])
        for a in range(len(components)) for b in range(len(components))
    )
    graph_type = "III" if "mixed" in kinds else ("II" if witness else "I")
    return graph_type, kinds, witness


def finite_paths(vertices: int, edges: list[tuple[int, int, str]], depth: int, cap: int) -> tuple[list[int], list[int]]:
    adjacency: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for source, target, word in edges:
        adjacency[source].append((target, word))
    states = [(vertex, 0, 0) for vertex in range(vertices)]
    all_counts, bounded_counts = [], []
    for _ in range(depth):
        following = []
        for vertex, odd, length in states:
            for target, word in adjacency[vertex]:
                edge_length, edge_odd, _ = explicit_affine(word)
                new_odd, new_length = odd + edge_odd, length + edge_length
                if pow(3, new_odd) > pow(2, new_length):
                    following.append((target, new_odd, new_length))
        states = following
        all_counts.append(len(states))
        bounded_counts.append(sum(pow(3, odd) <= cap * pow(2, length) for _, odd, length in states))
    return all_counts, bounded_counts


def expected_graph_rows(max_vertices: int, depth: int, cap: int) -> list[dict[str, object]]:
    indexed: list[tuple[tuple[int, tuple[int, ...]], dict[str, object]]] = []
    for vertices in range(max_vertices, 0, -1):
        values = list(range(-1, vertices))
        for choices in itertools.product(reversed(values), repeat=2 * vertices):
            edges = []
            for source in range(vertices):
                for offset, word in enumerate(("0", "1")):
                    target = choices[2 * source + offset]
                    if target >= 0:
                        edges.append((source, target, word))
            graph_type, kinds, witness = classify(vertices, edges)
            safe, bounded = finite_paths(vertices, edges, depth, cap)
            row = {
                "signature": f"v{vertices}:" + ",".join(str(value) for value in choices),
                "type": graph_type,
                "component_kinds": kinds,
                "positive_to_negative": witness,
                "safe_path_counts": safe,
                "safe_final_multiplier_at_most_cap": bounded,
            }
            indexed.append(((vertices, choices), row))
    indexed.sort(key=lambda pair: pair[0])
    return [row for _, row in indexed]


def verify_theory(root: Path) -> None:
    value = load(root / "phase18_theory.json")
    expected_claims = {
        "P107": "VERIFIED_THEOREM", "P108": "VERIFIED_THEOREM",
        "P109": "VERIFIED_THEOREM", "P110": "CONDITIONAL",
        "P111": "VERIFIED_THEOREM", "NG30": "REFUTED", "H72": "OPEN",
    }
    if value.get("claims") != expected_claims or value.get("proves_collatz") is not False:
        fail("theory claim boundary")
    if "finite condensation" not in str(value.get("P107", {}).get("proof_invariant", "")):
        fail("P107 proof invariant")
    if "need not be one" not in str(value.get("P108", {}).get("corrected_normal_form", "")):
        fail("P108 corrected normal form")
    repairs = value.get("P109", {}).get("construction_repairs", [])
    if len(repairs) != 4 or "H>1/(m_B*c_B)" not in repairs[2]:
        fail("P109 threshold repair")
    if value.get("P110", {}).get("scope") != "This does not exclude every itinerary through a mixed SCC.":
        fail("P110 conditional scope")
    stored = value.get("NG30", {}).get("counterexamples")
    if not isinstance(stored, list):
        fail("NG30 counterexamples")
    expected = []
    for k in (2, 3, 4, 8, 16, 32):
        n1 = pow(3, k).bit_length() - 1 - k
        positive = 4 * k + 3
        total_negative = pow(3, positive).bit_length() - 1 - positive
        n2 = total_negative - n1
        blocks = ["1" * (2 * k + 1), "0" * n1, "1" * (2 * k + 2), "0" * n2]
        path = path_from_blocks(blocks)
        if not path["strictly_coefficient_safe"] or not 1 < fraction(path["coefficient"]) < 2:
            fail("NG30 literal construction")
        expected.append({
            "k": k, "stage_lengths": [2 * k + 1, n1, 2 * k + 2, n2],
            "stage_signs": ["positive", "negative", "positive", "negative"],
            "path": path,
        })
    if stored != expected:
        fail("NG30 exact counterfamily")


def verify_graph_audit(root: Path) -> None:
    value = load(root / "phase18_graph_audit.json")
    max_vertices = int(value.get("maximum_vertices", 0))
    depth = int(value.get("safe_path_depth", 0))
    cap = int(value.get("final_multiplier_cap", 0))
    if (max_vertices, depth, cap) != (3, 12, 4):
        fail("graph audit bounds")
    rows = expected_graph_rows(max_vertices, depth, cap)
    counts = Counter(row["type"] for row in rows)
    by_vertices: dict[str, Counter[str]] = {}
    for vertices in range(1, max_vertices + 1):
        by_vertices[str(vertices)] = Counter(row["type"] for row in rows if row["signature"].startswith(f"v{vertices}:"))
    if value.get("row_storage") != "omitted; the independent verifier exhaustively reconstructs the canonical rows from the declared graph class":
        fail("graph audit storage boundary")
    if value.get("graphs_enumerated") != len(rows) or value.get("graphs_enumerated") != 4181:
        fail("graph audit count")
    if value.get("type_counts") != dict(sorted(counts.items())):
        fail("graph audit type counts")
    expected_by = {key: dict(sorted(count.items())) for key, count in by_vertices.items()}
    if value.get("type_counts_by_vertices") != expected_by:
        fail("graph audit vertex layers")
    if value.get("row_digest_sha256") != object_digest(rows):
        fail("graph audit digest")
    if value.get("claim") != {"E30": "VERIFIED_FINITE"} or value.get("proves_collatz") is not False:
        fail("graph finite claim boundary")


def verify_mixed(root: Path) -> None:
    value = load(root / "phase18_mixed_schedule.json")
    blocks, threshold = int(value.get("blocks", 0)), int(value.get("threshold", 0))
    if (blocks, threshold) != (512, 8):
        fail("mixed schedule bounds")
    odd = length = affine = 0
    old_residue, old_modulus = 0, 1
    words, rows, lifts, checkpoints = [], [], [], []
    for index in range(blocks):
        word = "1" if pow(3, odd) <= threshold * pow(2, length) else "0"
        if word == "1":
            affine = 3 * affine + pow(2, length)
            odd += 1
        length += 1
        modulus = pow(2, length)
        residue = (-affine * pow(pow(3, odd), -1, modulus)) % modulus
        lift = (residue - old_residue) // old_modulus
        if lift not in (0, 1):
            fail("mixed source lift")
        row = {
            "index": index + 1, "word": word, "q": odd, "L": length, "B": affine,
            "source_residue": residue, "lift": lift,
            "coefficient": encoded(Fraction(pow(3, odd), modulus)),
            "normalized_beta": encoded(Fraction(affine, pow(3, odd))),
        }
        rows.append(row)
        lifts.append(lift)
        words.append(word)
        if index + 1 in {1, 2, 4, 8, 16, 32, 64, 128, 256, blocks}:
            checkpoints.append(row)
        old_residue, old_modulus = residue, modulus
    if value.get("final") != rows[-1] or value.get("checkpoint_rows") != checkpoints:
        fail("mixed schedule reconstruction")
    if value.get("positive_blocks") != words.count("1") or value.get("negative_blocks") != words.count("0"):
        fail("mixed schedule counts")
    if value.get("row_digest_sha256") != object_digest(rows) or value.get("lift_digest_sha256") != object_digest(lifts):
        fail("mixed schedule digest")
    if value.get("nonzero_lifts") != sum(item != 0 for item in lifts):
        fail("mixed lift count")
    if fraction(value.get("symbolic_linear_beta_lower_bound")) != Fraction(words.count("1"), 3 * threshold):
        fail("mixed beta lower bound")
    if "do not prove" not in str(value.get("finite_boundary", "")) or value.get("proves_collatz") is not False:
        fail("mixed finite boundary")


PROJECT_FILES = [
    "artifacts/phase7_macro12.json", "artifacts/phase8_ab_semigroup_search.json",
    "artifacts/phase13_critical_countermodel.json", "artifacts/phase14_coalescent_theory.json",
    "artifacts/phase16_theory.json", "artifacts/phase17_suffix_code.json",
]


def verify_projects(artifact_root: Path, repository: Path) -> dict[str, object]:
    value = load(artifact_root / "phase18_project_models.json")
    hashes = {name: file_digest(repository / name) for name in PROJECT_FILES}
    if value.get("source_file_sha256") != hashes:
        fail("project model source digests")
    models = value.get("models")
    if not isinstance(models, list) or len(models) != 7:
        fail("project model rows")
    expected_classes = [
        "NOT_AN_EXACT_FINITE_GRAPH", "TYPE_III_OVERAPPROXIMATION", "NOT_FIXED_FINITE",
        "FORMAL_UNBOUNDED_STATE", "NOT_CLOSED", "NOT_A_CLOSED_AUTOMATON", "TYPE_I_SUBLANGUAGE",
    ]
    if [row.get("classification") for row in models] != expected_classes:
        fail("project model classifications")
    phase7 = load(repository / PROJECT_FILES[0])
    records = phase7.get("records")
    if not isinstance(records, list) or len(records) != 87015:
        fail("phase7 project input")
    signs = Counter("positive" if int(row[6]) > int(row[8]) else "negative" for row in records)
    observed = models[0].get("observed", {})
    if observed.get("coefficient_signs") != dict(signs) or observed.get("macro0") != path_from_blocks([str(records[0][3])]):
        fail("phase7 project reconstruction")
    phase17 = load(repository / PROJECT_FILES[-1])
    code_signs = Counter()
    for row in phase17.get("codewords", []):
        code_signs["positive" if fraction(row.get("multiplier")) > 1 else "negative"] += 1
    if models[-1].get("observed") != {"code_size": phase17.get("code_size"), "coefficient_signs": dict(code_signs)}:
        fail("phase17 project reconstruction")
    if "No accepted artifact" not in str(value.get("conclusion", "")) or value.get("proves_collatz") is not False:
        fail("project applicability boundary")
    return value


def verify_adversarial(artifact_root: Path, projects: dict[str, object]) -> None:
    value = load(artifact_root / "phase18_adversarial.json")
    rows = value.get("rows")
    if not isinstance(rows, list) or len(rows) != 74:
        fail("adversarial row count")
    for row in rows:
        word = row.get("word")
        if not isinstance(word, str):
            fail("adversarial word")
        if row.get("kind") == "literal_orbit":
            try:
                orbit_value, horizon = int(row["start"]), int(row["horizon"])
            except (KeyError, TypeError, ValueError) as exc:
                fail(f"adversarial literal parameters: {exc}")
            bits = []
            for _ in range(horizon):
                bit = orbit_value % 2
                bits.append(str(bit))
                orbit_value = (3 * orbit_value + 1) // 2 if bit else orbit_value // 2
            if word != "".join(bits):
                fail("adversarial literal orbit")
        elif row.get("kind") != "formal_word":
            fail("adversarial row kind")
        expected = path_from_blocks([word])
        critical = {
            "coefficient": expected["coefficient"],
            "normalized_beta": expected["normalized_beta"],
            "strictly_coefficient_safe": expected["strictly_coefficient_safe"],
            "source_residue": expected["canonical_source_residue_mod_2L"],
        }
        if any(row.get(key) != item for key, item in critical.items()):
            fail("adversarial affine row")
    if value.get("row_digest_sha256") != object_digest(rows):
        fail("adversarial digest")
    if value.get("macro0") != projects["models"][0]["observed"]["macro0"]:
        fail("macro 0 regression")
    expected_obstructions = {"NG02", "NG17", "NG19", *{f"NG{i}" for i in range(21, 30)}}
    if set(value.get("preserved_obstruction_scope", {})) != expected_obstructions:
        fail("adversarial obstruction set")
    if value.get("proves_collatz") is not False:
        fail("adversarial claim boundary")


def verify_obstruction(root: Path) -> None:
    try:
        text = (root / "phase18_obstruction_report.md").read_text(encoding="utf-8")
    except OSError as exc:
        fail(f"obstruction report: {exc}")
    required = [
        "NG30 — single-mountain SCC normal form (`REFUTED`)",
        "positive, negative,\npositive, negative",
        "finite-stage normal form",
        "not a Collatz orbit",
        "`proves_collatz=false`",
    ]
    if any(item not in text for item in required) or "NG30 — single-mountain SCC normal form (`VERIFIED_THEOREM`)" in text:
        fail("obstruction report boundary")


def verify(artifact_dir: Path, repository: Path | None = None) -> dict[str, object]:
    repo = repository or Path(__file__).resolve().parents[1]
    verify_theory(artifact_dir)
    verify_graph_audit(artifact_dir)
    verify_mixed(artifact_dir)
    projects = verify_projects(artifact_dir, repo)
    verify_adversarial(artifact_dir, projects)
    verify_obstruction(artifact_dir)
    return {
        "format": "collatz-phase18-verifier-v1",
        "valid": True,
        "claims": {
            "P107": "VERIFIED_THEOREM", "P108": "VERIFIED_THEOREM",
            "P109": "VERIFIED_THEOREM", "P110": "CONDITIONAL",
            "P111": "VERIFIED_THEOREM", "E30": "VERIFIED_FINITE",
            "NG30": "REFUTED", "H72": "OPEN",
        },
        "independence": {
            "generator_imported": False,
            "affine_method": "explicit odd-position sum",
            "SCC_method": "mutual reachability",
            "graph_enumeration": "reverse product followed by canonical tuple sort",
        },
        "graphs_recomputed": 4181,
        "mixed_blocks_recomputed": 512,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except ValueError as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        return 1
    if args.write_report:
        args.write_report.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
