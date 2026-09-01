# Current research status

**Last updated:** 2026-08-31

**Problem status:** `OPEN` — the Collatz conjecture is neither proved nor
disproved by this repository.

For the self-contained Phase 1–15 map, conventions, dependency branches, and
proof obligations, read [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md).

## What is currently proved?

- `VERIFIED_THEOREM`: the exact affine-cylinder identities and the symbolic
  algebra used by the certificate rules can be reconstructed with integer or
  rational arithmetic.
- `VERIFIED_THEOREM`: C02 now proves exact descent for every positive integral
  contracting realization of the ordered family `A^rB^s`, using six internal
  CRT cases and the isolated external gap theorem EXT05.
- `VERIFIED_THEOREM`: P65 proves that `z=B/(2^K-3^q)` is the minimum of the
  formal rational affine cycle of every coefficient-safe first-crossing word,
  and `gcd(B,D)=gcd(d,D)`. It asserts no positive integral cycle.
- `VERIFIED_THEOREM`: P66 proves that two integer trajectories share exactly
  `v2(m-n)` parity steps and then split, with exact transformed odd gap
  `3^a(m-n)/2^h` after their common prefix.
- `VERIFIED_THEOREM`: P68 proves that, after a coefficient-safe common prefix,
  `(h,a,u,orientation,y mod 2^L)` losslessly determines both tails' next `L`
  parity bits and their coefficient-safety decisions over that finite horizon.
- `VERIFIED_THEOREM`: P69 splits every possible counterexample into a
  nontrivial cycle, an infinite coefficient-safe tail, or a finite-crossing
  renewal ladder of increasing `3 mod 4` tail minima with exact height, gap,
  odd-count growth, and formal rational-denominator bounds.
- `VERIFIED_THEOREM`: P70 proves that an eventual dropping-safe pair-spacing
  inequality excludes the renewal-ladder branch; P71 proves exact affine-margin
  interval closure on every fixed pair cylinder.
- `VERIFIED_THEOREM`: P72 proves the exact normalized odd-orbit product and
  mod-6 packing bounds for every nonperiodic infinite coefficient-safe tail.
  Its octave defect satisfies
  `a_i>(8/9-epsilon)log2(i)` on a density-one set for every epsilon>0.
- `VERIFIED_THEOREM`: P73 rules out the single all-contact critical mechanical
  word as the infinite parity word of a positive integer. It does not rule out
  arbitrary infinite coefficient-safe tails.
- `VERIFIED_THEOREM`: P76 reconstructs the negative-real companion and moving
  rational shadows for every reciprocal-summable positive odd orbit. The
  shadows converge to `h_0` over the reals and `-x_0` over the 2-adics, but no
  effective reduced-height contradiction is known.
- `VERIFIED_THEOREM`: P77--P79 give the unique renewal first-upcrossing code,
  its exact weighted stopping/pressure bounds, the universal `13/9` companion
  threshold, and the normalized ordinary-integrality rule
  `v2(C_w)=r-2` for a nontrivial block's initial one-run.
- `VERIFIED_THEOREM`: P81 gives the necessary-and-sufficient integer identity
  for two parity words to coalesce after an affine source rewrite. P82 shows
  that, if positive permanent-safe counterexample sources exist, their least
  source is irreducible under every uniform positive downward rewrite. This is
  a structural reduction, not an existence or termination proof for H72.
- `VERIFIED_THEOREM`: P83 sharpens the renewal companion threshold by initial
  one-run (`13/9`, `137/81`, and `43/27` in the audited cases), and P84 gives a
  universal positive decrement for every nontrivial renewal block. P85 gives
  an eventual reduced-denominator and gcd bound when the octave defect is
  positive; the zero-defect case remains outside P85.
- `VERIFIED_THEOREM`: P86 strengthens least-source coalescent pruning across
  different odd counts: a smaller safe path to the same endpoint is forbidden
  whenever its terminal coefficient is at least the target's. P87 proves the
  strict-valley suffix extraction that makes unsafe coalescent targets usable,
  with positivity and source descent checked separately. P88 proves endpoint
  injectivity for every fixed finite `{1,2}` odd-gap word.
- `VERIFIED_THEOREM`: P89 upgrades a least counterexample's every safe prefix
  to ancestral minimality. P91/P92 give the exact cross-Q carry and uniform
  endpoint-cylinder dominance rules. P93/P94 give unique finite renewal
  decomposition and its Beatty support, P95 gives shifted-defect jump classes,
  and P96 gives the exact 3-adic measure bound inherited from P78. The measure
  statement is not a pointwise ordinary-integer exclusion.
- `VERIFIED_THEOREM`: P97 repairs the q=1 correction boundary and proves exact
  signed same-Q carry lower bounds. P98 proves normalized correction and the
  prefix-closed same-Q geodesic criterion. P99/P100 give internally proved
  local merges and distinct-odd-value mod-72 reciprocal packing. P101 gives
  the nonperiodic G250/H250 dichotomy; P102 separately retains the weaker
  distinctness-free factor-3 boundary.
- `VERIFIED_THEOREM`: P104 strengthens the distinct-odd finite-crossing split
  to G270/H270 using exact r<=4 predecessor exclusions. G270 has `Y_q<2N`
  and all-prefix same-Q geodesicity; H270 has `N<q/270`, `X<q/135`, and
  `Z<2q/135`. P105 gives the exact exponent-code pressure identity, and P106
  gives an 11-word suffix-decodable r=4 code. None excludes its branch.
- `VERIFIED_THEOREM`: P107--P109 give the finite affine-graph trichotomy.
  Without a mixed SCC, safe-path normalized correction is uniformly bounded;
  bounded-final paths are arbitrarily long exactly when a positive SCC reaches
  a negative SCC. A mixed SCC admits a formal balanced safe path with linear
  correction growth. P111 makes eventual zero canonical source lifts a
  necessary condition for one fixed positive ordinary source.
- `VERIFIED_THEOREM`: P112 localizes every affine-only smaller predecessor
  below a target height to a long word or a near-diagonal coefficient band.
  P113 proves exact source/endpoint tilted martingales: the first-passage
  affine correction has infinite first moment but finite moments of every
  order below one. P114 combines the exact occupation identity with P72 to
  exclude the fixed-packet balanced P109 itinerary without EXT07. P115 makes
  eventual zero accelerated source lifts equivalent to one fixed positive
  ordinary source, and P116 gives effective exponential canonical-residue
  growth for ultimately periodic noncycle words.
- `VERIFIED_THEOREM`: P117 uses P72 to rule out bounded critical discrepancy
  and every global odd-index discrepancy envelope below `(8/9)log j`. P118,
  using the isolated external Gelfond--Schneider input EXT09, proves that
  `ln(2)/ln(3)` is transcendental. P120 proves that bounded binary balance
  gives a natural frequency and uniform factor discrepancy. P122 proves the
  corresponding bounded-discrepancy formula for every non-erasing morphic
  image of a Sturmian word.
