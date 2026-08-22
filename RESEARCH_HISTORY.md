# Collatz conjecture research history

This is the chronological human-readable record of the repository. It is
designed to preserve both successful results and failed mechanisms when the
original chat is unavailable. The live status is in
[`docs/STATUS.md`](docs/STATUS.md); stable claim IDs are in
[`docs/CLAIMS_LEDGER.md`](docs/CLAIMS_LEDGER.md).

**The Collatz conjecture remains `OPEN`. Nothing in Phases 1–6 proves or
disproves it.**

## 1. Conventions and evidence policy

The default map is the shortcut Collatz map

\[
T(n)=\begin{cases}
n/2,&n\equiv0\pmod2,\\
(3n+1)/2,&n\equiv1\pmod2.
\end{cases}
\]

For a parity prefix of length `k`, let `q_k` be its odd-step count. Then

\[
T^k(n)=\frac{3^{q_k}n+B_k}{2^k}.
\]

On the exact cylinder `n=r+2^k t`, this becomes

\[
T^k(n)=y+3^{q_k}t.
\]

A prefix is coefficient-safe when `3^{q_j} >= 2^j` for every
`1 <= j <= k`. Certificate arithmetic uses arbitrary-precision integers and
exact rational numbers. Search code and verifier code are separate, and an
`OPEN` record is never a proof rule.

The mandatory status labels are `VERIFIED_THEOREM`, `VERIFIED_FINITE`,
`CONDITIONAL`, `EXTERNAL_THEOREM`, `EXTERNAL_EVIDENCE`, `HEURISTIC`,
`CONJECTURE`, `REFUTED`, `RETRACTED`, and `OPEN`.

## 2. Pre-certificate period

### Least counterexample and coefficient drift

The durable starting observation is that a least positive counterexample `N`
could never visit a smaller positive integer. Whenever
`3^{q_k} < 2^k`, the affine formula constrains `N` through the correction
`B_k`. This ties a possible first coefficient crossing to approximation
between powers of 2 and 3 and to the critical density `log 2 / log 3`.

This observation survived every later phase, but by itself it supplies no
lower bound for the least compatible positive residue.

### Local word exchange

An early proposal attempted to sort parity words by local exchanges
`01 <-> 10`, hoping that an extremal Christoffel/Sturmian word would maximize
the affine correction. It failed because smooth changes in a real affine
quantity do not control carry jumps in the least positive residue modulo
`2^k`.

**Status:** `REFUTED` as a universal monotonicity mechanism.

### Retracted strong claims

Early exploratory claims about mandatory numbers of “mountains,” very large
lower bounds, or new kernel maps were withdrawn. Their derivations applied a
cycle-only condition to a nonperiodic trajectory, relied on unchecked
computation, or failed to prove equivalence with the original Collatz map.

**Status:** `RETRACTED`. They are retained in the negative ledger so that the
same logical shortcuts are not rediscovered.

## 3. Finite-state and rational-shadow no-go lesson

Positive integers can reproduce dangerous local behavior for arbitrarily long
finite times. The central examples are

- `2^m-1`, shadowing the negative fixed point `-1`;
- `8^m-5`, shadowing the negative cycle through `-5,-7,-10`;
- arbitrary safe concatenations in `(110|111)^*`;
- later, the mixed blocks `A=11101`, `B=1100`, and `A^rB^s`.

Consequently, a proof based only on a bounded observation window, fixed
modulus, fixed finite local dictionary, or bounded-state Lyapunov correction
is incomplete unless it includes an unbounded arithmetic mechanism. Finite
models remain valuable for certificates, counterexamples, and lemma discovery.

## 4. Phase 1–2 — adaptive affine certificates

**Milestone:** `main` at `42dc629`  
**Acceptance record:** [`RUN_RESULTS.md`](RUN_RESULTS.md)

Phase 1 represented each parity cylinder exactly and implemented the rules
`SPLIT`, `DESCENT`, `FINITE_TAIL`, `DIRECT`, and explicit `OPEN`. The
independent verifier imports neither the search nor the model implementation
and reconstructs every accepted inequality and direct witness.

### `VERIFIED_FINITE` results

- Depth 26: 190,069 `DESCENT`, 1,227,442 `SPLIT`, and 1,037,374 `OPEN`.
- Literal shortcut iteration agrees with the cylinder evaluation for all
  16,777,214 starts `2 <= n < 2^24`, totaling 54,413,413 shortcut steps.
