# Proof-oriented research roadmap

The ranking is by closeness to a complete Collatz implication, not by ease of
computation. Every proposal begins with a small exact falsification test and
the mandatory adversarial families.

## P0 — Eventual critical-prefix barrier

**Target.** Prove `M(K_q-1) > H_q` for all sufficiently large `q`.

**Why this would solve Collatz.** By P54, a least positive counterexample whose
coefficient first crosses below one at that barrier would have to satisfy the
opposite inequality. Eventual proof plus exact checking of the finite remainder
closes the least-counterexample route.

**Missing theorem.** An effective eventual lower bound for the least positive
coefficient-safe representative `M(k)` strong enough to dominate `H_q`.

**Fast falsification test.** Apply any proposed bound to all exact `M(k)` data,
the known failures `(17,27),(29,27),(41,703)`, and generated prefixes from
`2^m-1`, `8^m-5`, `(110|111)^*`, and `A^rB^s` before proving it.

**Success criterion.** A repository-contained proof with explicit threshold,
or a finite certificate format for the remainder, independently audited
without external record-minimality assumptions.

## P1 — Renewal-ladder dropping-safe barrier

**Target.** Prove H70, the eventual inequality used by P70:

```text
Delta_down_Kq(floor(H_q)+floor((q-1)/3))
  > floor((q-1)/3).
```

**Why this helps.** P69 is unconditional and exhaustive: this target would
eliminate every nonperiodic counterexample whose tail minima have finite
coefficient crossings. A complete Collatz proof would still have to exclude a
nontrivial cycle and an infinite coefficient-safe tail.

EXT07/P74 now provide a separate conditional bypass: if the external
Garcia--Tal--Heppner sparsity input is admitted, every nonperiodic positive
orbit is eventually permanently coefficient-safe. H70 remains valuable as an
internal, external-input-independent theorem and must not be reported as
proved by that bypass.

**Missing theorem.** A cross-cylinder ordinary-height lower bound for
dropping-safe pairs. P71 closes all affine margin inequalities inside one fixed
parity cylinder, but retains all `2^L` residue classes. No sound quotient/carry
state merges them.

**Fast falsification test.** Rebuild the exact failures
`q=17,22,27,29,32,34`, all witnessed by `(27,31)`, and require every proposed
merge to survive NG19 plus the universal NG20 pairs `2^k-5,2^k-1`. Treat every
empty-set finite pass as vacuous.

**Success criterion.** A repository proof of the eventual inequality with an
effective threshold and independently certified finite remainder. Separately
state which argument excludes the other two P69 branches.

## P1 — Infinite-safe-tail transition packing

**Target.** Prove H72: combine P72/P75 with actual odd-orbit transitions,
positivity, or effective ordinary-height information until no infinite
coefficient-safe positive-integer tail can satisfy the resulting law.

**Why this helps.** This would eliminate the permanent-safe nonperiodic branch
of P69. Under EXT07/P74 the finite-crossing nonperiodic branch is conditionally
absent; a nontrivial-cycle exclusion remains separate.

**Missing theorem.** P75 conditionally upgrades P72 to reciprocal summability,
`a_j->infinity`, and an external `O((A+1)2^(beta A))` small-defect count. P76
adds exact real/2-adic rational shadows. NG21 shows mod-6 packing is
exponent-sharp, while NG22 shows the strengthened analytic conditions and an
odd 2-adic source are still mutually compatible. A successful proof must use
positive ordinary-integrality, effective reduced height/gcd, or a genuinely
stronger orbit-transition invariant.

**Fast falsification test.** Apply the proposed exclusion to the exact finite
orbits, all-contact prefixes, NG21, the NG22 formal exponent/2-adic source, and
every mandatory adversarial family. Reject any proof that identifies a general
2-adic source with a positive ordinary integer or promotes finite scarcity to
an eventual statement.

**Success criterion.** An orbit-specific arithmetic theorem that excludes
every positive ordinary integer permanent-safe source, with an independently
checkable finite remainder. A stronger exponent unsupported by new transition
data, or a contradiction that also rejects NG22 without using positivity,
does not meet this criterion.

## P1 — Structural lower bounds for `M(k)`

**Target.** Derive recursive, combinatorial, or Diophantine inequalities that
force every coefficient-safe residue representative to grow effectively.

**Why this would solve Collatz.** A bound such as
`M(k) >= k^{5.117+epsilon}` with effective constants would plausibly dominate
the current contextual polynomial upper bound for `H_q`.

**Missing theorem.** A bridge from prefix-density constraints to the ordinary
size of the least compatible positive residue; modulus `2^k` alone supplies no
such bridge.

**Fast falsification test.** Compute the proposed recursion exactly on the
known `M(k)` records and search for a smaller compatible residue at the first
unsupported depth.

**Success criterion.** An explicit monotone lower bound, composable across
prefix blocks and valid for every admissible word, with a proof that survives
carry behavior.

