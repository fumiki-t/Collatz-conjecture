# Phase 34 audit — least-state/profile bridge and critical area 209

The supplied Phase 34 note was treated as an untrusted proposal. All accepted
decisions below use integers or exact rational enclosures. The least-value and
discrepancy-minimum rotations are never identified. `proves_collatz=false`.

## 1. P202: least-value/profile vertical bridge

Write the discrepancy-minimum critical boundaries as
`E_j=E0_j+a_j`, periodically extended. Since the mechanical boundary is a
ceiling sequence,

```text
|(E0_(t+r)-E0_t)-Lr/q| < 1.
```

For `lambda=3^q/2^L` this gives, without floating point,

```text
(1/2) lambda^(r/q) < C0(t,r) < 2 lambda^(r/q).
```

At an odd state minimum `m`, P133 gives `C(t,r)>lambda` for every proper
segment. Substituting `C=C0*2^(a_t-a_(t+r))` shows

```text
a_(t+r)-a_t < 1+(1-r/q)log2(1/lambda) < 2.
```

The left side is integral, so every coordinate is at most `a_t+1` and
`h<=a_t+1`. This transports only vertical profile information; it does not
assert that `t` is a discrepancy-minimum rotation. NG36 is unchanged.

## 2. P203: least-state exponential moment

Unrolling the affine return map from `t` gives the exact identity

```text
m(1-lambda)=(lambda/3) sum_(r=0)^(q-1) 1/C(t,r).
```

The lower mechanical coefficient bound implies `lambda/C0(t,r)<2`, hence

```text
m(1-lambda) < (2/3)2^(-a_t) sum_j 2^a_j
            < (4/3)2^(-h) sum_j 2^a_j.
```

Convexity of `2^x` on the integer profile interval `[0,h]` gives

```text
m(1-lambda) < (4/3)[q2^(-h)+(1-2^(-h))A/h].
```

After clearing positive denominators, strictness is retained by subtracting
one from the integer numerator:

```text
m_prof=floor((4*2^L*(qh+A(2^h-1))-1)/(3(2^L-3^q)h2^h)).
```

The usable state bound is `min(m_P133,m_prof)` for each legal height.

## 3. P204/E48: exact area-209 bootstrap

Assume `118<=A<=208`. P180 gives

```text
L < 5015+209 log2(q/(3 lambda(1-lambda))).
```

EXT17 and the elementary rational bounds at `Q=10^13` give cutoff margin
`1383372477367/3`; the derivative upper bound is
`981204840627/20000000000000 < 19/12`. Thus `q<Q`. P177/P199 give
`d<19136/81`, hence `d<=236`. For `q>=8192`, the exact exponent comparison
is already `-6311/627`, so Legendre reduces the slope to an upper regular
convergent of `log2(3)`.

Separate outward log series reconstruct nine upper convergents and 1,725
legal multiples. Every row violates the P180 envelope. For `971<=q<=8191`,
the independent optimizer reconstructs 7,221 rows: 1,216 reduced-period
rejections, 5,979 state/E46 rejections, 26 admissible rows, and no P195
survivor. The closest row is `q=2301,L=3647,A=208`, with margin `-32`.

Therefore every critical primitive positive nontrivial integer cycle has
`A>=209`. This is P204. E48 is the bounded reconstruction, not an asymptotic
claim.

## 4. Exact obstruction

At `A=209`, the first scalar survivor is

```text
(q,L,h,J,Sigma,E,n,Z)=(2301,3647,2,105,103,105,24,10),
RHS-3L=24,
m_P133=860946,
m_prof=978246,
583561<=m<=860946.
```

No trajectory certificate for this interval was generated. Repeating finite
height bootstraps is not a uniform arbitrary-area argument.

## 5. P205: first 2-adic defect

Let `f_j=floor(j log2 3)`, `d_j=f_j-a_j`, and work modulo `2^K`. Directly
subtracting the two inverse affine source series gives

```text
r(w)-r(c_q) = sum_(a_j>0) 3^(-j-1)2^d_j(2^a_j-1)  (mod 2^K).
```

The edited odd positions `d_j` are strictly increasing and each remaining
coefficient is odd. The unique least 2-adic valuation therefore survives:

```text
v2(r(w)-r(c_q))=min_(a_j>0)d_j.
```

Before the first defect all labels agree. Since a mechanical gap is one or
two and edited odd positions must remain strictly increasing, the first
positive defect can only occur across gap two and must have `a_j=1`.
The valuation then identifies that first label. P205 stops here: overlapping
later edits and relabeling prevent an unaudited branch-free iteration.

## 6. Independent finite evidence

The independent verifier imports no generator or `src`. It reconstructs:

- all 1,725 CF candidates and 7,221 low-`q` rows;
- 10,103 positive critical rational discrepancy-minimum rotations through
  `q<=12`, including every proper segment coefficient and fixed-point identity;
- 21,766 legal binary-profile defect rows through `q<=18`;
- mandatory adversarial family metadata and all interpretation boundaries.

No `a_t=h-1` control was found in the bounded rational corpus. This is only a
finite observation and is not promoted to `a_t=h`.

## What this result does not prove

The result does not exclude area 209 or arbitrary area, close H89/H133/H172,
exclude either nonperiodic branch, or prove or disprove Collatz.
`proves_collatz=false`.
