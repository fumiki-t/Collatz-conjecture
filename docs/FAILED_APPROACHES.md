# Failed and deprioritized approaches

Failures are retained as research assets. Each entry states the precise scope
that failed; it must not be read as a theorem excluding every possible
strengthening of the idea.

The cross-phase lesson map is in
[`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md#6-failed-mechanisms-and-surviving-lessons).
This file remains the detailed canonical failure archive.

## NG01 — Local parity exchange `01 <-> 10`

**Status:** `REFUTED`

**Exact hypothesis.** Local exchanges monotonically order affine corrections
and reduce extremal coefficient-safe words to a canonical
Christoffel/Sturmian form.

**Why it looked plausible.** The real affine correction changes in a
structured way under adjacent exchanges.

**Smallest counterexample / failure.** The minimal positive representative
modulo `2^k` has carry jumps not controlled by the real correction order. The
proposed monotonicity does not survive those jumps; no stable smallest numeric
counterexample was preserved from the exploratory period.

**Failure scope.** Fundamental for this local real-order argument, not for all
uses of Sturmian words.

**Weaker statement retained.** Exchange calculations may still locate
extremal real affine corrections at a fixed combinatorial type.

**Rules out.** Proofs that identify the least positive cylinder representative
solely by locally sorting a parity word.

## NG02 — Fixed finite-state Lyapunov correction

**Status:** `REFUTED`

**Exact hypothesis.** A bounded observation window or bounded state correction
can assign a universally decreasing rank to every critical prefix.

**Why it looked plausible.** Typical Collatz paths contract and short states
capture many finite certificates.

**Smallest counterexample / failure.** Families `2^m-1` and `8^m-5` shadow
negative cycles for arbitrarily long finite times; `(110|111)^*` supplies a
large coefficient-safe language. Any fixed window can be reproduced beyond
its horizon.

**Failure scope.** Fundamental for ranks whose full information is bounded
independently of depth.

**Weaker statement retained.** Finite-state ranks are useful bounded
certificate rules and falsification tools.

**Rules out.** Promoting a bounded-state success rate to a universal descent
theorem without an unbounded arithmetic component.

## NG03 — Fixed modulus contraction

**Status:** `REFUTED`

**Exact hypothesis.** Refinement modulo one fixed integer eventually makes
every surviving class contract.

**Why it looked plausible.** Congruence classes determine finite parity
segments, and many classes close immediately.

**Smallest counterexample / failure.** Arbitrarily long positive shadows of
negative rational cycles share every prescribed bounded modular observation.
Phases 4–5 also retain refill cycles and noncontracting templates.

**Failure scope.** Fundamental for a proof whose state is only one fixed
modulus. It does not exclude a growing-modulus theorem with a proved rank.

**Weaker statement retained.** Mod-9 and mod-27 sections compress exact returns
and expose useful obstructions.

**Rules out.** Increasing a fixed modulus and treating finite closure as an
eventual theorem.

## NG04 — Short periodic dictionary

**Status:** `REFUTED`

**Exact hypothesis.** Every depth-26 coefficient-safe survivor contains, as a
prefix or suffix, at least three repetitions of some block of length at most
16.

**Why it looked plausible.** The dictionary explains 913,466 of 1,037,374
survivors at that depth.

**Smallest counterexample / failure.** The smallest unexplained representative
is `27`, with parity word `11011111010110111011110100`. There are 123,908
unexplained survivors.

**Failure scope.** Exact finite counterexample to this dictionary. It is not a
theorem about every parametric macro language.

**Weaker statement retained.** Short blocks remain descriptive clustering
features.

**Evidence.** [`../RUN_RESULTS.md`](../RUN_RESULTS.md).

## NG05 — Naive 2-adic bit-growth

**Status:** `RETRACTED`

**Exact hypothesis.** Increasing parity-prefix length automatically forces
ordinary positive representatives to gain a comparable number of bits.

**Why it looked plausible.** A length-`k` parity word selects one residue
modulo `2^k`.

**Smallest counterexample / failure.** Residue precision and Archimedean size
are different: a compatible residue can have an unusually small positive
representative. `M(k)` is defined precisely because no automatic lower bound
follows from the modulus.

**Failure scope.** Invalid implication, retracted rather than merely
computationally refuted.

**Weaker statement retained.** Exact cylinder congruences are useful when
paired with an independently proved least-representative lower bound.

## NG06 — Real-versus-2-adic sign contradiction

**Status:** `RETRACTED`

**Exact hypothesis.** A real limit with one sign and a 2-adic reconstruction
with another sign directly contradict each other.

**Why it looked plausible.** The same formal affine series admits real and
2-adic interpretations.

**Smallest counterexample / failure.** Sign and convergence are topology
dependent; equality of formal expressions does not identify their real and
2-adic limits. No valid bridge theorem was supplied.

**Failure scope.** Fundamental logical gap in the proposed shortcut.

**Weaker statement retained.** Simultaneous real/2-adic/3-adic compatibility
may be informative only after a precise common arithmetic object is proved.

## NG07 — Ternary split plus reverse merge as a standalone strategy

**Status:** `REFUTED`

**Exact hypothesis.** Bounded ternary refinement and exact reverse merges make
the unresolved mixed frontier subcritical.

**Why it looked plausible.** Phase 3 closes 43,198 records by exact reverse
merge.

**Smallest counterexample / failure.** The smallest unresolved representative
is `27`; after two ternary refinements 79,350 mixed nodes remain. Tested
unresolved counts grow from 15,870 to 31,740 to 79,350.

**Failure scope.** Exact rejection of the configured bounded rule language,
not of every reverse-preimage argument.

**Weaker statement retained.** Reverse merges are valid certificate rules when
their strict smaller-family dependency is reconstructed.

**Evidence.** [`../PHASE3_RUN_RESULTS.md`](../PHASE3_RUN_RESULTS.md).

## NG08 — Mod-9 finite rank on `1,5,21`

**Status:** `REFUTED`

**Exact hypothesis.** A fixed return horizon or constants-only rank on the
Phase 4 recurrence constants `1`, `5`, and `21` closes every mod-9 return
cylinder.

**Why it looked plausible.** The return code is exact, prefix-free, and has
Kraft sum one; each excursion is compressed to a small recurrence family.

**Smallest counterexample / failure.** Monotone one-return descent already
fails at `11 -> 20` and `47 -> 182`. The smallest configured unresolved family
is `47+18432t`, with endpoint `155+59049t` after three returns. There are
23,785 `OPEN` records.

**Failure scope.** Exact bounded ranking failure; a new unbounded
well-founded rank is not excluded.

**Weaker statement retained.** The return parametrization and Kraft identity
remain reusable exact structure.

**Evidence.** [`../PHASE4_RUN_RESULTS.md`](../PHASE4_RUN_RESULTS.md).

## NG09 — Four dangerous shadows are complete

**Status:** `REFUTED`

**Exact hypothesis.** All near-critical behavior is controlled by the four
noncontracting Phase 5 shadow centers associated with `1`, `101`, `1101`, and
`011101`.

**Why it looked plausible.** Exactly those four of the 108 labeled simple
mod-27 cycles are noncontracting.

**Smallest counterexample / failure.** With `A=11101` and `B=1100`,
`W=AB=111011100` has map `(729x+817)/512` and fixed point `-817/217`, outside
the four centers. The family `A^rB^s` also produces new near-critical centers.

**Failure scope.** Fundamental for any fixed finite center list. The general
arbitrary-closeness statement depends on the external irrational-rotation
density theorem; the displayed `W` counterexample is exact and internal.

**Weaker statement retained.** The four centers classify noncontracting simple
cycles in the exact mod-27 graph.

**Evidence.** [`../PHASE5_RUN_RESULTS.md`](../PHASE5_RUN_RESULTS.md).

## NG10 — H5-A/H5-B bounded shadow ranking

**Status:** `REFUTED` for the quantified bounded surrogates; the original
unquantified ideas were never precise enough to be theorem claims.

**Exact hypothesis.** The configured aligned-repetition/switch-cost tests
force bounded shadow paths into a finite well-founded ranking.

**Why it looked plausible.** Long beam paths often align with the four simple
dangerous words and low-precision switches appear costly.

**Smallest counterexample / failure.** H5-A retains 2,141 counterexamples; the
smallest recorded family is
`461826978031+474989023199232t` at return depth 20. H5-B retains 80 bounded
candidates; the smallest starts at `362638` at return depth 5. The mandatory
`A^rB^s` family defeats the assumption that only four centers need ranking.

**Failure scope.** Bounded surrogate and tested rank languages only.

**Weaker statement retained.** Exact return maps and switch witnesses remain
diagnostic data.

## NG11 — Sturmian-only transcendence shortcut

**Status:** `REFUTED` as a route to the full conjecture.

**Exact hypothesis.** It suffices to prove irrationality/transcendence or
aperiodicity consequences for critical Sturmian parity words.

**Why it looked plausible.** Sturmian/mechanical words naturally realize the
critical density `log 2 / log 3` with minimal complexity.

**Smallest counterexample / failure.** A hypothetical coefficient-safe orbit
is not known to have Sturmian or even low word complexity. The language
`(110|111)^*` supplies many nonperiodic safe finite words outside a single
Sturmian model.

**Failure scope.** Logical incompleteness, not a counterexample to the external
Sturmian theorems.

**Weaker statement retained.** Sturmian words are important adversarial and
extremal test cases.

## NG12 — Naive predecessor-tree density comparison

**Status:** `REFUTED` as a standalone contradiction.

**Exact hypothesis.** A large predecessor set combined with an almost-all
forward-descent theorem must intersect the orbit or residue class of a least
counterexample in a way that forces descent.

**Why it looked plausible.** Strong lower bounds exist for predecessors, while
almost-all results make exceptional forward orbits sparse.

**Smallest counterexample / failure.** Two global density statements need not
control one designated exceptional integer or its thin arithmetic set. The
argument supplied no quantitative intersection or invariance theorem.

**Failure scope.** Fundamental gap in naive density comparison. A future
approach with an explicit bridge theorem remains possible.

**Weaker statement retained.** Predecessor growth can support a proof if it is
tied to the least-counterexample cylinder or an invariant measure with the
needed exceptional-set control.

## NG13 — Early strong numerical and kernel claims

**Status:** `RETRACTED`

**Exact hypothesis.** Exploratory claims about mandatory numbers of
"mountains", very large lower bounds, or derived kernel maps were treated as
if they transferred to every nonperiodic positive trajectory.

**Why it looked plausible.** The experiments showed striking regularities and
some formulas were correct in a narrower cyclic setting.

**Smallest counterexample / failure.** The supporting work either applied a
cycle-only identity outside cycles, used unchecked computation, or failed to
prove equivalence between a derived map and the original Collatz map. Exact
smallest counterexamples were not preserved.

**Failure scope.** The original claims are withdrawn in full.

**Weaker statement retained.** None as a theorem. Their historical value is
the present certificate/verifier/status discipline.

## NG14 — Uniform contraction of 12-odd contact macros

**Status:** `REFUTED`

**Exact hypothesis.** Every exact contact-return excursion with 12 odd steps
has multiplier below one.

**Why it looked plausible.** Phase 7 forces many pairs of boundary contacts,
so a uniformly contracting return alphabet would convert analytic pressure
into descent.

**Smallest counterexample / failure.** Macro id 0 has word
`1111111111110000000` and multiplier `3^12/2^19>1`.

**Failure scope.** Fundamental for uniform contraction of this exact alphabet;
it does not exclude a global frequency or transition theorem.

**Weaker statement retained.** The 87,015 macros are an independently verified
finite alphabet for testing stronger concatenation constraints.

## NG15 — Compulsory four-dangerous-word decomposition

**Status:** `REFUTED`

**Exact hypothesis.** Every 12-odd contact-return macro decomposes into the
four Phase 5 noncontracting words `1`, `101`, `1101`, and `011101`.

**Why it looked plausible.** Those four words are the complete noncontracting
simple-cycle list in the Phase 5 mod-27 graph.

**Smallest counterexample / failure.** Macro id 0 is not a concatenation of
the four words.

**Failure scope.** Fundamental for compulsory local decomposition into the
fixed four-word dictionary, not for growing moving-shadow coordinates.

**Weaker statement retained.** Dangerous-word decompositions remain exact
diagnostic fields for the macros where they exist.

## NG16 — Local arithmetic unrealizability of contact macros

**Status:** `REFUTED`

**Exact hypothesis.** Every 12-odd contact-return macro is incompatible with a
positive integral source satisfying its full parity word.

**Why it looked plausible.** Dense boundary contacts could have conflicted
with the inverse parity residue or odd-modulus endpoint conditions.

**Smallest counterexample / failure.** Macro id 0 has an exact positive
power-of-two residue realization, reconstructed by the independent verifier.

**Failure scope.** Fundamental for one-macro unrealizability. It does not
decide whether arbitrary macro concatenations remain globally compatible.

**Weaker statement retained.** Arithmetic compatibility must be tested across
transitions or unbounded concatenations, not one macro at a time.

## NG17 — Contact closure plus weighted pressure is sufficient

**Status:** `REFUTED`

**Exact hypothesis.** The Phase 9 forced-contact closure rule, together with
the Phase 7 weighted contact lower bound, excludes every finite critical defect
word without using its endpoint or least positive inverse-parity residue.

**Why it looked plausible.** A low-phase contact forces the next defect to
remain zero and transfers exactly `2/3` of its weight to a high-phase contact.
This increases the exact contact lower bound from 31,327,720,462 to
35,251,435,772 and appears to impose strong local rigidity.

**Smallest counterexample / failure.** The specification's arbitrary contact
indicator needs the zero-index correction `c_0=1`. With that correction, the
symbolic all-contact construction
`c_j=1, a_j=0, d_j=floor(j*log_3(2)), e_j=b_j` obeys the exact recurrence and
closure and strictly satisfies the q0 weighted pressure. It therefore survives
every test available to a contact-only mechanism. The artifact stores exact
rational-logarithm interval checks rather than a floating-point comparison.

**Failure scope.** Fundamental for every argument whose only information is
the contact indicator, the forced successor relation, and total weighted
pressure. It is not a counterexample to Collatz and does not refute mechanisms
that also use endpoint minimality, canonical 2-adic/3-adic residues, or the
Archimedean near-diagonal condition.

**Weaker statement retained.** P59's forced-contact closure is exact and gives
a stronger conditional contact and short-return lower bound. Future work must
combine it with the endpoint arithmetic represented by P60--P62 and C04.

## NG18 — Strict per-depth safe-pair spacing growth

**Status:** `REFUTED`

**Exact hypothesis.** For fixed finite `H`, nested coefficient-safe sets force
`Delta_(k+1)(H)>Delta_k(H)` whenever both spacings are defined.

**Why it looked plausible.** Passing to the next depth only deletes safe
starts, and deletion merges its two adjacent gaps by exact addition. Repeated
mergers therefore appear to create a direct depth-by-depth growth mechanism.

**Smallest counterexample / failure.** In the independently verified Phase 10
production prefix `H=1,500,000`, `Delta_2=Delta_3=4`. The minimizing pair can
survive a layer even while other points are deleted, so the minimum need not
increase. The same value persists at further early depths.

**Failure scope.** Fundamental for strict growth at every depth. It does not
refute nondecrease, growth at selected record depths, or a stronger recursive
cylinder certificate carrying more state.

**Weaker statement retained.** Whenever both finite spacings are defined,
nesting proves `Delta_(k+1)(H)>=Delta_k(H)`. Phase 10 verifies the deletion and
neighbor-gap rule exactly, but it finds no composable certificate reaching
`K0-1` and `H=2^72`.

## Phase 10 supplement — branch depth alone is not a certificate

**Status:** research obstruction; no new universal claim is marked refuted

The exact first-divergence coordinate `h=v2(m-n)` is useful but does not by
itself rank joint coefficient-safe continuation. In E16 the finite envelope
`R_h(1500000)` is highly nonmonotone: it reaches 213 at `h=7`, falls, and rises
again at several later h values. This is evidence against treating a larger
common 2-adic prefix as a standalone monotone potential, but a bounded profile
is not a universal counterexample to every function of h.

The surviving exact state must also retain the common-prefix odd count, the
odd normalized gap, inherited coefficient surplus, and both tail residue
states. Future compression proposals should be rejected as soon as two
histories share the proposed state but have different exact continuation
behavior. Merely extending H without specifying such a state is not a new
mechanism.

## Two-tail supplement — shortening the exact future residue

**Status:** `REFUTED` (NG19)

**Exact hypothesis.** For horizon `L=12`, there exists a width `b<L` such that
the state `(h,a,u,orientation,y mod 2^b)` decides whether both post-branch tails
remain coefficient-safe through the next L steps.

**Why it looked plausible.** P66 fixes the transformed odd gap as `3^a u`,
the branch orientation fixes the first split, and much of the coefficient
decision appears to depend only on a short suffix of each tail. A truncated
residue would have produced a small finite transition system suitable for C05.

**Smallest counterexamples.** E17 enumerates pairs in increasing upper endpoint
and then increasing positive gap. It stores an opposite-outcome collision for
every `b=0,...,11`. For `b=0,1`, `(3,7)` and `(27,31)` already share the state
but disagree. The hardest tested truncation, `b=11`, collides at pairs
`(1407,1663)` and `(15551,15807)`, both with `h=8`, `a=7`, `u=1`, orientation
`01`, and left-tail residue 1788 modulo 2048.

**Failure scope.** Fundamental for this exact state family at `L=12`: no
choice `b<L` is lossless, because one explicit collision refutes each choice.
It does not prove that every possible finite automaton fails, nor that all
unbounded descriptions require storing a literal growing residue window.

**Weaker statement retained.** P68 proves that `b=L` is sufficient for an
L-step decision. A future certificate must retain equivalent carry/residue
information or prove a dominance relation that safely merges the recorded
opposite-outcome histories.

## Phase 11 — height-free dropping-safe spacing

**Status:** `REFUTED` (NG20)

**Exact hypothesis.** Dropping-safe spacing can be bounded from below as a
function of depth alone, eventually by a value greater than 4, without an
ordinary-height restriction.

**Why it looked plausible.** Longer non-dropping prefixes become rare in every
fixed finite height, and Phase 11's renewal gaps grow like `q/3`. A depth-only
spacing estimate would have removed the difficult dependence on `H_q`.

**Universal counterexample.** For every `k>=3`, both

```text
2^k-5 and 2^k-1
```

are k-step dropping-safe and differ by 4. The first word follows the repeating
parity pattern `(110)^*`; the second follows `1^k`. Closed orbit formulas in
the Phase 11 result prove the claim for all k, while the verifier directly
regresses through k=256.

**Failure scope.** Fundamental for every height-free spacing bound exceeding
4. It also explains why finite disappearance at fixed H cannot be treated as
depth-only progress.

**Weaker statement retained.** P70 retains the exact coupled height
`floor(H_q)+floor((q-1)/3)`. P71 closes margin inequalities on each fixed
parity cylinder, but a new cross-cylinder dominance theorem is required.

## Phase 12 — improving the packing exponent from mod 6 alone

**Status:** `REFUTED` (NG21)

**Exact hypothesis.** Distinct odd values bounded below by a fixed `S`, with
every value after the first coprime to six, force the normalized product
`Y_j` to grow like `O(j^gamma)` for some `gamma<1/9`.

**Why it looked plausible.** Actual odd Collatz iterates obey congruence
restrictions, and the first packing estimate leaves a large density-one octave
defect. A better exponent would strengthen `8/9` toward a pointwise or
contradictory lower bound for `a_i`.

**Exact countermodel.** Enumerate all positive integers coprime to six and set

```text
Y_(i+1)=Y_i*(1+1/(3x_i)).
```

Every complete block of six contributes exactly two values. Elementary
harmonic estimates give

```text
sum 1/x_i=(1/3)log j+O(1),
log Y_j=(1/9)log j+O(1).
```

The artifact independently reconstructs the first 4,096 exact product factors.

**Failure scope.** Fundamental only for arguments using distinctness, a lower
height, and coprimality modulo six as their complete input. The countermodel is
not a Collatz orbit and does not show that exponent `1/9` is dynamically
optimal.

**Weaker statement retained.** P72 proves the `1/9` upper envelope and the
density-one `8/9-epsilon` octave-defect bound. H72 must exploit actual
successive-transition congruences or another orbit-specific invariant.

## Garcia--Tal audit — analytic-only companion contradiction

**Status:** `REFUTED` (NG22)

**Exact hypothesis.** The four conditions

```text
a_j -> infinity
sum 2^(-a_j) < infinity
h_j > 1
sum 1/h_j = infinity
```

are already contradictory, possibly after also requiring a coherent odd
2-adic source with the same exponent sequence.

**Why it looked plausible.** P75 conditionally makes the positive-orbit defect
summable, while P76 produces a negative-real companion whose reciprocal sum
diverges. The opposite real growth behavior and common parity/exponent data
suggest a product-formula or simultaneous-approximation contradiction.

**Exact countermodel.** Start with `h_0=3/2`. Use `e_j=1` on
`1<h_j<=5/3`, `e_j=2` on `5/3<h_j<=2`, and
`h_(j+1)=(3h_j-1)/2^e_j`. The interval `(1,2]` is invariant. The construction
has linearly growing defect, summable `2^-a_j`, divergent `1/h_j`, and a unique
coherent odd 2-adic inverse-series source. E21 independently reconstructs
1,026 steps and rejects every positive ordinary source below `2^1174` for
that prefix.

**Failure scope.** Fundamental for the four analytic conditions, even after
adding general 2-adic coherence. It is not a Collatz counterexample: the
2-adic source has not been shown to be a positive ordinary integer. The finite
height exclusion is not an infinite nonexistence theorem.

**Weaker statement retained.** P75 and P76 are valid necessary structure for a
hypothetical permanent-safe positive orbit. H72 must add positivity,
ordinary-integrality/effective height, or transition information that fails on
the NG22 source.

## Phase 13 — raw Haar volume controls canonical representatives

**Status:** `REFUTED` (NG23)

**Exact hypothesis.** For renewal addresses, the raw endpoint Haar mass
`sum 3^(-Q)` or two-sided product mass `sum 2^(-L)3^(-Q)`, with coefficient
one, controls the count of canonical least positive representatives below
ordinary height `H`.

**Why it looked plausible.** The address masses factor exactly as `sigma^i`
and `tau^i`, while positive renewal boundaries grow by at most `(3/2)^i`.
If local Haar mass directly transferred to ordinary representatives, the exact
pressure products `7/8` and `57/128` would exclude a permanent-safe orbit.

**Smallest counterexample.** The first codeword `u=1` has `L=Q=B=1`, least
positive source representative 1, and least positive endpoint representative
2. At `H=2`, the canonical endpoint and two-sided counts are both one, while

```text
H*3^(-Q) = 2/3,
H^2*2^(-L)*3^(-Q) = 2/3.
```

**Failure scope.** Exact refutation of coefficient one and of the logical step
from local Haar measure to one designated ordinary representative. It does not
refute an estimate with an unspecified fixed constant, a subexponential
factor, or an arithmetic separation theorem using the coupled affine
recurrence.

**Weaker statement retained.** P78's mass factorizations are exact, and P80
proves that either explicitly quantified anti-concentration estimate would be
sufficient. P79 adds the orbit-specific valuation rule
`v2(C_w)=r-2`. The estimates themselves remain open.

**Rules out.** Summing local cylinder volumes, discarding the per-address
ordinary lattice `+1` error, and concluding that a particular positive source
cannot exist. Endpoint 3-adic cylinders can also be nested, so the sum of
address masses is not automatically a union measure.

**Evidence.** [`../PHASE13_RUN_RESULTS.md`](../PHASE13_RUN_RESULTS.md),
`artifacts/phase13_residue_audit.json`, and the independent Phase 13 verifier.

## Phase 14 — coalescent equivalence as a two-sided quotient

**Status:** `REFUTED` (NG24)

**Exact hypothesis.** Equality of the canonical endpoint state `(Q,r3)` is
preserved when the same renewal block is concatenated on either side, so a
coalescent class alone supplies a closed block transfer operator.

**Why it looked plausible.** If two words reach the same endpoint, appending
the same future word plainly preserves coalescence. The complete `Q<=13`
graph also has one finite normal form in every endpoint class.

**Smallest counterexample.** The minimum collision is

```text
11101 ~ 111100, endpoint residue 20 modulo 3^4.
```

After prefixing both by the renewal block `110`, the endpoint residues become
263 and 587 modulo `3^6`, respectively. They are no longer coalescent.

**Failure scope.** Fundamental for a state containing only the current
coalescent endpoint class and treating block composition as two-sided. It
does not refute the exact right-ideal statement in P82 or a larger state that
retains the missing 3-adic lift/carry and affine data.

**Weaker statement retained.** Appending the same right suffix preserves every
P81 rewrite exactly. The `Q<=13` finite graph terminates and is confluent, but
no all-depth confluence or asymptotic pressure theorem follows.

**Evidence.** [`../PHASE14_RUN_RESULTS.md`](../PHASE14_RUN_RESULTS.md),
`artifacts/phase14_coalescent_theory.json`, and the independent Phase 14
verifier.

## Phase 15 — same-Q safe targets are a complete dominance language

**Status:** `REFUTED` (NG25)

**Exact hypothesis.** Every smaller coefficient-safe path that coalesces with
a safe target and preserves at least its terminal coefficient surplus can be
found among safe competitors with the same odd count.

**Why it looked plausible.** P81's affine rewrite identity and E23's finite
graph are organized by fixed `(Q,r3)` endpoint classes, and same-Q source
relations are especially simple.

**Smallest recorded cross-Q witness.** The safe word `111110100` maps 287 to
410 with coefficient `729/512`. The one-bit word `1` maps 273 to the same 410
with coefficient `3/2`. Thus the smaller useful ancestor has Q=1 rather than
Q=6. A separate witness has the Q=5 word `1110110` dominate the Q=4 target
`110110`.

**Failure scope.** Fundamental for same-Q completeness. It does not refute
P81 or same-Q rewrites; they remain a valid subset of P86 dominance.

**Weaker statement retained.** P86 gives the exact cross-Q condition. E24
enumerates it through `Q_b,Q_d<=17`, but no eventual frontier theorem follows.

## Phase 15 — arbitrary coalescent targets must already be safe

**Status:** `REFUTED` (NG26)

**Exact hypothesis.** An unsafe shorter same-Q target can be discarded before
testing whether it yields a downward coalescent reduction.

**Why it looked plausible.** P82 needs a coefficient-safe replacement path,
so an unsafe target appears unusable if treated as an indivisible word.

**Counterexample.** The unsafe Q=15 target
`1010110111111101011100` maps 937121 to 3205946. Its unique strict valley is
after `1010`; the suffix `110111111101011100` is coefficient-safe and maps
527131 to the same endpoint, below safe target source 1874247, with larger
terminal coefficient surplus.

**Failure scope.** Fundamental for pre-valley filtering, not for safe-suffix
dominance. Positivity and `V<S` still require explicit checks.

**Weaker statement retained.** P87 proves exact valley extraction. E24 finds
12, 90, and 233 additional reductions at Q=15,16,17 beyond same-Q safe
targets; zero in lower audited layers is finite evidence only.

## Phase 15B — same-Q total compression gain is at most three

**Status:** `REFUTED` (NG27)

**Exact hypothesis.** If two coefficient-safe words have the same odd count
and endpoint residue, replacing the longer by the shortest word in that class
always saves at most three shortcut steps.

**Why it looked plausible.** The shifted correction
`D=B+2^L-3^Q` exposes exact power-of-two jump classes, and every audited layer
below Q=19 had maximum total gain at most three.

**Smallest-source maximum-gain counterexample in the audited Q=19 layer.**

```text
d=11111111111111101110000000001, source 44,466,175
a=1111111111101111110100100,     source  2,779,135
common endpoint 96,263,966
d_source+1 = 16*(a_source+1)
length gain = 4.
```

**Failure scope.** Exact refutation of the universal gain-three bound. It
does not refute P95 jump classes, and it neither proves nor disproves an
unbounded, linear, or composable gain theorem.

**Weaker statement retained.** P95 gives the exact normalized jump invariant;
E26 records every same-Q endpoint class through Q=19. Future compression
claims must state their ordering and composition law and survive this witness.

**Evidence.** [`../PHASE15B_RUN_RESULTS.md`](../PHASE15B_RUN_RESULTS.md),
`artifacts/phase15b_compression.json`, and the independent Phase 15B verifier.

## Phase 16 — same-Q endpoint carry is always positive

**Status:** `REFUTED` (NG28)

**Exact hypothesis.** If two coefficient-safe words have the same odd count
and endpoint, with `d` longer than `a`, then the integer carry in
`S_d=2^kS_a+m` is positive.

**Why it looked plausible.** All 225,943 same-Q endpoint pairs through Q=17
have positive carry, and shorter paths amplify the normalized affine
correction by `2^k`.

**Smallest stored counterexample (by the supplied audited witness).** At
Q=26, the length-39 word
`111111111101111110101011110010001001100` and length-40 word
`1101101101110011100111011101010101101101` are both safe and reach endpoint
716727426419. Their sources are 155014110207 and 310028220411, with
`S_d=2S_a-3`.

**Failure scope.** Fundamental for positivity, not for quantitative carry
bounds. A common legal suffix preserves the endpoint relation when both
extended paths remain safe.

**Weaker statement retained.** P97 proves `m>-q/3` and
`m>(2^k-q)/3`; negative carry can occur only when `2^k<q`. Future recurrences
must store signed carry and survive this Q=26 pair.

**Evidence.** [`../PHASE16_RUN_RESULTS.md`](../PHASE16_RUN_RESULTS.md),
`artifacts/phase16_theory.json`, and the independent Phase 16 verifier.

## Phase 17 — unbounded coefficient-only predecessor Haar pressure

**Status:** `REFUTED` (NG29)

**Exact hypothesis.** Predecessor words selected only by coefficient threshold,
with their effect combined only through summed 3-adic Haar cylinder mass, can
drive the normalized finite-crossing cutoff arbitrarily far.

**Why it looked plausible.** P105 gives an exact first-passage second-moment
identity and a `t^-2` endpoint-cylinder mass bound. Adding longer predecessor
words appears to delete increasingly many endpoint residue classes.

**Exact obstruction.** Even granting collision-free maximal deletion and
ignoring the fact that the formal deletion exceeds the baseline near height
one, the most favorable remaining-density envelopes are

```text
A_min(U)=(U-1)/3-(1/2)(1-1/U)
R_min(U)=(1/3)log(U)-(1/4)(1-1/U^2).
```

Exact rational logarithm enclosures place `R_min(U)=3log(2)` between
`1083.903` and `1083.904`, where `A_min(U)<360.469`.

**Failure scope.** The refutation is deliberately narrow. It does not cover
the affine correction, one fixed positive ordinary source, actual transition
dependence, canonical representatives, signed carry, or geodesicity.

**Weaker statement retained.** P105's word-mass identity and upper union bound
remain exact. P104's finite r<=4 sieve improves the split to 270, and P106's
fixed r=4 code is suffix-decodable. None is an all-depth exclusion.

**Evidence.** [`../PHASE17_RUN_RESULTS.md`](../PHASE17_RUN_RESULTS.md),
`artifacts/phase17_pressure.json`, and the independent Phase 17 verifier.

## Phase 18 — one-switch sign-pure SCC normal form

**Status:** `REFUTED` (NG30)

**Exact hypothesis.** In a finite affine graph with no mixed SCC, every long
coefficient-safe path with bounded final coefficient is, after deleting
bounded connectors, one positive cycle packet followed by one negative cycle
packet.

**Why it looked plausible.** A positive SCC must supply the discrepancy buffer
needed for long repetition in a later negative SCC. This correctly
characterizes the existence of long bounded-final paths, but it does not force
all other sign-pure SCCs on the condensation path into the same order.

**Exact counterfamily.** Use a four-SCC chain with loop signs `+,-,+,-` and
label the positive loops and connectors by `1`, the negative loops by `0`. For
every `k>=2`, define

```text
n1=floor(log2((3/2)^k))
R=4k+3
n2=floor(log2((3/2)^R))-n1
w_k=1^(2k+1) 0^n1 1^(2k+2) 0^n2.
```

Every prefix coefficient is strictly greater than one, the terminal
coefficient lies in `(1,2)`, and all four packets grow with `k`. The first
negative and later positive packets therefore cannot be bounded connectors.

**Failure scope.** Structural for the one-switch claim, not for finite-state
classification. P108's exact weaker form survives: the SCC condensation gives
a graph-bounded number of sign-pure packets and connectors, possibly with
several sign changes.

**Evidence.** [`../PHASE18_RUN_RESULTS.md`](../PHASE18_RUN_RESULTS.md),
`artifacts/phase18_theory.json`, and the independent Phase 18 verifier.

## Phase 19 — finite-mean affine correction under endpoint tilt

**Status:** `REFUTED` (NG31)

**Exact hypothesis.** At first coefficient passage, the normalized affine
correction has finite mean under the endpoint law `P_+(e)=3/4^e`, so it can be
inserted as a uniformly average-small error into coefficient-only Haar
pressure.

**Why it looked plausible.** The first-passage multiplier overshoot is bounded,
and Phase 17 gives an exact second-moment word law.  Finite stopped means also
grow smoothly, which can conceal the critical tail.

**Exact obstruction.** For `T_t=inf{n>=1:c_n>=t}` and every bounded horizon
`R`, exact change of measure gives

```text
E_+ beta_(T_t cap R) = (1/3) E_- (T_t cap R).
```

Under the source law, Doob's inequality gives
`P_-(T_t=infinity)>=1-1/t`.  Therefore the right side grows at least as
`R(1-1/t)/3`, and monotone convergence proves `E_+ beta_T=infinity` for every
`t>1`.

**Failure scope.** This refutes finite-mean affine bookkeeping, not all
affine-aware methods.  Every fractional moment of order `0<s<1` remains
finite with the explicit P113 bound.  Deterministic valley extraction,
ordinary source height, carry, and transition dependence are outside NG31.

**Smallest reusable falsifier.** The obstruction is symbolic for every
`t>1`; it is not a fitted finite counterexample.  The exact bounded tree
through `R=12` is retained only as an implementation diagnostic.

**Evidence.** [`../PHASE19_RUN_RESULTS.md`](../PHASE19_RUN_RESULTS.md),
[`../research/audits/affine-lift/REPORT.md`](../research/audits/affine-lift/REPORT.md),
`artifacts/phase19_stopped_duality.json`, and the independent Phase 19
verifier.

## Phase 20 — finite parity complexity as an asymptotic classifier

**Status:** boundary recorded; no new NG claim ID.

**Exact invalid shortcut.** A long finite prefix with `p(n)=n+O(1)`, bounded
balance, a Sturmian-looking factor profile, or many terminal zero source lifts
certifies that its infinite continuation is morphic, quasi-Sturmian, balanced,
or eventually lift-stable.

**Why it looked plausible.** The all-contact and P109 prefixes have very small
finite excess, while source 167 has a long zero-lift suffix. These profiles are
strong diagnostics for proposed symbolic models.

**Failure.** A finite word admits infinitely many continuations with different
factor languages and balance growth. In the exact E32 audit, source 167 has
504 trailing zero full-step lift bits in its stored 512-bit eventually cyclic
continuation, but its permanent coefficient safety already fails at step 29.
Conversely, the formal NG22 controllers remain coefficient-safe through the
stored prefix without known positive ordinary sources. Neither direction
supports an asymptotic classification.

**Failure scope.** Fundamental for finite-prefix classification, not for a
theorem that derives an infinite word class or a nonzero lift from an exact
recurrence.

**Weaker statement retained.** P117/P121/P123/P124 give genuine necessary
conditions under their stated hypotheses. E32 is a regression/falsification
set for any proposed recurrence connecting right-special factors, balance,
ordinary height, and P115 lift digits.

**Evidence.** [`../PHASE20_RUN_RESULTS.md`](../PHASE20_RUN_RESULTS.md),
[`../research/audits/parity-complexity/REPORT.md`](../research/audits/parity-complexity/REPORT.md),
and `artifacts/phase20_complexity_audit.json`.

## Mandatory regression rule

Every future universal mechanism must be tested against `2^m-1`, `8^m-5`,
`(110|111)^*`, `A=11101`, `B=1100`, `A^rB^s`, Phase 7 macro id 0, NG21, NG22,
NG23, NG24, NG25, NG26, NG27, NG28, NG29, NG30, NG31, source 167, both
Phase 20 NG22 controllers, and all exact counterexamples above. Passing a bounded regression is necessary
evidence, never a proof of universality.
