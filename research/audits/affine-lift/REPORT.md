# Phase 19 audit — affine valleys, critical tails, and source lifts

## 1. Result and scope

This audit treats `phase19_affine_lift_note.md` as an untrusted research
proposal.  The supplied note has SHA-256
`e798d0ac572fa48d8b71610075c0a0b5f549cfd9c1f3b030ef11bfafd006da22`.
Its main identities survive, with three scope repairs:

1. exact valuations after zero source lifts require realization of the whole
   infinite tail; a terminal finite congruence alone proves only divisibility;
2. the periodic theorem requires an odd step in the repeating block; the
   all-zero block has fixed point zero and is not a positive odd-cycle case;
3. eleven terminal zero lifts at source 167 are a finite obstruction to any
   bounded zero-run rule, not evidence of eventual stabilization.

P112--P116 are `VERIFIED_THEOREM`, E31 is `VERIFIED_FINITE`, NG31 is
`REFUTED`, and H112 remains `OPEN`.  P114 supersedes the external-input use in
P110 for the particular balanced P109 construction, but it does not exclude
every path in a mixed SCC.  H72 and the Collatz conjecture remain open;
`proves_collatz=false`.

All acceptance decisions use integers, `Fraction`, or symbolic inequalities.
No floating-point tail fit is used.

## 2. Accelerated affine coordinates

For positive odd-step exponents `e_0,...,e_(n-1)`, put

\[
E_n=\sum_{i<n}e_i,
\qquad c_n=\frac{3^n}{2^{E_n}},
\qquad
\beta_n=\sum_{j<n}\frac{2^{E_j}}{3^{j+1}}
       =\sum_{j<n}\frac1{3c_j}.
\]

If `x` is the initial odd value and `y_n` the value after the `n` accelerated
odd steps, direct induction gives

\[
y_n=c_n(x+\beta_n),
\qquad
c_{n+1}=c_n\frac3{2^{e_n}},
\qquad
\beta_{n+1}=\beta_n+\frac1{3c_n}.
\]

Writing `A_n=3^n beta_n`, the integral affine form is

\[
2^{E_n}y_n=3^n x+A_n,
\qquad
A_n=\sum_{j<n}3^{n-1-j}2^{E_j}.
\]

The generator obtains `A_n` by recurrence.  The verifier instead reconstructs
the displayed exponent-position sum.

## 3. P112 — deterministic affine-or-valley theorem

Let `N` be a positive reference height, let `x<N` be a positive predecessor
of `y=uN` with `u>=1`, and let a finite accelerated word send `x` to `y`.
The word itself need not be coefficient-safe.  Put

\[
c=c_n,
\qquad m=\min_{0\le j\le n}c_j,
\]

and cut immediately after the last index `r` with `c_r=m`.  Every nonempty
prefix of the remaining suffix has coefficient `c_(r+k)/m>1`: equality would
give a later minimum, and no nonempty power of three equals a power of two.
Thus the suffix is strictly coefficient-safe, with terminal coefficient

\[
C_b=\frac c m.
\]

Let `v` be its positive source.  The suffix affine correction is positive, so

\[
v<\frac y{C_b}.
\]

If `C_b>u`, then `v<N`; this is the safe-valley alternative.  Otherwise
`m>=c/u`, whence

\[
\beta_n=\sum_{j<n}\frac1{3c_j}
\le\frac n{3m}\le\frac{nu}{3c}.
\]

Since `x=uN/c-beta_n<N`, also

\[
\beta_n>N\left(\frac uc-1\right).
\]

Combining the strict lower and weak upper bounds yields

\[
\boxed{n>3N\left(1-\frac cu\right)}.
\]

Thus a predecessor that does not expose a smaller safe valley is either long
on the scale of `N` or lies in the stated near-diagonal coefficient band.  The
theorem localizes that band; it does not prove the band empty.

## 4. P113 and NG31 — two tilts and the critical first moment

Define two geometric exponent laws on `e>=1`:

\[
\mathbb P_-(e)=2^{-e},
\qquad
\mathbb P_+(e)=\frac3{4^e},
\qquad M_e=\frac3{2^e}.
\]

The elementary geometric sums give

\[
\mathbb E_-M_e=1,
\qquad
\mathbb E_+M_e^{-1}=1.
\]

Therefore `c_n` and `c_n beta_n-n/3` are martingales under `P_-`, while
`1/c_n` and `beta_n-n/(3c_n)` are martingales under `P_+`.

For `t>1`, set `T_t=inf{n>=1:c_n>=t}` and first stop at the bounded time
`tau=T_t cap R`.  Optional stopping is used only at this bounded time.  On
every stopped prefix `w`,

