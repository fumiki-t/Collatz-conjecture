from __future__ import annotations

import pytest

from src.model import shortcut_step


def parity_prefix(n: int, length: int) -> str:
    bits: list[str] = []
    value = n
    for _ in range(length):
        bits.append(str(value % 2))
        value = shortcut_step(value)
    return "".join(bits)


@pytest.mark.parametrize("m", list(range(1, 65)))
def test_minus_one_shadow_has_unbounded_odd_prefix(m: int) -> None:
    assert parity_prefix((1 << m) - 1, m) == "1" * m


@pytest.mark.parametrize("m", list(range(1, 33)))
def test_minus_five_cycle_shadow_repeats_110(m: int) -> None:
    assert parity_prefix((1 << (3 * m)) - 5, 3 * m) == "110" * m


@pytest.mark.parametrize("start", [1, 3, 7, 9, 27, 47, 63, 91, 97, 871, 6171])
def test_required_adversarial_starts_have_finite_direct_prefix(start: int) -> None:
    value = start
    for _ in range(10_000):
        if value == 1 or value < start:
            break
        value = shortcut_step(value)
    else:
        pytest.fail(f"no checked direct prefix for {start}")
    assert value == 1 or value < start
