# Phase 20 audit — parity-complexity barriers

## 1. Result and scope

This audit treats `phase20_parity_complexity_note.md` as an untrusted research
proposal. The supplied note has SHA-256
`0fcd6d82b1fe5ad33e2125fbb6500ee7dccc6f14a6f15cd774bf42e402c77eb9`.
Its main implications survive, with these dependency and attribution repairs:

1. López--Stoll gives a **lower limiting** parity-one density, not existence
   of a natural density. The arXiv TeX theorem and proof were inspected, not
   only the abstract.
2. General morphic words need not have natural letter frequencies. The
   algebraicity result is used only when the frequency exists; Saari's pure
   binary theorem is recorded separately.
3. The fixed-packet P109 itinerary is excluded internally by P114, not P112.
4. Finite factor complexity may be below `n+1` because the stored word is a
   finite prefix. Morse--Hedlund is applied only to the infinite word.

P117, P118, P120, and P122 are `VERIFIED_THEOREM`. P119, P121, P123, and
P124 are `CONDITIONAL` on their named external inputs. E32 is
`VERIFIED_FINITE`; H112 and H72 remain `OPEN`. The Collatz conjecture remains
open and `proves_collatz=false`.

All finite acceptance decisions use integers or `Fraction`. Logarithms occur
only in symbolic proofs and definitions.

## 2. Convention

The full shortcut map is

\[
T(x)=\begin{cases}x/2,&x\equiv0\pmod2,\\(3x+1)/2,&x\equiv1\pmod2.\end{cases}
\]

Let `v_l` be the parity of the input to step `l`, and put

\[
h(\ell)=\sum_{j<\ell}v_j,
\qquad \rho_c=\frac{\log2}{\log3},
\qquad C_\ell=\frac{3^{h(\ell)}}{2^\ell}.
\]

At the odd accelerated time `E_j`, write

\[
c_j=C_{E_j},\qquad D_j=\log c_j.
\]

For a positive nonperiodic permanent-safe tail from minimum `S`, P72 gives

\[
\beta_q=\sum_{j<q}\frac1{3c_j}
\le S\left[e^{1/S}\left(1+\frac{3q}{S}\right)^{1/9}-1\right].
\tag{2.1}
\]

## 3. EXT08 — López--Stoll quantifier audit

López and Stoll use exactly the shortcut map above on `Z_2`. Their
`Q_odd` is the rational 2-adic subring. In the TeX source, Theorem
`aperiodic` states that if `zeta in Q_odd` has a divergent trajectory, where
“divergent” is explicitly defined as an infinite orbit set, then

\[
\boxed{\liminf_{\ell\to\infty}\frac{h(\ell)}\ell=\rho_c.}
\tag{3.1}
\]

The proof separates `liminf>rho_c`, excluded by the real conjugacy argument,
and `liminf<rho_c`, excluded for a rational 2-adic infinite orbit using the
Monks--Yazinski lower bound. Equality is the remaining case.

This is registered as EXT08, an `EXTERNAL_THEOREM`. The repository has audited
the map, input-parity convention, `liminf`, rationality domain, and cyclic
boundary; it does not reproduce the paper's full real-conjugacy proof.
Every positive integer is rational 2-adic, but EXT08 does not assert that its
orbit terminates.

## 4. P117 — discrepancy no-go from P72

Assume the P72 hypotheses and suppose first that

\[
0<h(\ell)-\rho_c\ell\le K\qquad(\ell\ge1).
\]

Then `1<C_l<=3^K`, so at odd times

\[
\beta_q=\sum_{j<q}\frac1{3c_j}\ge\frac q{3^{K+1}}.
\tag{4.1}
\]

The right side is linear, contradicting the `O_S(q^(1/9))` upper bound
(2.1). Thus no positive ordinary permanent-safe nonperiodic orbit has bounded
critical discrepancy. EXT08 is not used.

More generally, suppose for constants `K` and `gamma<8/9` that

\[
D_j\le\gamma\log(j+2)+K\qquad(j\ge0).
\tag{4.2}
\]

If `gamma<0`, (4.2) already contradicts `D_j>0` for all sufficiently large
`j`. For `0<=gamma<8/9`,

