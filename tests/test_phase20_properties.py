from fractions import Fraction

from src.phase20_search import (
    all_contact_word,
    interval_controller_word,
    rolling_factor_metrics,
    safety_horizon,
    source_lifts,
    square_root_word,
)


def test_formal_controllers_are_safe_on_declared_prefix() -> None:
    for word in (all_contact_word(512), square_root_word(512), interval_controller_word(512)):
        assert safety_horizon(word)["strict_safe_steps"] == 512


def test_abelian_complexity_is_balance_plus_one() -> None:
    words = [all_contact_word(128), square_root_word(128), interval_controller_word(128)]
    for word in words:
        for row in rolling_factor_metrics(word, 32):
            assert row["abelian_complexity"] == row["balance"] + 1


def test_binary_source_lifts_reconstruct_nested_residues() -> None:
    word = square_root_word(128)
    residues, lifts = source_lifts(word)
    old = 0
    modulus = 1
    for residue, lift in zip(residues, lifts):
        assert residue == old + lift * modulus
        old = residue
        modulus *= 2


def test_exact_phase20_exponent_threshold() -> None:
    for gamma in (Fraction(0), Fraction(1, 2), Fraction(7, 9), Fraction(71, 81)):
        assert gamma < Fraction(8, 9)
        assert 1 - gamma > Fraction(1, 9)
    assert 1 - Fraction(8, 9) == Fraction(1, 9)


def test_finite_balanced_factor_bounds() -> None:
    # A finite sanity check of the max/min factor-count quantities used in the
    # P120 proof.  The theorem itself is the sub/superadditive derivation.
    word = all_contact_word(256)
    metrics = rolling_factor_metrics(word, 64)
    assert all(row["balance"] == 1 for row in metrics)
    assert all(row["factor_complexity"] == row["n"] + 1 for row in metrics)
