# Branch-point decomposition: run results

Branch: `research/phase10-branch-point`

Base commit: `b3ab86a102c0df3f2e7ded72b8dd32dc1fa53312`

This research supplement strengthens Phase 10 without claiming a proof or
disproof of the Collatz conjecture. It decomposes every positive near-gap pair
by its first parity divergence, independently verifies the resulting finite
branch profile, and leaves C04 and C05 `OPEN`. `proves_collatz=false`.

## Reproduction commands

```bash
.venv/bin/python src/branch_point_search.py \
  --artifact-dir artifacts --bound 1500000
.venv/bin/python verifier/verify_branch_point.py \
  --artifact-dir artifacts \
  --output artifacts/branch_point_verifier.json
.venv/bin/python scripts/research_health.py
.venv/bin/python -m pytest tests/test_branch_point_properties.py \
  tests/test_branch_point_verifier.py tests/test_research_health.py -q
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
shasum -a 256 artifacts/SHA256SUMS
```

The independent verifier does not import the generator. It recomputes every
coefficient stopping time, checks each stored witness directly, and proves the
finite upper bound for each branch depth by searching for forbidden residue
side pairs one depth higher. It also reconstructs all exhaustive and mandatory
adversarial digests. Tampered theorem statements, dependency boundaries,
witnesses, adversarial hashes, and C05 statuses are rejected.

## P66 — exact first-divergence lemma (`VERIFIED_THEOREM`)

Let `0<n<m`, `d=m-n`, and `h=v2(d)`. The parity-vector map on a prefix of
length `j` is a bijection modulo `2^j`, so

```text
the first j parity bits agree  <=>  n=m (mod 2^j).
```

Consequently, the two parity prefixes agree for exactly `h` steps and differ
at step `h+1`. If their common prefix contains `a` odd branches, the common
affine map gives

```text
T^h(m)-T^h(n) = 3^a*d/2^h = 3^a*(d/2^h).
```

Because `d/2^h` is odd, the transformed gap is odd and the two next branch
bits are opposite. This is an integer/algebraic theorem, not a statistical
claim. The finite audit checks all 32,385 pairs with `2<=n<m<=256` as a
regression, while the proof itself is not inferred from that enumeration.

## P67 — q0 branch reduction (`CONDITIONAL`)

P63 gives `4|d` in the positive q0 near-return box, while
`0<d<=4,142,380,786<2^32`. Therefore

```text
2 <= h=v2(d) <= 31.
```

P64 makes both endpoints coefficient-safe through `K0-1`. Thus every positive
q0 gap belongs to exactly one of 30 branch cases. After `h` common steps, the
two paths enter opposite parity branches with the odd transformed gap above.

This is a lossless q0-specific reduction, but it does not make the two remaining tails
independently coefficient-safe from a fresh zero budget. They inherit the
common-prefix coefficient surplus. Excluding simultaneous continuation of both
budgeted tails in all 30 cases would give the q0 consequence needed from C05;
the global spacing statement C05 is stronger.

## E16 — exact finite branch profile (`VERIFIED_FINITE`)

For each branch depth define

```text
R_h(H)=max {min(tau(n),tau(m))-1:
            2<=n<m<=H, v2(m-n)=h}.
```

The production run exhausts `H=1,500,000`. Branch depths `0<=h<=20` occur in
this finite range. The profile is:

| `h` | `R_h(H)` | witness `(n,m)` | gap |
|---:|---:|---:|---:|
| 0 | 0 | `(2,1126015)` | 1126013 |
| 1 | 1 | `(5,1126015)` | 1126010 |
| 2 | 175 | `(626331,1126015)` | 499684 |
| 3 | 183 | `(1126015,1345383)` | 219368 |
| 4 | 174 | `(667375,1126015)` | 458640 |
| 5 | 172 | `(381727,1126015)` | 744288 |
| 6 | 183 | `(1126015,1127871)` | 1856 |
| 7 | 213 | `(1126015,1394431)` | 268416 |
| 8 | 169 | `(1042431,1394431)` | 352000 |
| 9 | 182 | `(1027431,1345383)` | 317952 |
| 10 | 187 | `(1126015,1327743)` | 201728 |
| 11 | 166 | `(401151,1394431)` | 993280 |
| 12 | 153 | `(401151,1003263)` | 602112 |
| 13 | 152 | `(288615,1345383)` | 1056768 |
| 14 | 152 | `(376831,753663)` | 376832 |
| 15 | 148 | `(376831,1130495)` | 753664 |
| 16 | 164 | `(362343,1345383)` | 983040 |
| 17 | 118 | `(454655,847871)` | 393216 |
| 18 | 120 | `(303103,565247)` | 262144 |
| 19 | 164 | `(601727,1126015)` | 524288 |
| 20 | 107 | `(171007,1219583)` | 1048576 |

The largest finite joint-safe depth is 213 at `h=7`, reproducing the Phase 10
closest-pair obstruction from a different classification. The profile is not
monotone in `h`; large shared 2-adic depth alone does not force unusually long
joint coefficient safety in this range.

The mandatory adversarial audit verifies 5,156 adjacent pairs drawn from
`2^m-1`, `8^m-5`, all 4,096 twelve-block `(110|111)^*` residues, A, B, and
the `A^rB^s` inverse-parity residues for `1<=r,s<=32`.

## Research obstruction

The branch decomposition replaces the q0-specific positive-gap problem by 30
exact cases, but the finite profile does not yield a monotone,
subadditive, or contracting continuation rule. In particular, `h` controls
the first split and transformed gap but not the later coefficient-surplus
budget. A scalable certificate must retain at least:

```text
(branch depth h, common odd count a, odd normalized gap,
 inherited coefficient surplus, two tail residue states).
```

Discarding the inherited surplus or either tail residue would not be a
lossless C05 argument.

## What this result does not prove

This supplement does not prove C04, C05, H54, H57, the existence or
nonexistence of a least counterexample, or the Collatz conjecture. The finite
bound `H=1,500,000` supplies no conclusion at `H=2^72`, and the unobserved
finite branch depths `21,...,31` are not ruled out at the target height.

## Acceptance result and SHA-256

Acceptance result: `184 passed in 192.40s`. The focused supplement and health
suite passes 6 tests, including independent acceptance and tamper rejection.
`artifacts/branch_point_verifier.json` records `valid=true`, C05 as `OPEN`, and
`proves_collatz=false`.

```text
a48725b21ce94bb04f2732c652fb17fbf3a85ddf6a1c7e956a3cf03d23ebaa3b  branch_point_decomposition.json
48ed58e00778879888f264a0ccd2b072649d39df97ced9808d365650ae2a0302  branch_point_verifier.json
```

SHA-256 of `artifacts/SHA256SUMS`:
`ac70fa231476c86edc0f3d88be53b310aacca2939a9ee981c70574f05001a39a`.
