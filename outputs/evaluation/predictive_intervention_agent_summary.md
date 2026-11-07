# Predictive Simulation and Intervention Agent: episode summary

> The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35 outcomes.

- Trace: `outputs/agentic_traces/predictive_intervention_agent_20261106_101319.json` (and `.md`)
- Mode: REAL_LLM_MODE; model: gpt-4o-mini; status: **COMPLETED_WITH_VALIDATION_ERRORS**
- Tokens: {'provider': 'openai-responses', 'model': 'gpt-4o-mini', 'successful_responses': 1, 'input_tokens': 3986, 'output_tokens': 1319}; elapsed 21.32 s
- One run; not repeated or tuned.

## Validation

- Deterministic validation: **FAIL**; numerals found 0, unsupported 0.
- Error: overall_recommendation: unknown id 'CASE_1.change.cumulative_total'
- Error: overall_recommendation: unknown id 'CASE_3.change.cumulative_total'
- Error: MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE: unknown id 'CASE_1.change.cumulative_total'
- Error: LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: unknown id 'CASE_3.change.cumulative_total'
- Error: management_tradeoffs[0]: unknown id 'CASE_1.change.cumulative_total'
- Error: management_tradeoffs[0]: unknown id 'CASE_3.change.cumulative_total'

## Preference by objective vs Python's single-metric facts (advisory)

| Objective | Agent prefers | Lowest-metric case(s) | Agreement |
|---|---|---|---|
| MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE | CASE_1 | CASE_1 | MATCH |
| PROTECT_FLIGHT_TEST_EXECUTION | CASE_2 | CASE_1, CASE_2 | PARTIAL |
| LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE | CASE_3 | CASE_1, CASE_2 | DIFFERS |

## Human review

True: This interpretation of a synthetic model requires a human program manager's decision based on the objectives outlined.

## Overall recommendation (model text)

The recommendation varies by objective: for minimizing total propagated disturbance, INTERVENTION_1 is preferred; for protecting flight test execution, INTERVENTION_2 is recommended; and for limiting pre-maturity production exposure, INTERVENTION_3 is the best choice.

See the trace for the full interpretation, citations with Python-attached values, assumptions and uncertainties.

## Reviewer assessment (added after the run; my reading of the trace, not part of the generated output)

**What worked**
- **Structure and coverage.** It returned the full schema, assessed each intervention once, and set human review to
  True with a reason.
- **Limitations.** It covered all eight required limitations and made no claim to predict F-35 outcomes.
- **INTERVENTION_2 framing.** It said the capacity absorbs the entire disturbance reaching flight test, with capacity
  left unused, and that a larger disturbance could exceed it.
- **INTERVENTION_3 framing.** It said the policy reduces the committed share of production exposure but not the
  disturbance entering D8.
- **Objective framing.** The recommendation is conditional on the objective; there is no composite score.

**What went wrong**
1. **Invalid citations (caught by Python).** Six citations use ids that do not exist, for example
   `CASE_1.change.cumulative_total`. The real ids end in `.absolute_reduction` or `.percent_reduction`.
2. **Factual error (not caught by any automated check).** For CASE_2 it states that the disturbance entering D8
   "remains unchanged". In the deterministic results CASE_2 reduces cumulative D8 to zero (a 100% reduction), because
   the disturbance is absorbed at D6 before it reaches D7 or D8.
3. **Misreading of the production-exposure objective (flagged by the advisory check as DIFFERS).** It prefers CASE_3
   and calls INTERVENTION_3 "the best choice". But CASE_1 and CASE_2 stop any disturbance reaching D8, so their
   pre-maturity committed exposure is zero, lower than CASE_3's.
   - INTERVENTION_3 is the only option that manages exposure *once disturbance reaches D8*.
   - It is not the lowest-exposure option in this scenario.
4. **Flight-test objective incomplete (flagged PARTIAL).** It names only CASE_2. CASE_1 also leaves flight test with
   zero effective disturbance.
5. **Gap in the numeric guard.** The model wrote quantities as words ("about ten point four", "about three
   quarters", "about sixty percent"). These match the facts, but the numeral check validates digits only, so spelled-out
   numbers are unverified. The prompt invited this by asking for quantities in words. This is a design gap to fix
   before relying on the guard, not a model failure.

**Bottom line.** The deterministic layer and the validation did their jobs: the facts are intact, and two of the
three substantive problems were caught or flagged. The model's interpretation is useful as a draft, but it is not
reliable without human review. That supports keeping human review mandatory and motivates the Module 6 layer.
This was a single run, so these observations describe this run only.
