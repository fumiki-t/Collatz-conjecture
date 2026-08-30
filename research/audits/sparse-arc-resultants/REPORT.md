# Phase 24 audit — sparse circular arcs and coprime area-two exclusion

Status: accepted exact derivations and bounded computations.  The supplied
Phase 24 note was treated as an untrusted proposal.  H133, H147, every
nonperiodic branch, and the Collatz conjecture remain `OPEN`;
`proves_collatz=false`.

## 1. Convention and inherited input

Use the odd accelerated map

\[
x_{i+1}=(3x_i+1)/2^{e_i},\qquad e_i=v_2(3x_i+1)\ge1.
\]

For a coprime slope `gcd(q,L)=1` in the positive-cycle range
`q<L<2q`, put

\[
D=2^L-3^q>0.
\]

P135 supplies the residue-indexed nonnegative profile
`a=(a_0,...,a_(q-1))`, `a_0=0`, and the slope root

\[
\gamma=2^u3^v\pmod D,\qquad uq+vL=1,
\]

with `gamma^q=2`, `gamma^L=3`.  If

\[
A_a(X)=\sum_{r<q}2^{a_r}X^r,
\]

then the cycle integrality condition is equivalent to
`A_a(gamma)=0 mod D`.

Set `b_r=2^(a_r)-1`.  Because

\[
(\gamma-1)\sum_{r<q}\gamma^r=\gamma^q-1=1\pmod D,
\]

the same condition is

\[
Q_a(\gamma)=0\pmod D,
\qquad
Q_a(X)=1+(X-1)\sum_{r<q}b_rX^r\pmod {X^q-2}.
\tag{1.1}
\]

No new external Diophantine theorem is introduced.  P149 uses the already
recorded EXT05 statement

\[
D>{1\over2}(64/25)^q\qquad(q>12)
\tag{1.2}
\]

only on the critical line `L=ceil(q log_2 3)`.

## 2. P147 — sparse circular-arc certificate

Let

\[
P(X)=\sum_{j\in J}c_jX^j\ne0,
\qquad J\subseteq\{0,\ldots,q-1\},\quad M=|J|.
\]

For each `j`, the congruence

\[
Lb_j\equiv-j\pmod q
\tag{2.1}
\]

has a unique residue.  These `M` residues are distinct.  Their positive
circular gaps sum to `q`, so a largest gap has length at least
`ceil(q/M)`.  Delete one such gap and choose integer lifts in the remaining
arc.  Their width obeys

\[
W\le q-\lceil q/M\rceil.
\tag{2.2}
\]

Define

\[
A_j=(Lb_j+j)/q,
\quad A_*=\min_jA_j,
\quad b^*=\max_jb_j,
\]

and

\[
R_{\rm arc}(P)=
\sum_{j\in J}c_j2^{A_j-A_*}3^{b^*-b_j}\in\mathbb Z.
\tag{2.3}
\]

Equation (2.1) gives

\[
\gamma^j=2^{A_j}3^{-b_j}\pmod D.
\]

Multiplication by the unit `2^(-A_*)3^(b^*)` proves

\[
P(\gamma)=0\pmod D\Longrightarrow D\mid R_{\rm arc}(P).
\tag{2.4}
\]

The `A_j` are distinct.  Indeed, `A_j=A_k` would imply
`L(b_j-b_k)=k-j`; because `|j-k|<q<L`, this forces `b_j=b_k` and `j=k`.
If all nonzero `c_j` are odd, the unique term with exponent `A_j-A_*=0`
is odd and every other term is even.  Hence

\[
R_{\rm arc}(P)\ne0.
\tag{2.5}
\]

Choose `k` with `A_k=A_*` and write `alpha=log_2 3`.  Since `L/q>alpha`,

\[
\begin{aligned}
\log_2\!left(2^{A_j-A_*}3^{b^*-b_j}\right)
&=(b^*-b_k)\alpha
 +(b_j-b_k)(L/q-\alpha)+(j-k)/q\\
&<LW/q+1.
\end{aligned}
\]

