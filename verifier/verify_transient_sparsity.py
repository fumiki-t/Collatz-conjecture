"""Separate reconstruction: no import of the proposal generator.
All-scale proofs are in research/audits/transient-sparsity/REPORT.md, not finite samples.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from fractions import Fraction as Rat
from pathlib import Path

HERE=Path(__file__).resolve().parent

def encode(v): return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def hashed(seq):
    h=hashlib.sha256()
    for row in seq: h.update(encode(row)+b'\n')
    return h.hexdigest()
def rr(x): return [str(x.numerator),str(x.denominator)]
def need(ok,why):
    if not ok: raise ValueError(why)
def nxt(x): return (x//2 if x%2==0 else x+(x+1)//2)

def make_trace(n):
    path=[]; places={}
    for _ in range(100000):
        if n in places:
            return path,places[n],len(path)-places[n]
        places[n]=len(path); path.append(n); n=nxt(n)
    raise ValueError('reference trace UNKNOWN')

def reconstruct_capacity():
    # Pascal coefficients and independently propagated affine extrema.
    a=[1]; odd=[1]; rowdata=[[0,1,1]]
    pascal=[1]; low=[0]; high=[0]
    for length in range(1,501):
        previous_pascal=pascal
        pascal=[1]+[pascal[j-1]+pascal[j] for j in range(1,len(pascal))]+[1]
        ll=[]; hh=[]
        for weight in range(length+1):
            lows=[]; highs=[]
            if weight<length:
                lows.append(low[weight]); highs.append(high[weight])
            if weight>0:
                lows.append(3*low[weight-1]+2**(length-1))
                highs.append(3*high[weight-1]+2**(length-1))
            ll.append(min(lows)); hh.append(max(highs))
        low,high=ll,hh
        source_sum=odd_sum=0
        for weight in range(length+1):
            numerator=3**weight*(2**length-1)+high[weight]-low[weight]
            slots=numerator//2**length+1
            exponent=(slots-1).bit_length()
            bound=pascal[weight]
            if exponent<length: bound=min(bound,a[exponent])
            source_sum+=bound
            if weight:
                bound=previous_pascal[weight-1]
                if exponent<length: bound=min(bound,a[exponent])
                odd_sum+=bound
        a.append(min(2**length,source_sum+length))
        odd.append(min(2**(length-1),odd_sum+length))
        rowdata.append([length,str(a[-1]),str(odd[-1])])
    geometric=Rat(1440)*Rat(44**501,45**501)
    def tail_from(k):
        z=geometric
        for n in range(500,k-1,-1): z+=Rat(odd[n],2**n)
        return z
    global_r=tail_from(5)
    for k in range(16): global_r+=Rat(1,2*k+1)
    return a,odd,{
        'Nmax':500,'rows':rowdata,'row_digest':hashed(rowdata),
        'tail':rr(geometric),'F19':rr(tail_from(19)),'F49':rr(tail_from(49)),
        'odd_reciprocal_global_upper':rr(global_r),
        'checks':{'F19_lt_15_over_2':tail_from(19)<Rat(15,2),
                  'F49_lt_2079_over_1000':tail_from(49)<Rat(2079,1000),
                  'global_lt_82_over_5':global_r<Rat(82,5)}
    }

def constants():
    a=Rat(2,3)+Rat(2,81)+Rat(2,1215)
    b=3*a+Rat(10,21)
    # Deliberately reformulate the power comparisons as rational comparisons.
    c={
        'alpha_theta':Rat(3**14,2**23)<1,
        'entropy':Rat(23**690,14**420*9**270)<2**667,
        'low_at_135':Rat(24**690,1)<=Rat(2**667,3**406)**135,
        'low_fails_134':Rat(24**690,1)>Rat(2**667,3**406)**134,
        'low_persists':Rat(3**406,2**667)<1,
        'recursive_size_at_57':4**23<Rat(2**23,3**14)**57,
        'boundary_loss_at_135':Rat(135,1)**30<Rat(2**29,1)**134,
        'boundary_loss_persists':Rat(136,135)**30<2**29,
        'base_power':2**134<32**30,
        'geometric_ratio':Rat(45,44)**30<2,
        'half_log_gap':Rat(2079,3000)<a,
        'factor_13':b>Rat(5,2),
        'factor_256':Rat(82,120)<a,
    }
    need(all(c.values()),'a symbolic constant comparison failed')
    return {'comparisons':c,'log2_lower':rr(a),'log13_lower':rr(b)}

def affine():
    all_rows=[]; ex=[]
    for length in range(15):
        indexed={}; mn=[None]*(length+1); mx=[None]*(length+1)
        for residue in range(2**length):
            x=residue if residue else 2**length
            initial=x; mask=weight=0
            for t in range(length):
                bit=x%2; mask+=bit*2**t; weight+=bit; x=nxt(x)
            B=2**length*x-3**weight*initial
            need(mask not in indexed,'parity collision in full residue enumeration')
            indexed[mask]=[length,mask,weight,B,residue]
            mn[weight]=B if mn[weight] is None else min(mn[weight],B)
            mx[weight]=B if mx[weight] is None else max(mx[weight],B)
        need(len(indexed)==2**length,'missing parity word')
        all_rows.extend(indexed[k] for k in sorted(indexed))
        for w in range(length+1): ex.append([length,w,mn[w],mx[w]])
    return {'word_scope':'all words, length 0..14','words':len(all_rows),
            'word_digest':hashed(all_rows),'extrema':ex}

def finite_prefix(a,odd):
    accumulated=[]; nonzero=0; max_deletion=0; largest=Rat(0)
    for source in [*range(1,128),703]:
        values,entry,period=make_trace(source)
        lengths={min(z,len(values)) for z in [1,2,3,4,8,16,len(values)]}
        if source==703 and len(values)>=80: lengths.add(80)
        for size in sorted(lengths):
            segment=values[:size]; ordered=sorted(segment)
            weight=sum(x%2 for x in segment)
            ratio=Rat(2**size*nxt(segment[-1]),source*3**weight)
            need(ratio<256,'finite distortion bound failed on a sample')
            largest=max(largest,ratio)
            for exponent in range(1,9):
                width=2**exponent
                anchors={1,source,max(1,ordered[-1]-width+1),ordered[len(ordered)//2],
                         max(1,ordered[0]-width//2)}
                for start in sorted(anchors):
                    selected=[(idx,x) for idx,x in enumerate(segment) if start<=x<start+width]
                    removed=[x for idx,x in selected if idx>=size-exponent]
                    nonzero+=bool(removed); max_deletion=max(max_deletion,len(removed))
                    need(len(removed)<=exponent,'more than N terminal points removed')
                    groups={}; used=set()
                    for index,point in selected:
                        if index>=size-exponent: continue
                        x=point; weight=0
                        for _ in range(exponent):
                            weight+=x%2; x=nxt(x)
                        need(x in segment and x not in used,'retained image not injective into segment')
                        used.add(x); groups.setdefault(weight,[]).append(x)
                    need(len(selected)<=a[exponent],'general capacity failed')
                    need(sum(x%2 for _,x in selected)<=odd[exponent],'odd capacity failed')
                    # Verify the images directly against the affine span, without source parity tables.
                    for w,ys in groups.items():
                        min_b=3**w-2**w; max_b=min_b*2**(exponent-w)
                        span=Rat(3**w*(width-1)+max_b-min_b,2**exponent)
                        need(max(ys)-min(ys)<=span,'image span failed')
                    accumulated.append([source,size,exponent,start,len(selected),len(used),
                                        [[w,sorted(points)] for w,points in sorted(groups.items())]])
    sharp=[]
    for m in [3,4,8,16,32,64,128,256,512,1024]:
        # Explicit trajectory: 2^m,2^(m-1),...,2,1, then 2 repeats.
        orbit=[2**j for j in range(m,-1,-1)]
        for N in sorted({1,2,min(8,m-1),m-1}):
            if N>m-1: continue
            images=set()
            for j in range(m+1):
                t=j+N
                value=(orbit[t] if t<=m else (2 if (t-(m-1))%2==0 else 1))
                images.add(value)
            loss=len(orbit)-len(images)
            need(loss==N,'sharp collision-loss control failed')
            sharp.append([m,N,len(orbit),len(images),loss])
    return {'source_scope':'1..127 and 703; specified prefix lengths and all listed translated windows',
            'source_count':128,'window_cases':len(accumulated),'window_digest':hashed(accumulated),
            'nonzero_terminal_deletions':nonzero,'max_terminal_deletions':max_deletion,
            'largest_finite_product':rr(largest),'sharp_loss_rows':sharp}

def rebuild():
    a,o,c=reconstruct_capacity()
    need(all(c['checks'].values()),'rational tail certificate failed')
    return {'schema':'transient-sparsity-v1','proves_collatz':False,
            'status':'VERIFIED_FINITE','capacity':c,'constants':constants(),
            'affine':affine(),'finite_prefix':finite_prefix(a,o)}

def verify_against(data, expected):
    need(type(data) is dict,'top level must be an object')
    need(type(data.get('proves_collatz')) is bool and data['proves_collatz'] is False,'overclaim flag')
    # Canonical byte comparison also rejects bool/int substitutions and extra/missing scope fields.
    need(encode(data)==encode(expected),'reconstruction differs from submitted evidence')
    return True

def duplicate_reject(pairs):
    d={}
    for k,v in pairs:
        need(k not in d,'duplicate JSON key')
        d[k]=v
    return d

def normalization(source, length):
    need(type(source) is int and source>0 and type(length) is int and length>=0,'path domain')
    x=source; inputs=[]; weight=0
    for _ in range(length):
        need(x not in inputs,'repeated input')
        inputs.append(x); weight+=x%2; x=nxt(x)
    ratio=Rat(x*2**length,source*3**weight)
    minimum=min(inputs,default=source)
    bound=256
    if minimum>=524288: bound=13
    if minimum>=562949953421312: bound=2
    need(ratio<bound,'normalization')
    return [str(source),length,str(x),weight,rr(ratio),str(minimum),bound]

def reconstruct_regressions():
    words={'11101','1100'}; level={''}
    for _ in range(4):
        level={w+suffix for w in level for suffix in ('110','111')}; words.update(level)
    for r in range(1,5):
        for s in range(1,5): words.add('11101'*r+'1100'*s)
    word_rows=[]
    for w in sorted(words):
        residue=0
        for i,bit in enumerate(w):
            point=residue
            for _ in range(i): point=nxt(point)
            if point%2!=int(bit): residue+=2**i
        source=residue or 2**len(w); point=source; weight=0
        for bit in w:
            need(point%2==int(bit),'literal family word'); weight+=point%2; point=nxt(point)
        B=point*2**len(w)-source*3**weight
        word_rows.append([w,str(B),str(residue),str(point)])
    seeds=set()
    for m in range(1,13): seeds.update((2**m-1,2**(3*m)-5))
    paths=[]
    for source in sorted(seeds):
        trace,_,_=make_trace(source); paths.append(normalization(source,min(64,len(trace))))
    paths.extend((normalization(1,0),normalization(1,2)))
    for m in (20,50,72): paths.append(normalization(2**m-1,m))
    ks=[]
    for row in paths:
        source=int(row[0]); Y=source*Rat(*map(int,row[4])); ceil=0
        while 2**ceil<source: ceil+=1
        need(2**(ceil+10)>=3*Y,'global K')
        k19=ceil+6 if int(row[5])>=source>=524288 else None
        if k19 is not None: need(2**k19>=3*Y,'non-dropping K')
        ks.append([row[0],row[1],ceil+10,k19])
    repeat=[]
    for length in range(41):
        endpoint=1 if length%2==0 else 2; odd_count=(length+1)//2
        ratio=Rat(2**length*endpoint,3**odd_count)
        repeat.append([length,str(endpoint),rr(ratio),ratio<256])
    need(all(row[3] for row in repeat[:39]) and not repeat[39][3],'minimal source-1 failure')
    historical={
        'phase43_certificate_7.json':'b7c821cc4070ba0442096530b17f1617949ac58044105444873b2dbe542581b5',
        'phase43_certificate_703.json':'0c475092e4a1e137cd22601c8519b735ee4eac8f25a032373bb438db820feae5',
        'phase38_capacity_certificate.json':'7020f8e8b9b0157ec0881825b9063838a597ae3dcba9040ba7fff6c2e3ba29ec'}
    root=HERE.parent
    for name,digest in historical.items():
        need(hashlib.sha256((root/'artifacts'/name).read_bytes()).hexdigest()==digest,'historical evidence changed')
    # Recheck the actual all-length potentials, not just hashes or status labels.
    sys.path.insert(0,str(root))
    from verifier.verify_phase43 import check
    for name in ('phase43_certificate_7.json','phase43_certificate_703.json'):
        check(json.loads((root/'artifacts'/name).read_text(),object_pairs_hook=duplicate_reject))
    need(nxt(-1)==-1,'negative fixed control')
    return {'schema':'transient-sparsity-regressions-v1','status':'VERIFIED_FINITE',
            'proves_collatz':False,'words':word_rows,'paths':paths,'K_rows':ks,
            'repeated_source_1':repeat,'first_failure_within_source_1':39,
            'historical_sha256':historical,'negative_fixed_control':[-1,-1,3,2]}

def reconstruct_scope():
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

def audit(artifact_dir):
    expected={'evidence':rebuild(),'scope':reconstruct_scope(),'regressions':reconstruct_regressions()}
    for name,obj in expected.items():
        data=json.loads((artifact_dir/('transient_sparsity_'+name+'.json')).read_text(),
                        object_pairs_hook=duplicate_reject)
        verify_against(data,obj)
    e=expected['evidence']; r=expected['regressions']
    return {'valid':True,'generator_imported':False,'status':'VERIFIED_FINITE','proves_collatz':False,
            'capacity_rows':len(e['capacity']['rows']),'affine_words':e['affine']['words'],
            'prefix_window_cases':e['finite_prefix']['window_cases'],
            'nonzero_terminal_deletions':e['finite_prefix']['nonzero_terminal_deletions'],
            'regression_words':len(r['words']),'normalization_paths':len(r['paths']),
            'NG46_potentials_verified':2,'historical_files_preserved':3,
            'raw_capacity_tail_claimed':False,'infinite_proofs_machine_formalized':False}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--artifact-dir',type=Path,required=True)
    p.add_argument('--output',type=Path); args=p.parse_args()
    try: out=audit(args.artifact_dir)
    except (ValueError,TypeError,KeyError,OSError,ZeroDivisionError) as exc:
        print(json.dumps({'valid':False,'error':str(exc),'proves_collatz':False})); return 1
    if args.output: args.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n')
    print(json.dumps(out,sort_keys=True)); return 0

if __name__=='__main__': sys.exit(main())
