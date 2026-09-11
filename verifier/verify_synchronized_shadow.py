#!/usr/bin/env python3
"""Independent finite reconstruction; never imports generate.py.
Graphs: enumerate all fixed-weight words and source cylinders instead of tracing
one alternative per offset. Kernel: SCC/reverse reachability instead of pruning.
The written infinite proofs still require mathematical review.
"""
from __future__ import annotations
import argparse, functools, itertools, json, math, hashlib, sys
from fractions import Fraction
from pathlib import Path

LEFT=('11011111000','11011011111000','11011110011010','11011110101010')
RIGHT=('11111010100','11111111000100','11111011010100','11111011110000')
D='1101101101011011011010110110101101'
A='1111111111011100011111001100001100'

def check(c,msg):
    if not c:raise ValueError(msg)

def positional(word):
    positions=[i for i,v in enumerate(word) if v=='1'];q=len(positions)
    return len(word),q,sum(2**p*3**(q-1-j) for j,p in enumerate(positions))

def inverse(a,m):
    # Extended Euclid, separate from generator's pow(...,-1,...).
    t,newt,r,newr=0,1,m,a
    while newr:
        q=r//newr;t,newt=newt,t-q*newt;r,newr=newr,r-q*newr
    check(r==1,'inverse domain');return t%m

def source(word):
    L,q,B=positional(word);m=2**L
    return (-B*inverse(3**q,m))%m

def advance(x,word):
    check(type(x)is int and x>0,'positive source required')
    for s in word:
        check((x&1)==(s=='1'),'word not literal')
        x=(x*3+1)>>1 if x&1 else x>>1
    return x

def safe_word(word):
    return all(3**word[:k].count('1')>2**k for k in range(1,len(word)+1))

def frac(t):return [t.numerator,t.denominator]

def ord2(n):
    check(n!=0,'v2 zero');k=0;n=abs(n)
    while n%2==0:n//=2;k+=1
    return k

def floor_power_log(j):
    n=3**j;v=0
    while n>=2:n//=2;v+=1
    return v

@functools.lru_cache(None)
def word_pool(L,q):
    out=[];m=2**L;inv=inverse(3**q,m)
    for pp in itertools.combinations(range(L),q):
        B=sum(2**p*3**(q-1-j) for j,p in enumerate(pp))
        w=['0']*L
        for p in pp:w[p]='1'
        out.append((''.join(w),B,(-B*inv)%m))
    return out

def infinite_kernel(states,edges):
    adj={d:[] for d in states};rev={d:[] for d in states}
    for d,i,t,w in edges:adj[d].append(t);rev[t].append(d)
    # Kosaraju SCC and backward reachability of cyclic components.
    seen=set();order=[]
    def dfs(d):
        seen.add(d)
        for t in adj[d]:
            if t not in seen:dfs(t)
        order.append(d)
    for d in states:
        if d not in seen:dfs(d)
    seen=set();components=[]
    for d in reversed(order):
        if d in seen:continue
        todo=[d];seen.add(d);cc=[]
        while todo:
            z=todo.pop();cc.append(z)
            for p in rev[z]:
                if p not in seen:seen.add(p);todo.append(p)
        components.append(cc)
    live=set()
    for cc in components:
        if len(cc)>1 or any(t==cc[0] for t in adj[cc[0]]):live.update(cc)
    todo=list(live)
    while todo:
        z=todo.pop()
        for p in rev[z]:
            if p not in live:live.add(p);todo.append(p)
    # Reconstruct the supplied layer certificate separately.
    surviving=set(states);layers=[]
    while surviving!=live:
        dead=sorted(d for d in surviving if not any(t in surviving for t in adj[d]))
        check(dead,'SCC/pruning disagreement');layers.append(dead);surviving.difference_update(dead)
    # A state fails the all-label property if an adversary has a finite exit.
    ed={(d,i):t for d,i,t,w in edges}
    bad={d for d in states if any((d,i) not in ed for i in range(4))}
    while True:
        more={d for d in states if any(ed.get((d,i)) in bad for i in range(4))}
        new=bad|more
        if new==bad:break
        bad=new
    return sorted(live),layers,sorted(set(states)-bad)

