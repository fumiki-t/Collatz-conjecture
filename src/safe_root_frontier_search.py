from __future__ import annotations
from fractions import Fraction
from collections import defaultdict,Counter
import json,copy,time,argparse
from pathlib import Path
from src.safe_ancestor_window import affine,literal,bounds,decode,scan
from src.safe_root_frontier import search
from verifier.verify_safe_root_certificate import check,position_map

OUT=Path('artifacts')

def require(c,msg):
    if not c:raise RuntimeError(msg)

def extrema():
    observed={};counts=[0]*19;words=0
    for L in range(19):
      for mask in range(1<<L):
        words+=1;ps=[j for j in range(L) if(mask>>j)&1];q=len(ps)
        a=1;is_safe=True
        for j in range(L):
            if(mask>>j)&1:a*=3
            if a<=1<<(j+1):is_safe=False;break
        if not is_safe:continue
        counts[L]+=1
        if not q:continue
        B=sum((1<<p)*3**(q-1-i) for i,p in enumerate(ps))
        key=q,L
        if key not in observed:observed[key]=[B,B,1]
        else:observed[key][0]=min(observed[key][0],B);observed[key][1]=max(observed[key][1],B);observed[key][2]+=1
        w=''.join('1' if(mask>>j)&1 else '0' for j in range(L))
        require(decode(q,L,B)==w,'decoder')
    rows=[]
    for L in range(1,19):
      for q in range(1,L+1):
        bd=bounds(q,L)
        if (q,L) not in observed:require(bd is None,'spurious extremum');continue
        require(bd is not None,'missing extremum')
        A,lo,hi,ps=bd
        require(observed[q,L][:2]==[lo,hi],'extremum mismatch')
        require(all(ps[j]<ps[j+1] for j in range(q-1)),'positions')
        rows.append({'q':q,'L':L,'min':lo,'max':hi,'safe_words':observed[q,L][2]})
    return {'word_checks':words,'extrema_rows':rows,'safe_counts':counts}

