#!/usr/bin/env python3
"""Independent exact Phase 40 verifier.

Shortest paths use exact-total-length inverse feasibility, not a priority
queue. The C++ helper enumerates literal tail masks by closed zero-position
sums, with checked integer bounds; Python checks all thresholds with arbitrary
precision and cross-checks small complete levels by direct prefix safety.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import subprocess
import sys
import tempfile
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = ("phase40_bellman.json", "phase40_safety_minimality.json",
         "phase40_cloud.json", "phase40_regressions.json")
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]
STATUSES = {**{f"P{n}":"VERIFIED_THEOREM" for n in range(242,247)},
            "NG43":"REFUTED", "E56":"VERIFIED_FINITE",
            "H112":"OPEN", "H72":"OPEN", "H133":"OPEN"}


class VerificationError(RuntimeError):
    """Evidence is malformed, incomplete, or inconsistent with reconstruction."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def envelope(kind: str, **values: object) -> dict:
    return {"format":f"collatz-phase40-{kind}-v1", "proves_collatz":False, **values}


@lru_cache(maxsize=None)
def positional_affine(word: str) -> tuple[int, int]:
    require(set(word) <= {"0","1"}, "nonbinary literal word")
    odd_positions = [j for j,bit in enumerate(word) if bit == "1"]
    weight = len(odd_positions)
    correction = sum(2**position*3**(weight-rank-1)
                     for rank,position in enumerate(odd_positions))
    return weight, correction


def shortcut(value: int) -> int:
    return (3*value+1)//2 if value % 2 else value//2


def walk(source: int, word: str) -> list[int]:
    trajectory = [source]
    for bit in word:
        require(trajectory[-1] % 2 == int(bit), "literal parity disagreement")
        trajectory.append(shortcut(trajectory[-1]))
    q,b = positional_affine(word)
    require(2**len(word)*trajectory[-1] == 3**q*source+b, "odd-position affine identity")
    return trajectory


@lru_cache(maxsize=None)
def least_positive_source(word: str) -> int:
    # Successive source bits are fixed by the next literal parity.
    residue = 0
    for index,bit in enumerate(word):
        if walk(residue,word[:index])[-1] % 2 != int(bit):
            residue += 2**index
    answer = residue or 2**len(word)
    walk(answer,word)
    return answer


def prefix_safe(word: str) -> bool:
    return all(3**word[:j].count("1") > 2**j for j in range(1,len(word)+1))


def odd_step(value: int) -> tuple[int,int]:
    require(value % 2 == 1, "odd-step source parity")
    endpoint,e = shortcut(value),1
    while endpoint % 2 == 0:
        endpoint = shortcut(endpoint)
        e += 1
    return endpoint,e


def describe_word(word: str, source: int | None = None) -> dict:
    initial = least_positive_source(word) if source is None else source
    weight,correction = positional_affine(word)
    return {"word":word, "length":len(word), "Q":weight, "B":str(correction),
            "source":str(initial), "endpoint":str(walk(initial,word)[-1]), "safe":prefix_safe(word)}


@lru_cache(maxsize=None)
def exact_length_feasible(remaining: int, endpoint: int, length: int) -> bool:
    """Existence of a positive odd inverse path with exactly the given length."""
    if remaining == 0:
        return length == 0 and endpoint > 0 and endpoint % 2 == 1
    if length < remaining or endpoint <= 0 or endpoint % 2 == 0 or endpoint % 3 == 0:
        return False
    for exponent in range(1,length-remaining+2):
        quotient,remainder = divmod(2**exponent*endpoint-1,3)
        if remainder == 0 and quotient > 0 and quotient % 2 == 1:
            if exact_length_feasible(remaining-1,quotient,length-exponent):
                return True
    return False


def minimum_length(q: int, endpoint: int, actual_bound: int) -> int:
    for length in range(q,actual_bound+1):
        if exact_length_feasible(q,endpoint,length):
            return length
    raise VerificationError("actual path missing from inverse exact-length search")


