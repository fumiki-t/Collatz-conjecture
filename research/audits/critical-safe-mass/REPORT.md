# Critical safe-word mass — independent mathematical audit

2026-09-10; base `df6c063b7428b768b4ea071dd7cea1a5a218220c`.
Unnumbered supplement; latest numbered phase remains 44.
`proves_collatz=false`; H112/H72/H89/H133 and EXT08 retain `OPEN` status.

## 1. Decision, provenance and conventions

Accept the proposal with explicit domain and verification refinements, not
as a Collatz solution. P271 is the generating function and two-sided critical
word bound; P272 is the translated source/filter mass; P273 is the renewal
consequence. E63 records finite arithmetic. NG49 rejects the mass-only
emptiness inference. No prior theorem is retracted or renumbered.

The supplied ZIP SHA-256 is
`18a55d177dea20c2cf5ea97ffb702e705ddc5e373af556895205f7b6568c861c`.
All seven member hashes were validated. Notes, code and local reports were
read before executing the acceptance computation. The supplied evidence
hash is `59320323891bb32dafe58d4e433afb7a6db41b3e532a6e10cd34e1c37e689a98`.
Reusing audited supplied implementations does not constitute independent
authorship. The generator/verifier use logically different reconstructions.
The infinite proofs below are written mathematics, not proof-assistant output.

Use the shortcut map T(x)=x/2 for even x, (3x+1)/2 for odd x. Bits are input
parities; length n and weight q give coefficient 3^q/2^n. Define

    alpha=log_2(3), theta=1/alpha, rho=H_2(theta), mu=2^rho.

Here H_2 is binary entropy, and rho is the boundary exponent of P220.
We never use a decimal approximation to decide a certificate. Both alpha
and theta are irrational by unique factorization; hence a nonempty word
never has coefficient exactly one. Let U_0=1, V_0=0, and for n>=1:

* U_n counts words whose every nonempty prefix has coefficient >1;
* V_n=sum_(k:3^k>2^n) binomial(n,k), imposing only terminal positivity.

These are not the P77 first-upcrossing code, odd-time defects a_q, or
P228/P269 capacity arrays. U_26=1037374 is the already known safe frontier;
the new result is its all-depth critical generating-function control.

## 2. P271: exact generating function, including mean ties

Give one a real increment alpha-1, and zero an increment -1. For a fixed
finite set of n distinct labels and a fixed coloring, every nonempty subset
has nonzero sum: alpha q-m=0 would contradict unique factorization or
nonemptiness. There are finitely many such subsets, so a sufficiently small
perturbation of the n labeled increments preserves **all** subset-sum signs.
Also avoid the finitely many proper hyperplanes on which two disjoint
nonempty subsets have equal averages. This is possible in every small ball.
Perturbations may depend on n and the coloring; no infinite-word perturbation,
randomness, symmetry or continuous increment distribution is assumed.

For a permutation of the labels, require each of its cycles to have positive
sum. In a cycle of size k and total s, form k centered prefix values
`k S_j-j s`, j=0,...,k-1. They are distinct: a tie would equate the averages
of a nonempty segment and its nonempty complementary segment. Rotate the
cycle to start at the unique minimum. Every proper internal point then lies
strictly above its chord. Order the rotated cycles by increasing average.
Their averages are distinct and positive, and their chords form the lower
convex hull of the concatenated path. All its nonempty partial sums are >0.

Conversely, for any positive-partial-sum labeled linear order, the first
lower-hull slope is min_j S_j/j>0. Later slopes strictly increase; a tied
internal chord would again give two disjoint subsets with equal averages.
Each hull face therefore recovers one rotated cycle, with its cyclic order.
The hull slopes recover the ordering. These maps are inverse. Crucially,
both the linear positivity condition and the cycle positivity condition
depend only on subset-sum signs, so their counts agree before perturbation.
We do not claim the original unperturbed hull has unique faces or rotations:
the two-one example already has tied centered values 0,0.

Sum over all label colorings. Positive linear orders number n! U_n. For
cycle counts m_k with sum k m_k=n, the cycle-index count, including the
V_k positive colorings of a k-cycle, divided by n!, is

    product_k V_k^m_k/(k^m_k m_k!).

