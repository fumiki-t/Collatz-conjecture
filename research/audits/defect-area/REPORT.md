# Phase 23 audit — defect area, finite-word boundary, and cycle separation

Status: accepted repository derivations and bounded computations; P142, P143,
and P146 retain their stated hypotheses; H89, H133, and Collatz remain `OPEN`;
`proves_collatz=false`.

## 1. Convention and the supplied boundary error

For a coefficient-safe first-crossing word with `q` odd steps, put

\[
K_q=\lceil q\log_2 3\rceil,
\qquad f_j=\lfloor j\log_2 3\rfloor,
\qquad 0\le j<q.
\]

The finite base word `c_q` has ones at `f_j` and length `K_q`.  Its last
symbol is zero, while the corresponding infinite mechanical word has its next
one at

\[
f_q=K_q-1.
\]

Thus `c_q` is not literally a factor of that infinite word.  The proposed
bound `|L_n(c_q)|<=n+1` is false.  The smallest counterexample is

```text
q=4, c_q=1101100, n=2, A=0,
L_2(c_q)={00,01,10,11}.
```

Hence `4>3`.  This is NG32.  Replacing the terminal mechanical one by zero
changes only the terminal length-`n` window, so the exact repaired base bound
is

\[
|\mathcal L_n(c_q)|\le n+2.
\tag{1.1}
\]

No external Sturmian theorem is needed: for an infinite mechanical word, a
length-`n` factor is determined by the position of one fractional part among
at most `n+1` cut points.  Restriction to the prefix cannot add factors, and
the final substitution adds at most one.

## 2. P141 — exact critical defect area

Let the odd positions of a safe first-crossing word `w` be

\[
0=d_0<\cdots<d_{q-1}.
\]

Safety immediately before each odd step gives `d_j<=f_j`.  Set

\[
a_j=f_j-d_j,\qquad A(w)=\sum_j a_j.
\]

For prefix-one counts `h_w(t),h_c(t)`, the contribution of odd step `j` to
`h_w(t)-h_c(t)` is one exactly when `d_j<t<=f_j`.  Therefore

\[
A(w)=\sum_{t=0}^{K_q}(h_w(t)-h_c(t)).
\tag{2.1}
\]

It follows that the number of noncontact prefix times is at most `A(w)`.
Moving the `j`th one from `f_j` to `d_j` gives a literal chain of exactly
`A(w)` adjacent swaps `01->10`; the prefix-count formula also proves
minimality of that number.

One internal adjacent swap can change factors only at starts whose length-`n`
window contains one of the two swapped positions, at most `n+1` starts.
Combining this with (1.1) gives the corrected theorem

\[
\boxed{|\mathcal L_n(w)|\le(A(w)+1)(n+1)+1.}
\tag{2.2}
\]

## 3. P142 — contact height and repaired repetition inequality

Write a prefix map as

\[
x_t={3^{h(t)}\over2^t}(N+\beta_t),
\qquad \beta_t=B_t/3^{h(t)}.
\]

The safe correction estimate gives `0<=beta_t<=h(t)/3<=q/3`.  At a contact
time, the mechanical coefficient is in `[1,3)`, hence

\[
x_t<3N+q.
\tag{3.1}
\]

Under P54, `N<=H_q=B_q^max/D_q`, so every contact state is below
`U_q=3H_q+q`.  Define the integer width

\[
n_q=\min\{n:2^nD_q\ge3B_q^{\max}+qD_q\}.
\tag{3.2}
\]

Assume the states in the critical segment are pairwise distinct.  Among the
`K_q-n_q+1` legal starts there are at least that number minus `A(w)` contacts.
Two equal length-`n_q` factors at contact starts would, by P125, make their
positive state difference a nonzero multiple of `2^n_q`; (3.1) makes its
absolute value strictly smaller.  Therefore those factors are distinct.
Using (2.2) gives

\[
\boxed{K_q\le A(w)(n_q+2)+2n_q+1,}
\tag{3.3}
\]

and

\[
A(w)\ge
\max\left(0,\left\lceil{K_q-2n_q-1\over n_q+2}\right\rceil\right).
\tag{3.4}
\]

P142 is `CONDITIONAL` because its H89 use retains P54 and pairwise state
distinctness.  It is not applied to a periodic branch.

## 4. P143 — conditional asymptotics and Phase 7 contacts

If effective constants satisfy `H_q<=Cq^mu` for all sufficiently large `q`,
then `n_q<=mu log_2 q+O(1)`.  Equation (3.3) yields

