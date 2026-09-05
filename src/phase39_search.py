#!/usr/bin/env python3
"""Exact bounded Phase 39 search; proofs and conditional scope are in REPORT.md."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from math import comb
from pathlib import Path


FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def envelope(kind: str, **values: object) -> dict:
    return {"format": f"collatz-phase39-{kind}-v1", "proves_collatz": False, **values}


def affine(word: str) -> tuple[int, int]:
    q = b = 0
    for j, bit in enumerate(word):
        if bit == "1":
            q += 1
            b = 3 * b + (1 << j)
        elif bit != "0":
            raise ValueError("binary word required")
    return q, b


def safe(word: str) -> bool:
    q = 0
    for j, bit in enumerate(word, 1):
        q += bit == "1"
        if 3**q <= 1 << j:
            return False
    return True


def source(word: str) -> int:
    q, b = affine(word)
    mod = 1 << len(word)
    return (-b * pow(3**q, -1, mod)) % mod or mod


def realize(n: int, word: str) -> int:
    for bit in word:
        assert n % 2 == int(bit)
        n = (3 * n + 1) // 2 if bit == "1" else n // 2
    return n


def words(limit: int, include_empty: bool = False) -> list[str]:
    return ([""] if include_empty else []) + ["".join(t) for n in range(1, limit + 1) for t in itertools.product("01", repeat=n)]


def carry_audit() -> dict:
    literals = [w for w in words(8) if safe(w)]
    relations = []
    for a in literals:
        qa, ba = affine(a)
        for d in literals:
            qd, bd = affine(d)
            k, s = len(d) - len(a), qd - qa
            if a == d or min(k, s) < 0:
                continue
            numerator = (1 << k) * ba - bd
            if numerator % 3**qa == 0:
                relations.append([a, d, k, s, str(numerator // 3**qa)])
    rows = []
    lifts = descents = macro = 0
    for p in words(6, include_empty=True):
        qp, bp = affine(p)
        for a, d, k, s, encoded_m in relations:
            m = int(encoded_m)
            n = source(p + d)
            state = realize(n, p)
            endpoint = realize(state, d)
            gamma = (1 << k) - 3**s
            old = gamma * bp + (1 << len(p)) * m
            current = gamma * state + m
            assert old == (1 << len(p)) * current - gamma * 3**qp * n
            lift = current % 3**qp == 0
            assert lift == (old % 3**qp == 0)
            ancestor = None
            if lift:
                lifts += 1
                candidate = Fraction(3**s * n - old // 3**qp, 1 << k)
                if candidate.denominator == 1 and candidate > 0:
                    ancestor = candidate.numerator
                    assert realize(ancestor, p + a) == endpoint
                    descents += ancestor < n and safe(p + a) and safe(p + d)
            if gamma >= 0:
                bound3 = (1 << k) * (3 * state + a.count("1") + d.count("1"))
                assert 3 * abs(current) <= bound3
                if lift and current:
                    assert 3**(qp + 1) <= bound3
                    macro += 1
            rows.append([p, a, d, str(n), str(state), str(old), str(current), lift, None if ancestor is None else str(ancestor)])
    universal = []
    for r in range(4, 33):
        a, d = "1" * (r - 1) + "01", "1" * r + "00"
        qa, ba = affine(a)
        qd, bd = affine(d)
        assert safe(a) and safe(d) and qa == qd == r
        assert 2 * ba - bd == 3**r
        n = source(d)
        x = (n - 1) // 2
        assert n == 2*x+1 and realize(n, d) == realize(x, a)
        universal.append([r, str(ba), str(bd), str(n), str(x), str(realize(n, d))])
    # A rational cutoff for |gamma| C (3/2)^Q + |m| < 3^Q.
    cutoffs = []
    for a, d, k, s, em in relations:
        gamma, m, Q = abs((1 << k) - 3**s), abs(int(em)), 0
        while 2 * gamma * 100 >= 1 << Q or 2*m >= 3**Q:
            Q += 1
        assert Fraction(gamma * 100, 1 << Q) + Fraction(m, 3**Q) < 1
        cutoffs.append([a, d, Q])
    return envelope("carry", maximum_word_length=8, maximum_prefix_length=6,
                    relations=relations, row_count=len(rows), lift_count=lifts,
                    safe_descent_count=descents, macro_bound_count=macro,
                    rows_sha256=digest(rows), selected_rows=rows[:3] + rows[-3:],
                    universal_rewrite_rows=universal, fixed_bound_constant=100,
                    fixed_relation_cutoffs=cutoffs)


def jump_dag() -> dict:
    paths = {"": 1}
    levels, vertices, checks, first_gain = [], [], [], {}
    unsafe_count = 0
    for ell in range(1, 13):
        groups = defaultdict(list)
        for tail, jump in paths.items():
            groups[jump].append(tail)
        levels.append([ell, len(paths), len(groups), sum(len(g)>1 for g in groups.values())])
        for jump, tails in sorted(groups.items()):
            tails.sort()
            assert jump % 2 == 1
            vertices.append([ell, str(jump), [[t, t.count("1")] for t in tails]])
        for R in range(1, 13):
            for v, jump in paths.items():
                w = "1" * R + "0" + v
                if not safe(w):
                    continue
                qw, bw = affine(w)
                assert bw + (1 << len(w)) - 3**qw == (1 << R) * jump
                for t in groups[jump]:
                    k = t.count("1") - v.count("1")
                    if not 1 <= k <= R - 1:
                        continue
                    alt = "1" * (R-k) + "0" + t
                    qa, ba = affine(alt)
                    alt_safe = safe(alt)
                    unsafe_count += not alt_safe
                    n = source(w)
                    x = (n+1) // (1 << k) - 1
                    assert (n+1) % (1 << k) == 0 and 0 < x < n
                    assert qa == qw and len(w) - len(alt) == k
                    assert realize(n, w) == realize(x, alt)
                    checks.append([ell, R, v, t, k, alt_safe, str(n), str(x)])
                    if alt_safe and str(k) not in first_gain:
                        first_gain[str(k)] = checks[-1]
        paths = {t+b: 3*j if b=="1" else j+(1 << ell) for t,j in paths.items() for b in "01"}
    return envelope("jump-dag", maximum_tail_length=12, tail_length_counts_initial_zero=True,
                    maximum_suffix_length=11, maximum_initial_run=12,
                    levels=levels, vertices=vertices, rewrite_count=len(checks),
                    unsafe_candidate_count=unsafe_count, maximum_gain=max(map(int, first_gain)),
                    first_safe_gain=first_gain, rewrite_rows_sha256=digest(checks),
                    ordering="ell, initial run, lexicographic original tail, lexicographic alternative tail",
                    safety_scope="Full word safety tested separately; no all-depth implication is inferred.")


def accelerated(n: int) -> tuple[int, int]:
    value, e = 3*n+1, 0
    while value % 2 == 0:
        value //= 2
        e += 1
    return value, e


def capacity_cycle() -> dict:
    binomial_rows = []
    for N in range(1, 501):
        count = sum(comb(N-1, s-1) for s in range(1, N+1) if 3**s > 1 << N)
        assert count**30 < 1 << (29*N)
        binomial_rows.append([N, str(count)])
    assert 3**14 < 2**23
    assert 23**690 < 2**667 * 14**420 * 9**270
    rows, integer_cycles, rational_examples = [], [], []
    for q in range(1, 6):
        for es in itertools.product(range(1, 5), repeat=q):
            word = "".join("1"+"0"*(e-1) for e in es)
            _, b = affine(word)
            start = Fraction(b, (1 << len(word)) - 3**q)
            if start <= 0:
                continue
            values = [start]
            for e in es:
                values.append((3*values[-1]+1)/(1 << e))
            assert values[-1] == start
            minimum = min(values[:-1])
            product = Fraction(1)
            directions = []
            for x, nxt, e in zip(values, values[1:], es):
                y, yn = (x+1)/2, (nxt+1)/2
                inc = Fraction((1 << (e-1))-1, 3*y)
                assert (1 << e)*yn == 3*y + (1 << (e-1))-1
                assert 0 <= inc < 1/minimum
                product *= 1+inc
                directions.append((yn>y)-(yn<y))
            assert product == Fraction(1 << len(word), 3**q)
            integral = all(x.denominator==1 and x.numerator%2 for x in values[:-1])
            row = [list(es), str(start), str(minimum), sum(e>=2 for e in es), str(product), integral, directions]
            rows.append(row)
            if integral:
                for e, sign, x in zip(es, directions, values):
                    assert sign==1 if e==1 else sign==-1 or (x==1 and e==2)
                integer_cycles.append(row)
            elif q==1:
                rational_examples.append(row)
    direct = []
    for n in range(1, 1025, 2):
        x = n
        for j in range(64):
            nxt, e = accelerated(x)
            assert nxt>x if e==1 else nxt<x or (x==1 and e==2)
            direct.append([n,j,str(x),e,str(nxt)])
            x = nxt
    endpoint_rows = []
    for word in words(12):
        q, _ = affine(word)
        if not q:
            continue
        n = source(word)
        end = realize(n, word)
        assert 1 <= n <= 1 << len(word) and 1 <= end < 3**q
        lifts = []
        for t in (0, 1, 3):
            lifted = n + (1 << len(word))*t
            image = realize(lifted, word)
            assert image == end + 3**q*t
            lifts.append([t, str(lifted), str(image)])
        endpoint_rows.append([word, str(n), str(end), lifts])
    return envelope("capacity-cycle", maximum_capacity_N=500, binomial_rows=binomial_rows,
                    entropy_certificate={"theta_numerator":14,"theta_denominator":23,"rho_numerator":29,"rho_denominator":30,"power_slope_valid":True,"power_entropy_valid":True},
                    X1_bound=1, cycle_scope={"maximum_odd_count":5,"maximum_exponent":4},
                    rational_cycle_count=len(rows), cycle_rows_sha256=digest(rows),
                    positive_integral_cycles=integer_cycles, rational_direction_exceptions=rational_examples,
                    direct_event_count=len(direct), direct_event_rows_sha256=digest(direct),
                    positive_endpoint_lifts={"maximum_word_length":12,"word_count":len(endpoint_rows),"lift_count":3*len(endpoint_rows),"rows_sha256":digest(endpoint_rows),"selected_rows":endpoint_rows[:2]+endpoint_rows[-2:]},
                    conditional_reduction={"uses_external_X02":True,"uses_phase38_E54":True,"H112_status":"OPEN","H72_status":"OPEN","cycle_exclusion_claimed":False,"reciprocal_includes_initial_odd_source":True})


def regressions() -> dict:
    wordlist = ["11101", "1100"] + ["11101"*r+"1100"*s for r in range(1,5) for s in range(1,5)]
    wordlist += ["".join(bs) for j in range(1,5) for bs in itertools.product(("110","111"),repeat=j)]
    word_rows = []
    for w in sorted(set(wordlist), key=lambda w:(len(w),w)):
        q,b=affine(w); n=source(w)
        word_rows.append([w,q,str(b),str(n),str(realize(n,w)),safe(w)])
    source_rows = []
    for label, starts in [("2^m-1",[2**m-1 for m in range(2,13)]),("8^m-5",[8**m-5 for m in range(1,9)]),("source 167",[167])]:
        for n in starts:
            x=n; bits=""
            for _ in range(32):
                bit=x%2;bits+=str(bit);x=(3*x+1)//2 if bit else x//2
            source_rows.append([label,str(n),bits,str(x)])
    residues=[]
    for w in ["11101","111100","11011101","110111100"]:
        q,b=affine(w); residues.append([w,str(realize(source(w),w)%3**q)])
    assert residues[0][1]==residues[1][1] and residues[2][1]!=residues[3][1]
    # NG22: exact h-policy maintains 1<h<=2 and a coherent odd 2-adic source.
    h=Fraction(3,2); word=""; formal=[]
    for j in range(128):
        e=1 if h<=Fraction(5,3) else 2
        h=(3*h-1)/(1 << e)
        assert 1<h<=2
        word += "1"+"0"*(e-1)
        formal.append([j,e,str(h),str(source(word))])
    negative=[]
    for n, es in [(-1,[1]),(-5,[1,2]),(-17,[1,1,1,2,1,1,4])]:
        x=n; trace=[n]
        for e in es:
            nxt, actual=accelerated(x);assert e==actual;x=nxt;trace.append(x)
        assert x==n
        negative.append([n,es,trace])
    return envelope("regressions", mandatory_families=FAMILIES, word_rows=word_rows,
                    source_rows=source_rows, NG24_endpoint_residues=residues,
                    NG22_formal_policy={"steps":128,"rows_sha256":digest(formal),"last_row":formal[-1],"ordinary_positive_source_claimed":False},
                    NG41_scalar_survivor={"q":2301,"L":3647,"A":229,"h":2,"J":138,"Sigma":90,"E":92,"n":24,"Z":10,"P207_margin":10,"P208_margin":43,"actual_cycle":False},
                    NG42_orientation={"q":3,"K":5,"actual":[0,1,2],"mechanical":[0,1,3],"missed_position":2},
                    zero_carry_controls={"identity":{"a":"1","d":"1","k":0,"s":0,"m":0},"periodic":{"a":"1","d":"101","S":1,"k":2,"s":1,"m":-1,"endpoint":2}},
                    negative_cycles=negative, AB_witness={"word":"111011100","B":817,"multiplier":"729/512","fixed_point":"-817/217"})


OBSTRUCTION = """# Phase 39 obstruction record

