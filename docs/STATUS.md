# Current research status

**Last updated:** 2026-08-28

**Problem status:** `OPEN` — the Collatz conjecture is neither proved nor
disproved by this repository.

For the self-contained Phase 1–15 map, conventions, dependency branches, and
proof obligations, read [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md).

## What is currently proved?

- `VERIFIED_THEOREM`: the exact affine-cylinder identities and the symbolic
  algebra used by the certificate rules can be reconstructed with integer or
  rational arithmetic.
- `VERIFIED_THEOREM`: C02 now proves exact descent for every positive integral
  contracting realization of the ordered family `A^rB^s`, using six internal
  CRT cases and the isolated external gap theorem EXT05.
- `VERIFIED_THEOREM`: P65 proves that `z=B/(2^K-3^q)` is the minimum of the
  formal rational affine cycle of every coefficient-safe first-crossing word,
  and `gcd(B,D)=gcd(d,D)`. It asserts no positive integral cycle.
- `VERIFIED_THEOREM`: P66 proves that two integer trajectories share exactly
  `v2(m-n)` parity steps and then split, with exact transformed odd gap
  `3^a(m-n)/2^h` after their common prefix.
- `VERIFIED_THEOREM`: P68 proves that, after a coefficient-safe common prefix,
  `(h,a,u,orientation,y mod 2^L)` losslessly determines both tails' next `L`
  parity bits and their coefficient-safety decisions over that finite horizon.
- `VERIFIED_THEOREM`: P69 splits every possible counterexample into a
  nontrivial cycle, an infinite coefficient-safe tail, or a finite-crossing
  renewal ladder of increasing `3 mod 4` tail minima with exact height, gap,
  odd-count growth, and formal rational-denominator bounds.
- `VERIFIED_THEOREM`: P70 proves that an eventual dropping-safe pair-spacing
  inequality excludes the renewal-ladder branch; P71 proves exact affine-margin
  interval closure on every fixed pair cylinder.
- `VERIFIED_THEOREM`: P72 proves the exact normalized odd-orbit product and
  mod-6 packing bounds for every nonperiodic infinite coefficient-safe tail.
  Its octave defect satisfies
  `a_i>(8/9-epsilon)log2(i)` on a density-one set for every epsilon>0.
- `VERIFIED_THEOREM`: P73 rules out the single all-contact critical mechanical
  word as the infinite parity word of a positive integer. It does not rule out
  arbitrary infinite coefficient-safe tails.
- `VERIFIED_THEOREM`: P76 reconstructs the negative-real companion and moving
  rational shadows for every reciprocal-summable positive odd orbit. The
  shadows converge to `h_0` over the reals and `-x_0` over the 2-adics, but no
  effective reduced-height contradiction is known.
- `VERIFIED_THEOREM`: P77--P79 give the unique renewal first-upcrossing code,
  its exact weighted stopping/pressure bounds, the universal `13/9` companion
  threshold, and the normalized ordinary-integrality rule
  `v2(C_w)=r-2` for a nontrivial block's initial one-run.
- `VERIFIED_THEOREM`: P81 gives the necessary-and-sufficient integer identity
  for two parity words to coalesce after an affine source rewrite. P82 shows
  that, if positive permanent-safe counterexample sources exist, their least
  source is irreducible under every uniform positive downward rewrite. This is
  a structural reduction, not an existence or termination proof for H72.
- `VERIFIED_THEOREM`: P83 sharpens the renewal companion threshold by initial
  one-run (`13/9`, `137/81`, and `43/27` in the audited cases), and P84 gives a
  universal positive decrement for every nontrivial renewal block. P85 gives
  an eventual reduced-denominator and gcd bound when the octave defect is
  positive; the zero-defect case remains outside P85.
- `VERIFIED_THEOREM`: P86 strengthens least-source coalescent pruning across
  different odd counts: a smaller safe path to the same endpoint is forbidden
  whenever its terminal coefficient is at least the target's. P87 proves the
  strict-valley suffix extraction that makes unsafe coalescent targets usable,
  with positivity and source descent checked separately. P88 proves endpoint
  injectivity for every fixed finite `{1,2}` odd-gap word.
