#!/usr/bin/env python3
"""Exact finite checks for the substitution-arithmetic supplement. Standard library only.

This checks auxiliary identities, finite functional equations, and 32 declared
source-bound certificates. It is NOT a proof-assistant verification of the
universal theorem. It imports no generator.
"""
from __future__ import annotations
from collections import defaultdict
from fractions import Fraction
from itertools import product
from pathlib import Path
import hashlib, json, sys

if hasattr(sys,'set_int_max_str_digits'): sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parents[1]

class Reject(ValueError): pass

def need(condition,message):
    if not condition: raise Reject(message)

def integer(x):
    need(type(x) is int,'integer type')
    return x


def keys(value, expected):
    need(type(value) is dict and set(value)==set(expected.split()),'exact object keys')


def validate_schema(data):
    keys(data,'format status proves_collatz auxiliary_degree coefficient_conditions base_comparison auxiliaries finite_exclusion_certificates')
    need(data['format']=='collatz-binary-uniform-substitution-v1','format')
    for k in ('auxiliary_degree','coefficient_conditions'):integer(data[k])
    keys(data['base_comparison'],'left right')
    for v in data['base_comparison'].values():integer(v)
    need(type(data['auxiliaries']) is list and type(data['finite_exclusion_certificates']) is list,'array types')
    for row in data['auxiliaries']:
        keys(row,'u v seed degree_x_bound degree_y_max p q leading')
        need(integer(row['degree_x_bound'])==10,'auxiliary degree binding')
        need(integer(row['degree_y_max'])>=0,'nonnegative degree')
        need(type(row['p']) is list and type(row['q']) is list,'polynomial arrays')
        keys(row['leading'],'order poly')
        integer(row['leading']['order'])
        decode_bivariate([row['leading']['poly']])
    for row in data['finite_exclusion_certificates']:
        keys(row,'u v seed source_bound_power tower_level tower_scale first_difference eta leading_v2 height_exponent word_length source_bit_length source_hex_sha256 word_sha256 strict_integer_comparison')
        for k in ('source_bound_power','tower_level','tower_scale','first_difference','eta','leading_v2','height_exponent','word_length','source_bit_length'):
            need(integer(row[k])>=0,'nonnegative integer certificate field')
        need(1<=row['tower_level']<30,'bounded replay level')
        for k in ('word_sha256','source_hex_sha256'):
            s=row[k];need(type(s) is str and len(s)==64 and all(c in '0123456789abcdef' for c in s),'digest encoding')


def strict_load(path):
    def unique(pairs):
        out={}
        for k,v in pairs:
            need(k not in out,'duplicate JSON key');out[k]=v
        return out
    return json.loads(Path(path).read_text(),object_pairs_hook=unique)

def val2(x):
    need(type(x) is int and x!=0,'nonzero valuation')
    x=abs(x);return (x & -x).bit_length()-1

def clean(p): return {a:c for a,c in p.items() if c}
def plus(*polys):
    ans=defaultdict(int)
    for p in polys:
        for e,c in p.items(): ans[e]+=c
    return clean(ans)
def scale(p,c):return clean({e:a*c for e,a in p.items()})
def shift(p,a,b):return {(i+a,j+b):c for (i,j),c in p.items()}
def mul(p,q):
    out=defaultdict(int)
    for (i,j),a in p.items():
        for (k,l),b in q.items():out[i+k,j+l]+=a*b
    return clean(out)

def word_series(word):
    h=0;ans={}
    for j,c in enumerate(word):
        if c=='1':ans[j,h]=1;h+=1
    return ans

def decode_bivariate(rows):
    need(type(rows) is list and len(rows)<=11,'bounded x degree array')
    ans={}
    for i,p in enumerate(rows):
        need(type(p) is dict,'coefficient row')
        for j,c in p.items():
            need(type(j) is str and j.isascii() and j.isdigit() and str(int(j))==j,'degree encoding')
            need(int(j)<=64,'finite certificate y degree limit')
            need(type(c) is str and 0<len(c)<=128 and c.isascii() and (c[1:] if c.startswith('-') else c).isdigit(),'coefficient encoding')
            need(str(int(c))==c,'canonical coefficient encoding')
            need(int(c)!=0,'zero coefficient encoding')
            ans[i,int(j)]=int(c)
    return ans

