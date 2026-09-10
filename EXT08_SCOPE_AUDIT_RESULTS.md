# EXT08 scope audit — run and acceptance record

Date: 2026-09-10. Branch: `audit/ext08-scope`.
Base: `2da31e63c87f7c2225899f2d2c500629a0e5668d` (Phase 44 retained).
This correction audit does not renumber the latest research phase.

## Outcome

EXT08 is now **OPEN**, not an accepted external theorem and not REFUTED.
The [mathematical audit](research/audits/ext08-scope/REPORT.md) records three
explicit aperiodic prescribed-real words and the failure of auxiliary
real/parity and completion-transfer steps in the cited proof. The theorem
statement itself has not been disproved. P268 and NG47 record that distinction;
E61 records exact finite checks. `proves_collatz=false`.

P119/P121/P123/P124/P128 remain conditional on the unestablished EXT08.
P127 already supplies the stronger positive-ordinary complexity route for
P123/P124's conclusions. P118/P120/P122/P125--P127, P219--P222/P242/P243 and
Phases 42--44 are unaffected. H112/H72/H89/H133 remain OPEN.

## Reproduce

From the repository root, with the declared development requirements and
full Git history (the immutable baseline must be available):

```sh
.venv/bin/python src/ext08_scope_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_ext08_scope.py --artifact-dir artifacts --output artifacts/ext08_scope_verifier.json
.venv/bin/python -m pytest -q tests/test_ext08_scope.py tests/test_phase20_verifier.py tests/test_phase21_verifier.py tests/test_research_health.py
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/research_health.py --strict
.venv/bin/python scripts/check_markdown_links.py
cd artifacts
shasum -a 256 -c SHA256SUMS
```

Independent mechanisms: integer homogeneous generation versus Fraction
real dynamics, positional series and bit-by-bit positive source lifting.
Both supplied implementations were read/audited and adapted; no claim of
independent authorship is made. The verifier imports no corresponding
generator and uses explicit failure checks, including under `python -O`.
Literature scope and infinite proofs are written audits, not machine-formalized.

## Finite results

The accepted scope is three 4096-bit schedules, 12291 prefixes including
the empty prefixes, and 28209 literal positive finite-prefix steps.
Exact odd counts are 3561, 3560, 3551. Safety flags are true, false, true.
The non-safe second model is deliberate: prefix 10 has multiplier 3/4.
The repeated real state is -5 at times 0 and 3 (also 3 and 6); its first
illegal literal bit is at time 36. There are 72 exact regression words and
three 96-step actual cycle controls. The real-limit -2 model diverges from
literal parity at time zero. These are not infinite positive Collatz orbits.

See [models](artifacts/ext08_scope_models.json),
[regressions](artifacts/ext08_scope_regressions.json),
[impact/supersession](artifacts/ext08_scope_impact.json), and
[verifier result](artifacts/ext08_scope_verifier.json).
The [experiment manifest](research/experiments/ext08-scope-audit.json)
records scope, commands, independence and acceptance checks.

## Acceptance checks

Initial scoped tests: 84 passed in 16.62s (model/regression/tamper tests and
Phase 20/21 verifier paths), then 16 passed in 16.36s (control plane and
Phase 20/21 properties). Two additional quarantine tests were added after
those runs and are included in the final clean-worktree acceptance below.
Final integrated CI-equivalent run: **226 passed in 269.10s** (75 new audit
tests, five control-plane tests, 140 Phase 44 tests and six Phase 24 verifier
tests). Clean detached implementation worktree: **102 passed in 36.61s**
(75 new tests, five control-plane, eleven Phase 20/21 verifier tests and
eleven Phase 20/21 property tests). This is **248 distinct scoped tests**,
not 328 different tests. The new suite includes 39 corruption/quarantine
checks, including an optimized-Python rejection.

Clean-worktree strict research-health: valid=true, no errors or warnings,
355 claims, latest numbered phase 44, 297 manifest entries. The generated
index, compileall, all 161 tracked Markdown link checks and diff checks pass.
All four new artifact outputs regenerate byte-for-byte in a separate
directory. All previous 293 artifact hashes are unchanged.
The whole historical repository suite and the large Phase 21 corpus are not
rerun; old evidence is retained and affected metadata/tamper paths are tested.

## History and hashes

Seven historical Phase 20/21 evidence files are pinned to baseline Git blobs.
No old acceptance artifact is rewritten. The current registry's `scope_audits`
entry and research-health guard prevent reusing old EXT08 status snapshots
as current evidence. This is a correction record, not a new claim authority.
The ledger and its generated retrieval index agree.

Supplied bundle SHA-256:
`e4d5692be68bbbe0e08e4380b87623b2e6ce61b78a564d2bb0aa6775074550aa`.
All eight supplied member hashes match. Regenerated model JSON is byte-for-byte
identical to the supplied evidence:
`212d620887af40d631e021175b156818e3cc796c3bf3f9f3d64c4287229ff2fd`.
The repository [SHA-256 manifest](artifacts/SHA256SUMS) covers the acceptance
artifacts; implementation commit and manifest digest are also recorded in
the experiment acceptance metadata.

Implementation commit: `71696aeada34d2e3a6637d1c0849d404b3111d04`.
SHA-256 of the complete artifact manifest:
`5e278fe5bd7223aa0abf52042285094a6979eae909a48a84d83c18334c2aeb53`.

GitHub issue creation returned HTTP 403 for the connected integration.
The tracked mathematical report serves as the local claim-audit docket;
no issue creation, author communication or external endorsement is claimed.

## What this result does not prove

It does not refute EXT08's density statement, classify the three 2-adic
sources as rational or irrational, construct a nonperiodic ordinary integer
orbit, or solve H112/H72/H89/H133. It does not prove or disprove Collatz.
The next step is a repaired/independent EXT08 proof or ordinary-source
arithmetic using the surviving internal results, not an equation of limits
in different completions or another depth extension.
