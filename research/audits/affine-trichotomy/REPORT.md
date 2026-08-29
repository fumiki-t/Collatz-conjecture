# Phase 18 audit — affine finite-state trichotomy

## 1. Result and scope

This audit treats `phase18_affine_trichotomy_note.md` as an untrusted research
proposal.  It accepts the finite-state affine mechanism after two repairs:

1. sign-pure SCC paths have a finite-stage condensation normal form, not in
   general one global positive packet followed by one global negative packet;
2. the mixed-SCC switching threshold must control the least internal prefix of
   the negative packet, not just its terminal coefficient.

P107--P109 and P111 are `VERIFIED_THEOREM`, P110 is `CONDITIONAL` on EXT07,
E30 is `VERIFIED_FINITE`, and NG30 is `REFUTED`.  H72 remains `OPEN`.
No new external theorem is introduced and `proves_collatz=false`.

The theorem applies to a supplied **closed finite directed graph**.  The audit
does not assume that the full permanent-safe Collatz language has such a
presentation.

## 2. Exact affine calculus

Every directed edge has a nonempty shortcut parity word `w` and map

\[
F_w(x)=\frac{3^{q(w)}x+B_w}{2^{L(w)}}
      =c_w(x+b_w),
\qquad
c_w=\frac{3^{q(w)}}{2^{L(w)}},\quad
b_w=\frac{B_w}{3^{q(w)}}\ge0.
\]

Appending a bit on the right gives the exact integer recurrence

\[
(L,q,B)\mapsto
\begin{cases}
(L+1,q,B),&0,\\
(L+1,q+1,3B+2^L),&1.
\end{cases}
\]

For a path `P=e_1...e_n`, let `C_i=c_{e_1}\cdots c_{e_i}` and write

\[
F_P(x)=C_n(x+\beta_P).
\]

Direct composition proves

\[
\boxed{\displaystyle
\beta_P=\sum_{i=1}^n\frac{b_{e_i}}{C_{i-1}}},
\qquad C_0=1.
\]

The generator checks this recurrence against the literal combined affine
constant `B_P/3^q`; the verifier reconstructs `B_P` independently as the
explicit sum over odd-bit positions.

For proof notation put `s(e)=log c_e` and
`S_i=sum_(j<=i)s(e_j)=log C_i`.  Every sign decision is nevertheless exact:
the programs compare `3^q` with `2^L` and never use floating point.

## 3. SCC classification

A simple directed cycle is positive or negative according as its exact
coefficient is greater or less than one.  Equality is impossible for a
nonempty cycle, because `3^q=2^L` forces `q=L=0`.  An SCC is:

- positive when all its simple cycles are positive;
- negative when all are negative;
- mixed when it has cycles of both signs;
- acyclic when it is a singleton without a loop.

Every closed walk decomposes into simple cycles, so a sign-pure SCC gives the
same strict sign to every nonempty closed walk.

## 4. P107 — uniform normalized correction without mixed SCCs

**Statement.** In a finite directed graph with no mixed SCC, there is a
constant `K_G` such that every finite path satisfying `C_i>1` for all
nonempty prefixes has `beta_P<=K_G`.

**Proof.** Fix a positive SCC.  There are finitely many simple cycles; let
`delta>0` be the least of their discrepancies.  Cycle erasure writes every
walk prefix as a simple residual path plus simple cycles.  Residual paths have
bounded length and bounded negative discrepancy, while every erased cycle
adds at least `delta`.  Thus, uniformly over entry vertices, the discrepancy
grows at least linearly with walk length up to a fixed additive error.  Hence

\[
\sum e^{-S_{i-1}}
\]

over every visit to a positive SCC is bounded by a geometric series.

For a negative SCC, apply the same argument in reverse.  Each erased cycle
has discrepancy at most `-delta`; global prefix safety `S_i>0` anchors the
right endpoint.  Moving backward through the visit therefore raises
discrepancy linearly up to a bounded residual error, giving another uniform
geometric bound for `sum e^{-S_(i-1)}`.