- `CONDITIONAL`: P80 proves that either a quantified endpoint or two-sided
  canonical-representative anti-concentration estimate would exclude the
  permanent-safe positive branch. Neither estimate is proved.
- `OPEN`: H70 is that eventual dropping-safe pair-spacing inequality. No
  threshold or cross-cylinder proof is known.
- `OPEN`: H72 asks for an orbit-specific packing improvement strong enough to
  exclude every infinite coefficient-safe tail. NG21 blocks a mod-6-only
  improvement, while NG22 blocks a contradiction from the strengthened
  analytic conditions plus a general odd 2-adic source alone, and NG23 blocks
  replacement of deterministic ordinary representatives by raw Haar volume.
  NG24 additionally shows that endpoint coalescence classes are a right
  congruence under a common suffix but not a left congruence under prefixing.
- `EXTERNAL_THEOREM` / `CONDITIONAL`: EXT07 is the Garcia--Tal interval
  sparsity theorem using Heppner's quantitative input. Assuming it, P74 proves
  reciprocal orbit summability and an odd permanent-safe tail minimum for
  every nonperiodic positive orbit; P75 gives summable octave defects and
  `#{j:a_j<=A}=O((A+1)2^(beta A))` for some external `beta<1`.
- `CONDITIONAL`: P54 gives
  `M(K_q-1) <= N <= H_q` under the least-positive-counterexample and
  first-coefficient-crossing hypotheses.
- `CONDITIONAL`: P57 independently gives
  `S(a)>=3N delta` and `W(C)>=6N delta-S0` under the same least-counterexample
  framework.
- `CONDITIONAL`: Phase 9 verifies forced-contact closure, the exact endpoint
  displacement bound `d<=4142380786<2^32`, endpoint congruences, G4
  impossibility, and a reverse continued-fraction barrier inside that same
  least-counterexample first-crossing framework.
- `CONDITIONAL`: Phase 10 reduces the q0 endpoint pair to the single residue
  `rho=d`, proves `4|rho`, and proves renewal coefficient safety through
  `K0-1=114208327603` for every orbit point in `[N,N+W]` in that framework.
- `CONDITIONAL`: P67 decomposes every positive q0 near-return gap into exactly
  one of 30 first-divergence cases `2<=h<=31`. Both post-split tails retain a
  shared coefficient-surplus budget; their simultaneous continuation is open.
- `VERIFIED_FINITE`: the exact modular graphs, return templates, certificate
  nodes, and finite ranges listed below were independently reconstructed.

No item above proves the Collatz conjecture.

## What is only computationally verified?

- Phase 1–2: depth 26 has 190,069 `DESCENT`, 1,227,442 `SPLIT`, and
  1,037,374 `OPEN` nodes. Literal shortcut iteration agrees for all 16,777,214
  starts with `2 <= n < 2^24`.
- Phase 3: 43,198 reverse-merge closures and 79,350 final mixed `OPEN` nodes;
  the exact boundary-gap audit reaches depth 36.
- Phase 4: 52 configured mod-9 templates, 10,335 closed certificate records,
  and 23,785 `OPEN` records; direct audit covers 1,864,135 section elements.
- Phase 5: 52 mod-27 first-return templates and 108 labeled simple cycles; four
  are noncontracting. The direct audit covers 2,485,513 section integers.
- Phase 6: all `H_q` through `q=200000` were scanned exactly, giving 37 record
  indices. Five certificates verify 14 barrier-record inequalities and cover
  every `94 <= q <= 4960`. Direct search determines `M(k)` through `k=223`.
- Phase 7: the first post-bound crossing pair is certified as
  `(q0,K0)=(72057431991,114208327604)` after the external `N>2075*2^60` input.
  Under external Denjoy--Koksma, exact consequences force 31,327,720,462
  contacts and 889,748,829 genuine `h=12` pairs. The exact finite alphabet has
  87,015 macros, and selected fixed layers contain `1,2,7,312455` words.