- `CONDITIONAL`: EXT08 is López--Stoll's audited `liminf` critical-density
  theorem for rational 2-adic infinite orbits. With the word-theoretic inputs
  EXT10--EXT13, P119 excludes algebraic-frequency morphic, pure binary
  morphic, primitive substitutive, and automatic parity vectors. P121/P123/
  P124 force unbounded balance, exclude quasi-Sturmian tails, and give
  `p(n)-n -> infinity` in a positive permanent-safe noncyclic candidate.
  These conclusions retain their external dependencies.
- `VERIFIED_THEOREM`: P125 proves directly that the LCP of two distinct
  integer parity tails is `v2(a-b)`. P126 converts a repeated factor into a
  strict exact source-height inequality. P127 then proves unconditionally
  that every positive nonperiodic integer orbit has
  `liminf p(n)/n>=1/log2(3/2)`. P129/P130 bound Diophantine prefix
  stammering and prefix powers, while P131 gives an exact finite
  height/complexity capacity inequality.
- `CONDITIONAL` / `VERIFIED_THEOREM`: assuming only EXT08, P128 raises the
  necessary `limsup` complexity slope to `log(3)/log(3/2)`. P132, under P54,
  supplies an exact repetition rejection certificate for H89 searches. No
  theorem forces a certifying repeat at all large critical depths.
- `VERIFIED_THEOREM`: P133--P138 give a cycle-minimum coefficient valley, the
  G170/H170 split, the coprime residue-indexed slope profile, exact slope-root
  and resultant divisibility, the radial-energy obstruction, and exclusion of
  every coprime area-zero or area-one positive profile. P140 gives only a
  weaker grouped resultant condition for noncoprime slopes. P139's quantitative
  Christoffel source gap is conditional on EXT15.
- `OPEN`: H133 asks for a uniform algebraic-energy or ordinary-source
  obstruction for arbitrary-area coprime profiles and the general noncoprime
  branch. Phase 22 does not eliminate positive nontrivial cycles.
- `VERIFIED_THEOREM` / `CONDITIONAL`: P141 proves the exact critical
  defect-area, prefix-excess, and adjacent-swap identities and the repaired
  finite factor bound `p(n)<=(A+1)(n+1)+1`. Under P54 and distinct critical
  states, P142 gives `K_q<=A(n_q+2)+2n_q+1`. P143's polynomial-height and
  Phase 7 q0 consequences retain their missing effective inputs.
- `VERIFIED_THEOREM` / `CONDITIONAL`: P144/P145 prove the coprime cycle
  edit-area, triangular-height, cyclic-complexity, and primitive-positive
  state-separation conditions. P146's `A=Omega(q^(2/3))` conclusion remains
  conditional on an unproved effective polynomial cycle-minimum bound.
- `OPEN`: H141 asks for the missing ordinary-source/carry/resultant theorem
  that turns defect area into an eventual H89 or all-area H133 obstruction.
  E35 adds exact bounded regression data but no asymptotic closure.
- `VERIFIED_THEOREM`: P147 gives the exact sparse circular-arc divisor and
  strict size bound. P148 classifies area-two and area-three coprime residue
  profiles, and P149 combines the area-two case with EXT05 and E36 to force
  every hypothetical positive nontrivial coprime cycle to have defect area at
  least three. P150 gives only a noncritical fixed-area theorem under explicit
  sparse-lift nonvanishing.
- `VERIFIED_THEOREM` / `CONDITIONAL`: P151 proves support-sensitive Hamming
  factor bounds. Under P54 and distinct states, P152 gives
  `q<=(2n_q+1)s+2n_q+2`; the EXT04 q0 enclosure yields `n_q0=73` and
  `s>=490186612`. P153's X02 correction upper is `s<=49708569439`, so the
  exact support squeeze does not exclude q0.
- `VERIFIED_THEOREM`: P154 gives a coprime resonant-grid resultant divisor,
  nonvanishing, and conjugate-product bound. P155 excludes the exact critical
  seven-grid area-three family; its large part uses EXT05.
- `VERIFIED_THEOREM`: P156 extends reduced-slope edit area, triangular height,
  and cyclic factor complexity to every gcd class. P157 supplies the matching
  primitive-positive ordinary-state separation theorem.
- `VERIFIED_THEOREM` / `CONDITIONAL`: P158 proves every critical primitive
  positive nontrivial cycle has `A_*>=6`; P159 proves every noncritical one
  has `A_*>100000`. Conditional on X02, P160 raises the latter to
  `A_*>5*10^15`. P161 records the exact noncritical slope/area phase diagram.
- `VERIFIED_THEOREM` / `REFUTED` / `OPEN`: P158 closes H147's critical
  coprime area-three positive-cycle obligation, while NG35 proves that the
  same EXT05/factor-separation scalar mechanism cannot exclude critical area
  six. H133 remains open at critical area six and arbitrary large area.
- `EXTERNAL_THEOREM` / `VERIFIED_THEOREM`: EXT17 is Matveev's external
  two-logarithm theorem. P162--P164 use polynomial multiplier gaps to force
  `liminf A_*/q^(2/3)>=((log_2 3)^2/2)^(1/3)` along every hypothetical
  unbounded positive-cycle sequence; the noncritical gap is internal and the
  critical gap depends on EXT17.
- `VERIFIED_THEOREM` / `REFUTED` / `OPEN`: P165 forces arbitrary-gcd support
  `s_*=Omega(sqrt(q))` and gives exact Hamming/factor/height bounds. NG36
  refutes universal least-value/discrepancy rotation alignment for positive
  rational shadows. Both tall and diffuse profiles survive, so H133 remains
  open.
- `VERIFIED_THEOREM`: P166/P167 resolve the reduced profile into exact
  balanced zero-token transport and cyclic level components. P168 optimizes
  transport against height to obtain the sharp slope-dependent
  `q^(2/3)` area constant.
- `VERIFIED_THEOREM` / `REFUTED` / `OPEN`: P169 gives constants at least
  `3/2` noncritically and in `(1.535941,1.535942)` critically; the latter
  retains EXT17. P170 localizes equality, and P171 gives a corrected sparse
  multilevel polynomial. NG37/NG38 preserve the two proposal failures. H172
  and H133 remain open.
- `VERIFIED_THEOREM` / `CONDITIONAL` / `OPEN`: P173 proves automatic
  nonvanishing and exact 2-adic valuation for every coprime P147 arc. P174
  gives exact resonance inequalities, P175 excludes every fixed area
  eventually, and P176 gives an all-gcd maximum-state bound. P177 yields the
  internal reduced-period floor `q0>=971`; P178 conditionally yields
  `q0>=72057431991` from X02. Growing-area coefficient height and full-`D`
  noncoprime arithmetic keep H172/H133 open.
- `VERIFIED_THEOREM` / `REFUTED` / `OPEN`: P179 replaces the `2J` edit bound
  by exact direct component rotations. P180/P181 improve the all-gcd area
  constant by `2^(2/3)`; P182 gives exact branch constants; P183/P184 force
  repaired equality scales and all but `o(J)` singleton transports. NG39
  preserves the indispensable span term. A strict subleading pair-location
  resultant remains missing, so H172/H133 stay open.
