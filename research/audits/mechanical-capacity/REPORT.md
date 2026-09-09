# Phase 42 audit — mechanical capacity, defect variation, and signed carry

Base: Phase 41 acceptance `098251967ee347ce9847a10c08ffc303bf21c48a`.
Date: 2026-09-10. The supplied followup is a proposal, not mathematical
authority. `proves_collatz=false`; H112/H72/H89/H133 remain `OPEN`.

## 1. Scope, dependencies, and audit changes

| ID | Status | Exact scope |
|---|---|---|
| P252 | `VERIFIED_THEOREM` | Simultaneous pure-mechanical interval capacity and its integrated energy inequality, under positive literal distinct-state hypotheses. |
| P253 | `VERIFIED_THEOREM` | Finite maximum-defect/downward-variation inequality; the asymptotic variation corollary additionally uses P221. |
| P254 | `VERIFIED_THEOREM` | A positive permanent-safe orbit with nondecreasing odd defect has lower limiting defect divided by square-root time at least `sqrt(2 log_2 3)`. |
| P255 | `VERIFIED_THEOREM` | The specific Phase 13 square-root word u, and P251's finite extension w, have no positive ordinary integer infinite source. |
| P256 | `VERIFIED_THEOREM` | The minimum q for negative carry between two positive literal safe same-q words, with a shorter alternative, is exactly 22. |
| E58 | `VERIFIED_FINITE` | Declared finite orbit checks, the complete q<=21 pruning remainder, eight repeat-and-split certificates, and retained regressions. |

Inputs are the internally rederived parity correspondence P125, elementary
irrational mechanical coding, and the square-shell argument already in P251.
Only the general asymptotic part of P253 uses P221 reciprocal summability.
P254/P255 do **not** require P221, Garcia--Tal, Heppner, or X02. No new
external theorem or literature-wide originality claim is asserted. This is
an orbit-specific application of P125/P131's existing height/complexity
principle, not a replacement for those results.

The acceptance makes the following issues explicit:

- The finite prefix starts at an odd source with defect zero. It is not an
  arbitrary internal interval with unadjusted inherited defects.
- All counted full shortcut input states must be distinct. Our finite checker
  uses the slightly stronger condition that the final endpoint is distinct too.
- Pure intervals are literal factors of the *infinite* mechanical word.
  The mutated terminal zero of P141/NG32 is not included.
- In the general asymptotic argument, `H_q -> infinity` must be proved before
  discarding `D_q/q`; merely assuming `H_q=o(sqrt(q))` is insufficient.
- The 2,048-source finite CAP check has zero factor occurrences. It checks
  conventions and identities but is vacuous as a numerical packing test.
  The separate repeat certificates have genuinely positive excess counts.
- Old accepted Phase 41 JSON, including its historical ordinary-source
  `OPEN` field, remains immutable. P255 supplies the later answer for that
  specific model; P251 and NG45 remain valid at the formal/2-adic level.

## 2. Convention, normalization, and distinctness

Use the full shortcut map `T(x)=x/2` for even x and `(3x+1)/2` for odd x.
Its parity word records the **input** parity at each step. For an odd source
`S>=1`, write its odd states as x_j, exponents `e_j=v2(3x_j+1)>=1`, and

```text
E_0=0, E_j=sum_{t<j} e_t, alpha=log_2 3,
f_j=floor(j alpha), a_j=f_j-E_j, b_j=f_(j+1)-f_j in {1,2}.
```

An entire odd block is `1 0^(e_j-1)`; after it the next input is odd. A
coefficient-safe q-complete prefix means `3^(#ones)>2^L` at every nonempty
full prefix, equivalently `a_j>=0` at its odd endpoints. The minimum
coefficient in an odd block is at one of its endpoints. Equality of
nontrivial powers of 2 and 3 never occurs.

Put `Y_j=2^E_j x_j/3^j`. Exact affine induction gives

```text
Y_q = S + beta_q,
beta_q = sum_{j<q} 2^E_j/3^(j+1) <= q/3,
Y_(j+1)=Y_j(1+1/(3x_j)).
```

Choose **any** integer `K>=2` with `2^K>=3Y_q`. For finite purposes
`K=max(2,ceil(log_2(3S+q)))` suffices. K may depend on q.

