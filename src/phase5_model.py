"""Exact mod-27 bounded-return model for Phase 5."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import gcd


MODULUS = 27
UNITS = tuple(residue for residue in range(1, MODULUS) if gcd(residue, 3) == 1)
SECTION = (1, 11, 20, 26)
SECTION_SET = frozenset(SECTION)
DANGEROUS_FORMS = {
    "C1": (1, 1),
    "C7": (1, 7),
    "C23": (11, 23),
    "C146": (17, 146),
}
DANGEROUS_CYCLES = {
    "1": Fraction(-1, 1),
    "101": Fraction(-7, 1),
    "1101": Fraction(-23, 11),
    "011101": Fraction(-146, 17),
}


def shortcut_step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def colored_target(residue: int, bit: int) -> int:
    if residue not in UNITS or bit not in (0, 1):
        raise ValueError("invalid colored mod-27 edge")
    representative = residue if residue % 2 == bit else residue + MODULUS
    return shortcut_step(representative) % MODULUS


def colored_graph() -> dict[int, dict[int, int]]:
    return {
        residue: {bit: colored_target(residue, bit) for bit in (0, 1)}
        for residue in UNITS
    }


@dataclass(frozen=True, slots=True)
class AffineMap:
    A: int
    B: int
    k: int
    q: int

    @property
    def denominator(self) -> int:
        return 1 << self.k

    @property
    def multiplier(self) -> Fraction:
        return Fraction(self.A, self.denominator)

    @property
    def fixed_point(self) -> Fraction | None:
        difference = self.denominator - self.A
        return None if difference == 0 else Fraction(self.B, difference)

    def apply(self, value: int) -> int:
        numerator = self.A * value + self.B
        if numerator % self.denominator:
            raise ValueError("affine word is not integral on this value")
        return numerator // self.denominator

    def compact(self) -> dict[str, object]:
        fixed = self.fixed_point
        return {
            "k": self.k,
            "q": self.q,
            "A": self.A,
            "B": self.B,
            "denominator": self.denominator,
            "multiplier": [self.A, self.denominator],
            "fixed_point": None if fixed is None else [fixed.numerator, fixed.denominator],
        }


def affine_word(word: str) -> AffineMap:
    coefficient = 1
    constant = 0
    denominator = 1
    odd_steps = 0
    for raw_bit in word:
        if raw_bit not in "01":
            raise ValueError("parity word must be binary")
        if raw_bit == "1":
            coefficient *= 3
            constant = 3 * constant + denominator
            odd_steps += 1
        denominator *= 2
    return AffineMap(coefficient, constant, len(word), odd_steps)


def compose_affine(first: AffineMap, second: AffineMap) -> AffineMap:
    """Return second(first(x))."""
    return AffineMap(
        second.A * first.A,
        second.A * first.B + second.B * first.denominator,
        first.k + second.k,
        first.q + second.q,
    )


def parity_residue(word: str) -> int:
    """Unique starting residue modulo 2^len(word) with this shortcut word."""
    coefficient = 1
    constant = 0
    result = 0
    for index, raw_bit in enumerate(word):
        bit = int(raw_bit)
        modulus = 1 << (index + 1)
        result = ((bit << index) - constant) * pow(coefficient, -1, modulus) % modulus
        if bit:
            coefficient *= 3
            constant = 3 * constant + (1 << index)
    return result


def cylinder_family(source_residue: int, word: str) -> tuple[int, int]:
    power = 1 << len(word)
    parity_class = parity_residue(word)
    parameter = (source_residue - parity_class) * pow(power, -1, MODULUS) % MODULUS
    return parity_class + power * parameter, MODULUS * power


@dataclass(frozen=True, slots=True)
class ReturnTemplate:
    source_residue: int
    target_residue: int
    word: str
    path: tuple[int, ...]
    affine: AffineMap
    source_base: int
    source_step: int
    target_base: int
    target_step: int

    @property
    def name(self) -> str:
        return f"r{self.source_residue}-to-r{self.target_residue}-{self.word}"

    def compact(self) -> dict[str, object]:
        value = {
            "name": self.name,
            "source_residue": self.source_residue,
            "target_residue": self.target_residue,
            "word": self.word,
            "path": list(self.path),
            "source_family": [self.source_base, self.source_step],
            "target_family": [self.target_base, self.target_step],
        }
        value.update(self.affine.compact())
        return value


def enumerate_return_templates() -> list[ReturnTemplate]:
    graph = colored_graph()
    rows: list[ReturnTemplate] = []

    def visit(source: int, residue: int, word: str, path: tuple[int, ...]) -> None:
        for bit in (0, 1):
            target = graph[residue][bit]
            next_word = word + str(bit)
            next_path = path + (target,)
            if target in SECTION_SET:
                affine = affine_word(next_word)
                source_base, source_step = cylinder_family(source, next_word)
                target_numerator = affine.A * source_base + affine.B
                if target_numerator % affine.denominator:
                    raise AssertionError("template endpoint is non-integral")
                target_base = target_numerator // affine.denominator
                rows.append(
                    ReturnTemplate(
                        source,
                        target,
                        next_word,
                        next_path,
                        affine,
                        source_base,
                        source_step,
                        target_base,
                        MODULUS * affine.A,
                    )
                )
            else:
                if target in path:
                    raise AssertionError("section-deleted graph contains a cycle")
                visit(source, target, next_word, next_path)

    for source in SECTION:
        visit(source, source, "", (source,))
    return sorted(rows, key=lambda row: (row.source_residue, row.word, row.target_residue))


def first_return_to_section(value: int, *, limit: int = 100) -> tuple[int, str, tuple[int, ...]]:
    if value % MODULUS not in SECTION_SET:
        raise ValueError("start is outside the four-residue section")
    current = value
    word: list[str] = []
    path = [value % MODULUS]
    for _ in range(limit):
        word.append(str(current % 2))
        current = shortcut_step(current)
        path.append(current % MODULUS)
        if current % MODULUS in SECTION_SET:
            return current, "".join(word), tuple(path)
    raise RuntimeError("first return exceeded the explicit limit")


def topological_audit() -> dict[str, object]:
    graph = colored_graph()
    internal = set(UNITS) - SECTION_SET
    indegree = {residue: 0 for residue in internal}
    for source in internal:
        for target in graph[source].values():
            if target in internal:
                indegree[target] += 1
    queue = sorted(residue for residue, degree in indegree.items() if degree == 0)
    order: list[int] = []
    while queue:
        source = queue.pop(0)
        order.append(source)
        for target in graph[source].values():
            if target not in internal:
                continue
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    if len(order) != len(internal):
        raise AssertionError("section-deleted graph is cyclic")
    longest = {residue: 0 for residue in internal}
    for source in order:
        for target in graph[source].values():
            if target in internal:
                longest[target] = max(longest[target], longest[source] + 1)
    return {
        "deleted_vertices": list(SECTION),
        "remaining_vertices": sorted(internal),
        "topological_order": order,
        "acyclic": True,
        "maximum_internal_edges": max(longest.values()),
        "maximum_first_return_length": max(len(row.word) for row in enumerate_return_templates()),
    }


def rotate_cycle(
    nodes: tuple[int, ...], bits: tuple[int, ...], offset: int
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return nodes[offset:] + nodes[:offset], bits[offset:] + bits[:offset]


def canonical_cycle_key(nodes: tuple[int, ...], bits: tuple[int, ...]) -> tuple[tuple[int, int], ...]:
    return min(
        tuple(zip(*rotate_cycle(nodes, bits, offset), strict=True))
        for offset in range(len(bits))
    )


def enumerate_simple_cycles() -> list[dict[str, object]]:
    graph = colored_graph()
    unique: dict[tuple[tuple[int, int], ...], tuple[tuple[int, ...], tuple[int, ...]]] = {}
    for start in UNITS:
        def visit(residue: int, nodes: tuple[int, ...], bits: tuple[int, ...]) -> None:
            for bit in (0, 1):
                target = graph[residue][bit]
                if target == start:
                    cycle_bits = bits + (bit,)
                    key = canonical_cycle_key(nodes, cycle_bits)
                    unique.setdefault(key, (nodes, cycle_bits))
                elif target not in nodes:
                    visit(target, nodes + (target,), bits + (bit,))

        visit(start, (start,), ())

    rows: list[dict[str, object]] = []
    for key, (raw_nodes, raw_bits) in unique.items():
        selected: tuple[tuple[int, ...], tuple[int, ...]] | None = None
        dangerous_name: str | None = None
        for offset in range(len(raw_bits)):
            nodes, bits = rotate_cycle(raw_nodes, raw_bits, offset)
            word = "".join(map(str, bits))
            if word in DANGEROUS_CYCLES and affine_word(word).fixed_point == DANGEROUS_CYCLES[word]:
                selected = nodes, bits
                dangerous_name = word
                break
        if selected is None:
            pairs = min(
                (
                    tuple(zip(*rotate_cycle(raw_nodes, raw_bits, offset), strict=True)),
                    rotate_cycle(raw_nodes, raw_bits, offset),
                )
                for offset in range(len(raw_bits))
            )
            selected = pairs[1]
        nodes, bits = selected
        word = "".join(map(str, bits))
        affine = affine_word(word)
        row = {
            "nodes": list(nodes),
            "word": word,
            "canonical_edge_key": [list(pair) for pair in key],
            "dangerous_rotation": dangerous_name,
            "noncontracting": affine.A >= affine.denominator,
        }
        row.update(affine.compact())
        rows.append(row)
    return sorted(
        rows,
        key=lambda row: (len(str(row["word"])), str(row["word"]), tuple(row["nodes"])),
    )


def v2(value: int) -> int:
    if value == 0:
        raise ValueError("v2(0) is unbounded")
    positive = abs(value)
    return (positive & -positive).bit_length() - 1


def shadow_values(value: int) -> dict[str, int]:
    return {name: v2(coefficient * value + constant) for name, (coefficient, constant) in DANGEROUS_FORMS.items()}
