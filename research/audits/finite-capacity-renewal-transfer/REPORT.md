# Phase 38 independent audit: finite capacity and renewal transfer

**Audit date:** 2026-09-04

**Base commit:** `fae3d911e0a32fb977dfa676c3dab4dd224fe6ee`

**Repository status:** `OPEN`
**`proves_collatz=false`**

The supplied Phase 38 note was treated as an untrusted proposal.  Every
accepted inequality below was rederived, the finite rows were regenerated,
and a second implementation reconstructs the evidence without importing the
generator.

## 1. Classification

| ID | Status | Audited result |
|---|---|---|
| P227 | `VERIFIED_THEOREM` | Exact fixed-weight integer image-capacity formula. |
| P228 | `VERIFIED_THEOREM` | Recursive general and odd-source dyadic capacity bounds. |
| E54 | `VERIFIED_FINITE` | Exact rows through `N=500`, reciprocal certificate, finite address and adversarial audits. |
| P229 | `VERIFIED_THEOREM` | Every primitive positive noncritical cycle has minimum below `2^49`. |
| P230 | `CONDITIONAL` | X02 implies that every primitive positive cycle is critical. |
| P231 | `VERIFIED_THEOREM` | Exact renewal threshold-mass conservation. |
| P232 | `VERIFIED_THEOREM` | Convergent source weights and divergent companion weights. |
| P233 | `VERIFIED_THEOREM` | One transfer series has the stated real and 2-adic limits. |
| P234 | `VERIFIED_THEOREM` | Pointwise `30/29` defect growth at every renewal boundary. |
| H72, H133 | `OPEN` | Permanent-safe tails and arbitrary-area critical cycles are not excluded. |

P230 is not an internal theorem: X02 remains external finite evidence.  No
literature-wide novelty claim is made for the elementary capacity induction
or the completion-dependent rational series.

## 2. Map and interval conventions

The full shortcut map is

\[
T(x)=
\begin{cases}
x/2,&x\equiv0\pmod2,\\
(3x+1)/2,&x\equiv1\pmod2.
\end{cases}
\]

For a literal parity word `v=s_0...s_(N-1)` of weight `s`, composition gives