- `VERIFIED_THEOREM` / `VERIFIED_FINITE` / `REFUTED` / `OPEN`: P185
  statically extracts 1,280 disjoint singleton swaps in E43's finite corpus.
  P186 proves the double-hit factor inequality; P187/P188 improve the area
  constant by another exact `2^(2/3)`. P189 gives the repaired local equality
  structure and P190 the exact grid recurrence. NG40 refutes promotion to a
  global near-grid when residual contexts have positive density. H172/H133
  remain open.
- `VERIFIED_THEOREM` / `VERIFIED_FINITE` / `OPEN`: P191/P192 prune every
  fixed-radius family of short nonspine leaves and prove the corresponding
  finite double-hit inequality. P193 repairs the P187 proof by taking the
  cycle limit for every fixed `R` before `R->infinity`, forcing normalized
  slack to vanish at equality. P194 then upgrades local incidence to an
  `o(L)`-defect approximate grid. E44 independently checks 10,485 rotations
  and 522,870 radius/width cases. H172/H133 remain open; the H89 Hamming-shell
  numbers in the supplied v2 note were not accepted.
- `VERIFIED_THEOREM` / `VERIFIED_FINITE` / `OPEN`: Phase 32 adds P195's exact
  triple-hit inequality and P196's stronger necessary area constant.
  P197--P199 restore the full noncoprime cofactor, prove primitive block
  oscillation, and reduce critical area six to `d<=s<=6`. E45 independently
  reconstructs 10,485 profiles, 522,870 hit capacities, and 2,936 positive
  support arcs. The proposed `d=s=6` eventual exclusion is not accepted:
  H200 records its missing explicit cutoff/identity classification. H172 and
  H133 remain open.
- `CONDITIONAL`: P110 uses EXT07 to exclude the particular balanced P109
  itinerary from positive ordinary nonperiodic orbits. It does not exclude all
  mixed-SCC itineraries.
- `CONDITIONAL`: P103 applies P102 to the Phase 7 q0 scenario using X02 and
  makes the q0 critical word all-prefix same-Q geodesic. This retains every
  earlier conditional/external input and is not a contradiction.
- `OPEN`: H97 is exclusion of the positive ordinary-source G250 geodesic
  branch. H98 is exclusion of the H250 box `N<q/250`, `X<q/125`,
  `Z<2q/125`. Neither is proved, and neither covers repeated periodic values.
- `OPEN`: H104/H105 are the sharper Phase 17 replacements for the
  distinct-odd finite-crossing split: exclude the G270 positive-source
  geodesic branch or the H270 two-sided box. H97/H98 remain valid historical
  weaker obligations; the repeated periodic branch is still separate.
- `CONDITIONAL` / `OPEN`: P90 shows that eventual H89,
  `M_star(K_q-1)>H_q`, plus a finite first-crossing remainder would exclude
  both finite and never-crossing least-counterexample cases. H89 is unproved;
  E25 is only the finite bound `M_star(210)>5000000`.
- `CONDITIONAL`: P80 proves that either a quantified endpoint or two-sided
  canonical-representative anti-concentration estimate would exclude the
  permanent-safe positive branch. Neither estimate is proved.
- `OPEN`: H70 is that eventual dropping-safe pair-spacing inequality. No
  threshold or cross-cylinder proof is known.
- `OPEN`: H72 asks for an orbit-specific packing improvement strong enough to
  exclude every infinite coefficient-safe tail. NG21 blocks a mod-6-only
  improvement, while NG22 blocks a contradiction from the strengthened
  analytic conditions plus a general odd 2-adic source alone, and NG23 blocks
  replacement of deterministic ordinary representatives by raw Haar volume.
  NG24 additionally shows that endpoint coalescence classes are a right
  congruence under a common suffix but not a left congruence under prefixing.
  Phase 18 further shows that every exact mixed finite abstraction has formal
  balanced survivors, while no accepted H72 model is a closed finite graph.
  Phase 19 excludes the canonical bounded-strip survivor internally and adds
  H112, the narrower open target of proving infinitely many nonzero source
  lifts on every infinite coefficient-safe all-prefix same-Q-geodesic branch.
  Source 167's eleven terminal zero lifts forbid any bounded zero-run shortcut.
  Phase 20 further removes automatic, primitive substitutive, and
  quasi-Sturmian symbolic tails conditionally, but leaves unbalanced
  escaping-discrepancy words with unbounded yet possibly `o(n)` complexity
  excess. Phase 21 unconditionally replaces that weak factor-complexity
  necessity by a linear slope for positive integer nonperiodic orbits, but
  does not connect factor diversity to nonzero P115 lifts or an ordinary
  height upper bound.
- `EXTERNAL_THEOREM` / `CONDITIONAL`: EXT07 is the Garcia--Tal interval
  sparsity theorem using Heppner's quantitative input. Assuming it, P74 proves
  reciprocal orbit summability and an odd permanent-safe tail minimum for
  every nonperiodic positive orbit; P75 gives summable octave defects and
  `#{j:a_j<=A}=O((A+1)2^(beta A))` for some external `beta<1`.
- `CONDITIONAL`: P54 gives
  `M(K_q-1) <= N <= H_q` under the least-positive-counterexample and
  first-coefficient-crossing hypotheses.
- `CONDITIONAL`: P57 independently gives
  `S(a)>=3N delta` and `W(C)>=6N delta-S0` under the same least-counterexample
  framework.
- `CONDITIONAL`: Phase 9 verifies forced-contact closure, the exact endpoint
  displacement bound `d<=4142380786<2^32`, endpoint congruences, G4
  impossibility, and a reverse continued-fraction barrier inside that same
  least-counterexample first-crossing framework.
- `CONDITIONAL`: Phase 10 reduces the q0 endpoint pair to the single residue
  `rho=d`, proves `4|rho`, and proves renewal coefficient safety through
  `K0-1=114208327603` for every orbit point in `[N,N+W]` in that framework.
- `CONDITIONAL`: P67 decomposes every positive q0 near-return gap into exactly
  one of 30 first-divergence cases `2<=h<=31`. Both post-split tails retain a
  shared coefficient-surplus budget; their simultaneous continuation is open.
- `VERIFIED_FINITE`: the exact modular graphs, return templates, certificate
  nodes, and finite ranges listed below were independently reconstructed.

No item above proves the Collatz conjecture.

## What is only computationally verified?

- Phase 1–2: depth 26 has 190,069 `DESCENT`, 1,227,442 `SPLIT`, and
  1,037,374 `OPEN` nodes. Literal shortcut iteration agrees for all 16,777,214
  starts with `2 <= n < 2^24`.
- Phase 3: 43,198 reverse-merge closures and 79,350 final mixed `OPEN` nodes;
  the exact boundary-gap audit reaches depth 36.
- Phase 4: 52 configured mod-9 templates, 10,335 closed certificate records,
  and 23,785 `OPEN` records; direct audit covers 1,864,135 section elements.
- Phase 5: 52 mod-27 first-return templates and 108 labeled simple cycles; four
  are noncontracting. The direct audit covers 2,485,513 section integers.
