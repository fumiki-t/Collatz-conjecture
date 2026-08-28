# Collatz conjecture research history

This is the chronological human-readable record of the repository. It is
designed to preserve both successful results and failed mechanisms when the
original chat is unavailable. The live status is in
[`docs/STATUS.md`](docs/STATUS.md); stable claim IDs are in
[`docs/CLAIMS_LEDGER.md`](docs/CLAIMS_LEDGER.md).

**The Collatz conjecture remains `OPEN`. Nothing in Phases 1–13 proves or
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

## 10. Phase 7 — boundary-defect arithmetic

**Branch / milestone:** `feat/phase7-boundary-defect-arithmetic` / `0d58dd1`

**Acceptance record:** [`PHASE7_RUN_RESULTS.md`](PHASE7_RUN_RESULTS.md)

Under the least-positive-counterexample and first-crossing assumptions, Phase
7 independently reconstructs

\[
S(a)\ge 3N\delta,
\qquad
W(C)\ge 6N\delta-S_0.
\]

These identities are `CONDITIONAL` symbolic implications. The algebra itself
does not require an external theorem. Substitution of `N>2075*2^60` is kept as
`EXTERNAL_EVIDENCE`, while the rotation-sum step is explicitly
`EXTERNAL_THEOREM: DENJOY_KOKSMA`.

### Exact first crossing and contacts

Exact rational logarithm enclosures and Farey-neighbor arithmetic certify the
first possible crossing pair after the external bound as

\[
(q_0,K_0)=(72{,}057{,}431{,}991,114{,}208{,}327{,}604).
\]

The denominator decomposition
`q0=6586818670+65470613321` uses consecutive continued-fraction denominators;
no giant powers are constructed. With the external inputs separated, the
certificate forces at least 31,327,720,462 contacts. For `h=12`, it first
certifies 889,748,841 cyclic pairs and then removes the at most 12 wrap pairs,
giving 889,748,829 genuine indices `0<=j<j+12<q0`.

### Exact 12-odd macros and arithmetic frontier

The generator and independent verifier reconstruct 13 mechanical factors and
87,015 contact-return macros. Macro id 0, word
`1111111111110000000`, is the smallest stored counterexample to all three
candidate statements that every macro contracts, decomposes into the four
Phase 5 dangerous words, or is unrealizable over positive integers.

Fixed layers `q=1,3,5,17` contain exactly `1,2,7,312455` words and have
distinct positive 2-adic representatives. Their exact Pareto fronts do not
yield a monotone or `q`-uniform high-`B`/small-`r2` separation theorem. The
mandatory `A^rB^s` audit checks all `1<=r,s<=128`; no bounded paradoxical
contracting endpoint is found, but the universal candidate remains `OPEN`.

### What this result does not prove

The contact bounds and finite macro alphabet do not exclude a least
counterexample, prove an eventual lower bound for `M(k)`, or prove the Collatz
conjecture. The main bottleneck is now stated more precisely: high correction
must be linked to a sufficiently large least positive inverse-parity residue.

## 11. Phase 8 — contracting mixed blocks and octave bridge

**Branch:** `feat/phase8-mixed-block-octave`

**Acceptance record:** [`PHASE8_RUN_RESULTS.md`](PHASE8_RUN_RESULTS.md)

Phase 8 first closes the ordered mixed family left open in Phase 7. For an
integral realization of `F_(r,s)=B^s composed with A^r`, the exact coordinate
`u=(49x+73)/32^r` satisfies `v2(u)=2`, `u>=4`, and two CRT congruences. Direct
expansion reduces strict descent to

```text
u*(Q-P)>108*(16^s-9^s).
```

Elementary inequalities and six exact CRT base cases cover the small regimes.
The remaining `r>=4`, `1/2<P/Q<1` regime uses EXT05, the exact power-gap bound
in Rozier--Terracol Lemma B.1. Its application begins at exponent 30, so it
does not use that paper's finite check for exponents 13 through 18.

**Status:** C02 changed from `CONJECTURE` to `VERIFIED_THEOREM`. This proves
descent for every contracting ordered `A^rB^s` realization, not arbitrary
interleavings.

### Conditional octave consequences

Under the Phase 7 least-counterexample and first-crossing framework, the exact
normalization

```text
x_j=2^(theta_j+a_j)*(N+R_j),  0<=R_j<=j/3
```

connects boundary defect `a_j` to the actual octave of the odd iterate. Exact
rational logarithm bounds prove `q0*eta<2`; after the two Denjoy--Koksma blocks,
the integer exception count is at most 5. Consequently, under P58, X02, EXT04,
and the Phase 7 contact certificates, at least 31,327,720,457 odd iterates,
889,748,819 nonwrapping `h=12` pairs, and 7,308,576,455 consecutive short
returns have the stated first-octave property.

The short returns have exactly four maps:
`(3x+1)/2`, `(3x+1)/4`, `(9x+5)/8`, and `(9x+5)/16`. Their source intervals and
endpoint parity constraints are verified, but no global rank follows from the
alphabet.

### C03 bounded falsification

The arbitrary-block conjecture C03 remains `OPEN`. Exact enumeration through
block length 18 finds no counterexample among 79,184 contracting words. Of
these, 79,166 contain both `A` and `B`; the difference consists of the 18 pure
words `B^n`. The smallest mixed descent margin is 1,249 at `BBA`. A separate
first-block-boundary crossing enumeration through length 22 reconstructs
12,265 words with the specified length distribution.

