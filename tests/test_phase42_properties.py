import ast
import itertools
from pathlib import Path

import pytest

from src import phase42_search as search
from verifier import verify_phase42 as verify


@pytest.mark.parametrize("S", [1, 3, 7, 27, 31, 167, 255, 1023, 4095, 2**20-1, 8**8-5])
def test_accelerated_and_full_step_decompositions_agree(S):
    assert search.capacity_row(S) == verify.capacity_row(S)


@pytest.mark.parametrize("steps", [0, 1, 2, 4, 9, 16, 64, 512, 4096])
def test_recurrence_matches_closed_square_formula(steps):
    assert search.square_word(steps) == verify.closed_model(steps)


def test_complete_small_B_image_and_invalid_triples():
    for L in range(9):
        image = {}
        for bits in itertools.product("01", repeat=L):
            w = "".join(bits)
            q, B = verify.positions(w)
            assert search.affine(w) == (q, B)
            assert search.decode_B(L, q, B) == verify.forced_word(L, q, B) == w
            image[q, B] = w
        if L <= 5:
            for q in range(L+1):
                for B in range(3**L+1):
                    assert search.decode_B(L, q, B) == image.get((q, B))


def test_safe_extremal_bound_and_source_congruence():
    for L in range(1, 13):
        for value in range(1 << L):
            word = format(value, f"0{L}b")
            if search.safe(word):
                q, B = search.affine(word)
                assert B <= search.Bmax(q)
                if q >= 2:
                    assert word.startswith("11") and search.source(word) % 4 == 3


def test_exact_parity_separation():
    for a in range(1, 65):
        wa, _ = verify.forward(a, 8)
        for b in range(a+1, 65):
            wb, _ = verify.forward(b, 8)
            v = ((b-a) & -(b-a)).bit_length()-1
            assert wa[:v] == wb[:v] and wa[v] != wb[v]


@pytest.mark.parametrize("K", [2, 3, 8, 17])
def test_capacity_energy_nonvacuous_synthetic_and_sharp_leading_term(K):
    # Abstract CAP data, not claimed to be literal ordinary orbits.
    H = 12
    for bump in (0, 1, 2):
        blocks = [(r, r+K-1+int(r == H)*bump) for r in range(H+1)]
        for h in range(2*H+K+1):
            lhs = sum(max(ell-h-K+1, 0) for r, ell in blocks if r <= h)
            assert lhs <= h+K+1
        energy = sum(max(ell-r-K+1, 0)*(max(ell-r-K+1, 0)+1) for r, ell in blocks)
        assert energy == bump*(bump+1)
        assert energy <= (2*H+K+1)*(2*H+3*K+2)
    assert sum(r+K-1 for r in range(H+1)) == H*(H+1)//2+(K-1)*(H+1)
    # Local interval caps alone do not give simultaneous CAP.
    bad = [(0, K+1)]*(K+1)
    assert all(ell-K+1 <= K+1 for _, ell in bad)
    assert sum(ell-K+1 for _, ell in bad) > K+1


def test_pure_infinite_word_is_not_NG32_terminal_mutation():
    f = [(3**j).bit_length()-1 for j in range(100)]
    mechanical = "".join("1" if t in f else "0" for t in range(f[-1]))
    for n in range(1, 24):
        assert len({mechanical[i:i+n] for i in range(len(mechanical)-n+1)}) <= n+1
    critical = "1101100"
    assert len({critical[i:i+2] for i in range(len(critical)-1)}) == 4
    assert not search.safe(critical)


def test_positive_distinctness_cannot_be_dropped():
    w, states = verify.forward(-5, 6)
    assert w == "110110" and states[0] == states[3]
    assert search.safe(w)  # A formal safe negative cycle is not a positive path.
    assert verify.capacity_row(1)["q"] == 0  # Positive trivial cycle contracts.
    with pytest.raises(verify.VerificationError):
        verify.capacity_row(-5)


def test_q22_minimum_and_P88_boundary():
    data = search.carry_audit()
    assert data == verify.carry_expected()
    w = data["witness"]
    assert set(w["target_exponents"]) == {1, 2}
    a = w["alternative"]
    ps = [i for i, bit in enumerate(a) if bit == "1"]+[len(a)]
    assert max(b-a for a, b in zip(ps, ps[1:])) > 2
    assert data["q21_patterns"] == 12 and len(data["q21_checks"]) == 48


def test_nonvacuous_finite_repeat_proof():
    row = search.repeat_certificate(8)
    assert row["clean_occurrences"] == 25 > row["capacity"] == 20
    assert verify.verify_repeat(row) == 117


def test_verifier_has_no_generator_imports():
    tree = ast.parse(Path("verifier/verify_phase42.py").read_text())
    imports = [n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names]
    assert all(not name.startswith("src") and "phase42_search" not in name for name in imports)