def first_bits(u,v,seed,n):
    # Random access through base-r digits; no expanding-word iteration.
    r=len(u);images=(u,v);start=int(seed)
    ans=[]
    for t in range(n):
        digs=[];i=t
        while i:
            digs.append(i%r);i//=r
        state=start
        for d in reversed(digs):state=int(images[state][d])
        ans.append(str(state))
    return ''.join(ans)

def source_lift(word):
    # At time j, adding 2^j to a source increases T^j by 3^(odd count).
    source=0;endpoint=0;three=1;mod=1
    for ch in word:
        wanted=int(ch)
        if (endpoint & 1)!=wanted:
            source+=mod;endpoint+=three
        need((endpoint&1)==wanted,'lift parity')
        if wanted: endpoint=(3*endpoint+1)//2;three*=3
        else:endpoint//=2
        mod*=2
    need(0<=source<mod,'lift interval')
    return source

def coefficient_at_y(p,num,den):
    degree=max((j for (_,j) in p),default=0)
    return sum(c*num**j*den**(degree-j) for (_,j),c in p.items())

def finite_fe_checks():
    checks=0;nonzero=0
    words=[''.join(bits) for n in range(6) for bits in product('01',repeat=n)]
    for r in [2,3,4]:
        images=[''.join(bits) for bits in product('01',repeat=r)]
        for u in images:
            for v in images:
                A0=word_series(u);A1=word_series(v)
                q0=u.count('1');q1=v.count('1');delta=q1-q0
                C={(0,0):1,(r,q0):-1}
                B=plus(A1,scale(A0,-1),scale(shift(A1,r,q0),-1),shift(A0,r,q1))
                for poly in (A0,B,C):
                    need(all(0<=i<=2*r-1 and 0<=j<=2*r-1 for i,j in poly),'bidegree bound')
                need(sum(map(abs,B.values()))<=4*r,'B norm')
                if u!=v:
                    j0=next(i for i in range(r) if u[i]!=v[i])
                    low={e:c for e,c in B.items() if e[0]==j0}
                    need(len(low)==1 and abs(next(iter(low.values())))==1,'unit first difference')
                    need(min(i for i,j in B)==j0,'B lowest degree');nonzero+=1
                for w in words:
                    expanded=''.join((u,v)[int(b)] for b in w)
                    G=word_series(expanded)
                    n=len(w);ones=w.count('1')
                    GS={}
                    h=0
                    for i,c in enumerate(w):
                        if c=='1': GS[r*i,q0*i+delta*h]=1;h+=1
                    end_y=q0*n+delta*ones
                    right=plus(A0,scale(shift(A0,r*n,end_y),-1),mul(B,GS))
                    need(mul(C,G)==right,'finite polynomial functional equation')
                    checks+=1
    return checks,nonzero