### What this result does not prove

The bounded C03 search does not prove C03. The octave consequences retain
their explicit conditional and external inputs. Phase 8 supplies neither an
eventual lower bound for `M(k)` nor a proof of the Collatz conjecture.

## 12. Phase 9 — two-sided criticality and near-diagonal residues

Phase 9 began from the exact Phase 8 commit
`ad4f8848efa3aafc211cf80089563ae9406bc418` and kept the P54/P57
least-positive-counterexample framework explicitly conditional. Its first
result is the exact forced-contact recurrence P59: a zero defect in the low
rotation phase forces the next defect to remain zero, with successor weight
ratio `2/3`.

### Contact sharpness and improved finite counts

The proposed contact-only completion fails. After correcting the symbolic
contact indicator to require `c_0=1`, the all-contact construction obeys every
closure rule and strictly exceeds the required weighted pressure. NG17 is
therefore `REFUTED`, but only for arguments that discard endpoint and
least-positive-residue information.

An exact search over all reduced dual parameters of denominator at most 256
selects `lambda=143/199`. Under P58/P59/P57, X02, EXT04, and the Phase 7
certificate, this raises the conditional contact lower bound from
31,327,720,462 to 35,251,435,772. Exact gap counting and the five octave
exceptions then give E14: at least 16,848,437,652 first-octave consecutive
short returns of odd gap at most 2. The optimizer is finite-grid optimal, not a
claimed global continuous optimum.

### Endpoint and reverse localization

The exact endpoint identity yields

```text
S(a)=3*N*delta+3*(1+delta)*d,
0<=d<=4,142,380,786<2^32.
```

The same conditional setting forces `X=7 or 19 mod 36`. The map
`G4=(9x+5)/16` has the smaller odd predecessor `z=(2y-1)/3`, so it is forbidden
on a first-octave return of a least counterexample. Exact continued fractions
then put the first reverse coefficient pair not excluded by the uniform
minimality threshold at
`(a,L)=(615582794569,975675645481)`; the previous semiconvergent
`(478054749257,757698850864)` is still insufficient. No valid reverse path is
claimed.

### Two-sided finite audit and remaining obstruction

The generator and logically independent verifier enumerate every
coefficient-safe first-crossing word through `q=21`, 22,475,497 words in all.
Each row is included in a deterministic binary SHA-256 digest. No nontrivial
paradoxical canonical word occurs in this finite range. A separate exhaustive
tree through shortcut length 21 finds exactly five positive paradoxical
cylinders, all at length 8, and no new global rank.

C04 remains `OPEN`: q0 was not enumerated, and there is no theorem excluding
the canonical residues `r2,r3` from the strip
`0<=r3-r2<=4,142,380,786`, `r3=7 or 19 mod 36`. The reverse residue audit
covers all 287 contracting coefficient pairs through `a=30` but only 30
explicit lower-mechanical exponent words; arbitrary compositions remain a
combinatorial obstruction. The bounded results overlap prior finite-order work
of Rozier--Terracol and Winkler and do not reprove those external results.

### What this result does not prove

Phase 9 does not prove C04, C03, H54, H57, or the Collatz conjecture. Its large
numerical consequences retain their named conditional and external inputs.
The q<=21 and length<=21 searches cannot establish an eventual result.

## 13. Phase 10 — gap reduction and renewal spacing

Phase 10 began from the exact Phase 9 commit
`d1017982290e71b92438d07c6949f282e5bd1d96`. It preserves the
least-positive-counterexample and X02 dependencies explicitly rather than
promoting their consequences to unconditional statements.

### One-residue gap reduction

From `3^q r2+B=2^K r3`, `D=2^K-3^q`, and `d=r3-r2`, exact algebra gives
`B=D r2+2^K d` and hence `d=B*3^(-q) mod D`. In the Phase 9 q0 box, exact
logarithm intervals prove `D>W`, so the least residue `rho` equals `d`, the
integer quotient `m` equals `N`, and `X=m+rho`. Canonical ranges are certified
without constructing the giant q0 powers. Least-counterexample minimality and
P61 also force `4|rho`. P63 is `CONDITIONAL`; C04 remains `OPEN` because the
unknown word still determines `B mod D`.

### Renewal barrier

For any orbit point `N<=S<=N+W`, a first coefficient crossing must obey
`V/(V+W)<=(3+1/V)^q/2^K`. Phase 10 reconstructs the Phase 7 Stern--Brocot
parents and two strictly positive rational-logarithm margins at the preceding
upper parent. This excludes `q<q0`; the exact first-crossing index rule then
proves P64: every such S is conditionally safe through
`K0-1=114208327603`. A positive endpoint gap would therefore create two
distinct long-safe integers within W.

### Finite spacing and rational cycles

The exact spacing scan through `H=1,500,000` gives
`Delta_213=268416`, witnessed by `(1126015,1394431)`. At the next depth the
finite prefix contains only one safe value. The generator's forward deletion
and heap implementation is independently reconstructed by reverse activation
and a Fenwick tree. NG18 records the smallest shortcut obstruction
`Delta_2=Delta_3=4`: nesting gives nondecrease, not strict growth. No scalable
cylinder certificate proves C05 at `(K0-1,2^72)`, so C05 is `OPEN`.

