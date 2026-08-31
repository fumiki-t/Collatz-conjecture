# Phase 29 audit — automatic arc nonvanishing

**Status:** accepted exact derivations and bounded finite verification

**Branch:** `feat/phase29-arc-nonvanishing`
**Collatz conjecture:** open; `proves_collatz=false`

The supplied Phase 29 note was treated as an untrusted proposal.  This report
records the derivations that survived independent reconstruction, the exact
external dependencies, and the obstruction that remains.

## 1. Conventions

Let `q,L` be coprime, `2^L>3^q`, and let `a_t` be the reduced defect profile in
odd-time coordinates.  Residue and time coordinates are related by

\[
 r_t=[-Lt]_q,
 \qquad
 E_t=(Lt+r_t)/q.
\]

Write `u=[L^{-1}]_q` and `c=(Lu-1)/q`.  The profile in polynomial residue
coordinates is `a_t=a_{r_t}`.  The reduced polynomial is always formed after
the relation `X^q=2`; in particular its endpoint coefficient is retained.

## 2. P173 — every coprime P147 arc is nonzero

Direct coefficient comparison gives

\[
 C_0=2^{a_u+1}-1,
 \qquad
 C_{r_t}=2^{a_{t+u}}-2^{a_t}\quad(t\not\equiv0\pmod q).
\]

For an integer lift of time `t`, define

\[
 W_t=
 \begin{cases}
 E_t,&q\mid t,\\
 E_t+\min(a_t,a_{t+u}),&q\nmid t.
 \end{cases}
\]

Because `E_t+a_t` and `E_{t+u}-c+a_{t+u}` are both strictly increasing,
`W_t=min(E_t+a_t,E_{t+u}-c+a_{t+u})` off the endpoint.  The adjacent endpoint
comparisons are strict as well.  Thus `W_t` is strictly increasing on all
integer times.

Every circular arc of P147 contains at most one representative of each
residue.  Its summands therefore have distinct 2-adic valuations.  The
summand with least valuation cannot cancel, so every such arc integer is
nonzero and

\[
 v_2(R_{\rm arc})=min_t W_t-A_{\min}.
\]

This closes the cancellation hypothesis left by P150 in the coprime setting.
It does not provide an upper bound strong enough when the profile area grows.

## 3. P174/P175 — resonance and fixed-area exclusion

Let `M` be reduced-polynomial support and `C` its `l1` norm.  Combining P147
with P173 gives the exact necessary inequalities

\[
 3^{\lceil q/M\rceil}<4C(12q)^{1,564,920,000}
\]

on the critical branch, and

\[
 2^{L\lceil q/M\rceil/q}<4C
\]

on the noncritical branch.  The first inequality uses `EXT17` (Matveev); the
second is internal.  With P171's fixed-area bounds
`M<=2A+1` and `C<=3*2^A-2`, both inequalities fail eventually for every fixed
`A`.  Hence only finitely many coprime primitive positive-cycle profiles can
have area at most a fixed `A`.  This is not a uniform arbitrary-area result.

## 4. P176 — arbitrary-gcd state bound

Let `d=gcd(q,L)`, `q=dq0`, `L=dL0`, and
`lambda0=3^q0/2^L0`.  At a maximum of the P156 reduced discrepancy profile,
each actual suffix coefficient is no larger than the corresponding repeated
mechanical-baseline suffix coefficient `c^(0)_(t,r)`.  With
`S^(0)_t=sum_(r=1)^q0 c^(0)_(t,r)`, the fixed-cycle identity and a geometric
sum over the `d` repetitions give

\[
 x_t\le {S_t^{(0)}\over3(1-\lambda_0)}
 <{2q_0\over3(1-\lambda_0)}.
\]

This applies to every gcd class and does not equate the least-value and
discrepancy-minimum rotations prohibited by NG36.

## 5. P177/P178 — reduced-period consequences

Using E28 (`V=300000`) and the exact Farey-neighbor pair

\[
 {1054\over665}<\log_2 3<{485\over306},\qquad665+306=971,
\]

an exact rational logarithm enclosure proves the required upper margin at
`q0=971`.  P176 therefore yields `q0>=971` for every primitive positive
nontrivial integer cycle.

The same argument with the X02 height input and its stated Farey pair yields
`q0>=72,057,431,991`.  Because X02 is external evidence rather than an
internally verified theorem, P178 is deliberately `CONDITIONAL`.

## 6. Independent finite verification (E41)

The generator and verifier use separate implementations.  The verifier does
not import `src.phase29_search`; it rebuilds recursive compositions, cyclic
classes, the time/residue permutation, coefficients, valuations, suffix
products, synthetic profiles, and 224-term rational log boxes.

It checked:

- 43,470 tied-largest-gap profiles and 93,629 individual arc cuts;
- 797 coprime cyclic classes through `q<=8` and five large legal profiles;
- 5,615 maximum-state rows across 2,214 all-gcd cyclic classes;
- the E28 and X02 Farey certificates;
- all mandatory adversarial families and NG34--NG38 controls.

Tamper tests reject changed digests, margins, endpoint data, removed external
dependencies, promotion of P178, and `proves_collatz=true`.

## 7. Remaining obstruction

P173 removes exact cancellation as the cause of H172.  The live obstruction
is quantitative: profile support and coefficient height can grow with area,
and the current resonance bounds do not dominate that growth.  A full-`D`
noncoprime resultant/nonvanishing theorem is also absent.  H172 and H133 stay
`OPEN`.

## What this result does not prove

It does not exclude arbitrary-area coprime cycles, any noncoprime cycle, either
nonperiodic P69 branch, or the Collatz conjecture.  Finite agreement is not an
asymptotic theorem, and the X02 consequence is not unconditional.
