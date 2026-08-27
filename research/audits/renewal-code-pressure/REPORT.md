# Phase 13 independent audit: renewal code, pressure, and canonical residues

**Audit date:** 2026-08-26

**Base:** `origin/main` at `70f9cc8d895cf28143e8c6e094ffd076c60db959`

**Repository status:** `OPEN`
**`proves_collatz=false`**

The two preceding scratch audits were treated as untrusted conjecture and
finite sanity data.  Phase 13 rederived the mathematics and rebuilt the
generator and verifier separately.  The verifier does not import
`src.phase13_search`.

## 1. Accepted classification

| ID | Status | Audited result |
|---|---|---|
| P77 | `VERIFIED_THEOREM` | Unique strict-suffix renewal decomposition and the reversed first-upcrossing prefix code. |
| P78 | `VERIFIED_THEOREM` | Weighted first-passage identity and strict bounds for `kappa`, `sigma`, `tau`, and `nu`. |
| P79 | `VERIFIED_THEOREM` | Universal companion threshold, positive-source bridge, and normalized correction/valuation rules. |
| P80 | `CONDITIONAL` | Either quantified canonical-residue anti-concentration premise would exclude the permanent-safe positive branch. The premises are not proved. |
| E22 | `VERIFIED_FINITE` | Length-512 DP, 4096-step critical model, and all `Q<=12`, 1–4 block addresses through height 2048. |
| NG23 | `REFUTED` | A coefficient-one raw Haar-volume estimate controls canonical positive representatives. |
| NG22 | `REFUTED` | Existing status retained; the square-root model is additional formal/2-adic evidence, not a new claim. |
| H72 | `OPEN` | The required ordinary-positive anti-concentration theorem remains missing. |

No literature-wide novelty is claimed for the weighted first-passage/Kraft
identity; it is a standard-looking stopping/coding consequence.

## 2. Renewal decomposition and orientation

For full shortcut bits `s_k in {0,1}`, put

\[
q(n)=\sum_{k<n}s_k,
\qquad
\Delta_n=q(n)\log3-n\log2.
\]

Assume

\[
\Delta_n>0\quad(n>0),
\qquad
\Delta_n\longrightarrow+\infty.
\tag{2.1}
\]

Set `t_0=0` and

\[
t_{i+1}=\operatorname*{argmin}_{n>t_i}\Delta_n.
\tag{2.2}
\]

Existence follows from divergence to infinity.  Uniqueness follows because
`Delta_m=Delta_n` would give `3^a=2^b`; unique factorization forces `m=n`.
Define the forward block

\[
w_i=s_{t_i}\cdots s_{t_{i+1}-1},
\qquad u_i=\operatorname{rev}(w_i).
\]

For a proper prefix of `u_i` of length `ell`, the corresponding suffix of
`w_i` has discrepancy

\[
\Delta_{t_{i+1}}-\Delta_{t_{i+1}-\ell}<0.
\]

The whole block has positive discrepancy.  Hence `u_i` belongs to

\[
\mathcal U=\{u:\ 3^{q(p)}<2^{|p|}\text{ for every nonempty proper prefix }p,
\ 3^{q(u)}>2^{|u|}\}.
\tag{2.3}
\]

If one member of `U` were a proper prefix of another, the latter would have
already crossed, so `U` is prefix-free.  The last bit of every `u` is one.
For a nontrivial word its first bit is zero; therefore the forward block
starts in one and ends in zero.  The unique length-one exception is `w=u=1`.

The infinite forward decomposition is unique because of (2.2).  It must not
be justified by falsely declaring `reverse(U)` prefix-free.

For a forward word `w=s_0...s_(L-1)`, exact composition gives

\[
F_w(x)=\frac{3^qx+B_w}{2^L},
\]

where scanning left-to-right leaves `B` unchanged on zero and replaces
`B` by `3B+2^j` on a one at position `j`.

## 3. Martingale and pressure identities

For `u in U`, define

\[
L=|u|,\qquad q=\#1(u),\qquad c(u)=3^q/2^L.
\]

