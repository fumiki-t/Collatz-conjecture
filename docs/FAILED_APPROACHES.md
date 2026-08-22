# Failed and deprioritized approaches

Failures are retained as research assets. Each entry states the precise scope
that failed; it must not be read as a theorem excluding every possible
strengthening of the idea.

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

## Mandatory regression rule

Every future universal mechanism must be tested against `2^m-1`, `8^m-5`,
`(110|111)^*`, `A=11101`, `B=1100`, `A^rB^s`, and all exact counterexamples
above. Passing a bounded regression is necessary evidence, never a proof of
universality.
