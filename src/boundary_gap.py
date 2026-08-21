"""Exact meet-in-the-middle audit of the boundary-gap hypothesis."""

from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from dataclasses import dataclass

from src.phase3_model import LatticeNode, coefficient_survivors


def coefficient_threshold(depth: int) -> int:
    q = 0
    while pow(3, q) < 1 << depth:
        q += 1
    return q


@dataclass(frozen=True, slots=True)
class Suffix:
    residue: int
    affine_constant: int
    word: str


def suffix_groups(first_length: int, suffix_length: int) -> dict[tuple[int, int], list[Suffix]]:
    """Enumerate every suffix word and its exact global-prefix requirement."""

    groups: dict[tuple[int, int], list[Suffix]] = defaultdict(list)
    modulus = 1 << suffix_length

    def visit(
        length: int,
        odd_count: int,
        affine_constant: int,
        word: str,
        required_initial_odds: int,
    ) -> None:
        if length == suffix_length:
            if modulus == 1:
                residue = 0
            else:
                multiplier = pow(3, odd_count)
                residue = (-affine_constant * pow(multiplier, -1, modulus)) % modulus
            groups[(odd_count, required_initial_odds)].append(
                Suffix(residue, affine_constant, word)
            )
            return
        next_depth = first_length + length + 1
        for bit in (0, 1):
            next_odds = odd_count + bit
            next_constant = (
                affine_constant
                if bit == 0
                else 3 * affine_constant + (1 << length)
            )
            requirement = max(
                required_initial_odds,
                coefficient_threshold(next_depth) - next_odds,
            )
            visit(
                length + 1,
                next_odds,
                next_constant,
                word + str(bit),
                requirement,
            )

    visit(0, 0, 0, "", -1)
    return groups


@dataclass(frozen=True, slots=True)
class IndexedSuffix:
    x: int
    base_value: int
    suffix: Suffix


class ModularMinimumIndex:
    """Exact range-min index for C*((a*d+b) mod N)-B."""

    def __init__(self, suffixes: list[Suffix], a: int, modulus: int, coefficient: int) -> None:
        self.modulus = modulus
        self.coefficient = coefficient
        self.rows = sorted(
            (
                IndexedSuffix(
                    (a * suffix.residue) % modulus,
                    coefficient * ((a * suffix.residue) % modulus)
                    - suffix.affine_constant,
                    suffix,
                )
                for suffix in suffixes
            ),
            key=lambda row: (row.x, row.base_value, row.suffix.word),
        )
        self.xs = [row.x for row in self.rows]
        self.prefix: list[IndexedSuffix] = []
        best: IndexedSuffix | None = None
        for row in self.rows:
            if best is None or (row.base_value, row.suffix.word) < (
                best.base_value,
                best.suffix.word,
            ):
                best = row
            self.prefix.append(best)
        self.suffix: list[IndexedSuffix] = [self.rows[0]] * len(self.rows)
        best = None
        for index in range(len(self.rows) - 1, -1, -1):
            row = self.rows[index]
            if best is None or (row.base_value, row.suffix.word) < (
                best.base_value,
                best.suffix.word,
            ):
                best = row
            self.suffix[index] = best

    def query(self, shift: int) -> tuple[int, IndexedSuffix]:
        cutoff = self.modulus - shift
        index = bisect_left(self.xs, cutoff)
        options: list[tuple[int, str, IndexedSuffix]] = []
        if index:
            row = self.prefix[index - 1]
            options.append(
                (
                    row.base_value + self.coefficient * shift,
                    row.suffix.word,
                    row,
                )
            )
        if index < len(self.rows):
            row = self.suffix[index]
            options.append(
                (
                    row.base_value
                    + self.coefficient * (shift - self.modulus),
                    row.suffix.word,
                    row,
                )
            )
        value, _word, row = min(options)
        return value, row


