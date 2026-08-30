# Research handoff

Read [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md) first for the complete
map. This file is the compact ten-minute orientation for a technically
competent researcher or AI continuing the project without the original chat.

## 1. Safety boundary

The Collatz conjecture remains `OPEN`. This repository contains exact finite
certificates, some internally checked algebra, external theorems, failed
mechanisms, and conjectural directions. Keep those categories separate using
the taxonomy in [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md) and the protocol in
[`../AGENTS.md`](../AGENTS.md).

Do not edit generated artifacts manually. Do not infer an eventual theorem
from finite coverage. Any proof candidate moves to an
`audit/proof-candidate-*` branch and receives adversarial human review before
README language changes.

## 2. Mathematical setup

The shortcut map is

\[
T(n)=n/2\quad(n\text{ even}),\qquad
T(n)=(3n+1)/2\quad(n\text{ odd}).
\]

For a parity prefix of length `k` with `q_k` odd steps,

\[
T^k(n)=\frac{3^{q_k}n+B_k}{2^k}.
\]

A prefix is coefficient-safe when `3^{q_j} >= 2^j` for every prefix
`1 <= j <= k`. Define `M(k)` as the least positive integer at least 2 with a
coefficient-safe prefix of length `k`.

For each `q`, Phase 6 defines

\[
K_q=\lceil q\log_2 3\rceil,\qquad
H_q=B_q^{\max}/(2^{K_q}-3^q),
\]

with `B_q^max` given explicitly in the Phase 6 result and verifier.

## 3. What the twenty-five phases established

- Phase 1–2 built exact affine cylinders and an independent verifier. The
  depth-26 frontier has 1,037,374 unresolved nodes. A short-period dictionary
  leaves 123,908 unexplained; representative 27 is the smallest residual.
- Phase 3 added ternary refinement and exact reverse merges. It closes 43,198
  records but leaves 79,350 mixed `OPEN` records. Bounded refinement alone is
  not subcritical in the tested range.
- Phase 4 used the strongly sufficient section `2 mod 9` and an exact
  prefix-free first-return code. Refill constants `1,5,21` defeat the tested
  finite rankings; 23,785 records remain open.
- Phase 5 used `{1,11,20,26} mod 27`, where complement acyclicity bounds first
  returns. It found 52 templates, 108 labeled simple cycles, and four
  noncontracting cycles. Fixed four-shadow completeness fails.
- The adversarial words `A=11101`, `B=1100`, and
  `W=AB=111011100` matter: `W` has affine map `(729x+817)/512` and fixed point
  `-817/217`. Exact `A^rB^s` records approach multiplier one; the universal
  arbitrary-closeness conclusion uses an external density theorem.
- Phase 6 derived the current critical-prefix barrier and added exact lower
  bound certificates for `M(k)`.
- Phase 7 derives exact boundary-defect contact pressure. With external
  `N>2075*2^60` and Denjoy--Koksma separated, it certifies the first crossing
  `(q0,K0)`, 31,327,720,462 contacts, and 889,748,829 genuine `h=12` pairs.
  Its 87,015 exact macros contain immediate counterexamples to uniform descent,
  compulsory four-word decomposition, and local unrealizability.
- Phase 8 proves C02 for every contracting ordered `A^rB^s` realization,
  localizes almost all conditional q0 contacts to the first octave, and leaves
  arbitrary contracting `{A,B}*` interleavings C03 `OPEN`.
- Phase 9 strengthens contact and short-return counts, confines the conditional
  endpoint to `0<=d<=4,142,380,786` with `X=7 or 19 mod 36`, and creates a
  large reverse coefficient barrier. Contact-only closure is refuted; C04 is
  the remaining two-sided residue obstruction.
- Phase 10 reduces C04 to one gap residue `rho`, proves `4|rho`, and derives a
  conditional renewal barrier: every point in `[N,N+W]` is coefficient-safe
  through `K0-1=114,208,327,603`. The exact finite spacing target C05 remains
  `OPEN`. P65 proves only a formal rational-cycle minimum, not an integer cycle.