- Phase 8: under P58, X02, EXT04, and the Phase 7 certificates, exact counting
  gives at most 5 octave exceptions, at least 31,327,720,457 first-octave odd
  iterates, 889,748,819 first-octave `h=12` pairs, and 7,308,576,455
  first-octave consecutive returns of odd gap at most 2. The C03 falsification
  search reconstructs all 79,184 contracting `{A,B}` words through block
  length 18 (79,166 mixed) and 12,265 first block-boundary crossings through
  length 22, with no counterexample.
- Phase 9: the exact denominator-at-most-256 contact dual selects
  `lambda=143/199`, giving 35,251,435,772 closure-aware contacts and
  16,848,437,652 first-octave short returns after exception damage. Independent
  enumeration rebuilds 22,475,497 coefficient-safe first-crossing words
  through `q=21`, all 287 contracting reverse coefficient pairs through
  `a=30`, 30 lower-mechanical reverse words, and every parity word through
  shortcut length 21. No nontrivial paradoxical first-crossing word occurs in
  the small layers; exactly five bounded paradoxical cylinders occur at length
  8 in the unrestricted tree.
- Phase 10: independent enumeration reconstructs 81,118 first-crossing words
  through `q=15`. Exact spacing for every `2<=n<=1,500,000` reaches
  `Delta_213=268416` at `(1126015,1394431)`; at `k=214` only one safe value
  remains in that finite prefix. The target at `H=2^72` was not evaluated.
- Phase 10 branch supplement: E16 reconstructs `R_h(1500000)` for every
  `0<=h<=20`. The largest joint-safe depth is 213 at `h=7`, witnessed by
  `(1126015,1394431)`. Its independent verifier also checks 32,385 small pairs
  and 5,156 mandatory adversarial pairs.
- Two-tail supplement: E17 scans 6,887,319 eligible pairs with
  `2<=n<m<=20000`, `m-n<=512`, and `L=12`. For every shortened residue width
  `b=0,...,11`, it retains the first exact collision between a jointly safe
  and non-safe continuation. The mandatory adversarial audit covers 5,156
  adjacent family pairs.
- Phase 11: E18 independently recomputes every `q<=4961`. The only failures are
  `17,22,27,29,32,34`, all at pair `(27,31)` and gap 4; all `35<=q<=4961`
  pass, with final height 1,666,251. Passes from `q=141` are structurally
  vacuous in the finite scan. E19 represents 16,775,072 pairs by 262,144 exact
  affine cylinders and verifies 48,822 dropping-safe pairs at depth 12.
- Phase 12: E20 checks all 25,000 starts `S=3 mod 4` through 100,000 and 2,144
  mandatory adversarial instances. The longest recorded prefixes contain 85
  and 90 odd iterates respectively; all normalization and rational
  first-crossing comparisons agree with the independent verifier. The
  all-contact audit reconstructs 512 finite canonical residues, and NG21's
  sharpness regression contains 4,096 coprime-to-6 factors.
- Phase 15: E24 exhausts every coefficient-safe word and surplus dominator
  through `Q<=17`, plus every relevant shorter same-Q arbitrary target. At
  Q=17 there are 663,535 safe words, of which 320,168 are dominated by
  `Q_b<=Q_d`; all 32,596 safe `{1,2}`-gap words survive that test. Strict-valley
  extraction adds exactly 12, 90, and 233 reductions at Q=15,16,17 beyond
  same-Q safe targets. These are cutoff facts, not an asymptotic theorem.
- Garcia--Tal audit: E21 independently reconstructs the NG22 formal exponent
  policy through 1,026 odd steps. It verifies `E_1024=1174`, `a_1024=449`,
  and a canonical-residue renewal by `2*2^1174`; hence no positive ordinary
  source below `2^1174` realizes the audited prefix. This finite exclusion is
  not an infinite-source theorem.
- Phase 13: E22 independently rebuilds the first-passage DP through length
  512, 3,331 codewords and every 1--4 block address with total `Q<=12`, all
  ordinary heights through 2,048, 2,144 adversarial convention instances, and
  a 4,096-step square-root countermodel. Its duplicate audit was restricted to
  fixed block-count layers; all finite ratios remain non-asymptotic.