P65 is an exact theorem about the formal rational affine cycle of a
coefficient-safe first-crossing word. The fixed point `z=B/D` is minimal
because every prefix difference has numerator
`(3^a_j-2^j)B+B_jD>=0`, and `gcd(B,D)=gcd(d,D)`. It asserts neither a positive
integer cycle nor Christoffel extremality. The latter is recorded separately
as external preprint context. Independent finite audits cover all 81,118
first-crossing words through `q=15` and the mandatory adversarial families.

### What this result does not prove

Phase 10 does not prove C04, C05, H54, H57, or the Collatz conjecture. Its
renewal application retains the least-counterexample and X02 inputs. Finite
disappearance below 1,500,000 cannot establish a spacing bound at `2^72`.

## 14. Phase 10 supplement — first-divergence branch coordinates

The supplement starts from Phase 10 commit
`b3ab86a102c0df3f2e7ded72b8dd32dc1fa53312` and asks for a lossless state
behind C05 rather than a larger raw scan. P66 proves the exact branch identity:
for `d=m-n>0`, two integer trajectories share exactly `h=v2(d)` parity steps,
then split, and their transformed gap is the odd integer
`3^a(d/2^h)` after a common prefix with a odd steps.

Combining P66 with P63/P64 gives conditional P67. Since `4|d` and
`0<d<=W<2^32`, every positive q0 near-return belongs to exactly one of the 30
cases `2<=h<=31`. Both endpoints remain safe through K0-1, but their tails
inherit a common-prefix coefficient surplus and cannot be treated as fresh
independent safe paths.

E16 exhausts `2<=n<=1,500,000` and reconstructs the maximum joint-safe depth
`R_h(H)` for every finite branch depth `0<=h<=20`. The profile peaks at 213 for
`h=7`, pair `(1126015,1394431)`, and is nonmonotone in h. An implementation-
independent verifier proves each finite upper bound by ruling out opposite
residue sides one depth higher. It also rebuilds 32,385 small-pair rows and
5,156 mandatory adversarial pairs.

This does not prove C05. It identifies the minimum information a future
certificate must preserve: h, common odd count, odd normalized gap, inherited
coefficient surplus, and both tail residue states. The branch-depth coordinate
alone is recorded as an obstruction rather than promoted from finite data.

### What this result does not prove

The supplement does not prove C04, C05, H54, H57, or Collatz. Branch depths
21--31 are absent from E16 only because `H=1,500,000`; no target-height case is
excluded.

## 15. Two-tail finite-state theorem and collision mining

The next supplement tests the explicit state suggested by P66/P67 instead of
extending the safe-pair depth. Let `h` be the common-prefix length, `a` its odd
count, `u=(m-n)/2^h`, and `y=T^h(n)`. P68 proves that, for a pair already
coefficient-safe through the common prefix,

```text
(h, a, u, branch orientation, y mod 2^L)
```

determines both next-L parity words and all coefficient-safety decisions during
those L steps. The reason is exact: the other tail starts at `y+3^a u`, a
length-L parity word is determined by the start modulo `2^L`, and the inherited
coefficient is `3^a/2^h`.

The theorem gives a lossless finite-horizon description, but its state grows
with L. NG19 therefore tests whether any literal shortening `b<L` remains
lossless at `L=12`. E17 scans all 6,887,319 eligible pairs with
`2<=n<m<=20,000` and `m-n<=512` in a fixed minimality order. Every
`b=0,...,11` has an exact collision between opposite joint-safety outcomes. The
last required collision occurs for `b=11` at `(1407,1663)` versus
`(15551,15807)`.

The generator and independent verifier separately reconstruct coefficient
stopping times, transformed gaps, parity tails, collision minimality, and the
5,156-pair mandatory adversarial digest. Tamper tests reject changes to P68,
NG19 witnesses, finite digests, adversarial data, and the C05 status.

### What this result does not prove

P68 does not give an unbounded finite automaton, and E17 cannot prove that
every alternative compression fails. NG19 refutes only the entire tested
family of literal shorter residue windows at `L=12`. C04, C05, H54, and the
Collatz conjecture remain open; `proves_collatz=false`.

## 16. Phase 11 — renewal ladder and affine-margin cylinders

P69 replaces the least-global-counterexample viewpoint by the successive tail
minima of any nonperiodic counterexample orbit. These minima strictly increase,
are all `3 mod 4`, and never drop below themselves. At a finite coefficient
first crossing with q odd steps, exact affine arithmetic gives

```text
S_i<=H_q,
4<=S_(i+1)-S_i<=d_i<=floor((q-1)/3),
q_i->infinity,
den(B_i/D_q)>3D_q/q.
```

Here q counts odd steps and need not be odd-valued. The formal denominator is
not an integer-cycle claim. Together with the periodic and infinite-
coefficient-safe alternatives, this yields the unconditional three-branch
counterexample trichotomy.

P70 proves that the eventual H70 dropping-safe spacing inequality eliminates
the finite-crossing ladder branch. It leaves nontrivial cycles and infinite
coefficient-safe tails as separate obligations. E18 independently recomputes
every `q<=4961`: exactly `17,22,27,29,32,34` fail, all at pair `(27,31)` and
gap 4, while every `35<=q<=4961` passes. The final height is 1,666,251. The
first structurally vacuous q is 141, so the later empty finite sets are not
evidence of eventuality.

NG20 is a universal no-go: for every `k>=3`, the k-step dropping-safe integers
`2^k-5` and `2^k-1` differ by 4. Any spacing argument must retain ordinary
height.