- The Phase 10 branch supplement proves P66 and conditionally reduces every
  positive q0 gap to 30 cases `2<=v2(d)<=31`. E16's finite branch profile peaks
  at joint-safe depth 213 for `h=7`; it supplies falsification data, not a q0
  bound.
- The two-tail supplement proves P68: the next L steps are exactly determined
  by `(h,a,u,orientation,y mod 2^L)`. E17 finds, for every `b<12`, a minimal
  safe/non-safe collision when that residue is shortened to b bits. Thus the
  literal fixed-window compression NG19 is refuted; C05 remains open.
- Phase 11 proves the unconditional P69 counterexample trichotomy. Its
  finite-crossing branch is an infinite ladder of `3 mod 4` tail minima with
  exact height and gap bounds. P70 reduces that branch to H70, an eventual
  dropping-safe pair spacing inequality. E18 finds exactly six failures through
  q=4961, while NG20 proves height-free spacing impossible. P71 closes exact
  affine margins inside each fixed pair cylinder but not across cylinders.
- Phase 12 proves P72 for P69's infinite-safe-tail branch: exact normalized
  odd-orbit growth is at most `j^(1/9)` up to constants, and
  `a_i>(8/9-epsilon)log2(i)` on a density-one index set. P73 rules out the
  all-contact critical mechanical word. NG21 shows the `1/9` exponent cannot
  be improved from distinctness and mod-6 packing alone; H72 remains open.
- The Garcia--Tal audit isolates EXT07 as an external interval-sparsity input.
  Assuming it, P74 gives reciprocal summability and a permanent-safe odd tail
  minimum for every nonperiodic positive orbit, so the renewal ladder is
  conditionally bypassed rather than H70 being proved. P75 strengthens octave
  defects, and P76 gives real/2-adic moving shadows. NG22 shows these analytic
  conditions plus a general odd 2-adic source are still consistent; positivity
  and effective ordinary height are now the H72 boundary.
- Phase 13 proves the renewal first-upcrossing code P77, exact weighted
  pressure bounds P78, and the `13/9` threshold plus valuation-conditioned
  positive-source transfer P79. P80 isolates two sufficient but unproved
  canonical-residue anti-concentration estimates. NG23 refutes substituting
  raw Haar volume for deterministic least positive representatives at the
  minimum word `u=1,H=2`; H72 remains open.
- Phase 14 proves the exact coalescent rewrite criterion P81 and reduces any
  least positive permanent-safe counterexample source to a P81-irreducible
  renewal address (P82). P83 sharpens block thresholds, P84 proves a positive
  decrement at every nontrivial renewal block, and P85 gives eventual
  rational-shadow denominator/gcd bounds once the octave defect is positive.
  E23 exhausts total odd count `Q<=13`: 30,084 addresses form 24,197 endpoint
  classes and 5,949 positive downward rewrite pairs. NG24 refutes left
  congruence, so endpoint classes alone do not form a closed prefix transfer.
- Phase 15 proves P86 surplus dominance across different odd counts and P87
  strict-valley extraction from unsafe coalescent targets. E24 exhausts every
  safe target and competitor through Q=17 and reproduces 12, 90, and 233 new
  valley reductions at Q=15,16,17. NG25/NG26 refute same-Q and safe-target
  completeness. P88 proves finite endpoint injectivity for `{1,2}` odd-gap
  words; all 32,596 such safe Q=17 words survive `Q_b<=Q_d` dominance, so H72
  remains open.
- Phase 15B proves P89 ancestral minimality for every safe prefix of a least
  counterexample. P91/P92 give cross-Q prefix carries and uniform-cylinder
  dominance; P93--P96 give finite renewal decomposition, Beatty support,
  shifted jump classes, and a non-pointwise 3-adic measure bound. E25 proves
  only `M_star(210)>5000000`; E26 is bounded at Q=17/19; NG27 records a
  gain-four compression witness. P90's eventual H89 route is conditional and
  H89 remains open.
