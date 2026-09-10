#!/usr/bin/env python3
"""Implementation-separated checks for critical-safe-mass evidence.
This file never imports generate.py or repository code. The infinite result
still requires auditing the written proof; finite checks do not establish it.
"""
from __future__ import annotations
import argparse
import copy
from fractions import Fraction
from itertools import permutations
import json
import math
import hashlib
import sys
from pathlib import Path

class VerificationError(ValueError):
    pass

def need(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)

def keys(d: dict, expected: set[str], label: str) -> None:
    need(type(d) is dict and set(d) == expected, label+": keys")

def rat(d: dict) -> Fraction:
    keys(d, {"numerator", "denominator"}, "rational")
    need(type(d["numerator"]) is str and type(d["denominator"]) is str, "rational strings")
    p, q = int(d["numerator"]), int(d["denominator"])
    need(q > 0 and math.gcd(p,q)==1 and str(p)==d["numerator"] and str(q)==d["denominator"], "canonical rational")
    return Fraction(p,q)

def no_duplicates(pairs: list[tuple]) -> dict:
    out = {}
    for k,v in pairs:
        need(k not in out, "duplicate JSON key")
        out[k]=v
    return out

def cycle_recurrence(max_n: int) -> tuple[list[int], list[int]]:
    # b_n by Pascal rows; a_n by cycle-index recurrence (not safe-prefix DP).
    a, b, row = [1], [0], [1]
    for n in range(1, max_n+1):
        row = [1]+[row[k-1]+row[k] for k in range(1,n)]+[1]
        b.append(sum(row[k] for k in range(n+1) if (3**k) > (1<<n)))
        value = sum(b[k]*a[n-k] for k in range(1,n+1))
        need(value % n == 0, "cycle recurrence integrality")
        a.append(value//n)
    return a,b

def small_words_and_residues(max_n: int, a: list[int], b: list[int]) -> tuple[dict[int,set[int]], int]:
    residues: dict[int,set[int]] = {}
    inspected = 0
    for n in range(max_n+1):
        ac,bc=0,0
        rr=set()
        for mask in range(1<<n):
            inspected += 1
            q=mask.bit_count()
            bc += 3**q > (1<<n)
            safe=True
            prefix_ones=0
            for j in range(n):
                prefix_ones += (mask>>j)&1
                if 3**prefix_ones <= (1<<(j+1)):
                    safe=False
                    break
            if not safe:
                continue
            ac += 1
            if n<=16:
                positions=[j for j in range(n) if (mask>>j)&1]
                B=sum((1<<j)*3**(q-1-k) for k,j in enumerate(positions))
                r=0 if n==0 else (-B*pow(3**q,-1,1<<n)) % (1<<n)
                need(r not in rr, "distinct word cylinder")
                rr.add(r)
        need(ac==a[n] and bc==b[n], f"exhaustive words n={n}")
        if n<=16:
            residues[n]=rr
    return residues,inspected

def interval_specs() -> list[tuple[str,int,int,int]]:
    out=[("full_shell",n,2**n,2**n) for n in range(17)]
    for n in range(1,15):
        width=min(2**n,257+3*n)
        for start in (1,3*2**n+7,2**200+12345+37*n):
            out.append(("translated",n,start,width))
    return out

def integer_trace(n: int, length: int) -> tuple[bool,int]:
    # Independent direct control, no early return: reconstruct all prefix products.
    q=0
    ok=True
    first=-1
    for t in range(1,length+1):
        if n % 2:
            n=(3*n+1)//2
            q+=1
        else:
            n//=2
        if 3**q <= 2**t:
            ok=False
            if first<0:
                first=t
    return ok,first

def arithmetic_reference(a: list[int], b: list[int]) -> dict[str,Fraction]:
    u=Fraction(19317,10000)
    weight=Fraction(1)
    total=Fraction(0)
    for n in range(1,513):
        weight *= Fraction(10000,19317)
        total += weight*b[n]/n
    c2=Fraction(22*10**6*63**2,7*8*232839*26**2)
    need(3**63 < 2**100 and 2**1000 < 3**631, "theta enclosure")
    need(10**7000 > 19317**1000*631**631*369**369, "entropy lower bound")
    need(1933**100*63**63*37**37 > 10**500, "entropy upper bound")
    for n in range(1,513):
        need((24*a[n])**2*n**3*1000**(2*n) >= 1933**(2*n), "finite lower envelope")
        need(a[n]**2*n**3*10000**(2*n) < 446**2*19317**(2*n), "finite upper envelope")
    need(c2<16, "binomial Fourier constant")
    need(121<128, "square-root tail enclosure")
    total_upper=total+Fraction(4,11)
    need(total_upper < Fraction(219,100), "critical exponent sum")
    log3_lower=2*(Fraction(1,2)+Fraction(1,24)+Fraction(1,160))
    need(log3_lower==Fraction(263,240), "positive log terms")
    need(Fraction(219,100)<2*log3_lower, "exponential below 9")
    need(36*(Fraction(219,100)**2+3*Fraction(219,100)+1)<446, "coefficient envelope")
    return {"mu_lower":u,"mu_upper":Fraction(1933,1000),"safe_coefficient_lower":Fraction(1,24),
            "finite_sum_upper":total,"tail_upper":Fraction(4,11),
            "S_upper":total_upper,"binomial_constant_squared_upper":c2,
            "S_rational_bound":Fraction(219,100)}

def validate_data(d: dict, a: list[int], b: list[int], arithmetic: dict,
                  residues: dict[int,set[int]]) -> None:
    keys(d,{"schema","scope","counts","mass_certificate","interval_queries","controls"},"root")
    need(d["schema"]=="critical-safe-mass-v1", "schema")
    need(json.dumps(d["scope"],sort_keys=True)==json.dumps({"max_n":512,"word_enumeration_n":18,"labeled_bijection_n":6,
                        "proves_collatz":False,"permanent_source_existence_asserted":False,
                        "status":"VERIFIED_FINITE"},sort_keys=True),"scope")
    need(d["scope"]["proves_collatz"] is False and
         d["scope"]["permanent_source_existence_asserted"] is False,"false flags")
    need(type(d["counts"]) is list and len(d["counts"])==513,"count domain")
    for n,item in enumerate(d["counts"]):
        keys(item,{"n","a","b"},"row")
        need(type(item["n"]) is int and item["n"]==n,"row index")
        need(type(item["a"]) is str and item["a"]==str(a[n]),"a row")
        need(type(item["b"]) is str and item["b"]==str(b[n]),"b row")
    m=d["mass_certificate"]
    keys(m,set(arithmetic)|{"safe_coefficient_constant","critical_mass_upper","exact_checks"},"mass")
    for k,value in arithmetic.items():
        need(rat(m[k])==value,k)
    need(type(m["safe_coefficient_constant"]) is int and m["safe_coefficient_constant"]==446,"constant")
    need(type(m["critical_mass_upper"]) is int and m["critical_mass_upper"]==9,"mass constant")
    names={"theta_above_63_over_100","theta_below_631_over_1000","mu_lower_exact",
           "mu_upper_exact","coefficient_lower_table","coefficient_upper_table",
           "binomial_constant_squared_below_16","tail_8_over_sqrt_512_below_4_over_11",
           "S_upper_below_219_over_100","219_over_100_below_twice_log3_lower",
           "coefficient_constant_below_446"}
    keys(m["exact_checks"],names,"checks")
    need(all(m["exact_checks"][x] is True for x in names),"exact check flags")
    need(type(d["interval_queries"]) is list and len(d["interval_queries"])==59,"interval domain")
    for item,(kind,n,start,width) in zip(d["interval_queries"],interval_specs()):
        keys(item,{"kind","n","start","width","safe_through_n","word_capacity"},"interval")
        need(item["kind"]==kind and type(item["n"]) is int and item["n"]==n,"interval identity")
        need(item["start"]==str(start) and type(item["width"]) is int and item["width"]==width,"interval range")
        # Modular membership from positional affine sums, no trace of these sources.
        period=1<<n
        count=sum(1 for r in residues[n] if start+((r-start)%period)<start+width)
        need(type(item["safe_through_n"]) is int and item["safe_through_n"]==count,"interval count")
        need(type(item["word_capacity"]) is int and item["word_capacity"]==a[n] and count<=a[n],"interval capacity")
        if kind=="full_shell":
            need(count==a[n],"nonvacuous full-shell equality")
    controls=d["controls"]
    keys(controls,{"one_is_not_permanent_safe","seven_first_failed_prefix","all_one_sources"},"controls")
    need(controls["one_is_not_permanent_safe"] is True and integer_trace(1,2)[1]==2,"cycle control")
    need(type(controls["seven_first_failed_prefix"]) is int and controls["seven_first_failed_prefix"]==integer_trace(7,19)[1],"seven control")
    need(controls["all_one_sources"]==[str(2**n-1) for n in range(1,33)],"all-one source list")
    for n in range(1,33):
        need(integer_trace(2**n-1,n)[0],"finite all-one trace")

# Explicit finite test of the cycle/convex-minorant bijection, with labeled
# infinitesimal perturbations realized by exact integers at this finite scale.
def cycles(p: tuple[int,...]) -> list[list[int]]:
    seen=set(); out=[]
    for i in range(len(p)):
        if i in seen:
            continue
        c=[];j=i
        while j not in seen:
            seen.add(j);c.append(j);j=p[j]
        need(j==i,"permutation cycle closure")
        out.append(c)
    return out

def cycles_to_positive(p: tuple[int,...], weights: list[int]) -> tuple[int,...]:
    blocks=[]
    for c in cycles(p):
        k=len(c); total=sum(weights[j] for j in c)
        need(total>0,"positive cycle expected")
        centered=[0];acc=0
        for j,label in enumerate(c[:-1],1):
            acc+=weights[label]
            centered.append(k*acc-j*total)
        need(len(set(centered))==k,"generic centered minimum")
        m=min(range(k),key=centered.__getitem__)
        cc=c[m:]+c[:m]
        blocks.append((Fraction(total,k),cc))
    need(len({mean for mean,_ in blocks})==len(blocks),"generic cycle means")
    blocks.sort(key=lambda pair:pair[0])
    return tuple(label for _,block in blocks for label in block)

def inverse_convex_minorant(order: tuple[int,...], weights: list[int]) -> tuple[int,...]:
    sums=[0]
    for label in order:
        sums.append(sums[-1]+weights[label])
    need(all(x>0 for x in sums[1:]),"strict positive linear path")
    hull=[]
    for t in range(len(sums)):
        while len(hull)>=2:
            i,j=hull[-2:]
            if (sums[j]-sums[i])*(t-j) >= (sums[t]-sums[j])*(j-i):
                hull.pop()
            else:
                break
        hull.append(t)
    p=[-1]*len(order)
    for i,j in zip(hull,hull[1:]):
        block=order[i:j]
        for left,right in zip(block,block[1:]+block[:1]):
            p[left]=right
    return tuple(p)

def check_bijection(a: list[int], max_n: int=6) -> dict:
    checked=0;positive=0;rows=[]
    for n in range(1,max_n+1):
        for m in range(1,n+1):
            for q in range(m+1):
                need((317*q>200*m)==(3**q>2**m),"finite rational slope sign")
        base=2*n*n+1
        perturb=[base**i for i in range(n)]
        large=(n+1)*sum(perturb)+1
        npositive=0
        for mask in range(1<<n):
            weights=[large*(317*((mask>>i)&1)-200)+perturb[i] for i in range(n)]
            check_generic(weights,mask)
            images=set()
            good_linear=0
            for p in permutations(range(n)):
                checked+=1
                ss=0;pos=True
                for label in p:
                    ss+=weights[label]
                    pos &= ss>0
                good_linear+=pos
                if any(sum(weights[i] for i in c)<=0 for c in cycles(p)):
                    continue
                order=cycles_to_positive(p,weights)
                need(order not in images,"cycle map injectivity")
                images.add(order)
                need(inverse_convex_minorant(order,weights)==p,"inverse convex map")
                npositive+=1
            need(len(images)==good_linear,"cycle map surjectivity")
        need(npositive==math.factorial(n)*a[n],"aggregate cycle identity")
        positive+=npositive
        rows.append({"n":n,"positive_labeled_cycles":npositive})
    return {"labeled_permutation_color_pairs":checked,"positive_pairs":positive,"rows":rows}

def check_generic(weights, coloring):
    n=len(weights); subsets={}
    for mask in range(1,2**n):
        total=sum(weights[i] for i in range(n) if mask>>i&1)
        size=mask.bit_count(); ones=(mask&coloring).bit_count()
        need((total>0)==(3**ones>2**size),'perturbation changed subset sign')
        need(total!=0,'zero subset sum')
        subsets[mask]=(total,size)
    for left,(x,a) in subsets.items():
        for right,(y,b) in subsets.items():
            if left<right and not left&right:
                need(x*b!=y*a,'disjoint subset averages tied')

def tamper_checks(d: dict, a: list[int], b: list[int], ar: dict, rr: dict) -> int:
    variants=[]
    def change(fn):
        x=copy.deepcopy(d);fn(x);variants.append(x)
    change(lambda x:x["scope"].__setitem__("proves_collatz",True))
    change(lambda x:x["scope"].__setitem__("permanent_source_existence_asserted",True))
    change(lambda x:x["scope"].__setitem__("max_n",511))
    change(lambda x:x["scope"].__setitem__("status","VERIFIED_THEOREM"))
    change(lambda x:x["counts"][22].__setitem__("a",str(int(x["counts"][22]["a"])+1)))
    change(lambda x:x["counts"][31].__setitem__("b","0"))
    change(lambda x:x["counts"].pop())
    change(lambda x:x["mass_certificate"]["mu_lower"].__setitem__("numerator","19318"))
    change(lambda x:x["mass_certificate"]["mu_upper"].__setitem__("numerator","1932"))
    change(lambda x:x["mass_certificate"]["safe_coefficient_lower"].__setitem__("denominator","23"))
    change(lambda x:x["mass_certificate"]["finite_sum_upper"].__setitem__("numerator","0"))
    change(lambda x:x["mass_certificate"]["tail_upper"].__setitem__("denominator","12"))
    change(lambda x:x["mass_certificate"].__setitem__("critical_mass_upper",8))
    change(lambda x:x["mass_certificate"].__setitem__("safe_coefficient_constant",445))
    change(lambda x:x["mass_certificate"]["exact_checks"].__setitem__("mu_lower_exact",False))
    change(lambda x:x["interval_queries"][10].__setitem__("safe_through_n",0))
    change(lambda x:x["interval_queries"].pop())
    change(lambda x:x["interval_queries"][20].__setitem__("width",100000000))
    change(lambda x:x["controls"].__setitem__("one_is_not_permanent_safe",False))
    change(lambda x:x["controls"].__setitem__("seven_first_failed_prefix",4))
    change(lambda x:x.__setitem__("future_orbits_proved_finite",True))
    for j,x in enumerate(variants):
        try:
            validate_data(x,a,b,ar,rr)
        except (VerificationError,TypeError,ValueError):
            continue
        raise VerificationError(f"tamper {j} accepted")
    try:
        json.loads('{"x":1,"x":2}',object_pairs_hook=no_duplicates)
    except VerificationError:
        pass
    else:
        raise VerificationError("duplicate JSON accepted")
    return len(variants)+1

def scope_reference():
    return {
        'schema':'critical-safe-mass-scope-v1','status':'VERIFIED_FINITE','proves_collatz':False,
        'base_commit':'df6c063b7428b768b4ea071dd7cea1a5a218220c',
        'zip_sha256':'18a55d177dea20c2cf5ea97ffb702e705ddc5e373af556895205f7b6568c861c',
        'U':'all nonempty prefixes coefficient > 1; U_0=1',
        'V':'terminal coefficient > 1 only; V_0=0',
        'rho':'H_2(log(2)/log(3))','mu':'2^rho',
        'mass_domain':'permanent positive sources and the distance-dependent finite filter C_b',
        'count_domain':'permanent positive sources only; not arbitrary finite filters or all orbit values',
        'renewal_index':'i, not every odd index q','EXT08_used':False,
        'mass_implies_emptiness':False,'P80_address_multiplicity_counted':False,
        'permanent_source_existence_asserted':False,'finite_check_proves_infinite_theorem':False,
        'orbit_bits_assumed_random':False,'unperturbed_means_assumed_distinct':False,
        'general_identity_novelty_claimed':False,'H112_status':'OPEN','H72_status':'OPEN',
        'Y_limit_bound_from_P270':'Y_infinity <= 256 S_0, not strict by passage to limit'
    }

def same(data,expected):
    need(json.dumps(data,sort_keys=True)==json.dumps(expected,sort_keys=True),'exact reconstruction differs')

def regression_reference(residues):
    root=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root))
    from verifier.verify_transient_sparsity import reconstruct_regressions
    from verifier.verify_phase41 import formal_expected
    old=reconstruct_regressions()
    words=[]
    for w,B,r,endpoint in old['words']:
        q=0; safe=True
        for length,bit in enumerate(w,1):
            q+=int(bit); safe &= 3**q>2**length
        words.append([w,r,safe])
    paths=[[row[0],row[1],integer_trace(int(row[0]),row[1])[0]] for row in old['paths']]
    filters=[]
    for b in (0,1,2,7,2**200):
        for n in range(11):
            modulus=2**n; lo=b+modulus
            points=[lo+(r-lo)%modulus for r in residues[n]]
            filters.append([str(b),n,len(points),str(min(points)),str(max(points))])
    historical={**old['historical_sha256'],
        'phase41_formal.json':'aa7f6c5feb4ff7970d9c8d275f410fa9e89db68e274f13cb0711ca2db20165be',
        'ext08_scope_impact.json':'25678454f558515adba6683df3bcd4d2daf5f36bbcbd632f17e6326e6d3f0007',
        'transient_sparsity_evidence.json':'72089367cc5a903b9b7a843d44663fb3c7e7b7ab630850e96ea611f828652319'}
    for name,sha in historical.items():
        need(hashlib.sha256((root/'artifacts'/name).read_bytes()).hexdigest()==sha,'historical hash')
    same(json.loads((root/'artifacts/phase41_formal.json').read_text(),object_pairs_hook=no_duplicates),formal_expected())
    return {'schema':'critical-safe-mass-regressions-v1','status':'VERIFIED_FINITE','proves_collatz':False,
         'finite_only':True,'words':words,'paths':paths,'filters':filters,
         'historical_sha256':historical,'tied_mean_control':{'bits':'11','centered':[0,0]},
         'mass_only_countermodel':{'set':'{2^k:k>=1}','uniform_upper':3,'permanent_safe':False}}