def boundary_gap_minimum(parent_depth: int) -> dict[str, object]:
    """Return the exact minimum over every admissible boundary parent word."""

    target_odds = coefficient_threshold(parent_depth)
    multiplier = pow(3, target_odds)
    if not ((1 << parent_depth) <= multiplier < (1 << (parent_depth + 1))):
        raise ValueError("this depth has no coefficient boundary on its even child")

    first_length = parent_depth // 2
    suffix_length = parent_depth - first_length
    modulus = 1 << suffix_length
    first_nodes = coefficient_survivors(first_length)
    grouped_firsts: dict[int, list[LatticeNode]] = defaultdict(list)
    for node in first_nodes:
        grouped_firsts[node.odd_capacity].append(node)
    grouped_suffixes = suffix_groups(first_length, suffix_length)
    coefficient = (1 << (parent_depth + 1)) - multiplier

    candidate_count = 0
    best: tuple[int, str, int, int, int] | None = None
    for first_odds, nodes in sorted(grouped_firsts.items()):
        suffix_odds = target_odds - first_odds
        candidates = [
            suffix
            for (odd_count, requirement), group in grouped_suffixes.items()
            if odd_count == suffix_odds and requirement <= first_odds
            for suffix in group
        ]
        candidate_count += len(nodes) * len(candidates)
        if not candidates:
            continue
        inverse_first_slope = pow(pow(3, first_odds), -1, modulus)
        index = ModularMinimumIndex(
            candidates, inverse_first_slope, modulus, coefficient
        )
        suffix_multiplier = pow(3, suffix_odds)
        for node in nodes:
            shift = (-inverse_first_slope * node.y) % modulus
            indexed_value, indexed = index.query(shift)
            parameter_residue = (indexed.x + shift) % modulus
            r = node.r + (1 << first_length) * parameter_residue
            numerator = (
                suffix_multiplier
                * (node.y + pow(3, first_odds) * parameter_residue)
                + indexed.suffix.affine_constant
            )
            if numerator % modulus:
                raise AssertionError("suffix affine image is non-integral")
            y = numerator // modulus
            gap = 2 * r - y
            expected_scaled_gap = (
                2 * modulus * node.r
                - suffix_multiplier * node.y
                + indexed_value
            )
            if gap * modulus != expected_scaled_gap:
                raise AssertionError("range-min reconstruction mismatch")
            word = node.parity + indexed.suffix.word
            candidate = (gap, word, r, y, target_odds)
            if best is None or candidate < best:
                best = candidate
    if best is None:
        raise AssertionError("boundary candidate set unexpectedly empty")
    gap, word, r, y, q = best
    epsilon = y % 2
    margin = gap + epsilon * ((1 << (parent_depth + 1)) - pow(3, q))
    return {
        "boundary_depth": parent_depth + 1,
        "parent_depth": parent_depth,
        "odd_steps": q,
        "candidate_words": candidate_count,
        "minimum_gap": gap,
        "r": r,
        "y": y,
        "word": word,
        "even_child_selector": epsilon,
        "uniform_descent_margin": margin,
        "method": "exact_meet_in_the_middle_range_minimum",
        "domain": "t_min=0 boundary parents",
    }


def audit_boundary_gaps(max_boundary_depth: int) -> dict[str, object]:
    if max_boundary_depth < 1:
        raise ValueError("max boundary depth must be positive")
    rows: list[dict[str, object]] = []
    counterexample: dict[str, object] | None = None
    # Depths 0 and 1 have t_min>0 root-domain exceptions (r=0 and r=1).
    # The boundary-margin formula at t=0 is not the actual domain margin there.
    for parent_depth in range(2, max_boundary_depth):
        q = coefficient_threshold(parent_depth)
        if pow(3, q) >= 1 << (parent_depth + 1):
            continue
        row = boundary_gap_minimum(parent_depth)
        rows.append(row)
        if int(row["minimum_gap"]) <= 0 and counterexample is None:
            counterexample = row
    return {
        "format": "collatz-boundary-gap-minima-v1",
        "max_boundary_depth": max_boundary_depth,
        "exhaustive": True,
        "uses_beam_search": False,
        "hypothesis": "2*r-y > 0 at coefficient boundary parents",
        "domain": "t_min=0; the two positive-t_min root exceptions are excluded",
        "counterexample": counterexample,
        "minima": rows,
        "claim_scope": "finite exhaustive search only; not a theorem",
    }
