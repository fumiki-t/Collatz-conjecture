# Substitution arithmetic: independent audit

Audited 2026-09-13 against main `40888313b01bffbe198e110736404549683bedc5`.
Proposal: [unaltered supplied proof](PROPOSAL.md); [request](REQUEST.md).
Canonical labels are in [the ledger](../../../docs/CLAIMS_LEDGER.md).
P285/P286 below are written mathematical derivations, not proof-assistant
formalizations. E66 is their explicitly bounded arithmetic audit.
No EXT08, density theorem, primitivity, or presumed orbit coverage is used.
`proves_collatz=false`.

## 1. Exact statement and conventions

On the 2-adic integers use the shortcut map
`T(z)=z/2` for even z and `(3z+1)/2` for odd z. Write its full parity bits
as w_n, and h(n)=sum_{i<n}w_i. This is not the accelerated odd-only map.
Every infinite binary word has the unique inverse source

\[
 \Phi_2(w)=-\sum_{n\ge0}w_n2^n/3^{h(n)+1}\in\mathbb Z_2.
\]

This follows directly by solving the length-N affine congruence modulo
2^N; the series converges because its n-th summand has valuation at least n.
It agrees with the repository's P125 convention, including negative inputs.

**P285 (U1).** For every r>=2, every binary substitution
sigma(0)=u, sigma(1)=v with |u|=|v|=r, and every one-sided fixed word
w=sigma(w) which is **not ultimately periodic**, Phi_2(w) is not rational.
Consequently it is not any ordinary integer, positive or negative. Every
shift of w, and every arbitrary finite prefix followed by such a shift,
also has irrational inverse source. No coding from a larger alphabet is
included. Here and below “aperiodic” means not ultimately periodic.

**P286 (U2).** For each such fixed word w there are c_w>0, C_w and N_w
such that its canonical residue 0<=r_N<2^N satisfies
`r_N >= 2^(c_w N-C_w)` for N>=N_w. Equivalently, a positive ordinary
integer S matching N initial bits satisfies
`N <= C'_w(1+log_2(S+1))`. Constants depend on this fixed substitution and
word. The finite certificates give explicit bounds only for the four
declared examples, not a uniform constant over all substitutions.

## 2. Rational series forces eventual periodicity

Put F(x,y)=sum w_n x^n y^{h(n)} and K(x,y)=sum x^n y^{h(n)}.
For any nonzero rational b, F(x,b) is rational in x if and only if w is
ultimately periodic. The reverse direction groups a periodic tail into
blocks of length p and weight b^q, giving a geometric denominator
`1-x^p b^q`.

For the forward direction, let c_n=w_n b^{h(n)}. A rational series has an
eventual constant-coefficient recurrence of some order d>=1. For all
sufficiently large n normalize the state (c_n,...,c_{n+d-1}) by b^{h(n)}.
Each coordinate is 0 or one of 1,b,...,b^{d-1}, so there are finitely many
states. The first coordinate is exactly w_n. The recurrence predicts the
next normalized last coordinate, then division by b^{w_n} uniquely updates
the state. A deterministic finite state trajectory is eventually periodic,
hence so is w_n. Polynomial series have only finitely many ones and satisfy
the conclusion directly. This argument works also at b=1 and b=-1.

It follows that F(x,y) is not in Q(y)(x): otherwise specialize at a
nonzero rational b avoiding the finitely many roots where a proposed
denominator polynomial in x becomes identically zero. The preceding lemma
would make w ultimately periodic. This step needs no complex-analytic theorem.

## 3. Functional equation and unit leading coefficient

Let q_0=|u|_1, q_1=|v|_1, delta=q_1-q_0, eta=|delta|. For a finite word a,
let A_a(x,y)=sum_{j:a_j=1}x^j y^{|a_{<j}|_1}. Set A_0=A_u, A_1=A_v and

\[
 X=x^r y^{q_0},\quad Y=y^\delta,\quad
 C=1-X,\quad B=(1-X)A_1-(1-XY)A_0.
\]

Telescoping gives `(1-x)K=1+x(y-1)F`. Substitution block summation, followed
by this identity at (X,Y), gives exactly

\[
 C(x,y)F(x,y)=A_0(x,y)+B(x,y)F(X,Y).
\]

For a finite input a of length N and H ones, the correct boundary version is

\[
 C A_{\sigma(a)}=A_0(1-X^NY^H)+B A_a(X,Y).
\]

