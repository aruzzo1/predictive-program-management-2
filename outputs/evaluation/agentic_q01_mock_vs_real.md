# Agentic Q01: MOCK_AGENT_MODE vs REAL_LLM_MODE

Episode: **A1 Mission-System Software Maturity → A2 Flight-Test Execution**
Query (Q01): *What evidence indicates that mission-system software maturity affected F-35 flight-test execution?*
Retrieval: HYBRID_RERANKED_V2_1, top_k 5. Orchestration: LangGraph. ToT config unchanged (successors 3, beam 3,
depth 3, threshold 70, near tie 5, budget 20).

| | MOCK_AGENT_MODE | REAL_LLM_MODE |
|---|---|---|
| Trace | `outputs/agentic_traces/episode_20261025_163132_A1_A2.{json,md}` | `outputs/agentic_traces/episode_20261030_132058_A1_A2.{json,md}` |
| Generator / critic | Rule-based stand-ins (text features) | OpenAI `gpt-4o-mini`, Responses API, strict structured output, temperature 0, separate stateless calls |
| Model calls | 6 (mock, counted) | 4 (1 generator + 3 critic) |
| Tokens | n/a | 6,961 in / 688 out |
| Elapsed | 18.1 s | 59.7 s (both include embedding/reranker load) |
| Depth reached | 2 | 1 |
| Stop status | NO_NEW_CANDIDATES | NO_VIABLE_CANDIDATE |
| **Decision** | **PARTIALLY_SUPPORTED**, DIRECT, 82.5 (near tie with INDIRECT 77.5) | **UNRESOLVED**: no hypothesis survived |

The retrieved evidence was **identical** in both runs: same five chunks, same order (E1 DOTE p33 c05, E2 DOTE p29 c02,
E3 DOTE p33 c03, E4 DOTE p30 c05, E5 GAO-10-382 p31 c01). Every difference below comes from the generator and critic.

## Hypotheses (depth 1)

| ID | MOCK | REAL |
|---|---|---|
| D1.root.1 | DIRECT, cites E1–E5 | DIRECT, cites **E2** only |
| D1.root.2 | INDIRECT via `integrat*` (keyword stem), cites E1–E5 | INDIRECT via **"software integration and test"**, cites E1, E4 |
| D1.root.3 | NONE, cites E1 | **UNCERTAIN**, cites E5 |

Real generator:
- Cites selectively. The mock cites every passage. The real DIRECT hypothesis cites only E2, the passage that says the
  claim outright: "Development of mission systems software continued to experience delays that affected flight test progress."
- Names a real mediating activity. "Software integration and test" is grounded in E1 ("Mission systems labs and CATB
  are important to software integration and test … integration precedes verification events"). The mock used a keyword stem.
- Proposes UNCERTAIN as the null alternative instead of NONE, which is the softer choice the prompt allows.
- Weaknesses: E3 ("discovery in flight test, and deferrals to later increments") is never cited. E5 is used for
  UNCERTAIN, although it supports a dependency ("Further delays may affect the already delayed first mission system flight
  test"). The DIRECT assumption ("without other intervening factors") is stronger than the evidence needs. Assumptions are generic.
- All three hypotheses passed deterministic Python validation: the cited IDs exist, the chunks were retrieved, the
  activities are correct and the INDIRECT mediator is named.

## Critic assessments

| ID | MOCK Doc/Eng/Model/Pred → total | REAL Doc/Eng/Model/Pred → total | REAL hard constraint |
|---|---|---|---|
| D1.root.1 DIRECT | 95/90/50/85 → 82.5, pass | 80/70/50/75 → **70.0** | **FAIL**: "cites no evidence, or cites IDs that are not in the retrieved evidence" |
| D1.root.2 INDIRECT | 95/80/50/75 → 77.5, pass | 70/80/50/75 → **70.0** | **FAIL**: "cites no evidence that directly supports the indirect relationship" |
| D1.root.3 NONE / UNCERTAIN | 40/30/50/30 → 37.0, FAIL (stated dependency contradicts NONE) | 0/0/50/0 → 10.0 | FAIL: "cites no evidence that definitively establishes …" |

The real critic:
- Kept the model-consistency criterion at 50 (neutral, no DSM) on every hypothesis, as instructed.
- Gave sub-scores that are moderate and plausible. The Python-computed totals for DIRECT and INDIRECT land exactly on the threshold (70.0).
- **Misapplied the hard constraints.** The failure it gives for D1.root.1 is the hard-constraint rule copied word for word
  from the prompt, and it is **factually false**: E2 exists, was returned by retrieval, and passed deterministic
  validation. The critic's own summary says E2 shows software delays "affecting flight test progress" but "does not
  explicitly confirm a direct correlation". That is a judgement about how strong the evidence is, which belongs in
  `documentary_evidence_score`, not in a hard-constraint failure. The failures for D1.root.2 and D1.root.3 have the same
  problem: "insufficiently direct support" is presented as "cites no evidence".
- Scored the UNCERTAIN hypothesis 0 on documentary, engineering and predictive. That reads as the critic penalising a
  null claim for not asserting a dependency, rather than judging whether the uncertainty is justified.

## ToT behaviour

- **MOCK:** two hypotheses survived in a near tie (82.5 vs 77.5), so the search refined to depth 2. The refinements were
  rejected as duplicates, and the run stopped with NO_NEW_CANDIDATES. The decision was PARTIALLY_SUPPORTED (DIRECT, near tie with INDIRECT).
- **REAL:** all three hypotheses were rejected at depth 1 on the critic's hard-constraint flags, so the run stopped with
  NO_VIABLE_CANDIDATE and the decision was UNRESOLVED. No refinement, beam or budget logic was exercised beyond depth 1.
- Without the hard-constraint flags, DIRECT and INDIRECT would both have reached the threshold, tied at 70.0 (70.0 is not
  below 70). The controller would then have refined to depth 2. The final outcome of that path cannot be inferred from this run.
- The controller behaved as designed. The deterministic layer enforced everything it checks. However, it treats a critic
  `hard_constraint_pass = false` as final, and nothing checks whether the critic's stated reason is true. Python validation
  can make the critic stricter but cannot overrule a false failure.

## Assessment

In my reading, the UNRESOLVED outcome comes from **critic error, not from the evidence**: E2 states the dependency in the
source's own words, and E5 and E3 corroborate it. The mock's PARTIALLY_SUPPORTED DIRECT outcome is closer to what a human
reader would conclude, but the mock reached it by keyword rules and it is not analysis. Neither result should be treated as
an analytical finding yet.

What the real run does show:
1. The Responses API structured-output path works end to end. All 4 responses parsed into the Pydantic schemas, with no
   schema, refusal or API errors.
2. Generator quality is clearly better than the mock: selective citations, a grounded mediator, an explicit null alternative.
3. The critic (gpt-4o-mini with the current prompt) mixes up *weak support* with *hard-constraint violation*. This is the
   main issue to address before the real pipeline's decisions mean anything.

## Limitations of this comparison

- n = 1 run, one question, one model. Temperature 0 does not guarantee identical output on a rerun.
- The mock run is from 2026-10-25 and the real run from 2026-10-30. Retrieval output was verified identical.
- No prompt, threshold or retrieval change was made between runs. This compares modes, not tuned configurations.
- "Maturity" vs "delays": the evidence speaks of software delays and development problems, not maturity metrics as
  such. A careful critic could fairly lower the documentary score for that gap. It is not a hard-constraint violation.