The condensation graph is acyclic.  A path visits each SCC at most once, and
all inter-SCC/simple residual segments have graph-bounded total length.  Since
`b_e` has a finite maximum, the affine identity in Section 2 turns the finite
sum of these geometric bounds into a uniform bound for `beta_P`.  This proves
P107.  The value need not be small or effectively useful unless the graph is
actually supplied.

## 5. P108 and NG30 — the corrected sign-pure trichotomy

Assume no SCC is mixed and fix any terminal coefficient cap `R>1`.

If no positive SCC can reach a negative SCC, every safe path with
`1<C_final<=R` has bounded length.  Indeed, repeatable negative cycles must
occur before repeatable positive cycles in the condensation order.  Prefix
safety bounds the total negative repetition before any positive buffer is
available, while the terminal cap bounds the later positive repetition.
All acyclic connectors are already graph-bounded.  This is Type I.

Conversely, suppose a positive SCC reaches a negative SCC.  Rotate a positive
closed walk after its last minimum so every nonempty internal prefix has
positive discrepancy.  Repeat it enough times to absorb the fixed connector.
At the negative SCC, repeat a negative closed walk only while its least
internal prefix remains above discrepancy zero.  The stopping rule leaves a
positive terminal discrepancy bounded by a constant depending only on that
closed walk.  Increasing the number of positive repetitions makes the total
path arbitrarily long.  This is Type II.

The proposal's stronger one-switch normal form is false.  On a four-SCC chain
with loop signs `+,-,+,-`, take for every `k>=2`

\[
n_1=\lfloor\log_2( (3/2)^k )\rfloor,
\quad R_k=4k+3,
\quad n_2=\lfloor\log_2( (3/2)^{R_k} )\rfloor-n_1,
\]

and

\[
w_k=1^{2k+1}0^{n_1}1^{2k+2}0^{n_2}.
\]

Both floors are computed exactly from integer bit lengths.  Every prefix has
coefficient greater than one, the final coefficient lies in `(1,2)`, and all
four packets have unbounded length.  Thus the first negative packet cannot be
absorbed into a bounded connector.  NG30 records this refutation.

What survives is the precise finite-stage normal form: a path consists of a
graph-bounded number of sign-pure cycle packets and bounded connectors along
the SCC condensation.  The number of sign changes is bounded by the graph,
but need not equal one.

## 6. P109 — a mixed SCC has balanced formal survivors

Suppose an SCC is mixed.  Strong connectivity and sufficiently many repeats
produce positive and negative closed walks based at a common vertex.  Rebase
at the position after the last minimum of the positive walk, obtaining a
packet `A` whose every nonempty internal prefix has coefficient greater than
one.  Rebase the negative walk `B` at the same vertex.

Let `c_A>1`, `c_B<1`, and let `m_B>0` be the least coefficient of an internal
prefix of `B`, including its terminal prefix.  Choose an exact rational
threshold

\[
H>\frac1{m_Bc_B}.
\]

At a packet boundary with coefficient `C`, append `A` when `C<=H` and `B`
when `C>H`.  After the initial `A`, all literal prefixes stay above one.
At boundaries the coefficient lies in a fixed interval contained in

\[
(Hc_B,Hc_A].
\]

Runs of either packet have graph-dependent bounded length.  Hence `A` occurs
with positive lower frequency.  Its normalized correction `b_A` is positive,
because a positive Collatz packet contains an odd edge.  Every `A` occurrence
adds at least `b_A/H` to beta.  Therefore beta grows at least linearly in the
number of packets while coefficient remains bounded above and below.  This is
an infinite **formal** coefficient-safe path; no ordinary source has been
constructed.

The stored one-state example uses `A=1`, `B=0`, `H=8`, and 512 exact packet
steps.  It is E30 finite evidence for conventions, not the proof of P109.

## 7. P110 — conditional positive-source exclusion

If the particular P109 path were realized by a fixed positive ordinary
source `x_0`, then at packet boundaries

\[
x_n=C_n(x_0+\beta_n)=\Theta(n),
\]

