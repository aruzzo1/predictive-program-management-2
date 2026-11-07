# Predictive Simulation and Intervention Agent: first vs second real episode

> The intervention comparison is an illustrative test-harness experiment. It evaluates how alternative management
> policies affect a synthetic, evidence-calibrated dependency model; it does not predict historical or actual F-35
> outcomes.

Both episodes:
- used `gpt-4o-mini`, temperature 0, one structured call each;
- ran on the same frozen deterministic facts;
- were run once, with no rerun or tuning.

Between them, the **agent contract and the validation layer** changed (contract v2). The model, the facts and the
simulation did not.

| | First episode | Second episode |
|---|---|---|
| Trace | `outputs/agentic_traces/predictive_intervention_agent_20261106_101319` (preserved unchanged) | `outputs/agentic_traces/predictive_intervention_agent_20261106_102300` |
| Contract | v1: free-text effects, digits-only numeral check | v2: structured effect claims, comparative claims, secondary options, spelled-number check, objective-minimum check, fact-id citation rules |
| Tokens (in / out) | 3,986 / 1,319 | 4,958 / 1,780 |
| Status | COMPLETED_WITH_VALIDATION_ERRORS | **COMPLETED_WITH_VALIDATION_ERRORS** (usable downstream: **no**) |
| Human review | required (agent set true) | required (agent set true; Python also requires it) |

## First real episode

The first two counts below are from the v1 run itself. The rest come from re-checking its preserved text, read-only,
with the new text-level checks (`legacy_findings`); its schema has no structured claims to check.

| Failure mode | Count | Detail | Caught at the time? |
|---|---|---|---|
| Invalid citations | **6** | `CASE_1.change.cumulative_total` and `CASE_3.change.cumulative_total`, each cited three times; invented, truncated ids | Yes (v1) |
| Spelled-out quantities | **8** | "ten point four", "zero point five", "zero", "three quarters", "sixty percent", "four-day" | No: the v1 check read digits only |
| Qualitative factual errors | **1** | CASE_2: "the overall disturbance entering D8 (cumulative_D8 remains unchanged)". In fact CASE_2's D8 is eliminated | No |
| Objective-selection errors | **1** | LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE: preferred CASE_3, which CASE_1 and CASE_2 strictly beat (they have zero committed exposure) | Flagged only as advisory "DIFFERS" |
| Objective tie handling | 1 note | PROTECT_FLIGHT_TEST_EXECUTION: preferred CASE_2 alone, where CASE_1 and CASE_2 tie | v1 called this "PARTIAL"; under v2, naming one member of a tie is allowed |

## Second real episode

| Check | Errors | Detail |
|---|---|---|
| Citations | **0** | Every cited id exists. Every required claim cites a fact id, and each assessment cites facts of its own case. |
| Numeric (digits and spelled-out) | **0** | No digits and no number words in the prose. The model described direction instead ("completely cleared", "reduced", "remains unchanged"). |
| Structured effect claims | **0 of 12** | All four effects for each intervention match Python, including CASE_2's D8 entering = ELIMINATED (the first episode's error) and CASE_3's D8 entering = UNCHANGED with D8 committed = REDUCED. |
| Structured boolean claims | **2 of 6** | CASE_1 and CASE_2 `alters_propagation_upstream_of_D8` claimed false; it is true for both, since D4, D6 and D7 differ from NO ACTION. The model apparently read "upstream" as "upstream of the intervention point". The field's definition was in the prompt, but the name invites that reading. |
| Comparative claims | **0 of 7** | Every case-versus-NO-ACTION relation the model stated is correct. |
| Prose D8 rule | 0 | CASE_3's "the disturbance entering D8 remains unchanged" is correct and passes. |
| Objectives | **3** | LIMIT_PRE_MATURITY_PRODUCTION_EXPOSURE again prefers **CASE_3**, which CASE_1 and CASE_2 strictly beat. **Rejected.** The model also listed CASE_2 as a "secondary option" for that objective, claiming REDUCED and not the minimum. Both are wrong: CASE_2 is ELIMINATED and is a minimum. **Rejected.** |
| Coverage / human review | 0 | All eight limitations covered; human review set to true. |

Free text that no check covers:
- The overall recommendation still says limiting pre-maturity production exposure "favors INTERVENTION_3". The
  structured objective field carrying the same error was rejected.
- The trade-off statement that INTERVENTION_1 "does not allow for any operational flexibility" has no basis in the
  facts.

The raw response is preserved and was not repaired.

## Did the strengthened validation prevent or detect the earlier failure modes?

| First-episode failure mode | Second episode |
|---|---|
| Invented / unknown citation ids | **Not repeated** (0). If they recur, v2 rejects them, as it did in the first episode's re-check. |
| Numbers in words evading the numeral check | **Not repeated** (0). v2 now **detects** them: re-checking the first episode finds all 8. |
| Prose factual error on CASE_2 D8 | **Not repeated.** The structured CASE_2 D8 field is now correct and validated. v2 **detects** the original sentence via the prose rule. |
| CASE_3 preferred for minimizing production exposure | **Repeated.** In v1 it was an advisory note; v2 **rejects** it as an objective-validation error, so the interpretation is not usable downstream. |

The same misreading of the production-exposure objective appeared in both runs, and v2 also caught two new errors
(the upstream flag and a wrong secondary option). **This does not show that the model became more reliable.**

What changed is the **system's** ability to constrain and check the model:
- every claim that matters is either structured and recomputed by Python, or text-checked against the facts;
- the errors are recorded by category;
- an interpretation that fails is kept as it was returned, marked COMPLETED_WITH_VALIDATION_ERRORS and not usable
  downstream, and sent to human review.

Under v2 the second episode's errors could not have passed silently. In v1 the CASE_2 D8 error and the number words
did pass silently.

This is two single runs, so it supports no statistical claim about either contract or the model.

## Remaining gaps

- **Free text is checked only partly** (the D8 prose rule, numbers and citations). An unsupported qualitative sentence
  that names no checkable claim can still pass, for example "no operational flexibility", or a recommendation
  sentence restating a rejected preference.
- **The upstream field's name is ambiguous.** `alters_propagation_upstream_of_D8` evidently reads differently from
  its definition. Renaming it, for example to `changes_any_D1_to_D7_trajectory`, is a contract decision for the user;
  it was not changed after seeing the result.
- **The spelled-number detector is a word list.** It excludes "one" alone, which is too common in prose, and could
  miss unusual phrasings.
