import math

from src.phase23_search import (
    defect_data,
    expanded_word,
    literal_swap_count,
    mechanical_word,
)


def factor_set(word: str, width: int) -> set[str]:
    return {word[start : start + width] for start in range(len(word) - width + 1)}


def test_supplied_sharp_factor_bound_has_minimal_boundary_counterexample() -> None:
    word, _ = mechanical_word(4)
    assert word == "1101100"
    assert defect_data(word, 4)[0] == 0
    assert factor_set(word, 2) == {"00", "01", "10", "11"}
    assert len(factor_set(word, 2)) == 4 > 3
    assert len(factor_set(word, 2)) <= 4  # corrected (A+1)(n+1)+1


def test_critical_area_is_prefix_excess_and_literal_swap_distance() -> None:
    word = "1111000"
    area, noncontacts, _, defects = defect_data(word, 4)
    assert defects == (0, 0, 1, 1)
    assert area == 2
    assert noncontacts <= area


def test_cycle_profile_swap_reconstruction_is_literal() -> None:
    baseline = expanded_word((2, 2, 1))
    target = expanded_word((3, 1, 1))
    assert baseline == "10101"
    assert target == "10011"
    assert literal_swap_count(baseline, target) == 1


def test_triangular_height_bound_arithmetic() -> None:
    for height in range(9):
        staircase = tuple(range(height + 1))
        assert sum(staircase) == height * (height + 1) // 2


def test_no_floating_point_in_phase23_acceptance_modules() -> None:
    import inspect
    import src.phase23_search as generator

    source = inspect.getsource(generator)
    assert "math.log" not in source
    assert "float(" not in source
    assert math.isfinite(1)
