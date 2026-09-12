# Substitution arithmetic — audit and reproduction

`proves_collatz=false`. Input baseline:
`40888313b01bffbe198e110736404549683bedc5`; work branch
`codex/substitution-arithmetic`. See the [proof audit](research/audits/substitution-arithmetic/REPORT.md),
[unaltered proposal](research/audits/substitution-arithmetic/PROPOSAL.md),
[provenance](research/audits/substitution-arithmetic/PROVENANCE.md), and
[experiment contract](research/experiments/substitution-arithmetic.json).

## Accepted mathematical scope

- P285: an aperiodic binary r-uniform fixed word (r>=2) cannot have a
  rational 2-adic shortcut-parity source, also after a shift/finite prefix.
- P286: its canonical least nonnegative residues grow exponentially in
  prefix length, with word-dependent constants.
- E66: bounded auxiliary, functional-equation and source-certificate
  verification. Universal claims are written derivations, not formalized
  by the finite verifier or a proof assistant.

No primitivity or EXT08 is used. The four concrete positive-source
exclusions overlap earlier P126/P130 repeat inequalities. General orbit
coverage is not established; P119 remains CONDITIONAL and H112/H72/H89/H133
and EXT08 remain OPEN. No old claim status was changed.

## Exact finite results

| Reconstruction | Result |
|---|---:|
| Primitive auxiliary pairs, degree in x <=10 | 4 |
| Vanishing coefficients in Q[y] | 84 |
| Nonzero x^21 leading polynomials | 4 |
| Finite functional equations (all images r=2,3,4, input lengths 0..5) | 21168 |
| Different-image unit leading terms | 308 |
| Source-range exclusion certificates | 32 |
| Distinct prefixes independently replayed | 18 |
| Total bits of distinct prefixes | 493370 |
| Exact tower/error/height steps | 16 |
| Mandatory-family and periodic/empty control words | 65 |

The four substitutions (u,v,seed) are (01,10,0), (011,110,1),
(01100,11110,1), (11,10,1). Each has a certificate excluding every
`1<=S<=2^B` for B=8,16,32,64,128,256,512,1024. These are repeated bounds
on 18 distinct prefixes, not 32 independent words. Prefix lengths range
from 1702 to 90112. The records deliberately store digests and bit lengths
instead of enormous decimal source values. Auxiliary coefficients and all
32 certificate rows match the supplied JSON values exactly; metadata was
changed from proposal to this bounded finite-evidence schema.

## Independence and safety checks

Generator: fraction-free SymPy nullspace, expanding substitution and affine
modular inverse. Verifier: standard-library sparse polynomials, Euclidean
Q[y] gcd, base-r random-access bits, and parity carry lifting. It imports
neither generator nor SymPy, and uses explicit exceptions under `python -O`.
No independent authorship is claimed: supplied implementations were adapted
and their logic audited here. The infinite derivations were separately
reconstructed in REPORT.md, including eta=0,1,>=2 nonvanishing cases and
the actual leading order in the finite-agreement bound.

Tamper tests include wrong identities/bounds, digest/source corruption,
duplicate JSON keys, noncanonical coefficient encodings, nonprimitive y
content, bool/float substitution for integers and excessive replay levels.
The finite schema caps polynomial y degree at 64 and tower levels at
12/7/5 for r=2/3/5; it is not a general-purpose unlimited certificate API.
The original 23 limited tests are retained among the expanded suite.
During hardening a malformed `--1` encoding initially raised a generic
ValueError rather than the intended Reject; this was corrected before
acceptance. No accepted arithmetic result changed.

The first dependency regression run found that mentioning “No EXT08” in
the ledger's assumptions column was parsed as a positive dependency. The
exclusion statement was moved to notes, and exact P285/P286 dependency IDs
are now tested. The quarantine checker was not weakened; no mathematical
premise or historical artifact changed.

## Reproduction

From the repository root, using Python 3.13.0 and the existing test environment:

```sh
.venv/bin/python -m pip install -r research/audits/substitution-arithmetic/requirements-generator.txt
.venv/bin/python -m src.substitution_arithmetic_search --artifact-dir artifacts
.venv/bin/python -O verifier/verify_substitution_arithmetic.py --artifact-dir artifacts --output artifacts/substitution_arithmetic_verifier.json
.venv/bin/python -m pytest -q tests/test_substitution_arithmetic.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/research_health.py --strict
```

SymPy 1.14.0 / mpmath 1.3.0 are optional **generator-only** dependencies.
The standalone verifier can run with a fresh standard-library Python.
For isolated reproduction substitute a new temporary directory for both
`--artifact-dir` values and the verifier output path. Do not overwrite
historical artifacts. Health's strict mode requires a clean worktree.

## Acceptance record

SHA-256 of [artifacts/SHA256SUMS](artifacts/SHA256SUMS):
`3a90a0bdb1c2c746d97071a1df90a3a42baa7f89460a1a05cfce5ba9bf3faf9e`.
The manifest adds four entries; all 313 prior entries are unchanged (317 total).
All four new JSON files reproduce byte-for-byte in an independent temporary
directory, with the standalone verifier under isolated optimized Python.

Tested implementation commit: `f0562c2fb9fe7c03d9bfacbbec8394f1dfd6bb25`.
The clean detached worktree passed **588 selected tests in 53.77s** and
strict health (382 claims, 317 artifacts, no errors or warnings). Focused
tests: **69 passed in 0.78s**; optimized unittest subset: **32 passed**.
These counts overlap. All 178 tracked Markdown files pass local-link checks,
the generated index matches, and compile/diff checks pass. The standalone
verifier also passes `-I -S -O`, disabling site-packages. The initial clean
test launch raced checkout completion and ran no tests; the recorded run
was restarted after a clean checkout was confirmed.

Commands and detailed results are recorded in the experiment's
`recorded_result`. The implementation/acceptance commit chain avoids a
self-referential hash. Prior main's GitHub integrity run 34639849034 passed.
The full historical repository test suite and a wholesale Phase 1--44 proof
re-audit are not claimed. No workflow/publication system was added.

## What this result does not prove

It does not exclude arbitrary automatic/morphic words, permanent-safe tails,
all normalized-height geodesics or positive cycles, nor show that an ordinary
Collatz orbit must fall in the proved self-similar class. No Collatz proof,
general last-join bound or ancestor-existence theorem is supplied. The next
useful input must link ordinary source/carry/lifts to a contradicting
arithmetic relation; deeper substitution tables alone are not such a bridge.
