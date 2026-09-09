from fractions import Fraction

import pytest

from src import phase41_search as search
from verifier import verify_phase41 as independent


@pytest.mark.parametrize("L,q,D,word", [(0, 0, 0, ""), (0, 1, 0, None),
    (0, 0, 1, None), (-1, 0, 0, None), (3, -1, 0, None), (3, 4, 0, None),
    (3, 2, -1, None), (3, 0, 7, "000"), (3, 3, 0, "111"),
    (3, 2, 0, None), (3, 0, 0, None), (2, 0, 1, None), (2, 1, 1, None),
    (True, 1, 0, None), (2, 1.0, 0, None)])
def test_decoder_boundaries(L, q, D, word):
    assert search.decode(L, q, D) == word


def test_complete_small_decoder_against_word_image():
    for L in range(8):
        image = {(q, D): w for w in independent.level(L)
                 for q, _, D in [independent.positions(w)]}
        for q in range(-1, L+2):
            for D in range(-1, 3**max(0, L-1)+2):
                assert search.decode(L, q, D) == image.get((q, D))


def test_minimal_hole_and_exact_stop():
    assert search.fiber(14, 24573) == [(1, "00000000000001"), (2, "01000000000001"),
                                     (5, "00001101001100"), (6, "01001101001100")]
    for L in range(1, 14):
        for f in independent.tail_map(L).values():
            assert all(b[0] == a[0]+1 for a, b in zip(f, f[1:]))


def test_mixed_even_source_is_not_filtered():
    # A positive initial run can disappear completely: 5 --100--> 2,
    # 2 --01--> 2, with coefficient gain two and an even competitor.
    data = search.mixed_rewrite(5, 1, "00", "01", 1)
    assert data["h"] == data["R"] and data["z"] > 0 and data["z"] % 2 == 0
    assert data == search.mixed_rewrite(data["source"], data["R"], data["tail"], data["alternate"], data["h"])


@pytest.mark.parametrize("S,R,v,a,h", [(7, 2, "00", "01", 1), # wrong initial run
    (7, 2, "00", "01", 2), (8, 2, "00", "01", 1), # bad budget/parity
    (7, 2, "00", "00", 0), (7, 2, "00", "10", 0),
    (7, 2, "00", "01", 0), (7, -1, "00", "01", 0)])
def test_mixed_rejects_invalid_inputs(S, R, v, a, h):
    with pytest.raises(ValueError):
        search.mixed_rewrite(S, R, v, a, h)


def test_ng43_retains_unsafe_competitor():
    rows = search.regressions_audit()["pairs"]
    for name in ("NG43_original", "NG43_lex_first"):
        row = next(r for r in rows if r["name"] == name)
        assert row["target"]["safe"] and not row["competitor"]["safe"]
        assert row["valley_time"] == 5
    row = next(r for r in rows if r["name"] == "NG26")
    assert row["valley_source"] == 527131


def test_ancestor_oracle_keeps_longer_cross_q_and_even_paths():
    assert search.candidate(27, 3, 2, 31) == "110"
    assert [27, 3, 2, "110"] in search.ancestor_hits(31, 0, 0, 3)
    assert search.candidate(2, 1, 0, 1) == "0"
    assert search.candidate(1, 0, 0, 1) == ""
    assert search.candidate(0, 0, 0, 1) is None
    assert search.candidate(27, 3, 1, 31) is None
    for y in range(1, 32):
        assert search.ancestor_hits(y, 0, 0, 8) == independent.forward_hits(y, 0, 0, 8)


def test_ancestor_source_bound_strict_and_empty_competitor():
    # Unsafe target 2 --0--> 1 is strictly dominated by the empty path from 1.
    assert [1, 0, 0, ""] in search.ancestor_hits(1, 1, 0, 0)
    assert search.ancestor_hits(1, 0, 0, 10) == []
    with pytest.raises(ValueError):
        search.ancestor_hits(1, 1, 2, 2)


def test_formal_prefix_exact_model_not_integer_claim():
    data = search.formal_audit()
    assert data == independent.formal_expected()
    assert Fraction(*data["correction"]) <= 8
    assert Fraction(*data["bound"]) < 3
    assert data["positive_ordinary_source"] == data["H112"] == "OPEN"


def test_source7_clock_and_167_finite_zero_run():
    data = search.regressions_audit()
    assert [r["chi"] for r in data["source7_clocks"]] == [0, 1, 1]
    assert next(r[0] for r in data["source167"] if not r[4]) == 29


def test_no_generator_import_and_no_decoder_recursion_in_verifier():
    import ast
    from pathlib import Path
    tree = ast.parse(Path(independent.__file__).read_text())
    imports = [node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)]
    imports += [alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names]
    assert not any("phase41_search" in name or name == "src" for name in imports)
    assert not hasattr(independent, "decode")


def test_finite_normalization_and_cocycle_include_even_inputs():
    # Finite identities hold also on terminating trajectories; no infinite
    # normalized height or nonperiodicity is being inferred from this check.
    for S in range(1, 65):
        w, states = independent.forward(S, 16)
        product = Fraction(S)
        for L in range(1, 17):
            n = states[L-1]
            if n % 2:
                product *= Fraction(3*n+1, 3*n)
            q, B, _ = search.affine(w[:L])
            normalized = Fraction(2**L*states[L], 3**q)
            assert normalized == product == S+Fraction(B, 3**q)
            qtail = w[1:L].count("1")
            assert Fraction(2**(L-1)*states[L], 3**qtail) == Fraction(3**int(w[0]), 2)*normalized


def test_query_cli_explicit_cap_and_cross_q(monkeypatch, capsys):
    import json
    monkeypatch.setattr("sys.argv", ["phase41_search", "--endpoint", "31", "--maximum-length", "3"])
    search.main()
    result = json.loads(capsys.readouterr().out)
    assert [27, 3, 2, "110"] in result["hits"]
    assert result["all_Q_geodesic_certificate"] is False


def test_query_cli_rejects_implicit_cap(monkeypatch):
    monkeypatch.setattr("sys.argv", ["phase41_search", "--endpoint", "31"])
    with pytest.raises(SystemExit):
        search.main()