The literal identity a=d=1 has k=s=m=0 and zero carry at every depth.
The accepted fixed-rewrite theorem excludes identity relations. The nonidentity
pair a=1,d=101 at S=1 has k=2,s=1,m=-1 and zero carry, with both endpoints 2;
this is the periodic exception. No finite-dictionary direct-lift theorem rules
out arbitrary compositions, prefix-changing rules, or other proof methods.

The tail DAG audit checks safe alternatives separately from their weights.
No failure of that safety condition was found through tail length 12 and
initial run 12; this is not an all-depth safety theorem or global confluence.
The smallest DAG collision is J=3 at tail length 2, from tails 0 and 1.

Positive rational event directions require care: e=3 fixes x=1/5,y=3/5.
The accepted strict direction theorem assumes positive ordinary odd integers.
NG22, NG24, NG41, NG42, source 167, and negative cycles remain retained controls.

## What this result does not prove

H112 and H72 remain OPEN. The macroscopic carry lower bound constructs no
ancestor. The X02/H112 reduction is conditional. Finite DAG collisions do not
exclude positive ordinary infinite geodesics. Event counts do not exclude
arbitrary-area critical cycles. proves_collatz=false.
"""


def generate(directory: Path) -> dict:
    directory.mkdir(parents=True, exist_ok=True)
    outputs={"phase39_carry_audit.json":carry_audit(),"phase39_jump_dag.json":jump_dag(),"phase39_capacity_cycle.json":capacity_cycle(),"phase39_regressions.json":regressions()}
    for name,value in outputs.items():
        (directory/name).write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
    (directory/"phase39_obstruction_report.md").write_text(OBSTRUCTION)
    return {"valid":True,"carry_rows":outputs["phase39_carry_audit.json"]["row_count"],"dag_rewrites":outputs["phase39_jump_dag.json"]["rewrite_count"],"proves_collatz":False}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir",type=Path,default=Path("artifacts"))
    print(json.dumps(generate(parser.parse_args().artifact_dir),sort_keys=True))
