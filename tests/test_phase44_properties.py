import ast
from fractions import Fraction
import itertools
import json
from pathlib import Path

import pytest

from src import phase44_search as gen
from verifier import verify_phase44 as check


@pytest.mark.parametrize('q',[0,1,2,31,32,33,510,511,512,513,1022,1023,1024,2047,4096,5000])
def test_event_jumps_equal_stepwise_model(q):
    a=gen.model_exponents(q); b=check.event_model(q)
    assert a==b
    assert gen.alignment(a)['stats']==check.reconstruct_alignment(b)['stats']
    assert all(e in (1,2,3) for e in a)


def test_logarithm_enclosures_against_integer_powers():
    a=gen.floors(4096); b=check.mechanical(4096); power=1
    for j in range(4097):
        assert a[j]==b[j]==power.bit_length()-1
        power*=3


@pytest.mark.parametrize('n,r',list(itertools.product(range(1,9),(0,1,2,8,16))))
def test_ball_all_budgets_and_hockey_stick(n,r):
    assert gen.ball(n,r)==check.bound(n,r)
    assert gen.ball(n,r)==(n+r+1)*sum(__import__('math').comb(2*n+j,j) for j in range(r+1))


@pytest.mark.parametrize('exps',[[],[1],[12],[1,1],[1,1,1],[3,1],[1,4,1,4],[8,1,1,8]])
def test_alignment_boundaries_empty_all_inserted_and_deleted(exps):
    a=gen.alignment(exps); b=check.reconstruct_alignment(exps)
    assert a['stats']==b['stats']
    f=gen.floors(len(exps)); baseline=bytearray(f[-1])
    for p in f[:-1]: baseline[p]=1
    for n in range(1,len(a['word'])+3):
        costs=gen.charges(a,n)
        assert costs==check.range_charges(b,n)
        assert sum(costs)<=n*a['stats']['t']
        for i,cost in enumerate(costs):
            retained=[p for p in a['mapping'][i:i+n] if p is not None]
            base=bytes(baseline[retained[0]:retained[-1]+1]) if retained else b''
            assert check.zero_distance(base,bytes(a['word'][i:i+n]))<=cost
    assert a['stats']['t']==a['stats']['a']+2*a['stats']['D']


def test_endpoint_deletion_not_charged():
    assert gen.charges(gen.alignment([1,1]),2)==[0]
    assert gen.charges(gen.alignment([1,1,1]),3)==[1]
    assert gen.charges(gen.alignment([3,1]),2)[1]==2


def test_exhaustive_edit_balls_match_inverse_dp():
    assert gen.small_balls()==check.inverse_balls()


def test_complete_small_alignment_and_orbit_transcripts():
    finite=check.finite_reference()
    assert finite==json.loads(Path('artifacts/phase44_finite.json').read_text())
    assert gen.alignment_audit(gen.small_balls())==finite['alignment']
    assert gen.orbit_audit()==finite['orbits']


@pytest.mark.parametrize('source',[1,3,7,27,31,167,703,2**12-1,8**12-5])
def test_literal_safe_unsafe_and_full_state_repeat(source):
    assert list(gen.orbit_records(source))==list(check.independent_orbits(source))


def test_cycle_closing_endpoint_allowed_second_traversal_not_allowed():
    rows=list(gen.orbit_records(1,4))
    assert len(rows)==1 and rows[0][2]==2 and rows[0][8]==1 and not rows[0][9]
    # 3's odd path reaches odd 1, but its next block would repeat even 2
    # before a new odd boundary; both implementations must stop there.
    rows=list(gen.orbit_records(3,64))
    assert len(rows)==2 and rows[-1][2]==5


def test_ng32_mutated_terminal_is_not_infinite_mechanical_language():
    w=b'\x01\x01\x00\x01\x01\x00\x00'
    assert len({w[i:i+2] for i in range(6)})==4
    assert len(gen.small_language()[2])==3


def test_exact_model_tail_and_sparsity_constants():
    data=gen.theory(); check.theory_check(data)
    assert Fraction(*data['beta_infinity_upper'])<2
    assert 33**33<2**168


def test_analytic_model_conditions_and_finite_no_gain():
    exps=gen.model_exponents(4096); data=gen.alignment(exps)
    assert data['profile'][32]==15
    assert all(a>=2*((j+1).bit_length()-1)-3 for j,a in enumerate(data['profile']) if j>=32)
    assert all(l<=r+2 for r,p,j,l in data['intervals'])
    # Every finite inverse source is odd and has the exact prescribed exponent
    # list when the final odd bit is included. No stable ordinary source claim.
    E=0; residue=0; mod=1
    for j,e in enumerate(exps[:128]):
        E+=e; mod=1<<(E+1)
        residue=(-sum((1<<sum(exps[:k]))*pow(3**(k+1),-1,mod) for k in range(j+2)))%mod
        x=residue
        for ee in exps[:j+1]:
            assert x&1
            v=3*x+1
            assert (v & -v)==1<<ee
            x=v>>ee
    word=b'\x00'+b'\x01'*6+bytes(data['word'])
    coefficient=Fraction(1); correction=Fraction()
    for bit in word:
        if not bit: correction+=1/coefficient
        coefficient*=Fraction(3 if bit else 1,2)
        assert correction<Fraction(857,729)


def test_no_generator_import_and_no_assert_acceptance():
    tree=ast.parse(Path(check.__file__).read_text())
    assert not any(isinstance(n,ast.Assert) for n in ast.walk(tree))
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom):
            assert not (node.module or '').startswith(('src','phase44_search'))
        if isinstance(node,ast.Import):
            assert all(not n.name.startswith(('src','phase44_search')) for n in node.names)
