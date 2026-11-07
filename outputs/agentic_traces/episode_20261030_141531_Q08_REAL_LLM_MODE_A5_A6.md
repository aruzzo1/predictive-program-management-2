# Dependency reasoning episode: Development / Test Maturity → Production Commitment / Rework Risk

> **REAL_LLM_MODE.** Generator and critic are separate, stateless calls to gpt-4o-mini (openai-responses, structured output, temperature 0). Hypotheses and sub-scores are model output; validation, the weighted total, pruning and the decision are deterministic Python. Tokens: 9438 in / 1066 out over 4 successful responses.

- Case: **Q08** (REAL_LLM_MODE)
- Query: *What evidence describes dependencies between F-35 development testing and production decisions (development-test-production concurrency)?*
- Activities: A5 Development / Test Maturity (test); A6 Production Commitment / Rework Risk (production)
- Retrieval: HYBRID_RERANKED_V2_1, top_k 5; orchestration: langgraph
- ToT config: {'max_successors': 3, 'beam_width': 3, 'max_depth': 3, 'score_threshold': 70.0, 'near_tie': 5.0, 'max_model_calls': 20}
- Model calls: 4, of which comparative review: 0; depth reached 1; stop status **NO_VIABLE_CANDIDATE**; elapsed 30.87 s

## Retrieved evidence

| ID | Source | PDF p. | Chunk | Rank | Excerpt |
|---|---|---|---|---|---|
| E1 | GAO-07-360 (2007-03-15) | 7 | `GAO-07-360-p007-c00` | 1 | The degree of concurrency between development and production in the JSF program’s acquisition strategy still includes significant risks for cost and schedule overruns or late delivery of promised capabilities to the warf… |
| E2 | GAO-07-360 (2007-03-15) | 20 | `GAO-07-360-p020-c02` | 2 | Past programs have encountered difficulties in developing software, which delayed flight test schedules. JSF program officials acknowledged that the software effort will become particularly challenging during 2007 and 2… |
| E3 | DOTE-FY2024-F35 (undated) | 2 | `DOTE-FY2024-F35-p002-c00` | 3 | The F-35 development effort too was facing challenges in delivering reliable, fully functional software to the operational test (OT) teams. In February 2024, the United Operational Test Team (UOTT) called for a “stop tes… |
| E4 | GAO-07-360 (2007-03-15) | 22 | `GAO-07-360-p022-c00` | 4 | While some concurrency may be beneficial to efficiently transition from the development stage of a program to production, the JSF is currently planned to be significantly more concurrent than the F-22A program that faile… |
| E5 | DOTE-FY2010-F35 (undated) | 33 | `DOTE-FY2010-F35-p033-c03` | 5 | F-35 mission systems software development and test is tending towards familiar historical patterns of extended development, discovery in flight test, and deferrals to later increments. The modifications recommended by t… |

## Hypotheses and critic assessments

| Hypothesis | Depth | Type | Cites | Valid | Doc (30%) | Eng (30%) | Model (20%) | Pred (20%) | Total | Hard constraints |
|---|---|---|---|---|---|---|---|---|---|---|
| D1.root.1 | 1 | DIRECT | E1 | yes | 75 | 70 | 50 | 60 | **65.5** | pass (Python: PASS) |
| D1.root.2 | 1 | INDIRECT via Software Development | E2 | yes | 75 | 70 | 50 | 60 | **65.5** | pass (Python: PASS) |
| D1.root.3 | 1 | UNCERTAIN | E4, E5 | yes | 40 | 50 | 50 | 30 | **43.0** | pass (Python: PASS) |

Reasoning summaries:

- **D1.root.1**: The evidence indicates that the concurrency between development and production in the JSF program has significant risks, suggesting that the lack of completed testing directly affects the production commitment and associated rework risks. Assumptions: The risks mentioned in the evidence are directly linked to the production commitment and rework risk.
- **D1.root.2**: The evidence suggests that challenges in software development delayed flight test schedules, which in turn affects the production commitment and increases the risk of rework due to untested systems. Assumptions: Software development issues are a significant intermediate factor affecting flight testing and subsequently production decisions.
- **D1.root.3**: The evidence presents various challenges and risks associated with concurrency but does not definitively establish a clear dependency between development testing and production commitment, leaving the relationship ambiguous. Assumptions: The evidence does not provide a clear causal link between development testing outcomes and production commitment.

