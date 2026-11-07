# Predictive Simulation and Intervention Agent: trace (validation contract v3)

> The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35 outcomes.

REAL_LLM_MODE, model `gpt-4o-mini`

- Status: **COMPLETED_WITH_VALIDATION_ERRORS**; usable downstream: **False**; human review required: **True**
- Elapsed 112.92 s; 2026-11-06T10:47:15
- Token usage: {'provider': 'openai-responses', 'model': 'gpt-4o-mini', 'successful_responses': 1, 'input_tokens': 5240, 'output_tokens': 1509}
- Initiating disturbance: DISTURBANCE_1: A210 +8 workdays, A230 float 4, exposed 4 workdays, normalized D4 = 1.0 (reference 4 workdays = 1.0)

## Deterministic facts supplied (Python-authoritative)

| Fact id | Value |
|---|---|
| `CASE_0.cumulative_D4` | 2.948070526 |
| `CASE_0.cumulative_D6` | 4.082450867 |
| `CASE_0.cumulative_D6_arrived_before_absorption` | 4.082450867 |
| `CASE_0.cumulative_D7` | 0.974035263 |
| `CASE_0.cumulative_D8` | 2.40953064 |
| `CASE_0.cumulative_total` | 10.4140873 |
| `CASE_0.final_total` | 0.4699115753 |
| `CASE_0.peak_step` | 2 |
| `CASE_0.peak_total` | 1.3125 |
| `CASE_1.change.cumulative_D6.absolute_reduction` | 4.082450867 |
| `CASE_1.change.cumulative_D6.percent_reduction` | 100 |
| `CASE_1.change.cumulative_D8.absolute_reduction` | 2.40953064 |
| `CASE_1.change.cumulative_D8.percent_reduction` | 100 |
| `CASE_1.change.cumulative_D8_committed_pre_maturity.absolute_reduction` | 2.40953064 |
| `CASE_1.change.cumulative_D8_committed_pre_maturity.percent_reduction` | 100 |
| `CASE_1.change.cumulative_total.absolute_reduction` | 10.4140873 |
| `CASE_1.change.cumulative_total.percent_reduction` | 100 |
| `CASE_1.change.peak_total.absolute_reduction` | 1.3125 |
| `CASE_1.change.peak_total.percent_reduction` | 100 |
| `CASE_1.cumulative_D4` | 0 |
| `CASE_1.cumulative_D6` | 0 |
| `CASE_1.cumulative_D6_arrived_before_absorption` | 0 |
| `CASE_1.cumulative_D7` | 0 |
| `CASE_1.cumulative_D8` | 0 |
| `CASE_1.cumulative_total` | 0 |
| `CASE_1.final_total` | 0 |
| `CASE_1.peak_total` | 0 |
| `CASE_2.D6_first_arrival` | 0.75 |
| `CASE_2.D6_first_arrival_step` | 1 |
| `CASE_2.change.cumulative_D6.absolute_reduction` | 4.082450867 |
| `CASE_2.change.cumulative_D6.percent_reduction` | 100 |
| `CASE_2.change.cumulative_D8.absolute_reduction` | 2.40953064 |
| `CASE_2.change.cumulative_D8.percent_reduction` | 100 |
| `CASE_2.change.cumulative_D8_committed_pre_maturity.absolute_reduction` | 2.40953064 |
| `CASE_2.change.cumulative_D8_committed_pre_maturity.percent_reduction` | 100 |
| `CASE_2.change.cumulative_total.absolute_reduction` | 9.414087296 |
| `CASE_2.change.cumulative_total.percent_reduction` | 90.397622 |
| `CASE_2.change.peak_total.absolute_reduction` | 0.3125 |
| `CASE_2.change.peak_total.percent_reduction` | 23.809524 |
| `CASE_2.cumulative_D4` | 1 |
| `CASE_2.cumulative_D6` | 0 |
| `CASE_2.cumulative_D6_arrived_before_absorption` | 0.75 |
| `CASE_2.cumulative_D7` | 0 |
| `CASE_2.cumulative_D8` | 0 |
| `CASE_2.cumulative_total` | 1 |
| `CASE_2.final_total` | 0 |
| `CASE_2.intervention_capacity` | 1 |
| `CASE_2.intervention_unused` | 0.25 |
| `CASE_2.intervention_used` | 0.75 |
| `CASE_2.peak_step` | 0 |
| `CASE_2.peak_total` | 1 |
| `CASE_3.change.cumulative_D6.absolute_reduction` | 0 |
| `CASE_3.change.cumulative_D6.percent_reduction` | 0 |
| `CASE_3.change.cumulative_D8.absolute_reduction` | 0 |
| `CASE_3.change.cumulative_D8.percent_reduction` | 0 |
| `CASE_3.change.cumulative_D8_committed_pre_maturity.absolute_reduction` | 1.445718384 |
| `CASE_3.change.cumulative_D8_committed_pre_maturity.percent_reduction` | 60 |
| `CASE_3.change.cumulative_total.absolute_reduction` | 0 |
| `CASE_3.change.cumulative_total.percent_reduction` | 0 |
| `CASE_3.change.peak_total.absolute_reduction` | 0 |
| `CASE_3.change.peak_total.percent_reduction` | 0 |
| `CASE_3.cumulative_D4` | 2.948070526 |
| `CASE_3.cumulative_D6` | 4.082450867 |
| `CASE_3.cumulative_D6_arrived_before_absorption` | 4.082450867 |
| `CASE_3.cumulative_D7` | 0.974035263 |
| `CASE_3.cumulative_D8` | 2.40953064 |
| `CASE_3.cumulative_D8_committed_pre_maturity` | 0.9638122559 |
| `CASE_3.cumulative_D8_gated_deferred` | 1.445718384 |
| `CASE_3.cumulative_total` | 10.4140873 |
| `CASE_3.final_total` | 0.4699115753 |
| `CASE_3.peak_step` | 2 |
| `CASE_3.peak_total` | 1.3125 |
| `DISTURBANCE_1.available_float_days` | 4 |
| `DISTURBANCE_1.exposed_delay_days` | 4 |
| `DISTURBANCE_1.gross_slip_days` | 8 |
| `DISTURBANCE_1.initial_D4` | 1 |
| `INTERVENTION_1.exposed_delay_days` | 0 |
| `INTERVENTION_1.recovery_days` | 4 |
| `INTERVENTION_2.capacity_days` | 4 |
| `INTERVENTION_2.capacity_normalized` | 1 |
| `INTERVENTION_3.post_maturity_commitment_fraction` | 0.6 |
| `INTERVENTION_3.pre_maturity_commitment_fraction` | 0.4 |
| `MAPPING.reference_exposed_delay_days` | 4 |
| `SIMULATION.horizon_last_step` | 12 |
| `WTM.spectral_radius` | 0.9114378278 |