## P1 — Anti-concentration of inverse parity residues

**Target.** Prove that high-correction coefficient-safe parity words cannot
have unusually small positive representatives under the inverse parity map.

**Why this would solve Collatz.** A uniform small-residue exclusion gives the
needed lower bound for `M(k)` directly.

**Missing theorem.** A deterministic, `q`-uniform separation inequality over
the generalized Ballot language. Phase 7 fixed-layer Pareto fronts and
fixed-`(k,q)` rigidity do not supply this Archimedean minimum bound.

**Fast falsification test.** Measure the joint `(B,r2)` Pareto frontier in exact
dynamic-programming/meet-in-the-middle slices, beginning with Phase 7's
`q=1,3,5,17` records; attack monotonicity with macro id 0 and `A^rB^s` before
scaling.

**Success criterion.** An effective inequality for the minimum, or a tail
bound strong enough to imply it after a union bound whose constants and
dependencies are rigorous.

## P1 — Two-sided near-diagonal residue exclusion

**Target.** Prove C04: at the q0 first crossing, exclude canonical residues
`r2,r3` satisfying `3^q*r2+B=2^K*r3`, `0<=r3-r2<=4142380786`, and
`r3=7 or 19 mod 36` in the Phase 9 size window.

**Why this helps Collatz.** Under P54, P57--P61, and their stated
least-counterexample/external inputs, C04 would remove the q0 near-return
endpoint. A parameterized theorem for all later barrier records, together with
the finite remainder, would be needed for a full implication. C04 is the most
direct new arithmetic prototype produced by Phase 9, not a complete route by
itself.

**Missing theorem.** A simultaneous Archimedean and 2-adic/3-adic
anti-concentration theorem for generalized-Ballot parity words. Contact count
and weighted pressure alone cannot supply it because NG17 is refuted.

**Fast falsification test.** Reconstruct the exact q<=21 layer digests, attack
any compressed state with examples that share its visible fields but have
different carries, and include the full mandatory adversarial set. Never treat
zero bounded survivors as an asymptotic conclusion.

**Success criterion.** A lossless recursive or meet-in-the-middle exclusion
certificate at q0 with an independent verifier, or an exact near-diagonal
counterexample that determines which proposed state discarded necessary
information.

Phase 10 gives the exact one-residue formulation
`rho=[B*3^(-q)]_(2^K-3^q)`, with `rho=d`, `m=N`, `X=m+rho`, and `4|rho` in the
q0 box. This removes one residue variable but does not determine `B mod D`.

## P1 — Long-safe pair spacing

**Target.** Prove C05,
`Delta_(K0-1)(2^72)>4142380786`, or find an exact counterexample.

**Why this helps.** P64 conditionally makes both `N` and `X=N+d` safe through
`K0-1`; C05 would therefore exclude every positive q0 gap `d<=W`. The `d=0`
case would still require the gap/rational-cycle arithmetic.

**Missing theorem.** A scalable cylinder or difference-state lower bound that
connects coefficient-safe depth with ordinary spacing up to height `2^72`.
Nested-set deletion gives only nondecrease; NG18 refutes strict growth at every
depth.

**Fast falsification test.** Reconstruct the Phase 10 spacing records through
`H=1,500,000`, beginning with `Delta_2=Delta_3=4`, and attack any proposed
recursion with all mandatory adversarial families before increasing depth.

**Success criterion.** An exact certificate accepted by a logically
independent verifier at `(k,H)=(K0-1,2^72)`, or the least exact safe pair at
distance at most W with its full cylinder witnesses.

P66/P67 now split every positive target gap into the 30 cases
`2<=h=v2(d)<=31`. A lossless continuation state must retain at least the
common odd count, odd normalized gap, inherited coefficient surplus, and both
tail residue states. E16 supplies exact finite witnesses for falsifying a
proposed compression: `R_h(1500000)` is nonmonotone in h and peaks at 213 for
`h=7`.

P68 now proves that `(h,a,u,orientation,y mod 2^L)` is lossless for the next
`L` steps. NG19 records the matching obstruction: at `L=12`, every shortened
window `b<L` has an exact opposite-outcome collision below `H=20000`. The next
useful experiment must therefore add composable arithmetic structure—such as
carry intervals, cylinder transitions, or a provable dominance relation—rather
than merely choosing a smaller fixed residue window or extending the same scan.
P71 supplies exact interval closure inside each fixed residue cylinder, but no
cross-cylinder dominance; that merge is now the precise next certificate
problem shared by C05 and the new H70 route.

## P1 — Arbitrary reverse-residue barrier

**Target.** Extend P62 from a coefficient barrier and the lower-mechanical
family to every positive composition of reverse exponents.

**Why this helps.** Phase 9 eliminates all reverse coefficients before
`(a,L)=(615582794569,975675645481)` in the conditional q0 scenario, but only a
valid-path residue theorem can turn coefficient scarcity into an orbit
obstruction.

