#!/usr/bin/env python3
"""Exact local experiments for a research proposal, not a Collatz proof.
All output paths are local. No dependencies beyond the Python standard library.
"""
from __future__ import annotations
import argparse, itertools, json, math, hashlib, sys
from fractions import Fraction
from pathlib import Path

U = ("11011111000", "11011011111000", "11011110011010", "11011110101010")
V = ("11111010100", "11111111000100", "11111011010100", "11111011110000")
D22 = "1101101101011011011010110110101101"
A22 = "1111111111011100011111001100001100"

def need(ok: bool, msg: str) -> None:
    if not ok: raise ValueError(msg)

def affine(w: str) -> tuple[int,int,int]:
    need(type(w) is str and set(w)<=set('01'), 'invalid word')
    q=B=0
    for j,b in enumerate(w):
        if b=='1': q+=1; B=3*B+(1<<j)
    return len(w),q,B

def safe(w: str) -> bool:
    q=0
    for j,b in enumerate(w,1):
        q+=int(b)
        if 3**q <= 1<<j: return False
    return True

def residue(w: str) -> int:
    L,q,B=affine(w)
    return (-B*pow(3**q,-1,1<<L))%(1<<L)

def step(x: int) -> int:
    return (3*x+1)//2 if x%2 else x//2

def replay(x: int, w: str) -> int:
    need(type(x) is int and x>0,'nonpositive source')
    for b in w:
        need(x%2==int(b),'literal parity failed')
        x=step(x)
    return x

def literal(x: int,L: int) -> str:
    out=[]
    for _ in range(L):
        out.append(str(x%2));x=step(x)
    return ''.join(out)

def f2(j: int) -> int:
    return (3**j).bit_length()-1

def decode(L: int,q: int,B: int) -> str|None:
    if L<0 or q<0 or q>L or B<0:return None
    x=(-B*pow(3**q,-1,1<<L))%(1<<L)
    w=literal(x,L)
    return w if affine(w)==(L,q,B) else None

def frac(x: Fraction) -> list[int]:return [x.numerator,x.denominator]

def v2(n: int) -> int:
    need(n!=0,'v2 zero')
    return (abs(n)&-abs(n)).bit_length()-1

def kernel(states: list[int], edges: list[list], universal=False) -> tuple[list[int],list[list[int]]]:
    E={(d,i):t for d,i,t,w in edges}
    live=set(states);removed=[]
    while True:
        new={d for d in live if (all if universal else any)(
            (d,i) in E and E[d,i] in live for i in range(4))}
        if new==live:break
        removed.append(sorted(live-new));live=new
    return sorted(live),removed

def shadow_graph(p: int,b: int) -> dict:
    need(b%2==1, 'this complete graph uses odd denominators only')
    lows=[];highs=[];data=[]
    for u in U:
        L,q,B=affine(u);A=3**q;M=1<<L
        Bmin=A-(1<<q);Bmax=(1<<(L-q))*Bmin
        low=Fraction(p*B-b*Bmax,A-M);high=Fraction(p*B-b*Bmin,A-M)
        lows.append(low);highs.append(high)
        data.append([L,q,B,Bmin,Bmax,frac(low),frac(high)])
    low=min(lows);high=max(highs)
    lo=math.ceil(low);hi=math.floor(high);edges=[];same_weight=0
    for d in range(lo,hi+1):
        for i,u in enumerate(U):
            L,q,B=affine(u);M=1<<L;A=3**q
            r=(p*residue(u)+d)*pow(b,-1,M)%M
            w=literal(r,L);_,qq,Bw=affine(w)
            if qq!=q:continue
            same_weight+=1
            num=A*d+b*Bw-p*B
            need(num%M==0,'nonintegral offset')
            dd=num//M
            if lo<=dd<=hi:edges.append([d,i,dd,w])
    live,removed=kernel(list(range(lo,hi+1)),edges)
    universal,_=kernel(list(range(lo,hi+1)),edges,True)
    essential=[e for e in edges if e[0] in live and e[2] in live]
    return {'p':p,'b':b,'real_bounds':[frac(low),frac(high)],
            'integer_bounds':[lo,hi],'bounds_rows':data,
            'transition_cases':4*(hi-lo+1),'same_weight_cases':same_weight,
            'edges':edges,'kernel':live,'removed_layers':removed,
            'essential_edges':essential,'universal_kernel':universal}

