"""Exact exploratory evidence for transient orbit sparsity.
No theorem status or full Collatz proof is asserted by this program.
"""
from __future__ import annotations
import argparse, hashlib, json, math
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NMAX = 500

def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()

def digest(rows):
    h = hashlib.sha256()
    for row in rows:
        h.update(canon(row)); h.update(b'\n')
    return h.hexdigest()

def frac(x):
    x = Fraction(x)
    return [str(x.numerator), str(x.denominator)]

def T(n):
    return (3*n+1)//2 if n&1 else n//2

def first_repeat(s, limit=100000):
    values=[]; seen={}; x=s
    while x not in seen:
        if len(values)>=limit:
            raise RuntimeError('finite trace cap exhausted; UNKNOWN, not evidence')
        seen[x]=len(values); values.append(x); x=T(x)
    return values, seen[x], len(values)-seen[x]

def capacities():
    A=[1]; O=[1]; powers=[3**j for j in range(NMAX+1)]
    rows=[[0,1,1]]
    for N in range(1,NMAX+1):
        W=1<<N; a=o=0
        for s in range(N+1):
            span_num=powers[s]*(W-1)+((1<<(N-s))-1)*(powers[s]-(1<<s))
            Y=1+span_num//W
            m=(Y-1).bit_length()
            c=math.comb(N,s)
            a+=min(c,A[m]) if m<N else c
            if s:
                c=math.comb(N-1,s-1)
                o+=min(c,A[m]) if m<N else c
        A.append(min(W,N+a)); O.append(min(W//2,N+o))
        rows.append([N,str(A[-1]),str(O[-1])])
    tail=1440*Fraction(44,45)**501
    F=lambda m: sum((Fraction(O[n],1<<n) for n in range(m,NMAX+1)),tail)
    rtotal=sum((Fraction(1,n) for n in range(1,32,2)),Fraction(0))+F(5)
    return A,O,{
        'Nmax':NMAX,'rows':rows,'row_digest':digest(rows),
        'tail':frac(tail),'F19':frac(F(19)),'F49':frac(F(49)),
        'odd_reciprocal_global_upper':frac(rtotal),
        'checks':{'F19_lt_15_over_2':F(19)<Fraction(15,2),
                  'F49_lt_2079_over_1000':F(49)<Fraction(2079,1000),
                  'global_lt_82_over_5':rtotal<Fraction(82,5)}
    }

def constant_checks():
    L2=Fraction(842,1215)
    # log 13 = 3 log 2 + log(13/8), atanh parameter (13/8-1)/(13/8+1)=5/21.
    L13=3*L2+2*Fraction(5,21)
    comparisons={
        'alpha_theta':3**14 < 2**23,
        'entropy':23**690 < 2**667*14**420*9**270,
        'low_at_135':24**690*3**(406*135) <= 2**(667*135),
        'low_fails_134':24**690*3**(406*134) > 2**(667*134),
        'low_persists':3**406 < 2**667,
        'recursive_size_at_57':4**23*3**(14*57) < 2**(23*57),
        'boundary_loss_at_135':135**30 < 2**(29*134),
        'boundary_loss_persists':136**30 < 2**29*135**30,
        'base_power':134<150,
        'geometric_ratio':2*44**30>45**30,
        'half_log_gap':Fraction(2079,1000)<3*L2,
        'factor_13':L13>Fraction(5,2),
        'factor_256':Fraction(82,5)<24*L2,
    }
    assert all(comparisons.values())
    return {'comparisons':comparisons,'log2_lower':frac(L2),'log13_lower':frac(L13)}

def affine_audit():
    rows=[]; extrema=[]
    for N in range(15):
        lo=[None]*(N+1); hi=[None]*(N+1)
        for mask in range(1<<N):
            q=mask.bit_count(); B=0; right=q
            for j in range(N):
                if (mask>>j)&1:
                    right-=1; B+=(1<<j)*3**right
            lo[q]=B if lo[q] is None else min(lo[q],B)
            hi[q]=B if hi[q] is None else max(hi[q],B)
            r=(-B*pow(3**q,-1,1<<N))%(1<<N) if N else 0
            rows.append([N,mask,q,B,r])
        for q in range(N+1):
            assert lo[q]==3**q-2**q
            assert hi[q]==2**(N-q)*(3**q-2**q)
            extrema.append([N,q,lo[q],hi[q]])
    return {'word_scope':'all words, length 0..14','words':len(rows),
            'word_digest':digest(rows),'extrema':extrema}

def prefix_audit(A,O):
    sources=list(range(1,128))+[703]
    rows=[]; nonzero=0; max_deleted=0; max_factor=Fraction(0)
    for S in sources:
        values,mu,p=first_repeat(S)
        ms=sorted(set(min(x,len(values)) for x in [1,2,3,4,8,16,len(values)]))
        if S==703 and 80<=len(values): ms=sorted(set(ms+[80]))
        for M in ms:
            P=values[:M]; ps=sorted(P)
            prod=Fraction(1)
            for v in P:
                if v&1: prod*=Fraction(3*v+1,3*v)
            max_factor=max(max_factor,prod)
            Q=sum(v&1 for v in P)
            assert prod==Fraction((1<<M)*T(P[-1]),3**Q*S)
            assert prod<256
            hp=[0]
            for v in P: hp.append(hp[-1]+(v&1))
            for N in range(1,9):
                W=1<<N
                starts=sorted(set([1,S,max(1,ps[-1]-W+1),ps[len(ps)//2],max(1,ps[0]-W//2)]))
                for a in starts:
                    idx=[i for i,x in enumerate(P) if a<=x<a+W]
                    retained=[i for i in idx if i+N<M]
                    deleted=len(idx)-len(retained)
                    assert deleted<=N
                    if deleted: nonzero+=1
                    max_deleted=max(max_deleted,deleted)
                    groups={}
                    for i in retained:
                        q=hp[i+N]-hp[i]
                        groups.setdefault(q,[]).append(P[i+N])
                    assert len(set(P[i+N] for i in retained))==len(retained)
                    for q,ys in groups.items():
                        Y=1+(3**q*(W-1)+(2**(N-q)-1)*(3**q-2**q))//W
                        assert max(ys)-min(ys)+1<=Y
                        mm=(Y-1).bit_length()
                        assert len(ys)<=math.comb(N,q)
                        if mm<N: assert len(ys)<=A[mm]
                    assert len(idx)<=A[N]
                    assert sum(P[i]&1 for i in idx)<=O[N]
                    rows.append([S,M,N,a,len(idx),len(retained),
                                 [[q, sorted(ys)] for q,ys in sorted(groups.items())]])
    # Actual orbits with equality in the N-loss estimate on the full orbit set.
    sharp=[]
    for m in [3,4,8,16,32,64,128,256,512,1024]:
        vals,mu,p=first_repeat(1<<m)
        assert p==2 and mu==m-1
        for N in sorted(set([1,2,min(8,mu),mu])):
            if N>mu: continue
            image=[]
            for x in vals:
                for _ in range(N): x=T(x)
                image.append(x)
            loss=len(vals)-len(set(image))
            assert loss==N
            sharp.append([m,N,len(vals),len(set(image)),loss])
    return {'source_scope':'1..127 and 703; specified prefix lengths and all listed translated windows',
            'source_count':len(sources),'window_cases':len(rows),'window_digest':digest(rows),
            'nonzero_terminal_deletions':nonzero,'max_terminal_deletions':max_deleted,
            'largest_finite_product':frac(max_factor),'sharp_loss_rows':sharp}

def normalization(source, length):
    if type(source) is not int or source < 1 or type(length) is not int or length < 0:
        raise ValueError('positive integer source and nonnegative integer length required')
    seen=set(); x=source; ratio=Fraction(1); q=0
    for _ in range(length):
        if x in seen: raise ValueError('repeated input')
        seen.add(x)
        if x&1: ratio*=Fraction(3*x+1,3*x); q+=1
        x=T(x)
    floor=min(seen,default=source)
    bound=2 if floor>=2**49 else 13 if floor>=2**19 else 256
    assert ratio<bound
    return [str(source),length,str(x),q,frac(ratio),str(floor),bound]

def regressions():
    from itertools import product
    words={'11101','1100'}
    for n in range(1,5):
        words.update(''.join(p) for p in product(('110','111'),repeat=n))
    words.update('11101'*r+'1100'*s for r in range(1,5) for s in range(1,5))
    word_rows=[]
    for w in sorted(words):
        b=q=0
        for j,bit in enumerate(w):
            if bit=='1': b=3*b+2**j; q+=1
        mod=2**len(w); residue=(-b*pow(3**q,-1,mod))%mod
        source=residue or mod; x=source; literal=''
        for _ in w: literal+=str(x%2); x=T(x)
        assert literal==w
        word_rows.append([w,str(b),str(residue),str(x)])
    sources=sorted({2**m-1 for m in range(1,13)}|{8**m-5 for m in range(1,13)})
    paths=[normalization(s,min(64,len(first_repeat(s)[0]))) for s in sources]
    paths+=[normalization(1,0),normalization(1,2)]
    paths += [normalization(2**m-1,m) for m in (20,50,72)]
    k_rows=[]
    for row in paths:
        s=int(row[0]); y=s*Fraction(*map(int,row[4])); ceil_log=(s-1).bit_length()
        k=ceil_log+10; assert 2**k>=3*y
        k19=ceil_log+6 if int(row[5])>=s>=2**19 else None
        if k19 is not None: assert 2**k19>=3*y
        k_rows.append([row[0],row[1],k,k19])
    repeat=[]; x=1; ratio=Fraction(1)
    for length in range(41):
        repeat.append([length,str(x),frac(ratio),ratio<256])
        if x%2: ratio*=Fraction(3*x+1,3*x)
        x=T(x)
    assert next(row[0] for row in repeat if not row[3])==39
    historical={}
    for name in ('phase43_certificate_7.json','phase43_certificate_703.json',
                 'phase38_capacity_certificate.json'):
        historical[name]=hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest()
    return {'schema':'transient-sparsity-regressions-v1','status':'VERIFIED_FINITE',
            'proves_collatz':False,'words':word_rows,'paths':paths,'K_rows':k_rows,
            'repeated_source_1':repeat,'first_failure_within_source_1':39,
            'historical_sha256':historical,'negative_fixed_control':[-1,-1,3,2]}

def scope():
    return {'schema':'transient-sparsity-scope-v1','status':'VERIFIED_FINITE','proves_collatz':False,
            'base_commit':'feb29b423d43445f1c7d826d6ef71a25e2854b44',
            'proposal_zip_sha256':'0f3811f9274e5cf605ddd3f66e0f935a0ad28c9e97aec4a0c3835401b5763eda',
            'input_contract':'distinct positive integer input states; closing endpoint may repeat; empty path allowed',
            'tail_contract':'actual odd shell counts only; finite recursive upper bounds through N=500',
            'tail_applies_to_raw_recursive_capacities':False,'old_capacity_tables_replaced':False,
            'P267_reused_without_duplicate_claim':True,'external_theorem_required':False,
            'general_bound':256,'floor_19_bound':13,'floor_49_bound':2,
            'all_competitor_source_pool_requires_distinct_target_inputs':True,
            'repeated_target_cycle_deletion_only_supplies_a_witness':True,
            'infinite_proofs_machine_formalized':False,'H112_status':'OPEN','H72_status':'OPEN'}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--artifact-dir',type=Path,required=True)
    args=p.parse_args(); args.artifact_dir.mkdir(parents=True,exist_ok=True)
    a,o,c=capacities()
    evidence={'schema':'transient-sparsity-v1','status':'VERIFIED_FINITE','proves_collatz':False,
              'capacity':c,'constants':constant_checks(),'affine':affine_audit(),
              'finite_prefix':prefix_audit(a,o)}
    for name,data in [('evidence',evidence),('scope',scope()),('regressions',regressions())]:
        (args.artifact_dir/('transient_sparsity_'+name+'.json')).write_bytes(
            json.dumps(data,sort_keys=True,indent=2).encode()+b'\n')
    print(json.dumps({'capacity_rows':len(c['rows']),'words':evidence['affine']['words'],
                      'windows':evidence['finite_prefix']['window_cases'],'proves_collatz':False}))

if __name__=='__main__': main()