\[
\beta_q\ge\frac{e^{-K}}3\sum_{j<q}(j+2)^{-\gamma}
\ge\frac{e^{-K}}3\int_2^{q+2}x^{-\gamma}\,dx.
\]

This has order `q^(1-gamma)`, and the exact comparison

\[
\gamma<\frac89\quad\Longleftrightarrow\quad1-\gamma>\frac19
\]

contradicts (2.1). This is a global-envelope exclusion, not a pointwise lower
bound for every large `j`.

## 5. P118 and P119 — transcendence and conditional class exclusions

Unique factorization first shows that `rho_c` is irrational: a rational value
`m/n` would give `3^m=2^n`. If `rho_c` were algebraic irrational,
Gelfond--Schneider (EXT09) would make `3^rho_c` transcendental. On the positive
real branch `3^rho_c=2`, a contradiction. Therefore

\[
\boxed{\rho_c\text{ is transcendental}.}
\tag{5.1}
\]

Now assume EXT08 and suppose a rational 2-adic noncyclic shortcut orbit has a
natural one-frequency `rho`. Equation (3.1) forces `rho=rho_c`; hence `rho`
cannot be algebraic. This yields the following conditional exclusions.

- By Allouche--Shallit, an existing letter frequency of a morphic word is
  algebraic. Therefore a frequency-bearing morphic parity word is impossible.
- Saari proves existence of letter frequencies for every pure binary morphic
  word, so this entire subclass is impossible.
- A primitive substitution has frequencies from the normalized Perron vector
  of its integral incidence matrix. The Perron eigenvalue and vector
  coordinates are algebraic, and a letter-to-letter coding preserves
  algebraicity. Thus primitive substitutive parity words are impossible.
- Bell proves that both lower and upper asymptotic densities of every
  `k`-automatic set are rational. EXT08 already fixes the lower density at the
  transcendental number `rho_c`, so every automatic parity word is impossible
  even when its natural density does not exist.

These are collected as P119 (`CONDITIONAL`). No logarithmic frequency is
substituted for a natural or lower density.

## 6. P120 and P121 — bounded balance

For an infinite binary word, let `A_n` and `B_n` be the maximum and minimum
number of ones among its length-`n` factors. Concatenating two adjacent factor
pieces proves

\[
A_{m+n}\le A_m+A_n,
\qquad B_{m+n}\ge B_m+B_n.
\]

The elementary division argument behind the subadditive lemma gives

\[
\alpha=\inf_n\frac{A_n}{n},
\qquad \beta=\sup_n\frac{B_n}{n}
\]

as their limiting normalized values. If the word is `K`-balanced, then
`0<=A_n-B_n<=K`, so `alpha=beta=:rho`. Every factor `u` of length `n` obeys

\[
B_n\le\rho n\le A_n,
\qquad \boxed{\left||u|_1-\rho n\right|\le K.}
\tag{6.1}
\]

Applying (6.1) to prefixes also proves existence of the natural frequency.
This is P120 and uses no Collatz or literature hypothesis.

For a positive permanent-safe nonperiodic orbit, EXT08 identifies this
frequency with `rho_c`; (6.1) then gives bounded critical discrepancy,
contradicting P117. Hence P121 conditionally gives unbounded balance. Since
one-counts of consecutive length-`n` windows change by at most one, their set
is an integer interval, and binary abelian complexity equals balance plus one.
It is therefore also unbounded.

## 7. P122 and P123 — quasi-Sturmian exclusion

Let `s` be Sturmian with slope `theta`, and let `phi` map letters `a,b` to
finite binary words. Put

\[
A=|\phi(a)|,\ B=|\phi(b)|,
\quad a_1=|\phi(a)|_1,\ b_1=|\phi(b)|_1.
\]

Cassaigne's condition `phi(ab)!=phi(ba)` implies that neither image is empty:
if one were empty, the two concatenations would be equal. In a prefix of `m`
Sturmian letters the number `r_m` of `b` letters satisfies
`|r_m-theta*m|<=1`. Complete image blocks consequently have length and
one-count

\[
L_m=mA+r_m(B-A),
\qquad H_m=ma_1+r_m(b_1-a_1).
\]

With

\[
\rho_\phi=
\frac{(1-\theta)a_1+\theta b_1}
     {(1-\theta)A+\theta B},
\]

