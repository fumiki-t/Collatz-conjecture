# AI research guide

This is the operational entry point for an AI agent continuing the repository.
The Collatz conjecture remains `OPEN`; no finite search in this repository is a
proof of the conjecture. Phase 32's triple-hit/full-cofactor audit is the
latest research layer.

## Read in this order

1. [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md) — conventions, global
   branch map, Phase 1–32 evidence boundaries, and current obligations.
2. [`STATUS.md`](STATUS.md) — current mathematical state.
3. [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md) — exact claim labels and dependencies.
4. [`ROADMAP.md`](ROADMAP.md) — prioritized proof obligations and fast
   falsification tests.
5. [`FAILED_APPROACHES.md`](FAILED_APPROACHES.md) — shortcuts not to rediscover.
6. [`../PHASE32_RUN_RESULTS.md`](../PHASE32_RUN_RESULTS.md), then its inputs;
   use the Phase 31 records for the immediately preceding layer:
   [`../PHASE30_RUN_RESULTS.md`](../PHASE30_RUN_RESULTS.md),
   [`../PHASE29_RUN_RESULTS.md`](../PHASE29_RUN_RESULTS.md),
   [`../PHASE28_RUN_RESULTS.md`](../PHASE28_RUN_RESULTS.md),
   [`../PHASE27_RUN_RESULTS.md`](../PHASE27_RUN_RESULTS.md),
   [`../PHASE26_RUN_RESULTS.md`](../PHASE26_RUN_RESULTS.md),
   [`../PHASE25_RUN_RESULTS.md`](../PHASE25_RUN_RESULTS.md),
   [`../PHASE24_RUN_RESULTS.md`](../PHASE24_RUN_RESULTS.md),
   [`../PHASE23_RUN_RESULTS.md`](../PHASE23_RUN_RESULTS.md),
   [`../PHASE22_RUN_RESULTS.md`](../PHASE22_RUN_RESULTS.md),
   [`../PHASE21_RUN_RESULTS.md`](../PHASE21_RUN_RESULTS.md),
   [`../PHASE20_RUN_RESULTS.md`](../PHASE20_RUN_RESULTS.md),
   [`../PHASE19_RUN_RESULTS.md`](../PHASE19_RUN_RESULTS.md),
   [`../PHASE18_RUN_RESULTS.md`](../PHASE18_RUN_RESULTS.md),
   [`../PHASE17_RUN_RESULTS.md`](../PHASE17_RUN_RESULTS.md),
   [`../PHASE16_RUN_RESULTS.md`](../PHASE16_RUN_RESULTS.md),
   [`../PHASE15B_RUN_RESULTS.md`](../PHASE15B_RUN_RESULTS.md),
   [`../PHASE15_RUN_RESULTS.md`](../PHASE15_RUN_RESULTS.md),
   [`../PHASE14_RUN_RESULTS.md`](../PHASE14_RUN_RESULTS.md),
   [`../PHASE13_RUN_RESULTS.md`](../PHASE13_RUN_RESULTS.md),
   [`../PHASE12_RUN_RESULTS.md`](../PHASE12_RUN_RESULTS.md), the accompanying
   [`../research/audits/garcia-tal-phase12/REPORT.md`](../research/audits/garcia-tal-phase12/REPORT.md),
   [`../PHASE11_RUN_RESULTS.md`](../PHASE11_RUN_RESULTS.md), and the earlier
   inputs
   [`../PHASE10_RUN_RESULTS.md`](../PHASE10_RUN_RESULTS.md),
   [`../BRANCH_POINT_RUN_RESULTS.md`](../BRANCH_POINT_RUN_RESULTS.md), and
   [`../TWO_TAIL_RUN_RESULTS.md`](../TWO_TAIL_RUN_RESULTS.md).
7. [`../AGENTS.md`](../AGENTS.md) — mandatory exact-arithmetic and proof-claim
   protocol.

Run this before changing research code:

```bash
.venv/bin/python scripts/research_health.py
```

It checks navigation freshness, public Markdown links/private paths,
claim-label uniqueness, tracked artifact hashes, active claim statuses, and
the latest supplemental verifier boundary.
From a clean acceptance worktree use `--strict`; this additionally rejects
untracked files under `artifacts/`. Existing local exploratory files are
reported as warnings in non-strict mode so they are not silently confused with
manifested evidence.

Machine-readable entry points are in [`../research/registry.json`](../research/registry.json)
and [`../research/README.md`](../research/README.md). The registry is checked
against the claims ledger and points to scoped context packs for the active
obligations, including H54, H70/H72, H89, H133, and H141. The closed H147 pack
is retained as a handoff record. `research/claims-index.json` is regenerated from the ledger for efficient
AI lookup; it is not edited independently. The registry is an operational
index, not a duplicate theorem source.