def equal_coefficient() -> dict:
    small=[]
    for q in range(1,21):
        P=3**q;bm=sum((1<<f2(j))*3**(q-1-j) for j in range(q))
        bn=P-(1<<q)
        need(bm-bn<4*P,'q<=20 bound')
        small.append([q,bm,bn,4*P-(bm-bn)])
    q=21;P=3**q;pos=[f2(j) for j in range(q)]
    bm=sum((1<<p)*3**(q-1-j) for j,p in enumerate(pos))
    allowance=bm-(5*P-(1<<q))
    need(allowance*6<P,'q21 allowance')
    moved=[None]+[j for j in range(1,q) if pos[j]-pos[j-1]==2]
    rows=[]
    for j in moved:
        pp=pos.copy()
        if j is not None: pp[j]-=1
        B=sum((1<<p)*3**(q-1-i) for i,p in enumerate(pp))
        for L in range(pp[-1]+1,f2(q)+1):
            candidate=B-4*P
            w=decode(L,q,candidate)
            need(w is None,'q21 coequal pair unexpectedly exists')
            rows.append([j,L,B,candidate])
    L,q,B=affine(D22);_,_,bb=affine(A22)
    s=residue(D22);r=residue(A22);y=replay(s,D22)
    need(s+4==r and y==replay(r,A22) and B-bb==4*3**q,'q22 example')
    need(safe(D22) and safe(A22),'q22 safety')
    return {'q1_to_q20':small,'q21_allowance':allowance,'q21_rows':rows,
            'witness':{'small_word':D22,'large_word':A22,'L':L,'q':q,
                       'B_small_source':B,'B_large_source':bb,'small_source':s,
                       'large_source':r,'endpoint':y}}

