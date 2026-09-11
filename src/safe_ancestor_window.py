"""Exact fixed-Q safe ancestor windows. No all-Q no-hit assertion."""
from __future__ import annotations
from fractions import Fraction
from dataclasses import dataclass

def positive_int(x, name):
    if type(x) is not int or x < 1: raise ValueError(f'{name} must be a positive integer')

def integer(x, name):
    if type(x) is not int: raise ValueError(f'{name} must be an integer')

def ceil_div(a:int,b:int)->int:return -((-a)//b)

def affine(word:str)->tuple[int,int,int,int]:
    if type(word) is not str or set(word)-{'0','1'}:raise ValueError('binary word required')
    A=1;B=0
    for j,s in enumerate(word):
        if s=='1':A*=3;B=3*B+(1<<j)
    return A,1<<len(word),B,word.count('1')

def literal(source:int,length:int):
    positive_int(source,'source');integer(length,'length')
    if length<0:raise ValueError('negative length')
    n=source;word=[];states=[source]
    for _ in range(length):
        s=n&1;word.append(str(s));n=(3*n+1)//2 if s else n//2;states.append(n)
    return n,''.join(word),states

def safe(word:str)->bool:
    if type(word) is not str or set(word)-{'0','1'}:raise ValueError('binary word required')
    A=1
    for j,s in enumerate(word,1):
        if s=='1':A*=3
        if A<=1<<j:return False
    return True

def bounds(q:int,L:int):
    positive_int(q,'q');integer(L,'L')
    A=3**q
    if L<q or A<=1<<L:return None
    fs=[];P=1
    for j in range(q):
        fs.append(P.bit_length()-1);P*=3
    ps=[min(fs[j],L-q+j) for j in range(q)]
    Bmin=A-(1<<q)
    Bmax=0;P=A
    for p in ps:
        P//=3
        Bmax+=(1<<p)*P
    return A,Bmin,Bmax,ps

def decode(q:int,L:int,B:int):
    """O(q) valuation steps, followed by O(L) output; no modular inverse."""
    if any(type(x) is not int for x in [q,L,B]) or q<0 or L<0 or q>L or B<0:return None
    if q==0:return '0'*L if B==0 else None
    rem=B;prev=-1;ps=[];P=3**(q-1)
    for _ in range(q):
        if rem<=0:return None
        p=(rem & -rem).bit_length()-1
        if p<=prev or p>=L:return None
        rem-= (1<<p)*P
        if rem<0:return None
        ps.append(p);prev=p;P//=3
    if rem:return None
    chars=['0']*L
    for p in ps:chars[p]='1'
    return ''.join(chars)

@dataclass(frozen=True)
class Witness:
    source:int
    endpoint:int
    length:int
    odd_count:int
    correction:int
    word:str
    kind:str


def scan(y:int,Q:int,gamma:Fraction=Fraction(1), tie_source:int|None=None):
    positive_int(y,'endpoint');integer(Q,'Q')
    if Q<0:raise ValueError('Q must be nonnegative')
    if not isinstance(gamma,Fraction) or gamma<1:raise ValueError('gamma must be an exact Fraction >=1')
    if tie_source is not None:positive_int(tie_source,'tie_source')
    witnesses=[];pairs=0;candidate_count=0;decodes=0
    if gamma==1 and tie_source is not None and y<tie_source:
        witnesses.append(Witness(y,y,0,0,0,'','equal_smaller'))
    for q in range(1,Q+1):
        A=3**q
        # c<y is necessary for a nonempty positive path, c>=gamma is the search band.
        lowL=max(q,(A//y).bit_length())
        highL=(A*gamma.denominator//gamma.numerator).bit_length()-1
        highL=min(highL,A.bit_length()-1)
        for L in range(lowL,highL+1):
            M=1<<L
            cmp=A*gamma.denominator-M*gamma.numerator
            if cmp<0 or (cmp==0 and tie_source is None):continue
            bd=bounds(q,L)
            if bd is None:continue
            _,Bmin,Bmax,_=bd;pairs+=1
            zlo=max(1,ceil_div(M*y-Bmax,A))
            zhi=(M*y-Bmin)//A
            if cmp==0:zhi=min(zhi,tie_source-1)
            step=4 if q>=2 else 2
            residue=3 if q>=2 else 1
            start=zlo+(residue-zlo)%step
            for z in range(start,zhi+1,step):
                candidate_count+=1
                B=M*y-A*z
                word=decode(q,L,B);decodes+=1
                if word is None or not safe(word):continue
                if (A*z+B)!=M*y:raise AssertionError('affine failed')
                witnesses.append(Witness(z,y,L,q,B,word,'strict' if cmp>0 else 'equal_smaller'))
    return witnesses,{'pairs':pairs,'integer_candidates':candidate_count,'decode_calls':decodes,'q_limit':Q,'complete_all_Q':False}
