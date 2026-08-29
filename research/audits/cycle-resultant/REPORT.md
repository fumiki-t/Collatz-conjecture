# Phase 22 audit — cycle slope profiles, resultants, and near-Christoffel exclusion

Status: accepted repository derivations and bounded computations; the positive
nontrivial-cycle branch and Collatz remain `OPEN`; `proves_collatz=false`.

## 1. Convention, repaired scope, and literal legality

Use the odd accelerated map

\[
x_{i+1}=(3x_i+1)/2^{e_i},\qquad e_i=v_2(3x_i+1)\ge1.
\]

For a word `e=(e_0,...,e_(q-1))`, put `L=sum e_i`, `E_0=0`,
`E_j=sum_(i<j)e_i`,

\[
B(e)=\sum_{j=0}^{q-1}3^{q-1-j}2^{E_j},\qquad
D=2^L-3^q.
\]

Direct induction gives

\[
2^Lx_q=3^qx_0+B(e).
\]

Thus a positive fixed point requires `D>0` and `D|B`. Conversely, if these
hold then `x=B/D` is odd, and the fixed-point equation modulo `2^L` places
`x` in the unique finite parity cylinder of the expanded shortcut word
`10^(e_0-1)...10^(e_(q-1)-1)`. Hence all literal valuations are forced. The
word can still be a power of a shorter period; primitivity is a separate
condition. This repairs the proposal's ambiguous phrase “and literal
legality”: divisibility implies legality here, but not primitive period.

A nontrivial positive cycle also has `L<2q`. Indeed,

\[
2^L/3^q=\prod_i(1+1/(3x_i))<(4/3)^q
\]

because every odd cycle value exceeds one. Therefore the finite admissible
range `q<L<2q` is correct for nontrivial positive cycles; `L=2q` retains only
powers of the trivial cycle in the bounded regression.

## 2. P133 — coefficient valley at a cycle minimum

Rotate a primitive positive cycle to its least odd value `m`. For the expanded
shortcut period, let `c_t=3^{q_t}/2^t` and `lambda=c_L=3^q/2^L`.
At time `t`, the remaining suffix has coefficient `lambda/c_t`.

If that suffix contains an odd step and `c_t<=lambda`, its coefficient is at
least one and its positive affine correction makes its endpoint strictly
larger than its positive start, contradicting return to `m`. If the suffix is
all even, its coefficient is strictly below one, which itself contradicts
`lambda/c_t>=1`. Hence every proper prefix obeys

\[
c_t>\lambda.
\]

At odd boundaries `c_j=3^j/2^{E_j}`. With

\[
\beta=B/3^q=\sum_{j<q}\frac1{3c_j},
\]

the fixed-point equation is `m=lambda(m+beta)`. Strict prefix valley gives
`beta<q/(3lambda)` and therefore

\[
m(1-\lambda)=\lambda\beta<q/3.
\]

This proof is cycle-internal and uses no least-counterexample hypothesis.

## 3. P134 — cycle G170/H170 split

In a primitive odd cycle the `q` odd values are pairwise distinct and, except
for the trivial cycle, coprime to six. The exact product identity is

\[
1/\lambda=\prod_i(1+1/(3x_i)).
\]

Applying P72's finite distinct-residue packing argument to this finite set
gives

\[
\log(1/\lambda)\le 1/m+\frac19\log(1+3q/m).
\]

E28 internally verifies that a nontrivial positive cycle minimum must satisfy
`m>=300000`. If `q<=170m`, the right side is at most
`1/300000+log(511)/9`. A 24-term rational atanh-series enclosure stored in
`phase22_theory.json` proves this is strictly below `log 2`. Thus
`lambda>1/2`; together with `lambda<1`,

\[
L=\lceil q\log_2 3\rceil.
\]

Every primitive positive cycle therefore lies in this G170 branch or obeys
`q>170m`. This is a cycle split, not Phase 17's least-counterexample G270/H270
split.

## 4. P135 — canonical coprime profile and slope root

Assume `gcd(L,q)=1`. Rotate the exponent word so

\[
H_j=qE_j-Lj
\]

