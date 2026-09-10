from __future__ import annotations

import ast
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from src.ext08_scope_search import build, regressions
from verifier.verify_ext08_scope import validate, verify_regressions, audit
from scripts.audit_claim_supersession import audit_supersession

ROOT = Path(__file__).resolve().parents[1]


def mutate(data, path, value):
    for key in path[:-1]:
        data = data[key]
    data[path[-1]] = value


@pytest.fixture(scope="module")
def small():
    return build(128)


@pytest.mark.parametrize("n", [64, 128, 257])
def test_independent_ranges(n):
    result = validate(build(n))
    assert result["valid"]
    assert result["checked_prefixes_total"]==3*(n+1)
    assert [m["safe_in_checked_range"] for m in result["models"]]==[True,False,True]


@pytest.mark.parametrize("path,value", [
    (("scope","proves_collatz"),True),
    (("scope","counterexample_to_EXT08_theorem_statement"),True),
    (("scope","rationality_of_corresponding_2adic_sources_determined"),True),
    (("scope","prescribed_real_branches_are_literal_collatz_orbits"),True),
    (("scope","positive_integer_infinite_sources_claimed"),True),
    (("scope","proves_collatz"),0),
    (("format_version",),True),
    (("steps_per_model",),129),
    (("models",0,"initial_u_numerator"),True),
    (("models",0,"word"),"0"*128),
    (("models",0,"real_limit"),"-2/1"),
    (("models",0,"density_deficit"),2),
    (("models",0,"checkpoints",3,"canonical_source_mod_2n"),"0"),
    (("models",0,"checkpoints",3,"state"),"-5/1"),
    (("models",0,"checkpoints",3,"partial_real_series"),"-1/1"),
    (("models",0,"checkpoints",1,"n"),True),
    (("models",2,"all_nonempty_finite_prefixes_coefficient_safe"),False),
    (("models",1,"state_and_series_sha256"),"0"*64),
    (("models",1,"first_literal_mismatch"),None),
    (("models",0,"q_final"),0),
    (("lemma24_repetition","second_time"),4),
    (("exact_constants","block_growth"),"81/16"),
    (("models",),[]),
])
def test_model_tampering_rejected(small,path,value):
    data = deepcopy(small)
    mutate(data,path,value)
    with pytest.raises(ValueError):
        validate(data)


def test_full_accepted_audit():
    result = audit(ROOT/"artifacts")
    assert result == json.loads((ROOT/"artifacts/ext08_scope_verifier.json").read_text())
    assert result["checked_prefixes_total"] == 12291
    assert result["literal_finite_prefix_steps"] == 28209


def test_supplied_certificate_regenerated_exactly():
    encoded = (json.dumps(build(),ensure_ascii=False,indent=2)+"\n").encode()
    assert encoded == (ROOT/"artifacts/ext08_scope_models.json").read_bytes()
    assert hashlib.sha256(encoded).hexdigest()=="212d620887af40d631e021175b156818e3cc796c3bf3f9f3d64c4287229ff2fd"


@pytest.mark.parametrize("m",range(1,30))
def test_dyadic_branch_interval_and_denominator(m):
    # Exhaust all odd dyadic seeds up to denominator 32, for m literal
    # prescribed steps. This checks the induction boundary, not infinity.
    for b in range(1,6):
        for a in range(1,3*2**(b-1),2):
            u = Fraction(a,2**b)
            for j in range(m):
                assert u!=1
                u = 3*u/2 if u<1 else (u-1)/2
                assert 0<u<Fraction(3,2)
                assert u.denominator==2**(b+j+1)


def test_exact_buffer_minimum_and_density():
    assert 3**4>2**5
    assert 9**11<4*8**11
    assert 9**12>4*8**12
    assert Fraction(1,4)*Fraction(3,2)**3<1


def test_mandatory_regressions():
    data = regressions()
    assert data==json.loads((ROOT/"artifacts/ext08_scope_regressions.json").read_text())
    assert verify_regressions(data)>50
    row = next(r for r in data["words"] if r["word"]=="111011100")
    assert (row["B"],row["q"])==("817",6)
    assert Fraction(-817,3**6-2**9)==Fraction(-817,217)


@pytest.mark.parametrize("path,value", [
    (("words",0,"B"),"1"), (("words",1,"residue"),"0"),
    (("words",1,"positive_source"),"-1"), (("cycles",2,"endpoint"),-2),
    (("words",),[]), (("proves_collatz",),True),
])
def test_regression_tamper(path,value):
    data = regressions()
    mutate(data,path,value)
    with pytest.raises(ValueError):
        verify_regressions(data)


@pytest.mark.parametrize("path,value", [
    (("status_transition","to"),"REFUTED"),
    (("status_transition","to"),"EXTERNAL_THEOREM"),
    (("EXT08_statement_refuted",),True),
    (("historical_verification_is_current_theorem_acceptance",),True),
    (("historical_files",0,"sha256"),"0"*64),
    (("conditional_claims",),[]),
    (("proves_collatz",),True),
])
def test_supersession_tamper(path,value):
    data=json.loads((ROOT/"artifacts/ext08_scope_impact.json").read_text())
    mutate(data,path,value)
    assert audit_supersession(ROOT,data)


def test_no_generator_import_and_optimized_tamper(tmp_path):
    path=ROOT/"verifier/verify_ext08_scope.py"
    tree=ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom):
            assert not (node.module or "").startswith("src")
        if isinstance(node,ast.Import):
            assert all(not a.name.startswith("src") for a in node.names)
    result=subprocess.run([sys.executable,"-O","-c",
        "from verifier.verify_ext08_scope import validate; import json; "
        "d=json.load(open('artifacts/ext08_scope_models.json')); "
        "d['scope']['proves_collatz']=True; validate(d)"],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode!=0 and "scope/overclaim" in result.stderr


@pytest.mark.parametrize("kind",["repromote", "unconditional_dependency"])
def test_current_ledger_quarantine(monkeypatch,kind):
    import scripts.audit_claim_supersession as checker
    from scripts.build_claim_index import build_index
    index=build_index(ROOT)
    if kind=="repromote":
        next(c for c in index["claims"] if c["id"]=="EXT08")["status"]="EXTERNAL_THEOREM"
    else:
        next(c for c in index["claims"] if c["id"]=="P127")["dependency_ids"].append("EXT08")
    monkeypatch.setattr(checker,"build_index",lambda root:index)
    data=json.loads((ROOT/"artifacts/ext08_scope_impact.json").read_text())
    errors=checker.audit_supersession(ROOT,data)
    assert errors
    assert any("ledger mismatch" in e or "unconditional theorem" in e for e in errors)
