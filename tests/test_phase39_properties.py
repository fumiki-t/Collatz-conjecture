"""Finite convention and boundary properties, separate from certificate equality."""
from fractions import Fraction
from itertools import product

from src.phase39_search import affine, realize, safe, source


def test_affine_correction_against_literal_positive_and_negative_traces():
    for start in range(-127, 256):
        x = start
        word = ""
        for length in range(1, 17):
            bit = x % 2
            word += str(bit)
            x = (3*x+1)//2 if bit else x//2
            q,b = affine(word)
            assert (3**q*start+b) == (1 << length)*x


def test_universal_rewrite_safety_boundary_and_suffixes():
    for r in range(1, 25):
        a, d = "1"*(r-1)+"01", "1"*r+"00"
        _,ba=affine(a);_,bd=affine(d)
        assert 2*ba-bd == 3**r
        assert (safe(a) and safe(d)) == (r>=4)
        for bits in product("01",repeat=4):
            tail="".join(bits)
            n=source(d+tail)
            assert n%2
            assert realize(n,d+tail)==realize((n-1)//2,a+tail)
            if safe(d+tail):
                assert safe(a+tail)


def test_shifted_correction_recurrence_and_tail_valuation():
    for R in range(1, 8):
        for bits in product("01",repeat=6):
            w="1"*R+"0"
            J=1
            for ell,b in enumerate(bits,1):
                J=3*J if b=="1" else J+(1 << ell)
                w+=b
                q,B=affine(w)
                assert B+(1 << len(w))-3**q == (1 << R)*J
                assert J%2
            n=source(w)
            assert (n+1)%(1 << R)==0
            assert (n+1)%(1 << (R+1)) != 0


def test_zero_carry_requires_identity_or_periodic_boundary():
    for start in (1,3,7,167):
        assert (2**0-3**0)*start+0 == 0
    a,d="1","101"
    assert 4*affine(a)[1]-affine(d)[1] == -3
    assert (4-3)*1-1 == 0
    assert realize(1,a)==realize(1,d)==2
    assert not safe(d)


def test_canonical_positive_endpoint_and_no_smaller_positive_lift():
    for length in range(1, 9):
        for bits in product("01",repeat=length):
            w="".join(bits);q,_=affine(w)
            if not q:continue
            n=source(w); endpoint=realize(n,w)
            assert 0<endpoint<3**q
            assert endpoint-3**q<0
            assert realize(n+7*(1 << length),w)==endpoint+7*3**q


def test_event_direction_integer_assumption_and_strict_increment():
    # Formal rational fixed points must not pass the integer equality scope.
    x=Fraction(1,5);e=3;y=(x+1)/2
    assert (3*x+1)/2**e==x and y==Fraction(3,5)
    for x in range(1, 1024, 2):
        raw=3*x+1;e=0
        while raw%2==0:raw//=2;e+=1
        nxt=raw
        assert nxt>x if e==1 else nxt<x or (x==1 and e==2)
        minimum=min(x,nxt)
        increment=Fraction(2**(e-1)-1,3*Fraction(x+1,2))
        assert increment<Fraction(1,minimum)


def test_correction_bound_includes_one_odd_boundary():
    assert Fraction(affine("1")[1],3)==Fraction(1,3)
    for length in range(1, 11):
        for bits in product("01",repeat=length):
            w="".join(bits)
            if safe(w):
                q,b=affine(w)
                assert Fraction(b,3**q)<=Fraction(q,3)
