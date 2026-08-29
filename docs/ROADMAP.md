# Proof-oriented research roadmap

The ranking is by closeness to a complete Collatz implication, not by ease of
computation. Every proposal begins with a small exact falsification test and
the mandatory adversarial families.

The global branch map and uniform Phase 1–15 terminology are in
[`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md). This file remains the
operational ranking; the synthesis remains the orientation layer.

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

## P0 — Eventual ancestral-prefix barrier

**Target.** Prove H89, `M_star(K_q-1)>H_q`, for all sufficiently large `q`,
and certify the finite first-crossing remainder.

**Why this would solve Collatz.** P90 repairs both cases. P54 handles a finite
coefficient first crossing. If no crossing occurs, P89 gives
`M_star(K_q-1)<=N` for every `q`, while `H_q>q/6` eventually exceeds the fixed
least counterexample `N`.

**Missing theorem.** E25 proves only `M_star(210)>5000000`. P91/P92/P95 give
exact carry and dominance rules, but no all-depth recursion proves sufficient
ancestral pruning or residue growth.

Phase 16 adds P97's signed carry bound and P98's geodesic criterion. For
distinct odd values, P101 reduces a finite crossing to H97 (G250 geodesic) or
H98 (the ultra-low two-sided box). These are sharper subtargets, not proofs of
H89, and P102 keeps the repeated periodic branch separate.

Phase 17 strengthens this finite-crossing split to H104 (G270 geodesic) and
H105 (`N<q/270`, `X<q/135`, `Z<2q/135`) after the internally audited E28
boundary. NG29 shows that coefficient-only summed-Haar predecessor pressure
cannot extend the cutoff without bound; the next state must retain more
ordinary arithmetic.

**Fast falsification test.** Reconstruct NG24--NG28, especially the Q=19
gain-four pair and Q=26 carry -3 pair, and require the proposed state to preserve P91/P97 signed prefix carries,
literal positivity, safety, and ordinary source order. Run the mandatory
families before extending E25--E27.

**Success criterion.** An explicit eventual H89 proof and independently
verified finite remainder. Finite record growth, Haar measure, or a bounded
compression gain is insufficient.

## P0 — Phase 17 G270/H270 exclusions

**Targets.** Prove H104 and H105. H104 excludes positive ordinary-source
all-prefix same-Q geodesic critical words in G270. H105 excludes the H270 box
`N<q/270`, `X<q/135`, `Z<2q/135`.

**Why this helps.** P104 makes the two branches exhaustive for a
least-counterexample finite crossing with distinct odd values; E28 supplies
the internal `N>=300000` boundary. Proving both removes that branch. P102
still leaves repeated periodic values as a separate cycle obligation.

**Missing theorem.** H104 needs a positivity/ordinary-height invariant absent
from the formal all-contact 2-adic word. H105 needs a two-sided
source/endpoint certificate for a length-Theta(q) history whose two ordinary
heights are O(q). P105/NG29 show that summed coefficient-only Haar pressure
cannot supply that invariant by itself.

**Fast falsification test.** H104 must survive NG17, P73, NG24--NG29, and
E27/E29. H105 must retain both canonical residues, signed carry, literal
safety, and ordinary height; reject a state at the first NG19 or NG24--NG29
collision.

**Success criterion.** Repository proofs for both branches with an effective
finite remainder. A contact/geodesic-only contradiction, raw address count,
or a proof that silently assumes odd-value distinctness on a cycle fails.

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

Phase 13 now supplies the exact renewal code P77, pressure bounds P78, and the
valuation-conditioned positive-source transfer P79. P80 proves that either a
uniform endpoint bound
`N_i^(3)(H)<=exp(epsilon*i)H*sigma^i` or its two-sided analogue with
`H^2*tau^i` would close this branch. NG23 shows that raw Haar volume cannot
replace that missing deterministic ordinary-height theorem: `u=1,H=2`
already has count 1 and predicted volume `2/3`.

Phase 14 supplies a second exact reduction. P81 classifies every affine
coalescent source rewrite, and P82 says that a least positive permanent-safe
counterexample source must be irreducible under all positive downward P81
rewrites. E23 finds 5,949 such rewrite pairs through total `Q<=13`. P83--P85
add run-sensitive thresholds, block decrement, and eventual rational-height
bounds. NG24 shows why this is not yet a recursive proof: coalescent endpoint
classes are stable under common right suffixes but not under common prefixes.

Phase 15 broadens the least-source reduction to P86 surplus dominance across
different odd counts and P87 safe suffixes extracted from unsafe targets. E24
exhausts this frontier through Q=17, while NG25/NG26 refute same-Q and
safe-target completeness. P88 identifies the `{1,2}`-gap endpoint-injective
core; all 32,596 safe words in its Q=17 layer survive competitors with
`Q_b<=Q_d`. This is a cutoff fact, not a persistent-core theorem.

Phase 15B adds P89 ancestral minimality, P91/P92 carry-aware uniform cylinder
dominance, P93/P94 canonical finite renewal decomposition, and P95 shifted
jump classes. E25 proves only `M_star(210)>5000000`; E26 remains bounded at
Q=17/19. P96's 3-adic complement is distributional, and NG27 refutes a
universal gain-three compression bound.

Phase 16 adds actual local transition restrictions P99 and the P100 mod-72
packing law. These close neither infinite-safe H72 nor the periodic branch;
P100's distinctness and finite-crossing hypotheses must not be imported into
an infinite/repeated setting without proof.

Phase 17 adds P105's exponent first-passage identity and P106's
suffix-decodable r=4 subcode. NG29 proves a ceiling only for the explicitly
scoped coefficient-only summed-Haar calculus. It neither closes H72 nor
refutes affine-aware, fixed-source, transition-aware, or carry-aware methods.

Phase 18 adds a design-level finite-state trichotomy. P107/P108 prove that a
closed sign-pure SCC graph has bounded normalized affine correction and a
finite-stage Type I/II structure. P109 shows that every mixed SCC admits a
formal balanced survivor with linear correction; P110 excludes only its
canonical balanced schedule conditionally on EXT07. P111 isolates eventual
zero source lifts as the fixed-positive-integer boundary. NG30 refutes a
single positive-then-negative packet order. No current H72 abstraction is a
closed finite graph, so these theorems constrain future models rather than
close the branch.

**Fast falsification test.** Apply the proposed exclusion to the exact finite
orbits, all-contact prefixes, NG21, both NG22 formal exponent/2-adic sources,
the NG23 `u=1,H=2` obstruction, the NG24 prefixed collision, both Phase 15
  cross-Q/unsafe-target witnesses, NG27--NG30, the `{1,2}` core, and every mandatory
adversarial family. Reject any proof that identifies a general
2-adic source with a positive ordinary integer, drops the per-address lattice
`+1`, treats `(Q,r3)` as a prefix-closed state, assumes one-switch SCC order,
or promotes finite scarcity to an eventual statement. Any proposed finite
automaton must prove prefix completeness and track P111 source lifts.

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

Phase 13 gives a more focused infinite-tail version. Renewal address masses
factor as `sigma^i` and `tau^i`, and the ordinary source determines the initial
one-run through `v2((S+1)/4)=v2(C_w)`. What remains missing is a theorem that
turns this coupled valuation/affine recurrence into subexponential endpoint or
two-sided canonical-representative counts. Standard Haar measure is
insufficient by NG23.

Phase 14 gives a finite reduction mechanism rather than a volume bound. Any
proof that every sufficiently long positive address admits a P81 downward
rewrite would eliminate the least-source branch by P82, but it must carry
enough prefix information to survive NG24. The finite normal forms in E23 do
not establish such eventual reducibility.

Phase 15 replaces same-Q irreducibility by the stronger Pareto state
`(ordinary source, terminal coefficient)` at each endpoint and permits valley
suffixes of unsafe targets. An all-depth recursion must retain cross-Q carry
data, distinguish NG24--NG26, and explain the endpoint-injective `{1,2}` core.
Finite survivor counts alone do not imply pressure decay.

Phase 15B strengthens the candidate minimum from `M` to `M_star` and exposes
the exact P91 carry plus P95 jump state. Any useful recursion must distinguish
NG27's gain-four collision rather than impose a bounded compression gain.

P97/NG28 additionally require a signed carry state; Q<=17 carry positivity is
only E27 finite evidence.

**Fast falsification test.** First reconstruct NG23--NG28 and all E22--E27
finite ratios, then measure the joint `(B,r2,r3,C_w)` Pareto frontier in exact
dynamic-programming/meet-in-the-middle slices. Attack every proposed constant
or monotonicity with macro id 0, NG22, and `A^rB^s` before scaling.

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
