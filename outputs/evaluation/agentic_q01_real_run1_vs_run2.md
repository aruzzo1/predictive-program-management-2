# Agentic Q01: REAL_LLM_MODE Run 1 vs Run 2 (validation-ownership fix)

Episode: **A1 Mission-System Software Maturity → A2 Flight-Test Execution**.
Query (Q01): *What evidence indicates that mission-system software maturity affected F-35 flight-test execution?*
Fixed across both runs: retrieval HYBRID_RERANKED_V2_1 top 5, corpus, `gpt-4o-mini`, temperature 0, ToT config
(successors 3, beam 3, depth 3, threshold 70, near tie 5, budget 20), the Checkpoint 4.1 weights (30/30/20/20), the
generator prompt, LangGraph orchestration.

| | Run 1 (before fix) | Run 2 (after fix) |
|---|---|---|
| Trace | `outputs/agentic_traces/episode_20261030_132058_A1_A2.{json,md}` | `outputs/agentic_traces/episode_20261030_134626_A1_A2.{json,md}` |
| Who sets `hard_constraint_pass` | LLM critic (AND-ed with its failure list) | Deterministic Python only. Critic claim is advisory |
| Critic prompt | Critic listed and enforced the hard constraints | Critic told that structural validation is done by Python. Validity ≠ strength. Weak support lowers scores |
| Critic output schema | scores + `hard_constraint_pass` + `hard_constraint_failures` + summary | scores + `evidence_strength_summary`, `contradictions`, `unsupported_assumptions`, `critic_concerns`, advisory `critic_claimed_hard_failure(_reasons)`, summary |
| Model calls | 4 (1 generator + 3 critic) | 4 (1 generator + 3 critic) |
| Tokens | 6,961 in / 688 out | 8,613 in / 992 out (longer critic prompt and richer output) |
| Depth / stop status | 1 / NO_VIABLE_CANDIDATE | 1 / NO_VIABLE_CANDIDATE |
| **Decision** | **UNRESOLVED** | **UNRESOLVED** |
| **Why** | All three rejected on **critic-asserted hard-constraint failures**, one of them factually false | All three **passed** Python's hard constraints and were rejected **below threshold** on the critic's qualitative scores |

Retrieved evidence was identical in both runs (E1 DOTE p33 c05, E2 DOTE p29 c02, E3 DOTE p33 c03, E4 DOTE p30 c05,
E5 GAO-10-382 p31 c01).

## Hypotheses and evidence IDs

| ID | Run 1 | Run 2 |
|---|---|---|
| D1.root.1 | DIRECT, cites E2 | DIRECT, cites E2 |
| D1.root.2 | INDIRECT via "software integration and test", cites **E1, E4** | INDIRECT via "software integration and test", cites **E1** |
| D1.root.3 | UNCERTAIN, cites E5 | UNCERTAIN, cites E5 |

**The generator changed between runs, although its prompt and code did not.** INDIRECT dropped E4, and the
assumptions were reworded. For example, DIRECT's "without other intervening factors" became "the delays … are
significant enough to impact flight test execution". This is sampling variation at temperature 0. It means the
Run 1 → Run 2 differences mix two causes: the critic fix and the generator's own variation. Both runs leave E3 uncited,
and both use E5 (which supports a dependency) for UNCERTAIN.

## Deterministic validation, critic scores, disagreements and pruning

| ID | Python validation (both runs) | Run 1 Doc/Eng/Model/Pred → total; hard constraint | Run 2 Doc/Eng/Model/Pred → total; hard constraint | Run 2 pruning |
|---|---|---|---|---|
| D1.root.1 DIRECT | PASS | 80/70/50/75 → 70.0; **FAIL** ("cites no evidence, or cites IDs that are not in the retrieved evidence") | 70/60/50/70 → **63.0**; PASS | BELOW THRESHOLD |
| D1.root.2 INDIRECT | PASS | 70/80/50/75 → 70.0; **FAIL** ("cites no evidence that directly supports …") | 40/60/50/30 → **46.0**; PASS | BELOW THRESHOLD |
| D1.root.3 UNCERTAIN | PASS | 0/0/50/0 → 10.0; **FAIL** ("cites no evidence that definitively establishes …") | 30/40/50/20 → **35.0**; PASS | BELOW THRESHOLD |