- Phase 6: all `H_q` through `q=200000` were scanned exactly, giving 37 record
  indices. Five certificates verify 14 barrier-record inequalities and cover
  every `94 <= q <= 4960`. Direct search determines `M(k)` through `k=223`.
- Phase 7: the first post-bound crossing pair is certified as
  `(q0,K0)=(72057431991,114208327604)` after the external `N>2075*2^60` input.
  Under external Denjoy--Koksma, exact consequences force 31,327,720,462
  contacts and 889,748,829 genuine `h=12` pairs. The exact finite alphabet has
  87,015 macros, and selected fixed layers contain `1,2,7,312455` words.
- Phase 8: under P58, X02, EXT04, and the Phase 7 certificates, exact counting
  gives at most 5 octave exceptions, at least 31,327,720,457 first-octave odd
  iterates, 889,748,819 first-octave `h=12` pairs, and 7,308,576,455
  first-octave consecutive returns of odd gap at most 2. The C03 falsification
  search reconstructs all 79,184 contracting `{A,B}` words through block
  length 18 (79,166 mixed) and 12,265 first block-boundary crossings through
  length 22, with no counterexample.
- Phase 9: the exact denominator-at-most-256 contact dual selects
  `lambda=143/199`, giving 35,251,435,772 closure-aware contacts and
  16,848,437,652 first-octave short returns after exception damage. Independent
  enumeration rebuilds 22,475,497 coefficient-safe first-crossing words
  through `q=21`, all 287 contracting reverse coefficient pairs through
  `a=30`, 30 lower-mechanical reverse words, and every parity word through
  shortcut length 21. No nontrivial paradoxical first-crossing word occurs in
  the small layers; exactly five bounded paradoxical cylinders occur at length
  8 in the unrestricted tree.
- Phase 10: independent enumeration reconstructs 81,118 first-crossing words
  through `q=15`. Exact spacing for every `2<=n<=1,500,000` reaches
  `Delta_213=268416` at `(1126015,1394431)`; at `k=214` only one safe value
  remains in that finite prefix. The target at `H=2^72` was not evaluated.
- Phase 10 branch supplement: E16 reconstructs `R_h(1500000)` for every
  `0<=h<=20`. The largest joint-safe depth is 213 at `h=7`, witnessed by
  `(1126015,1394431)`. Its independent verifier also checks 32,385 small pairs
  and 5,156 mandatory adversarial pairs.
- Two-tail supplement: E17 scans 6,887,319 eligible pairs with
  `2<=n<m<=20000`, `m-n<=512`, and `L=12`. For every shortened residue width
  `b=0,...,11`, it retains the first exact collision between a jointly safe
  and non-safe continuation. The mandatory adversarial audit covers 5,156
  adjacent family pairs.
- Phase 11: E18 independently recomputes every `q<=4961`. The only failures are
  `17,22,27,29,32,34`, all at pair `(27,31)` and gap 4; all `35<=q<=4961`
  pass, with final height 1,666,251. Passes from `q=141` are structurally
  vacuous in the finite scan. E19 represents 16,775,072 pairs by 262,144 exact
  affine cylinders and verifies 48,822 dropping-safe pairs at depth 12.
- Phase 12: E20 checks all 25,000 starts `S=3 mod 4` through 100,000 and 2,144
  mandatory adversarial instances. The longest recorded prefixes contain 85
  and 90 odd iterates respectively; all normalization and rational
  first-crossing comparisons agree with the independent verifier. The
  all-contact audit reconstructs 512 finite canonical residues, and NG21's
  sharpness regression contains 4,096 coprime-to-6 factors.
- Phase 15: E24 exhausts every coefficient-safe word and surplus dominator
  through `Q<=17`, plus every relevant shorter same-Q arbitrary target. At
  Q=17 there are 663,535 safe words, of which 320,168 are dominated by
  `Q_b<=Q_d`; all 32,596 safe `{1,2}`-gap words survive that test. Strict-valley
  extraction adds exactly 12, 90, and 233 reductions at Q=15,16,17 beyond
  same-Q safe targets. These are cutoff facts, not an asymptotic theorem.
- Phase 15B: E25 scans 2,500,000 odd sources through their complete safe
  prefixes without an endpoint-height cutoff, reconstructing 12,443,880 safe
  occurrences and proving `M_star(210)>5000000`. E26 audits 663,535 safe Q=17
  words, 72,804 renewal blocks through Q=17, and 5,936,673 safe Q=19 words for
  same-Q compression. All are finite statements.
- Phase 16: E27 independently enumerates all safe/critical words through
  Q=17 and 68 adversarial rows. At Q=17, 253,018 of 312,455 critical words
  are same-Q geodesic and 27,949 are also contact-rich. All 225,943 same-Q
  endpoint pairs through the cutoff have positive carry; NG28 at Q=26 shows
  that the finite sign pattern is not universal.
- Phase 17: E28 checks every `1<=n<300000`, with maximum shortcut stopping
  time 278 at least source 230631 and maximum peak 12324038948 at least source
  270271. E29 independently reconstructs 23 supercritical exponent words
  through r=4, mod-648 counts `51,66,72,117,129,172,192,204,212,216`, the
  exact 270 logarithm certificate, an 11-word code through three concatenated
  blocks, and 62 adversarial rows. These are bounded results.
- Phase 18: E30 classifies all 4,181 deterministic partial `{0,1}` graphs on
  at most three vertices, reconstructs a 512-packet mixed schedule, and checks
  74 adversarial rows. The finite classification is not a closed model of H72.
- Phase 19: E31 independently reconstructs 136 affine-valley rows, the exact
  first-passage trees through depth 12, all 406,353 same-Q geodesic critical
  rows through `Q=17`, eight periodic samples through 16 repeats, and 63
  adversarial rows. At `Q=17`, source 167 has eleven terminal zero lifts but
  crosses coefficient safety three shortcut steps later. This is a finite
  falsifier, not an eventual theorem.
- Phase 20: E32 independently reconstructs thirteen 512-bit parity prefixes,
  all 832 factor rows through length 64, 38 mandatory source-family rows, and
  64 `A^rB^s` rows. The finite factor profiles do not certify morphicity,
  quasi-Sturmian structure, balance, or any asymptotic complexity law.
- Phase 21: E33 independently reconstructs all 299,999 sources `1<=N<300000`
  through first state repetition, every repeat width through 64, 502,523
  critical and 406,353 same-Q geodesic words through `Q=17`, 11 named
  controls, and 132 mandatory-family rows. P132 rejects 160,429 critical and
  120,982 geodesic words; the surviving majority blocks an asymptotic
  conclusion from the finite rate.
- Phase 22: E34 independently reconstructs 16,623 positive exponent
  compositions and 2,214 cyclic classes through `q<=8`, all 4,786 valid
  coprime profiles of defect area at most two through `q<=22`, 1,309 resultants
  by independent multiplication-matrix/Sylvester methods, 30 named word
  controls, and 22 numeric controls. Only the trivial cycle and its powers are
  integral in the exhaustive scope. All area-bounded profiles meet the direct
  source barrier, but this finite zero-survivor result is not eventual.
