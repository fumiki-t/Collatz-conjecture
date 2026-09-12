#!/usr/bin/env python3
import copy,json,unittest
from pathlib import Path
from verifier import verify_substitution_arithmetic as verify

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.data=json.loads((Path(__file__).resolve().parents[1]/'artifacts/substitution_arithmetic_evidence.json').read_text())
    def reject(self,mutate):
        d=copy.deepcopy(self.data);mutate(d)
        with self.assertRaises(verify.Reject):verify.check_evidence(d,replay_sources=False)
    def test_proposal(self):verify.check_evidence(self.data,replay_sources=False)
    def test_flag(self):self.reject(lambda d:d.__setitem__('proves_collatz',True))
    def test_status(self):self.reject(lambda d:d.__setitem__('status','VERIFIED_THEOREM'))
    def test_degree(self):self.reject(lambda d:d.__setitem__('auxiliary_degree',9))
    def test_degree_float(self):self.reject(lambda d:d.__setitem__('auxiliary_degree',10.0))
    def test_base(self):self.reject(lambda d:d['base_comparison'].__setitem__('left',2**20))
    def test_scope(self):self.reject(lambda d:d['finite_exclusion_certificates'].pop())
    def test_duplicate(self):self.reject(lambda d:d['finite_exclusion_certificates'].__setitem__(1,copy.deepcopy(d['finite_exclusion_certificates'][0])))
    def test_bound_float(self):self.reject(lambda d:d['finite_exclusion_certificates'][0].__setitem__('source_bound_power',8.0))
    def test_level(self):self.reject(lambda d:d['finite_exclusion_certificates'][0].__setitem__('tower_level',1))
    def test_N(self):self.reject(lambda d:d['finite_exclusion_certificates'][0].__setitem__('word_length',1))
    def test_eta(self):self.reject(lambda d:d['finite_exclusion_certificates'][0].__setitem__('eta',100))
    def test_height(self):self.reject(lambda d:d['finite_exclusion_certificates'][0].__setitem__('height_exponent',0))
    def test_leading(self):self.reject(lambda d:d['auxiliaries'][0]['leading']['poly'].__setitem__('0','1'))
    def test_P(self):self.reject(lambda d:d['auxiliaries'][0]['p'][0].__setitem__('0','1234567'))
    def test_Q(self):self.reject(lambda d:d['auxiliaries'][0]['q'][0].__setitem__('0','1234567'))
    def test_substitution(self):self.reject(lambda d:d['auxiliaries'][0].__setitem__('u','00'))
    def test_seed(self):self.reject(lambda d:d['auxiliaries'][0].__setitem__('seed','1'))
    def test_safe_r5_invariant(self):
        for symbol,image in [('0','01100'),('1','11110')]:
            lower=2 if symbol=='0' else 0
            for j,out in enumerate(image):
                D=3*image[:j].count('1')-2*j
                self.assertGreaterEqual(2*lower+D,2 if out=='0' else 0)
    def test_unit_exception(self):
        # Length-one identity substitution has every word as a fixed point,
        # so the universal theorem MUST retain r>=2.
        self.assertEqual(''.join(('0','1')[int(c)] for c in '010111'),'010111')
    def test_periodic_scope(self):
        # Constant word 111... has rational 2-adic source -1; aperiodicity is essential.
        w='1'*64
        self.assertEqual(verify.source_lift(w),(1<<64)-1)
    def test_positive_periodic_exception(self):
        w=verify.first_bits('010','101','1',64)
        self.assertEqual(w,'10'*32)
        self.assertEqual(verify.source_lift(w),1)
    def test_periodic_zero(self):self.assertEqual(verify.source_lift('0'*64),0)

    def test_tower_error_and_height(self):self.assertEqual(verify.tower_checks(),16)
    def test_common_y_content(self):
        self.assertFalse(verify.primitive_y_content([{'0':'-1','1':'1'},{'1':'-1','2':'1'}]))
        self.assertTrue(verify.primitive_y_content([{'0':'-1','1':'1'},{'0':'1'}]))
    def test_specialization_can_kill_a_nonzero_polynomial(self):
        self.assertEqual(verify.coefficient_at_y({(0,0):-1,(0,1):1},1,1),0)
        with self.assertRaises(verify.Reject):verify.val2(0)
    def test_valuation_loss_is_real(self):
        from fractions import Fraction
        # u=11,v=10: first difference at 1. Dividing by B loses one bit here.
        B=verify.plus(verify.word_series('10'),verify.scale(verify.word_series('11'),-1),
            verify.scale(verify.shift(verify.word_series('10'),2,2),-1),
            verify.shift(verify.word_series('11'),2,1))
        self.assertEqual(verify.rational_v2(verify.evaluate(B,Fraction(2),Fraction(1,3))),1)
    def test_family_replay(self):
        path=Path(__file__).resolve().parents[1]/'artifacts/substitution_arithmetic_regressions.json'
        self.assertGreater(verify.check_regressions(verify.strict_load(path)),40)
    def test_duplicate_json(self):
        import tempfile
        with tempfile.TemporaryDirectory() as root:
            path=Path(root)/'bad.json';path.write_text('{"a":1,"a":1}')
            with self.assertRaises(verify.Reject):verify.strict_load(path)
    def test_degree_alias(self):
        with self.assertRaises(verify.Reject):verify.decode_bivariate([{'00':'1'}])
    def test_nonprimitive_auxiliary_rejected(self):
        def mutate(d):
            row=d['auxiliaries'][0]
            for key in ('p','q'):
                row[key]=[{str(int(j)+1):c for j,c in p.items()} for p in row[key]]
        self.reject(mutate)
    def test_all_source_replay_digest_rejections(self):
        # All identities are cheap; stop on the first (2690-bit) replay.
        for key in ('word_sha256','source_hex_sha256','source_bit_length'):
            d=copy.deepcopy(self.data)
            d['finite_exclusion_certificates'][0][key]=1 if key=='source_bit_length' else '0'*64
            with self.subTest(key=key),self.assertRaises(verify.Reject):verify.check_evidence(d)