\[
A(w)\ge\left({\log_2 3\over\mu}+o(1)\right){q\over\log_2q}.
\tag{4.1}
\]

Similarly, if a critical word has `C` zero defects, at most `n_q` associated
contact starts lie beyond the legal factor-start range.  The repaired bound is

\[
A(w)\ge
\left\lceil{C-2n_q-2\over n_q+1}\right\rceil.
\tag{4.2}
\]

The existing Phase 7 artifacts certify a conditional contact count, but do
not contain a convenient exact upper certificate for the enormous `n_q0` in
the form required by (3.2).  This audit does not substitute floating-point
logs or accept the proposal's unverified Wu--Wang conversion.  The numerical
`q0` consequence therefore remains conditional.

## 5. P144 — coprime cycle edit area

For the Phase 22 coprime residue profile `a_r`, the time-`j` height is

\[
H_j=r_j+qa_{r_j},\qquad r_j=(-Lj\bmod q).
\]

The profile-zero word has the same residues and odd boundaries `E_j^0`.
Thus

\[
E_j-E_j^0=a_{r_j}.
\]

The literal expanded parity word is obtained from its Christoffel baseline by
exactly `A=sum_r a_r` adjacent swaps `10->01`.  In time order the profile can
decrease only by one at a wrap transition.  A path reaching height `h` and
returning to zero must therefore contain levels `h,h-1,...,1`, so

\[
A\ge h(h+1)/2.
\tag{5.1}
\]

The cyclic Christoffel baseline has at most `n+1` cyclic length-`n` factors.
The same swap-window argument, now without the finite terminal mutation,
gives

\[
p_{\rm cyc}(n)\le(A+1)(n+1).
\tag{5.2}
\]

## 6. P145 and P146 — positive cycle separation

For a primitive positive integer cycle, let `m` be its least odd value,
`lambda=3^q/2^L`, and `h=max a_r`.  For any cyclic segment, the height range
and `lambda<1` give coefficient below `2^(h+1)`.  Its correction product is at
most the full product `1/lambda`.  Hence the largest odd state, and then the
largest shortcut state, satisfy

\[
M_{\rm odd}<2^{h+1}m/\lambda,
\qquad M<2^{h+2}m/\lambda.
\tag{6.1}
\]

With

\[
n_{\rm cyc}=\left\lceil\log_2(2^{h+2}m/\lambda)\right\rceil,
\]

all cyclic length-`n_cyc` factors must be distinct by P125 and ordinary
positive height separation.  Equation (5.2) yields

\[
L\le(A+1)(n_{\rm cyc}+1).
\tag{6.2}
\]

This theorem is deliberately not applied to rational noninteger shadows or
negative cycles.  If one additionally assumes an effective
`m<=Cq^mu` for all large coprime positive cycles, the exact product bound gives
`n_cyc<=h+O(log q)`.  Equations (5.1) and (6.2) then force
`A=Omega(q^(2/3))`.  P146 remains conditional because no such effective
polynomial minimum theorem is accepted here.

## 7. E35 — exact finite audit

The generator and independent verifier rebuild:

- all 502,523 critical first-crossing words through `q<=17`;
- 31 corrected area-bound rejections;
- 82,227 direct factor-width checks and the P132 comparison through `q<=12`;
- zero Phase-23-only rejections through `q<=12` (all are already caught by
  P132), while the union has 3,579 rejected words;
- all 4,786 valid coprime profiles of area at most two through `q<=22`;
- 156,178 literal cyclic factor-width checks;
- all 2,214 cyclic classes through `q<=8`, with only the trivial cycle and its
  powers integral; the only primitive positive coprime row is the trivial
  cycle.

The verifier reconstructs the recursion, literal swaps, substrings, profiles,
and cycles without importing the generator.  NG21--NG31, source 167, all
mandatory families, the all-contact word, and both negative-cycle controls are
retained as regressions.

## 8. H141 and interpretation

Area may be concentrated in a few deep excursions.  Since `2^-a` is decreasing
and convex, an area lower bound alone does not uniformly suppress the affine
correction.  H141 asks for an exact admissible-path/carry/source theorem that
turns area and contact information into either H89 rejection or an all-area
H133 obstruction.  A finite extension without such a theorem is not the next
step.

## What this result does not prove

- The exact Phase 7 `q0` candidate is not excluded.
- P142 does not cover a periodic branch.
- P144--P146 do not exclude arbitrary-area or noncoprime positive cycles.
- H89, H133, H112, H72, and the Collatz conjecture remain open.
- `proves_collatz=false`.
