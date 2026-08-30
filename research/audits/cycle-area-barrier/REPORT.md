# Phase 26 audit — reduced-slope edit profiles and cycle-area barriers

## 1. Audit outcome and convention

The supplied note was treated as an untrusted proposal.  The shortcut map is

\[
T(x)=\begin{cases}(3x+1)/2,&x\text{ odd},\\x/2,&x\text{ even},\end{cases}
\]

and an odd cycle is written

\[
x_{i+1}=(3x_i+1)/2^{e_i},\qquad e_i\ge1.
\]

For a primitive positive nontrivial cycle, `q<L<2q` and
`lambda=3^q/2^L<1`.  The audit accepts P156--P159 and P161 as exact theorems,
P160 only conditionally on X02, E38 as a bounded computation, and NG35 as a
refuted proof extension.  P158 closes the former H147 obligation by excluding
all critical coprime area-three positive cycles through a stronger
arbitrary-slope argument.  H133 remains open.

## 2. P156 — reduced-slope time profile

Put

\[
d=\gcd(q,L),\qquad q=dq_0,\qquad L=dL_0.
\]

Rotate the exponent word after a minimum of its closed walk and set

\[
H_j=q_0E_j-L_0j\ge0,\qquad
r_j=[-L_0j]_{q_0}.
\]

Since `gcd(q0,L0)=1`, there is a unique nonnegative integer `a_j` with

\[
H_j=r_j+q_0a_j,qquad a_0=a_q=0.
\]

Consequently

\[
E_j=\frac{L_0j+r_j}{q_0}+a_j=:E_j^{(0)}+a_j.
\tag{2.1}
\]

The baseline increments `E_(j+1)^(0)-E_j^(0)` are 1 or 2 and repeat with
period `q0`; hence the expanded baseline is the reduced rational mechanical
word repeated `d` times.  The ordered `j`-th one moves from `E_j^(0)` to
`E_j`, never crosses the next one because every actual exponent is positive,
and therefore the literal adjacent-swap distance is exactly

\[
A_* = \sum_{0\le j<q}a_j.
\tag{2.2}
\]

The rational periodic baseline has at most `n+1` cyclic length-`n` factors
for `n<L0`; for `n>=L0` it has at most `L0<=n`.  One adjacent swap affects at
most `n+1` cyclic starts.  Thus

\[
p_{\rm cyc}(n)\le(A_*+1)(n+1),\qquad1\le n\le L.
\tag{2.3}
\]

The baseline increment is at most two while every actual exponent is at
least one, so `a_(j+1)-a_j>=-1`.  A path returning from height `h_*` to zero
must contain levels `h_*,...,1`, giving

\[
A_*\ge h_*(h_*+1)/2.
\tag{2.4}
\]

If there are several minimum rotations, every zero of `H` occurs at a time
multiple of `q0`; changing the chosen zero only cyclically shifts the repeated
baseline and time profile.  Hence `A_*` and `h_*` are invariant.  For `d=1`,
residue-indexing the same time profile reproduces P144 exactly.

## 3. P157 — arbitrary-slope factor separation

For any cyclic segment of `r` odd steps,

\[
\log_2 C_{i,j}
=r\left(\log_2 3-\frac{L_0}{q_0}\right)
-\frac{H_j-H_i}{q_0}.
\]

The first term is negative and `0<=H_j<q0(h_*+1)`, so
`C_(i,j)<2^(h_*+1)`.  The affine correction factors over a segment form a
subproduct of

\[
\prod_{i<q}(1+1/(3x_i))=1/\lambda.
\]

Starting at the least odd value `m` therefore gives

\[
M_{\rm odd}<2^{h_*+1}m/\lambda.
\]

Every nontrivial positive-cycle odd value exceeds one; the intervening full
shortcut state is less than twice its odd predecessor.  Hence

\[
M<2^{h_*+2}m/\lambda.
\tag{3.1}
\]

Let

\[
n_{\rm cyc}=\left\lceil\log_2(2^{h_*+2}m/\lambda)\right\rceil.
\]

All `L` full-cycle states are positive, distinct, and below `2^n_cyc`.
P125 then makes their cyclic length-`n_cyc` parity factors distinct.  Combining
this with (2.3), and then P133's strict
`m<q/[3(1-lambda)]`, yields

\[
L\le(A_*+1)(n_{\rm cyc}+1)
<(A_*+1)\left[h_*+4+
\log_2\frac{q}{3\lambda(1-\lambda)}\right].
\tag{3.2}
\]

Positivity and primitivity enter only at the distinct ordinary-state step.
The theorem is not applied to negative cycles, nonprimitive powers, or
nonintegral rational shadows.

## 4. P158 — critical area is at least six

On the critical line `L=ceil(q log_2 3)`, put

\[
z=(2^L-3^q)/3^q,\qquad R=75/64.
\]

For `q>=512`, EXT05 gives `z>R^(-q)/2`, while criticality gives `0<z<1`.
Since `R^q>6/5`,

\[
\frac1{\lambda(1-\lambda)}=z+2+1/z<\frac92R^q.
\]