Every infinite positive permanent-safe orbit is injective: a repetition
would force eventual periodicity, but a positive periodic segment has affine
multiplier less than one, since its correction B is positive and
`(2^L-3^q)x=B>0`. Repeating that segment would eventually violate safety of
the whole word. In a finite theorem, distinctness is an explicit hypothesis,
not a conclusion from finite safety.

P125 follows directly by induction: when two integers have the same parity,
one step divides their difference by two and multiplies by an odd number.
Their first n parity bits agree iff they are congruent modulo `2^n`.
Consequently distinct positive states strictly below `2^n` have distinct
length-n factors. This is the ordinary-integer input absent in a formal or
merely 2-adic word.

## 3. P252 — pure intervals and simultaneous CAP

Let sigma have ones at f_j (j>=0). Equivalently, with `gamma=1/alpha`,

```text
sigma_t=ceil((t+1)gamma)-ceil(t gamma), t>=0.
```

The equivalence follows by counting integers j in
`[t/alpha,(t+1)/alpha)`. A length-n factor is determined by the fractional
part of t gamma and the cut points `0,-gamma,...,-n gamma` modulo one.
The cut at zero is the circle boundary; there are at most n+1 intervals.
With the ceiling convention every boundary takes one of its adjacent
one-sided values. No isolated additional factor appears. Thus sigma has
at most n+1 factors of length n. This elementary partition argument, not a
finite complexity measurement, is the input used below.

Since `a_(j+1)-a_j=b_j-e_j<=1`, split the odd indices at every nonzero
defect change. In a run of constant defect r starting at odd index p:

- a zero change follows the corresponding mechanical segment;
- an up-change is necessarily `b_j=2,e_j=1`, deleting its final zero;
- a down-change of d has `e_j=b_j+d`, adding d trailing zeros. Exclude
  those d zeros from the pure interval.

Write the resulting intervals as `(r_i,ell_i,s_i)`, with full start
`s_i=E_p`. Their words are exactly
`sigma[f_p:f_p+ell_i]`. Include the possibly empty final interval at q.
Intervals never overlap, and the excluded extra zeros are not counted.
This construction has no finite terminal-one-to-zero substitution, so
P141's extra terminal `+1` is not being discarded.

At an odd input of height r, its coefficient is `2^(r+theta_j)<2^(r+1)`,
where `0<=theta_j<1`. The largest coefficient within the following pure
segment is at most `(3/2)` times that coefficient. At every pure input,
the partial normalized value is at most Y_q. Therefore

```text
0 < x_t < 3*2^r Y_q <= 2^(r+K).
```

For every integer h>=0 put n=h+K. All length-n windows wholly inside pure
intervals with `r_i<=h` start at distinct positive states below `2^n`.
P125 makes their factors distinct, but all lie in sigma's n+1-factor
language. Hence, simultaneously for **all h**, including h>max r_i,

```text
sum_{i:r_i<=h} max(ell_i-h-K+1,0) <= h+K+1.             (CAP)
```

Set `H=max a_j`, `delta_i=max(ell_i-r_i-K+1,0)`. CAP at h=r_i gives
`delta_i<=r_i+K+1`. Interval i contributes the triangle
`delta_i+(delta_i-1)+...+1` as h runs from r_i to r_i+delta_i-1.
That support ends at most at `2H+K`. Summing CAP through this height yields

```text
sum_i delta_i(delta_i+1)
  <= (2H+K+1)(2H+3K+2) = M(H,K).                       (ENERGY)
```

For J intervals, `ell_i<=r_i+K-1+delta_i` and Cauchy--Schwarz give

```text
sum ell_i <= sum r_i +(K-1)J+sqrt(J M(H,K)).
```

This uses the capacity **jointly** across intervals. Separate bounds on
each interval do not imply CAP; the tests include abstract counterexamples
to that replacement and nonzero triangular-energy examples.

## 4. P253 — downward variation and its scope

Define `D=sum_{j<q} max(a_j-a_(j+1),0)`; D in this section is neither the
cycle denominator nor the shifted affine correction. Up-moves are unit
moves, so their number is `a_q+D<=H+D`. The number of down-changes is at
most D. Consequently

```text
J <= H+2D+1 = J0,
sum r_i <= H(H+1)/2+2HD,
sum ell_i+D=E_q.
```

For the second inequality, every height 0,...,H is attained, since a_0=0
and upward jumps have size one. Charge each first visit its height; there
are at most 2D extra intervals, each of height at most H.