\[
\frac{\mathbb P_+(w)}{c(w)}
=\frac{3^n}{4^{E_n}}\frac{2^{E_n}}{3^n}
=2^{-E_n}=\mathbb P_-(w).
\]

The stopped `P_+` martingale consequently gives the exact duality

\[
\boxed{
\mathbb E_+\beta_{T_t\wedge R}
=\frac13\mathbb E_-[T_t\wedge R].
}
\]

Under `P_+`, the walk has positive log drift.  The finite Chernoff argument
already audited in Phase 17 proves `T_t<infinity` almost surely without
assuming an unbounded optional-stopping theorem.  Under `P_-`, the
nonnegative martingale `c_n`, stopped at a finite horizon, gives Doob's bound

\[
\mathbb P_-(T_t<\infty)\le\frac1t.
\]

Hence

\[
\mathbb E_-[T_t\wedge R]\ge R(1-1/t).
\]

Monotone convergence in the bounded identity proves

\[
\boxed{\mathbb E_+\beta_{T_t}=\infty.}
\]

This refutes NG31, the proposed use of the affine correction as a finite-mean
average-small error.

For `0<s<1`, subadditivity and Tonelli give

\[
\mathbb E_+\beta_{T_t}^s
\le 3^{-s}\sum_{j\ge0}\mathbb E_+c_j^{-s}
=\frac{3^{-s}}{1-R(s)},
\qquad
R(s)=\frac{3^{1-s}}{2^{2-s}-1}.
\]

Strict Hölder/log-convexity for the nonconstant random variable `M_e^-1`,
together with `R(0)=R(1)=1`, proves `R(s)<1`.  Thus every moment below one is
finite, while the first moment diverges.

Finally, first-passage words satisfy `c(w)>=t` and
`P_+(w)=3^(-|w|)c(w)^2`.  Markov's inequality yields, for every `B>0`,

\[
\sum_{\substack{w\in\mathcal F_t\\\beta(w)\ge B}}3^{-|w|}
\le
\frac{3^{-s}}{(1-R(s))t^2B^s}.
\]

This is a Haar-volume upper bound, not a deterministic ordinary-source count.

## 5. P114 — P72 occupation obstruction

For a positive nonperiodic permanent-safe odd orbit from tail minimum `S`,
put `D_i=log c_i`.  The Phase 12 normalization has
`Y_j=S+beta_j`, so the affine identity gives exactly

\[
\boxed{
\sum_{i<j}e^{-D_i}=3\beta_j=3(Y_j-S).
}
\]

P72 supplies

\[
Y_j\le
S e^{1/S}\left(1+\frac{3j}{S}\right)^{1/9}.
\]

For fixed `H`, each index with `D_i<=H` contributes at least `e^-H`.
Therefore

\[
R_H(j):=\#\{i<j:D_i\le H\}
\le
3e^H S\left[
e^{1/S}\left(1+\frac{3j}{S}\right)^{1/9}-1
\right]
=O_{S,H}(j^{1/9}).
\]

This strengthens Phase 18 for P109's fixed-packet balanced construction.  Its
packet-boundary discrepancy is bounded, and its positive packet occurs with
positive lower frequency.  Choose one odd step inside that fixed packet.
Its displacement from the boundary and its coefficient factor are bounded by
the packet, so linearly many accelerated odd boundaries lie in one fixed
strip.  If the itinerary had a positive ordinary P72 realization, this would
contradict the sublinear occupation bound.  EXT07 is not needed for this
particular exclusion.

The conclusion does not cover arbitrary mixed-SCC itineraries whose
discrepancy escapes and returns to every bounded strip only `O(j^(1/9))`
times.

## 6. P115 — exact source-lift stabilization

Let `r_n` be the canonical positive source representative modulo `2^E_n` for
the first `n` accelerated odd steps.  Nested cylinders give the unique lift

\[
r_{n+1}=r_n+\lambda_n2^{E_n},
\qquad 0\le\lambda_n<2^{e_n}.
\]

Let `y_n` be the canonical endpoint of the `n`-step prefix.  Substituting the
lift into the next affine congruence and dividing by `2^E_n` proves

\[
\boxed{
3^{n+1}\lambda_n\equiv-(3y_n+1)\pmod{2^{e_n}}.
}
\]

An infinite exponent word has a fixed positive ordinary source `N` exactly
when `r_n=N` eventually: once `2^E_n>N`, `N` itself is the least positive
representative.  This is in turn equivalent to `lambda_n=0` eventually.
Conversely, eventual zero lifts make the nested residue sequence a fixed
positive integer satisfying every prefix congruence.

After the **entire infinite word** is known to be realized by this integer,
the declared exponent is the exact valuation `v2(3y_n+1)`.  At a lone finite
terminal prefix, the displayed congruence proves divisibility only; later
parity data are needed to rule out a larger valuation.