def rebuild_bellman() -> dict:
    rows = []
    for source in range(1,256,2):
        value,word,old_redundancy = source,"",0
        product = Fraction(source)
        for weight in range(1,9):
            product *= Fraction(3*value+1,3*value)
            value,exponent = odd_step(value)
            word += "1"+"0"*(exponent-1)
            _,correction = positional_affine(word)
            normal = Fraction(2**len(word)*value,3**weight)
            require(normal == source+Fraction(correction,3**weight) == product,
                    "finite normalization product/affine agreement")
            shortest = minimum_length(weight,value,len(word))
            redundancy = len(word)-shortest
            require(old_redundancy <= redundancy and 2**redundancy < normal,
                    "Bellman monotonicity or strict finite height bound")
            old_redundancy = redundancy
            rows.append([source,weight,str(value),len(word),shortest,redundancy,str(normal)])
    scaling = []
    for source in range(1,128,2):
        odd_values,exponents = [source],[]
        for _ in range(8):
            endpoint,exponent = odd_step(odd_values[-1])
            odd_values.append(endpoint)
            exponents.append(exponent)
        normal = Fraction(2**sum(exponents)*odd_values[-1],3**8)
        for cut in range(1,8):
            left_length = sum(exponents[:cut])
            right_length = sum(exponents[cut:])
            tail_normal = Fraction(2**right_length*odd_values[-1],3**(8-cut))
            require(tail_normal*Fraction(2**left_length,3**cut) == normal,
                    "coalescing normalized-height scaling")
            scaling.append([source,cut,str(odd_values[cut]),str(normal)])
    target = describe_word("111111000",63)
    competitor = describe_word("11111010",31)
    require(target["endpoint"] == competitor["endpoint"] == "91" and target["Q"] == competitor["Q"] == 6,
            "exact half-factor coalescence")
    require(Fraction(2**competitor["length"],3**6)/Fraction(2**target["length"],3**6) == Fraction(1,2),
            "safe half-factor strictness control")
    return envelope("bellman", maximum_source=255, odd_steps=8, rows=rows,
                    row_count=len(rows), rows_sha256=digest(rows), scaling_count=len(scaling),
                    scaling_sha256=digest(scaling),
                    half_factor_control={"target":target,"competitor":competitor,
                                         "shortest_length":minimum_length(6,91,9),
                                         "normalization_ratio":"1/2","nonperiodic_claimed":False},
                    reduction={"uses_X02":False,"uses_capacity_2_to_49":False,
                               "H112_status":"OPEN","H72_status":"OPEN","cycle_exclusion_claimed":False,
                               "effective_stabilization_index_claimed":False,
                               "replacement_bound":"at most half; strict only after an unsafe valley or r>1",
                               "normalization_domain":"all positive odd sources with a non-eventually-periodic future"})


def threshold_table(maximum: int) -> list[list[int]]:
    answer = []
    for length in range(1,maximum+1):
        row = []
        for weight in range(length):
            run = next(r for r in itertools.count(1) if 3**(r+weight) > 2**(r+length))
            require(run <= 43 and run+weight <= 68 and run+length < 127,
                    "checked C++ power envelope")
            row.append(run)
        answer.append(row)
    return answer


def direct_small_levels(maximum: int = 9) -> list[dict]:
    """A third small-domain check: direct safety for every relevant initial run."""
    levels = []
    for ell in range(1,maximum+1):
        grouped = defaultdict(list)
        for mask in range(2**(ell-1)):
            tail = format(mask,f"0{ell}b")
            q,b = positional_affine(tail)
            jump = b+2**ell-3**q
            run = next(r for r in itertools.count(1) if prefix_safe("1"*r+tail))
            grouped[jump].append((tail,q,run))
        pair_count = failing_count = run_count = 0
        first = None
        for jump,group in grouped.items():
            for original,weight,minimum in group:
                for alternative,other_weight,other_minimum in group:
                    gain = other_weight-weight
                    if gain <= 0:
                        continue
                    pair_count += 1
                    # Beyond this exact endpoint both words are safe, so there
                    # are no omitted larger R values in this direct audit.
                    failed = [run for run in range(gain+1,other_minimum+gain)
                              if prefix_safe("1"*run+original)
                              and not prefix_safe("1"*(run-gain)+alternative)]
                    if not failed:
                        continue
                    failing_count += 1
                    run_count += len(failed)
                    candidate = {"original_tail":original,"alternative_tail":alternative,
                                 "J":str(jump),"gain":gain,"Rlo":min(failed),"Rhi":max(failed),
                                 "original_Rmin":minimum,"alternative_Rmin":other_minimum}
                    if first is None or (original,alternative) < (first["original_tail"],first["alternative_tail"]):
                        first = candidate
        levels.append({"ell":ell,"tail_count":2**(ell-1),"vertex_count":len(grouped),
                       "collision_vertex_count":sum(len(g)>1 for g in grouped.values()),
                       "weight_gain_pair_count":pair_count,"failing_pair_count":failing_count,
                       "failing_initial_run_count":run_count,"first_failure":first})
    return levels