def check_evidence(data, replay_sources=True):
    validate_schema(data)
    need(type(data) is dict and data.get('status')=='VERIFIED_FINITE','proposal status')
    need(data.get('proves_collatz') is False,'Collatz flag')
    need(data.get('auxiliary_degree')==10 and type(data['auxiliary_degree']) is int,'degree')
    need(data.get('coefficient_conditions')==21,'order target')
    need(data.get('base_comparison')=={'left':2**21,'right':3**13},'base margin')
    need(2**21>3**13,'integer base inequality')
    expected=[('01','10','0'),('011','110','1'),('01100','11110','1'),('11','10','1')]
    aux=data.get('auxiliaries');certs=data.get('finite_exclusion_certificates')
    need(type(aux) is list and len(aux)==4,'auxiliary scope')
    need(type(certs) is list and len(certs)==32,'certificate scope')
    info={};identity_count=0
    for row,key in zip(aux,expected):
        need((row.get('u'),row.get('v'),row.get('seed'))==key,'substitution binding')
        u,v,seed=key;r=len(u)
        need(len(v)==r and (u,v)[int(seed)][0]==seed,'fixed point convention')
        P=decode_bivariate(row['p']);Q=decode_bivariate(row['q'])
        need(primitive_y_content(row['p']+row['q']),'common y content')
        need(len(row['p'])==11 and len(row['q'])==11,'auxiliary x degree')
        need(Q,'nonzero Q')
        sequence=first_bits(u,v,seed,22)
        residual=plus(P,mul(Q,word_series(sequence)))
        for k in range(21):
            need(not any(i==k for i,j in residual),'Padé vanishing order')
            identity_count+=1
        lead={(0,j):c for (i,j),c in residual.items() if i==21}
        claimed={(0,int(j)):int(c) for j,c in row['leading']['poly'].items()}
        need(row['leading']['order']==21 and lead==claimed and lead,'leading coefficient')
        dy=max(j for i,j in P|Q)
        need(row['degree_y_max']==dy,'y degree')
        C=sum(abs(c) for c in P.values())+sum(abs(c) for c in Q.values())
        info[key]=(P,Q,lead,dy,C)
    seen=set();cache={};matched_bits=0
    for item in certs:
        u,v,seed=item['u'],item['v'],item['seed'];key=(u,v,seed)
        need(key in info,'certificate substitution')
        P,Q,lead,dy,C=info[key];r=len(u);delta=v.count('1')-u.count('1');eta=abs(delta)
        source_power=integer(item['source_bound_power']);k=integer(item['tower_level'])
        need(source_power in [8,16,32,64,128,256,512,1024] and 1<=k<={2:12,3:7,5:5}[r],'finite bounds')
        need((key,source_power) not in seen,'duplicate query');seen.add((key,source_power))
        m=r**k;deltak=delta**k
        yn,yd=(3**(-deltak),1) if deltak<0 else (1,3**deltak)
        lh=coefficient_at_y(lead,yn,yd);need(lh!=0,'leading specialization')
        nu=val2(lh);need(nu<m,'leading term dominates')
        j0=next(i for i,(a,b) in enumerate(zip(u,v)) if a!=b)
        sr=(r**k-1)//(r-1)
        se=(eta**k-1)//(eta-1) if eta!=1 else k
        E=10*m+(2*r-1)*(sr+se)+dy*eta**k
        N=21*m+nu+j0*sr+1
        need(item['tower_scale']==m and item['first_difference']==j0 and item['eta']==eta,'tower parameters')
        need(item['leading_v2']==nu and item['height_exponent']==E and item['word_length']==N,'certificate powers')
        need(item['strict_integer_comparison'] is True,'comparison flag')
        need((1<<(21*m+nu))>3*(1<<source_power)*C*(4*r)**k*3**E,'strict all-source height contradiction')
        if replay_sources:
            cachekey=(key,N)
            if cachekey not in cache:
                word=first_bits(u,v,seed,N);res=source_lift(word)
                cache[cachekey]=(word,res);matched_bits+=N
            word,res=cache[cachekey]
            need(res>(1<<source_power),'independent finite ordinary-source exclusion')
            need(item['source_bit_length']==res.bit_length(),'source size')
            need(item['source_hex_sha256']==hashlib.sha256(hex(res).encode()).hexdigest(),'source digest')
            need(item['word_sha256']==hashlib.sha256(word.encode()).hexdigest(),'word digest')
    return {'auxiliaries':4,'zero_coefficient_identities':identity_count,'leading_polynomials':4,
            'source_bound_queries':len(seen),'distinct_prefix_replays':len(cache),
            'distinct_prefix_total_bits':matched_bits}


def primitive_y_content(rows):
    """Euclidean gcd in Q[y], independent of generator polynomial software."""
    def trim(p):
        while p and not p[-1]:p.pop()
        return p
    def rem(p,q):
        p=p[:]
        while p and len(p)>=len(q):
            c=p[-1]/q[-1];d=len(p)-len(q)
            for j,a in enumerate(q):p[j+d]-=c*a
            trim(p)
        return p
    g=[]
    for row in rows:
        if not row:continue
        p=[Fraction(0)]*(max(map(int,row))+1)
        for j,c in row.items():p[int(j)]=Fraction(int(c))
        while p:g,p=p,rem(g,p)
        if len(g)==1:return True
    return len(g)==1


def evaluate(poly,x,y):
    return sum(c*x**i*y**j for (i,j),c in poly.items())


def rational_v2(value):
    value=Fraction(value)
    return val2(value.numerator)-val2(value.denominator)


