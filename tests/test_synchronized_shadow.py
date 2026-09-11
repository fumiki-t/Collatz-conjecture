#!/usr/bin/env python3
"""Small exact regressions and explicit corruption rejection; works with -O."""
import copy, json, unittest
from pathlib import Path
from verifier import verify_synchronized_shadow as verify
ROOT=Path(__file__).resolve().parents[1]/'artifacts'

class Checks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/'synchronized_shadow_evidence.json').read_text())
        verify.reconstruct()
    def test_valid_reconstruction(self):
        self.assertTrue(verify.verify_data(self.data)['valid'])
    def test_same_slope_centres_are_distinct(self):
        rows=self.data['macro_checks']['macros'][1:]
        self.assertEqual({(r['L'],r['q']) for r in rows},{(14,9)})
        self.assertEqual(len({r['B_u'] for r in rows}),3)
    def test_common_centre_boundary(self):
        # H(x)=(x-1)/2 commutes with all-ones maps centered at -1.
        for k in range(1,13):
            L,q,B=verify.positional('1'*k)
            self.assertEqual(B,3**k-2**k)
            self.assertEqual(2*B, B+3**k-2**k)
        # S=2^m-1 has m initial odd steps and finite valuation resource.
        for m in range(1,33):
            S=2**m-1
            self.assertEqual(verify.advance(S,'1'*m),3**m-1)
            self.assertEqual(verify.ord2(S+1),m)
    def test_exact_essential_kernels(self):
        self.assertEqual(self.data['unit_shadow']['universal_kernel'],[0,4])
        self.assertEqual(self.data['two_thirds_shadow']['universal_kernel'],[])
        for e in self.data['two_thirds_shadow']['essential_edges']:
            if e[0]==e[2]:self.assertIn((e[0],e[1]),[(-167,3),(-41,0)])

def corruptions():
    return [
      ('edge_omission',lambda d:d['unit_shadow']['edges'].pop()),
      ('edge_target',lambda d:d['unit_shadow']['edges'][0].__setitem__(2,0)),
      ('edge_source',lambda d:d['unit_shadow']['edges'][0].__setitem__(0,0)),
      ('edge_word',lambda d:d['unit_shadow']['edges'][0].__setitem__(3,'0'*11)),
      ('lower_bound',lambda d:d['unit_shadow']['integer_bounds'].__setitem__(0,-215)),
      ('rational_bound',lambda d:d['unit_shadow']['real_bounds'][0].__setitem__(0,-30042)),
      ('kernel_omission',lambda d:d['unit_shadow']['kernel'].pop()),
      ('kernel_addition',lambda d:d['unit_shadow']['kernel'].append(6)),
      ('layer_omission',lambda d:d['unit_shadow']['removed_layers'].pop()),
      ('ratio_denominator',lambda d:d['two_thirds_shadow'].__setitem__('b',1)),
      ('universal_scope',lambda d:d['two_thirds_shadow'].__setitem__('universal_kernel',[0])),
      ('q21_missing_case',lambda d:d['equal_coefficient']['q21_rows'].pop()),
      ('q22_number',lambda d:d['equal_coefficient']['witness'].__setitem__('q',21)),
      ('q22_source',lambda d:d['equal_coefficient']['witness'].__setitem__('small_source',7435082748)),
      ('bool_int',lambda d:d['unit_shadow'].__setitem__('p',True)),
      ('float_int',lambda d:d['macro_checks'].__setitem__('pairs',4092.0)),
      ('proof_flag',lambda d:d.__setitem__('proves_collatz',True)),
      ('ancestry_overclaim',lambda d:d.__setitem__('global_ancestor_existence_proved',True)),
      ('scope_loss',lambda d:d.__setitem__('peer_scope','all positive sources without synchronization')),
      ('infinite_promotion',lambda d:d['macro_checks'].__setitem__('infinite_positive_source_asserted',True)),
      ('macro_edit',lambda d:d['macro_checks']['macros'][0].__setitem__('u','1'*11)),
      ('missing_key',lambda d:d.pop('date')),
      ('extra_key',lambda d:d.__setitem__('accepted',True)),
      ('valuation_witness',lambda d:d['repeated_lifts']['rows'][0].__setitem__(4,1)),
      ('conjugacy_omission',lambda d:d['affine_closure_barrier']['complete_symbolic_contractions'].pop()),
      ('conjugacy_false_zero',lambda d:d['affine_closure_barrier']['complete_symbolic_contractions'][0].__setitem__(2,0)),
      ('conjugacy_scope',lambda d:d['affine_closure_barrier'].__setitem__('scope','all source descent impossible')),
      ('quarter_translation',lambda d:d['subalphabet_contractions']['families'][0].__setitem__('d',-94)),
    ]

for name,change in corruptions():
    def test(self,change=change):
        data=copy.deepcopy(self.data);change(data)
        with self.assertRaises((ValueError,TypeError,KeyError)):
            verify.verify_data(data)
    setattr(Checks,'test_reject_'+name,test)
del test  # Do not expose the dynamically bound unittest method as a pytest test.

import ast
import itertools
import subprocess
import sys
from fractions import Fraction
import pytest

def test_full_acceptance():
    out=verify.audit(ROOT)
    assert out['valid'] and out['ratio_integer_lifts']==334
    assert out['NG46_potentials_checked']==2 and not out['backlog_accepted']

@pytest.mark.parametrize('key',[k for k,v in verify.scope_reference().items() if v is False])
def test_scope_promotions_rejected(key):
    obj=verify.scope_reference();obj[key]=True
    with pytest.raises(ValueError):verify.same(obj,verify.scope_reference())

