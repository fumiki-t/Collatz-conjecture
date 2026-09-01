# Phase 32 audit — triple-hit capacity and full-cofactor rigidity

## Scope and status

The supplied Phase 32 note was treated as an untrusted proposal.  This audit
accepts P195--P199 and bounded result E45.  The proposed eventual `d=s=6`
exclusion is not accepted; its missing effective classification is H200 OPEN.
H172 and H133 remain OPEN. `proves_collatz=false`.

## 1. Conventions

Let the repeated reduced mechanical word have shortcut length `L`, odd count
`q`, zero count `p=L-q`, and zero density `eta=p/L`.  Apply P185 at a fixed
discrepancy-minimum rotation.  It produces `K=J-E` pairwise-disjoint static
singleton swaps `10->01` and an `E`-component residual word.  For cyclic
length-`n` factors let `U` be the starts whose residual length-`(n+2)` context
differs from the mechanical context.  P186 gives

```text
|U| <= min(L, 2A+E(n+1)).
```

This rotation is not silently identified with P133's least ordinary state.

## 2. P195 — finite triple-hit inequality

A mechanical binary word is balanced, so each cyclic factor of length `m`
contains at most `ceil(pm/L)` zeros.  An adjacent singleton swap affects a
length-`n` factor only when its swapped zero is in an interval of `n+1`
mechanical positions.  Therefore a fixed mechanical length-`(n+2)` context
contains at most

```text
Z_n = ceil(p(n+1)/L)
```

eligible anchors.  Mechanical length-`(n+2)` contexts have at most `n+3`
types.  Thus the factors outside `U` hit by exactly `r=0,1,2` extracted swaps
have at most

```text
C_r(n)=(n+3) binom(Z_n,r)
```

types.  If all `L` cyclic length-`n` factors are distinct, their corresponding
start counts satisfy the same bounds.  Writing `H_t` for singleton incidence,
each swap contributes at most `n+1`, hence

```text
sum_t H_t <= K(n+1).
```

Every nonexceptional start not counted at hit levels zero, one, or two has at
least three hits.  Consequently

```text
3(L-|U|)-3C_0-2C_1-C_2 <= K(n+1).
```

Substituting `K=J-E` and the P186 bound proves

```text
3L <= (J+2E)(n+1)+6A
      +(n+3)[3+2Z_n+binom(Z_n,2)].
```

No equality of influence-set sizes is used.  A positive-density residual core
remains visible through `E`.

## 3. P196 — optimized triple-hit area constant

Use exactly the P193 cycle regime: primitive positive cycle candidates with
`q->infinity`, `L/q->ell in (1,2]`, a fixed inverse-polynomial multiplier gap,
and state-separation width `n=h+O(log q)`.  On a subsequence with bounded
`A/q^(2/3)`, pass to convergent normalized variables

```text
x=J/q^(2/3), y=h/q^(1/3), z=Sigma/q^(2/3).
```

P193 gives `xy>=2ell`.  Since `E<=h+Sigma`, division of P195 by `q` gives

```text
(x+2z)y+(eta^2/2)y^3 >= 3ell,
eta=(ell-1)/ell.
```

P167 gives the objective

```text
A/q^(2/3) >= x+z+y^2/[2(ell-1)].
```

For fixed `y`, the minimum uses

```text
x=2ell/y,
z=[ell-(eta^2/2)y^3]/(2y).
```

The one-variable derivative then gives

```text
y^3=5ell/[2/(ell-1)-eta^2].
```

The denominator is positive and `z>0` throughout `1<ell<=2`; the exact check
reduces to `7 eta^2(ell-1)<4`.  Substitution proves

```text
C_3(ell)
 = (3/4)(5ell)^(2/3)[2/(ell-1)-((ell-1)/ell)^2]^(1/3).
```

Its cube is strictly decreasing on this interval.  At `ell=2` it is exactly
`4725/64`, placing the constant in `(4.195083,4.195084)`.  With EXT17 and an
outward rational enclosure of `log_2 3`, the critical constant lies in
`(4.430667,4.430668)`.  Only this critical specialization depends on EXT17.
The larger diagnostic obtained by separately imposing `z=0` is not promoted.

## 4. P197 — exact full-cofactor decomposition

Write

```text
q=dq0, L=dL0, R=2^L0, S=3^q0,
M_d=sum_(c=0)^(d-1) R^c S^(d-1-c).
```

For the repeated mechanical baseline, its boundary at `cq0+t` is
`cL0+E_t^(0)`.  The actual boundary adds profile value `a_(cq0+t)`.
Splitting the affine correction by blocks therefore gives exactly