@lru_cache(maxsize=1)
def cpp_minimality() -> str:
    helper = ROOT/"verifier"/"phase40_minimality.cpp"
    try:
        with tempfile.TemporaryDirectory(prefix="collatz-phase40-verifier-") as temporary:
            executable = Path(temporary)/"minimality"
            subprocess.run(["c++","-O3","-std=c++17",str(helper),"-o",str(executable)],
                           capture_output=True,text=True,check=True,timeout=120)
            result = subprocess.run([str(executable)],capture_output=True,text=True,check=True,timeout=900)
    except (OSError,subprocess.SubprocessError) as exc:
        raise VerificationError(f"independent C++ reconstruction failed: {exc}") from exc
    try:
        computed = json.loads(result.stdout)
    except (ValueError,RecursionError) as exc:
        raise VerificationError(f"malformed independent C++ result: {exc}") from exc
    require(computed.get("maximum_tail_length") == 25 and computed.get("initial_run_bound") is None
            and computed.get("proves_collatz") is False, "independent enumeration scope")
    require(computed.get("threshold_table") == threshold_table(25), "arbitrary-precision threshold cross-check")
    require(computed.get("levels",[])[:9] == direct_small_levels(9), "small direct safety cross-check")
    return canonical(computed)


def rebuild_safety() -> dict:
    reconstruction = json.loads(cpp_minimality())
    levels = reconstruction["levels"]
    failures = [row["ell"] for row in levels if row["failing_pair_count"]]
    require(failures and failures[0] == 25, "claimed finite first-failure length")
    v = "0110110110110110001101101"
    alternative = "0011111111111111010000100"
    target,competitor = "1111"+v,"111"+alternative
    n,m = least_positive_source(target),least_positive_source(competitor)
    coefficients = [Fraction(3**competitor[:j].count("1"),2**j) for j in range(len(competitor)+1)]
    valley = min(range(len(coefficients)),key=coefficients.__getitem__)
    require(sum(c == coefficients[valley] for c in coefficients) == 1, "unique strict valley")
    ancestor = walk(m,competitor[:valley])[-1]
    suffix = competitor[valley:]
    require(prefix_safe(target) and not prefix_safe(competitor) and prefix_safe(suffix), "unsafe-gain valley rescue")
    require(walk(n,target)[-1] == walk(m,competitor)[-1] == walk(ancestor,suffix)[-1], "valley common endpoint")
    require(Fraction(3**suffix.count("1"),2**len(suffix)) > Fraction(3**target.count("1"),2**len(target)),
            "rescued coefficient dominance")
    def minimum_run(tail):
        return next(r for r in itertools.count(1) if prefix_safe("1"*r+tail))
    q,b = positional_affine(v)
    q_alt,b_alt = positional_affine(alternative)
    jump = b+2**len(v)-3**q
    require(jump == b_alt+2**len(alternative)-3**q_alt == 166692291, "supplied jump collision")
    canonical_source = least_positive_source(suffix)
    lift,remainder = divmod(ancestor-canonical_source,2**len(suffix))
    require(remainder == 0 and lift >= 0, "ordinary suffix lift")
    witness = {"tail":v,"alternative_tail":alternative,"J":str(jump),
               "original_Rmin":minimum_run(v),"alternative_Rmin":minimum_run(alternative),
               "target":describe_word(target,n),"competitor":describe_word(competitor,m),
               "valley_index":valley,"valley_coefficient":str(coefficients[valley]),
               "rescued_suffix":describe_word(suffix,ancestor),"suffix_canonical_source":str(canonical_source),
               "suffix_source_lift":lift}
    return envelope("safety-minimality",maximum_tail_length=25,initial_run_bound=None,
                    threshold_table=threshold_table(25),levels=levels,
                    total_tail_count=sum(row["tail_count"] for row in levels),first_failure_length=failures[0],
                    ordering="ell, lexicographic original tail, lexicographic alternative tail; least failing R",
                    witness=witness)