- Exact coefficient-safe counts include
  `a_10=64`, `a_15=1295`, `a_20=27328`, `a_22=93222`, and
  `a_26=1037374`.

The depth-limited `OPEN` set is the generalized Ballot language whose every
prefix obeys `3^{q_j} >= 2^j`. This explains why coefficient information alone
retains a very large frontier; it does not identify which finite words extend
to a positive infinite counterexample.

### Phase 2 short-shadow dictionary

The precise dictionary required a prefix or suffix containing at least three
consecutive copies of a block of length at most 16. It explains 913,466 of the
1,037,374 depth-26 survivors and leaves 123,908 unexplained. The smallest
unexplained representative is 27, with exact parity word
`11011111010110111011110100`.

**Status:** `REFUTED` as a complete fixed short-period dictionary.

### What this result does not prove

It does not close any `OPEN` node, establish asymptotic survivor growth, or
rule out every possible parametric macro language.

## 5. Phase 3 — mixed binary/ternary certificates

**Branch / milestone:** `feat/phase3-mixed-merge` / `d7bb6d9`  
**Acceptance record:** [`PHASE3_RUN_RESULTS.md`](PHASE3_RUN_RESULTS.md)

Phase 3 introduced exact binary and ternary `LatticeNode` refinements and a
bounded `REVERSE_MERGE` rule. The verifier reconstructs divisibility,
positivity, strict smaller-family inequalities, and the full forward affine
path without importing the search model.

### `VERIFIED_FINITE` results

- Binary frontier: 27,328.
- Stored records at ternary levels 1 and 2: 47,610 and 95,220.
- Accepted reverse-merge closures: 43,198.
- Final mixed `OPEN`: 79,350.
- Exact boundary-gap audit: through depth 36, with minimum 1 at depth 5 and no
  counterexample in the tested domain.
- `(110|111)^*`: 4,096 words checked without a coefficient violation.

The smallest unresolved family is
`n(t)=27+9437184t`, with
`T^20(n(t))=395+129140163t`. Unresolved populations progress from 15,870 to
31,740 to 79,350 in the configured refinement.

### What this result does not prove

Reverse merges are valid local certificates, but bounded mixed refinement is
not an asymptotic closure theorem. The tested frontier is supercritical rather
than decreasing.

## 6. Phase 4 — exact first return modulo 9

**Branch / milestone:** `feat/phase4-return9` / `909fad1`  
**Acceptance record:** [`PHASE4_RUN_RESULTS.md`](PHASE4_RUN_RESULTS.md)

Using the externally established strongly sufficient section `n = 2 mod 9`,
Phase 4 built an exact prefix-free first-return code. The configured finite
representation has 52 templates and the full code has Kraft sum 1. The
parametric recurrence reduces to refill constants `1`, `5`, and `21`.

### `VERIFIED_FINITE` results

- Direct audit: 1,864,135 section elements below `2^24` and 7,340,021 shortcut
  steps.
- Certificate: 34,788 records, of which 10,335 close and 23,785 are `OPEN`.
- At exact return depth 3: 33,696 cylinders, with 9,911 closed at that level.
- Smallest unresolved family:
  `47+18432t -> 155+59049t` after three returns.

### Ranking failure

Monotone one-return descent fails at `11 -> 20` and `47 -> 182`. Refill
transitions prevent the tested constants-only rank from becoming well founded.
Negative diagnostic cycles cannot be used as closure rules for positive
families.

### What this result does not prove

Kraft sum one and a finite return dictionary do not imply subcritical
unresolved growth. The configured run also leaves all `a>8` return families
outside its finite dictionary.

## 7. Phase 5 — mod-27 returns and dangerous cycles

**Branch / milestones:** `feat/phase5-dangerous-cycles` / `39c90b4`,
`4444d7c`  
**Acceptance record:** [`PHASE5_RUN_RESULTS.md`](PHASE5_RUN_RESULTS.md)

Phase 5 used the section `{1,11,20,26} mod 27`. Deleting that section from the
unit graph leaves a DAG, so first returns have length at most 9.

### Exact graph and path results

- 52 labeled first-return templates.
- 108 labeled simple cycles up to cyclic rotation.
- Exactly four noncontracting simple words:
  `1`, `101`, `1101`, and `011101`.