```text
C_c=sum_(t<q0) 3^(q0-1-t)2^(E_t^(0)+a_(cq0+t)),
B=sum_(c<d) R^c S^(d-1-c) C_c.
```

The baseline block correction `B0` gives

```text
B=B0 M_d+Delta,
Delta=sum_(j<q)(2^a_j-1)2^E_j^(0)3^(q-1-j).
```

For an integral cycle, `(R^d-S^d)=(R-S)M_d` divides `B`, so `M_d|Delta`.
The converse is not asserted: the missing `R-S` factor matters.

## 5. P198 — primitive block oscillation

For a positive integral block-boundary source `x0=B/(R^d-S^d)`, put
`k=(R-S)x0`.  Then

```text
sum_(c<d)(C_c-k)R^cS^(d-1-c)=0.
```

Thus `SX-R` divides `P(X)=sum(C_c-k)X^c` in `Z[X]`.  If `P` is nonzero, its
lowest nonzero coefficient is a nonzero multiple of `R`.  The same identity
makes `k` a positive weighted average of the `C_c`, so

```text
max C_c-min C_c >= R.
```

If `P=0`, all `C_c` agree.  The map from strictly increasing boundaries
`F_0<...<F_(q0-1)` to `sum 3^(q0-1-t)2^F_t` is injective: repeatedly take the
2-adic valuation, subtract the recovered lowest term, and continue.  Equal
block corrections therefore give identical exponent blocks.  For `d>1` the
word is a proper power, contradicting primitivity.  Positivity/integrality is
essential to the weighted-average step; rational shadows remain controls.

## 6. P199 — positive support arc and the area-six gcd reduction

Assume `M_d|Delta`, and let the positive profile support have size `s`.  Cut
after a largest cyclic support gap and lift the remaining support to an
interval `[u,u+W]`, where `W<=q-ceil(q/s)`.  Extend the mechanical boundary by

```text
E0(t)=ceil(Lt/q), E0(t+q)=E0(t)+L.
```

Because `2^L=R^d` and `3^q=S^d` are congruent modulo `M_d`, shifting a term by
`q` does not change the normalized residue.  After multiplication by common
powers of two and three, the exact positive integer is

```text
R_time=sum_(t in support lifts)
 (2^a_t-1) 2^(E0(t)-E_min) 3^(u+W-t),
M_d | R_time.
```

Mechanical balance gives `E0(t)-E_min<=L(t-u)/q+1`, while
`3^(u+W-t)<2^(L(u+W-t)/q)`.  Finally
`sum(2^a_t-1)<=2^A-1`.  Hence, with no cancellation,

```text
0<R_time<2^[A+1+(L/q)W].
```

Since `M_d>R^(d-1)=2^(L-L0)`, this proves

```text
(L/q)ceil(q/s)<L0+A+1.
```

For critical area six, P177 supplies `q0>=971,L0>=1539`.  Since `s<=6`, the
last inequality gives `d<s(1+7/L0)<s+1`, hence `d<=s<=6`.  This is a six-class
reduction, not an exclusion.

## 7. H200 — why the proposed bounded-grid exclusion remains open

For `A=s=d=6`, using the actual largest gap in the preceding proof gives
`q0-20<=g_i<=q0+4`.  This does reduce support to six columns with bounded
offsets.  The supplied note then invokes a finite coefficient set, a uniformly
bounded quotient, an infinite constant subsequence, and coefficient-identity
classification.  It does not enumerate that set, give an explicit first
exceptional `(q0,L0)`, or check every identity.  The asserted conclusion is
therefore not yet an independently reproducible effective theorem.  H200 is
the exact missing classification/cutoff obligation.

## 8. Independent finite audit

The generator and verifier independently reconstructed:

```text
positive-D cyclic classes              7,398
discrepancy-minimum rotations          10,485
cyclic widths                          174,290
0/1/2 capacity checks                  522,870
distinct-factor widths                 110,899
full-cofactor decompositions           10,485
noncoprime decompositions                7,543
M_d-divisible profile rows               2,959
positive support-arc certificates        2,936
positive integral rows                       9
primitive noncoprime integral rows           0
```

The nine integral rows are trivial-cycle powers/rotations; they do not test a
nontrivial primitive premise.  The 2,936 positive arcs deliberately include
nonintegral `M_d|Delta` shadows to exercise the arc arithmetic while retaining
an explicit `integral_positive=false` marker.  The verifier imports no
generator or `src` module.  Tampered theory, corpus declarations, and
overclaims are rejected.

## What this result does not prove

This result does not exclude `d=s=6`, any other area-six class, arbitrary-area
positive cycles, the finite-crossing or permanent-safe nonperiodic branch, or
the Collatz conjecture. `proves_collatz=false`.