Consequently, as a formal power series,

    sum_(n>=0) U_n z^n = exp(sum_(k>=1) V_k z^k/k),       (GF)
    n U_n = sum_(k=1..n) V_k U_(n-k).                    (REC)

The usual labeled cycle count includes the factorial for indistinguishable
cycles of the same size; omitting it would invalidate GF. This is a
classical cycle/convex-envelope method, not a new general identity.

## 3. Uniform binomial upper and lower bounds

We prove for every integer n>=1:

    mu^n/(24 sqrt(n)) <= V_n <=4 mu^n/sqrt(n).           (BIN)

Put t=theta/(1-theta)>1, v=theta(1-theta). The auxiliary distribution
K~Bin(n,theta) gives the algebraic coefficient identity

    binomial(n,k)=mu^n t^(-(k-theta*n)) Pr(K=k).

This distribution is only a counting device; actual Collatz parity bits
are never assumed independent. Fourier inversion gives

    Pr(K=k) <= (1/(2pi)) integral_(-pi..pi)
                        |1-theta+theta exp(iu)|^n du
              <= sqrt(pi)/(2 sqrt(2 n v)),

because the squared modulus is `1-4v sin^2(u/2)`, `1-x<=exp(-x)`, and
concavity gives `sin(|u|/2)>=|u|/pi`. Extend the resulting Gaussian integral
to the full real line. Since theta*n is not an integer, the geometric tail
over k>theta*n is strictly less than `t/(t-1)=theta/(2theta-1)`.

Exact powers give `63/100<theta<631/1000`. On this interval v is at least
232839/10^6, while theta/(2theta-1) is at most 63/26. Thus the square of
the atom/geometric constant is at most

    (22/7)/(8*(232839/10^6))*(63/26)^2 <16.

For completeness, pi<22/7 follows internally from the positive integral
`integral_0^1 x^4(1-x)^4/(1+x^2) dx=22/7-pi`; polynomial division and
`integral_0^1 4/(1+x^2) dx=pi` verify the identity. E63's tests check the
polynomial identity, not a floating-point quadrature. This proves the upper
bound in BIN uniformly, including n=1.

For the lower bound, Var(K)<=n/4, so Chebyshev puts at least 3/4 of the
mass at distance <sqrt(n) from its mean. That open interval has at most
3sqrt(n) integers, so a largest atom is at least 1/(4sqrt(n)). The binomial
atom ratio shows its unique mode is m=floor((n+1)theta). The first accepted
integer k=ceil(n theta) is either m or m+1. In the latter case m=floor(n theta)
and the ratio from m to k is at least

    n theta/(n theta+1) >=theta/(theta+1)>1/3.

Hence Pr(K=k)>=1/(12sqrt(n)). Also the tilt at k is greater than
`t^-1=(1-theta)/theta>1/2`, using theta<2/3 (equivalently 8<9).
The first tail term proves the lower bound in BIN. This accounts for
rounding at every n, rather than assuming an asymptotic constant exists.

## 4. Exact critical sum and coefficient order

Let `F=sum_(n>=1) V_n/(n mu^n)`. BIN implies F<infinity. By nonnegative
monotone convergence in GF,

    sum_(n>=0) U_n mu^-n=exp(F).

Take u=19317/10000. Entropy decreases on (1/2,1), and

    10^7000 >19317^1000 *631^631 *369^369

proves `u<mu`. E63 independently reconstructs all V_n for 1<=n<=512 and
the rational sum `F512plus=sum V_n/(n u^n)`. The analytic remainder obeys

    sum_(n>512) V_n/(n mu^n)
       <=4 sum_(n>512) n^(-3/2) <8/sqrt(512)<4/11.

The strict sum/integral comparison uses a decreasing function; its final
square-root comparison is the integer inequality 121<128. The exact
certificate verifies

    F512plus+4/11 <219/100 <263/120 <2 log(3).

The final strict inequality follows from the first three positive terms
of the atanh series, `log 3>1+1/12+1/80=263/240`. Therefore

    sum_(n>=0) U_n mu^-n <9.                             (Z9)

