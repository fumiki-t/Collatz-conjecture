"""Exact integer model used by the Phase 1 searcher.

This module deliberately contains no claim about the Collatz conjecture.  It
only implements finite affine-cylinder calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction


def ceil_div(a: int, b: int) -> int:
    """Return ceil(a / b) using integers only (b must be positive)."""

    if b <= 0:
        raise ValueError("the divisor must be positive")
    return -((-a) // b)


def shortcut_step(n: int) -> int:
    if n <= 0:
        raise ValueError("the shortcut Collatz map is defined here for n > 0")
    return n // 2 if n % 2 == 0 else (3 * n + 1) // 2


def direct_witness(n: int, *, max_steps: int = 100_000) -> tuple[int, int]:
    """Return (step_count, endpoint) for a prefix ending below n or at 1."""

    if n <= 0:
        raise ValueError("n must be positive")
    value = n
    for steps in range(max_steps + 1):
        if steps > 0 and (value < n or value == 1):
            return steps, value
        value = shortcut_step(value)
    raise RuntimeError(f"no direct witness for {n} within {max_steps} steps")


@dataclass(frozen=True, slots=True)
class Node:
    k: int
    r: int
    y: int
    q: int
    parity: str = ""

    def __post_init__(self) -> None:
        if self.k < 0 or not 0 <= self.r < 1 << self.k:
            raise ValueError("invalid affine-cylinder residue")
        if self.q < 0 or len(self.parity) != self.k:
            raise ValueError("invalid parity metadata")

    @property
    def input_stride(self) -> int:
        return 1 << self.k

    @property
    def output_slope(self) -> int:
        return 3**self.q

    @property
    def t_min(self) -> int:
        return max(0, ceil_div(2 - self.r, self.input_stride))

    @property
    def descent_slope(self) -> int:
        return self.output_slope - self.input_stride

    @property
    def descent_intercept(self) -> int:
        return self.y - self.r

    def value_at(self, t: int) -> tuple[int, int]:
        if t < self.t_min:
            raise ValueError("parameter lies outside the positive-integer domain")
        return self.r + self.input_stride * t, self.y + self.output_slope * t

    def has_uniform_descent(self) -> bool:
        slope = self.descent_slope
        return slope < 0 and self.descent_intercept + slope * self.t_min < 0

    def finite_tail_high(self) -> int | None:
        if self.input_stride <= self.output_slope:
            return None
        return self.descent_intercept // (self.input_stride - self.output_slope)

    def split(self) -> tuple["Node", "Node"]:
        children: list[Node] = []
        a = self.output_slope
        b = self.input_stride
        for epsilon in (0, 1):
            r_child = self.r + epsilon * b
            z = self.y + epsilon * a
            parity_bit = z % 2
            if parity_bit == 0:
                y_child = z // 2
                q_child = self.q
            else:
                y_child = (3 * z + 1) // 2
                q_child = self.q + 1
            children.append(
                Node(
                    self.k + 1,
                    r_child,
                    y_child,
                    q_child,
                    self.parity + str(parity_bit),
                )
            )
        return children[0], children[1]

    def compact(self) -> list[int | str]:
        return [self.k, self.r, self.y, self.q, self.parity]


def affine_word(word: str) -> tuple[int, int, int, int]:
    """Return (L, q, P, B) for W(x)=(P*x+B)/2**L."""

    p = 1
    b = 0
    q = 0
    denominator = 1
    for bit in word:
        if bit not in "01":
            raise ValueError("a parity word may contain only 0 and 1")
        if bit == "1":
            p *= 3
            b = 3 * b + denominator
            q += 1
        denominator *= 2
    return len(word), q, p, b


def rational_fixed_point(word: str) -> Fraction | None:
    length, _q, p, b = affine_word(word)
    denominator = (1 << length) - p
    return None if denominator == 0 else Fraction(b, denominator)