def graph(p,b):
    data=[];lows=[];highs=[]
    for word in LEFT:
        L,q,B=positional(word);P=3**q;M=2**L
        mn=P-2**q;mx=2**(L-q)*mn
        lo=Fraction(p*B-b*mx,P-M);hi=Fraction(p*B-b*mn,P-M)
        lows.append(lo);highs.append(hi)
        data.append([L,q,B,mn,mx,frac(lo),frac(hi)])
    low=min(lows);high=max(highs);lo=math.ceil(low);hi=math.floor(high)
    edges=[];same_weight=0
    for i,u in enumerate(LEFT):
        L,q,B=positional(u);M=2**L;P=3**q;r=source(u)
        for v,Bv,rv in word_pool(L,q):
            residue_d=(b*rv-p*r)%M
            kmin=-((residue_d-lo)//M);kmax=(hi-residue_d)//M
            for k in range(kmin,kmax+1):
                d=residue_d+M*k;same_weight+=1
                check(lo<=d<=hi,'offset enumeration')
                num=P*d+b*Bv-p*B
                check(num%M==0,'edge congruence')
                t=num//M
                if lo<=t<=hi:edges.append([d,i,t,v])
    edges.sort();check(len({(e[0],e[1]) for e in edges})==len(edges),'not deterministic')
    states=list(range(lo,hi+1));live,layers,univ=infinite_kernel(states,edges)
    return {'p':p,'b':b,'real_bounds':[frac(low),frac(high)],'integer_bounds':[lo,hi],
            'bounds_rows':data,'transition_cases':4*len(states),'same_weight_cases':same_weight,
            'edges':edges,'kernel':live,'removed_layers':layers,
            'essential_edges':[e for e in edges if e[0]in live and e[2]in live],
            'universal_kernel':univ}

def valuation_decode(L,q,B):
    positions=[];remaining=B
    for j in range(q):
        if remaining<=0:return None
        p=ord2(remaining)
        if p>=L or (positions and p<=positions[-1]):return None
        positions.append(p);remaining-=2**p*3**(q-1-j)
    if remaining!=0:return None
    w=['0']*L
    for p in positions:w[p]='1'
    return ''.join(w)

def coequal():
    low=[]
    for q in range(1,21):
        pp=[floor_power_log(j) for j in range(q)];P=3**q
        mx=sum(2**p*3**(q-1-j) for j,p in enumerate(pp));mn=P-2**q
        margin=4*P-mx+mn;check(margin>0,'small q margin')
        low.append([q,mx,mn,margin])
    q=21;P=3**q;pp=[floor_power_log(j) for j in range(q)]
    mx=sum(2**p*3**(q-1-j) for j,p in enumerate(pp));allow=mx-5*P+2**q
    check(6*allow<P,'one-defect reduction invalid')
    rows=[]
    for j in [None]+[j for j in range(1,q) if pp[j]-pp[j-1]==2]:
        positions=pp.copy()
        if j is not None:positions[j]-=1
        B=sum(2**p*3**(q-1-k) for k,p in enumerate(positions))
        for L in range(positions[-1]+1,floor_power_log(q)+1):
            check(valuation_decode(L,q,B-4*P) is None,'q21 unexpected')
            rows.append([j,L,B,B-4*P])
    L,q,bd=positional(D);l,qq,ba=positional(A);s=source(D);r=source(A);y=advance(s,D)
    check(L==l and q==qq and r-s==4 and bd-ba==4*3**q,'coequal example algebra')
    check(advance(r,A)==y and safe_word(D) and safe_word(A),'coequal literal/safety')
    return {'q1_to_q20':low,'q21_allowance':allow,'q21_rows':rows,
            'witness':{'small_word':D,'large_word':A,'L':L,'q':q,
                       'B_small_source':bd,'B_large_source':ba,'small_source':s,
                       'large_source':r,'endpoint':y}}

def macro_record():
    macros=[]
    for u,v in zip(LEFT,RIGHT):
        L,q,B=positional(u);l,qq,bb=positional(v)
        check((l,qq)==(L,q) and bb-B==4*(2**L-3**q),'four macros')
        check(safe_word(u) and safe_word(v),'safety')
        macros.append({'u':u,'v':v,'L':L,'q':q,'B_u':B,'B_v':bb,
                       'r_u':source(u),'r_v':source(v),'centre':frac(Fraction(-B,3**q-2**L))})
    num=pairs=steps=shrinks=triples=0;chk=0
    for depth in range(1,6):
        for labels in itertools.product(range(4),repeat=depth):
            num+=1;w=''.join(LEFT[i] for i in labels);future=w+LEFT[0]
            rr=source(future);mod=2**len(future)
            for lift in (0,1,2**20+3):
                s=rr+mod*lift;x=s;y=s+4;pairs+=1
                for i in labels:
                    x=advance(x,LEFT[i]);y=advance(y,RIGHT[i]);steps+=2*len(LEFT[i])
                    check(y==x+4,'parallel boundary')
                first=advance(s,LEFT[labels[0]])
                check(first%6==1,'boundary not odd 1 mod3')
                z=(2*first+7)//3;check(z%2==1 and (3*z+1)//2==first+4,'predecessor')
                check(6*z<5*s,'source shrink');shrinks+=1
                if labels[0]==1:
                    ee=advance(s+3,'01111111010100')
                    check(ee==first+4 and (s+3)%2==0,'third peer')
                    for i in labels[1:]:ee=advance(ee,RIGHT[i])
                    check(ee==y and (s+3)//2<s,'half peer')
                    steps+=sum(len(LEFT[i]) for i in labels);triples+=1
                chk=(chk+x+y+z)%(2**127-1)
    return {'macros':macros,'max_blocks':5,'schedules':num,'pairs':pairs,
            'direct_pair_and_third_steps':steps,'shrink_checks':shrinks,
            'third_source_checks':triples,'endpoint_checksum':chk,
            'infinite_positive_source_asserted':False}

def lifts():
    rows=[]
    for r in range(17):
        d=LEFT[0]*r+D;a=RIGHT[0]*r+A;L,q,B=positional(d);n0=source(d);M=2**L
        check(source(a)==n0+4,'lift first residue')
        for k in (0,1,2,2**64+7):
            s=n0+M*k;y=advance(s,d)
            check(advance(s+4,a)==y and ord2(139*s+2903)==11*r+5,'lift collision/rank')
            t=((1-n0)*inverse(M,3))%3+3*k;S=n0+M*t;z=(2*S+7)//3
            check(z<S and advance(z,'1'+a)==advance(S,d),'lift strict improvement')
            rows.append([r,k,L,q,s,y,S,z])
    return {'r_max':16,'rows':rows}

def closure_barrier():
    L=14;q=9;D=3**q-2**L;B0=positional(LEFT[1])[2]
    vals=sorted(B for w,B,r in word_pool(L,q));available=set(vals);rows=[]
    # Generate nearby ordered pairs instead of a scale/correction grid.
    for i,B in enumerate(vals):
        for C in vals[i+1:]:
            k=C-B
            if k>=288:break
            if B+9*k not in available:continue
            rem=(k*B0-288*B)%D
            check(rem!=0,'integer-compatible common conjugacy')
            rows.append([k,B,rem])
    rows.sort();boundary=[]
    for B in vals:
        if B+288 in available and B+2592 in available and (B0-B)%D==0:
            boundary.append([B,(B0-B)//D])
    check(boundary==[[20963,4],[34159,0]],'translation boundary')
    return {'L':L,'q':q,'A_minus_M':D,'source_corrections':[positional(LEFT[i])[2] for i in (1,2,3)],
            'word_count':len(vals),'candidate_grid':len(vals)*287,
            'complete_symbolic_contractions':rows,'integer_compatible_contractions':0,
            'unit_slope_integer_translations':boundary,
            'scope':'one invertible affine map conjugating all three literal maps; arbitrary output words; maps at least one integer to an integer'}

def pair_contractions():
    specs=[(1,4,-95,(1,2)),(1,8,-83,(2,3)),(3,32,-241,(2,3))];out=[]
    for p,b,d,inds in specs:
        vv=[]
        for i in inds:
            L,q,B=positional(LEFT[i]);num=p*B+(2**L-3**q)*d
            check(num%b==0,'divisibility of correction')
            word=valuation_decode(L,q,num//b);check(word is not None,'conjugate not literal')
            vv.append(word)
        count=steps=chk=0
        for n in range(1,7):
            for address in itertools.product(range(2),repeat=n):
                w=''.join(LEFT[inds[j]] for j in address);full=w+LEFT[inds[0]]
                rr=source(full);mod=2**len(full)
                for t in (0,1,2**20+3):
                    S=rr+mod*t;check((p*S+d)%b==0,'initial integer coordinate')
                    Z=(p*S+d)//b;check(0<Z<S,'initial source decrease')
                    x=S;y=Z
                    for j in address:
                        x=advance(x,LEFT[inds[j]]);y=advance(y,vv[j]);steps+=28
                        check(b*y-p*x==d,'exact coordinate relation')
                    count+=1;chk=(chk+x+y)%(2**127-1)
        out.append({'p':p,'b':b,'d':d,'input_indices':list(inds),'output_words':vv,
                    'max_blocks':6,'finite_pairs':count,'direct_steps':steps,'checksum':chk})
    return {'families':out,'infinite_positive_source_asserted':False}

@functools.lru_cache(None)
def reconstruct():
    return {'schema':'synchronized-shadow-v1','date':'2026-09-11',
            'base_commit':'12df6b8781957923d8069293f4ad2c0e13c0f7bd',
            'status':'VERIFIED_FINITE','proves_collatz':False,
            'global_ancestor_existence_proved':False,
            'peer_scope':'same full block lengths and same odd count in every block',
            'unit_shadow':graph(1,1),'two_thirds_shadow':graph(2,3),
            'equal_coefficient':coequal(),'macro_checks':macro_record(),'repeated_lifts':lifts(),
            'affine_closure_barrier':closure_barrier(),'subalphabet_contractions':pair_contractions()}

def normalized_json(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)

def verify_data(obj):
    # Canonical serialization distinguishes bool/int and float/int and rejects extras.
    check(normalized_json(obj)==normalized_json(reconstruct()),'independent reconstruction mismatch')
    check(obj['proves_collatz'] is False,'proof boundary')
    return {'valid':True,'generator_imported':False,'independent_external_review':False,
            'proves_collatz':False,'unit_offset_cases':obj['unit_shadow']['transition_cases'],
            'unit_edges':len(obj['unit_shadow']['edges']),
            'two_thirds_cases':obj['two_thirds_shadow']['transition_cases'],
            'two_thirds_edges':len(obj['two_thirds_shadow']['edges']),
            'enumerated_word_corpus':sum(len(word_pool(L,q)) for L,q in ((11,7),(14,9))),
            'q21_complete_remainder':len(obj['equal_coefficient']['q21_rows']),
            'finite_schedules':obj['macro_checks']['schedules'],
            'finite_pairs':obj['macro_checks']['pairs'],
            'direct_pair_and_third_steps':obj['macro_checks']['direct_pair_and_third_steps'],
            'third_source_checks':obj['macro_checks']['third_source_checks'],
            'lift_rows':len(obj['repeated_lifts']['rows']),
            'common_affine_candidates':len(obj['affine_closure_barrier']['complete_symbolic_contractions']),
            'subalphabet_finite_pairs':sum(v['finite_pairs'] for v in obj['subalphabet_contractions']['families']),
            'scope':'Finite graph complete only under proved bounded affine-offset and synchronized per-block-count hypotheses; written proofs in the audit REPORT.md, not formalized.'}

def no_duplicates(pairs):
    out={}
    for k,v in pairs:
        check(k not in out,'duplicate JSON key');out[k]=v
    return out

def same(obj,expected):
    check(normalized_json(obj)==normalized_json(expected),'exact field/type/scope mismatch')

def scope_reference():
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

def forced_single_label(edges):
    # Negative live states must form a DAG after removing single-label loops.
    remaining={d for d,i,t,w in edges if d<0}
    loops={d:i for d,i,t,w in edges if d==t and d<0}
    check(set(loops.values())<={0,3},'unexpected eventual label')
    rank={d:0 for d in loops}
    for d in loops:
        check(all(t==d and i==loops[d] for dd,i,t,w in edges if dd==d),'loop escape')
    remaining-=rank.keys()
    while remaining:
        ready={d for d in remaining if all(t in rank for dd,i,t,w in edges if dd==d)}
        check(ready,'negative nontrivial cycle')
        for d in ready:rank[d]=1+max(rank[t] for dd,i,t,w in edges if dd==d)
        remaining-=ready
    return sorted(rank.items())

def regression_reference():
    root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
    from verifier.verify_transient_sparsity import reconstruct_regressions
    from verifier.verify_phase41 import formal_expected
    old=reconstruct_regressions();loss=[];P=3**21
    for j in range(1,21):
        v=2**(floor_power_log(j)-1)*3**(20-j);check(12*v>P,'one-position loss')
        loss.append([j,v,12*v-P])
    thresholds=[]
    for w in LEFT:
        L,q,B=positional(w);c=Fraction(3**q,2**L);t=(4*Fraction(B,2**L)+14)/(5-4*c)
        check(c<Fraction(5,4) and t<source(w),'all-lift shrink threshold')
        thresholds.append(frac(t))
    ratio_edges=[]
    for d,i,t,w in graph(2,3)['edges']:
        L,q,B=positional(LEFT[i]);M=2**L;r=source(LEFT[i])
        k=(-(2*(r+100*M)+d)*inverse(2*M%3,3))%3
        S=r+(100+k)*M;check((2*S+d)%3==0,'initial mod3 condition');R=(2*S+d)//3
        l,qq,Bv=positional(w)
        check(R>0 and R%M==source(w),'positive literal cylinder')
        x=(3**q*S+B)//M;y=(3**q*R+Bv)//M
        check(3*y-2*x==t,'ratio edge affine propagation')
        ratio_edges.append([d,i,k,S,R,x,y])
    historical={**old['historical_sha256'],
        'phase41_formal.json':'aa7f6c5feb4ff7970d9c8d275f410fa9e89db68e274f13cb0711ca2db20165be',
        'ext08_scope_impact.json':'25678454f558515adba6683df3bcd4d2daf5f36bbcbd632f17e6326e6d3f0007',
        'critical_safe_mass_evidence.json':'01da8c0829d1bf171def08f4a20f995f3cfe7a43a7e56860ce0c0eb5975d3757'}
    for name,h in historical.items():
        check(hashlib.sha256((root/'artifacts'/name).read_bytes()).hexdigest()==h,'historical artifact changed')
    same(json.loads((root/'artifacts/phase41_formal.json').read_text(),object_pairs_hook=no_duplicates),formal_expected())
    return {'schema':'synchronized-shadow-regressions-v1','status':'VERIFIED_FINITE',
        'proves_collatz':False,'finite_only':True,'words':old['words'],'paths':old['paths'],
        'q21_loss_margins':loss,'shrink_thresholds':thresholds,'ratio_edge_integer_lifts':ratio_edges,
        'historical_sha256':historical}

def audit(directory):
    def read(name):
        return json.loads((directory/('synchronized_shadow_'+name+'.json')).read_text(),object_pairs_hook=no_duplicates)
    report=verify_data(read('evidence'));same(read('scope'),scope_reference())
    reg=regression_reference();same(read('regressions'),reg)
    ranks=[forced_single_label(reconstruct()[name]['essential_edges']) for name in ('unit_shadow','two_thirds_shadow')]
    report.update(status='VERIFIED_FINITE',negative_exit_ranks=ranks,regression_words=len(reg['words']),
        normalization_paths=len(reg['paths']),ratio_integer_lifts=len(reg['ratio_edge_integer_lifts']),
        NG46_potentials_checked=2,NG45_formal_evidence_rebuilt=True,historical_files_preserved=6,
        infinite_positive_source_constructed=False,all_ancestors_classified=False,EXT08_used=False,
        backlog_accepted=False)
    return report

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--artifact-dir',type=Path,required=True)
    ap.add_argument('--output',type=Path);a=ap.parse_args()
    try: result=audit(a.artifact_dir)
    except (ValueError,TypeError,KeyError,OSError,ZeroDivisionError) as exc:
        print(json.dumps({'valid':False,'error':str(exc),'proves_collatz':False}));return 1
    if a.output:a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,ensure_ascii=False,sort_keys=True));return 0
if __name__=='__main__':sys.exit(main())
