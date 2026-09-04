# Phase 36 audit — root intervals and the positive event polynomial

The supplied Phase 36 note was treated as an untrusted proposal.  Its cycle
root localization, bounded-root capacity, shifted positive recurrence, and
coprime event polynomial survive exact reconstruction.  They eliminate the
exact Phase 35 area-229 scalar obstruction and raise the accepted critical
cycle-area floor to `A>=230`.  The proposed transfer of the same root
intervals to the P206 decoder has the opposite orientation and is refuted;
a corrected mirror-localization theorem survives.  `proves_collatz=false`.

## 1. P211 — cycle root localization, factor complexity, and gaps

Fix a discrepancy-minimum reduced cycle profile

```text
a_0=a_q=0,  a_j>=0,
E_j=E_j^(0)+a_j,
```

where the repeated reduced-mechanical exponents are in `{1,2}` and the
actual odd boundaries are strictly increasing.  Let the level-one support be
the disjoint ordinary intervals `[u_i,v_i)` and define binary root intervals

```text
I_i=[E^(0)_(u_i),E^(0)_(v_i)).
```

For `u_i<=j<v_i`, nonnegativity gives `E_j>=E_j^(0)>=E^(0)_(u_i)`, while
strict increase and `a_(v_i)=0` give
`E_j<E_(v_i)=E^(0)_(v_i)`.  Old and new odd markers outside the level-one
support coincide.  Thus every changed binary position lies in the disjoint
union of the `I_i`.  If `s_i=|I_i|`, then

```text
T_1=sum_i s_i <= 2 sum_i(v_i-u_i).
```

A cyclic length-`n` window meets `I_i` from at most `s_i+n-1` starts.
Every other window is mechanical, so for `1<=n<=L`,

```text
p_cyc(n) <= p_0(n)+T_1+U(n-1) <= n+1+T_1+U(n-1).
```

If all `L` target factors are distinct and `G_i` are the complementary
binary gaps, every root-free start produces a distinct mechanical factor.
Mechanical balance therefore gives

```text
sum_i (G_i-n+1)_+ <= n+1,
G_i <= 2n.
```

The last implication also covers `G_i<n` directly.  No asymptotic or
floating-point step is used.

## 2. P212 — one-root-hit capacity

Suppose a cyclic target differs from a mechanical baseline only in `U`
disjoint intervals of span at most `R`.  After a mechanical context and
relative placement are fixed, suppose at most `C` replacement strings are
legal.  Let `I` be the total number of start/root incidences.  Then

```text
I <= U(n+R-1).
```

Root-free factors have at most `n+1` types.  A factor meeting exactly one
root is determined by a mechanical context of length at most `n+R-1`, one of
at most `n+R-1` relative placements, and one of `C` replacements.  Hence
there are at most `C(n+R)(n+R-1)` such types.

If all target factors are distinct, write `N_0,N_1,N_2` for starts meeting
zero, one, or at least two roots.  Since `I>=N_1+2N_2`,

```text
2L <= I+2N_0+N_1
   <= U(n+R-1)+2(n+1)+C(n+R)(n+R-1).
```

The proof includes cyclic wraparound and uses the explicit `U,R,C`
hypotheses; it is not a uniform all-area cycle theorem.

## 3. P213 — the exact NG41 scalar tuple is not realizable

The Phase 35 survivor is

```text
(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,229,2,138,90,92,24,10).
```

Here the P185 spine charge is

```text
B_h=floor(2301/(3647-2301))=1,
A-J=B_h+Sigma=91,
E=h+Sigma=92.
```

The exact P208 margins for `2<=E<=92` are negative through `E=91` and
equal `43` at `E=92`.  Hence any profile at this scalar boundary must attain
equality in P185.  Equality forces the level-one spine component and every
nonspine nonsingleton level-one component to have odd-label length exactly
two; singleton components have length one.  Height two and descent legality
leave exactly the root profiles

```text
[1], [1,1], [2,1].
```

Their mechanical binary spans are at most four.  A height-two profile has at
least one level-two component, so the number of level-one roots satisfies
`U<=J-1=137`.  P212 at `(n,R,C)=(24,4,3)` would require

```text
2L <= 137(27)+2(25)+3(28)(27)=6017,
```

but `2L=7294`.  Therefore the scalar tuple cannot be the reduced profile of
a primitive positive integer cycle.  This is a profile nonrealizability
theorem, not evidence that the scalar optimizer itself was wrong.

## 4. P214/E52 — corrected critical floor `A>=230`

The consequence was not inferred from the displayed tuple alone.  The full
Phase 35 split was rerun at `A=229`.  P199 gives

```text
d < 229(1539+230)/1539 = 405101/1539,
```

so `d<=263`.  Exact rational-log continued fractions produce 1,926 legal
upper-convergent multiples below `q<11,500,000,000,000`; all fail the
area-229 envelope.  The independent low-`q` audit reconstructs all 7,221
rows for `971<=q<=8191`:

```text
q0 rejections:           1216
state/E46 rejections:    5979
P208 rejections:           25
P207 rejections:            0
joint scalar survivors:     1
```

The sole survivor is exactly the P213 tuple, now excluded by root capacity.
Together with the accepted Phase 33--35 inputs, every critical primitive
positive nontrivial integer cycle therefore has reduced-profile area
`A>=230`.  A diagnostic at area 230 still has the row