Substitution in ENERGY and `q alpha=E_q+a_q+theta_q<E_q+H+1` proves

```text
q alpha < H(H+1)/2+2HD+(K-1)(H+2D+1)
          +sqrt((H+2D+1)(2H+K+1)(2H+3K+2))+D+H+1.      (VAR)
```

The finite verifier checks the stronger intermediate assertion about E_q:
if `R=E_q-[H(H+1)/2+2HD+(K-1)J0+D]` is positive, then
`R^2<=J0 M`. No rounded logarithm or square root decides acceptance.

For a positive infinite permanent-safe orbit, P221 makes Y_infinity finite,
so a single fixed K works for every q. Injectivity implies x_j tends to
infinity. Since `x_j/Y_j=2^(a_j+theta_j)`, **a_j and H_q tend to infinity**.
If `H_q=o(sqrt(q))`, then

```text
liminf_{q->infinity} H_q D_q/q >= alpha/2.               (VAR-INF)
```

To check the errors rigorously, take any subsequence on which `H D/q` is
bounded. On it `D/q ->0` because H tends to infinity, and `H^2/q ->0` by
hypothesis. With fixed K the square-root error divided by q has square
`O(H^3/q^2+H^2D/q^2+H^2/q^2)`, which tends to zero. All other terms except
2HD are o(q). Divide VAR by q; no subsequence with limiting HD/q<alpha/2
can remain. If no bounded subsequence exists, the conclusion is automatic.
This is a necessary variation cost, not a contradiction.

## 5. P254 — monotone defect and the square-root constant

Assume an infinite positive permanent-safe orbit has nondecreasing a_j
from its odd source. Then D=0,H=a_q, and VAR simplifies to

```text
q alpha < a_q(a_q+1)/2 + K(a_q+1)
          +sqrt((a_q+1)(2a_q+K+1)(2a_q+3K+2)).          (MON)
```

Use the elementary choice `K=O_S(log q)` from Section 2; P221 is not
needed. On any subsequence with `a_q/sqrt(q)` bounded, the K term is o(q)
and the square-root term is o(q), including when a_q is small. Therefore

```text
liminf a_q/sqrt(q) >= sqrt(2 log_2 3).                  (MON-INF)
```

If the liminf were smaller, its bounded realizing subsequence would
contradict MON. No upper growth assumption on all subsequences is needed.

The leading constant is sharp **for this CAP relaxation**: abstract data
`r=0,...,H`, `ell_r=r+K-1` have zero CAP left side at every h and total
length `H(H+1)/2+(K-1)(H+1)`. Such data are not asserted to arise from an
ordinary orbit. Improving the leading constant requires another constraint,
not a stronger estimate of these same zero-capacity data. Nor has defect
monotonicity been proved for arbitrary safe or coefficient-maximal orbits.

## 6. P255 — the particular formal model has no ordinary positive source

The Phase 13/P251 recurrence is

```text
A_0=0;
A_(j+1)=A_j+1 iff b_j=2 and A_j<floor(sqrt(j+1)), else A_j;
e_j=b_j-(A_(j+1)-A_j), E_j=f_j-A_j.
```

There cannot be two consecutive b=1, since `3^2>2^3`. The square-root
target rises only at squares and is attained either at that square or the
next index. At j=1 the lag is explicit: A_1=0,A_2=1. For all j>=1 the
independent closed formula is

```text
A_j=floor(sqrt(j))-1_{j is a square and f_j-f_(j-1)=1}.
```

Thus A_j is nondecreasing, `floor(sqrt(j))-1<=A_j<=floor(sqrt(j))`,
and `A_j/sqrt(j)->1`. All full prefixes are safe and e_j is 1 or 2, as
proved in P251. If a positive integer realized this infinite word u, P254
would apply. But `1<sqrt(2 log_2 3)`, already from `3>2`, is an exact
contradiction. The finite prefix `110111111` carries a positive integer
to a positive odd integer, so w=`110111111u` is impossible too.

This excludes a specific formal model, not the permanent-safe language.
Its coherent odd 2-adic inverse source continues to exist; P255 says that
source is not a positive ordinary integer. P251's formal all-depth no-gain
statement and NG45's analytic-only counterexample remain true. Neither
full geodesicity nor H112 is being settled by this result.

### Finite repeat-and-split certificates