substitution cancels the main `m` term in `H_m-rho_phi L_m`; the remaining
term is a fixed coefficient times `r_m-theta*m`. Thus complete-block
discrepancy is bounded. An arbitrary output prefix adds at most one partial
image block, and a finite leading word adds another fixed error. This proves
P122.

EXT12 characterizes every quasi-Sturmian word as a finite prefix followed by
such a nonperiodic morphic image of a Sturmian word. Under EXT08, P122's
frequency is `rho_c`, so P117 rules the word out. This is P123
(`CONDITIONAL`). Sturmian words are included as a special case.

## 8. P124 — factor-complexity excess

If an infinite one-sided word has `p(n+1)=p(n)`, every length-`n` factor in
the tail has a unique right extension. Iteration on the finite factor set
makes the word eventually periodic. Therefore a non-eventually-periodic word
has

\[
p(n+1)>p(n),
\]

and `d(n)=p(n)-n` is a nondecreasing positive integer sequence. If `d(n)`
were bounded, it would eventually be constant, which is precisely the
quasi-Sturmian regime. P116 separates an ultimately periodic parity word at a
fixed positive source into the cycle branch or a nonpositive/nonintegral
rational shadow. Thus, for the noncyclic branch, P123 gives

\[
\boxed{p(n)-n\longrightarrow+\infty.}
\]

This is P124 (`CONDITIONAL`). It proves neither a linear excess nor positive
entropy; `n+o(n)` complexity remains possible.

## 9. Consequence for H112/H72

Any positive ordinary H112 candidate still needs eventual zero source lifts
by P115. Phase 20 adds necessary symbolic conditions: its infinite parity word
must have unbounded balance, unbounded abelian complexity, and unbounded
factor-complexity excess; it cannot be automatic, pure binary morphic,
primitive substitutive, Sturmian, or quasi-Sturmian under EXT08.

This localizes H112 to a more complicated escaping-discrepancy language. It
does not show that this language is empty and does not prove the eventual
nonzero-lift assertion.

## 10. E32 — exact finite falsification audit

The generator produced thirteen 512-bit prefixes and all factor statistics
through length 64. They include the all-contact word, both NG22 controllers,
P109, sources 167/1,126,015/1,394,431, both mandatory source families, and the
mandatory formal block families.

At factor length 64, selected exact rows are:

| word | `p(64)` | excess | balance | safe steps in stored prefix |
|---|---:|---:|---:|---:|
| all-contact | 65 | 1 | 1 | 512 |
| NG22 square-root | 438 | 374 | 4 | 512 |
| NG22 interval | 449 | 385 | 2 | 512 |
| P109 | 69 | 5 | 2 | 512 |
| source 167 | 45 | -19 | 5 | 28 |
| source 1,126,015 | 332 | 268 | 22 | 223 |
| `A^8B^8` periodic sample | 72 | 8 | 3 | 512 |

Negative finite-prefix excess is possible because the prefix does not contain
the whole infinite factor language. These rows are falsification and
regression data only. They do not establish any asymptotic word class.

The adversarial artifact additionally reconstructs 38 exact source-family
rows (`m=2..20`) and 64 `A^rB^s` rows (`1<=r,s<=8`).

## 11. Independence and tamper rejection

The generator computes factor sets with rolling integer encodings and affine
constants by recurrence. The verifier imports no generator code; it rebuilds
factor sets by direct string slicing and affine constants by the closed
odd-position sum

\[
B=\sum_{r=0}^{q-1}3^{q-1-r}2^{d_r}.
\]

It reconstructs every word from its mathematical/source definition, every
canonical residue, every lift, all 832 factor rows, and all adversarial rows.
Tests require rejection after changing a factor count, replacing the EXT08
`liminf`, or setting `proves_collatz=true`.

## What this result does not prove

- It does not prove EXT08--EXT13 internally.
- It does not exclude general morphic words without natural frequency.
- It does not turn a finite low-complexity prefix into an asymptotic class.
- It does not prove superlinear factor complexity, positive entropy, or
  randomness.
- It does not prove H112 or H72, eliminate nontrivial cycles, or prove the
  Collatz conjecture.

`proves_collatz=false`.
