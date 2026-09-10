"""Finite evidence is not an all-scale proof; test both arithmetic and scope."""
import copy
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import pytest

from src import transient_sparsity_search as search
from verifier import verify_transient_sparsity as verify


@pytest.fixture(scope='module')
def expected():
    return {'evidence':verify.rebuild(),'scope':verify.reconstruct_scope(),
            'regressions':verify.reconstruct_regressions()}


@pytest.mark.parametrize('name',['evidence','scope','regressions'])
def test_reconstruct_committed(name,expected):
    data=json.loads(Path(f'artifacts/transient_sparsity_{name}.json').read_text())
    assert verify.verify_against(data,expected[name])


MUTATIONS=[
    ('evidence',('proves_collatz',),True),
    ('evidence',('proves_collatz',),0),
    ('evidence',('status',),'VERIFIED_THEOREM'),
    ('evidence',('capacity','Nmax'),499),
    ('evidence',('capacity','rows',10,1),'769'),
    ('evidence',('capacity','rows',10,2),'507'),
    ('evidence',('capacity','row_digest'),'0'*64),
    ('evidence',('capacity','tail',0),'0'),
    ('evidence',('capacity','F49',0),'1'),
    ('evidence',('capacity','checks','F19_lt_15_over_2'),False),
    ('evidence',('capacity','checks','F49_lt_2079_over_1000'),1),
    ('evidence',('constants','comparisons','low_at_135'),False),
    ('evidence',('constants','log2_lower',0),'843'),
    ('evidence',('affine','words'),32766),
    ('evidence',('affine','word_digest'),'0'*64),
    ('evidence',('affine','extrema',10,2),1),
    ('evidence',('finite_prefix','source_count'),127),
    ('evidence',('finite_prefix','nonzero_terminal_deletions'),0),
    ('evidence',('finite_prefix','max_terminal_deletions'),0),
    ('evidence',('finite_prefix','window_digest'),'0'*64),
    ('scope',('tail_applies_to_raw_recursive_capacities',),True),
    ('scope',('old_capacity_tables_replaced',),True),
    ('scope',('P267_reused_without_duplicate_claim',),False),
    ('scope',('external_theorem_required',),True),
    ('scope',('all_competitor_source_pool_requires_distinct_target_inputs',),False),
    ('scope',('repeated_target_cycle_deletion_only_supplies_a_witness',),False),
    ('scope',('infinite_proofs_machine_formalized',),True),
    ('scope',('floor_19_bound',),2),
    ('scope',('H112_status',),'VERIFIED_THEOREM'),
    ('scope',('H72_status',),'REFUTED'),
    ('regressions',('first_failure_within_source_1',),40),
    ('regressions',('repeated_source_1',39,3),True),
    ('regressions',('paths',0,2),'0'),
    ('regressions',('words',0,2),'0'),
    ('regressions',('K_rows',0,2),0),
    ('regressions',('historical_sha256','phase43_certificate_7.json'),'0'*64),
]


@pytest.mark.parametrize('name,path,value',MUTATIONS)
def test_tamper_rejection(name,path,value,expected):
    bad=copy.deepcopy(expected[name]); cursor=bad
    for key in path[:-1]: cursor=cursor[key]
    assert verify.encode(cursor[path[-1]])!=verify.encode(value), 'mutation must change bytes'
    cursor[path[-1]]=value
    with pytest.raises(ValueError): verify.verify_against(bad,expected[name])


@pytest.mark.parametrize('name',['evidence','scope','regressions'])
@pytest.mark.parametrize('operation',['missing','extra'])
def test_scope_shape(name,operation,expected):
    bad=copy.deepcopy(expected[name])
    if operation=='missing': del bad['status']
    else: bad['all_repeated_orbits_covered']=True
    with pytest.raises(ValueError): verify.verify_against(bad,expected[name])


def test_duplicate_json_rejected():
    with pytest.raises(ValueError):
        json.loads('{"proves_collatz":true,"proves_collatz":false}',object_pairs_hook=verify.duplicate_reject)


