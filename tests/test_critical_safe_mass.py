"""Exact finite acceptance and deliberate boundary violations."""
import ast
import copy
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from src import critical_safe_mass_search as search
from verifier import verify_critical_safe_mass as verify


@pytest.fixture(scope='module')
def reference():
    a,b=verify.cycle_recurrence(512)
    residues,words=verify.small_words_and_residues(18,a,b)
    ar=verify.arithmetic_reference(a,b)
    data=json.loads(Path('artifacts/critical_safe_mass_evidence.json').read_text())
    return a,b,residues,words,ar,data


def test_generator_vs_cycle_recurrence(reference):
    a,b,*_=reference
    assert search.counts(512)==(a,b)
    assert a[0]==1 and b[0]==0 and a[26]==1037374


def test_all_evidence(reference):
    a,b,residues,words,ar,data=reference
    verify.validate_data(data,a,b,ar,residues)
    assert words==524287
    assert verify.tamper_checks(data,a,b,ar,residues)==22
    for name,expected in [('scope',verify.scope_reference()),('regressions',verify.regression_reference(residues))]:
        verify.same(json.loads(Path(f'artifacts/critical_safe_mass_{name}.json').read_text()),expected)


def test_full_bijection(reference):
    out=verify.check_bijection(reference[0])
    assert out['labeled_permutation_color_pairs']==50362
    assert out['positive_pairs']==6327
    report=json.loads(Path('artifacts/critical_safe_mass_verifier.json').read_text())
    assert out==report['bijection']


@pytest.mark.parametrize('field',['EXT08_used','mass_implies_emptiness','P80_address_multiplicity_counted',
    'permanent_source_existence_asserted','finite_check_proves_infinite_theorem','orbit_bits_assumed_random',
    'unperturbed_means_assumed_distinct','general_identity_novelty_claimed','proves_collatz'])
def test_reject_scope_promotions(field):
    expected=verify.scope_reference(); bad=copy.deepcopy(expected); bad[field]=True
    with pytest.raises(ValueError): verify.same(bad,expected)


@pytest.mark.parametrize('field,value',[
    ('count_domain','all finite distinct trajectories'),('mass_domain','all positive integers'),
    ('renewal_index','every odd time q'),('H112_status','VERIFIED_THEOREM'),
    ('H72_status','REFUTED'),('rho','29/30'),
    ('Y_limit_bound_from_P270','Y_infinity < 256 S_0 by passage to limit')])
def test_reject_quantifier_changes(field,value):
    expected=verify.scope_reference(); bad=copy.deepcopy(expected); bad[field]=value
    with pytest.raises(ValueError): verify.same(bad,expected)


MUTATIONS=[
    (('scope','max_n'),512.0), (('scope','labeled_bijection_n'),6.0),
    (('scope','proves_collatz'),0), (('scope','status'),'VERIFIED_THEOREM'),
    (('counts',0,'b'),'1'), (('counts',0,'a'),'0'), (('counts',26,'a'),'1037375'),
    (('counts',512,'n'),512.0), (('mass_certificate','mu_lower','numerator'),'19318'),
    (('mass_certificate','finite_sum_upper','numerator'),'0'),
    (('mass_certificate','safe_coefficient_lower','denominator'),'23'),
    (('mass_certificate','tail_upper','denominator'),'12'),
    (('mass_certificate','critical_mass_upper'),9.0),
    (('mass_certificate','exact_checks','mu_lower_exact'),1),
    (('interval_queries',0,'safe_through_n'),0),
    (('interval_queries',20,'start'),'0'),
    (('controls','seven_first_failed_prefix'),9.0),
]


@pytest.mark.parametrize('path,value',MUTATIONS)
def test_evidence_tampering(reference,path,value):
    a,b,residues,_,ar,data=reference; bad=copy.deepcopy(data); cursor=bad
    for key in path[:-1]: cursor=cursor[key]
    assert json.dumps(cursor[path[-1]])!=json.dumps(value)
    cursor[path[-1]]=value
    with pytest.raises(ValueError): verify.validate_data(bad,a,b,ar,residues)


@pytest.mark.parametrize('where',[(),('scope',),('counts',0),('mass_certificate',),('controls',)])
@pytest.mark.parametrize('operation',['missing','extra'])
def test_missing_or_extra_fields(reference,where,operation):
    a,b,residues,_,ar,data=reference; bad=copy.deepcopy(data); cursor=bad
    for key in where: cursor=cursor[key]
    if operation=='extra': cursor['unexpected']=True
    else: cursor.pop(next(iter(cursor)))
    with pytest.raises((ValueError,KeyError)): verify.validate_data(bad,a,b,ar,residues)