- Phase 16 repairs the q=1 correction boundary, proves P97--P102 carry,
  normalized-geodesic, local-merge, mod-72 packing, and finite-crossing
  dichotomy results, and retains P103 as a conditional q0 consequence. For
  distinct odd values and `N>=100000`, G250 is all-prefix same-Q geodesic and
  H250 has `N<q/250`, `X<q/125`, `Z<2q/125`. H97 and H98 remain open. NG28's
  exact Q=26 carry -3 witness forbids positive-carry recurrences; E27 is finite
  through Q=17.
- Phase 17 enumerates all 23 supercritical accelerated inverse words through
  r=4 and combines their endpoint exclusions with the odd-even-even rule in a
  mod-648 upper envelope. P104 sharpens the distinct-odd finite-crossing split:
  G270 is all-prefix same-Q geodesic, while H270 has `N<q/270`, `X<q/135`,
  and `Z<2q/135`. P105 proves an exact exponent-code pressure identity; P106
  gives an 11-word suffix-decodable r=4 code. NG29 caps only the
  coefficient-only summed-Haar envelope. H104/H105 remain open, and E28/E29
  are finite.
- Phase 18 proves the exact trichotomy for any supplied closed finite affine
  graph. P107/P108 handle sign-pure SCCs; P109 constructs formal balanced
  survivors in mixed SCCs; P111 makes eventual zero source lifts necessary
  for a fixed positive ordinary source. P110 excludes only the canonical
  balanced itinerary conditionally on EXT07. NG30 refutes a one-switch SCC
  normal form. E30 finds no current prefix-complete closed finite model for the
  full H72 language, so H72 remains open.
- Phase 19 proves the affine-or-valley predecessor alternative, exact
  source/endpoint tilted martingales, and P72's fixed-strip occupation bound.
  The endpoint-tilted affine correction has infinite first moment (NG31), so
  mean-small affine pressure is invalid. P115 characterizes a fixed positive
  source by eventual zero accelerated lifts, while P116 removes ultimately
  periodic noncycles. Source 167 has eleven terminal zero lifts and then
  crosses coefficient safety, so H112 and H72 remain open.
- Phase 20 proves the internal P72 discrepancy-envelope barrier, the
  transcendence application for `ln(2)/ln(3)`, bounded-balance frequency, and
  morphic-Sturmian output discrepancy. Conditionally on EXT08 and external
  word theorems, automatic, primitive substitutive, bounded-balance, and
  quasi-Sturmian parity tails are excluded and `p(n)-n -> infinity` is
  necessary. E32 is finite only; H112 and H72 remain open.
- Phase 21 proves exact integer parity separation and a strict repeated-factor
  height inequality. Consequently every positive nonperiodic integer orbit
  has unconditional linear factor complexity with slope at least
  `1/log2(3/2)`; EXT08 conditionally raises a limsup slope. P132 rejects
  160,429 of 502,523 critical words through `Q=17`, but most survive, so H89,
  H112, and H72 remain open.
- Phase 22 attacks the separate positive-cycle branch. P133/P134 give a
  minimum-cycle coefficient valley and G170/H170 split. P135--P138 convert
  coprime exponent classes into residue-indexed profiles, slope-root and
  resultant conditions, and exclude area zero and one. P139 conditionally
  adds the EXT15 Christoffel gap; P140 is a weaker noncoprime condition. E34
  has zero nontrivial integral cycles in its complete `q<=8` scope and zero
  combined survivors among area-at-most-two profiles through `q<=22`, but
  H133 and the full positive-cycle branch remain open.
- Phase 23 links critical and cycle words by Christoffel defect area. NG32
  repairs the supplied finite mechanical factor bound at the smallest witness
  `q=4,c_q=1101100,n=2`; P141 keeps the necessary terminal `+1`. P142 gives a
  conditional area/repetition inequality, while P144/P145 give exact coprime
  cycle edit, triangular-height, complexity, and positive-state separation
  conditions. E35 is bounded and H141/H89/H133 remain open.
- Phase 24 proves the sparse circular-arc divisor and excludes every coprime
  area-two positive cycle profile, so a hypothetical nontrivial coprime cycle
  has area at least three. E36's area-three ratios are finite only; NG33 blocks
  generic seven-point cardinality and H147/H133 remain open.
