import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from src import phase44_search as gen
from verifier import verify_phase44 as verifier


@pytest.fixture
def payload():
    return json.loads(Path('artifacts/phase44_model.json').read_text())


def test_complete_independent_acceptance():
    result=verifier.audit(Path('artifacts'))
    assert result==json.loads(Path('artifacts/phase44_verifier.json').read_text())
    assert result['valid'] and not result['generator_imported'] and not result['proves_collatz']


@pytest.mark.parametrize('field,value',[('schema','wrong'),('base','0'*40),('proves_collatz',True),
                                      ('proves_collatz',0),('stats',{}),('repeat_certificates',[])])
def test_metadata_tampering(payload,field,value):
    payload[field]=value
    assert not verifier.verify_model(payload)


@pytest.mark.parametrize('field',['q','E','a','H','D','U','t','pure_intervals','max_pure_length_minus_height','a32'])
def test_statistics_tampering(payload,field):
    payload['stats'][field]+=1
    assert not verifier.verify_model(payload)


@pytest.mark.parametrize('field',['word_sha256','exponent_sha256'])
def test_model_digest_tampering(payload,field):
    payload['stats'][field]='0'*64
    assert not verifier.verify_model(payload)


@pytest.mark.parametrize('field',['K','n','windows','charged_edits','charge_upper','low_edit_occurrences','distinct_low_edit_words'])
def test_window_tampering(payload,field):
    payload['windows'][field]+=1
    assert not verifier.verify_model(payload)


@pytest.mark.parametrize('field,value',[('B',7),('K',19),('n',57),('i',71),('j',136),('common',80),
    ('split',[0,0]),('required_full_prefix',216),('i',True),('B',8.0),('j',-1)])
def test_repeat_tampering(payload,field,value):
    payload['repeat_certificates'][0][field]=value
    assert not verifier.verify_model(payload)


def test_ball_and_vacuity_tampering(payload):
    item=copy.deepcopy(payload); item['windows']['edited_capacity'][1]['rhs']+=1
    assert not verifier.verify_model(item)
    payload['windows']['old_CAP_all_zero']=False
    assert not verifier.verify_model(payload)


@pytest.mark.parametrize('field',['beta32','beta_tail_upper','beta_infinity_upper','entropy_comparison','dependency_hashes'])
def test_theory_tampering(field):
    data=json.loads(Path('artifacts/phase44_theory.json').read_text()); data[field]=[]
    with pytest.raises((ValueError,TypeError,KeyError)): verifier.theory_check(data)


@pytest.mark.parametrize('n,r',[(0,0),(-1,1),(2,-1),(True,1),(2,False),(2.0,1)])
def test_invalid_ball_domains(n,r):
    with pytest.raises(ValueError): gen.ball(n,r)
    with pytest.raises(ValueError): verifier.bound(n,r)


def test_optimized_python_rejects_tampered_model():
    script="""
import json
from pathlib import Path
from verifier.verify_phase44 import verify_model
p=json.loads(Path('artifacts/phase44_model.json').read_text())
if not verify_model(p): raise SystemExit('valid model rejected')
p['windows']['edited_capacity'][1]['rhs']=0
if verify_model(p): raise SystemExit('tampering accepted under -O')
print('valid accepted and tampering rejected under -O')
"""
    result=subprocess.run([sys.executable,'-O','-c',script],capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr


def test_artifact_regeneration_in_separate_directory(tmp_path):
    gen.generate(tmp_path)
    for name in ('model','finite','regressions','theory'):
        assert (tmp_path/f'phase44_{name}.json').read_bytes()==Path(f'artifacts/phase44_{name}.json').read_bytes()
    assert verifier.audit(tmp_path)==json.loads(Path('artifacts/phase44_verifier.json').read_text())


@pytest.mark.parametrize('kind',['orbits','ball','alignment','transcript'])
def test_finite_summary_tampering(kind):
    data=json.loads(Path('artifacts/phase44_finite.json').read_text())
    if kind=='orbits': data['orbits']['complete_prefix_queries']-=1
    elif kind=='ball': data['ball_rows'][0][2]+=1
    elif kind=='alignment': data['alignment']['low_edit_memberships']+=1
    else: data['orbits']['transcript_sha256']='0'*64
    with pytest.raises(ValueError): verifier.same(data,verifier.finite_reference())


@pytest.mark.parametrize('kind',['inherited','ordinary','literal'])
def test_regression_tampering(kind):
    data=json.loads(Path('artifacts/phase44_regressions.json').read_text())
    if kind=='inherited': data['inherited']['controls']['q22_d']['source']+=2
    elif kind=='ordinary': data['ordinary_families'][0]['transcript_sha256']='0'*64
    else: data['literal_word_capacity'].pop()
    with pytest.raises(ValueError): verifier.regression_check(data)