For any finite parity word W, suppose starts i<j share at least n bits,
then differ at a later witnessed position. A positive source realizing W
cannot have equal states at i and j: deterministic iteration would forbid
the later split. If its source is at most 2^B and its prefix affine data
are `(q_t,C_t)`, check the two exact inequalities

```text
3^q_i 2^B+C_i < 2^(i+n),
3^q_j 2^B+C_j < 2^(j+n).
```

Both distinct states would be below 2^n with equal n-bit parity, contrary
to P125. This certificate requires **no** assumption of an infinite
nonperiodic future, and does not trust CAP to deduce the eventual split.
It checks the split and both affine bounds directly.

For u, `beta_q<=4`: each summand is at most
`(2/3)2^(-floor(sqrt(j)))`, and
`sum_{m>=0}(2m+1)/2^m=6`. The search uses the loose bound `Y<=2^B+4`,
pure intervals and CAP to find a collision. The verifier instead uses the
closed square formula and reconstructs both actual affine numerators.

| B (bound S<=2^B) | n | i | j | common length | required full prefix |
|---|---|---|---|---|---|
| 8 | 19 | 51 | 95 | 21 | 117 |
| 16 | 32 | 222 | 259 | 34 | 294 |
| 32 | 57 | 553 | 617 | 79 | 697 |
| 64 | 107 | 1906 | 2137 | 112 | 2250 |
| 128 | 206 | 6838 | 7488 | 208 | 7697 |
| 256 | 399 | 26257 | 26657 | 400 | 27058 |
| 512 | 782 | 96451 | 99609 | 782 | 100392 |
| 1024 | 1543 | 386295 | 389455 | 1548 | 391004 |

The bounds refer to u's source, **not** the source before the finite
extension defining w. For B<=128 a direct canonical-residue computation
also exceeds 2^B. The infinite exclusion comes from MON-INF, not from
extrapolating these eight finite checks.

## 7. P256 — negative signed carry first occurs at q=22

For safe words d,a of the same q, with `L_d=L_a+k`, k>=1, and a common
positive integer endpoint, write

```text
S_d=2^k S_a+m,   m=(2^k B_a-B_d)/3^q in Z.
```

For q>=2 both words start `11`, so both sources are 3 modulo 4. Hence
k=1 forces `m=1 mod 4`, and k>=2 forces `m=3 mod 4`. Negative m is thus
at most -3 in the first case and at most -1 in the second. Every q-one
word has `B_a>=3^q-2^q` (its jth odd position is at least j). Therefore
negative carry requires

```text
B_d >= 5*3^q-4*2^q.                                   (NC)
```

For k=1 the slightly stronger `5*3^q-2*2^q` holds; NC is a valid common
lower bound. Safety implies the odd positions `p_j<=f_j`, so

```text
B_d <= Bmax(q)=sum_{j<q}2^f_j 3^(q-1-j).
```

There is no unequal-length safe pair for q=0 or 1. For each q=2,...,20,
the artifact records exact integers `Bmax(q)<5*3^q-4*2^q`, independently
reconstructed from positional sums. This covers **every** word in those
weights without a depth cutoff.

At q=21, with `P=3^21=10460353203`, the allowance is

```text
Bmax-5P+4*2^21=1726852096 < P/6.
```

Moving any odd position j>=1 left by at least one loses at least
`2^(f_j-1)3^(q-1-j)>P/12`; the strict inequality follows from
`2^f_j>3^j/2`. Two moved positions are impossible. Position zero cannot
move. With only one moved position and its predecessor unchanged, it must
be a mechanical gap of size two, moved exactly one left. The complete
list of moved indices is

```text
none, 2,4,6,7,9,11,12,14,16,18,19.
```

The final odd position remains f_20=31 and the safe full length is 32 or
33. Only `(k,m)=(1,-3),(2,-1)` need be retained: every other congruence-
compatible negative case has
`B_d>=9P-8*2^21>Bmax`. This includes k>=3, k=1 with m<=-7, and k>=2
with m<=-5. The 12*2*2=48 cases are therefore complete, not a sample.
All their candidate corrections `B_a=(B_d+mP)/2^k` fail to decode as a
binary word of length L_d-k and weight 21. The generator uses the
leading-parity recursion; the verifier solves the forced source residue,
iterates it literally, and recomputes the positional correction and weight.
It does not import that decoder or rely on a stored rejection flag.

At q=22 the following literal safe pair attains negative carry:

