# Agentic Phase 1: three-case summary (Q01, Q04, Q08), REAL_LLM_MODE

The same unchanged architecture ran on all three cases:
- `gpt-4o-mini`, temperature 0, OpenAI Responses API with structured output;
- HYBRID_RERANKED_V2_1 retrieval, top 5;
- ToT with successors 3, beam 3, depth 3, threshold 70, near tie 5, budget 20;
- weights 30/30/20/20, with model consistency pinned at 50 (no DSM yet);
- critic scoring anchors and support labels;
- deterministic Python validation owning the hard constraints;
- one advisory comparative review of the survivors;
- LangGraph orchestration.

**Each case is a single run.** This is a capstone demonstration of the architecture, not a validated evaluation.

Q01 below is Run 3, which closed Q01 development. Under the advisory policy it remains **PARTIALLY_SUPPORTED, with the
comparative review preferring DIRECT**. Q04 and Q08 were each run exactly once, with no tuning.

| | Q01 | Q04 | Q08 |
|---|---|---|---|
| Question | Mission-system software maturity → flight-test execution | Late delivery / limited availability of test aircraft → sequence or pace of flight testing | Development testing ↔ production decisions (concurrency) |
| Source activity | A1 Mission-System Software Maturity (software) | A3 Test-Aircraft Availability (test) | A5 Development / Test Maturity (test) |
| Target activity | A2 Flight-Test Execution (test) | A4 Flight-Test Execution / Schedule (test) | A6 Production Commitment / Rework Risk (production) |
| Trace | `episode_20261030_140841_A1_A2` | `episode_20261030_141449_Q04_REAL_LLM_MODE_A3_A4` | `episode_20261030_141531_Q08_REAL_LLM_MODE_A5_A6` |
| Model calls | 9 (4 at depth 1, 4 at depth 2, 1 comparative) | 4 (1 gen + 3 critic) | 4 (1 gen + 3 critic) |
| Tokens (in / out) | 21,202 / 2,364 | 9,695 / 1,181 | 9,438 / 1,066 |
| Depth / stop | 2 / NO_NEW_CANDIDATES | 1 / NO_VIABLE_CANDIDATE | 1 / NO_VIABLE_CANDIDATE |
| Survivors | DIRECT 70.5, INDIRECT 70.5 | none (best 69.5) | none (best 65.5) |
| Comparative review | COMPLETED: prefers DIRECT; tie judged not genuine | NO_SURVIVORS (0 calls) | NO_SURVIVORS (0 calls) |
| Critic/Python disagreements | 0 | 0 | 0 |
| **Decision** | **PARTIALLY_SUPPORTED**, DIRECT (E2), type near-tied with INDIRECT | **UNRESOLVED** | **UNRESOLVED** |

Traces are in `outputs/agentic_traces/` as `.json` and `.md` files. The Q01 trace predates the case-labelled file names;
its JSON `agent_mode` and Markdown banner identify it as REAL_LLM_MODE.

## Retrieved evidence

| | Q01 | Q04 | Q08 |
|---|---|---|---|
| E1 | DOT&E FY2010 p33: software and sensor integration risks, integration before verification | GAO-11-325 p17: flight tests "hampered as in prior years by the late delivery of test aircraft" | GAO-07-360 p7: concurrency risks; at the LRIP decision "less than 1 percent of the test program will have been completed" |
| E2 | DOT&E FY2010 p29: software "delays that affected flight test progress" | DOT&E FY2010 p33: reliability and maintainability changes needed; uncertainty in mission-systems flight test | GAO-07-360 p20: past programs' software delayed flight test; "Challenges Created by Continued Concurrent Development and Production" |
| E3 | DOT&E FY2010 p33: extended development, discovery in flight test, deferrals | GAO-11-325 p31: "continuing effects from late delivery of test aircraft … substantially reduced" accomplishments | DOT&E FY2024 p2: software stop-test, manufacturing quality escapes |
| E4 | DOT&E FY2010 p30: TBR changes to flight-test planning parameters | GAO-09-303 p11: "delays in delivering test aircraft are expected to hamper and further compress test schedules" | GAO-07-360 p22: JSF planned "significantly more concurrent than the F-22A" |
| E5 | GAO-10-382 p31: software behind schedule; may delay first mission-system flight test | DOT&E FY2024 p2: operational-test timing and program description (off-topic) | DOT&E FY2010 p33: software development and flight-test patterns (off-topic for concurrency) |