## Current dependency map

```mermaid
flowchart TD
    E01["E01 exact affine cylinders"] --> P54["P54 critical-prefix reduction"]
    P54 --> H54["H54 eventual M greater than Hq"]
    H54 --> Goal["Least-counterexample route"]

    X02["X02 external lower bound"] --> E11["E11 q0 and contact certificate"]
    E11 --> P60["P60 near-diagonal endpoint"]
    P60 --> P63["P63 single gap residue"]
    P63 --> C04["C04 exclude q0 residue"]
    P63 --> P64["P64 renewal barrier"]
    P64 --> C05["C05 long-safe pair spacing"]
    P66["P66 exact branch-point lemma"] --> P67["P67 thirty q0 branch cases"]
    P63 --> P67
    P64 --> P67
    P67 --> C05
    P67 --> P68["P68 exact finite-horizon state"]
    P68 --> C05

    P69["P69 counterexample trichotomy"] --> Cycle["Exclude nontrivial cycles"]
    P69 --> P72["P72 odd-orbit packing"]
    P72 --> P73["P73 excludes all-contact word"]
    EXT07["EXT07 external interval sparsity"] --> P74["P74 permanent-safe reduction"]
    P74 --> P75["P75 summable defect strengthening"]
    P72 --> P75
    P75 --> H72["H72 positivity or height obstruction"]
    P76["P76 real and 2-adic shadows"] --> H72
    P77["P77 renewal prefix code"] --> P78["P78 pressure bounds"]
    P78 --> P80["P80 conditional anti-concentration"]
    P79["P79 threshold and valuation transfer"] --> P80
    P80 --> H72
    P81["P81 exact coalescent rewrite"] --> P82["P82 least-source irreducibility"]
    P82 --> H72
    P83["P83 run-sensitive thresholds"] --> H72
    P84["P84 block decrement"] --> H72
    P85["P85 eventual shadow height"] --> H72
    P86["P86 cross-Q surplus dominance"] --> H72
    P87["P87 strict-valley suffix"] --> P86
    P88["P88 gap-{1,2} injectivity"] --> H72
    P89["P89 ancestral minimality"] --> H89["H89 eventual Mstar barrier"]
    P91["P91 cross-Q prefix carry"] --> H89
    P92["P92 uniform cylinder dominance"] --> H89
    P95["P95 shifted jump class"] --> H89
    H89 --> P90["P90 repaired two-case implication"]
    P90 --> Goal
    P96["P96 3-adic endpoint measure"] --> H72
    NG25["NG25 same-Q incompleteness"] --> H72
    NG26["NG26 unsafe-target witness"] --> H72
    NG27["NG27 gain-four witness"] --> H89
    P97["P97 signed carry bounds"] --> H89
    P98["P98 same-Q geodesic criterion"] --> H104["H104 exclude G270"]
    P104["P104 270 dichotomy"] --> H104
    P104 --> H105["H105 exclude H270"]
    P105["P105 exponent pressure"] --> NG29["NG29 Haar ceiling"]
    NG29 --> H104
    P107["P107 sign-pure beta bound"] --> H72
    P108["P108 finite-state Type I/II"] --> H72
    P109["P109 mixed formal survivor"] --> H72
    P111["P111 source lifts"] --> H72
    NG30["NG30 one-switch failure"] --> H72
    P112["P112 affine-or-valley"] --> H104
    P112 --> H105
    P113["P113 critical affine moments"] --> NG31["NG31 finite-mean failure"]
    NG31 --> H72
    P114["P114 strip occupation"] --> H72
    P115["P115 exact source lifts"] --> H112["H112 nonzero lifts"]
    P116["P116 periodic residue growth"] --> H112
    EXT08["EXT08 critical liminf density"] --> P119["P119 symbolic class exclusions"]
    P117["P117 discrepancy barrier"] --> P121["P121 unbounded balance"]
    P119 --> H72
    P121 --> H72
    P123["P123 no quasi-Sturmian tail"] --> P124["P124 excess tends to infinity"]
    P124 --> H112
    P125["P125 exact parity LCP"] --> P126["P126 repeat-height bound"]
    P126 --> P127["P127 linear factor complexity"]
    EXT08 --> P128["P128 critical limsup slope"]
    P126 --> P128
    P126 --> P132["P132 H89 repeat certificate"]
    P132 --> H89
    P141["P141 corrected defect area"] --> P142["P142 conditional area repeat"]
    P142 --> H141["H141 defect/source bridge"]
    P142 --> H89
    P144["P144 cycle edit area"] --> P145["P145 cycle separation"]
    P145 --> H141
    P145 --> H133["H133 all-area cycle obstruction"]
    P147["P147 sparse arc divisor"] --> P149["P149 coprime area >= 3"]
    P148["P148 low-area shapes"] --> P149
    P151["P151 Hamming support"] --> P156["P156 all-gcd reduced profile"]
    P149 --> P156
    P154["P154 resonant resultant"] --> P155["P155 seven-grid exclusion"]
    P155 --> P158["P158 critical area at least 6"]
    P156 --> P157["P157 all-gcd cycle separation"]
    P157 --> P158
    P157 --> P159["P159 noncritical area above 100000"]
    P158 --> H147["H147 closed area-three obligation"]
    P158 --> H133
    P159 --> H133
    NG34["NG34 paired-arc failure"] --> H133
    NG35["NG35 area-six scalar failure"] --> H133
    P158 --> P162["P162 polynomial-gap area"]
    P159 --> P163["P163 noncritical gap"]
    P162 --> P164["P164 global area dispersion"]
    P163 --> P164
    EXT17["EXT17 Matveev input"] --> P164
    P164 --> P165["P165 support dispersion"]
    P165 --> H133
    NG36["NG36 rotation mismatch"] --> H133
    P165 --> P166["P166 exact transport"]
    P166 --> P168["P168 sharp area constant"]
    P167["P167 level descent"] --> P168
    P168 --> P169["P169 branch constants"]
    P168 --> P170["P170 rigidity"]
    P167 --> P171["P171 multilevel polynomial"]
    P170 --> H172["H172 transport resonance"]
    P171 --> H172
    H172 --> H133
    NG37["NG37 finite equality"] --> H172
    NG38["NG38 endpoint correction"] --> H172
    P185["P185 static extraction"] --> P186["P186 double-hit bound"]
    P186 --> P187["P187 area constant"]
    P187 --> P189["P189 repaired rigidity"]
    P190["P190 grid identity"] --> H172
    P189 --> H172
    NG40["NG40 residual-density obstruction"] --> H172
    P191["P191 all-radius pruning"] --> P192["P192 radius double-hit"]
    P192 --> P193["P193 repaired area limit"]
    P193 --> P194["P194 approximate grid"]
    P194 --> H172
    P127 --> H112
    H112 --> H72
    NG28["NG28 negative carry"] --> H89
    NG24["NG24 left-congruence failure"] --> H72
    NG23["NG23 raw Haar failure"] --> H72
    NG22["NG22 formal 2-adic obstruction"] --> H72
    P69 --> P70["P70 renewal-ladder implication"]
    H70["H70 eventual dropping-safe spacing"] --> P70
    P71["P71 exact pair-cylinder intervals"] --> H70
```