- Phase 25 proves support-sensitive Hamming factor bounds and conditionally
  certifies `n_q0=73`, but the q0 support lower/upper bounds remain far apart.
  NG34 stores the exact `q=63322` failure of a universal paired q/L arc gap.
  P154/P155 exclude the exact critical seven-grid area-three family using a
  low-degree resultant and EXT05; no theorem controls nearby grids, all area
  three, arbitrary area, or noncoprime slopes.

The chronological details and exact counts are in
[`../RESEARCH_HISTORY.md`](../RESEARCH_HISTORY.md).

## 4. Current strongest route

P54 is `CONDITIONAL`. If `N` is a least positive counterexample and its affine
coefficient first crosses below one at the `q`-barrier, the independently
audited algebra gives

\[
M(K_q-1)\le N\le H_q.
\]

Therefore `M(K_q-1) > H_q` excludes that first-crossing configuration. If the
inequality holds eventually and all remaining finite cases are checked, this
route would prove the original conjecture.

What is already finite and exact:

- 37 `H_q` records through `q=200000`; last record
  `q=190537`, `K_q=301994`, `floor(H_q)=710220447737`;
- five independently checked certificates covering every `94 <= q <= 4960`;
- direct exact determination of `M(k)` through `k=223`;
- early barrier failures `(q,N)=(17,27),(29,27),(41,703)`.

What is missing: a `q`-uniform high-correction/least-positive-residue
separation strong enough to imply an eventual lower bound for `M(k)`.

Phase 15B adds a parallel, stronger-state route:

```text
P89 ancestral minimality
  -> P91/P92/P95 exact carry/dominance language
  -> H89 eventual M_star(K_q-1)>H_q (OPEN)
  -> P90 plus a finite remainder excludes both crossing cases.
```

E25 is a depth-210 finite datum, not the missing eventual theorem.

Phase 17 gives the strongest finite-crossing split inside this route:

```text
distinct odd values -> G270 all-prefix geodesic (H104 OPEN)
                    or H270 ultra-low source/endpoint box (H105 OPEN)
repeated values     -> P102 factor-3 boundary; cycle branch remains separate.
```

The closest q0 subroute is now:

```text
P63 single gap residue
  -> P64 two long-safe endpoints
  -> P66/P67 thirty first-divergence cases
  -> P68 exact finite-horizon two-tail state
  -> C05 two-tail spacing certificate (OPEN).
```

The logically exhaustive Phase 11 route is:

```text
P69 counterexample trichotomy
  -> exclude nontrivial cycles (OPEN)
  -> EXT07/P74 conditional permanent-safe reduction
  -> P72/P75/P76/P77/P78/P79
  -> P80 canonical-residue anti-concentration (CONDITIONAL)
  -> P81/P82 least-source irreducibility reduction
  -> P83/P84/P85 threshold, decrement, and height constraints
  -> P86/P87 cross-Q surplus and strict-valley reduction
  -> P88/E24 finite {1,2}-gap hard core
  -> P89/P91--P96 ancestral/carry constraints and E25/E26 finite data
  -> P117/P119--P124 parity-complexity filters
  -> P125--P131 unconditional repetition-complexity filters
  -> H72 (OPEN)
  -> H70 eventual dropping-safe spacing via P70 (OPEN).
```

H70 would settle only its third branch through P70, so it must never be described as a
complete proof route by itself.

## 5. Where to work next

Start with [`AI_RESEARCH_GUIDE.md`](AI_RESEARCH_GUIDE.md) and
[`ROADMAP.md`](ROADMAP.md), priority P0/P1. A useful new proposal
should answer all of these before a large computation:

1. What precise inequality about `M(k)`, dropping-safe pair spacing, or
   odd-orbit transition packing is proposed?
2. Why would it dominate the relevant `H_q` height and gap allowance?
3. What is the fastest exact falsification test?
4. Does it survive every mandatory adversarial family?
5. What certificate can an implementation-independent verifier reconstruct?

For H54, H70, H72, H89, H104, or H105, use the scoped pack under
[`context/`](context/README.md). Confirm status against `CLAIMS_LEDGER.md`. Register a large experiment
under `research/experiments/`; `research/registry.json` is the machine-readable
entry point and is audited against the ledger.