import pytest


@pytest.mark.parametrize('key',['coefficient_conditions','auxiliary_degree'])
@pytest.mark.parametrize('value',[True,21.0,None])
def test_top_numeric_types(key,value):
    d=json.loads((Path(__file__).resolve().parents[1]/'artifacts/substitution_arithmetic_evidence.json').read_text())
    d[key]=value
    with pytest.raises(verify.Reject):verify.check_evidence(d,replay_sources=False)


@pytest.mark.parametrize('key',['source_bound_power','tower_level','tower_scale','first_difference','eta','leading_v2','height_exponent','word_length','source_bit_length'])
@pytest.mark.parametrize('convert',[float,bool])
def test_certificate_numeric_types(key,convert):
    d=json.loads((Path(__file__).resolve().parents[1]/'artifacts/substitution_arithmetic_evidence.json').read_text())
    row=d['finite_exclusion_certificates'][0];row[key]=convert(row[key])
    with pytest.raises(verify.Reject):verify.check_evidence(d,replay_sources=False)


@pytest.mark.parametrize('location',['top','aux','cert','leading','base'])
def test_unknown_fields(location):
    d=json.loads((Path(__file__).resolve().parents[1]/'artifacts/substitution_arithmetic_evidence.json').read_text())
    row={'top':d,'aux':d['auxiliaries'][0],'cert':d['finite_exclusion_certificates'][0],
         'leading':d['auxiliaries'][0]['leading'],'base':d['base_comparison']}[location]
    row['proved_everything']=True
    with pytest.raises(verify.Reject):verify.check_evidence(d,replay_sources=False)


@pytest.mark.parametrize('poly',[{'65':'1'},{'0':'--1'},{'0':'-0'},{'0':'1.0'},{'0':'0'},{'0':True}])
def test_malformed_or_unbounded_polynomial(poly):
    with pytest.raises(verify.Reject):verify.decode_bivariate([poly])


def test_oversized_tower_rejected_before_exponentiation():
    d=json.loads((Path(__file__).resolve().parents[1]/'artifacts/substitution_arithmetic_evidence.json').read_text())
    d['finite_exclusion_certificates'][16]['tower_level']=29
    with pytest.raises(verify.Reject):verify.check_evidence(d,replay_sources=False)


def test_verifier_import_boundary():
    import ast
    tree=ast.parse(Path(verify.__file__).read_text())
    imports=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):imports.extend(n.name for n in node.names)
        if isinstance(node,ast.ImportFrom):imports.append(node.module or '')
    assert not any(n.split('.')[0] in {'src','sympy','substitution_auxiliary','substitution_arithmetic_search'} for n in imports)


if __name__=='__main__':unittest.main()
