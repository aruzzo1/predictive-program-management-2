# Predictive Simulation and Intervention Agent: episode summary (validation contract v3)

> The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35 outcomes.

- Trace: `outputs/agentic_traces/predictive_intervention_agent_20261106_104715.json` (and `.md`)
- Mode: REAL_LLM_MODE; model: gpt-4o-mini; status: **COMPLETED_WITH_VALIDATION_ERRORS**; usable downstream: **False**
- Tokens: {'provider': 'openai-responses', 'model': 'gpt-4o-mini', 'successful_responses': 1, 'input_tokens': 5240, 'output_tokens': 1509}; elapsed 112.92 s
- One run; not repeated or tuned.

## Validation

- Result: **FAIL**; error counts: {'structure': 0, 'citation': 7, 'numeric': 0, 'qualitative': 1, 'objective': 4, 'narrative': 1, 'coverage': 4, 'human_review': 0}
- Error: comparative_claims[2]: unknown id 'CASE_0.cumulative_D8_committed_pre_maturity'
- Error: LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: unknown id 'CASE_0.cumulative_D8_committed_pre_maturity'
- Error: management_tradeoffs[0]: unknown id 'INTERVENTION_3_note'
- Error: no_action_assessment: must cite at least one FACT id
- Error: overall_recommendation: must cite at least one FACT id
- Error: management_tradeoffs[0]: must cite at least one FACT id
- Error: no_action_assessment must cite CASE_0 facts
- Error: prose contradicts D8 entering (ELIMINATED) in CASE_2.what_it_does_not_change: 'D8 exposure remains unchanged;'
- Error: MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE: prefers CASE_2, but ['CASE_1'] attain(s) a strictly lower cumulative total disturbance (t0..t12)
- Error: LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: prefers CASE_3, but ['CASE_1', 'CASE_2'] attain(s) a strictly lower cumulative D8 exposure committed before maturity (all of it for cases without staging)
- Error: preferred_for_total_disturbance: selects CASE_2, but ['CASE_1'] attain(s) a strictly lower cumulative total disturbance (t0..t12)
- Error: preferred_for_production_commitment: selects CASE_3, but ['CASE_1', 'CASE_2'] attain(s) a strictly lower cumulative D8 exposure committed before maturity (all of it for cases without staging)
- Error: free text contradicts preferred_for_total_disturbance in overall_recommendation: names ['CASE_2'] ('with INTERVENTION_1 and INTERVENTION_2 effectively minimizing total disturbance')
- Error: uncertainties do not cover LIMITATION.synthetic_imp_ims
- Error: uncertainties do not cover LIMITATION.single_deterministic_scenario
- Error: uncertainties do not cover LIMITATION.synthetic_intervention_magnitudes
- Error: uncertainties do not cover LIMITATION.no_historical_calibration
- Human review reasons: synthetic capstone scenario: decision support only, citation validation failed, qualitative validation failed, objective validation failed, narrative validation failed, coverage validation failed

## Authoritative objective selections vs deterministic minimum

| Field | Agent selects | Minimum | Agreement |
|---|---|---|---|
| preferred_for_total_disturbance | CASE_1, CASE_2 | CASE_1 | DIFFERS |
| preferred_for_flight_test | CASE_1, CASE_2 | CASE_1, CASE_2 | MATCH |
| preferred_for_production_commitment | CASE_3 | CASE_1, CASE_2 | DIFFERS |

Authoritative for downstream use: none (episode not VALIDATED)

## Narrative consistency: FAIL (1 contradiction(s), 0 unchecked clause(s))

## Overall recommendation (raw model text; explanatory only)

The interventions demonstrate varying impacts on disturbance metrics, with INTERVENTION_1 and INTERVENTION_2 effectively minimizing total disturbance, while INTERVENTION_3 offers a strategic approach to limit pre-maturity production exposure. Each intervention serves distinct management objectives, necessitating careful consideration based on specific program priorities.

See the trace for structured claim checks, citations with Python-attached values, and the full interpretation.