P71 adds the requested composable exact margins. On a fixed length-L parity
cylinder, every margin `T^j(x)-x` is affine in the cylinder parameter; all
inequalities for a fixed-gap pair intersect to one exact integer interval.
E19 represents 16,775,072 pairs by 262,144 cylinders at `H=262144`, depth 12,
and gap at most 64, finding 48,822 safe pairs. The rule composes locally but
does not merge the `2^L` residue classes; H70 remains open.

### What this result does not prove

Phase 11 does not prove H70, exclude the other two P69 branches, prove C04,
C05, H54, or Collatz. Its finite passes and exact local cylinder closure are not
an eventual theorem.

## 17. Phase 12 — infinite-safe-tail odd-orbit packing

P72 attacks the second branch of P69 without assuming a least global
counterexample. For a nonperiodic coefficient-safe tail beginning at tail
minimum `S`, let `x_j=T^(d_j)(S)` be the j-th odd iterate and set

```text
a_j=floor(j*log2(3))-d_j,
theta_j=fractional_part(j*log2(3)),
Y_j=2^d_j*x_j/3^j.
```

Exact affine normalization gives

```text
x_j=2^(a_j+theta_j)Y_j,
Y_(j+1)=Y_j(1+1/(3x_j)).
```

The odd values are distinct, and every value after the first is coprime to
six. Packing those values in the two admissible residue classes per six and
bounding the reciprocal sum by an integral proves

```text
Y_j<=S*exp(1/S)*(1+3j/S)^(1/9),
#{i<j:a_i<=A}
 <=3+[2^(A+1)S exp(1/S)/3]*(1+3j/S)^(1/9).
```

Consequently, for every epsilon>0,
`a_i>(8/9-epsilon)log2(i)` on a density-one set of indices. At any finite
coefficient first crossing the same normalization gives the strict endpoint
bound requested in the Phase 12 specification. These are theorem-level
deductions, not extrapolations from finite orbit data.

P73 applies the count with `A=0` to the all-contact positions
`d_j=floor(j log2(3))`. This is the critical upper mechanical word of slope
`ln(2)/ln(3)`, and it cannot be the infinite forward parity word of a positive
integer, although every finite prefix retains an exact canonical 2-adic
residue. The result is explicitly separated from the earlier symbolic NG17
construction, which used only contact closure and pressure.

The overlap audit records Lagarias's critical parity-density restriction,
Monks--Yazinski's rational 2-adic extension, and Lopez--Stoll's work on
critical Sturmian parity words. Phase 12 makes no novelty claim against that
literature and does not import it as proof input.

E20 independently audits 25,000 starts `S=3 mod 4` through 100,000 and 2,144
mandatory adversarial instances. The longest recorded prefixes contain 85 and
90 odd iterates. The all-contact residue audit reaches 512 odd inputs.

NG21 preserves the main obstruction: the abstract ordered list of all integers
coprime to six has exactly the reciprocal density needed for product exponent
`1/9`. Thus no smaller exponent follows from the packing premises alone. The
abstract list is not a Collatz orbit; H72 remains open for an orbit-specific
transition or congruence improvement.

### What this result does not prove

Phase 12 does not eliminate arbitrary infinite coefficient-safe tails,
nontrivial cycles, the renewal ladder, H70, C04, C05, H54, or Collatz.
`proves_collatz=false`.

## 18. Predecessor-tree and density detour

Strong external results count many predecessors or show descent for almost all
starting values. A naive attempt to combine those densities with a least
counterexample fails: two global density statements need not control one
designated exceptional integer or its thin arithmetic cylinder.

**Status:** `REFUTED` as a standalone density comparison. A future approach
would need an explicit transport, invariance, or intersection theorem for the
least-counterexample set.

## 19. Numerical consistency audit

The canonical figures above were resolved using this priority:

1. independent verifier result;
2. latest committed phase result;
3. older prose.

No contradictory phase counts were found. Apparent differences have distinct
scopes:

- Phase 4 has 34,788 total certificate records and 33,696 depth-3 cylinders;
  10,335 records close overall while 9,911 close at depth 3.
- Test totals 117, 129, 137, 145, 149, and 154 belong to successive repository
  states, not competing reruns of one commit.
- Phase 5 H5-A/H5-B results concern quantified bounded surrogates; the original
  legacy labels were underspecified and are not universal theorem claims.
- `H_q=O(q^5.117)` is contextual external arithmetic, not a verified internal
  result.
- The Phase 8 values 79,184 and 79,166 count all contracting `{A,B}` words and
  only genuinely mixed words, respectively; the 18-word difference is the
  pure family `B^n` for lengths 1 through 18.
- The Phase 9 value 22,475,497 counts first-crossing words through `q=21`; the
  five paradoxical records instead come from the separate unrestricted
  parity-word tree through shortcut length 21.
- The Phase 10 value 81,118 counts first-crossing words only through `q=15` in
  its independent gap/rational-cycle audit; it does not replace the deeper
  Phase 9 enumeration or evaluate q0.
- The branch supplement's 32,385 and 5,156 counts refer to exhaustive small
  integer pairs and mandatory adversarial adjacent pairs, not first-crossing
  words.
- Phase 11's 16,775,072 count is the number of fixed-gap pairs represented by
  affine cylinders; 262,144 is the cylinder count and 48,822 is the exact
  depth-12 dropping-safe pair count. They are not first-crossing words.