Arrows mean “is an input to,” not “has been proved unconditionally.” X02 is
external evidence; P54, P60, P63, P64, and P67 are conditional. P68 is an
unconditional finite-horizon theorem. P69--P73 and P76 are internal theorems
or exact reductions. EXT07 is external; P74/P75 are conditional on it.
P77--P79, P81--P89, P91--P102, P104--P109, P111--P118, P120, P122, P125--P127,
P129--P138, P140, P141, P144, P145, P147--P199 are
exact renewal/ancestral/critical/finite-state/word theorems; P80, P90, P103,
P110, P119, P121, P123, P124, P128, P142, P143, and P146 are conditional implications.
NG22 is a formal/2-adic countermodel, NG23 is a raw-volume failure, NG24 is a
left-congruence failure, NG25--NG31 delimit the finite ancestral/affine
search language, NG32 is the finite critical mechanical boundary failure, and
NG33 is the generic seven-point area-three exponent failure; NG34 is the exact
failure of a universal paired q/L threshold; NG35 is the exact critical
area-six scalar-coefficient failure; NG36 is the positive-rational rotation
alignment failure; NG37/NG38 are the finite-strictness and endpoint-correction
failures, NG39 preserves mechanical span, and NG40 blocks the obsolete
single-radius grid promotion. P191--P194 bypass NG40 only through the
all-fixed-`R` family and only yield the grid conclusion at sharp equality.
H147 is closed by P158. H54, H70, H72,
H89, H104, H105, H112, H133, H141, H172, C04, C05, every uneliminated P69 branch,
and the Collatz conjecture remain open.

## Active proof obligations