The boundary term must not be omitted. Although delta can be negative,
XY=x^r y^{q_1}; all polynomials C,A_0,B have nonnegative exponents. Each
substituted monomial has y exponent q_0 times its zero count plus q_1 times
its one count, also nonnegative.

An aperiodic fixed word has u!=v. If q_1-q_0=r, the images are 0^r and
1^r and each fixed word is constant; if delta=-r, the first symbol is
flipped and there is no one-sided fixed word. Thus eta<r.
Let j_0 be the first position where u and v differ. In A_1-A_0 the lowest
x term is precisely `+/- x^j_0 y^e`; the two remaining terms in B have
x degree at least r. Therefore for v_2(x)>0 and v_2(y)=0,

\[
 v_2(C)=0,\qquad v_2(B)=j_0v_2(x).
\]

In particular B never vanishes at any tower point below. With d_r=2r-1,
all coordinate degrees of C,A_0,B are at most d_r and their coefficient
1-norms are bounded by 2,r,4r respectively. For B, the largest possible y
degree is q_0+q_1-1<=2r-1. E66 independently checks the full finite identity,
these bounds, and the leading monomial for all images of lengths 2,3,4.

## 4. Rational evaluation tower and ordinary height

Start x_0=2,y_0=1/3 and set x_{k+1}=x_k^r y_k^{q_0}, y_{k+1}=y_k^delta.
Writing p_k=|sigma^k(0)|_1 (p_0=0), induction gives

\[
 x_k=2^{r^k}/3^{p_k},\quad y_k=3^{-\delta^k},\quad
 p_{k+1}=rp_k+q_0\delta^k=q_0r^k+\delta p_k,
 \qquad 0\le p_k\le r^k.
\]

The second recurrence also follows by counting the two types of blocks;
the difference of the image populations is delta^k. Thus v_2(x_k)=r^k,
y_k is a unit, and the ordinary reduced rational heights satisfy
H(x_k)<=3^{r^k}, H(y_k)<=3^{eta^k}. Use 0^0=1 at k=0.

Suppose F(x_0,y_0)=U_0/V_0 is rational with integers V_0!=0. Common
bihomogenization of degree d_r in each variable gives integer
evaluations Atilde,Btilde,Ctilde with a common **odd** denominator. Define

\[
 U_{k+1}=\widetilde C_kU_k-\widetilde A_{0,k}V_k,
 \qquad V_{k+1}=\widetilde B_kV_k.
\]

Then V_k!=0 and U_k/V_k=F(x_k,y_k). For M_k=max(|U_k|,|V_k|),

\[
 M_k\le M_0(4r)^k3^{d_r(s_r(k)+s_\eta(k))},
 \qquad s_t(k)=\sum_{j=0}^{k-1}t^j.
\]

Indeed max(2+r,4r)=4r controls the numerator/denominator update. Since
d_r/(r-1)<=3 and eta<r, the exponent is at most 3r^k+o(r^k).
This is an ordinary absolute-value bound for finite integers, **not** an
identification of a real infinite sum with its 2-adic value.

## 5. Auxiliary existence, specialization, nonvanishing

There are 22 coefficients of P,Q in Q(y)[x] of x degree <=10, and only
21 homogeneous conditions making R=P+QF vanish in x degrees 0,...,20.
Take any nonzero solution, clear denominators, and divide the common
Q[y] content of all coefficients of P and Q; clear any remaining numerical
denominators. Now P,Q are integral and primitive with respect to y.
Q cannot be zero (a degree-10 P vanishing to order 21 would be zero), and
R is not identically zero by Section 2. Let d>=21 be its first nonzero
x degree, with coefficient R_d(y) in Z[y].

The specialization audit is essential:

- If eta>=2, the rational y_k are distinct. Hence R_d(y_k)!=0 eventually.
  Clearing its odd denominator bounds its numerator by
  `||R_d||_1 3^(deg_y(R_d) eta^k)`. Its 2-adic valuation nu_k is nonnegative
  and O(eta^k+1)=o(r^k). Every coefficient R_l(y_k) is 2-adically integral.
  Thus eventually nu_k<r^k, so the first term dominates all later terms.
- If eta is 0 or 1, y_k belongs to the finite set {1,1/3,3}. Primitivity
  implies P(x,b),Q(x,b) are not both identically zero at each of these b.
  If Q(x,b)=0 then the nonzero P suffices; otherwise Section 2 prevents
  P(x,b)+Q(x,b)F(x,b) from vanishing identically. Its first nonzero degree
  d_b>=21 and valuation nu_b are fixed. For this finite set of b they are
  bounded, and the same first-term domination holds for large k.