def direct_oracles():
    YMAX=256;QMAX=12;LMAX=(3**QMAX).bit_length()-1
    entries=defaultdict(list);raw_entries=defaultdict(list);steps=0
    for z in range(1,YMAX+1):
        x=z;a=1;m=1;q=0;w='';safety=True
        for L in range(1,LMAX+1):
            bit=x&1;w+=str(bit);x=(3*x+1)//2 if bit else x//2;m*=2
            if bit:a*=3;q+=1
            steps+=1;safety=safety and a>m
            if q>QMAX or x>YMAX or a<=m:continue
            row=(z,L,q,w,Fraction(a,m));raw_entries[x].append(row)
            if safety:entries[x].append(row)
    gammas=[Fraction(1),Fraction(9,8),Fraction(3,2),Fraction(27,16),Fraction(2),Fraction(9,4),Fraction(3),Fraction(4)]
    qs=[1,2,4,8,12];queries=0;hits=0;candidates=0;query_rows=[]
    for y in range(1,YMAX+1):
      for Q in qs:
       for g in gammas:
        S=max(1,(y*g.denominator)//g.numerator)
        oracle,st=scan(y,Q,g,S)
        got={(h.source,h.length,h.odd_count,h.word,h.kind) for h in oracle}
        expected={(z,L,q,w,'strict' if c>g else 'equal_smaller') for z,L,q,w,c in entries[y] if q<=Q and(c>g or(c==g and z<S))}
        raw=any(q<=Q and(c>g or(c==g and z<S)) for z,L,q,w,c in raw_entries[y])
        require(got==expected,'window oracle disagrees')
        require(bool(got)==raw,'valley existence mismatch')
        require(len(got)==len(oracle),'duplicate witness')
        queries+=1;hits+=len(got);candidates+=st['integer_candidates']
        query_rows.append({'endpoint':y,'Q':Q,'gamma':str(g),'tie_source':S,
            'witnesses':[h.__dict__ for h in oracle],'statistics':st})
    return {'endpoint_max':YMAX,'odd_limits':qs,'thresholds':[str(x)for x in gammas],'queries':queries,'forward_steps':steps,'safe_witness_occurrences':hits,'decoder_candidates':candidates,'rows':query_rows}

def all_length_certificates():
    rootmax=705;reference={};allstates=set();cycle_count=0
    for z in range(1,rootmax+1):
        x=z;a=1;m=1;w='';seen={};hits={};coeff=[]
        while x not in seen:
            seen[x]=len(w);hits[x]=(Fraction(a,m),w);coeff.append(Fraction(a,m));allstates.add(x)
            bit=x&1;w+=str(bit);m*=2
            if bit:a*=3;x=(3*x+1)//2
            else:x//=2
        require(Fraction(a,m)<coeff[seen[x]],'noncontracting positive cycle')
        reference[z]=hits;cycle_count+=1
    query_list=[(S,L) for S in range(1,128) for L in range(21)]+[(703,80)]
    stats=Counter();certs=[];rows=[]
    for S,L in query_list:
        y,w,_=literal(S,L);A,M,B,Q=affine(w);g=Fraction(A,M)
        b=(M*y-1)//A;require(b<=rootmax,'reference source cap')
        expected=any(y in reference[z] and(reference[z][y][0]>g or(reference[z][y][0]==g and z<S)) for z in range(1,b+1))
        c=search(S,L);require(check(c),'frontier certificate rejected')
        require((c['status']=='IMPROVEMENT')==expected,'complete reference mismatch')
        stats[c['status']]+=1
        if c['status']=='NO_LEX_IMPROVEMENT':
            stats['certified_frontier_roots']+=c['diagnostics']['frontier_size'];stats['tree_nodes']+=c['diagnostics']['tree_nodes'];stats['trace_steps']+=c['diagnostics']['trace_steps']
        certs.append(c)
        rows.append({'source':S,'length':L,'status':c['status']})
    write_json('certificates',certs)
    return {'queries':len(rows),'status_counts':dict(stats),'reference_roots':rootmax,'reference_states':len(allstates),'cycle_checks':cycle_count,'rows':rows}

def controls():
    examples=[(7435082751,34,32),(29023002619,34,32),(358030447,29,32),(7,4,128),(703,80,128)]
    rows=[]
    for S,L,Qmax in examples:
        y,w,_=literal(S,L);A,M,B,Q=affine(w)
        hits,stats=scan(y,Qmax,Fraction(A,M),S)
        for h in hits:
            yy,ww,_=literal(h.source,h.length)
            require(yy==y and ww==h.word,'control literal mismatch')
        rows.append({'source':S,'length':L,'endpoint':y,'odd_budget':Qmax,'statistics':stats,'witnesses':[h.__dict__ for h in hits]})
    require(any(h['kind']=='equal_smaller' and h['source']==7435082747 for h in rows[0]['witnesses']),'q22 equal collision lost')
    require(any(h['source']==14511501311 for h in rows[1]['witnesses']),'negative carry q22 lost')
    require(any(h['source']==151044095 for h in rows[2]['witnesses']),'NG43 valley source lost')
    require(not rows[3]['witnesses'] and not rows[4]['witnesses'],'known geodesic control mismatch')
    for p in [3,17,80,256,1024]:
        S=(1<<p)-1;L=min(p,24);y,w,_=literal(S,L);A,M,B,Q=affine(w)
        hs,st=scan(y,24,Fraction(A,M),S)
        for h in hs:require(literal(h.source,h.length)[0]==y,'big integer witness')
        rows.append({'source_bit_length':p,'target_length':L,'statistics':st,'witness_count':len(hs)})
    for p in [80,256,1024]:
        S=(1<<p)+7;L=4;y,w,_=literal(S,L);A,M,B,Q=affine(w)
        hs,st=scan(y,24,Fraction(A,M),S)
        require(bool(hs),'nonvacuous big integer control')
        for h in hs:require(literal(h.source,h.length)[0]==y,'big additive witness')
        rows.append({'large_nonvacuous_source_bits':p+1,'target_length':L,'statistics':st,'witness_count':len(hs)})
    return rows

def tamper():
    c=search(703,80);bad=[]
    def mutation(name,fn):
        b=copy.deepcopy(c);fn(b);bad.append((name,b))
    mutation('schema version',lambda b:b.__setitem__('schema_version',2))
    mutation('query scope',lambda b:b.__setitem__('query_scope','all_positive_orbits_excluded'))
    mutation('overclaim flag',lambda b:b.__setitem__('proves_collatz',True))
    mutation('source bound',lambda b:b.__setitem__('source_bound',704))
    mutation('depth',lambda b:b.__setitem__('depth',9))
    mutation('float source bound',lambda b:b.__setitem__('source_bound',705.0))
    mutation('float depth',lambda b:b.__setitem__('depth',10.0))
    mutation('missing leaf',lambda b:b['leaves'].pop())
    mutation('duplicate leaf',lambda b:b['leaves'].append(copy.deepcopy(b['leaves'][0])))
    mutation('missing trace',lambda b:b['traces'].pop())
    mutation('duplicate trace',lambda b:b['traces'].append(copy.deepcopy(b['traces'][0])))
    mutation('frontier source',lambda b:next(x for x in b['leaves']if x['kind']=='frontier').__setitem__('source',0))
    mutation('false empty',lambda b:next(x for x in b['leaves']if x['kind']=='frontier').__setitem__('kind','empty'))
    mutation('false crossing',lambda b:next(x for x in b['leaves']if x['kind']=='frontier').__setitem__('kind','coefficient_crossing'))
    mutation('unknown leaf',lambda b:b['leaves'][0].__setitem__('kind','unproved'))
    mutation('trace root',lambda b:b['traces'][0].__setitem__('source',0))
    mutation('trace parity',lambda b:b['traces'][0].__setitem__('word','0'+b['traces'][0]['word'][1:]))
    mutation('unknown cut',lambda b:b['traces'][0].__setitem__('cut','timeout'))
    mutation('unknown result',lambda b:b.__setitem__('status','UNKNOWN'))
    mutation('source bool',lambda b:b.__setitem__('source',True))
    mutation('target invalid',lambda b:b.__setitem__('target_word','2'))
    rejected=[]
    for name,b in bad:
        try:check(b)
        except (ValueError,KeyError,TypeError):rejected.append(name)
        else:raise RuntimeError('tamper accepted: '+name)
    Bsrc=16;N=5;leaves=[];traces=[]
    def blind(v):
        A,M,B=position_map(v);r=(-B*pow(A,-1,M))%M if M>1 else 0;z=r or M
        if z>Bsrc:leaves.append({'word':v,'kind':'empty'});return
        if A<M:leaves.append({'word':v,'kind':'coefficient_crossing'});return
        if len(v)==N:
            leaves.append({'word':v,'kind':'frontier','source':z});x=z;a=m=1;vv=''
            while a>=m:
                bit=x&1;vv+=str(bit);m*=2
                if bit:a*=3;x=(3*x+1)//2
                else:x//=2
            traces.append({'source':z,'word':vv,'cut':'coefficient_crossing'});return
        blind(v+'0');blind(v+'1')
    blind('')
    fake={'schema_version':1,'query_scope':'all_positive_sources_all_lengths_lex','proves_collatz':False,'status':'NO_LEX_IMPROVEMENT','source':17,'target_word':'','source_bound':16,'depth':5,'leaves':leaves,'traces':traces,'diagnostics':{}}
    try:check(fake)
    except ValueError as e:
        require('short-prefix' in str(e),'wrong blind-cover rejection');rejected.append('short hit before crossing leaf')
    else:raise RuntimeError('blind cover accepted')
    unknown=search(703,80,limit=1)
    require(unknown['status']=='UNKNOWN','budget status')
    try:check(unknown)
    except ValueError:rejected.append('actual budget exhaustion')
    else:raise RuntimeError('budget accepted')
    return rejected

def write_json(name,data):
    (OUT/('safe_root_frontier_'+name+'.json')).write_text(json.dumps(data,sort_keys=True,indent=2)+'\n')

def main():
    global OUT
    parser=argparse.ArgumentParser()
    parser.add_argument('--artifact-dir',type=Path,default=OUT)
    args=parser.parse_args();OUT=args.artifact_dir
    OUT.mkdir(parents=True,exist_ok=True)
    t=time.time();result={}
    for name,fn in [('extrema',extrema),('direct_oracles',direct_oracles),('all_length_certificates',all_length_certificates),('controls',controls),('tamper_rejections',tamper)]:
        result[name]=fn();print(name,'done',round(time.time()-t,3),flush=True)
    result['proves_collatz']=False
    result['schema']='safe-root-frontier-evidence-v1'
    result['scope']={'all_length_certificates':'all positive literal sources, all lengths and Q, lexicographic coefficient then smaller source',
        'fixed_Q_complete_all_Q':False,'initial_frontier_bound_is_trace_time_bound':False,
        'general_termination_proved':False,'global_ancestor_existence_proved':False,
        'B2_B6_accepted':False,'EXT08_used':False}
    write_json('evidence',result)
    write_json('regressions',regressions())
    print('Wrote evidence, certificates and regressions; proves_collatz=false')

def regressions():
    from src.safe_ancestor_window import safe
    import itertools
    words=set(['11101','1100'])
    words.update(''.join(parts) for n in range(1,5) for parts in itertools.product(['110','111'],repeat=n))
    words.update('11101'*r+'1100'*s for r in range(5) for s in range(5) if r+s)
    words.update(literal(2**m-1,m+3)[1] for m in range(3,13))
    words.update(literal(8**m-5,3*m+3)[1] for m in range(1,9))
    rows=[]
    for w in sorted(words,key=lambda w:(len(w),w)):
        A,M,B,q=affine(w);z=(-B*pow(A,-1,M))%M or M
        y,actual,_=literal(z,len(w));require(actual==w,'family residue')
        if safe(w) and q:
            bd=bounds(q,len(w));require(bd[1]<=B<=bd[2] and decode(q,len(w),B)==w,'family window')
        rows.append({'word':w,'source':z,'endpoint':y,'q':q,'B':B,'safe':safe(w)})
    return {'schema':'safe-root-frontier-regressions-v1','proves_collatz':False,'finite_only':True,
        'family_rows':rows,'short_hit_obstruction':{'target_source':17,'target_word':'','ancestor_source':11,'ancestor_word':'1','first_crossing_word':'11010'},
        'minimal_empty_target_obstruction':minimal_blind_obstruction(),
        'same_source_valley_failure':{'source':6,'word':'011','endpoint':8,'valley_source':3,'safe_suffix':'11'}}

def minimal_blind_obstruction():
    from src.safe_ancestor_window import safe
    for S in range(1,18):
        N=(S-1).bit_length();early=[];surviving=[]
        for z in range(1,S):
            x=z;a=m=1;w=''
            while a>=m:
                if x==S and (a>m or z<S):
                    early.append((z,w))
                    if safe(literal(z,N)[1]):surviving.append((z,w))
                bit=x%2;w+=str(bit);m*=2
                if bit:x=(3*x+1)//2;a*=3
                else:x//=2
        if early and not surviving:
            z,w=early[0];cross='';x=z
            while safe(cross):
                bit=x%2;cross+=str(bit);x=(3*x+1)//2 if bit else x//2
            return {'source':S,'ancestor_source':z,'ancestor_word':w,'depth':N,
                'crossing_word':cross,'minimality_domain':'positive empty targets ordered by source'}
    raise RuntimeError('no short-hit obstruction in declared range')

if __name__=='__main__':main()
