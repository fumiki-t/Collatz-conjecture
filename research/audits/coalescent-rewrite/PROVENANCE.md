# Phase 14 coalescent-rewrite provenance

## Base and scope

- Base: `origin/main` at
  `7e6f637cb0bed954a5f50f71a1aa6c45b127dc8f`.
- Branch: `feat/phase14-coalescent-rewrite`.
- Result commit: `cb9f9b2da4faec3e785bbf49f5e3a12745f19603`.
- Existing local untracked artifacts and scratch files were preserved, were not
  staged, and were not used as accepted evidence.

## Untrusted input

The pasted Phase 14 proposal was read as a research specification and
untrusted mathematical note. Its SHA-256 is:

```text
459ec92d42358bc48cc7a6dd0e77956abe7322001b7cc4189cd089a8eeab8d13  pasted-text.txt
```

The proposal referred to a separate `phase14_research_note.md`, but no such
separate attachment was present. No absent note was treated as evidence.

## Independent reconstruction

- Generator/search: `src/phase14_search.py`.
- Verifier: `verifier/verify_phase14.py`.
- The verifier contains none of `phase14_search`, `from src`, or `import src`.
- The generator uses dataclass addresses and incremental affine composition;
  the verifier uses tuple states and independently reconstructs every word's
  affine constant, canonical residues, and literal trace.
- Both enumerate every renewal address of every block count with total
  `Q<=13`, but use separate block/address construction functions and compare
  fixed row digests only after reconstructing the arithmetic.
- Tamper tests modify a theorem example, a finite collision count, a threshold
  equality, and the mandatory-family digest; every mutation is rejected.

## Commands and results

```bash
.venv/bin/python src/phase14_search.py \
  --artifact-dir artifacts --max-total-q 13 --threshold-q 14
.venv/bin/python verifier/verify_phase14.py \
  --artifact-dir artifacts --output artifacts/phase14_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase14_properties.py tests/test_phase14_verifier.py
.venv/bin/python -m pytest -q
```

Results:

```text
focused Phase 14 suite: 9 passed in 52.25s
complete repository suite: 228 passed in 278.87s
verifier: valid=true
P81-P85=VERIFIED_THEOREM
E23=VERIFIED_FINITE
NG24=REFUTED
P80=CONDITIONAL
H72=OPEN
proves_collatz=false
```

The global `artifacts/SHA256SUMS` stored at the result commit has SHA-256:

```text
bfcbc79f937f67ffc55bb15c591e6eaa10b50a35ea8138bb51cb4b4b1e64ba50
```

## Acceptance boundary

The repository accepts P81--P85 with their written hypotheses, E23 only
through total `Q<=13`, and NG24's exact counterexample. It does not accept
global rewrite confluence, eventual reducibility, asymptotic irreducible
pressure, either P80 premise, H72, cycle exclusion, or a Collatz proof.
`proves_collatz=false`.