In both cases R(x_k,y_k)!=0 and v_2(R(x_k,y_k))>=21r^k eventually.
Common-content removal is not a substitute for the second case: both the
nonzero specialization and rational-series lemma are required. In the four
finite examples we verify the actual x^21 leading polynomial and its
valuation at each certificate's level, with no asymptotic substitution.

## 6. Integer contradiction: proof of P285

Let d_y be the maximum y degree of P,Q, C_aux their combined coefficient
1-norm, and D_k the common odd denominator from their degree-(10,d_y)
homogenization. The integer

\[
 Z_k=D_k\{V_kP(x_k,y_k)+U_kQ(x_k,y_k)\}
     =D_kV_kR(x_k,y_k)
\]

is nonzero and divisible by 2^{21r^k}. On the other hand,

\[
 |Z_k|\le C_{aux}M_0(4r)^k
 3^{10r^k+d_rs_r(k)+d_rs_\eta(k)+d_y\eta^k}
 \le 3^{13r^k+o(r^k)}.
\]

The exact comparison is 2^21=2097152 >1594323=3^13. To avoid a hidden
floating decision, choose any real epsilon>0 sufficiently small that
3^{13+epsilon}<2^21, whose existence follows from this strict integer gap
and continuity. For all sufficiently large k the bound is smaller than
2^{21r^k}, impossible for a nonzero divisible integer. This proves U1.
Shifts and finite prefixes follow because every finite parity affine map
and its inverse preserve rationality; no real/2-adic identification is used.

## 7. Finite agreement and quantifiers: proof of P286

If a positive integer S matches the first N bits, then
v_2(F(2,1/3)-(-3S))>=N by the inverse parity congruence. Start the same
rational tower with U_0=-3S,V_0=1; it need not equal F. The exact linear
update gives, at level k,

\[
 v_2\big(F(x_k,y_k)-U_k/V_k\big)
 \ge N-j_0s_r(k).
\]

The loss cannot be dropped. Denominators V_k are nonzero independently of
U_0. Also Q(x_k,y_k) is 2-adically integral. Section 5 gives constants k_0,D
depending only on w, with nonzero true residual of valuation at most D r^k
and at least 21r^k for k>=k_0. This upper bound uses the actual d, or the
finite collection d_b, **not an unjustified assumption d=21**.
Thus N>j_0s_r(k)+D r^k implies that the approximate residual is nonzero
with the same valuation. The integer height bound of Section 6 still holds,
now with M_0=3S.

Fix a positive margin less than log_2(2^21/3^13). Absorb all word-dependent
o(r^k) terms and C_aux into k_0 and a constant. There is a constant M>0
such that r^k>=M(1+log_2(S+1)), k>=k_0 forces the nonzero integer's upper
bound below 2^{21r^k}. Choose the least such k; its scale is at most a
word-dependent constant times (1+log_2(S+1)), since consecutive scales
have ratio r. Since s_r(k)<=r^k/(r-1), matching more than another fixed
constant times (1+log_2(S+1)) bits yields the contradiction. Small k and
small N are absorbed by increasing the constants. This proves the claimed
finite-match bound with its quantifiers.

For large N the canonical residue is nonzero (w contains a 1), so apply
the bound to S=r_N, then reduce the positive exponent constant/adjust the
additive constant to obtain P286. When r_N=0 at short prefixes, no
positive-source bound is claimed.

For E66, d is exactly 21, nu=v_2(R_21(y_k))<m=r^k, and each row checks

\[
 2^{21m+\nu}>3\,2^{B_0}C_{aux}(4r)^k3^E,\quad
 E=10m+d_r(s_r+s_\eta)+d_y\eta^k,\quad
 N=21m+\nu+j_0s_r+1.
\]

These inequalities exclude **every** 1<=S<=2^{B_0} with that prefix, not
just a sample of sources. Separately the independent verifier lifts the
canonical residue and checks r_N>2^{B_0}. The generator finds witnesses;
the verifier does not assume its first successful k is minimal. No such
minimality claim is accepted.

## 8. Four examples, aperiodicity and overlap

The four fixed words are (u,v,seed)=(01,10,0), (011,110,1),
(01100,11110,1), (11,10,1). Their delta values are 0,0,2,-1.
Each seed is preserved as the first symbol of its image.

Their aperiodicity can be proved without numerical tests:

1. Thue--Morse is the parity of the binary digit sum. For fixed period p,
   the value at 2^k-p is k minus the digit-sum parity of p-1, modulo 2;
   it alternates with k, whereas the value at 2^k is 1. This contradicts
   eventual period p.
