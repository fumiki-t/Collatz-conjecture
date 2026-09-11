"""Boundary regressions; not an independent proof of an infinite theorem."""
from fractions import Fraction
import copy
import unittest
from src.safe_ancestor_window import bounds,decode,scan,literal,affine
from src.safe_root_frontier import search
from verifier.verify_safe_root_certificate import check

class BoundaryTests(unittest.TestCase):
    def test_empty_target_one(self):
        c=search(1,0)
        self.assertEqual(c['status'],'NO_LEX_IMPROVEMENT')
        self.assertEqual(c['source_bound'],0)
        self.assertTrue(check(c))

    def test_coefficient_below_one_empty_witness(self):
        c=search(1,2)
        self.assertEqual(c['status'],'IMPROVEMENT')
        self.assertEqual(c['witness'],{'source':1,'word':''})
        self.assertTrue(check(c))

    def test_generic_empty_tie(self):
        hs,st=scan(3,0,Fraction(1),4)
        self.assertEqual([(h.source,h.word,h.kind) for h in hs],[(3,'','equal_smaller')])
        self.assertFalse(st['complete_all_Q'])
        self.assertFalse(scan(3,0,Fraction(1),3)[0])

    def test_even_unsafe_original_and_valley_replacement(self):
        y,w,_=literal(6,3)
        self.assertEqual((y,w),(8,'011'))
        hs,_=scan(8,2,Fraction(1))
        self.assertIn((3,'11'),[(h.source,h.word) for h in hs])
        self.assertNotIn((6,'011'),[(h.source,h.word) for h in hs])

    def test_q_one_and_invalid_domains(self):
        self.assertEqual(bounds(1,1)[:3],(3,1,1))
        self.assertIsNone(bounds(1,2))
        self.assertIsNone(bounds(3,2))
        with self.assertRaises(ValueError):bounds(True,2)
        with self.assertRaises(ValueError):scan(10,3,1.0)
        with self.assertRaises(ValueError):scan(10,-1,Fraction(1))

    def test_decoder_boundaries(self):
        self.assertEqual(decode(0,0,0),'')
        self.assertEqual(decode(0,3,0),'000')
        self.assertEqual(decode(3,3,19),'111')
        for triple in [(1,0,1),(0,3,1),(2,2,-1),(2,2,6),(True,3,19)]:
            self.assertIsNone(decode(*triple))

    def test_budget_is_unknown(self):
        c=search(703,80,limit=1)
        self.assertEqual(c['status'],'UNKNOWN')
        with self.assertRaises(ValueError):check(c)

    def test_known_all_length_controls(self):
        for S,L,count in [(7,4,2),(703,80,44)]:
            c=search(S,L)
            self.assertEqual(c['status'],'NO_LEX_IMPROVEMENT')
            self.assertEqual(c['diagnostics']['frontier_size'],count)
            self.assertTrue(check(c))

    def test_safe_equal_coefficient_witness(self):
        S=7435082751;y,w,_=literal(S,34);A,M,_,_=affine(w)
        hs,_=scan(y,22,Fraction(A,M),S)
        self.assertIn((7435082747,22,34,'equal_smaller'),[(h.source,h.odd_count,h.length,h.kind)for h in hs])

    def test_normalization_equality_for_same_source(self):
        c=search(703,80)
        normal=next(t for t in c['traces'] if t['cut']=='normalization')
        self.assertEqual(normal['source'],703)
        # Search's finite boundary equality is accepted for z=S.
        self.assertTrue(check(c))
        b=copy.deepcopy(c);b['traces'].remove(normal)
        with self.assertRaises(ValueError):check(b)

    def test_smaller_source_equality_requires_continuing(self):
        d='1101101101011011011010110110101101'
        a='1111111111011100011111001100001100'
        left='11011111000'*2+d
        right='11111010100'*2+a
        A,M,B,_=affine(left)
        z=(-B*pow(A,-1,M))%M
        S=z+4
        y0,actual,_=literal(z,len(left))
        self.assertEqual(actual,left)
        self.assertEqual(literal(S,len(right))[:2],(y0,right))
        self.assertEqual(y0%2,0)
        y=y0//2;gamma=Fraction(A,2*M)
        self.assertGreater(gamma,1)
        H=Fraction(y,gamma)
        self.assertEqual(Fraction(M*y0,A),H)
        self.assertLess(z,S)
        self.assertNotEqual(y0,y)
        # At this equality state the source has not reached the target yet;
        # one more even step is an equal-coefficient, smaller-source hit.
        self.assertFalse(Fraction(M*y0,A)>H or (Fraction(M*y0,A)==H and z>=S))
        self.assertEqual(literal(z,len(left)+1)[0],y)

if __name__=='__main__':unittest.main()
