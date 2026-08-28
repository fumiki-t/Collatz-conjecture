# Phase 16 audit — critical geodesic / ultra-low-height dichotomy

## 1. Result and scope

This audit treats `phase16_critical_dichotomy_v2.md` as an untrusted research
proposal.  It accepts the carry, normalized-correction, geodesic, local-merge,
packing, and dichotomy mechanisms only after the repairs below.  It does not
accept either branch as impossible.

The shortcut map is

\[
T(x)=x/2\quad(x\equiv0\pmod2),\qquad
T(x)=(3x+1)/2\quad(x\equiv1\pmod2).
\]

For a word `w` of length `L`, odd count `q`, and correction `B(w)`,

\[
F_w(x)=\frac{3^q x+B(w)}{2^L}.
\]

`Safe` means `3^{q_l}>2^l` at every nonempty prefix of length `l`.  Equality
cannot occur for positive `l`, so this agrees with the repository's weak-form
coefficient convention.

Accepted labels are P97--P102 `VERIFIED_THEOREM`, P103 `CONDITIONAL`, E27
`VERIFIED_FINITE`, NG28 `REFUTED`, and H97/H98 `OPEN`.
`proves_collatz=false`.

## 2. Repairs to the proposal

Two small gaps were repaired rather than copied.

First, the proposed inequality `B/3^q<q/3` is false for `q=1`: the only safe
word is `1`, and `B/3=1/3`.  P97 therefore states

\[
\frac{B}{3^q}=\frac13\quad(q=1),\qquad
\frac13<\frac{B}{3^q}<\frac q3\quad(q\ge2).
\]

Every distinct-length safe same-`Q` pair has `q>=2`, so both proposed carry
bounds survive unchanged.

Second, the displayed function `Phi(t)` is defined in the stated form only
after the continuous packing has filled the first four height intervals,
namely `t>=133/576`.  In the G250 proof, `t<133/576` is handled directly by
`Y_q<=N+q/3<2N`; `133/576<=t<=250` uses monotonicity of `Phi`.  No formula is
used outside its domain.

## 3. NG28 — negative same-Q carry

For

```text
a = 111111111101111110101011110010001001100
d = 1101101101110011100111011101010101101101
```

literal reconstruction gives

```text
Q(a)=Q(d)=26
L(a)=39, L(d)=40
B(a)=2,830,029,652,969
B(d)=13,285,656,790,925
S(a)=155,014,110,207
S(d)=310,028,220,411
endpoint=716,727,426,419
```

Both words are safe, and

\[
2B(a)-B(d)=-7,625,597,484,987=-3\cdot3^{26},
\]

so `S(d)=2S(a)-3`.  Thus the universal positive-carry hypothesis is
`REFUTED`.  A common legal suffix may extend the collision whenever the two
extended paths remain safe; this is not an assertion about arbitrary illegal
suffixes.

## 4. P97 — correction and carry bounds

Let the odd positions of a safe word be

\[
0=d_0<d_1<\cdots<d_{q-1}.
\]

The exact affine recurrence gives

\[
\frac{B(w)}{3^q}
=\sum_{j=0}^{q-1}\frac{2^{d_j}}{3^{j+1}}.
\]

The first term is `1/3`.  For `j>=1`, safety just before the `j`-th
zero-indexed odd position gives `2^{d_j}<3^j`, so each later term is strictly
below `1/3`.  This proves the repaired bound in Section 2.

Suppose safe words `a,d` have the same odd count and endpoint and
`L(d)=L(a)+k`, `k>=1`.  Equating affine maps gives

\[
S_d=2^kS_a+m,\qquad
m=2^k\frac{B(a)}{3^q}-\frac{B(d)}{3^q}\in\mathbb Z.
\]

Such a pair necessarily has `q>=2`.  Positivity and the upper correction
bound give

\[
m>-\frac q3.
\]

The strict lower correction bound for `a` gives

\[
m>\frac{2^k-q}{3}.
\]

Consequently `m<0` implies `2^k<q`.  This bound survives NG28, but it does not
make carry nonnegative.

## 5. P98 — normalized correction and geodesicity

Let `x_i` be the odd inputs encountered before the prefix with `j` odd
steps.  At an odd step,

\[
\frac{T(x_i)}{(3/2)x_i}=1+\frac1{3x_i},
\]

while intervening even steps cancel under coefficient normalization.  Hence

\[
Y_j=N\prod_{i<j}\left(1+\frac1{3x_i}\right)
=N+\frac{B_j}{3^j}.
\]

It is strictly increasing with `j`.  At a coefficient first crossing, the
crossing bit is even.  If `X` is the crossing endpoint and `Z=2X` the
preceding safe endpoint, then