Therefore

\[
\boxed{|R_{\rm arc}(P)|<2\|P\|_1,2^{LW/q}.}
\tag{2.6}
\]

On the critical line `2^L<2*3^q`, so

\[
|R_{\rm arc}(P)|<4\|P\|_1,3^W.
\tag{2.7}
\]

The generator chooses the first largest-gap tie.  The independent verifier
also rebuilds the certificate with the last tie and rechecks (2.2)--(2.6).

## 3. P148 — profile recurrence and area-two classification

Put `m=L-q`.  Time progression sends a residue `r` to `r-m mod q`.
Substitution in the profile height `r+qa_r` gives

\[
e=
\begin{cases}
1+a_{r-m}-a_r,&r\ge m,\\
2+a_{r-m+q}-a_r,&r<m.
\end{cases}
\tag{3.1}
\]

Thus positivity of every recovered exponent is equivalent to

\[
a_{r-m}\ge a_r\quad(r\ge m),
\qquad
a_{r-m+q}\ge a_r-1\quad(r<m).
\tag{3.2}
\]

Because `D>0`, `L/q>log_2 3>3/2`, hence `m>q/2`.  A positive cell at a
residue `r>=m` therefore needs a distinct root cell at `r-m<m`.  A cell of
height two at `r<m` needs another cell at `r+q-m`; if that cell lies at least
`m`, it in turn needs its own root.

At total area two a height-two cell is therefore impossible.  The complete
list is

\[
\{s,t\},\quad1\le s<t<m,
\tag{3.3}
\]

or

\[
\{s,s+m\},\quad1\le s<q-m.
\tag{3.4}
\]

Conversely, (3.2) directly verifies every profile in (3.3)--(3.4).

For later diagnostics, the same argument classifies area three.  Three unit
cells are either three roots, or two roots plus the unique upper cell attached
to one root.  A doubled root has the forced predecessor
`r+q-m`, and is valid precisely for

\[
1\le r<2m-q.
\tag{3.5}
\]

The verifier independently enumerates every weak area-two profile in the
theorem remainder and every weak area-three profile through `q<=30` before
matching these shapes.

## 4. P149 — critical area-two exclusion

For a two-cell profile,

\[
Q_a=1-X^s+X^{s+1}-X^t+X^{t+1}\pmod {X^q-2}.
\tag{4.1}
\]

Term cancellation is retained.  Away from `t=q-1`, there are at most five
nonzero odd coefficients and `||Q_a||_1<=5`.  At the boundary,

\[
Q_a=3-X^s+X^{s+1}-X^{q-1},
\tag{4.2}
\]

so there are at most four nonzero odd coefficients and `||Q_a||_1=6`.
P147 makes the arc integer nonzero in every case.

On the critical line, the uniform estimates `M<=5` and `||Q_a||_1<=6`
give

\[
0<|R_{\rm arc}(Q_a)|
<24\,3^{q-\lceil q/5\rceil}.
\tag{4.3}
\]

For `q=61,...,65`, the artifact verifies exactly

\[
48\,3^{q-\lceil q/5\rceil}25^q<64^q.
\tag{4.4}
\]

Increasing `q` by five multiplies the left exponential part by
`3^4*25^5`, which is strictly below `64^5`.  Thus (4.4) holds for every
`q>=61`.  Combining (1.2)--(4.4) yields

\[
0<|R_{\rm arc}(Q_a)|<D,
\]

contradicting (2.4) for any integral profile.  E36 independently checks the
complete critical remainder `q<=60`.

## 5. P149 — noncritical area-two exclusion

If `L>=ceil(q log_2 3)+1`, then `3^q<2^(L-1)` and

\[
D>2^{L-1}.
\tag{5.1}
\]

In the nonboundary case P147 gives

\[
|R_{\rm arc}|<10\,2^{4L/5}<2^{L-1}\qquad(L\ge22).
\tag{5.2}
\]