## 20. Current strategy

The primary target is

\[
M(K_q-1)>H_q\qquad\text{for all sufficiently large }q.
\]

Highest-priority directions are a deterministic separation between high affine
correction and small inverse-parity representatives, recursive lower bounds for
`M(k)`, and arithmetic structure at continued-fraction/`H_q` records. Phase 7
shows that contact density and a finite macro alphabet alone are insufficient;
Phase 8 additionally shows that exact octave localization and ordered-block
descent do not yet control arbitrary block interleavings.
Phase 9 sharpens the conditional endpoint to a near-diagonal two-sided residue
box and refutes contact pressure alone as a completion mechanism. C04 and a
carry-aware arbitrary reverse-residue recursion are now the closest new
arithmetic targets inside that framework.
Phase 10 reduces C04 to a single gap residue and proves the conditional renewal
barrier. Its new C05 spacing target is a concrete alternative formulation, but
finite neighbor-gap deletion has not produced a scalable proof.
The branch supplement reduces the q0-specific positive-gap consequence needed
from C05 to 30 cases and specifies a lossless candidate state. Global C05 is
stronger. Phase 11 adds the exhaustive counterexample trichotomy and H70 as an
alternate spacing target. P71 gives exact local interval closure, but no
cross-cylinder state bound; NG20 proves height cannot be discarded.
Phase 12 constrains the infinite-safe-tail branch and eliminates its
all-contact mechanical extreme. NG21 shows that the coarse packing exponent is
sharp, so H72 must use actual orbit transitions rather than another mod-6-only
count.
Exact certificate extension remains useful for the finite remainder and for
testing structural conjectures, but it is not the missing theorem.

Bounded finite-state and modular searches are now primarily falsification
tools. Every universal proposal must survive `2^m-1`, `8^m-5`,
`(110|111)^*`, `A`, `B`, and `A^rB^s`.

## 21. Reproduction and immutable evidence

- Phase 1–2: [`RUN_RESULTS.md`](RUN_RESULTS.md)
- Phase 3: [`PHASE3_RUN_RESULTS.md`](PHASE3_RUN_RESULTS.md)
- Phase 4: [`PHASE4_RUN_RESULTS.md`](PHASE4_RUN_RESULTS.md)
- Phase 5: [`PHASE5_RUN_RESULTS.md`](PHASE5_RUN_RESULTS.md)
- Phase 6: [`PHASE6_RUN_RESULTS.md`](PHASE6_RUN_RESULTS.md)
- Phase 7: [`PHASE7_RUN_RESULTS.md`](PHASE7_RUN_RESULTS.md)
- Phase 8: [`PHASE8_RUN_RESULTS.md`](PHASE8_RUN_RESULTS.md)
- Phase 9: [`PHASE9_RUN_RESULTS.md`](PHASE9_RUN_RESULTS.md)
- Phase 10: [`PHASE10_RUN_RESULTS.md`](PHASE10_RUN_RESULTS.md)
- Branch-point supplement: [`BRANCH_POINT_RUN_RESULTS.md`](BRANCH_POINT_RUN_RESULTS.md)
- Two-tail supplement: [`TWO_TAIL_RUN_RESULTS.md`](TWO_TAIL_RUN_RESULTS.md)
- Phase 11: [`PHASE11_RUN_RESULTS.md`](PHASE11_RUN_RESULTS.md)
- Phase 12: [`PHASE12_RUN_RESULTS.md`](PHASE12_RUN_RESULTS.md)
- Phase 13: [`PHASE13_RUN_RESULTS.md`](PHASE13_RUN_RESULTS.md)
- Current manifest: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

The current manifest hash is recorded in the latest phase acceptance report.
Generated JSON/CSV/certificates must be regenerated, not hand edited.

## 22. Current one-paragraph handoff

Phases 1–5 built a robust exact-computation framework and showed why bounded
state, fixed period, fixed shadow, and finite mixed-modulus mechanisms leave
large unresolved families. Phase 6 supplies the direct reduction
`M(K_q-1) <= N <= H_q`; Phase 7 derives exact boundary-defect contact pressure
but finds immediate counterexamples inside the resulting finite macro
alphabet. Phase 8 proves descent for every contracting ordered `A^rB^s` word
and localizes almost all certified contacts to the first octave, yet arbitrary
interleavings remain open. Phase 9 strengthens the contact and short-return
counts, confines the conditional endpoint to `d<2^32`, and creates an enormous
reverse coefficient barrier, but C04 remains open because simultaneous
2-adic/3-adic near-diagonal residues are not excluded. Exact certificates cover
substantial finite ranges. Phase 10 turns the q0 endpoint into one gap residue
and proves that a positive gap would give two integers safe through K0-1 within
distance W, but C05 is unproved and its finite spacing recursion stalls far
below the target. P66/P67 now decompose positive gaps into 30 exact first-
divergence cases. P68 supplies the exact finite-horizon state, while NG19's
stored collisions show that no shorter literal residue window works at
`L=12`. Phase 11 splits every counterexample into a cycle, an infinite
coefficient-safe tail, or a finite-crossing renewal ladder. H70 would eliminate
only the ladder branch. Its exact affine-margin cylinders compose locally, but
NG19 blocks literal residue truncation and NG20 blocks height-free spacing.
Phase 12 proves a density-one octave-defect bound for the infinite-safe-tail
branch and rules out the all-contact critical word. NG21 shows that improving
its exponent requires genuine transition information. Phase 13 gives the
renewal prefix code, exact pressure identities, universal companion threshold,
and valuation-conditioned ordinary-source transfer. P80 states a sufficient
canonical-residue anti-concentration target, while NG23 refutes substituting
raw Haar volume for deterministic ordinary representatives. No eventual lower
bound for `M(k)`, cross-cylinder spacing theorem, or complete safe-tail
exclusion is known.

