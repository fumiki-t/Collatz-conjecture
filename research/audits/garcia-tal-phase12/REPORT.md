# Garcia–Tal–Heppner sparsity and the Phase 11–12 nonperiodic branch

**Repository audit record — 2026-08-25**

This proof audit is archived with an independent finite certificate, verifier,
tamper tests, and a local SHA-256 manifest. Its four derivation labels are local
to the mathematical audit and are not repository claim statuses:

- `VERIFIED_DERIVATION`: checked derivation, with all external inputs named;
- `EXTERNAL_INPUT`: statement taken from a cited primary source and not
  reproved here;
- `FAILED`: proposed implication is false or is not supplied by the stated
  premises;
- `OPEN`: not resolved by this audit.

The source checkout audited was `main` at
`e1eb31bdf13c7084f3ac575ec0b9e3c1f09e6c0b`. The AI research control plane,
`docs/CLAIMS_LEDGER.md`, and `docs/context/H72.md` were read before doing the
derivations. The accepted ledger translation is EXT07 (`EXTERNAL_THEOREM`),
P74 and P75 (`CONDITIONAL`), NG22 (`REFUTED`), and E21
(`VERIFIED_FINITE`). Existing H70 and H72 remain `OPEN`.

## Executive result

| Item | Audit classification | Result |
|---|---|---|
| Garcia–Tal Proposition 1, (6), Corollary 1 | `EXTERNAL_INPUT` | The paper really gives a location-uniform interval bound stronger than Banach density zero. Its only unproved input here is Heppner's quantitative proposition. |
| Specialization to shortcut Collatz | `VERIFIED_DERIVATION` | `d=2`, `m=3`, `R_2={0,-1}` is exactly the repository's shortcut map. |
| Reciprocal orbit sum | `VERIFIED_DERIVATION` conditional on the external input | Every non-eventually-periodic positive shortcut orbit satisfies `sum_k 1/z_k < infinity`. |
| Banach density zero alone | `FAILED` | Banach density zero by itself does not imply reciprocal summability; equation (6), not merely Corollary 1, is essential. |
| Permanent-safe tail minimum | `VERIFIED_DERIVATION` conditional on the external input | Every nonperiodic positive orbit has an odd tail minimum from which every coefficient prefix is safe forever. |
| P69 finite-crossing renewal ladder | `FAILED` as a surviving nonperiodic branch once Garcia–Tal/Heppner is admitted | Under the external theorem, the nonperiodic finite-crossing ladder cannot occur. This does not eliminate cycles or permanent-safe tails. |
| Phase 12 defect | `VERIFIED_DERIVATION` conditional on the external input | `sum_j 2^{-a_j}<infinity`, hence `a_j -> infinity`, and `#{j:a_j<=A}=O_S((A+1)2^{beta A})`. |
| Timewise pointwise logarithmic defect | `FAILED` from the counting estimate alone | The count does not locate the last small-defect time. It gives a density-one logarithmic bound, not a bound for every large time. |
| Negative real companion | `VERIFIED_DERIVATION` | `h_n>1`, the forced branch recurrence holds, and `sum_n 1/h_n=infinity`. |
| Moving rational shadows | `VERIFIED_DERIVATION` | Exact real and 2-adic limits, errors, reduced denominator, and height identities hold. |
| Immediate Roth/Ridout/subspace contradiction | `FAILED` | The required algebraicity and height-relative approximation exponent are absent; the product formula is exactly compensated at odd primes. |
| Analytic conditions alone are contradictory | `FAILED` | An exact formal exponent construction satisfies all four requested analytic conditions and has a genuine odd 2-adic source. |
| Positive ordinary-integer source for that formal word | `OPEN` | No such source was found; an exact prefix calculation excludes every positive source below `2^1174`. |
| Literature-wide novelty of the elementary consequences | `OPEN` | Structural overlap is identified below, but no claim of literature-wide novelty is made. |

This audit does **not** prove the Collatz conjecture.

## 0. Conventions and quantifiers

### 0.1 Full shortcut orbit

Throughout Sections 1–2,

\[
T(z)=
\begin{cases}
z/2,&z\equiv0\pmod2,\\
(3z+1)/2,&z\equiv1\pmod2,
\end{cases}
\qquad z_k=T^k(z_0),
\]

with `z_0` a positive integer. Put

\[
\varepsilon_k=\mathbf 1_{z_k\text{ odd}},\qquad
m_k=\sum_{r=0}^{k-1}\varepsilon_r,\qquad
\Delta_k=m_k\log 3-k\log 2.
\]

“Nonperiodic” means “not eventually periodic”. For a deterministic map this
is equivalent to having an infinite orbit, and then all `z_k` are distinct.

### 0.2 Odd accelerated orbit

After the permanent odd tail minimum is selected, Sections 3–5 use

\[
x_{j+1}=\frac{3x_j+1}{2^{e_j}},\qquad
e_j=v_2(3x_j+1)\ge1,
\]

where every `x_j` is odd. Define

\[
E_0=0,\qquad E_j=\sum_{r=0}^{j-1}e_r.
\]

Thus `E_j` is the number of full shortcut steps from `x_0` to `x_j`. It is
the quantity called `d_j` in Phase 12. Put

\[
\theta_j=\{j\log_2 3\},\qquad
a_j=\lfloor j\log_2 3\rfloor-E_j,
\]

