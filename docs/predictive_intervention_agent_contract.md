# Predictive Simulation and Intervention Agent: output contract (v3)

Module 5, Agent 2. The agent interprets the frozen deterministic intervention comparison
(`outputs/simulation/intervention_comparison.json`). **Python is authoritative for every number and every
validated claim.** The model never calculates or edits results. Code: `src/ppm_agent/agents/predictive_intervention.py`;
schema: `src/ppm_agent/models/intervention.py`; prompt: `src/ppm_agent/agents/prompts/predictive_intervention.md`.

## Authoritative versus explanatory output

| Kind | Fields | Use downstream |
|---|---|---|
| **Authoritative, structured; validated by Python** | per intervention: `effect_on_total_disturbance`, `effect_on_D6_exposure`, `effect_on_D8_entering`, `effect_on_D8_committed`, `disturbance_reaches_D8`, `changes_any_D1_to_D7_trajectory`; `comparative_claims`; `preferred_for_total_disturbance`, `preferred_for_flight_test`, `preferred_for_production_commitment`; `secondary_options` | Only from a **VALIDATED** episode. Exposed as `meta.authoritative_preferences`. |
| **Explanatory, free text; checked but never authoritative** | `overall_recommendation`, rationales, trade-offs, assessments' prose | Never used as an intervention choice (`meta.overall_recommendation_is_authoritative = false`). |

## Field definitions

- **Effect enums**, relative to CASE_0 (NO ACTION):
  - ELIMINATED: the value falls to zero;
  - REDUCED;
  - UNCHANGED;
  - INCREASED.
- **Metrics:**
  - total = cumulative total disturbance;
  - D6 = effective D6 after any absorption;
  - D8 entering = cumulative D8;
  - D8 committed = D8 exposure committed before maturity (all of it for cases without staging).
- **`changes_any_D1_to_D7_trajectory`** (renamed in v3 from `alters_propagation_upstream_of_D8`):
  - TRUE if any node trajectory among D1 to D7 differs from NO ACTION at any step from t0 to t12;
  - FALSE only if every D1 to D7 trajectory is identical.
  - Python computes it step by step from `predictive_trajectories.csv`.
  - Current truth: CASE_1 TRUE (the disturbance is removed entirely, which is a change), CASE_2 TRUE, CASE_3 FALSE.
- **`preferred_for_*`:**
  - Each must contain only cases that attain the minimum of its single metric. Ties are allowed: listing the full tie
    or one member is accepted, but a strictly beaten case is rejected.
  - Current minima: total → CASE_1; flight test → CASE_1 and CASE_2; production commitment → CASE_1 and CASE_2.
- **`secondary_options`:** a case that is useful under a narrower condition, with its effect versus NO ACTION and a
  truthful `is_minimum_for_objective`. For example, CASE_3 reduces committed exposure while upstream propagation
  continues; it is useful, but it is not the minimum.

## Deterministic validation categories

| Category | Rule |
|---|---|
| structure | each intervention assessed once with its matching id; every objective present |
| citation | every cited id exists, with no repair; required claims cite at least one FACT id; each assessment cites a fact of its own case |
| numeric | digits must equal a catalogue value; spelled-out quantities (number words, decimals, fractions, percentages, multipliers in words) are rejected |
| qualitative | every structured effect, boolean and comparative claim is recomputed from the facts; a backup prose rule rejects D8 "unchanged" statements that contradict the facts |
| objective | `preferred_for_*`, the explanatory per-objective list and secondary options are checked against the deterministic minima and effects |
| narrative | the explanatory per-objective list must equal the structured fields; free-text preference clauses must not name a case outside an objective's structured selection or its minimum (see the rule below) |
| coverage | all eight LIMITATION ids are covered |
| human_review | the agent's flag must be true for the synthetic capstone scenario |

**Narrative rule** (deterministic, no LLM):
1. Split the text into sentences, then clauses.
2. A clause with no objective inherits the one named earlier in the same sentence.
3. A clause is checked only if it has:
   - a preference verb (favors, preferred, recommended, best, optimal, choice, minimizes, should use, ...);
   - exactly one objective;
   - at least one named case.
4. Hedged clauses (not, rather than, secondary, although, ...) and clauses naming several objectives are recorded as
   unchecked, not guessed.

## Outcome

| Status | Meaning |
|---|---|
| VALIDATED | all categories pass; structured selections usable downstream |
| COMPLETED_WITH_VALIDATION_ERRORS | raw response preserved and not repaired; errors recorded by category; not usable downstream |
| FAILED | the call failed; nothing invented |

Python requires human review for every episode in this synthetic scenario. It lists each failed category as an
additional reason.

## Version history

- **v1:** free-text effects and a digits-only numeral check.
- **v2:** structured effects and comparisons, spelled-number rejection, objective-minimum check, fact-id citation
  rules.
- **v3:**
  - renamed `alters_propagation_upstream_of_D8` to `changes_any_D1_to_D7_trajectory`, now trajectory-based;
  - added the authoritative `preferred_for_*` fields;
  - free text became explanatory only, checked for contradictions.

Earlier traces are preserved unchanged, and tests pin their hashes.