- Phase 24: E36 independently reconstructs 7,057 critical area-two profiles
  through `q<=60`, 204 noncritical area-two profiles with `L<=21`, 544,073
  critical direct modular rows through `q<=250`, and 521,154 critical
  area-three profiles through `q<=100`.  The area-two remainder completes
  P149; the area-three worst ratios `35/41` and `80/94` remain finite only.
- Phase 25: E37 independently reconstructs 502,523 critical words, 82,227
  critical factor widths, 33,577 area-three profiles, and 167,884 selected
  cyclic factor widths. It verifies `n_q0=73`, resultant norm 209, the first
  seven-grid threshold `Q=11`, and the corrected `q=63322` arc falsifier with
  modular gcd one.
- Phase 26: E38 independently reconstructs all 2,214 positive-D cyclic
  exponent classes through `q<=8`, including 1,417 noncoprime classes, 3,101
  minimum rotations, 45,369 cyclic factor widths, 2,214 rational odd-height
  rows, and 797 exact P144 coprime reproductions.
- Phase 27: E39 independently reconstructs the same 2,214-class all-gcd
  corpus with 3,101 support Hamming/height checks, 45,369 support factor
  checks, six critical and seven noncritical exact envelope rows, eight
  tall/diffuse synthetic profiles, seven mandatory-family rows, and the exact
  `e=(1,3)` rotation obstruction.
- Phase 28: E40 independently reconstructs 2,214 cyclic classes, 3,101
  minimum rotations, 179,606 density intervals, 45,369 factor widths, 3,101
  transport/polynomial rows, five synthetic profiles, seven mandatory-family
  rows, and both exact proposal obstructions.
- Garcia--Tal audit: E21 independently reconstructs the NG22 formal exponent
  policy through 1,026 odd steps. It verifies `E_1024=1174`, `a_1024=449`,
  and a canonical-residue renewal by `2*2^1174`; hence no positive ordinary
  source below `2^1174` realizes the audited prefix. This finite exclusion is
  not an infinite-source theorem.
- Phase 13: E22 independently rebuilds the first-passage DP through length
  512, 3,331 codewords and every 1--4 block address with total `Q<=12`, all
  ordinary heights through 2,048, 2,144 adversarial convention instances, and
  a 4,096-step square-root countermodel. Its duplicate audit was restricted to
  fixed block-count layers; all finite ratios remain non-asymptotic.
- Phase 14: E23 exhausts all 30,084 renewal addresses with total odd count
  `Q<=13`. It finds 24,197 endpoint classes, 5,829 nontrivial collision
  classes, 5,949 positive downward rewrite pairs, 5,887 reducible addresses,
  and 24,197 finite normal forms. The smallest collision is
  `1|110|1=11101` versus `111100`, with `F_111100(2x+1)=F_11101(x)`.
  No finite rewrite cycle or nonunique normal form occurs in this scope, but
  neither observation is an asymptotic theorem.

These are `VERIFIED_FINITE`; none supplies an eventual statement.

## Strongest verified result

The strongest proof-oriented finite result is the Phase 6 certificate range:
every barrier case `94 <= q <= 4960` is excluded by exact
`M(K_q-1) > H_q` certificates and record monotonicity. The largest shared
certificate is `M(232) > 1358717` with 3,219 nodes.

The strongest exact structural result outside Phase 6 is the Phase 5 mod-27
audit: deleting `{1,11,20,26}` leaves a DAG, first returns have length at most
9, and exactly four of 108 labeled simple cycles are noncontracting.

Phase 7 adds the strongest large-`q` conditional consequence, but it depends
on external computational evidence and Denjoy--Koksma. It does not supersede
the internally verified Phase 6 finite barrier range.

Phase 8 closes C02 as a genuine theorem for the ordered contracting family
`A^rB^s`. This is the strongest new universal block result, but it covers only
one ordering family and therefore does not supersede the P54 barrier route.

Phase 17 gives the strongest current finite-first-crossing localization for
distinct odd values: G270 is all-prefix same-Q geodesic, while H270 has
`N<q/270`, `X<q/135`, and `Z<2q/135`. This is a dichotomy rather than an
exclusion and does not supersede the Phase 6 barrier certificates.

Phase 9 gives the strongest current localization of the q0 conditional
endpoint: `0<=X-N<2^32`, `X=7 or 19 mod 36`, G4 is forbidden, and the first
reverse coefficient pair not eliminated by the uniform threshold is
`(a,L)=(615582794569,975675645481)`. These are conditional consequences, not
an existence or exclusion theorem for the endpoint.

Phase 10 gives the strongest renewal consequence of that localization: every
`S` in `[N,N+W]` is conditionally coefficient-safe through `K0-1`. Thus a
positive q0 gap would create two long-safe integers within distance `W`, but
the required global spacing lower bound C05 is still open.

Phase 26 gives the strongest current area localization of the separate
positive-cycle branch. P156/P157 extend edit-area state separation to every
gcd class. P158 forces critical `A_*>=6`, closing H147 globally in its
positive-cycle scope, while P159 forces noncritical `A_*>100000`. NG35 shows
that the scalar critical proof stops exactly at area six. H133 remains open.

Phase 27 gives the strongest asymptotic localization of that branch. P164
forces `A_*=Omega(q^(2/3))` and P165 forces `s_*=Omega(sqrt(q))` along any
unbounded hypothetical sequence, across every gcd class. These bounds split
the surviving geometry into tall and diffuse profiles but do not exclude
either. The critical step depends on external EXT17.

Phase 28 sharpens that localization. P166/P167 resolve the profile into exact
zero-token transport and level components; P168/P169 improve the area
constant to at least `3/2` noncritically and to a certified critical interval
above it. P170 identifies the only equality scales, while P171 supplies a
corrected sparse multilevel polynomial. NG37/NG38 show why finite strictness
and endpoint-free bounds cannot finish the argument. H172/H133 remain open.

Phase 31 v2 now gives the strongest area localization of the cycle branch.
P185/P186 convert the nonspine singleton population into static disjoint
swaps and a double-hit capacity bound. P187/P188 raise the noncritical
constant to `(3.779763,3.779764)` and the EXT17-dependent critical constant
to `(3.870329,3.870330)`. NG40 correctly refutes the old single-radius global
promotion. P191--P194 add the missing all-fixed-`R` family: at sharp equality
the residual slack is `o(q^(2/3))` and the singleton anchors form an
approximate low-denominator grid outside `o(L)` starts. H172 must still turn
that grid into a strict full-`D` resultant, while H133 must also control
families strictly above the sharp area frontier.

## Strongest conditional route

`P54` (`CONDITIONAL`) is the current main route. A least positive
counterexample whose coefficient first crosses below one at the `q`-barrier
must satisfy

\[
M(K_q-1)\le N\le H_q.
\]

Thus an eventual proof of `M(K_q-1) > H_q`, plus the finite remainder, would
rule out such a counterexample and close the conjecture through this route.

P69 adds a logically exhaustive alternate decomposition. P70 would exclude
its finite-crossing renewal-ladder branch, but nontrivial cycles and infinite
coefficient-safe tails would still require independent exclusion. Therefore
P70 alone is not a complete Collatz route.