For explicit coefficient order set f_n=V_n/(n mu^n), with f_0=0 and
sum f_n=F. In an r-fold convolution contributing at n, some coordinate is
at least n/r. Choose it in at most r ways; bound its f by
4 r^(3/2)n^(-3/2), and remove the sum constraint on the other coordinates.
Thus `(f^{*r})_n<=4 r^(5/2) F^(r-1)n^(-3/2)`, also when r>n (left side 0).
Expanding GF and using r^(5/2)<=r^3 gives

    U_n mu^-n <=4 exp(F)(F^2+3F+1)n^(-3/2)
               <446 n^(-3/2),

since `36*((219/100)^2+3*(219/100)+1)=1112949/2500<446`.
The k=n term in REC gives U_n>=V_n/n. We obtain, for all n>=1,

    mu^n/(24 n^(3/2)) <=U_n<446 mu^n/n^(3/2).            (ORDER)

In particular U_n=Theta(mu^n n^(-3/2)). No convergence of the normalized
coefficient ratio is asserted. The finite verifier also uses
nu=1933/1000>mu, certified by `1933^100 63^63 37^37>10^500`, for stronger
two-sided envelopes through 512. **These strengthened rational envelopes
are finite only**: replacing mu by a fixed smaller/larger rational at all
depths would conflict with ORDER's exponential growth rate.

## 5. P272: translated mass, finite filter and its exact boundary

Let Ssafe be the set of all positive ordinary integer sources whose every
nonempty prefix is coefficient-safe; existence is not assumed. For each
fixed integer b>=0, define

    C_b={x integer >b: x is safe through floor(log_2(x-b)) steps}.

Each length-n parity word specifies exactly one residue modulo 2^n (P125,
or direct parity induction). Thus in `[b+2^n,b+2^(n+1))`, **exactly U_n**
points belong to C_b. For n=0 the condition is empty and the one point is
b+1. This shell partition and x-b>=2^n give

    sum_(x in Ssafe,x>b) (x-b)^(-rho)
      <=sum_(x in C_b) (x-b)^(-rho) <=sum U_n mu^-n <9.  (MASS)

The constant is independent of b. C_b has at least one point in every
shell, so this is a nonvacuous infinite-set statement even if Ssafe is empty.
For b=0 the actual finite-safe sources 2^k-1 supply an explicit infinite
subfamily, without being asserted permanently safe.

For integer X>=2 and any integer-translated interval of length X, choose
n=ceil(log_2 X). Each n-bit residue occurs at most once, and every permanent
source passes that n-bit test. ORDER and mu<2 therefore imply

    # (Ssafe intersect I) <=U_n
       <892 X^rho/(log_2 X)^(3/2).                      (COUNT)

We do not apply COUNT unconditionally to C_b in arbitrary windows: the
length imposed at a C_b point varies with its distance to b. Nor do we
apply it to all states of an orbit, all collision-free sets, or all finite
distinct paths. Unlike P220, this counts the permanent-safe source class
across possible orbits, but **not multiplicity of addresses** for P80.

For K>=2, the same shell argument gives the tail, valid also for C_b,

    sum_(x>=b+2^K) (x-b)^(-rho)<892/sqrt(K-1),

with 9 available as a second bound. For fixed b and 0<s<rho, lower-bounding
each shell by `U_n 2^(-(n+1)s)` and using ORDER proves divergence. For s<=0
the infinitely many terms are at least one; for s>rho use termwise comparison
with MASS. The real convergence boundary of this filter's Dirichlet series
is **exactly rho, and convergence holds at rho**. This does not rule out
stronger bounds for its all-depth subset Ssafe using additional arithmetic.

## 6. P273: renewal boundary growth, with an explicit normalization option

On a P222 positive nonperiodic permanent-safe tail, P77 gives boundaries
`S_0<S_1<...`, each of which is itself permanently safe. For i>=2, apply
COUNT to `[1,S_i+1)`, containing at least i+1 such points. As S_i>=i+1,

    S_i >(i/892)^(1/rho) (log_2 i)^(3/(2rho)).           (RENEW)