and

\[
Y_j=\frac{2^{E_j}x_j}{3^j}.
\]

No floating-point comparison is used in any proof below.

## 1. Garcia–Tal and Heppner

### 1.1 Primary-source statement

**Classification: `EXTERNAL_INPUT`.**

The source is M. V. P. Garcia and F. A. Tal, “A note on the generalized
3n+1 problem,” *Acta Arithmetica* 90 (1999), 245–250,
[DOI 10.4064/aa-90-3-245-250](https://doi.org/10.4064/aa-90-3-245-250),
[publisher PDF](https://matwbn.icm.edu.pl/ksiazki/aa/aa90/aa9033.pdf).

For their Hasse map `H`, Proposition 1 quotes Heppner. Under

\[
m<d^{d/(d-1)},
\]

there exist `delta_1,delta_2 in (0,1)` such that, with

\[
N(k)=\lfloor\log_d k\rfloor,
\]

and

\[
g(k)=\#\{n\le k:H^{N(k)}(n)\ge n k^{-\delta_1}\},
\]

one has

\[
g(k)=O(k^{\delta_2}).
\]

This quantitative estimate is not proved in Garcia–Tal; they cite
E. Heppner, “Eine Bemerkung zum Hasse–Syracuse Algorithmus,” *Archiv der
Mathematik* 31 (1978), 317–320. That Heppner proposition is the minimal
external assumption in the present audit.

Garcia–Tal's Theorem 1 then considers a complete set `P` of representatives
under equal-time collision,

\[
u\sim v\iff \exists r\ge0\quad H^r(u)=H^r(v),
\]

and proves, for **every** positive location `a` and length `k`, their equation
(6):

\[
\#(P\cap\{a,\ldots,a+k-1\})
\le
2(\lfloor\log_d k\rfloor+1)
\bigl(k^{1-\delta_1}+g(k)\bigr).
\tag{GT6}
\]

Corollary 1 states that every orbit has Banach density zero. Its proof also
records the point needed here: if an orbit is infinite, two distinct orbit
points never collide after the same number of further iterations, since such
a collision would make the orbit eventually periodic. Therefore the whole
infinite orbit may be included in one representative set `P`, and (GT6)
applies to the orbit itself.

### 1.2 Exact shortcut specialization

**Classification: `VERIFIED_DERIVATION`.**

Garcia–Tal define

\[
H(z)=
\begin{cases}
z/d,&z\equiv0\pmod d,\\
(mz-\phi(mz))/d,&z\not\equiv0\pmod d,
\end{cases}
\]

where `phi` chooses the representative in `R_d`. Set

\[
d=2,\qquad m=3,\qquad R_2=\{0,-1\}.
\]

If `z` is odd, `3z` has nonzero residue represented by `-1`, so

\[
H(z)=\frac{3z-(-1)}2=\frac{3z+1}{2}.
\]

If `z` is even, `H(z)=z/2`. This is exactly the full shortcut convention in
the repository. The parameter condition is strict:

\[
3<2^{2/(2-1)}=4.
\]

### 1.3 Uniform power-log interval bound

**Classification: `VERIFIED_DERIVATION` conditional on Proposition 1.**

Let

\[
\beta=\max(1-\delta_1,\delta_2)<1.
\]

The `O(k^{delta_2})` in Proposition 1 supplies constants `C_g,k_0`. After
enlarging one constant to cover `k<k_0`, (GT6) gives an absolute constant
`C_GT` for the fixed Collatz map such that every nonperiodic positive orbit
set `O` satisfies

\[
\boxed{
\#(O\cap[a,a+X))
\le C_{GT}X^\beta\log(2X)
}
\tag{1.1}
\]

for every integer `a>=1` and `X>=1`. Thus the location `a` is genuinely
uniform. The paper does not give numerical values of `delta_1`, `delta_2`,
or `C_GT`; the result is qualitative but its quantifiers are sufficient.

### 1.4 Dyadic shells imply reciprocal summability

**Classification: `VERIFIED_DERIVATION` conditional on (1.1).**

For `r>=0`, apply (1.1) to

\[
[2^r,2^{r+1}),
\]

whose length is `2^r`. Then

\[
\begin{aligned}
\sum_{x\in O\cap[2^r,2^{r+1})}\frac1x
&\le
2^{-r}\#(O\cap[2^r,2^{r+1}))\\
&\le C'(r+1)2^{-(1-\beta)r}.
\end{aligned}
\]

The last expression is summable because `1-beta>0`. Hence

\[
\boxed{\sum_{x\in O}\frac1x<\infty.}
\tag{1.2}
\]

The orbit is injective, so this set-sum is also

\[
\sum_{k=0}^\infty\frac1{z_k}<\infty.
\]

### 1.5 Minimal invalid shortcut

**Classification: `FAILED`.**

Corollary 1's Banach-density-zero conclusion alone is insufficient for
(1.2). For example, a set comparable to

\[
\{\lfloor n\log n\rfloor:n\ge2\}
\]

has gaps tending to infinity and hence Banach density zero, while its
reciprocal series behaves like `sum 1/(n log n)` and diverges. The valid
argument must retain the quantitative exponent `beta<1` in equation (6).

There was no defect in the required Garcia–Tal quantifier. The smallest
possible defect would have been relying only on the stated Corollary rather
than on the stronger displayed estimate used to prove it.

## 2. Permanent coefficient-safe tail

### 2.1 Exact product formula

**Classification: `VERIFIED_DERIVATION`.**

At one full shortcut step,

\[
z_{r+1}
=\frac{3^{\varepsilon_r}}2 z_r
\left(1+\frac{\varepsilon_r}{3z_r}\right).
\]

Multiplication from `r=0` to `k-1` gives

\[
\boxed{
z_k
=z_0\frac{3^{m_k}}{2^k}
\prod_{\substack{0\le r<k\\z_r\ {\rm odd}}}
\left(1+\frac1{3z_r}\right).
}
\tag{2.1}
\]

Taking logs,

\[
\log z_k
=\log z_0+\Delta_k
+\sum_{\substack{0\le r<k\\z_r\ {\rm odd}}}
\log\left(1+\frac1{3z_r}\right).
\tag{2.2}
\]

### 2.2 Discrepancy escape

**Classification: `VERIFIED_DERIVATION` conditional on (1.2).**

By `log(1+u)<=u`, (1.2) makes the correction sum in (2.2) converge to a
finite limit. Since the nonperiodic orbit is an injective sequence of
positive integers, `z_k -> infinity`: only finitely many distinct positive
integers lie below any fixed height. Equation (2.2) therefore forces

\[
\boxed{\Delta_k\longrightarrow+\infty.}
\tag{2.3}
\]

### 2.3 A permanent-safe minimum

**Classification: `VERIFIED_DERIVATION` conditional on (2.3).**

Because `Delta_k -> infinity`, it attains a global minimum at some finite
time `t`. For every `n>=t`,

\[
\Delta_n-\Delta_t
=(m_n-m_t)\log3-(n-t)\log2\ge0,
\]

so

\[
\boxed{3^{m_n-m_t}\ge2^{n-t}.}
\tag{2.4}
\]

Dividing (2.1) at times `n` and `t` gives

\[
\frac{z_n}{z_t}
=\frac{3^{m_n-m_t}}{2^{n-t}}
\prod_{\substack{t\le r<n\\z_r\ {\rm odd}}}
\left(1+\frac1{3z_r}\right).
\]

For `n>t`, equality between a positive power of 3 and a positive power of 2
is impossible, and the ratio is strictly greater than one. Thus

\[
z_n>z_t\qquad(n>t).
\tag{2.5}
\]

If `z_t` were even, `z_{t+1}=z_t/2<z_t`, contradicting (2.5). Hence `z_t`
is odd. It is simultaneously

1. a strict minimum of the actual tail;
2. a suffix minimum of the coefficient discrepancy; and
3. coefficient-safe for every future prefix.

This proves the requested permanent-safe tail statement, conditional only on
the named Garcia–Tal/Heppner external input.

### 2.4 Consequence for P69 and H70

**Classification: `VERIFIED_DERIVATION` as a strategic implication.**

The repository records this implication as conditional claim P74; H70 itself
remains `OPEN`.

P69 currently separates a hypothetical counterexample into a nontrivial
cycle, an infinite coefficient-safe tail, or a finite-crossing renewal
ladder. With Garcia–Tal/Heppner admitted, every nonperiodic positive orbit
enters the second branch. Therefore the finite-crossing renewal-ladder branch
does not survive as a possible nonperiodic integer orbit.

This does not make P70 or H70 mathematically false. It changes their strategic
role:

- H70 remains an internally formulated, exact spacing route that avoids this
  external analytic input and may be useful in generalized settings;
- it is no longer needed to eliminate a nonperiodic positive Collatz orbit if
  the Garcia–Tal/Heppner theorem is accepted;
- the remaining global alternatives are a nontrivial cycle and a permanent
  coefficient-safe tail;
- H72, augmented by the stronger conditions in Section 3, becomes the central
  noncycle target.

## 3. Phase 12 defect strengthening

Start the odd accelerated orbit at the permanent odd minimum `x_0=z_t`.
Then (2.4) says `3^j>2^{E_j}` for every `j>=1`, so `a_j>=0`.

### 3.1 Exact octave identity

**Classification: `VERIFIED_DERIVATION`.**

The odd recurrence gives

\[
Y_{j+1}=Y_j\left(1+\frac1{3x_j}\right),
\qquad
Y_j=x_0\prod_{r=0}^{j-1}\left(1+\frac1{3x_r}\right).
\tag{3.1}
\]

Also,

\[
\boxed{
\frac{2^{E_j}}{3^j}
=2^{-a_j-\theta_j}
=\frac{Y_j}{x_j},
\qquad
x_j=2^{a_j+\theta_j}Y_j.
}
\tag{3.2}
\]

### 3.2 Summable defects and pointwise escape

**Classification: `VERIFIED_DERIVATION` conditional on (1.2).**

The odd iterates form a subseries of the full orbit, so

\[
\sum_j\frac1{x_j}<\infty.
\]

Consequently (3.1) converges to a finite positive value

\[
Y_\infty
=x_0\prod_{r=0}^\infty\left(1+\frac1{3x_r}\right).
\]

Since `0<=theta_j<1`, (3.2) yields

\[
2^{-a_j}=2^{\theta_j}\frac{Y_j}{x_j}
\le\frac{2Y_\infty}{x_j}.
\]

Therefore

\[
\boxed{
\sum_{j=0}^\infty2^{-a_j}<\infty,
\qquad a_j\longrightarrow+\infty.
}
\tag{3.3}
\]

The second conclusion follows because the terms of a convergent positive
series tend to zero.

### 3.3 Garcia–Tal count for small defect

**Classification: `VERIFIED_DERIVATION` conditional on (1.1).**

Fix an integer `A>=0`. If `a_j<=A`, then by (3.2)

\[
x_j<2^{A+1}Y_\infty.
\]

The `x_j` are distinct members of the full orbit. With

\[
X_A=\left\lceil2^{A+1}Y_\infty\right\rceil,
\]

the interval estimate at location 1 gives

\[
\#\{j:a_j\le A\}
\le C_{GT}X_A^\beta\log(2X_A).
\]

Since `Y_infinity` is fixed for the orbit,

\[
\boxed{
\#\{j:a_j\le A\}
=O_{x_0}\bigl((A+1)2^{\beta A}\bigr),
\qquad \beta<1.
}
\tag{3.4}
\]

The exponent `beta` and the Garcia–Tal part of the constant depend only on
the fixed map. The displayed `O_{x_0}` additionally depends on the orbit
through `Y_infinity`. No uniform bound in the starting value is claimed.

For any fixed `c<1/beta`, (3.4) also gives

\[
\begin{aligned}
\#\{1\le j\le J:a_j\le c\log_2j\}
&\le
\#\{j:a_j\le \lfloor c\log_2J\rfloor\}\\
&=O_{x_0}\bigl((\log J+1)J^{\beta c}\bigr)
=o(J).
\end{aligned}
\]

Thus, on a density-one set of odd indices,

\[
\boxed{a_j>c\log_2j\quad\text{for every fixed }c<1/\beta.}
\tag{3.5}
\]

In particular, because `beta<1`, the coefficient `c=1` is valid. This is a
conditional strengthening of P72's `8/9-epsilon` density-one coefficient.

### 3.4 What (3.4) does not say

**Classification: `FAILED`.**

The bound counts all indices having `a_j<=A`, but it does not bound the
largest time at which one occurs. It therefore does **not** prove a
timewise pointwise estimate such as

\[
a_j\ge(1/\beta-o(1))\log_2j
\quad\text{for every sufficiently large }j.
\]

It proves (3.3) and the density-one assertion (3.5). Turning it into an
effective last-occurrence bound would require orbit-transition information
not present in Garcia–Tal's value-space interval estimate.

## 4. The negative real companion

Define the convergent tail product

\[
P_n=\prod_{r=n}^\infty\left(1+\frac1{3x_r}\right)
\]

and

\[
h_n=x_n(P_n-1)>0.
\]

### 4.1 Forced branch recurrence

**Classification: `VERIFIED_DERIVATION`.**

Using

\[
P_n=\left(1+\frac1{3x_n}\right)P_{n+1}
\]

and `2^{e_n}x_{n+1}=3x_n+1` gives

\[
\boxed{
h_n=\frac{1+2^{e_n}h_{n+1}}3,
\qquad
h_{n+1}=\frac{3h_n-1}{2^{e_n}}.
}
\tag{4.1}
\]

Hence `y_n=-h_n` satisfies

\[
y_{n+1}=\frac{3y_n+1}{2^{e_n}}.
\]

“The same exponent sequence” here means the same prescribed affine branch
word. It is not a claim that a real map selects `e_n` by a 2-adic valuation.

### 4.2 Strict lower bound `h_n>1`

**Classification: `VERIFIED_DERIVATION`.**

First suppose `0<h_n<1`. Positivity of `h_{n+1}` implies `3h_n-1>0`, and
because `e_n>=1`,

\[
h_{n+1}\le\frac{3h_n-1}{2}.
\]

Thus

\[
1-h_{n+1}\ge\frac32(1-h_n).
\]

Iteration would eventually make `1-h_{n+r}>1`, contradicting
`h_{n+r}>0`. Therefore `h_n>=1` for every `n`.

If `h_n=1`, (4.1) gives `h_{n+1}=2^{1-e_n}`. The already proved lower
bound forces `e_n=1` and `h_{n+1}=1`. Inductively all future exponents
would equal 1. But then the positive integer odd orbit would obey

\[
x_{n+r}+1=\left(\frac32\right)^r(x_n+1).
\]

Integrality for every `r` would require `2^r` to divide the fixed positive
integer `x_n+1` for every `r`, which is impossible. Hence

\[
\boxed{h_n>1\quad\text{for all }n.}
\tag{4.2}
\]

### 4.3 Divergent reciprocal companion sum

**Classification: `VERIFIED_DERIVATION`.**

The positive and negative products are

\[
x_n=x_0\frac{3^n}{2^{E_n}}
\prod_{r=0}^{n-1}\left(1+\frac1{3x_r}\right)
\tag{4.3}
\]

and

\[
h_n=h_0\frac{3^n}{2^{E_n}}
\prod_{r=0}^{n-1}\left(1-\frac1{3h_r}\right).
\tag{4.4}
\]

If `sum 1/h_r` converged, (4.2) would make the product in (4.4) converge
to a strictly positive limit. The product in (4.3) also has a strictly
positive finite limit. Their ratio would give

\[
\frac{h_n}{x_n}\longrightarrow c>0.
\]

But the definition gives

\[
\frac{h_n}{x_n}=P_n-1\longrightarrow0,
\]

a contradiction. Therefore

\[
\boxed{\sum_{n=0}^\infty\frac1{h_n}=\infty.}
\tag{4.5}
\]

## 5. Moving rational shadows

### 5.1 Prefix affine map

For the first `n` odd steps, define

\[
B_0=0,\qquad B_{n+1}=3B_n+2^{E_n}.
\]

Equivalently,

\[
B_n=\sum_{j=0}^{n-1}3^{n-1-j}2^{E_j}.
\tag{5.1}
\]

Then

\[
F_n(z)=\frac{3^nz+B_n}{2^{E_n}},
\qquad F_n(x_0)=x_n.
\tag{5.2}
\]

Permanent coefficient safety gives

\[
D_n=3^n-2^{E_n}>0
\]

for `n>=1`. Define

\[
H_n=\frac{B_n}{D_n}>0.
\]

The fixed point of the prefix affine map is `-H_n`, not `H_n`:

\[
F_n(-H_n)=-H_n.
\]

### 5.2 Real limit and exact error

**Classification: `VERIFIED_DERIVATION`.**

Put

\[
C_n=\prod_{r=0}^{n-1}\left(1+\frac1{3x_r}\right),
\qquad
\lambda_n=\frac{2^{E_n}}{3^n}=2^{-a_n-\theta_n}.
\]

The affine identity gives

\[
\frac{B_n}{3^n}=x_0(C_n-1).
\]

Therefore

\[
H_n=\frac{x_0(C_n-1)}{1-\lambda_n}.
\]

By (3.3), `lambda_n -> 0`, while `C_n -> P_0`. Hence

\[
\boxed{H_n\longrightarrow x_0(P_0-1)=h_0\quad\text{in }\mathbb R.}
\tag{5.3}
\]

There is also an exact error identity:

\[
\boxed{
H_n-h_0
=\frac{\lambda_n(h_0-h_n)}{1-\lambda_n}.
}
\tag{5.4}
\]

Indeed,

\[
\lambda_nh_n=x_0(P_0-C_n)\longrightarrow0.
\]

This also shows why (5.3) remains valid even if `h_n` is unbounded; it is
not legitimate to replace (5.4) by an unproved `O(lambda_n)` bound.

### 5.3 Real inverse-parity series

**Classification: `VERIFIED_DERIVATION`.**

Equation (5.1) says

\[
\frac{B_n}{3^n}
=\sum_{j=0}^{n-1}\frac{2^{E_j}}{3^{j+1}}.
\]

Unrolling (4.1), with the remainder controlled by
`lambda_n h_n -> 0`, gives

\[
\boxed{
h_0=\sum_{j=0}^\infty\frac{2^{E_j}}{3^{j+1}},
\qquad
y_0=-h_0=-\sum_{j=0}^\infty\frac{2^{E_j}}{3^{j+1}}.
}
\tag{5.5}
\]

Thus the negative companion is exactly the real value of the usual inverse
parity series for this word.

### 5.4 The 2-adic limit and exact error

**Classification: `VERIFIED_DERIVATION`.**

From (5.2),

\[
B_n=2^{E_n}x_n-3^nx_0.
\]

Consequently

\[
\boxed{
H_n+x_0
=\frac{2^{E_n}(x_n-x_0)}{D_n}.
}
\tag{5.6}
\]

The denominator `D_n` is odd. Nonperiodicity gives `x_n!=x_0` for `n>0`,
and both are odd, so

\[
v_2(H_n+x_0)=E_n+v_2(x_n-x_0)\ge E_n+1.
\]

Since `E_n>=n`,

\[
\boxed{
|H_n+x_0|_2\le2^{-E_n-1}\longrightarrow0,
\qquad H_n\longrightarrow-x_0\quad\text{in }\mathbb Q_2.
}
\tag{5.7}
\]

The same formal partial sums in (5.5) therefore tend to `h_0` over the
reals and to `-x_0` over `Q_2`; the factor `(1-lambda_n)^{-1}` in `H_n`
tends to 1 in both completions.

### 5.5 Reduced denominator and height

**Classification: `VERIFIED_DERIVATION`.**

Let

\[
g_n=\gcd(B_n,D_n).
\]

Modulo `D_n`, `3^n` is congruent to `2^{E_n}`. Since `D_n` is odd,
`2^{E_n}` is invertible modulo `D_n`, and

\[
\boxed{
g_n=\gcd(x_n-x_0,D_n).
}
\tag{5.8}
\]

Writing `H_n=b_n/q_n` in lowest positive terms,

\[
\boxed{
q_n=\frac{D_n}{\gcd(x_n-x_0,D_n)},
\qquad
b_n=\frac{B_n}{\gcd(x_n-x_0,D_n)}.
}
\tag{5.9}
\]

The naive projective height is exactly

\[
\boxed{\mathcal H(H_n)=\max(b_n,q_n).}
\tag{5.10}
\]

Moreover `q_n -> infinity`. If some fixed bound `Q` held along an infinite
subsequence, real convergence would bound the corresponding numerators, so
only finitely many reduced rationals could occur. One rational would repeat
infinitely often. Its real value would then be `h_0`, while its 2-adic value
would be `-x_0`, impossible because `h_0>1` and `-x_0<0`. Since
`H_n -> h_0>0`, (5.10) also makes `mathcal H(H_n)` comparable to `q_n` for
all sufficiently large `n`.

This is qualitative only. The gcd in (5.9) can be large, and no effective
lower bound for `q_n` in terms of `n`, `E_n`, or `D_n` has been proved.

### 5.6 Why standard Diophantine tools do not contradict the shadows

**Classification: `FAILED` for an immediate contradiction.**

1. **Product formula.** For the nonzero rational
   `R_n=H_n+x_0`, (5.6) makes the 2-adic norm small, but
   `|R_n|_infinity -> h_0+x_0>0`. The product formula is restored by the
   odd finite places, especially primes dividing the reduced denominator in
   (5.9). Those odd primes are not confined to a fixed finite set. There is
   no contradiction.

2. **Roth.** Roth's theorem concerns approximation to a fixed algebraic
   irrational real number at a rate beyond height exponent 2. Here the
   algebraicity, or even irrationality, of `h_0` is unknown. More
   importantly, (5.4) supplies no estimate of the form
   `|H_n-h_0| < mathcal H(H_n)^{-2-epsilon}`: `h_n` may grow and the gcd in
   (5.9) may collapse the reduced height.

3. **Ridout.** The 2-adic target in (5.7) is the rational integer `-x_0`,
   and 2-adic proximity alone can be arbitrarily strong for rational
   approximants. Again there is no exponent greater than 2 relative to the
   reduced height. Ridout's theorem does not turn (5.7) into a contradiction.

4. **Subspace theorem.** A mixed real/2-adic application would need fixed
   algebraic linear forms and a height-saving product inequality. The real
   coefficient `h_0` is not known algebraic, (5.4) and (5.7) have no proved
   joint height exponent, and the uncontrolled odd denominators absorb the
   product formula. The fact that the two completions have different limits
   is not itself exceptional; weak approximation permits such behavior.

Primary references for the conditions just invoked are K. F. Roth,
“Rational approximations to algebraic numbers,” *Mathematika* 2 (1955),
1–20, [DOI](https://doi.org/10.1112/S0025579300000644), and D. Ridout,
“The p-adic generalization of the Thue–Siegel–Roth theorem,” *Mathematika*
5 (1958), 40–48,
[DOI](https://doi.org/10.1112/S0025579300001339). No result from those papers
is used to prove (5.3)–(5.10).

## 6. Literature and novelty boundary

### 6.1 External results and direct overlap

**Classification: `EXTERNAL_INPUT`.**

1. **Garcia–Tal / Heppner.** Garcia–Tal's equation (6), based on Heppner,
   is the sole external theorem needed for Sections 1.3 through 3.3. The
   reciprocal-shell argument and its Collatz consequences are elementary
   deductions made in this audit; they are not stated as literature-new.

2. **Bernstein–Lagarias parity conjugacy.** D. J. Bernstein and J. C.
   Lagarias, “The 3x+1 Conjugacy Map,” *Canadian Journal of Mathematics* 48
   (1996), 1154–1169,
   [DOI](https://doi.org/10.4153/CJM-1996-060-x), establishes the 2-adic
   parity conjugacy and unique 2-adic reconstruction. The uniqueness of the
   2-adic source used in Section 7 is therefore standard structure, not a new
   claim.

3. **Rozier inverse parity series.** O. Rozier, “Parity sequences of the
   3x+1 map on the 2-adic integers and Euclidean embedding,” *Integers* 19
   (2019), A8, [arXiv:1805.00133](https://arxiv.org/abs/1805.00133),
   Corollary 2 writes

   \[
   x=-\sum_{k\ge0}s_k2^k3^{-\sigma_k}
   \]

   in `Z_2`. If the 1-bits occur at the odd-input times `E_j`, this is
   exactly

   \[
   x_0=-\sum_{j\ge0}\frac{2^{E_j}}{3^{j+1}}
   \quad\text{in }\mathbb Q_2.
   \]

   Equation (5.5) identifies the real value of the same series with
   `-h_0`. The inverse series itself is known; the present contribution is
   the conditional convergence route from Garcia–Tal and the exact linkage
   to the Phase 12 variables.

4. **López–Stoll.** J. López and P. Stoll, “The 3x+1 Conjugacy Map over a
   Sturmian Word,” *Integers* 9 (2009), 141–162,
   [DOI](https://doi.org/10.1515/INTEG.2009.014), studies inverse conjugacy
   over Sturmian/mechanical words. Their preprint “The 3x+1 Periodicity
   Conjeture in R,” [arXiv:2101.12747](https://arxiv.org/abs/2101.12747),
   studies the conjugacy as a real series and states a critical lower-density
   condition for rational 2-adic noncyclic trajectories. These are direct
   overlap for critical density and real inverse-series behavior. They do not
   supply the arbitrary-orbit interval sparsity (1.1), and this audit does
   not assume that a hypothetical orbit is Sturmian.

5. **Siegel `(p,q)`-adic correspondence.** M. C. Siegel, “The Collatz
   Conjecture & Non-Archimedean Spectral Theory: Part I,”
   [arXiv:2007.15936](https://arxiv.org/abs/2007.15936), constructs a mixed
   `(2,q)`-adic numen and proves correspondence statements for periodic
   points, together with one direction for divergent points. The elementary
   rational shadows `H_n` are compatible with that broad mixed-adic
   viewpoint, but (5.3)–(5.10) neither invoke the numen nor establish a new
   correspondence principle.

### 6.2 What is direct, what is external, what remains open

**Classification: `VERIFIED_DERIVATION` for the separation below.**

- **External theorem:** Heppner's exponent estimate as quoted in
  Garcia–Tal Proposition 1, and hence Garcia–Tal equation (6).
- **Direct consequences checked here:** reciprocal summability, discrepancy
  escape, the permanent-safe tail minimum, summable octave defects, the
  small-defect count, the negative companion identities, and both limits of
  `H_n`.
- **Known structural overlap:** parity conjugacy, inverse parity series,
  critical-density/Sturmian analysis, and mixed-adic correspondence.
- **Open arithmetic content:** exclusion of a positive integral source for
  every permanent-safe word; an orbit-transition strengthening of (3.4);
  effective control of the gcd and height in (5.9); and elimination of the
  nontrivial-cycle branch.
- **Open novelty question:** whether every elementary consequence in
  Sections 2–5 has appeared in exactly this form elsewhere. This audit did
  not perform an exhaustive literature-wide novelty search and makes no
  novelty claim.

## 7. Formal counterexample to an analytic-only contradiction

The target conditions were

\[
a_j\to\infty,\qquad
\sum_j2^{-a_j}<\infty,\qquad
h_j>1,\qquad
\sum_j\frac1{h_j}=\infty.
\tag{7.1}
\]

### 7.1 Exact construction

**Classification: `VERIFIED_DERIVATION`.**

Set `h_0=3/2`. Recursively choose

\[
e_j=
\begin{cases}
1,&1<h_j\le5/3,\\
2,&5/3<h_j\le2,
\end{cases}
\qquad
h_{j+1}=\frac{3h_j-1}{2^{e_j}}.
\tag{7.2}
\]

The interval `(1,2]` is invariant:

- if `1<h<=5/3`, then `1<(3h-1)/2<=2`;
- if `5/3<h<=2`, then `1<(3h-1)/4<=5/4`.

Therefore `1<h_j<=2` for every `j`, and

\[
\sum_j\frac1{h_j}\ge\sum_j\frac12=\infty.
\]

Define `E_j`, `theta_j`, and `a_j` from this exponent word exactly as in
Section 0.2. Iterating (7.2) gives

\[
\frac{h_j}{h_0}
=\frac{3^j}{2^{E_j}}
\prod_{r=0}^{j-1}\left(1-\frac1{3h_r}\right).
\]

Because `h_j/h_0>2/3` and `h_r<=2`,

\[
2^{a_j+\theta_j}
=\frac{3^j}{2^{E_j}}
\ge\frac23\left(\frac65\right)^j.
\tag{7.3}
\]

The cases `j=1,2` are directly `3>2` and `9>8`; (7.3) is greater than
one for `j>=3`. Hence the word is coefficient-safe, `a_j>=0`, and

\[
a_j\ge j\log_2(6/5)+\log_2(2/3)-1.
\]

Thus `a_j -> infinity` linearly and `sum 2^{-a_j}` converges geometrically.
All four conditions in (7.1) hold.

### 7.2 It also has a genuine odd 2-adic source

**Classification: `VERIFIED_DERIVATION`.**

Every such positive exponent word defines

\[
\boxed{
\xi_0=-\sum_{j=0}^\infty\frac{2^{E_j}}{3^{j+1}}
\in\mathbb Z_2.
}
\tag{7.4}
\]

The series converges 2-adically because `E_j -> infinity`, and its first
term makes `xi_0` odd. Every shifted tail `xi_j` is also odd and satisfies

\[
3\xi_j+1=2^{e_j}\xi_{j+1}.
\]

Thus `v_2(3xi_j+1)=e_j` exactly. The example is not merely a real formal
recurrence; it survives the unique 2-adic-source requirement.

What is not known is whether `xi_0` is a positive ordinary integer. If it
were, it would be a genuine permanent-safe Collatz orbit and hence a
counterexample. No such claim is made.

### 7.3 Exact finite positive-source search

**Classification: `VERIFIED_DERIVATION` for the finite statement; `OPEN`
globally.**

An exact rational/integer scratch calculation generated 1,026 exponents.
The canonical residues from the affine B recurrence were independently
cross-checked at lengths 64, 256, 1,024, and 1,026 against the direct
2-adic inverse-series sum; all four comparisons agreed exactly.
The first 64 are

```text
1211111121111111121111211111121111211112111111112111112111112111
```

At `n=1024`,

```text
E_1024 = 1174
a_1024 = 449
bit_length(r_1024) = 1172
SHA-256(big-endian r_1024) = a0cd4f2a2fe7583b916ce674299893ad6daec01b933739878b7c18aa49c1ac65
```

where `r_n` is the least nonnegative canonical source residue modulo
`2^{E_n}`. At `n=1026`,

\[
r_{1026}=r_{1024}+2\cdot2^{1174}.
\]

Any positive integer below `2^1174` realizing the infinite word would have
to equal `r_1024`, but that integer fails the longer prefix. Therefore the
exact finite conclusion is

\[
\boxed{\text{no positive ordinary source }M<2^{1174}.}
\tag{7.5}
\]

The computation used `fractions.Fraction`, integer powers, modular inverses,
and `bit_length`; floating point made no decision. A compact reproduction is:

```bash
python3 - <<'PY'
from fractions import Fraction
from hashlib import sha256

N = 1026
h = Fraction(3, 2)
es = []
for _ in range(N):
    e = 1 if h <= Fraction(5, 3) else 2
    es.append(e)
    h = (3*h - 1) / (1 << e)
    assert Fraction(1) < h <= Fraction(2)

E = B = 0
rows = {}
for n, e in enumerate(es, 1):
    B = 3*B + (1 << E)
    E += e
    modulus = 1 << E
    r = (-B * pow(pow(3, n, modulus), -1, modulus)) % modulus
    a = (3**n).bit_length() - 1 - E
    if n in (1024, 1026):
        rows[n] = (E, a, r)

E0, a0, r0 = rows[1024]
E2, a2, r2 = rows[1026]
assert (E0, a0, r0.bit_length()) == (1174, 449, 1172)
assert r2 == r0 + 2*(1 << 1174)
raw = r0.to_bytes((r0.bit_length()+7)//8, 'big')
assert sha256(raw).hexdigest() == (
    'a0cd4f2a2fe7583b916ce674299893ad6daec01b933739878b7c18aa49c1ac65'
)
print('exact formal obstruction verified')
PY
```

This finite bound is not evidence that no larger positive source exists.
The global positive-integrality question remains `OPEN`.

## 8. Final strategic assessment

### 8.1 Strongest valid conclusion

**Classification: `VERIFIED_DERIVATION` conditional on one external theorem.**

If Garcia–Tal equation (6), and therefore its Heppner input, is admitted,
then every nonperiodic positive shortcut Collatz orbit has all of the
following properties:

1. `sum_k 1/z_k < infinity`;
2. `Delta_k -> infinity`;
3. an odd permanent coefficient-safe tail minimum;
4. `sum_j 2^{-a_j}<infinity` and `a_j -> infinity`;
5. `#{j:a_j<=A}=O_{x_0}((A+1)2^{beta A})` for some universal `beta<1`;
6. a negative real companion with `h_j>1` and `sum 1/h_j=infinity`;
7. rational shadows converging to `h_0` in `R` and to `-x_0` in `Q_2`.

The Phase 11 finite-crossing renewal ladder is thereby removed from the
nonperiodic positive-integer branch, but the permanent-safe branch is not.

### 8.2 Exact bottleneck after the audit

**Classification: `OPEN`.**

The formal construction in Section 7 shows that all currently derived
analytic conditions, even together with a genuine odd 2-adic source, are
consistent. A proof route must use a property distinguishing positive
ordinary integers from general 2-adic sources. Plausible exact targets are:

- an effective lower bound on the least positive inverse-parity
  representative for words obeying (3.3)–(3.4);
- orbit-transition anti-concentration that bounds the **last time** of a
  small defect, not merely its total number;
- an effective upper bound on `gcd(x_n-x_0,D_n)` strong enough to convert
  (5.4) and (5.7) into a height-relative inequality;
- a proof that the simultaneous real/2-adic source generated by every such
  permanent-safe word cannot be a positive rational integer.

The mod-6 packing language refuted by NG21 cannot supply this distinction by
itself. Merely applying the product formula, Roth, Ridout, or the subspace
theorem without the missing height and algebraicity inputs is also a failed
shortcut.

### 8.3 What this result does not prove

- It does not prove or disprove the Collatz conjecture.
- It does not eliminate nontrivial cycles.
- It does not eliminate permanent coefficient-safe positive-integer tails.
- It does not prove H72.
- It does not turn Garcia–Tal's existential exponent into an effective
  certificate.
- It does not establish that any derivation in this audit is new in
  the literature.
- It does not change H70 or H72 from `OPEN`.

## 9. Reproduction and verification record

Generate the finite obstruction certificate:

```bash
.venv/bin/python src/garcia_tal_formal_obstruction.py \
  --output research/audits/garcia-tal-phase12/formal_obstruction.json
```

Run the independent inverse-series verifier:

```bash
.venv/bin/python verifier/verify_garcia_tal_formal_obstruction.py \
  research/audits/garcia-tal-phase12/formal_obstruction.json \
  --output research/audits/garcia-tal-phase12/verifier_result.json
```

The recorded verifier result is `valid=true`, `verified_depth=1026`,
`E21=VERIFIED_FINITE`, `NG22=REFUTED`, and `proves_collatz=false`.

Run the focused generator/verifier and tamper-rejection tests:

```bash
.venv/bin/python -m pytest -q \
  tests/test_garcia_tal_formal_obstruction.py
```

Result: `8 passed`. The whole repository result at acceptance was:

```text
210 passed in 254.84s
```

Verify the audit-local hashes from the repository root:

```bash
shasum -a 256 -c research/audits/garcia-tal-phase12/SHA256SUMS
```

The source checkout and accepted audit commit are separated deliberately:
the former is recorded at the start of this report, and the latter is recorded
in `PROVENANCE.md` after the audit content is committed.
