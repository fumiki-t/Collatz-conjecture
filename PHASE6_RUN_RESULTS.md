# Phase 6 acceptance run

Branch: `feat/phase6-critical-prefix-barrier`

Phase 6 separates a conditional symbolic theorem, exact finite certificates,
external record evidence, and unresolved asymptotic research. It does not
prove the Collatz conjecture.

## Reproduction commands

```bash
.venv/bin/python src/phase6_search.py \
  --artifact-dir artifacts \
  --hq-limit 200000 --m-search-bound 1500000 \
  --certificate-max-x 1500000 --direct-threshold 64
.venv/bin/python verifier/verify_phase6.py \
  --artifact-dir artifacts \
  --output artifacts/barrier_theorem_verifier.json
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

## Tests

```text
149 passed in 72.27s (0:01:12)
```

Phase 6 tests cover the supplied `H_q` sanity records, exhaustive small-q
critical parity words, exact stopping times, all four certificate rules,
independent reconstruction, and tamper rejection.

## SYMBOLIC_THEOREM_VERIFIED

- The P54 implication is algebraically correct under the stated assumptions
  that `N` is a least positive counterexample and the coefficient first crosses
  below one after `K` steps with `q` odd steps.
- The verifier checks the final-even contradiction, `K=bitlength(3^q)`, the
  zero-indexed odd-position bound, `B<=B_q^max`, the exact rearrangement
  `D_q*N<=B`, `H_q>q/6`, and the sparse-record implication.
- This validates the conditional proof schema. It does not establish an
  eventual lower bound for `M(k)`.

## EXACT_H_Q_RECORDS

- Every `q` through 200,000 was compared exactly; no floating point is used for
  record acceptance or for skipped-q rejection.
- There are 37 records. The first twelve match the supplied sanity indices.
- The last is `q=190537`, `K_q=301994`,
  `floor(H_q)=710220447737`.

## EXACT_FINITE_CERTIFICATES

- Five binary-cylinder certificates use `COEFF_CROSS`, `EMPTY_RANGE`,
  `BINARY_SPLIT`, and `DIRECT`.
- They certify 14 barrier-record inequalities at
  `q=1,3,5,94,147,200,253,306,971,1636,2301,2966,3631,4296`.
- Monotonicity of `M` and exact barrier-record maximality extend the continuous
  certified range to every `q` from 94 through 4,960.
- The largest shared certificate proves `M(232)>1358717` using 3,219 nodes.
- Exact failed-record witnesses are `(q,N)=(17,27),(29,27),(41,703)`.

## EXACT_DIRECT_M_SEARCH

- Every start from 2 through 1,500,000 was checked, producing 13 exact
  coefficient-stopping records and determining `M(k)` through `k=223`.
- For `66<=K_q<=224`, the smallest exact ratio is at `q=46`, `K_q=73`,
  `M(72)=703`:

```text
M/H_q = 409001776799012900018489 / 98878719971867038884317 > 4
```

## EXTERNAL_RECORD_EVIDENCE

- All 35 supplied starts independently reproduce both their shortcut dropping
  time and coefficient stopping time.
- Their record minimality is explicitly not verified.
- Under the external record-list assumption, there are eight failures, the last
  at `q=41,K_q=65`; every `66<=K_q<=1005` passes and the minimum ratio remains
  the `q=46` value above.

## ADVERSARIAL_AND_OBSTRUCTION_REPORT

- The audit covers 545 cases from `2^m-1`, `8^m-5`, `(110|111)^*`, and the
  required `A=11101`, `B=1100`, `A^rB^s` families.
- The finite `A^rB^s` records shrink the coefficient margin below `2^-13`.
  The general no-fixed-margin conclusion additionally uses the explicitly named
  irrational-rotation density theorem; the verifier checks its exact premises
  but does not reprove that theorem.
- `W=111011100`, fixed point `-817/217`, remains a counterexample to four-center
  rational-shadow completeness.
- No eventual polynomial lower bound for `M(k)` was obtained. The Wu-Wang
  estimate and `H_q=O(q^5.117)` are recorded only as external research context,
  not as inputs to a finite certificate.

## Phase 6 SHA-256

```text
7cd0534e80de2d3f1a9c59b59bf196d6a6820cc23e9b4aa87f8bf0444849961d  Hq_records.csv
95e284c191fc9baab983125d57ee5838ab804209da8585f1e422f14dcf570c7d  M_lower_bound_certificates.json
5d88350d121eee685ba902a5ac0bc2edb47c69d140d9c587b7ddecb49a258637  M_search_records.csv
aa5c96844a8087a6924e3ff4dfcd7c0b7c1cec2fda977f1a1fe90b5d86a0ba73  barrier_theorem_verifier.json
203ece86c1e6fc33e0c345914508cdd50aee664c4d0e7afa478c6d49c46d224e  external_record_audit.csv
5848f49b597864a95218913d1cff8bacdd44155b14f7c4c1754f3cf8226ca5cb  phase6_obstruction_report.md
```

The complete manifest is `artifacts/SHA256SUMS`; its own SHA-256 is
`1f7d1b4c564a01c9af7ea82abaa949df3444ed757bfc09faad00a526e2487653`.