The second strict inequality follows at `L=22` from
`10^5*2^(4L)<2^(5L-5)` and then improves by a factor two per unit increase of
`L`.  In the boundary case,

\[
|R_{\rm arc}|<12\,2^{3L/4}<2^{L-1},
\tag{5.3}
\]

already for `L>=19`; the exact fourth-power comparison is stored.  E36 checks
every noncritical remainder with `L<=21`.

Together with P136 and P138, Sections 4--5 prove:

\[
\boxed{\text{Every hypothetical positive nontrivial coprime cycle profile has area at least three.}}
\tag{5.4}
\]

This says nothing about noncoprime profiles.

## 6. P150 — fixed-area noncritical boundary

If `A=sum a_r`, at most `A` values `b_r` are nonzero and

\[
\sum_rb_r\le2^A-1.
\]

Consequently

\[
|\operatorname{supp}Q_a|\le2A+1,
\qquad
\|Q_a\|_1\le3\,2^A-2=:C_A.
\tag{6.1}
\]

Assume the particular sparse lift `R_arc(Q_a)` is nonzero.  From P147,

\[
|R_{\rm arc}|<2C_A,2^{L(1-1/(2A+1))}.
\]

Let `t_A=bit_length(4C_A)`.  Since `2^(t_A)>4C_A`, every noncritical
profile with

\[
L\ge(2A+1)t_A
\tag{6.2}
\]

satisfies `0<|R_arc|<2^(L-1)<D` and is excluded.

The nonvanishing hypothesis in P150 is essential.  Arbitrary-area reduced
polynomials need not have all nonzero coefficients odd, so the area-two parity
argument cannot be silently reused.

## 7. E36 — finite audit and falsification corpus

The generator and independent verifier agree on:

- 7,057 valid critical coprime area-two profiles through `q<=60`;
- 204 valid noncritical coprime area-two profiles with `L<=21`;
- zero integral profiles in both complete remainders;
- 544,073 critical area-two profiles in the direct modular scan through
  `q<=250`, again with zero modular integrality witnesses;
- 521,154 valid critical coprime area-three profiles through `q<=100`;
- maximum reduced-polynomial support seven;
- worst one-sided q-arc ratio `35/41`, at `q=41,L=65`;
- worst q/L effective diagnostic ratio `80/94`, at `q=94,L=149`;
- zero failures of the exact finite comparison
  `3^W*25^d<64^d` after choosing the better diagnostic denominator.

The area-three statements are finite diagnostics only.  The verifier uses a
shifted Bezout pair, literal exponent reconstruction, the opposite largest-gap
tie, and independent weak-profile checks.  Tamper tests reject altered counts,
weakened strict inequalities, area-three metadata, and a Collatz overclaim.

The regression artifact retains the trivial cycle, both standard negative
cycles, a boundary coefficient-three case, adjacent-root cancellation,
largest-gap ties, and every mandatory adversarial family.

## 8. NG33 and H147 — the area-three obstruction

A generic area-three polynomial can have seven nonzero terms.  Cardinality
alone gives only `W/q<=6/7`.  But

\[
3^6 25^7>64^7,
\tag{8.1}
\]

equivalently `3^(6/7)>64/25`.  Thus the generic seven-point largest-gap bound
cannot combine with EXT05 to give an eventual critical exclusion.  NG33 records
this failed method; it is not evidence for a cycle.

H147 asks for a uniform improvement using the paired support

\[
\{0,s,s+1,t,t+1,u,u+1\}
\]

and validity constraints, or a stronger arithmetic replacement.  The finite
ratios above motivate that question but do not prove a positive uniform gap.
Arbitrary area and the noncoprime branch remain further obligations.

## 9. What this result does not prove

Phase 24 does not exclude coprime profiles of area at least three, any general
noncoprime cycle, H89, H112, H72, H70, or the Collatz conjecture.  It does not
turn the finite area-three ratios into an asymptotic statement, and it does not
claim a new irrationality measure.  `proves_collatz=false`.