\[
T^N(x)=\frac{3^s x+B_v}{2^N},\qquad
B_v=\sum_{j:s_j=1}2^j3^{\#\{r>j:s_r=1\}}.
\tag{2.1}
\]

An integer interval of length `X` means `[a,a+X)` intersected with the
integers, so its extreme sources are `a` and `a+X-1`.  “Capacity” below is an
upper bound on an actual occupancy; it does not assert that every integer in
the enclosing image interval is attained.

## 3. P227: fixed-weight integer image capacity

P219 gives

\[
B_{\min}=3^s-2^s,qquad
B_{\max}=2^{N-s}(3^s-2^s).
\tag{3.1}
\]

The smallest possible real image numerator over all sources and weight-`s`
words is at least `3^s a+B_min`; the largest is at most
`3^s(a+X-1)+B_max`.  Their real span is therefore

\[
\frac{3^s(X-1)+(2^{N-s}-1)(3^s-2^s)}{2^N}.
\tag{3.2}
\]

An interval of real span `d` contains at most `1+floor(d)` integers.  Hence

\[
\boxed{
Y_{N,s}(X)=1+\left\lfloor
\frac{3^s(X-1)+(2^{N-s}-1)(3^s-2^s)}{2^N}
\right\rfloor.}
\tag{3.3}
\]

This is translation independent.  Each parity word determines one source
residue modulo `2^N`, so a source interval with `X<=2^N` contains at most one
source realizing that word.

## 4. P228: recursive capacities

Set `A_0=1`, and for `N>=1` let

\[
m_{N,s}=\lceil\log_2Y_{N,s}(2^N)\rceil.
\]

For an equal-time collision-free positive set in a translated interval of
length `2^N`, split the set by the weight `s` of its first `N` parity bits.
The time-`N` image of a slice is again an equal-time collision-free positive
set.  By P227 it lies in an integer interval with at most `Y` integers, hence
inside a translated interval of length `2^m`.

If `m<N`, strong induction bounds the slice by `A_m`; its parity-word count
also bounds it by `binomial(N,s)`.  If `m>=N`, only the word-count bound is
used.  Summing gives

\[
\boxed{A_N=\sum_{s=0}^N
\begin{cases}
\min\{\binom Ns,A_{m_{N,s}}\},&m_{N,s}<N,\\
\binom Ns,&m_{N,s}\ge N.
\end{cases}}
\tag{4.1}
\]

If every source is odd, the first bit is one, so there are only
`binomial(N-1,s-1)` words of weight `s`.  The time-`N` images need not be odd,
which is why the recursive term remains `A_m`, not `O_m`.  Thus

\[
\boxed{O_N=\sum_{s=1}^N
\begin{cases}
\min\{\binom{N-1}{s-1},A_{m_{N,s}}\},&m_{N,s}<N,\\
\binom{N-1}{s-1},&m_{N,s}\ge N.
\end{cases}}
\tag{4.2}
\]

This proves the two capacity bounds at every `N`; the computed values are
exact values of these recursive upper bounds, not claims about optimal
occupancy.

## 5. E54: exact reciprocal certificate

Both implementations regenerate all rows `0<=N<=500`.  Selected values are:

| N | A_N | O_N |
|---:|---:|---:|
| 0 | 1 | 1 |
| 10 | 769 | 507 |
| 20 | 454346 | 325836 |
| 30 | 267261223 | 196144373 |
| 40 | 185532462462 | 130669342714 |
| 48 | 31389510367718 | 24049149806528 |
| 49 | 58609921347648 | 42931358264194 |
| 50 | 114046720881162 | 86887448694020 |

The full rows and exact rational sum are in the capacity artifact.  Direct
integer cross multiplication verifies

\[
\sum_{N=49}^{500}\frac{O_N}{2^N}
+1440\left(\frac{44}{45}\right)^{501}<\frac{2079}{1000}.
\tag{5.1}
\]

P220 gives `O_N<32*2^(29N/30)`.  Since

\[
2\,44^{30}>45^{30},
\]

we have `2^(-1/30)<44/45`, and the geometric tail from `N=501` is strictly
less than the second term in (5.1).  The positive-term expansion

\[
\log2=2\sum_{k\ge0}\frac{3^{-(2k+1)}}{2k+1}
\]

has its first three terms equal to

\[
\frac23+\frac2{81}+\frac2{1215}=\frac{842}{1215}.
\]

Finally `2079*405=841995<842000=842*1000`, so

\[
\frac{2079}{1000}<\frac{842}{405}<3\log2.
\]

Combining these exact comparisons proves

\[
\boxed{\sum_{N=49}^{\infty}\frac{O_N}{2^N}<3\log2.}
\tag{5.2}
\]

The supplied note contained the typographical string
`2079/1000 < < 842/405`; only the single strict comparison above is used.

### Private digest boundary

The note supplied a private digest but did not specify its byte encoding and
explicitly excluded it from acceptance evidence.  The repository defines the
row encoding in the artifact and obtains
`7cbeb6b18addf9ff2ed16b472f497d634bdd1a78cdf7a544e9715a5a755ce83f`,
which differs from the private target.  The verifier checks every row and the
inequality directly.  No values were changed to chase an opaque digest.

## 6. P229 and P230: the cycle consequence

Let a primitive positive cycle have odd states `O` and minimum `m>=2^49`.
The minimum is odd, since an even minimum would map immediately to the
smaller positive value `m/2`.
At every common time shift, distinct cycle states remain distinct, so the odd
states are an equal-time collision-free set.  The shell
`[2^N,2^(N+1))` has length `2^N` and contains at most `O_N` odd states.
Therefore

\[
\sum_{x\in\mathcal O}\frac1x
\le\sum_{N\ge49}\frac{O_N}{2^N}<3\log2.
\tag{6.1}
\]

For `lambda=3^q/2^L`, the exact cycle product is

\[
\frac1\lambda=\prod_{x\in\mathcal O}\left(1+\frac1{3x}\right).
\]

Since `log(1+u)<u` for `u>0`,

\[
\log(1/\lambda)<\frac13\sum_{x\in\mathcal O}\frac1x<\log2,
\]

so `lambda>1/2`.  A noncritical positive cycle has
`L>=ceil(q log_2 3)+1` and hence `lambda<1/2`.  Consequently

\[
\boxed{m<2^{49}}
\]

for every primitive positive noncritical cycle.

X02 says every positive start below `V=2075*2^60` reaches 1.  Conditional on
that external evidence, a nontrivial cycle minimum is at least `V>2^49`, so
P229 excludes its noncritical case.  The trivial cycle is itself critical.
Thus, and only conditionally on X02, every primitive positive cycle satisfies

\[
L=\lceil q\log_2 3\rceil.
\]

## 7. P231: exact renewal threshold mass

At P77 renewal boundary `i`, define

\[
A_i=S_i+1,\qquad H_i=h_i-1.
\]

For the next forward block `w_i`, put

\[
c_i=\frac{3^{Q_i}}{2^{L_i}},\qquad
R_i=\frac{B_i+2^{L_i}}{3^{Q_i}},\qquad r_i=R_i-1.
\]

The positive and companion affine maps give exactly

\[
A_{i+1}=c_i(A_i+r_i),\qquad
H_{i+1}=c_i(H_i-r_i).
\tag{7.1}
\]

P79 gives `r_i=0` for the one-block and `r_i>=4/9` for every nontrivial
block.  Companion legality is `0<=r_i<H_i`.  Addition yields

\[
A_{i+1}+H_{i+1}=c_i(A_i+H_i).
\tag{7.2}
\]

For `zeta_i=H_i/(A_i+H_i)`, direct subtraction using (7.1)--(7.2) gives

\[
\zeta_i-\zeta_{i+1}=\frac{r_i}{A_i+H_i}.
\tag{7.3}
\]

P224 supplies `H_i/A_i->0`, hence `zeta_i->0`.  Telescoping and monotone
convergence give the exact tail identity

\[
\boxed{\frac{h_i-1}{S_i+h_i}
=\sum_{k=i}^{\infty}\frac{R_k-1}{S_k+h_k}.}
\tag{7.4}
\]

## 8. P232: the two weighted regimes

The renewal states are strictly increasing because `c_i>1`, `A_i>0`, and
`r_i>=0`.  The first `i+1` states form a subset of the nonperiodic orbit and
lie in an interval of length `A_i`.  P220 therefore gives

\[
i+1<32A_i^{29/30},\qquad
A_i>\left(\frac{i+1}{32}\right)^{30/29}.
\tag{8.1}
\]

Since `30/29>1`, comparison with a p-series proves

\[
\sum_i\frac1{A_i}<\infty.
\tag{8.2}
\]

Equation (7.3) says that `sum r_i/(A_i+H_i)` is finite.  Eventually
`H_i<=A_i` by P224, so multiplication by `(A_i+H_i)/A_i<=2` gives

\[
\sum_i\frac{r_i}{A_i}<\infty,
\qquad
\boxed{\sum_i\frac{R_i}{S_i+1}<\infty.}
\tag{8.3}
\]

For the companion scale put `t_i=r_i/H_i` in `[0,1)`.  If
`C_i=prod_(j<i)c_j`, iteration of (7.1) gives

\[
\frac{H_i}{H_0C_i}=\prod_{j<i}(1-t_j).
\tag{8.4}
\]

Equation (7.2) also gives

\[
C_i=\frac{A_i+H_i}{A_0+H_0},
\]

so the left side of (8.4) is a fixed positive multiple of `zeta_i` and tends
to zero.  Hence `sum -log(1-t_i)=infinity`.  If `t_i>=1/2` infinitely often,
then `sum t_i` diverges.  Otherwise, eventually
`-log(1-t_i)<=2t_i`, with the same conclusion.  Thus

\[
\boxed{\sum_i\frac{R_i-1}{h_i-1}=\infty.}
\tag{8.5}
\]

## 9. P233: real and 2-adic transfer

Dividing (7.1) by `C_(i+1)=C_i c_i` gives

\[
\frac{A_{i+1}}{C_{i+1}}=\frac{A_i}{C_i}+\frac{r_i}{C_i},
\qquad
\frac{H_{i+1}}{C_{i+1}}=\frac{H_i}{C_i}-\frac{r_i}{C_i}.
\tag{9.1}
\]

Because `(A_i+H_i)/C_i=A_0+H_0` and `zeta_i->0`,
`H_i/C_i->0` over the reals.  Therefore

\[
\boxed{\sum_{i\ge0}\frac{r_i}{C_i}=H_0\quad(\mathbb R)},
\qquad
\boxed{\frac{A_i}{C_i}\longrightarrow A_0+H_0\quad(\mathbb R)}.
\tag{9.2}
\]

Write cumulative block length and weight as `mathcal L_i,mathcal Q_i`.  Then

\[
\frac{A_i}{C_i}=\frac{2^{\mathcal L_i}A_i}{3^{\mathcal Q_i}}.
\]

Here `A_i` is an integer, the denominator is odd, and
`mathcal L_i->infinity`.  This expression tends to zero in `Q_2`; the first
identity in (9.1) then gives

\[
\boxed{\sum_{i\ge0}\frac{r_i}{C_i}=-A_0\quad(\mathbb Q_2)}.
\tag{9.3}
\]

More precisely, if a nontrivial forward block begins with a run of `ell_i`
ones, P79 gives

\[
r_i=\frac{4C_{w_i}}{3^{Q_i}},\qquad v_2(C_{w_i})=\ell_i-2,
\]

and hence

\[
v_2(r_i/C_i)=\mathcal L_i+\ell_i.
\tag{9.4}
\]

All transfer terms have odd reduced denominator.  Equations (9.2) and (9.3)
are limits in different completions and do not imply equality of the two
limits.

## 10. P234: pointwise renewal-boundary defect

At an odd renewal boundary, P72's normalization has

\[
S_i=2^{a_{n_i}+\vartheta_{n_i}}Y_{n_i},qquad
0\le\vartheta_{n_i}<1,\qquad Y_{n_i}\le Y_\infty.
\]

Thus `S_i<2^(a_(n_i)+1)Y_infinity`, while `A_i=S_i+1<=2S_i`.
Combining this with (8.1) yields

\[
\boxed{a_{n_i}\ge\frac{30}{29}\log_2(i+1)-O_{S_0}(1)}
\tag{10.1}
\]

at every renewal boundary.  Replacing the explicit P220 exponent by any
`rho>rho_*` gives `a_(n_i)>=rho^(-1)log_2(i)-O(1)`.  This is not an eventual
bound at every odd iterate.

## 11. Independent finite audit

The generator and verifier independently reconstruct:

- 501 recursive `A_N,O_N` rows through `N=500`;
- the exact finite reciprocal sum, geometric tail, and logarithm lower bound;
- 12,672 sources in 148 translated-interval cases and 608 fixed-weight image
  groups through `N<=10`, including translations above `2^120`;
- 154 first-upcrossing codewords through length 14;
- 423 finite renewal addresses, 817 exact block transitions, and 717 nonzero
  transfer-valuation checks;
- all mandatory adversarial families, including
  `W=111011100`, map `(729x+817)/512`, fixed point `-817/217`;
- the trivial cycle and the NG22 real/2-adic completion warning.

For each finite address, the source is reconstructed from its unique residue
modulo the total `2`-power.  A rational companion is chosen above the exact
finite threshold tail; the verifier checks legality, the positive and
companion transitions, zeta telescoping, transfer telescoping, odd reduced
denominators, and (9.4).  These bounded checks audit conventions and are not
the proof of the infinite statements.

## 12. Remaining obstruction

Phase 38 makes P226's noncritical cutoff practical and rewrites the H72
survivor as an exact transfer problem.  It does not supply the missing
rootwise carry or ordinary-source ordering theorem.  A productive next target
would have to combine (8.3)/(9.4) with P79 valuations and P86/P91 ancestry, or
derive a genuine height obstruction for the same rational digits.

## What this result does not prove

The finite capacity bound is not P80 address anti-concentration.  The two
weighted regimes and two completion limits are compatible with an infinite
formal transfer.  P230 still depends on X02, and P229 does not address
critical arbitrary-area cycles.  H72, H133, and the Collatz conjecture remain
open.  `proves_collatz=false`.