Before the last bit the coefficient is at most one; the last bit multiplies
it by `3/2`.  Therefore

\[
1<c(u)\le3/2.
\tag{3.1}
\]

Under fair independent bits,

\[
M_n=3^{q(n)}/2^n
\]

is a martingale.  Let `T` be the first strict crossing of one.  Then
`M_(T wedge n)<=3/2`, so bounded-time optional stopping and bounded
convergence apply.  On `T=infinity`, the mean logarithmic increment is
`(1/2)log(3/4)<0`; the strong law gives `M_n->0`.  Thus

\[
\boxed{\sum_{u\in\mathcal U}2^{-L(u)}c(u)=1.}
\tag{3.2}
\]

Define

\[
\kappa=\sum2^{-L},\quad
\sigma=\sum3^{-q},\quad
\tau=\sum2^{-L}3^{-q},\quad
\nu=\sum4^{-L}.
\]

The event starting with one stops immediately at `u=1`; it has probability
`1/2` and weighted mass `3/4`.  Every other stopping word starts with zero,
has `c>1`, and has total weighted mass `1/4`.  Hence

\[
\kappa<\frac12+\frac14=\frac34.
\tag{3.3}
\]

Also `3^-q=2^-L/c`, so the nontrivial part of `sigma` is smaller than the
nontrivial part of `kappa`.  Every nontrivial word has length at least three.
Consequently

\[
\boxed{
\kappa<\frac34,\qquad
\sigma<\frac7{12},\qquad
\tau<\frac{19}{96},\qquad
\nu<\frac9{32}.}
\tag{3.4}
\]

The last two estimates use, respectively,
`tau_other<=sigma_other/8<1/32` and
`nu_other<=kappa_other/8<1/32`.

For `i` codewords, Tonelli's theorem for nonnegative series gives

\[
\sum_{\mathcal U^i}2^{-L}=\kappa^i,
\quad
\sum_{\mathcal U^i}3^{-Q}=\sigma^i,
\quad
\sum_{\mathcal U^i}2^{-L}3^{-Q}=\tau^i.
\tag{3.5}
\]

## 4. Threshold and positive-source bridge

The affine constant has the expansion