- Phase 14: E23 exhausts all 30,084 renewal addresses with total odd count
  `Q<=13`. It finds 24,197 endpoint classes, 5,829 nontrivial collision
  classes, 5,949 positive downward rewrite pairs, 5,887 reducible addresses,
  and 24,197 finite normal forms. The smallest collision is
  `1|110|1=11101` versus `111100`, with `F_111100(2x+1)=F_11101(x)`.
  No finite rewrite cycle or nonunique normal form occurs in this scope, but
  neither observation is an asymptotic theorem.

These are `VERIFIED_FINITE`; none supplies an eventual statement.

## Strongest verified result

The strongest proof-oriented finite result is the Phase 6 certificate range:
every barrier case `94 <= q <= 4960` is excluded by exact
`M(K_q-1) > H_q` certificates and record monotonicity. The largest shared
certificate is `M(232) > 1358717` with 3,219 nodes.

The strongest exact structural result outside Phase 6 is the Phase 5 mod-27
audit: deleting `{1,11,20,26}` leaves a DAG, first returns have length at most
9, and exactly four of 108 labeled simple cycles are noncontracting.

Phase 7 adds the strongest large-`q` conditional consequence, but it depends
on external computational evidence and Denjoy--Koksma. It does not supersede
the internally verified Phase 6 finite barrier range.

Phase 8 closes C02 as a genuine theorem for the ordered contracting family
`A^rB^s`. This is the strongest new universal block result, but it covers only
one ordering family and therefore does not supersede the P54 barrier route.

Phase 9 gives the strongest current localization of the q0 conditional
endpoint: `0<=X-N<2^32`, `X=7 or 19 mod 36`, G4 is forbidden, and the first
reverse coefficient pair not eliminated by the uniform threshold is
`(a,L)=(615582794569,975675645481)`. These are conditional consequences, not
an existence or exclusion theorem for the endpoint.

Phase 10 gives the strongest renewal consequence of that localization: every
`S` in `[N,N+W]` is conditionally coefficient-safe through `K0-1`. Thus a
positive q0 gap would create two long-safe integers within distance `W`, but
the required global spacing lower bound C05 is still open.

## Strongest conditional route

`P54` (`CONDITIONAL`) is the current main route. A least positive
counterexample whose coefficient first crosses below one at the `q`-barrier
must satisfy

\[
M(K_q-1)\le N\le H_q.
\]

Thus an eventual proof of `M(K_q-1) > H_q`, plus the finite remainder, would
rule out such a counterexample and close the conjecture through this route.

P69 adds a logically exhaustive alternate decomposition. P70 would exclude
its finite-crossing renewal-ladder branch, but nontrivial cycles and infinite
coefficient-safe tails would still require independent exclusion. Therefore
P70 alone is not a complete Collatz route.

## Current main bottleneck