```text
d=1101101101101011010110110110110101
  (L,q,B)=(34,22,160921024637), S_d=29023002619
a=111111111111011101101011000100100
  (L,q,B)=(33,22,33388922905), S_a=14511501311
common endpoint y=53013941237
S_d=2*S_a-3, 2*B_a-B_d=-3*3^22.
```

This proves minimality in **q**, not in length, source height, or
lexicographic order. The target's exponents are all 1 or 2, but the
alternative has larger exponents, so P88's two-sided `{1,2}` injectivity
is not refuted. NG28's historical q=26 witness is preserved unchanged;
its false carry-positivity hypothesis remains `REFUTED`.

## 8. Finite acceptance, provenance, and independence

The generator constructs accelerated safe prefixes and partitions at
defect changes. The verifier starts with full shortcut iteration, removes
extra zeros segment by segment, and checks literal mechanical alignment,
strict state heights, interval arithmetic, and all declared levels.
It reconstructs all aggregate digests; stored derived values are not inputs
to proof decisions. The repeat verifier checks certificates directly and
requires the full eight-bound domain, types, schemas and no extra fields.
Ambiguous JSON, omitted cases, modified hypotheses, altered arithmetic,
wrong source/split/height data and proof-flag changes are tested for rejection.

The bounded ordinary sample is exactly the 2,048 odd S in [1,4095], with
at most 300 completed odd steps, stopping before a repeated state or
coefficient failure. It has 5,069 odd steps, 4,304 intervals and 30,060
checked levels. **All counted n-factors are absent in this sample**, so
these CAP checks must not be described as strong finite packing evidence.
The written P252 proof supplies the theorem; separate abstract unit tests
exercise nonzero capacity/energy and joint-versus-local failure. Eight
model repeat certificates exercise the nonvacuous integer rejection rule.

All six required families are retained (24 parameterized ordinary sources,
80 distinct words), with source167, source7, NG28's q=26 pair, NG32,
NG43's safe/unsafe pair and positive/negative cycle controls. Dependency
tests additionally retain P251/NG44/NG45 and the older paired controls.

The supplied ZIP SHA-256 is
`16b1f1c15421afbcb3c9753eba96335025a1996176781865538a4f3278b232f9`.
All seven supplied SHA256SUMS entries matched; the standalone note is
byte-identical to its ZIP member. Input member hashes:

```text
9d34671860b0cbe10af82da95083eff0e6a0f0aa9c8755b52576c07c46e01cad PROOF_AND_CODEX_ADDENDUM_JA.md
aedd70fa3939c58795a483cfc04860b913121ddebc9a08a9a0a8367c4d53f344 audit_followup.py
b893decb2e208f0f9999f954d78cf3933ef09cd206ba598d126bfe5f1d85f8bd audit_results.json
33016ebb4e2a424ac4088a3f1a58b16930a00d96f6c1c4ccb10ccc5cd7cdca06 capacity_checks.json
6284495dc02691d3ac8cee5a88ebb8a03324a4a2e3336baf42b9b59d906d4d9d check_capacity.py
a5c2545b20916f78a14e440d26fbcabbc3c2b3ea7783a81c0118f61d3c0f55dc verification.json
45f857ff6ead501e7d93033aa64495daed5dbb32dd158d08a456f6f0890f57af verify_followup.py
```

Supplied scripts were read as untrusted proposals, not executed as an
acceptance authority. New repository outputs are generated by the local
implementation and independently checked. Reproduction commands, actual
test counts, commit and the accepted manifest hash are in
[`PHASE42_RUN_RESULTS.md`](../../../PHASE42_RUN_RESULTS.md) and the
[`experiment contract`](../../experiments/phase42-mechanical-capacity.json).

## What this result does not prove

P255 excludes u and its finite extension w, not other monotone words with
larger defect, not oscillating defects, and not all H112 geodesics. VAR-INF
permits sufficiently large downward variation. No theorem forces the actual
defect of a coefficient-maximal positive source to be monotone or to stay
below P254's threshold. The q=22 carry result demonstrates the need for
signed arithmetic; it does not force a useful ancestor at every large q.
No effective last zero-lift time, general descent theorem, positive-cycle
exclusion, or solution of the Collatz conjecture is supplied.

The next useful question is to connect ordinary lifts, source order and
ancestral minimality to an upper defect/variation budget contradicting VAR
or MON. Neither another depth-only model scan nor re-proving the coherent
2-adic source can provide that missing bridge.