def tower_checks():
    checks=0
    for u,v,seed in [('01','10','0'),('011','110','1'),('01100','11110','1'),('11','10','1')]:
        r=len(u);q0=u.count('1');delta=v.count('1')-q0;d=2*r-1
        A=word_series(u);A1=word_series(v)
        B=plus(A1,scale(A,-1),scale(shift(A1,r,q0),-1),shift(A,r,v.count('1')))
        C={(0,0):1,(r,q0):-1}
        j0=next(j for j in range(r) if u[j]!=v[j])
        N=32*r**3+1;x=Fraction(2);y=Fraction(1,3);p=0;sr=0
        f=Fraction(7);g=f+2**N;U=7;V=1;M=7
        for k in range(4):
            need(x==Fraction(2**(r**k),3**p),'tower x')
            need(y==Fraction(3)**(-delta**k),'tower y')
            need(0<=p<=r**k,'tower population')
            a,b,c=(evaluate(poly,x,y) for poly in (A,B,C))
            need(rational_v2(c)==0 and rational_v2(b)==j0*r**k,'tower unit/loss')
            denom=x.denominator**d*y.denominator**d
            aa,bb,cc=(z*denom for z in (a,b,c))
            need(all(z.denominator==1 for z in (aa,bb,cc)),'common homogenization')
            aa,bb,cc=map(int,(aa,bb,cc))
            U,V=cc*U-aa*V,bb*V
            f,g=(c*f-a)/b,(c*g-a)/b
            sr+=r**k
            need(Fraction(U,V)==f and V!=0,'rational integer tower')
            need(rational_v2(g-f)==N-j0*sr,'exact finite agreement loss')
            M*=4*r*3**(d*(r**k+abs(delta)**k))
            need(max(abs(U),abs(V))<=M,'height envelope')
            nextp=r*p+q0*delta**k
            need(nextp==q0*r**k+delta*p,'population recurrence equivalence')
            x,y=x**r*y**q0,y**delta;p=nextp
            checks+=1
    return checks


def check_regressions(data):
    words={'', '1'*64, '0'*64, '10'*32}
    for m in range(1,13):
        for n in ((1<<m)-1,(1<<(3*m))-5):
            bits=[]
            for j in range(40):
                bit=n&1;bits.append(str(bit));n=(n*(3 if bit else 1)+bit)//2
            words.add(''.join(bits))
    for size in range(1,4):
        for mask in range(1<<size):
            words.add(''.join('111' if mask>>j&1 else '110' for j in range(size)))
    for r in range(5):
        for s in range(5):words.add('11101'*r+'1100'*s)
    rows=[]
    for w in sorted(words,key=lambda x:(len(x),x)):
        source=source_lift(w);q=w.count('1');h=0;B=0
        for j,bit in enumerate(w):
            if bit=='1':B+=2**j*3**(q-1-h);h+=1
        endpoint=Fraction(3**q*source+B,2**len(w))
        need(endpoint.denominator==1,'family affine endpoint')
        rows.append({'word':w,'source':source,'endpoint':int(endpoint)})
    expected={'schema_version':1,'family_rows':rows,'proves_collatz':False}
    need(json.dumps(data,sort_keys=True)==json.dumps(expected,sort_keys=True),'complete typed family reconstruction')
    need(source_lift('10'*32)==1 and source_lift('1'*64)==2**64-1 and source_lift('0'*64)==0,'periodic controls')
    return len(rows)


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir',type=Path,default=ROOT/'artifacts')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    data=strict_load(args.artifact_dir/'substitution_arithmetic_evidence.json')
    aux=strict_load(args.artifact_dir/'substitution_arithmetic_auxiliaries.json')
    need(json.dumps(aux,sort_keys=True)==json.dumps(data['auxiliaries'],sort_keys=True),'auxiliary artifact binding')
    result=check_evidence(data)  # Acceptance never skips canonical-source replay.
    checks,nonzero=finite_fe_checks()
    result.update({'finite_functional_equations':checks,'distinct_image_first_difference_checks':nonzero,
        'tower_error_height_checks':tower_checks(),
        'family_words':check_regressions(strict_load(args.artifact_dir/'substitution_arithmetic_regressions.json')),
        'valid':True,'generator_imported':False,'universal_proof_machine_formalized':False,
        'EXT08_used':False,'general_orbit_coverage_proved':False,'proves_collatz':False})
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