No asymptotic lower bound is known for the least coefficient-safe
representative `M(k)`. Phase 7 narrows the missing statement: no `q`-uniform
inequality is known that prevents a high affine correction `B` from coexisting
with an unusually small least positive inverse-parity residue.
Phase 8 shows that even many exact first-octave returns do not yet supply a
well-founded rank for arbitrary interleavings of the four short-return maps or
the block alphabet `{A,B}`; C03 remains `OPEN`.
Phase 9 further shows that contact closure and weighted pressure alone cannot
finish the argument: NG17 is refuted by the exact all-contact construction.
The remaining C04 bottleneck is a simultaneous Archimedean and 2-adic/3-adic
near-diagonal exclusion at q0. The reverse coefficient barrier does not yet
classify arbitrary exponent-word residues or prove that a valid path exists.
The needed result must dominate `H_q`; the contextual estimate
`H_q = O(q^5.117)` depends on an external Diophantine estimate and is not an
input to current certificates.
Phase 10 makes the same obstruction one-dimensional via
`rho=[B*P^(-1)]_D`, but neither determines this residue for the unknown q0 word
nor proves `Delta_(K0-1)(2^72)>W`. The finite neighbor-gap recursion does not
scale to the required depth and height.
P66/P67 sharpen the positive-gap side further into 30 exact first-divergence
cases. The missing scalable state must retain the common-prefix surplus, odd
normalized gap, and both tail residues; branch depth alone is insufficient.
P68 now gives a lossless state for any fixed horizon, while NG19 shows that at
`L=12` none of the shorter windows `b<L` retains enough information even in a
small exact domain. The open problem is therefore a composable symbolic state,
not a fixed truncation of the future residue.
Phase 11 supplies one such local composition rule: exact affine margins close
to an integer interval on each fixed parity cylinder. It does not merge
different cylinders, so the state count remains exponential. The new H70
eventual dropping-safe barrier is unproved, and finite passes after `q=141` are
empty-set statements rather than asymptotic progress.
Phase 12 constrains the infinite-safe-tail branch using actual odd orbit
values. The coarse mod-6 packing input is sharp at exponent `1/9`; excluding
the branch requires an additional transition, positivity, or ordinary-height
mechanism, not a larger finite range. P73 removes only the all-contact
extremal word. The Garcia--Tal audit conditionally upgrades every nonperiodic
positive orbit to a permanent-safe tail and gives summable defects, but NG22
shows that those analytic conditions remain consistent with a formal exponent
word and a genuine odd 2-adic source. The new boundary is therefore positive
ordinary-integrality or effective rational-shadow height, not mere 2-adic
coherence.
Phase 13 converts that boundary into a precise counting target. P78 supplies
local masses `sigma^i` and `tau^i`, while P79 couples the source to each
block's initial run through an exact 2-adic valuation. P80 shows the needed
ordinary-height decay, but NG23 proves that raw Haar mass cannot supply it:
the per-address lattice error and deterministic least representative must be
controlled arithmetically.
Phase 14 adds an exact coalescent rewrite relation. P82 reduces a hypothetical
positive permanent-safe counterexample to an irreducible renewal address, and
E23 shows that the finite relation removes many addresses. NG24 blocks the
tempting finite-state shortcut: endpoint equality does not survive arbitrary
left extension, so an asymptotic proof still needs a carry-aware lift or a
different well-founded invariant. P85 narrows the rational-shadow height
problem only after the octave defect becomes positive.

## Secondary directions

- Lift P81 coalescence through left extension with enough exact carry data to
  prove that every positive renewal address is eventually reducible, while
  explicitly surviving NG24.
- Prove one of P80's canonical-residue anti-concentration estimates using the
  coupled `(B,r2,r3,C_w)` recurrence, P85's eventual height bounds, and every
  per-address ordinary lattice error.
- Prove C04 by excluding the q0 near-diagonal canonical residue pair, with a
  lossless carry-aware recursion or meet-in-the-middle certificate.
- Prove or refute C05 with a recursive safe-pair cylinder/difference-state
  certificate that scales jointly in depth and ordinary integer height.
- Seek a sound cross-cylinder dominance or quotient/carry recursion extending
  P71; it must distinguish every stored NG19 collision.
- Attack H72 by proving multi-step exclusions or residue-transition scarcity
  among the actual odd iterates; any proposed exponent improvement must use
  information absent from the NG21 coprime-to-6 saturator.
- Upgrade the finite mechanical reverse-residue audit to a recursive forbidden
  residue theorem for arbitrary positive exponent compositions.
- Derive recursive or meet-in-the-middle lower bounds for `M(k)`.
- Explain small `M(k)` using moving rational shadows of unbounded height and
  simultaneous 2-adic/3-adic constraints.
- Seek a common well-founded potential for the partial integer block system
  `A:32u->81u`, `B:16u+108->9u+108`, beginning with an adversarial audit of
  arbitrary interleavings rather than only `A^rB^s`.
- Extend exact certificates only when testing a precise structural conjecture.
- Revisit predecessor-tree density only with a bridge from global density to a
  single least counterexample.

## What was recently refuted?

- `REFUTED`: same-Q safe-target rewrites are complete for surplus dominance
  (NG25). The Q=1 word `1` maps 273 to the same endpoint 410 reached by
  `111110100` from 287 and has larger coefficient. A Q=5 ancestor also
  dominates a Q=4 target.
- `REFUTED`: an arbitrary coalescent target must itself be safe (NG26). The
  named unsafe Q=15 word has a strict-valley safe suffix that coalesces from
  527131 below the safe target source 1874247.