def test_verifier_has_no_generator_import():
    import ast
    tree=ast.parse(Path(verify.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom): assert not (node.module or '').startswith('src')
        if isinstance(node,ast.Import):
            assert all(not a.name.startswith('src') and 'search' not in a.name for a in node.names)


def test_terminal_loss_all_abstract_subsets():
    count=0
    for M in range(11):
        for N in range(13):
            for mask in range(1<<M):
                selected=[i for i in range(M) if mask>>i&1]
                images=[i+N for i in selected if i+N<M]
                assert len(selected)-len(images)<=N
                assert len(images)==len(set(images)) and all(j<M for j in images)
                count+=1
    assert count==26611


@pytest.mark.parametrize('s,M',[(1,0),(1,2),(7,4),(703,80),(2**20-1,20),(2**50-1,50)])
def test_normalization_boundaries(s,M):
    assert search.normalization(s,M)==verify.normalization(s,M)


@pytest.mark.parametrize('s,M',[(1,3),(1,40),(-1,1),(0,0),(True,1),(3,-1),(3,True)])
def test_bad_domain_rejected(s,M):
    for fn in (search.normalization,verify.normalization):
        with pytest.raises(ValueError): fn(s,M)


def test_negative_and_zero_window_anchors(expected):
    rows=expected['evidence']['capacity']['rows']
    for s in (1,3,7,27,703):
        P,_,_=verify.make_trace(s)
        for M in (0,1,2,8,len(P)):
            segment=P[:M]
            for N in range(9):
                for a in (-2**N,-1,0,1):
                    selected=[(i,x) for i,x in enumerate(segment) if a<=x<a+2**N]
                    kept=[i+N for i,x in selected if i+N<len(segment)]
                    assert len(selected)-len(kept)<=N
                    assert len(selected)<=int(rows[N][1])
                    assert sum(x%2 for i,x in selected)<=int(rows[N][2])


def test_minimal_repeated_source_control():
    assert Fraction(4,3)**19<256<Fraction(4,3)**20
    assert verify.nxt(-1)==-1


def test_optimized_python_rejects_tamper(tmp_path):
    # Subprocess rejection must survive removal of every Python assert.
    for path in Path('artifacts').glob('transient_sparsity_*.json'):
        (tmp_path/path.name).write_bytes(path.read_bytes())
    target=tmp_path/'transient_sparsity_scope.json'
    bad=json.loads(target.read_text()); bad['tail_applies_to_raw_recursive_capacities']=True
    target.write_text(json.dumps(bad))
    run=subprocess.run([sys.executable,'-O','verifier/verify_transient_sparsity.py',
                        '--artifact-dir',str(tmp_path)],capture_output=True,text=True)
    assert run.returncode==1 and json.loads(run.stdout)['valid'] is False


@pytest.mark.parametrize('mutation',['duplicate','missing_report','missing_claim','bool_as_int','missing_contract','experiment_mismatch'])
def test_supplement_health_contract(mutation):
    from scripts.research_health import supplement_audit
    registry=json.loads(Path('research/registry.json').read_text())
    item=registry['supplemental_acceptances'][0]
    assert item['id']=='transient-sparsity'
    claim_map={c:'OPEN' for record in registry['supplemental_acceptances'] for c in record['claim_ids']}
    assert supplement_audit(Path('.'),registry,claim_map)==[]
    if mutation=='duplicate': registry['supplemental_acceptances'].append(copy.deepcopy(item))
    elif mutation=='missing_report': item['report']='nonexistent-report.md'
    elif mutation=='missing_claim': item['claim_ids'].append('P999999')
    elif mutation=='bool_as_int': item['expected_verifier_fields']['raw_capacity_tail_claimed']=0
    elif mutation=='missing_contract': del item['expected_verifier_fields']
    elif mutation=='experiment_mismatch': item['id']='different-id'
    assert supplement_audit(Path('.'),registry,claim_map)