## Current main bottleneck

No asymptotic lower bound is known for the least coefficient-safe
representative `M(k)`. Phase 7 narrows the missing statement: no `q`-uniform
inequality is known that prevents a high affine correction `B` from coexisting
with an unusually small least positive inverse-parity residue.
Phase 8 shows that even many exact first-octave returns do not yet supply a
well-founded rank for arbitrary interleavings of the four short-return maps or
the block alphabet `{A,B}`; C03 remains `OPEN`.
Phase 9 further shows that contact closure and weighted pressure alone cannot
finish the argument: NG17 is refuted by the exact all-contact construction.
The remaining C04 bottleneck is a simultaneous Archimedean and 2-adic/3-adic
near-diagonal exclusion at q0. The reverse coefficient barrier does not yet
classify arbitrary exponent-word residues or prove that a valid path exists.
The needed result must dominate `H_q`; the contextual estimate
`H_q = O(q^5.117)` depends on an external Diophantine estimate and is not an
input to current certificates.
Phase 10 makes the same obstruction one-dimensional via
`rho=[B*P^(-1)]_D`, but neither determines this residue for the unknown q0 word
nor proves `Delta_(K0-1)(2^72)>W`. The finite neighbor-gap recursion does not
scale to the required depth and height.
P66/P67 sharpen the positive-gap side further into 30 exact first-divergence
cases. The missing scalable state must retain the common-prefix surplus, odd
normalized gap, and both tail residues; branch depth alone is insufficient.
The cycle branch has a separate bottleneck. Phase 31 v2 adds all-radius
short-leaf transport beyond Phase 28--31's area and singleton localization.
At the sharp frontier P194 now forces an approximate grid; strictly
above-frontier families remain unrestricted by that equality theorem. A new
transition-sensitive correction-loss, ordinary-source, radial-energy, or
resultant input must exclude all regimes, while
explicitly transporting between P133's least-value rotation and P156's
discrepancy-minimum rotation after NG36 and retaining P171's endpoint term
after NG38, while explicitly preserving NG40 as the falsifier of any proof
that omits the all-fixed-`R` quantifier.
H172/H133 record this obligation without
conflating it with H89/H112/H72; H147 is closed.
P68 now gives a lossless state for any fixed horizon, while NG19 shows that at
`L=12` none of the shorter windows `b<L` retains enough information even in a
small exact domain. The open problem is therefore a composable symbolic state,
not a fixed truncation of the future residue.
Phase 11 supplies one such local composition rule: exact affine margins close
to an integer interval on each fixed parity cylinder. It does not merge
different cylinders, so the state count remains exponential. The new H70
eventual dropping-safe barrier is unproved, and finite passes after `q=141` are
empty-set statements rather than asymptotic progress.
Phase 12 constrains the infinite-safe-tail branch using actual odd orbit
values. The coarse mod-6 packing input is sharp at exponent `1/9`; excluding
the branch requires an additional transition, positivity, or ordinary-height
mechanism, not a larger finite range. Phase 17 sharpens the finite-crossing
analogue: H104 needs a positive ordinary-source geodesic exclusion, while
H105 needs a two-sided ultra-low-height exclusion. P73 removes only the all-contact
extremal word. The Garcia--Tal audit conditionally upgrades every nonperiodic
positive orbit to a permanent-safe tail and gives summable defects, but NG22
shows that those analytic conditions remain consistent with a formal exponent
word and a genuine odd 2-adic source. The new boundary is therefore positive
ordinary-integrality or effective rational-shadow height, not mere 2-adic
coherence.
Phase 13 converts that boundary into a precise counting target. P78 supplies
local masses `sigma^i` and `tau^i`, while P79 couples the source to each
block's initial run through an exact 2-adic valuation. P80 shows the needed
ordinary-height decay, but NG23 proves that raw Haar mass cannot supply it:
the per-address lattice error and deterministic least representative must be
controlled arithmetically.
Phase 14 adds an exact coalescent rewrite relation. P82 reduces a hypothetical
positive permanent-safe counterexample to an irreducible renewal address, and
E23 shows that the finite relation removes many addresses. NG24 blocks the
tempting finite-state shortcut: endpoint equality does not survive arbitrary
left extension, so an asymptotic proof still needs a carry-aware lift or a
different well-founded invariant. P85 narrows the rational-shadow height
problem only after the octave defect becomes positive.
Phase 17 shows that four-odd-step predecessor sieving improves the numerical
split but does not create an unbounded volume method. NG29 caps the explicitly
scoped coefficient-only summed-Haar envelope below normalized count 360.469.
Further progress must retain affine correction, a fixed positive ordinary
source, transitions, canonical representatives, or signed carry.
Phase 21 rules out subcritical linear factor complexity for every positive
nonperiodic integer orbit, not merely selected low-description languages.
This still does not make H112 finite-state: the surviving target may have zero
entropy and linear complexity above P127's constant. The next useful mechanism
must couple P115's lift digits or P91/P97 carry to repeated/right-special
factors or ordinary height; merely measuring more finite factors cannot prove
eventual nonzero lifts.

## Secondary directions

- Lift P81 coalescence through left extension with enough exact carry data to
  prove that every positive renewal address is eventually reducible, while
  explicitly surviving NG24.
- Prove one of P80's canonical-residue anti-concentration estimates using the
  coupled `(B,r2,r3,C_w)` recurrence, P85's eventual height bounds, and every
  per-address ordinary lattice error.
- Prove C04 by excluding the q0 near-diagonal canonical residue pair, with a
  lossless carry-aware recursion or meet-in-the-middle certificate.
- Prove or refute C05 with a recursive safe-pair cylinder/difference-state
  certificate that scales jointly in depth and ordinary integer height.
- Seek a sound cross-cylinder dominance or quotient/carry recursion extending
  P71; it must distinguish every stored NG19 collision.
- Attack H72 by proving multi-step exclusions or residue-transition scarcity
  among the actual odd iterates; any proposed exponent improvement must use
  information absent from the NG21 coprime-to-6 saturator.
- Upgrade the finite mechanical reverse-residue audit to a recursive forbidden
  residue theorem for arbitrary positive exponent compositions.
- Derive recursive or meet-in-the-middle lower bounds for `M(k)`.
- Explain small `M(k)` using moving rational shadows of unbounded height and
  simultaneous 2-adic/3-adic constraints.
- Seek a common well-founded potential for the partial integer block system
  `A:32u->81u`, `B:16u+108->9u+108`, beginning with an adversarial audit of
  arbitrary interleavings rather than only `A^rB^s`.
- Extend exact certificates only when testing a precise structural conjecture.
- Revisit predecessor-tree density only with a bridge from global density to a
  single least counterexample.

## What was recently refuted?

- `REFUTED`: the Phase 26 EXT05 plus factor-separation scalar mechanism also
  excludes critical area six. NG35 records the exact reversal
  `75^7=13348388671875>13194139533312=3*64^7`. This does not construct an
  area-six cycle; it identifies the first point needing a new invariant.