| ID | Status | Exact missing step | Fastest useful next test |
|---|---|---|---|
| H54 | `OPEN` | Prove `M(K_q-1)>H_q` eventually | Attack any proposed `M(k)` inequality with all stored record failures and mandatory adversarial families |
| H89 | `OPEN` | Prove `M_star(K_q-1)>H_q` eventually and certify the finite first-crossing remainder | Combine P151--P153 support locations with signed P91/P97 carry and P132; the q0 support count alone leaves a wide interval |
| H104 | `OPEN` | Exclude every positive ordinary-source all-prefix same-Q geodesic G270 word | Retain fixed source plus affine/carry state; reject contact/all-contact/Haar-only shortcuts with NG17/P73/NG29 |
| H105 | `OPEN` | Empty the H270 box `N<q/270`, `X<q/135`, `Z<2q/135` | Use a two-sided exact state and keep the periodic branch separate; test NG19 and NG24--NG29 |
| H70 | `OPEN` | Prove the eventual dropping-safe pair spacing used by P70 | Reproduce the six E18 failures; reject height-free rules with NG20 and every lossy merge with NG19 |
| H72 | `OPEN` | Prove one of P80's ordinary canonical-residue bounds, eventual P86 surplus reducibility, H112, or an equivalent positivity/height obstruction extending P72/P75--P132 | Reject NG21--NG31 and source 167, require a prefix-complete closed state model, and retain P115 ordinary-source lift stabilization; test on E20/E22--E26/E30--E33, the `{1,2}` core, and all mandatory families |
| H112 | `OPEN` | Force infinitely many nonzero source lifts on every infinite safe all-prefix same-Q-geodesic branch | Connect P125--P131 repeat/right-special structure to exact lift/carry/ordinary height; reject bounded zero-run rules on source 167 and finite-rate inference on E33 |
| H133 | `OPEN` | Exclude every cycle after P196's area growth and P197--P199 full-cofactor reduction | Cover both negative cycles, E43--E45, NG34--NG40, all Phase 28--32 profiles, H200, and the above-frontier regime first |
| H141 | `OPEN` | Turn defect geometry into an ordinary-source/carry obstruction for H89 or P194 into H133 rejection | Test one exact weighted inequality on NG32--NG40, concentrated/diffuse defects, both negative cycles, and E37--E44 before extending q |
| H172 | `OPEN` | Combine P194's `o(L)`-defect grid with P197's full cofactor and preserve both rotations | Allow adversarial bad-start placement; falsify first on NG34--NG40 and E43--E45 |
| C04 | `OPEN` | Exclude `rho=[B*3^(-q0)]_D` from the q0 near box | Preserve affine constant, carries, and both canonical residue ranges |
| C05 | `OPEN` | Prove `Delta_(K0-1)(2^72)>W` | For its weaker q0-specific consequence, use the 30 branch cases; reject any state that forgets inherited surplus or either tail residue |
| C03 | `OPEN` | Rank arbitrary contracting `{A,B}*` interleavings | Test BBA and all near-critical `A^rB^s` records first |

The current best direct target is not a larger raw enumeration. It is a sound
cross-cylinder merge extending P71's exact per-cylinder interval state

```text
(h, a, odd normalized gap, inherited coefficient surplus,
 left tail residue state, right tail residue state).
```

NG19 supplies exact safe/non-safe collisions for every fixed shortening
`y mod 2^b`, `b<12`; NG20 supplies a universal height-free gap-4 pair. Any
next prototype must preserve ordinary height and either separate those
histories, retain equivalent carry information, or prove a sound dominance
rule before scaling it.

## Experiment contract

Every new experiment should state, before a large run:

1. claim ID and exact quantifiers;
2. why success would advance H54, H70, H72, H133, H141, C04, or C05;
3. smallest adversarial falsification range;
4. exact acceptance arithmetic;
5. logically independent reconstruction method;
6. stop criterion and artifact size policy;
7. “What this result does not prove.”

Record these fields in `research/experiments/<experiment-id>.json` using
`research/schemas/experiment.schema.json`. An accepted manifest must name all
artifacts and preserve the recorded manifest hash. Phase 32 provides the
latest accepted example.

Use `VERIFIED_FINITE` for bounded profiles even when every tested row passes.
Use `CONDITIONAL` when a least-counterexample or external premise is retained.
Do not introduce a new claim ID for a renamed copy of an existing obligation.

## High-value next experiments

- Search for a quotient/carry dominance relation merging P71 cylinders while
  retaining ordinary height and explicitly separating every NG19 collision.
