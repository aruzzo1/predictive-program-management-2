# Predictive Simulation and Intervention Agent: trace (validation contract v2)

> The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35 outcomes.

REAL_LLM_MODE, model `gpt-4o-mini`

- Status: **COMPLETED_WITH_VALIDATION_ERRORS**; usable downstream: **False**; human review required: **True**
- Elapsed 15.67 s; 2026-11-06T10:23:00
- Token usage: {'provider': 'openai-responses', 'model': 'gpt-4o-mini', 'successful_responses': 1, 'input_tokens': 4958, 'output_tokens': 1780}
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

- Result: **FAIL**; error counts: {'structure': 0, 'citation': 0, 'numeric': 0, 'qualitative': 2, 'objective': 3, 'coverage': 0, 'human_review': 0}
- Error: CASE_1.alters_propagation_upstream_of_D8: claimed False, deterministic True
- Error: CASE_2.alters_propagation_upstream_of_D8: claimed False, deterministic True
- Error: LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: prefers CASE_3, but ['CASE_1', 'CASE_2'] attain(s) a strictly lower cumulative D8 exposure committed before maturity (all of it for cases without staging)
- Error: secondary_options[0] CASE_2: effect claimed REDUCED, deterministic ELIMINATED
- Error: secondary_options[0] CASE_2: is_minimum_for_objective False, deterministic True
- Human review reasons: synthetic capstone scenario: decision support only, qualitative validation failed, objective validation failed

## Structured claims vs deterministic truth

| Case | Claim | Agent | Python | Match |
|---|---|---|---|---|
| CASE_1 | effect_on_total_disturbance | ELIMINATED | ELIMINATED | yes |
| CASE_1 | effect_on_D6_exposure | ELIMINATED | ELIMINATED | yes |
| CASE_1 | effect_on_D8_entering | ELIMINATED | ELIMINATED | yes |
| CASE_1 | effect_on_D8_committed | ELIMINATED | ELIMINATED | yes |
| CASE_1 | disturbance_reaches_D8 | False | False | yes |
| CASE_1 | alters_propagation_upstream_of_D8 | False | True | **NO** |
| CASE_2 | effect_on_total_disturbance | REDUCED | REDUCED | yes |
| CASE_2 | effect_on_D6_exposure | ELIMINATED | ELIMINATED | yes |
| CASE_2 | effect_on_D8_entering | ELIMINATED | ELIMINATED | yes |
| CASE_2 | effect_on_D8_committed | ELIMINATED | ELIMINATED | yes |
| CASE_2 | disturbance_reaches_D8 | False | False | yes |
| CASE_2 | alters_propagation_upstream_of_D8 | False | True | **NO** |
| CASE_3 | effect_on_total_disturbance | UNCHANGED | UNCHANGED | yes |
| CASE_3 | effect_on_D6_exposure | UNCHANGED | UNCHANGED | yes |
| CASE_3 | effect_on_D8_entering | UNCHANGED | UNCHANGED | yes |
| CASE_3 | effect_on_D8_committed | REDUCED | REDUCED | yes |
| CASE_3 | disturbance_reaches_D8 | True | True | yes |
| CASE_3 | alters_propagation_upstream_of_D8 | False | False | yes |
|  | comparative_claims[0] | CASE_1 LOWER_THAN CASE_0 on TOTAL_DISTURBANCE | LOWER_THAN | yes |
|  | comparative_claims[1] | CASE_2 LOWER_THAN CASE_0 on TOTAL_DISTURBANCE | LOWER_THAN | yes |
|  | comparative_claims[2] | CASE_3 EQUAL_TO CASE_0 on TOTAL_DISTURBANCE | EQUAL_TO | yes |
|  | comparative_claims[3] | CASE_1 LOWER_THAN CASE_0 on D6_EXPOSURE | LOWER_THAN | yes |
|  | comparative_claims[4] | CASE_2 LOWER_THAN CASE_0 on D6_EXPOSURE | LOWER_THAN | yes |
|  | comparative_claims[5] | CASE_3 EQUAL_TO CASE_0 on D6_EXPOSURE | EQUAL_TO | yes |
|  | comparative_claims[6] | CASE_3 LOWER_THAN CASE_0 on D8_COMMITTED | LOWER_THAN | yes |

## Interpretation (raw model text; cited values attached by Python; not repaired)

**No action.** The no-action scenario results in a cumulative total disturbance that is significant, with disturbances across various metrics remaining high.  
Cites: `CASE_0.cumulative_total` = 10.41

### CASE_1 / INTERVENTION_1

- **Objective addressed:** MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE
- **Effect on trajectory:** The trajectory is completely cleared of disturbances.
- **Does not change:** No disturbances propagate to D8.
- Cites: `CASE_1.change.cumulative_total.absolute_reduction` = 10.41

