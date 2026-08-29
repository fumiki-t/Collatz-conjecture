# Phase 21 audit — orbit separation, repetition, and factor complexity

Status: accepted repository derivations and bounded computations; Collatz remains
`OPEN`; `proves_collatz=false`.

## 1. Convention and scope

Throughout,

\[
T(x)=x/2\quad(2\mid x),\qquad T(x)=(3x+1)/2\quad(2\nmid x),
\]

`x_t=T^t(N)`, `v_t=x_t mod 2`, and
`h(t)=sum_{r<t}v_r`.  Parity is the input parity.  A positive orbit is
non-eventually-periodic exactly where no two states in the considered infinite
tail are equal.  Every theorem using state distinctness states that hypothesis;
the cycle case is never silently included.

The supplied note was treated as an untrusted proposal.  Its main inequalities
survive.  Three scope repairs were required:

1. López--Stoll supplies a `liminf` density and is used only in P128.
2. The Adamczewski--Bugeaud definition requires increasing periodic-part
   lengths.  To pass from the finite stammering inequality to `Dio(v)`, one
   must also prove `|U_nV_n| -> infinity`; otherwise a fixed bounded pair would
   force eventual periodicity.
3. Formal NG22/P109/A/B words and a finite canonical residue are not positive
   ordinary infinite sources.

## 2. P125 — exact finite parity correspondence

For integers `a,b` of the same parity, one shortcut step gives

\[
T(a)-T(b)=
\begin{cases}
(a-b)/2,&a,b\text{ even},\\
3(a-b)/2,&a,b\text{ odd}.
\end{cases}
\]

The multiplier after division by two is odd.  Induction therefore proves, for
every `n>=1`,

\[
v(a)_{[0,n)}=v(b)_{[0,n)}
\iff a\equiv b\pmod {2^n}.
\]

If `a!=b`, equality holds for exactly `v2(a-b)` initial bits.  Thus

\[
\operatorname{LCP}(v(a),v(b))=v_2(a-b).
\]

This is rederived internally.  Bernstein--Lagarias EXT14 is novelty/context,
not a proof dependency.

## 3. P126 — repeated-factor height

An odd step satisfies `T(x)+1=3(x+1)/2`; an even step satisfies
`T(x)+1=(x+2)/2<=x+1`.  Hence, exactly,

\[
(x_t+1)2^{h(t)}\le (N+1)3^{h(t)}.
\]

Suppose `i<j`, the states are distinct and positive, and the length-`n`
factors at `i,j` agree.  P125 gives `2^n | x_j-x_i`, so

\[
2^n\le |x_j-x_i|<\max(x_i,x_j)
  <(N+1)(3/2)^{h(j)}.
\]

The second inequality is strict because distinct positive integers differ by
less than their maximum.  Therefore

\[
2^{n+h(j)}<(N+1)3^{h(j)}. \tag{P126}
\]

Replacing the last `<` by `<=`, replacing `h(j)` by `h(i)`, or omitting state
distinctness changes the theorem and is rejected by tamper tests.

## 4. P127 — unconditional linear factor complexity

Let `p(n)` be the number of length-`n` factors of the infinite parity word.
Among the `p(n)+1` factors starting at `0,...,p(n)`, two agree.  Apply P126 with
second start `j<=p(n)` and `h(j)<=j`:

\[
n<\log_2(N+1)+\log_2(3/2)p(n).
\]

Thus

\[
p(n)>\frac{n-\log_2(N+1)}{\log_2(3/2)},\qquad
\liminf_{n\to\infty}\frac{p(n)}n\ge
\frac1{\log_2(3/2)}.
\]

Acceptance decisions use P126's integer inequality; logarithms only restate
it.  This unconditionally strengthens P123/P124 for positive nonperiodic
integer orbits.  Their historical external conditional formulations remain in
the ledger.

## 5. P128 — EXT08 critical-density limsup

Assume EXT08.  Choose `m_k` with

\[
h(m_k)/m_k\to\rho_c=\log 2/\log 3
\]

and put

\[
n_k=\lfloor\log_2(N+1)+\log_2(3/2)h(m_k)\rfloor+1.
\]

P126 forbids a repeated length-`n_k` factor whose second start is at most
`m_k`.  Hence `p(n_k)>=m_k+1`, while
`n_k/m_k -> (1-rho_c)`.  Therefore

\[
\limsup_{n\to\infty}\frac{p(n)}n\ge
\frac1{1-\rho_c}=\frac{\log 3}{\log(3/2)}.
\]

This is `CONDITIONAL`: EXT08 is not reproved, and no natural density is used.

## 6. P129/P130 — stammering and prefix powers