2. For (011,110), w_{3n}=w_n, w_{3n+1}=1, w_{3n+2}=1-w_n. Any eventual
   period divisible by 3 can be divided by 3 using the first identity.
   A remaining period coprime to 3, combined with the middle identity,
   forces every tail residue class to be 1, contradicting the last identity.
3. For (01100,11110), h(5^k)=(2*5^k+2^k)/3. Eventual periodicity would
   force density 2/3 and bounded discrepancy h(n)-2n/3, impossible here.
   This example is permanently coefficient-safe: define D(n)=3h(n)-2n.
   From the images, D(5n+j)=2D(n)+D_{w_n}(j). Induction simultaneously
   gives D(n)>=0 and D(n)>=2 whenever w_n=0; the ten local cases are exact
   test checks. Thus 3h(n)>=2n and 9>8 implies 3^{h(n)}>=2^n.
4. For (11,10), w_{2n}=1, w_{2n+1}=1-w_n. Divide all powers of 2 from
   an eventual period using the odd subsequence; an odd remaining period
   and the even subsequence force a constant tail, a contradiction.

**Overlap with P125--P131 matters.** The last three words start 11, hence
start sigma^k(1)^2 for every k. P130 already excludes their positive
ordinary sources: its square bound is S+1>(4/3)^{r^k}. For Thue--Morse,
the repeated sigma^k(1) blocks start at i=2^k,j=2^{k+1}, have length n=2^k,
and h(j)=2^k for k>=1. P126 gives again S+1>(4/3)^{2^k}. A hypothetical
ordinary realization of the infinite aperiodic word has distinct states,
as required there. A finite repeated block alone does not establish that
distinctness; for finite repeat certificates one must supply a later split.
Our finite source certificates instead use arithmetic/lifting and do not
silently assume finite-path distinctness.

Thus these four positive-source exclusions, and their exponential scale,
are **not** new evidence of conceptual novelty. P285 additionally proves
the rational-source exclusion for the whole stated binary uniform class.
The local repeat arguments above do not establish that general rational
claim. We do not assert a literature-wide priority theorem or that no other
class-wide repetition argument exists.

## 9. External comparison, boundary controls and next step

M. Sharpe's author-hosted [rung1.tex](https://github.com/msharpe248/collatz/blob/main/paper/rung1.tex),
dated 2026-08-28, was read at its degree-one Padé construction and height
comparison. It treats the (011,110) example using a one-variable Mahler
equation and a nonzero integer bounded by its divisibility. This is relevant
methodological overlap, not an external premise for Sections 1--7. We did
not execute its Lean development or accept every claim in the manuscript.
The present two-variable identity also treats unbalanced image counts.
Adamczewski--Faverjon's [Nishioka-method paper](https://arxiv.org/abs/2210.14528)
is context only (metadata/abstract checked), not an invoked transcendence
theorem. See [literature](../../../docs/LITERATURE.md).

Mandatory counterexamples to scope expansion are retained: r=1 identity
fixes every binary word; (010,101), seed 1, has distinct images but fixed
word (10)^infinity with source 1; all ones and all zeros have sources -1
and 0. A nonzero polynomial can specialize to zero (y-1 at y=1).
Neither “different images imply aperiodicity” nor “nonzero formal residual
implies nonzero evaluation” is used. These are boundary controls, not
newly numbered refutations of already accepted hypotheses.

E66 checks all six mandatory adversarial families through its declared
finite domains (65 distinct words including periodic/empty controls).
These arbitrary finite words are used to verify map/residue arithmetic,
not claimed to satisfy the infinite substitution hypothesis. Historical
NG43/NG45/NG46/NG51 are preserved and included through dependency tests;
their prior artifacts are not rewritten.

The useful next mathematical task is an orbit-specific bridge from one
ordinary source, its carry/lifts or repeated ancestry to an unavoidable
self-similar relation or a comparable height-versus-divisibility conflict.
No such covering theorem is supplied. A deeper fixed-word table or
EXT08's quarantined density assertion cannot replace it.

## What this result does not prove

It does not exclude every automatic word, nonuniform morphic word, critical
formal word, permanent-safe tail, normalized-height geodesic, or positive
cycle. It does not prove that ordinary Collatz words belong to this special
language. P119 remains its historical CONDITIONAL claim, EXT08 stays OPEN,
and H112/H72/H89/H133 remain OPEN. Finite computations neither prove the
universal derivations by themselves nor supply a proof of Collatz.