def audit(directory):
    read=lambda name: json.loads((directory/('critical_safe_mass_'+name+'.json')).read_text(),object_pairs_hook=no_duplicates)
    data=read('evidence'); a,b=cycle_recurrence(512)
    residues,word_count=small_words_and_residues(18,a,b); ar=arithmetic_reference(a,b)
    validate_data(data,a,b,ar,residues)
    same(read('scope'),scope_reference()); reg=regression_reference(residues); same(read('regressions'),reg)
    bij=check_bijection(a); tamper=tamper_checks(data,a,b,ar,residues)
    return {'valid':True,'generator_imported':False,'status':'VERIFIED_FINITE','proves_collatz':False,
        'count_rows':513,'two_sided_envelope_rows':512,'exhaustive_words':word_count,
        'interval_queries':59,'interval_points':sum(x[3] for x in interval_specs()),
        'nonzero_interval_queries':sum(x['safe_through_n']>0 for x in data['interval_queries']),
        'finite_safe_occurrences':sum(x['safe_through_n'] for x in data['interval_queries']),
        'bijection':bij,'tamper_rejections':tamper,'finite_checks_are_not_an_infinite_proof':True,
        'filter_shells':len(reg['filters']),'regression_words':len(reg['words']),
        'historical_files_preserved':len(reg['historical_sha256']),'NG46_potentials_checked':2,
        'NG45_formal_evidence_rebuilt':True,'generic_subset_checks':True,
        'permanent_source_existence_asserted':False,'EXT08_used':False}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--artifact-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path); args=parser.parse_args()
    try: report=audit(args.artifact_dir)
    except (ValueError,KeyError,TypeError,OSError,ZeroDivisionError) as exc:
        print(json.dumps({'valid':False,'error':str(exc),'proves_collatz':False})); return 1
    if args.output: args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True)); return 0

if __name__=='__main__': sys.exit(main())