Retrieval found directly relevant, explicit passages for all three questions. For Q04 three of the five passages state
the dependency in so many words; for Q08 two to three do. Each case also retrieved one or two off-topic passages.

## Hypotheses, scores, labels, validation and pruning

Scores are Doc / Eng / Model / Pred → total, where Model is pinned at 50. "Python" is the deterministic validation result.

**Q01** (depth 1, then depth 2 refinement)

| ID | Type | Cites | Scores → total | Label | Python | Outcome |
|---|---|---|---|---|---|---|
| D1.root.1 | DIRECT | E2 | 75/80/50/70 → 70.5 | STRONGLY_SUPPORTED | PASS | **survived** (preferred by review) |
| D1.root.2 | INDIRECT via software integration and test | E1, E4 | 75/80/50/70 → 70.5 | STRONGLY_SUPPORTED | PASS | **survived** |
| D1.root.3 | UNCERTAIN | E5 | 40/50/50/40 → 45.0 | WEAKLY_SUPPORTED | PASS | below threshold |
| D2.…1.2 | INDIRECT via software integration and test | E1, E5 | 75/70/50/80 → 69.5 | STRONGLY_SUPPORTED | PASS | below threshold |
| D2.…1.3 | UNCERTAIN | E3, E4 | 60/70/50/60 → 61.0 | INFERRED | PASS | below threshold |
| D2.…1.1, 2.1, 2.2 | DIRECT / DIRECT / INDIRECT | – | – | – | FAIL: duplicate | rejected before the critic |
| D2.…2.3 | UNCERTAIN | none | – | – | FAIL: no citation | rejected before the critic |

**Q04**

| ID | Type | Cites | Scores → total | Label | Python | Outcome |
|---|---|---|---|---|---|---|
| D1.root.1 | DIRECT | E1, E3 | 75/70/50/80 → **69.5** | STRONGLY_SUPPORTED | PASS | below threshold (by 0.5) |
| D1.root.2 | INDIRECT via reliability and maintainability improvements | E2 | 60/70/50/60 → 61.0 | INFERRED | PASS | below threshold |
| D1.root.3 | UNCERTAIN | E4, E5 | 60/50/50/40 → 51.0 | INFERRED | PASS | below threshold |

**Q08**

| ID | Type | Cites | Scores → total | Label | Python | Outcome |
|---|---|---|---|---|---|---|
| D1.root.1 | DIRECT | E1 | 75/70/50/60 → **65.5** | STRONGLY_SUPPORTED | PASS | below threshold |
| D1.root.2 | INDIRECT via software development | E2 | 75/70/50/60 → 65.5 | STRONGLY_SUPPORTED | PASS | below threshold |
| D1.root.3 | UNCERTAIN | E4, E5 | 40/50/50/30 → 43.0 | WEAKLY_SUPPORTED | PASS | below threshold |

## Findings

### 1. Did the generator produce meaningfully different hypotheses across the three cases?

**In content, yes. In structure, no.**

- **Content.** The generator cited different, mostly relevant passages per case and named case-specific mediators:
  "software integration and test", "reliability and maintainability improvements" and "software development".
- **Structure.** It produced exactly one DIRECT, one INDIRECT and one UNCERTAIN in every case. No RECIPROCAL or NONE,
  and never two competing variants of the same type.

Three weaknesses recur:
- **The UNCERTAIN alternative cites evidence that supports a dependency.** Q01 used E5 for it. Q04 used E4, which says
  aircraft delays "are expected to hamper and further compress test schedules". Q08 used E4 (the concurrency risk).
- **Assumptions overstate the claim.** Examples: Q04's "increase in flight tests is solely attributed to the availability
  of test aircraft"; Q01's "without other intervening factors". These are what the critic then penalises.
- **Some mediators are weak.** Q04's INDIRECT rests on E2, which does not mention aircraft delivery. Q08's "software
  development" is a different activity, not a link between test maturity and production commitment.

The Q04 DIRECT summary is also garbled: "hampered … as evidenced by the substantial increase in flight tests".

### 2. Did the critic discriminate among strong, partial and weak hypotheses?

**Partially.**

What worked:
- In all three cases the ranking was sensible: the best-supported positive hypothesis came first, and UNCERTAIN came
  last (Q01 45, Q04 51, Q08 43).
- Labels matched the anchor bands consistently: 75 ↔ STRONGLY_SUPPORTED, 60 ↔ INFERRED, 40 ↔ WEAKLY_SUPPORTED.
- The weak Q04 INDIRECT was correctly scored INFERRED (61.0).

