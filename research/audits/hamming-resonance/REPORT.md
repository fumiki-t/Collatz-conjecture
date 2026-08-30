# Phase 25 audit — Hamming support and resonant area three

Status: accepted internal derivations, conditional reductions, exact finite
computations, and one refuted universal mechanism.  The repository remains
`OPEN`; `proves_collatz=false`.

## 1. Audit boundary

The attached note was not treated as mathematical authority.  Every accepted
formula was rederived using the full-shortcut critical-word convention and the
Phase 22--24 coprime residue-profile convention.  EXT04, X02, and EXT05 retain
their existing external statuses.

## 2. P151 — Hamming perturbation

Let equal-length words `u,v` differ in `H` positions.  A length-`n` factor of
`v` absent from `u` must start at a window containing at least one changed
position.  Each changed position lies in at most `n` linear windows, and in
exactly `n` cyclic windows when `1<=n<=L`.  Thus

\[
p_v(n)\le p_u(n)+nH,
\qquad
p_v^{\rm cyc}(n)\le p_u^{\rm cyc}(n)+nH.
\]

For a critical word, each nonzero labelled defect removes at most one old one
position and adds at most one new one position.  Therefore
`H(c_q,w)<=2s`.  P141's repaired finite-base bound gives

\[
p_w(n)\le(2s+1)n+2.
\]

The same labelled-boundary argument for a coprime cycle profile gives
`H(v_a,v_0)<=2s` and

\[
p^{\rm cyc}_{v_a}(n)\le(2s+1)n+1.
\]

Literal reconstruction verifies the sharper area-three values: Hamming 2 for
a doubled root, 4 for a root-child plus a second root, and 6 for three roots.
The validity recurrence prevents the boundary cancellations that would change
these values.

## 3. P152/P153 — conditional critical support squeeze

Assume P54 and pairwise-distinct states in the critical segment.  There are
`q-s` contact starts.  Removing starts from the final `n_q` positions leaves
at least `q-s-n_q` legal starts.  P125 and the exact P142 height width make
their length-`n_q` factors distinct.  P151 therefore yields

\[
q-s-n_q\le(2s+1)n_q+2,
\]

or

\[
q\le(2n_q+1)s+2n_q+2.
\]

For q0, the Phase 7 rational logarithm and delta enclosures, together with
the explicitly external EXT04 `S0` enclosure, certify

\[
2^{72}<S_0/\delta_{q_0}+q_0\le2^{73}.
\]

Thus `n_q0=73` and `s>=490186612`.  This does not become unconditional merely
because the interval arithmetic is exact.

For each positive defect, `w_j>1/2` and `1-2^{-a_j}>=1/2`; its normalized
loss is strictly greater than `1/4`.  Hence

\[
S(a)<S_0-s/4.
\]

P54 endpoint minimality gives `S(a)>=3N delta_q`, so

\[
s<4(S_0-3N\delta_q).
\]

At q0, X02 and the exact stored enclosures give the integer upper bound
`49,708,569,439`.  It is far above the support lower bound and does not exclude
the layer.

## 4. Area-three types

The Phase 24 recurrence gives exactly:

1. a doubled root and its forced predecessor;
2. two roots and the upper child of one root;
3. three independent roots.

For the first type, with `n=2q-L`, `gamma^n=4/3` and the reduced congruence is

\[
3+13\gamma^r(\gamma-1)\equiv0\pmod D.
\]

For the second type, `gamma^{L-q}=3/2` collapses a root-child pair to
`(5/2)gamma^r`, leaving at most five monomials after clearing two.  The third
type has the full paired seven-term polynomial.  These collapses are exact,
but no uniform exclusion of the first two families is claimed here.

## 5. NG34 — exact paired-arc falsifier

For `q=63322`, `L=100363`, and roots `q/7,2q/7,3q/7`, both the q-arc and
L-arc exact threshold comparisons fail.  The independently reconstructed
L-residues are

```text
0, 14338, 28525, 43013, 57200, 71688, 85875.
```

The proposal's nearby list was arithmetically wrong.  Direct modular gcd is
one, so the corrected row is not a cycle; it refutes only the universal
paired-width assertion.

## 6. P154 — resonant-grid resultant

Let `q=dQ`, put roots at `c_iQ`, and set `P(Z)=sum Z^c_i`, with no boundary
wrap.  If the coprime profile is integral, `z=gamma^Q` satisfies

\[
z^d\equiv2,
\qquad
(P(z)-1)^Q-zP(z)^Q\equiv0\pmod D.
\]

Therefore `D` divides the integer resultant of `Z^d-2` and
`R=(P-1)^Q-ZP^Q`.  If this resultant vanished over the complex numbers for
`Q>=2`, then `alpha=(P(z)-1)/P(z)` would satisfy `alpha^Q=z`.  Taking the
field norm gives `Q v_2(N(alpha))=1`, impossible because the valuation of the
rational norm is an integer.  Thus the resultant is nonzero.

At every root `|z|=2^(1/d)`, the triangle inequality gives

\[
|\operatorname{Res}|\le
(1+2^{1/d})^d M(d,P)^q,
\]

where `M` is the geometric mean of the selected conjugate maxima.  This is a
coprime theorem; it is not a noncoprime resultant replacement.

## 7. P155 — exact seven-grid exclusion

For `d=7` and `P=Z+Z^2+Z^3`, exact rational trigonometric intervals prove
that the positive conjugate selects `|P|` and every nonreal conjugate selects
`|P-1|`.  A direct integer determinant gives

\[
|\operatorname{Res}(Z^7-2,P-1)|=209.
\]

Since `P(theta)>3`,

\[
M^7=209{P(\theta)\over P(\theta)-1}<627/2,
\]

and `627*25^7<2*64^7`.  The exact comparison with the harmless factor
`(1+theta)^7<3^7` first succeeds at `Q=11`.  EXT05 then makes the nonzero
resultant strictly smaller than `D`, contradicting divisibility.  The nine
coprime rows among `1<=Q<=10` have direct modular gcd one; `Q=5` is explicitly
outside the coprime scope.

## 8. E37 and independence

The generator audits 502,523 critical words, 82,227 critical factor widths,
33,577 area-three profiles, and 167,884 selected cyclic factor widths.  The
verifier reconstructs weak profiles rather than trusting the classification,
uses a different Bezout representative and rational enclosure precision, and
computes resultants using a Sylvester matrix instead of the production
quotient-ring norm.  It imports no Phase 25 generator module.

## 9. H147 handoff

The exact resonance theorem closes the single seven-grid family that supplies
NG34.  It does not prove an inverse theorem.  The next valid target is a
quantitative statement that a two-arc failure is either one of finitely many
collapsed Type-A/B cases or lies in a controlled low-denominator
near-resonance class admitting a nonzero low-degree resultant.

## 10. What this result does not prove

The audit does not exclude all area-three coprime cycles, arbitrary-area or
noncoprime cycles, H89, H133, H147, H72, or Collatz.
`proves_collatz=false`.
