"""Regenerate finite substitution certificates; SymPy is generator-only."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
if hasattr(__import__('sys'),'set_int_max_str_digits'): __import__('sys').set_int_max_str_digits(0)


def v2(n):
    if n==0: raise ValueError('zero valuation')
    n=abs(n);return (n & -n).bit_length()-1

def prefix(u,v,seed,n):
    w=seed
    while len(w)<n:
        w=''.join(u if b=='0' else v for b in w)
    return w[:n]

def source_affine(word):
    b=0;q=0;two=1
    for ch in word:
        if ch=='1': b=3*b+two;q+=1
        two*=2
    residue=(-b*pow(pow(3,q),-1,two))%two
    return residue

def degree_y(row):
    return max([int(e) for p in row['p']+row['q'] for e in p] or [0])

def norm(row):
    return sum(abs(int(c)) for pp in row['p']+row['q'] for c in pp.values())

def poly_y_homog(p,num,den):
    d=max(map(int,p),default=0)
    return sum(int(c)*num**int(e)*den**(d-int(e)) for e,c in p.items()),d


def regressions():
    from itertools import product
    words={'', '1'*64, '0'*64, '10'*32}
    for m in range(1,13):
        for source in (2**m-1,8**m-5):
            word=''
            for _ in range(40):
                bit=source%2;word+=str(bit)
                source=(3*source+1)//2 if bit else source//2
            words.add(word)
    for n in range(1,4):
        words.update(''.join(t) for t in product(('110','111'),repeat=n))
    words.update('11101'*r+'1100'*s for r in range(5) for s in range(5))
    rows=[]
    for word in sorted(words,key=lambda w:(len(w),w)):
        source=source_affine(word);endpoint=source;bits=''
        for _ in word:
            bit=endpoint%2;bits+=str(bit)
            endpoint=(3*endpoint+1)//2 if bit else endpoint//2
        if bits!=word:raise ValueError('literal parity')
        rows.append({'word':word,'source':source,'endpoint':endpoint})
    return {'schema_version':1,'family_rows':rows,'proves_collatz':False}

from src.substitution_auxiliary import auxiliary


def generate(artifact_dir):
    artifact_dir.mkdir(parents=True, exist_ok=True)
    rows=[auxiliary(*key) for key in [('01','10','0'),('011','110','1'),('01100','11110','1'),('11','10','1')]]
    (artifact_dir/'substitution_arithmetic_auxiliaries.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')

    cert=[]
    for row in rows:
        u,v,seed=row['u'],row['v'],row['seed'];r=len(u);delta=v.count('1')-u.count('1');eta=abs(delta)
        first=next(i for i,(a,b) in enumerate(zip(u,v)) if a!=b)
        dy=degree_y(row); c=norm(row)
        for B in [8,16,32,64,128,256,512,1024]:
            for k in range(1,30):
                m=r**k;dk=delta**k
                yn=3**(-dk) if dk<0 else 1;yd=3**dk if dk>=0 else 1
                lead,ld=poly_y_homog(row['leading']['poly'],yn,yd)
                if lead==0:continue
                nu=v2(lead)
                if nu>=m:continue
                sr=sum(r**j for j in range(k));se=sum(eta**j for j in range(k))
                E=10*m+(2*r-1)*(sr+se)+dy*eta**k
                lower=1 << (21*m+nu)
                upper=3*(1<<B)*c*(4*r)**k *3**E
                if lower>upper:
                    N=21*m+nu+first*sr+1
                    word=prefix(u,v,seed,N);res=source_affine(word)
                    if not res>(1<<B): raise AssertionError(('source lower bound',u,v,B,k,N))
                    item={'u':u,'v':v,'seed':seed,'source_bound_power':B,'tower_level':k,
                          'tower_scale':m,'first_difference':first,'eta':eta,'leading_v2':nu,
                          'height_exponent':E,'word_length':N,'source_bit_length':res.bit_length(),
                          'source_hex_sha256':hashlib.sha256(hex(res).encode()).hexdigest(),
                          'word_sha256':hashlib.sha256(word.encode()).hexdigest(),
                          'strict_integer_comparison':True}
                    cert.append(item)
                    print(u,v,B,'k',k,'N',N,'source bits',res.bit_length(),flush=True)
                    break
            else:raise AssertionError(('no certificate',u,v,B))
    summary={'format':'collatz-binary-uniform-substitution-v1',
             'status':'VERIFIED_FINITE','proves_collatz':False,
             'auxiliary_degree':10,'coefficient_conditions':21,
             'base_comparison':{'left':2**21,'right':3**13},
             'auxiliaries':rows,'finite_exclusion_certificates':cert}
    (artifact_dir/'substitution_arithmetic_evidence.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    (artifact_dir/'substitution_arithmetic_regressions.json').write_text(json.dumps(regressions(),indent=2,sort_keys=True)+'\n')


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir',type=Path,default=Path('artifacts'))
    generate(parser.parse_args().artifact_dir)


if __name__=='__main__':main()