def rebuild_cloud() -> dict:
    rows,transitions = [],[]
    for source in range(1,4096,2):
        value,elapsed = source,0
        for step in range(32):
            endpoint,exponent = odd_step(value)
            ratio = Fraction(2**exponent,value+1)
            require(ratio < Fraction(3,endpoint), "all-j direct moment comparison")
            transitions.append([source,step,str(value),exponent,str(endpoint),str(ratio)])
            for reduction in range(1,(exponent-1)//2+1):
                shorter = exponent-2*reduction
                predecessor,remainder = divmod(2**shorter*endpoint-1,3)
                require(remainder == 0 and predecessor > 0 and predecessor % 2 == 1,
                        "alternate positive ordinary predecessor")
                require(odd_step(predecessor) == (endpoint,shorter), "alternate exact valuation")
                require(3*4**reduction*predecessor == 3*value+1-4**reduction,
                        "cloud source formula")
                offset = elapsed+2*reduction
                require(elapsed < offset < elapsed+exponent, "strict disjoint offset window")
                require(Fraction(4**reduction,value+1) < Fraction(1,predecessor), "cloud moment comparison")
                rows.append([source,step,str(value),exponent,elapsed,reduction,str(predecessor),str(endpoint),offset])
            value,elapsed = endpoint,elapsed+exponent
    controls,traces = [5,1],[]
    for initial in controls:
        trajectory = [initial]
        for _ in range(4):
            trajectory.append(shortcut(trajectory[-1]))
        traces.append(trajectory)
    require(odd_step(21) == (1,6) and traces[0][4] == traces[1][4], "periodic cloud collision control")
    return envelope("cloud",maximum_source=4095,odd_steps=32,row_count=len(rows),rows_sha256=digest(rows),
                    selected_rows=rows[:4]+rows[-4:],transition_count=len(transitions),transition_sha256=digest(transitions),
                    periodic_control={"source":21,"exponent":6,"cloud_sources":controls,"traces":traces,"equal_time_collision":4},
                    proof_scope={"nonperiodicity_required_for_cloud_injectivity":True,
                                 "finite_orbits_claimed_nonperiodic":False,
                                 "moment_quantifier":"every real p>rho_star; all j, not just e_j>=3",
                                 "direct_moment_bound":"2^e/(x+1)<3/x_next",
                                 "new_independent_obstruction_claimed":False})


def rebuild_regressions() -> dict:
    rows = []
    for power in range(1,17):
        for label,source in (("2^m-1",2**power-1),("8^m-5",8**power-5)):
            value,word = source,""
            for _ in range(64):
                word += str(value % 2)
                value = shortcut(value)
            rows.append([label,power,str(source),describe_word(word,source)])
    for count in range(1,6):
        for blocks in itertools.product(("110","111"),repeat=count):
            word = "".join(blocks)
            rows.append(["(110|111)^*",count,word,describe_word(word)])
    for r in range(1,5):
        for s in range(1,5):
            word = "11101"*r+"1100"*s
            rows.append(["A^rB^s",r,s,describe_word(word)])
    for label,word in (("A=11101","11101"),("B=1100","1100")):
        rows.append([label,1,word,describe_word(word)])
    companion,formal = Fraction(3,2),""
    for _ in range(128):
        exponent = 1 if companion <= Fraction(5,3) else 2
        companion = (3*companion-1)/2**exponent
        require(1 < companion <= 2, "NG22 companion policy")
        formal += "1"+"0"*(exponent-1)
    endpoints = [[word,describe_word(word)["endpoint"]] for word in ("11011101","110111100")]
    require(endpoints[0][1] != endpoints[1][1], "NG24 prefixed endpoint distinction")
    value,word,residues = 167,"",[]
    old,modulus = 0,1
    for _ in range(17):
        value,exponent = odd_step(value)
        word += "1"+"0"*(exponent-1)
        residue = least_positive_source(word)
        require((residue-old) % modulus == 0 and 167 % 2**len(word) == residue % 2**len(word),
                "P115 affine-prefix source residue")
        residues.append(str(residue))
        old,modulus = residue,2**len(word)
    trailing = 0
    for index in range(len(residues)-1,0,-1):
        if residues[index] != residues[index-1]:
            break
        trailing += 1
    require(trailing == 11 and prefix_safe(word), "source167 finite safe plateau")
    value,first_failure,weight = 167,None,0
    for length in range(1,10001):
        weight += value % 2
        value = shortcut(value)
        if 3**weight < 2**length:
            first_failure = length
            break
    require(first_failure == 29, "source167 coefficient crossing")
    negative_cycles = [[-1,[1]],[-5,[1,2]],[-17,[1,1,1,2,1,1,4]]]
    for source,exponents in negative_cycles:
        value = source
        for expected_exponent in exponents:
            value,exponent = odd_step(value)
            require(exponent == expected_exponent, "negative cycle exponent")
        require(value == source, "negative cycle closure")
    mechanical = [(3**j).bit_length()-1 for j in range(3)]
    require(mechanical == [0,1,3] and 2 not in range(3,5), "NG42 orientation control")
    q0,length0,area,height,components,surplus,exceptional,width,zeroes = 2301,3647,229,2,138,90,92,24,10
    scalar = width+1+components*(width-1)+min(2*area,length0*area//q0+components)
    residual = area-components+exceptional
    residual_span = min(2*residual,length0*residual//q0+exceptional)
    triple = ((components+2*exceptional)*(width+1)+3*residual_span
              +(width+3)*(3+2*zeroes+zeroes*(zeroes-1)//2))
    require(scalar-length0 == 10 and triple-3*length0 == 43, "NG41 reconstructed scalar margins")
    q,b = positional_affine("111011100")
    fixed = Fraction(b,512-3**q)
    require((q,b,fixed) == (6,817,Fraction(-817,217)), "AB rational witness")
    return envelope("regressions",mandatory_families=FAMILIES,family_rows=rows,
                    NG22={"steps":128,"last_companion":str(companion),"source_residue":str(least_positive_source(formal+"1")),
                          "ordinary_positive_infinite_source_claimed":False},
                    NG24={"prefixed_endpoints":endpoints},
                    NG41={"q":q0,"L":length0,"A":area,"h":height,"J":components,
                          "Sigma":surplus,"E":exceptional,"n":width,"Z":zeroes,
                          "P207_margin":scalar-length0,"P208_margin":triple-3*length0,"actual_cycle":False},
                    NG42={"q":3,"K":5,"actual_odd_positions":[0,1,2],"mechanical_positions":mechanical,
                          "wrong_interval":[3,5],"missed_position":2},
                    source167={"accelerated_source_residues":residues,"critical_word":word,
                               "trailing_zero_lifts":trailing,"first_coefficient_failure_length":first_failure,
                               "infinite_safe_stabilization_claimed":False},
                    AB={"word":"111011100","Q":q,"B":str(b),"denominator":512,"fixed_point":str(fixed)},
                    negative_cycles=negative_cycles,cycle_exclusion_claimed=False)


@lru_cache(maxsize=1)
def reconstructed_payloads() -> tuple[str,...]:
    # Immutable internal values, with no artifact-derived bounds or seeds.
    return tuple(canonical(builder()) for builder in
                 (rebuild_bellman,rebuild_safety,rebuild_cloud,rebuild_regressions))


def load_payload(path: Path) -> dict:
    def unique_pairs(pairs):
        value = {}
        for key,item in pairs:
            require(key not in value, f"duplicate JSON key in {path.name}: {key}")
            value[key] = item
        return value
    try:
        value = json.loads(path.read_text(encoding="utf-8"),object_pairs_hook=unique_pairs,
                           parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
        require(isinstance(value,dict),f"{path.name} must be an object")
        return value
    except (OSError,UnicodeError,ValueError,RecursionError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def verify(directory: Path) -> dict:
    directory = Path(directory)
    payloads = [load_payload(directory/name) for name in FILES]
    for name,value,expected in zip(FILES,payloads,reconstructed_payloads()):
        try:
            agrees = canonical(value) == expected
        except (TypeError,ValueError,RecursionError) as exc:
            raise VerificationError(f"malformed {name}: {exc}") from exc
        require(agrees,f"{name}: independently reconstructed artifact mismatch")
    try:
        hashes = {name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in FILES}
    except OSError as exc:
        raise VerificationError(f"cannot hash verified artifact: {exc}") from exc
    bellman,minimality,cloud,_ = payloads
    return {"valid":True,"generator_imported":False,"floating_point_used_for_acceptance":False,
            "input_sha256":hashes,"claim_statuses":STATUSES,
            "bellman_rows":bellman["row_count"],"total_tail_count":minimality["total_tail_count"],
            "first_failure_length":minimality["first_failure_length"],
            "failing_pairs_at_length25":minimality["levels"][-1]["failing_pair_count"],
            "cloud_rows":cloud["row_count"],"cloud_transitions":cloud["transition_count"],
            "uses_X02_in_new_reduction":False,"H112_proved":False,"proves_collatz":False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir",type=Path,default=ROOT/"artifacts")
    parser.add_argument("--output",type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except VerificationError as exc:
        result = {"valid":False,"error":str(exc),"proves_collatz":False}
    encoded = json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(encoded,encoding="utf-8")
    print(encoded,end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