- Their rational fixed points are `-1`, `-7`, `-23/11`, and `-146/17`.
- Every other simple cycle has multiplier at most `27/32`.
- For positive 20-to-20 paths with no internal 20 or 26, `101` is the unique
  noncontracting simple path; every other path satisfies
  `R(x) <= (27x+46)/32 < x`.
- Direct audit: 2,485,513 section integers below `2^24` and 7,162,840 shortcut
  steps.

### H5-A/H5-B bounded failures

The quantified H5-A surrogate retains 2,141 bounded counterexamples. Its
smallest recorded family occurs at return depth 20:
`461826978031+474989023199232t`. The bounded H5-B search retains 80 candidates;
the smallest starts at 362,638 and switches `C146 -> C23` at return depth 5.
These results refute the configured surrogates, not every possible unbounded
switch-cost lemma.

### Adversarial blocks beyond four centers

Define

\[
A=11101,\qquad F_A(x)=\frac{81x+73}{32},
\]

\[
B=1100,\qquad F_B(x)=\frac{9x+5}{16}.
\]

Then `W=AB=111011100` has

\[
F_W(x)=\frac{729x+817}{512}
\]

and fixed point `-817/217`, outside the four simple-cycle centers. For
`A^rB^s`, the multiplier is

\[
\frac{3^{4r+2s}}{2^{5r+4s}}.
\]

Eight exact record pairs are
`(1,1),(2,3),(5,8),(18,29),(31,50),(44,71),(57,92),(184,297)`; the last has
multiplier excess below `2^-13`. The conclusion that multipliers above one can
approach one arbitrarily closely additionally uses an external
irrational-rotation density theorem.

**Status:** four-shadow completeness is `REFUTED` by `W`; the eight records are
`VERIFIED_FINITE`; arbitrary closeness is `EXTERNAL_THEOREM` plus checked
premises.

### What this result does not prove

The exact graph classification is not a universal finite-shadow
classification. No well-founded rank for arbitrary precision and repetition
count was synthesized.

## 8. Moving-shadow hierarchy

For a coefficient-safe word with

\[
F_w(x)=\frac{3^q x+B_w}{2^k},
\]

the correction obeys the useful exact bound `B_w <= q 3^{q-1}`. Together with
the mixed-block counterexamples, this suggests replacing fixed rational
centers by approximants whose arithmetic height grows with the path.

The working hypothesis is that an indefinitely critical positive trajectory
would have to generate rational approximants of unbounded height. No theorem
yet converts that height growth into descent or a lower bound for `M(k)`.

**Status:** `CONJECTURE` / strategic interpretation, not a certificate rule.

## 9. Phase 6 — critical-prefix barrier

**Branch / milestone:** `feat/phase6-critical-prefix-barrier` / `8684d53`  
**Acceptance record:** [`PHASE6_RUN_RESULTS.md`](PHASE6_RUN_RESULTS.md)

Define

\[
M(k)=\min\{n\ge2:3^{q_j(n)}\ge2^j\text{ for }1\le j\le k\},
\]

\[
K_q=\lceil q\log_2 3\rceil,
\]

\[
B_q^{\max}=\sum_{j=0}^{q-1}3^{q-1-j}
2^{\lfloor j\log_2 3\rfloor},\quad
D_q=2^{K_q}-3^q,\quad H_q=B_q^{\max}/D_q.
\]

### P54 conditional barrier

If `N` is a least positive counterexample and its coefficient first crosses
below one after `K_q` shortcut steps with `q` odd steps, the independently
audited algebra gives

\[
M(K_q-1)\le N\le H_q.
\]

Therefore `M(K_q-1)>H_q` rules out that first-crossing configuration. If this
inequality is proved for every sufficiently large `q` and the finite remainder
is checked, this route would exclude a positive indefinitely coefficient-safe
counterexample.

**Status:** `CONDITIONAL`. The implication is checked; eventuality is missing.

### `VERIFIED_FINITE` Phase 6 results

- Every `H_q` through `q=200000` was scanned using exact integer arithmetic.
  There are 37 record indices; the last is
  `q=190537`, `K_q=301994`, `floor(H_q)=710220447737`.
- Five independent binary-cylinder certificates establish 14 barrier-record
  inequalities at
  `q=1,3,5,94,147,200,253,306,971,1636,2301,2966,3631,4296`.