has its minimum at `H_0=0`. The residues `H_j mod q=-Lj mod q` are all
different, so this rotation is unique. Indexing by the residue `r`—not by the
time `j`—gives

\[
H_j=r+qa_r,\qquad a_r\ge0,\quad a_0=0.
\]

Conversely, `H_j=(-Lj mod q)+q a_(-Lj mod q)` and
`e_j=(H_(j+1)-H_j+L)/q` reconstruct a word precisely when every recovered
exponent is positive. This gives the asserted bijection between valid profiles
and cyclic exponent classes.

For `D>1`, choose `uq+vL=1` and put `gamma=2^u3^v mod D`, interpreting
negative powers as inverses. Since `3^q=2^L mod D`,

\[
\gamma^q=2,\qquad \gamma^L=3\pmod D.
\]

Moreover

\[
qE_j+L(q-1-j)=H_j+L(q-1),
\]

so for `A_a(X)=sum_(r<q)2^{a_r}X^r`,

\[
B(e)=\gamma^{L(q-1)}A_a(\gamma)\pmod D.
\]

The prefactor is a unit, proving `D|B` iff `A_a(gamma)=0 mod D`.

## 5. P136/P137 — area zero and resultant divisibility

At area zero, `A_a=1+X+...+X^(q-1)`. If it vanished at `gamma`, then

\[
(\gamma-1)A_a(\gamma)=\gamma^q-1=1\pmod D,
\]

which is impossible for `D>1`. If `D=1`, the equation
`2^L-3^q=1` is impossible modulo eight for `L>=3`; the only remaining pair is
`(q,L)=(1,2)`, the trivial cycle.

Let `f=X^q-2`. Eisenstein at two makes `f` irreducible over `Q`; since
`deg A_a<q`,

\[
R(a)=\operatorname{Res}(f,A_a)\ne0.
\]

The integer Bezout identity for the resultant, evaluated at `gamma mod D`,
proves that any integral coprime profile has `D|R(a)`, hence `|R(a)|>=D`.
The generator computes this norm as a multiplication-matrix determinant. The
verifier instead computes a `2q-1` Sylvester determinant.

## 6. P137 — radial-energy upper bound

Put `b_r=2^{a_r}-1` and reduce

\[
Q_a=1+(X-1)\sum_rb_rX^r\pmod {X^q-2}.
\]

Its coefficients are

\[
d_0=1+2b_{q-1},\qquad d_r=b_{r-1}-b_r\quad(1\le r<q).
\]

Because `|Res(f,X-1)|=1`, the magnitudes of the resultants of `A_a` and
`Q_a` agree. For `theta=2^(1/q)`, Parseval on the roots `theta*zeta` and
AM--GM give

\[
|R(a)|\le\left(\sum_{r<q}d_r^2\theta^{2r}\right)^{q/2}.
\]

The finite certificate encloses `theta^2=4^(1/q)` above by the least 48-bit
dyadic rational `U` with `U^q>=4`, and accepts an energy exclusion only when

\[
\left(\sum d_r^2U^r\right)^q<D^2.
\]

No floating-point comparison is used.

## 7. P138 — all coprime area-one positive profiles

If area is one, exactly one `a_s` equals one. Positivity of the reconstructed
word forces `1<=s<=L-q-1`, and

\[
Q_a=1-X^s+X^{s+1},\qquad
\mathcal E=1+\theta^{2s}+\theta^{2s+2}.
\]

On the critical line `L=ceil(q log_2 3)`, `q>=13` gives
`E<185/32`. The exact integer checks

\[
4\,8^{13}<9^{13},\qquad
4\,115625^{13}<131072^{13}
\]

combine with EXT05 to give `E^(q/2)<D`, contradicting P137. The finite audit
independently checks all critical `q<=12` cases.

If `L>=ceil(q log_2 3)+1`, put `A=2^(L/q)>3`. Then
`E<1+A^2/2`, and for `q>=4`,

\[
2(1/2+1/A^2)^{q/2}<2(11/18)^{q/2}\le2(11/18)^2<1.
\]

Thus `E^(q/2)<2^(L-1)<D`. The finite audit checks the remaining `q<4`
lengths. Hence every positive coprime area-one profile is excluded. The
critical large-`q` part depends on EXT05; the noncritical proof does not.