The next exact target is H112: prove that every infinite coefficient-safe
all-prefix same-Q-geodesic branch has infinitely many nonzero lifts.  P115
would then exclude a positive ordinary source in that sublanguage.  P115 by
itself does not prove H112.

## 7. Source 167 — the finite zero-run obstruction

At `Q=17`, the least-source geodesic word

```text
11101101111110011110001010
```

has source 167, endpoint 325, accelerated exponents

```text
1,1,2,1,2,1,1,1,1,1,3,1,1,1,4,2,2
```

and source residues

```text
1,3,7,7,39,167,167,167,167,167,167,167,167,167,167,167,167.
```

Its final eleven exponent lifts are zero.  Nevertheless, the literal orbit
continues with shortcut bits `100` and crosses below coefficient one three
steps later, at `(L,Q)=(29,18)`, with value 122.  Thus no theorem that sees
only a bounded terminal zero-lift run can infer eventual stabilization.

## 8. P116 — periodic rational lifts

For a nonempty repeating block `w` containing an odd step, write

\[
F_w(x)=\frac{3^q x+B}{2^L}.
\]

The unique 2-adic fixed source is

\[
\xi_w=\frac{B}{2^L-3^q}.
\]

Reduce it as `a/d` with `d>0` odd.  Its canonical residue `r_K` modulo `2^K`
satisfies

\[
dr_K=a+z2^K.
\]

If `xi_w` is not a positive integer and `2^K>=2|a|`, then `z` cannot be zero
and positivity forces `z>=1`.  Consequently

\[
r_K\ge\frac{2^K-|a|}{d}
\ge\frac{2^{K-1}}d
\ge 2^{K-P},
\qquad P=1+\lceil\log_2d\rceil.
\]

The same argument applies after a finite affine prefix: its preimage of the
rational periodic point is again rational with odd reduced denominator.  The
positive-integer exception enters the represented periodic cycle.  Therefore
an ultimately periodic noncycle word cannot be the stable prefix language of
one fixed positive source.

This is an elementary rational congruence argument consistent with standard
2-adic eventual periodicity.  No literature-wide novelty is claimed.  The
all-zero repeating block is outside the odd-step statement; its fixed point
is zero.

## 9. E31 — finite exact audit

The generator and independent verifier reconstruct:

```text
P112 product audit, n<=6 and 1<=e_i<=4:
  eligible positive-predecessor rows: 136
  safe-valley / affine-length:         104 / 32

T_2 bounded stopping, R<=12:
  active nodes at R=12:                11,433
  ordinary leaves:                      3,330
  E_- (T cap 12):                       566235/65536
  E_+ beta_(T cap 12):                  188745/65536

same-Q geodesic critical words, Q<=17:
  total audited rows:                  406,353
  Q=17 critical / geodesic:            312,455 / 253,018
  maximum terminal zero lifts:         11

periodic samples:                       8 words x 16 repeats
mandatory/adversarial rows:             63
```

The stopped tree sums the infinite exponent tails that cannot hit before the
horizon by exact geometric series.  Its total mass is one under both tilts.
The source-lift audit stores row digests rather than 406,353 derived rows; the
verifier independently re-enumerates every row.  Tamper tests alter theorem
status, stopped mass, source-167 data, periodic residues, adversarial digests,
and the obstruction report, and require rejection.

These finite data check implementations and expose the source-167 obstruction.
They are not evidence for an eventual lift theorem or an asymptotic tail fit.

## 10. Strategic interpretation

- P112 gives an exact local sieve: short affine-only predecessors must be very
  near the target coefficient.  H89/H104/H105 still need ordinary source,
  endpoint, carry, and height information to empty this band.
- P113 shows why simply averaging the affine correction into Phase 17's Haar
  pressure cannot work: the relevant first moment is infinite.  Fractional
  tail control survives and may still combine with deterministic height.
- P114 internally excludes the canonical balanced P109 itinerary, but leaves
  aperiodic escaping-discrepancy schedules.
- P115 identifies eventual nonzero lifts as the exact ordinary-integrality
  bottleneck.  H112 is intentionally narrower than H72 and is a concrete next
  theorem target.
- P116 removes ultimately periodic noncycle lift stabilization by an
  elementary effective bound.  Nontrivial positive cycles remain a separate
  branch.

## 11. What this result does not prove

- H112 or any all-depth nonzero-lift theorem;
- emptiness of P112's near-diagonal affine-only band;
- exclusion of every aperiodic escaping-discrepancy mixed itinerary;
- H72, H89, H104, or H105;
- exclusion of nontrivial positive cycles;
- the Collatz conjecture.

`proves_collatz=false`.
