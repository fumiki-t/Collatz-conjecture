# Phase 33 audit — critical-area bootstrap

## Scope and status

The Phase 33 v3 note was treated as an untrusted proposal.  This audit accepts
P200, P201, E46, and E47. H200 is RETRACTED as a method-specific obligation:
its concrete area-six target is closed by the stronger P201 theorem, while the
older offset-polynomial classification was bypassed, not silently claimed.
H172 and H133 remain
OPEN. `proves_collatz=false`.

## 1. Conventions and accepted inputs

For a critical primitive positive nontrivial cycle write

```text
L=ceil(q alpha), alpha=log_2(3), lambda=3^q/2^L,
q=d q0, L=d L0.
```

The proof uses the accepted P133, P156, P164/EXT17, P177, P180, P195,
P199, and E28 with their original scopes.  In particular, positivity and
integrality are never extended to negative cycles or rational shadows.

## 2. Exact scalar envelopes and global cutoffs

For `A<=61`, P156 gives `J<=61,h<=10`; substituting the worst legal values in
P180 yields

```text
L < 929 + 62 log_2(q/[3 lambda(1-lambda)]).
```

For `A<=117`, the analogous bounds `J<=117,h<=14` give

```text
L < 2241 + 118 log_2(q/[3 lambda(1-lambda)]).
```

Put `x=2^L/3^q-1`.  EXT17 gives `x>(12q)^(-K)` with
`K=1564920000`, while `lambda(1-lambda)=x/(1+x)^2>x/4`.
Using `alpha>19/12`, the integer power bounds in the artifact give the exact
positive margins

```text
Q61=2800000000000:  201619589401/3,
Q117=5500000000000: 641842698055/3.
```

The corresponding derivative bounds are strictly below `19/12`, so all
solutions lie below the stated cutoffs.  No floating-point comparison enters
the decision.

## 3. Gcd and Legendre reductions

P177 gives `q0>=971,L0>=1539`.  P199 and `s<=A` imply

```text
d < A(1+(A+1)/L0).
```

This is `97661/1539<64` for `A<=61` and
`21541/171<126` for `A<=117`, hence `d<=63` and `d<=125`.

The P180 envelope bounds the multiplier gap.  For
`lambda in (1/2,1)`, `-log_2(lambda)<=2(1-lambda)` and
`1-lambda<2lambda(1-lambda)`, so

```text
0<L/q-alpha<2*2^((C-L)/a),
```

where `(C,a)` is `(929,62)` or `(2241,118)`.  With `L>19q/12`, the exact
base-two exponents at `q=2048` and `q=4096` are respectively
`-2477/186` and `-3529/354`; the comparison decreases thereafter.  Thus

```text
0<L0/q0-alpha<1/(2q0^2),
```

and Legendre's theorem makes `L0/q0` an upper regular convergent.

An outward rational atanh enclosure reconstructs the CF prefix.  The first
frontier contains eight upper convergents and 461 critical multiples; the
second contains those eight plus `8573543875303/5409303924479` and 915
multiples.  For each multiple put
`delta=L ln2-q ln3`.  Since `0<delta<ln2`,

```text
lambda(1-lambda)>delta/4.
```

The generator and verifier independently round
`log_2(4q/(3delta))` upward to an integer.  Even this deliberately coarse
P180 upper bound is negative for all 461 and 915 candidates.

## 4. Exhaustive low-q P195 audit

For each critical `q`, first reject `q0<971`.  P133 supplies the exact largest
possible least cycle value

```text
m_max=floor((q*2^L-1)/(3(2^L-3^q))).
```

If `m_max<300000`, E28 rejects the row.  Otherwise P167 and P185 give the
complete legal scalar region

```text
B_h=sum_(0<=r<h) floor(rq/(L-q)),
Sigma=A-J-B_h>=0,
h<=J, E<=min(J,h+Sigma).
```

For exclusion through `A*`, it is safe to set `A=A*`: the feasible region and
P195 right side are monotone in area.  Set `m=m_max`; the state-separation
width and the P195 right side are nondecreasing in `m`.  The exhaustive exact
integer maximization then gives:

| area ceiling | q rows | q0 rejects | P133/E28 rejects | admissible | P195 survivors |
|---:|---:|---:|---:|---:|---:|
| 61 | 1,077 | 405 | 669 | 3 | 0 |
| 117 | 3,125 | 808 | 2,305 | 12 | 1 |

At area 61 the closest margin is `-3` at `q=971`.  At area 117 the only
survivor is `q=971`; the closest other row is `q=1636` with margin `-21`.
This proves P200 from the already accepted inputs.

## 5. E46 finite descent and P201

The certificate lists every odd source from 300001 through 583559 and its
first shortcut iterate below the source.  The independent verifier does not
trust the stored step or endpoint: it replays every trajectory and rejects a
missing, reordered, or altered row.  It reconstructs 141,780 rows.

Together with E28, strong induction proves convergence for every positive
`n<583561`: even `n>=300000` immediately halves; every odd such `n` reaches a
smaller positive value by the certificate.  On the first required interval,
the maximum first-descent time is 121 at 303103, with first lower value
208055.  This eliminates the sole area-117 scalar survivor and proves P201.

The additionally certified interval through 583560 reaches the next scalar
height obstruction.  Its maximum is 173 steps at 381727, first lower value
323434.  It is accepted as finite evidence, not automatically promoted to a
third scalar tier.

## 6. H200 transition and next obstruction

P201 excludes every critical area from 6 through 117, including H200's
`A=s=d=6` target in every gcd class. Because H200's literal statement requests
a particular classification that was not completed, it changes from OPEN to
RETRACTED rather than VERIFIED_THEOREM. The target is closed by P201; the
method-specific obligation is withdrawn without recycling its claim ID.

The exact next scalar survivor is

```text
(q,L,A)=(1636,2593,118),
h=7,J=46,Sigma=39,E=46,n=29,Z=12,
P195 RHS-3L=45.
```

E46 now covers its P133 height range.  A further area theorem still requires
a new envelope, cutoff, gcd bound, Legendre threshold, frontier, and low-q
audit.  Repeating finite tiers cannot become an all-area proof without a
uniform termination mechanism.

## 7. Independence and adversarial boundaries

The verifier imports neither `src` nor the generator.  It uses a longer raw
rational log series without dyadic rounding, a separate CF implementation,
a separately coded legal-parameter optimizer, and a separate shortcut
iterator.  Tamper tests alter a frontier count, a trajectory row, and the
`proves_collatz` boundary; all are rejected.

The regression artifact retains `2^m-1`, `8^m-5`, `(110|111)^*`, `A=11101`,
`B=1100`, `A^rB^s`, the trivial cycle and powers, both negative cycles,
rational shadows, and NG34--NG40.  These are scope controls rather than
evidence for the universal cycle theorem.

## What this result does not prove

It does not provide an upper bound on hypothetical cycle area, exclude
noncritical or arbitrary-area positive cycles, eliminate either nonperiodic
branch, or prove the Collatz conjecture. `proves_collatz=false`.