## 8. P139 — external Christoffel stability translation

Fernández--Ibáñez Proposition 5.2 states that a local `10 -> 01` exchange
increases their correction by `2^p 3^s`, and Theorem 7.3 makes the
Christoffel conjugacy class the unique maximizer of `C_min`. These statements
are recorded as EXT15 rather than reproved.

In the final exchange into the lower Christoffel representative, let the moved
one be its `k`-th one. Its one-based position is

\[
i_k=\lfloor (k-1)L/q\rfloor+1.
\]

The exchange weight is `2^(i_k-2)3^(q-k)`. Since
`L/q>log_2 3`,

\[
4g\ge2^{i_k}3^{q-k}>3^{q-1}.
\]

Following the paper's monotone swap chain therefore gives, conditionally on
EXT15,

\[
C_{\min}(d)\le C_{\rm chr}-g,
\qquad g>3^{q-1}/4
\]

for every non-Christoffel coprime class. This gap alone is not an all-`q`
cycle exclusion.

## 9. P140 — weaker noncoprime reduction

Let `d=gcd(L,q)>1`, `L=dL_0`, `q=dq_0`, and
`D_0=2^L0-3^q0`. Then `D_0|D`. After any minimum-height rotation for
`H_j=q_0E_j-L_0j`, group equal residues by

\[
A_r=\sum_{H_j=r\bmod q_0}2^{(H_j-r)/q_0}.
\]

The same exponent identity modulo `D_0` gives

\[
D_0\mid\sum_{r<q_0}A_r\gamma^r
\]

for every integral word, and hence the corresponding degree-`q_0-1`
resultant divisibility. This is a necessary condition only. Residues repeat,
the minimum rotation need not be unique, and no coprime-profile bijection is
claimed. When `D_0=1`, the modulus is trivial; a Christoffel power reduces to
the shorter primitive word.

## 10. E34 — exact finite audit

The generator and independent verifier rebuild:

- 16,623 positive exponent compositions and 2,214 cyclic classes for all
  `q<=8`, `q<L<=2q`, `D>0`;
- 797 coprime and 1,417 noncoprime classes in that scope;
- only the trivial cycle and its nonprimitive powers as integral classes;
- all 4,786 valid coprime profiles of area at most two through `q<=22`;
- 63 area-zero, 670 area-one, and 4,053 area-two profiles;
- all 797 exhaustive coprime classes plus 512 deterministic larger-scope
  profiles—1,309 resultants total—by multiplication matrices and independent
  Sylvester determinants;
- the trivial positive cycle, the negative cycles `(-5,-7)` and
  `(-17,-25,-37,-55,-41,-61,-91)`, 30 named word controls, and 22 numeric
  family controls.

All 4,786 bounded profiles satisfy the direct source exclusion
`C_min<300000D`; the energy certificate independently excludes 62 area-zero,
667 area-one, and 3,841 area-two rows. Zero survivors in this finite region is
not an asymptotic theorem. The exact remaining obstruction is arbitrary defect
area beyond the finite scope and the weak general noncoprime condition.

## 11. Literature and novelty boundary

- EXT15 is exactly Fernández--Ibáñez Proposition 5.2 and Theorems 6.4/7.3,
  with their lower Christoffel orientation.
- EXT16 records Knight's “high cycle” result as terminology/overlap evidence.
  A high cycle is an extremal rational-cycle class, not every Collatz cycle;
  no Phase 22 theorem depends on it.
- EXT05 is Rozier--Terracol Lemma B.1 and is used only where stated.
- Eisenstein, resultants, Parseval/AM--GM, and the Terras/Garner affine formula
  are classical context; the used identities are written out here.

No literature-wide novelty claim is made.

## 12. What this result does not prove

- Larger-area coprime profiles are not uniformly excluded.
- P140 does not eliminate general noncoprime profiles.
- Finite zero-survivor counts do not imply eventual zero survivors.
- The positive nontrivial-cycle branch, H89, H112, H72, and Collatz remain
  open.
- `proves_collatz=false`.