If a prefix is `UV^w`, write `a=|U|`, `d=|V|`, and `K=|UV^w|`.
The starts `a,a+d` agree for `K-a-d` bits, so P126 yields

\[
K<a+d+\log_2(3/2)h(a+d)+\log_2(N+1)
 <\log_2(3)(a+d)+\log_2(N+1).
\]

In Condition `(*)` for the Diophantine exponent, increasing `|V_n^{w_n}|`
and non-eventual periodicity force `|U_nV_n| -> infinity`: if those lengths
were bounded along a subsequence, one fixed pair `(U,V)` would give
arbitrarily long periodic tails and hence eventual periodicity.  Dividing and
taking the supremum proves

\[
\operatorname{Dio}(v)\le\log_2 3.
\]

For a prefix `W^r`, put `d=|W|`, `q=|W|_1`.  The starts `0,d` agree for
`(r-1)d` bits, so

\[
N+1>2^{(r-1)d}(2/3)^q\ge(2^r/3)^d.
\]

For `r=2`, this is `d<log_{4/3}(N+1)`.  An internal power starting at time
`i>0` uses local source `x_i`; the original `N` cannot be substituted.

## 7. P131 — height/complexity tradeoff

Among positive integers at most `H`, one residue modulo `2^n` occurs at most

\[
1+\lfloor(H-1)/2^n\rfloor
\]

times.  P125 partitions the first `m+1` distinct states by their length-`n`
parity factors.  For `H_m=max_{j<=m}x_j`,

\[
p(n)\ge\left\lceil\frac{m+1}
 {1+\lfloor(H_m-1)/2^n\rfloor}\right\rceil.
\]

At `n=ceil(log2 H_m)` the denominator is one.  Consequently polynomial
complexity of degree `d` forces `H_m>=exp(Omega(m^(1/d)))`; zero entropy forces
`log H_m/log m -> infinity`.  These are lower bounds on peaks, not upper bounds
and not contradictions.

## 8. P132 — H89 repetition certificate

Under P54, `N<=H_q=B_q^max/D_q`.  P126 implies every repeat in the critical
prefix satisfies

\[
2^{n+h(j)}D_q<(B_q^{max}+D_q)3^{h(j)}.
\]

Thus the reversed weak inequality is an exact rejection certificate.  It uses
only integers and can reject a word before enumerating its source residue.
Nothing here forces every large critical word to contain such a repeat.

## 9. E33 finite audit

The generator and independent verifier rebuilt:

- all 299,999 sources `1<=N<300000` through their first repeated state;
- every repeated width `1<=n<=64`, compressed by the maximum LCP at each
  second start (the maximum inequality implies every smaller one);
- all 502,523 critical words and 406,353 same-Q geodesic words through Q=17;
- 11 named 512-bit controls and 132 mandatory-family rows.

The direct interval has maximum 279 distinct states at source 230631, maximum
state 12,324,038,948 at source 270271, and maximum distinct-state LCP 20 at
source 33019.  All sources enter the `1,2` cycle; finite distinct segments were
audited, and the periodic tail was not treated as nonperiodic.

P132 rejects 160,429 critical and 120,982 geodesic words.  At Q=17 it rejects
32,524 of 312,455 critical and 21,462 of 253,018 geodesic words.  Most words
survive; this is an obstruction to promoting the filter to H89.

Generator and verifier use different representations:

- generator: rolling factor integers, dynamic LCP tables, integer safe-word
  frontier, bit-hack reversed keys;
- verifier: direct substring tuples, literal affine position sums, string
  recursion, byte-table reversed keys.

Five metadata tamper classes are rejected before the expensive finite replay.

## 10. Literature boundary

- Bernstein--Lagarias gives the standard 2-adic parity conjugacy.
- Adamczewski--Bugeaud fixes the Diophantine-exponent Condition `(*)`.
- Bugeaud--Kim uses `r(n,x)` for the shortest prefix containing a second
  length-`n` occurrence; Phase 21's second start is `R_v(n)=r(n,v)-n` under
  the repository's zero-based indexing.
- Nicholson--Rampersad supplies initial nonrepetitive-complexity terminology.
- Stérin is binary carry/first-source context, not a proof input.
- López--Stoll EXT08 is used only by P128.

No literature-wide novelty claim is made.  Targeted searches did not locate
the exact slopes P127/P128, so they are described only as repository
derivations.

## 11. What this result does not prove

- A lower factor-complexity bound does not bound orbit peaks from above.
- Finite Q<=17 exclusion rates do not imply eventual repetition.
- Repeat avoidance has not been converted to nonzero P115 source lifts.
- H89, H112, H72, the nontrivial-cycle branch, and Collatz remain open.
- `proves_collatz=false`.