## 23. AI research control-plane audit

The post-Phase 12 repository added an operational layer for long-running AI
collaboration without changing any mathematical claim status. The claims
ledger remains the single prose source of truth; `research/registry.json`
contains only the machine-checkable current acceptance boundary, active
obligations, dependencies, and mandatory adversarial set. Scoped context packs
for H54, H70, and H72 reduce repeated context loading while explicitly
deferring to the ledger. A deterministic `research/claims-index.json` projects
all 72 ledger rows for AI retrieval and is rejected as stale whenever the
source ledger hash changes.

The Phase 12 acceptance was encoded as the reference experiment contract with
exact scope, commands, independence boundary, artifacts, stop conditions, and
interpretation limits. `research_health.py` now cross-checks the registry and
experiment manifests against the ledger, resolves the latest verifier through
the registry rather than a Phase 12 hard-code, inspects forbidden verifier
imports, and reports untracked artifact files. Strict mode rejects those files
in a clean acceptance worktree. A lightweight GitHub Actions gate runs these
checks and latest tamper tests; the expensive full suite remains manually
dispatchable.

This infrastructure is not evidence for Collatz and introduces no new claim
ID. Its purpose is to make stale context, provenance drift, unexplained
artifacts, and finite-to-asymptotic promotion harder for future AI agents.

## 24. Garcia--Tal--Heppner independent audit

**Milestone:** 2026-08-25 audit from `main` at
`e1eb31bdf13c7084f3ac575ec0b9e3c1f09e6c0b`

**Audit record:**
[`research/audits/garcia-tal-phase12/REPORT.md`](research/audits/garcia-tal-phase12/REPORT.md)

The audit checked Garcia--Tal Proposition 1, equation (6), and Corollary 1 at
the primary-source level. For `d=2,m=3,R={0,-1}`, their Hasse map is exactly
the shortcut Collatz map. Assuming the Heppner quantitative input quoted by
Garcia--Tal, equation (6) gives a location-uniform
`O(X^beta log(2X))`, `beta<1`, interval bound for every nonperiodic orbit.
Dyadic shells then give reciprocal orbit summability. Banach density zero by
itself would not suffice.

P74 records the conditional direct consequence: coefficient discrepancy tends
to infinity, so a global suffix minimum yields an odd permanent
coefficient-safe tail minimum. Thus, if EXT07 is admitted, P69's nonperiodic
finite-crossing renewal ladder cannot occur. This does not prove H70 and does
not eliminate nontrivial cycles or the permanent-safe tail.

P75 strengthens Phase 12 conditionally: `sum 2^-a_j` converges, `a_j` tends to
infinity, and the Garcia--Tal interval estimate yields
`#{j:a_j<=A}=O((A+1)2^(beta A))`. P76 independently derives the negative-real
companion and moving rational shadows, with exact real limit `h_0`, 2-adic
limit `-x_0`, error identities, and reduced-denominator formula. No effective
height/gcd estimate strong enough for Roth, Ridout, the subspace theorem, or a
product-formula contradiction was obtained.

NG22 preserves the decisive failure. An exact invariant exponent policy from
`h_0=3/2` satisfies all requested analytic conditions and has a coherent odd
2-adic source. E21 reconstructs the first 1,026 exponents independently; at
1,024 steps `E=1174` and `a=449`, while the 1,026-step canonical residue renews
the prior residue by `2*2^1174`. Consequently no positive ordinary source
below `2^1174` realizes the audited prefix, but no global positive-source
nonexistence theorem follows.

### What this result does not prove

The audit does not prove or disprove Collatz, does not eliminate a
permanent-safe positive orbit, and does not prove a nontrivial-cycle theorem.
EXT07 is an external theorem whose Heppner input is not reproved here. The
formal NG22 source is not a positive ordinary Collatz orbit.

## 25. Phase 13 — renewal-code pressure and canonical residues

**Branch:** `feat/phase13-renewal-code-pressure`

**Acceptance record:** [`PHASE13_RUN_RESULTS.md`](PHASE13_RUN_RESULTS.md)
**Detailed audit:**
[`research/audits/renewal-code-pressure/REPORT.md`](research/audits/renewal-code-pressure/REPORT.md)

Phase 13 treated the two preceding scratch audits as untrusted hypotheses and
implemented a fresh generator plus a verifier that imports no generator code.
P77 proves that strict suffix-minimum blocks of a permanent-safe discrepancy
word reverse to a prefix-free first-upcrossing code. P78 proves the exact
weighted stopping identity and strict bounds

```text
kappa < 3/4,
sigma < 7/12,
tau < 19/96,
nu < 9/32.
```

P79 reconstructs the universal `R(w)>=13/9` threshold, equality only for
`w=110`, and the positive ordinary divisibility bridge. The additional
normalization `C_w=(B_w+2^L-3^q)/4` is integral on renewal blocks; for
nontrivial `w`, it satisfies `C_w>=2^(L-3)` and `v2(C_w)=r-2`, where `r` is
the initial one-run. This is a genuine orbit-specific transfer rule but does
not by itself yield a global count.

