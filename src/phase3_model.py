"""Exact mixed-modulus lattice model for Phase 3 search.

The independent verifier intentionally does not import this module.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Iterator


def ceil_div(a: int, b: int) -> int:
    if b <= 0:
        raise ValueError("divisor must be positive")
    return -((-a) // b)


def valuation(value: int, prime: int) -> int:
    if value <= 0 or prime <= 1:
        raise ValueError("valuation requires a positive value and prime > 1")
    exponent = 0
    while value % prime == 0:
        value //= prime
        exponent += 1
    return exponent


@dataclass(frozen=True, slots=True)
class LatticeNode:
    steps: int
    r: int
    M: int
    y: int
    A: int
    t_min: int
    parity: str = ""
    ternary_path: tuple[int, ...] = ()

    def __post_init__(self) -> None:
        if self.steps < 0 or self.M <= 0 or self.A <= 0:
            raise ValueError("invalid lattice coefficients")
        if self.r < 0 or self.y < 0:
            raise ValueError("Phase 3 nodes use non-negative affine constants")
        if len(self.parity) != self.steps:
            raise ValueError("parity metadata length differs from Collatz steps")
        if any(digit not in (0, 1, 2) for digit in self.ternary_path):
            raise ValueError("invalid ternary path")

    def values(self, t: int) -> tuple[int, int]:
        if t < self.t_min:
            raise ValueError("parameter outside node domain")
        return self.r + self.M * t, self.y + self.A * t

    @property
    def odd_capacity(self) -> int:
        return valuation(self.A, 3)

    def binary_split(self) -> tuple["LatticeNode", "LatticeNode"]:
        children: list[LatticeNode] = []
        for epsilon in (0, 1):
            r_child = self.r + epsilon * self.M
            z = self.y + epsilon * self.A
            bit = z % 2
            if bit == 0:
                y_child = z // 2
                a_child = self.A
            else:
                y_child = (3 * z + 1) // 2
                a_child = 3 * self.A
            children.append(
                LatticeNode(
                    self.steps + 1,
                    r_child,
                    2 * self.M,
                    y_child,
                    a_child,
                    ceil_div(self.t_min - epsilon, 2),
                    self.parity + str(bit),
                    self.ternary_path,
                )
            )
        return children[0], children[1]

    def ternary_children(self) -> Iterator["LatticeNode"]:
        """Yield children lazily in eta order; do not construct a 3**s batch."""

        for eta in (0, 1, 2):
            yield LatticeNode(
                self.steps,
                self.r + eta * self.M,
                3 * self.M,
                self.y + eta * self.A,
                3 * self.A,
                ceil_div(self.t_min - eta, 3),
                self.parity,
                self.ternary_path + (eta,),
            )

    def compact(self) -> list[object]:
        return [
            self.steps,
            self.r,
            self.M,
            self.y,
            self.A,
            self.t_min,
            self.parity,
            list(self.ternary_path),
        ]


@dataclass(frozen=True, slots=True)
class ReverseMergeWitness:
    exponents: tuple[int, ...]
    c: int
    S: int

    @property
    def odd_steps(self) -> int:
        return len(self.exponents)

    @property
    def exponent_sum(self) -> int:
        return sum(self.exponents)


def is_strict_smaller_positive(node: LatticeNode, c: int, slope: int) -> bool:
    if slope <= 0 or slope > node.M:
        return False
    if c + slope * node.t_min <= 0:
        return False
    return c - node.r + (slope - node.M) * node.t_min < 0


def find_reverse_merge(node: LatticeNode, *, extra_length: int = 8) -> ReverseMergeWitness | None:
    """Breadth-first exact search in (odd-step count, exponent sum, lexicographic) order."""

    max_odd_steps = node.odd_capacity
    exponent_limit = node.steps + extra_length
    queue: deque[tuple[int, int, int, tuple[int, ...]]] = deque(
        [(node.y, node.A, 0, ())]
    )
    while queue:
        constant, slope, exponent_sum, exponents = queue.popleft()
        odd_steps = len(exponents)
        if odd_steps and is_strict_smaller_positive(node, constant, slope):
            return ReverseMergeWitness(exponents, constant, slope)
        if (
            odd_steps >= max_odd_steps
            or exponent_sum >= exponent_limit
            or constant % 3 == 0
            or slope % 3 != 0
        ):
            continue

        parity = 1 if constant % 3 == 2 else 0
        first_b = 1 if parity else 2
        remaining_after = max_odd_steps - (odd_steps + 1)
        for b in range(first_b, exponent_limit - exponent_sum + 1, 2):
            next_slope = (1 << b) * slope // 3
            # Even under the optimistic choice b=1 for every remaining odd
            # predecessor, the slope must still be able to reach <= M.
            if next_slope * (1 << remaining_after) > node.M * pow(3, remaining_after):
                break
            numerator = (1 << b) * constant - 1
            if numerator % 3:
                raise AssertionError("reverse parity congruence was computed incorrectly")
            next_constant = numerator // 3
            if next_constant <= 0:
                continue
            queue.append(
                (
                    next_constant,
                    next_slope,
                    exponent_sum + b,
                    exponents + (b,),
                )
            )
    return None


def coefficient_survivors(depth: int) -> list[LatticeNode]:
    if depth < 0:
        raise ValueError("depth must be non-negative")
    result: list[LatticeNode] = []

    def visit(node: LatticeNode) -> None:
        if node.steps == depth:
            result.append(node)
            return
        for child in node.binary_split():
            if child.A >= child.M:
                visit(child)

    visit(LatticeNode(0, 0, 1, 0, 1, 2, "", ()))
    return result


def represented_minimum(node: LatticeNode) -> int:
    return node.r + node.M * node.t_min
