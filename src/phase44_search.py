"""Phase 44 exact zero-edit experiments. Finite evidence, not a Collatz proof."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path

BASE = "44430b21705bd69acb6cc29760ee27bdf2433b1f"
Q = 1_000_000
BOUNDS = (8, 16, 32, 64, 128, 256, 512, 1024)
ROOT = Path(__file__).resolve().parents[1]


def integer(x, lower=0):
    if type(x) is not int or x < lower:
        raise ValueError("integer outside declared domain")
    return x


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encoded(x):
    return (json.dumps(x, sort_keys=True, separators=(",", ":"))+"\n").encode()


@lru_cache(maxsize=1)
def alpha_box():
    def logarithm(x):
        z = Fraction(x-1, x+1)
        low = sum((2*z**(2*k+1)/(2*k+1) for k in range(64)), Fraction())
        return low, low+2*z**129/(129*(1-z*z))
    l2,u2 = logarithm(2)
    l3,u3 = logarithm(3)
    lo,hi,den = l3/u2,u3/l2,1 << 104
    return lo.numerator*den//lo.denominator, (hi.numerator*den+hi.denominator-1)//hi.denominator, den


def floors(q):
    integer(q)
    lo,hi,den = alpha_box()
    values = [j*lo//den for j in range(q+1)]
    require(all(values[j] == j*hi//den for j in range(q+1)), "unresolved log floor")
    return values


def ball(n, r):
    integer(n, 1); integer(r)
    return (n+r+1)*comb(2*n+r+1, r)


def model_exponents(q):
    f = floors(q)
    a = p = 0
    exponents = []
    for j in range(q):
        b = f[j+1]-f[j]
        target = max(16, 2*((j+1).bit_length()-1))
        change = 0
        if a < target-1:
            change = int(b == 2)
        elif f[j+1]-f[p] >= a:
            change = -1 if a >= target else int(b == 2)
        exponents.append(b-change)
        a += change
        if change:
            p = j+1
    return exponents


def alignment(exponents):
    require(all(type(e) is int and e >= 1 for e in exponents), "invalid exponents")
    f = floors(len(exponents))
    word, ins, deletions, mapping = bytearray(), [], [], []
    intervals, a, H, D, U, p, start = [], 0, 0, 0, 0, 0, 0
    profile = [0]
    beta32 = Fraction()
    for j,e in enumerate(exponents):
        b = f[j+1]-f[j]
        E = len(word)
        if j < 32:
            beta32 += Fraction(1 << E, 3**(j+1))
        word.extend([1]+[0]*(e-1))
        mapping.extend([f[j]+v if v < b else None for v in range(e)])
        ins.extend(range(E+b, E+e))
        deletions.extend([E+e]*max(b-e, 0))
        change = b-e
        if change:
            intervals.append([a, p, j+1, f[j+1]-f[p]-max(change,0)])
            start, p = len(word), j+1
        a += change
        H = max(H,a); D += max(-change,0); U += max(change,0)
        profile.append(a)
    intervals.append([a,p,len(exponents),len(word)-start])
    stats = dict(q=len(exponents), E=len(word), a=a, H=H, D=D, U=U, t=U+D,
                 pure_intervals=len(intervals), max_pure_length_minus_height=max(row[3]-row[0] for row in intervals),
                 a32=profile[32] if len(exponents)>=32 else None,
                 beta32=[beta32.numerator,beta32.denominator],
                 word_sha256=hashlib.sha256(word).hexdigest(),
                 exponent_sha256=hashlib.sha256(encoded(exponents)).hexdigest())
    return dict(word=word, ins=ins, deletions=deletions, mapping=mapping,
                intervals=intervals, stats=stats, profile=profile)


def charges(data, n):
    integer(n,1)
    L=len(data['word']); M=max(L-n+1,0)
    if not M:
        return []
    ins=[0]*L; gaps=[0]*(L+1)
    for i in data['ins']: ins[i]+=1
    for i in data['deletions']: gaps[i]+=1
    v=sum(ins[:n])+sum(gaps[1:n]); answer=[v]
    for i in range(1,M):
        v += ins[i+n-1]-ins[i-1]+gaps[i+n-1]-gaps[i]
        answer.append(v)
    return answer


def model_payload(q=Q):
    data=alignment(model_exponents(q)); s=data['stats']; w=data['word']
    K=(3*(1 << 16)+q-1).bit_length(); n=s['H']+K
    costs=charges(data,n); hist=Counter(costs)
    low=set(); key=0; mask=(1 << n)-1
    for i,b in enumerate(w):
        key=((key<<1)|b)&mask
        if i>=n-1 and costs[i-n+1]<=1: low.add(key)
    rows=[]
    for r in range(5):
        rhs=ball(n,r)+n*s['t']//(r+1)
        rows.append(dict(r=r,ball_upper=ball(n,r),rhs=rhs,excess=len(costs)-rhs,inequality_holds=len(costs)<=rhs))
    windows=dict(source_bound_bits=16,K=K,n=n,windows=len(costs),
                 charged_edits=sum(costs),charge_upper=n*s['t'],
                 charge_histogram={str(k):v for k,v in sorted(hist.items())},
                 low_edit_occurrences=sum(v for k,v in hist.items() if k<=1),distinct_low_edit_words=len(low),
                 old_CAP_all_zero=all(ell<=r+K-1 for r,p,j,ell in data['intervals']),edited_capacity=rows)
    repeats=[]
    for B in BOUNDS:
        K=(3*(1 << B)+q-1).bit_length(); n=s['H']+K
        seen={}; key=0; mask=(1 << n)-1
        for pos,b in enumerate(w):
            key=((key<<1)|b)&mask
            if pos<n-1: continue
            j=pos-n+1
            if key not in seen:
                seen[key]=j; continue
            i=seen[key]; common=n
            while j+common<len(w) and w[i+common]==w[j+common]: common+=1
            if j+common<len(w):
                repeats.append(dict(B=B,K=K,n=n,i=i,j=j,common=common,
                                    split=[w[i+common],w[j+common]],required_full_prefix=j+common+1))
                break
        else:
            raise ValueError("no repeat-and-split witness within declared model")
    return dict(schema="phase44-model-v1",base=BASE,proves_collatz=False,stats=s,windows=windows,repeat_certificates=repeats)


def small_language(maximum=10):
    f=floors(3000); word=bytearray(f[-1])
    for p in f[:-1]: word[p]=1
    result={0:{b''}}
    for n in range(1,maximum+1):
        result[n]={bytes(word[i:i+n]) for i in range(len(word)-n+1)}
        require(len(result[n])==n+1,"incomplete mechanical language sample")
    return result


def small_balls():
    language=small_language(); results={}
    for n in range(1,9):
        acc=set()
        for r in range(3):
            for a in range(r+1):
                b=r-a; m=n+a-b
                if m<0 or b>n: continue
                for base in language[m]:
                    for deleted in itertools.combinations([i for i,v in enumerate(base) if v==0],a):
                        kept=bytes(v for i,v in enumerate(base) if i not in deleted)
                        for added in itertools.combinations(range(n),b):
                            it=iter(kept)
                            acc.add(bytes(0 if i in added else next(it) for i in range(n)))
            results[n,r]=set(acc)
    return results


def alignment_audit(balls):
    words=widths=members=0
    for q in range(1,6):
        for exps in itertools.product(range(1,5),repeat=q):
            data=alignment(exps); words+=1
            for n in range(1,min(8,len(data['word']))+1):
                costs=charges(data,n); widths+=1
                require(sum(costs)<=n*data['stats']['t'],"window edit charge overflow")
                for i,cost in enumerate(costs):
                    if cost<=2:
                        require(bytes(data['word'][i:i+n]) in balls[n,cost],"alignment outside edit ball")
                        members+=1
    return dict(exponent_words=words,window_width_cases=widths,low_edit_memberships=members)


def orbit_records(S, maximum=64):
    integer(S,1); integer(maximum)
    require(S%2==1,"odd source required")
    x=S; seen=set(); inputs=[]; word=bytearray(); a=H=D=0; safe=True
    for q in range(1,maximum+1):
        if x in seen: break
        numerator=3*x+1; e=(numerator & -numerator).bit_length()-1
        trial=x; block=[]
        for _ in range(e):
            block.append(trial); trial=(3*trial+1)//2 if trial&1 else trial//2
        if len(set(block))!=len(block) or any(v in seen for v in block): break
        x=trial; seen.update(block); inputs.extend(block); word.extend(v&1 for v in block)
        E=len(word); new_a=(3**q).bit_length()-1-E
        D+=max(a-new_a,0); a=new_a; H=max(H,a); safe &= a>=0
        Y=Fraction((1 << E)*x,3**q); bound=3*Y
        ceil=(bound.numerator+bound.denominator-1)//bound.denominator
        K=max(2,(ceil-1).bit_length()); n=H+K; M=max(E-n+1,0); t=a+2*D
        require(all(v < 1 << n for v in inputs),"height bound failed")
        require(len({bytes(word[i:i+n]) for i in range(M)})==M,"distinct factors failed")
        rhs=[ball(n,r)+n*t//(r+1) for r in range(4)]
        require(all(M<=v for v in rhs),"literal edit-capacity failed")
        yield [S,q,E,a,H,D,K,n,M,safe,Y.numerator,Y.denominator,max(inputs),rhs]


def orbit_audit():
    rows=[row for S in range(1,512,2) for row in orbit_records(S)]
    return dict(odd_sources=256,maximum_odd_steps=64,complete_prefix_queries=len(rows),
                queries_with_positive_windows=sum(row[8]>0 for row in rows),
                coefficient_safe_queries=sum(row[9] for row in rows),inequality_checks=4*len(rows),
                transcript_sha256=hashlib.sha256(encoded(rows)).hexdigest(),
                first_nonvacuous_safe=next(row for row in rows if row[8] and row[9]),
                first_nonvacuous_unsafe=next(row for row in rows if row[8] and not row[9]))


def regressions():
    # Reuse the retained generator's family catalogue, not old derived JSON.
    try:
        from .phase43_search import regressions as old_controls
    except ImportError:
        from phase43_search import regressions as old_controls
    data=old_controls()
    families=[]
    for name in ('2^m-1','8^m-5'):
        for m in range(1,13):
            S=(2**m-1) if name=='2^m-1' else 8**m-5
            rows=list(orbit_records(S,64))
            families.append(dict(family=name,m=m,source=S,queries=len(rows),transcript_sha256=hashlib.sha256(encoded(rows)).hexdigest()))
    literal=[]
    for row in data['families']:
        values=list(orbit_records(row['source']))
        literal.append(dict(word=row['word'],source=row['source'],queries=len(values),
                            transcript_sha256=hashlib.sha256(encoded(values)).hexdigest()))
    return dict(proves_collatz=False,inherited=data,ordinary_families=families,literal_word_capacity=literal)


def theory():
    exps=model_exponents(32); data=alignment(exps)
    tail=Fraction(480,3*2**15)+Fraction(1,96)
    upper=Fraction(*data['stats']['beta32'])+tail
    require(upper<2 and 33**33<2**168,"theory rational comparison")
    return dict(proves_collatz=False,beta32=data['stats']['beta32'],beta_tail_upper=[tail.numerator,tail.denominator],
                beta_infinity_upper=[upper.numerator,upper.denominator],
                entropy_comparison=[str(33**33),str(2**168)],
                finite_sparsity=dict(N0=135,theta=[14,23],rho=[29,30],constant=32,
                                     integer_tests=[3**14<2**23,23**690<2**667*14**420*9**270,
                                                    24**690*3**(406*135)<=2**(667*135),135**30<2**(134*29)]),
                dependency_hashes={name:hashlib.sha256((ROOT/'artifacts'/name).read_bytes()).hexdigest()
                                   for name in ('phase43_certificate_7.json','phase43_certificate_703.json')})


def generate(directory):
    directory.mkdir(parents=True,exist_ok=True)
    balls=small_balls()
    finite=dict(proves_collatz=False,ball_rows=[[n,r,len(v),ball(n,r)] for (n,r),v in balls.items()],
                alignment=alignment_audit(balls),orbits=orbit_audit())
    for name,data in dict(model=model_payload(),finite=finite,regressions=regressions(),theory=theory()).items():
        (directory/f'phase44_{name}.json').write_bytes(encoded(data))
    return dict(valid=True,model_odd_steps=Q,orbits=finite['orbits'],proves_collatz=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifact-dir',type=Path,required=True)
    print(json.dumps(generate(parser.parse_args().artifact_dir),indent=2))
