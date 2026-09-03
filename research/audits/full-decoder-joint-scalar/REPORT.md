# Phase 35 audit — full decoder and corrected joint scalar sieve

The supplied Phase 35 note was treated as an untrusted proposal. Its modular
decoder and structural inequalities survive exact reconstruction, but its
claimed `A>=238` conclusion does not follow from the stated sieve. The
accepted exact consequence is `A>=229`. `proves_collatz=false`.

## 1. P206: complete modular defect decoder

Fix `q`, `K=ceil(q log2 3)`, the mechanical odd positions
`f_j=floor(j log2 3)`, and a valid coefficient-safe word with positions
`d_j=f_j-a_j`. Write

```text
B_c=sum_j 3^(q-1-j)2^f_j,
B_w=sum_j 3^(q-1-j)2^d_j,
D=2^K-3^q,
R_0=B_c-ND mod 2^K.
```

For the canonical source residue `N=-B_w 3^(-q) mod 2^K`, `R_0` equals
`B_c-B_w` modulo `2^K`. Every nonzero defect contributes

```text
3^(q-1-j) 2^d_j (2^a_j-1).
```

Its coefficient is odd and the valid positions `d_j` are strictly increasing.
Therefore the least remaining 2-adic valuation is unique and cannot cancel.
If that valuation is `d`, the next label is the first still-unprocessed `j`
with `f_j>d`; all intervening labels have zero defect. Subtracting the exact
term and repeating terminates precisely when the remainder is zero. This
recovers the whole profile without branching on the valid critical-safe image.

The source residue also realizes the literal parity cylinder. Its endpoint
`X` satisfies the exact integer identity

```text
B_c-ND=(B_c-B_w)+2^K(X-N).
```

Thus the decoder also recovers the displacement and tests P98's normalized
box by `0<=3(X-N)<q`.

This theorem is a decoder, not an ancestor theorem. It neither constructs a
smaller positive source nor preserves the P89 order/carry obligations after a
rewrite. H89 remains open.

## 2. P207: exact P179 corollary

P179 gives a mechanical baseline of at most `n+1`, direct transport by `J`
components with cost `J(n-1)`, and exact transported support bounded by

```text
min(2A, floor(LA/q)+J).
```

Consequently every cyclic length-`n` factor count obeys

```text
p_cyc(n) <= n+1+J(n-1)+min(2A,floor(LA/q)+J).
```

No asymptotic limit or floating-point decision enters this corollary.

## 3. P208: residual-area sharpening of P195

In P195, let `K_sing=J-E` be the extracted singleton components. Each removes
one profile-area unit, so the residual profile has exactly

```text
A_res=A-K_sing=A-J+E.
```

Applying P179 to the residual `E` components gives the exact span bound

```text
T_res <= min(2A_res,floor(LA_res/q)+E).
```

Substitution before the old `T_res<=2A` coarsening yields

```text
3L <= (J+2E)(n+1)+3T_res
      +(n+3)(3+2Z+binom(Z,2)).
```

The displayed Phase 34 obstruction
`(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,209,2,105,103,105,24,10)`
passes P208 by 24 but fails P207: its right side is 2858, a margin of `-789`.

## 4. P209: mismatch gives a better upper approximation

If a least-state rotation has profile value `h-1` and a later profile point
has value `h`, the corresponding proper coefficient obeys `C_0/2>lambda`.
Writing the associated mechanical discrepancy as `epsilon_r` gives
`epsilon_r<epsilon-1`, while mechanical balance gives `epsilon_r>-1`.
For `k=q-r` and `n=L-s-1`, exact rearrangement gives

```text
0 < n-k log2(3) < epsilon.
```

It is therefore a strictly better upper linear-form approximation with
smaller denominator. This is a structural consequence; it is not required by
the corrected finite scalar floor below.

## 5. P210/E50: corrected critical area floor

For `A<=228`, the looser valid envelope

```text
L < 5950+238 log2(q/[3 lambda(1-lambda)])
```

is sufficient. At `Q=11,500,000,000,000`, the exact cutoff margin is
`2109414590734/3`, and the derivative bound is
`558676440357/11500000000000 < 19/12`. P199 gives
`d<7072/27`, hence `d<=261`. The exact Legendre comparison at `q=8192`
uses exponent `-535/357`.

Separate rational-log arithmetic finds nine upper convergents and 1,912 legal
multiples for `d<=261`; all violate the envelope. For `971<=q<=8191`, the
joint optimizer reconstructs 7,221 rows:

```text
q0 rejections:          1216
state/E46 rejections:   5979
P208 rejections:          25
P207 rejections:           1
joint survivors:           0
```

Together with the accepted cycle inputs, this proves that every critical
primitive positive nontrivial integer cycle has `A>=229`.

## 6. NG41: why the proposed area 238 claim fails

The proposal's own joint scalar conditions admit the exact tuple

```text
(q,L,A,h,J,Sigma,E,n,Z)=(2301,3647,229,2,138,90,92,24,10)
A_res=183, T_res=366
P207 margin=10, P208 margin=43.
```

Thus those conditions cannot prove `A>=238`. This refutes the proposed
derivation, not the possibility that some future stronger theorem proves the
same numerical floor. The tuple is a scalar obstruction, not a claimed
realizable positive integer cycle.

The proposal also quoted incompatible auxiliary values. Exact reconstruction
gives cutoff margin `2109414590734/3`, Legendre exponent `-535/357`, and 1,996
frontier candidates at its `d<=273`, rather than 651,592,977,457,
`-3073/714`, and 1,908.

## 7. E49 and independent verification

E49 enumerates every critical-safe odd-position word through `q=18`, totaling
1,166,058 words. For each it independently checks the canonical source,
complete decoded profile, literal shortcut endpoint, displacement identity,
and P98 box predicate. Counts by `q` are stored in the artifact.

The verifier imports neither the generator nor `src`. It reimplements the
word recursion, modular decoder, literal orbit, profile/state optimizer,
rational logarithm series, continued fractions, and both scalar inequalities.
Tamper tests separately reject changes to decoder evidence, scalar evidence,
and the no-overclaim flag.

## What this result does not prove

Phase 35 does not construct a smaller P89 ancestor, close H89, realize or
exclude the area-229 scalar tuple, prove an all-area cycle contradiction,
address either nonperiodic branch, or prove or disprove Collatz.
`proves_collatz=false`.