- `REFUTED`: sign-pure SCC paths always have one global positive packet then
  one global negative packet (NG30). The exact four-SCC `+,-,+,-`
  counterfamily remains safe with final coefficient in `(1,2)` while all four
  packets grow. Only the finite-stage SCC-condensation normal form survives.
- `REFUTED`: coefficient-threshold predecessor exclusions combined only by
  summed 3-adic Haar mass can push the normalized cutoff arbitrarily far
  (NG29). Even a deliberately optimistic collision-free envelope reaches its
  reciprocal threshold below 360.469. This does not refute affine-aware,
  fixed-source, transition-aware, carry-aware, or geodesic methods.
- `REFUTED`: every shorter safe same-Q endpoint predecessor has positive carry
  (NG28). The exact Q=26 pair has common endpoint 716,727,426,419 and carry
  -3, despite positive carry for every E27 pair through Q=17.
- `REFUTED`: same-Q total compression gain is universally at most three
  (NG27). At Q=19 an exact gain-four pair has sources 44,466,175 and 2,779,135
  with `y+1=16(x+1)`. This does not supply a composable gain theorem.
- `REFUTED`: same-Q safe-target rewrites are complete for surplus dominance
  (NG25). The Q=1 word `1` maps 273 to the same endpoint 410 reached by
  `111110100` from 287 and has larger coefficient. A Q=5 ancestor also
  dominates a Q=4 target.
- `REFUTED`: an arbitrary coalescent target must itself be safe (NG26). The
  named unsafe Q=15 word has a strict-valley safe suffix that coalesces from
  527131 below the safe target source 1874247.
- `REFUTED`: coalescent endpoint equivalence is a two-sided congruence under
  renewal concatenation. The exact pair `11101~111100` stays equivalent under
  a common suffix, but prefixing both by `110` gives endpoint residues 263 and
  587 modulo `3^6`. Endpoint `(Q,r3)` alone is not a closed transfer state.
- `REFUTED`: coefficient-one raw Haar endpoint or product volume controls the
  canonical least positive representative count. NG23's minimum obstruction
  is `u=1,H=2`: the count is 1 and both volume predictions are `2/3`.
- `REFUTED`: the conditions `a_j->infinity`, `sum 2^-a_j<infinity`,
  `h_j>1`, and `sum 1/h_j=infinity`, even with a coherent odd 2-adic source,
  are contradictory by themselves. NG22 gives an exact invariant formal
  policy. It is not a positive ordinary Collatz orbit.
- `REFUTED`: distinctness, a lower height, and `gcd(x_i,6)=1` alone force a
  growth exponent below `1/9`. The exact abstract coprime-to-6 saturator has
  logarithmic product exponent `1/9`; it is not a Collatz orbit.
- `REFUTED`: height-free dropping-safe spacing eventually exceeds 4. For every
  `k>=3`, `2^k-5` and `2^k-1` are k-step dropping-safe and differ by 4.
- `REFUTED`: the finite critical mechanical word always inherits the infinite
  Sturmian `n+1` factor bound. NG32's smallest counterexample is
  `q=4,c_q=1101100,n=2,A=0`, with all four binary length-two factors. P141
  retains the necessary terminal `+1`.
- `REFUTED`: for `L=12`, some shortened residue window `b<L` universally
  decides two-tail joint coefficient safety. Every `b=0,...,11` has an exact
  opposite-outcome collision below `H=20000` and gap 512.
- `REFUTED`: nested safe-set deletion forces strict spacing growth at every
  depth. The exact Phase 10 prefix has `Delta_2=Delta_3=4`; only nondecrease
  survives without a stronger state invariant.
- `REFUTED`: forced-contact closure plus weighted contact pressure alone is
  sufficient. With the required correction `c_0=1`, the exact all-contact
  construction still satisfies closure and pressure but carries no endpoint
  or least-residue exclusion.
- `REFUTED`: four fixed rational shadow centers are complete. The exact block
  `W=111011100` has map `(729x+817)/512` and fixed point `-817/217` outside the
  four centers.
- `REFUTED`: the quantified H5-A bounded surrogate; 2,141 bounded
  counterexamples were retained.
- `REFUTED`: fixed short-period dictionaries universally explain critical
  prefixes; the smallest depth-26 residual representative is 27.
- `REFUTED`: the tested constants-only Phase 4 ranking closes refill cycles.
- `REFUTED` as a standalone strategy: adding only bounded binary/ternary or
  modular refinements makes the tested frontier manageable asymptotically.
- `REFUTED`: every 12-odd contact-return macro contracts, decomposes into the
  four Phase 5 dangerous words, or is locally unrealizable. Macro id 0,
  `1111111111110000000`, refutes all three candidate statements.
- `RETRACTED`: early strong numerical claims based on cycle-only assumptions,
  unchecked computations, or invalid equivalences.

## Next 6 concrete research questions

1. Can the gap residue `rho=[B*3^(-q)]_(2^K-3^q)`, `4|rho`, be excluded from
   `[0,W]` for every q0-critical word by a scalable exact recursion?
2. Can P91/P92/P95/P97 propagate ancestral-minimal fronts across Q with a
   well-founded signed-carry state that survives NG24--NG28 and proves H89, or at
   least an effective lower bound for `M_star(K_q-1)` beyond E25?
3. Can H104's positive ordinary-source G270 geodesic words be excluded while
   the formal all-contact 2-adic prefixes remain allowed, or can H105 be
   excluded with an exact two-sided source/endpoint-height automaton?
4. Can P71's exact per-cylinder margin interval be merged across residue
   cylinders by a sound dominance/carry rule strong enough to prove H70
   without relying on EXT07, or can an exact successor rule separate actual
   odd orbits from both NG21 and NG22?
5. Can P126/P132 be made composable: either force a certifying repeat along
   every H89 critical branch, or turn repeat avoidance/right-special growth
   into a nonzero P115 source lift or an ordinary-height contradiction while
   surviving both NG22 controllers, P109, source 167, and the mandatory
   adversarial families?
6. Can P170's near-extremal scales and P171's corrected endpoint polynomial
   force a nonzero resonance/resultant or canonical-residue obstruction? The
   invariant must also handle non-near-extremal tall/diffuse profiles, every
   gcd class, NG34--NG38, and both rotation conventions.

## Codex tasks worth doing

- Start with [`AI_RESEARCH_GUIDE.md`](AI_RESEARCH_GUIDE.md) and run
  `scripts/research_health.py` before modifying research code.
- Select one obligation from `research/registry.json`, read its scoped context
  pack when present, and register any large run under `research/experiments/`.
- Run `scripts/research_health.py --strict` from a clean acceptance worktree;
  untracked artifact warnings are not accepted evidence.
- Formalize one precise candidate inequality for `M(k)` and search for its
  smallest exact counterexample before scaling.
- Formalize an H89 recursion in `(Q,L,B,r2,r3,D,signed carry)` and reject it first on
  NG24--NG28 before extending the E25--E27 bounds.
- Prototype H104 and H105 separately. Preserve a fixed positive ordinary
  source for H104 and both ordinary heights for H105; never apply P104 to a repeated
  cycle segment.
