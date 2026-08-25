from __future__ import annotations

from fractions import Fraction

from src.phase13_search import (
    above,
    append_block,
    codewords_by_q,
    critical_countermodel_artifact,
    first_crossing,
    pressure_dynamic_program,
    realizes_word,
    threshold_bridge_artifact,
    valuation_two,
    word_constant,
)


def test_first_upcrossing_orientation_prefix_free_and_multiplier() -> None:
    blocks = codewords_by_q(9)
    codes = sorted(block.code for block in blocks)
    assert all(first_crossing(code) for code in codes)
    assert all(not right.startswith(left) for left, right in zip(codes, codes[1:]))
    for block in blocks:
        assert Fraction(1) < Fraction(3**block.odd_count, 2**block.length) <= Fraction(3, 2)
        assert block.forward == block.code[::-1]
        assert block.correction == word_constant(block.forward)
        if block.forward != "1":
            assert block.forward.startswith("11")
            assert block.forward.endswith("0")


def test_pressure_partial_masses_obey_analytic_bounds() -> None:
    row = pressure_dynamic_program(128)["final"]
    for key, upper in (
        ("kappa", Fraction(3, 4)),
        ("sigma", Fraction(7, 12)),
        ("tau", Fraction(19, 96)),
        ("nu", Fraction(9, 32)),
    ):
        value = Fraction(int(row[key]["numerator"]), int(row[key]["denominator"]))
        assert value < upper
    assert Fraction(3, 2) * Fraction(7, 12) == Fraction(7, 8)
    assert Fraction(9, 4) * Fraction(19, 96) == Fraction(57, 128)


def test_threshold_Cw_valuation_and_positive_boundary_bridge() -> None:
    blocks = codewords_by_q(9)
    artifact = threshold_bridge_artifact(blocks)
    finite = artifact["finite_block_audit"]
    assert finite["R_13_over_9_words"] == ["110"]
    assert finite["q3_count"] == 0
    for block in blocks:
        R = Fraction(block.correction + 2**block.length, 3**block.odd_count)
        if block.forward == "1":
            assert R == 1
            continue
        C = (block.correction + 2**block.length - 3**block.odd_count) // 4
        run = len(block.forward) - len(block.forward.lstrip("1"))
        assert C >= 2 ** (block.length - 3)
        assert valuation_two(C) == run - 2
        assert (C == 2 ** (block.length - 3)) == (block.forward == "110")

        # Choose an exact lift whose source and endpoint are both 3 mod 4.
        base = append_block(None, block).source_residue
        candidates = [base + (2**block.length) * lift for lift in range(1, 9)]
        S = next(
            value
            for value in candidates
            if value % 4 == 3
            and realizes_word(value, block.forward)[0]
            and realizes_word(value, block.forward)[1] % 4 == 3
        )
        S_prime = realizes_word(S, block.forward)[1]
        U, U_prime = (S + 1) // 4, (S_prime + 1) // 4
        assert 2**block.length * U_prime == 3**block.odd_count * U + C
        assert valuation_two(U) == valuation_two(C)


def test_one_block_and_companion_ratio_identities() -> None:
    for U in range(2, 50, 2):
        S = 4 * U - 1
        S_prime = (3 * S + 1) // 2
        assert (S_prime + 1) // 4 == 3 * U // 2
        assert S_prime % 4 == 3
    for S in (3, 11, 27, 59):
        for R in (Fraction(13, 9), Fraction(43, 27), Fraction(443, 243)):
            h = R + Fraction(1, 7)
            ratio = (h - 1) / (S + 1)
            ratio_prime = (h - R) / (S + R)
            assert ratio - ratio_prime == (R - 1) * (S + h) / ((S + 1) * (S + R))
            assert 0 < ratio_prime < ratio


def test_square_root_countermodel_exact_prefix() -> None:
    artifact = critical_countermodel_artifact(512)
    finite = artifact["finite_audit"]
    assert finite["odd_steps"] == 512
    assert finite["final_E"] == finite["full_shortcut_length"]
    assert finite["latest_residue_change_index"] <= 512
    assert artifact["NG22_additional_evidence"]["positive_ordinary_source"] == "OPEN"