## Deterministic validation

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

## Structured claims vs deterministic truth

| Case | Claim | Agent | Python | Match |
|---|---|---|---|---|
| CASE_1 | effect_on_total_disturbance | ELIMINATED | ELIMINATED | yes |
| CASE_1 | effect_on_D6_exposure | ELIMINATED | ELIMINATED | yes |
| CASE_1 | effect_on_D8_entering | ELIMINATED | ELIMINATED | yes |
| CASE_1 | effect_on_D8_committed | ELIMINATED | ELIMINATED | yes |
| CASE_1 | disturbance_reaches_D8 | False | False | yes |
| CASE_1 | changes_any_D1_to_D7_trajectory | True | True | yes |
| CASE_2 | effect_on_total_disturbance | REDUCED | REDUCED | yes |
| CASE_2 | effect_on_D6_exposure | ELIMINATED | ELIMINATED | yes |
| CASE_2 | effect_on_D8_entering | ELIMINATED | ELIMINATED | yes |
| CASE_2 | effect_on_D8_committed | ELIMINATED | ELIMINATED | yes |
| CASE_2 | disturbance_reaches_D8 | False | False | yes |
| CASE_2 | changes_any_D1_to_D7_trajectory | True | True | yes |
| CASE_3 | effect_on_total_disturbance | UNCHANGED | UNCHANGED | yes |
| CASE_3 | effect_on_D6_exposure | UNCHANGED | UNCHANGED | yes |
| CASE_3 | effect_on_D8_entering | UNCHANGED | UNCHANGED | yes |
| CASE_3 | effect_on_D8_committed | REDUCED | REDUCED | yes |
| CASE_3 | disturbance_reaches_D8 | True | True | yes |
| CASE_3 | changes_any_D1_to_D7_trajectory | False | False | yes |
|  | comparative_claims[0] | CASE_1 LOWER_THAN CASE_0 on TOTAL_DISTURBANCE | LOWER_THAN | yes |
|  | comparative_claims[1] | CASE_2 LOWER_THAN CASE_0 on TOTAL_DISTURBANCE | LOWER_THAN | yes |
|  | comparative_claims[2] | CASE_3 LOWER_THAN CASE_0 on D8_COMMITTED | LOWER_THAN | yes |

## Authoritative objective selections (structured) vs deterministic minimum

| Field | Agent selects | Minimum (Python) | Agreement |
|---|---|---|---|
| preferred_for_total_disturbance | CASE_1, CASE_2 | CASE_1 | DIFFERS |
| preferred_for_flight_test | CASE_1, CASE_2 | CASE_1, CASE_2 | MATCH |
| preferred_for_production_commitment | CASE_3 | CASE_1, CASE_2 | DIFFERS |