- Extend P71 only with a proposed cross-cylinder dominance/carry invariant;
  test it first on NG19 and NG20.
- Extend P72 only with an orbit-specific transition invariant; test it first
  against NG21--NG28 and E20/E22/E23/E24/E25/E26/E27 before claiming an exponent or
  anti-concentration improvement.
- Treat P127/P128 as necessary conditions, not a complexity proof strategy by
  themselves. A useful Phase 21 successor must connect repeated or
  right-special factors to P115 lift digits, P91/P97 carry, or ordinary
  height, and must explain the P132 survivors rather than only extend Q.
- Treat P137 as a necessary cycle certificate: first falsify any proposed
  energy lower bound on the Phase 22 profiles and negative cycles, and do not
  scale composition depth unless the rule covers arbitrary area or strengthens
  P140's noncoprime modulus.
- Start new cycle work from P194's sharp-frontier approximate grid. Combine
  its paired anchors with a full-`D` low-denominator resultant that tolerates
  adversarial `o(L)` bad starts, and separately justify any reduction of
  above-frontier families. Rebuild NG34--NG40, E43/E44, and the Phase 28--31
  synthetic profiles first. Do not drop the all-fixed-`R` quantifier or claim
  actual maximum-state saturation from P183.
- Build an independent verifier for any new lower-bound certificate format.
- Audit proof dependencies and claim statuses after each result.
- Maintain adversarial regressions for `2^m-1`, `8^m-5`, `(110|111)^*`,
  `A=11101`, `B=1100`, and `A^rB^s`.
- Replace external record minimality with compact internal certificates where
  feasible.

## Tasks not worth doing without a new idea

- Merely extend Phase 1–5 search depth or modulus.
- Add another fixed finite shadow dictionary.
- Extend the Phase 11 q-limit without a nonvacuous asymptotic mechanism; E18 is
  already structurally empty from q=141 in its finite height.
- Retry height-free dropping-safe spacing greater than 4; NG20 refutes it for
  every depth k>=3.
- Retry a packing exponent below `1/9` using only distinctness and
  coprimality modulo six; NG21 is sharp for exactly that information set.
- Seek a contradiction from only summable octave defects, `h_j>1`, divergent
  companion reciprocals, and a general odd 2-adic source; NG22 realizes all
  four analytic conditions exactly.
- Replace deterministic canonical representatives by Haar cylinder volume or
  discard the per-address ordinary lattice `+1`; NG23 refutes that step at the
  first codeword.
- Extend coefficient-only predecessor Haar pressure to a larger word depth
  without adding affine, fixed-source, transition, representative, or carry
  information; NG29 proves a finite ceiling for that information set.
- Retry contact closure plus weighted pressure without a new endpoint or
  least-residue invariant; NG17 is an exact no-go for that information set.
- Infer an asymptotic law from high finite coverage or a beam search.
- Infer morphicity, quasi-Sturmian structure, balance, entropy, or asymptotic
  factor complexity from E32's finite prefixes.
- Retry naive predecessor-density intersection without a theorem controlling
  the exceptional least counterexample.
- Use floating point to accept a certificate or a near-critical inequality.

## Immediate audit pointers

- Machine-readable control plane: [`../research/registry.json`](../research/registry.json)
- Experiment contract: [`../research/README.md`](../research/README.md)
- Scoped AI contexts: [`context/README.md`](context/README.md)
- Claim statuses: [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md)
- Negative results: [`FAILED_APPROACHES.md`](FAILED_APPROACHES.md)
- Prioritized program: [`ROADMAP.md`](ROADMAP.md)
- Phase 6 acceptance: [`../PHASE6_RUN_RESULTS.md`](../PHASE6_RUN_RESULTS.md)
- Phase 7 acceptance: [`../PHASE7_RUN_RESULTS.md`](../PHASE7_RUN_RESULTS.md)
- Phase 8 acceptance: [`../PHASE8_RUN_RESULTS.md`](../PHASE8_RUN_RESULTS.md)
- Phase 9 acceptance: [`../PHASE9_RUN_RESULTS.md`](../PHASE9_RUN_RESULTS.md)
- Phase 10 acceptance: [`../PHASE10_RUN_RESULTS.md`](../PHASE10_RUN_RESULTS.md)
- Branch-point supplement: [`../BRANCH_POINT_RUN_RESULTS.md`](../BRANCH_POINT_RUN_RESULTS.md)
- Two-tail supplement: [`../TWO_TAIL_RUN_RESULTS.md`](../TWO_TAIL_RUN_RESULTS.md)
- Phase 11 acceptance: [`../PHASE11_RUN_RESULTS.md`](../PHASE11_RUN_RESULTS.md)
- Phase 12 acceptance: [`../PHASE12_RUN_RESULTS.md`](../PHASE12_RUN_RESULTS.md)
- Phase 13 acceptance: [`../PHASE13_RUN_RESULTS.md`](../PHASE13_RUN_RESULTS.md)
- Phase 14 acceptance: [`../PHASE14_RUN_RESULTS.md`](../PHASE14_RUN_RESULTS.md)
- Phase 15 acceptance: [`../PHASE15_RUN_RESULTS.md`](../PHASE15_RUN_RESULTS.md)
- Phase 16 acceptance: [`../PHASE16_RUN_RESULTS.md`](../PHASE16_RUN_RESULTS.md)
- Phase 17 acceptance: [`../PHASE17_RUN_RESULTS.md`](../PHASE17_RUN_RESULTS.md)
- Phase 22 acceptance: [`../PHASE22_RUN_RESULTS.md`](../PHASE22_RUN_RESULTS.md)
- Phase 23 acceptance: [`../PHASE23_RUN_RESULTS.md`](../PHASE23_RUN_RESULTS.md)
- Phase 24 acceptance: [`../PHASE24_RUN_RESULTS.md`](../PHASE24_RUN_RESULTS.md)
- Phase 25 acceptance: [`../PHASE25_RUN_RESULTS.md`](../PHASE25_RUN_RESULTS.md)
- Phase 26 acceptance: [`../PHASE26_RUN_RESULTS.md`](../PHASE26_RUN_RESULTS.md)
- Phase 27 acceptance: [`../PHASE27_RUN_RESULTS.md`](../PHASE27_RUN_RESULTS.md)
- Phase 28 acceptance: [`../PHASE28_RUN_RESULTS.md`](../PHASE28_RUN_RESULTS.md)
- Phase 29 acceptance: [`../PHASE29_RUN_RESULTS.md`](../PHASE29_RUN_RESULTS.md)
- Phase 30 acceptance: [`../PHASE30_RUN_RESULTS.md`](../PHASE30_RUN_RESULTS.md)
- Phase 31 acceptance: [`../PHASE31_RUN_RESULTS.md`](../PHASE31_RUN_RESULTS.md)
- Phase 31 v2 acceptance:
  [`../PHASE31_SHORT_LEAF_RESULTS.md`](../PHASE31_SHORT_LEAF_RESULTS.md)
- Hashes: [`../artifacts/SHA256SUMS`](../artifacts/SHA256SUMS)
