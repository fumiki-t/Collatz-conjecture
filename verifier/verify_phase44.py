"""Independent Phase 44 checker: event jumps, inverse edit DP, full-state orbits.

No generator imports. All acceptance checks remain active under python -O.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from array import array
from bisect import bisect_left
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from math import comb
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE='44430b21705bd69acb6cc29760ee27bdf2433b1f'
Q=1_000_000
BOUNDS=(8,16,32,64,128,256,512,1024)


class VerificationError(ValueError):
    pass


def need(ok, message):
    if not ok: raise VerificationError(message)


def integer(x, minimum=0):
    need(type(x) is int and x>=minimum, 'invalid integer domain')
    return x


def encode(x):
    return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()


def same(x,y):
    need(encode(x)==encode(y),'reconstructed data mismatch')


@lru_cache(maxsize=1)
def logarithm_bounds():
    # alpha=3/2+log(9/8)/(2 log 2); neither supplied enclosure is reused.
    def integral(t):
        term=t; low=Fraction()
        for k in range(68):
            low+=2*term/(2*k+1); term*=t*t
        return low,low+2*term/(137*(1-t*t))
    l2,u2=integral(Fraction(1,3)); lr,ur=integral(Fraction(1,17))
    lo=Fraction(3,2)+lr/(2*u2); hi=Fraction(3,2)+ur/(2*l2)
    den=1<<96
    return lo.numerator*den//lo.denominator,(hi.numerator*den+hi.denominator-1)//hi.denominator,den


def mechanical(q):
    integer(q); lo,hi,den=logarithm_bounds()
    f=[j*lo//den for j in range(q+1)]
    need(all(f[j]==j*hi//den for j in range(q+1)), 'undecided logarithm floor')
    p=1
    for j in range(min(q,4096)+1):
        need(f[j]==p.bit_length()-1,'power/log disagreement'); p*=3
    return f


def event_model(q):
    """Jump to next change in each height epoch; no per-step recurrence replay."""
    f=mechanical(q)
    exps=[f[j+1]-f[j] for j in range(q)]
    p=r=cursor=0
    while cursor<q:
        h=max(16,2*((cursor+1).bit_length()-1))
        stop=min(q,max(511,(1<<(h//2+1))-1))
        if r<h-1:
            j=cursor
        else:
            # First input index whose baseline block reaches the old height.
            j=max(cursor,bisect_left(f,f[p]+r,lo=cursor+1)-1)
        delta=-1 if r>=h else 1
        if delta==1 and j<q and f[j+1]-f[j]==1: j+=1
        if j>=stop:
            cursor=stop
            continue
        need(j<q and (delta<0 or f[j+1]-f[j]==2),'event search')
        exps[j]-=delta
        r+=delta; p=cursor=j+1
    return exps


def reconstruct_alignment(exps):
    need(all(type(e) is int and e>0 for e in exps),'exponent domain')
    f=mechanical(len(exps)); positions=[0]
    for e in exps: positions.append(positions[-1]+e)
    w=bytearray(positions[-1]); baseline=bytearray(f[-1])
    for p in positions[:-1]: w[p]=1
    for p in f[:-1]: baseline[p]=1
    profile=[fj-p for fj,p in zip(f,positions)]
    inserted=[]; deleted=[]; intervals=[]; start=0
    for j,e in enumerate(exps):
        b=f[j+1]-f[j]
        inserted.extend(range(positions[j]+b,positions[j+1]))
        deleted.extend([positions[j+1]]*max(b-e,0))
        if b!=e:
            ell=positions[j+1]-positions[start]-max(e-b,0)
            need(w[positions[start]:positions[start]+ell]==baseline[f[start]:f[start]+ell],'pure factor mismatch')
            intervals.append([profile[start],start,j+1,ell]); start=j+1
    ell=positions[-1]-positions[start]
    need(w[positions[start]:]==baseline[f[start]:f[start]+ell],'last pure factor')
    intervals.append([profile[-1],start,len(exps),ell])
    beta=sum((Fraction(2**positions[j],3**(j+1)) for j in range(min(32,len(exps)))),Fraction())
    s=dict(q=len(exps),E=len(w),a=profile[-1],H=max(profile),D=len(inserted),U=len(deleted),t=len(inserted)+len(deleted),
           pure_intervals=len(intervals),max_pure_length_minus_height=max(v[3]-v[0] for v in intervals),
           a32=profile[32] if len(exps)>=32 else None,beta32=[beta.numerator,beta.denominator],
           word_sha256=hashlib.sha256(w).hexdigest(),exponent_sha256=hashlib.sha256(encode(exps)).hexdigest())
    need(s['t']==s['a']+2*s['D'],'edit variation identity')
    return dict(word=w,inserted=inserted,deleted=deleted,intervals=intervals,stats=s,profile=profile,positions=positions)


def range_charges(data,n):
    integer(n,1)
    M=max(len(data['word'])-n+1,0); difference=array('i',[0])*(M+1)
    for positions,offset in ((data['inserted'],0),(data['deleted'],-1)):
        for p in positions:
            left=max(0,p-n+1); right=min(M-1,p+offset)
            if left<=right:
                difference[left]+=1; difference[right+1]-=1
    answer=[]; c=0
    for i in range(M):
        c+=difference[i]; answer.append(c)
    return answer


def bound(n,r):
    integer(n,1); integer(r)
    # Hockey-stick product, rather than importing generator's binomial routine.
    choose=1
    for j in range(1,r+1): choose=choose*(2*n+1+j)//j
    return (n+r+1)*choose


@lru_cache(maxsize=1)
def model_reference():
    data=reconstruct_alignment(event_model(Q)); w=data['word']; s=data['stats']
    need(min(data['profile'])==0 and max(data['profile'])<=max(16,2*Q.bit_length()),'model safety')
    need(all(a>=2*((j+1).bit_length()-1)-3 for j,a in enumerate(data['profile']) if j>=32),'finite lower envelope')
    K=(3*(1<<16)+Q-1).bit_length(); n=s['H']+K; costs=range_charges(data,n); hist=Counter(costs)
    low={bytes(w[i:i+n]) for i,c in enumerate(costs) if c<=1}
    need(sum(costs)<=n*s['t'] and len(low)<=bound(n,1),'charge/ball consistency')
    rows=[]
    for r in range(5):
        rhs=bound(n,r)+n*s['t']//(r+1)
        rows.append(dict(r=r,ball_upper=bound(n,r),rhs=rhs,excess=len(costs)-rhs,inequality_holds=len(costs)<=rhs))
    windows=dict(source_bound_bits=16,K=K,n=n,windows=len(costs),charged_edits=sum(costs),charge_upper=n*s['t'],
                 charge_histogram={str(k):v for k,v in sorted(hist.items())},low_edit_occurrences=sum(v for k,v in hist.items() if k<=1),
                 distinct_low_edit_words=len(low),old_CAP_all_zero=all(l<=r+K-1 for r,p,j,l in data['intervals']),edited_capacity=rows)
    return data,windows


def repeat_check(row,data,expected_B):
    need(set(row)=={'B','K','n','i','j','common','split','required_full_prefix'},'repeat fields')
    for k in row:
        if k!='split': integer(row[k])
    same(row['B'],expected_B)
    B,K,n,i,j,c=(row[k] for k in ('B','K','n','i','j','common'))
    same(K,(3*(1<<B)+Q-1).bit_length())
    need(3*(1<<B)+Q<=1<<K,'insufficient source height K')
    need(n==data['stats']['H']+K and 0<=i<j and c>=n,'repeat range')
    w=data['word']; need(j+c<len(w),'split outside prefix')
    same(list(w[i:i+c]),list(w[j:j+c]))
    need(w[i+c]!=w[j+c],'repeat without later split')
    same(row['split'],[w[i+c],w[j+c]]); same(row['required_full_prefix'],j+c+1)
    # Independently certify actual affine upper heights at both starts, without
    # relying on distinct input states or the million-step terminal endpoint.
    targets={i,j}; p=two=1; affine=0
    for k in range(j+1):
        if k in targets:
            need(p*(1<<B)+affine < (1<<n)*two,'repeat affine height')
        if k<j:
            if w[k]: affine=3*affine+two; p*=3
            two*=2


def check_model(payload):
    need(type(payload) is dict,'model object')
    same(sorted(payload),sorted(('schema','base','proves_collatz','stats','windows','repeat_certificates')))
    same(payload['schema'],'phase44-model-v1'); same(payload['base'],BASE); same(payload['proves_collatz'],False)
    data,windows=model_reference()
    same(payload['stats'],data['stats']); same(payload['windows'],windows)
    need(type(payload['repeat_certificates']) is list and len(payload['repeat_certificates'])==8,'repeat coverage')
    for B,row in zip(BOUNDS,payload['repeat_certificates']): repeat_check(row,data,B)


def verify_model(payload):
    try:
        check_model(payload)
        return True
    except (ValueError,TypeError,KeyError,IndexError,OverflowError):
        return False


def zero_distance(source,target):
    """Shortest zero-only edit distance; ones cannot be inserted or deleted."""
    inf=len(source)+len(target)+1
    dp=[[inf]*(len(target)+1) for _ in range(len(source)+1)]; dp[0][0]=0
    for i in range(len(source)+1):
        for j in range(len(target)+1):
            v=dp[i][j]
            if i<len(source) and source[i]==0: dp[i+1][j]=min(dp[i+1][j],v+1)
            if j<len(target) and target[j]==0: dp[i][j+1]=min(dp[i][j+1],v+1)
            if i<len(source) and j<len(target) and source[i]==target[j]: dp[i+1][j+1]=min(dp[i+1][j+1],v)
    return dp[-1][-1]


@lru_cache(maxsize=1)
def inverse_balls():
    power=1; positions=[]
    while power.bit_length()-1<4096:
        positions.append(power.bit_length()-1); power*=3
    word=bytearray(4096)
    for p in positions: word[p]=1
    language={0:{b''}}
    for m in range(1,11):
        language[m]={bytes(word[i:i+m]) for i in range(4097-m)}
        need(len(language[m])==m+1,'language completeness')
    balls={}
    for n in range(1,9):
        candidates=list(map(bytes,itertools.product((0,1),repeat=n)))
        for r in range(3):
            bases=set().union(*(language[m] for m in range(max(0,n-r),n+r+1)))
            balls[n,r]={v for v in candidates if any(zero_distance(b,v)<=r for b in bases)}
            need(len(balls[n,r])<=bound(n,r),'small ball bound')
    return balls


def independent_orbits(S,maximum=64):
    integer(S,1); integer(maximum); need(S%2==1,'odd source required')
    x=S; states=[]; seen=set(); word=bytearray(); powers=1; odd=0; a=D=H=0; safe=True
    while (odd<maximum or x%2==0) and x not in seen:
        seen.add(x); states.append(x); bit=x%2; word.append(bit)
        if bit: powers*=3; odd+=1
        x=x//2 if not bit else (3*x+1)//2
        if x%2==0: continue
        E=len(word); nxt=powers.bit_length()-1-E
        D+=max(a-nxt,0); a=nxt; H=max(H,a); safe=bool(safe and a>=0)
        Y=Fraction(x*2**E,powers); K=2
        while (1<<K)*Y.denominator<3*Y.numerator: K+=1
        n=H+K; M=max(E-n+1,0)
        need(max(states)<1<<n,'literal height')
        factors=[bytes(word[i:i+n]) for i in range(M)]
        need(len(set(factors))==M,'literal separation')
        rhs=[bound(n,r)+n*(a+2*D)//(r+1) for r in range(4)]
        need(all(M<=v for v in rhs),'literal capacity')
        yield [S,odd,E,a,H,D,K,n,M,safe,Y.numerator,Y.denominator,max(states),rhs]


@lru_cache(maxsize=1)
def finite_reference():
    balls=inverse_balls(); words=widths=members=0
    for q in range(1,6):
        for exps in itertools.product(range(1,5),repeat=q):
            data=reconstruct_alignment(exps); words+=1
            for n in range(1,min(8,len(data['word']))+1):
                widths+=1; costs=range_charges(data,n)
                need(sum(costs)<=n*data['stats']['t'],'alignment charge')
                for i,c in enumerate(costs):
                    if c<=2:
                        need(bytes(data['word'][i:i+n]) in balls[n,c],'inverse edit membership'); members+=1
    rows=[row for S in range(1,512,2) for row in independent_orbits(S)]
    orbits=dict(odd_sources=256,maximum_odd_steps=64,complete_prefix_queries=len(rows),
                queries_with_positive_windows=sum(row[8]>0 for row in rows),coefficient_safe_queries=sum(row[9] for row in rows),
                inequality_checks=4*len(rows),transcript_sha256=hashlib.sha256(encode(rows)).hexdigest(),
                first_nonvacuous_safe=next(row for row in rows if row[8] and row[9]),
                first_nonvacuous_unsafe=next(row for row in rows if row[8] and not row[9]))
    return dict(proves_collatz=False,ball_rows=[[n,r,len(v),bound(n,r)] for (n,r),v in balls.items()],
                alignment=dict(exponent_words=words,window_width_cases=widths,low_edit_memberships=members),orbits=orbits)


def regression_check(data):
    try:
        from .verify_phase43 import regression_check as old_check
    except ImportError:
        from verify_phase43 import regression_check as old_check
    old_check(data['inherited'])
    rows=[]
    for family in ('2^m-1','8^m-5'):
        for m in range(1,13):
            S=2**m-1 if family=='2^m-1' else 8**m-5
            values=list(independent_orbits(S))
            rows.append(dict(family=family,m=m,source=S,queries=len(values),transcript_sha256=hashlib.sha256(encode(values)).hexdigest()))
    same(data['ordinary_families'],rows); same(data['proves_collatz'],False)
    literal=[]
    for row in data['inherited']['families']:
        values=list(independent_orbits(row['source']))
        literal.append(dict(word=row['word'],source=row['source'],queries=len(values),
                            transcript_sha256=hashlib.sha256(encode(values)).hexdigest()))
    same(data['literal_word_capacity'],literal)


def theory_check(data):
    try:
        from .verify_phase43 import check as potential_check
    except ImportError:
        from verify_phase43 import check as potential_check
    prefix=reconstruct_alignment(event_model(32)); beta=Fraction(*prefix['stats']['beta32'])
    tail=Fraction(5,1024)+Fraction(1,96); upper=beta+tail
    same(data['beta32'],[beta.numerator,beta.denominator]); same(data['beta_tail_upper'],[tail.numerator,tail.denominator])
    same(data['beta_infinity_upper'],[upper.numerator,upper.denominator]); need(upper<2,'beta tail')
    same(data['entropy_comparison'],[str(33**33),str(2**168)]); need(33**33<2**168,'entropy')
    tests=[3**14<2**23,23**690<2**667*14**420*9**270,24**690*3**(406*135)<=2**(667*135),135**30<2**(134*29)]
    need(all(tests) and 3**406<2**667 and 4**23*3**(14*135)<2**(23*135)
         and 136*2<135*3 and 3**30<2**59,'finite sparsity induction')
    same(data['finite_sparsity'],dict(N0=135,theta=[14,23],rho=[29,30],constant=32,integer_tests=tests))
    hashes={}
    for name in ('phase43_certificate_7.json','phase43_certificate_703.json'):
        content=(ROOT/'artifacts'/name).read_bytes(); hashes[name]=hashlib.sha256(content).hexdigest()
        potential_check(json.loads(content))
    same(data['dependency_hashes'],hashes); same(data['proves_collatz'],False)


def audit(directory):
    model=json.loads((directory/'phase44_model.json').read_bytes()); check_model(model)
    finite=json.loads((directory/'phase44_finite.json').read_bytes()); same(finite,finite_reference())
    regression_check(json.loads((directory/'phase44_regressions.json').read_bytes()))
    theory_check(json.loads((directory/'phase44_theory.json').read_bytes()))
    return dict(valid=True,generator_imported=False,model_odd_steps=Q,shortcut_bits=model['stats']['E'],
                low_edit_occurrences=model['windows']['low_edit_occurrences'],distinct_low_edit_words=model['windows']['distinct_low_edit_words'],
                edit_capacity_r1_excess=model['windows']['edited_capacity'][1]['excess'],repeat_certificates=8,
                actual_prefix_queries=finite['orbits']['complete_prefix_queries'],alignment_words=finite['alignment']['exponent_words'],
                proves_collatz=False)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--artifact-dir',type=Path,required=True); p.add_argument('--output',type=Path)
    args=p.parse_args()
    try:
        result=audit(args.artifact_dir)
    except (ValueError,TypeError,KeyError,IndexError,OverflowError) as error:
        print(json.dumps(dict(valid=False,error=str(error),proves_collatz=False))); raise SystemExit(1)
    if args.output: args.output.write_bytes(encode(result))
    print(json.dumps(result,indent=2))
