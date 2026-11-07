# Dependency reasoning episode: Test-Aircraft Availability → Flight-Test Execution / Schedule

> **REAL_LLM_MODE.** Generator and critic are separate, stateless calls to gpt-4o-mini (openai-responses, structured output, temperature 0). Hypotheses and sub-scores are model output; validation, the weighted total, pruning and the decision are deterministic Python. Tokens: 9695 in / 1181 out over 4 successful responses.

- Case: **Q04** (REAL_LLM_MODE)
- Query: *What evidence describes how late delivery or limited availability of F-35 test aircraft constrained the sequence or pace of flight testing?*
- Activities: A3 Test-Aircraft Availability (test); A4 Flight-Test Execution / Schedule (test)
- Retrieval: HYBRID_RERANKED_V2_1, top_k 5; orchestration: langgraph
- ToT config: {'max_successors': 3, 'beam_width': 3, 'max_depth': 3, 'score_threshold': 70.0, 'near_tie': 5.0, 'max_model_calls': 20}
- Model calls: 4, of which comparative review: 0; depth reached 1; stop status **NO_VIABLE_CANDIDATE**; elapsed 35.1 s

## Retrieved evidence

| ID | Source | PDF p. | Chunk | Rank | Excerpt |
|---|---|---|---|---|---|
| E1 | GAO-11-325 (2011-04-07) | 17 | `GAO-11-325-p017-c00` | 1 | Although still hampered as in prior years by the late delivery of test aircraft, flight tests substantially increased in volume and pace at the two main government test sites--Edwards Air Force Base, California, for CTOL… |
| E2 | DOTE-FY2010-F35 (undated) | 33 | `DOTE-FY2010-F35-p033-c04` | 2 | in previous schedules are not achievable in the flight test program until changes are made to all variants that improve reliability and maintainability in flight test operations. Additionally, the process must begin to… |
| E3 | GAO-11-325 (2011-04-07) | 31 | `GAO-11-325-p031-c03` | 3 | programs have failed to demonstrate that the system works as intended before entering production, discovering costly design problems late in development when the more complex software and advanced capabilities are integr… |
| E4 | GAO-09-303 (2009-03-12) | 11 | `GAO-09-303-p011-c02` | 4 | Continuing delays in delivering test aircraft are expected to hamper and further compress test schedules. In particular, the joint team projects that the two aircraft dedicated to carrier suitability tests will be late… |
| E5 | DOTE-FY2024-F35 (undated) | 2 | `DOTE-FY2024-F35-p002-c01` | 5 | DOT&E assesses that dedicated operational testing of these aircraft will not occur until mid to late FY26, approximately two years after the configuration began delivery to the field. DESCRIPTION The F-35 Joint Strike F… |

## Hypotheses and critic assessments

| Hypothesis | Depth | Type | Cites | Valid | Doc (30%) | Eng (30%) | Model (20%) | Pred (20%) | Total | Hard constraints |
|---|---|---|---|---|---|---|---|---|---|---|
| D1.root.1 | 1 | DIRECT | E1, E3 | yes | 75 | 70 | 50 | 80 | **69.5** | pass (Python: PASS) |
| D1.root.2 | 1 | INDIRECT via Reliability and maintainability improvements | E2 | yes | 60 | 70 | 50 | 60 | **61.0** | pass (Python: PASS) |
| D1.root.3 | 1 | UNCERTAIN | E4, E5 | yes | 60 | 50 | 50 | 40 | **51.0** | pass (Python: PASS) |

Reasoning summaries:

- **D1.root.1**: The late delivery of test aircraft directly hampered the pace of flight testing, as evidenced by the substantial increase in flight tests despite the ongoing delays. This indicates a direct dependency where the availability of aircraft affects the execution of flight tests. Assumptions: The increase in flight tests is solely attributed to the availability of test aircraft and not other factors.
- **D1.root.2**: The late delivery of test aircraft indirectly affected the flight-test execution by necessitating changes to improve reliability and maintainability, which are prerequisites for effective flight testing. This suggests that the delivery issues led to intermediate activities that ultimately constrained the flight-test schedule. Assumptions: Improvements in reliability and maintainability are necessary for the flight tests to proceed effectively.
- **D1.root.3**: The evidence presents conflicting information regarding the extent to which late delivery of test aircraft affects flight testing. While some passages indicate a direct impact, others suggest that other factors, such as technical issues and uncertainties, also play significant roles, leading to uncertainty about the dependency. Assumptions: The relationship between aircraft delivery and flight testing is influenced by multiple factors, making it difficult to ascertain a clear dependency.

Critic findings (qualitative; expressed through the scores, never a structural rejection):

- **D1.root.1** [STRONGLY_SUPPORTED]: The hypothesis is reasonably supported by the evidence, indicating a strong relationship between aircraft availability and flight test execution. However, the assumption that the increase in flight tests is solely due to aircraft availability is not fully supported, introducing some uncertainty. *Evidence strength:* The evidence indicates that late delivery of test aircraft has hampered flight testing, with E1 stating that flight tests increased despite ongoing delays, suggesting a direct relationship. However, the evidence does not explicitly state that the increase in flight tests is solely due to aircraft availability, requiring some inference. *Contradictions:* none. *Unsupported assumptions:* The increase in flight tests is solely attributed to the availability of test aircraft and not other factors.. *Other concerns:* The evidence does not clarify the extent to which other factors may have influenced the pace of flight testing..
- **D1.root.2** [INFERRED]: The hypothesis presents a plausible indirect relationship between late delivery of test aircraft and flight-test execution through the lens of reliability and maintainability improvements. However, the evidence does not directly confirm this causal pathway, leading to a moderate score for documentary evidence. The assumptions made in the hypothesis are not fully supported by the evidence, raising concerns about its overall validity. *Evidence strength:* The evidence suggests that improvements in reliability and maintainability are necessary for effective flight testing, as indicated in E2, which states that changes must be made to improve these aspects before previous schedules can be achieved. However, it does not explicitly state that the late delivery of test aircraft directly caused these improvements, requiring inference. Thus, the support is plausible but not definitive. *Contradictions:* none. *Unsupported assumptions:* Improvements in reliability and maintainability are necessary for the flight tests to proceed effectively.. *Other concerns:* The hypothesis relies on the assumption that reliability and maintainability improvements are directly linked to the late delivery of test aircraft, which is not explicitly supported by the evidence..
- **D1.root.3** [INFERRED]: The hypothesis presents an uncertain dependency between test aircraft availability and flight-test execution/schedule. While there is some evidence suggesting a relationship, it is not definitively established due to the influence of other factors. This uncertainty affects the overall strength of the hypothesis. *Evidence strength:* The evidence suggests that late delivery of test aircraft has an impact on flight testing, but it also indicates that other factors, such as technical issues and uncertainties, play significant roles. For example, E4 states that delays in delivering test aircraft are expected to hamper test schedules, which implies a dependency, but it does not establish it as a direct cause. Thus, the support is inferred rather than explicitly stated. *Contradictions:* none. *Unsupported assumptions:* The relationship between aircraft delivery and flight testing is influenced by multiple factors, making it difficult to ascertain a clear dependency.. *Other concerns:* The evidence presents conflicting information regarding the extent of the impact of late aircraft delivery on flight testing, leading to uncertainty about the dependency..

## Critic / Python validation disagreements

Hard constraints are owned by deterministic Python validation; a critic's hard-failure claim is advisory and is compared with Python's result.

None recorded.

## Pruning decisions

| Depth | Hypothesis | Action | Score | Reason |
|---|---|---|---|---|
| 1 | D1.root.1 | REJECTED | 69.5 | BELOW THRESHOLD (69.5 < 70.0) |
| 1 | D1.root.2 | REJECTED | 61.0 | BELOW THRESHOLD (61.0 < 70.0) |
| 1 | D1.root.3 | REJECTED | 51.0 | BELOW THRESHOLD (51.0 < 70.0) |

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