```text
(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,230,2,139,90,92,24,10),
P207 margin=35, P208 margin=68.
```

No larger floor is claimed without a new complete frontier audit.

## 5. P215 — shifted positive recurrence

For an odd positive cycle `2^e_j x_(j+1)=3x_j+1`, set
`y_j=(x_j+1)/2`.  Direct substitution gives

```text
2^e_j y_(j+1)=3y_j+(2^(e_j-1)-1).
```

Iterating one period, with `E_j=sum_(i<j)e_i` and
`D=2^L-3^q`, gives the exact positive divisor identity

```text
D y_0=sum_j (2^(e_j-1)-1) 2^E_j 3^(q-1-j).
```

Every summand is nonnegative and the support is precisely `e_j>=2`.
Formal rational fixed points used in the finite audit are scope controls;
they are not promoted to positive integral cycles.

## 6. P216 — coprime positive event polynomial

Assume `gcd(q,L)=1`, put `r_t=[-Lt]_q`, `s=2q-L`, and work in
`Z[X]/(X^q-2)`.  For

```text
A_a(X)=sum_t 2^a_t X^r_t,
P_a(X)=(2-X^s)A_a(X),
```

the coefficient at `r_(t+1)` is reconstructed with the quotient wrap factor:

```text
C_(t+1)=2^(a_t+2-e_t^(0))(2^(e_t-1)-1) >= 0.
```

Thus `supp(P_a)={r_(t+1):e_t>=2}`.  Using
`e_t=e_t^(0)+a_(t+1)-a_t`, summing the displayed coefficients gives the
exact norm

```text
||P_a||_1=sum_(t:e_t^(0)=2) 2^a_t.
```

For the coprime slope root `gamma`, `gamma^q=2` and `gamma^L=3`
modulo `D`, hence `gamma^s=4/3` and
`2-gamma^s=2/3` is a unit.  Consequently

```text
A_a(gamma)=0 mod D  iff  P_a(gamma)=0 mod D.
```

All nonzero event coefficients are positive, so its sparse circular-arc
integer is positive without an odd-coefficient cancellation argument.

## 7. P217 — event-arc inequalities

Let

```text
M=#{t:e_t>=2},
C=sum_(t:e_t^(0)=2) 2^a_t.
```

Applying P147 to the positive event polynomial gives the exact necessary
conditions

```text
critical:     3^ceil(q/M) < 4C(12q)^1564920000,
noncritical:  2^(L ceil(q/M)/q) < 4C.
```

The critical statement retains EXT17.  The event polynomial is currently a
coprime-slope tool; neither inequality excludes arbitrary area.

## 8. NG42/P218 — decoder orientation and mirror repair

The cycle profile moves odd boundaries right:
`E_j=E_j^(0)+a_j`.  P206 instead decodes safe positions
`d_j=f_j-a_j`, which move left.  Directly reusing the cycle interval
`[f_u,f_v)` is therefore false.  The smallest exhaustive counterexample is

```text
q=3, K=5,
actual positions=(0,1,2), mechanical positions=(0,1,3),
profile=(0,0,1), changed binary positions={2,3}.
```

The naive interval `[3,5)` misses position 2.  This is NG42.

A corrected exact statement survives.  Extend `f_q=K`.  For each level-one
component `[u,v)` of the decoded profile, `u>=1` and strict increase gives

```text
f_(u-1)+1 <= d_j < f_v  for u<=j<v.
```

Both old and new odd markers therefore lie in the pairwise-disjoint mirror
interval

```text
[f_(u-1)+1,f_v).
```

This is P218.  It localizes changes but supplies no smaller positive source,
signed carry, or ancestor relation.

## 9. E51/E52 and independent verification

E51 exhausts the positive-`D` cyclic exponent corpus through `q<=8`:

```text
cyclic classes:                 2214
minimum rotations:             3101
factor-width checks:          45369
distinct-factor checks:       27832
coprime event classes:          797
event support coefficients:    2908
```

It checks root localization, all factor/gap inequalities, the shifted
rational recurrence, positive/signed arc certificates, support, norm, and
modular equivalence.  Its one integral fixed point is the trivial cycle.

E52 independently reconstructs the 1,926-member area-229 high frontier, all
7,221 low-`q` rows, the exact root-capacity contradiction, and all 1,166,058
P206 safe words through `q<=18`.  The decoder corpus confirms the mirror
theorem and preserves the first NG42 counterexample.

The Phase 36 verifier imports neither the Phase 36 generator nor `src`.  It
independently rebuilds both corpora and reuses only the previously accepted
Phase 35 *verifier* arithmetic for the shared cutoff/CF/decoder primitives.
Tamper tests reject root, event, scalar, decoder, and overclaim changes.

## 10. Remaining strategic boundary

The new H172 split is still open:

1. root-sparse/short-root profiles should violate factor capacity;
2. root-dense/event-dense profiles should violate the positive divisor or
   full-`D` resultant constraints.

No uniform incompatibility between these alternatives is known.  H133 still
needs an arbitrary-area cycle exclusion, and H89 still needs ordinary source
order, positivity, ancestry, and carry after P206/P218 decoding.

## What this result does not prove

Phase 36 does not exclude area 230 or arbitrary-area positive cycles, prove a
root/event dichotomy, turn mirror roots into smaller ancestors, close H89,
H133, or H172, address either nonperiodic branch, or prove or disprove the
Collatz conjecture.  `proves_collatz=false`.