### CASE_2 / INTERVENTION_2

- **Objective addressed:** PROTECT_FLIGHT_TEST_EXECUTION
- **Effect on trajectory:** The trajectory is improved with unused capacity remaining.
- **Does not change:** The overall disturbance is still present but reduced significantly.
- Cites: `CASE_2.change.cumulative_total.absolute_reduction` = 9.414

### CASE_3 / INTERVENTION_3

- **Objective addressed:** LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE
- **Effect on trajectory:** The share of production exposure committed before maturity is limited.
- **Does not change:** The disturbance entering D8 remains unchanged.
- Cites: `CASE_3.change.cumulative_total.absolute_reduction` = 0

## Management trade-offs

- While INTERVENTION_1 completely eliminates disturbances, it does not allow for any operational flexibility, unlike INTERVENTION_3, which reduces pre-maturity commitments but retains upstream disturbances. (cites `CASE_1.change.cumulative_total.absolute_reduction` = 10.41, `CASE_3.change.cumulative_D8_committed_pre_maturity.absolute_reduction` = 1.446)

## Preferred intervention by objective

| Objective | Agent prefers | Minimum (Python) | Agreement | Rationale | Caveats |
|---|---|---|---|---|---|
| MINIMIZE_TOTAL_PROPAGATED_DISTURBANCE | CASE_1 | CASE_1 | MATCH | INTERVENTION_1 completely eliminates total disturbance, achieving the objective. | This is under the assumption that complete elimination is feasible in practice. |
| PROTECT_FLIGHT_TEST_EXECUTION | CASE_2 | CASE_1, CASE_2 | SUBSET_OF_TIE | INTERVENTION_2 effectively absorbs disturbances, ensuring flight test execution is protected. | This assumes the cumulative capacity is sufficient for the disturbances encountered. |
| LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE | CASE_3 | CASE_1, CASE_2 | DIFFERS | INTERVENTION_3 reduces the share of production exposure committed before maturity, aligning with the objective. | This does not address upstream disturbances, which remain unchanged. |

## Secondary options (useful under a narrower condition)

- CASE_2 for LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: Useful when upstream disturbances are manageable and flight test execution is prioritized. (effect vs NO ACTION REDUCED; minimum: False; cites `CASE_2.change.cumulative_total.absolute_reduction` = 9.414)

## Overall recommendation

The choice of intervention depends on the specific management objective: complete elimination of disturbances favors INTERVENTION_1, while protecting flight test execution favors INTERVENTION_2, and limiting pre-maturity production exposure favors INTERVENTION_3.
(cites `CASE_1.change.cumulative_total.absolute_reduction` = 10.41, `CASE_2.change.cumulative_total.absolute_reduction` = 9.414, `CASE_3.change.cumulative_D8_committed_pre_maturity.absolute_reduction` = 1.446)

**Agent's human review flag:** True. This is decision support from a synthetic model, and a human program manager must decide.

**Confidence / support:** The results are derived from a synthetic model and should be interpreted with caution, considering the assumptions and limitations outlined.

## Key assumptions

- The IMP/IMS is a synthetic, evidence-calibrated schedule, not an actual or reconstructed F-35 contractor schedule. (cites ASSUMPTION.synthetic_baseline)
- INTERVENTION_2 absorbs D6 disturbance from a cumulative capacity of 1.0 normalized unit that never resets. (cites ASSUMPTION.resequencing_cumulative_capacity)
- INTERVENTION_3 commits 40% of D8 exposure before maturity and gates 60%. (cites ASSUMPTION.staged_commitment_split)

## Uncertainties

- The IMP/IMS and all activity-level links are synthetic, limiting the applicability of results to real-world scenarios. (cites LIMITATION.synthetic_imp_ims)
- Weights are ordinal evidence tiers, not calibrated probabilities or rework fractions, affecting the reliability of propagation outcomes. (cites LIMITATION.ordinal_weights)
- The 4-day normalization is a synthetic constant, not a calibration, which may impact the interpretation of results. (cites LIMITATION.normalization_4_day)
- Only one deterministic initiating scenario is evaluated, limiting the understanding of variability in outcomes. (cites LIMITATION.single_deterministic_scenario)
- Recovery days, resequencing capacity and commitment fractions are synthetic policy values, which may not reflect actual operational conditions. (cites LIMITATION.synthetic_intervention_magnitudes)
- Cumulative metrics are truncated at t12, meaning that NO ACTION has not fully decayed by this point, potentially skewing results. (cites LIMITATION.horizon_t12_truncation)
- Interventions are evaluated one at a time, never in combination, which may overlook synergistic effects. (cites LIMITATION.no_intervention_combinations)
- Nothing is calibrated to historical F-35 outcomes; results do not predict them, limiting their applicability. (cites LIMITATION.no_historical_calibration)