def macro_checks(max_blocks=5) -> dict:
    macro=[]
    for u,v in zip(U,V):
        L,q,B=affine(u);l,r,b=affine(v);A=3**q;M=1<<L
        need((L,q)==(l,r) and b-B==4*(M-A),'offset identity')
        need(safe(u) and safe(v),'macro safety')
        macro.append({'u':u,'v':v,'L':L,'q':q,'B_u':B,'B_v':b,
                      'r_u':residue(u),'r_v':residue(v),
                      'centre':frac(Fraction(-B,A-M))})
    schedules=pairs=steps=shrinks=triples=0
    # Appending a known next block enforces the next odd boundary as well.
    checksum=0
    for depth in range(1,max_blocks+1):
        for labels in itertools.product(range(4),repeat=depth):
            schedules+=1
            wu=''.join(U[i] for i in labels);wv=''.join(V[i] for i in labels)
            full=wu+U[0];r=residue(full);M=1<<len(full)
            for lift in (0,1,(1<<20)+3):
                s=r+M*lift;x=s;y=s+4;pairs+=1
                for i in labels:
                    x=replay(x,U[i]);y=replay(y,V[i]);steps+=2*len(U[i])
                    need(y-x==4,'switching difference')
                first=replay(s,U[labels[0]])
                need(first%2==1 and first%3==1,'first boundary')
                z=(2*first+7)//3
                need(z%2==1 and step(z)==first+4 and 6*z<5*s,'5/6 shrink')
                shrinks+=1
                if labels[0]==1:
                    tt=s+3;vv='01111111010100'
                    end=replay(tt,vv)
                    need(end==first+4 and tt%2==0,'even third source')
                    for i in labels[1:]:end=replay(end,V[i])
                    need(end==y and (s+3)//2<s,'half shrink')
                    steps+=sum(len(U[i]) for i in labels);triples+=1
                checksum=(checksum+x+y+z)%((1<<127)-1)
    return {'macros':macro,'max_blocks':max_blocks,'schedules':schedules,
            'pairs':pairs,'direct_pair_and_third_steps':steps,'shrink_checks':shrinks,
            'third_source_checks':triples,'endpoint_checksum':checksum,
            'infinite_positive_source_asserted':False}

def repeated_lifts() -> dict:
    rows=[]
    for r in range(17):
        d=U[0]*r+D22;a=V[0]*r+A22
        L,q,B=affine(d);s0=residue(d);M=1<<L
        need(residue(a)==s0+4,'lift residue')
        for k in (0,1,2,(1<<64)+7):
            s=s0+M*k;y=replay(s,d)
            need(replay(s+4,a)==y and v2(139*s+2903)==11*r+5,'lift audit')
            t=(1-s0)*pow(M,-1,3)%3+3*k
            S=s0+M*t;z=(2*S+7)//3
            need(z<S and step(z)==S+4 and replay(z,'1'+a)==replay(S,d),'gain lift')
            rows.append([r,k,L,q,s,y,S,z])
    return {'r_max':16,'rows':rows}

def affine_closure_barrier() -> dict:
    L=14;q=9;M=1<<L;A=3**q;D=A-M;B0=affine(U[1])[2]
    pool={}
    for pp in itertools.combinations(range(L),q):
        w=['0']*L
        for j in pp:w[j]='1'
        word=''.join(w);B=affine(word)[2]
        need(B not in pool,'correction injectivity');pool[B]=word
    triples=[]
    for k in range(1,288):
        for B in sorted(pool):
            if B+k in pool and B+9*k in pool:
                rem=(k*B0-288*B)%D
                need(rem!=0,'affine contraction candidate has integer source')
                triples.append([k,B,rem])
    boundary=[]
    for B in sorted(pool):
        if B+288 in pool and B+2592 in pool and (B0-B)%D==0:
            boundary.append([B,(B0-B)//D])
    need(boundary==[[20963,4],[34159,0]],'unit slope boundary')
    return {'L':L,'q':q,'A_minus_M':D,'source_corrections':[affine(U[i])[2] for i in (1,2,3)],
            'word_count':len(pool),'candidate_grid':len(pool)*287,
            'complete_symbolic_contractions':triples,'integer_compatible_contractions':0,
            'unit_slope_integer_translations':boundary,
            'scope':'one invertible affine map conjugating all three literal maps; arbitrary output words; maps at least one integer to an integer'}

def subalphabet_contractions() -> dict:
    specs=[(1,4,-95,(1,2)),(1,8,-83,(2,3)),(3,32,-241,(2,3))]
    result=[]
    for p,b,d,inds in specs:
        words=[]
        for i in inds:
            L,q,B=affine(U[i]);num=p*B+((1<<L)-3**q)*d
            need(num%b==0,'conjugate correction')
            v=decode(L,q,num//b);need(v is not None,'conjugate word')
            words.append(v)
        pairs=steps=checksum=0
        for n in range(1,7):
            for address in itertools.product(range(2),repeat=n):
                wu=''.join(U[inds[j]] for j in address);full=wu+U[inds[0]]
                r=residue(full);mod=1<<len(full)
                for t in (0,1,(1<<20)+3):
                    S=r+mod*t;need((p*S+d)%b==0,'coordinate integrality')
                    Z=(p*S+d)//b;need(0<Z<S,'coordinate positivity/shrink')
                    x=S;y=Z
                    for j in address:
                        x=replay(x,U[inds[j]]);y=replay(y,words[j]);steps+=28
                        need(b*y-p*x==d,'affine coordinate propagation')
                    pairs+=1;checksum=(checksum+x+y)%((1<<127)-1)
        result.append({'p':p,'b':b,'d':d,'input_indices':list(inds),'output_words':words,
                       'max_blocks':6,'finite_pairs':pairs,'direct_steps':steps,'checksum':checksum})
    return {'families':result,'infinite_positive_source_asserted':False}

def create() -> dict:
    return {'schema':'synchronized-shadow-v1','date':'2026-09-11',
            'base_commit':'12df6b8781957923d8069293f4ad2c0e13c0f7bd',
            'status':'VERIFIED_FINITE','proves_collatz':False,
            'global_ancestor_existence_proved':False,
            'peer_scope':'same full block lengths and same odd count in every block',
            'unit_shadow':shadow_graph(1,1),'two_thirds_shadow':shadow_graph(2,3),
            'equal_coefficient':equal_coefficient(),'macro_checks':macro_checks(),
            'repeated_lifts':repeated_lifts(),'affine_closure_barrier':affine_closure_barrier(),
            'subalphabet_contractions':subalphabet_contractions()}

def scope():
    return {'schema':'synchronized-shadow-scope-v1','status':'VERIFIED_FINITE',
        'proves_collatz':False,'EXT08_used':False,'H112_status':'OPEN','H72_status':'OPEN',
        'zip_sha256':'6b276556e66271daddae1077d9ca7bdc06a421e0414004b71a319e647ab519e2',
        'peer_domain':'same L and q in every prescribed left block; right words unrestricted',
        'height_equal_domain':'equal intrinsic normalized limits, not assumed bounded difference',
        'ratio_initial_integrality':'3 divides 2*S+d for ratio 2/3; graph is an overapproximation',
        'conjugacy_domain':'one affine identity for u2/u3/u4, 0<r<1, at least one integer input and output',
        'coequal_minimality':'minimum q only, same L/q and safe literal words; not P256',
        'all_ancestors_classified':False,'infinite_positive_source_constructed':False,
        'shrink_language_closed':False,'backlog_B1_B6_accepted':False,
        'infinite_proofs_machine_formalized':False,'independent_authorship_claimed':False,
        'global_ancestor_existence_proved':False,'same_height_min_and_max_interchangeable':False}

def regressions():
    root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
    from src.transient_sparsity_search import regressions as older
    old=older(); words=old['words']; paths=old['paths']
    loss=[];P=3**21
    for j in range(1,21):
        v=(1<<(f2(j)-1))*3**(20-j);need(12*v>P,'one-position loss')
        loss.append([j,v,12*v-P])
    thresholds=[]
    for u in U:
        L,q,B=affine(u); M=1<<L;A=3**q
        t=Fraction(4*B+14*M,5*M-4*A)
        need(t<residue(u),'5/6 all-lift cutoff')
        thresholds.append(frac(t))
    ratio_edges=[]
    for d,i,t,w in shadow_graph(2,3)['edges']:
        L,q,B=affine(U[i]);M=1<<L;r=residue(U[i])
        lifts=[k for k in range(3) if (2*(r+M*(100+k))+d)%3==0]
        need(len(lifts)==1,'mod3 source condition')
        k=lifts[0];S=r+M*(100+k);R=(2*S+d)//3
        x=replay(S,U[i]);y=replay(R,w)
        need(3*y-2*x==t,'actual ratio edge')
        ratio_edges.append([d,i,k,S,R,x,y])
    historical=dict(old['historical_sha256'])
    for name in ('phase41_formal.json','ext08_scope_impact.json','critical_safe_mass_evidence.json'):
        historical[name]=hashlib.sha256((root/'artifacts'/name).read_bytes()).hexdigest()
    return {'schema':'synchronized-shadow-regressions-v1','status':'VERIFIED_FINITE',
        'proves_collatz':False,'finite_only':True,'words':words,'paths':paths,
        'q21_loss_margins':loss,'shrink_thresholds':thresholds,'ratio_edge_integer_lifts':ratio_edges,
        'historical_sha256':historical}

def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--artifact-dir',type=Path,required=True)
    args=ap.parse_args();args.artifact_dir.mkdir(parents=True,exist_ok=True);obj=create()
    for name,data in [('evidence',obj),('scope',scope()),('regressions',regressions())]:
        (args.artifact_dir/('synchronized_shadow_'+name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'output':str(args.artifact_dir),'unit_edges':len(obj['unit_shadow']['edges']),
                     'unit_kernel':obj['unit_shadow']['kernel'],
                     'two_thirds_edges':len(obj['two_thirds_shadow']['edges']),
                     'q21_candidates':len(obj['equal_coefficient']['q21_rows']),
                     'finite_macros':{k:v for k,v in obj['macro_checks'].items() if k!='macros'},
                     'lift_rows':len(obj['repeated_lifts']['rows'])},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
