# Phase 13 renewal-code-pressure provenance

## Base and scope

- Fetched base: `origin/main` at
  `70f9cc8d895cf28143e8c6e094ffd076c60db959`.
- Branch: `feat/phase13-renewal-code-pressure`.
- Result commit: `be2e5221dbc12bd99a1cdff8e4eaab68e11255b8`.
- Existing untracked artifacts and scratch files were not modified, staged, or
  used as accepted evidence.

## Untrusted inputs

The following files were read as hypotheses and comparison data only:

| Input | SHA-256 |
|---|---|
| `scratch/RENEWAL_CODE_COMPANION_CRITICAL_AUDIT.md` | `9791d27f5686d1a2397c92d983c9382653635cfb25dc8c50dffe4e7771f38bde` |
| `scratch/renewal_code_critical_audit.py` | `861273870637a41f68f904fd28eaed7a9bc262b0e808623681cc31e203764d34` |
| `scratch/renewal_code_critical_finite.json` | `cf4a9dab5b435a5088b9cdca1564da81e8ceac6d17d87fb295fd1eb74193e0cd` |
| `scratch/RENEWAL_PRESSURE_RESIDUE_AUDIT.md` | `2fdcd49c690aeb2f011f55226e9cd1fb9bdff54128910549c5b150527ba56d25` |
| `scratch/renewal_pressure_residue_audit.py` | `d03cbbb6c10d15a3e1a44bced238cd6bd31f067fdcf19cc8ad4543871df3686d` |
| `scratch/renewal_pressure_residue_finite.json` | `4bc3d982b3d19956c017b5301ccda7f68e60b761b618f472363264179f525f4e` |

## Independent reconstruction

- Generator: `src/phase13_search.py`.
- Verifier: `verifier/verify_phase13.py`.
- The verifier contains none of `phase13_search`, `from src`, or `import src`.
- Generator and verifier use separate state representations for first passage,
  affine composition, critical residues, address enumeration, and lattice
  counts.
- Tests mutate orientation, prefix status, weighted identity, analytic bounds,
  threshold equality, q=3 absence, divisibility, normalized valuation,
  critical digest, raw Haar obstruction, lattice error, cylinder overlap, and
  pressure factors.

## Comparison outcome

The independent reconstruction agrees with both scratch audits on the
length-512 DP values, threshold equality word, q=3 absence, 4096-step critical
checkpoints/digests, `Q<=12` address counts, finite canonical ratios, lattice
errors, and endpoint overlap counts.

Phase 13 additionally proves `nu<9/32` and the normalized correction rules
`C_w>=2^(L-3)` and `v2(C_w)=r-2`.  These additions do not prove the open
anti-concentration premise.

## Acceptance boundary

The repository accepts P77–P79 as theorems, P80 as a conditional implication,
E22 as finite computation, and NG23 as a refuted mechanism.  NG22 receives
additional evidence without a new claim ID.  H72 and the Collatz conjecture
remain open; `proves_collatz=false`.