Good near-term work includes a P91/P92/P95/P97 recursion aimed at H89 that
incorporates P132 repeat certificates, a cross-Q
carry recursion for P86's endpoint Pareto frontier,
inverse-parity anti-concentration, recursive lower bounds, a cross-cylinder
quotient/carry state extending P71, and a positive ordinary-integrality or
effective shadow-height obstruction extending P75--P85. Start from the stored
NG19 collisions, universal NG20 pair, both NG22 formal 2-adic sources, NG23's
raw-volume obstruction, NG24's left-congruence failure, and the NG25--NG31
cross-Q/unsafe-target witnesses: any proposed merge
must distinguish them or prove a sound dominance relation. Any finite-state
proposal must additionally prove transition closure and retain P115 canonical
source lifts. H112 is the focused same-Q-geodesic subtarget; source 167 must
reject every bounded zero-run surrogate. A complexity-based successor must
map an exact right-special/return-word event to a nonzero lift, signed carry,
or ordinary height; E32/E33's finite profiles alone cannot do so. Certificate
extension is useful when it tests such structure; raw depth extension is
secondary.

## 6. Reproduce and audit

From the repository root:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python verifier/verify_phase10.py \
  --artifact-dir artifacts --output /tmp/collatz_phase10_verifier.json
.venv/bin/python verifier/verify_branch_point.py \
  --artifact-dir artifacts --output /tmp/collatz_branch_verifier.json
.venv/bin/python verifier/verify_two_tail.py \
  --artifact-dir artifacts --output /tmp/collatz_two_tail_verifier.json
.venv/bin/python verifier/verify_phase11.py \
  --artifact-dir artifacts --output /tmp/collatz_phase11_verifier.json
.venv/bin/python verifier/verify_phase12.py \
  --artifact-dir artifacts --output /tmp/collatz_phase12_verifier.json
.venv/bin/python verifier/verify_phase13.py \
  --artifact-dir artifacts --output /tmp/collatz_phase13_verifier.json
.venv/bin/python verifier/verify_phase14.py \
  --artifact-dir artifacts --output /tmp/collatz_phase14_verifier.json
.venv/bin/python verifier/verify_phase17.py \
  --artifact-dir artifacts --write-report /tmp/collatz_phase17_verifier.json
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py
shasum -a 256 artifacts/SHA256SUMS
```

Use `scripts/research_health.py --strict` in a clean acceptance worktree. The
non-strict command deliberately reports local untracked artifacts as warnings
without treating them as accepted evidence.

The current manifest hash is recorded in
[`../PHASE17_RUN_RESULTS.md`](../PHASE17_RUN_RESULTS.md).
For regeneration commands and individual artifact hashes, use the phase result
files linked from [`INDEX.md`](INDEX.md).

Before changing a claim status, read its row in
[`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md), its failure history in
[`FAILED_APPROACHES.md`](FAILED_APPROACHES.md), and any external dependency in
[`LITERATURE.md`](LITERATURE.md).

The current local `scratch/` inventory is superseded by the accepted
Garcia--Tal and Phase 13--17 audits; it is not accepted evidence. No
post-Phase-17 scratch candidate is accepted evidence. See the scratch index in
[`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md#10-scratch-index).

## If you only remember one thing

The current bottleneck is not finite verification, contact density, or the
Phase 17 dichotomy. It is a
rigorous asymptotic link from high affine correction to ordinary height, or a
cross-cylinder spacing theorem. P71 solves exact margins only inside a fixed
finite cylinder; NG19 prevents literal truncation, and NG20 prevents discarding
height. EXT07/P74 conditionally collapses the nonperiodic alternatives to a
permanent-safe tail, but P75/P76 do not exclude it: NG22 satisfies their
analytic consequences at the formal/2-adic level. P77--P79 expose exact
renewal pressure and valuation structure, while NG23 shows Haar volume alone
cannot control an ordinary representative. P81/P82 expose exact downward
coalescence and least-source irreducibility, but NG24 prevents a prefix-closed
endpoint quotient. The remaining distinction is a carry-aware deterministic
positive-height anti-concentration or eventual-reducibility theorem. Collatz
remains open.