\[
X=\frac{3^q}{2^{K_q}}Y_q<Y_q.
\]

Now let a safe prefix `d` from `N` reach `M` with odd count `j`.  If a safe
word `a`, shorter by `k>=1` with the same odd count, also reaches `M` from a
positive source `x`, then

\[
Y_j=2^k\left(x+\frac{B(a)}{3^j}\right),
\qquad x<Y_j/2^k.
\]

Under P89's least-counterexample ancestral minimality, `Y_j<2N` therefore
forbids `a`.  Since `Y_j<=Y_q`, `Y_q<2N` makes every prefix same-`Q`
geodesic.

Prefix closure also follows directly.  If a geodesic word had a prefix with
a shorter same-`Q` safe alternative, append the original right suffix.  Both
paths start that suffix at the same endpoint.  The alternative prefix has a
larger coefficient because it is shorter with the same odd count, so every
extended coefficient remains above the original safe coefficient.  The
result is a shorter safe same-`Q` word to the final endpoint, a contradiction.

## 6. P99 — local merge restrictions

All statements here are proved by literal shortcut traces.  The primary
literature is context, not a dependency.

- If `x=2 mod 3`, then `u=(2x-1)/3` is odd and `T(u)=x` (`1`).
- If `x=4 mod 9`, then `u=(8x-5)/9` follows `110` to `x`.
- If `x=8 mod 9`, then `u=(4x-5)/9` follows `11` to `x`.
- If `x=5 mod 8`, equivalently `v2(3x+1)>=3`, the paths from
  `(x-1)/2` (`01`) and from `x` (`100`) merge at `(3x+1)/8`.
- If `x=-1 mod 3^r`, then
  `u_r=2^r(x+1)/3^r-1` follows `1^r` to `x`.

For an odd value `x` on a least-counterexample orbit, each proposed source
would share the nonconvergent future.  Least positivity therefore gives

\[
\begin{aligned}
x<3N/2&\Rightarrow x\not\equiv2\pmod3,\\
x<9N/8&\Rightarrow x\not\equiv4\pmod9,\\
x<9N/4&\Rightarrow x\not\equiv8\pmod9,\\
x<2N&\Rightarrow x\not\equiv5\pmod8,
\end{aligned}
\]

and `u_r>=N` gives the exact all-odd inequality

\[
x+1\ge(3/2)^r(N+1).
\]

Angeltveit's 2026 preprint, Section 2.3, gives the same mod-3/mod-9 and
odd-even-even sieve patterns.  This repository's theorem is the elementary
specialization above and invokes no result from that preprint.

## 7. P100 — discrete mod-72 packing

On a nonperiodic orbit the odd values are distinct.  Every odd input after
the initial `N` is coprime to 6.  Combining P99 modulo `lcm(8,9)=72` gives:

| normalized height | allowed residues | density |
|---|---:|---:|
| `[N,9N/8)` | 6 | `1/12` |
| `[9N/8,3N/2)` | 9 | `1/8` |
| `[3N/2,2N)` | 15 | `5/24` |
| `[2N,9N/4)` | 20 | `5/18` |
| `[9N/4,infinity)` | 24 | `1/3` |

The exact lists, not only the counts, are stored in
`artifacts/phase16_theory.json` and independently rebuilt.

For a decreasing nonnegative function `f`, one residue class modulo 72 in an
interval `[a,b)` satisfies

\[
\sum f(x)\le f(a)+\frac1{72}\int_a^b f(u)\,du.
\]

Indeed, charge the first point to `f(a)` and each later point to the preceding
length-72 interval.  Applying this to `f(x)=1/x` creates at most one left
endpoint error per allowed residue.  The five interval errors total
`6+9+15+20+24=74`; the possibly non-unit initial value `N` is a 75th point
mass.

The continuous capacity below `9N/4` is

\[
N\left(\frac1{96}+\frac3{64}+\frac5{48}+\frac5{72}\right)
=\frac{133}{576}N.
\]

For `t=q/N>=133/576`, the continuous cutoff having mass `q` is

\[
H/N=3t+299/192.
\]

The 75 point masses plus this truncated continuous measure dominate the
cumulative count of the `q` odd inputs.  Integration gives

\[
\sum_{i<q}\frac1{x_i}\le\frac{75}{N}+\Phi(t),
\]

where

\[
\Phi(t)=\frac{13}{36}\log\frac98+
\frac13\log\frac43+
\frac13\log\left(\frac{3t+299/192}{9/4}\right).
\]

Finally `log(1+u)<=u` gives

\[
\log(Y_q/N)\le25/N+\Phi(t)/3.
\]

The distinctness hypothesis is essential; P100 is not applied to a repeated
periodic segment.

## 8. P101 — the nonperiodic 250 dichotomy

