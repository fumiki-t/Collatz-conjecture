"""Independent finite reconstruction for the safe-root-frontier supplement.

No search imports. Small windows are checked against *literal forward orbits*;
their extrema/candidate counts are rebuilt by a binary recurrence. Large
controls decode by the canonical residue and literal iteration, not valuations.
All-length conclusions additionally require the separate certificate checker.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import itertools
import json
from pathlib import Path
import sys
if __package__ in (None, ''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from verifier.verify_safe_root_certificate import check, req, position_map, run

def no_duplicates(pairs):
    d={}
    for k,v in pairs:
        req(k not in d,'duplicate JSON key');d[k]=v
    return d

def same(a,b):
    req(json.dumps(a,sort_keys=True,allow_nan=False)==json.dumps(b,sort_keys=True,allow_nan=False),
        'exact evidence field/type/value mismatch')

def trajectory(z,L):
    x=z;out=[]
    for _ in range(L):
        b=x%2;out.append(str(b));x=(3*x+1)//2 if b else x//2
    return x,''.join(out)

def safe_word(w):
    return all(3**w[:k].count('1')>2**k for k in range(1,len(w)+1))

@lru_cache(None)
def extrema_reference():
    # DFS enumerates every branch, including branches already known unsafe.
    # Affine recurrence differs from the generator's position-mask sums.
    table={};counts=[0]*20;nodes=0
    stack=[(0,0,1,0,True)]
    while stack:
        L,q,A,B,safe=stack.pop()
        if L<=18:nodes+=1
        if safe:
            counts[L]+=1
            if q:
                old=table.get((q,L),(B,B,0))
                table[q,L]=(min(B,old[0]),max(B,old[1]),old[2]+1)
        if L==19:continue
        M=1<<L
        stack.append((L+1,q,A,B,safe and A>2*M))
        stack.append((L+1,q+1,3*A,3*B+M,safe and 3*A>2*M))
    rows=[{'q':q,'L':L,'min':lo,'max':hi,'safe_words':n}
        for (q,L),(lo,hi,n) in sorted(table.items(),key=lambda x:(x[0][1],x[0][0])) if L<=18]
    return {'word_checks':nodes,'extrema_rows':rows,'safe_counts':counts[:19]},table

def correction_range(q,L):
    # Choose each odd position from right to left, respecting its own safety
    # limit and the strict ordering of all positions to its right.
    next_pos=L;B=0
    for j in reversed(range(q)):
        p=min(next_pos-1,(3**j).bit_length()-1)
        B+=2**p*3**(q-1-j);next_pos=p
    return 3**q-2**q,B

def window_reference(y,Q,g,tie,table=None):
    rows=[];candidates=pairs=0
    if g==1 and tie is not None and y<tie:
        rows.append({'source':y,'endpoint':y,'length':0,'odd_count':0,'correction':0,'word':'','kind':'equal_smaller'})
    for q in range(1,Q+1):
        A=3**q
        # Enumerate all safe terminal lengths; no logarithmic-band shortcut.
        for L in range(q,A.bit_length()):
            M=2**L;c=Fraction(A,M)
            if c>=y or c<g or (c==g and tie is None):continue
            pairs+=1
            lo,hi=(table[q,L][:2] if table is not None else correction_range(q,L))
            zmin=max(1,-((hi-M*y)//A));zmax=(M*y-lo)//A
            if c==g:zmax=min(zmax,tie-1)
            for z in range(zmin,zmax+1):
                if z%(4 if q>=2 else 2)!=(3 if q>=2 else 1):continue
                candidates+=1
                # Reconstruct from the literal integer, independent of B decoder.
                x,w=trajectory(z,L)
                if x!=y or w.count('1')!=q or not safe_word(w):continue
                aa,mm,B=position_map(w);req((aa,mm)==(A,M),'literal count')
                rows.append({'source':z,'endpoint':y,'length':L,'odd_count':q,
                    'correction':B,'word':w,'kind':'strict' if c>g else 'equal_smaller'})
    return rows,{'pairs':pairs,'integer_candidates':candidates,'decode_calls':candidates,
        'q_limit':Q,'complete_all_Q':False}

@lru_cache(None)
def direct_reference():
    _,table=extrema_reference();safe_entries=defaultdict(list);raw_entries=defaultdict(list)
    steps=0
    for z in range(1,257):
        for L in range(1,20):
            x,w=trajectory(z,L);q=w.count('1');steps+=1
            if x>256 or q>12 or 3**q<=2**L:continue
            r=(z,L,q,w,Fraction(3**q,2**L));raw_entries[x].append(r)
            if safe_word(w):safe_entries[x].append(r)
    qs=[1,2,4,8,12];gs=[Fraction(s) for s in ['1','9/8','3/2','27/16','2','9/4','3','4']]
    rows=[];hits=candidates=0
    for y in range(1,257):
        for Q in qs:
            for g in gs:
                S=max(1,int(Fraction(y,g)))
                got,stat=window_reference(y,Q,g,S,table)
                expected={(z,L,q,w,'strict' if c>g else 'equal_smaller')
                    for z,L,q,w,c in safe_entries[y] if q<=Q and (c>g or c==g and z<S)}
                actual={(r['source'],r['length'],r['odd_count'],r['word'],r['kind']) for r in got}
                req(actual==expected and len(got)==len(actual),'literal window completeness')
                raw=any(q<=Q and (c>g or c==g and z<S) for z,L,q,w,c in raw_entries[y])
                req(raw==bool(got),'global valley reduction')
                rows.append({'endpoint':y,'Q':Q,'gamma':str(g),'tie_source':S,'witnesses':got,'statistics':stat})
                hits+=len(got);candidates+=stat['integer_candidates']
    return {'endpoint_max':256,'odd_limits':qs,'thresholds':list(map(str,gs)),
        'queries':len(rows),'forward_steps':steps,'safe_witness_occurrences':hits,
        'decoder_candidates':candidates,'rows':rows}

def controls_reference():
    rows=[]
    for S,L,Q in [(7435082751,34,32),(29023002619,34,32),(358030447,29,32),(7,4,128),(703,80,128)]:
        y,w=trajectory(S,L);a,m,_=position_map(w);hs,st=window_reference(y,Q,Fraction(a,m),S)
        rows.append({'source':S,'length':L,'endpoint':y,'odd_budget':Q,'statistics':st,'witnesses':hs})
    for p in [3,17,80,256,1024]:
        S=2**p-1;L=min(p,24);y,w=trajectory(S,L);a,m,_=position_map(w)
        hs,st=window_reference(y,24,Fraction(a,m),S)
        rows.append({'source_bit_length':p,'target_length':L,'statistics':st,'witness_count':len(hs)})
    for p in [80,256,1024]:
        S=2**p+7;L=4;y,w=trajectory(S,L);a,m,_=position_map(w)
        hs,st=window_reference(y,24,Fraction(a,m),S);req(hs,'nonvacuous large source')
        rows.append({'large_nonvacuous_source_bits':p+1,'target_length':L,'statistics':st,'witness_count':len(hs)})
    return rows

def all_length_reference(certs):
    req(type(certs) is list,'certificate list')
    queries=[(S,L) for S in range(1,128) for L in range(21)]+[(703,80)]
    req(len(certs)==len(queries),'query coverage')
    # Complete first-visit coefficients, since every positive return contracts.
    by_endpoint=defaultdict(dict);states=set()
    for z in range(1,706):
        x=z;c=Fraction(1);seen={}
        while x not in seen:
            seen[x]=c;states.add(x);by_endpoint[x][z]=c
            if x%2:x=(3*x+1)//2;c*=Fraction(3,2)
            else:x//=2;c/=2
        req(c<seen[x],'positive return must contract')
    stats=Counter();rows=[]
    for (S,L),cert in zip(queries,certs):
        req(check(cert),'certificate arithmetic')
        y,w=trajectory(S,L);req(cert['source']==S and cert['target_word']==w,'query identity')
        A,M,_=position_map(w);g=Fraction(A,M);bound=(M*y-1)//A
        req(bound<=705,'source oracle cap')
        expected=any(z<=bound and (c>g or c==g and z<S) for z,c in by_endpoint[y].items())
        req((cert['status']=='IMPROVEMENT')==expected,'all-length first-return comparison')
        stats[cert['status']]+=1
        if not expected:
            d=cert['diagnostics'];stats['certified_frontier_roots']+=d['frontier_size']
            stats['tree_nodes']+=d['tree_nodes'];stats['trace_steps']+=d['trace_steps']
        rows.append({'source':S,'length':L,'status':cert['status']})
    return {'queries':len(rows),'status_counts':dict(stats),'reference_roots':705,
        'reference_states':len(states),'cycle_checks':705,'rows':rows}

def regression_reference():
    words={'11101','1100'}
    for n in range(1,5):
        words.update(''.join(p) for p in itertools.product(('110','111'),repeat=n))
    for r in range(5):
        for s in range(5):
            if r+s:words.add('11101'*r+'1100'*s)
    for m in range(3,13):words.add(trajectory(2**m-1,m+3)[1])
    for m in range(1,9):words.add(trajectory(8**m-5,3*m+3)[1])
    rows=[]
    for w in sorted(words,key=lambda w:(len(w),w)):
        # Build the residue by lifting and checking the next literal parity,
        # rather than the generator's modular inverse of the affine map.
        r=0
        for L,b in enumerate(w):
            x,_=trajectory(r,L)
            if x%2!=int(b):r+=2**L
        z=r or 2**len(w);y,actual=trajectory(z,len(w));req(actual==w,'cylinder lift')
        a,m,B=position_map(w);q=w.count('1');safe=safe_word(w)
        if safe and q:
            lo,hi=correction_range(q,len(w));req(lo<=B<=hi,'adversarial safe extrema')
        rows.append({'word':w,'source':z,'endpoint':y,'q':q,'B':B,'safe':safe})
    req(run(11,'1')[-1][0]==17 and run(11,'11010')[-1][0]==10 and not safe_word('11010'),'short-hit obstruction')
    req(run(6,'011')[-1][0]==run(3,'11')[-1][0]==8,'global source versus same source')
    failures=[]
    for S in range(1,15):
        N=(S-1).bit_length();early=False;surviving=False
        for z in range(1,S):
            x=z;a=m=1;w=''
            while a>=m:
                if x==S and (a>m or z<S):
                    early=True
                    if safe_word(trajectory(z,N)[1]):surviving=True
                bit=x%2;w+=str(bit);m*=2
                if bit:x=(3*x+1)//2;a*=3
                else:x//=2
        if early and not surviving:failures.append(S)
    req(failures==[14],'minimum empty-target short-hit obstruction')
    return {'schema':'safe-root-frontier-regressions-v1','proves_collatz':False,'finite_only':True,
        'family_rows':rows,'short_hit_obstruction':{'target_source':17,'target_word':'',
        'ancestor_source':11,'ancestor_word':'1','first_crossing_word':'11010'},
        'minimal_empty_target_obstruction':{'source':14,'ancestor_source':9,'ancestor_word':'1','depth':4,'crossing_word':'10','minimality_domain':'positive empty targets ordered by source'},
        'same_source_valley_failure':{'source':6,'word':'011','endpoint':8,'valley_source':3,'safe_suffix':'11'}}

REJECTIONS=['schema version','query scope','overclaim flag','source bound','depth',
    'float source bound','float depth','missing leaf','duplicate leaf','missing trace',
    'duplicate trace','frontier source','false empty','false crossing','unknown leaf',
    'trace root','trace parity','unknown cut','unknown result','source bool','target invalid',
    'short hit before crossing leaf','actual budget exhaustion']

def scope_reference():
    return {'all_length_certificates':'all positive literal sources, all lengths and Q, lexicographic coefficient then smaller source',
        'fixed_Q_complete_all_Q':False,'initial_frontier_bound_is_trace_time_bound':False,
        'general_termination_proved':False,'global_ancestor_existence_proved':False,
        'B2_B6_accepted':False,'EXT08_used':False}

def audit(directory):
    def read(name):return json.loads((directory/('safe_root_frontier_'+name+'.json')).read_text(),object_pairs_hook=no_duplicates)
    data=read('evidence');certs=read('certificates');reg=read('regressions')
    ex,_=extrema_reference();direct=direct_reference();whole=all_length_reference(certs)
    expected={'extrema':ex,'direct_oracles':direct,'all_length_certificates':whole,
        'controls':controls_reference(),'tamper_rejections':REJECTIONS,
        'schema':'safe-root-frontier-evidence-v1','scope':scope_reference(),'proves_collatz':False}
    same(data,expected);same(reg,regression_reference())
    # Retain prior formal and all-length potential counterexamples by their
    # existing independent verifiers, not by trusting old status fields.
    from verifier.verify_transient_sparsity import reconstruct_regressions
    from verifier.verify_phase41 import formal_expected
    old=reconstruct_regressions()
    root=Path(__file__).resolve().parents[1]
    same(json.loads((root/'artifacts/phase41_formal.json').read_text()),formal_expected())
    return {'valid':True,'status':'VERIFIED_FINITE','generator_imported':False,
        'word_checks':ex['word_checks'],'extrema_pairs':len(ex['extrema_rows']),
        'fixed_Q_queries':direct['queries'],'decoder_candidates':direct['decoder_candidates'],
        'safe_witness_occurrences':direct['safe_witness_occurrences'],
        'all_length_queries':whole['queries'],'status_counts':whole['status_counts'],
        'reference_states':whole['reference_states'],'family_words':len(reg['family_rows']),
        'NG46_potentials_checked':2,'NG45_formal_evidence_rebuilt':True,
        'general_termination_proved':False,'global_ancestor_existence_proved':False,
        'EXT08_used':False,'proves_collatz':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--artifact-dir',type=Path,required=True)
    p.add_argument('--output',type=Path);a=p.parse_args()
    try:result=audit(a.artifact_dir)
    except (ValueError,KeyError,TypeError,OSError,ZeroDivisionError) as e:
        print(json.dumps({'valid':False,'error':str(e),'proves_collatz':False}));return 1
    if a.output:a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True));return 0

if __name__=='__main__':sys.exit(main())