@pytest.mark.parametrize('mode',['unreduced','negative_denominator','leading_zero','integer_not_string'])
def test_rational_canonical_form(mode):
    bad={'numerator':'1','denominator':'2'}
    if mode=='unreduced': bad={'numerator':'2','denominator':'4'}
    elif mode=='negative_denominator': bad['denominator']='-2'
    elif mode=='leading_zero': bad['numerator']='01'
    else: bad['numerator']=1
    with pytest.raises(ValueError): verify.rat(bad)


def test_tied_means_are_not_generic():
    with pytest.raises(ValueError): verify.check_generic([117,117],3)
    with pytest.raises(ValueError): verify.cycles_to_positive((1,0),[117,117])


def test_wrong_perturbation_sign_rejected():
    with pytest.raises(ValueError): verify.check_generic([1],0)


def test_finite_safety_not_permanent():
    assert search.literal_safe(1,0) and search.literal_safe(1,1)
    assert not search.literal_safe(1,2)
    assert not search.literal_safe(2,1)
    for k in range(1,33): assert search.literal_safe(2**k-1,k)


def test_powers_of_two_translated_distance_control():
    for b in range(2049):
        first=next(k for k in range(1,13) if 2**k>b)
        for j in range(12): assert 2**(first+j)-b>=2**j
    u=Fraction(19317,10000)
    assert u>Fraction(3,2) and u/(u-1)<3<9


def test_pi_enclosure_polynomial_identity():
    # x^4(1-x)^4=(1+x^2)*(x^6-4x^5+5x^4-4x^2+4)-4.
    q=[4,0,-4,0,5,-4,1]; product=[0]*9
    for i,c in enumerate(q): product[i]+=c; product[i+2]+=c
    product[0]-=4
    assert product==[0,0,0,0,1,-4,6,-4,1]
    assert sum((Fraction(c,i+1) for i,c in enumerate(q)),Fraction(0))==Fraction(22,7)


def test_duplicates_and_no_generator_import():
    with pytest.raises(ValueError): json.loads('{"x":1,"x":2}',object_pairs_hook=verify.no_duplicates)
    for node in ast.walk(ast.parse(Path(verify.__file__).read_text())):
        if isinstance(node,ast.ImportFrom): assert not (node.module or '').startswith('src')
        if isinstance(node,ast.Import): assert all('search' not in a.name for a in node.names)


def test_optimized_python_rejection(tmp_path):
    for p in Path('artifacts').glob('critical_safe_mass_*.json'):
        (tmp_path/p.name).write_bytes(p.read_bytes())
    path=tmp_path/'critical_safe_mass_scope.json'; bad=json.loads(path.read_text())
    bad['mass_implies_emptiness']=True; path.write_text(json.dumps(bad))
    result=subprocess.run([sys.executable,'-O','verifier/verify_critical_safe_mass.py',
                           '--artifact-dir',str(tmp_path)],capture_output=True,text=True)
    assert result.returncode==1 and json.loads(result.stdout)['valid'] is False


@pytest.mark.parametrize('path,value',[
    (('finite_only',),False), (('words',0,2),'true'),
    (('filters',0,2),0), (('filters',10,3),'0'),
    (('tied_mean_control','centered'),[0,1]),
    (('mass_only_countermodel','permanent_safe'),True),
    (('historical_sha256','phase41_formal.json'),'0'*64),
])
def test_regression_tampering(reference,path,value):
    expected=verify.regression_reference(reference[2]); bad=copy.deepcopy(expected); cursor=bad
    for key in path[:-1]: cursor=cursor[key]
    assert json.dumps(cursor[path[-1]])!=json.dumps(value)
    cursor[path[-1]]=value
    with pytest.raises(ValueError): verify.same(bad,expected)


def test_registry_registers_new_supplement():
    from scripts.research_health import supplement_audit
    registry=json.loads(Path('research/registry.json').read_text())
    records=registry['supplemental_acceptances']
    item=next(x for x in records if x['id']=='critical-safe-mass')
    assert item['claim_ids']==['P271','P272','P273','E63','NG49']
    claim_map={c:'OPEN' for r in records for c in r['claim_ids']}
    assert supplement_audit(Path('.'),registry,claim_map)==[]
    item['expected_verifier_fields']['EXT08_used']=True
    assert supplement_audit(Path('.'),registry,claim_map)
