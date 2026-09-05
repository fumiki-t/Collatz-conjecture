# Phase 38 run results — finite capacity and renewal transfer

## Outcome

Phase 38 was implemented and independently audited on branch
`feat/phase38-finite-capacity-renewal-transfer` from Phase 37 acceptance
commit `fae3d911e0a32fb977dfa676c3dab4dd224fe6ee`.

The supplied note was treated as an untrusted proposal. Its central capacity
and renewal identities are valid after preserving three boundaries:

- the recursively computed `A_N,O_N` are upper capacities, not optimal
  occupancy claims;
- “every positive cycle is critical” remains conditional on X02;
- different real and 2-adic limits of one rational transfer series are not a
  contradiction.

Accepted labels are P227--P229 and P231--P234 as `VERIFIED_THEOREM`, E54 as
`VERIFIED_FINITE`, and P230 as `CONDITIONAL`. H72, H133, and the Collatz
conjecture remain `OPEN`. `proves_collatz=false`.

## Main conclusions

P227 gives the exact integer image capacity

\[
Y_{N,s}(X)=1+\left\lfloor
\frac{3^s(X-1)+(2^{N-s}-1)(3^s-2^s)}{2^N}
\right\rfloor.
\]

P228 uses it in strong-induction recurrences for the general bound `A_N` and
odd-source bound `O_N`. Exact rows through `N=500`, P220's tail, and the first
three positive terms of the logarithm series certify

\[
\sum_{N=49}^{\infty}\frac{O_N}{2^N}<3\log2.
\]

It follows that every primitive positive noncritical cycle has minimum
`m<2^49` (P229). X02 would then force every positive cycle to be critical,
but that is P230 `CONDITIONAL`, not an internal cycle exclusion.

At renewal boundaries, with `A_i=S_i+1`, `H_i=h_i-1`, and `r_i=R_i-1`,
P231--P233 prove

\[
\zeta_i-\zeta_{i+1}=\frac{r_i}{A_i+H_i},
\]

\[
\sum_i\frac{R_i}{S_i+1}<\infty,
\qquad
\sum_i\frac{R_i-1}{h_i-1}=\infty,
\]

and

\[
\sum_i\frac{r_i}{C_i}=H_0\quad(\mathbb R),
\qquad
\sum_i\frac{r_i}{C_i}=-A_0\quad(\mathbb Q_2).
\]

Every nonzero transfer term has the exact initial-run valuation recorded in
P233. P234 gives

\[
a_{n_i}\ge\frac{30}{29}\log_2(i+1)-O_{S_0}(1)
\]

at every renewal boundary. This last statement does not cover every odd
iterate.

## Exact finite audit

The generator and the implementation-independent verifier reconstruct:

- 501 `A_N,O_N` rows through `N=500`;
- the exact finite reciprocal fraction, rational geometric tail, and
  `log(2)>842/1215` certificate;
- 12,672 sources in 148 translated interval cases and 608 fixed-weight
  groups through `N<=10`, including translations above `2^120`;
- 154 first-upcrossing codewords through length 14;
- 423 finite renewal addresses and 817 exact block transitions;
- 717 nonzero transfer terms with exact 2-adic valuations;
- all mandatory adversarial families, including
  `111011100 -> (729x+817)/512` with fixed point `-817/217`;
- the trivial-cycle convention and NG22 completion boundary.

The supplied private target digest does not match the repository's canonical
row digest. The proposal did not specify its serialization and explicitly
said it was not acceptance evidence. The accepted check is independent
row-by-row reconstruction; the discrepancy is retained in the obstacle
report.

## Reproduction

```bash
.venv/bin/python src/phase38_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase38.py \
  --artifact-dir artifacts --output artifacts/phase38_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase38_properties.py \
  tests/test_phase38_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The focused Phase 38 and research-health suite passed `17` tests in `87.19s`.
The complete repository regression passed `515` tests in `3092.21s`
(`51:32`). Strict research health returned `valid=true`, `errors=[]`, and
`warnings=[]` over 259 tracked artifacts before acceptance.

## Artifacts and SHA-256

| Artifact | SHA-256 |
|---|---|
| `phase38_capacity_certificate.json` | `7020f8e8b9b0157ec0881825b9063838a597ae3dcba9040ba7fff6c2e3ba29ec` |
| `phase38_obstruction_report.md` | `2777702e549805ceed713edbc77a6c84be4c395caad4808a3ef56249dbe47645` |
| `phase38_regressions.json` | `54144d8b8b821f5a21fd7617e2d2c4c42eaa73d9512e0fc66a48d1f5476f6045` |
| `phase38_renewal_transfer.json` | `a5d322029326d0074599f42d781b4cbdc3ac316f7ca2f38c57c8d091b79b51b7` |
| `phase38_verifier.json` | `4b790d15098e8d938184b13c78800475c3c56b84db9ada79331a2744b3a0a4bb` |

The repository-defined capacity row digest is
`7cbeb6b18addf9ff2ed16b472f497d634bdd1a78cdf7a544e9715a5a755ce83f`.
The complete `artifacts/SHA256SUMS` manifest has SHA-256
`1fbe822b0a1a986cc773a4c0efeedacbc6ce9bd0faddae02afe5abf12a9a6a37`.

## What this result does not prove

Phase 38 does not enumerate every start below `2^49`, exclude critical
arbitrary-area cycles, prove P80, turn a real or 2-adic source into a positive
ordinary integer, or force renewal extinction. It does not prove or disprove
the Collatz conjecture. `proves_collatz=false`.