If `A_*<=5`, (2.4) gives `h_*<=2`, and (3.2) implies

\[
L<6\log_2(96qR^q).
\tag{4.1}
\]

The artifact independently stores the exact positive comparisons

\[
3^{512}64^{6\cdot512}>(96\cdot512)^6 75^{6\cdot512},
\]

and

\[
3\cdot64^6q^6>75^6(q+1)^6
\]

at `q=512`.  The latter ratio improves with `q`, so (4.1) contradicts
`L>q log_2 3` for every larger `q`.

For `1<=q<512`, E28 gives `m>=300000`.  P133 makes

\[
900000(2^{K_q}-3^q)<q2^{K_q}
\]

necessary.  The exact 511-row scan has no passing `q`.  Therefore every
critical primitive positive nontrivial cycle has

\[
A_*\ge6.
\tag{4.2}
\]

This includes both coprime and noncoprime slopes.

## 5. P159 — noncritical area exceeds 100000

Noncriticality gives `lambda<1/2`.  P133 then yields `m<2q/3`.
The P134 packing bound and E28 imply `q>170m>=51,000,000`; an independent
rational logarithm certificate also proves the weaker conservative endpoint
`q>50,000,000` from

\[
1/300000+\log(501)/9<\log2.
\]

Suppose `A_*<=100000`.  Equation (2.4) gives `h_*<=446`.  Multiplying the
upper bound for `n_cyc+1` by `log 2`, the verifier checks at `q=50,000,000`
that

\[
q\log3>(100001)\left[(450)\log2+
\log(2q/3)+1/300000+\frac19\log(1+3q/300000)\right].
\]

It also checks the positive derivative margin

\[
9q\log3>10(100001),
\]

which dominates the derivative of the bracket for every larger `q`.
This contradicts P157 and proves

\[
A_*>100000
\tag{5.1}
\]

for every noncritical primitive positive nontrivial cycle.

## 6. P160 — conditional X02 amplification

X02 would give `m>=2075*2^60`.  P134 then gives

\[
q>170(2075\cdot2^{60})>4\cdot10^{23}.
\]

If `A_*<=5*10^15`, (2.4) gives `h_*<=99,999,999`.  The same independent
endpoint and derivative calculation at `q=4*10^23` has positive exact rational
margins, proving conditionally

\[
A_*>5\cdot10^{15}.
\]

This is `CONDITIONAL`, because the repository does not reproduce X02's full
external computation.

## 7. P161 and NG35 — phase diagram and first obstruction

For noncritical `t=L-q log_2 3>1`, use `m<2q/3` and
`1/[lambda(1-lambda)]<2/lambda` in P157.  For `A_*>0`, exact rearrangement
gives

\[
t>\frac{\log_2 3}{A_*}q-
\frac{A_*+1}{A_*}(\log_2q+h_*+5-\log_2 3).
\tag{7.1}
\]

The critical scalar method cannot be extended from `A_*<=5` to `A_*<=6`:

\[
75^7=13348388671875
>
13194139533312=3\cdot64^7.
\]

Thus the exponential margin reverses exactly when the complexity multiplier
becomes seven.  NG35 refutes only this proposed proof extension; it does not
construct an area-six cycle.  Critical area six is the first remaining
cycle-area target.

## 8. E38 — independent finite audit

The generator and verifier separately reconstruct every positive-D cyclic
exponent class through `q<=8`:

- 2,214 cyclic classes, of which 2,186 are primitive;
- 797 coprime and 1,417 noncoprime classes;
- 3,101 minimum-height rotations;
- 45,369 cyclic factor-width checks;
- 2,214 positive rational odd-height checks;
- 797 exact reproductions of the P144 coprime profile.

The verifier uses recursive composition generation, ordered-one displacement
instead of the generator's swap simulation, direct rational traces, and a
separately coded atanh interval routine.  It imports no production code.
Tamper tests alter the profile digest, scalar margin, P160 status, and
`proves_collatz`; every mutation is rejected.

## 9. Strategic consequence

P158 closes H147 in its intended positive-cycle scope by excluding every
critical coprime area-three profile through the stronger arbitrary-slope
state-separation barrier.  Phase 24/25 remain independent arithmetic assets:
their resultant mechanisms may be needed at critical area six and above.

H133 is not closed.  Its repaired first target is critical area six, where
support, resonance, radial energy, and ordinary-source correction must supply
information beyond the failed scalar coefficient comparison.  In the
noncritical branch, fixed small area is no longer the frontier; useful
quantities include support, height transitions, total variation of `2^a_j`,
and correction loss from the repeated reduced baseline.

## 10. External-input boundary

- EXT05 is used only in the large-critical proof of P158 and is not reproved.
- E28 is an internally verified finite computation and supplies
  `m>=300000`.
- X02 is external finite evidence and appears only in conditional P160.
- Mechanical/Christoffel terminology is contextual; P156 is derived directly.

## What this result does not prove

Phase 26 does not exclude critical area six or above, arbitrary-area positive
cycles, the finite-crossing or permanent-safe nonperiodic branches, or the
Collatz conjecture. `proves_collatz=false`.