- Attack H70 separately from the other two P69 branches; do not describe a
  renewal-ladder result as a full counterexample exclusion.
- For H141, optimize a stated weighted correction/source inequality against
  concentrated defects, NG32, and P152/P153's nonempty q0 support interval
  before any larger critical/profile scan.
- For H133/H172, test H200's bounded area-six grid first, then P194's
  arbitrary-area approximate grid. Rebuild NG34--NG40, E43--E45, and the
  Phase 28--32 synthetic profiles. Seek a
  low-denominator full-`D` resultant that tolerates adversarial `o(L)` bad
  starts, and separately test what reduces above-frontier families to the
  sharp regime. Keep span, endpoint term, the all-fixed-`R` quantifier, and
  both rotations. Do not infer actual maximum-state saturation from the
  `n_cyc` proxy.
- Attack H72 through positive ordinary-integrality, effective reduced
  shadow-height/gcd, P79's valuation-conditioned successor congruences, or a
  P86 cross-Q surplus state retaining the carries lost in NG24.
  Mod-6 density is blocked by NG21, analytic/general-2-adic coherence by NG22,
  raw local-volume counting by NG23, and endpoint-only prefix propagation by
  NG24; same-Q or safe-target-only pruning is blocked by NG25/NG26, and
  bounded same-Q gain by NG27, positive carry by NG28, and coefficient-only
  unbounded Haar pressure by NG29, a one-switch SCC normal form by NG30, and
  finite-mean affine averaging by NG31.
- Attack H112 with P115's exact lift digit plus signed carry and ordinary
  height. Source 167 must reject any rule based only on a bounded terminal
  zero-lift run; P116 already handles ultimately periodic noncycles. P127/
  P131 may be used only through a proved implication from repeat/right-special
  structure to a lift, carry, or ordinary-height event.
- Attack H104 and H105 as separate obligations. A proof of one branch does not
  close P104, and neither branch applies to repeated periodic values.
- Attack H89 only with a proposed all-depth P91/P92/P95/P97/P132 recurrence. E25's
  `M_star(210)>5000000` and P96's 3-adic complement are not asymptotic or
  pointwise substitutes; E33 shows that repeat rejection alone leaves most
  bounded critical words alive.
- Derive exact lower bounds on the ordinary size of a pair of inverse-parity
  residues from their odd normalized gap and common-prefix affine constant.
- Test whether any proposed branch potential composes across the record
  witnesses at `h=2,3,6,7,10,19` before attempting q0.
- Connect the gap residue `rho` to Christoffel/rotation extremality only after
  writing the exact external theorem and the repository-specific translation
  as separate lemmas.
- Continue H54 only with a proposed asymptotic inequality, never by extending
  Phase 1–5 depth for its own sake.

## Known traps

- Contact density without endpoint residues: refuted by NG17.
- Strict spacing growth at every depth: refuted by NG18.
- A fixed dictionary of dangerous words or shadow centers: refuted by
  NG04/NG09/NG15 and `A^rB^s`.
- A fixed `b<L` tail-residue window for an L-step safety decision: refuted at
  `L=12` by NG19.
- Height-free dropping-safe spacing greater than 4: refuted for every `k>=3`
  by NG20.
- Contradiction from only summable octave defects, `h_j>1`, divergent
  companion reciprocals, and an odd 2-adic source: refuted by NG22.
- Coalescent endpoint equivalence as a two-sided concatenation congruence:
  refuted by NG24; only common right suffixes preserve it.
- A packing exponent below `1/9` from distinctness and coprimality modulo six
  alone: refuted by NG21's abstract saturator, which is not a Collatz orbit.
- Replacing deterministic least positive representatives by Haar cylinder
  volume or discarding one lattice error per address: refuted by NG23.
- Positive same-Q carry: refuted by NG28 at Q=26 even though every pair through
  E27's Q=17 cutoff is positive.
- Unbounded coefficient-only predecessor Haar pressure: refuted by NG29; the
  optimistic envelope reaches its threshold below normalized count 360.469.
- Treating finite disappearance of safe pairs below a bound as a larger-H
  spacing theorem.
- Treating formal rational cycles as positive integral Collatz cycles.
- Treating separate source files as proof of logical independence.

## Completion checklist

Before handing off a meaningful result:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py --strict
git diff --check
```

Update `STATUS`, `CLAIMS_LEDGER`, `RESEARCH_HISTORY`, `FAILED_APPROACHES`,
`ROADMAP`, `HANDOFF`, and the relevant result report. Preserve every old
counterexample and keep `proves_collatz=false` unless the emergency proof audit
has actually completed.