## Narrative consistency (free text is explanatory only)

- Result: **FAIL**; 1 contradiction(s), 0 consistent preference clause(s), 0 unchecked (hedged or several objectives)
- Contradiction in overall_recommendation: 'with INTERVENTION_1 and INTERVENTION_2 effectively minimizing total disturbance' names ['CASE_2']; preferred_for_total_disturbance is ['CASE_1', 'CASE_2'], minimum ['CASE_1']

## Interpretation (raw model text; cited values attached by Python; not repaired)

**No action.** The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35 outcomes.  
Cites: `LIMITATION.no_historical_calibration`

### CASE_1 / INTERVENTION_1

- **Objective addressed:** MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE
- **Effect on trajectory:** All disturbances eliminated; trajectory unchanged from NO ACTION.
- **Does not change:** No disturbances propagate; no exposure remains.
- Cites: `CASE_0.cumulative_total` = 10.41, `CASE_1.change.cumulative_total.absolute_reduction` = 10.41

### CASE_2 / INTERVENTION_2

- **Objective addressed:** MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE
- **Effect on trajectory:** D6 disturbance absorbed; trajectory altered from NO ACTION.
- **Does not change:** D8 exposure remains unchanged; no disturbances reach D8.
- Cites: `CASE_0.cumulative_total` = 10.41, `CASE_2.change.cumulative_total.absolute_reduction` = 9.414

### CASE_3 / INTERVENTION_3

- **Objective addressed:** LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE
- **Effect on trajectory:** D8 exposure committed reduced; trajectory unchanged for D1 to D7.
- **Does not change:** D6 exposure and D8 disturbance entering remain unchanged.
- Cites: `CASE_0.cumulative_total` = 10.41, `CASE_3.change.cumulative_total.absolute_reduction` = 0

## Management trade-offs

- INTERVENTION_3 reduces the share of D8 exposure committed before maturity but does not reduce upstream propagation or the disturbance entering D8. (cites `INTERVENTION_3_note`)

## Preferred intervention by objective (explanation)

| Objective | Agent prefers | Minimum (Python) | Agreement | Rationale | Caveats |
|---|---|---|---|---|---|
| MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE | CASE_1, CASE_2 | CASE_1 | DIFFERS | Both interventions eliminate or reduce total disturbance compared to NO ACTION. | Both cases achieve lower total disturbance than NO ACTION; CASE_1 eliminates it entirely. |
| PROTECT_FLIGHT_TEST_EXECUTION | CASE_1, CASE_2 | CASE_1, CASE_2 | MATCH | Both interventions eliminate D6 exposure, ensuring flight test execution is protected. | D6 exposure is eliminated in both cases, safeguarding flight test execution. |
| LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE | CASE_3 | CASE_1, CASE_2 | DIFFERS | Only CASE_3 reduces the share of D8 exposure committed before maturity. | While it does not reduce D8 disturbance entering, it limits pre-maturity commitment. |

## Secondary options (useful under a narrower condition)


## Overall recommendation (explanatory only; not an authoritative choice)

The interventions demonstrate varying impacts on disturbance metrics, with INTERVENTION_1 and INTERVENTION_2 effectively minimizing total disturbance, while INTERVENTION_3 offers a strategic approach to limit pre-maturity production exposure. Each intervention serves distinct management objectives, necessitating careful consideration based on specific program priorities.
(cites `LIMITATION.single_deterministic_scenario`)

**Agent's human review flag:** True. This is decision support from a synthetic model, and a human program manager must decide.

**Confidence / support:** The results are derived from a synthetic model with defined assumptions and limitations, emphasizing the need for human oversight in decision-making.

## Key assumptions

- The IMP/IMS (v1.1) is a synthetic, evidence-calibrated schedule, not an actual or reconstructed F-35 contractor schedule. (cites ASSUMPTION.synthetic_baseline)
- INTERVENTION_2 absorbs D6 disturbance from a cumulative capacity of 1.0 normalized unit that never resets. (cites ASSUMPTION.resequencing_cumulative_capacity)
- INTERVENTION_3 commits 40% of D8 exposure before maturity and gates 60%. (cites ASSUMPTION.staged_commitment_split)

## Uncertainties

- Weights are ordinal evidence tiers, not calibrated probabilities or rework fractions. (cites LIMITATION.ordinal_weights)
- The 4-day normalization is a synthetic constant, not a calibration. (cites LIMITATION.normalization_4_day)
- Cumulative metrics are truncated at t12; NO ACTION has not fully decayed by t12. (cites LIMITATION.horizon_t12_truncation)
- Interventions are evaluated one at a time, never in combination. (cites LIMITATION.no_intervention_combinations)