because `C_n` is bounded above and below and `beta_n=Theta(n)`.  Packet lengths
are fixed, so the boundary subsequence alone gives

\[
\sum_n\frac1{x_n}=\infty.
\]

The boundary values tend to infinity and therefore are not eventually
periodic.  EXT07, through its location-uniform interval estimate and the
dyadic-shell argument recorded in the Garcia--Tal audit, says that a positive
non-eventually-periodic shortcut orbit has convergent reciprocal sum.  Thus,
**conditional on EXT07**, this constructed balanced itinerary has no positive
ordinary source.

This excludes neither every itinerary in a mixed SCC nor every finite-state
formal survivor.

## 8. P111 — canonical 2-adic source lifts

Let `r_2(P)` be the least nonnegative source residue modulo `2^L` for a prefix
`P`.  If an edge of length `ell` is appended, the longer cylinder is contained
in the old one, so exactly

\[
r_2(Pe)=r_2(P)+\lambda_P2^L,
\qquad 0\le\lambda_P<2^{\ell}.
\]

If one fixed positive integer `N` realizes every prefix, then both residues
are congruent to `N`.  Once `2^L>N`, the least nonnegative representative is
literally `N`; every later lift is therefore zero.  Eventual zero lift is a
necessary condition for positive ordinary integrality.

The converse is not asserted.  In particular, finitely many nonzero lifts do
not rule out later stabilization, and a coherent nonstabilizing 2-adic source
is not a positive ordinary integer.

## 9. E30 — independent finite audit

The generator enumerates every deterministic partial graph on one, two, or
three vertices with labels `0` and `1`: each source-label pair is absent or
has one target.  The total is

\[
2^2+3^4+4^6=4181.
\]

Exact SCC/cycle classification gives:

```text
Type I:    1696
Type II:    176
Type III:  2309
```

Every graph is also enumerated through safe path depth 12 with terminal
coefficient at most 4.  The independent verifier enumerates graph choices in
reverse order, uses mutual reachability rather than the generator's SCC
algorithm, reconstructs affine constants by an explicit odd-position sum,
then canonicalizes the rows.  The path counts are only a sanity audit.

The finite evidence additionally includes:

- the 512-packet mixed one-state schedule and every canonical source lift;
- 74 rows from all mandatory families;
- Phase 7 macro 0 and the preserved NG02/NG17/NG19/NG21--NG29 boundaries;
- exact SHA-256 pinning and applicability classification for existing models.

Tamper tests change the theorem status, graph digest, mixed source residue,
project input digest, adversarial digest, and obstruction status.  Every
mutation is rejected.

## 10. Applicability to current H72 models

No accepted model is presently a closed finite graph for all H72 candidates.

| Existing model | Exact Phase 18 classification |
|---|---|
| Phase 7 macro alphabet | Contains positive and negative macros, but has no closed transition graph; free concatenation is a Type III overapproximation only |
| Phase 8 A/B semigroup | Type III in the coefficient abstraction; literal integer guards require unbounded affine state |
| Phase 10/11 two-tail states | Not fixed finite; residues, heights, and margins grow with horizon |
| Phase 13 NG22 model | Formal unbounded square-root controller with a coherent 2-adic source, no positive ordinary source |
| Phase 14 quotient | Not prefix-closed by NG24 |
| Phase 16 predecessor rules | Local height-conditioned sieve, not a closed automaton |
| Phase 17 suffix code | Exact Type I expanding sublanguage, not the full critical language |

Consequently Phase 18 sharpens the design test for future automata: a
sign-pure closed model gives bounded beta, while a mixed closed model admits
formal balanced survivors.  Either way, a proof of H72 must retain enough
ordinary-integrality information to avoid an unsound finite quotient.

## 11. What this result does not prove

- that the permanent-safe language is regular or has a closed finite graph;
- that P107's graph-dependent bound controls any current all-depth model;
- that every mixed-SCC path has divergent reciprocal sum;
- that the formal mixed path has a positive ordinary source;
- H72, H89, H104, H105, exclusion of nontrivial cycles, or Collatz.

`proves_collatz=false`.