P80 isolates the missing theorem. Either a uniformly subexponential endpoint
canonical-representative count with mass `sigma^i`, or its two-sided analogue
with mass `tau^i`, would combine with boundary growth to exclude a positive
permanent-safe orbit. The exact decay factors are `7/8` and `57/128`. Both
counting premises remain unproved, so H72 remains open.

NG23 records the least failure of the raw Haar shortcut. For `u=1,H=2`, the
canonical count is one while endpoint and two-sided volume predictions are
both `2/3`. Local Haar measure therefore cannot be silently substituted for
ordinary least positive representatives or a designated positive source.

E22 independently reconstructs the length-512 DP, every address with total
`Q<=12` and one through four blocks, heights through 2048, 2144 mandatory
adversarial convention instances, and a 4096-step square-root countermodel.
The latter is added to NG22's evidence without creating a duplicate claim ID.
Its coherent 2-adic source is not known to be a positive ordinary integer.

### What this result does not prove

Phase 13 does not prove either anti-concentration premise, does not prove H72,
does not eliminate nontrivial cycles, and does not prove or disprove the
Collatz conjecture. `proves_collatz=false`.

## 26. Research synthesis and repository integrity audit

**Branch:** `docs/research-synthesis-through-phase13`

The 2026-08-27 synthesis audit added
[`docs/RESEARCH_SYNTHESIS.md`](docs/RESEARCH_SYNTHESIS.md) as a single
self-contained map over Phases 1–13. It defines conventions, distinguishes the
P54/H54 and EXT07/P74/H72 routes, keeps nontrivial cycles separate, classifies
the local scratch inventory, and links every detail back to the existing
claims ledger, phase reports, audits, literature, and failure archive.

No mathematical claim status changed. X02's evidence row gained a direct
primary-source literature pointer and an updated audit date; its statement and
`EXTERNAL_EVIDENCE` status are unchanged. The live source still reported the
completed boundary `2075*2^60` at audit time.

The audit also added a public Markdown link/private-path checker to the
research health gate and updated CI to run the latest Phase 13 tamper tests.
This is repository integrity work, not a new mathematics phase.

### What this result does not prove

The synthesis does not validate a new theorem, resolve H54/H70/H72/C03/C04/C05,
exclude nontrivial cycles, or prove or disprove Collatz.
`proves_collatz=false`.

## 27. Phase 14 — coalescent rewrites and H72 reduction

**Branch:** `feat/phase14-coalescent-rewrite`

**Acceptance record:** [`PHASE14_RUN_RESULTS.md`](PHASE14_RUN_RESULTS.md)
**Detailed audit:**
[`research/audits/coalescent-rewrite/REPORT.md`](research/audits/coalescent-rewrite/REPORT.md)

Phase 14 treated the attached research note as an untrusted proposal and
rederived its usable claims under the repository's full shortcut convention.
P81 gives the exact necessary-and-sufficient criterion

```text
Q(a)=Q(d),  L(d)=L(a)+k,
2^k B(a)-B(d)=m 3^Q
```

for `F_d(2^k x+m)=F_a(x)`, with cylinder legality and positivity audited
separately. P82 shows that a least positive discrepancy-escaping
permanent-safe counterexample source would have only rewrite-irreducible
initial renewal addresses. Common right suffixes preserve a rewrite, and the
least positive source is a terminating potential, but confluence is not
proved.

P83 sharpens the companion threshold by initial one-run, with exact equality
words `110`, `111010`, and `111100`. P84 gives a positive decrement for every
nontrivial renewal block. P85 gives reduced-denominator and gcd bounds whenever
the octave defect is positive, hence eventually in the P76 setting; the
unqualified zero-defect case remains outside the theorem.

E23 independently exhausts all 30,084 renewal addresses with total `Q<=13`.
They form 24,197 endpoint classes and 5,949 positive downward rewrite pairs;
5,887 addresses are reducible. The minimum collision is
`1|110|1=11101` versus `111100`, satisfying
`F_111100(2x+1)=F_11101(x)`. No finite rewrite cycle or nonunique normal form
occurs in this bound.

NG24 records the structural obstruction: coalescence is a right congruence but
not a left congruence. Prefixing the minimum pair by `110` gives distinct
endpoint residues 263 and 587 modulo `3^6`. Thus `(Q,r3)` is not a closed
prefix-transfer state, and the finite normal forms do not imply eventual
reducibility.

### What this result does not prove

Phase 14 does not prove rewrite confluence, eventual reducibility, an
asymptotic irreducible pressure bound, either P80 anti-concentration premise,
H72, exclusion of nontrivial cycles, or the Collatz conjecture.
`proves_collatz=false`.

## 28. Phase 15 — surplus-dominating ancestors

**Branch:** `feat/phase15-surplus-dominance`

**Acceptance record:** [`PHASE15_RUN_RESULTS.md`](PHASE15_RUN_RESULTS.md)
**Detailed audit:**
[`research/audits/surplus-dominance/REPORT.md`](research/audits/surplus-dominance/REPORT.md)

