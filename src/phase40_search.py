#!/usr/bin/env python3
"""Exact Phase 40 finite audit; all infinite assertions require REPORT.md.

The C++ accelerator uses proved-safe packed integers, not approximate arithmetic.
Python reconstructs its complete safety-threshold table with arbitrary precision.
"""
from __future__ import annotations

import argparse
import hashlib
import heapq
import itertools
import json
import subprocess
import tempfile
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


def digest(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def envelope(kind, **kw):
    return {"format": f"collatz-phase40-{kind}-v1", "proves_collatz": False, **kw}


def affine(word):
    q = b = 0
    for j, bit in enumerate(word):
        if bit == "1":
            q += 1
            b = 3*b+(1 << j)
        elif bit != "0":
            raise ValueError("binary word required")
    return q, b


def safe(word):
    q = 0
    for j, bit in enumerate(word, 1):
        q += bit == "1"
        if 3**q <= 1 << j:
            return False
    return True


def source(word):
    q, b = affine(word)
    mod = 1 << len(word)
    return (-b*pow(3**q, -1, mod)) % mod or mod


def realize(n, word):
    for bit in word:
        assert n % 2 == int(bit)
        n = (3*n+1)//2 if bit == "1" else n//2
    return n


def accelerated(n):
    y, e = 3*n+1, 0
    while y % 2 == 0:
        y //= 2
        e += 1
    return y, e


def minimum_run(tail):
    r = 1
    while not safe("1"*r+tail):
        r += 1
    return r


@lru_cache(None)
def shortest_length(q, endpoint, bound):
    """Dijkstra search backwards in the positive odd inverse tree.

    Every edge has exponent >=1. An actual path supplies the finite bound;
    the first q-layer node popped is globally minimal, including unbounded
    competitors (none above the bound can beat it).
    """
    heap = [(0, 0, endpoint)]
    seen = {}
    while heap:
        cost, depth, y = heapq.heappop(heap)
        if (depth, y) in seen:
            continue
        seen[depth, y] = cost
        if depth == q:
            return cost
        for e in range(1, bound-cost-(q-depth-1)+1):
            raw = (1 << e)*y-1
            if raw % 3 == 0:
                z = raw//3
                if z > 0 and z % 2:
                    heapq.heappush(heap, (cost+e, depth+1, z))
    raise ValueError("no positive path within bound")


def word_row(word, n=None):
    if n is None:
        n = source(word)
    q, b = affine(word)
    return {"word": word, "length": len(word), "Q": q, "B": str(b),
            "source": str(n), "endpoint": str(realize(n, word)), "safe": safe(word)}


def bellman():
    rows = []
    for S in range(1, 256, 2):
        x, E, beta, product, old_r = S, 0, Fraction(0), Fraction(S), 0
        for q in range(1, 9):
            beta += Fraction(1 << E, 3**q)
            product *= 1+Fraction(1, 3*x)
            x, e = accelerated(x)
            E += e
            normal = Fraction((1 << E)*x, 3**q)
            assert normal == S+beta == product
            ell = shortest_length(q, x, E)
            redundancy = E-ell
            assert old_r <= redundancy and 1 << redundancy < normal
            old_r = redundancy
            rows.append([S, q, str(x), E, ell, redundancy, str(normal)])
    scaling = []
    for S in range(1, 128, 2):
        x, E, es = S, 0, []
        for _ in range(8):
            x, e = accelerated(x)
            es.append(e)
        for cut in range(1, 8):
            left = "".join("1"+"0"*(e-1) for e in es[:cut])
            right = "".join("1"+"0"*(e-1) for e in es[cut:])
            mid = realize(S, left)
            end = realize(mid, right)
            value = Fraction((1 << (len(left)+len(right)))*end, 3**8)
            scaled = Fraction((1 << len(right))*end, 3**(8-cut))*Fraction(1 << len(left), 3**cut)
            assert value == scaled
            scaling.append([S, cut, str(mid), str(value)])
    return envelope("bellman", maximum_source=255, odd_steps=8, rows=rows,
                    row_count=len(rows), rows_sha256=digest(rows),
                    scaling_count=len(scaling), scaling_sha256=digest(scaling),
                    half_factor_control={"target": word_row("111111000", 63),
                                         "competitor": word_row("11111010", 31),
                                         "shortest_length": shortest_length(6, 91, 9),
                                         "normalization_ratio": "1/2", "nonperiodic_claimed": False},
                    reduction={"uses_X02": False, "uses_capacity_2_to_49": False,
                               "H112_status": "OPEN", "H72_status": "OPEN", "cycle_exclusion_claimed": False,
                               "effective_stabilization_index_claimed": False,
                               "replacement_bound": "at most half; strict only after an unsafe valley or r>1",
                               "normalization_domain": "all positive odd sources with a non-eventually-periodic future"})


def safety_minimality(maximum=25):
    thresholds = []
    for ell in range(1, maximum+1):
        row = []
        for q in range(ell):
            R = 1
            while 3**(R+q) <= 1 << (R+ell):
                R += 1
            assert R+q <= 68 and R+ell < 127
            row.append(R)
        thresholds.append(row)
    with tempfile.TemporaryDirectory(prefix="collatz-phase40-generator-") as temp:
        binary = Path(temp)/"enumerate"
        subprocess.run(["c++", "-O3", "-std=c++17", str(ROOT/"src/phase40_minimality.cpp"), "-o", str(binary)], check=True)
        output = subprocess.run([str(binary), str(maximum)], check=True, capture_output=True, text=True, timeout=900)
        levels = json.loads(output.stdout)
    v, alt = "0110110110110110001101101", "0011111111111111010000100"
    d, a = "1111"+v, "111"+alt
    n, m = source(d), source(a)
    coeffs = [Fraction(1)]
    for L in range(1, len(a)+1):
        coeffs.append(Fraction(3**a[:L].count("1"), 1 << L))
    valley = min(range(len(coeffs)), key=coeffs.__getitem__)
    z = realize(m, a[:valley])
    suffix = a[valley:]
    assert safe(d) and not safe(a) and safe(suffix)
    assert realize(n, d) == realize(m, a) == realize(z, suffix)
    q, b = affine(v)
    J = b+(1 << len(v))-3**q
    assert J == 166692291
    witness = {"tail": v, "alternative_tail": alt, "J": str(J),
               "original_Rmin": minimum_run(v), "alternative_Rmin": minimum_run(alt),
               "target": word_row(d, n), "competitor": word_row(a, m),
               "valley_index": valley, "valley_coefficient": str(coeffs[valley]),
               "rescued_suffix": word_row(suffix, z), "suffix_canonical_source": str(source(suffix)),
               "suffix_source_lift": (z-source(suffix))//(1 << len(suffix))}
    return envelope("safety-minimality", maximum_tail_length=maximum, initial_run_bound=None,
                    threshold_table=thresholds, levels=levels,
                    total_tail_count=sum(row["tail_count"] for row in levels),
                    first_failure_length=next((r["ell"] for r in levels if r["failing_pair_count"]), None),
                    ordering="ell, lexicographic original tail, lexicographic alternative tail; least failing R",
                    witness=witness)


def cloud():
    rows, transitions = [], []
    for S in range(1, 4096, 2):
        x, E = S, 0
        for j in range(32):
            y, e = accelerated(x)
            ratio = Fraction(1 << e, x+1)
            assert ratio < Fraction(3, y)
            transitions.append([S, j, str(x), e, str(y), str(ratio)])
            for r in range(1, (e-1)//2+1):
                raw = 3*x+1-(4**r)
                assert raw % (3*4**r) == 0
                z = raw//(3*4**r)
                assert z > 0 and z % 2 and accelerated(z) == (y, e-2*r)
                assert E < E+2*r < E+e
                assert Fraction(4**r, x+1) < Fraction(1, z)
                rows.append([S, j, str(x), e, E, r, str(z), str(y), E+2*r])
            x, E = y, E+e
    def step(x):
        return (3*x+1)//2 if x % 2 else x//2
    control = [5, 1]
    traces = [[z] for z in control]
    for trace in traces:
        for _ in range(4):
            trace.append(step(trace[-1]))
    assert traces[0][-1] == traces[1][-1]
    return envelope("cloud", maximum_source=4095, odd_steps=32,
                    row_count=len(rows), rows_sha256=digest(rows), selected_rows=rows[:4]+rows[-4:],
                    transition_count=len(transitions), transition_sha256=digest(transitions),
                    periodic_control={"source": 21, "exponent": 6, "cloud_sources": control,
                                      "traces": traces, "equal_time_collision": 4},
                    proof_scope={"nonperiodicity_required_for_cloud_injectivity": True,
                                 "finite_orbits_claimed_nonperiodic": False,
                                 "moment_quantifier": "every real p>rho_star; all j, not just e_j>=3",
                                 "direct_moment_bound": "2^e/(x+1)<3/x_next",
                                 "new_independent_obstruction_claimed": False})


def regressions():
    words = []
    for m in range(1, 17):
        for name, n in [("2^m-1", (1 << m)-1), ("8^m-5", 8**m-5)]:
            bits, x = "", n
            for _ in range(64):
                bits += str(x % 2)
                x = (3*x+1)//2 if x % 2 else x//2
            words.append([name, m, str(n), word_row(bits, n)])
    for n in range(1, 6):
        for blocks in itertools.product(("110", "111"), repeat=n):
            w = "".join(blocks)
            words.append(["(110|111)^*", n, w, word_row(w)])
    for r in range(1, 5):
        for s in range(1, 5):
            w = "11101"*r+"1100"*s
            words.append(["A^rB^s", r, s, word_row(w)])
    for name, w in [("A=11101", "11101"), ("B=1100", "1100")]:
        words.append([name, 1, w, word_row(w)])
    h, es, residue, E = Fraction(3, 2), [], 0, 0
    for j in range(128):
        e = 1 if h <= Fraction(5, 3) else 2
        h = (3*h-1)/(1 << e)
        assert 1 < h <= 2
        es.append(e)
    formal = "".join("1"+"0"*(e-1) for e in es)
    endpoints = []
    for w in ("11011101", "110111100"):
        endpoints.append([w, word_row(w)["endpoint"]])
    x, w, residues = 167, "", []
    for _ in range(17):
        x, e = accelerated(x)
        w += "1"+"0"*(e-1)
        # P115 uses the affine prefix modulus 2^E, not an extra final odd bit.
        residues.append(str(source(w)))
    trailing = 0
    for left, right in zip(residues[-2::-1], residues[:0:-1]):
        if left != right:
            break
        trailing += 1
    assert trailing == 11 and safe(w)
    x, future = 167, ""
    while safe(future):
        future += str(x % 2)
        x = (3*x+1)//2 if x % 2 else x//2
    return envelope("regressions", mandatory_families=FAMILIES, family_rows=words,
                    NG22={"steps": 128, "last_companion": str(h), "source_residue": str(source(formal+"1")),
                          "ordinary_positive_infinite_source_claimed": False},
                    NG24={"prefixed_endpoints": endpoints},
                    NG41={"q": 2301, "L": 3647, "A": 229, "h": 2, "J": 138,
                          "Sigma": 90, "E": 92, "n": 24, "Z": 10,
                          "P207_margin": 10, "P208_margin": 43, "actual_cycle": False},
                    NG42={"q": 3, "K": 5, "actual_odd_positions": [0, 1, 2], "mechanical_positions": [0, 1, 3],
                          "wrong_interval": [3, 5], "missed_position": 2},
                    source167={"accelerated_source_residues": residues, "critical_word": w,
                               "trailing_zero_lifts": trailing, "first_coefficient_failure_length": len(future),
                               "infinite_safe_stabilization_claimed": False},
                    AB={"word": "111011100", "Q": affine("111011100")[0], "B": str(affine("111011100")[1]),
                        "denominator": 512, "fixed_point": "-817/217"},
                    negative_cycles=[[-1, [1]], [-5, [1, 2]], [-17, [1, 1, 1, 2, 1, 1, 4]]],
                    cycle_exclusion_claimed=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=ROOT/"artifacts")
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    for name, build in [("bellman", bellman), ("safety_minimality", safety_minimality), ("cloud", cloud), ("regressions", regressions)]:
        value = build()
        (args.artifact_dir/f"phase40_{name}.json").write_text(json.dumps(value, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        print(json.dumps({"generated": name, "proves_collatz": False}), flush=True)


if __name__ == "__main__":
    main()