- `REFUTED`: coalescent endpoint equivalence is a two-sided congruence under
  renewal concatenation. The exact pair `11101~111100` stays equivalent under
  a common suffix, but prefixing both by `110` gives endpoint residues 263 and
  587 modulo `3^6`. Endpoint `(Q,r3)` alone is not a closed transfer state.
- `REFUTED`: coefficient-one raw Haar endpoint or product volume controls the
  canonical least positive representative count. NG23's minimum obstruction
  is `u=1,H=2`: the count is 1 and both volume predictions are `2/3`.
- `REFUTED`: the conditions `a_j->infinity`, `sum 2^-a_j<infinity`,
  `h_j>1`, and `sum 1/h_j=infinity`, even with a coherent odd 2-adic source,
  are contradictory by themselves. NG22 gives an exact invariant formal
  policy. It is not a positive ordinary Collatz orbit.
- `REFUTED`: distinctness, a lower height, and `gcd(x_i,6)=1` alone force a
  growth exponent below `1/9`. The exact abstract coprime-to-6 saturator has
  logarithmic product exponent `1/9`; it is not a Collatz orbit.
- `REFUTED`: height-free dropping-safe spacing eventually exceeds 4. For every
  `k>=3`, `2^k-5` and `2^k-1` are k-step dropping-safe and differ by 4.
- `REFUTED`: for `L=12`, some shortened residue window `b<L` universally
  decides two-tail joint coefficient safety. Every `b=0,...,11` has an exact
  opposite-outcome collision below `H=20000` and gap 512.
- `REFUTED`: nested safe-set deletion forces strict spacing growth at every
  depth. The exact Phase 10 prefix has `Delta_2=Delta_3=4`; only nondecrease
  survives without a stronger state invariant.
- `REFUTED`: forced-contact closure plus weighted contact pressure alone is
  sufficient. With the required correction `c_0=1`, the exact all-contact
  construction still satisfies closure and pressure but carries no endpoint
  or least-residue exclusion.
- `REFUTED`: four fixed rational shadow centers are complete. The exact block
  `W=111011100` has map `(729x+817)/512` and fixed point `-817/217` outside the
  four centers.
- `REFUTED`: the quantified H5-A bounded surrogate; 2,141 bounded
  counterexamples were retained.
- `REFUTED`: fixed short-period dictionaries universally explain critical
  prefixes; the smallest depth-26 residual representative is 27.
- `REFUTED`: the tested constants-only Phase 4 ranking closes refill cycles.
- `REFUTED` as a standalone strategy: adding only bounded binary/ternary or
  modular refinements makes the tested frontier manageable asymptotically.
- `REFUTED`: every 12-odd contact-return macro contracts, decomposes into the
  four Phase 5 dangerous words, or is locally unrealizable. Macro id 0,
  `1111111111110000000`, refutes all three candidate statements.
- `RETRACTED`: early strong numerical claims based on cycle-only assumptions,
  unchecked computations, or invalid equivalences.

## Next 3 concrete research questions

1. Can the gap residue `rho=[B*3^(-q)]_(2^K-3^q)`, `4|rho`, be excluded from
   `[0,W]` for every q0-critical word by a scalable exact recursion?
2. Can P86/P87 surplus fronts be propagated across Q with a finite or
   well-founded carry state that distinguishes NG24--NG26 and proves eventual
   reducibility of every positive renewal address, including the `{1,2}` core?
3. Can P71's exact per-cylinder margin interval be merged across residue
   cylinders by a sound dominance/carry rule strong enough to prove H70
   without relying on EXT07, or can an exact successor rule separate actual
   odd orbits from both NG21 and NG22?

## Codex tasks worth doing

- Start with [`AI_RESEARCH_GUIDE.md`](AI_RESEARCH_GUIDE.md) and run
  `scripts/research_health.py` before modifying research code.
- Select one obligation from `research/registry.json`, read its scoped context
  pack when present, and register any large run under `research/experiments/`.
- Run `scripts/research_health.py --strict` from a clean acceptance worktree;
  untracked artifact warnings are not accepted evidence.
