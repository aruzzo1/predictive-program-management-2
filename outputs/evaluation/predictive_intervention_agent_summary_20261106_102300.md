# Predictive Simulation and Intervention Agent: episode summary (validation contract v2)

> The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35 outcomes.

- Trace: `outputs/agentic_traces/predictive_intervention_agent_20261106_102300.json` (and `.md`)
- Mode: REAL_LLM_MODE; model: gpt-4o-mini; status: **COMPLETED_WITH_VALIDATION_ERRORS**; usable downstream: **False**
- Tokens: {'provider': 'openai-responses', 'model': 'gpt-4o-mini', 'successful_responses': 1, 'input_tokens': 4958, 'output_tokens': 1780}; elapsed 15.67 s
- One run; not repeated or tuned.

## Validation

- Result: **FAIL**; error counts: {'structure': 0, 'citation': 0, 'numeric': 0, 'qualitative': 2, 'objective': 3, 'coverage': 0, 'human_review': 0}
- Error: CASE_1.alters_propagation_upstream_of_D8: claimed False, deterministic True
- Error: CASE_2.alters_propagation_upstream_of_D8: claimed False, deterministic True
- Error: LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: prefers CASE_3, but ['CASE_1', 'CASE_2'] attain(s) a strictly lower cumulative D8 exposure committed before maturity (all of it for cases without staging)
- Error: secondary_options[0] CASE_2: effect claimed REDUCED, deterministic ELIMINATED
- Error: secondary_options[0] CASE_2: is_minimum_for_objective False, deterministic True
- Human review reasons: synthetic capstone scenario: decision support only, qualitative validation failed, objective validation failed

## Objective preferences vs deterministic minimum

| Objective | Agent prefers | Minimum | Agreement |
|---|---|---|---|
| MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE | CASE_1 | CASE_1 | MATCH |
| PROTECT_FLIGHT_TEST_EXECUTION | CASE_2 | CASE_1, CASE_2 | SUBSET_OF_TIE |
| LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE | CASE_3 | CASE_1, CASE_2 | DIFFERS |

## Overall recommendation (raw model text)

The choice of intervention depends on the specific management objective: complete elimination of disturbances favors INTERVENTION_1, while protecting flight test execution favors INTERVENTION_2, and limiting pre-maturity production exposure favors INTERVENTION_3.

See the trace for structured claim checks, citations with Python-attached values, and the full interpretation.