- **Run 1 disagreements.** Run 1 had no field for them, so none were recorded. Applying the new rules to Run 1's critic
  outputs gives **3 disagreements**: Python PASS vs critic FAIL on all three hypotheses. The D1.root.1 claim is
  objectively false, because E2 exists and was retrieved. With those claims treated as advisory, D1.root.1 and D1.root.2
  would have survived at exactly 70.0, tied, and the search would have refined to depth 2. Those are Run 1's scores
  under Run 1's prompt. This is a statement about how the new rules treat that output, not a prediction of a rerun.
- **Run 2 disagreements: none.** The critic set `critic_claimed_hard_failure = false` for every hypothesis. The
  disagreement mechanism was therefore **not exercised live**. It is covered by unit tests only.
- **Model consistency.** It was 50 on every hypothesis in both runs. In Run 2 the critic returned 50 itself, so the
  Python pin did not have to intervene.

## Critic concerns (Run 2, new fields)

- **DIRECT (E2):** "E2 indicates that delays in mission systems software development have affected flight test
  progress … however, the evidence does not explicitly state a direct causal relationship". It flagged the assumption
  that the delays were "significant enough to impact flight test execution" as unsupported, and raised a concern that
  the effect may be "correlational". No contradictions listed.
- **INDIRECT (E1):** E1 shows integration and test matters to flight test, but does not say that software maturity
  acts *through* integration and test. The mediating-step assumption is flagged as unsupported.
- **UNCERTAIN (E5):** the evidence suggests "a correlation between software delays and flight-test challenges but
  does not confirm a causal relationship". No contradictions listed.

## Is the responsibility boundary cleaner and more internally consistent?

**The boundary: yes.**
- In Run 1, three branches were rejected on structural grounds that Python had already verified as false. The pruning
  reason ("HARD CONSTRAINT: cites no evidence") contradicted the trace's own validation column ("Valid: yes").
- In Run 2, no structural claim conflicts with Python. Every rejection is a sub-threshold score from documented
  sub-scores with written rationale. The `hard_constraint_pass` field means one thing: Python's verdict.
- Had the critic made a false claim, it would have been recorded as a disagreement, kept in the trace, and not acted on.

**The analysis: not demonstrably better.** The verdict is unchanged, and the critic's qualitative judgement still has
visible problems, now in the right lane:
- **It may be miscalibrated on DIRECT.** E2 states in the source's own words that software delays "affected flight test
  progress". The critic still calls that assumption "unsupported" and raises "correlational" doubts about an explicit
  documentary causal statement. Reasonable readers could score this differently. The real gap is "maturity" vs
  "delays", and the critic does not mention it.
- **Its judgements are inconsistent across hypotheses.** It says that the evidence lacks a clear causal link (arguing
  for UNCERTAIN) and also scores UNCERTAIN lowest (35.0). Each hypothesis is judged in isolation, so the critic never
  weighs the alternatives against each other.
- **It lists no contradictions anywhere**, although E2 arguably contradicts the UNCERTAIN claim that the evidence
  "does not specify direct impacts on flight tests".
- **The scores dropped broadly.** DIRECT fell from 70.0 to 63.0 and INDIRECT from 70.0 to 46.0. Part of this is plausibly
  the new prompt's instruction that weak support must lower scores. Part may be run-to-run variation. One run cannot
  separate the two.

Because the threshold, weights and prompt were not tuned to Q01, this UNRESOLVED is an honest product of the current
critic's calibration, not of a structural defect.

## Limitations

- n = 1 run per configuration. The generator varied between runs at temperature 0, so the effect of the fix on the
  scores cannot be isolated from sampling variation.
- The live run did not exercise the disagreement path. The new prompt tells the critic that Python validates structure,
  which plausibly suppresses false claims. That is intended, but it also makes the disagreement rate a weaker probe of
  critic reliability.
- The critic judges each hypothesis independently and never compares alternatives, which allows the cross-hypothesis
  inconsistency noted above.