Critic findings (qualitative; expressed through the scores, never a structural rejection):

- **D1.root.1** [STRONGLY_SUPPORTED]: The hypothesis is reasonably supported by the evidence, indicating a strong relationship between development/test maturity and production commitment/rework risk. However, the direct link to rework risk is not explicitly stated, which introduces some uncertainty. *Evidence strength:* The evidence indicates significant risks associated with the concurrency between development and production in the JSF program, suggesting that incomplete testing affects production commitment and rework risks. For instance, it states that 'the degree of concurrency... includes significant risks for cost and schedule overruns.' This supports the hypothesis but requires some interpretation regarding the direct impact on production commitment and rework risk. *Contradictions:* none. *Unsupported assumptions:* The risks mentioned in the evidence are directly linked to the production commitment and rework risk.. *Other concerns:* The evidence does not explicitly link the risks to rework risk, leaving some ambiguity..
- **D1.root.2** [STRONGLY_SUPPORTED]: The hypothesis is reasonably supported by the evidence, particularly in terms of the relationship between software development challenges and flight test delays. However, the assumption that these challenges are a significant intermediate factor lacks direct support, which introduces some uncertainty regarding the overall strength of the dependency. *Evidence strength:* The evidence indicates that challenges in software development have delayed flight test schedules, which aligns with the hypothesis that these delays affect production commitment and increase rework risk. Specifically, E2 states that past programs faced software development difficulties that delayed flight tests, supporting the indirect relationship proposed in the hypothesis. *Contradictions:* none. *Unsupported assumptions:* Software development issues are a significant intermediate factor affecting flight testing and subsequently production decisions.. *Other concerns:* The assumption regarding the significance of software development issues as an intermediate factor is not explicitly supported by the evidence, which may limit the strength of the hypothesis..
- **D1.root.3** [WEAKLY_SUPPORTED]: Overall, the evidence presents a weak connection between development testing and production commitment, primarily highlighting risks without establishing a clear causal relationship. The assumptions made in the hypothesis are not strongly supported by the evidence. *Evidence strength:* The evidence discusses challenges and risks associated with concurrency in development and production but does not explicitly establish a clear dependency between development testing and production commitment. For example, E4 mentions that while some concurrency may be beneficial, the JSF program is significantly more concurrent than previous programs, which raises concerns about timely delivery and capability. This suggests a potential relationship but lacks direct evidence of causation. *Contradictions:* none. *Unsupported assumptions:* The evidence does not provide a clear causal link between development testing outcomes and production commitment.. *Other concerns:* The hypothesis remains ambiguous due to the lack of definitive evidence linking development testing to production commitment..

## Critic / Python validation disagreements

Hard constraints are owned by deterministic Python validation; a critic's hard-failure claim is advisory and is compared with Python's result.

None recorded.

## Pruning decisions

| Depth | Hypothesis | Action | Score | Reason |
|---|---|---|---|---|
| 1 | D1.root.1 | REJECTED | 65.5 | BELOW THRESHOLD (65.5 < 70.0) |
| 1 | D1.root.2 | REJECTED | 65.5 | BELOW THRESHOLD (65.5 < 70.0) |
| 1 | D1.root.3 | REJECTED | 43.0 | BELOW THRESHOLD (43.0 < 70.0) |

## Comparative review of survivors

One advisory call after pruning; it cannot rescore, revive a pruned hypothesis or change validation.

- Status: **NO_SURVIVORS** (REAL_LLM_MODE); comparative model calls: 0
- Reviewed (survivors, score order): none
- Preferred: -; agrees with score ranking: -
- Near tie: numerical (Python) -; judged genuine by reviewer -

## Decision

**UNRESOLVED**: - (hypothesis -, critic score -), evidence [].

No hypothesis survived validation, hard constraints and the score threshold.

## Events

- retrieved 5 passages via HYBRID_RERANKED_V2_1
- [graph] retrieve_evidence
- depth 1: generator expanded root -> ['D1.root.1', 'D1.root.2', 'D1.root.3'] (REAL_LLM_MODE)
- [graph] generate_hypotheses (depth 1)
- [graph] route after prune: decide (status NO_VIABLE_CANDIDATE)
- comparative review: NO_SURVIVORS