\[
B_w=\sum_{j:s_j=1}2^j3^{\#\{r>j:s_r=1\}}.
\tag{4.1}
\]

At fixed `(L,q)`, exchanging adjacent `01` to `10` strictly decreases `B`.
The unique minimizer is `1^q0^(L-q)`, for which

\[
B_{\min}=\sum_{j=0}^{q-1}2^j3^{q-1-j}=3^q-2^q.
\tag{4.2}
\]

Put

\[
R(w)=\frac{B_w+2^L}{3^q}.
\]

The last bit of `u=reverse(w)` is one, so its length `L-1` prefix has
`q-1` ones and satisfies `3^(q-1)<=2^(L-1)`, while the whole word satisfies
`3^q>2^L`.

- `q=1` forces `w=1`.
- `q=2` forces `(L,w)=(3,110)` and `R=13/9`.
- `q=3` would require both `L>=5` and `L<=4`, so it is impossible.
- For `q>=4`, (4.2) and the two power inequalities give `R>13/9`.

Therefore

\[
\boxed{w\ne1\Longrightarrow R(w)\ge13/9,}
\]

with equality exactly for `w=110`.

For a positive boundary source `S` and companion `h>1`,

\[
S'=\frac{3^qS+B_w}{2^L},
\qquad
h'=\frac{3^qh-B_w}{2^L}.
\]

Thus `h'>1` is equivalent to `h>R(w)`.  If `h<=13/9`, the next block must be
`1`.  Across `r` repeated one-blocks,

\[
S_r+1=(3/2)^r(S+1),
\quad 2^r\mid S+1.
\]

Because `S` is a positive ordinary integer, `2^r<=S+1`.  This is the exact
Archimedean bridge absent for a general 2-adic source.  With
`alpha=log_2(3/2)`, first threshold exit gives

\[
\boxed{h-1>\frac49(S+1)^{-\alpha}.}
\tag{4.3}
\]

## 5. Normalized correction and valuation transfer

At a renewal boundary `S congruent 3 mod 4`, set

\[
U=(S+1)/4,\quad V=(h-1)/4,
\quad C_w=(B_w+2^L-3^q)/4.
\]

Then

\[
2^LU'=3^qU+C_w,
\qquad
2^LV'=3^qV-C_w.
\tag{5.1}
\]

For `w=1`, `C_w=0`.  A nontrivial renewal word begins with at least two ones
and ends in zero.  Formula (4.1) modulo four proves that `C_w` is integral.
From (4.2),

\[
C_w\ge(2^L-2^q)/4\ge2^{L-3},
\tag{5.2}
\]

with equality only at `w=110`.

Let `r` be the initial one-run of a nontrivial `w`.  The first zero occurs at
position `r`.  Separating the initial-run contribution in (4.1) shows

\[
B_w+2^L-3^q=2^r\cdot\text{odd},
\]

and therefore

\[
\boxed{v_2(C_w)=r-2.}
\tag{5.3}
\]

If both `U` and `U'` in (5.1) are integers, divisibility by `2^L` forces
`v_2(U)=v_2(C_w)=r-2`.  For the one-block, boundary integrality is equivalent
to `U` even, and then `U'=3U/2`.

For

\[
z=(h-1)/(S+1),
\]

direct substitution gives

\[
z'=\frac{h-R}{S+R},
\quad
z-z'=\frac{(R-1)(S+h)}{(S+1)(S+R)}.
\tag{5.4}
\]

Thus `z` strictly decreases on every nontrivial block and is unchanged on a
one-block.  Equations (5.1)–(5.4) are exact orbit-specific structure, but the
finite search found no recursive closure or uniform anti-concentration bound.

## 6. Square-root critical countermodel

Let

\[
f_j=\lfloor j\log_2 3\rfloor,
\quad b_j=f_{j+1}-f_j,
\]

and increment `A_j` exactly when `b_j=2` and
`A_j<floor(sqrt(j+1))`.  Put

\[
e_j=b_j-(A_{j+1}-A_j),
\quad E_j=\sum_{r<j}e_r.
\]

Because `1<log_2 3<2`, `b_j in {1,2}`.  There are no consecutive `b_j=1`
because `2log_2 3>3`.  An induction across square boundaries gives

\[
\lfloor\sqrt j\rfloor-1\le A_j\le\lfloor\sqrt j\rfloor.
\tag{6.1}
\]

The only delicate induction case is `j+1=m^2` with maximal lag.  Then the
preceding `b` must have been one; nonconsecutivity forces the current `b` to
be two and the recurrence increments `A`.

Telescoping gives

\[
E_j=f_j-A_j,
\]

so `e_j in {1,2}`, every full shortcut prefix is coefficient-safe, and
`E_j/j->log_2 3`.  The square-shell count from (6.1) gives

\[
\sum_j2^{-A_j}<\infty.
\]

Since `E_j->infinity`, the inverse series

\[
\xi_0=-\sum_{j\ge0}2^{E_j}/3^{j+1}
\]

converges in `Z_2` and gives a coherent odd 2-adic source with the prescribed
exponents.  The real series

\[
h_j=\sum_{n\ge0}\frac{2^{E_{j+n}-E_j}}{3^{n+1}}
\]

satisfies the same companion recurrence.  Positivity plus the recurrence
gives `h_j>=1`; equality would force every later `e_j=1`, while the number of
unconverted `b_j=2` is linear.  Hence `h_j>1`.  Square-shell summation gives
`h_j=O(sqrt(j))`, so `sum 1/h_j` diverges.

This model supplies additional evidence for NG22.  It does not have a known
positive ordinary source and does not receive a new NG identifier.

## 7. Canonical residues and the open pressure implication

For an address `a=(u_1,...,u_i)`, let the forward word be the concatenation
of `reverse(u_j)`.  If a block `b` follows address `a`, exact composition is

\[
B(ab)=3^{Q(b)}B(a)+2^{L(a)}B(b).
\tag{7.1}
\]

The canonical residues are

\[
r_2=[-B3^{-Q}]_{2^L},
\qquad
r_3=[B2^{-L}]_{3^Q}.
\tag{7.2}
\]

The verifier reconstructs the literal parity word from the least positive
source representative.  The correct lifted identity is

\[
3^Qr_2+B=2^L(r_3+k3^Q),
\]

not necessarily the same equation with `k=0`.

Let `N_i^(3)(H)` count addresses in `U^i`, with multiplicity, whose least
positive endpoint representative is at most `H`.  Let `N_i^(2,3)(H)` count
addresses whose least positive source and endpoint representatives are both
at most `H`.

For a permanent-safe positive orbit and its companion,

\[
S_i+h_i=(S_0+h_0)\prod_{j<i}c(u_j)
\le(S_0+h_0)(3/2)^i.
\tag{7.3}
\]

The exact conditional premises registered in P80 are:

> For every `epsilon>0`, for all sufficiently large `i` and every ordinary
> `H>=1`, either
> `N_i^(3)(H)<=exp(epsilon i) H sigma^i`, or
> `N_i^(2,3)(H)<=exp(epsilon i) H^2 tau^i`.

At `H` comparable with the right side of (7.3), the actual address contributes
at least one.  But the upper bounds decay after choosing `epsilon` small,
because

\[
(3/2)\sigma<7/8,
\qquad
(9/4)\tau<57/128.
\]

Therefore either premise excludes the permanent-safe positive branch.  This
is a conditional implication only.  Phase 13 does not prove either premise.

The finite duplicate audit in this report was performed separately at each
fixed block count. It did not assert injectivity after different block counts
are combined. Phase 14 records the resulting cross-layer collisions and the
first same-layer collision at `Q=13`; this clarification changes no P77--P80
claim status.

## 8. Raw Haar failure

For `u=1`,

\[
L=Q=B=1,
\quad r_2^+=1,
\quad r_3^+=2.
\]

At `H=2`, the canonical endpoint and two-sided counts both equal one, but

\[
H3^{-Q}=2/3,
\qquad
H^22^{-L}3^{-Q}=2/3.
\]

Thus the coefficient-one raw volume mechanism is refuted.  The ordinary
lattice estimate for one residue class contains `+1`; summed over all
addresses, these errors are not controlled by `sigma^i` or `tau^i`.
Furthermore, 3-adic cylinders overlap exactly when their residues agree
modulo `3^min(Q,Q')`.  Summed Haar mass is not a theorem about one designated
positive integer.

This counterexample does not refute an estimate with an unspecified uniform
constant.  The existence of such a bound is still open.

## 9. Exact finite audit

The independent verifier reconstructed:

- DP through word length 512:
  `kappa_512=0.713684603460011531809273...`,
  weighted partial mass `0.999999999987953731850549...`, and
  `sigma_512=0.517160543190006388966665...`;
- 3331 first-upcrossing words with `Q<=12`;
- every address with total `Q<=12` and 1–4 blocks;
- every ordinary height `1<=H<=2048` for the lattice audit;
- 2144 mandatory adversarial convention instances;
- 4096 odd exponents of the square-root countermodel.

The 4096-step model has `A=64`, `E=6428`, and its residue SHA-256 is
`dcd32b0409c2d063a639037299c93504d043f0cd4df81e9a3bbba806262acddd`.
The last residue change occurs at step 4095, excluding positive sources below
`2^6425` for that finite prefix only.

The finite address counts are 3331, 1863, 2053, and 1860 for block counts
1–4.  Compatible endpoint-cylinder pairs occur in every layer; exact
duplicate `(Q,r_3)` cylinders happen to be absent in this finite range.  That
absence and all finite ratios remain `VERIFIED_FINITE`, never a theorem.

## 10. What this result does not prove

- It does not prove endpoint or two-sided anti-concentration.
- It does not prove that no positive ordinary source realizes a permanent-safe
  word.
- It does not prove H72.
- It does not eliminate nontrivial cycles.
- It does not prove or disprove the Collatz conjecture.

`proves_collatz=false`.
