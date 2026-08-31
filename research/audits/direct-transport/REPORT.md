# Phase 30 audit — direct token transport

**Status:** accepted exact derivations with one proposal repair

**Branch:** `feat/phase30-direct-transport`

**Collatz conjecture:** open; `proves_collatz=false`

The supplied note was treated as an untrusted proposal. Its direct transport,
area constant, and singleton-normal-form arguments survive. The statement
that the *actual maximum orbit state* must saturate P157's height bound does
not follow and is not accepted.

## 1. P179 — direct factor-set transport

Let `a_0=a_q=0` be the discrepancy-minimum reduced profile over the repeated
mechanical baseline boundaries `E_j^(0)`. For every ordinary component
`[u,v)` of `I_k={j:a_j>=k}`, raising the truncated profile from level `k-1`
to `k` shifts exactly the labelled odd boundaries `u,...,v-1` one shortcut
position right.

At both component endpoints the old offset is `k-1`. Hence the affected
binary segment has exact length

\[
s=E_v^{(0)}-E_u^{(0)}
\]

and the operation is its one-symbol cyclic right rotation. A new cyclic
length-`n` factor can start only in the segment or its `n-1`-position backward
neighborhood, giving at most `s+n-1` possible new starts. If `n>L`, the same
bound follows trivially from at most `L<=n` cyclic starts.

Telescoping factor-set additions over all `J` components proves

\[
p_{\rm cyc}(n)\le p_{\rm base}(n)+T_{\rm span}+J(n-1).
\]

The exact span obeys

\[
T_{\rm span}\le2A,
\qquad
qT_{\rm span}\le LA+qJ,
\]

because each mechanical increment is at most two and each interval satisfies
`q(E_v-E_u)<=L(v-u)+q`. With `p_base(n)<=n+1`, this yields

\[
p_{\rm cyc}(n)\le(J+1)n+2A+1.
\]

This is a direct factor-set inclusion, not an adjacent-swap count.

## 2. NG39 — the span cannot be dropped

For

```text
q=6, L=10
e=(2,2,1,3,1,1)
baseline=(2,2,1,2,2,1)
profile=(0,0,0,0,1,0,0)
A=J=1, T_span=2, n=4
```

the baseline has five factors and the actual word has ten. Thus the proposed
span-free bound gives `5+1*4=9<10`, whereas P179 gives equality
`5+2+1*3=10`. NG39 records this exact refutation.

## 3. P180 — sharpened positive-cycle separation

For a primitive positive nontrivial cycle, P157 defines

\[
n_{\rm cyc}=\left\lceil\log_2(2^{h+2}m/\lambda)\right\rceil
\]

and P125 makes all `L` cyclic factors at that width distinct. P179 therefore
gives

\[
L\le(J+1)n_{\rm cyc}+2A+1.
\]

Since `ceil(x)<x+1` and P133 gives the strict
`m<q/[3(1-lambda)]`, exact substitution yields

\[
L<(J+1)\left[h+3+\log_2{q\over3\lambda(1-\lambda)}\right]+2A+1.
\]

Positivity and primitivity enter at ordinary-state separation; the factor
theorem itself is purely combinatorial.

## 4. P181/P182 — sharper asymptotic area constant

For a hypothetical primitive-positive cycle sequence with `q->infinity`,
`L/q->ell in (1,2]`, and a fixed inverse-polynomial multiplier gap, either
`A/q^(2/3)` is unbounded or a bounded subsequence has

\[
x={J\over q^{2/3}},\qquad y={h\over q^{1/3}},
\qquad \ell\le xy.
\]

P167 independently gives

\[
\liminf {A\over q^{2/3}}\ge x+{y^2\over2(\ell-1)}.
\]

The unique optimizer under `xy>=ell` has
`y^3=ell(ell-1)` and `x=ell/y`, proving

\[
\liminf{A\over q^{2/3}}\ge
C_{\rm move}(\ell)={3\ell^{2/3}\over2(\ell-1)^{1/3}}.
\]

Its cube is exactly four times the P168 constant's cube. The noncritical
minimum occurs at `ell=2` and is `(3/2)2^(2/3)` in `(2.381101,2.381102)`.
The critical specialization is in `(2.438154,2.438155)` and retains EXT17.

## 5. P183 — repaired equality rigidity

Equality in P181 forces the unique normalized scales

\[
h/q^{1/3}\to(\ell(\ell-1))^{1/3},\quad
J/q^{2/3}\to{\ell^{2/3}\over(\ell-1)^{1/3}},\quad
A/J\to3/2,
\]

vanishing normalized P167 descent slack, and leading-order saturation of the
direct factor bound. It also forces the selected `n_cyc` proxy to have leading
scale `h` because all logarithmic correction terms are `o(q^(1/3))`.

The proposal's stronger sentence about ratio-one saturation of the *actual
maximum state* is not derivable: `n_cyc` is defined from an upper bound, and
factor-count saturation does not reverse P157's state inequality. No such
claim is recorded.

## 6. P184 — singleton-transport normal form

Choose a maximum-height index and, at each level, the unique nested component
containing it. P167's descent proof is localized on this spine, so its total
excess length is at least

\[
B_h=\sum_{r=1}^{h-1}\left\lfloor{r\over\ell-1}\right\rfloor.
\]

Since total component excess is `A-J`, every non-spine excess—including all
secondary peaks—is at most

\[
\Sigma=A-J-B_h.
\]

At P181 equality, `Sigma=o(q^(2/3))=o(J)` and the spine itself has only
`h=o(J)` components. Each non-spine nonsingleton consumes at least one excess
unit. Therefore all but `o(J)` components are singleton intervals. This is a
component-count normal form, not an arithmetic contradiction.

## 7. E42 — independent finite audit

The generator uses explicit string rotations. The verifier instead rebuilds
every intermediate word from incremented boundary profiles and compares exact
factor-set differences. It imports no generator code. Exact checks cover:

- 2,214 cyclic classes and 3,101 discrepancy-minimum rotations through `q<=8`;
- all 45,369 cyclic widths;
- 9,498 component rotations and 141,643 affected-start inequalities;
- 9,303 spine/secondary-peak charging inequalities;
- five independently synthesized large profiles at 50 declared widths;
- exact 96-term/160-term rational logarithm enclosures;
- NG39, trivial powers, both negative-cycle controls, and every mandatory
  adversarial family.

Tamper tests reject corpus digests, constants, removed EXT17 dependence,
literal state-saturation promotion, NG39 changes, and Collatz overclaims.

## 8. Remaining H172 boundary

Near equality now consists of one nested spine, `J-o(J)` adjacent singleton
transports, and only `o(J)` other interval transports. P171 turns these into
paired endpoint binomials, but no theorem uses their locations to obtain a
strict subleading resonance/resultant gap. Another area lower bound alone will
not close H172.

## What this result does not prove

It does not exclude arbitrary-area cycles, prove a pair-aware resultant,
exclude either nonperiodic P69 branch, or prove the Collatz conjecture.
`proves_collatz=false`.