**Missing theorem.** A recursive forbidden-residue invariant that retains the
affine constant and endpoint minimality while compressing arbitrary exponent
words without losing carries.

**Fast falsification test.** Enumerate all compositions only at small `a`,
compare them with the mechanical representative, and search for two words with
the same proposed compressed state but opposite minimality classifications.

**Success criterion.** An exact state recursion whose verifier covers every
composition in a stated range and whose proof extends beyond that finite
range; zero survivors in one mechanical subfamily is insufficient.

## P2 — Moving rational shadows and simultaneous 2-adic/3-adic constraints

**Target.** Show that any indefinitely coefficient-safe positive path must
create rational shadow centers of unbounded height, then prove that the needed
simultaneous approximations are impossible or force descent.

**Why this would solve Collatz.** It would replace the refuted finite shadow
dictionary with an arithmetic obstruction that grows with depth and could
exclude an infinite critical path.

**Missing theorem.** A quantitative height-growth lemma plus a simultaneous
approximation bound linked to positivity and cylinder congruence.

**Fast falsification test.** Use `A^rB^s` records to attack every fixed-margin,
fixed-height, or four-center version; verify that the proposal also handles
`(110|111)^*`.

**Success criterion.** A proved lower bound on required shadow height that
translates into an explicit lower bound for `M(k)` or a direct contradiction.

## P2 — Arbitrary contracting mixed blocks

**Target.** Resolve C03 for arbitrary finite words in `{A,B}*`, or find its
smallest exact counterexample.

**Why this helps Collatz.** Phase 8 proves descent for every contracting
ordered word `A^rB^s`, but contact-return paths can interleave blocks. A common
potential for all contracting interleavings would control a broader mandatory
adversarial mechanism, though it would not by itself cover every Collatz word.

**Missing theorem.** A well-founded rank, modular separation, or endpoint
inequality for the partial integer dynamics
`A:32u->81u`, `B:16u+108->9u+108`. Exact search through block length 18 has no
counterexample, but finite survival cannot establish C03.

**Fast falsification test.** Preserve the exact Phase 8 enumeration, whose
79,184 contracting words include 79,166 genuinely mixed words, and test any
candidate potential first on `BBA`, the minimum mixed-margin record, as well
as long near-critical `A^rB^s` words and Phase 7 macro id 0.

**Success criterion.** A symbolic proof accepted independently for every
finite word, or an exact positive integral counterexample with its full parity
and affine certificate.

## P2 — Extend exact barrier certificates

**Target.** Extend independently verified coverage beyond `q=4960` and replace
external dropping-record minimality where practical.

**Why this helps Collatz.** It reduces the finite remainder once an eventual
theorem is found and tests whether proposed structure predicts difficult
records.

**Missing theorem.** None for a finite extension; the limitation is certificate
size and search strategy. This task cannot supply eventuality by itself.

**Fast falsification test.** Target the next uncovered record and compare any
new pruning rule with the independent verifier before broad scanning.

**Success criterion.** New compact exact certificates, tamper-rejection tests,
an independent verifier result, and SHA-256 manifest, with no asymptotic claim.

## P3 — Predecessor-tree and density approaches

**Target.** Find a quantitative bridge from predecessor abundance or
almost-everywhere descent to the particular cylinder of a least counterexample.

**Why this could solve Collatz.** Such a bridge could force the exceptional
orbit to intersect a verified descending set.

**Missing theorem.** Exceptional-set control or invariance strong enough for a
single designated integer; global density comparison is insufficient.

**Fast falsification test.** State the exact sets and density notions, then
construct abstract sparse sets satisfying both marginal bounds but having empty
intersection. If this is possible, the proposed bridge is incomplete.

**Success criterion.** A rigorous intersection/transport theorem that applies
to the least-counterexample arithmetic set, with all external results cited at
the exact theorem level.

## P4 — Bounded finite-state or modular experiments

**Target.** Use bounded models to falsify new conjectures, discover exact
templates, or generate candidate lemmas.

**Why this does not currently solve Collatz.** Phases 1–5 show that fixed depth,
modulus, state, or shadow dictionaries retain supercritical or refill-driven
frontiers.

**Missing theorem.** Any unbounded well-founded invariant that connects the
finite model to all depths.

**Fast falsification test.** Run the mandatory adversarial set at depths well
beyond the state horizon and mine the smallest counterexample.

**Success criterion.** A precise new asymptotic hypothesis or proof rule,
rather than a larger success percentage. Without that, stop after recording
the obstruction.

## Stop criteria for large computation

Do not spend a large compute budget unless the experiment has:

1. a precise claim ID and status;
2. a finite scope and early stop condition;
3. a fast adversarial counterexample pass;
4. a planned independent verifier and artifact;
5. a stated interpretation boundary;
6. a reason the result changes P0/P1 knowledge rather than only extending a
   previous depth.
