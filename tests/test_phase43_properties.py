import ast
from fractions import Fraction
import json
from pathlib import Path

import pytest

from src import phase43_search as search
from verifier import verify_phase43 as verifier


@pytest.mark.parametrize("S",[1,2,3,5,7,27,31,59,127,167,703,2**20-1,8**8-5])
def test_normalization_additive_product_and_strict_bound(S):
    x,q,Y=S,0,Fraction(S)
    for k in range(41):
        y,c,H,B=search.target_data(S,k)
        yy,qq,cc,HH,BB,_=verifier.literal(S,k)
        assert (y,c,H,B)==(yy,cc,HH,BB)
        assert (x,q,Y)==(y,qq,H)
        assert H == Fraction(2**k*x,3**q)
        assert B < H <= B+1
        if x & 1:
            Y += Fraction(2**k,3**(q+1))
            q+=1
        x=search.step(x)


@pytest.mark.parametrize("S,L",[(1,0),(1,1),(1,10),(2,0),(2,1),(2,8),
                             (3,0),(5,3),(7,11),(31,0),(59,6),(703,80)])
def test_search_verifies_with_even_empty_unsafe_and_cycle_targets(S,L):
    assert verifier.verify(search.search(S,L))


def test_even_competitor_and_longer_different_q_are_legal():
    even=search.search(5,3)
    even["witness"]={"source":2,"length":2,"odd_count":1}
    assert verifier.verify(even)
    cross=search.search(59,6)
    assert cross["witness"]=={"source":39,"length":7,"odd_count":5}
    assert verifier.verify(cross)
    empty=search.search(2,1)
    assert empty["witness"]=={"source":1,"length":0,"odd_count":0}


def test_reference_first_hit_dominates_every_later_cycle_visit():
    r=json.loads(Path("artifacts/phase43_reference.json").read_text())
    graph,cycles=verifier.reference(r,705)
    assert cycles==[(1,2)]
    for y in (1,2,20,76,1256):
        first=verifier.first_hit_coefficients(y,graph)
        for z in range(1,65):
            x,c=z,Fraction(1)
            for _ in range(250):
                if x == y:
                    assert c <= first[z]
                c*=Fraction(3 if x & 1 else 1,2)
                x=search.step(x)


def test_703_certificate_all_prefixes_and_nonmonotone_defect():
    data=search.search(703,80)
    assert verifier.verify(data)
    assert data["diagnostics"]==dict(work=25848,vertices=1188,maximum_branch_length=92,
        cut_kinds={"normalization_cut":254,"cycle_avoiding_endpoint":451})
    r=json.loads(Path("artifacts/phase43_reference.json").read_text())
    graph,_=verifier.reference(r,705)
    for L in range(81):
        y,c,H,B=search.target_data(703,L)
        first=verifier.first_hit_coefficients(y,graph)
        assert all(first.get(z,Fraction())<=c for z in range(1,B+1))
    odd=search.regressions()["odd_703"]
    assert odd[43:45]==[[43,50165,62,6],[44,4703,67,2]]


def test_open_boundary_and_omitted_endpoint_are_supported():
    big=search.search(703,80)
    W={x for x,_,_ in big["potential"]}
    assert 5024 in W and 2512 not in W and verifier.verify(big)
    tiny=search.search(1,0)
    tiny["potential"]=[] # Outside default already gives f(1)=1; B=0.
    assert verifier.verify(tiny)


def test_capacity_reconstruction_and_exact_log_inequalities():
    data=search.capacities()
    assert verifier.capacity_check(data)==49
    assert Fraction(*data["reciprocal_upper"])==Fraction(32986055029845591,4398046511104000)
    assert Fraction(*data["reciprocal_upper"]) < Fraction(751,100) < Fraction(7244,945)


def test_generator_and_independent_formal_controls_agree():
    assert verifier.regression_check(search.regressions())==(61,22)


def test_smallest_monotonicity_falsifier_and_smaller_source_safety_boundary():
    row=search.search(7,4)
    assert row["status"]=="CERTIFIED_NO_STRICT_IMPROVEMENT" and verifier.verify(row)
    assert row==json.loads(Path("artifacts/phase43_certificate_7.json").read_text())
    assert verifier.literal(7,4)[-1]==[7,11,17,26,13]
    for S,max_safe_length in ((1,1),(2,0),(3,3),(4,0),(5,1),(6,0)):
        _,_,c,_,_,states=verifier.literal(S,max_safe_length+1)
        assert c<1
        q=0
        defects=[]
        for k,x in enumerate(states[:-1]):
            if x % 2:
                defects.append((3**q).bit_length()-1-k)
            q+=x%2
        assert all(a<=b for a,b in zip(defects,defects[1:]))


def test_verifier_imports_no_search_or_potential_solver():
    tree=ast.parse(Path(verifier.__file__).read_text())
    imports=[n.module or "" for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]
    imports += [a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
    assert not any(n.startswith("src") or "search" in n for n in imports)
    assert not hasattr(verifier,"search") and not hasattr(verifier,"potential")


@pytest.mark.parametrize("args",[(0,1),(-1,1),(True,1),(1,-1),(1,True),(Fraction(3,2),1),(1,1.0)])
def test_invalid_target_inputs(args):
    with pytest.raises(ValueError):
        search.search(*args)


@pytest.mark.parametrize("field,value",[("maximum_work",0),("maximum_work",True),
    ("maximum_candidates",0),("maximum_candidates",1.5)])
def test_invalid_resource_limits(field,value):
    with pytest.raises(ValueError):
        search.search(703,80,**{field:value})


def test_cli_three_statuses(monkeypatch,capsys):
    for args,status in [(["--source","1","--length","0"],"CERTIFIED_NO_STRICT_IMPROVEMENT"),
        (["--source","59","--length","6"],"IMPROVEMENT"),
        (["--source","703","--length","80","--maximum-work","1"],"UNKNOWN")]:
        monkeypatch.setattr("sys.argv",["phase43_search"]+args)
        search.main()
        assert json.loads(capsys.readouterr().out)["status"]==status