Limits:
- **DIRECTLY_STATED was never used,** even for Q04's E1 and E3, which state the effect of late test-aircraft delivery
  on flight testing explicitly. The critic deducted for the generator's overreaching *assumption* rather than crediting
  the explicit *evidence*.
- **DIRECT and INDIRECT were tied exactly in two of three cases** (Q01 75/80/50/70; Q08 75/70/50/60). The critic does
  not separate the two types when both are "strongly supported".
- **No contradictions were listed in any case,** although Q04's E4 contradicts its UNCERTAIN hypothesis.
- **Q08 INDIRECT was over-scored.** It got STRONGLY_SUPPORTED (75) on E2, which talks about software in *past
  programs* generally.

### 3. Did ToT branching provide value beyond a single linear interpretation?

**Breadth helped; depth was barely exercised.**

What breadth added:
- In every case a null alternative was put next to the positive ones and scored explicitly. A linear pipeline would
  have produced one unchallenged claim.
- In Q01 the DIRECT/INDIRECT ambiguity is visible and is preserved in the verdict.

Depth:
- **Only Q01 refined (depth 2).** Its six refinements produced nothing better: three duplicates and one uncited
  hypothesis were rejected by Python before any critic call, and two were scored lower.
- **Q04 and Q08 stopped at depth 1,** because refinement only expands hypotheses that survive the threshold. Q04's
  DIRECT at 69.5 lost points to a fixable overstated assumption, but the design does not refine below-threshold branches.

### 4. Did the comparative review help explain ambiguity without overriding deterministic policy?

**Yes in Q01. Not exercised in Q04 or Q08.**

- In Q01 it separated two hypotheses the critic had scored identically. It preferred DIRECT for needing fewer
  intermediate assumptions and judged the numerical tie not genuine.
- The verdict stayed PARTIALLY_SUPPORTED, as the policy requires.
- Q04 and Q08 had no survivors, so the review correctly made no call (`NO_SURVIVORS`).

### 5. Were any critic/Python disagreements recorded?

**No.** There were zero disagreements in Q01 Run 3, Q04 and Q08, and every hypothesis that reached the critic passed
Python validation. The only disagreements found in this phase were the three from Q01 Run 1, identified retrospectively
by applying the new rules to that run's critic output. At depth 2 of Q01, Python's own checks rejected 4 hypotheses
before the critic (duplicates and a missing citation), as designed.

### 6. Does the architecture appear sufficiently functional for the class-capstone demonstration?

**Yes, as a working, auditable architecture, with clearly stated analytical limits.**

What it demonstrates:
- All three cases ran end to end through the full pipeline: retrieve → evidence objects → generator → deterministic
  validation → individual critic → bounded ToT → comparative review → decision → trace.
- Each run stayed within budget, and every case produced complete, labelled JSON and Markdown traces.
- The deterministic layer behaved correctly throughout: validation, duplicate rejection, Python-owned hard
  constraints, threshold pruning, and stop conditions.
- No decision was forced. Two of the three cases honestly returned UNRESOLVED.

What it does not yet demonstrate is well-calibrated analytical judgement. The system is **conservative**: it
under-credits dependencies that the sources state explicitly. Q04 is the clearest case; in my reading three of its five
passages state the dependency outright, yet the result is UNRESOLVED at 69.5. Two structural reasons, both observable
in the traces:

1. **The threshold sits on the critic's modal score.** With model consistency pinned at 50, a total of 70 needs the
   other three criteria to average 75 (by weight). 75 is exactly where the critic places "strongly supported" evidence.
   The three positive outcomes landed at 70.5, 69.5 and 65.5, so verdicts are decided by ±0.5 points.
2. **Generator overreach is scored, not corrected.** Overstated assumptions lower the critic's scores, and a
   sub-threshold branch is never refined, so a sound dependency can be lost to wording.

These are findings to report, not to tune away here. Thresholds, weights and prompts were left unchanged by design.

## Limitations

- One run per case with one model (`gpt-4o-mini`). Earlier Q01 runs showed generator variation at temperature 0, and
  outcomes sit within ±0.5 of the threshold. A rerun could change verdicts.
- The MVP activity pairs for Q04 and Q08 were defined for this exercise. Q08's compound target ("Production Commitment
  / Rework Risk") asks for more than the evidence states: the passages discuss cost and schedule risk and production
  before testing, not rework. That likely lowered the scores.
- No human-annotated ground truth exists for these dependencies. "Clearly documented" above is my reading of the
  retrieved passages, not a validated label.
- This is not publication-level validation.