The verifier encloses each logarithm by

\[
\log x=2\sum_{n=0}^{s-1}\frac{z^{2n+1}}{2n+1}+R_s,
\quad z=\frac{x-1}{x+1},
\]

with

\[
0<R_s<\frac{2z^{2s+1}}{(2s+1)(1-z^2)}.
\]

To avoid a slowly convergent ratio, it uses

\[
\frac{144299}{324}=2^8\frac{144299}{82944}.
\]

Twelve exact rational terms certify

\[
\Phi(250)+75/100000<3\log2
\]

with a strictly positive stored rational margin.  No floating-point value
decides acceptance.

Assume `N>=100000`, a finite coefficient first crossing, and distinct odd
inputs before crossing.

If `q<=250N`, then either `q/N<133/576` and P97 directly gives `Y_q<2N`, or
P100 and monotonicity of `Phi` give

\[
\log(Y_q/N)\le25/N+\Phi(250)/3<\log2.
\]

Thus branch G250 has `Y_q<2N`, so P98 makes every safe prefix same-`Q`
geodesic.

If `q>250N`, put `t=q/N`.  Direct differentiation gives

\[
\frac{d}{dt}\log\left(\frac{e^{\Phi(t)/3}}t\right)
=\frac{1}{3(3t+299/192)}-\frac1t<0.
\]

The same endpoint comparison at `t=250` then gives

\[
Y_q<q/125,qquad X<q/125,qquad Z<2q/125,
\]

and `N<q/250`.  This is branch H250.  The theorem proves the dichotomy; H97
and H98 are the still-open exclusions of its two branches.

## 9. P102/P103 — periodic-safe boundary and q0 consequence

Without distinctness, P97 gives the universally valid bound

\[
Y_q\le N+q/3.
\]

Therefore `q<3N` still implies `Y_q<2N` and all-prefix geodesicity.  If
`q>=3N`, only

\[
N\le q/3,\qquad X<Y_q\le2q/3
\]

is obtained.  This retains the nontrivial-cycle branch.

In the Phase 7 conditional scenario,

\[
q_0=72057431991<3(2075\cdot2^{60})<3N
\]

after importing X02.  Hence P103 says that the q0 critical word must be
all-prefix same-`Q` geodesic, whether or not values repeat.  Its status is
`CONDITIONAL` because P54's least-counterexample/first-crossing framework and
the external finite computation X02 remain assumptions.

## 10. E27 — finite layers and adversarial audit

The generator exhausts every safe word through `Q=17`.  A word is called
critical in this artifact when

\[
L=\lfloor\log_2(3^Q)\rfloor,
\]

so appending zero is the coefficient first crossing.  A contact is an odd
position `d_j=floor(log2(3^j))`.  The finite diagnostic `contact-rich` means
exactly `100*contacts>43*Q`, matching the Phase 7 threshold; it is not a new
asymptotic definition.

At `Q=17` the audit finds:

```text
all safe words over all lengths: 663,535
critical words:                  312,455
same-Q geodesic:                 253,018
all-prefix same-Q geodesic:      253,018
contact-rich:                     32,813
contact-rich geodesic:            27,949
minimum critical source:             167
minimum critical endpoint:           325
```

The equality of whole-word and all-prefix counts independently checks P98's
prefix closure.  Through `Q=17`, 225,943 same-endpoint pairs are reconstructed;
none has negative carry and the minimum is 1.  This finite absence does not
weaken NG28's exact `Q=26` counterexample.

The adversarial artifact contains 68 exact rows covering `2^m-1`, `8^m-5`,
`(110|111)^*`, `A`, `B`, `A^rB^s`, the Phase 7 all-contact prefix, NG27, and
NG28.  These are convention and falsification regressions only.

## 11. Literature and newness boundary

- Vigleik Angeltveit, *An improved algorithm for checking the Collatz
  conjecture for all n < 2^N*, arXiv:2602.10466 (2026), Section 2.3 and Lemmas
  2.6--2.9: primary-source context for path merging and mod-9/odd-even-even
  sieves.
- The all-contact/geodesic formal boundary remains governed by P73 and NG17.
  Phase 16 does not infer positive ordinary integrality from a coherent
  2-adic word.
- A predecessor transducer is a proposed H98 direction only.  No transducer,
  pumping lemma, or external theorem is used in P97--P102.

The repository contribution is the exact specialization, repaired proof,
finite audit, and explicit two-branch obligation.  It is not a literature-wide
novelty claim.

## 12. What this result does not prove

- H97/G250 or H98/H250;
- exclusion of a nontrivial periodic orbit;
- eventual H89 or the infinite-safe H72 obligation;
- an asymptotic conclusion from Q<=17;
- the Collatz conjecture.

`proves_collatz=false`.
