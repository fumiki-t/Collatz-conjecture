"""Independent finite-potential checker and closed-graph reference.

No barrier search, stopping cutoff, potential solver, or generator is imported.
Only proof fields are certified; search diagnostics are not mathematical input.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
import json
from math import gcd, isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INHERITED = {
    "artifacts/phase33_descent_certificate.csv": "33ca0323c9c9c69d375e0e3da8e6d7746260f045dff5ed898f87dfe7d2ae4c58",
    "artifacts/phase33_descent_summary.json": "62e08d955ff1685f384373588d19e43f8ece7410cffee152cbc22a3af899129c",
    "artifacts/phase33_verifier.json": "415730783bb59633e95bd90bde566d6a1876fe09bae312f993dc700eaf8dafdd",
    "artifacts/phase38_capacity_certificate.json": "7020f8e8b9b0157ec0881825b9063838a597ae3dcba9040ba7fff6c2e3ba29ec",
    "artifacts/phase38_verifier.json": "4b790d15098e8d938184b13c78800475c3c56b84db9ada79331a2744b3a0a4bb",
}


class VerificationError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise VerificationError(message)


def integer(x, minimum=0):
    need(type(x) is int and x >= minimum, "invalid integer")
    return x


def same(a,b):
    # Unlike Python equality, distinguish 1, 1.0 and True in evidence fields.
    need(json.dumps(a,sort_keys=True) == json.dumps(b,sort_keys=True), "reconstruction mismatch")


def advance(x):
    return x//2 + (x+1 if x % 2 else 0)


def literal(source, length):
    integer(source, 1)
    integer(length)
    x, positions, states = source, [], [source]
    for k in range(length):
        if x % 2:
            positions.append(k)
        x = advance(x)
        states.append(x)
    q = len(positions)
    B = sum((1 << k)*3**(q-j-1) for j,k in enumerate(positions))
    need(3**q*source+B == (1 << length)*x, "affine identity")
    c = Fraction(3**q, 1 << length)
    H = Fraction(source)+Fraction(B,3**q)
    bound = -(-H.numerator//H.denominator)-1
    return x,q,c,H,bound,states


def check(record):
    need(type(record) is dict, "record must be an object")
    need(record.get("schema") == "collatz-phase43-normalization-barrier-v1", "schema")
    need(record.get("proves_collatz") is False, "overclaim")
    y,q,c,H,bound,_ = literal(record["source"],record["length"])
    same([record["endpoint"],record["odd_count"],record["source_bound"]],[y,q,bound])
    status = record["status"]
    if status == "IMPROVEMENT":
        w = record["witness"]
        endpoint,weight,slope,_,_,_ = literal(w["source"],w["length"])
        same(w["odd_count"], weight)
        need(endpoint == y and slope > c, "not a strict literal improvement")
        return
    need(status == "CERTIFIED_NO_STRICT_IMPROVEMENT", "UNKNOWN is not a certificate")
    rows = record["potential"]
    need(type(rows) is list, "potential rows")
    f, previous = {}, 0
    for row in rows:
        need(type(row) is list and len(row) == 3, "potential row")
        x,n,d = (integer(row[0],1),integer(row[1]),integer(row[2],1))
        need(x > previous and gcd(n,d) == 1, "canonical sorted rational rows")
        previous = x
        f[x] = Fraction(n,d)
    value = lambda x: f.get(x,Fraction(y,x))
    need(value(y) == 1, "endpoint potential")
    for x,r in f.items():
        need(r <= Fraction(y,x), "missing upper envelope")
        need(2*r >= (3 if x % 2 else 1)*value(advance(x)), "one-step inequality")
    # Every z<H must be explicitly listed: its default y/z exceeds c.
    need(bound <= len(f), "candidate coverage")
    for z in range(1,bound+1):
        need(value(z) <= c, "candidate cap")
    # All other positive sources satisfy y/z<=c. Outside-W edges follow
    # globally from the checked envelope and T(x)>=a(x)x (P258 proof).


def verify(record):
    try:
        check(record)
        return True
    except (KeyError, TypeError, ValueError, ZeroDivisionError, OverflowError):
        return False


def reference(data, maximum_seed):
    same(data["proves_collatz"],False)
    same(data["maximum_seed"],maximum_seed)
    vertices = data["vertices"]
    need(type(vertices) is list, "reference vertices")
    for x in vertices:
        integer(x,1)
    same(vertices, sorted(set(vertices)))
    V = set(vertices)
    need(set(range(1,maximum_seed+1)) <= V, "missing reference seed")
    need(all(advance(x) in V for x in V), "reference not forward closed")
    reached, cycles = set(), set()
    for seed in range(1,maximum_seed+1):
        trail, positions, x = [], {}, seed
        while x not in positions and x not in reached:
            positions[x] = len(trail)
            trail.append(x)
            x = advance(x)
        if x in positions:
            cyc = trail[positions[x]:]
            q = sum(v % 2 for v in cyc)
            need(3**q < 2**len(cyc), "positive cycle must contract")
            cycles.add(tuple(sorted(cyc)))
        reached.update(trail)
    same(sorted(reached), vertices)
    incoming = {x:[] for x in V}
    for x in V:
        incoming[advance(x)].append(x)
    return incoming, sorted(cycles)


def first_hit_coefficients(endpoint, incoming):
    # Reverse graph traversal gives the unique FIRST-hit path to endpoint.
    # Contracting cycle revisits cannot increase that coefficient.
    if endpoint not in incoming:
        return {}
    coeff, queue = {endpoint: Fraction(1)}, deque([endpoint])
    while queue:
        v = queue.popleft()
        for z in incoming[v]:
            if z not in coeff:
                coeff[z] = Fraction(3 if z % 2 else 1,2)*coeff[v]
                queue.append(z)
    return coeff


def capacity_check(data):
    same(data["proves_collatz"],False)
    A,O,pascal = [1],[1],[1]
    for N in range(1,49):
        old = pascal
        pascal = [1]+[old[s-1]+old[s] for s in range(1,N)]+[1]
        a=o=0
        for s in range(N+1):
            size=1+(3**s*((1 << N)-1)+((1 << (N-s))-1)*(3**s-(1 << s)))//(1 << N)
            m=(size-1).bit_length()
            a+=min(pascal[s],A[m]) if m<N else pascal[s]
            if s:
                o+=min(old[s-1],A[m]) if m<N else old[s-1]
        A.append(a)
        O.append(o)
    same(data["rows"],[[n,A[n],O[n]] for n in range(49)])
    U=Fraction(2079,1000)+sum((Fraction(O[n],2**n) for n in range(19,49)),Fraction())
    pair=lambda x:[x.numerator,x.denominator]
    l2=Fraction(2,3)+Fraction(2,81)+Fraction(2,1215)
    # t=(13/8-1)/(13/8+1)=5/21 in the positive atanh series.
    l138=2*(Fraction(13,8)-1)/(Fraction(13,8)+1)
    lower=9*l2+3*l138
    same(data["reciprocal_upper"],pair(U))
    same(data["coarse_upper"],[751,100])
    same(data["log2_lower"],pair(l2))
    same(data["log13_over8_lower"],pair(l138))
    same(data["three_log13_lower"],pair(lower))
    need(U < Fraction(751,100) < lower, "13S comparison")
    same(data["inherited_sha256"],INHERITED)
    for name,digest in INHERITED.items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, "inherited input changed")
    same(data["inherited_scope"],"E46 convergence below 583561 and E54 shell-49 tail are reused, not rerun")
    return 49


def word_check(row):
    w,z = row["word"],row["source"]
    need(type(w) is str and set(w) <= {"0","1"}, "word")
    need(type(z) is int and z != 0, "literal source")
    positions=[k for k,b in enumerate(w) if b == "1"]
    q=len(positions)
    B=sum(2**k*3**(q-j-1) for j,k in enumerate(positions))
    x,states=z,[z]
    for b in w:
        need(x % 2 == int(b), "literal parity")
        x=advance(x)
        states.append(x)
    same(row,dict(word=w,source=z,endpoint=x,q=q,B=B,states=states))


def regression_check(data):
    same(data["proves_collatz"],False)
    rows, controls = data["families"],data["controls"]
    for row in rows+list(controls.values()):
        word_check(row)
    # Exact fixed family coverage, including empty r or s separately.
    from itertools import product
    expected={"".join(bs) for k in range(1,5) for bs in product(("110","111"),repeat=k)}
    expected.update("11101"*r+"1100"*s for r in range(4) for s in range(4) if r+s)
    prefix=rows[:len(expected)]
    same([r["word"] for r in prefix],sorted(expected))
    for r in prefix:
        need(0 < r["source"] <= 2**len(r["word"]), "canonical representative")
    same([r["source"] for r in rows[len(expected):]], [z for m in range(1,9) for z in (2**m-1,8**m-5)])
    need(all(len(r["word"]) == 20 for r in rows[len(expected):]),"family prefix length")
    pairs={"NG24":(15,7),"NG25_lower":(287,273),"NG25_higher":(59,39),
           "NG26":(1874247,937121),"NG28":(310028220411,155014110207),
           "q22":(29023002619,14511501311),"NG43":(358030447,179015223)}
    expected_keys={k+s for k in pairs for s in ("_d","_a")}
    expected_keys.update(("source167","source7","positive_cycle","negative1","negative5","negative17","NG22_formal","NG45_formal"))
    same(sorted(controls),sorted(expected_keys))
    safe=lambda w:all(3**w[:k].count("1") >= 2**k for k in range(1,len(w)+1))
    for k,(d,a) in pairs.items():
        dr,ar=controls[k+"_d"],controls[k+"_a"]
        same([dr["source"],ar["source"]],[d,a])
        need(dr["endpoint"] == ar["endpoint"],"coalescent regression")
        cd=Fraction(3**dr["q"],2**len(dr["word"]))
        ca=Fraction(3**ar["q"],2**len(ar["word"]))
        need(ca>cd,"coefficient gain regression")
        if k in ("NG28","q22"):
            need(dr["q"] == ar["q"] and d == 2*a-3,"signed carry")
        if k in ("NG26","NG43"):
            need(safe(dr["word"]) and not safe(ar["word"]),"unsafe competitor retained")
    same([controls["source167"]["source"],controls["source7"]["source"]],[167,7])
    same(controls["source7"]["endpoint"],1)
    need(safe(controls["source167"]["word"]),"167 finite safety")
    for key,z in (("positive_cycle",1),("negative1",-1),("negative5",-5),("negative17",-17)):
        same([controls[key]["source"],controls[key]["endpoint"]],[z,z])
    # Independent closed square-index formula, not the model recurrence.
    defects=[0]+[isqrt(j)-int(j == isqrt(j)**2 and
                  (3**j).bit_length()-(3**(j-1)).bit_length() == 1)
                 for j in range(1,129)]
    E=[(3**j).bit_length()-1-defects[j] for j in range(129)]
    positions=set(E[:-1])
    u="".join("1" if k in positions else "0" for k in range(E[-1]))
    same(controls["NG22_formal"]["word"],u)
    same(controls["NG45_formal"]["word"],"110111111"+u)
    same(data["formal_scope"],"finite canonical residues; P255 excludes these particular infinite ordinary sources; no general language exclusion")
    weights=set()
    for v in range(1 << 13):
        w="0"+format(v,"013b")
        D=sum(2**k*3**w[k+1:].count("1") for k,b in enumerate(w) if b == "0")
        if D==24573:
            weights.add(w.count("1"))
    same(data["weight_hole_control"],[14,24573,sorted(weights)])
    _,_,_,_,_,states=literal(703,80)
    q=0
    odd=[]
    for k,x in enumerate(states):
        if x % 2:
            odd.append([q,x,k,(3**q).bit_length()-1-k])
        if k:
            need(3**q>2**k,"703 full coefficient safety")
        q+=x%2
    same(data["odd_703"],odd)
    same(odd[43:45],[[43,50165,62,6],[44,4703,67,2]])
    return len(rows),len(controls)


def audit(directory):
    read=lambda name:json.loads((directory/f"phase43_{name}.json").read_text())
    queries=read("queries")
    same(queries["proves_collatz"],False)
    records=queries["records"]
    cases=[(s,L) for s in range(1,128) for L in range(21)]+[(703,80)]
    same([[r["source"],r["length"]] for r in records],[list(c) for c in cases])
    target=[literal(s,L) for s,L in cases]
    bound=max(r[4] for r in target)
    graph,cycles=reference(read("reference"),bound)
    cache={}
    counts=Counter()
    falsifiers=[]
    for record,(y,q,c,H,B,_) in zip(records,target):
        check(record)
        if y not in cache:
            cache[y]=first_hit_coefficients(y,graph)
        improving=[z for z in range(1,B+1) if cache[y].get(z,Fraction())>c]
        expected="IMPROVEMENT" if improving else "CERTIFIED_NO_STRICT_IMPROVEMENT"
        same(record["status"],expected)
        if improving:
            same(record["witness"]["source"],min(improving))
        counts[expected]+=1
        if expected == "CERTIFIED_NO_STRICT_IMPROVEMENT" and record["source"] % 2:
            states=literal(record["source"],record["length"])[-1]
            j,odd=0,[]
            for k,x in enumerate(states):
                if x % 2:
                    odd.append([j,x,k,(3**j).bit_length()-1-k])
                j+=x%2
            for a,b in zip(odd,odd[1:]):
                if a[3]>b[3]:
                    falsifiers.append([record["source"],record["length"],a,b])
                    break
    same(queries["monotonicity_falsifiers"],falsifiers)
    same(falsifiers[0],[7,4,[2,17,2,1],[3,13,4,0]])
    minimal=read("certificate_7")
    check(minimal)
    same(minimal,next(r for r in records if (r["source"],r["length"]) == (7,4)))
    big=read("certificate_703")
    same(big,records[-1])
    rows={x:Fraction(n,d) for x,n,d in big["potential"]}
    need(5024 in rows and 2512 not in rows,"open exit regression")
    families,controls=regression_check(read("regressions"))
    n=capacity_check(read("capacity"))
    return dict(valid=True,generator_imported=False,query_count=len(records),
                certified_no_improvement=counts["CERTIFIED_NO_STRICT_IMPROVEMENT"],
                improvements=counts["IMPROVEMENT"],reference_vertices=len(graph),
                reference_cycles=[list(c) for c in cycles],maximum_candidate_source=bound,
                certificate_703_vertices=len(rows),capacity_rows=n,
                finite_monotonicity_falsifiers=len(falsifiers),minimal_monotonicity_query=[7,4],
                family_rows=families,retained_controls=controls,
                inherited_E46_E54="hash-pinned reuse, not full rerun",
                diagnostics_scope="search work/cut counters are non-proof diagnostics",
                all_prefix_703_scope="all prefixes 0..80, all positive starts/lengths/Q via P261",
                proves_collatz=False)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir",type=Path)
    p.add_argument("--certificate",type=Path)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    try:
        if a.certificate:
            check(json.loads(a.certificate.read_text()))
            result=dict(valid=True,proves_collatz=False)
        elif a.artifact_dir:
            result=audit(a.artifact_dir)
        else:
            p.error("provide --certificate or --artifact-dir")
    except (KeyError,TypeError,ValueError,OverflowError) as e:
        result=dict(valid=False,error=str(e),proves_collatz=False)
    encoded=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if a.output:
        a.output.write_text(encoded)
    print(encoded,end="")
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
