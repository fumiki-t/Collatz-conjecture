# Input provenance

Input: `collatz_substitution_arithmetic_20260912_bundle.zip` (13 members).
ZIP SHA-256: `ce2af256416abe870af8a7dd3518eaaeae187cb79f1aa3cc69de95d8227acd47`.
All 12 non-manifest member hashes were checked before implementation.
The two archived Markdown documents are byte-identical to the inputs.

```text
b5e3243cf812ef2e02388a32e604854d038f96b7b37f69844fadf2ac258545ae  CODEX_PROMPT_JA.md
98848ad2d7b247045f2fccf463bc1f1fcdd2cc22b6f11dc6bf057276755df599  PROOF_JA.md
5447de4a104975c5519e2fbbf3e071ce996697cf95c97ffd76a256164cc14150  README.md
5917d94584cd183d4159890818effe907b1d4a41e62522caf8088163af7d091f  RESEARCH_LOG_JA.md
8c9900a1329b6a3f64776e0a33336b3c380fbf41a86976f4c31952ea37259482  RUN_RECORD.md
9f712da2d32838d039893feae635311f837b5eaf165e9df91f7377a5dacef957  auxiliary_candidates.json
6912a664c81eee7cfebb08e4ad9db77d601ac7e67cb678c71459696411fb61ec  build_certificates.py
92f4dd8cc60657b9c8fc5c36d72345e8dbeecf2ac92f8cc610cac24dfad9edb8  evidence.json
493d706f94875a6ecffae8208d87bb971eaf1fe809d383f55c82a4652d3b0657  explore_aux.py
eb913b905d608826695bf1f321a31aefafc58486eb5baf123064ef09a87b71ba  test_checks.py
3dd7229c5269a98caa016700c38d95bea99e598e214fe7c97abd866077a04a89  verification.json
f312a1f3cfef03aefb95473b2afa3b1abdf3d5c78a012653a20131695aa1799a  verify.py
```

The supplied code and results have proposal provenance, not independent
authorship. Generator and verifier were adapted and audited here; the latter
imports no generator or SymPy and reconstructs sparse polynomial identities,
base-r word digits, and carry lifts. Generated auxiliary and 32 certificate
values compare exactly with the supplied values; format/status metadata was
intentionally changed to this supplement's bounded VERIFIED_FINITE record.
The extra regressions, typed schema, content gcd, valuation-loss/height checks,
and rejection tests were added during this audit. See REPORT.md for the
independent mathematical derivation and its nonformalization boundary.

Only this ZIP was considered as new proposed research. Existing scratch and
all older accepted artifact bytes were preserved. The original auxiliary
polynomial generator needs optional SymPy; the accepted verifier is standard
library only. No unrelated workflow/publication bundle was incorporated.