- Record monotonicity extends exact continuous coverage to every
  `94 <= q <= 4960`.
- The largest shared certificate is `M(232)>1358717` with 3,219 nodes.
- Direct exact search through 1,500,000 determines `M(k)` through `k=223` and
  finds 13 coefficient-stopping records.
- Exact early failures are `(q,N)=(17,27),(29,27),(41,703)`.
- For `66 <= K_q <= 224`, the smallest exact ratio is at
  `q=46`, `K_q=73`, `M(72)=703`, and exceeds 4 exactly.

### External evidence kept separate

The repository reproduces the stated dropping and coefficient-stopping times
for 35 supplied record holders, but does not prove their global record
minimality. Only under that external assumption does the evidence cover every
`66 <= K_q <= 1005`.

The Wu–Wang irrationality-measure estimate and the contextual conversion
`H_q=O(q^5.117)` are not proved here and are not inputs to a finite
certificate.

### What this result does not prove

Finite coverage through `q=4960`, the scan through 200,000, and the external
record evidence do not imply `M(K_q-1)>H_q` eventually. No asymptotic lower
bound for `M(k)` is known.

## 10. Predecessor-tree and density detour

Strong external results count many predecessors or show descent for almost all
starting values. A naive attempt to combine those densities with a least
counterexample fails: two global density statements need not control one
designated exceptional integer or its thin arithmetic cylinder.

**Status:** `REFUTED` as a standalone density comparison. A future approach
would need an explicit transport, invariance, or intersection theorem for the
least-counterexample set.

## 11. Numerical consistency audit

The canonical figures above were resolved using this priority:

1. independent verifier result;
2. latest committed phase result;
3. older prose.

No contradictory phase counts were found. Apparent differences have distinct
scopes:

- Phase 4 has 34,788 total certificate records and 33,696 depth-3 cylinders;
  10,335 records close overall while 9,911 close at depth 3.
- Test totals 117, 129, 137, 145, and 149 belong to successive repository
  states, not competing reruns of one commit.
- Phase 5 H5-A/H5-B results concern quantified bounded surrogates; the original
  legacy labels were underspecified and are not universal theorem claims.
- `H_q=O(q^5.117)` is contextual external arithmetic, not a verified internal
  result.

## 12. Current strategy

The primary target is

\[
M(K_q-1)>H_q\qquad\text{for all sufficiently large }q.
\]

Highest-priority directions are deterministic anti-concentration of inverse
parity residues, recursive lower bounds for `M(k)`, arithmetic structure at
`H_q` records, and moving rational shadows only insofar as they explain small
`M(k)`. Exact certificate extension is useful for the finite remainder and for
testing structural conjectures, but it is not the missing theorem.

Bounded finite-state and modular searches are now primarily falsification
tools. Every universal proposal must survive `2^m-1`, `8^m-5`,
`(110|111)^*`, `A`, `B`, and `A^rB^s`.

## 13. Reproduction and immutable evidence

- Phase 1–2: [`RUN_RESULTS.md`](RUN_RESULTS.md)
- Phase 3: [`PHASE3_RUN_RESULTS.md`](PHASE3_RUN_RESULTS.md)
- Phase 4: [`PHASE4_RUN_RESULTS.md`](PHASE4_RUN_RESULTS.md)
- Phase 5: [`PHASE5_RUN_RESULTS.md`](PHASE5_RUN_RESULTS.md)
- Phase 6: [`PHASE6_RUN_RESULTS.md`](PHASE6_RUN_RESULTS.md)
- Current manifest: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

The SHA-256 of `artifacts/SHA256SUMS` after Phase 6 is
`1f7d1b4c564a01c9af7ea82abaa949df3444ed757bfc09faad00a526e2487653`.
Generated JSON/CSV/certificates must be regenerated, not hand edited.

## 14. Current one-paragraph handoff

Phases 1–5 built a robust exact-computation framework and showed why bounded
state, fixed period, fixed shadow, and finite mixed-modulus mechanisms leave
large unresolved families. Phase 6 supplies the most direct current reduction:
a least counterexample at its first coefficient crossing must satisfy
`M(K_q-1) <= N <= H_q`. Exact certificates cover a substantial finite range,
but the repository has no eventual lower bound for `M(k)`. Future work should
focus on arithmetic anti-concentration of coefficient-safe parity cylinders,
not merely greater finite search depth.