Phase 15 treated the supplied surplus-dominance note as an untrusted proposal.
P86 proves that a least positive permanent-safe discrepancy-escaping source
cannot have a smaller safe path to the same endpoint whose terminal
coefficient is at least the original prefix's. This extends P82 beyond same-Q
renewal rewrites. P87 proves that an unsafe shorter coalescent target can be
cut at its unique negative discrepancy valley to obtain a strictly safe
suffix; positivity and source descent remain separate exact checks. P88 proves
fixed-Q endpoint injectivity for odd-gap words with every exponent in `{1,2}`.

E24 independently exhausts every coefficient-safe word and every competitor
through Q=17, plus every relevant shorter same-Q arbitrary target. It
reproduces the supplied safe-word and lower-Q dominance counts. At Q=17 there
are 663,535 safe words, with 320,168 dominated by competitors satisfying
`Q_b<=Q_d`; 343,367 survive. The `{1,2}`-gap layer contains 32,596 safe words,
all endpoint-distinct and all surviving that lower-or-equal-Q test. Valley
extraction adds exactly 12, 90, and 233 reductions at Q=15,16,17 beyond
same-Q safe targets.

NG25 preserves the cross-Q witness `111110100` from source 287 versus the
one-bit ancestor `1` from 273 at common endpoint 410, refuting same-Q
completeness. NG26 preserves the Q=15 unsafe target whose strict-valley suffix
coalesces from 527131 below the safe target source 1874247. These failures
define the minimum search language for a future all-depth frontier recursion.

### What this result does not prove

Phase 15 does not prove eventual surplus-frontier extinction, persistent
survival of the finite gap core, either P80 anti-concentration premise, H72,
exclusion of nontrivial cycles, or the Collatz conjecture.
`proves_collatz=false`.

## 29. Phase 15B — ancestral-minimal frontier

**Branch:** `feat/phase15b-ancestral-frontier`

**Acceptance record:** [`PHASE15B_RUN_RESULTS.md`](PHASE15B_RUN_RESULTS.md)
**Detailed audit:**
[`research/audits/ancestral-frontier/REPORT.md`](research/audits/ancestral-frontier/REPORT.md)

Phase 15B treated the supplied ancestral-frontier note as an untrusted
proposal and did not recycle its P86--P88 labels. P89 proves that every safe
prefix of a least positive counterexample is ancestrally minimal. P90 repairs
the proposed full route: an eventual H89 inequality excludes finite crossings
through P54 and excludes a never-crossing least counterexample by combining
P89 with Phase 6's `H_q>q/6`. H89 itself remains open.

P91 reconstructs the exact cross-Q affine identity and common-prefix carry;
P92 turns a first positive source comparison into uniform cylinder dominance.
P93/P94 give the unique finite safe renewal decomposition and Beatty support.
P95 gives shifted-correction composition, exact initial-run valuation, and
jump coalescence. P96 bounds the covered 3-adic endpoint union by
`sigma<7/12`, while explicitly preserving the measure/ordinary-point gap.

E25 scans every odd source through 5,000,000 without endpoint-height
truncation. It reconstructs 12,443,880 safe occurrences at 5,297,663
endpoints, finds maximum ancestral depth 209, and proves only the finite result
`M_star(210)>5000000`. E26 independently enumerates safe/frontier and renewal
data through Q=17 and same-Q compression through Q=19. NG27 records the first
audited gain-four obstruction to the universal gain-three hypothesis, with
sources 44,466,175 and 2,779,135 satisfying `y+1=16(x+1)`.

### What this result does not prove

Phase 15B does not prove H89, an eventual ancestral-frontier contraction,
P80, H72, exclusion of nontrivial cycles, or the Collatz conjecture.
`proves_collatz=false`.

## 30. Phase 16 — critical geodesic / ultra-low-height dichotomy

**Branch:** `feat/phase16-critical-dichotomy`

**Acceptance record:** [`PHASE16_RUN_RESULTS.md`](PHASE16_RUN_RESULTS.md)
**Detailed audit:**
[`research/audits/critical-dichotomy/REPORT.md`](research/audits/critical-dichotomy/REPORT.md)

Phase 16 treated the supplied note as untrusted and repaired two boundary
errors: `B/3^q<q/3` has equality at q=1, and the displayed `Phi(t)` packing
formula begins only at `t=133/576`. P97 retains the corrected carry bounds;
NG28 refutes universal carry positivity with an exact safe Q=26 pair of carry
-3. P98 proves normalized correction and the prefix-closed same-Q geodesic
criterion. P99 internally proves the mod-3/mod-9, odd-even-even, and all-odd
merges; Angeltveit is recorded only as primary-source overlap context.

P100 gives the exact mod-72 counts `6,9,15,20,24` and reciprocal packing
bound for distinct odd inputs. An exact rational atanh-series enclosure proves
P101's nonperiodic 250 dichotomy: either all prefixes are same-Q geodesic, or
`N<q/250`, `X<q/125`, and `Z<2q/125`. P102 separately retains the weaker
distinctness-free factor-3 bound. P103 conditionally adds all-prefix
geodesicity to the Phase 7 q0 scenario under X02.

E27 exhausts Q<=17. At Q=17, 253,018 of 312,455 critical words are geodesic;
27,949 are also contact-rich under the exact Phase 7 threshold. The finite
cutoff has 225,943 same-Q endpoint pairs and no negative carry, demonstrating
why the separately stored Q=26 NG28 witness is required.

### What this result does not prove

Phase 16 does not exclude G250/H97, H250/H98, the periodic branch, H89, H72,
nontrivial cycles, or the Collatz conjecture. `proves_collatz=false`.