- Formalize one precise candidate inequality for `M(k)` and search for its
  smallest exact counterexample before scaling.
- Extend P71 only with a proposed cross-cylinder dominance/carry invariant;
  test it first on NG19 and NG20.
- Extend P72 only with an orbit-specific transition invariant; test it first
  against NG21--NG26 and E20/E22/E23/E24 before claiming an exponent or
  anti-concentration improvement.
- Build an independent verifier for any new lower-bound certificate format.
- Audit proof dependencies and claim statuses after each result.
- Maintain adversarial regressions for `2^m-1`, `8^m-5`, `(110|111)^*`,
  `A=11101`, `B=1100`, and `A^rB^s`.
- Replace external record minimality with compact internal certificates where
  feasible.

## Tasks not worth doing without a new idea

- Merely extend Phase 1–5 search depth or modulus.
- Add another fixed finite shadow dictionary.
- Extend the Phase 11 q-limit without a nonvacuous asymptotic mechanism; E18 is
  already structurally empty from q=141 in its finite height.
- Retry height-free dropping-safe spacing greater than 4; NG20 refutes it for
  every depth k>=3.
- Retry a packing exponent below `1/9` using only distinctness and
  coprimality modulo six; NG21 is sharp for exactly that information set.
- Seek a contradiction from only summable octave defects, `h_j>1`, divergent
  companion reciprocals, and a general odd 2-adic source; NG22 realizes all
  four analytic conditions exactly.
- Replace deterministic canonical representatives by Haar cylinder volume or
  discard the per-address ordinary lattice `+1`; NG23 refutes that step at the
  first codeword.
- Retry contact closure plus weighted pressure without a new endpoint or
  least-residue invariant; NG17 is an exact no-go for that information set.
- Infer an asymptotic law from high finite coverage or a beam search.
- Retry naive predecessor-density intersection without a theorem controlling
  the exceptional least counterexample.
- Use floating point to accept a certificate or a near-critical inequality.

## Immediate audit pointers

- Machine-readable control plane: [`../research/registry.json`](../research/registry.json)
- Experiment contract: [`../research/README.md`](../research/README.md)
- Scoped AI contexts: [`context/README.md`](context/README.md)
- Claim statuses: [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md)
- Negative results: [`FAILED_APPROACHES.md`](FAILED_APPROACHES.md)
- Prioritized program: [`ROADMAP.md`](ROADMAP.md)
- Phase 6 acceptance: [`../PHASE6_RUN_RESULTS.md`](../PHASE6_RUN_RESULTS.md)
- Phase 7 acceptance: [`../PHASE7_RUN_RESULTS.md`](../PHASE7_RUN_RESULTS.md)
- Phase 8 acceptance: [`../PHASE8_RUN_RESULTS.md`](../PHASE8_RUN_RESULTS.md)
- Phase 9 acceptance: [`../PHASE9_RUN_RESULTS.md`](../PHASE9_RUN_RESULTS.md)
- Phase 10 acceptance: [`../PHASE10_RUN_RESULTS.md`](../PHASE10_RUN_RESULTS.md)
- Branch-point supplement: [`../BRANCH_POINT_RUN_RESULTS.md`](../BRANCH_POINT_RUN_RESULTS.md)
- Two-tail supplement: [`../TWO_TAIL_RUN_RESULTS.md`](../TWO_TAIL_RUN_RESULTS.md)
- Phase 11 acceptance: [`../PHASE11_RUN_RESULTS.md`](../PHASE11_RUN_RESULTS.md)
- Phase 12 acceptance: [`../PHASE12_RUN_RESULTS.md`](../PHASE12_RUN_RESULTS.md)
- Phase 13 acceptance: [`../PHASE13_RUN_RESULTS.md`](../PHASE13_RUN_RESULTS.md)
- Phase 14 acceptance: [`../PHASE14_RUN_RESULTS.md`](../PHASE14_RUN_RESULTS.md)
- Phase 15 acceptance: [`../PHASE15_RUN_RESULTS.md`](../PHASE15_RUN_RESULTS.md)
- Hashes: [`../artifacts/SHA256SUMS`](../artifacts/SHA256SUMS)
