#!/usr/bin/env python3
"""Exact finite evidence for the critical-safe-mass proposal.
No repository modules, floating-point acceptance, or network access.
This is a generator, not an authority for the infinite proof.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import json
import math
import sys
from pathlib import Path

MAX_N = 512
SCHEMA = "critical-safe-mass-v1"

def frac(f: Fraction) -> dict[str, str]:
    return {"numerator": str(f.numerator), "denominator": str(f.denominator)}

def counts(max_n: int) -> tuple[list[int], list[int]]:
    powers = [3**j for j in range(max_n + 1)]
    layer = [1]
    a, b = [1], [0]
    for n in range(1, max_n + 1):
        nxt = [0] * (n + 1)
        for q, value in enumerate(layer):
            if powers[q] > (1 << n):
                nxt[q] += value
            if powers[q + 1] > (1 << n):
                nxt[q + 1] += value
        layer = nxt
        a.append(sum(layer))
        b.append(sum(math.comb(n, q) for q in range(n + 1)
                     if powers[q] > (1 << n)))
    return a, b

def literal_safe(source: int, n: int) -> bool:
    x, p3, p2 = source, 1, 1
    for _ in range(n):
        odd = x & 1
        x = (3*x + 1)//2 if odd else x//2
        p2 *= 2
        if odd:
            p3 *= 3
        if p3 <= p2:
            return False
    return True

def interval_queries(a: list[int]) -> list[dict[str, int | str]]:
    queries: list[dict[str, int | str]] = []
    # Full dyadic shells: exactly a_n passing finite prefixes, not permanent orbits.
    for n in range(0, 17):
        lo, width = 1 << n, 1 << n
        actual = sum(literal_safe(x, n) for x in range(lo, lo + width))
        if actual != a[n]:
            raise ArithmeticError("dyadic shell mismatch")
        queries.append({"kind": "full_shell", "n": n, "start": str(lo),
                        "width": width, "safe_through_n": actual,
                        "word_capacity": a[n]})
    # Translated intervals, including very large ordinary integers and partial blocks.
    for n in range(1, 15):
        period = 1 << n
        width = min(period, 257 + 3*n)
        for lo in (1, 3*period + 7, (1 << 200) + 12345 + 37*n):
            actual = sum(literal_safe(x, n) for x in range(lo, lo + width))
            if actual > a[n]:
                raise ArithmeticError("translated capacity violation")
            queries.append({"kind": "translated", "n": n, "start": str(lo),
                            "width": width, "safe_through_n": actual,
                            "word_capacity": a[n]})
    return queries

def generate(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    a, b = counts(MAX_N)
    for n in range(1, MAX_N + 1):
        if n*a[n] != sum(b[k]*a[n-k] for k in range(1, n+1)):
            raise ArithmeticError("cycle recurrence mismatch")
    u = Fraction(19317, 10000)
    nu = Fraction(1933, 1000)
    finite = sum((Fraction(b[n], n) / u**n for n in range(1, MAX_N + 1)), Fraction())
    tail = Fraction(4, 11)
    upper = finite + tail
    c2 = Fraction(22, 7) / (8*Fraction(232839, 10**6)) * Fraction(63, 26)**2
    checks = {
        "theta_above_63_over_100": 3**63 < 2**100,
        "theta_below_631_over_1000": 3**631 > 2**1000,
        "mu_lower_exact": (1000*10000)**1000 > 19317**1000 * 631**631 * 369**369,
        "mu_upper_exact": 1933**100 * 63**63 * 37**37 > 10**500,
        "coefficient_lower_table": all((24*a[n])**2*n**3*1000**(2*n) >= 1933**(2*n) for n in range(1,MAX_N+1)),
        "coefficient_upper_table": all(a[n]**2*n**3*10000**(2*n) < 446**2*19317**(2*n) for n in range(1,MAX_N+1)),
        "binomial_constant_squared_below_16": c2 < 16,
        "tail_8_over_sqrt_512_below_4_over_11": 8**2 * 11**2 < 4**2 * 512,
        "S_upper_below_219_over_100": upper < Fraction(219, 100),
        "219_over_100_below_twice_log3_lower": Fraction(219, 100) < Fraction(263, 120),
        "coefficient_constant_below_446": 36*(Fraction(219, 100)**2 + 3*Fraction(219,100) + 1) < 446,
    }
    if not all(checks.values()):
        raise ArithmeticError("exact numerical certificate failed")
    data = {
        "schema": SCHEMA,
        "scope": {"max_n": MAX_N, "word_enumeration_n": 18,
                  "labeled_bijection_n": 6, "proves_collatz": False,
                  "permanent_source_existence_asserted": False,
                  "status": "VERIFIED_FINITE"},
        "counts": [{"n": n, "a": str(a[n]), "b": str(b[n])} for n in range(MAX_N+1)],
        "mass_certificate": {"mu_lower": frac(u), "mu_upper": frac(nu),
                             "safe_coefficient_lower": frac(Fraction(1,24)), "finite_sum_upper": frac(finite),
                             "tail_upper": frac(tail), "S_upper": frac(upper),
                             "binomial_constant_squared_upper": frac(c2),
                             "S_rational_bound": frac(Fraction(219, 100)),
                             "safe_coefficient_constant": 446,
                             "critical_mass_upper": 9,
                             "exact_checks": checks},
        "interval_queries": interval_queries(a),
        "controls": {"one_is_not_permanent_safe": not literal_safe(1, 2),
                     "all_one_sources": [str((1 << n)-1) for n in range(1,33)]},
    }
    # The second control's exact horizon is computed, never inferred.
    seven = [literal_safe(7,n) for n in range(0,20)]
    data["controls"]["seven_first_failed_prefix"] = next(n for n in range(1,20) if not seven[n])
    (out/"critical_safe_mass_evidence.json").write_text(json.dumps(data, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps({"generated": str(out/"critical_safe_mass_evidence.json"), "count_rows": len(a),
                      "interval_queries": len(data["interval_queries"]), "proves_collatz": False}))

def supplementary(out):
    root=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(root))
    from src.transient_sparsity_search import regressions
    old=regressions()
    words=[]
    for w,B,residue,endpoint in old['words']:
        source=int(residue) or 2**len(w)
        words.append([w,residue,literal_safe(source,len(w))])
    paths=[[row[0],row[1],literal_safe(int(row[0]),row[1])] for row in old['paths']]
    filters=[]
    for b in (0,1,2,7,2**200):
        for n in range(11):
            lo=b+2**n
            survivors=[x for x in range(lo,lo+2**n) if literal_safe(x,n)]
            filters.append([str(b),n,len(survivors),str(min(survivors)),str(max(survivors))])
    import hashlib
    historical=dict(old['historical_sha256'])
    for name in ('phase41_formal.json','ext08_scope_impact.json','transient_sparsity_evidence.json'):
        historical[name]=hashlib.sha256((root/'artifacts'/name).read_bytes()).hexdigest()
    scope={
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
    reg={'schema':'critical-safe-mass-regressions-v1','status':'VERIFIED_FINITE','proves_collatz':False,
         'finite_only':True,'words':words,'paths':paths,'filters':filters,
         'historical_sha256':historical,'tied_mean_control':{'bits':'11','centered':[0,0]},
         'mass_only_countermodel':{'set':'{2^k:k>=1}','uniform_upper':3,'permanent_safe':False}}
    for name,obj in [('scope',scope),('regressions',reg)]:
        (out/('critical_safe_mass_'+name+'.json')).write_text(json.dumps(obj,sort_keys=True,indent=2)+'\n')

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--artifact-dir',type=Path,required=True)
    args=parser.parse_args(); generate(args.artifact_dir); supplementary(args.artifact_dir)