@pytest.mark.parametrize('key',['peer_domain','height_equal_domain','ratio_initial_integrality',
    'conjugacy_domain','coequal_minimality'])
def test_quantifiers_cannot_be_dropped(key):
    obj=verify.scope_reference();obj[key]='unrestricted'
    with pytest.raises(ValueError):verify.same(obj,verify.scope_reference())

@pytest.mark.parametrize('kind',['loss','threshold','ratio_lift','old_hash','missing','extra'])
def test_regression_tampering(kind):
    good=verify.regression_reference();bad=copy.deepcopy(good)
    if kind=='loss':bad['q21_loss_margins'][0][1]+=1
    elif kind=='threshold':bad['shrink_thresholds'][0][0]+=1
    elif kind=='ratio_lift':bad['ratio_edge_integer_lifts'][0][4]+=1
    elif kind=='old_hash':bad['historical_sha256']['phase41_formal.json']='0'*64
    elif kind=='missing':bad.pop('finite_only')
    else:bad['all_sources_classified']=True
    with pytest.raises(ValueError):verify.same(bad,good)

def test_duplicate_json_rejected():
    with pytest.raises(ValueError):json.loads('{"x":1,"x":2}',object_pairs_hook=verify.no_duplicates)

def test_no_generator_import():
    tree=ast.parse(Path(verify.__file__).read_text())
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): names=[a.name for a in node.names]
        elif isinstance(node,ast.ImportFrom): names=[node.module or '']
        else:continue
        assert all(not n.startswith('src') and 'synchronized_shadow_search' not in n for n in names)

def test_optimized_rejection(tmp_path):
    script='''
from verifier.verify_synchronized_shadow import same,scope_reference
d=scope_reference();d['all_ancestors_classified']=True
try:same(d,scope_reference())
except ValueError:raise SystemExit(0)
raise SystemExit(1)
'''
    done=subprocess.run([sys.executable,'-O','-c',script],cwd=ROOT.parent,capture_output=True,text=True)
    assert done.returncode==0,done.stderr

def test_forced_loop_certificate_rejects_new_cycle():
    edges=copy.deepcopy(verify.reconstruct()['unit_shadow']['essential_edges'])
    edges.append([-81,0,-77,'1'])
    with pytest.raises(ValueError):verify.forced_single_label(edges)

def test_mod3_omission_has_finite_falsifier():
    d,i,t,w=verify.reconstruct()['two_thirds_shadow']['edges'][0]
    L,q,B=verify.positional(verify.LEFT[i]);r=verify.source(verify.LEFT[i]);M=2**L
    cases=[2*(r+M*(100+k))+d for k in range(3)]
    assert sum(n%3==0 for n in cases)==1
    assert sum(n%3!=0 for n in cases)==2

def test_even_third_source_is_literal_but_not_initially_safe():
    s=15288571;word='01111111010100'
    assert verify.advance(s,verify.LEFT[1])==18367003
    assert verify.advance(s+3,word)==18367007
    assert not verify.safe_word(word)
    assert (s+3)//2<s

def test_q21_width_and_complete_one_move_reduction():
    e=verify.reconstruct()['equal_coefficient'];P=3**21
    mx=e['q21_allowance']+5*P-2**21
    assert mx-(P-2**21)<8*P
    assert len({row[0] for row in e['q21_rows']})==12
    assert {row[1] for row in e['q21_rows']}=={32,33}

def primitive(word):
    return next(word[:n] for n in range(1,len(word)+1)
        if len(word)%n==0 and word[:n]*(len(word)//n)==word)

def test_common_centre_commutation_and_finite_valuation_budget():
    groups={}
    for L in range(1,7):
        for bits in itertools.product('01',repeat=L):
            w=''.join(bits);_,q,B=verify.positional(w)
            if 3**q<=2**L:continue
            c=Fraction(-B,3**q-2**L);groups.setdefault(c,[]).append(w)
            assert c.denominator%2==1 and c<0
            for count in (1,2,3):
                whole=w*count;s=verify.source(whole) or 2**len(whole)
                y=verify.advance(s,whole);z=c.denominator*s-c.numerator
                assert verify.ord2(c.denominator*y-c.numerator)==verify.ord2(z)-count*L
    for c,words in groups.items():
        assert len({primitive(w) for w in words})==1
        for u,v in itertools.product(words,repeat=2):
            assert verify.positional(u+v)==verify.positional(v+u)
            assert u+v==v+u

def test_fixed_affine_is_not_general_rewriting():
    # Exact equality of maps can fail the integer-source condition.
    k,K,rem=verify.reconstruct()['affine_closure_barrier']['complete_symbolic_contractions'][0]
    r=Fraction(k,288);s=Fraction(k*34159-288*K,288*3299)
    assert 0<r<1 and rem!=0
    pool={B for w,B,res in verify.word_pool(14,9)}
    assert all(r*B-3299*s in pool for B in (34159,36751,34447))
    assert all((r*n+s).denominator!=1 for n in range(3299))

def test_mandatory_family_affine_and_decoder_regressions():
    reg=verify.regression_reference()
    assert len(reg['words'])==48 and len(reg['paths'])==28
    for w,B,r,y in reg['words']:
        L,q,b=verify.positional(w)
        assert b==int(B) and verify.valuation_decode(L,q,b)==w
        assert verify.source(w)==int(r)
        assert verify.advance(int(r) or 2**L,w)==int(y)

def test_ng43_safety_distinction_retained():
    a='0110110110110010110101101';b='0011111111111011100001100'
    assert verify.safe_word('1111'+a)
    assert verify.safe_word('1111'+b)
    qa=a.count('1');qb=b.count('1');assert qb>qa
    assert not verify.safe_word('1'*(4-(qb-qa))+b)