Let q_i be the odd-time index of that boundary, and use the Phase 12 exact
normalization `S_i=2^(a_(q_i)+vartheta_(q_i))Y_(q_i)`, 0<=vartheta<1.
With Y_infinity finite this gives

    a_(q_i) > log_2(i)/rho +3 log_2(log_2 i)/(2rho)
               -log_2(892)/rho -log_2(2Y_infinity).     (DEFECT)

P221 is one existing route to finite Y_infinity. **The current main gives
another:** all input prefixes of a nonperiodic positive orbit are distinct,
so P270 bounds their increasing normalized products by 256S_0. Monotone
convergence yields `Y_infinity<=256S_0`, not a strict inequality merely
by taking limits. Thus replacing the last term by `-log_2(512S_0)` is a
valid explicit weaker DEFECT bound. No new external theorem is required.

MASS also gives sum_i S_i^(-rho)<9. These are pointwise conditions on the
**renewal index i**, not on every intervening odd time q. P234 remains valid;
this supplement strengthens its boundary rate, not its conclusion to a
nonperiodic exclusion or a finite last-small-defect time.

## 7. NG49 and retained falsifiers

The infinite ordinary set P={2^k:k>=1} satisfies the translated mass bound
for every b>=0. If 2^k0 is its first point above b, the successive distances
are at least 2^j (j=0,1,...). Therefore its mass is at most
`sum mu^-j=mu/(mu-1)<3<9`, since mu>u>3/2. All its points fail safety at
their first step. This is a **set-theoretic countermodel** to the hypothesis
that the mass condition alone forces a positive integer set finite or empty;
it is not a permanent-safe orbit or a Collatz counterexample. No smallest
infinite countermodel under a specified ordering is claimed.

The even source 2 and source 1's first crossing at step 2 guard against
calling shell-filter membership permanent safety. The unperturbed word 11
guards against assuming unique centered minima before tie removal.
NG45's formal word is independently rebuilt; the 7/703 NG46 all-length
potentials are rechecked. NG48 and the other prior counterexamples remain
unchanged. All six mandatory families receive finite word/path safety tests;
passing any such finite test is never treated as a permanent source.
The old Phase 41 formal artifact's positive-source annotation is a historical
snapshot; it does not undo P255's subsequent ordinary-source exclusion.

## 8. Literature and independence boundary

Abramson and Pitman, *Concave Majorants of Random Walks and Related Poisson
Processes*, arXiv:1011.3262v2 (2011), is classical context. We checked
[Theorem 1, Lemma 2 and the Section 2 construction](https://arxiv.org/html/1011.3262v2#S2)
and the equal-mean discussion. Their concave-majorant orientation is reversed
here to a convex minorant. Section 2's genericity is not automatic for two
increments; our finite sign-preserving perturbation supplies what our
specialization needs. No external theorem from that paper is a proof input,
and no general-identity or literature-wide novelty is claimed.

The generator uses surviving-prefix DP, binomial sums and literal positive
iteration. The verifier uses Pascal/cycle recurrence, all binary words through
18, positional affine residues, and cycle-to-hull/inverse checks through six
labels. We additionally verify **every** subset sign and disjoint-subset mean
for every tested coloring. This finite construction supports the implementation
but is not a substitute for the all-n argument in Section 2.

E63 records 513 count rows, 524287 words, 50362 permutation/color cases,
6327 positive cases and 59 original nonzero interval queries. Added evidence
has 55 full filter shells, 48 family words and six pinned older file hashes.
Schema checks reject numeric type coercion, scope changes and duplicate keys.
Commands, tests and hashes are in the [run record](../../../CRITICAL_SAFE_MASS_RUN_RESULTS.md).

## What this result does not prove

No permanent-safe positive source is constructed or excluded. Summability,
even at the sharp filter exponent and uniformly under translation, is not
emptiness. COUNT does not apply to arbitrary whole trajectories or address
multiplicity. Neither an improving ancestor, a source/lift-linked lower mass
bound, H112/H72/H89/H133 nor an arbitrary-area positive-cycle exclusion is
proved. Positive cycles remain separate: their contracting total coefficient
prevents any source on them being permanently coefficient-safe.

Next seek actual integer ancestors or an orbit-forced supply of **distinct
permanent-safe sources** contradicting MASS/COUNT. Such a supply theorem is
absent. More count depth or a random-parity heuristic would not fill this gap.
