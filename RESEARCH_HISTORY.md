# Collatz conjecture research history

This is the chronological human-readable record of the repository. It is
designed to preserve both successful results and failed mechanisms when the
original chat is unavailable. The live status is in
[`docs/STATUS.md`](docs/STATUS.md); stable claim IDs are in
[`docs/CLAIMS_LEDGER.md`](docs/CLAIMS_LEDGER.md).

**The Collatz conjecture remains `OPEN`. Nothing in Phases 1–8 proves or
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

## 16. Predecessor-tree and density detour

Strong external results count many predecessors or show descent for almost all
starting values. A naive attempt to combine those densities with a least
counterexample fails: two global density statements need not control one
designated exceptional integer or its thin arithmetic cylinder.

**Status:** `REFUTED` as a standalone density comparison. A future approach
would need an explicit transport, invariance, or intersection theorem for the
least-counterexample set.

## 17. Numerical consistency audit

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

## 18. Current strategy

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
stronger. State-collision mining at small height is now more valuable than
extending the undifferentiated spacing profile.
Exact certificate extension remains useful for the finite remainder and for
testing structural conjectures, but it is not the missing theorem.

Bounded finite-state and modular searches are now primarily falsification
tools. Every universal proposal must survive `2^m-1`, `8^m-5`,
`(110|111)^*`, `A`, `B`, and `A^rB^s`.

## 19. Reproduction and immutable evidence

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
- Current manifest: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

The current manifest hash is recorded in the latest phase acceptance report.
Generated JSON/CSV/certificates must be regenerated, not hand edited.

## 20. Current one-paragraph handoff

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
`L=12`. No eventual lower bound for `M(k)` is known. Future work should target
a composable carry-aware two-tail cylinder theorem that separates those
collisions, not merely greater depth.
