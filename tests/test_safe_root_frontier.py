"""Exact regression, completeness and tamper rejection tests for the supplement."""
import ast
import copy
import json
from pathlib import Path
import subprocess
import sys
import pytest
from verifier import verify_safe_root_frontier as v
from verifier.verify_safe_root_certificate import check
from src.safe_root_frontier import search
from src.safe_root_frontier_search import tamper
from src.safe_ancestor_window import scan,bounds,decode
from fractions import Fraction

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def good():return search(703,80)

def test_full_independent_audit():
    r=v.audit(ROOT/'artifacts')
    assert r['valid'] and r['fixed_Q_queries']==10240
    assert r['status_counts']['NO_LEX_IMPROVEMENT']==185

def test_all_23_supplied_mutations():
    assert tamper()==v.REJECTIONS

@pytest.mark.parametrize('key',['tree_nodes','frontier_size','trace_steps','short_hits'])
@pytest.mark.parametrize('edit',['increment','float','bool','missing'])
def test_diagnostic_tamper(good,key,edit):
    b=copy.deepcopy(good)
    if edit=='increment':b['diagnostics'][key]+=1
    elif edit=='float':b['diagnostics'][key]=float(b['diagnostics'][key])
    elif edit=='bool':b['diagnostics'][key]=True
    else:b['diagnostics'].pop(key)
    with pytest.raises(ValueError):check(b)

@pytest.mark.parametrize('edit',['top_extra','leaf_extra','trace_extra','bool_trace','float_source','trace_cut','target_endpoint','empty_leaves','empty_traces'])
def test_certificate_tamper(good,edit):
    b=copy.deepcopy(good)
    if edit=='top_extra':b['all_prefixes_proved']=True
    elif edit=='leaf_extra':b['leaves'][0]['trusted']=True
    elif edit=='trace_extra':b['traces'][0]['trusted']=True
    elif edit=='bool_trace':b['traces'][0]['source']=True
    elif edit=='float_source':b['source']=703.0
    elif edit=='trace_cut':b['traces'][0]['cut']='budget_exhausted'
    elif edit=='target_endpoint':b['target_word']=b['target_word'][:-1]+str(1-int(b['target_word'][-1]))
    elif edit=='empty_leaves':b['leaves']=[]
    else:b['traces']=[]
    with pytest.raises(ValueError):check(b)

@pytest.mark.parametrize('key',list(v.scope_reference()))
def test_scope_tamper(key):
    b=v.scope_reference();b[key]=True
    with pytest.raises(ValueError):v.same(b,v.scope_reference())

@pytest.mark.parametrize('kind',['missing','float','bool','witness','candidate','Q_promotion'])
def test_window_data_tamper(kind):
    original=v.direct_reference();b=copy.deepcopy(original)
    if kind=='missing':b['rows'].pop()
    elif kind=='float':b['queries']=float(b['queries'])
    elif kind=='bool':b['forward_steps']=True
    elif kind=='witness':next(r for r in b['rows'] if r['witnesses'])['witnesses'].pop()
    elif kind=='candidate':b['rows'][0]['statistics']['integer_candidates']+=1
    else:b['rows'][0]['statistics']['complete_all_Q']=True
    with pytest.raises(ValueError):v.same(b,original)

def test_first_hit_and_tie_cut_controls():
    c=search(7,4);assert check(c)
    c=search(14,0);assert check(c)
    assert c['witness']=={'source':9,'word':'1'}
    c=search(17,0);assert check(c)

def test_general_safe_word_extrema():
    _,table=v.extrema_reference()
    for (q,L),(lo,hi,count) in table.items():
        b=bounds(q,L);assert b[1:3]==(lo,hi)
        assert v.correction_range(q,L)==(lo,hi)
        assert (hi-lo)*3<q*3**q

def test_no_generator_imports():
    for name in ('verify_safe_root_certificate.py','verify_safe_root_frontier.py'):
        tree=ast.parse((ROOT/'verifier'/name).read_text())
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):names=[a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom):names=[node.module or '']
            else:continue
            assert all(not s.startswith('src') and 'ancestor_window' not in s and 'frontier_search' not in s for s in names)

def test_duplicate_json_rejection():
    with pytest.raises(ValueError):json.loads('{"q":1,"q":2}',object_pairs_hook=v.no_duplicates)

def test_optimized_tamper():
    p=subprocess.run([sys.executable,'-O','-c',
        "from src.safe_root_frontier_search import tamper; r=tamper(); raise SystemExit(0 if len(r)==23 else 1)"],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0,p.stderr

@pytest.mark.parametrize('args',[(0,1),(True,1),(1,False),(1,-1)])
def test_invalid_target(args):
    with pytest.raises(ValueError):search(*args)

def test_unknown_is_not_certificate():
    c=search(703,80,limit=1);assert c['status']=='UNKNOWN'
    with pytest.raises(ValueError):check(c)

def test_valid_certificate_can_cover_an_earlier_target(good):
    # Removing the last even step preserves the relevant normalization and
    # can remain a valid theorem. This is not an invalid arithmetic mutation;
    # a corpus verifier separately binds every expected source/target query.
    b=copy.deepcopy(good);b['target_word']=b['target_word'][:-1]
    assert check(b)
    assert b['target_word']!=good['target_word']

def test_regression_evidence_tampering():
    original=v.regression_reference();bad=copy.deepcopy(original)
    bad['minimal_empty_target_obstruction']['source']=17
    with pytest.raises(ValueError):v.same(bad,original)

def test_coefficient_only_query_excludes_equal_peers():
    y=13581056558;g=Fraction(3**22,2**34)
    strict,st=scan(y,22,g)
    assert all(h.kind=='strict' for h in strict)
    tied,_=scan(y,22,g,7435082751)
    assert any(h.source==7435082747 and h.kind=='equal_smaller' for h in tied)
    assert st['complete_all_Q'] is False
